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
from homeassistant.const import CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_NAME
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
from .const import (
    CONF_STATION_NAME,
    CONF_STATION_TYPE,
    DOMAIN,
    NAME,
    STATION_NAME_FORMAT,
    STATION_TYPE_DYNAMIC,
    STATION_TYPE_STATIC,
    SUBENTRY_TYPE_STATION,
)

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
            name = user_input[CONF_NAME]
            latitude = user_input[CONF_LOCATION][CONF_LATITUDE]
            longitude = user_input[CONF_LOCATION][CONF_LONGITUDE]

            # Unique ID for dynamic stations: based on coordinates
            unique_id = f"dynamic_{round(latitude, 6)}_{round(longitude, 6)}"

            LOGGER.debug(
                "Creating dynamic station entry: name=%s, unique_id=%s, lat=%s, lon=%s",
                name,
                unique_id,
                latitude,
                longitude,
            )

            # Check if already configured
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                for subentry in entry.subentries.values():
                    if subentry.unique_id == unique_id:
                        return self.async_abort(reason="already_configured")

            return self.async_create_entry(
                title=name,
                data={
                    CONF_NAME: name,
                    CONF_STATION_TYPE: STATION_TYPE_DYNAMIC,
                    CONF_LATITUDE: latitude,
                    CONF_LONGITUDE: longitude,
                },
                unique_id=unique_id,
            )

        return self.async_show_form(
            step_id=STEP_MAP,
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_LOCATION): LocationSelector(),
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
            # Validate unique custom name across subentries
            desired_name: str = user_input[CONF_NAME]
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                for subentry in entry.subentries.values():
                    existing_name = subentry.data.get(CONF_NAME) or subentry.title
                    if existing_name and existing_name == desired_name:
                        return self.async_abort(reason="already_configured")

            api = LUNMistoAirApi(session=async_get_clientsession(self.hass))
            station = await api.get_station_by_name(user_input[CONF_STATION_NAME])
            return await self._async_create_entry(
                station,
                custom_name=desired_name,
            )

        api = LUNMistoAirApi(session=async_get_clientsession(self.hass))
        stations = await api.get_all_stations()

        return self.async_show_form(
            step_id=STEP_STATION_NAME,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
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
        *,
        custom_name: str | None = None,
    ) -> SubentryFlowResult:
        """Create a subentry for a static station."""
        # Unique ID for static stations: the station name from API
        unique_id = station.name

        # Check if already configured
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            for subentry in entry.subentries.values():
                if subentry.unique_id == unique_id:
                    return self.async_abort(reason="already_configured")

        name = custom_name or STATION_NAME_FORMAT.format(
            city=station.city.capitalize(),
            station=station.name,
        )

        LOGGER.debug(
            "Creating static station entry: name=%s, station=%s, unique_id=%s",
            name,
            station.name,
            unique_id,
        )

        return self.async_create_entry(
            title=name,
            data={
                CONF_NAME: name,
                CONF_STATION_TYPE: STATION_TYPE_STATIC,
                CONF_STATION_NAME: station.name,
            },
            unique_id=unique_id,
        )
