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

API Library:
- PyPi: https://pypi.org/project/gaggiuino_api/
- Repository: https://github.com/ALERTua/gaggiuino_api

### Note: There are not many API Endpoints currently available. The current state of this integration covers the initial API endpoints introduced in https://github.com/Zer0-bit/gaggiuino/releases/tag/dev-6655d6d. Make sure your machine firmware is of at least this tag.

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

### Note: Currently, no API Endpoint allows getting the currently selected profile. That's why the initial profile selection is empty. However, the selector selects the profile correctly.

![img](/images/35_integration_entries.png)

![img](/images/45_integration_device.png)

### Note: While the Gagguino Profile IDs are unique, their names are not, you can have multiple profiles with the same name, but their IDs will be different. The profile selection method calls for a profile ID to be provided, that's why I decided to visually represent the selector items as both Profile Names and their corresponding IDs. I know this is not very convenient in automation, but I am open to your ideas.
