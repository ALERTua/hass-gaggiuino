"""Platform for Gaggiuino switch entities."""

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up the Gaggiuino switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            GaggiuinoLedDiscoSwitch(coordinator),
            GaggiuinoForcePredictiveSwitch(coordinator),
            GaggiuinoHwScalesEnabledSwitch(coordinator),
            GaggiuinoBtScalesEnabledSwitch(coordinator),
            GaggiuinoDisplayDarkModeSwitch(coordinator),
        ]
    )


class GaggiuinoLedDiscoSwitch(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SwitchEntity
):
    """Representation of a Gaggiuino LED disco switch."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_led_disco"
        self._attr_name = "LED Disco"
        self._attr_has_entity_name = True
        self._attr_translation_key = "led_disco"
        self._attr_icon = "mdi:led-variant-on"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self.coordinator.data.settings.led.disco

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_update_settings("led", disco=True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_update_settings("led", disco=False)


class GaggiuinoForcePredictiveSwitch(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SwitchEntity
):
    """Representation of a Gaggiuino force predictive switch."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_force_predictive"
        self._attr_name = "Force Predictive Scales"
        self._attr_has_entity_name = True
        self._attr_translation_key = "force_predictive"
        self._attr_icon = "mdi:scale-balance"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self.coordinator.data.settings.scales.force_predictive

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_update_settings("scales", force_predictive=True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_update_settings("scales", force_predictive=False)


class GaggiuinoHwScalesEnabledSwitch(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SwitchEntity
):
    """Representation of a Gaggiuino hardware scales enabled switch."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_hw_scales_enabled"
        self._attr_name = "Hardware Scales"
        self._attr_has_entity_name = True
        self._attr_translation_key = "hw_scales_enabled"
        self._attr_icon = "mdi:scale-bathroom"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self.coordinator.data.settings.scales.hw_scales_enabled

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_update_settings("scales", hw_scales_enabled=True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_update_settings("scales", hw_scales_enabled=False)


class GaggiuinoBtScalesEnabledSwitch(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SwitchEntity
):
    """Representation of a Gaggiuino Bluetooth scales enabled switch."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_bt_scales_enabled"
        self._attr_name = "Bluetooth Scales"
        self._attr_has_entity_name = True
        self._attr_translation_key = "bt_scales_enabled"
        self._attr_icon = "mdi:bluetooth"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self.coordinator.data.settings.scales.bt_scales_enabled

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_update_settings("scales", bt_scales_enabled=True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_update_settings("scales", bt_scales_enabled=False)


class GaggiuinoDisplayDarkModeSwitch(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SwitchEntity
):
    """Representation of the dark mode of the display."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_display_dark_mode"
        self._attr_name = "Display Dark Mode"
        self._attr_has_entity_name = True
        self._attr_translation_key = "display_dark_mode"
        self._attr_icon = "mdi:theme-light-dark"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self.coordinator.data.settings.display.lcd_dark_mode

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.async_update_settings("display", lcd_dark_mode=True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.async_update_settings("display", lcd_dark_mode=False)
