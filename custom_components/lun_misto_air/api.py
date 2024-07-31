"""API for LUN Misto Air."""

from dataclasses import dataclass
from typing import Any, Self

import requests


class LUNMistoAirError(Exception):
    """Base class for exceptions."""


class LUNMistoAirConnectionError(LUNMistoAirError):
    """Raised for connection errors."""


class LUNMistoAirResponseError(LUNMistoAirError):
    """Raised for response errors."""


class LUNMistoAirStationNotFoundError(LUNMistoAirError):
    """Raised when a station is not found."""


class LUNMistoAirCityNotFoundError(LUNMistoAirError):
    """Raised for station errors."""


@dataclass(slots=True)
class LUNMistoAirStation:
    """Represents a station."""

    name: str
    latitude: float
    longitude: float
    city: str
    aqi: int
    avg_pm10: float
    avg_pm25: float
    avg_pm100: float
    updated: str

    @classmethod
    def from_dict(cls: type[Self], data: dict) -> Self:
        """Initialize from a dict."""
        return cls(
            name=data["name"],
            latitude=data["lat"],
            longitude=data["lng"],
            city=data["city"],
            aqi=data["aqi"],
            avg_pm10=data["avgPm10"],
            avg_pm25=data["avgPm25"],
            avg_pm100=data["avgPm100"],
            updated=data["updated"],
        )


class LUNMistoAirApi:
    """API for LUN Misto Air."""

    base_url = "https://misto.lun.ua/api/v1/air/stations"
    timeout = 60

    def _request(self, url: str) -> list[dict[str, Any]]:
        """Private method to handle HTTP requests."""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()  # Return JSON data
        except requests.exceptions.HTTPError as http_err:
            msg = f"HTTP error occurred: {http_err}"
            raise LUNMistoAirResponseError(msg) from http_err
        except requests.exceptions.Timeout as timeout_err:
            msg = f"Request timed out: {timeout_err}"
            raise LUNMistoAirConnectionError(msg) from timeout_err
        except requests.exceptions.RequestException as req_err:
            msg = f"Request error occurred: {req_err}"
            raise LUNMistoAirConnectionError(msg) from req_err
        except Exception as err:
            msg = f"An unexpected error occurred: {err}"
            raise LUNMistoAirError(msg) from err

    def get_all_stations(self) -> list[LUNMistoAirStation]:
        """Fetch and return data for all stations."""
        if data := self._request(self.base_url):
            return [LUNMistoAirStation.from_dict(station) for station in data]
        return []

    def get_by_station_name(self, station_name: str) -> LUNMistoAirStation:
        """Fetch and return data for a specific station by its name."""
        if stations := self.get_all_stations():
            for station in stations:
                if station.name == station_name:
                    return station
        raise LUNMistoAirStationNotFoundError

    def get_by_city(self, city: str) -> list[LUNMistoAirStation]:
        """Fetch and return data for all stations in a specific city."""
        if stations := self.get_all_stations():
            return [
                station for station in stations if station.city.lower() == city.lower()
            ]
        raise LUNMistoAirCityNotFoundError
