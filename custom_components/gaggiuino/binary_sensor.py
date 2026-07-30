"""Platform for sensor integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .common import get_status_attr
from .const import (
    DOMAIN,
    READY_STABILISATION_SECONDS,
    READY_TEMP_TOLERANCE_C,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import GaggiuinoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Gaggiuino binary sensor entities."""

    key: str
    name: str
    device_class: BinarySensorDeviceClass | None = None
    entity_category: EntityCategory | None = None
    value_fn: Callable[[Any], bool] | None = None


BINARY_SENSORS = [
    BinarySensorEntityDescription(
        key="availability",
        translation_key="availability",
        name="Availability",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: coordinator.gaggiuino_online,
    ),
    BinarySensorEntityDescription(
        key="health",
        translation_key="health",
        name="Health",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: not coordinator.healthy,
    ),
    BinarySensorEntityDescription(
        key="brew_switch",
        translation_key="brew_switch",
        name="Brew Switch",
        icon="mdi:water-pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=get_status_attr("brewSwitchState"),
    ),
    BinarySensorEntityDescription(
        key="steam_switch",
        translation_key="steam_switch",
        name="Steam Switch",
        icon="mdi:water-pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=get_status_attr("steamSwitchState"),
    ),
]


def _temperature_in_range(coordinator: GaggiuinoDataUpdateCoordinator) -> bool:
    """Return True if current temperature is within tolerance of target."""
    temp = get_status_attr("temperature")(coordinator)
    target = get_status_attr("targetTemperature")(coordinator)
    if temp is None or target is None:
        return False
    try:
        return abs(float(temp) - float(target)) <= READY_TEMP_TOLERANCE_C
    except (TypeError, ValueError):
        return False


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Gaggiuino sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities: list[BinarySensorEntity] = [
        GaggiuinoBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    ]
    entities.append(GaggiuinoReadyToBrewBinarySensor(coordinator))

    async_add_entities(entities)


class GaggiuinoBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Gaggiuino binary sensor."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: GaggiuinoDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_has_entity_name = True
        self._attr_translation_key = description.translation_key
        self._attr_icon = description.icon
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator) is True


class GaggiuinoReadyToBrewBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Machine online and temperature stable for the stabilisation period."""

    def __init__(self, coordinator: GaggiuinoDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_ready_to_brew"
        self._attr_name = "Ready to Brew"
        self._attr_has_entity_name = True
        self._attr_translation_key = "ready_to_brew"
        self._attr_icon = "mdi:coffee-maker-check"
        self._attr_device_info = coordinator.device_info
        self._attr_is_on = False

        self._stable_since: datetime | None = None
        self._unsub_ready: Callable[[], None] | None = None
        self._hold_duration = timedelta(seconds=READY_STABILISATION_SECONDS)

    async def async_added_to_hass(self) -> None:
        """Run initial evaluation when entity is added."""
        await super().async_added_to_hass()
        self._evaluate()

    async def async_will_remove_from_hass(self) -> None:
        """Cancel scheduled timer when entity is removed."""
        self._reset_stabilisation()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Re-evaluate when coordinator data changes."""
        self._evaluate()
        super()._handle_coordinator_update()

    @callback
    def _async_ready_fired(self, _now: datetime) -> None:
        """Handle stabilisation timer completion."""
        self._unsub_ready = None
        self._evaluate()

    def _reset_stabilisation(self) -> None:
        """Clear stabilisation tracking and cancel pending timer."""
        self._stable_since = None
        if self._unsub_ready is not None:
            self._unsub_ready()
            self._unsub_ready = None

    def _schedule_ready_at(self, when: datetime) -> None:
        """Schedule a one-shot callback when stabilisation period ends."""
        if self._unsub_ready is not None:
            self._unsub_ready()
        self._unsub_ready = async_track_point_in_time(
            self.hass, self._async_ready_fired, when
        )

    def _set_off(self) -> bool:
        """Turn sensor off and reset stabilisation. Returns True if state changed."""
        self._reset_stabilisation()
        if self._attr_is_on:
            self._attr_is_on = False
            return True
        return False

    def _evaluate(self) -> None:
        """Update ready state from connectivity and temperature stability."""
        changed = False

        if not self.coordinator.gaggiuino_online or not _temperature_in_range(
            self.coordinator
        ):
            changed = self._set_off()
        else:
            now = dt_util.utcnow()
            if self._stable_since is None:
                self._stable_since = now
                self._schedule_ready_at(now + self._hold_duration)
            elif (now - self._stable_since) >= self._hold_duration:
                if not self._attr_is_on:
                    self._attr_is_on = True
                    changed = True

        if changed:
            self.async_write_ha_state()
