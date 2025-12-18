"""Config flow for Xiaomi Pet Air Purifier integration."""
import logging
from typing import Any

import voluptuous as vol
from miio import Device, DeviceException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, MODEL_CPA5

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_TOKEN): str,
        vol.Optional(CONF_NAME, default="Pet Air Purifier"): str,
    }
)


class XiaomiPetAirPurifierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Pet Air Purifier."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            token = user_input[CONF_TOKEN]

            # Test connection
            device = Device(host, token)
            try:
                info = await self.hass.async_add_executor_job(device.info)
                model = info.model

                # Check if model is supported
                if model not in [MODEL_CPA5, "xiaomi.airp.cpa4"]:
                    _LOGGER.warning(
                        "Device model %s may not be fully supported. Expected %s",
                        model,
                        MODEL_CPA5,
                    )

                # Check if already configured
                await self.async_set_unique_id(info.mac_address)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Pet Air Purifier"),
                    data={
                        CONF_HOST: host,
                        CONF_TOKEN: token,
                        CONF_NAME: user_input.get(CONF_NAME, "Pet Air Purifier"),
                    },
                )

            except DeviceException:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
