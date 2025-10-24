"""Init file for LUN Misto Air integration."""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import (
    device_registry as dr,
)
from homeassistant.helpers import (
    entity_registry as er,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LUNMistoAirApi
from .const import CONF_STATION_NAME, DOMAIN, SUBENTRY_TYPE_STATION
from .coordinator import LUNMistoAirCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # noqa: ARG001
    """Set up LUN Misto Air."""
    await async_migrate_integration(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a new entry."""
    api = LUNMistoAirApi(session=async_get_clientsession(hass))

    # Initialize runtime_data as a dict to store multiple coordinators
    entry.runtime_data = {}

    # Create a coordinator for each station subentry
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_TYPE_STATION:
            continue

        coordinator = LUNMistoAirCoordinator(hass, api, entry, subentry)
        await coordinator.async_config_entry_first_refresh()

        entry.runtime_data[subentry.subentry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(async_update_entry))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Update a given config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_integration(hass: HomeAssistant) -> None:
    """Migrate integration entry structure to subentries."""
    from homeassistant.config_entries import ConfigSubentry

    entries = hass.config_entries.async_entries(DOMAIN)

    # Check if we have any VERSION 1 entries to migrate
    if not any(entry.version == 1 for entry in entries):
        return

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    for entry in entries:
        if entry.version != 1:
            continue

        # Skip if entry doesn't have station data
        if SUBENTRY_TYPE_STATION not in entry.data:
            LOGGER.warning(
                "VERSION 1 entry %s has no station data, skipping",
                entry.entry_id,
            )
            continue

        # Create a subentry for this station
        subentry = ConfigSubentry(
            data=MappingProxyType(
                {CONF_STATION_NAME: entry.data["station"]},
            ),
            subentry_type=SUBENTRY_TYPE_STATION,
            title=entry.title,
            unique_id=entry.data["station"],
        )

        # Add the subentry to the entry
        hass.config_entries.async_add_subentry(entry, subentry)

        # Move entities to the subentry
        entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

        # Get the old device using entry_id as identifier
        old_device = device_registry.async_get_device(
            identifiers={(DOMAIN, entry.entry_id)},
        )

        # Get or create device with station name as identifier
        device = device_registry.async_get_device(
            identifiers={(DOMAIN, entry.data["station"])},
        )

        for entity_entry in entities:
            entity_registry.async_update_entity(
                entity_entry.entity_id,
                config_entry_id=entry.entry_id,
                config_subentry_id=subentry.subentry_id,
            )

        if device is not None:
            device_registry.async_update_device(
                device.id,
                add_config_subentry_id=subentry.subentry_id,
                add_config_entry_id=entry.entry_id,
            )
            device_registry.async_update_device(
                device.id,
                remove_config_entry_id=entry.entry_id,
                remove_config_subentry_id=None,
            )

        # Remove old device if it exists and is different
        if old_device is not None and old_device != device:
            device_registry.async_remove_device(old_device.id)

        # Update entry to VERSION 2 and clear old data
        hass.config_entries.async_update_entry(
            entry,
            version=2,
            data={},
            unique_id=None,
        )

        LOGGER.info("Migrated entry %s to VERSION 2 with subentries", entry.entry_id)
