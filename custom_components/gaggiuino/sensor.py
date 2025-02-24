"""Platform for sensor integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import GaggiuinoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    from . import DOMAIN

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([APIAvailabilitySensor(coordinator)])


class APIAvailabilitySensor(CoordinatorEntity, SensorEntity):
    """Representation of the Gaggiuino API availability sensor."""

    _attr_name = "Gaggiuino API Availability"
    _attr_native_value = "unavailable"
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_api_availability"

    @property
    def native_value(self) -> str:
        """Return the availability state."""
        return "available" if self.coordinator.last_update_success else "unavailable"
