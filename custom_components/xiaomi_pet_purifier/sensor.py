"""Sensor platform for Xiaomi Pet Air Purifier."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Pet Air Purifier")

    sensors = [
        XiaomiPetAirPurifierSensor(
            coordinator,
            name,
            "pm25",
            "mdi:air-filter",
            "µg/m³",
            SensorDeviceClass.PM25,
            SensorStateClass.MEASUREMENT,
        ),
        XiaomiPetAirPurifierSensor(
            coordinator,
            name,
            "filter_life",
            "mdi:air-filter",
            PERCENTAGE,
            None,
            SensorStateClass.MEASUREMENT,
        ),
        XiaomiPetAirPurifierSensor(
            coordinator,
            name,
            "filter_used_time",
            "mdi:clock-outline",
            UnitOfTime.DAYS,
            None,
            SensorStateClass.TOTAL_INCREASING,
        ),
        XiaomiPetAirPurifierSensor(
            coordinator,
            name,
            "filter_left_time",
            "mdi:clock-outline",
            UnitOfTime.DAYS,
            None,
            SensorStateClass.MEASUREMENT,
        ),
    ]

    async_add_entities(sensors, True)


class XiaomiPetAirPurifierSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Xiaomi Pet Air Purifier sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        device_name: str,
        sensor_type: str,
        icon: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{sensor_type}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": device_name,
            "manufacturer": "Xiaomi",
            "model": "Smart Pet Care Air Purifier (CPA5)",
        }
        self._attr_translation_key = sensor_type

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_type)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
