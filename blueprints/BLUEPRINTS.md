## Blueprints

### [Gaggiuino Heated Up Notification](/blueprints/automation/gaggiuino_heated_up.yaml)

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FALERTua%2Fhass-gaggiuino%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fgaggiuino_heated_up.yaml)

Notifies when Gaggiuino Temperature reaches the Selected Profile Target Temperature. Triggers only once an hour.

* Create a dummy Gaggiuino profile with target temperature of 15°C
* Name it "OFF", for example.
* Take its full name from the integration Profile Selector. E.g. `OFF (ID: 7)`

![img.png](images/heat_up_1.png)

* Fill this full profile name to the blueprint's `Gaggiuino OFF Profile Name` field

![img_1.png](images/heat_up_2.png)
