# Flight Portal ✈️

Real-time flight display system for Adafruit MatrixPortal with web-based configuration interface.

![Flight Portal Demo](https://user-images.githubusercontent.com/103124527/206902629-1f31bd41-d8a8-415e-a35a-625efb20b3d6.MOV)
*(video sped up - speeds and delays are fully configurable)*

## 🎯 What's New in v3

The Flight Portal has been completely restructured with powerful new features:

- **🎨 Dynamic Layouts** - Switch between different display layouts without re-uploading code
- **🌐 Web Interface** - Modern CRUD interface for managing all settings
- **📊 Multiple Layout Templates** - Classic, Detailed, Minimal, and Tracking layouts included
- **📝 Flexible Field Mapping** - Display any combination of API fields (altitude, speed, heading, etc.)
- **⚙️ Remote Configuration** - Device polls web server for settings updates
- **🎬 Adjustable Timing** - Fine-tune animation speeds and delays via web UI
- **🔄 OTA Firmware Updates** - Update device firmware wirelessly (perfect for commercial deployments)

## 📋 Quick Start

### Option 1: Latest with OTA Updates (v3 - Recommended for Commercial)

1. **Install Web Interface**
   ```bash
   cd web-interface
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

2. **Configure via Browser**
   - Open http://localhost:3100
   - Set WiFi credentials and location bounds
   - Choose your preferred layout

3. **Deploy Device Code with OTA**
   - Update `CONFIG_SERVER` in `code_v3_ota.py` with your computer's IP
   - Copy `code_v3_ota.py` to MatrixPortal as `code.py`
   - Devices can now be updated wirelessly!

### Option 2: Standard Web Config (v2)

Use `code_v2.py` for web configuration without OTA updates

### Option 3: Legacy Setup (v1)

Use original `code.py` with manual configuration in `secrets.py`

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete setup instructions
- **[OTA-UPDATES.md](OTA-UPDATES.md)** - OTA firmware update guide (includes licensing for commercial use)
- **[web-interface/README.md](web-interface/README.md)** - Web interface documentation
- **[TO-DO.md](TO-DO.md)** - Detailed feature checklist and roadmap

## 🛠️ Hardware Requirements

1. **[MatrixPortal M4](https://www.adafruit.com/product/4745)** - Adafruit's ESP32-powered LED matrix controller
2. **64x32 RGB LED Matrix Panel (P4)** - Available from Adafruit or AliExpress
3. **[3D Printed Case](https://www.thingiverse.com/thing:5701517)** (optional)
4. **[Acrylic Diffuser](https://www.adafruit.com/product/4749)** (optional)
5. **6x M3 Screws** - 8mm length recommended
6. **USB Power Supply** - 5V, 2A minimum

## 🎨 Available Layouts

### Classic (Default)
- Row 1: Flight Number → Airline Name
- Row 2: Route Codes → Full Route Names
- Row 3: Aircraft Code → Aircraft Model

### Detailed
- Row 1: Flight Number → Airline Name
- Row 2: Route Codes → Route with Altitude
- Row 3: Aircraft Code → Aircraft with Speed
- Row 4: Altitude → Speed and Heading

### Minimal
- Row 1: Flight Number → Airline Name
- Row 2: Route Codes → Full Route Names

### Tracking
- Row 1: Flight Number → Callsign
- Row 2: Altitude → Altitude Detailed
- Row 3: Speed → Speed and Heading

## 📝 Available Data Fields

The system can display any of these fields from the FlightRadar24 API:

**Flight Info:** Flight Number, Callsign, Airline Name
**Aircraft:** Model, Code, Registration
**Route:** Origin/Destination Names & Codes
**Real-time:** Altitude, Speed, Heading, Lat/Lon
**Computed:** Route combinations, formatted values

See `web-interface/config/fields.json` for complete list.

## 🌐 Web Interface Features

- **📊 Dashboard** - System status overview
- **🎨 Layout Manager** - Switch between display layouts
- **📝 Field Browser** - View all available data fields
- **📡 WiFi Configuration** - Set network credentials
- **📍 Location Settings** - Define geographic search area
- **🎬 Display Settings** - Adjust animations and timing
- **ℹ️ System Info** - Configuration and status

Access at: **http://localhost:3100** or **http://flightportal:3100**

## 🔧 Configuration

### Via Web Interface (v2)

All settings managed through the web UI:
- WiFi credentials
- Geographic bounds
- Active layout selection
- Animation speeds
- Query intervals

Configuration is automatically synced to the device every 5 minutes.

### Via Code (v1 Legacy)

Edit `secrets.py`:
```python
secrets = {
    'ssid': 'Your-WiFi-Network',
    'password': 'Your-Password',
    'bounds_box': '51.6,51.4,-0.3,-0.1'  # top,bottom,left,right
}
```

## 🔌 CircuitPython Libraries Required

Install these from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries):

- `adafruit_matrixportal/`
- `adafruit_portalbase/`
- `adafruit_requests.mpy`
- `adafruit_esp32spi/`
- `adafruit_display_text/`
- `adafruit_bitmap_font/`
- `adafruit_io/` (v1 only)
- `neopixel.mpy`

## ⚡ Power Requirements

- **Typical consumption:** ~2W
- **Power method:** USB-C to MatrixPortal, with power pass-through to panel
- **Supply rating:** 5V, 2A minimum recommended

## 🐛 Debugging

Connect via serial console at 115200 baud to see:
- WiFi connection status
- Configuration fetch results
- Flight detection messages
- Error diagnostics

**Mac/Linux:** `screen /dev/tty.usbmodem* 115200`
**Windows:** PuTTY or Tera Term on appropriate COM port

## 🗺️ Setting Geographic Bounds

Your bounds define the rectangular area to search for flights.

**Format:** `top_latitude,bottom_latitude,left_longitude,right_longitude`

**Examples:**
- Central London: `51.6,51.4,-0.3,-0.1`
- New York City: `40.9,40.6,-74.1,-73.8`
- Los Angeles: `34.2,33.9,-118.5,-118.1`

**How to find your coordinates:**
1. Go to [Google Maps](https://maps.google.com)
2. Right-click your location → "What's here?"
3. Copy the coordinates
4. Create a bounding box (±0.1-0.2 degrees)

## 🎯 Project Structure

```
flightportal/
├── code.py              # Original device code (v1)
├── code_v2.py           # New device code with web config (v2)
├── secrets.py           # WiFi credentials (legacy/backup)
├── README.md            # This file
├── INSTALLATION.md      # Detailed setup guide
├── TO-DO.md             # Feature checklist
├── LICENSE              # Non-commercial license
└── web-interface/       # Web configuration interface
    ├── app.py           # Flask application
    ├── requirements.txt # Python dependencies
    ├── README.md        # Web interface docs
    ├── setup-hostname.sh  # Hostname setup (Linux/Mac)
    ├── setup-hostname.bat # Hostname setup (Windows)
    ├── config/          # Configuration files (auto-generated)
    │   ├── device_config.json
    │   ├── layouts.json
    │   └── fields.json
    ├── templates/       # HTML templates
    │   └── index.html
    └── static/          # Static assets
        ├── css/
        └── js/
```

## 🔄 Upgrading from v1 to v2

1. Keep your existing `code.py` and `secrets.py` as backup
2. Set up web interface (see [INSTALLATION.md](INSTALLATION.md))
3. Configure WiFi and location in web interface
4. Update `CONFIG_SERVER` IP in `code_v2.py`
5. Copy `code_v2.py` to device as `code.py`
6. Device will fetch config from web server on startup

The v2 code is backward compatible - if the web server is unavailable, it falls back to `secrets.py` values.

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome! Please note the non-commercial license terms.

## ⚠️ Disclaimer

This project uses unofficial FlightRadar24 API access. The API structure may change at any time, potentially breaking functionality. Use responsibly and respect API rate limits.

## 📜 License

### ⚠️ IMPORTANT: License Restriction for Commercial Use

This project is currently licensed under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

**Current License Allows:**
- ✅ Personal, non-commercial use
- ✅ Modification and derivative works
- ✅ Sharing with attribution

**Current License PROHIBITS:**
- 🚫 **Selling devices or products based on this code**
- 🚫 **Commercial use or resale**
- 🚫 **Offering as a paid service**

### 🏢 If You Want to Sell Devices

**You MUST change the license first!** See [OTA-UPDATES.md](OTA-UPDATES.md) for recommended licenses:
- **MIT License** - Most permissive, allows commercial use
- **Apache 2.0** - Includes patent protection
- **Dual License** - Open source + commercial version
- **Proprietary** - Keep commercial version private

**To change license:**
1. Replace the [LICENSE](LICENSE) file
2. Update README.md (this file)
3. Add copyright headers to code files
4. Commit changes before selling

See [LICENSE](LICENSE) file for current full terms.

## 🙏 Acknowledgments

- Adafruit for the excellent MatrixPortal hardware and libraries
- FlightRadar24 for flight data (unofficial API usage)
- The maker community for inspiration

## 📸 Gallery

![Hardware Assembly](https://user-images.githubusercontent.com/103124527/208709167-dd4b6ff2-4c80-4e38-840f-e5b958e2ed78.jpg)

### Wiring Details (Optional)

For a cleaner installation, you can solder power directly to the matrix panel:

![Wiring 1](https://user-images.githubusercontent.com/103124527/206903066-7af5c076-101e-4598-b3ba-0f64766e4162.jpg)
![Wiring 2](https://user-images.githubusercontent.com/103124527/206903084-42378ce0-b8d8-4810-a18a-f35b9a509752.jpg)
![Wiring 3](https://user-images.githubusercontent.com/103124527/206903089-16d0f7f7-2dc0-4082-a012-0e1c9999a63a.jpg)
![Wiring 4](https://user-images.githubusercontent.com/103124527/206903092-0a131b80-cd20-4c8c-b892-9b0a5c1d544b.jpg)

---

**Made with ✈️ for aviation enthusiasts**
