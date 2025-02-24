"""Platform for Gaggiuino select entities."""
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GaggiuinoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Gaggiuino selects based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GaggiuinoProfileSelect(coordinator)])


class GaggiuinoProfileSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Gaggiuino profile selector."""

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the selector."""
        super().__init__(coordinator)
        self._attr_name = "Profile"
        self._attr_has_entity_name = True
        self._attr_unique_id = "gaggiuino_profile"
        self._attr_translation_key = "profile"

    @property
    def current_option(self) -> str | None:
        """Return the currently selected profile."""
        if self.coordinator.data is None:
            return None

        profile = self.coordinator.data.get("current_profile")
        return profile.name if profile else None

    @property
    def options(self) -> list[str]:
        """Return the list of available profiles."""
        if self.coordinator.data is None:
            return []
        profiles = self.coordinator.data.get("profiles", [])
        return [p.name for p in profiles]

    async def async_select_option(self, option: str) -> None:  # TODO: select by ID
        """Change the selected option."""
        profiles = self.coordinator.data.get("profiles", [])
        selected_profile = next((p for p in profiles if p.name == option), None)
        if not selected_profile:
            raise ValueError(f"Profile {option} not found")

        await self.coordinator.select_profile(selected_profile.id)

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.base_url)},
            "name": "Gaggiuino",
            "manufacturer": "Gaggiuino",
        }
