[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua/)

![HA LUN Misto Air Logo](./icons/logo@2x.png)

# 💨 HA LUN Misto Air

[![GitHub Release][gh-release-image]][gh-release-url]
[![GitHub Downloads][gh-downloads-image]][gh-downloads-url]
[![hacs][hacs-image]][hacs-url]
[![GitHub Sponsors][gh-sponsors-image]][gh-sponsors-url]
[![Patreon][patreon-image]][patreon-url]
[![Buy Me A Coffee][buymeacoffee-image]][buymeacoffee-url]
[![Twitter][twitter-image]][twitter-url]

> An integration for air quality monitoring by [LUN Misto][lun-misto].

This integration for [Home Assistant][home-assistant] provides information about air quality metrics by [LUN Misto][lun-misto]: Air Quality Index (AQI), PM2.5, PM10, PM1.

**💡 Note:** This is not affiliated with [LUN][lun-misto] in any way. This integration is developed by an individual. Information may vary from their official website.

## Sponsorship

Your generosity will help me maintain and develop more projects like this one.

- 💖 [Sponsor on GitHub][gh-sponsors-url]
- ☕️ [Buy Me A Coffee][buymeacoffee-url]
- 🤝 [Support on Patreon][patreon-url]
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

<img width="419" alt="Options to select measuring station" src="https://github.com/user-attachments/assets/c396de2e-1cd3-4bd9-b132-1ae14072f033">

You can select measuring station by choosing the point on the map. The integration will automatically fetch the data from the nearest station.

<img width="388" alt="image" src="https://github.com/user-attachments/assets/08d97907-e656-4cff-9eb1-577552a6c1e0">

You can also find your station on [LUN Misto website][lun-misto]. Select the stations with the same name in the list:

<img width="452" alt="image" src="https://github.com/user-attachments/assets/5a7acc0c-2c4e-4e09-84ad-4756e287b7a9">

The integration will create a sensor for each of the available metrics:

<img width="338" alt="image" src="https://github.com/user-attachments/assets/d51ae379-db91-4853-99c0-2b87186fb7a8">

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
[hacs-image]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[gh-sponsors-url]: https://github.com/sponsors/denysdovhan
[gh-sponsors-image]: https://img.shields.io/github/sponsors/denysdovhan?style=flat-square
[patreon-url]: https://patreon.com/denysdovhan
[patreon-image]: https://img.shields.io/badge/support-patreon-F96854.svg?style=flat-square
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
[add-translation]: https://github.com/denysdovhan/ha-lun-misto-air/blob/master/contributing.md#how-to-add-translation
[calendar-card]: https://www.home-assistant.io/dashboards/calendar/
