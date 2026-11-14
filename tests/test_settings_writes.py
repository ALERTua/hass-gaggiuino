"""Each control writes its whole settings group back with exactly one change."""

import asyncio
import copy
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .conftest import FakeMachine, setup_entry

WRITES = [
    pytest.param(
        ("light", "turn_on", "light.gaggiuino_led", {}),
        {},
        ("led", {"state": True}),
        "on",
        id="light_on",
    ),
    pytest.param(
        ("light", "turn_off", "light.gaggiuino_led", {}),
        {"state": True},
        ("led", {"state": False}),
        "off",
        id="light_off",
    ),
    pytest.param(
        ("light", "turn_on", "light.gaggiuino_led", {"rgb_color": [1, 2, 3]}),
        {"state": True},
        ("led", {"color": {"R": 1, "G": 2, "B": 3}}),
        "on",
        id="light_color",
    ),
    pytest.param(
        ("switch", "turn_off", "switch.gaggiuino_led_disco", {}),
        {},
        ("led", {"disco": False}),
        "off",
        id="led_disco",
    ),
    pytest.param(
        ("switch", "turn_on", "switch.gaggiuino_force_predictive_scales", {}),
        {},
        ("scales", {"forcePredictive": True}),
        "on",
        id="force_predictive",
    ),
    pytest.param(
        ("switch", "turn_on", "switch.gaggiuino_hardware_scales", {}),
        {},
        ("scales", {"hwScalesEnabled": True}),
        "on",
        id="hw_scales",
    ),
    pytest.param(
        ("switch", "turn_off", "switch.gaggiuino_bluetooth_scales", {}),
        {},
        ("scales", {"btScalesEnabled": False}),
        "off",
        id="bt_scales",
    ),
    pytest.param(
        ("number", "set_value", "number.gaggiuino_steam", {"value": 130}),
        {},
        ("boiler", {"steamSetPoint": 130}),
        "130.0",
        id="steam_set_point",
    ),
    pytest.param(
        (
            "select",
            "select_option",
            "select.gaggiuino_release_channel",
            {"option": "Test"},
        ),
        {},
        ("system", {"releaseChannel": 1}),
        "Test",
        id="release_channel",
    ),
    pytest.param(
        ("number", "set_value", "number.gaggiuino_display_brightness", {"value": 30}),
        {},
        ("display", {"lcdBrightness": 30}),
        "30.0",
        id="display_brightness",
    ),
    pytest.param(
        ("switch", "turn_off", "switch.gaggiuino_display_dark_mode", {}),
        {},
        ("display", {"lcdDarkMode": False}),
        "off",
        id="display_dark_mode",
    ),
]


@pytest.mark.parametrize(("call", "led_start", "change", "new_state"), WRITES)
async def test_settings_write(
    hass: HomeAssistant,
    machine: FakeMachine,
    call: tuple[str, str, str, dict[str, Any]],
    led_start: dict[str, Any],
    change: tuple[str, dict[str, Any]],
    new_state: str,
) -> None:
    """The POST body is the group that was read with one change, and the entity shows it."""
    machine.settings["led"].update(led_start)
    await setup_entry(hass)
    domain, service, entity_id, service_data = call
    group, changed = change
    expected = copy.deepcopy(machine.settings[group]) | changed
    status_reads = len(machine.requests("GET", "system/status"))

    await hass.services.async_call(
        domain, service, {"entity_id": entity_id, **service_data}, blocking=True
    )

    assert machine.requests("POST", f"settings/{group}") == [expected]
    state = hass.states.get(entity_id)
    assert state.state == new_state
    if "rgb_color" in service_data:
        assert state.attributes["rgb_color"] == tuple(service_data["rgb_color"])
    # The new value comes from a read of the group, not from a new poll.
    assert len(machine.requests("GET", "system/status")) == status_reads


async def test_two_led_writes_at_once(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The light and the disco switch write the LED group at once, and no change is lost."""
    await setup_entry(hass)
    original = copy.deepcopy(machine.settings["led"])

    await asyncio.gather(
        hass.services.async_call(
            "light", "turn_on", {"entity_id": "light.gaggiuino_led"}, blocking=True
        ),
        hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": "switch.gaggiuino_led_disco"},
            blocking=True,
        ),
    )

    posts = machine.requests("POST", "settings/led")
    assert len(posts) == 2
    for post in posts:
        # Each write sends the whole group: only the two changed keys can differ.
        assert post | {"state": original["state"], "disco": original["disco"]} == (
            original
        )
    last_post = posts[-1]
    assert last_post["state"] is True
    assert last_post["disco"] is False
    assert hass.states.get("light.gaggiuino_led").state == "on"
    assert hass.states.get("switch.gaggiuino_led_disco").state == "off"


async def test_display_write_keeps_the_other_keys(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The display POST has each key that the machine sent, also a key that the model lacks."""
    machine.settings["display"].update(homeTileLeftTop=7, futureKey="kept")
    await setup_entry(hass)
    before = copy.deepcopy(machine.settings["display"])

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.gaggiuino_display_brightness", "value": 30},
        blocking=True,
    )

    [body] = machine.requests("POST", "settings/display")
    assert body == before | {"lcdBrightness": 30}
    assert body["homeTileLeftTop"] == 7
    assert body["futureKey"] == "kept"


async def test_refused_write_raises(hass: HomeAssistant, machine: FakeMachine) -> None:
    """A write that the machine refuses raises HomeAssistantError and changes no state."""
    await setup_entry(hass)
    machine.refuse_writes = True

    with pytest.raises(HomeAssistantError, match="refused"):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": "number.gaggiuino_steam", "value": 130},
            blocking=True,
        )

    assert hass.states.get("number.gaggiuino_steam").state == "125.0"
