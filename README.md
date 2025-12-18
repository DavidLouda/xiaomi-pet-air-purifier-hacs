# Xiaomi Pet Air Purifier for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/DavidLouda/xiaomi-pet-air-purifier-hacs.svg)](https://github.com/DavidLouda/xiaomi-pet-air-purifier-hacs/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Custom Home Assistant integration for **Xiaomi Smart Pet Care Air Purifier (xiaomi.airp.cpa5)**.

## Features

- ✅ Full control via Home Assistant
- 🎛️ **Fan entity** with speed control (1-17 levels)
- 📊 **Sensors**: PM2.5, Filter life, Filter usage time
- 🔒 **Switches**: Child lock, Buzzer/Alarm
- 💡 **Number entity**: Display brightness control
- 🌐 **Preset modes**: Auto, Sleep, Favorite
- 🔄 Auto-discovery and easy setup via UI

## Supported Models

- `xiaomi.airp.cpa5` - Xiaomi Smart Pet Care Air Purifier ✅ Tested

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **three dots** in the top right corner
4. Select **Custom repositories**
5. Add this repository URL: `https://github.com/DavidLouda/xiaomi-pet-air-purifier-hacs`
6. Category: **Integration**
7. Click **Add**
8. Find **Xiaomi Pet Air Purifier** in HACS and click **Download**
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from [Releases](https://github.com/DavidLouda/xiaomi-pet-air-purifier-hacs/releases)
2. Extract the `custom_components/xiaomi_pet_purifier` folder
3. Copy it to your Home Assistant `config/custom_components/` directory
4. Restart Home Assistant

## Configuration

### Prerequisites

Before adding the integration, you need:
- **IP address** of your air purifier
- **Token** (32-character hex string)

#### Getting the Token

**Method 1: Using micloud**
```bash
pip install micloud python-miio

python3 << 'SCRIPT'
from micloud import MiCloud
import getpass

user = input("Xiaomi email: ")
pwd = getpass.getpass("Password: ")
region = input("Region (cn/de/us/sg/ru/i2): ") or "de"

mc = MiCloud(user, pwd)
if mc.login():
    for d in mc.get_devices(country=region):
        if "airp.cpa5" in d.get("model", ""):
            print(f"\nName: {d['name']}")
            print(f"Token: {d['token']}")
            print(f"IP: {d.get('localip','offline')}")
else:
    print("Login failed!")
SCRIPT
```

**Method 2: Using miiocli**
```bash
pip install python-miio
miiocli cloud
```

### Setup via UI

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** (bottom right)
3. Search for **Xiaomi Pet Air Purifier**
4. Enter:
   - **IP Address**: Your purifier's IP (e.g., `192.168.1.137`)
   - **Token**: 32-character token
   - **Name**: Custom name (optional)
5. Click **Submit**

The integration will create:
- **1 Fan entity** (main control)
- **4 Sensors** (PM2.5, filter life, used time, remaining time)
- **2 Switches** (child lock, buzzer)
- **1 Number entity** (brightness)

## Entities

### Fan: `fan.pet_air_purifier`

Control the air purifier:
- **Turn on/off**
- **Set speed** (1-100%, maps to fan levels 1-17)
- **Change mode**: Auto, Sleep, Favorite

**Attributes:**
- `pm25`: Current PM2.5 level
- `fan_level`: Raw fan level (1-17)
- `mode_value`: Raw mode value
- `filter_life_remaining`: Filter life percentage
- `filter_used_days`: Days filter has been used
- `filter_left_days`: Days remaining before replacement

### Sensors

- **PM2.5**: Air quality in µg/m³
- **Filter Life Remaining**: Percentage (%)
- **Filter Used Time**: Days used
- **Filter Time Remaining**: Days remaining

### Switches

- **Child Lock**: Prevent physical button presses
- **Buzzer**: Enable/disable sound alerts

### Number

- **Display Brightness**: 
  - `0` = Off
  - `1` = Dim  
  - `2` = Bright

## Usage Examples

### Automation: Turn on when PM2.5 is high
```yaml
automation:
  - alias: "Air Purifier Auto On"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pet_air_purifier_pm2_5
        above: 35
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.pet_air_purifier
        data:
          preset_mode: "Auto"
```

### Automation: Sleep mode at night
```yaml
automation:
  - alias: "Air Purifier Night Mode"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: fan.set_preset_mode
        target:
          entity_id: fan.pet_air_purifier
        data:
          preset_mode: "Sleep"
      - service: number.set_value
        target:
          entity_id: number.pet_air_purifier_display_brightness
        data:
          value: 0
```

### Script: Boost purification
```yaml
script:
  purifier_boost:
    sequence:
      - service: fan.turn_on
        target:
          entity_id: fan.pet_air_purifier
        data:
          preset_mode: "Favorite"
          percentage: 100
```

### Lovelace Card Example
```yaml
type: entities
title: Air Purifier
entities:
  - entity: fan.pet_air_purifier
  - entity: sensor.pet_air_purifier_pm2_5
  - entity: sensor.pet_air_purifier_filter_life_remaining
  - entity: switch.pet_air_purifier_child_lock
  - entity: number.pet_air_purifier_display_brightness
```

## Troubleshooting

### Device not connecting

1. **Check IP address**: Ensure the purifier is on the same network
2. **Verify token**: Token must be exactly 32 hex characters
3. **Firewall**: Ensure UDP port 54321 is not blocked
4. **Check logs**: Settings → System → Logs → Search for `xiaomi_pet_purifier`

### Entity not updating

- The integration polls every 30 seconds
- Check if device is online in Mi Home app
- Restart Home Assistant

### Token changed

If you reset the device or re-pair it in Mi Home app, the token changes:
1. Get new token (see Configuration section)
2. Go to Settings → Devices & Services → Xiaomi Pet Air Purifier
3. Click **Configure**
4. Enter new token

## Development

### Testing locally
```bash
# Clone repository
git clone https://github.com/DavidLouda/xiaomi-pet-air-purifier-hacs.git
cd xiaomi-pet-air-purifier-hacs

# Copy to HA config
cp -r custom_components/xiaomi_pet_purifier /path/to/homeassistant/custom_components/

# Restart Home Assistant
```

### Manual device communication test
```bash
pip install python-miio

# Test connection
python3 -m miio.cli device --ip YOUR_IP --token YOUR_TOKEN info

# Get status
python3 -m miio.cli genericmiot --ip YOUR_IP --token YOUR_TOKEN status
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/DavidLouda/xiaomi-pet-air-purifier-hacs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DavidLouda/xiaomi-pet-air-purifier-hacs/discussions)

## Credits

- Based on [python-miio](https://github.com/rytilahti/python-miio) by @rytilahti
- Inspired by other Xiaomi integrations in Home Assistant

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details

## Changelog

### v1.0.0 (2024-12-18)
- Initial release
- Support for xiaomi.airp.cpa5
- Fan control with speed and modes
- PM2.5 and filter sensors
- Child lock and buzzer switches
- Display brightness control
