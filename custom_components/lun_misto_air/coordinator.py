"""Coordinator for LUN Misto Air integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import location

from .api import (
    LUNMistoAirApi,
    LUNMistoAirError,
    LUNMistoAirStation,
    LUNMistoAirStationNotFoundError,
)
from .const import (
    CONF_STATION_NAME,
    CONF_STATION_TYPE,
    DOMAIN,
    STATION_TYPE_DYNAMIC,
    UPDATE_INTERVAL,
)

LOGGER = logging.getLogger(__name__)


class LUNMistoAirCoordinator(DataUpdateCoordinator[LUNMistoAirStation]):
    """The LUN Misto Air data update coordinator."""

    config_entry: ConfigEntry
    config_subentry: ConfigSubentry
    station_name: str

    def __init__(
        self,
        hass: HomeAssistant,
        api: LUNMistoAirApi,
        config_entry: ConfigEntry,
        config_subentry: ConfigSubentry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self.hass = hass
        self._api = api
        self.config_entry = config_entry
        self.config_subentry = config_subentry
        self.station_name = self.config_subentry.data.get(CONF_STATION_NAME, "")

    def _distance_to_station(self, st: LUNMistoAirStation) -> float:
        latitude = self.config_subentry.data[CONF_LATITUDE]
        longitude = self.config_subentry.data[CONF_LONGITUDE]
        dist = location.distance(latitude, longitude, st.latitude, st.longitude)
        return dist if dist is not None else float("inf")

    async def _fetch_static_station(self) -> LUNMistoAirStation:
        """Fetch data for a static station by name."""
        return await self._api.get_station_by_name(self.station_name)

    async def _fetch_dynamic_station(self) -> LUNMistoAirStation:
        """Fetch data for the nearest station based on stored coordinates."""
        stations = await self._api.get_all_stations()
        if not stations:
            msg = "No stations found"
            raise UpdateFailed(msg)

        return min(stations, key=self._distance_to_station)

    async def _async_update_data(self) -> LUNMistoAirStation:
        try:
            station_type = self.config_subentry.data.get(CONF_STATION_TYPE)

            if station_type == STATION_TYPE_DYNAMIC:
                return await self._fetch_dynamic_station()

            return await self._fetch_static_station()
        except LUNMistoAirStationNotFoundError as exc:
            msg = f"Station '{self.station_name}' not found"
            raise UpdateFailed(msg) from exc
        except LUNMistoAirError as exc:
            msg = f"Error fetching data: {exc}"
            raise UpdateFailed(msg) from exc
