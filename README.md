[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

![](/icons/logo.png)

Home Assistant HACS Integration for Gaggiuino
---------------------------
Repository: https://github.com/ALERTua/hass-gaggiuino

Gaggiuino Repository: https://github.com/Zer0-bit/gaggiuino/releases
API Library:
- PyPi: https://pypi.org/project/gaggiuino_api/
- Repository: https://github.com/ALERTua/gaggiuino_api

### Note: There are not many API Endpoints currently available. The current state of this integration covers the initial API endpoints introductd in https://github.com/Zer0-bit/gaggiuino/releases/tag/dev-6655d6d . Make sure your machine firmware is of at least this tag.

## Integration Installation

### Adding the integration to HACS
<details><summary> Adding the integration to HACS </summary>

1. Add HACS Custom Repository for this project

![img](/media/15_HACS_add_repo.png)

2. The integration can now be found in the HACS Community Store

![img](/media/16_HACS_repo_added.png)

3. Open the integration in the HACS Community Store
and download it using the corresponding button in the lower right corner.

![img](/media/17_HACS_select_repo.png)

4. Restart your Home Assistant

</details>

### Adding the integration to Home Assistant

<details><summary> Adding the integration to Home Assistant </summary>

5. Open your Settings→Devices&Services, press Add Integration button in the lower right corner,
search for this integration, and select it.

![img](/media/25_add_integration.png)

</details>

## Integration setup

1. Enter your Gaggiuino web address

![img](/media/26_config_flow.png)

Integration setup complete. Your Gaggiuino is now available as a device.

### Note: At the moment there's no API Endpoint that allows getting the currently selected profile. That's why the initial profile selection is empty. But the selector selects the profile correctly.

![img](/media/35_integration_entries.png)

![img](/media/45_integration_device.png)

### Note: While the Gagguino Profile IDs are unique, their names are not, you can have multiple profiles with the same name, but their IDs will be different. Profile selection method calls for a profile ID to be provided, that's why I decided to visually represent the selector items as both Profile Names and their corresponding IDs. I know this is not very convenient in automations, I am open to your ideas.
