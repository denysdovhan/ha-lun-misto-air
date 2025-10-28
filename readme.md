[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua/)

![HA LUN Misto Air Logo](./icons/logo@2x.png#gh-light-mode-only)
![HA LUN Misto Air Logo](./icons/dark_logo@2x.png#gh-dark-mode-only)

# 💨 HA LUN Misto Air

[![GitHub Release][gh-release-image]][gh-release-url]
[![GitHub Downloads][gh-downloads-image]][gh-downloads-url]
[![hacs][hacs-image]][hacs-url]
[![GitHub Sponsors][gh-sponsors-image]][gh-sponsors-url]
[![Buy Me A Coffee][buymeacoffee-image]][buymeacoffee-url]
[![Twitter][twitter-image]][twitter-url]

> An integration for air quality monitoring by [LUN Misto][lun-misto].

This integration for [Home Assistant][home-assistant] provides information about air quality metrics by [LUN Misto][lun-misto]: Air Quality Index (AQI), PM2.5, PM10, PM1, temperature, humidity and pressure.

> [!NOTE]
> This is not affiliated with [LUN][lun-misto] in any way. This integration is developed by an individual. Information may vary from their official website.

## Sponsorship

Your generosity will help me maintain and develop more projects like this one.

- 💖 [Sponsor on GitHub][gh-sponsors-url]
- ☕️ [Buy Me A Coffee][buymeacoffee-url]
- Bitcoin: `bc1q7lfx6de8jrqt8mcds974l6nrsguhd6u30c6sg8`
- Ethereum: `0x6aF39C917359897ae6969Ad682C14110afe1a0a1`

## Installation

The quickest way to install this integration is via [HACS][hacs-url] by clicking the button below:

[![Add to HACS via My Home Assistant][hacs-install-image]][hasc-install-url]

If it doesn't work, adding this repository to HACS manually by adding this URL:

1. Visit **HACS** → **Integrations** → **...** (in the top right) → **Custom repositories**
1. Click **Add**
1. Paste `https://github.com/denysdovhan/ha-lun-misto-air` into the **URL** field
1. Chose **Integration** as a **Category**
1. **LUN Misto Air** will appear in the list of available integrations. Install it normally.

## Usage

This integration is configurable via UI. On **Devices and Services** page, click **Add Integration** and search for **LUN Misto Air**.

<img width="100%" alt="Integration page" src="./media/integration-page.png" />

This integration supports subentries, so you can setup multiple stations for a single configurations.

<img width="405" height="266" alt="Selecting stations" src="./media/station-menu.png" />

You can select measuring station by choosing the point on the map. The integration will be automatically finding the nearest station to specified location on every update:

<img width="610" height="832" alt="Station from the map" src="./media/map.png" />

You can also find your station on [LUN Misto website][lun-misto-air]. Select the stations with the same name in the list:

<img width="430" height="404" alt="Station from the list" src="./media/list.png" />

The integration will create a sensor for each of the available metrics:

<img width="326" height="477" alt="Provided sensors" src="./media/sensors.png" />

## Translations

Help us translate this integration into more languages.

[**🌐 Translate via Inlang**](https://inlang.com/editor/github.com/denysdovhan/ha-lun-misto-air?ref=badge)

Translation files live in `custom_components/lun_misto_air/translations/` (e.g., `en.json`, `uk.json`).

## Development

Want to contribute to the project?

First, thanks! Check [contributing guideline](./CONTRIBUTING.md) for more information.

## License

MIT © [Denys Dovhan][denysdovhan]

<!-- Badges -->

[gh-release-url]: https://github.com/denysdovhan/ha-lun-misto-air/releases/latest
[gh-release-image]: https://img.shields.io/github/v/release/denysdovhan/ha-lun-misto-air?style=flat-square
[gh-downloads-url]: https://github.com/denysdovhan/ha-lun-misto-air/releases
[gh-downloads-image]: https://img.shields.io/github/downloads/denysdovhan/ha-lun-misto-air/total?style=flat-square
[hacs-url]: https://github.com/hacs/integration
[hacs-image]: https://img.shields.io/badge/hacs-custom-orange.svg?style=flat-square
[gh-sponsors-url]: https://github.com/sponsors/denysdovhan
[gh-sponsors-image]: https://img.shields.io/github/sponsors/denysdovhan?style=flat-square
[buymeacoffee-url]: https://buymeacoffee.com/denysdovhan
[buymeacoffee-image]: https://img.shields.io/badge/support-buymeacoffee-222222.svg?style=flat-square
[twitter-url]: https://twitter.com/denysdovhan
[twitter-image]: https://img.shields.io/badge/twitter-%40denysdovhan-00ACEE.svg?style=flat-square

<!-- References -->

[lun-misto]: https://misto.lun.ua/
[lun-misto-air]: https://misto.lun.ua/air
[home-assistant]: https://www.home-assistant.io/
[denysdovhan]: https://github.com/denysdovhan
[hasc-install-url]: https://my.home-assistant.io/redirect/hacs_repository/?owner=denysdovhan&repository=ha-lun-misto-air&category=integration
[hacs-install-image]: https://my.home-assistant.io/badges/hacs_repository.svg
