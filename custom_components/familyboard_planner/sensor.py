"""Sensor platform for Familyboard Planner.

Exposes a lightweight entity per planner (event count + calendar metadata)
that the frontend card uses as its anchor: it reads `config_entry_id` from
the attributes and then fetches the full event list on demand via the
WebSocket API in websocket_api.py.
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FamilyboardPlannerCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: FamilyboardPlannerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FamilyboardPlannerSensor(coordinator, entry)])


class FamilyboardPlannerSensor(CoordinatorEntity[FamilyboardPlannerCoordinator], SensorEntity):
    """Represents one planner board (a set of calendars with colors)."""

    _attr_has_entity_name = True
    _attr_name = "Termine"
    _attr_icon = "mdi:calendar-heart"

    def __init__(self, coordinator: FamilyboardPlannerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_events"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Familyboard Planner",
            model="Familienplaner",
        )

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.get("events", []))

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "config_entry_id": self._entry.entry_id,
            "calendars": self.coordinator.data.get("calendars", []),
            "range_start": self.coordinator.data.get("range_start"),
            "range_end": self.coordinator.data.get("range_end"),
        }
