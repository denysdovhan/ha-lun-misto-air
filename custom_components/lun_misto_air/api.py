"""Asynchronous API for LUN Misto Air."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self

from aiohttp import ClientError, ClientSession, ClientTimeout


class LUNMistoAirError(Exception):
    """Base class for exceptions."""


class LUNMistoAirConnectionError(LUNMistoAirError):
    """Raised for connection errors."""


class LUNMistoAirResponseError(LUNMistoAirError):
    """Raised for response errors."""


class LUNMistoAirStationNotFoundError(LUNMistoAirError):
    """Raised when a station is not found."""


class LUNMistoAirCityNotFoundError(LUNMistoAirError):
    """Raised when a city is not found."""


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
    def from_dict(cls: type[Self], data: dict[str, Any]) -> Self:
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
    """Asynchronous API for LUN Misto Air."""

    base_url = "https://misto.lun.ua/api/v1/air/stations"

    def __init__(
        self,
        session: ClientSession | None = None,
        timeout: int = 60,
    ) -> None:
        """Initialize the API."""
        self.session = session or ClientSession()
        self.close_session = session is None
        self.timeout = ClientTimeout(total=timeout)

    async def close(self) -> None:
        """Close the client session if we created it."""
        if self.close_session and not self.session.closed:
            await self.session.close()

    async def _request(self, url: str) -> Any:
        """Make an asynchronous HTTP request."""
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                http_ok = 200
                if response.status != http_ok:
                    text = await response.text()
                    msg = f"HTTP error {response.status}: {text}"
                    raise LUNMistoAirResponseError(msg)  # noqa: TRY301
                return await response.json()
        except TimeoutError as err:
            msg = "Request timed out"
            raise LUNMistoAirConnectionError(msg) from err
        except ClientError as err:
            msg = f"Connection error: {err}"
            raise LUNMistoAirConnectionError(msg) from err
        except Exception as err:
            msg = f"Unexpected error: {err}"
            raise LUNMistoAirError(msg) from err

    async def get_all_stations(self) -> list[LUNMistoAirStation]:
        """Fetch and return data for all stations."""
        data = await self._request(self.base_url)
        return [LUNMistoAirStation.from_dict(station) for station in data]

    async def get_station_by_name(self, station_name: str) -> LUNMistoAirStation:
        """Fetch and return data for a specific station by its name."""
        stations = await self.get_all_stations()
        for station in stations:
            if station.name == station_name:
                return station
        msg = f"Station with name '{station_name}' not found."
        raise LUNMistoAirStationNotFoundError(msg)

    async def get_stations_by_city(self, city: str) -> list[LUNMistoAirStation]:
        """Fetch and return data for all stations in a specific city."""
        stations = await self.get_all_stations()
        matching_stations = [
            station for station in stations if station.city.lower() == city.lower()
        ]
        if not matching_stations:
            msg = f"No stations found in city '{city}'."
            raise LUNMistoAirCityNotFoundError(msg)
        return matching_stations
