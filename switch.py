"""Switch platform for v412ctl."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    api_client = hass.data[DOMAIN][entry.entry_id]["api_client"]
    controls = hass.data[DOMAIN][entry.entry_id]["controls"]
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
                        details["value"],
                        device_data["device_info"],
                    )
                )
    async_add_entities(entities)


class ControlSwitch(SwitchEntity):
    def __init__(self, api_client, device_id, control, value, device_info):
        self.api_client = api_client
        self.device_id = device_id
        self.control = control
        self._attr_is_on = bool(value)
        self._attr_device_info = device_info
        self._attr_name = f"v412 Device {device_id} {control}"
        self._attr_unique_id = f"{device_id}_{control}_v412ctl"

    async def async_turn_on(self, **kwargs):
        success = await self.api_client.set_control(self.device_id, self.control, 1)
        if success:
            self._attr_is_on = True
        else:
            _LOGGER.error(
                f"Failed to turn on {self.control} on device {self.device_id}"
            )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.api_client.set_control(self.device_id, self.control, 0)
        if success:
            self._attr_is_on = False
        else:
            _LOGGER.error(
                f"Failed to turn off {self.control} on device {self.device_id}"
            )
        self.async_write_ha_state()


async def async_update(self):
    value = await self.api_client.get_control(self.device_id, self.control)
    if value is not None:
        self._attr_is_on = bool(int(value))
    else:
        _LOGGER.error(f"Failed to update {self.control} on device {self.device_id}")
