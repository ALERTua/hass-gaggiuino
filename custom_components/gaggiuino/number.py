"""Platform for Gaggiuino number entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

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
    """Set up the Gaggiuino number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GaggiuinoSteamSetPointNumber(coordinator)])


class GaggiuinoSteamSetPointNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Gaggiuino steam set point number entity."""

    _attr_native_min_value = 100.0
    _attr_native_max_value = 165.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_steam_set_point"
        self._attr_name = "Steam"
        self._attr_has_entity_name = True
        self._attr_translation_key = "steam_set_point"
        self._attr_icon = "mdi:thermometer-high"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the current steam set point."""
        if self.coordinator.boiler_settings is None:
            return None
        return float(self.coordinator.boiler_settings.steamSetPoint)

    async def async_set_native_value(self, value: float) -> None:
        """Set the steam set point."""
        if self.coordinator.boiler_settings is None:
            return

        new_settings = self.coordinator.boiler_settings.to_api_dict()
        new_settings["steamSetPoint"] = int(value)

        await self.coordinator.update_boiler_settings(new_settings)
        await self.coordinator.async_request_refresh()
