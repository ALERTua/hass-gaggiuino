"""End-to-end tests of the integration in Home Assistant against a real machine.

The tests are deselected by default. Run them with `uv run pytest -m e2e tests/e2e`.
Each test that changes the machine reads the raw state first and restores it in a `finally`
block, also when an assert fails. A write goes only to the `led` and `display` settings
groups and to the profile select.
"""

import asyncio
from typing import Any

import pytest
from gaggiuino_api import GaggiuinoClient
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .e2e_support import RawMachine, is_selected, wait_until

pytestmark = pytest.mark.e2e

LED = "light.gaggiuino_led"
LED_DISCO = "switch.gaggiuino_led_disco"
DISPLAY_BRIGHTNESS = "number.gaggiuino_display_brightness"
DISPLAY_DARK_MODE = "switch.gaggiuino_display_dark_mode"
PROFILE = "select.gaggiuino_profile"

# The temperature can move between the poll at setup and the direct read, in °C.
TEMPERATURE_TOLERANCE = 1.0


def on_off(value: bool) -> str:
    """Return the state of a light or a switch for `value`."""
    return STATE_ON if value else STATE_OFF


def state_of(hass: HomeAssistant, entity_id: str) -> str:
    """Return the state of an entity that must exist."""
    state = hass.states.get(entity_id)
    assert state is not None, entity_id
    return state.state


async def call(hass: HomeAssistant, domain: str, service: str, **data: Any) -> None:
    """Call a service of Home Assistant and wait until it ends."""
    await hass.services.async_call(domain, service, data, blocking=True)


async def test_setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """The entry loads, the machine is available, and no enabled entity is unavailable."""
    assert state_of(hass, "binary_sensor.gaggiuino_availability") == STATE_ON
    registry = er.async_get(hass)
    enabled = [
        e.entity_id
        for e in er.async_entries_for_config_entry(registry, entry.entry_id)
        if not e.disabled
    ]
    assert enabled
    unavailable = [e for e in enabled if state_of(hass, e) == STATE_UNAVAILABLE]
    assert unavailable == []


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "entry")
async def test_values_match_the_machine(
    hass: HomeAssistant, client: GaggiuinoClient
) -> None:
    """The entities show what a direct read of the machine gives."""
    status = await client.status()
    settings = await client.settings.get()

    assert state_of(hass, "sensor.gaggiuino_profile_id") == str(status.profile_id)
    assert state_of(hass, "sensor.gaggiuino_profile_name") == status.profile_name
    assert state_of(hass, "sensor.gaggiuino_water_level") == str(status.water_level)
    assert (
        state_of(hass, "sensor.gaggiuino_operation_mode")
        == status.operation_mode.value.lower()
    )
    assert (
        state_of(hass, "sensor.gaggiuino_core_version")
        == settings.versions.core_version
    )
    assert float(state_of(hass, DISPLAY_BRIGHTNESS)) == settings.display.lcd_brightness
    assert state_of(hass, LED) == on_off(settings.led.state)
    temperature = float(state_of(hass, "sensor.gaggiuino_temperature"))
    assert abs(temperature - status.temperature) <= TEMPERATURE_TOLERANCE


@pytest.mark.usefixtures("entry", "idle_machine")
async def test_led_light(hass: HomeAssistant, raw: RawMachine) -> None:
    """On, a color and off each reach the raw LED group, and the other keys stay."""
    original = await raw.get("settings/led")
    color = {key: 255 - original["color"][key] for key in ("R", "G", "B")}
    steps = [
        ("turn_on", {}, {"state": True}),
        (
            "turn_on",
            {"rgb_color": [color["R"], color["G"], color["B"]]},
            {"color": {**original["color"], **color}},
        ),
        ("turn_off", {}, {"state": False}),
    ]
    expected = dict(original)
    try:
        for service, data, change in steps:
            await call(hass, "light", service, entity_id=LED, **data)
            expected |= change
            assert await raw.wait_for_group("led", expected), service
            assert state_of(hass, LED) == on_off(expected["state"])
            if "color" in change:
                rgb = hass.states.get(LED).attributes["rgb_color"]
                assert rgb == (color["R"], color["G"], color["B"])
    finally:
        await raw.restore_group("led", original)


@pytest.mark.parametrize(
    ("group", "entity_id", "key"),
    [
        pytest.param("led", LED_DISCO, "disco", id="led_disco"),
        pytest.param("display", DISPLAY_DARK_MODE, "lcdDarkMode", id="dark_mode"),
    ],
)
@pytest.mark.usefixtures("entry", "idle_machine")
async def test_switch(
    hass: HomeAssistant, raw: RawMachine, group: str, entity_id: str, key: str
) -> None:
    """A switch flips one key of its raw group, and the other keys stay."""
    original = await raw.get(f"settings/{group}")
    new = not original[key]
    try:
        await call(
            hass, "switch", "turn_on" if new else "turn_off", entity_id=entity_id
        )
        assert await raw.wait_for_group(group, {**original, key: new})
        assert state_of(hass, entity_id) == on_off(new)
    finally:
        await raw.restore_group(group, original)


@pytest.mark.usefixtures("entry", "idle_machine")
async def test_display_brightness(hass: HomeAssistant, raw: RawMachine) -> None:
    """One step of the brightness reaches the raw display group, and the other keys stay."""
    original = await raw.get("settings/display")
    brightness = original["lcdBrightness"]
    new = brightness - 1 if brightness > 0 else brightness + 1
    try:
        await call(hass, "number", "set_value", entity_id=DISPLAY_BRIGHTNESS, value=new)
        assert await raw.wait_for_group("display", {**original, "lcdBrightness": new})
        assert float(state_of(hass, DISPLAY_BRIGHTNESS)) == new
    finally:
        await raw.restore_group("display", original)


@pytest.mark.usefixtures("entry", "idle_machine")
async def test_two_led_writes_at_once(hass: HomeAssistant, raw: RawMachine) -> None:
    """The light and the disco switch write the LED group at once, and the machine has both."""
    original = await raw.get("settings/led")
    light_on = not original["state"]
    disco = not original["disco"]
    try:
        await asyncio.gather(
            call(hass, "light", "turn_on" if light_on else "turn_off", entity_id=LED),
            call(
                hass, "switch", "turn_on" if disco else "turn_off", entity_id=LED_DISCO
            ),
        )
        expected = {**original, "state": light_on, "disco": disco}
        assert await raw.wait_for_group("led", expected)
        assert state_of(hass, LED) == on_off(light_on)
        assert state_of(hass, LED_DISCO) == on_off(disco)
    finally:
        await raw.restore_group("led", original)


@pytest.mark.usefixtures("entry", "idle_machine")
async def test_profile_select(hass: HomeAssistant, client: GaggiuinoClient) -> None:
    """The select goes to another saved profile and back, and the machine follows."""
    profiles = await client.profiles.list()
    [selected] = [p for p in profiles if p.selected]
    others = [p for p in profiles if not p.selected]
    if not others:
        pytest.skip("The machine needs at least two saved profiles")
    try:
        for profile in (others[0], selected):
            option = f"{profile.name} (ID: {profile.id})"
            await call(
                hass, "select", "select_option", entity_id=PROFILE, option=option
            )
            assert await wait_until(lambda pid=profile.id: is_selected(client, pid))
            assert state_of(hass, PROFILE) == option
            assert state_of(hass, "sensor.gaggiuino_profile_id") == str(profile.id)
    finally:
        if not await is_selected(client, selected.id):
            await client.profiles.select(selected.id)
            assert await wait_until(lambda: is_selected(client, selected.id))
