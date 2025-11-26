# Watchlist Alert Display Layout

This document defines the special display layout used when a tracked aircraft (from the watchlist) is detected.

## Layout Specifications

### Display Dimensions
- **Matrix Size**: 64x32 pixels
- **Colors**: RGB (0-255 each channel)
- **Font**: Built-in bitmap fonts (size 5x7 or 6x10)

### Alert Mode Behavior

When a watchlist aircraft is detected:
1. **Visual Alert**: Flashing red border (2 pixels wide)
2. **Priority Display**: Watchlist aircraft takes display priority
3. **Cycle Time**: If multiple watchlist aircraft, cycle every 5 seconds
4. **Alert Duration**: Show alert layout for 15 seconds minimum

### Layout Structure

```
┌────────────────────────────────────────────────────────┐
│ ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★ (flash border)    │
│ ★                                                    ★ │
│ ★  TRACKED                                           ★ │
│ ★  N12345                    (Large, cyan/yellow)   ★ │
│ ★  Cessna 172                (Medium, white)        ★ │
│ ★  5,500ft  120kts  E        (Small, green)         ★ │
│ ★  12.3mi NW                 (Small, white)         ★ │
│ ★                                                    ★ │
│ ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★                    │
└────────────────────────────────────────────────────────┘
```

### Row Layout (32 pixels height)

**Row 1-2** (Pixels 0-3): Flashing border + header
- Border: 2px, flashing red/yellow (0.5s cycle)
- Text: "TRACKED" (white, bold)

**Row 3** (Pixels 4-11): Tail Number
- Font: Large (6x10 or custom)
- Color: Cyan (0, 255, 255) or Yellow (255, 255, 0)
- Position: Left-aligned, 4px padding
- Example: "N12345"

**Row 4** (Pixels 12-19): Aircraft Type
- Font: Medium (5x7)
- Color: White (255, 255, 255)
- Position: Left-aligned, 4px padding
- Example: "Cessna 172" or "C172"

**Row 5** (Pixels 20-27): Flight Data
- Font: Small (5x7 or 4x6)
- Color: Green (0, 255, 0)
- Position: Three columns
- Format: "ALT  SPD  HDG"
- Example: "5500ft 120kt E"

**Row 6** (Pixels 28-31): Distance & Direction
- Font: Small (5x7 or 4x6)
- Color: White (255, 255, 255)
- Position: Centered or left-aligned
- Format: "DIST DIR"
- Example: "12.3mi NW"

### Color Scheme

**Alert Colors:**
- **Border Flash**: Alternates RED (255, 0, 0) ↔ YELLOW (255, 255, 0)
- **"TRACKED" Label**: WHITE (255, 255, 255)
- **Tail Number**: CYAN (0, 255, 255) or YELLOW (255, 255, 0)
- **Aircraft Type**: WHITE (255, 255, 255)
- **Flight Data**: GREEN (0, 255, 0)
- **Distance/Dir**: WHITE (255, 255, 255)

### Animation Sequence

```python
# Pseudo-code for alert animation
while watchlist_aircraft_detected:
    # Flash border (500ms cycle)
    for frame in range(10):  # 5 seconds total
        if frame % 2 == 0:
            border_color = RED
        else:
            border_color = YELLOW

        draw_border(border_color)
        draw_content()
        sleep(0.5)

    # If multiple watchlist aircraft, switch to next
    if len(watchlist_matches) > 1:
        current_aircraft = next_aircraft()
```

### Data Fields

The following fields should be displayed for watchlist aircraft:

1. **tailNumber** (required)
   - Registration/tail number (e.g., "N12345", "G-ABCD")
   - Source: `flight['registration']` from API

2. **aircraftType** (optional)
   - Short aircraft type (e.g., "C172", "PA28")
   - Source: `flight['aircraft_code']` from API
   - Fallback to full model if code unavailable

3. **altitude** (required)
   - Current altitude in feet
   - Source: `flight['altitude']`
   - Format: "5,500ft" or "5.5kft"

4. **speed** (required)
   - Ground speed in knots
   - Source: `flight['ground_speed']`
   - Format: "120kt" or "120kts"

5. **heading** (required)
   - Heading as cardinal direction
   - Source: Calculate from `flight['track']` (degrees)
   - Format: N, NE, E, SE, S, SW, W, NW

6. **distance** (required)
   - Distance from display location
   - Source: Calculate from lat/lon
   - Format: "12.3mi" or "5.2nm"

7. **direction** (required)
   - Direction from display location
   - Source: Calculate bearing from lat/lon
   - Format: N, NE, E, SE, S, SW, W, NW

### Optional Fields (if space allows)

8. **nickname** (if set in watchlist)
   - User-defined nickname
   - Display instead of or below aircraft type
   - Example: "John's Plane"

9. **airline/operator** (if available)
   - Source: `flight['airline_short']`
   - Example: "Flight School XYZ"

## Implementation Notes

### Firmware Changes (code_v4_watchlist.py)

1. **On Boot**:
   - Fetch watchlist from API: `GET /api/watchlist?deviceId={id}`
   - Store in memory: `watchlist = ['N12345', 'N67890', ...]`

2. **On Each Flight Update**:
   - Check if `flight['registration']` matches any in watchlist
   - If match: Set `alert_mode = True` and `alert_aircraft = flight`

3. **Display Logic**:
   ```python
   if alert_mode and alert_aircraft:
       display_watchlist_alert(alert_aircraft)
   else:
       display_normal_layout(flights)
   ```

4. **Alert Duration**:
   - Show alert for minimum 15 seconds
   - If aircraft still in range after 15s, continue showing
   - If aircraft leaves range, return to normal display

### Web Interface Changes

Add "Watchlist" tab to web interface with:
- **Input field**: Add tail number
- **Optional fields**: Nickname, Notes
- **List view**: Show all watchlist entries
- **Delete button**: Remove from watchlist
- **Test lookup**: Verify tail number format

### Database Schema

```json
{
  "deviceId": "device123",
  "tailNumber": "N12345",
  "added": 1234567890,
  "nickname": "John's Cessna",
  "notes": "Flight school aircraft #3"
}
```

## Testing

### Test Cases

1. **Single watchlist aircraft in range**
   - Expected: Alert layout displays immediately
   - Border flashes red/yellow
   - Shows aircraft details

2. **Multiple watchlist aircraft in range**
   - Expected: Cycles between aircraft every 5 seconds
   - Each gets full alert display
   - Border continues flashing

3. **Watchlist aircraft leaves range**
   - Expected: Returns to normal display after current cycle
   - No abrupt transitions

4. **No watchlist configured**
   - Expected: Normal display mode at all times
   - No alert checking overhead

5. **Invalid tail number in watchlist**
   - Expected: No match (silent fail)
   - Logs warning but continues normal operation

### Visual Testing

Use these test tail numbers for common aircraft:
- **N12345**: Generic test tail number
- **N172SP**: Cessna 172 (common training aircraft)
- **N737NG**: Boeing test flight
- **G-ABCD**: UK-registered aircraft
- **VH-ABC**: Australian aircraft

## Future Enhancements

1. **Audio Alerts**: Beep or tone when watchlist aircraft detected
2. **History Log**: Track when each watchlist aircraft was seen
3. **Proximity Alerts**: Alert only when within X miles
4. **Altitude Filters**: Only alert if above/below certain altitude
5. **Time-Based Filters**: Only alert during certain hours
6. **Push Notifications**: Send to mobile app when detected
7. **Multiple Devices**: Share watchlist across devices
8. **Pattern Recognition**: Learn pilot's common routes

## Reference Layouts

For comparison, here are the existing normal layouts:

### Normal Layout (3-row)
```
Row 1: N12345  AA1234  UA567
Row 2: 5500ft  12000ft 35000ft
Row 3: 12mi NW 8mi N   45mi E
```

### Normal Layout (detail view)
```
Row 1: N12345
Row 2: Cessna 172
Row 3: 5500ft 120kt E
Row 4: 12.3mi NW
```

The watchlist alert should be visually distinct from normal layouts with the flashing border and "TRACKED" label.
