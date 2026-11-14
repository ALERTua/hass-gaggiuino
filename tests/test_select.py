"""The profile select shows the saved profiles and selects one on the machine."""

from homeassistant.components.select import ATTR_OPTION
from homeassistant.components.select import DOMAIN as SELECT_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, SERVICE_SELECT_OPTION
from homeassistant.core import HomeAssistant

from .conftest import FakeMachine, setup_entry

PROFILE = "select.gaggiuino_profile"


async def test_profile_options(hass: HomeAssistant, machine: FakeMachine) -> None:
    """The options are the saved profiles, and the current one is the selected one."""
    await setup_entry(hass)

    state = hass.states.get(PROFILE)

    assert state.attributes["options"] == ["_Long (ID: 7)", "_OFF (ID: 9)"]
    assert state.state == "_OFF (ID: 9)"


async def test_profile_select(hass: HomeAssistant, machine: FakeMachine) -> None:
    """A select sends the id of the profile and shows the new profile at once."""
    await setup_entry(hass)

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: PROFILE, ATTR_OPTION: "_Long (ID: 7)"},
        blocking=True,
    )

    assert machine.requests("POST", "profile-select/7") == [None]
    assert hass.states.get(PROFILE).state == "_Long (ID: 7)"
    assert hass.states.get("sensor.gaggiuino_profile_name").state == "_Long"
