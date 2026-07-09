"""WebSocket API exposing merged calendar events to the frontend card.

The event payload can get large (many events x several calendars), so it is
served on demand via WebSocket instead of being stuffed into entity
attributes, which keeps the sensor state lightweight and out of the
recorder's way.
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN


@websocket_api.websocket_command(
    {
        vol.Required("type"): "familyboard_planner/get_events",
        vol.Required("config_entry_id"): str,
    }
)
@websocket_api.async_response
async def ws_get_events(hass: HomeAssistant, connection, msg) -> None:
    coordinator = hass.data.get(DOMAIN, {}).get(msg["config_entry_id"])
    if coordinator is None:
        connection.send_error(msg["id"], "not_found", "Unknown Familyboard Planner config entry")
        return
    connection.send_result(msg["id"], coordinator.data)


@websocket_api.websocket_command({vol.Required("type"): "familyboard_planner/list_entries"})
@websocket_api.async_response
async def ws_list_entries(hass: HomeAssistant, connection, msg) -> None:
    entries = [
        {
            "config_entry_id": entry_id,
            "title": coordinator.entry.title,
            "calendars": coordinator.calendars,
        }
        for entry_id, coordinator in hass.data.get(DOMAIN, {}).items()
    ]
    connection.send_result(msg["id"], {"entries": entries})


def async_setup_websocket_api(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_get_events)
    websocket_api.async_register_command(hass, ws_list_entries)
