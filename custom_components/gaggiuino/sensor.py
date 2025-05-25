"""Platform for sensor integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfMass,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .common import get_status_attr

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import GaggiuinoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class GaggiuinoSensorEntityDescription(SensorEntityDescription):
    """Class describing Gaggiuino sensor entities."""

    value_fn: Callable[[Any], Any] | None = None
    attr_name: str | None = None


SENSORS: tuple[GaggiuinoSensorEntityDescription, ...] = (
    GaggiuinoSensorEntityDescription(
        key="uptime",
        translation_key="uptime",
        name="Uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=get_status_attr("upTime"),
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    GaggiuinoSensorEntityDescription(
        key="profile_id",
        translation_key="profile_id",
        name="Profile ID",
        icon="mdi:coffee",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=get_status_attr("profileId"),
    ),
    GaggiuinoSensorEntityDescription(
        key="profile_name",
        translation_key="profile_Name",
        name="Profile Name",
        icon="mdi:coffee",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=get_status_attr("profileName"),
    ),
    GaggiuinoSensorEntityDescription(
        key="latest_shot_id",
        translation_key="latest_shot_id",
        name="Latest Shot ID",
        icon="mdi:coffee",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: coordinator.latest_shot_id,
    ),
    GaggiuinoSensorEntityDescription(
        key="target_temperature",
        translation_key="target_temperature",
        name="Target Temperature",
        icon="mdi:thermometer-high",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_status_attr("targetTemperature"),
        suggested_display_precision=2,
    ),
    GaggiuinoSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        name="Temperature",
        icon="mdi:thermometer-water",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_status_attr("temperature"),
        suggested_display_precision=2,
    ),
    GaggiuinoSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        name="Pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_status_attr("pressure"),
        suggested_display_precision=1,
    ),
    GaggiuinoSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        name="Water Level",
        icon="mdi:car-coolant-level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_status_attr("waterLevel"),
    ),
    GaggiuinoSensorEntityDescription(
        key="weight",
        translation_key="weight",
        name="Weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_status_attr("weight"),
        suggested_display_precision=2,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    from . import DOMAIN

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [GaggiuinoSensor(coordinator, description) for description in SENSORS]

    async_add_entities(entities)


class GaggiuinoSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Gaggiuino sensor."""

    entity_description: GaggiuinoSensorEntityDescription

    def __init__(
        self,
        coordinator: GaggiuinoDataUpdateCoordinator,
        description: GaggiuinoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_has_entity_name = True
        self._attr_translation_key = description.translation_key
        self._attr_icon = description.icon
        self._attr_device_info = coordinator.device_info
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator)
