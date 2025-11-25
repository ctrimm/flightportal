# Over-The-Air (OTA) Firmware Updates

Complete guide for implementing and managing OTA firmware updates for your Flight Portal devices.

## 🚨 Important: Licensing for Commercial Use

### Current License Issue

The project currently has a **CC BY-NC-SA 4.0** license that **PROHIBITS commercial use and resale**. If you want to sell devices with OTA updates, you need to change the license.

### Recommended Licenses for Commercial Products

Choose one of these options:

#### Option 1: MIT License (Most Permissive)
```
✅ Allows commercial use
✅ Allows selling products
✅ Simple and widely understood
✅ Minimal restrictions
```

#### Option 2: Apache 2.0 License
```
✅ Allows commercial use
✅ Includes patent protection
✅ Requires attribution
✅ Industry standard
```

#### Option 3: Dual License
```
✅ GPL/AGPL for community (open source)
✅ Commercial license for your products
✅ You control both versions
✅ Can monetize while staying open
```

#### Option 4: Keep Code Proprietary
```
✅ Don't publish commercial version
✅ Only share open-source base version
✅ Full control over updates
✅ No licensing issues
```

### To Change License

1. **Replace LICENSE file** with your chosen license
2. **Update README.md** to reflect new license
3. **Add copyright headers** to your code files
4. **Commit changes** before selling

---

## 📋 Table of Contents

1. [How OTA Updates Work](#how-ota-updates-work)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Publishing Updates](#publishing-updates)
5. [Security Considerations](#security-considerations)
6. [Commercial Deployment](#commercial-deployment)
7. [Troubleshooting](#troubleshooting)

---

## How OTA Updates Work

### Update Flow

```
1. Device boots with FIRMWARE_VERSION = "3.0.0"
2. Device connects to WiFi
3. Device fetches config from web server (every 5 min)
4. Device checks for firmware updates (every 1 hour)
5. Server compares versions: 3.0.0 vs 3.1.0
6. If update available:
   - Display notification on LED matrix
   - Download new firmware code
   - Backup current code.py to code.backup
   - Write new code to code.py
   - Restart device
7. Device boots with new version 3.1.0
```

### Safety Features

- **Automatic Backup**: Current firmware backed up before update
- **Sanity Checking**: Validates downloaded code before installing
- **Rollback Capability**: Can restore from backup if update fails
- **Watchdog Timer**: Device auto-reboots if update hangs
- **Version Tracking**: Prevents downgrade attacks

---

## Architecture

### Components

**Device Side (`code_v3_ota.py`):**
- `FIRMWARE_VERSION` constant
- `check_for_firmware_update()` - Queries server for new version
- `download_and_install_update()` - Downloads and installs firmware
- `handle_ota_update()` - Main OTA orchestration logic

**Server Side (`web-interface/app.py`):**
- `/api/firmware/check` - Check if update available
- `/api/firmware/download` - Download firmware file
- `/api/firmware/upload` - Upload new firmware (admin)
- `/api/firmware/versions` - List all versions
- `firmware/` directory - Stores firmware files
- `firmware/manifest.json` - Version metadata

### Configuration

Add to `device_config.json`:
```json
{
  "ota": {
    "enabled": true,
    "auto_update": false,
    "check_interval": 3600
  }
}
```

**Settings:**
- `enabled` - Enable/disable OTA (default: true)
- `auto_update` - Install updates automatically (default: false)
- `check_interval` - Seconds between update checks (default: 3600 = 1 hour)

---

## Setup Instructions

### 1. Prepare Your Environment

```bash
cd flightportal
```

### 2. Copy OTA-Enabled Firmware

The OTA firmware is in `code_v3_ota.py`. This includes:
- Firmware version tracking
- Update checking logic
- Safe installation procedure
- Automatic backup/restore

### 3. Configure Server

The web interface already has OTA endpoints enabled. Just start the server:

```bash
cd web-interface
python app.py
```

The server will create:
- `firmware/` directory (stores firmware files)
- `firmware/manifest.json` (version metadata)

### 4. Deploy Initial Firmware to Device

1. Edit `code_v3_ota.py` line 36:
   ```python
   CONFIG_SERVER = "192.168.1.100:3100"  # Your server IP
   ```

2. Copy to MatrixPortal as `code.py`:
   ```bash
   cp code_v3_ota.py /Volumes/CIRCUITPY/code.py
   ```

3. Device will boot and register as version `3.0.0`

### 5. Verify OTA System

Watch device serial console:
```
Firmware Version: 3.0.0
Checking for firmware updates (current version: 3.0.0)...
Firmware is up to date
```

---

## Publishing Updates

### Method 1: Via API (Recommended)

Use the REST API to publish updates:

```bash
curl -X POST http://localhost:3100/api/firmware/upload \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "version": "3.1.0",
  "changelog": "Added new feature X, fixed bug Y",
  "code": "$(cat code_v3_ota_updated.py | sed 's/"/\\"/g')",
  "mandatory": false
}
EOF
```

**Or use Python:**
```python
import requests

with open('code_v3_ota_updated.py', 'r') as f:
    firmware_code = f.read()

response = requests.post('http://localhost:3100/api/firmware/upload', json={
    'version': '3.1.0',
    'changelog': 'Bug fixes and improvements',
    'code': firmware_code,
    'mandatory': False
})

print(response.json())
```

### Method 2: Manual File Copy

1. Copy your firmware file:
   ```bash
   cp code_v3_ota_v3.1.0.py web-interface/firmware/code_3_1_0.py
   ```

2. Update `web-interface/firmware/manifest.json`:
   ```json
   {
     "current_version": "3.1.0",
     "versions": [
       {
         "version": "3.1.0",
         "released": "2025-11-25T10:00:00",
         "changelog": "Bug fixes and improvements",
         "filename": "code_3_1_0.py",
         "mandatory": false
       },
       {
         "version": "3.0.0",
         "released": "2025-11-24T12:00:00",
         "changelog": "Initial OTA support",
         "filename": "code_v3_ota.py",
         "mandatory": false
       }
     ]
   }
   ```

### Version Numbering

Use **Semantic Versioning** (semver):
- **Major**: Breaking changes (3.0.0 → 4.0.0)
- **Minor**: New features, backward compatible (3.0.0 → 3.1.0)
- **Patch**: Bug fixes (3.0.0 → 3.0.1)

**Update FIRMWARE_VERSION in your code:**
```python
FIRMWARE_VERSION = "3.1.0"  # Must match manifest version
```

---

## Security Considerations

### ⚠️ Security Risks

1. **No Authentication**: Any device can request firmware
2. **No Encryption**: Firmware sent over HTTP (not HTTPS)
3. **No Code Signing**: Can't verify firmware authenticity
4. **Network Attacks**: Man-in-the-middle possible

### 🔒 Security Improvements (Recommended for Production)

#### 1. Add Authentication

Require API key for firmware access:

```python
# In device code
FIRMWARE_API_KEY = "your-secret-key-12345"

# Add to request headers
headers = {
    "Authorization": f"Bearer {FIRMWARE_API_KEY}",
    ...
}

# In server code
@app.route('/api/firmware/download')
def download_firmware():
    api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
    if api_key != os.environ.get('FIRMWARE_API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401
    # ... rest of code
```

#### 2. Add HTTPS

Use SSL/TLS for encrypted communication:

```python
# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365

# Run Flask with HTTPS
app.run(host='0.0.0.0', port=3100,
        ssl_context=('cert.pem', 'key.pem'))
```

#### 3. Add Code Signing

Sign firmware with a private key:

```python
import hashlib
import hmac

# On server: Sign firmware
SECRET_KEY = "your-signing-key"
firmware_code = "..."
signature = hmac.new(
    SECRET_KEY.encode(),
    firmware_code.encode(),
    hashlib.sha256
).hexdigest()

# On device: Verify signature
received_signature = "..."
computed_signature = hmac.new(
    SECRET_KEY.encode(),
    firmware_code.encode(),
    hashlib.sha256
).hexdigest()

if received_signature != computed_signature:
    print("SECURITY: Firmware signature invalid!")
    return False
```

#### 4. Device Registration

Track which devices are authorized:

```python
# Each device has unique ID
DEVICE_ID = "FP-00001"

# Server maintains whitelist
AUTHORIZED_DEVICES = ["FP-00001", "FP-00002", ...]

# Check before serving firmware
if device_id not in AUTHORIZED_DEVICES:
    return jsonify({"error": "Device not authorized"}), 403
```

---

## Commercial Deployment

### Cloud Hosting Options

For selling devices commercially, host the web interface on a cloud server:

#### Option 1: Heroku (Easiest)
```bash
# Install Heroku CLI
# Create Procfile:
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create flightportal-updates
git push heroku main
```

#### Option 2: AWS EC2
- Launch t2.micro instance (free tier)
- Install Python and dependencies
- Run behind nginx reverse proxy
- Use Let's Encrypt for HTTPS

#### Option 3: DigitalOcean
- $5/month droplet
- One-click Flask app deployment
- Built-in firewall and monitoring

#### Option 4: Cloudflare Workers
- Serverless edge computing
- Free tier: 100,000 requests/day
- Global CDN distribution

### Update Strategy for Production

**Staged Rollout:**
```
1. Test update on internal devices (alpha)
2. Release to 10% of devices (beta)
3. Monitor for 24 hours
4. If stable, release to 50%
5. Monitor for 24 hours
6. Release to 100%
```

**Canary Deployment:**
- Maintain multiple firmware versions
- Assign devices to "stable" or "beta" channels
- Beta users get early access
- Stable users get tested versions

**Emergency Rollback:**
- Keep previous version available
- Implement "rollback" endpoint
- Devices can request older version if issues

### Analytics and Monitoring

Track update status:

```python
# Log update events
@app.route('/api/firmware/download')
def download_firmware():
    device_id = request.headers.get('X-Device-ID')
    log_download(device_id, version)
    # ... serve firmware

# Track success/failure
@app.route('/api/firmware/status', methods=['POST'])
def report_update_status():
    data = request.json
    # Log: device_id, version, success, error_message
    save_update_log(data)
```

### Device Fleet Management

For managing multiple devices:

```python
# Database schema
devices = {
    "FP-00001": {
        "current_version": "3.0.0",
        "last_seen": "2025-11-25T10:00:00",
        "update_channel": "stable",
        "location": "Customer A"
    }
}

# Different channels
channels = {
    "stable": "3.0.0",
    "beta": "3.1.0-beta",
    "dev": "3.2.0-dev"
}
```

---

## Troubleshooting

### Update Fails to Download

**Symptoms:**
```
Error checking for firmware update: [Errno -2]
```

**Solutions:**
1. Verify CONFIG_SERVER IP address
2. Check firewall allows port 3100
3. Ensure web server is running
4. Test URL in browser: `http://YOUR_IP:3100/api/firmware/check?version=3.0.0`

### Update Downloads But Won't Install

**Symptoms:**
```
Downloaded code failed sanity check
```

**Solutions:**
1. Verify firmware file is valid Python code
2. Check file contains "Flight Portal" string
3. Ensure file is not corrupted
4. Check file size (should be > 1000 bytes)

### Device Bricks After Update

**Symptoms:**
- Device won't boot
- No serial output
- Black screen

**Recovery:**
1. Connect device to computer
2. Enter bootloader mode (double-click reset)
3. Restore from `code.backup`:
   ```bash
   cp /Volumes/CIRCUITPY/code.backup /Volumes/CIRCUITPY/code.py
   ```
4. If backup missing, copy original `code_v3_ota.py`

### Updates Not Checking

**Symptoms:**
```
(No firmware check messages in serial console)
```

**Solutions:**
1. Check `ota.enabled` is `true` in config
2. Verify `check_interval` (default 3600 seconds)
3. Force check by restarting device
4. Check system time is correct

### Version Comparison Issues

**Symptoms:**
- Device reports update available when none exists
- Device never updates despite new version

**Solution:**
Ensure version format is correct:
- ✅ Good: `"3.1.0"` (semver)
- ❌ Bad: `"v3.1"`, `"3.1.0-beta"`, `"3.1"`

---

## API Reference

### Check for Updates

```http
GET /api/firmware/check?version=3.0.0

Response:
{
  "update_available": true,
  "version": "3.1.0",
  "changelog": "Bug fixes",
  "mandatory": false,
  "download_url": "http://localhost:3100/api/firmware/download"
}
```

### Download Firmware

```http
GET /api/firmware/download

Response: (plain text Python code)
"""
Flight Portal v3.1.0
...
"""
```

### Upload New Version

```http
POST /api/firmware/upload
Content-Type: application/json

{
  "version": "3.1.0",
  "changelog": "New features",
  "code": "...(full Python code)...",
  "mandatory": false
}

Response:
{
  "success": true,
  "message": "Firmware version 3.1.0 uploaded successfully"
}
```

### List Versions

```http
GET /api/firmware/versions

Response:
{
  "current_version": "3.1.0",
  "versions": [
    {
      "version": "3.1.0",
      "released": "2025-11-25T10:00:00",
      "changelog": "...",
      "filename": "code_3_1_0.py",
      "mandatory": false
    }
  ]
}
```

---

## Best Practices

### Development Workflow

1. **Version Numbering**
   - Increment version in code
   - Update manifest version
   - Match exactly (case-sensitive)

2. **Testing**
   - Test on dev device first
   - Verify update downloads
   - Verify device boots after update
   - Check rollback works

3. **Changelog**
   - Be specific about changes
   - List bug fixes
   - Mention breaking changes
   - Include upgrade instructions

4. **Backup Strategy**
   - Keep all firmware versions
   - Never delete old versions
   - Backup manifest regularly

### Production Checklist

- [ ] License allows commercial use
- [ ] HTTPS enabled
- [ ] Authentication implemented
- [ ] Code signing active
- [ ] Device registration required
- [ ] Update logging enabled
- [ ] Monitoring/alerts configured
- [ ] Emergency rollback tested
- [ ] Customer support trained

---

## Future Enhancements

### Planned Features

- **Delta Updates**: Only download changed code (reduce bandwidth)
- **Compressed Updates**: Gzip compression for faster downloads
- **Scheduled Updates**: Install updates at specific times
- **User Confirmation**: Physical button to approve updates
- **Update Channels**: Stable, beta, dev tracks
- **Batch Updates**: Update multiple devices simultaneously
- **Update Notifications**: Email/SMS when update published
- **Version Pinning**: Lock devices to specific version
- **A/B Partitions**: Dual boot for safer updates

---

**For questions or support, refer to the main project documentation.**
