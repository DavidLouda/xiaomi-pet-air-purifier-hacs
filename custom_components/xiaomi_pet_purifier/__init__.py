"""Xiaomi Pet Air Purifier integration."""
import logging
from datetime import timedelta

from miio import Device, DeviceException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.FAN, Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi Pet Air Purifier from a config entry."""
    host = entry.data[CONF_HOST]
    token = entry.data[CONF_TOKEN]

    device = Device(host, token)

    # Test connection
    try:
        await hass.async_add_executor_job(device.info)
    except DeviceException as ex:
        raise ConfigEntryNotReady(f"Unable to connect to device: {ex}") from ex

    # Create coordinator
    coordinator = XiaomiPetAirPurifierCoordinator(hass, device, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class XiaomiPetAirPurifierCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data updates."""

    def __init__(
        self, hass: HomeAssistant, device: Device, entry: ConfigEntry
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.device = device
        self.entry = entry

    async def _async_update_data(self):
        """Fetch data from device."""
        try:
            return await self.hass.async_add_executor_job(self._get_data)
        except DeviceException as ex:
            raise UpdateFailed(f"Error communicating with device: {ex}") from ex

    def _get_data(self):
        """Get data from device (runs in executor)."""
        properties = [
            {"did": "power", "siid": 2, "piid": 1},
            {"did": "mode", "siid": 2, "piid": 5},
            {"did": "pm25", "siid": 3, "piid": 1},
            {"did": "filter_life", "siid": 4, "piid": 1},
            {"did": "filter_used_time", "siid": 4, "piid": 2},
            {"did": "filter_left_time", "siid": 4, "piid": 3},
            {"did": "brightness", "siid": 5, "piid": 1},
            {"did": "alarm", "siid": 6, "piid": 1},
            {"did": "child_lock", "siid": 7, "piid": 1},
            {"did": "fan_level", "siid": 8, "piid": 1},
        ]

        response = self.device.send("get_properties", properties)

        data = {}
        for item in response:
            if "value" in item:
                data[item["did"]] = item["value"]

        return data
