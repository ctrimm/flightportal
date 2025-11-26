# Flight Portal Web Interface

A modern web-based CRUD interface for managing your MatrixPortal flight display settings.

## Features

- 📊 **Dashboard** - System status overview
- 🎨 **Layout Manager** - Switch between different display layouts
- 📝 **Display Fields** - View all available API data fields
- 📡 **WiFi Configuration** - Set up network credentials
- 📍 **Location Settings** - Define geographic search bounds
- 🎬 **Display Settings** - Adjust animations, speeds, and timing

## Quick Start

### 1. Install Dependencies

```bash
cd web-interface
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:3100`

### 3. Set Up Hostname (Optional)

To access via `http://flightportal:3100`, you need to add a hosts file entry:

**Linux/Mac:**
```bash
sudo ./setup-hostname.sh
```

**Windows (Run as Administrator):**
```bash
./setup-hostname.bat
```

Or manually add this line to your hosts file:
- Linux/Mac: `/etc/hosts`
- Windows: `C:\Windows\System32\drivers\etc\hosts`

```
127.0.0.1    flightportal
```

## Access URLs

- **http://localhost:3100** - Direct local access
- **http://flightportal:3100** - Hostname access (after hosts file setup)
- **http://YOUR_IP:3100** - Network access (from other devices on same network)

## Configuration Files

All settings are stored in the `config/` directory:

- **device_config.json** - Main device settings (WiFi, location, active layout, timing)
- **layouts.json** - Layout definitions
- **fields.json** - Available API field definitions

These files are automatically created with defaults on first run.

## Device Integration

### How It Works

1. **Web Interface** manages configuration files locally
2. **Device (MatrixPortal)** polls the web server for configuration updates
3. **Device** applies new settings without requiring code re-upload

### Device Code Requirements

The MatrixPortal device code needs to:
1. Connect to WiFi
2. Periodically fetch config from `http://flightportal:3100/api/config`
3. Parse and apply the configuration
4. Render flights using the active layout

## API Reference

### Configuration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config` | GET | Get complete device configuration |
| `/api/config` | PUT | Update complete device configuration |
| `/api/config/wifi` | GET | Get WiFi settings |
| `/api/config/wifi` | PUT | Update WiFi settings |
| `/api/config/bounds` | GET | Get geographic bounds |
| `/api/config/bounds` | PUT | Update geographic bounds |
| `/api/config/active-layout` | PUT | Set active layout |

### Layout Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/layouts` | GET | List all layouts |
| `/api/layouts/:id` | GET | Get specific layout |
| `/api/layouts` | POST | Create new layout |
| `/api/layouts/:id` | PUT | Update layout |
| `/api/layouts/:id` | DELETE | Delete layout |

### Field Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/fields/available` | GET | List all available API fields |

### Display Settings Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/display/colors` | GET | Get color settings |
| `/api/display/timing` | GET | Get timing settings |
| `/api/display/timing` | PUT | Update timing settings |

### System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Get system status |

## Development

### Project Structure

```
web-interface/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/                # Configuration files (auto-generated)
│   ├── device_config.json
│   ├── layouts.json
│   └── fields.json
├── static/                # Static assets (CSS, JS, images)
│   ├── css/
│   └── js/
└── templates/             # HTML templates
    └── index.html         # Main UI
```

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Running in Production

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3100 app:app
```

## Customization

### Adding a New Layout

1. Go to the **Layouts** tab
2. Click **Create New Layout** (UI feature to be added)
3. Or manually edit `config/layouts.json`:

```json
{
  "id": "my-layout",
  "name": "My Custom Layout",
  "description": "Description of what this layout shows",
  "rows": [
    {
      "y": 4,
      "color": "0xEE82EE",
      "short_field": "flight_number",
      "long_field": "airline_name"
    }
  ]
}
```

### Adding a New Field

Fields are defined in `config/fields.json`. You can add:

1. **API Fields** - Direct paths from FlightRadar24 JSON
2. **Computed Fields** - Combinations of other fields

Example API field:
```json
{
  "id": "my_field",
  "name": "My Field",
  "description": "Description",
  "path": "path.to.json.value",
  "type": "string",
  "category": "identification"
}
```

Example computed field:
```json
{
  "id": "my_computed_field",
  "name": "My Computed Field",
  "description": "Description",
  "type": "computed",
  "category": "custom",
  "formula": "field1 + ' - ' + field2"
}
```

## Troubleshooting

### Port Already in Use

If port 3100 is already in use, change it in `app.py`:

```python
app.run(host='0.0.0.0', port=YOUR_PORT, debug=True)
```

### CORS Errors

If you're accessing from a different domain, CORS is enabled by default. If issues persist, check your browser console and ensure Flask-CORS is installed.

### Cannot Access via Hostname

1. Verify hosts file entry: `cat /etc/hosts | grep flightportal`
2. Clear DNS cache:
   - Mac: `sudo dscacheutil -flushcache`
   - Windows: `ipconfig /flushdns`
   - Linux: `sudo systemd-resolve --flush-caches`

### Configuration Not Saving

1. Check file permissions in `config/` directory
2. Check console output for error messages
3. Verify JSON syntax if editing files manually

## Security Notes

- This interface is designed for **local network use only**
- WiFi passwords are stored in plain text in `device_config.json`
- For remote access, set up authentication and HTTPS
- Do not expose this server directly to the internet

## Support

For issues, questions, or feature requests:
1. Check the main project README
2. Review the TO-DO.md file for planned features
3. Check the troubleshooting section above

## License

Same as the main Flight Portal project.
