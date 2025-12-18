"""Select platform for Xiaomi Pet Air Purifier."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_AUTO, MODE_FAVORITE, MODE_SLEEP, PIID_MODE, SIID_AIR_PURIFIER

_LOGGER = logging.getLogger(__name__)

MODE_TO_VALUE = {
    "Auto": MODE_AUTO,
    "Sleep": MODE_SLEEP,
    "Favorite": MODE_FAVORITE,
}
VALUE_TO_MODE = {v: k for k, v in MODE_TO_VALUE.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Pet Air Purifier")

    async_add_entities(
        [XiaomiPetAirPurifierModeSelect(coordinator, name)],
        True,
    )


class XiaomiPetAirPurifierModeSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Xiaomi Pet Air Purifier mode select."""

    _attr_has_entity_name = True
    _attr_translation_key = "mode"

    def __init__(self, coordinator, device_name: str) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_mode"
        self._attr_options = list(MODE_TO_VALUE.keys())
        self._attr_icon = "mdi:air-purifier"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": device_name,
            "manufacturer": "Xiaomi",
            "model": "Smart Pet Care Air Purifier (CPA5)",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        mode_value = self.coordinator.data.get("mode")
        return VALUE_TO_MODE.get(mode_value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = MODE_TO_VALUE.get(option)
        if value is None:
            return

        try:
            # Optimistic update
            self.coordinator.data["mode"] = value
            self.async_write_ha_state()

            await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [
                    {
                        "did": "mode",
                        "siid": SIID_AIR_PURIFIER,
                        "piid": PIID_MODE,
                        "value": value,
                    }
                ],
            )
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            _LOGGER.error("Failed to set mode to %s: %s", option, ex)
