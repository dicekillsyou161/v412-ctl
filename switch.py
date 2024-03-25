"""Switch platform for v412-ctl integration."""
import logging
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    api_client = hass.data[DOMAIN][config_entry.entry_id]["api_client"]
    controls = hass.data[DOMAIN][config_entry.entry_id]["controls"]
    entities = []

    for device_id, device_data in controls.items():
        device_controls = device_data["controls"]
        for control, details in device_controls.items():
            if details["type"] == "bool":
                entities.append(
                    ControlSwitch(
                        api_client,
                        device_id,
                        control,
                        device_data["device_info"],
                        details["value"],
                    )
                )
    async_add_entities(entities)


class ControlSwitch(SwitchEntity):
    def __init__(self, api_client, device_id, control, device_info, state):
        self.api_client = api_client
        self.device_id = device_id
        self.control = control
        self._attr_is_on = state
        self._attr_device_info = device_info
        self._attr_name = f"{control}.D{device_id}_v412ctl"
        self._attr_unique_id = f"{control}.d{device_id}_v412ctl"

    async def async_turn_on(self, **kwargs):
        if await self.api_client.set_control(self.device_id, self.control, 1):
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        if await self.api_client.set_control(self.device_id, self.control, 0):
            self._attr_is_on = False
            self.async_write_ha_state()
