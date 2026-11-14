"""The category of an entity decides its section on the device page."""

import pytest
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import FakeMachine, setup_entry

DIAGNOSTIC = [
    "binary_sensor.gaggiuino_boiler_heating",
    "binary_sensor.gaggiuino_hot_water",
    "binary_sensor.gaggiuino_steam_left_on",
    "binary_sensor.gaggiuino_steaming",
    "sensor.gaggiuino_energy",
    "sensor.gaggiuino_last_backflush",
    "sensor.gaggiuino_last_descale",
    "sensor.gaggiuino_power",
    "sensor.gaggiuino_pressure",
    "sensor.gaggiuino_pump_flow",
    "sensor.gaggiuino_session_energy",
    "sensor.gaggiuino_shots_since_backflush",
    "sensor.gaggiuino_shots_since_descale",
    "sensor.gaggiuino_warmup_elapsed",
    "sensor.gaggiuino_weight",
    "sensor.gaggiuino_weight_flow",
]
PRIMARY = [
    "binary_sensor.gaggiuino_brew_switch",
    "binary_sensor.gaggiuino_brew_switch_active",
    "binary_sensor.gaggiuino_brewing",
    "binary_sensor.gaggiuino_scales",
    "binary_sensor.gaggiuino_startup_finished",
    "binary_sensor.gaggiuino_steam_switch",
    "binary_sensor.gaggiuino_steam_valve",
    "sensor.gaggiuino_boiler_temperature",
    "sensor.gaggiuino_operation_mode",
    "sensor.gaggiuino_profile_id",
    "sensor.gaggiuino_profile_name",
    "sensor.gaggiuino_temperature",
]


@pytest.mark.parametrize(
    ("entity_ids", "category"),
    [(DIAGNOSTIC, EntityCategory.DIAGNOSTIC), (PRIMARY, None)],
)
async def test_categories(
    hass: HomeAssistant,
    machine: FakeMachine,
    entity_ids: list[str],
    category: EntityCategory | None,
) -> None:
    """Each entity is in the section that the owner of the integration chose for it."""
    await setup_entry(hass)
    registry = er.async_get(hass)

    for entity_id in entity_ids:
        entry = registry.async_get(entity_id)
        assert entry is not None, entity_id
        assert entry.entity_category is category, entity_id
