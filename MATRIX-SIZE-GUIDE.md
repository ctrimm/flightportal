# Matrix Size Compatibility Guide

This guide covers using Flight Portal with different RGB LED matrix sizes on the Adafruit MatrixPortal M4 (PID 4745).

## Hardware Specifications

### Adafruit MatrixPortal M4 (PID 4745)

**Processor:** ATSAMD51J19 (120MHz Cortex M4)
- **RAM:** 192 KB SRAM
- **Flash:** 512 KB
- **Interface:** HUB75 RGB Matrix

**Supported Matrix Sizes:**
- ✅ 64x32 (default, fully supported)
- ✅ 64x64 (supported with chaining or single panel)
- ⚠️ 128x32 (supported but requires special configuration)
- ⚠️ 128x64 (technically possible but challenging due to memory)

---

## Matrix Configuration

### 64x32 (Default - Recommended for Most Users)

**Memory Usage:** ~6 KB framebuffer
**Status:** ✅ Fully supported, best performance

**Hardware Setup:**
- Single 64x32 HUB75 panel
- Connect directly to MatrixPortal
- Standard 5V 4A power supply

**Code:**
```python
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
```

**Best For:**
- Single device deployments
- Battery/portable applications
- Memory-constrained scenarios
- Maximum update rate

---

### 64x64 (Your Configuration)

**Memory Usage:** ~12 KB framebuffer
**Status:** ✅ Supported with considerations

**Hardware Setup Options:**

#### Option A: Single 64x64 Panel (Recommended)
```
[MatrixPortal M4] ──► [64x64 HUB75 Panel]
```
- Cleanest solution
- Single panel purchase
- Standard wiring
- Power: 5V 6A recommended

#### Option B: Two 64x32 Panels Chained
```
[MatrixPortal M4] ──► [64x32 Panel #1] ──► [64x32 Panel #2]
```
- Stack panels vertically
- Use ribbon cable between panels
- Power: 5V 6-8A recommended (both panels)
- May need to configure chaining in software

**Code:**
```python
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
```

**Advantages:**
- 2x display area vs 64x32
- Better visibility from distance
- More room for multiple aircraft info
- Cleaner watchlist alert layout

**Limitations:**
- Higher memory usage (leaves ~40KB free)
- Slower refresh rate vs 64x32
- Requires more power
- May need to disable some features if memory tight

**Recommended Settings for 64x64:**
```python
bit_depth=4  # Lower bit depth = less memory
WATCHLIST_ENABLED = True  # Should work fine
USE_HTTPS = True  # May need to disable if low memory
```

---

### 128x32

**Memory Usage:** ~12 KB framebuffer
**Status:** ⚠️ Supported but uncommon

**Hardware Setup:**
- Two 64x32 panels side-by-side
- Or single 128x32 panel (rare)
- Power: 5V 6-8A

**Code:**
```python
MATRIX_WIDTH = 128
MATRIX_HEIGHT = 32
```

**Best For:**
- Wide format displays
- Long-format installations
- Scrolling text displays

---

### 128x64 (Largest Supported)

**Memory Usage:** ~24 KB framebuffer
**Status:** ⚠️ Challenging, not recommended without optimization

**Hardware Setup:**
- Four 64x32 panels (2x2 grid)
- Or two 128x32 panels (stacked)
- Or two 64x64 panels (side-by-side)
- Power: 5V 12-15A (multiple power supplies recommended)

**Code:**
```python
MATRIX_WIDTH = 128
MATRIX_HEIGHT = 64
```

**Critical Limitations:**
- **High memory usage** (~24KB framebuffer alone)
- **MUST disable features:**
  - Set `bit_depth=2` (lower color depth)
  - Set `USE_HTTPS = False` (use HTTP only)
  - Consider disabling watchlist or reducing features
  - Disable debug logging

**Memory Optimization Required:**
```python
# Minimal configuration for 128x64
MATRIX_WIDTH = 128
MATRIX_HEIGHT = 64
bit_depth = 2  # Only 4 colors per pixel
USE_HTTPS = False  # Disable HTTPS to save memory
WATCHLIST_ENABLED = False  # May need to disable
```

**Test Before Buying Hardware:**
The 192KB RAM gets tight. You may encounter:
- `MemoryError` exceptions
- Random crashes
- Inability to load all libraries

---

## Memory Management

### Checking Available Memory

Add this to your code to monitor memory:
```python
import gc

gc.collect()
free_mem = gc.mem_free()
print(f"Free memory: {free_mem} bytes ({free_mem/1024:.1f} KB)")

if free_mem < 50000:  # Less than 50KB
    print("⚠️ WARNING: Low memory!")
```

### Memory Budget (Approximate)

| Component | Memory Usage |
|-----------|-------------|
| CircuitPython Runtime | ~30-40 KB |
| Network Stack | ~20-30 KB |
| HTTPS/TLS | ~25-35 KB |
| Crypto (HMAC) | ~5-10 KB |
| 64x32 Framebuffer | ~6 KB |
| 64x64 Framebuffer | ~12 KB |
| 128x64 Framebuffer | ~24 KB |
| Code + Variables | ~20-30 KB |
| **Total (64x32)** | **~100-125 KB** ✅ Safe |
| **Total (64x64)** | **~110-135 KB** ✅ OK |
| **Total (128x64)** | **~130-165 KB** ⚠️ Tight |

**Safe Zone:** >50KB free after boot
**Warning Zone:** 30-50KB free
**Danger Zone:** <30KB free (crashes likely)

---

## Power Requirements

### Power Supply Sizing

**Formula:** `Amps = (Width × Height ÷ 500) × 0.8`

| Matrix Size | Max Power | Recommended PSU |
|-------------|-----------|----------------|
| 64x32 | ~3A | 5V 4A |
| 64x64 | ~5A | 5V 6-8A |
| 128x32 | ~5A | 5V 6-8A |
| 128x64 | ~10A | 5V 12-15A (or 2x PSUs) |

**Important:**
- Always use regulated 5V supply
- MatrixPortal powered separately via USB-C
- Connect matrix power to screw terminals on MatrixPortal
- For 128x64, use multiple power injection points

---

## Code Migration Guide

### From v4 (64x32 only) → v4.1 (Multi-size)

1. **Update firmware file:**
   ```bash
   # Use new file
   cp code_v4_1_multisize.py code.py
   ```

2. **Configure matrix size:**
   ```python
   # At top of code.py
   MATRIX_WIDTH = 64   # Your width
   MATRIX_HEIGHT = 64  # Your height
   ```

3. **Test memory on boot:**
   - Watch serial console
   - Check "Free memory" line
   - Should show >50KB free

4. **Optimize if needed:**
   - Lower `bit_depth` (4 → 2)
   - Disable HTTPS if tight
   - Reduce watchlist size

### Key Changes in v4.1

1. **Adaptive Border:**
   - Scales thickness with display size
   - `create_alert_border()` uses `MATRIX_WIDTH`/`MATRIX_HEIGHT`

2. **Adaptive Text Positioning:**
   - Y positions scale with height
   - Text scale increases for larger displays

3. **Memory Monitoring:**
   - Boot-time memory check
   - Warnings if low memory detected

4. **Flexible Layout:**
   - Max flights calculated from height
   - Text lengths adapt to width

---

## Hardware Wiring

### Single Panel (64x32 or 64x64)

```
[5V PSU] ───┬──► [MatrixPortal Power In]
            └──► [LED Matrix Power In]

[MatrixPortal HUB75 Out] ──► [LED Matrix HUB75 In]

[USB-C] ──► [MatrixPortal] (for programming/power)
```

### Chained Panels (64x64 from two 64x32)

```
[5V PSU 6A+] ───┬──► [MatrixPortal Power In]
                ├──► [Panel #1 Power In]
                └──► [Panel #2 Power In]

[MatrixPortal HUB75 Out] ──► [Panel #1 HUB75 In]
[Panel #1 HUB75 Out] ──► [Panel #2 HUB75 In]
```

**Chaining Configuration:**
In your `secrets.py` or `code.py`:
```python
# For vertical chaining (64x64 from two 64x32)
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
# MatrixPortal should auto-detect chaining
```

### Large Displays (128x64)

```
[PSU #1 5V 8A] ───┬──► [MatrixPortal]
                  ├──► [Top-Left Panel]
                  └──► [Top-Right Panel]

[PSU #2 5V 8A] ───┬──► [Bottom-Left Panel]
                  └──► [Bottom-Right Panel]

Panels chained: TL → TR → BL → BR
```

---

## Troubleshooting

### "MemoryError" on Boot

**Causes:**
- Display too large for available RAM
- Too many libraries imported
- HTTPS + large display = no memory

**Solutions:**
1. Lower bit depth: `bit_depth=2`
2. Disable HTTPS: `USE_HTTPS = False`
3. Disable watchlist: `WATCHLIST_ENABLED = False`
4. Remove unused imports
5. Use 64x32 instead

### Display Shows Garbage/Corruption

**Causes:**
- Insufficient power
- Bad wiring
- Memory corruption

**Solutions:**
1. Check power supply amperage
2. Add capacitor (1000µF 6.3V) to power input
3. Shorten ribbon cables
4. Check for loose connections

### Watchlist Alerts Don't Show

**Causes:**
- Border creation exceeds memory with large display
- Text positioning off-screen

**Solutions:**
1. Check `MATRIX_WIDTH` and `MATRIX_HEIGHT` are correct
2. Verify adaptive layout code
3. Check serial output for errors
4. Test with smaller display first

### Display Flickers/Slow Refresh

**Causes:**
- Large framebuffer + complex graphics
- CPU can't keep up with refresh rate
- Network operations blocking display

**Solutions:**
1. Lower bit depth
2. Simplify alert border (remove flashing)
3. Increase sleep time between updates
4. Use async operations (advanced)

---

## Recommended Configuration by Use Case

### Home Display (Single User)
- **Size:** 64x32
- **Why:** Best balance of cost, power, performance
- **Memory:** Plenty of headroom for all features

### Flight School Lobby
- **Size:** 64x64 or 128x32
- **Why:** More visible from distance, more aircraft on screen
- **Memory:** Disable HTTPS if needed, use HTTP locally

### Airport/FBO
- **Size:** 128x64
- **Why:** Maximum visibility, professional appearance
- **Memory:** Minimal config, focus on reliability

### Portable/Battery Powered
- **Size:** 64x32
- **Why:** Lowest power consumption
- **Battery:** 5V USB power bank (10,000mAh = ~6 hours)

---

## Testing Checklist

Before purchasing hardware:

- [ ] Confirm MatrixPortal M4 (PID 4745)
- [ ] Verify matrix panel pitch (P4 recommended, P5 acceptable)
- [ ] Calculate power requirements
- [ ] Check PSU amperage rating
- [ ] Plan mounting/enclosure
- [ ] Consider viewing distance vs. matrix size
- [ ] Test code with simulator if possible

After hardware arrives:

- [ ] Test single panel first
- [ ] Measure power draw with multimeter
- [ ] Check boot memory with serial console
- [ ] Verify all pixels work (dead pixel check)
- [ ] Test watchlist alert with full border
- [ ] Run for 24 hours to check stability
- [ ] Monitor for memory leaks

---

## Upgrade Path

### Starting Small → Growing Large

**Phase 1:** Start with 64x32
- Learn the system
- Test code stability
- Validate use case

**Phase 2:** Upgrade to 64x64
- Buy second 64x32 panel (if using chaining)
- Or single 64x64 panel
- Update code: `MATRIX_HEIGHT = 64`
- Test memory usage

**Phase 3:** Consider 128x64 (if needed)
- Only if truly needed for visibility
- Requires significant optimization
- Consider external controller (Raspberry Pi) instead

---

## Alternative: Use Raspberry Pi for Large Displays

If you need 128x64 or larger:

**Consider:** Raspberry Pi + rpi-rgb-led-matrix library
- Much more RAM (1GB+)
- Python 3 instead of CircuitPython
- Can drive 128x64 easily
- More expensive ($35+ vs $25 MatrixPortal)

**Pros:**
- No memory constraints
- Faster refresh
- More processing power

**Cons:**
- More complex setup
- Higher power consumption
- No built-in WiFi setup (Pi Zero W: yes, Pi 4: yes)
- Requires Linux knowledge

For 64x32 or 64x64: **MatrixPortal is perfect** ✅
For 128x64+: **Consider Raspberry Pi** 🤔

---

## Summary

### ✅ Best Configuration for Your 64x64 Display

```python
# code.py configuration
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64
bit_depth = 4  # Good color depth
USE_HTTPS = True  # Secure communication
WATCHLIST_ENABLED = True  # Full features
```

**Hardware:**
- Adafruit MatrixPortal M4 (PID 4745)
- Single 64x64 HUB75 RGB LED Matrix (P4 pitch)
- 5V 6-8A power supply
- USB-C cable for programming

**Memory:** Should have ~40-50KB free (safe)
**Performance:** Smooth refresh, all features working
**Power:** ~5A average, 7A peak

**You're good to go!** The code in `code_v4_1_multisize.py` is fully compatible with your 64x64 setup. Just set the matrix size constants and deploy.

---

## Future: 128x64 Support

If you expand to 128x64 in the future:

1. Test memory first with `code_v4_1_multisize.py`
2. Set `MATRIX_WIDTH = 128` and `MATRIX_HEIGHT = 64`
3. Monitor boot memory
4. Disable features if needed:
   - `bit_depth = 2`
   - `USE_HTTPS = False`
   - Consider simplifying watchlist alerts

**Or migrate to Raspberry Pi** for ultimate flexibility.

---

**Questions?** Check the troubleshooting section or test with your actual hardware!
