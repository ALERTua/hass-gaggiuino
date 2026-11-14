"""Fixtures of the end-to-end tests: Home Assistant runs the integration against a real machine.

The machine answers at `GAGGIUINO_BASE_URL`, by default at `DEFAULT_BASE_URL` of the library.
"""

import os
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import patch

import aiohttp
import pytest
import pytest_asyncio
import pytest_socket
from aiohttp.resolver import AsyncResolver
from gaggiuino_api import GaggiuinoClient
from gaggiuino_api.const import DEFAULT_BASE_URL
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry
from yarl import URL

from custom_components.gaggiuino.const import DOMAIN

from .e2e_support import RawMachine

BASE_URL = os.getenv("GAGGIUINO_BASE_URL", DEFAULT_BASE_URL)


def allow_machine_network(hosts: list[str]) -> None:
    """Let a socket connect only to the machine; pytest-socket lifts this after each test."""
    pytest_socket.enable_socket()
    pytest_socket.socket_allow_hosts(hosts, allow_unix_socket=True)


async def read_machine_state(hosts: list[str]) -> dict[str, Any]:
    """Read the state that the tests change, on an own session outside Home Assistant."""
    allow_machine_network(hosts)
    resolver = AsyncResolver()
    try:
        connector = aiohttp.TCPConnector(resolver=resolver)
        async with aiohttp.ClientSession(connector=connector) as session:
            return await RawMachine(session, BASE_URL).state()
    finally:
        await resolver.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def machine_hosts() -> list[str]:
    """Return the addresses of the machine, from the resolver that Home Assistant gets in tests."""
    host = URL(BASE_URL).host
    assert host, f"No host in GAGGIUINO_BASE_URL {BASE_URL!r}"
    resolver = AsyncResolver()
    try:
        answers = await resolver.resolve(host)
    finally:
        await resolver.close()
    return sorted({answer["host"] for answer in answers})


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def machine_unchanged(machine_hosts: list[str]) -> AsyncIterator[None]:
    """Make sure that the session leaves the profiles and the written settings as it found them."""
    before = await read_machine_state(machine_hosts)
    yield
    assert await read_machine_state(machine_hosts) == before


@pytest.fixture(autouse=True)
def machine_network(machine_hosts: list[str]) -> None:
    """Open the network of each test to the machine, and to nothing else."""
    allow_machine_network(machine_hosts)


@pytest.fixture(autouse=True)
async def dns_resolver(disable_mock_zeroconf_resolver: None) -> AsyncIterator[None]:
    """Give the session of Home Assistant a DNS resolver on the loop of the test.

    The resolver of the test package lives on the session loop, which a test cannot use.
    """
    resolver = AsyncResolver()
    # Home Assistant closes its resolver with `real_close` when it stops.
    resolver.real_close = resolver.close
    with patch(
        "homeassistant.helpers.aiohttp_client._async_make_resolver",
        return_value=resolver,
    ):
        yield
    await resolver.close()


@pytest.fixture
async def entry(hass: HomeAssistant) -> MockConfigEntry:
    """Set up the integration against the real machine and return its loaded entry."""
    config_entry = MockConfigEntry(domain=DOMAIN, data={"url": BASE_URL}, version=2)
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    return config_entry


@pytest.fixture
def client(hass: HomeAssistant) -> GaggiuinoClient:
    """Return a library client on the session of Home Assistant, for direct reads."""
    return GaggiuinoClient(BASE_URL, session=async_get_clientsession(hass))


@pytest.fixture
def raw(hass: HomeAssistant) -> RawMachine:
    """Return raw reads and writes on the session of Home Assistant."""
    return RawMachine(async_get_clientsession(hass), BASE_URL)


@pytest.fixture
async def idle_machine(client: GaggiuinoClient) -> None:
    """Skip a writing test while the machine brews, steams or gives hot water."""
    status = await client.status()
    if status.brew_active or status.steam_active or status.hot_water_active:
        pytest.skip("The machine is busy: a writing test runs only on an idle machine")
