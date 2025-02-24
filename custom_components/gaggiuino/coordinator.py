"""Data update coordinator for Gaggiuino integration."""
from datetime import timedelta
import logging
from typing import Any

from gaggiuino_api import GaggiuinoAPI

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_PROFILE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class GaggiuinoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Gaggiuino data."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = GaggiuinoAPI(base_url=entry.data[CONF_HOST])
        self.profile_id = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with self.api:
                profiles = await self.api.get_profiles()
            current_profile = None
            if self.profile_id is not None:
                current_profile = next((p for p in profiles if p.id == self.profile_id), None)
            data = {
                "available": True,
                "profiles": profiles,
                "current_profile": current_profile
            }
            return data
        except Exception as error:
            raise UpdateFailed(error) from error

    async def select_profile(self, profile_id: int) -> None:
        """Select a new profile."""
        if profile_id == self.profile_id:
            return

        profiles = self.data.get("profiles", [])
        if not any(p.id == profile_id for p in profiles):
            raise ValueError(f"Profile with ID {profile_id} not found")

        try:
            async with self.api:
                await self.api.select_profile(profile_id)
            self.profile_id = profile_id
            await self.async_refresh()
        except Exception as error:
            raise UpdateFailed(error) from error
