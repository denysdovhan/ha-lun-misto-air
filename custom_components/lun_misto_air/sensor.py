"""Sensor platform for Lun Misto Air integration."""

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .api import LUNMistoAirStation
from .const import (
    ATTR_CITY,
    ATTR_STATION_NAME,
    ATTR_UPDATED,
    SUGGESTED_PRECISION,
)
from .coordinator import LUNMistoAirCoordinator
from .data import LUNMistoAirConfigEntry
from .entity import LUNMistoAirEntity

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LUNMistoAirSensorDescription(SensorEntityDescription):
    """Lun Misto Air entity description."""

    available_fn: Callable[[LUNMistoAirStation], bool] = lambda _: True
    value_fn: Callable[[LUNMistoAirStation], StateType]


SENSOR_TYPES: tuple[LUNMistoAirSensorDescription, ...] = (
    LUNMistoAirSensorDescription(
        key="aqi",
        translation_key="aqi",
        device_class=SensorDeviceClass.AQI,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda station: station.aqi,
        available_fn=lambda station: station.aqi is not None,
    ),
    LUNMistoAirSensorDescription(
        key="pm25",
        translation_key="pm25",
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=SUGGESTED_PRECISION,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda station: station.avg_pm25,
        available_fn=lambda station: station.avg_pm25 is not None,
    ),
    LUNMistoAirSensorDescription(
        key="pm10",
        translation_key="pm10",
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=SUGGESTED_PRECISION,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda station: station.avg_pm100,
        available_fn=lambda station: station.avg_pm100 is not None,
    ),
    LUNMistoAirSensorDescription(
        key="pm1",
        translation_key="pm1",
        device_class=SensorDeviceClass.PM1,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=SUGGESTED_PRECISION,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        value_fn=lambda station: station.avg_pm10,
        available_fn=lambda station: station.avg_pm10 is not None,
    ),
    LUNMistoAirSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda station: station.temperature,
    ),
    LUNMistoAirSensorDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda station: station.humidity,
    ),
    LUNMistoAirSensorDescription(
        key="pressure",
        translation_key="pressure",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        native_unit_of_measurement=UnitOfPressure.HPA,
        value_fn=lambda station: station.pressure / 100,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: LUNMistoAirConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Lun Misto Air sensor platform."""
    # Get all coordinators from runtime_data (one per subentry)
    coordinators: dict[str, LUNMistoAirCoordinator] = (
        config_entry.runtime_data.coordinators
    )

    for subentry_id, coordinator in coordinators.items():
        async_add_entities(
            [
                LUNMistoAirSensor(coordinator, description)
                for description in SENSOR_TYPES
            ],
            update_before_add=True,
            config_subentry_id=subentry_id,
        )


class LUNMistoAirSensor(LUNMistoAirEntity, SensorEntity):
    """Define a Lun Misto Air sensor."""

    entity_description: LUNMistoAirSensorDescription

    def __init__(
        self,
        coordinator: LUNMistoAirCoordinator,
        description: LUNMistoAirSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_subentry.subentry_id}-{self.entity_description.key}"
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return the extra state attributes."""
        return {
            ATTR_STATION_NAME: self.coordinator.data.name,
            ATTR_CITY: self.coordinator.data.city.capitalize(),
            ATTR_UPDATED: self.coordinator.data.updated,
            ATTR_LATITUDE: self.coordinator.data.latitude,
            ATTR_LONGITUDE: self.coordinator.data.longitude,
        }

    @property
    def available(self) -> bool:
        """Check if entity is available."""
        return self.entity_description.available_fn(self.coordinator.data)

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
