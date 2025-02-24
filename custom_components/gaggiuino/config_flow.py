"""Config flow for Gaggiuino integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlowResult

from gaggiuino_api import GaggiuinoAPI
from gaggiuino_api.const import DEFAULT_BASE_URL
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from .const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_BASE_URL): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    _LOGGER.debug(f"{DOMAIN} config flow user input: {data=}")
    api = GaggiuinoAPI(base_url=data[CONF_HOST])
    try:
        async with api:
            profiles = await api.get_profiles()
    except Exception as err:
        raise CannotConnect from err
    
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
                info = await validate_input(self.hass, user_input)
                _LOGGER.debug(f"{DOMAIN} config flow async_step_user: {info=}")
                data = {
                    CONF_HOST: user_input[CONF_HOST],
                }
                return self.async_create_entry(title=info["title"], data=data)
            except CannotConnect:
                _LOGGER.exception("CannotConnect exception")
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        if errors:
            _LOGGER.debug(f"{DOMAIN} config flow async_step_user: {errors=}")

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
