"""Config flow for Gaggiuino integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from gaggiuino_api import GaggiuinoAPI
from gaggiuino_api.const import DEFAULT_BASE_URL
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_BASE_URL): str,
    }
)


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    _LOGGER.debug("config flow user input data: %s", data)
    api = GaggiuinoAPI(base_url=data[CONF_HOST])
    try:
        async with api:
            profiles = await api.get_profiles()
    except Exception as err:
        _LOGGER.exception("Error on validate_input")
        raise CannotConnectError from err

    return {"title": f"{DOMAIN} ({data[CONF_HOST]})", "profiles": profiles}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gaggiuino."""

    VERSION = 1

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
                    CONF_HOST: user_input[CONF_HOST],
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

        # noinspection PyTypeChecker
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""
