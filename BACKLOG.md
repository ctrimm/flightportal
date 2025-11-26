# Flight Portal Feature Backlog

This document tracks future features and enhancements planned for Flight Portal.

## Priority: High (Next Release)

### ✅ Tail Number Tracking & Watchlist (IN PROGRESS)
Track specific aircraft by tail number and get alerted when they're in your area.

**Features:**
- Add multiple tail numbers to personal watchlist
- Visual alerts when tracked aircraft detected
- Special display layout for watchlist aircraft
- Persistent storage per device
- Activity history (when tracked aircraft were seen)

**Target Users:**
- Flight school operators tracking student aircraft
- Pilots watching for friends/flying buddies
- Flying clubs monitoring club aircraft
- FBOs tracking customer aircraft
- Aviation enthusiasts following specific planes

**Status:** Currently implementing

---

## Priority: Medium (Future Releases)

### METAR/TAF Display Mode
Display current weather conditions and forecasts for local airport(s).

**Features:**
- Current METAR (weather observation)
- TAF (Terminal Aerodrome Forecast)
- Decode and display key info:
  - Wind speed/direction
  - Visibility
  - Cloud coverage
  - Temperature/dewpoint
  - Altimeter setting
- Toggle between flight tracking and weather modes
- Multiple airport monitoring

**Data Source:** Aviation Weather Center API (aviationweather.gov)

**Use Cases:**
- Pre-flight weather check at home
- FBO lobby displays
- Flight school briefing rooms
- Hangar displays

**Estimated Effort:** Medium (API integration, display layouts)

---

### NOTAM (Notice to Airmen) Alerts
Display active NOTAMs for your local area.

**Features:**
- Fetch NOTAMs for configured airports/radius
- Filter by type (runway closures, airspace restrictions, etc.)
- Highlight critical NOTAMs
- Scrolling display for multiple NOTAMs
- Auto-refresh every 30 minutes

**Data Source:** FAA NOTAM API

**Use Cases:**
- Daily briefing displays
- Flight planning reminders
- Airport operations awareness
- FBO information displays

**Estimated Effort:** Medium-High (NOTAM parsing complexity)

---

### Sunrise/Sunset Times
Display sunrise/sunset times for VFR flight planning.

**Features:**
- Local sunrise/sunset based on location
- Civil, nautical, and astronomical twilight
- Time until sunset (for day VFR planning)
- Visual indicator of current phase (day/night/twilight)
- Automatic timezone handling

**Data Source:** Calculate locally or use sunrise-sunset.org API

**Use Cases:**
- VFR flight planning
- Night currency tracking
- Airport operations planning
- Pilot briefing displays

**Estimated Effort:** Low (straightforward API/calculation)

---

### TFR (Temporary Flight Restriction) Alerts
Display active TFRs in your area with visual warnings.

**Features:**
- Fetch active TFRs within configured radius
- Visual alert when TFR is active nearby
- Display TFR details:
  - Type (presidential, sporting event, etc.)
  - Altitude restrictions
  - Effective times
  - Distance from your location
- Flashing warning for TFRs affecting your area
- Map-style display showing TFR boundary

**Data Source:** FAA TFR API

**Use Cases:**
- Critical safety information
- Pre-flight planning
- Flight school briefings
- Avoiding airspace violations

**Priority Note:** High safety value - consider moving up priority

**Estimated Effort:** High (real-time alerts, map display on small LED)

---

## Priority: Low (Nice to Have)

### Aircraft Type Database with Photos
Enhanced aircraft identification with type details.

**Features:**
- Aircraft type lookup (e.g., "C172" → "Cessna 172 Skyhawk")
- Manufacturer information
- Basic specifications (seats, cruise speed, etc.)
- ASCII art representations for LED display
- Option to show photos on web interface

**Data Source:** Build from FAA registry + aviation databases

**Estimated Effort:** Medium (data collection and storage)

---

### Flight Path History
Track and display recent aircraft movement paths.

**Features:**
- Store last N positions for each aircraft
- Draw flight path on virtual display
- Show direction of travel
- Highlight interesting patterns (circles, approaches)
- Export flight logs

**Estimated Effort:** Medium-High (data storage, visualization)

---

### ADS-B Integration (Advanced)
Direct ADS-B receiver integration as alternative to FlightRadar24.

**Features:**
- Support for dump1090/readsb receivers
- Local ADS-B data parsing
- No internet dependency (after setup)
- More accurate local tracking
- Filter by distance/altitude

**Hardware Required:** RTL-SDR dongle + antenna

**Estimated Effort:** Very High (hardware integration, protocol parsing)

**Note:** This would be a "Pro" version or separate product

---

### Multi-Airport Tracking
Track multiple airports simultaneously.

**Features:**
- Configure multiple locations
- Cycle through airports
- Show airport identifier (ICAO/IATA)
- Arrivals/departures per airport
- Distance from each airport

**Estimated Effort:** Low (configuration enhancement)

---

### Historical Flight Statistics
Track and display long-term statistics.

**Features:**
- Total flights tracked today/week/month
- Busiest times of day
- Most common aircraft types
- Most common routes
- Tracked aircraft appearances

**Estimated Effort:** Medium (requires data storage and aggregation)

---

### Voice Alerts (Experimental)
Audio notifications for tracked aircraft.

**Features:**
- Small speaker integration
- Text-to-speech announcements
- "N12345 is 5 miles northwest"
- Configurable alert distance
- Volume control via web interface

**Hardware Required:** I2S audio DAC + speaker

**Estimated Effort:** High (hardware integration, audio synthesis)

---

### Mobile App Companion
Smartphone app for on-the-go management.

**Features:**
- Remote watchlist management
- Push notifications for tracked aircraft
- View live display remotely
- Change layouts from phone
- Fleet management for multiple devices

**Estimated Effort:** Very High (mobile development for iOS/Android)

---

## Research / Future Exploration

### Integration Ideas
- **Home Assistant Integration**: Control via smart home
- **Discord/Slack Webhooks**: Notifications to chat platforms
- **Alexa/Google Home**: Voice queries ("Are there flights overhead?")
- **IFTTT Integration**: Trigger other automations
- **Flight Simulator Integration**: Display AI traffic in X-Plane/MSFS

### Alternative Display Hardware
- **E-Ink Display**: Lower power, outdoor visibility
- **OLED Display**: Higher contrast, lower power
- **Larger Matrix**: 128x64 or 128x32 for more info
- **RGB Strip**: Ambient lighting based on air traffic

### Business/Commercial Features
- **Multi-Tenant Dashboard**: Manage multiple customer devices
- **White-Label Option**: Rebrand for flight schools/FBOs
- **API Access**: Let customers build custom integrations
- **Fleet Analytics**: Aggregate data across all devices
- **Usage-Based Licensing**: Premium features via subscription

---

## Community Requests

*This section will be populated with user-requested features*

---

## Version Planning

### v1.0 (Current)
- Basic flight tracking
- Web configuration
- OTA updates
- Multiple layouts
- Stripe checkout

### v1.1 (Next - Pilot Focus)
- **Tail number watchlist** ✈️
- Social proof on marketing site
- Pilot-focused messaging

### v1.2 (Weather)
- METAR/TAF display
- Sunrise/sunset times

### v1.3 (Safety)
- NOTAM alerts
- TFR warnings

### v2.0 (Advanced)
- ADS-B integration
- Mobile app
- Advanced analytics

---

## How to Request Features

Users can request features by:
1. Opening an issue on GitHub
2. Emailing: support@flightportal.com
3. Voting on existing feature requests

**Note:** Features will be prioritized based on:
- User demand
- Safety value
- Implementation complexity
- Alignment with pilot/aviation focus
