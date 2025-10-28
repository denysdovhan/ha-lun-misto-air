"""Base entity for LUN Misto Air integration."""

import logging

from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATION_NAME_FORMAT
from .coordinator import LUNMistoAirCoordinator

LOGGER = logging.getLogger(__name__)


class LUNMistoAirEntity(CoordinatorEntity[LUNMistoAirCoordinator]):
    """Common logic for LUN Misto Air entity."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        subentry_data = self.coordinator.config_subentry.data
        city = self.coordinator.data.city.capitalize()
        station_name = self.coordinator.data.name
        identifier = self.coordinator.config_subentry.unique_id or "unknown"

        # Device name: user-provided name or fallback to "{city} {station}"
        # CONF_NAME is always used when present (for both static and dynamic)
        name = subentry_data.get(CONF_NAME) or STATION_NAME_FORMAT.format(
            city=city,
            station=station_name,
        )

        LOGGER.debug(
            "Device info for %s: name=%s (from CONF_NAME=%s), city=%s, station=%s",
            identifier,
            name,
            subentry_data.get(CONF_NAME),
            city,
            station_name,
        )

        return DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=name,
            manufacturer="LUN",
            entry_type=DeviceEntryType.SERVICE,
            translation_key="lun_misto_air",
            translation_placeholders={
                "name": name,
                "city": city,
                "station_name": station_name,
            },
        )
