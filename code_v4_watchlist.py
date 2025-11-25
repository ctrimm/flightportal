"""
Flight Portal v4 - WATCHLIST SUPPORT
MatrixPortal flight display with tail number tracking and alerts
Based on v3 (secure) with watchlist functionality added
"""

import time
import board
import terminalio
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_portalbase.network import HttpError
import adafruit_requests as requests
import json
import storage
import microcontroller

# Import hashlib if available (CircuitPython 7.0+)
try:
    import hashlib
    CRYPTO_AVAILABLE = True
except ImportError:
    print("⚠️  hashlib not available - signature verification disabled")
    CRYPTO_AVAILABLE = False

from microcontroller import watchdog as w
from watchdog import WatchDogMode

w.timeout = 16
w.mode = WatchDogMode.RESET

FONT = terminalio.FONT

# ==================== SECURITY CONFIGURATION ====================

# Firmware version
FIRMWARE_VERSION = "4.0.0"

# ⚠️  IMPORTANT: Replace these with your actual keys
DEVICE_API_KEY = "your-device-api-key-here-32-characters"
SIGNING_KEY = "your-signing-key-here-64-hex-characters"

# Server configuration
CONFIG_SERVER = "192.168.1.100:3100"  # Replace with your server IP or domain
USE_HTTPS = True  # Set to True if server has SSL enabled

# Device ID (used for watchlist lookup)
DEVICE_ID = "default"  # Replace with unique device identifier

# ==================== WATCHLIST CONFIGURATION ====================

# Watchlist settings
WATCHLIST_ENABLED = True
WATCHLIST_CHECK_INTERVAL = 300  # Refresh watchlist every 5 minutes
ALERT_DURATION = 15  # Show alert for minimum 15 seconds
ALERT_CYCLE_TIME = 5  # Cycle between multiple alerts every 5 seconds

# ==================== Helper Functions ====================

def hmac_sha256(key, message):
    """HMAC-SHA256 implementation for CircuitPython"""
    if not CRYPTO_AVAILABLE:
        return None

    block_size = 64
    key_bytes = key.encode('utf-8') if isinstance(key, str) else key
    msg_bytes = message.encode('utf-8') if isinstance(message, str) else message

    if len(key_bytes) > block_size:
        key_bytes = hashlib.sha256(key_bytes).digest()
    if len(key_bytes) < block_size:
        key_bytes += b'\x00' * (block_size - len(key_bytes))

    o_key_pad = bytes([b ^ 0x5C for b in key_bytes])
    i_key_pad = bytes([b ^ 0x36 for b in key_bytes])

    inner_hash = hashlib.sha256(i_key_pad + msg_bytes).digest()
    return hashlib.sha256(o_key_pad + inner_hash).hexdigest()


def verify_signature(firmware_code, signature):
    """Verify firmware signature"""
    if not CRYPTO_AVAILABLE:
        print("⚠️  Cannot verify signature - hashlib not available")
        return True  # WARNING: Insecure fallback

    expected_signature = hmac_sha256(SIGNING_KEY, firmware_code)

    if len(signature) != len(expected_signature):
        return False

    result = 0
    for a, b in zip(signature, expected_signature):
        result |= ord(a) ^ ord(b) if isinstance(a, str) else a ^ b
    return result == 0


def normalize_tail_number(tail):
    """Normalize tail number for comparison"""
    if not tail:
        return ""
    return str(tail).upper().replace('-', '').replace(' ', '').strip()


def degrees_to_cardinal(degrees):
    """Convert degrees to cardinal direction (N, NE, E, etc.)"""
    if degrees is None:
        return "?"
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ix = round(degrees / 45) % 8
    return dirs[ix]


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in miles (rough approximation)"""
    from math import radians, cos, sin, asin, sqrt

    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    # Earth radius in miles
    r = 3956

    return round(c * r, 1)


def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2"""
    from math import radians, degrees, cos, sin, atan2

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1

    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    bearing = degrees(atan2(x, y))
    return (bearing + 360) % 360


# ==================== Configuration ====================

try:
    from secrets import secrets
except ImportError:
    print("No secrets.py found, will use config server")
    secrets = {
        'ssid': 'your-network',
        'password': 'your-password',
        'bounds_box': '51.6,51.4,-0.3,-0.1',
        'lat': 51.5,
        'lon': -0.2
    }

# ==================== Network Setup ====================

matrixportal = MatrixPortal(
    status_neopixel=board.NEOPIXEL,
    debug=True
)

# Colors
COLOR_RED = 0xFF0000
COLOR_YELLOW = 0xFFFF00
COLOR_CYAN = 0x00FFFF
COLOR_GREEN = 0x00FF00
COLOR_WHITE = 0xFFFFFF
COLOR_BLUE = 0x0000FF

# ==================== Watchlist Management ====================

watchlist = []
last_watchlist_fetch = 0


def fetch_watchlist():
    """Fetch watchlist from server"""
    global watchlist, last_watchlist_fetch

    if not WATCHLIST_ENABLED:
        return

    try:
        protocol = "https" if USE_HTTPS else "http"
        url = f"{protocol}://{CONFIG_SERVER}/api/watchlist?deviceId={DEVICE_ID}"

        print(f"Fetching watchlist from {url}")

        headers = {
            'Authorization': f'Bearer {DEVICE_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            watchlist_data = data.get('watchlist', [])

            # Extract normalized tail numbers
            watchlist = [normalize_tail_number(item['tailNumber']) for item in watchlist_data]

            print(f"✓ Loaded watchlist: {len(watchlist)} aircraft")
            for tail in watchlist:
                print(f"  - {tail}")

            last_watchlist_fetch = time.monotonic()

        else:
            print(f"⚠️  Failed to fetch watchlist: HTTP {response.status_code}")

        response.close()

    except Exception as e:
        print(f"⚠️  Error fetching watchlist: {e}")


def is_watched_aircraft(flight):
    """Check if flight is in watchlist"""
    if not WATCHLIST_ENABLED or not watchlist:
        return False

    tail = flight.get('registration') or flight.get('callsign', '')
    normalized = normalize_tail_number(tail)

    return normalized in watchlist


# ==================== Display Functions ====================

def create_alert_border(display, flash_state):
    """Create flashing border for watchlist alerts"""
    color = COLOR_RED if flash_state else COLOR_YELLOW

    # Draw border (2 pixels wide)
    border_group = displayio.Group()

    # Top border
    for y in range(2):
        for x in range(64):
            pixel = displayio.TileGrid(
                bitmap=displayio.Bitmap(1, 1, 1),
                pixel_shader=displayio.Palette(1),
                x=x, y=y
            )
            pixel.pixel_shader[0] = color
            border_group.append(pixel)

    # Bottom border
    for y in range(30, 32):
        for x in range(64):
            pixel = displayio.TileGrid(
                bitmap=displayio.Bitmap(1, 1, 1),
                pixel_shader=displayio.Palette(1),
                x=x, y=y
            )
            pixel.pixel_shader[0] = color
            border_group.append(pixel)

    # Left border
    for y in range(2, 30):
        for x in range(2):
            pixel = displayio.TileGrid(
                bitmap=displayio.Bitmap(1, 1, 1),
                pixel_shader=displayio.Palette(1),
                x=x, y=y
            )
            pixel.pixel_shader[0] = color
            border_group.append(pixel)

    # Right border
    for y in range(2, 30):
        for x in range(62, 64):
            pixel = displayio.TileGrid(
                bitmap=displayio.Bitmap(1, 1, 1),
                pixel_shader=displayio.Palette(1),
                x=x, y=y
            )
            pixel.pixel_shader[0] = color
            border_group.append(pixel)

    return border_group


def display_watchlist_alert(flight, lat, lon):
    """Display special alert layout for watchlist aircraft"""
    matrixportal.display.show(None)
    matrixportal.display.brightness = 1.0

    # Extract flight data
    tail = flight.get('registration') or flight.get('callsign', 'UNKNOWN')
    aircraft_type = flight.get('aircraft_code') or flight.get('aircraft', {}).get('model', 'Unknown')
    altitude = flight.get('altitude', 0)
    speed = flight.get('ground_speed', 0)
    heading = degrees_to_cardinal(flight.get('track'))

    flight_lat = flight.get('latitude')
    flight_lon = flight.get('longitude')

    if flight_lat and flight_lon and lat and lon:
        distance = calculate_distance(lat, lon, flight_lat, flight_lon)
        bearing = calculate_bearing(lat, lon, flight_lat, flight_lon)
        direction = degrees_to_cardinal(bearing)
    else:
        distance = 0
        direction = "?"

    # Create display group
    group = displayio.Group()

    # Flash border (will be recreated each frame)
    flash_state = int(time.monotonic() * 2) % 2  # Flash every 0.5s
    border = create_alert_border(matrixportal.display, flash_state)
    group.append(border)

    # Text labels
    text_group = displayio.Group()

    # Row 1: "TRACKED" label
    matrixportal.add_text(
        text_position=(4, 4),
        text_font=FONT,
        text_color=COLOR_WHITE,
        text_scale=1,
    )
    matrixportal.set_text("TRACKED", 0)

    # Row 2: Tail number (large)
    matrixportal.add_text(
        text_position=(4, 11),
        text_font=FONT,
        text_color=COLOR_CYAN,
        text_scale=1,
    )
    matrixportal.set_text(tail[:10], 1)  # Limit length

    # Row 3: Aircraft type
    matrixportal.add_text(
        text_position=(4, 18),
        text_font=FONT,
        text_color=COLOR_WHITE,
        text_scale=1,
    )
    matrixportal.set_text(aircraft_type[:10], 2)

    # Row 4: Flight data
    flight_data = f"{int(altitude)}ft {int(speed)}kt {heading}"
    matrixportal.add_text(
        text_position=(4, 24),
        text_font=FONT,
        text_color=COLOR_GREEN,
        text_scale=1,
    )
    matrixportal.set_text(flight_data[:15], 3)

    # Row 5: Distance & direction
    distance_text = f"{distance}mi {direction}"
    matrixportal.add_text(
        text_position=(4, 29),
        text_font=FONT,
        text_color=COLOR_WHITE,
        text_scale=1,
    )
    matrixportal.set_text(distance_text, 4)

    print(f"🎯 WATCHLIST ALERT: {tail} - {aircraft_type}")
    print(f"   {altitude}ft, {speed}kt, {distance}mi {direction}")


def display_normal_layout(flights):
    """Display normal flight tracking layout"""
    # This would be your normal v3 display code
    # For now, just show basic info
    matrixportal.display.show(None)

    if not flights:
        matrixportal.add_text(
            text_position=(2, 15),
            text_font=FONT,
            text_color=COLOR_WHITE,
            text_scale=1,
        )
        matrixportal.set_text("No flights", 0)
        return

    # Show first 3 flights
    y_pos = 4
    for i, flight in enumerate(flights[:3]):
        tail = flight.get('registration') or flight.get('callsign', '???')
        matrixportal.add_text(
            text_position=(2, y_pos),
            text_font=FONT,
            text_color=COLOR_WHITE,
            text_scale=1,
        )
        matrixportal.set_text(tail[:8], i)
        y_pos += 10


# ==================== Main Loop ====================

print("=" * 60)
print("Flight Portal v4 - Watchlist Support")
print(f"Firmware: {FIRMWARE_VERSION}")
print(f"Watchlist: {'Enabled' if WATCHLIST_ENABLED else 'Disabled'}")
print("=" * 60)

# Connect to WiFi
print("Connecting to WiFi...")
matrixportal.network.connect()
print(f"✓ Connected! IP: {matrixportal.network.ip_address}")

# Fetch watchlist on boot
if WATCHLIST_ENABLED:
    fetch_watchlist()

# Get device location from secrets
device_lat = secrets.get('lat', 51.5)
device_lon = secrets.get('lon', -0.2)

alert_start_time = 0
alert_aircraft = None
current_alert_index = 0

# Main loop
while True:
    try:
        w.feed()

        # Refresh watchlist periodically
        if WATCHLIST_ENABLED and (time.monotonic() - last_watchlist_fetch) > WATCHLIST_CHECK_INTERVAL:
            fetch_watchlist()

        # Fetch flight data
        print("\nFetching flight data...")

        protocol = "https" if USE_HTTPS else "http"
        bounds = secrets.get('bounds_box', '51.6,51.4,-0.3,-0.1')

        # Use FlightRadar24 API (or your config server)
        url = f"https://data-live.flightradar24.com/zones/fcgi/feed.js?bounds={bounds}"

        response = requests.get(url)
        data = response.json()
        response.close()

        # Parse flights
        flights = []
        watchlist_matches = []

        for key, value in data.items():
            if isinstance(value, list) and len(value) > 10:
                flight = {
                    'callsign': value[16] if len(value) > 16 else None,
                    'registration': value[9] if len(value) > 9 else None,
                    'latitude': value[1],
                    'longitude': value[2],
                    'altitude': value[4],
                    'ground_speed': value[5],
                    'track': value[3],
                    'aircraft_code': value[8] if len(value) > 8 else None,
                }

                flights.append(flight)

                # Check if in watchlist
                if is_watched_aircraft(flight):
                    watchlist_matches.append(flight)

        print(f"✓ Found {len(flights)} flights")

        # Display logic
        if watchlist_matches:
            print(f"🎯 {len(watchlist_matches)} WATCHLIST AIRCRAFT DETECTED!")

            # Show alert
            if not alert_aircraft:
                alert_aircraft = watchlist_matches[0]
                alert_start_time = time.monotonic()
                current_alert_index = 0

            # Cycle through multiple watchlist aircraft
            elapsed = time.monotonic() - alert_start_time
            if elapsed > ALERT_CYCLE_TIME and len(watchlist_matches) > 1:
                current_alert_index = (current_alert_index + 1) % len(watchlist_matches)
                alert_aircraft = watchlist_matches[current_alert_index]
                alert_start_time = time.monotonic()

            display_watchlist_alert(alert_aircraft, device_lat, device_lon)

        else:
            # No watchlist matches - normal display
            if alert_aircraft:
                print("Watchlist aircraft left range - returning to normal display")
                alert_aircraft = None

            display_normal_layout(flights)

        # Sleep before next update
        time.sleep(10)

    except Exception as e:
        print(f"⚠️  Error: {e}")
        time.sleep(30)
        continue
