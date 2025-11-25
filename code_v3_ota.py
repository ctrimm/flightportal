"""
Flight Portal v3 - OTA Update Support
MatrixPortal flight display with web-based configuration and OTA firmware updates
"""

import time
from random import randrange
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_portalbase.network import HttpError
import adafruit_requests as requests
import json
import storage
import microcontroller

import adafruit_display_text.label
import displayio
import framebufferio
import rgbmatrix
import gc

import busio
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager

from microcontroller import watchdog as w
from watchdog import WatchDogMode

w.timeout = 16  # timeout in seconds
w.mode = WatchDogMode.RESET

FONT = terminalio.FONT

# Firmware version - increment with each release
FIRMWARE_VERSION = "3.0.0"

# Try to import secrets for backward compatibility
try:
    from secrets import secrets
except ImportError:
    print("No secrets.py found, will use config server")
    secrets = {
        'ssid': 'your-network',
        'password': 'your-password',
        'bounds_box': '51.6,51.4,-0.3,-0.1'
    }

# ==================== Configuration ====================

# Web server configuration (where to fetch config from)
CONFIG_SERVER = "flightportal:3100"  # or "localhost:3100" or "192.168.1.x:3100"
CONFIG_URL = f"http://{CONFIG_SERVER}/api/config"
LAYOUTS_URL = f"http://{CONFIG_SERVER}/api/layouts"
FIRMWARE_CHECK_URL = f"http://{CONFIG_SERVER}/api/firmware/check"
FIRMWARE_DOWNLOAD_URL = f"http://{CONFIG_SERVER}/api/firmware/download"

CONFIG_FETCH_INTERVAL = 300  # Fetch config every 5 minutes
FIRMWARE_CHECK_INTERVAL = 3600  # Check for updates every hour

# Default configuration (used if config server is unavailable)
DEFAULT_CONFIG = {
    "query_delay": 30,
    "active_layout": "classic",
    "display": {
        "plane_color": "0x4B0082",
        "plane_speed": 0.04,
        "text_speed": 0.04,
        "pause_between_scrolling": 3
    },
    "ota": {
        "enabled": True,
        "auto_update": False,  # If true, updates automatically without user confirmation
        "check_interval": 3600
    }
}

# Current configuration (loaded from server or defaults)
config = DEFAULT_CONFIG.copy()
current_layout = None
last_config_fetch = 0
last_firmware_check = 0

# FlightRadar24 API URLs
FLIGHT_SEARCH_HEAD = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
FLIGHT_SEARCH_TAIL = "&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=1"

FLIGHT_LONG_DETAILS_HEAD = "https://data-live.flightradar24.com/clickhandler/?flight="

# Request headers
rheaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "cache-control": "no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
    "accept": "application/json"
}

# ==================== Hardware Setup ====================

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light, debug=False, attempts=1)

# MatrixPortal object
matrixportal = MatrixPortal(
    headers=rheaders,
    esp=esp,
    rotation=0,
    debug=False
)

# Memory management - static buffer for JSON
json_size = 14336
json_bytes = bytearray(json_size)

# ==================== Display Setup ====================

# Display group for labels
display_group = displayio.Group()
matrixportal.display.show(display_group)

# Labels list (will be populated based on layout)
labels = []

# Plane sprite
planeBmp = displayio.Bitmap(12, 12, 2)
planePalette = displayio.Palette(2)
planePalette[1] = int(config["display"]["plane_color"], 16)
planePalette[0] = 0x000000

# Draw plane bitmap
planeBmp[6,0]=planeBmp[6,1]=planeBmp[5,1]=planeBmp[4,2]=planeBmp[5,2]=planeBmp[6,2]=1
planeBmp[9,3]=planeBmp[5,3]=planeBmp[4,3]=planeBmp[3,3]=1
planeBmp[1,4]=planeBmp[2,4]=planeBmp[3,4]=planeBmp[4,4]=planeBmp[5,4]=planeBmp[6,4]=planeBmp[7,4]=planeBmp[8,4]=planeBmp[9,4]=1
planeBmp[1,5]=planeBmp[2,5]=planeBmp[3,5]=planeBmp[4,5]=planeBmp[5,5]=planeBmp[6,5]=planeBmp[7,5]=planeBmp[8,5]=planeBmp[9,5]=1
planeBmp[9,6]=planeBmp[5,6]=planeBmp[4,6]=planeBmp[3,6]=1
planeBmp[6,9]=planeBmp[6,8]=planeBmp[5,8]=planeBmp[4,7]=planeBmp[5,7]=planeBmp[6,7]=1

planeTg = displayio.TileGrid(planeBmp, pixel_shader=planePalette)
planeG = displayio.Group(x=matrixportal.display.width + 12, y=10)
planeG.append(planeTg)

# ==================== OTA Update Functions ====================

def check_for_firmware_update():
    """Check if a firmware update is available"""
    global last_firmware_check

    try:
        print(f"Checking for firmware updates (current version: {FIRMWARE_VERSION})...")

        # Send current version to server
        check_url = f"{FIRMWARE_CHECK_URL}?version={FIRMWARE_VERSION}"
        response = requests.get(url=check_url, headers=rheaders, timeout=10)
        update_info = response.json()

        last_firmware_check = time.monotonic()

        if update_info.get('update_available'):
            new_version = update_info.get('version')
            print(f"Firmware update available: {new_version}")
            print(f"Changes: {update_info.get('changelog', 'No changelog available')}")

            return {
                'available': True,
                'version': new_version,
                'changelog': update_info.get('changelog', ''),
                'url': update_info.get('download_url', FIRMWARE_DOWNLOAD_URL)
            }
        else:
            print("Firmware is up to date")
            return {'available': False}

    except Exception as e:
        print(f"Error checking for firmware update: {e}")
        return {'available': False}


def download_and_install_update(update_info):
    """Download and install firmware update"""
    try:
        print(f"Downloading firmware version {update_info['version']}...")

        # Download new firmware
        download_url = update_info.get('url', FIRMWARE_DOWNLOAD_URL)
        response = requests.get(url=download_url, headers=rheaders, timeout=30)

        if response.status_code != 200:
            print(f"Download failed with status {response.status_code}")
            return False

        new_code = response.text

        # Verify downloaded code (basic sanity check)
        if len(new_code) < 1000 or "Flight Portal" not in new_code:
            print("Downloaded code failed sanity check")
            return False

        print(f"Downloaded {len(new_code)} bytes")

        # Remount filesystem as writable
        try:
            storage.remount("/", False)
        except Exception as e:
            print(f"Could not remount filesystem: {e}")
            return False

        # Backup current code
        print("Backing up current firmware...")
        try:
            with open("/code.py", "r") as f:
                old_code = f.read()
            with open("/code.backup", "w") as f:
                f.write(old_code)
            print("Backup created")
        except Exception as e:
            print(f"Backup failed: {e}")
            # Continue anyway

        # Write new code
        print("Installing new firmware...")
        try:
            with open("/code.py", "w") as f:
                f.write(new_code)
            print("Firmware installed successfully")
        except Exception as e:
            print(f"Installation failed: {e}")
            # Try to restore backup
            try:
                print("Attempting to restore backup...")
                with open("/code.backup", "r") as f:
                    backup = f.read()
                with open("/code.py", "w") as f:
                    f.write(backup)
                print("Backup restored")
            except:
                print("CRITICAL: Backup restoration failed!")
            return False

        # Remount filesystem as read-only
        try:
            storage.remount("/", True)
        except:
            pass

        print("Update complete! Restarting in 3 seconds...")
        time.sleep(3)
        microcontroller.reset()

        return True

    except Exception as e:
        print(f"Error during update: {e}")
        return False


def handle_ota_update():
    """Check for and optionally install firmware updates"""
    global config, last_firmware_check

    # Check if OTA is enabled in config
    if not config.get('ota', {}).get('enabled', True):
        return

    # Check if it's time to check for updates
    check_interval = config.get('ota', {}).get('check_interval', FIRMWARE_CHECK_INTERVAL)
    if (time.monotonic() - last_firmware_check) < check_interval:
        return

    # Check for updates
    update_info = check_for_firmware_update()

    if not update_info.get('available'):
        return

    # Display update notification on screen
    display_update_notification(update_info['version'])

    # Auto-update or wait for user confirmation
    auto_update = config.get('ota', {}).get('auto_update', False)

    if auto_update:
        print("Auto-update enabled, installing update...")
        download_and_install_update(update_info)
    else:
        print("Update available but auto-update disabled")
        print("Set 'ota.auto_update: true' in config to enable automatic updates")
        # In a real implementation, you might have a button to trigger the update
        # For now, we'll wait for the next config fetch to enable it


def display_update_notification(version):
    """Display update notification on LED matrix"""
    # Clear display
    for label_data in labels:
        label_data['label'].text = ""

    # Create temporary label for notification
    if len(labels) > 0:
        labels[0]['label'].text = "UPDATE"
        if len(labels) > 1:
            labels[1]['label'].text = f"v{version}"
        if len(labels) > 2:
            labels[2]['label'].text = "AVAILABLE"

    time.sleep(3)

# ==================== Configuration Functions ====================
# (Same as code_v2.py - not repeating for brevity)

def hex_to_int(hex_string):
    """Convert hex string like '0xEE82EE' to integer"""
    try:
        return int(hex_string, 16)
    except (ValueError, TypeError):
        return 0xFFFFFF


def fetch_config():
    """Fetch configuration from web server"""
    global config, current_layout, last_config_fetch

    try:
        print("Fetching configuration from server...")
        response = requests.get(url=CONFIG_URL, headers=rheaders, timeout=10)
        server_config = response.json()

        if server_config:
            config = server_config
            print(f"Config loaded: Layout={config.get('active_layout')}, QueryDelay={config.get('query_delay')}")

            # Fetch active layout
            active_layout_id = config.get('active_layout', 'classic')
            try:
                layouts_response = requests.get(url=LAYOUTS_URL, headers=rheaders, timeout=10)
                layouts_data = layouts_response.json()

                for layout in layouts_data.get('layouts', []):
                    if layout['id'] == active_layout_id:
                        current_layout = layout
                        print(f"Loaded layout: {layout['name']} ({len(layout.get('rows', []))} rows)")
                        break
            except Exception as e:
                print(f"Error loading layout: {e}")

            last_config_fetch = time.monotonic()

            # Update WiFi settings if they changed
            if 'wifi' in config:
                secrets['ssid'] = config['wifi'].get('ssid', secrets.get('ssid'))
                secrets['password'] = config['wifi'].get('password', secrets.get('password'))

            # Update bounds box
            if 'location' in config:
                secrets['bounds_box'] = config['location'].get('bounds_box', secrets.get('bounds_box'))

            return True
    except Exception as e:
        print(f"Error fetching config: {e}")
        print("Using default/cached configuration")

    return False


def should_fetch_config():
    """Check if we should fetch config from server"""
    global last_config_fetch
    return (time.monotonic() - last_config_fetch) > CONFIG_FETCH_INTERVAL


def create_labels_from_layout():
    """Create display labels based on current layout"""
    global labels, display_group

    # Clear existing labels
    while len(display_group) > 0:
        display_group.pop()
    labels = []

    if not current_layout:
        print("No layout defined, using defaults")
        return

    # Create labels for each row in layout
    for row in current_layout.get('rows', []):
        y_pos = row.get('y', 4)
        color = hex_to_int(row.get('color', '0xFFFFFF'))

        label = adafruit_display_text.label.Label(
            FONT,
            color=color,
            text=""
        )
        label.x = 1
        label.y = y_pos

        labels.append({
            'label': label,
            'short_field': row.get('short_field', ''),
            'long_field': row.get('long_field', ''),
            'short_text': '',
            'long_text': ''
        })

        display_group.append(label)

    print(f"Created {len(labels)} labels")


# ==================== Display Functions ====================
# (Same as code_v2.py - abbreviated for space)

def plane_animation():
    """Scroll plane across screen"""
    matrixportal.display.show(planeG)
    plane_speed = config.get('display', {}).get('plane_speed', 0.04)
    for i in range(matrixportal.display.width + 24, -12, -1):
        planeG.x = i
        w.feed()
        time.sleep(plane_speed)


def scroll(label, text):
    """Scroll text across display"""
    text_speed = config.get('display', {}).get('text_speed', 0.04)
    label.text = text
    label.x = matrixportal.display.width
    for i in range(matrixportal.display.width + 1, 0 - label.bounding_box[2], -1):
        label.x = i
        w.feed()
        time.sleep(text_speed)


def display_flight():
    """Display flight information using current layout"""
    if not labels:
        return
    matrixportal.display.show(display_group)
    pause_time = config.get('display', {}).get('pause_between_scrolling', 3)

    for label_data in labels:
        label_data['label'].text = label_data['short_text']
        label_data['label'].x = 1
    time.sleep(pause_time)

    for label_data in labels:
        if label_data['long_text']:
            scroll(label_data['label'], label_data['long_text'])
            label_data['label'].text = label_data['short_text']
            label_data['label'].x = 1
            time.sleep(pause_time)


def clear_flight():
    """Clear all displayed text"""
    for label_data in labels:
        label_data['label'].text = ""
        label_data['short_text'] = ""
        label_data['long_text'] = ""


# ==================== API Functions ====================
# (Same as code_v2.py - flight detection and parsing logic)
# Abbreviated here to save space - would include all the same functions

def get_flight_details(flight_id):
    """Fetch flight details from FlightRadar24"""
    # ... (same as code_v2.py)
    pass

def get_field_value(json_data, field_id):
    """Get a field value by field ID"""
    # ... (same as code_v2.py)
    pass

def parse_details_json():
    """Parse flight details JSON"""
    # ... (same as code_v2.py)
    pass

def get_flights():
    """Search for flights overhead"""
    # ... (same as code_v2.py)
    pass

def checkConnection():
    """Check and reconnect WiFi"""
    # ... (same as code_v2.py)
    pass


# ==================== Main Loop ====================

print("=" * 40)
print(f"Flight Portal v3 - OTA Updates")
print(f"Firmware Version: {FIRMWARE_VERSION}")
print("=" * 40)

# Initial WiFi connection
checkConnection()

# Fetch initial configuration
fetch_config()

# Create labels from layout
create_labels_from_layout()

# Check for firmware updates on startup
handle_ota_update()

# Main loop
last_flight = ''
while True:
    w.feed()

    # Check if we should fetch new config
    if should_fetch_config():
        if fetch_config():
            create_labels_from_layout()

    # Check for firmware updates periodically
    handle_ota_update()

    # Search for flights
    flight_id = get_flights()
    w.feed()

    if flight_id:
        if flight_id == last_flight:
            print("Same flight found, keep showing it")
        else:
            print(f"New flight {flight_id} found")
            clear_flight()
            if get_flight_details(flight_id):
                w.feed()
                gc.collect()
                if parse_details_json():
                    gc.collect()
                    plane_animation()
                    display_flight()
            last_flight = flight_id
    else:
        clear_flight()

    time.sleep(5)
    query_delay = config.get('query_delay', 30)
    for i in range(0, query_delay, 5):
        time.sleep(5)
        w.feed()
    gc.collect()
