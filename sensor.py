from homeassistant.helpers.entity import Entity
from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    api_client = hass.data[DOMAIN][config_entry.entry_id]["api_client"]
    controls = hass.data[DOMAIN][config_entry.entry_id]["controls"]
    sensors = []

    for device, control_names in controls.items():
        for control_name in control_names:
            sensors.append(ControlSensor(api_client, device, control_name))

    async_add_entities(sensors, True)


class ControlSensor(Entity):
    def __init__(self, api_client, device, control):
        self._api_client = api_client
        self._device = device
        self._control = control
        self._state = None
        self._attr_unique_id = f"{device}_{control}_sensor"

    async def async_update(self):
        self._state = await self._api_client.get_control(self._device, self._control)

    @property
    def name(self):
        return f"{self._device} {self._control}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._attr_unique_id
