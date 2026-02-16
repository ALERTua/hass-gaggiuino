"""Platform for Gaggiuino light entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
from homeassistant.const import EntityCategory
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
    """Set up the Gaggiuino light entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GaggiuinoLedLight(coordinator)])


class GaggiuinoLedLight(CoordinatorEntity, LightEntity):
    """Representation of a Gaggiuino LED light."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_led"
        self._attr_name = "LED"
        self._attr_has_entity_name = True
        self._attr_translation_key = "led"
        self._attr_icon = "mdi:led-variant-on"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return True if the light is on."""
        if self.coordinator.led_settings is None:
            return None
        return self.coordinator.led_settings.state

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        # LED doesn't support brightness, just on/off
        return None

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the RGB color of the light."""
        if self.coordinator.led_settings is None:
            return None
        color = self.coordinator.led_settings.color
        return (color.R, color.G, color.B)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if self.coordinator.led_settings is None:
            return

        new_settings = self.coordinator.led_settings.to_api_dict()
        new_settings["state"] = True

        # Handle RGB color if provided
        if "rgb_color" in kwargs:
            r, g, b = kwargs["rgb_color"]
            new_settings["color"] = {"R": r, "G": g, "B": b}

        await self.coordinator.update_led_settings(new_settings)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the light off."""
        if self.coordinator.led_settings is None:
            return

        new_settings = self.coordinator.led_settings.to_api_dict()
        new_settings["state"] = False

        await self.coordinator.update_led_settings(new_settings)
        await self.coordinator.async_request_refresh()
