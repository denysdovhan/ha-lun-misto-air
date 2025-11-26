# AI Coding Agents Guide

## Purpose

Agents act as senior Python collaborators. Keep responses concise,
clarify uncertainty before coding, and align suggestions with the rules linked below.

## Project Overview

This repository is a Home Assistant custom integration providing air quality data from [LUN Misto Air](https://lun.ua/misto/air). Main codebase lives under `custom_components/lun_misto_air`.

### Code structure

- `translations` — JSON translations per locale.
- `__init__.py` — sets up the integration, creates per-station coordinators and stores them in `entry.runtime_data.coordinators`, runs migrations v1→v2→v3, forwards sensor platform.
- `api.py` — HTTP client and `LUNMistoAirStation` dataclass, no HA dependencies.
- `config_flow.py` — config/options flows, creates station subentries (static/dynamic).
- `const.py` — constants and defaults; check here before adding new strings.
- `coordinator.py` — `LUNMistoAirCoordinator` fetches data for a station (static by name or nearest dynamic) and surfaces a `LUNMistoAirStation` in `data`.
- `entity.py` — base entity descriptors/device info for sensors; ensures unique IDs with `{subentry_id}-{sensor_key}`.
- `migrations.py` — data migrations; keep in sync with `CONFIG_ENTRY_VERSION` in `config_flow.py`.
- `manifest.json` — HA manifest.
- `sensor.py` — sensor entities bound to coordinators via `config_subentry_id`.
- `data.py` — runtime container (`LUNMistoAirRuntimeData`) and typed entry alias.
- `diagnostics.py` — exposes `async_get_config_entry_diagnostics` with entry metadata, subentries, coordinators, and station snapshots for HA diagnostics download.

### Using Coordinator to Fetch Data

We use one DataUpdateCoordinator per station subentry (static or dynamic) to fetch data from the LUN Misto Air API. Coordinators are created in `__init__.py` during setup and stored in `entry.runtime_data.coordinators` keyed by `subentry_id`. Platforms (e.g., `sensor.py`) read from this mapping and pass `config_subentry_id=subentry_id` when adding entities so entities bind to the right coordinator.

The coordinator:

- Receives the shared API client and subentry metadata (dependency injection).
- Fetches measurements for the configured station; picks dynamic vs static source.
- Computes derived values (AQI, last_updated, attribution) so platforms read ready values.
- Prefer logging and returning `None`/fallbacks instead of raising; add debug logs when behavior is unclear.
- Keep coordinator instances in `entry.runtime_data.coordinators`; avoid globals/singletons.

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

- Python deps defined in `pyproject.toml`, locked in `uv.lock`; manage env with `uv`.
- CI (`lint.yml`, `validate.yml`) installs uv via `astral-sh/setup-uv` and runs tools with `uv run`.
- Use `scripts/bootstrap` for fresh setup (installs uv via pipx if missing, syncs deps, installs pre-commit).
- Prefer running tooling via `uv run <tool>` to match the locked environment.

<instruction>Keep this guide synced when tooling, workflows, or runtime data structures change.</instruction>

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

- `scripts/bootstrap` - sets up development environment.
- `scripts/setup` - installs dependencies and installs pre-commit.
- `scripts/develop` - starts a development Home Assistant instance.
- `scripts/lint` - runs a ruff linter/formatter.

### Development Process

- Ask for clarification when requirements are ambiguous; surface 2–3 options when trade-offs matter.
- Update documentation and related rules when introducing new patterns or services.
- When unsure or need to make a significant decision ASK the user for guidance.
- Each time you make changes to Python code, run `scripts/lint` to check for errors and formatting issues. Fix any issues reported by the linter.
- Commit only when directly asked to do so. Write descriptive commit messages.

## Code Style

Use code style described in `pyproject.toml` configuration. Standard Python. 2-spaces indentation.

Never import modules in functions. All imports must be located on top of the file.

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

## Important directives

<important>
In all interactions and commit messages, be extremely concise and sacrifice grammar for the sake of concision.
</important>

<important>
If anything here is unclear (e.g., adding a new platform beyond sensors and calendar, or debugging with `debugpy`), tell me what you want to do and I'll expand these instructions.
</important>

<important>
If you struggle to find a solution, suggest to add logger statements and ask for output to get more context and understand the flow better. When logger output is provided, analyze it to understand what is going on.
</important>

<important>
When updating this file (`agents.md`), DON'T CHANGE the structure, formatting or style of the document. Just add relevant information, without restructuring: add list items, new sections, etc. NEVER REMOVE tags, like <important> or <instruction>.
</important>

<important>
At the end of each plan, give me a list of unresolved questions to answer, if any. Make the questions extremely concise. Sacrifice grammar for the sake of concision.
</important>
