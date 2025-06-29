# Battery Monitoring System 🔋

A fun and efficient battery monitoring system that helps you maintain optimal battery health with style!

## Features
- Background battery monitoring
- System tray icon for easy control
- Fun notifications when battery is too low or too high
- Automatic startup capability
- Easy to enable/disable

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. To add to startup (optional):
```bash
python startup_config.py --add
```

## Usage

1. Run the monitor:
```bash
python battery_monitor.py
```

2. Control via System Tray:
- Look for the green circle icon in your system tray
- Right-click to access the menu
- Toggle monitoring on/off
- Exit the application

## Notifications
- Below 20%: Reminds you to plug in your charger
- Above 85%: Reminds you to unplug your charger
- Notifications appear every 30 seconds when conditions are met

## Remove from Startup
```bash
python startup_config.py --remove
```

## Requirements
- Windows OS
- Python 3.6+
- Internet connection for initial setup

## Dependencies
- psutil
- plyer
- pystray
- Pillow
