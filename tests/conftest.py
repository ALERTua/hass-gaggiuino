"""Shared fixtures: Home Assistant loads the integration, and a mock plays the machine."""

import copy
import json
import re
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import PropertyMock, patch

import aiohttp
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
    AiohttpClientMockResponse,
)
from yarl import URL

from custom_components.gaggiuino.const import DOMAIN

FIXTURES = Path(__file__).parent / "fixtures"
BASE_URL = "http://gaggiuino.local"
ENTRY_ID = "test_entry"


def load_fixture(name: str) -> Any:
    """Return a saved answer of the machine as decoded JSON."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load the integration from `custom_components`."""


@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Enable each entity that is disabled by default."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        return_value=True,
        new_callable=PropertyMock,
    ):
        yield


class FakeMachine:
    """Plays the REST API of the machine: a settings write changes what the next read gets."""

    def __init__(self, aioclient_mock: AiohttpClientMocker) -> None:
        self.mock = aioclient_mock
        self.online = True
        # Paths under /api/ that answer 404, and a switch that makes each write fail.
        self.missing: set[str] = set()
        self.refuse_writes = False
        self.status: dict[str, Any] = load_fixture("status.json")[0]
        self.profiles: list[dict[str, Any]] = load_fixture("profiles_all.json")
        self.settings: dict[str, Any] = load_fixture("settings.json")
        self.answers: dict[str, Any] = {
            "health": load_fixture("health.json"),
            "shots/latest": load_fixture("shots_latest.json"),
            "firmware/progress": load_fixture("firmware_progress.json"),
            "maintenance": load_fixture("maintenance.json"),
        }
        pattern = re.compile(rf"^{re.escape(BASE_URL)}/api/")
        aioclient_mock.get(pattern, side_effect=self._answer)
        aioclient_mock.post(pattern, side_effect=self._answer)

    def requests(self, method: str, path: str) -> list[Any]:
        """Return the body of each request of `method` to `/api/<path>`, in order."""
        url = URL(f"{BASE_URL}/api/{path}")
        return [
            data
            for call_method, call_url, data, _ in self.mock.mock_calls
            if call_method.upper() == method and call_url == url
        ]

    async def _answer(
        self, method: str, url: URL, data: Any
    ) -> AiohttpClientMockResponse:
        if not self.online:
            raise aiohttp.ClientConnectionError("The machine is off")
        path = url.path.removeprefix("/api/")
        if path in self.missing:
            return AiohttpClientMockResponse(method, url, status=404, text="Not found")
        if method.upper() == "POST":
            return self._command(method, url, path, data)
        if path == "system/status":
            body: Any = [self.status]
        elif path == "profiles/all":
            body = self.profiles
        elif path == "settings":
            body = self.settings
        elif path.startswith("settings/"):
            body = self.settings[path.removeprefix("settings/")]
        else:
            body = self.answers[path]
        return AiohttpClientMockResponse(method, url, json=copy.deepcopy(body))

    def _command(
        self, method: str, url: URL, path: str, data: Any
    ) -> AiohttpClientMockResponse:
        if self.refuse_writes:
            refusal = {"success": False, "message": "The machine refused the write"}
            return AiohttpClientMockResponse(method, url, json=refusal)
        if path.startswith("settings/"):
            self.settings[path.removeprefix("settings/")] = copy.deepcopy(data)
        elif path.startswith("profile-select/"):
            selected_id = int(path.removeprefix("profile-select/"))
            for profile in self.profiles:
                profile["selected"] = (
                    "true" if profile["id"] == selected_id else "false"
                )
                if profile["id"] == selected_id:
                    self.status["profileId"] = str(selected_id)
                    self.status["profileName"] = profile["name"]
        else:
            raise AssertionError(f"No fake answer for POST {path}")
        return AiohttpClientMockResponse(method, url, json={"success": True})


@pytest.fixture
def machine(aioclient_mock: AiohttpClientMocker) -> FakeMachine:
    """Return the fake machine that answers each request of the integration."""
    return FakeMachine(aioclient_mock)


async def setup_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Add the config entry of the machine and set it up."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={"url": BASE_URL}, version=2, entry_id=ENTRY_ID
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
