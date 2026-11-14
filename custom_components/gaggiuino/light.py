"""Platform for Gaggiuino light entities."""

import logging
from typing import TYPE_CHECKING, Any, ClassVar

from gaggiuino_api import LedColor
from homeassistant.components.light import (
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.const import EntityCategory
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
    """Set up the Gaggiuino light entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GaggiuinoLedLight(coordinator)])


class GaggiuinoLedLight(CoordinatorEntity[GaggiuinoDataUpdateCoordinator], LightEntity):
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
    def is_on(self) -> bool:
        """Return True if the light is on."""
        return self.coordinator.data.settings.led.state

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        # LED doesn't support brightness, just on/off
        return None

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the RGB color of the light."""
        color = self.coordinator.data.settings.led.color
        return (color.r, color.g, color.b)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        changes: dict[str, Any] = {"state": True}
        if ATTR_RGB_COLOR in kwargs:
            r, g, b = kwargs[ATTR_RGB_COLOR]
            changes["color"] = LedColor(r=r, g=g, b=b)

        await self.coordinator.async_update_settings("led", **changes)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the light off."""
        await self.coordinator.async_update_settings("led", state=False)
