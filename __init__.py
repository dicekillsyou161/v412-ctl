"""The v412-ctl integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.NUMBER]
_LOGGER = logging.getLogger(__name__)


class CameraControlAPI:
    def __init__(self, hass, base_url, api_key):
        self.hass = hass
        self.base_url = base_url
        self.api_key = api_key

    async def list_controls(self, device):
        url = f"{self.base_url}/list-controls?device={device}"
        response = await self.hass.helpers.aiohttp_client.async_get_clientsession().get(
            url, headers={"Authorization": self.api_key}
        )
        if response.status == 200:
            return await response.json()
        else:
            _LOGGER.error(
                "Failed to list controls for device %s, status code %s",
                device,
                response.status,
            )
            return {}

    async def get_control(self, device, control):
        url = f"{self.base_url}/camera-status?device={device}&controls={control}"
        response = await self.hass.helpers.aiohttp_client.async_get_clientsession().get(
            url, headers={"Authorization": self.api_key}
        )
        if response.status == 200:
            control_data = await response.json()
            return control_data.get(control, {}).get("value")
        else:
            _LOGGER.error(
                "Failed to retrieve value for control %s on device %s: HTTP %s",
                control,
                device,
                response.status,
            )
            return None

    async def set_control(self, device, control, value):
        url = f"{self.base_url}/camera-control"
        data = {"device": device, "controls": {control: value}}
        response = (
            await self.hass.helpers.aiohttp_client.async_get_clientsession().post(
                url, json=data, headers={"Authorization": self.api_key}
            )
        )
        if response.status == 200:
            return True
        else:
            _LOGGER.error(
                "Failed to set value for control %s on device %s: HTTP %s",
                control,
                device,
                response.status,
            )
            return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    api_client = CameraControlAPI(hass, entry.data["base_url"], entry.data["api_key"])
    device_registry = async_get_device_registry(hass)

    devices_data = ["0", "2"]
    controls = {}
    for device_id in devices_data:
        device_controls = await api_client.list_controls(device_id)
        device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": f"v412 Device {device_id}",
            "manufacturer": "v412",
            "model": "Webcam",
        }
        # Here we don't pass device directly to device_info in entity
        device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id, **device_info
        )
        if device_controls:
            controls[device_id] = {
                "device_info": device_info,  # Pass device_info instead of device
                "controls": device_controls,
            }
        else:
            _LOGGER.error("No controls fetched for device %s.", device_id)

    hass.data[DOMAIN][entry.entry_id] = {"api_client": api_client, "controls": controls}

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
