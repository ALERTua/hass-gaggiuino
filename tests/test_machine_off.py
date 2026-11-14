"""While the machine is off, the entities are unavailable and the Availability sensor is off."""

from datetime import timedelta

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .conftest import FakeMachine, setup_entry
from .test_entities import ENTITY_IDS

AVAILABILITY = "binary_sensor.gaggiuino_availability"
OTHERS = sorted(set(ENTITY_IDS) - {AVAILABILITY})


async def _next_poll(hass: HomeAssistant) -> None:
    """Move the clock past the poll interval and let the poll finish."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=31))
    await hass.async_block_till_done()


def _unavailable(hass: HomeAssistant) -> list[str]:
    return [e for e in OTHERS if hass.states.get(e).state == STATE_UNAVAILABLE]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_machine_turns_off_and_on(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The entities go unavailable when the machine stops answering and come back after."""
    await setup_entry(hass)

    machine.online = False
    await _next_poll(hass)

    assert _unavailable(hass) == OTHERS
    assert hass.states.get(AVAILABILITY).state == "off"

    machine.online = True
    await _next_poll(hass)

    assert _unavailable(hass) == []
    assert hass.states.get(AVAILABILITY).state == "on"
    assert hass.states.get("sensor.gaggiuino_profile_id").state == "9"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_setup_while_machine_is_off(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The entry sets up while the machine is off, and the entities get values later."""
    machine.online = False
    entry = await setup_entry(hass)

    assert entry.state is ConfigEntryState.LOADED
    assert _unavailable(hass) == OTHERS
    assert hass.states.get(AVAILABILITY).state == "off"

    machine.online = True
    await _next_poll(hass)

    assert _unavailable(hass) == []
    assert hass.states.get(AVAILABILITY).state == "on"


async def test_device_card_follows_the_machine(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The card gets the board type after a setup without the machine, and a new firmware."""
    machine.online = False
    entry = await setup_entry(hass)
    registry = dr.async_get(hass)

    def card() -> tuple[str | None, str | None]:
        (device,) = dr.async_entries_for_config_entry(registry, entry.entry_id)
        return device.sw_version, device.model

    assert card() == (None, "Gaggiuino")

    machine.online = True
    await _next_poll(hass)

    assert card() == ("c929939", "STM32U585-PCB-NCP")

    machine.status["coreVersion"] = "abc1234"
    await _next_poll(hass)

    assert card() == ("abc1234", "STM32U585-PCB-NCP")
