"""Coordinator for LUN Misto Air integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    LUNMistoAirApi,
    LUNMistoAirError,
    LUNMistoAirStation,
    LUNMistoAirStationNotFoundError,
)
from .const import CONF_STATION, DOMAIN, UPDATE_INTERVAL

LOGGER = logging.getLogger(__name__)


class LUNMistoAirCoordinator(DataUpdateCoordinator[LUNMistoAirStation]):
    """The LUN Misto Air data update coordinator."""

    config_entry: ConfigEntry
    station_name: str

    def __init__(
        self,
        hass: HomeAssistant,
        api: LUNMistoAirApi,
        config_entry: ConfigEntry,
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
        self.station_name = self.config_entry.data[CONF_STATION]

    async def _async_update_data(self) -> LUNMistoAirStation:
        try:
            return await self._api.get_station_by_name(
                self.station_name,
                self.hass.config.latitude,
                self.hass.config.longitude,
            )
        except LUNMistoAirStationNotFoundError as exc:
            msg = f"Station '{self.station_name}' not found"
            raise UpdateFailed(msg) from exc
        except LUNMistoAirError as exc:
            msg = f"Error fetching data: {exc}"
            raise UpdateFailed(msg) from exc
