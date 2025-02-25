"""Data update coordinator for Gaggiuino integration."""

import logging
from datetime import timedelta
from typing import Any

from gaggiuino_api import GaggiuinoAPI
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GaggiuinoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Gaggiuino data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api: GaggiuinoAPI = GaggiuinoAPI(base_url=entry.data[CONF_HOST])
        self.entry: ConfigEntry = entry
        self.profile_id: int | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with self.api:
                profiles = await self.api.get_profiles()
        except Exception as error:
            raise UpdateFailed(error) from error

        current_profile = None
        if self.profile_id is not None:
            current_profile = next(
                (p for p in profiles if p.id == self.profile_id), None
            )
        return {
            "available": True,
            "profiles": profiles,
            "current_profile": current_profile,
        }

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        return {
            "identifiers": {("gaggiuino", self.config_entry.entry_id)},
            "name": "Gaggiuino",
            "manufacturer": "Gaggiuino",
            "model": "Gaggiuino",
        }

    async def select_profile(self, profile_id: int) -> None:
        """Select a new profile."""
        if profile_id == self.profile_id:
            return

        profiles = self.data.get("profiles", [])
        if not any(p.id == profile_id for p in profiles):
            msg = f"Profile with ID {profile_id} not found"
            raise ValueError(msg)

        try:
            async with self.api:
                await self.api.select_profile(profile_id)
            self.profile_id = profile_id
            await self.async_refresh()
        except Exception as error:
            raise UpdateFailed(error) from error
