"""The config flow checks the machine before it creates the entry."""

from ipaddress import ip_address
from unittest.mock import patch

import pytest
from gaggiuino_api import MINIMUM_FIRMWARE
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.gaggiuino.const import DOMAIN

from .conftest import BASE_URL, FakeMachine

# An address from the documentation range 192.0.2.0/24.
MACHINE_IP = "192.0.2.10"


async def _submit_url(hass: HomeAssistant) -> dict:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch("custom_components.gaggiuino.async_setup_entry", return_value=True):
        return await hass.config_entries.flow.async_configure(
            result["flow_id"], {"url": BASE_URL}
        )


async def test_flow_creates_entry(hass: HomeAssistant, machine: FakeMachine) -> None:
    """A machine that answers gives an entry with its URL."""
    result = await _submit_url(hass)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"gaggiuino ({BASE_URL})"
    assert result["data"] == {"url": BASE_URL}


async def test_flow_cannot_connect(hass: HomeAssistant, machine: FakeMachine) -> None:
    """A machine that does not answer shows the connection error."""
    machine.online = False

    result = await _submit_url(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_flow_old_firmware(hass: HomeAssistant, machine: FakeMachine) -> None:
    """A machine with an old firmware shows the error that names the minimum firmware."""
    del machine.status["livePowerWatts"]

    result = await _submit_url(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unsupported_firmware"}
    assert result["description_placeholders"]["minimum_firmware"] == "c929939"


async def test_flow_second_entry_of_same_host(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The manual step refuses a second entry for a host that has an entry."""
    first = await _submit_url(hass)
    assert first["type"] is FlowResultType.CREATE_ENTRY

    second = await _submit_url(hass)

    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "already_configured"


async def test_flow_host_of_an_entry_without_unique_id(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The manual step also refuses a host of an entry that an older version made."""
    MockConfigEntry(domain=DOMAIN, data={"url": f"{BASE_URL}/"}, version=2).add_to_hass(
        hass
    )

    result = await _submit_url(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


def _announcement(port: int | None = 80) -> ZeroconfServiceInfo:
    """Return the mDNS announcement that a machine makes."""
    return ZeroconfServiceInfo(
        ip_address=ip_address(MACHINE_IP),
        ip_addresses=[ip_address(MACHINE_IP)],
        port=port,
        hostname="gaggiuino.local.",
        type="_http._tcp.local.",
        name="gaggiuino._http._tcp.local.",
        properties={},
    )


async def _discover(hass: HomeAssistant, port: int | None = 80) -> dict:
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=_announcement(port),
    )


async def _confirm(hass: HomeAssistant, flow_id: str) -> dict:
    with patch("custom_components.gaggiuino.async_setup_entry", return_value=True):
        return await hass.config_entries.flow.async_configure(flow_id, {})


async def test_discovery_creates_entry(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A discovered machine asks for a confirmation, and the entry keeps the host name."""
    result = await _discover(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "zeroconf_confirm"
    assert result["description_placeholders"] == {"host": "gaggiuino.local"}

    created = await _confirm(hass, result["flow_id"])

    assert created["type"] is FlowResultType.CREATE_ENTRY
    assert created["title"] == f"gaggiuino ({BASE_URL})"
    assert created["data"] == {"url": BASE_URL}
    assert created["result"].unique_id == "gaggiuino.local"


async def test_discovery_port_goes_into_url(
    hass: HomeAssistant, machine: FakeMachine, aioclient_mock: AiohttpClientMocker
) -> None:
    """A port other than 80 is part of the URL of the entry."""
    aioclient_mock.get(f"{BASE_URL}:8080/api/system/status", json=[machine.status])

    result = await _discover(hass, port=8080)
    created = await _confirm(hass, result["flow_id"])

    assert created["data"] == {"url": f"{BASE_URL}:8080"}
    assert created["result"].unique_id == "gaggiuino.local"


@pytest.mark.parametrize(
    ("url", "unique_id"),
    [
        (BASE_URL, None),
        (f"{BASE_URL}/", None),
        (f"http://{MACHINE_IP}", None),
        ("http://other.example", "gaggiuino.local"),
    ],
    ids=["same-url", "same-url-with-slash", "ip-address", "same-unique-id"],
)
async def test_discovery_already_configured(
    hass: HomeAssistant, url: str, unique_id: str | None
) -> None:
    """A machine that has an entry is not offered again, and no request is made."""
    MockConfigEntry(
        domain=DOMAIN, data={"url": url}, version=2, unique_id=unique_id
    ).add_to_hass(hass)

    result = await _discover(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_discovery_cannot_connect(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A host that does not answer is not offered."""
    machine.online = False

    result = await _discover(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_discovery_old_firmware(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A machine with an old firmware is not offered, and the abort names the minimum."""
    del machine.status["livePowerWatts"]

    result = await _discover(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unsupported_firmware"
    assert result["description_placeholders"] == {"minimum_firmware": MINIMUM_FIRMWARE}
