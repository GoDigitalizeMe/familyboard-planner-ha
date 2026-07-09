"""Data update coordinator for Daely Planner.

Polls every configured calendar entity via the core `calendar.get_events`
service and merges the results into a single, color-tagged event list that
the frontend card can consume in one shot.
"""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CALENDARS,
    CONF_DAYS_AHEAD,
    CONF_DAYS_BEHIND,
    CONF_ENTITY_ID,
    CONF_PERSON,
    DEFAULT_DAYS_AHEAD,
    DEFAULT_DAYS_BEHIND,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class DaelyPlannerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and merge events from all calendars configured for one planner."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES),
        )
        self.entry = entry

    @property
    def calendars(self) -> list[dict[str, Any]]:
        return self.entry.data.get(CONF_CALENDARS, [])

    def _enriched_calendars(self) -> list[dict[str, Any]]:
        """Calendars enriched with the linked person's name/picture, if any."""
        enriched = []
        for calendar in self.calendars:
            picture = None
            person_name = None
            person_entity_id = calendar.get(CONF_PERSON)
            if person_entity_id:
                person_state = self.hass.states.get(person_entity_id)
                if person_state:
                    picture = person_state.attributes.get("entity_picture")
                    person_name = person_state.name
            enriched.append({**calendar, "picture": picture, "person_name": person_name})
        return enriched

    async def _async_update_data(self) -> dict[str, Any]:
        days_behind = self.entry.data.get(CONF_DAYS_BEHIND, DEFAULT_DAYS_BEHIND)
        days_ahead = self.entry.data.get(CONF_DAYS_AHEAD, DEFAULT_DAYS_AHEAD)
        start = dt_util.start_of_local_day() - timedelta(days=days_behind)
        end = dt_util.start_of_local_day() + timedelta(days=days_ahead)
        events: list[dict[str, Any]] = []
        calendars = self._enriched_calendars()

        for calendar in calendars:
            entity_id = calendar[CONF_ENTITY_ID]
            if self.hass.states.get(entity_id) is None:
                # Silently treating this as "0 events" would mask a startup
                # race (this integration loading before the calendar
                # platform behind entity_id has finished setting up).
                # Raising here makes async_config_entry_first_refresh()
                # turn it into a ConfigEntryNotReady, so Home Assistant
                # retries setup automatically instead of getting stuck
                # showing an empty calendar until something else happens
                # to reload the entry.
                raise UpdateFailed(f"Calendar entity {entity_id} is not (yet) available")

            try:
                response = await self.hass.services.async_call(
                    "calendar",
                    "get_events",
                    {
                        "entity_id": entity_id,
                        "start_date_time": start.isoformat(),
                        "end_date_time": end.isoformat(),
                    },
                    blocking=True,
                    return_response=True,
                )
            except HomeAssistantError as err:
                raise UpdateFailed(f"Error fetching events for {entity_id}: {err}") from err

            calendar_events = (response or {}).get(entity_id, {}).get("events", [])
            _LOGGER.debug(
                "Fetched %d event(s) for %s (%s to %s)", len(calendar_events), entity_id, start, end
            )
            for item in calendar_events:
                item_start = item.get("start", "")
                events.append(
                    {
                        "calendar_entity_id": entity_id,
                        "calendar_name": calendar["name"],
                        "color": calendar["color"],
                        "picture": calendar.get("picture"),
                        "summary": item.get("summary", ""),
                        "description": item.get("description"),
                        "location": item.get("location"),
                        "start": item_start,
                        "end": item.get("end"),
                        "all_day": "T" not in str(item_start),
                    }
                )

        events.sort(key=lambda event: event["start"])

        return {
            "events": events,
            "calendars": calendars,
            "range_start": start.isoformat(),
            "range_end": end.isoformat(),
        }
