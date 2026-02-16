"""Platform for Gaggiuino switch entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up the Gaggiuino switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            GaggiuinoLedDiscoSwitch(coordinator),
            GaggiuinoForcePredictiveSwitch(coordinator),
            GaggiuinoHwScalesEnabledSwitch(coordinator),
            GaggiuinoBtScalesEnabledSwitch(coordinator),
        ]
    )


class GaggiuinoLedDiscoSwitch(CoordinatorEntity, SwitchEntity):
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
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        if self.coordinator.led_settings is None:
            return None
        return self.coordinator.led_settings.disco

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        if self.coordinator.led_settings is None:
            return

        new_settings = self.coordinator.led_settings.to_api_dict()
        new_settings["disco"] = True

        await self.coordinator.update_led_settings(new_settings)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        if self.coordinator.led_settings is None:
            return

        new_settings = self.coordinator.led_settings.to_api_dict()
        new_settings["disco"] = False

        await self.coordinator.update_led_settings(new_settings)


class GaggiuinoForcePredictiveSwitch(CoordinatorEntity, SwitchEntity):
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
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        if self.coordinator.scales_settings is None:
            return None
        return self.coordinator.scales_settings.forcePredictive

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        if self.coordinator.scales_settings is None:
            return

        new_settings = self.coordinator.scales_settings.to_api_dict()
        new_settings["forcePredictive"] = True

        await self.coordinator.update_scales_settings(new_settings)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        if self.coordinator.scales_settings is None:
            return

        new_settings = self.coordinator.scales_settings.to_api_dict()
        new_settings["forcePredictive"] = False

        await self.coordinator.update_scales_settings(new_settings)


class GaggiuinoHwScalesEnabledSwitch(CoordinatorEntity, SwitchEntity):
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
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        if self.coordinator.scales_settings is None:
            return None
        return self.coordinator.scales_settings.hwScalesEnabled

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        if self.coordinator.scales_settings is None:
            return

        new_settings = self.coordinator.scales_settings.to_api_dict()
        new_settings["hwScalesEnabled"] = True

        await self.coordinator.update_scales_settings(new_settings)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        if self.coordinator.scales_settings is None:
            return

        new_settings = self.coordinator.scales_settings.to_api_dict()
        new_settings["hwScalesEnabled"] = False

        await self.coordinator.update_scales_settings(new_settings)


class GaggiuinoBtScalesEnabledSwitch(CoordinatorEntity, SwitchEntity):
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
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        if self.coordinator.scales_settings is None:
            return None
        return self.coordinator.scales_settings.btScalesEnabled

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the switch on."""
        if self.coordinator.scales_settings is None:
            return

        new_settings = self.coordinator.scales_settings.to_api_dict()
        new_settings["btScalesEnabled"] = True

        await self.coordinator.update_scales_settings(new_settings)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the switch off."""
        if self.coordinator.scales_settings is None:
            return

        new_settings = self.coordinator.scales_settings.to_api_dict()
        new_settings["btScalesEnabled"] = False

        await self.coordinator.update_scales_settings(new_settings)
