"""Custom types and runtime data for LUN Misto Air."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .api import LUNMistoAirApi
    from .coordinator import LUNMistoAirCoordinator


@dataclass(slots=True)
class LUNMistoAirRuntimeData:
    """
    Runtime data stored on the config entry.

    Holds shared objects for the integration lifetime, such as the API client
    and per-station coordinators, keyed by subentry_id.
    """

    api: LUNMistoAirApi
    coordinators: dict[str, LUNMistoAirCoordinator] = field(default_factory=dict)


# Type alias for a typed config entry with our runtime data
type LUNMistoAirConfigEntry = ConfigEntry[LUNMistoAirRuntimeData]
