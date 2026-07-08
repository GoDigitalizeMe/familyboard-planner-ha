"""Config flow for the Daely Planner integration.

Two steps: pick the calendar entities to include, then assign a display
name and color to each of them. The color step builds its schema
dynamically (one name/color field pair per selected calendar), so field
labels can't be pre-translated - a numbered legend is shown in the step
description instead so users can match "Feld 1", "Feld 2", ... to the
calendar it belongs to.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_CALENDARS,
    CONF_COLOR,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_PERSON,
    DEFAULT_PALETTE,
    DOMAIN,
)


def _default_color(index: int) -> str:
    return DEFAULT_PALETTE[index % len(DEFAULT_PALETTE)]


def _hex_to_rgb(hex_color: str) -> list[int]:
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]


def _rgb_to_hex(rgb: list[int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(int(c) for c in rgb))


def _build_color_step_schema(
    hass, entity_ids: list[str], existing: dict[str, dict[str, Any]]
) -> tuple[vol.Schema, str]:
    """Build the dynamic name/color schema and a numbered legend text."""
    fields: dict[Any, Any] = {}
    legend_lines: list[str] = []

    for pos, entity_id in enumerate(entity_ids, start=1):
        state = hass.states.get(entity_id)
        friendly = state.name if state else entity_id
        prior = existing.get(entity_id)
        default_name = prior[CONF_NAME] if prior else friendly
        default_color = prior[CONF_COLOR] if prior else _default_color(pos - 1)

        default_person = prior.get(CONF_PERSON) if prior else None

        fields[vol.Required(f"name_{pos}", default=default_name)] = str
        fields[
            vol.Required(f"color_{pos}", default=_hex_to_rgb(default_color))
        ] = selector.ColorRGBSelector()
        person_key = (
            vol.Optional(f"person_{pos}", default=default_person)
            if default_person
            else vol.Optional(f"person_{pos}")
        )
        fields[person_key] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="person")
        )

        legend_lines.append(f"{pos}. {friendly} ({entity_id})")

    return vol.Schema(fields), "\n".join(legend_lines)


def _collect_calendars(entity_ids: list[str], user_input: dict[str, Any]) -> list[dict[str, Any]]:
    calendars = []
    for pos, entity_id in enumerate(entity_ids, start=1):
        calendars.append(
            {
                CONF_ENTITY_ID: entity_id,
                CONF_NAME: user_input[f"name_{pos}"],
                CONF_COLOR: _rgb_to_hex(user_input[f"color_{pos}"]),
                CONF_PERSON: user_input.get(f"person_{pos}"),
            }
        )
    return calendars


class DaelyPlannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daely Planner."""

    VERSION = 1

    def __init__(self) -> None:
        self._title: str | None = None
        self._entity_ids: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._title = user_input["title"]
            self._entity_ids = user_input[CONF_CALENDARS]
            if not self._entity_ids:
                errors["base"] = "no_calendars"
            else:
                return await self.async_step_colors()

        schema = vol.Schema(
            {
                vol.Required("title", default="Familienplaner"): str,
                vol.Required(CONF_CALENDARS): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar", multiple=True)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_colors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            calendars = _collect_calendars(self._entity_ids, user_input)
            return self.async_create_entry(
                title=self._title or "Daely Planner",
                data={CONF_CALENDARS: calendars},
            )

        schema, legend = _build_color_step_schema(self.hass, self._entity_ids, {})
        return self.async_show_form(
            step_id="colors",
            data_schema=schema,
            description_placeholders={"calendar_list": legend},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DaelyPlannerOptionsFlow:
        return DaelyPlannerOptionsFlow(config_entry)


class DaelyPlannerOptionsFlow(config_entries.OptionsFlow):
    """Allow editing the calendar/color selection of an existing planner."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._entity_ids: list[str] = []
        self._existing: dict[str, dict[str, Any]] = {
            cal[CONF_ENTITY_ID]: cal for cal in config_entry.data.get(CONF_CALENDARS, [])
        }

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._entity_ids = user_input[CONF_CALENDARS]
            if not self._entity_ids:
                errors["base"] = "no_calendars"
            else:
                return await self.async_step_colors()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_CALENDARS, default=list(self._existing)
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="calendar", multiple=True)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)

    async def async_step_colors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            calendars = _collect_calendars(self._entity_ids, user_input)
            new_data = dict(self._config_entry.data)
            new_data[CONF_CALENDARS] = calendars
            self.hass.config_entries.async_update_entry(self._config_entry, data=new_data)
            return self.async_create_entry(title="", data={})

        schema, legend = _build_color_step_schema(self.hass, self._entity_ids, self._existing)
        return self.async_show_form(
            step_id="colors",
            data_schema=schema,
            description_placeholders={"calendar_list": legend},
        )
