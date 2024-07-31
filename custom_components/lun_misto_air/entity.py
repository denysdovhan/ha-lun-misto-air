"""Base entity for LUN Misto Air integration."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_STATION, DOMAIN
from .coordinator import LUNMistoAirCoordinator


class LUNMistoAirEntity(CoordinatorEntity[LUNMistoAirCoordinator]):
    """Common logic for LUN Misto Air entity."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            translation_key="lun_misto_air",
            translation_placeholders={CONF_STATION: str(self.coordinator.station_name)},
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            manufacturer="LUN",
            entry_type=DeviceEntryType.SERVICE,
        )
