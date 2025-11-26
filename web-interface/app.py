"""
Flight Portal Web Interface
A CRUD interface for managing MatrixPortal flight display settings
WITH SECURITY: Authentication, HTTPS, and Code Signing
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from functools import wraps
import json
import os
import hmac
import hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration paths
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
DEVICE_CONFIG_PATH = os.path.join(CONFIG_DIR, 'device_config.json')
LAYOUTS_CONFIG_PATH = os.path.join(CONFIG_DIR, 'layouts.json')
FIELDS_CONFIG_PATH = os.path.join(CONFIG_DIR, 'fields.json')
SECRETS_PATH = os.path.join(os.path.dirname(__file__), '.secrets.json')

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# ==================== Security Configuration ====================

def load_security_config():
    """Load security configuration (API keys, signing keys, SSL settings)"""
    if os.path.exists(SECRETS_PATH):
        try:
            with open(SECRETS_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading security config: {e}")

    # Default config (INSECURE - only for development)
    print("⚠️  WARNING: No .secrets.json found! Using default insecure keys.")
    print("⚠️  Run 'python generate_keys.py' to generate secure keys.")
    return {
        "admin_api_key": "INSECURE_DEFAULT_ADMIN_KEY",
        "device_api_key": "INSECURE_DEFAULT_DEVICE_KEY",
        "signing_key": "INSECURE_DEFAULT_SIGNING_KEY",
        "ssl_enabled": False,
        "ssl_cert": None,
        "ssl_key": None
    }

SECURITY_CONFIG = load_security_config()

def sign_firmware(firmware_code):
    """Sign firmware code with HMAC-SHA256"""
    signing_key = SECURITY_CONFIG['signing_key']
    signature = hmac.new(
        signing_key.encode('utf-8'),
        firmware_code.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_signature(firmware_code, signature):
    """Verify firmware signature"""
    expected_signature = sign_firmware(firmware_code)
    return hmac.compare_digest(signature, expected_signature)

def require_auth(required_role='device'):
    """Decorator for requiring authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get authorization header
            auth_header = request.headers.get('Authorization', '')

            # Extract bearer token
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Missing or invalid authorization header"}), 401

            token = auth_header.replace('Bearer ', '').strip()

            # Validate token based on role
            if required_role == 'admin':
                valid_token = SECURITY_CONFIG['admin_api_key']
            elif required_role == 'device':
                # Device endpoints accept either device or admin key
                valid_token = SECURITY_CONFIG['device_api_key']
                admin_token = SECURITY_CONFIG['admin_api_key']
                if token == admin_token or token == valid_token:
                    return f(*args, **kwargs)
                return jsonify({"error": "Invalid API key"}), 401
            else:
                return jsonify({"error": "Invalid role"}), 500

            # Constant-time comparison to prevent timing attacks
            if not hmac.compare_digest(token, valid_token):
                return jsonify({"error": "Invalid API key"}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Public endpoints (no auth required)
PUBLIC_ENDPOINTS = ['/', '/static']

# ==================== Configuration Paths ====================

# ==================== Helper Functions ====================

def load_json(filepath, default=None):
    """Load JSON from file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return default if default is not None else {}
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default if default is not None else {}

def save_json(filepath, data):
    """Save JSON to file with error handling"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def get_default_device_config():
    """Return default device configuration"""
    return {
        "wifi": {
            "ssid": "your-network",
            "password": "your-password"
        },
        "location": {
            "bounds_box": "51.6,51.4,-0.3,-0.1",
            "name": "Central London",
            "description": "Geographic bounding box for flight search"
        },
        "active_layout": "classic",
        "query_delay": 30,
        "display": {
            "plane_color": "0x4B0082",
            "plane_speed": 0.04,
            "text_speed": 0.04,
            "pause_between_scrolling": 3
        },
        "api": {
            "search_url": "https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds=",
            "details_url": "https://data-live.flightradar24.com/clickhandler/?flight="
        },
        "last_updated": datetime.now().isoformat()
    }

def get_default_layouts():
    """Return default layout configurations"""
    return {
        "layouts": [
            {
                "id": "classic",
                "name": "Classic",
                "description": "Original 3-row layout showing flight number, route, and aircraft",
                "rows": [
                    {
                        "y": 4,
                        "color": "0xEE82EE",
                        "short_field": "flight_number",
                        "long_field": "airline_name"
                    },
                    {
                        "y": 15,
                        "color": "0x4B0082",
                        "short_field": "route_codes",
                        "long_field": "route_full"
                    },
                    {
                        "y": 25,
                        "color": "0xFFA500",
                        "short_field": "aircraft_code",
                        "long_field": "aircraft_model"
                    }
                ]
            },
            {
                "id": "detailed",
                "name": "Detailed",
                "description": "More information including altitude and speed",
                "rows": [
                    {
                        "y": 2,
                        "color": "0xEE82EE",
                        "short_field": "flight_number",
                        "long_field": "airline_name"
                    },
                    {
                        "y": 11,
                        "color": "0x4B0082",
                        "short_field": "route_codes",
                        "long_field": "route_with_altitude"
                    },
                    {
                        "y": 20,
                        "color": "0xFFA500",
                        "short_field": "aircraft_code",
                        "long_field": "aircraft_with_speed"
                    },
                    {
                        "y": 29,
                        "color": "0x00CED1",
                        "short_field": "altitude",
                        "long_field": "speed_and_heading"
                    }
                ]
            },
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Clean, simple 2-row display",
                "rows": [
                    {
                        "y": 8,
                        "color": "0xEE82EE",
                        "short_field": "flight_number",
                        "long_field": "airline_name"
                    },
                    {
                        "y": 20,
                        "color": "0x4B0082",
                        "short_field": "route_codes",
                        "long_field": "route_full"
                    }
                ]
            },
            {
                "id": "tracking",
                "name": "Tracking",
                "description": "Real-time data focus with speed, altitude, and heading",
                "rows": [
                    {
                        "y": 4,
                        "color": "0xEE82EE",
                        "short_field": "flight_number",
                        "long_field": "flight_callsign"
                    },
                    {
                        "y": 15,
                        "color": "0x00CED1",
                        "short_field": "altitude",
                        "long_field": "altitude_detailed"
                    },
                    {
                        "y": 25,
                        "color": "0xFFA500",
                        "short_field": "speed",
                        "long_field": "speed_and_heading"
                    }
                ]
            }
        ]
    }

def get_default_fields():
    """Return available API field definitions"""
    return {
        "fields": [
            {
                "id": "flight_number",
                "name": "Flight Number",
                "description": "Flight number (e.g., BA123)",
                "path": "identification.number.default",
                "type": "string",
                "category": "identification"
            },
            {
                "id": "flight_callsign",
                "name": "Flight Callsign",
                "description": "Radio callsign used by pilot",
                "path": "identification.callsign",
                "type": "string",
                "category": "identification"
            },
            {
                "id": "airline_name",
                "name": "Airline Name",
                "description": "Full airline name",
                "path": "airline.name",
                "type": "string",
                "category": "airline"
            },
            {
                "id": "airline_short",
                "name": "Airline Short Name",
                "description": "Short airline name",
                "path": "airline.short",
                "type": "string",
                "category": "airline"
            },
            {
                "id": "aircraft_code",
                "name": "Aircraft Code",
                "description": "Aircraft type code (e.g., A320)",
                "path": "aircraft.model.code",
                "type": "string",
                "category": "aircraft"
            },
            {
                "id": "aircraft_model",
                "name": "Aircraft Model",
                "description": "Full aircraft model name",
                "path": "aircraft.model.text",
                "type": "string",
                "category": "aircraft"
            },
            {
                "id": "aircraft_registration",
                "name": "Aircraft Registration",
                "description": "Aircraft registration number",
                "path": "aircraft.registration",
                "type": "string",
                "category": "aircraft"
            },
            {
                "id": "airport_origin_name",
                "name": "Origin Airport Name",
                "description": "Departure airport full name",
                "path": "airport.origin.name",
                "type": "string",
                "category": "route",
                "transform": "remove_airport_suffix"
            },
            {
                "id": "airport_origin_code",
                "name": "Origin Airport Code",
                "description": "Departure airport IATA code",
                "path": "airport.origin.code.iata",
                "type": "string",
                "category": "route"
            },
            {
                "id": "airport_destination_name",
                "name": "Destination Airport Name",
                "description": "Arrival airport full name",
                "path": "airport.destination.name",
                "type": "string",
                "category": "route",
                "transform": "remove_airport_suffix"
            },
            {
                "id": "airport_destination_code",
                "name": "Destination Airport Code",
                "description": "Arrival airport IATA code",
                "path": "airport.destination.code.iata",
                "type": "string",
                "category": "route"
            },
            {
                "id": "altitude",
                "name": "Altitude",
                "description": "Current altitude in feet",
                "path": "trail.0.alt",
                "type": "number",
                "category": "position",
                "format": "altitude"
            },
            {
                "id": "speed",
                "name": "Speed",
                "description": "Current speed in knots",
                "path": "trail.0.spd",
                "type": "number",
                "category": "position",
                "format": "speed"
            },
            {
                "id": "heading",
                "name": "Heading",
                "description": "Current heading in degrees",
                "path": "trail.0.hd",
                "type": "number",
                "category": "position",
                "format": "heading"
            },
            {
                "id": "latitude",
                "name": "Latitude",
                "description": "Current latitude",
                "path": "trail.0.lat",
                "type": "number",
                "category": "position"
            },
            {
                "id": "longitude",
                "name": "Longitude",
                "description": "Current longitude",
                "path": "trail.0.lng",
                "type": "number",
                "category": "position"
            },
            {
                "id": "route_codes",
                "name": "Route Codes",
                "description": "Origin-Destination codes",
                "type": "computed",
                "category": "route",
                "formula": "airport_origin_code + '-' + airport_destination_code"
            },
            {
                "id": "route_full",
                "name": "Route Full Names",
                "description": "Origin-Destination full names",
                "type": "computed",
                "category": "route",
                "formula": "airport_origin_name + '-' + airport_destination_name"
            },
            {
                "id": "route_with_altitude",
                "name": "Route with Altitude",
                "description": "Route codes with current altitude",
                "type": "computed",
                "category": "route",
                "formula": "route_codes + ' @ ' + altitude + 'ft'"
            },
            {
                "id": "aircraft_with_speed",
                "name": "Aircraft with Speed",
                "description": "Aircraft model with current speed",
                "type": "computed",
                "category": "aircraft",
                "formula": "aircraft_model + ' ' + speed + 'kts'"
            },
            {
                "id": "speed_and_heading",
                "name": "Speed and Heading",
                "description": "Speed and heading combined",
                "type": "computed",
                "category": "position",
                "formula": "speed + 'kts @ ' + heading + '°'"
            },
            {
                "id": "altitude_detailed",
                "name": "Altitude Detailed",
                "description": "Altitude with thousands separator",
                "type": "computed",
                "category": "position",
                "formula": "format(altitude, ',') + 'ft'"
            }
        ]
    }

# Initialize config files if they don't exist
if not os.path.exists(DEVICE_CONFIG_PATH):
    save_json(DEVICE_CONFIG_PATH, get_default_device_config())
if not os.path.exists(LAYOUTS_CONFIG_PATH):
    save_json(LAYOUTS_CONFIG_PATH, get_default_layouts())
if not os.path.exists(FIELDS_CONFIG_PATH):
    save_json(FIELDS_CONFIG_PATH, get_default_fields())

# ==================== Web Routes ====================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

# ==================== API Endpoints ====================

# Device Configuration Endpoints
@app.route('/api/config', methods=['GET'])
@require_auth('device')
def get_config():
    """Get complete device configuration"""
    config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
    return jsonify(config)

@app.route('/api/config', methods=['PUT'])
@require_auth('admin')
def update_config():
    """Update complete device configuration"""
    try:
        data = request.json
        data['last_updated'] = datetime.now().isoformat()
        if save_json(DEVICE_CONFIG_PATH, data):
            return jsonify({"success": True, "message": "Configuration updated"})
        return jsonify({"success": False, "message": "Failed to save configuration"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# WiFi Settings
@app.route('/api/config/wifi', methods=['GET'])
@require_auth('device')
def get_wifi():
    """Get WiFi settings"""
    config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
    return jsonify(config.get('wifi', {}))

@app.route('/api/config/wifi', methods=['PUT'])
@require_auth('admin')
def update_wifi():
    """Update WiFi settings"""
    try:
        config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
        config['wifi'] = request.json
        config['last_updated'] = datetime.now().isoformat()
        if save_json(DEVICE_CONFIG_PATH, config):
            return jsonify({"success": True, "message": "WiFi settings updated"})
        return jsonify({"success": False, "message": "Failed to save WiFi settings"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# Location/Bounds Settings
@app.route('/api/config/bounds', methods=['GET'])
@require_auth('device')
def get_bounds():
    """Get geographic bounds"""
    config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
    return jsonify(config.get('location', {}))

@app.route('/api/config/bounds', methods=['PUT'])
@require_auth('admin')
def update_bounds():
    """Update geographic bounds"""
    try:
        config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
        config['location'] = request.json
        config['last_updated'] = datetime.now().isoformat()
        if save_json(DEVICE_CONFIG_PATH, config):
            return jsonify({"success": True, "message": "Location bounds updated"})
        return jsonify({"success": False, "message": "Failed to save location bounds"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# Layout Management
@app.route('/api/layouts', methods=['GET'])
@require_auth('device')
def get_layouts():
    """Get all layouts"""
    layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())
    return jsonify(layouts)

@app.route('/api/layouts/<layout_id>', methods=['GET'])
@require_auth('device')
def get_layout(layout_id):
    """Get specific layout by ID"""
    layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())
    for layout in layouts.get('layouts', []):
        if layout['id'] == layout_id:
            return jsonify(layout)
    return jsonify({"error": "Layout not found"}), 404

@app.route('/api/layouts', methods=['POST'])
@require_auth('admin')
def create_layout():
    """Create new layout"""
    try:
        layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())
        new_layout = request.json

        # Validate layout has required fields
        if 'id' not in new_layout or 'name' not in new_layout:
            return jsonify({"success": False, "message": "Layout must have id and name"}), 400

        # Check if ID already exists
        for layout in layouts.get('layouts', []):
            if layout['id'] == new_layout['id']:
                return jsonify({"success": False, "message": "Layout ID already exists"}), 400

        layouts.setdefault('layouts', []).append(new_layout)
        if save_json(LAYOUTS_CONFIG_PATH, layouts):
            return jsonify({"success": True, "message": "Layout created", "layout": new_layout})
        return jsonify({"success": False, "message": "Failed to save layout"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/layouts/<layout_id>', methods=['PUT'])
@require_auth('admin')
def update_layout(layout_id):
    """Update existing layout"""
    try:
        layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())
        updated_layout = request.json

        for i, layout in enumerate(layouts.get('layouts', [])):
            if layout['id'] == layout_id:
                layouts['layouts'][i] = updated_layout
                if save_json(LAYOUTS_CONFIG_PATH, layouts):
                    return jsonify({"success": True, "message": "Layout updated"})
                return jsonify({"success": False, "message": "Failed to save layout"}), 500

        return jsonify({"success": False, "message": "Layout not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/layouts/<layout_id>', methods=['DELETE'])
@require_auth('admin')
def delete_layout(layout_id):
    """Delete layout"""
    try:
        layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())

        for i, layout in enumerate(layouts.get('layouts', [])):
            if layout['id'] == layout_id:
                del layouts['layouts'][i]
                if save_json(LAYOUTS_CONFIG_PATH, layouts):
                    return jsonify({"success": True, "message": "Layout deleted"})
                return jsonify({"success": False, "message": "Failed to delete layout"}), 500

        return jsonify({"success": False, "message": "Layout not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/config/active-layout', methods=['PUT'])
@require_auth('admin')
def set_active_layout():
    """Set active layout"""
    try:
        config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
        data = request.json
        config['active_layout'] = data.get('layout_id')
        config['last_updated'] = datetime.now().isoformat()
        if save_json(DEVICE_CONFIG_PATH, config):
            return jsonify({"success": True, "message": "Active layout updated"})
        return jsonify({"success": False, "message": "Failed to save active layout"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# Field Management
@app.route('/api/fields/available', methods=['GET'])
@require_auth('device')
def get_available_fields():
    """Get all available API fields"""
    fields = load_json(FIELDS_CONFIG_PATH, get_default_fields())
    return jsonify(fields)

# Display Settings
@app.route('/api/display/colors', methods=['GET'])
@require_auth('device')
def get_colors():
    """Get color settings"""
    config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
    layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())
    active_layout_id = config.get('active_layout', 'classic')

    # Get colors from active layout
    for layout in layouts.get('layouts', []):
        if layout['id'] == active_layout_id:
            colors = {
                'plane_color': config.get('display', {}).get('plane_color', '0x4B0082'),
                'rows': [{'y': row['y'], 'color': row['color']} for row in layout.get('rows', [])]
            }
            return jsonify(colors)

    return jsonify({"plane_color": "0x4B0082", "rows": []})

@app.route('/api/display/timing', methods=['GET'])
@require_auth('device')
def get_timing():
    """Get timing settings"""
    config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
    return jsonify({
        'query_delay': config.get('query_delay', 30),
        'display': config.get('display', {})
    })

@app.route('/api/display/timing', methods=['PUT'])
@require_auth('admin')
def update_timing():
    """Update timing settings"""
    try:
        config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
        data = request.json

        if 'query_delay' in data:
            config['query_delay'] = data['query_delay']
        if 'display' in data:
            config['display'].update(data['display'])

        config['last_updated'] = datetime.now().isoformat()
        if save_json(DEVICE_CONFIG_PATH, config):
            return jsonify({"success": True, "message": "Timing settings updated"})
        return jsonify({"success": False, "message": "Failed to save timing settings"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# System Status
@app.route('/api/status', methods=['GET'])
@require_auth('device')
def get_status():
    """Get system status"""
    config = load_json(DEVICE_CONFIG_PATH, get_default_device_config())
    layouts = load_json(LAYOUTS_CONFIG_PATH, get_default_layouts())

    status = {
        "server": "running",
        "config_loaded": True,
        "active_layout": config.get('active_layout', 'classic'),
        "total_layouts": len(layouts.get('layouts', [])),
        "last_updated": config.get('last_updated', 'Never'),
        "wifi_configured": config.get('wifi', {}).get('ssid') != 'your-network'
    }
    return jsonify(status)

# ==================== OTA Firmware Update Endpoints ====================

# Firmware storage
FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), 'firmware')
FIRMWARE_MANIFEST_PATH = os.path.join(FIRMWARE_DIR, 'manifest.json')

# Ensure firmware directory exists
os.makedirs(FIRMWARE_DIR, exist_ok=True)

def get_firmware_manifest():
    """Get firmware manifest with version info"""
    try:
        if os.path.exists(FIRMWARE_MANIFEST_PATH):
            with open(FIRMWARE_MANIFEST_PATH, 'r') as f:
                return json.load(f)
        return {
            "current_version": "3.0.0",
            "versions": [
                {
                    "version": "3.0.0",
                    "released": datetime.now().isoformat(),
                    "changelog": "Initial OTA support release",
                    "filename": "code_v3_ota.py",
                    "mandatory": False
                }
            ]
        }
    except Exception as e:
        print(f"Error loading firmware manifest: {e}")
        return {"current_version": "3.0.0", "versions": []}

def save_firmware_manifest(manifest):
    """Save firmware manifest"""
    try:
        with open(FIRMWARE_MANIFEST_PATH, 'w') as f:
            json.dump(manifest, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving firmware manifest: {e}")
        return False

@app.route('/api/firmware/check', methods=['GET'])
@require_auth('device')
def check_firmware():
    """Check if firmware update is available"""
    device_version = request.args.get('version', '0.0.0')
    manifest = get_firmware_manifest()
    current_version = manifest.get('current_version', '3.0.0')

    # Simple version comparison (semver would be better)
    device_parts = [int(x) for x in device_version.split('.')]
    current_parts = [int(x) for x in current_version.split('.')]

    update_available = (
        current_parts[0] > device_parts[0] or
        (current_parts[0] == device_parts[0] and current_parts[1] > device_parts[1]) or
        (current_parts[0] == device_parts[0] and current_parts[1] == device_parts[1] and current_parts[2] > device_parts[2])
    )

    if update_available:
        # Find the version info
        version_info = next((v for v in manifest.get('versions', []) if v['version'] == current_version), {})
        protocol = 'https' if SECURITY_CONFIG['ssl_enabled'] else 'http'
        return jsonify({
            "update_available": True,
            "version": current_version,
            "changelog": version_info.get('changelog', 'No changelog available'),
            "mandatory": version_info.get('mandatory', False),
            "download_url": f"{protocol}://{request.host}/api/firmware/download"
        })
    else:
        return jsonify({
            "update_available": False,
            "current_version": device_version
        })

@app.route('/api/firmware/download', methods=['GET'])
@require_auth('device')
def download_firmware():
    """Download latest firmware with code signature"""
    manifest = get_firmware_manifest()
    current_version = manifest.get('current_version', '3.0.0')

    # Find the firmware file for current version
    version_info = next((v for v in manifest.get('versions', []) if v['version'] == current_version), {})
    filename = version_info.get('filename', 'code_v3_ota.py')

    # Try to find the file in firmware directory or root directory
    firmware_path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(firmware_path):
        # Try parent directory
        firmware_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)

    if os.path.exists(firmware_path):
        with open(firmware_path, 'r') as f:
            firmware_code = f.read()

        # Sign the firmware
        signature = sign_firmware(firmware_code)

        # Return firmware with signature in header
        response = app.make_response((firmware_code, 200))
        response.headers['Content-Type'] = 'text/plain'
        response.headers['X-Firmware-Signature'] = signature
        response.headers['X-Firmware-Version'] = current_version
        return response
    else:
        return jsonify({"error": "Firmware file not found"}), 404

@app.route('/api/firmware/upload', methods=['POST'])
@require_auth('admin')
def upload_firmware():
    """Upload new firmware version"""
    try:
        data = request.json
        version = data.get('version')
        changelog = data.get('changelog', 'No changelog provided')
        code = data.get('code')
        mandatory = data.get('mandatory', False)

        if not version or not code:
            return jsonify({"success": False, "message": "Version and code are required"}), 400

        # Save firmware file
        filename = f"code_{version.replace('.', '_')}.py"
        firmware_path = os.path.join(FIRMWARE_DIR, filename)

        with open(firmware_path, 'w') as f:
            f.write(code)

        # Update manifest
        manifest = get_firmware_manifest()
        manifest['current_version'] = version

        # Add version to list if not exists
        if not any(v['version'] == version for v in manifest.get('versions', [])):
            manifest.setdefault('versions', []).append({
                "version": version,
                "released": datetime.now().isoformat(),
                "changelog": changelog,
                "filename": filename,
                "mandatory": mandatory
            })

        save_firmware_manifest(manifest)

        return jsonify({
            "success": True,
            "message": f"Firmware version {version} uploaded successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/firmware/versions', methods=['GET'])
@require_auth('device')
def list_firmware_versions():
    """List all available firmware versions"""
    manifest = get_firmware_manifest()
    return jsonify(manifest)

if __name__ == '__main__':
    print("=" * 80)
    print("Flight Portal Web Interface - SECURE MODE")
    print("=" * 80)
    print()

    # Security status
    if SECURITY_CONFIG['admin_api_key'] == "INSECURE_DEFAULT_ADMIN_KEY":
        print("⚠️  WARNING: Using default insecure keys!")
        print("⚠️  Run 'python generate_keys.py' to generate secure keys")
        print()
    else:
        print("✅ Security keys loaded from .secrets.json")

    # SSL status
    protocol = "https" if SECURITY_CONFIG['ssl_enabled'] else "http"
    if SECURITY_CONFIG['ssl_enabled']:
        print("✅ HTTPS enabled")
        ssl_context = (
            SECURITY_CONFIG['ssl_cert'],
            SECURITY_CONFIG['ssl_key']
        )
    else:
        print("⚠️  HTTPS disabled - using HTTP")
        print("   Run 'python generate_keys.py' to generate SSL certificates")
        ssl_context = None

    print()
    print(f"Server URL: {protocol}://localhost:3100")
    print(f"Also accessible at: {protocol}://flightportal:3100 (if hosts file configured)")
    print()
    print(f"Config directory: {CONFIG_DIR}")
    print(f"Firmware directory: {FIRMWARE_DIR}")
    print()
    print("=" * 80)
    print()

    if ssl_context:
        app.run(host='0.0.0.0', port=3100, debug=True, ssl_context=ssl_context)
    else:
        app.run(host='0.0.0.0', port=3100, debug=True)
