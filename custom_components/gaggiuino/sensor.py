"""Platform for sensor integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from gaggiuino_api import FirmwareStatus, FirmwareType, OperationMode
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfMass,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GaggiuinoData, GaggiuinoDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class GaggiuinoSensorEntityDescription(SensorEntityDescription):
    """Class describing Gaggiuino sensor entities."""

    value_fn: Callable[[GaggiuinoData], str | int | float | datetime | None]


def _epoch_to_datetime(seconds: int) -> datetime | None:
    """Return the UTC time of epoch seconds. `0` means never recorded: give None."""
    if seconds == 0:
        return None
    try:
        return datetime.fromtimestamp(seconds, tz=UTC)
    except OverflowError, OSError, ValueError:
        return None


SENSORS: tuple[GaggiuinoSensorEntityDescription, ...] = (
    GaggiuinoSensorEntityDescription(
        key="uptime",
        translation_key="uptime",
        name="Uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.status.up_time,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    GaggiuinoSensorEntityDescription(
        key="profile_id",
        translation_key="profile_id",
        name="Profile ID",
        icon="mdi:coffee",
        value_fn=lambda data: data.status.profile_id,
    ),
    GaggiuinoSensorEntityDescription(
        key="profile_name",
        translation_key="profile_name",
        name="Profile Name",
        icon="mdi:coffee",
        value_fn=lambda data: data.status.profile_name,
    ),
    GaggiuinoSensorEntityDescription(
        key="latest_shot_id",
        translation_key="latest_shot_id",
        name="Latest Shot ID",
        icon="mdi:coffee",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.latest_shot_id,
    ),
    GaggiuinoSensorEntityDescription(
        key="target_temperature",
        translation_key="target_temperature",
        name="Target Temperature",
        icon="mdi:thermometer-high",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.target_temperature,
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
        value_fn=lambda data: data.status.temperature,
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
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.pressure,
        suggested_display_precision=1,
    ),
    GaggiuinoSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        name="Water Level",
        icon="mdi:car-coolant-level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.water_level,
    ),
    GaggiuinoSensorEntityDescription(
        key="weight",
        translation_key="weight",
        name="Weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.weight,
        suggested_display_precision=2,
    ),
    # Version sensors (diagnostic)
    GaggiuinoSensorEntityDescription(
        key="core_version",
        translation_key="core_version",
        name="Core Version",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.settings.versions.core_version,
    ),
    GaggiuinoSensorEntityDescription(
        key="front_version",
        translation_key="front_version",
        name="Frontend Version",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.settings.versions.front_version,
    ),
    GaggiuinoSensorEntityDescription(
        key="static_version",
        translation_key="static_version",
        name="Static Version",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.settings.versions.static_version,
    ),
    # Live status
    GaggiuinoSensorEntityDescription(
        key="operation_mode",
        translation_key="operation_mode",
        name="Operation Mode",
        device_class=SensorDeviceClass.ENUM,
        options=[mode.value.lower() for mode in OperationMode],
        value_fn=lambda data: data.status.operation_mode.value.lower(),
    ),
    GaggiuinoSensorEntityDescription(
        key="power",
        translation_key="power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.live_power_watts,
    ),
    GaggiuinoSensorEntityDescription(
        key="energy",
        translation_key="energy",
        name="Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.energy_watt_hours,
        suggested_display_precision=1,
    ),
    GaggiuinoSensorEntityDescription(
        key="session_energy",
        translation_key="session_energy",
        name="Session Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.session_energy_watt_hours,
        suggested_display_precision=1,
    ),
    GaggiuinoSensorEntityDescription(
        key="pump_flow",
        translation_key="pump_flow",
        name="Pump Flow",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.MILLILITERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.pump_flow,
        suggested_display_precision=2,
    ),
    GaggiuinoSensorEntityDescription(
        key="weight_flow",
        translation_key="weight_flow",
        name="Weight Flow",
        native_unit_of_measurement="g/s",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.weight_flow,
        suggested_display_precision=2,
    ),
    GaggiuinoSensorEntityDescription(
        key="warmup_remaining",
        translation_key="warmup_remaining",
        name="Warmup Remaining",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda data: data.status.warmup_remaining_seconds,
    ),
    GaggiuinoSensorEntityDescription(
        key="warmup_elapsed",
        translation_key="warmup_elapsed",
        name="Warmup Elapsed",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.warmup_elapsed_seconds,
    ),
    GaggiuinoSensorEntityDescription(
        key="boiler_temperature",
        translation_key="boiler_temperature",
        name="Boiler Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.boiler_temperature,
        suggested_display_precision=2,
    ),
    GaggiuinoSensorEntityDescription(
        key="readiness_state",
        translation_key="readiness_state",
        name="Readiness State",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.readiness_state,
    ),
    GaggiuinoSensorEntityDescription(
        key="core_type",
        translation_key="core_type",
        name="Core Type",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.core_type,
    ),
    GaggiuinoSensorEntityDescription(
        key="power_line_frequency",
        translation_key="power_line_frequency",
        name="Power Line Frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.power_line_frequency,
    ),
    GaggiuinoSensorEntityDescription(
        key="machine_name",
        translation_key="machine_name",
        name="Machine Name",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.machine_name,
    ),
    # Service history
    GaggiuinoSensorEntityDescription(
        key="last_descale",
        translation_key="last_descale",
        name="Last Descale",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _epoch_to_datetime(
            data.maintenance.last_descale_timestamp
        ),
    ),
    GaggiuinoSensorEntityDescription(
        key="shots_since_descale",
        translation_key="shots_since_descale",
        name="Shots Since Descale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.maintenance.shots_since_descale,
    ),
    GaggiuinoSensorEntityDescription(
        key="last_backflush",
        translation_key="last_backflush",
        name="Last Backflush",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _epoch_to_datetime(
            data.maintenance.last_backflush_timestamp
        ),
    ),
    GaggiuinoSensorEntityDescription(
        key="shots_since_backflush",
        translation_key="shots_since_backflush",
        name="Shots Since Backflush",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.maintenance.shots_since_backflush,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[SensorEntity] = [
        GaggiuinoSensor(coordinator, description) for description in SENSORS
    ]
    entities.append(GaggiuinoFirmwareStatusSensor(coordinator))

    async_add_entities(entities)


class GaggiuinoSensor(CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SensorEntity):
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
    def native_value(self) -> str | int | float | datetime | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)


class GaggiuinoFirmwareStatusSensor(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SensorEntity
):
    """Representation of a Gaggiuino firmware status sensor."""

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_firmware_status"
        self._attr_name = "Firmware Status"
        self._attr_has_entity_name = True
        self._attr_translation_key = "firmware_status"
        self._attr_icon = "mdi:update"
        self._attr_device_info = coordinator.device_info
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.coordinator.data.firmware_progress.status.value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        progress = self.coordinator.data.firmware_progress
        return {
            "progress": progress.progress,
            "type": progress.type.value,
            "possible_statuses": [status.value for status in FirmwareStatus],
            "possible_types": [firmware_type.value for firmware_type in FirmwareType],
        }
