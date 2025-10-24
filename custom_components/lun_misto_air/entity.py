"""Base entity for LUN Misto Air integration."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LUNMistoAirCoordinator


class LUNMistoAirEntity(CoordinatorEntity[LUNMistoAirCoordinator]):
    """Common logic for LUN Misto Air entity."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        city = self.coordinator.data.city.capitalize()
        station = self.coordinator.station_name
        return DeviceInfo(
            identifiers={(DOMAIN, station)},
            name=f"{city} ({station})",
            manufacturer="LUN",
            entry_type=DeviceEntryType.SERVICE,
            translation_key="lun_misto_air",
            translation_placeholders={
                "city": city,
                "station_name": station,
            },
        )
