"""Each entity keeps its ids and reads its value from the right field of the machine."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import ENTRY_ID, FakeMachine, setup_entry

# The ids of the entities as the integration made them before the move to gaggiuino_api 1.0.
ENTITY_IDS = {
    "sensor.gaggiuino_uptime": f"{ENTRY_ID}_uptime",
    "sensor.gaggiuino_profile_id": f"{ENTRY_ID}_profile_id",
    "sensor.gaggiuino_profile_name": f"{ENTRY_ID}_profile_name",
    "sensor.gaggiuino_latest_shot_id": f"{ENTRY_ID}_latest_shot_id",
    "sensor.gaggiuino_target_temperature": f"{ENTRY_ID}_target_temperature",
    "sensor.gaggiuino_temperature": f"{ENTRY_ID}_temperature",
    "sensor.gaggiuino_pressure": f"{ENTRY_ID}_pressure",
    "sensor.gaggiuino_water_level": f"{ENTRY_ID}_water_level",
    "sensor.gaggiuino_weight": f"{ENTRY_ID}_weight",
    "sensor.gaggiuino_core_version": f"{ENTRY_ID}_core_version",
    "sensor.gaggiuino_frontend_version": f"{ENTRY_ID}_front_version",
    "sensor.gaggiuino_static_version": f"{ENTRY_ID}_static_version",
    "sensor.gaggiuino_firmware_status": f"{ENTRY_ID}_firmware_status",
    "binary_sensor.gaggiuino_availability": f"{ENTRY_ID}_availability",
    "binary_sensor.gaggiuino_health": f"{ENTRY_ID}_health",
    "binary_sensor.gaggiuino_brew_switch": f"{ENTRY_ID}_brew_switch",
    "binary_sensor.gaggiuino_steam_switch": f"{ENTRY_ID}_steam_switch",
    "light.gaggiuino_led": f"{ENTRY_ID}_led",
    "number.gaggiuino_steam": f"{ENTRY_ID}_steam_set_point",
    "select.gaggiuino_profile": f"{ENTRY_ID}_profile",
    "select.gaggiuino_release_channel": f"{ENTRY_ID}_release_channel",
    "switch.gaggiuino_led_disco": f"{ENTRY_ID}_led_disco",
    "switch.gaggiuino_force_predictive_scales": f"{ENTRY_ID}_force_predictive",
    "switch.gaggiuino_hardware_scales": f"{ENTRY_ID}_hw_scales_enabled",
    "switch.gaggiuino_bluetooth_scales": f"{ENTRY_ID}_bt_scales_enabled",
}


async def test_entity_ids_stay(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, machine: FakeMachine
) -> None:
    """The registry holds each old entity with its old entity id and unique id."""
    entry = await setup_entry(hass)

    entries = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

    # The new entities are listed in `test_new_entities.py`.
    assert {
        e.entity_id: e.unique_id for e in entries if e.entity_id in ENTITY_IDS
    } == ENTITY_IDS


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_states_come_from_the_fields(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """Each entity shows the value of its own field of the machine."""
    # Distinct values, so that an entity that reads a neighbour field fails.
    machine.status["brewSwitchState"] = True
    machine.status["weight"] = "18.5"
    machine.settings["versions"]["frontVersion"] = "front01"
    await setup_entry(hass)

    expected = {
        "sensor.gaggiuino_uptime": "13306",
        "sensor.gaggiuino_profile_id": "9",
        "sensor.gaggiuino_profile_name": "_OFF",
        "sensor.gaggiuino_latest_shot_id": "580",
        "sensor.gaggiuino_target_temperature": "15.0",
        "sensor.gaggiuino_temperature": "20.786776",
        "sensor.gaggiuino_pressure": "-0.01887",
        "sensor.gaggiuino_water_level": "100",
        "sensor.gaggiuino_weight": "18.5",
        "sensor.gaggiuino_core_version": "c929939",
        "sensor.gaggiuino_frontend_version": "front01",
        "sensor.gaggiuino_static_version": "1af8db8",
        "sensor.gaggiuino_firmware_status": "IDLE",
        "binary_sensor.gaggiuino_availability": "on",
        "binary_sensor.gaggiuino_health": "off",
        "binary_sensor.gaggiuino_brew_switch": "on",
        "binary_sensor.gaggiuino_steam_switch": "off",
        "light.gaggiuino_led": "off",
        "number.gaggiuino_steam": "125.0",
        "select.gaggiuino_profile": "_OFF (ID: 9)",
        "select.gaggiuino_release_channel": "Stable",
        "switch.gaggiuino_led_disco": "on",
        "switch.gaggiuino_force_predictive_scales": "off",
        "switch.gaggiuino_hardware_scales": "off",
        "switch.gaggiuino_bluetooth_scales": "on",
    }
    assert {entity_id: hass.states.get(entity_id).state for entity_id in expected} == (
        expected
    )


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_firmware_status_attributes(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """The firmware status sensor shows the progress, the type and the enum values."""
    machine.answers["firmware/progress"].update(progress=42, type="F_FS")
    await setup_entry(hass)

    attributes = hass.states.get("sensor.gaggiuino_firmware_status").attributes

    assert attributes["progress"] == 42
    assert attributes["type"] == "F_FS"
    assert attributes["possible_statuses"] == [
        "IDLE",
        "IN_PROGRESS",
        "SUCCESS",
        "ERROR",
        "UNKNOWN",
    ]
    assert attributes["possible_types"] == ["C_FW", "F_FW", "F_FS", "UNKNOWN"]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_light_color(hass: HomeAssistant, machine: FakeMachine) -> None:
    """The LED light shows the color of the machine while it is on."""
    machine.settings["led"]["state"] = True
    await setup_entry(hass)

    assert hass.states.get("light.gaggiuino_led").attributes["rgb_color"] == (9, 0, 9)


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_no_latest_shot(hass: HomeAssistant, machine: FakeMachine) -> None:
    """A machine with no shot gives an unknown latest shot and keeps the other values."""
    machine.answers["shots/latest"] = []
    await setup_entry(hass)

    assert hass.states.get("sensor.gaggiuino_latest_shot_id").state == "unknown"
    assert hass.states.get("sensor.gaggiuino_profile_id").state == "9"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_latest_shot_not_found(hass: HomeAssistant, machine: FakeMachine) -> None:
    """An answer 404 for the latest shot gives an unknown shot id and keeps the other values."""
    machine.missing.add("shots/latest")
    await setup_entry(hass)

    assert hass.states.get("sensor.gaggiuino_latest_shot_id").state == "unknown"
    assert hass.states.get("sensor.gaggiuino_profile_id").state == "9"
    assert hass.states.get("binary_sensor.gaggiuino_availability").state == "on"
