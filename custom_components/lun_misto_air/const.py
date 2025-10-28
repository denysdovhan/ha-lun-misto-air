"""Constants for the LUN Misto Air integration."""

from typing import Final

DOMAIN: Final = "lun_misto_air"
NAME: Final = "LUN Misto Air"

# Configuration options
CONF_STATION_NAME: Final = "station_name"
CONF_STATION_TYPE: Final = "station_type"

# Station types
STATION_TYPE_STATIC: Final = "static"
STATION_TYPE_DYNAMIC: Final = "dynamic"

# Subentry types
SUBENTRY_TYPE_STATION: Final = "station"

# Station name format
STATION_NAME_FORMAT: Final = "{city} ({station})"

# Attributes
ATTR_STATION_NAME: Final = "station_name"
ATTR_CITY: Final = "city"
ATTR_UPDATED: Final = "updated"

# Consts
UPDATE_INTERVAL: Final = 10
SUGGESTED_PRECISION: Final = 3
