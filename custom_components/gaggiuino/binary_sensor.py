"""Platform for sensor integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
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
class GaggiuinoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Gaggiuino binary sensor entities."""

    value_fn: Callable[[GaggiuinoData], bool | None]
    attributes_fn: Callable[[GaggiuinoData], dict[str, Any]] | None = None


AVAILABILITY = BinarySensorEntityDescription(
    key="availability",
    translation_key="availability",
    name="Availability",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
    entity_category=EntityCategory.DIAGNOSTIC,
)

BINARY_SENSORS = [
    GaggiuinoBinarySensorEntityDescription(
        key="health",
        translation_key="health",
        name="Health",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: not data.healthy,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="brew_switch",
        translation_key="brew_switch",
        name="Brew Switch",
        icon="mdi:water-pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.status.brew_switch_state,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="steam_switch",
        translation_key="steam_switch",
        name="Steam Switch",
        icon="mdi:water-pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.status.steam_switch_state,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="brewing",
        translation_key="brewing",
        name="Brewing",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda data: data.status.brew_active,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="steaming",
        translation_key="steaming",
        name="Steaming",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.steam_active,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="hot_water",
        translation_key="hot_water",
        name="Hot Water",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.hot_water_active,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="boiler_heating",
        translation_key="boiler_heating",
        name="Boiler Heating",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.boiler_on,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="scales_present",
        translation_key="scales_present",
        name="Scales",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.scales_present,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="thermocouple_fault",
        translation_key="thermocouple_fault",
        name="Thermocouple Fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.thermocouple_faulted,
        attributes_fn=lambda data: {"reason": data.status.thermocouple_fault_reason},
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="pressure_sensor_fault",
        translation_key="pressure_sensor_fault",
        name="Pressure Sensor Fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.pressure_sensor_faulted,
        attributes_fn=lambda data: {"reason": data.status.pressure_sensor_fault_reason},
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="steam_forgotten_on",
        translation_key="steam_forgotten_on",
        name="Steam Left On",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.steam_forgotten_on,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="brew_valve",
        translation_key="brew_valve",
        name="Brew Valve",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.valve_open,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="steam_valve",
        translation_key="steam_valve",
        name="Steam Valve",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.steam_valve_on,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="valve_b",
        translation_key="valve_b",
        name="Valve B",
        device_class=BinarySensorDeviceClass.OPENING,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.valve_b_open,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="steam_boiler_relay",
        translation_key="steam_boiler_relay",
        name="Steam Boiler Relay",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.steam_boiler_relay_on,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="tare_pending",
        translation_key="tare_pending",
        name="Tare Pending",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.tare_pending,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="tof_ready",
        translation_key="tof_ready",
        name="Water Level Sensor Ready",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.tof_ready,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="startup_finished",
        translation_key="startup_finished",
        name="Startup Finished",
        value_fn=lambda data: data.status.startup_init_finished,
    ),
    GaggiuinoBinarySensorEntityDescription(
        key="brew_switch_active",
        translation_key="brew_switch_active",
        name="Brew Switch Active",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.brew_switch_active,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[BinarySensorEntity] = [
        GaggiuinoAvailabilitySensor(coordinator, AVAILABILITY)
    ]
    entities.extend(
        GaggiuinoBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )

    async_add_entities(entities)


class GaggiuinoBinarySensorBase(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], BinarySensorEntity
):
    """Common setup of the Gaggiuino binary sensors."""

    def __init__(
        self,
        coordinator: GaggiuinoDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_has_entity_name = True
        self._attr_translation_key = description.translation_key
        self._attr_icon = description.icon
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
        self._attr_device_info = coordinator.device_info


class GaggiuinoAvailabilitySensor(GaggiuinoBinarySensorBase):
    """Shows whether the last poll of the machine succeeded."""

    @property
    def available(self) -> bool:
        """Stay available while the machine is off, to show that state."""
        return True

    @property
    def is_on(self) -> bool:
        """Return true if the machine answered the last poll."""
        return self.coordinator.last_update_success


class GaggiuinoBinarySensor(GaggiuinoBinarySensorBase):
    """Representation of a Gaggiuino binary sensor."""

    entity_description: GaggiuinoBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on, None when the machine does not send it."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes, for example the reason of a fault."""
        if (attributes_fn := self.entity_description.attributes_fn) is None:
            return None
        return attributes_fn(self.coordinator.data)
