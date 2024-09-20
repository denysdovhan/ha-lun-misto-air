"""Config flow for LUN Misto Air integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_METHOD,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    LocationSelector,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)
from homeassistant.util import location

from .api import LUNMistoAirApi, LUNMistoAirStation
from .const import CONF_STATION, DOMAIN, NAME

LOGGER = logging.getLogger(__name__)

STEP_MAP = "map"
STEP_STATION_NAME = "station_name"


def distance_to_station(lat: float, lon: float, station: LUNMistoAirStation) -> float:
    """Return the distance to a station or infinity if the distance is None."""
    distance = location.distance(lat, lon, station.latitude, station.longitude)
    return distance if distance is not None else float("inf")


def get_stations_options(stations: list[LUNMistoAirStation]) -> list[SelectOptionDict]:
    """Return a list of options for the stations."""
    stations_by_city = sorted(stations, key=lambda station: station.city)
    return [
        SelectOptionDict(
            label=f"{station.city.capitalize()} ({station.name})",
            value=station.name,
        )
        for station in stations_by_city
    ]


class LUNMistoAirOptionsFlow(OptionsFlow):
    """Handle options flow for the LUN Misto Air integration."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.api = LUNMistoAirApi(session=async_get_clientsession(self.hass))

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the station flow."""
        if user_input is not None:
            LOGGER.debug("Updating options: %s", user_input)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_STATION: user_input[CONF_STATION],
                },
            )
            return self.async_create_entry(
                title=self.config_entry.title,
                data={
                    CONF_STATION: user_input[CONF_STATION],
                },
            )

        stations = await self.api.get_all_stations()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STATION,
                        default=self.config_entry.data[CONF_STATION],
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=get_stations_options(stations),
                            translation_key="city",
                        ),
                    ),
                },
            ),
        )


class LUNMistoAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for LUN Misto Air integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self.api = LUNMistoAirApi(session=async_get_clientsession(self.hass))
        self.data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LUNMistoAirOptionsFlow:
        """Get the options flow."""
        return LUNMistoAirOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            if user_input[CONF_METHOD] == STEP_MAP:
                return await self.async_step_map()
            return await self.async_step_station_name()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_METHOD): SelectSelector(
                        SelectSelectorConfig(
                            options=[STEP_MAP, STEP_STATION_NAME],
                            translation_key="method",
                        ),
                    ),
                },
            ),
        )

    async def async_step_map(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            LOGGER.debug("User data: %s", user_input)

            stations = await self.api.get_all_stations()
            if len(stations) == 0:
                errors["base"] = "no_stations"

            # Find the closest station
            closest_station = min(
                stations,
                key=lambda station: distance_to_station(
                    user_input[CONF_LOCATION][CONF_LATITUDE],
                    user_input[CONF_LOCATION][CONF_LONGITUDE],
                    station,
                ),
            )
            LOGGER.debug("Closest station: %s", closest_station)

            if not closest_station:
                errors["base"] = "cannot_find_station"
            if closest_station:
                return self.async_create_entry(
                    title=NAME,
                    data={
                        CONF_STATION: closest_station.name,
                    },
                )

        return self.async_show_form(
            step_id=STEP_MAP,
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_LOCATION,
                        ): LocationSelector(),
                    },
                ),
                {
                    CONF_LOCATION: {
                        CONF_LATITUDE: self.hass.config.latitude,
                        CONF_LONGITUDE: self.hass.config.longitude,
                    },
                },
            ),
            errors=errors,
        )

    async def async_step_station_name(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the station name step."""
        if user_input is not None:
            return self.async_create_entry(
                title=NAME,
                data={
                    CONF_STATION: user_input[CONF_STATION],
                },
            )

        stations = await self.api.get_all_stations()

        return self.async_show_form(
            step_id=STEP_STATION_NAME,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STATION,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=get_stations_options(stations),
                            translation_key="city",
                        ),
                    ),
                },
            ),
        )
