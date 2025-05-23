"""The Gaggiuino integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from httpx import TimeoutException

from .const import DOMAIN
from .coordinator import GaggiuinoDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gaggiuino from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("Gaggiuino async_config_entry_first_refresh")
    _coordinator = GaggiuinoDataUpdateCoordinator(hass, entry)
    try:
        await _coordinator.async_config_entry_first_refresh()
    except (TimeoutError, TimeoutException) as ex:
        raise ConfigEntryNotReady from ex

    _LOGGER.debug("Gaggiuino async_forward_entry_setups")
    hass.data[DOMAIN][entry.entry_id] = _coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("Gaggiuino async_setup_entry True")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
