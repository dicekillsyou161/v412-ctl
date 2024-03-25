"""Number platform for v412-ctl integration."""
import logging
from homeassistant.components.number import NumberEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    api_client = hass.data[DOMAIN][entry.entry_id]["api_client"]
    controls = hass.data[DOMAIN][entry.entry_id]["controls"]
    entities = []

    for device_id, device_data in controls.items():
        device_controls = device_data["controls"]
        for control, details in device_controls.items():
            if details["type"] == "int":
                entities.append(
                    ControlNumber(
                        api_client,
                        device_id,
                        control,
                        device_data["device_info"],
                        details["min"],
                        details["max"],
                        details["step"],
                        details["value"],
                    )
                )

    async_add_entities(entities)


class ControlNumber(NumberEntity):
    def __init__(
        self, api_client, device_id, control, device_info, min_val, max_val, step, value
    ):
        self.api_client = api_client
        self.device_id = device_id
        self.control = control
        self._attr_device_info = device_info
        self._attr_name = f"{control}.D{device_id}_v412ctl"
        self._attr_unique_id = f"{control}.d{device_id}_v412ctl"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_native_value = value

    async def async_set_value(self, value: float):
        if await self.api_client.set_control(self.device_id, self.control, value):
            self._attr_native_value = value
            self.async_write_ha_state()
