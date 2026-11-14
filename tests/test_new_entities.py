"""The entities that read more of the status, the service history and the display settings."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from gaggiuino_api import OperationMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.gaggiuino.const import DOMAIN

from .conftest import ENTRY_ID, FakeMachine, setup_entry
from .test_entities import ENTITY_IDS

TRANSLATIONS = (
    Path(__file__).parents[1] / "custom_components/gaggiuino/translations/en.json"
)

# Entity id -> (key of the unique id, enabled by default).
NEW_ENTITIES = {
    "sensor.gaggiuino_operation_mode": ("operation_mode", True),
    "sensor.gaggiuino_power": ("power", True),
    "sensor.gaggiuino_energy": ("energy", False),
    "sensor.gaggiuino_session_energy": ("session_energy", False),
    "sensor.gaggiuino_pump_flow": ("pump_flow", False),
    "sensor.gaggiuino_weight_flow": ("weight_flow", False),
    "sensor.gaggiuino_warmup_remaining": ("warmup_remaining", True),
    "sensor.gaggiuino_warmup_elapsed": ("warmup_elapsed", False),
    "sensor.gaggiuino_boiler_temperature": ("boiler_temperature", True),
    "sensor.gaggiuino_readiness_state": ("readiness_state", False),
    "sensor.gaggiuino_core_type": ("core_type", False),
    "sensor.gaggiuino_power_line_frequency": ("power_line_frequency", False),
    "sensor.gaggiuino_machine_name": ("machine_name", False),
    "sensor.gaggiuino_last_descale": ("last_descale", True),
    "sensor.gaggiuino_shots_since_descale": ("shots_since_descale", True),
    "sensor.gaggiuino_last_backflush": ("last_backflush", True),
    "sensor.gaggiuino_shots_since_backflush": ("shots_since_backflush", True),
    "binary_sensor.gaggiuino_brewing": ("brewing", True),
    "binary_sensor.gaggiuino_steaming": ("steaming", False),
    "binary_sensor.gaggiuino_hot_water": ("hot_water", False),
    "binary_sensor.gaggiuino_boiler_heating": ("boiler_heating", False),
    "binary_sensor.gaggiuino_scales": ("scales_present", False),
    "binary_sensor.gaggiuino_thermocouple_fault": ("thermocouple_fault", True),
    "binary_sensor.gaggiuino_pressure_sensor_fault": ("pressure_sensor_fault", True),
    "binary_sensor.gaggiuino_steam_left_on": ("steam_forgotten_on", True),
    "binary_sensor.gaggiuino_brew_valve": ("brew_valve", False),
    "binary_sensor.gaggiuino_steam_valve": ("steam_valve", False),
    "binary_sensor.gaggiuino_valve_b": ("valve_b", False),
    "binary_sensor.gaggiuino_steam_boiler_relay": ("steam_boiler_relay", False),
    "binary_sensor.gaggiuino_tare_pending": ("tare_pending", False),
    "binary_sensor.gaggiuino_water_level_sensor_ready": ("tof_ready", False),
    "binary_sensor.gaggiuino_startup_finished": ("startup_finished", True),
    "binary_sensor.gaggiuino_brew_switch_active": ("brew_switch_active", False),
    "number.gaggiuino_display_brightness": ("display_brightness", True),
    "switch.gaggiuino_display_dark_mode": ("display_dark_mode", True),
}

# Binary sensor -> the field of the status that it shows.
BINARY_FIELDS = {
    "binary_sensor.gaggiuino_brewing": "brewActive",
    "binary_sensor.gaggiuino_steaming": "steamActive",
    "binary_sensor.gaggiuino_hot_water": "hotWaterActive",
    "binary_sensor.gaggiuino_boiler_heating": "boilerOn",
    "binary_sensor.gaggiuino_scales": "scalesPresent",
    "binary_sensor.gaggiuino_thermocouple_fault": "thermocoupleFaulted",
    "binary_sensor.gaggiuino_pressure_sensor_fault": "pressureSensorFaulted",
    "binary_sensor.gaggiuino_steam_left_on": "steamForgottenOn",
    "binary_sensor.gaggiuino_brew_valve": "valveOpen",
    "binary_sensor.gaggiuino_steam_valve": "steamValveOn",
    "binary_sensor.gaggiuino_valve_b": "valveBOpen",
    "binary_sensor.gaggiuino_steam_boiler_relay": "steamBoilerRelayOn",
    "binary_sensor.gaggiuino_tare_pending": "tarePending",
    "binary_sensor.gaggiuino_water_level_sensor_ready": "tofReady",
    "binary_sensor.gaggiuino_startup_finished": "startupInitFinished",
    "binary_sensor.gaggiuino_brew_switch_active": "brewSwitchActive",
}


async def test_new_entities_are_registered(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, machine: FakeMachine
) -> None:
    """Each new entity has its own ids, and the registry holds no other entity."""
    entry = await setup_entry(hass)

    entries = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

    new_ids = {
        entity_id: f"{ENTRY_ID}_{key}" for entity_id, (key, _) in NEW_ENTITIES.items()
    }
    assert len(NEW_ENTITIES) == 35
    assert {e.entity_id: e.unique_id for e in entries} == ENTITY_IDS | new_ids
    for entity_id, (_, enabled) in NEW_ENTITIES.items():
        disabled_by = entity_registry.async_get(entity_id).disabled_by
        assert (disabled_by is None) is enabled, entity_id


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_status_sensors_read_their_fields(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """Each sensor shows its own field of the status."""
    # Distinct values, so that a sensor that reads a neighbour field fails.
    machine.status.update(
        operationMode="STEAM",
        livePowerWatts=1234,
        energyWattHours=2000.5,
        sessionEnergyWattHours=33.25,
        pumpFlow=1.5,
        weightFlow=2.5,
        warmupRemainingSeconds=61,
        warmupElapsedSeconds=62,
        boilerTemperature=93.5,
        readinessState=7,
        coreType="TEST-BOARD",
        powerLineFrequency=60,
        machineName="Test Machine",
    )
    await setup_entry(hass)

    expected = {
        "sensor.gaggiuino_operation_mode": "steam",
        "sensor.gaggiuino_power": "1234",
        "sensor.gaggiuino_energy": "2000.5",
        "sensor.gaggiuino_session_energy": "33.25",
        "sensor.gaggiuino_pump_flow": "1.5",
        "sensor.gaggiuino_weight_flow": "2.5",
        "sensor.gaggiuino_warmup_remaining": "61",
        "sensor.gaggiuino_warmup_elapsed": "62",
        "sensor.gaggiuino_boiler_temperature": "93.5",
        "sensor.gaggiuino_readiness_state": "7",
        "sensor.gaggiuino_core_type": "TEST-BOARD",
        "sensor.gaggiuino_power_line_frequency": "60",
        "sensor.gaggiuino_machine_name": "Test Machine",
    }
    assert {entity_id: hass.states.get(entity_id).state for entity_id in expected} == (
        expected
    )


@pytest.mark.parametrize(("entity_id", "field"), BINARY_FIELDS.items())
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_binary_sensor_reads_its_field(
    hass: HomeAssistant, machine: FakeMachine, entity_id: str, field: str
) -> None:
    """With one field on, only the binary sensor of that field is on."""
    machine.status["startupInitFinished"] = False
    machine.status[field] = True
    await setup_entry(hass)

    states = {e: hass.states.get(e).state for e in BINARY_FIELDS}

    assert states == {e: "on" if e == entity_id else "off" for e in BINARY_FIELDS}


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_fault_reason_attribute(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A fault sensor shows the reason of its own fault as the attribute `reason`."""
    machine.status.update(
        thermocoupleFaulted=True,
        thermocoupleFaultReason="open circuit",
        pressureSensorFaultReason="short circuit",
    )
    await setup_entry(hass)

    thermocouple = hass.states.get("binary_sensor.gaggiuino_thermocouple_fault")
    pressure = hass.states.get("binary_sensor.gaggiuino_pressure_sensor_fault")

    assert thermocouple.state == "on"
    assert thermocouple.attributes["reason"] == "open circuit"
    assert pressure.state == "off"
    assert pressure.attributes["reason"] == "short circuit"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_optional_fields_give_unknown(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A field that the machine does not send gives an unknown state, and the rest is fine."""
    for key in (
        "boilerTemperature",
        "brewSwitchActive",
        "steamForgottenOn",
        "readinessState",
        "warmupElapsedSeconds",
        "warmupRemainingSeconds",
    ):
        del machine.status[key]
    await setup_entry(hass)

    unknown = [
        "sensor.gaggiuino_boiler_temperature",
        "binary_sensor.gaggiuino_brew_switch_active",
        "binary_sensor.gaggiuino_steam_left_on",
        "sensor.gaggiuino_readiness_state",
        "sensor.gaggiuino_warmup_elapsed",
        "sensor.gaggiuino_warmup_remaining",
    ]
    assert [hass.states.get(e).state for e in unknown] == ["unknown"] * len(unknown)
    assert hass.states.get("sensor.gaggiuino_power").state == "4"
    assert hass.states.get("sensor.gaggiuino_profile_id").state == "9"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_operation_mode_enum(hass: HomeAssistant, machine: FakeMachine) -> None:
    """The mode is the lower-case value, each mode has a readable text, a new mode is unknown."""
    machine.status["operationMode"] = "BREW_AUTO"
    await setup_entry(hass)

    state = hass.states.get("sensor.gaggiuino_operation_mode")
    texts = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))["entity"]["sensor"][
        "operation_mode"
    ]["state"]

    assert state.state == "brew_auto"
    assert state.attributes["options"] == [m.value.lower() for m in OperationMode]
    assert set(texts) == set(state.attributes["options"])


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_new_operation_mode_is_unknown_mode(
    hass: HomeAssistant, machine: FakeMachine
) -> None:
    """A mode that the library does not know gives the option `unknown`."""
    machine.status["operationMode"] = "SOMETHING_NEW"
    await setup_entry(hass)

    assert hass.states.get("sensor.gaggiuino_operation_mode").state == "unknown"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_maintenance_sensors(hass: HomeAssistant, machine: FakeMachine) -> None:
    """The counters come from the service history, and an epoch gives the right UTC time."""
    machine.answers["maintenance"].update(
        lastDescaleTimestamp=1700000000,
        shotsSinceDescale=21,
        lastBackflushTimestamp=1700003600,
        shotsSinceBackflush=22,
    )
    await setup_entry(hass)

    descale = hass.states.get("sensor.gaggiuino_last_descale")
    backflush = hass.states.get("sensor.gaggiuino_last_backflush")

    assert datetime.fromisoformat(descale.state) == datetime(
        2023, 11, 14, 22, 13, 20, tzinfo=UTC
    )
    assert datetime.fromisoformat(backflush.state) == datetime(
        2023, 11, 14, 23, 13, 20, tzinfo=UTC
    )
    assert hass.states.get("sensor.gaggiuino_shots_since_descale").state == "21"
    assert hass.states.get("sensor.gaggiuino_shots_since_backflush").state == "22"


@pytest.mark.parametrize("epoch", [0, 2**62], ids=["never", "out_of_range"])
@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_timestamp_without_time_is_unknown(
    hass: HomeAssistant, machine: FakeMachine, epoch: int
) -> None:
    """The epoch `0` (never recorded) and a value that no date can hold give unknown."""
    machine.answers["maintenance"].update(
        lastDescaleTimestamp=epoch, lastBackflushTimestamp=epoch
    )
    await setup_entry(hass)

    assert hass.states.get("sensor.gaggiuino_last_descale").state == "unknown"
    assert hass.states.get("sensor.gaggiuino_last_backflush").state == "unknown"
    assert hass.states.get("sensor.gaggiuino_shots_since_descale").state == "11"


async def test_device_card(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry, machine: FakeMachine
) -> None:
    """The device card has the firmware version and the board type of the machine."""
    await setup_entry(hass)

    device = device_registry.async_get_device_by_identifier(
        (DOMAIN, ENTRY_ID), ENTRY_ID
    )

    assert device.sw_version == "c929939"
    assert device.model == "STM32U585-PCB-NCP"


async def test_device_card_while_machine_is_off(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry, machine: FakeMachine
) -> None:
    """Without data the device card keeps the generic model and has no firmware version."""
    machine.online = False
    await setup_entry(hass)

    device = device_registry.async_get_device_by_identifier(
        (DOMAIN, ENTRY_ID), ENTRY_ID
    )

    assert device.sw_version is None
    assert device.model == "Gaggiuino"
