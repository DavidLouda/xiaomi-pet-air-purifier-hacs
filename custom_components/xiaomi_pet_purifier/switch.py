"""Switch platform for Xiaomi Pet Air Purifier."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    PIID_ALARM,
    PIID_CHILD_LOCK,
    SIID_ALARM,
    SIID_PHYSICAL_CONTROLS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Pet Air Purifier")

    switches = [
        XiaomiPetAirPurifierSwitch(
            coordinator,
            name,
            "child_lock",
            "mdi:lock",
            SIID_PHYSICAL_CONTROLS,
            PIID_CHILD_LOCK,
        ),
        XiaomiPetAirPurifierSwitch(
            coordinator,
            name,
            "alarm",
            "mdi:volume-high",
            SIID_ALARM,
            PIID_ALARM,
        ),
    ]

    async_add_entities(switches, True)


class XiaomiPetAirPurifierSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Xiaomi Pet Air Purifier switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        device_name: str,
        switch_type: str,
        icon: str,
        siid: int,
        piid: int,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._switch_type = switch_type
        self._siid = siid
        self._piid = piid
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{switch_type}"
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": device_name,
            "manufacturer": "Xiaomi",
            "model": "Smart Pet Care Air Purifier (CPA5)",
        }
        self._attr_translation_key = switch_type

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get(self._switch_type, False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        try:
            # Optimistic update
            self.coordinator.data[self._switch_type] = True
            self.async_write_ha_state()

            await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [
                    {
                        "did": self._switch_type,
                        "siid": self._siid,
                        "piid": self._piid,
                        "value": True,
                    }
                ],
            )
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            # Revert on failure
            self.coordinator.data[self._switch_type] = False
            self.async_write_ha_state()
            _LOGGER.error("Failed to turn on %s: %s", self._switch_type, ex)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        try:
            # Optimistic update
            self.coordinator.data[self._switch_type] = False
            self.async_write_ha_state()

            await self.hass.async_add_executor_job(
                self.coordinator.device.send,
                "set_properties",
                [
                    {
                        "did": self._switch_type,
                        "siid": self._siid,
                        "piid": self._piid,
                        "value": False,
                    }
                ],
            )
            await self.coordinator.async_request_refresh()

        except Exception as ex:
            # Revert on failure
            self.coordinator.data[self._switch_type] = True
            self.async_write_ha_state()
            _LOGGER.error("Failed to turn off %s: %s", self._switch_type, ex)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
