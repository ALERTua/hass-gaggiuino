"""Data update coordinator for Gaggiuino integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

from gaggiuino_api import (
    GaggiuinoAPI,
    GaggiuinoBoilerSettings,
    GaggiuinoConnectionError,
    GaggiuinoConnectionTimeoutError,
    GaggiuinoLedSettings,
    GaggiuinoProfile,
    GaggiuinoScalesSettings,
    GaggiuinoSettings,
    GaggiuinoStatus,
    GaggiuinoSystemSettings,
    GaggiuinoVersions,
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
        self.healthy: bool = False
        self._latest_shot_id: int | None = None
        self.gaggiuino_online: bool = False
        # Settings data
        self._settings: GaggiuinoSettings | None = None
        self._boiler_settings: GaggiuinoBoilerSettings | None = None
        self._system_settings: GaggiuinoSystemSettings | None = None
        self._led_settings: GaggiuinoLedSettings | None = None
        self._scales_settings: GaggiuinoScalesSettings | None = None
        self._versions: GaggiuinoVersions | None = None
        self._firmware_progress: dict[str, Any] | None = None

    async def _async_update_data(self) -> dict[str, Any] | None:
        """Update data via library."""
        _LOGGER.debug("Gaggiuino _async_update_data")
        try:
            async with self.api:
                self._status = await self.api.get_status()
                self._profiles = await self.api.get_profiles()
                self._profile = self.api.profile
                self.healthy = await self.api.healthy()
                latest_shot_id_result = await self.api.get_latest_shot_id()
                if latest_shot_id_result is not None:
                    self._latest_shot_id = latest_shot_id_result.lastShotId
                # Fetch settings data
                self._settings = await self.api.get_settings()
                if self._settings is not None:
                    self._boiler_settings = self._settings.boiler
                    self._system_settings = self._settings.system
                    self._led_settings = self._settings.led
                    self._scales_settings = self._settings.scales
                    self._versions = self._settings.versions
                # Fetch firmware progress
                self._firmware_progress = await self.api.get_firmware_progress()
                self.gaggiuino_online = True
        except (GaggiuinoConnectionTimeoutError, GaggiuinoConnectionError) as err:
            _LOGGER.debug("Gaggiuino _async_update_data %s", type(err))
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
            self._settings = None
            self._boiler_settings = None
            self._system_settings = None
            self._led_settings = None
            self._scales_settings = None
            self._versions = None
            self._firmware_progress = None
            self.gaggiuino_online = False
            self.healthy = False
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
    def boiler_settings(self) -> GaggiuinoBoilerSettings | None:
        """Return the boiler settings."""
        return self._boiler_settings

    @property
    def system_settings(self) -> GaggiuinoSystemSettings | None:
        """Return the system settings."""
        return self._system_settings

    @property
    def led_settings(self) -> GaggiuinoLedSettings | None:
        """Return the LED settings."""
        return self._led_settings

    @property
    def scales_settings(self) -> GaggiuinoScalesSettings | None:
        """Return the scales settings."""
        return self._scales_settings

    @property
    def versions(self) -> GaggiuinoVersions | None:
        """Return the version information."""
        return self._versions

    @property
    def firmware_progress(self) -> dict[str, Any] | None:
        """Return the firmware progress."""
        return self._firmware_progress

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
                    self._profile = self.api.profile
                    self.data["profile"] = self._profile
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

    async def update_boiler_settings(
        self, settings: GaggiuinoBoilerSettings | dict[str, Any]
    ) -> bool:
        """Update boiler settings."""
        try:
            async with self.api:
                result = await self.api.update_boiler_settings(settings)
                if result:
                    self._boiler_settings = await self.api.get_boiler_settings()
                    self.async_update_listeners()
                return result
        except Exception as err:
            _LOGGER.exception("Exception while updating boiler settings")
            raise UpdateFailed(err) from err

    async def update_system_settings(
        self, settings: GaggiuinoSystemSettings | dict[str, Any]
    ) -> bool:
        """Update system settings."""
        try:
            async with self.api:
                result = await self.api.update_system_settings(settings)
                if result:
                    self._system_settings = await self.api.get_system_settings()
                    self.async_update_listeners()
                return result
        except Exception as err:
            _LOGGER.exception("Exception while updating system settings")
            raise UpdateFailed(err) from err

    async def update_led_settings(
        self, settings: GaggiuinoLedSettings | dict[str, Any]
    ) -> bool:
        """Update LED settings."""
        try:
            async with self.api:
                result = await self.api.update_led_settings(settings)
                if result:
                    self._led_settings = await self.api.get_led_settings()
                    self.async_update_listeners()
                return result
        except Exception as err:
            _LOGGER.exception("Exception while updating LED settings")
            raise UpdateFailed(err) from err

    async def update_scales_settings(
        self, settings: GaggiuinoScalesSettings | dict[str, Any]
    ) -> bool:
        """Update scales settings."""
        try:
            async with self.api:
                result = await self.api.update_scales_settings(settings)
                if result:
                    self._scales_settings = await self.api.get_scales_settings()
                    self.async_update_listeners()
                return result
        except Exception as err:
            _LOGGER.exception("Exception while updating scales settings")
            raise UpdateFailed(err) from err
