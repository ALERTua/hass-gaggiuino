"""Data update coordinator for Gaggiuino integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

from gaggiuino_api import (
    GaggiuinoAPI,
    GaggiuinoConnectionError,
    GaggiuinoConnectionTimeoutError,
    GaggiuinoProfile,
    GaggiuinoStatus,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL: Final = timedelta(seconds=30)


class GaggiuinoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Gaggiuino data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api: GaggiuinoAPI = GaggiuinoAPI(base_url=entry.data[CONF_HOST])
        self.entry: ConfigEntry = entry
        self._status: GaggiuinoStatus | None = None
        self._profile: GaggiuinoProfile | None = None
        self._profiles: list[GaggiuinoProfile] | None = None
        self._latest_shot_id: int | None = None
        self.gaggiuino_online = False

    async def _async_update_data(self) -> dict[str, Any] | None:
        """Update data via library."""
        _LOGGER.debug("Gaggiuino _async_update_data")
        try:
            async with self.api:
                self._status = await self.api.get_status()
                self._profiles = await self.api.get_profiles()
                self._profile = self.api.profile
                latest_shot_id_result = await self.api.get_latest_shot_id()
                if latest_shot_id_result is not None:
                    self._latest_shot_id = latest_shot_id_result.lastShotId
                self.gaggiuino_online = True
        except (GaggiuinoConnectionTimeoutError, GaggiuinoConnectionError) as err:
            _LOGGER.debug("Gaggiuino _async_update_data %s", type(err))

            # this sets all entities to unavailable while disconnected
            # self._status = None  # noqa: ERA001
            # self._profiles = None  # noqa: ERA001
            # self._profile = None  # noqa: ERA001
            # self._latest_shot_id = None  # noqa: ERA001

            self.gaggiuino_online = False

            # this sets all entities to unknown
            # raise UpdateFailed(
            #     "GaggiuinoConnectionTimeoutError"
            # ) from err
        except Exception as err:
            self._status = None
            self._profiles = None
            self._profile = None
            self._latest_shot_id = None
            self.gaggiuino_online = False
            _LOGGER.debug("Error on _async_update_data: %s %s", type(err), err)
            raise UpdateFailed(err) from err

        return {
            "status": self._status,
            "profile": self._profile,
            "profiles": self._profiles,
            "latest_shot_id": self._latest_shot_id,
        }

    @property
    def status(self) -> GaggiuinoStatus | None:
        """Return the current status object."""
        return self._status

    @property
    def profile(self) -> GaggiuinoProfile | None:
        """Return the current profile object."""
        return self._profile

    @property
    def profiles(self) -> list[GaggiuinoProfile] | None:
        """Return the available profiles object."""
        return self._profiles

    @property
    def latest_shot_id(self) -> list[GaggiuinoProfile] | None:
        """Return the latest shot id."""
        return self._latest_shot_id

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        return {
            "identifiers": {("gaggiuino", self.config_entry.entry_id)},
            "name": "Gaggiuino",
            "manufacturer": "Gaggiuino",
            "model": "Gaggiuino",
        }

    async def select_profile(self, profile: GaggiuinoProfile | int) -> None:
        """Select a new profile."""
        try:
            async with self.api:
                if await self.api.select_profile(profile):
                    self.data["profile"] = self._profile = self.api.profile  # type: GaggiuinoProfile
                    if self._status is not None:
                        self._status.profileId = self._profile.id
                        self._status.profileName = self._profile.name
                        self.data["status"] = self._status
        except GaggiuinoConnectionTimeoutError:
            _LOGGER.exception("Timeout setting profile")
            return
        except Exception as err:
            _LOGGER.exception("Exception while selecting a profile")
            raise UpdateFailed(err) from err

    async def health_ok(self) -> bool:
        """Return health ok boolean."""
        try:
            async with self.api:
                return await self.api.healthy()
        except Exception as err:
            _LOGGER.debug("Exception while checking health: %s", type(err))
            return False
