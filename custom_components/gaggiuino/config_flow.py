"""Config flow for Gaggiuino integration."""

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from gaggiuino_api import (
    DEFAULT_BASE_URL,
    MINIMUM_FIRMWARE,
    GaggiuinoClient,
    GaggiuinoResponseFormatError,
)
from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

_LOGGER = logging.getLogger(__name__)

HTTP_PORT = 80

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL, default=DEFAULT_BASE_URL): str,
    }
)


def _host_of(url: str) -> str | None:
    """Return the host name of a URL in lower case, or None when it has none."""
    try:
        host = URL(url).host
    except ValueError:
        return None
    return host.lower() if host else None


def _entry_title(url: str) -> str:
    """Return the title of the entry of a machine."""
    return f"{DOMAIN} ({url})"


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    _LOGGER.debug("config flow user input data: %s", data)
    client = GaggiuinoClient(data[CONF_URL], session=async_get_clientsession(hass))
    try:
        await client.status()
        await client.profiles.list()
    except GaggiuinoResponseFormatError as err:
        _LOGGER.exception("Unsupported answer on validate_input")
        raise UnsupportedFirmwareError from err
    except Exception as err:
        _LOGGER.exception("Error on validate_input")
        raise CannotConnectError from err

    return {"title": _entry_title(data[CONF_URL])}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gaggiuino."""

    VERSION = 2

    _discovered_host: str
    _discovered_url: str

    def _abort_if_host_has_entry(self, hosts: set[str]) -> None:
        """Abort when an entry has one of the hosts in its URL.

        An entry made before the unique id existed has none, so its URL is the only match.
        """
        for entry in self._async_current_entries(include_ignore=False):
            if _host_of(entry.data.get(CONF_URL, "")) in hosts:
                raise AbortFlow("already_configured")

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except UnsupportedFirmwareError:
                errors["base"] = "unsupported_firmware"
            except CannotConnectError:
                _LOGGER.exception("CannotConnectError")
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                _LOGGER.debug("config flow async_step_user info: %s", info)
                # A second entry of the same host would poll the same machine twice.
                if (host := _host_of(user_input[CONF_URL])) is not None:
                    await self.async_set_unique_id(host, raise_on_progress=False)
                    self._abort_if_unique_id_configured()
                    self._abort_if_host_has_entry({host})
                data = {
                    CONF_URL: user_input[CONF_URL],
                }
                # noinspection PyTypeChecker
                return self.async_create_entry(title=info["title"], data=data)

        if errors:
            _LOGGER.debug("config flow async_step_user errors: %s", errors)

        description_placeholders = {
            "default_url": DEFAULT_BASE_URL,
            "minimum_firmware": MINIMUM_FIRMWARE,
        }
        # noinspection PyTypeChecker
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle the mDNS announcement of a machine."""
        # The announcement has no MAC address, so the host name is the identity.
        # The URL keeps the name and not the IP address, because the IP can change.
        host = discovery_info.hostname.rstrip(".").lower()
        port = discovery_info.port
        url = f"http://{host}" if port in (None, HTTP_PORT) else f"http://{host}:{port}"

        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()
        self._abort_if_host_has_entry({host, *discovery_info.addresses})

        client = GaggiuinoClient(url, session=async_get_clientsession(self.hass))
        try:
            await client.status()
        except GaggiuinoResponseFormatError:
            return self.async_abort(
                reason="unsupported_firmware",
                description_placeholders={"minimum_firmware": MINIMUM_FIRMWARE},
            )
        except Exception:
            _LOGGER.debug("The discovered host %s did not answer", host, exc_info=True)
            return self.async_abort(reason="cannot_connect")

        self._discovered_host = host
        self._discovered_url = url
        self.context["title_placeholders"] = {"host": host}
        self._set_confirm_only()
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask the user to confirm the discovered machine."""
        if user_input is not None:
            # noinspection PyTypeChecker
            return self.async_create_entry(
                title=_entry_title(self._discovered_url),
                data={CONF_URL: self._discovered_url},
            )

        # noinspection PyTypeChecker
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"host": self._discovered_host},
        )


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""


class UnsupportedFirmwareError(HomeAssistantError):
    """Error to indicate that the firmware of the machine is too old."""
