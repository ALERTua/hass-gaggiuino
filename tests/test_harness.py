"""The test base works: Home Assistant starts and finds the integration."""

from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from custom_components.gaggiuino.const import DOMAIN


async def test_home_assistant_finds_the_integration(hass: HomeAssistant) -> None:
    """The loader reads the manifest of the integration under test."""
    integration = await async_get_integration(hass, DOMAIN)

    assert integration.domain == DOMAIN
