"""Config flow for v412ctl integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .const import CONF_API_KEY, CONF_BASE_URL, DOMAIN


class V412CtlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for v412ctl."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Here you can add checks to validate user input, like testing connection to the device
            session = aiohttp_client.async_get_clientsession(self.hass)
            base_url = user_input[CONF_BASE_URL]
            api_key = user_input[CONF_API_KEY]

            # Suppose you have a function to validate connection, you should implement it
            # valid = await validate_connection(base_url, api_key, session)

            valid = True  # Remove this line after implementing validation
            if valid:
                return self.async_create_entry(title="v412ctl", data=user_input)
            else:
                errors["base"] = "connection_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_BASE_URL,
                        description={"suggested_value": "http://camera-ip:port"},
                    ): str,
                    vol.Required(
                        CONF_API_KEY, description={"suggested_value": "Your API Key"}
                    ): str,
                }
            ),
            errors=errors,
        )
