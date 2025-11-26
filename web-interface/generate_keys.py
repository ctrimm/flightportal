#!/usr/bin/env python3
"""
Security Key Generation Utility
Generate API keys, signing keys, and SSL certificates for Flight Portal
"""

import secrets
import os
import subprocess
import json
from datetime import datetime

def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_urlsafe(length)

def generate_signing_key(length=64):
    """Generate a secure signing key for OTA updates"""
    return secrets.token_hex(length)

def generate_ssl_certificate():
    """Generate self-signed SSL certificate"""
    print("🔐 Generating SSL certificate...")

    # Check if openssl is available
    try:
        subprocess.run(['openssl', 'version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ OpenSSL not found. Please install OpenSSL:")
        print("   Mac: brew install openssl")
        print("   Ubuntu/Debian: sudo apt-get install openssl")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        return False

    # Generate private key and certificate
    try:
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa',
            '-out', 'ssl_key.pem',
            '2048'
        ], check=True, capture_output=True)

        # Generate certificate signing request and self-signed certificate
        subprocess.run([
            'openssl', 'req',
            '-new', '-x509',
            '-key', 'ssl_key.pem',
            '-out', 'ssl_cert.pem',
            '-days', '365',
            '-subj', '/C=US/ST=State/L=City/O=FlightPortal/CN=localhost'
        ], check=True, capture_output=True)

        print("✅ SSL certificate generated successfully")
        print("   Certificate: ssl_cert.pem")
        print("   Private Key: ssl_key.pem")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating SSL certificate: {e}")
        return False

def save_config(config, filename='.secrets.json'):
    """Save security configuration to file"""
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)

    # Set restrictive permissions (Unix-like systems)
    try:
        os.chmod(filename, 0o600)
    except:
        pass

    print(f"✅ Security configuration saved to {filename}")
    print("⚠️  Keep this file secure and DO NOT commit it to git!")

def load_config(filename='.secrets.json'):
    """Load security configuration from file"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None

def main():
    print("=" * 80)
    print("Flight Portal Security Key Generation")
    print("=" * 80)
    print()

    # Check if config already exists
    existing_config = load_config()

    if existing_config:
        print("⚠️  Existing security configuration found!")
        print()
        response = input("Generate new keys? This will invalidate existing devices! (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return
        print()

    print("Generating security keys...")
    print()

    # Generate keys
    api_key = generate_api_key()
    device_api_key = generate_api_key()
    signing_key = generate_signing_key()

    print(f"✅ API Key (Admin): {api_key[:16]}...{api_key[-8:]}")
    print(f"✅ API Key (Device): {device_api_key[:16]}...{device_api_key[-8:]}")
    print(f"✅ Signing Key: {signing_key[:16]}...{signing_key[-8:]}")
    print()

    # Generate SSL certificate
    ssl_generated = generate_ssl_certificate()
    print()

    # Save configuration
    config = {
        "admin_api_key": api_key,
        "device_api_key": device_api_key,
        "signing_key": signing_key,
        "ssl_enabled": ssl_generated,
        "ssl_cert": "ssl_cert.pem" if ssl_generated else None,
        "ssl_key": "ssl_key.pem" if ssl_generated else None,
        "generated_at": datetime.now().isoformat()
    }

    save_config(config)
    print()

    # Display instructions
    print("=" * 80)
    print("Setup Instructions")
    print("=" * 80)
    print()
    print("1. Update your device code (code_v3_ota.py):")
    print(f"   DEVICE_API_KEY = \"{device_api_key}\"")
    print(f"   SIGNING_KEY = \"{signing_key}\"")
    print()
    print("2. Start the web server:")
    print("   python app.py")
    print()
    print("3. Access the web interface:")
    if ssl_generated:
        print("   https://localhost:3100")
        print("   (You'll see a security warning - this is normal for self-signed certs)")
    else:
        print("   http://localhost:3100")
    print()
    print("4. API requests must include authentication:")
    print("   curl -H 'Authorization: Bearer <api_key>' https://localhost:3100/api/config")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Keep .secrets.json file secure")
    print("   - Add .secrets.json to .gitignore")
    print("   - Update device code with DEVICE_API_KEY")
    print("   - For production, use proper CA-signed certificates")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("❌ Cancelled by user")
