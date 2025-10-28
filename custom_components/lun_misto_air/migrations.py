"""Migration functions for LUN Misto Air integration."""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import CONF_NAME
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LUNMistoAirApi
from .const import (
    CONF_STATION_NAME,
    CONF_STATION_TYPE,
    DOMAIN,
    STATION_NAME_FORMAT,
    STATION_TYPE_STATIC,
    SUBENTRY_TYPE_STATION,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

LOGGER = logging.getLogger(__name__)


async def migrate_v1_to_v2(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Migrate VERSION 1 → VERSION 2: Create subentries."""
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    # Skip if entry doesn't have station data
    if SUBENTRY_TYPE_STATION not in entry.data:
        LOGGER.warning(
            "VERSION 1 entry %s has no station data, skipping",
            entry.entry_id,
        )
        return

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
    entities = er.async_entries_for_config_entry(
        entity_registry,
        entry.entry_id,
    )

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

    LOGGER.info(
        "Migrated entry %s from VERSION 1 to VERSION 2",
        entry.entry_id,
    )


async def migrate_v2_to_v3(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Migrate VERSION 2 → VERSION 3: Add CONF_NAME to subentries."""
    api = LUNMistoAirApi(session=async_get_clientsession(hass))

    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_TYPE_STATION:
            continue

        # Skip if CONF_NAME already exists
        if CONF_NAME in subentry.data:
            continue

        # Get station name and fetch data to create fallback name
        station_name = subentry.data.get(CONF_STATION_NAME)
        station_type = subentry.data.get(CONF_STATION_TYPE, STATION_TYPE_STATIC)

        # Determine fallback name
        if station_name and station_type == STATION_TYPE_STATIC:
            try:
                station = await api.get_station_by_name(station_name)
                fallback_name = STATION_NAME_FORMAT.format(
                    city=station.city.capitalize(),
                    station=station.name,
                )
            except Exception:  # noqa: BLE001
                fallback_name = subentry.title
                LOGGER.warning(
                    "Failed to fetch station %s, using title as fallback",
                    station_name,
                )
        else:
            # Dynamic station or no station name: use title
            fallback_name = subentry.title

        # Update subentry with CONF_NAME
        updated_data = dict(subentry.data)
        updated_data[CONF_NAME] = fallback_name

        updated_subentry = ConfigSubentry(
            data=MappingProxyType(updated_data),
            subentry_type=subentry.subentry_type,
            title=subentry.title,
            unique_id=subentry.unique_id,
            subentry_id=subentry.subentry_id,
        )

        hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
        hass.config_entries.async_add_subentry(entry, updated_subentry)

        LOGGER.info(
            "Added CONF_NAME='%s' to subentry %s",
            fallback_name,
            subentry.subentry_id,
        )

    # Update entry to VERSION 3
    hass.config_entries.async_update_entry(
        entry,
        version=3,
    )
    LOGGER.info(
        "Migrated entry %s from VERSION 2 to VERSION 3",
        entry.entry_id,
    )
