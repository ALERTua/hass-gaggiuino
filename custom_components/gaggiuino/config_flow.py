"""Config flow for Gaggiuino integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from gaggiuino_api import GaggiuinoAPI
from gaggiuino_api.const import DEFAULT_BASE_URL
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_URL
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, default=DEFAULT_BASE_URL): str,
    }
)


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    _LOGGER.debug("config flow user input data: %s", data)
    api = GaggiuinoAPI(base_url=data[CONF_URL])
    try:
        async with api:
            await api.get_profiles()
    except Exception as err:
        _LOGGER.exception("Error on validate_input")
        raise CannotConnectError from err

    return {"title": f"{DOMAIN} ({data[CONF_URL]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gaggiuino."""

    VERSION = 2

    async def async_migrate_entry(
        self,
        hass: HomeAssistant,  # noqa: ARG002
        entry: ConfigEntry,
    ) -> ConfigFlowResult:
        """Migrate config entry from version 1 to version 2."""
        if entry.version == 1:
            # Migrate from CONF_HOST ("host") to CONF_URL ("url")
            if CONF_HOST in entry.data:
                _LOGGER.debug("Migrating config entry from host to url")
                new_data = {**entry.data}
                new_data[CONF_URL] = new_data.pop(CONF_HOST)
                return self.async_update_entry(entry, data=new_data, version=2)

            # If already using new format, just update version
            return self.async_update_entry(entry, version=2)

        return entry

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(user_input)
                _LOGGER.debug("config flow async_step_user info: %s", info)
                data = {
                    CONF_URL: user_input[CONF_URL],
                }
                # noinspection PyTypeChecker
                return self.async_create_entry(title=info["title"], data=data)
            except CannotConnectError:
                _LOGGER.exception("CannotConnectError")
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        if errors:
            _LOGGER.debug("config flow async_step_user errors: %s", errors)

        description_placeholders = {"default_url": DEFAULT_BASE_URL}
        # noinspection PyTypeChecker
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders=description_placeholders,
        )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""
