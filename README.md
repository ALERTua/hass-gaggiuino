[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

[![repo_url](https://img.shields.io/badge/GitHub-grey?logo=github&logoColor=white)](https://github.com/ALERTua/hass-gaggiuino)
[![hacs_integration](https://img.shields.io/badge/HACS-Integration-blue.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ALERTua&repository=hass-gaggiuino&category=Integration)
[![Validate](https://github.com/ALERTua/hass-gaggiuino/actions/workflows/validate.yml/badge.svg)](https://github.com/ALERTua/hass-gaggiuino/actions/workflows/validate.yml)
[![GitHub Release](https://img.shields.io/github/v/release/ALERTua/hass-gaggiuino)](https://github.com/ALERTua/hass-gaggiuino/releases)


![](/images/logo.png)

Home Assistant HACS Integration for Gaggiuino
---------------------------
Repository: https://github.com/ALERTua/hass-gaggiuino

Gaggiuino Repository: https://github.com/Zer0-bit/gaggiuino/releases

Blueprints Readme: [link](/blueprints/BLUEPRINTS.md)

API Library:
- PyPi: https://pypi.org/project/gaggiuino_api/
- Repository: https://github.com/ALERTua/gaggiuino_api

# Table of Contents
1. [Installation](#installation)
2. [Troubleshooting](#faq--troubleshooting)
3. [Blueprint Library](/blueprints/BLUEPRINTS.md)

## Installation

[![Open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ALERTua&repository=hass-gaggiuino&category=Integration)
<details><summary> Adding the integration to HACS manually </summary>

1. Add HACS Custom Repository for this project

![img](/images/15_HACS_add_repo.png)

2. The integration can now be found in the HACS Community Store

![img](/images/16_HACS_repo_added.png)

3. Open the integration in the HACS Community Store
and download it using the corresponding button in the lower right corner.

![img](/images/17_HACS_select_repo.png)

4. Restart your Home Assistant

</details>

### Adding the integration to Home Assistant

<details><summary> Adding the integration to Home Assistant </summary>

5. Open your Settings→Devices&Services, press Add Integration button in the lower right corner,
search for this integration, and select it.

![img](/images/25_add_integration.png)

</details>

## Integration setup

1. Enter your Gaggiuino web address

![img](/images/26_config_flow.png)

Integration setup complete. Your Gaggiuino is now available as a device.

![img](/images/35_integration_entries.png)

![img](/images/45_integration_device.png)

## FAQ / Troubleshooting

**Q: `ERROR (MainThread) [custom_components.gaggiuino.coordinator] Error fetching gaggiuino data: Unhandled exception`**

**A:** Make sure you are on the latest firmware; make sure API Endpoints are available for Home Assistant.
E.g. http://gaggiuino.local/api/system/status


**Q: The states get updated only this frequently.**

**A:** Home Assistant integrations have a fixed update period. This one is fixed at 30 seconds. Due to this long refresh period, the integration can not be used to monitor shots.


**Q: Why do the profiles have their IDs in the Profile Selector?**

**A:** While the Gagguino Profile IDs are unique, their names are not, you can have multiple profiles with the same name, but their IDs will be different. The profile selection method calls for a profile ID to be provided, that's why I decided to visually represent the selector items as both Profile Names and their corresponding IDs. I know this is not very convenient in automation, but I am open to your ideas.

#### Note: I always implement features from the latest Gaggiuino Releases. Please make sure your machine is on the latest firmware available.


Feel free to post your automations in https://github.com/ALERTua/hass-gaggiuino/discussions/categories/ideas

I will gather the most valuable posts in a pinned one.

❤️
