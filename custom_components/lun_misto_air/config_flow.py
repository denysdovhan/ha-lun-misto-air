"""Config flow for LUN Misto Air integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
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
from .const import CONF_STATION_NAME, DOMAIN, NAME, SUBENTRY_TYPE_STATION

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


class LUNMistoAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for LUN Misto Air integration."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize config flow."""
        self.data: dict[str, Any] = {}

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls: type["LUNMistoAirConfigFlow"],
        config_entry: ConfigEntry,  # noqa: ARG003
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this handler."""
        return {SUBENTRY_TYPE_STATION: StationFlowHandler}

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        # Create the main entry without station data
        return self.async_create_entry(
            title=NAME,
            data={},
        )


class StationFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding stations."""

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> SubentryFlowResult:
        """User flow to create a sensor subentry."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["map", "station_name"],
        )

    async def async_step_map(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> SubentryFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api = LUNMistoAirApi(session=async_get_clientsession(self.hass))
            stations = await api.get_all_stations()
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

            if not closest_station:
                errors["base"] = "cannot_find_station"
            if closest_station:
                return await self._async_create_entry(closest_station)

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
    ) -> SubentryFlowResult:
        """Handle the station name step."""
        if user_input is not None:
            api = LUNMistoAirApi(session=async_get_clientsession(self.hass))
            station = await api.get_station_by_name(user_input[CONF_STATION_NAME])
            return await self._async_create_entry(station)

        api = LUNMistoAirApi(session=async_get_clientsession(self.hass))
        stations = await api.get_all_stations()

        return self.async_show_form(
            step_id=STEP_STATION_NAME,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STATION_NAME,
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=get_stations_options(stations),
                            translation_key="city",
                        ),
                    ),
                },
            ),
        )

    async def _async_create_entry(
        self,
        station: LUNMistoAirStation,
    ) -> SubentryFlowResult:
        """Create a subentry for a station."""
        station_name = station.name
        # Check if this station is already configured
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            for subentry in entry.subentries.values():
                if subentry.unique_id == station_name:
                    return self.async_abort(reason="already_configured")

        return self.async_create_entry(
            title=f"{station.city.capitalize()} ({station.name})",
            data={
                CONF_STATION_NAME: station_name,
            },
            unique_id=station_name,
        )
