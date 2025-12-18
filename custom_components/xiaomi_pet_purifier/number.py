"""Number platform for Xiaomi Pet Air Purifier."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FAN_SPEED_MAX,
    FAN_SPEED_MIN,
    PIID_BRIGHTNESS,
    PIID_FAN_LEVEL,
    SIID_FAVORITE,
    SIID_SCREEN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Pet Air Purifier")

    numbers = [
        XiaomiPetAirPurifierNumber(
            coordinator,
            name,
            "brightness",
            "mdi:brightness-6",
            0,
            2,
            1,
            SIID_SCREEN,
            PIID_BRIGHTNESS,
        ),
        XiaomiPetAirPurifierNumber(
            coordinator,
            name,
            "fan_level",
            "mdi:weather-windy",
            FAN_SPEED_MIN,
            FAN_SPEED_MAX,
            1,
            SIID_FAVORITE,
            PIID_FAN_LEVEL,
        ),
    ]

    async_add_entities(numbers, True)


class XiaomiPetAirPurifierNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Xiaomi Pet Air Purifier number entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        device_name: str,
        number_type: str,
        icon: str,
        min_value: int,
        max_value: int,
        step: int,
        siid: int,
        piid: int,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._number_type = number_type
        self._siid = siid
        self._piid = piid
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{number_type}"
        self._attr_icon = icon
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": device_name,
            "manufacturer": "Xiaomi",
            "model": "Smart Pet Care Air Purifier (CPA5)",
        }
        self._attr_translation_key = number_type

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get(self._number_type)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            # Optimistic update
            self.coordinator.data[self._number_type] = int(value)
            self.async_write_ha_state()

            await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [
                    {
                        "did": self._number_type,
                        "siid": self._siid,
                        "piid": self._piid,
                        "value": int(value),
                    }
                ],
            )
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            _LOGGER.error("Failed to set %s: %s", self._number_type, ex)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
