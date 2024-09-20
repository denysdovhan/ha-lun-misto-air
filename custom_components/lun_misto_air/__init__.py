"""Init file for Yasno Outages integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LUNMistoAirApi
from .coordinator import LUNMistoAirCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a new entry."""
    LOGGER.debug("Entry data: %s", entry.data)

    api = LUNMistoAirApi(session=async_get_clientsession(hass))
    coordinator = LUNMistoAirCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    LOGGER.info("Unload entry: %s", entry)
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Update a given config entry."""
    LOGGER.info("Reload entry: %s", entry)
    await hass.config_entries.async_reload(entry.entry_id)
