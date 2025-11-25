"""
Flight Portal v2 - Dynamic Layout Support
MatrixPortal flight display with web-based configuration
"""

import time
from random import randrange
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_portalbase.network import HttpError
import adafruit_requests as requests
import json

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
CONFIG_FETCH_INTERVAL = 300  # Fetch config every 5 minutes

# Default configuration (used if config server is unavailable)
DEFAULT_CONFIG = {
    "query_delay": 30,
    "active_layout": "classic",
    "display": {
        "plane_color": "0x4B0082",
        "plane_speed": 0.04,
        "text_speed": 0.04,
        "pause_between_scrolling": 3
    }
}

# Current configuration (loaded from server or defaults)
config = DEFAULT_CONFIG.copy()
current_layout = None
last_config_fetch = 0

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

# ==================== Configuration Functions ====================

def hex_to_int(hex_string):
    """Convert hex string like '0xEE82EE' to integer"""
    try:
        return int(hex_string, 16)
    except (ValueError, TypeError):
        return 0xFFFFFF  # Default to white


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

    # Show short text on all rows
    for label_data in labels:
        label_data['label'].text = label_data['short_text']
        label_data['label'].x = 1

    time.sleep(pause_time)

    # Scroll long text for each row
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

def get_flight_details(flight_id):
    """Fetch flight details from FlightRadar24"""
    global json_bytes, json_size

    byte_counter = 0
    chunk_length = 1024

    # Zero out old data
    for i in range(0, json_size):
        json_bytes[i] = 0

    try:
        response = requests.get(url=FLIGHT_LONG_DETAILS_HEAD + flight_id, headers=rheaders)

        for chunk in response.iter_content(chunk_size=chunk_length):
            if byte_counter + chunk_length <= json_size:
                for i in range(0, len(chunk)):
                    json_bytes[i + byte_counter] = chunk[i]
            else:
                print("Exceeded max string size while parsing JSON")
                return False

            # Look for trail section
            trail_start = json_bytes.find(b"\"trail\":")
            byte_counter += len(chunk)

            if trail_start != -1:
                trail_end = json_bytes[trail_start:].find(b"}")
                if trail_end != -1:
                    trail_end += trail_start
                    closing_bytes = b'}]}'
                    for i in range(0, len(closing_bytes)):
                        json_bytes[trail_end + i] = closing_bytes[i]
                    for i in range(trail_end + 3, json_size):
                        json_bytes[i] = 0

                    print(f"Details lookup saved {trail_end} bytes.")
                    return True
    except (RuntimeError, OSError, HttpError) as e:
        print(f"Error fetching flight details: {e}")
        return False

    print("Failed to find valid trail entry in JSON")
    return False


def extract_field_value(json_data, field_path):
    """Extract a value from JSON using dot notation path"""
    try:
        keys = field_path.split('.')
        value = json_data

        for key in keys:
            if '[' in key and ']' in key:
                # Handle array index like "trail[0]"
                field_name = key.split('[')[0]
                index = int(key.split('[')[1].split(']')[0])
                value = value[field_name][index]
            else:
                value = value[key]

        return str(value) if value is not None else ""
    except (KeyError, IndexError, TypeError):
        return ""


def format_field_value(value, format_type):
    """Format a field value based on type"""
    if not value:
        return value

    try:
        if format_type == "altitude":
            return f"{int(float(value)):,}ft"
        elif format_type == "speed":
            return f"{int(float(value))}kts"
        elif format_type == "heading":
            return f"{int(float(value))}°"
    except (ValueError, TypeError):
        pass

    return value


def get_field_value(json_data, field_id):
    """Get a field value by field ID, handling computed fields"""

    # Field mapping (simplified - should match fields.json in web interface)
    field_map = {
        'flight_number': 'identification.number.default',
        'flight_callsign': 'identification.callsign',
        'airline_name': 'airline.name',
        'airline_short': 'airline.short',
        'aircraft_code': 'aircraft.model.code',
        'aircraft_model': 'aircraft.model.text',
        'aircraft_registration': 'aircraft.registration',
        'airport_origin_name': 'airport.origin.name',
        'airport_origin_code': 'airport.origin.code.iata',
        'airport_destination_name': 'airport.destination.name',
        'airport_destination_code': 'airport.destination.code.iata',
        'altitude': 'trail.0.alt',
        'speed': 'trail.0.spd',
        'heading': 'trail.0.hd',
        'latitude': 'trail.0.lat',
        'longitude': 'trail.0.lng'
    }

    # Handle computed fields
    if field_id == 'route_codes':
        origin = get_field_value(json_data, 'airport_origin_code')
        dest = get_field_value(json_data, 'airport_destination_code')
        return f"{origin}-{dest}" if origin and dest else ""

    elif field_id == 'route_full':
        origin = get_field_value(json_data, 'airport_origin_name')
        dest = get_field_value(json_data, 'airport_destination_name')
        # Remove " Airport" suffix
        origin = origin.replace(" Airport", "")
        dest = dest.replace(" Airport", "")
        return f"{origin}-{dest}" if origin and dest else ""

    elif field_id == 'route_with_altitude':
        route = get_field_value(json_data, 'route_codes')
        altitude = get_field_value(json_data, 'altitude')
        if route and altitude:
            return f"{route} @ {format_field_value(altitude, 'altitude')}"
        return route

    elif field_id == 'aircraft_with_speed':
        aircraft = get_field_value(json_data, 'aircraft_model')
        speed = get_field_value(json_data, 'speed')
        if aircraft and speed:
            return f"{aircraft} {format_field_value(speed, 'speed')}"
        return aircraft

    elif field_id == 'speed_and_heading':
        speed = get_field_value(json_data, 'speed')
        heading = get_field_value(json_data, 'heading')
        if speed and heading:
            return f"{format_field_value(speed, 'speed')} @ {format_field_value(heading, 'heading')}"
        return ""

    elif field_id == 'altitude_detailed':
        altitude = get_field_value(json_data, 'altitude')
        return format_field_value(altitude, 'altitude')

    # Standard field lookup
    path = field_map.get(field_id)
    if path:
        return extract_field_value(json_data, path)

    return ""


def parse_details_json():
    """Parse flight details JSON and populate label texts"""
    global json_bytes, labels

    try:
        json_data = json.loads(json_bytes)

        flight_number = get_field_value(json_data, 'flight_number')
        if flight_number:
            print(f"Flight is called {flight_number}")
        else:
            callsign = get_field_value(json_data, 'flight_callsign')
            print(f"No flight number, callsign is {callsign}")

        # Populate labels based on current layout
        for label_data in labels:
            short_field = label_data['short_field']
            long_field = label_data['long_field']

            label_data['short_text'] = get_field_value(json_data, short_field) or ''
            label_data['long_text'] = get_field_value(json_data, long_field) or ''

        return True

    except (KeyError, ValueError, TypeError) as e:
        print(f"JSON error: {e}")
        return False


def get_flights():
    """Search for flights overhead"""
    bounds_box = secrets.get('bounds_box', '51.6,51.4,-0.3,-0.1')
    search_url = FLIGHT_SEARCH_HEAD + bounds_box + FLIGHT_SEARCH_TAIL

    try:
        response = requests.get(url=search_url, headers=rheaders).json()
    except (RuntimeError, OSError, HttpError, ValueError, requests.OutOfRetries) as e:
        print(f"Error searching for flights: {e}")
        checkConnection()
        return False

    if len(response) == 3:
        for flight_id, flight_info in response.items():
            if flight_id not in ["version", "full_count"]:
                if len(flight_info) > 13:
                    return flight_id

    return False


def checkConnection():
    """Check and reconnect WiFi if needed"""
    print("Check and reconnect WiFi")
    attempts = 10
    attempt = 1

    while (not esp.status == adafruit_esp32spi.WL_CONNECTED) and attempt < attempts:
        print(f"Connect attempt {attempt} of {attempts}")
        print("Reset ESP...")
        w.feed()
        wifi.reset()
        print("Attempt WiFi connect...")
        w.feed()
        try:
            wifi.connect()
        except OSError as e:
            print(f"{e.__class__.__name__}: {e}")
        attempt += 1

    if esp.status == adafruit_esp32spi.WL_CONNECTED:
        print("Successfully connected.")
    else:
        print("Failed to connect.")


# ==================== Main Loop ====================

print("=" * 40)
print("Flight Portal v2 - Dynamic Layout Support")
print("=" * 40)

# Initial WiFi connection
checkConnection()

# Fetch initial configuration
fetch_config()

# Create labels from layout
create_labels_from_layout()

# Main loop
last_flight = ''
while True:
    w.feed()

    # Check if we should fetch new config
    if should_fetch_config():
        if fetch_config():
            create_labels_from_layout()

    # Search for flights
    flight_id = get_flights()
    w.feed()

    if flight_id:
        if flight_id == last_flight:
            print("Same flight found, keep showing it")
        else:
            print(f"New flight {flight_id} found, clear display")
            clear_flight()

            if get_flight_details(flight_id):
                w.feed()
                gc.collect()

                if parse_details_json():
                    gc.collect()
                    plane_animation()
                    display_flight()
                else:
                    print("Error parsing JSON, skip displaying this flight")
            else:
                print("Error loading details, skip displaying this flight")

            last_flight = flight_id
    else:
        clear_flight()

    time.sleep(5)

    # Wait for next query with watchdog feeding
    query_delay = config.get('query_delay', 30)
    for i in range(0, query_delay, 5):
        time.sleep(5)
        w.feed()

    gc.collect()
