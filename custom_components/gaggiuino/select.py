"""Platform for Gaggiuino select entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from gaggiuino_api import GaggiuinoProfile
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import GaggiuinoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino select entities."""
    from . import DOMAIN

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GaggiuinoProfileSelect(coordinator)])


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
        self._profile_map: dict[str, int] = {}  # Maps display names to profile IDs

    def _update_profile_map(self) -> None:
        """Update the mapping of display names to profile IDs."""
        if self.coordinator.data is None:
            self._profile_map = {}
            return

        profiles: list[GaggiuinoProfile] = self.coordinator.data.get("profiles", [])
        self._profile_map = {
            _get_profile_display_name(profile): profile.id for profile in profiles
        }

    @property
    def current_option(self) -> str | None:
        """Return the currently selected profile."""
        if self.coordinator.data is None:
            return None

        profile: GaggiuinoProfile = self.coordinator.data.get("current_profile")
        return _get_profile_display_name(profile) if profile else None

    @property
    def options(self) -> list[str]:
        """Return the list of available profiles."""
        if self.coordinator.data is None:
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

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        return {
            "identifiers": {("gaggiuino", self.coordinator.config_entry.entry_id)},
            "name": "Gaggiuino",
            "manufacturer": "DIY",
            "model": "Gaggiuino",
        }
