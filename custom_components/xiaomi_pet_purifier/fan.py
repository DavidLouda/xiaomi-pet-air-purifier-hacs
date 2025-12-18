"""Fan platform for Xiaomi Pet Air Purifier."""
import asyncio
import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import (
    DOMAIN,
    FAN_SPEED_MAX,
    FAN_SPEED_MIN,
    MODE_AUTO,
    MODE_FAVORITE,
    MODE_SLEEP,
    PRESET_MODES,
)

_LOGGER = logging.getLogger(__name__)

SPEED_RANGE = (FAN_SPEED_MIN, FAN_SPEED_MAX)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fan platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Pet Air Purifier")

    async_add_entities([XiaomiPetAirPurifierFan(coordinator, name)], True)


class XiaomiPetAirPurifierFan(CoordinatorEntity, FanEntity):
    """Representation of Xiaomi Pet Air Purifier as a fan."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator, name: str) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_fan"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": name,
            "manufacturer": "Xiaomi",
            "model": "Smart Pet Care Air Purifier (CPA5)",
        }
        self._attr_preset_modes = PRESET_MODES
        self._attr_speed_count = int_states_in_range(SPEED_RANGE)

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return FanEntityFeature.PRESET_MODE | FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF

    @property
    def is_on(self) -> bool:
        """Return true if fan is on."""
        return self.coordinator.data.get("power", False)

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        mode = self.coordinator.data.get("mode")
        mode_map = {MODE_AUTO: "Auto", MODE_SLEEP: "Sleep", MODE_FAVORITE: "Favorite"}
        return mode_map.get(mode)

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.preset_mode != "Favorite":
            return None

        fan_level = self.coordinator.data.get("fan_level")
        if fan_level is None:
            return None

        return ranged_value_to_percentage(SPEED_RANGE, fan_level)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "pm25": self.coordinator.data.get("pm25"),
            "fan_level": self.coordinator.data.get("fan_level"),
            "mode_value": self.coordinator.data.get("mode"),
            "filter_life_remaining": self.coordinator.data.get("filter_life"),
            "filter_used_days": self.coordinator.data.get("filter_used_time"),
            "filter_left_days": self.coordinator.data.get("filter_left_time"),
        }

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        _LOGGER.debug("Turn on called with percentage=%s, preset_mode=%s", percentage, preset_mode)
        
        try:
            # First turn on the device
            result = await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [{"siid": 2, "piid": 1, "value": True}],
            )
            _LOGGER.debug("Turn on result: %s", result)

            # Wait a moment for device to turn on
            await asyncio.sleep(0.5)

            if preset_mode:
                await self.async_set_preset_mode(preset_mode)
            elif percentage is not None:
                await self.async_set_percentage(percentage)

            await self.coordinator.async_request_refresh()

        except Exception as ex:
            _LOGGER.error("Failed to turn on: %s", ex, exc_info=True)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        _LOGGER.debug("Turn off called")
        
        try:
            result = await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [{"siid": 2, "piid": 1, "value": False}],
            )
            _LOGGER.debug("Turn off result: %s", result)
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            _LOGGER.error("Failed to turn off: %s", ex, exc_info=True)
            raise

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        mode_map = {"Auto": MODE_AUTO, "Sleep": MODE_SLEEP, "Favorite": MODE_FAVORITE}
        mode_value = mode_map.get(preset_mode)

        if mode_value is None:
            _LOGGER.error("Invalid preset mode: %s", preset_mode)
            return

        _LOGGER.debug("Setting preset mode to %s (value=%s)", preset_mode, mode_value)

        try:
            result = await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [{"siid": 2, "piid": 5, "value": mode_value}],
            )
            _LOGGER.debug("Set preset mode result: %s", result)
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            _LOGGER.error("Failed to set preset mode: %s", ex, exc_info=True)
            raise

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage."""
        if percentage == 0:
            await self.async_turn_off()
            return

        fan_level = percentage_to_ranged_value(SPEED_RANGE, percentage)
        _LOGGER.debug("Setting percentage to %s (fan_level=%s)", percentage, fan_level)

        try:
            # First set to Favorite mode
            result1 = await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [{"siid": 2, "piid": 5, "value": MODE_FAVORITE}],
            )
            _LOGGER.debug("Set mode to Favorite result: %s", result1)

            await asyncio.sleep(0.3)

            # Then set fan level
            result2 = await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [{"siid": 8, "piid": 1, "value": fan_level}],
            )
            _LOGGER.debug("Set fan level result: %s", result2)
            
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            _LOGGER.error("Failed to set fan level: %s", ex, exc_info=True)
            raise

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
