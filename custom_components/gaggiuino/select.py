"""Platform for Gaggiuino select entities."""

import logging
from typing import TYPE_CHECKING, ClassVar

from gaggiuino_api import ProfileSummary, ReleaseChannel
from homeassistant.components.select import SelectEntity
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
    """Set up the Gaggiuino select entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            GaggiuinoProfileSelect(coordinator),
            GaggiuinoReleaseChannelSelect(coordinator),
        ]
    )


def _get_profile_display_name(profile: ProfileSummary) -> str:
    """Generate a unique display name for a profile."""
    return f"{profile.name} (ID: {profile.id})"


class GaggiuinoProfileSelect(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SelectEntity
):
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

    def _profile_map(self) -> dict[str, int]:
        """Map the display name of each profile to its id."""
        if self.coordinator.data is None:
            return {}
        return {
            _get_profile_display_name(profile): profile.id
            for profile in self.coordinator.data.profiles
        }

    @property
    def current_option(self) -> str | None:
        """Return the currently selected profile."""
        for profile in self.coordinator.data.profiles:
            if profile.selected:
                return _get_profile_display_name(profile)
        return None

    @property
    def options(self) -> list[str]:
        """Return the list of available profiles."""
        return list(self._profile_map())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        profile_map = self._profile_map()
        if option not in profile_map:
            msg = f"Invalid profile selection: {option}"
            raise ValueError(msg)

        await self.coordinator.async_select_profile(profile_map[option])


# Release channel options mapping
RELEASE_CHANNEL_OPTIONS = {
    "Stable": ReleaseChannel.STABLE,
    "Test": ReleaseChannel.TEST,
    "Debug": ReleaseChannel.DEBUG,
}


class GaggiuinoReleaseChannelSelect(
    CoordinatorEntity[GaggiuinoDataUpdateCoordinator], SelectEntity
):
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
        channel_value = self.coordinator.data.settings.system.release_channel
        for name, value in RELEASE_CHANNEL_OPTIONS.items():
            if value == channel_value:
                return name
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in RELEASE_CHANNEL_OPTIONS:
            msg = f"Invalid release channel selection: {option}"
            raise ValueError(msg)

        await self.coordinator.async_update_settings(
            "system", release_channel=RELEASE_CHANNEL_OPTIONS[option]
        )
