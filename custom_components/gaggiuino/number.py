"""Platform for Gaggiuino number entities."""

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GaggiuinoDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            GaggiuinoSteamSetPointNumber(coordinator),
            GaggiuinoDisplayBrightnessNumber(coordinator),
        ]
    )


class GaggiuinoSteamSetPointNumber(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], NumberEntity
):
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
    def native_value(self) -> float:
        """Return the current steam set point."""
        return float(self.coordinator.data.settings.boiler.steam_set_point)

    async def async_set_native_value(self, value: float) -> None:
        """Set the steam set point."""
        await self.coordinator.async_update_settings(
            "boiler", steam_set_point=int(value)
        )


class GaggiuinoDisplayBrightnessNumber(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], NumberEntity
):
    """Representation of the display brightness of the machine."""

    _attr_native_min_value = 0.0
    _attr_native_max_value = 100.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_display_brightness"
        self._attr_name = "Display Brightness"
        self._attr_has_entity_name = True
        self._attr_translation_key = "display_brightness"
        self._attr_icon = "mdi:brightness-6"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float:
        """Return the current brightness of the display."""
        return float(self.coordinator.data.settings.display.lcd_brightness)

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness of the display."""
        await self.coordinator.async_update_settings(
            "display", lcd_brightness=int(value)
        )
