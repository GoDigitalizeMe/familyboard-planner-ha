"""Constants for the Daely Planner integration."""

DOMAIN = "daely_planner"

CONF_CALENDARS = "calendars"
CONF_ENTITY_ID = "entity_id"
CONF_NAME = "name"
CONF_COLOR = "color"
CONF_PERSON = "person_entity_id"

# Pastel palette in the spirit of the Daely family calendar, auto-assigned
# to newly added calendars so users don't have to pick a color right away.
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
DEFAULT_DAYS_AHEAD = 14

PLATFORMS = ["sensor"]
