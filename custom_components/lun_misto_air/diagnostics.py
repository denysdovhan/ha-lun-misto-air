"""
Diagnostics support for LUN Misto Air.

See https://developers.home-assistant.io/docs/core/integration_diagnostics
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, cast

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers import entity_registry as er

from .const import CONF_STATION_NAME, CONF_STATION_TYPE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import LUNMistoAirStation
    from .data import LUNMistoAirConfigEntry, LUNMistoAirRuntimeData


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: LUNMistoAirConfigEntry,
) -> dict[str, object]:
    """Return diagnostics for a config entry."""
    entity_registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

    entity_states: dict[str, dict[str, object | None]] = {}
    for entity in entities:
        state = hass.states.get(entity.entity_id)
        entity_states[entity.entity_id] = {
            "config_subentry_id": entity.config_subentry_id,
            "original_name": entity.original_name,
            "unique_id": entity.unique_id,
            "state": state.as_dict() if state else None,
        }

    coordinators: list[dict[str, object | None]] = []
    runtime_data: LUNMistoAirRuntimeData | None = getattr(entry, "runtime_data", None)

    if runtime_data:
        for subentry_id, coordinator in runtime_data.coordinators.items():
            station = coordinator.data
            if is_dataclass(station) and not isinstance(station, type):
                station = asdict(cast("LUNMistoAirStation", station))

            coordinators.append(
                {
                    "subentry_id": subentry_id,
                    "station_name": coordinator.station_name,
                    "station_type": coordinator.config_subentry.data.get(
                        CONF_STATION_TYPE,
                    ),
                    "last_update_success": coordinator.last_update_success,
                    "update_interval": str(coordinator.update_interval),
                    "last_exception": (
                        str(coordinator.last_exception)
                        if coordinator.last_exception
                        else None
                    ),
                    "data": station,
                }
            )

    subentries: list[dict[str, object | None]] = []
    for subentry in entry.subentries.values():
        data = dict(subentry.data)
        subentry_options = getattr(subentry, "options", {})
        subentries.append(
            {
                "subentry_id": subentry.subentry_id,
                "title": subentry.title,
                "type": subentry.subentry_type,
                "data": {
                    "name": data.get(CONF_NAME),
                    "station_type": data.get(CONF_STATION_TYPE),
                    "station_name": data.get(CONF_STATION_NAME),
                    "latitude": data.get(CONF_LATITUDE),
                    "longitude": data.get(CONF_LONGITUDE),
                },
                "options": dict(cast("dict[str, object]", subentry_options)),
            }
        )

    api_info = None
    if runtime_data and runtime_data.api:
        api_info = {
            "base_url": runtime_data.api.base_url,
        }

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "minor_version": entry.minor_version,
            "domain": entry.domain,
            "title": entry.title,
            "state": str(entry.state),
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "subentries": subentries,
        "coordinators": coordinators,
        "api": api_info,
        "entities": entity_states,
    }
