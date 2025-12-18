"""Constants for Xiaomi Pet Air Purifier integration."""
from typing import Final

DOMAIN: Final = "xiaomi_pet_purifier"
CONF_MODEL: Final = "model"

# Device models
MODEL_CPA5: Final = "xiaomi.airp.cpa5"

# Update interval
SCAN_INTERVAL: Final = 30  # seconds

# MIoT service and property IDs
SIID_AIR_PURIFIER: Final = 2
PIID_POWER: Final = 1
PIID_MODE: Final = 5

SIID_ENVIRONMENT: Final = 3
PIID_PM25: Final = 1

SIID_FILTER: Final = 4
PIID_FILTER_LIFE: Final = 1
PIID_FILTER_USED_TIME: Final = 2
PIID_FILTER_LEFT_TIME: Final = 3

SIID_SCREEN: Final = 5
PIID_BRIGHTNESS: Final = 1

SIID_ALARM: Final = 6
PIID_ALARM: Final = 1

SIID_PHYSICAL_CONTROLS: Final = 7
PIID_CHILD_LOCK: Final = 1

SIID_FAVORITE: Final = 8
PIID_FAN_LEVEL: Final = 1

# Modes
MODE_AUTO: Final = 0
MODE_SLEEP: Final = 1
MODE_FAVORITE: Final = 2

PRESET_MODES: Final = ["Auto", "Sleep", "Favorite"]

# Brightness levels
BRIGHTNESS_OFF: Final = 0
BRIGHTNESS_DIM: Final = 1
BRIGHTNESS_BRIGHT: Final = 2

# Fan speed range
FAN_SPEED_MIN: Final = 1
FAN_SPEED_MAX: Final = 17
