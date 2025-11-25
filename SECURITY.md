# Flight Portal Security Guide

Complete security implementation guide for production deployment.

## 🔐 Security Features

This implementation includes:

- ✅ **API Key Authentication** - Bearer token authentication for all API endpoints
- ✅ **HTTPS/TLS** - Self-signed SSL certificates for encrypted communication
- ✅ **Code Signing** - HMAC-SHA256 signatures for OTA firmware updates
- ✅ **Role-Based Access** - Admin vs Device permission levels
- ✅ **Constant-Time Comparison** - Protection against timing attacks

## 🚀 Quick Start

### 1. Generate Security Keys

```bash
cd web-interface
python generate_keys.py
```

This creates:
- **Admin API Key** - For web interface and administrative tasks
- **Device API Key** - For device authentication
- **Signing Key** - For firmware code signing
- **SSL Certificate** - Self-signed cert for HTTPS (ssl_cert.pem)
- **SSL Private Key** - Private key for HTTPS (ssl_key.pem)
- **.secrets.json** - Secure configuration file (chmod 600)

### 2. Update Device Code

After generating keys, you'll receive output like:

```
API Key (Device): abc123def456...xyz789
Signing Key: 1a2b3c4d5e6f...9x8y7z
```

Update your device code (`code_v3_secure.py`) with these values:

```python
# Security configuration
DEVICE_API_KEY = "your-device-api-key-here"
SIGNING_KEY = "your-signing-key-here"
```

### 3. Start Secure Server

```bash
python app.py
```

You should see:
```
================================================================================
Flight Portal Web Interface - SECURE MODE
================================================================================

✅ Security keys loaded from .secrets.json
✅ HTTPS enabled

Server URL: https://localhost:3100
```

### 4. Test Authentication

**Test without authentication (should fail):**
```bash
curl https://localhost:3100/api/config -k
# Response: {"error": "Missing or invalid authorization header"}
```

**Test with authentication (should succeed):**
```bash
curl https://localhost:3100/api/config \
  -H "Authorization: Bearer YOUR_DEVICE_API_KEY" \
  -k
# Response: {config object}
```

## 📋 Security Configuration

### .secrets.json Format

```json
{
  "admin_api_key": "admin-key-32-chars",
  "device_api_key": "device-key-32-chars",
  "signing_key": "signing-key-64-chars",
  "ssl_enabled": true,
  "ssl_cert": "ssl_cert.pem",
  "ssl_key": "ssl_key.pem",
  "generated_at": "2025-11-25T10:00:00"
}
```

### File Permissions

**Critical:** Ensure `.secrets.json` has restrictive permissions:

```bash
chmod 600 .secrets.json  # Owner read/write only
```

### Gitignore

The `.gitignore` file prevents committing sensitive files:
- `.secrets.json`
- `ssl_cert.pem`
- `ssl_key.pem`
- `config/device_config.json` (may contain WiFi passwords)

**NEVER commit these files to version control!**

## 🔑 API Key Management

### Two-Tier Access Control

**Admin API Key:**
- Full access to all endpoints
- Can create/modify/delete layouts
- Can upload firmware
- Can change all settings

**Device API Key:**
- Read-only config access
- Can fetch layouts and firmware
- Can check for updates
- Cannot modify settings

### Key Rotation

To rotate keys (invalidates all existing devices):

```bash
python generate_keys.py
# Confirm rotation: y
# Update all device code with new DEVICE_API_KEY
# Redeploy to all devices
```

### Usage in Requests

**From Device (CircuitPython):**
```python
headers = {
    "Authorization": f"Bearer {DEVICE_API_KEY}",
    "User-Agent": "FlightPortal/3.0",
    "Accept": "application/json"
}

response = requests.get(CONFIG_URL, headers=headers)
```

**From Admin Tools:**
```bash
# Upload firmware
curl -X POST https://localhost:3100/api/firmware/upload \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d @firmware.json
```

## 🔒 HTTPS/SSL Configuration

### Self-Signed Certificates (Development/Local Network)

Generated automatically by `generate_keys.py`:

**Pros:**
- Free
- Works on local network
- Encrypted communication

**Cons:**
- Browser security warnings
- Not trusted by default
- Manual certificate acceptance required

**To trust self-signed cert:**

**macOS:**
```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain ssl_cert.pem
```

**Windows:**
```
1. Double-click ssl_cert.pem
2. Click "Install Certificate"
3. Select "Local Machine"
4. Place in "Trusted Root Certification Authorities"
```

**Linux:**
```bash
sudo cp ssl_cert.pem /usr/local/share/ca-certificates/flightportal.crt
sudo update-ca-certificates
```

### Production Certificates (Recommended)

For production/internet-facing deployments, use proper CA-signed certificates:

**Option 1: Let's Encrypt (Free)**
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate (requires public domain)
sudo certbot certonly --standalone -d your-domain.com

# Update .secrets.json
{
  "ssl_cert": "/etc/letsencrypt/live/your-domain.com/fullchain.pem",
  "ssl_key": "/etc/letsencrypt/live/your-domain.com/privkey.pem"
}
```

**Option 2: Commercial Certificate**
- Purchase from Namecheap, DigiCert, etc.
- Generate CSR: `openssl req -new -key ssl_key.pem -out request.csr`
- Submit CSR to certificate authority
- Install received certificate

### HTTPS in CircuitPython

CircuitPython's adafruit_requests library supports HTTPS but doesn't verify certificates by default:

```python
# Works with self-signed certificates
response = requests.get("https://server:3100/api/config", headers=headers)
```

For production, consider implementing certificate pinning (advanced).

## 🔐 Code Signing

### How It Works

**Server Side (Signing):**
```python
import hmac
import hashlib

signing_key = "your-64-char-signing-key"
firmware_code = "... (Python code) ..."

signature = hmac.new(
    signing_key.encode(),
    firmware_code.encode(),
    hashlib.sha256
).hexdigest()

# Signature sent in HTTP header: X-Firmware-Signature
```

**Device Side (Verification):**
```python
# Download firmware
response = requests.get(firmware_url, headers=auth_headers)
firmware_code = response.text
received_signature = response.headers.get('X-Firmware-Signature')

# Compute expected signature
expected_signature = hmac.new(
    SIGNING_KEY.encode(),
    firmware_code.encode(),
    hashlib.sha256
).hexdigest()

# Verify (constant-time comparison)
if hmac.compare_digest(received_signature, expected_signature):
    print("✅ Signature valid - installing firmware")
    install_firmware(firmware_code)
else:
    print("❌ Signature invalid - rejecting firmware")
    # Do NOT install
```

### Security Properties

- **Authenticity**: Firmware came from authorized server
- **Integrity**: Firmware wasn't modified in transit
- **Non-repudiation**: Only holder of signing key could create signature

### Key Size

- Uses HMAC-SHA256
- Signing key: 64 hex characters = 256 bits
- Signature output: 64 hex characters = 256 bits
- Cryptographically strong for foreseeable future

## 🛡️ Security Best Practices

### Production Checklist

- [ ] Run `generate_keys.py` to create unique keys
- [ ] Use production-grade CA-signed SSL certificates
- [ ] Change default port from 3100 to 443 (HTTPS standard)
- [ ] Enable firewall rules (allow only necessary ports)
- [ ] Implement rate limiting (prevent brute force attacks)
- [ ] Add logging/monitoring for failed auth attempts
- [ ] Implement automatic key rotation schedule
- [ ] Use environment variables instead of .secrets.json
- [ ] Enable HSTS headers (force HTTPS)
- [ ] Implement CSRF protection for web UI
- [ ] Add device registration/whitelist
- [ ] Monitor for unusual API usage patterns
- [ ] Implement audit logging for all admin actions
- [ ] Set up automated security updates
- [ ] Regular security audits

### Network Security

**Firewall Rules (iptables example):**
```bash
# Allow HTTPS
sudo iptables -A INPUT -p tcp --dport 3100 -j ACCEPT

# Block all other incoming
sudo iptables -A INPUT -j DROP

# Allow established connections
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

**Reverse Proxy (nginx example):**
```nginx
server {
    listen 443 ssl;
    server_name flightportal.local;

    ssl_certificate /path/to/ssl_cert.pem;
    ssl_certificate_key /path/to/ssl_key.pem;

    # Strong SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20;

    location / {
        proxy_pass http://localhost:3100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Application Security

**Rate Limiting:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/config')
@limiter.limit("10 per minute")
@require_auth('device')
def get_config():
    ...
```

**Logging:**
```python
import logging

logging.basicConfig(
    filename='security.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log all authentication attempts
@require_auth('device')
def protected_endpoint():
    logging.info(f"API access from {request.remote_addr}")
    ...
```

## 🚨 Incident Response

### If API Keys Are Compromised

1. **Immediately rotate keys:**
   ```bash
   python generate_keys.py  # Generate new keys
   ```

2. **Update all devices** with new DEVICE_API_KEY

3. **Review logs** for unauthorized access

4. **Check firmware** for modifications

5. **Consider blocking** suspect IP addresses

### If Signing Key Is Compromised

**CRITICAL** - Attacker can push malicious firmware to all devices!

1. **Immediately rotate signing key**
2. **Audit all recent firmware uploads**
3. **Review device logs for suspicious updates**
4. **Consider pushing emergency firmware rollback**
5. **Notify all device owners**

### If SSL Private Key Is Compromised

1. **Generate new certificate and key**
2. **Update server configuration**
3. **Restart web server**
4. **Monitor for man-in-the-middle attacks**

## 📊 Security Monitoring

### Metrics to Track

- Failed authentication attempts per IP
- Firmware download frequency per device
- Unusual API access patterns
- Configuration changes
- Certificate expiration dates

### Alerting

Set up alerts for:
- More than 10 failed auth attempts in 1 hour
- Firmware uploads outside business hours
- Configuration changes from unknown IPs
- SSL certificate expiring in < 30 days

## 📖 Additional Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Flask Security**: https://flask.palletsprojects.com/en/2.3.x/security/
- **Let's Encrypt**: https://letsencrypt.org/
- **NIST Cryptographic Standards**: https://csrc.nist.gov/

## 🆘 Support

For security concerns or questions:
1. Review this documentation
2. Check OTA-UPDATES.md for deployment security
3. Review INSTALLATION.md for setup procedures

**Never share your .secrets.json file or API keys publicly!**
