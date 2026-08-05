

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
[![Made in Ukraine](https://img.shields.io/badge/made_in-Ukraine-ffd700.svg?labelColor=0057b7)](https://stand-with-ukraine.pp.ua)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://stand-with-ukraine.pp.ua)
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

[![repo_url](https://img.shields.io/badge/GitHub-grey?logo=github&logoColor=white)](https://github.com/ALERTua/hass-gaggiuino)
[![hacs_integration](https://img.shields.io/badge/HACS-Integration-blue.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ALERTua&repository=hass-gaggiuino&category=Integration)
[![Validate](https://github.com/ALERTua/hass-gaggiuino/actions/workflows/validate.yml/badge.svg)](https://github.com/ALERTua/hass-gaggiuino/actions/workflows/validate.yml)
[![GitHub Release](https://img.shields.io/github/v/release/ALERTua/hass-gaggiuino)](https://github.com/ALERTua/hass-gaggiuino/releases)


![](/images/logo.png)

Integración HACS para Home Assistant para Gaggiuino
---------------------------
Repositorio: https://github.com/ALERTua/hass-gaggiuino

Repositorio de Gaggiuino: https://github.com/Zer0-bit/gaggiuino/releases

README de Blueprints: [enlace](/blueprints/BLUEPRINTS.md)

Biblioteca API:
- PyPi: https://pypi.org/project/gaggiuino_api/
- Repositorio: https://github.com/ALERTua/gaggiuino_api

# Tabla de Contenidos
1. [Instalación](#installation)
2. [Solución de Problemas](#faq--troubleshooting)
3. [Biblioteca de Blueprints](/blueprints/README.md)

## Installation

[![Open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ALERTua&repository=hass-gaggiuino&category=Integration)
<details><summary> Agregar la integración a HACS manualmente </summary>

1. Agrega el Repositorio Personalizado de HACS para este proyecto

![img](/images/15_HACS_add_repo.png)

2. Ahora la integración se puede encontrar en la Tienda Comunitaria de HACS

![img](/images/16_HACS_repo_added.png)

3. Abre la integración en la Tienda Comunitaria de HACS
y descárgala usando el botón correspondiente en la esquina inferior derecha.

![img](/images/17_HACS_select_repo.png)

4. Reinicia tu Home Assistant

</details>

### Agregar la integración a Home Assistant

<details><summary> Agregar la integración a Home Assistant </summary>

5. Abre Configuración→Dispositivos y Servicios, presiona el botón Agregar Integración en la esquina inferior derecha,
busca esta integración y selecciónala.

![img](/images/25_add_integration.png)

</details>

## Configuración de la integración

1. Ingresa la dirección web de tu Gaggiuino

![img](/images/26_config_flow.png)

Configuración de la integración completada. Tu Gaggiuino ahora está disponible como un dispositivo.

![img](/images/35_integration_entries.png)

![img](/images/45_integration_device.png)

## Preguntas Frecuentes / Solución de Problemas

**P: `ERROR (MainThread) [custom_components.gaggiuino.coordinator] Error fetching gaggiuino data: Unhandled exception`**

**R:** Asegúrate de tener el último firmware; verifica que los Endpoints de la API estén disponibles para Home Assistant.
Ej. http://gaggiuino.local/api/system/status


**P: Los estados solo se actualizan con esta frecuencia.**

**R:** Las integraciones de Home Assistant tienen un período de actualización fijo. Este está fijado en 30 segundos. Debido a este largo período de actualización, la integración no puede usarse para monitorear extracciones.


**P: ¿Por qué los perfiles muestran sus IDs en el Selector de Perfil?**

**R:** Aunque los IDs de Perfil de Gaggiuino son únicos, sus nombres no lo son; puedes tener múltiples perfiles con el mismo nombre, pero sus IDs serán diferentes. El método de selección de perfil requiere que se proporcione un ID de perfil, por eso decidí representar visualmente los elementos del selector como el Nombre del Perfil y su ID correspondiente. Sé que esto no es muy conveniente para la automatización, pero estoy abierto a tus ideas.
```yaml
action: select.select_option
target:
  entity_id: select.gaggiuino_profile
data:
  option: "OFF (ID: 7)"
```

#### Nota: Siempre implemento características de las últimas versiones (Releases) de Gaggiuino. Por favor, asegúrate de que tu máquina tenga el último firmware disponible.

Siempre puedes encontrarme en el Discord oficial de Gaggiuino.

No dudes en publicar tus automatizaciones en https://github.com/ALERTua/hass-gaggiuino/discussions/categories/ideas

Reuniré las publicaciones más valiosas en una fija.

❤️
