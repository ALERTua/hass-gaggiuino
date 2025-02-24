"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    from . import DOMAIN
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    async_add_entities(
        [
            APIAvailabilitySensor(coordinator),
        ]
    )


class APIAvailabilitySensor(SensorEntity):
    """Representation of the Gaggiuino API availability sensor."""
    
    _attr_name = "Gaggiuino API Availability"
    _attr_native_value = "unavailable"
    
    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        
    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            await self.coordinator.api.get_profiles()
            self._attr_native_value = "available"
        except Exception:
            self._attr_native_value = "unavailable"
    pass
