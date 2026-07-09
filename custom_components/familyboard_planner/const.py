"""Constants for the Familyboard Planner integration."""

DOMAIN = "familyboard_planner"

CONF_CALENDARS = "calendars"
CONF_ENTITY_ID = "entity_id"
CONF_NAME = "name"
CONF_COLOR = "color"
CONF_PERSON = "person_entity_id"
CONF_DAYS_BEHIND = "days_behind"
CONF_DAYS_AHEAD = "days_ahead"

# Pastel palette in the spirit of a warm family wall-calendar look,
# auto-assigned to newly added calendars so users don't have to pick a
# color right away.
DEFAULT_PALETTE = [
    "#F2A6A0",  # coral
    "#8FC1D4",  # sky blue
    "#F6D186",  # sand yellow
    "#A8D5BA",  # sage green
    "#C9A6E0",  # lavender
    "#F2A65A",  # warm orange
    "#7FB3B0",  # teal
    "#E397C4",  # pink
]

DEFAULT_SCAN_INTERVAL_MINUTES = 15
# Fallback defaults for entries that predate the days_behind/days_ahead
# options, and pre-filled defaults in the config/options flow. 7 days
# behind covers "the current week" without hardcoding a week-start day.
DEFAULT_DAYS_BEHIND = 7
DEFAULT_DAYS_AHEAD = 60

PLATFORMS = ["sensor"]
