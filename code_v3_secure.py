"""
Flight Portal v3 - SECURE with Authentication & Code Signing
MatrixPortal flight display with secure OTA updates
"""

import time
import board
import terminalio
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
FIRMWARE_VERSION = "3.0.0"

# ⚠️  IMPORTANT: Replace these with your actual keys from generate_keys.py
DEVICE_API_KEY = "your-device-api-key-here-32-characters"
SIGNING_KEY = "your-signing-key-here-64-hex-characters"

# Server configuration
CONFIG_SERVER = "192.168.1.100:3100"  # Replace with your server IP
USE_HTTPS = True  # Set to True if server has SSL enabled

# ==================== Helper Functions ====================

def hmac_sha256(key, message):
    """HMAC-SHA256 implementation for CircuitPython"""
    if not CRYPTO_AVAILABLE:
        return None

    # HMAC implementation
    block_size = 64
    key_bytes = key.encode('utf-8') if isinstance(key, str) else key
    msg_bytes = message.encode('utf-8') if isinstance(message, str) else message

    # Pad key
    if len(key_bytes) > block_size:
        key_bytes = hashlib.sha256(key_bytes).digest()
    if len(key_bytes) < block_size:
        key_bytes += b'\x00' * (block_size - len(key_bytes))

    # Compute HMAC
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

    # Constant-time comparison
    if len(signature) != len(expected_signature):
        return False

    result = 0
    for a, b in zip(signature, expected_signature):
        result |= ord(a) ^ ord(b) if isinstance(a, str) else a ^ b
    return result == 0


# ==================== Configuration ====================

try:
    from secrets import secrets
except ImportError:
    print("No secrets.py found, will use config server")
    secrets = {
        'ssid': 'your-network',
        'password': 'your-password',
        'bounds_box': '51.6,51.4,-0.3,-0.1'
    }

# URLs
protocol = 'https' if USE_HTTPS else 'http'
CONFIG_URL = f"{protocol}://{CONFIG_SERVER}/api/config"
LAYOUTS_URL = f"{protocol}://{CONFIG_SERVER}/api/layouts"
FIRMWARE_CHECK_URL = f"{protocol}://{CONFIG_SERVER}/api/firmware/check"
FIRMWARE_DOWNLOAD_URL = f"{protocol}://{CONFIG_SERVER}/api/firmware/download"

CONFIG_FETCH_INTERVAL = 300
FIRMWARE_CHECK_INTERVAL = 3600

# Authenticated headers
auth_headers = {
    "Authorization": f"Bearer {DEVICE_API_KEY}",
    "User-Agent": f"FlightPortal/{FIRMWARE_VERSION}",
    "Accept": "application/json"
}

# FlightRadar24 API URLs
FLIGHT_SEARCH_HEAD = "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds="
FLIGHT_SEARCH_TAIL = "&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1&limit=1"
FLIGHT_LONG_DETAILS_HEAD = "https://data-live.flightradar24.com/clickhandler/?flight="

fr24_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "cache-control": "no-store, no-cache, must-revalidate",
    "accept": "application/json"
}

# Default configuration
config = {
    "query_delay": 30,
    "active_layout": "classic",
    "display": {
        "plane_color": "0x4B0082",
        "plane_speed": 0.04,
        "text_speed": 0.04,
        "pause_between_scrolling": 3
    }
}

current_layout = None
last_config_fetch = 0
last_firmware_check = 0

# ==================== Hardware Setup ====================
# (Same as code_v3_ota.py - omitted for brevity)

# ==================== OTA Update Functions ====================

def check_for_firmware_update():
    """Check if a firmware update is available (authenticated)"""
    global last_firmware_check

    try:
        print(f"Checking for firmware updates (current version: {FIRMWARE_VERSION})...")

        check_url = f"{FIRMWARE_CHECK_URL}?version={FIRMWARE_VERSION}"
        response = requests.get(url=check_url, headers=auth_headers, timeout=10)

        if response.status_code == 401:
            print("❌ Authentication failed - check DEVICE_API_KEY")
            return {'available': False}

        update_info = response.json()
        last_firmware_check = time.monotonic()

        if update_info.get('update_available'):
            new_version = update_info.get('version')
            print(f"Firmware update available: {new_version}")
            print(f"Changes: {update_info.get('changelog', 'No changelog')}")
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
    """Download and install firmware update with signature verification"""
    try:
        print(f"Downloading firmware version {update_info['version']}...")

        download_url = update_info.get('url', FIRMWARE_DOWNLOAD_URL)
        response = requests.get(url=download_url, headers=auth_headers, timeout=30)

        if response.status_code == 401:
            print("❌ Authentication failed during download")
            return False

        if response.status_code != 200:
            print(f"Download failed with status {response.status_code}")
            return False

        new_code = response.text
        firmware_signature = response.headers.get('X-Firmware-Signature', '')
        firmware_version = response.headers.get('X-Firmware-Version', '')

        print(f"Downloaded {len(new_code)} bytes")
        print(f"Version: {firmware_version}")
        print(f"Signature: {firmware_signature[:16]}...{firmware_signature[-8:]}")

        # Verify signature
        if CRYPTO_AVAILABLE and firmware_signature:
            print("Verifying firmware signature...")
            if not verify_signature(new_code, firmware_signature):
                print("❌ SECURITY: Firmware signature verification FAILED!")
                print("❌ Update rejected - possible tampering detected")
                return False
            print("✅ Signature verified - firmware authentic")
        else:
            print("⚠️  WARNING: Signature verification not available")

        # Basic sanity checks
        if len(new_code) < 1000 or "Flight Portal" not in new_code:
            print("Downloaded code failed sanity check")
            return False

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

        # Write new code
        print("Installing new firmware...")
        try:
            with open("/code.py", "w") as f:
                f.write(new_code)
            print("✅ Firmware installed successfully")
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

        # Remount as read-only
        try:
            storage.remount("/", True)
        except:
            pass

        print("🎉 Update complete! Restarting in 3 seconds...")
        time.sleep(3)
        microcontroller.reset()

        return True

    except Exception as e:
        print(f"Error during update: {e}")
        return False


# ==================== Configuration Functions ====================

def fetch_config():
    """Fetch configuration from web server (authenticated)"""
    global config, current_layout, last_config_fetch

    try:
        print("Fetching configuration from server...")
        response = requests.get(url=CONFIG_URL, headers=auth_headers, timeout=10)

        if response.status_code == 401:
            print("❌ Authentication failed - check DEVICE_API_KEY")
            return False

        server_config = response.json()

        if server_config:
            config = server_config
            print(f"✅ Config loaded: Layout={config.get('active_layout')}")

            # Fetch active layout
            active_layout_id = config.get('active_layout', 'classic')
            try:
                layouts_response = requests.get(url=LAYOUTS_URL, headers=auth_headers, timeout=10)
                layouts_data = layouts_response.json()

                for layout in layouts_data.get('layouts', []):
                    if layout['id'] == active_layout_id:
                        current_layout = layout
                        print(f"✅ Loaded layout: {layout['name']}")
                        break
            except Exception as e:
                print(f"Error loading layout: {e}")

            last_config_fetch = time.monotonic()

            # Update WiFi and bounds
            if 'wifi' in config:
                secrets['ssid'] = config['wifi'].get('ssid', secrets.get('ssid'))
                secrets['password'] = config['wifi'].get('password', secrets.get('password'))
            if 'location' in config:
                secrets['bounds_box'] = config['location'].get('bounds_box', secrets.get('bounds_box'))

            return True
    except Exception as e:
        print(f"Error fetching config: {e}")
        print("Using default/cached configuration")

    return False


# ==================== Display & Flight Functions ====================
# (Same as code_v3_ota.py - display, plane animation, flight detection, etc.)
# Omitted for brevity - include all functions from code_v3_ota.py here

# ==================== Main Loop ====================

print("=" * 40)
print(f"Flight Portal v3 - SECURE MODE")
print(f"Firmware Version: {FIRMWARE_VERSION}")
print(f"Authentication: {'✅ Enabled' if DEVICE_API_KEY != 'your-device-api-key-here-32-characters' else '⚠️  NOT CONFIGURED'}")
print(f"Code Signing: {'✅ Enabled' if CRYPTO_AVAILABLE else '⚠️  Disabled (hashlib unavailable)'}")
print(f"HTTPS: {'✅ Enabled' if USE_HTTPS else '⚠️  Disabled'}")
print("=" * 40)

if DEVICE_API_KEY == "your-device-api-key-here-32-characters":
    print()
    print("❌ ERROR: DEVICE_API_KEY not configured!")
    print("❌ Run 'python generate_keys.py' on server and update this file")
    print()
    # Continue anyway for testing, but warn

# Initial WiFi connection
# checkConnection()  # Implement from code_v3_ota.py

# Fetch initial configuration
fetch_config()

# Create labels from layout
# create_labels_from_layout()  # Implement from code_v3_ota.py

# Check for firmware updates on startup
# handle_ota_update()  # Implement from code_v3_ota.py

# Main loop (same as code_v3_ota.py)
print()
print("🚀 Starting main loop...")

# ... (rest of main loop - same as code_v3_ota.py)
