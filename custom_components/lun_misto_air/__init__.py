"""Init file for LUN Misto Air integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LUNMistoAirApi
from .const import SUBENTRY_TYPE_STATION
from .coordinator import LUNMistoAirCoordinator
from .migrations import async_migrate_integration

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
