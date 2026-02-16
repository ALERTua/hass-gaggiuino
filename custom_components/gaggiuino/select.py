"""Platform for Gaggiuino select entities."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

if TYPE_CHECKING:
    from gaggiuino_api import GaggiuinoProfile
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
    """Set up the Gaggiuino select entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            GaggiuinoProfileSelect(coordinator),
            GaggiuinoReleaseChannelSelect(coordinator),
        ]
    )


def _get_profile_display_name(profile: GaggiuinoProfile) -> str:
    """Generate a unique display name for a profile."""
    return f"{profile.name} (ID: {profile.id})"


class GaggiuinoProfileSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Gaggiuino profile selector."""

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the selector."""
        super().__init__(coordinator)
        self._attr_name = "Profile"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:coffee"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_profile"
        self._attr_translation_key = "profile"
        self._attr_device_info = coordinator.device_info
        self._profile_map: dict[str, int] = {}  # Maps display names to profile IDs

    def _update_profile_map(self) -> None:
        """Update the mapping of display names to profile IDs."""
        if not (profiles := self.coordinator.profiles):
            self._profile_map = {}
            return

        self._profile_map = {
            _get_profile_display_name(profile): profile.id for profile in profiles
        }

    @property
    def current_option(self) -> str | None:
        """Return the currently selected profile."""
        if self.coordinator.profile is None:
            return None

        profile: GaggiuinoProfile = self.coordinator.profile
        return _get_profile_display_name(profile) if profile else None

    @property
    def options(self) -> list[str]:
        """Return the list of available profiles."""
        if self.coordinator.profiles is None:
            return []

        self._update_profile_map()
        return list(self._profile_map.keys())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._profile_map:
            msg = f"Invalid profile selection: {option}"
            raise ValueError(msg)

        profile_id = self._profile_map[option]
        await self.coordinator.select_profile(profile_id)
        await self.coordinator.async_refresh()


# Release channel options mapping
RELEASE_CHANNEL_OPTIONS = {
    "Stable": 0,
    "Test": 1,
    "Debug": 2,
}


class GaggiuinoReleaseChannelSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Gaggiuino release channel selector."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_options: ClassVar[list[str]] = list(RELEASE_CHANNEL_OPTIONS.keys())

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the selector."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_release_channel"
        self._attr_name = "Release Channel"
        self._attr_has_entity_name = True
        self._attr_translation_key = "release_channel"
        self._attr_icon = "mdi:source-branch"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> str | None:
        """Return the currently selected release channel."""
        if self.coordinator.system_settings is None:
            return None

        channel_value = self.coordinator.system_settings.releaseChannel
        for name, value in RELEASE_CHANNEL_OPTIONS.items():
            if value == channel_value:
                return name
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in RELEASE_CHANNEL_OPTIONS:
            msg = f"Invalid release channel selection: {option}"
            raise ValueError(msg)

        if self.coordinator.system_settings is None:
            return

        new_settings = self.coordinator.system_settings.to_api_dict()
        new_settings["releaseChannel"] = RELEASE_CHANNEL_OPTIONS[option]

        await self.coordinator.update_system_settings(new_settings)
        await self.coordinator.async_request_refresh()
