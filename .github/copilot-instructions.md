# Copilot Instructions for HA LUN Misto Air

This repository is a Home Assistant custom integration providing air quality data from LUN Misto.

## Architecture

Code lives under `custom_components/lun_misto_air`. The integration uses Config Entry Subentries:

- `config_flow.py`: The main flow creates an empty container entry. A `ConfigSubentryFlow` named "station" lets users add stations in two ways: pick on a map (LocationSelector → closest station) or choose from a list (SelectSelector). Each station becomes a subentry with `unique_id = station_name` and `data[CONF_STATION_NAME]`.
- `__init__.py`: Creates `LUNMistoAirApi`, instantiates one `LUNMistoAirCoordinator` per station subentry, calls `async_config_entry_first_refresh()`, stores coordinators on `entry.runtime_data[subentry_id]`, forwards setup to platforms, and wires reload/unload.
- `coordinator.py`: Polls the API every `UPDATE_INTERVAL` minutes (see `const.py`) and returns a `LUNMistoAirStation` model per subentry. Errors are surfaced as `UpdateFailed` using exceptions from `api.py`.
- `sensor.py`: Declares sensors via `SENSOR_TYPES` (tuple of `LUNMistoAirSensorDescription`). Each sensor reads values from the coordinator’s `LUNMistoAirStation`. Entities extend `LUNMistoAirEntity` to share device info. Entities are added with the subentry context.
- `api.py`: Async client for `https://misto.lun.ua/api/v1/air/stations`, returning `LUNMistoAirStation` (dataclass). Handle failures with `LUNMistoAir*Error` exceptions.

## Key conventions and patterns

- Store coordinators on `ConfigEntry.runtime_data` keyed by subentry id and access them in platforms (see `sensor.async_setup_entry`).
- Add entities with the subentry context using `async_add_entities(..., config_subentry_id=subentry_id)`; import callback type `AddConfigEntryEntitiesCallback`.
- Unique IDs: `f"{subentry_id}-{description.key}"` (stable per subentry and sensor type).
- Device identifiers: `(DOMAIN, station_name)` for the device that groups sensors per physical station.
- Device info: set `translation_placeholders={"city": city, "station_name": station_name}` in `LUNMistoAirEntity.device_info` so translations can render names consistently.
- Add new sensors by appending to `SENSOR_TYPES` with a `value_fn` and optional `available_fn`, `device_class`, `state_class`, and units. Also add translations under `translations/*.json` using the same `translation_key` as the description.
- Keep polling cadence and precision centralized: `UPDATE_INTERVAL`, `SUGGESTED_PRECISION` in `const.py`.
- Log with module-level `LOGGER`; avoid hard-coded strings visible to users—prefer translation keys.

### Using Coordinator to Fetch Data

The DataUpdateCoordinator is used to fetch data from the Yasno API and make it available to Home Assistant entities. It handles polling the API at regular intervals and manages the state of the data.

Documentation: https://developers.home-assistant.io/docs/integration_fetching_data

### Decouple API Data from Coordinator

Coordinator should not rely on API response structure. Instead, transform data into plain Python objects (e.g., dataclasses) on API class level, so coordinator only calls API methods and works with stable data structures.

## Developer workflow

- Install tooling once: `scripts/setup` (installs `homeassistant`, `ruff`, `pre-commit` and sets hooks). Pre-commit runs ruff lint/format and basic file checks.
- Run a local HA with this integration mounted: `scripts/develop` or VS Code task “Run Home Assistant on port 8123”. It bootstraps `config/`, sets `PYTHONPATH` to `custom_components`, then runs `hass --config config --debug`.
- The dev HA config is at `config/configuration.yaml` and enables `debugpy` and debug logging for this integration.
- CI gates: `.github/workflows/lint.yml` (ruff check/format), `validate.yml` (hassfest + HACS), and `release.yml` (version bump + zip packaging). Keep these green.

## Extending the integration (examples)

- Add a metric: update `LUNMistoAirStation` and `from_dict()` mapping in `api.py` if the API exposes a new field; then add an entry to `SENSOR_TYPES` in `sensor.py`, and translations for its `translation_key`.
- Change refresh rate: adjust `UPDATE_INTERVAL` in minutes in `const.py`.
- Surface more attributes: update `LUNMistoAirSensor.extra_state_attributes` or add per-entity attributes via translations under the matching sensor key.

## External dependencies and boundaries

- External API: `https://misto.lun.ua/api/v1/air/stations` (cloud polling). No auth. All HTTP and parsing lives in `api.py`.
- Home Assistant APIs used: Config Flow (selectors), DataUpdateCoordinator, CoordinatorEntity, Sensor platform, device registry.

## Translations

- Translations: copy `translations/en.json` to add locales; translate values only where appropriate per HA guidelines.
- Entities: Use the `translation_key` defined in `SENSOR_TYPES` (e.g., `aqi`, `pm25`, `pm10`, `pm1`).
- Placeholders: Reference `{city}` and `{station_name}` from `translation_placeholders` supplied by `device_info` when rendering names or descriptions.
- Add locales by copying `translations/en.json` and translating values per HA guidelines.

## Notes

When you make changes, add features or fix bugs, ensure to update these instructions accordingly. Do not create new versions of this file; just edit this one.

If anything here is unclear (e.g., adding a new platform beyond sensors, or debugging with `debugpy`), tell me what you want to do and I’ll expand these instructions.
