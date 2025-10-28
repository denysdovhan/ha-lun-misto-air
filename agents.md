# AI Coding Agents Guide

## Purpose

Agents act as senior Swift collaborators. Keep responses concise,
clarify uncertainty before coding, and align suggestions with the rules linked below.

## Project Overview

This repository is a Home Assistant custom integration providing air quality data from [LUN Misto Air](https://lun.ua/misto/air). Main codebase lives under `custom_components/lun_misto_air`.

### Code structure

- `translations` - folder containing translations.
- `__init__.py` - init file of the integration, creates entries, runs migrations from older to newer versions, etc.
- `api.py` - a file containing an API class for fetching data. Should be Home Assistant agnostinc, since in the future it's planned to move it to the separate package.
- `config_flow.py` - a file describing a flow to create new entries/subentries.
- `const.py` - a file containing constants used throught the project. Use `homeassistant.const` for commonly used constants.
- `coordinator.py` - a data fetching coordinator. Fetched data from the API, transform it to the proper format and passes them to sensors.
- `entity.py` - an entity descriptor that is used as a template when creating sensors. Contains important `DeviceInfo` joining different sensors into a single device.
- `migrations.py` - a file containing migrations between different versions specified in `config_flow.py`.
- `manifest.json` - a file declaring an integration manifest.
- `sensor.py` - declares sensors using entity descriptors. Implements sensor implementation.
- `data.py` - runtime data module. Defines `LUNMistoAirRuntimeData` dataclass that stores the shared API client and a mapping of coordinators per subentry (`coordinators: dict[subentry_id, LUNMistoAirCoordinator]`). Also defines a typed config entry alias `type LUNMistoAirConfigEntry = ConfigEntry[LUNMistoAirRuntimeData]`. Access this via `entry.runtime_data`.

<instruction>Fill in by LLM assistant memory</instruction>

### Using Coordinator to Fetch Data

We use one DataUpdateCoordinator per station subentry (static or dynamic) to fetch data from the LUN Misto Air API. Coordinators are created in `__init__.py` during setup and stored in `entry.runtime_data.coordinators` keyed by `subentry_id`. Platforms (e.g., `sensor.py`) read from this mapping and pass `config_subentry_id=subentry_id` when adding entities so entities bind to the right coordinator.

Documentation: https://developers.home-assistant.io/docs/integration_fetching_data

### Decouple API Data from Coordinator

Coordinator should not rely on API response structure. Instead, transform data into plain Python objects (e.g., dataclasses) on API class level, so coordinator only calls API methods and works with stable data structures.

### API

External API: `https://misto.lun.ua/api/v1/air/stations` (cloud polling). No auth. All HTTP and parsing lives in `api.py`.

## Runtime Data

- `LUNMistoAirRuntimeData` is a small container attached to each `ConfigEntry` under `entry.runtime_data`.
  - Fields:
    - `api`: a single shared `LUNMistoAirApi` client per entry.
    - `coordinators`: a dict keyed by `subentry_id` holding one `LUNMistoAirCoordinator` per station subentry.
- `type LUNMistoAirConfigEntry = ConfigEntry[LUNMistoAirRuntimeData]` is a typed alias used in function signatures for clarity.
- Initialization happens in `__init__.py`:
  - Build the API client, set `entry.runtime_data = LUNMistoAirRuntimeData(api=api)`.
  - For each station subentry, create a coordinator, refresh it, then store under `entry.runtime_data.coordinators[subentry_id]`.
- Platforms (e.g., `sensor.py`) retrieve coordinators via `config_entry.runtime_data.coordinators` and add entities with the appropriate `config_subentry_id`.

This pattern keeps setup logic centralized, avoids globals, and makes platform code simple and testable.

## Workflow

<instruction>Fill in by LLM assistant in memory</instruction>

This project is developed from Devcontainer described in `.devcontainer.json` file.

- **Adding/changing data fetching**
  - Extend `api.py` first; return Python objects (dataclasses) independent of raw JSON.
  - Use/extend `coordinator.py` to pick dynamic vs static station and compute derived values.
  - Keep all shared runtime stuff (API client, coordinators map) in `data.py` via `entry.runtime_data`.
- **Entities and platforms**
  - Add new sensor descriptors in `sensor.py` (use `translation_key`).
  - Unique ID is `{subentry_id}-{sensor_key}`; do not hardcode unique IDs in config flow.
  - Device naming relies on `CONF_NAME` (guaranteed by migrations); placeholders are provided via `device_info`.
- **Config flow**
  - Avoid manual unique_id creation. Duplicate detection is done by comparing subentry `data`:
    - Dynamic: same type + same `CONF_NAME`.
    - Static: same type + same `CONF_STATION_NAME`.
  - Default map selector position to Home location (from `hass.config`).
- **Migrations**
  - See `migrations.py`. Current version ensures every subentry has `CONF_NAME` (v3). Add new steps if stored schema changes.
- **Translations**
  - Edit `translations/*.json` directly. Update Inlang configuration when needed.
  - Translate values only; keep keys the same. Preserve placeholders: `{name}`, `{city}`, `{station_name}`.
- **When unsure**
  - Prefer adding debug logs and ask for the output to reason about runtime state.

### Develompent Scripts

- `scripts/setup` - installs dependencies and installs pre-commit.
- `scripts/develop` - starts a development Home Assistant instance.
- `scripts/lint` - runs a ruff linter/formatter.

### Development Process

- Ask for clarification when requirements are ambiguous; surface 2–3 options when trade-offs matter.
- Update documentation and related rules when introducing new patterns or services.
- When unsure or need to make a significant decision ASK the user for guidance
- Do not commit anything. Leave commits to be done by a developer.

## Code Style

Use code style described in `.ruff.toml` configuration. Standard Python. 2-spaces indentation.

## Translations

- Translations: copy `translations/en.json` to add locales; translate values only where appropriate per HA guidelines.
- Entities: Use the `translation_key` defined in `SENSOR_TYPES` (e.g., `aqi`, `pm25`, `pm10`, `pm1`).
- Placeholders: Reference `{city}` and `{station_name}` from `translation_placeholders` supplied by `device_info` when rendering names or descriptions.
- Add locales by copying `translations/en.json` and translating values per HA guidelines.

## Home Assistant API

Carefully read links to the Home Assistant Developer documentation for guidance.

Fetch these links to get more informations about specific Home Assistant APIs directly from its documentation:

- File structure: https://developers.home-assistant.io/docs/creating_integration_file_structure
- Config Flow: https://developers.home-assistant.io/docs/config_entries_config_flow_handler
- Fetching data: https://developers.home-assistant.io/docs/integration_fetching_data
- Repairs: https://developers.home-assistant.io/docs/core/platform/repairs
- Sensor: https://developers.home-assistant.io/docs/core/entity/sensor
- Config Entries: https://developers.home-assistant.io/docs/config_entries_index
- Data Entry Flow: https://developers.home-assistant.io/docs/data_entry_flow_index
- Manifest: https://developers.home-assistant.io/docs/creating_integration_manifest

## Notes

If anything here is unclear (e.g., adding a new platform beyond sensors, or debugging with `debugpy`), tell me what you want to do and I’ll expand these instructions.

If you struggle to find a solution, suggest to add logger statements and ask for output to get more context and understant the flow better. When logger output is provided, analyze it to understand what is going on.
