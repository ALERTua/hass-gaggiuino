"""Platform for sensor integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
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
class BinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Gaggiuino binary sensor entities."""

    key: str
    name: str
    device_class: BinarySensorDeviceClass | None = None
    entity_category: EntityCategory | None = None
    value_fn: Callable[[Any], bool] | None = None


BINARY_SENSORS = [
    BinarySensorEntityDescription(
        key="availability",
        name="Gaggiuino",
        translation_key="availability",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: coordinator.last_update_success,
    ),
    BinarySensorEntityDescription(
        key="brew_switch",
        name="Brew Switch",
        icon="mdi:water-pump",
        translation_key="brew_switch",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=get_status_attr("brewSwitchState"),
    ),
    BinarySensorEntityDescription(
        key="steam_switch",
        name="Steam Switch",
        icon="mdi:water-pump",
        translation_key="steam_switch",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=get_status_attr("steamSwitchState"),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    from . import DOMAIN

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        GaggiuinoBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    ]

    async_add_entities(entities)


class GaggiuinoBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Gaggiuino binary sensor."""

    _attr_has_entity_name = True
    entity_description: BinarySensorEntityDescription

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
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator) is True
