"""An old firmware stops the setup with a text that names the minimum firmware."""

from gaggiuino_api import MINIMUM_FIRMWARE
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from .conftest import FakeMachine, setup_entry


async def test_old_firmware_stops_setup(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A status without a required key fails the poll, and the entry waits for a retry."""
    del machine.status["livePowerWatts"]

    entry = await setup_entry(hass)

    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert f"firmware {MINIMUM_FIRMWARE} or newer" in entry.reason
    assert "live_power_watts" in entry.reason
