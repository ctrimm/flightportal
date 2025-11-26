# Flight Portal Restructure - TO-DO Punchlist

## 📋 Project Overview
Restructure the flight portal application to support:
- Dynamic layout switching
- Configurable display fields from API data
- Web-based CRUD interface for settings management
- Local hostname access (flightportal → localhost:3100)

---

## ✅ COMPLETED TASKS

### Phase 0: Assessment & Planning
- [x] Analyzed current codebase structure
- [x] Identified functionality and limitations
- [x] Created new branch: `claude/flight-portal-restructure-01ApyALdQraKQiyGqiDcagkd`
- [x] Created this TO-DO.md punchlist

---

## 🔄 IN PROGRESS

### Phase 1: Current Application Assessment
- [ ] **Functionality Review**
  - Code appears functional but needs testing
  - Hardcoded WiFi credentials in secrets.py (placeholder values)
  - Fixed 3-row layout with no runtime flexibility
  - Many API fields commented out (altitude, speed, heading, registration, etc.)
  - No remote configuration capability

---

## 📝 PENDING TASKS

### Phase 2: Architecture Design

#### 2.1 System Components
- [ ] Design three-tier architecture:
  - **Device Layer**: CircuitPython code on MatrixPortal
  - **Config Layer**: JSON-based configuration system
  - **Web Interface Layer**: Local web server for management

#### 2.2 Configuration System
- [ ] Design JSON schema for device configuration
  - WiFi settings
  - Geographic bounds
  - Layout templates
  - Display field mappings
  - Colors and timing parameters
  - API settings
- [ ] Create layout template format (JSON)
- [ ] Design field mapping system (API → Display)

#### 2.3 Communication Protocol
- [ ] Device polls web server for configuration updates
- [ ] RESTful API endpoints for config management
- [ ] Fallback to default config if server unavailable

---

### Phase 3: Web Interface Development

#### 3.1 Project Setup
- [ ] Choose web framework (Flask recommended for simplicity)
- [ ] Create project structure:
  ```
  web-interface/
  ├── app.py              # Flask application
  ├── requirements.txt     # Python dependencies
  ├── config/
  │   ├── device_config.json
  │   └── layouts.json
  ├── static/
  │   ├── css/
  │   └── js/
  └── templates/
      └── index.html
  ```
- [ ] Set up virtual environment
- [ ] Install dependencies (Flask, Flask-CORS, etc.)

#### 3.2 Backend API Development
- [ ] **Settings Management Endpoints**
  - [ ] `GET /api/config` - Get current device configuration
  - [ ] `PUT /api/config` - Update device configuration
  - [ ] `GET /api/config/wifi` - Get WiFi settings
  - [ ] `PUT /api/config/wifi` - Update WiFi settings
  - [ ] `GET /api/config/bounds` - Get geographic bounds
  - [ ] `PUT /api/config/bounds` - Update geographic bounds

- [ ] **Layout Management Endpoints**
  - [ ] `GET /api/layouts` - List all available layouts
  - [ ] `GET /api/layouts/:id` - Get specific layout
  - [ ] `POST /api/layouts` - Create new layout
  - [ ] `PUT /api/layouts/:id` - Update layout
  - [ ] `DELETE /api/layouts/:id` - Delete layout
  - [ ] `PUT /api/config/active-layout` - Set active layout

- [ ] **Field Management Endpoints**
  - [ ] `GET /api/fields/available` - List all available API fields
  - [ ] `GET /api/fields/active` - Get currently displayed fields
  - [ ] `PUT /api/fields/active` - Update displayed fields

- [ ] **Display Settings Endpoints**
  - [ ] `GET /api/display/colors` - Get color settings
  - [ ] `PUT /api/display/colors` - Update colors
  - [ ] `GET /api/display/timing` - Get timing settings
  - [ ] `PUT /api/display/timing` - Update timing (speeds, delays)

- [ ] **System Endpoints**
  - [ ] `GET /api/status` - Device connection status
  - [ ] `POST /api/restart` - Signal device restart
  - [ ] `GET /api/logs` - View device logs (if implemented)

#### 3.3 Frontend Development
- [ ] **Dashboard Page**
  - [ ] Current device status display
  - [ ] Quick stats (active layout, last update, flights detected)
  - [ ] Connection status indicator

- [ ] **WiFi Settings Page**
  - [ ] SSID input field
  - [ ] Password input field (masked)
  - [ ] Connection test button
  - [ ] Save button

- [ ] **Geographic Bounds Page**
  - [ ] Visual map interface (optional, using Leaflet.js)
  - [ ] Text input for bounds (lat_top, lat_bottom, lon_left, lon_right)
  - [ ] Preset locations dropdown
  - [ ] Save button

- [ ] **Layout Manager Page**
  - [ ] List of available layouts (card view)
  - [ ] Active layout indicator
  - [ ] "Set Active" button for each layout
  - [ ] "Edit" button for each layout
  - [ ] "Delete" button for each layout
  - [ ] "Create New Layout" button

- [ ] **Layout Editor Page**
  - [ ] Layout name input
  - [ ] Visual 64x32 grid preview
  - [ ] Row configuration:
    - [ ] Number of rows (1-3)
    - [ ] Y position for each row
    - [ ] Color picker for each row
    - [ ] Font selection (if multiple fonts added)
  - [ ] Field mapping for each row:
    - [ ] Short field dropdown (from available API fields)
    - [ ] Long field dropdown (from available API fields)
  - [ ] Save layout button
  - [ ] Preview layout button

- [ ] **Display Fields Page**
  - [ ] List of all available API fields with descriptions
  - [ ] Checkbox to enable/disable each field
  - [ ] Custom format templates for combined fields
  - [ ] Save button

- [ ] **Display Settings Page**
  - [ ] Color pickers for:
    - [ ] Row 1, 2, 3 colors
    - [ ] Plane animation color
    - [ ] Background color (if configurable)
  - [ ] Timing sliders:
    - [ ] Query delay (seconds)
    - [ ] Pause between label scrolling
    - [ ] Plane animation speed
    - [ ] Text scroll speed
  - [ ] Save button

- [ ] **API Settings Page**
  - [ ] FlightRadar24 API URLs (if they change)
  - [ ] Query delay configuration
  - [ ] Filter settings (altitude, airline, etc.)
  - [ ] Save button

#### 3.4 UI/UX Design
- [ ] Create responsive design (mobile-friendly)
- [ ] Add form validation
- [ ] Add loading indicators
- [ ] Add success/error notifications
- [ ] Add confirmation dialogs for destructive actions
- [ ] Add keyboard shortcuts for power users
- [ ] Add help tooltips for complex settings

---

### Phase 4: Device Code Refactoring

#### 4.1 Code Organization
- [ ] Split code.py into multiple modules:
  - [ ] `main.py` - Main application loop
  - [ ] `config.py` - Configuration management
  - [ ] `display.py` - Display rendering logic
  - [ ] `layouts.py` - Layout templates and rendering
  - [ ] `api.py` - FlightRadar24 API interactions
  - [ ] `network.py` - WiFi and HTTP management
  - [ ] `secrets.py` - Keep for backward compatibility

#### 4.2 Configuration System
- [ ] Create Config class to manage settings
- [ ] Implement config fetching from web server
- [ ] Add fallback to default/cached config
- [ ] Add config validation
- [ ] Implement config hot-reload (without device restart)

#### 4.3 Layout System
- [ ] Create Layout class
- [ ] Implement layout template parsing
- [ ] Support dynamic row count (1-5 rows)
- [ ] Support custom Y positions
- [ ] Support custom colors per row
- [ ] Support field mapping (API field → display row)

#### 4.4 Field Mapping System
- [ ] Create comprehensive field extractor from API JSON
- [ ] Add support for:
  - [ ] All commented-out fields (altitude, speed, heading, etc.)
  - [ ] Calculated fields (ETA, time in air, etc.)
  - [ ] Formatted fields (combined airport codes, etc.)
- [ ] Implement field value formatters:
  - [ ] Altitude formatter (ft/m conversion, thousands separator)
  - [ ] Speed formatter (knots/mph/kph conversion)
  - [ ] Heading formatter (degrees to compass direction)
  - [ ] Time formatter (Unix timestamp to readable)
  - [ ] Distance formatter (calculate distance from origin)

#### 4.5 Display Enhancements
- [ ] Add support for more than 3 rows
- [ ] Add support for static (non-scrolling) rows
- [ ] Add support for icons/sprites per layout
- [ ] Add support for different scroll speeds per row
- [ ] Add support for different animations (fade, slide, etc.)
- [ ] Add support for conditional display (show only if field exists)

#### 4.6 API Enhancements
- [ ] Uncomment and enable all available API fields
- [ ] Add response caching to reduce API calls
- [ ] Add retry logic with exponential backoff
- [ ] Add API error handling improvements
- [ ] Add filter support (altitude min/max, airline whitelist, etc.)

#### 4.7 Network Enhancements
- [ ] Implement config polling (check for updates every N minutes)
- [ ] Add HTTP client for web interface communication
- [ ] Add mDNS support (if available in CircuitPython)
- [ ] Add config push notification (webhook from web to device)

---

### Phase 5: Layout Templates

#### 5.1 Default Layouts
- [ ] **Classic Layout** (current 3-row design)
  - Row 1: Flight Number → Airline
  - Row 2: Route Codes → Full Route
  - Row 3: Aircraft Code → Aircraft Model

- [ ] **Detailed Layout** (more info)
  - Row 1: Flight Number + Airline
  - Row 2: Route with altitude
  - Row 3: Aircraft + Speed + Heading
  - Row 4: Registration + Distance

- [ ] **Minimal Layout** (clean, simple)
  - Row 1: Flight Number
  - Row 2: Route Codes

- [ ] **Tracking Layout** (real-time data focus)
  - Row 1: Flight Number + Callsign
  - Row 2: Altitude + Speed
  - Row 3: Heading + Position

- [ ] **Arrival/Departure Layout** (time-focused)
  - Row 1: Flight Number
  - Row 2: Route + Departure Time
  - Row 3: ETA + Current Status

#### 5.2 Layout Features
- [ ] Add layout preview images
- [ ] Add layout descriptions
- [ ] Add layout tags/categories
- [ ] Add layout sharing/export (JSON export)
- [ ] Add layout import

---

### Phase 6: Configuration Files

#### 6.1 Create Default Configurations
- [ ] `device_config.json` - Main device configuration
  ```json
  {
    "wifi": {
      "ssid": "your-network",
      "password": "your-password"
    },
    "location": {
      "bounds_box": "51.6,51.4,-0.3,-0.1",
      "name": "Central London"
    },
    "active_layout": "classic",
    "query_delay": 30,
    "display": {
      "plane_color": "0x4B0082",
      "plane_speed": 0.04,
      "text_speed": 0.04,
      "pause_between_scrolling": 3
    }
  }
  ```

- [ ] `layouts.json` - Layout definitions
  ```json
  {
    "layouts": [
      {
        "id": "classic",
        "name": "Classic",
        "description": "Original 3-row layout",
        "rows": [...]
      }
    ]
  }
  ```

- [ ] `fields.json` - Available API field definitions
  ```json
  {
    "fields": [
      {
        "id": "flight_number",
        "name": "Flight Number",
        "path": "identification.number.default",
        "type": "string"
      }
    ]
  }
  ```

---

### Phase 7: Local Hostname Setup

#### 7.1 Hosts File Configuration
- [ ] Add entry to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows)
  ```
  127.0.0.1    flightportal
  ```
- [ ] Create setup script for automated hosts file modification
- [ ] Add instructions in README for manual setup

#### 7.2 Web Server Configuration
- [ ] Configure Flask to listen on localhost:3100
- [ ] Add CORS support for cross-origin requests (if needed)
- [ ] Add SSL support (optional, for https://flightportal)

#### 7.3 Alternative Access Methods
- [ ] Add browser extension (optional) for URL rewriting
- [ ] Add reverse proxy setup instructions (nginx/Apache)
- [ ] Add mDNS/Avahi setup for `flightportal.local`

---

### Phase 8: Testing

#### 8.1 Unit Testing
- [ ] Test web API endpoints
- [ ] Test configuration validation
- [ ] Test layout parsing
- [ ] Test field extraction from API responses

#### 8.2 Integration Testing
- [ ] Test device config fetch from web server
- [ ] Test layout switching on device
- [ ] Test field mapping to display
- [ ] Test WiFi reconnection logic

#### 8.3 End-to-End Testing
- [ ] Test complete workflow:
  1. [ ] Start web interface
  2. [ ] Configure WiFi settings
  3. [ ] Set geographic bounds
  4. [ ] Create custom layout
  5. [ ] Set active layout
  6. [ ] Device fetches config and displays flight

#### 8.4 Hardware Testing
- [ ] Test on actual MatrixPortal hardware
- [ ] Test memory usage with new code
- [ ] Test display rendering performance
- [ ] Test WiFi connectivity stability
- [ ] Test watchdog timer functionality

---

### Phase 9: Documentation

#### 9.1 User Documentation
- [ ] Update README.md with new architecture overview
- [ ] Create INSTALLATION.md for setup instructions
- [ ] Create USER_GUIDE.md for web interface usage
- [ ] Create LAYOUTS.md for layout creation guide
- [ ] Create TROUBLESHOOTING.md for common issues

#### 9.2 Developer Documentation
- [ ] Create ARCHITECTURE.md explaining system design
- [ ] Create API_REFERENCE.md for web API endpoints
- [ ] Create DEVELOPMENT.md for contributing guidelines
- [ ] Add inline code comments and docstrings

#### 9.3 Configuration Documentation
- [ ] Create CONFIG_SCHEMA.md documenting JSON schemas
- [ ] Create FIELDS_REFERENCE.md listing all available API fields
- [ ] Create LAYOUT_EXAMPLES.md with sample layouts

---

### Phase 10: Advanced Features (Optional)

#### 10.1 Device Features
- [ ] Multiple flight tracking (queue system)
- [ ] Weather overlay option
- [ ] Clock display when no flights
- [ ] Statistics display (flights per day, etc.)
- [ ] Sound/buzzer notification when flight detected

#### 10.2 Web Interface Features
- [ ] User authentication for remote access
- [ ] Historical flight log viewer
- [ ] Analytics dashboard (most common routes, airlines, etc.)
- [ ] Export data as CSV/JSON
- [ ] Automated backups of configurations
- [ ] Multi-device support (manage multiple displays)

#### 10.3 Integration Features
- [ ] Home Assistant integration
- [ ] MQTT support for IoT ecosystems
- [ ] Webhook notifications (Discord, Slack, etc.)
- [ ] Mobile app (React Native or Flutter)

---

## 🎯 Current Focus
Working on Phase 1: Current Application Assessment

## 📊 Progress Summary
- **Completed**: 4 tasks
- **In Progress**: 1 task
- **Pending**: 100+ tasks
- **Estimated Completion**: Multiple phases over several iterations

---

## 📝 Notes

### Design Decisions
1. **Why Flask?**: Lightweight, easy to set up, Python-based (matches CircuitPython)
2. **Why JSON configs?**: Easy to parse in CircuitPython, human-readable, web-friendly
3. **Why polling vs push?**: CircuitPython HTTP server support is limited, polling is more reliable
4. **Why localhost:3100?**: Avoid conflicts with common ports (3000, 8080, 5000)

### Constraints
- MatrixPortal has limited RAM (~200KB free typically)
- 64x32 pixel display limits text density
- CircuitPython has limited library support vs full Python
- Device is WiFi-dependent for configuration updates

### Future Considerations
- Cloud sync for config backups
- OTA (Over-The-Air) firmware updates
- Multi-device fleet management
- Community layout sharing platform

---

**Last Updated**: 2025-11-25
**Branch**: `claude/flight-portal-restructure-01ApyALdQraKQiyGqiDcagkd`
