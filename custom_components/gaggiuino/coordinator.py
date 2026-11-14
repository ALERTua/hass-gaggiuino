"""Data update coordinator for Gaggiuino integration."""

import asyncio
import dataclasses
import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final, Literal

from gaggiuino_api import (
    MINIMUM_FIRMWARE,
    FirmwareProgress,
    GaggiuinoClient,
    GaggiuinoError,
    GaggiuinoNotFoundError,
    GaggiuinoResponseFormatError,
    Maintenance,
    ProfileSummary,
    Settings,
    Status,
)
from homeassistant.const import CONF_URL
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL: Final = timedelta(seconds=30)

type SettingsGroupName = Literal["boiler", "system", "led", "scales", "display"]


@dataclass(frozen=True, kw_only=True)
class GaggiuinoData:
    """The state of the machine from one poll."""

    status: Status
    profiles: list[ProfileSummary]
    healthy: bool
    latest_shot_id: int | None
    settings: Settings
    firmware_progress: FirmwareProgress
    maintenance: Maintenance


def unsupported_format_message(err: GaggiuinoResponseFormatError) -> str:
    """Return the text of a poll that got an answer in an unknown format."""
    return (
        "The machine answered in a format that this version of the integration "
        f"does not support. It needs Gaggiuino firmware {MINIMUM_FIRMWARE} or newer. "
        f"{err}"
    )


class GaggiuinoDataUpdateCoordinator(DataUpdateCoordinator[GaggiuinoData]):
    """Class to manage fetching Gaggiuino data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = GaggiuinoClient(
            entry.data[CONF_URL], session=async_get_clientsession(hass)
        )
        self.entry: ConfigEntry = entry
        # Held by the poll and each action: no stale poll overwrites a write, no two writes interleave.
        self._lock = asyncio.Lock()

    async def _async_update_data(self) -> GaggiuinoData:
        """Update data via library."""
        async with self._lock:
            try:
                status = await self.client.status()
                profiles = await self.client.profiles.list()
                healthy = await self.client.healthy()
                latest_shot_id = await self._latest_shot_id()
                settings = await self.client.settings.get()
                firmware_progress = await self.client.firmware.progress()
                maintenance = await self.client.maintenance()
            except GaggiuinoResponseFormatError as err:
                raise UpdateFailed(unsupported_format_message(err)) from err
            except GaggiuinoError as err:
                raise UpdateFailed(str(err)) from err

        self._update_device_card(status)
        return GaggiuinoData(
            status=status,
            profiles=profiles,
            healthy=healthy,
            latest_shot_id=latest_shot_id,
            settings=settings,
            firmware_progress=firmware_progress,
            maintenance=maintenance,
        )

    async def _latest_shot_id(self) -> int | None:
        """Return the id of the latest shot, or None when the machine gives none."""
        try:
            return await self.client.shots.latest_id()
        except (GaggiuinoResponseFormatError, GaggiuinoNotFoundError) as err:
            _LOGGER.debug("No latest shot id: %s", err)
            return None

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        info: dict[str, Any] = {
            "identifiers": {("gaggiuino", self.config_entry.entry_id)},
            "name": "Gaggiuino",
            "manufacturer": "Gaggiuino",
            "model": "Gaggiuino",
        }
        # Without data (the machine was off at setup) the card keeps the generic values.
        if self.data is not None:
            info["sw_version"] = self.data.status.core_version
            info["model"] = self.data.status.core_type
        return info

    def _update_device_card(self, status: Status) -> None:
        """Put the firmware version and the board type of a poll on the device card.

        The entities give the card its values only when they are added. A machine that was
        off at that time, or that got a firmware update later, changes them after it.
        """
        registry = dr.async_get(self.hass)
        entry_id = self.config_entry.entry_id
        # The entry has one device. Before the entities are added it has none.
        for device in dr.async_entries_for_config_entry(registry, entry_id):
            card = (device.sw_version, device.model)
            if card != (status.core_version, status.core_type):
                registry.async_update_device(
                    device.id, sw_version=status.core_version, model=status.core_type
                )

    async def async_select_profile(self, profile_id: int) -> None:
        """Select a profile, then read the profiles and the status that it changes."""
        async with self._lock:
            try:
                await self.client.profiles.select(profile_id)
                profiles = await self.client.profiles.list()
                status = await self.client.status()
            except GaggiuinoError as err:
                raise HomeAssistantError(str(err)) from err
            self.async_set_updated_data(
                dataclasses.replace(self.data, profiles=profiles, status=status)
            )

    async def async_update_settings(
        self, group: SettingsGroupName, **changes: Any
    ) -> None:
        """Write the changes to one settings group, then read that group back."""
        settings_group = getattr(self.client.settings, group)
        async with self._lock:
            try:
                await settings_group.update(**changes)
                fresh = await settings_group.get()
            except GaggiuinoError as err:
                raise HomeAssistantError(str(err)) from err
            settings = dataclasses.replace(self.data.settings, **{group: fresh})
            self.async_set_updated_data(
                dataclasses.replace(self.data, settings=settings)
            )
