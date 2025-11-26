#!/usr/bin/env python3
"""
Firmware Upload Utility
Upload new firmware versions to the Flight Portal OTA server
"""

import requests
import json
import sys
import os
from datetime import datetime

def upload_firmware(server_url, firmware_file, version, changelog, mandatory=False):
    """Upload firmware to the OTA server"""

    # Validate inputs
    if not os.path.exists(firmware_file):
        print(f"❌ Error: Firmware file '{firmware_file}' not found")
        return False

    # Read firmware code
    print(f"📖 Reading firmware from {firmware_file}...")
    with open(firmware_file, 'r') as f:
        firmware_code = f.read()

    # Validate firmware
    if len(firmware_code) < 1000:
        print(f"❌ Error: Firmware file too small ({len(firmware_code)} bytes)")
        return False

    if "Flight Portal" not in firmware_code:
        print(f"⚠️  Warning: Firmware doesn't contain 'Flight Portal' signature")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False

    # Check version in code
    if f'FIRMWARE_VERSION = "{version}"' not in firmware_code:
        print(f"⚠️  Warning: FIRMWARE_VERSION in code doesn't match {version}")
        print("Make sure to update FIRMWARE_VERSION constant in your code!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False

    print(f"📦 Firmware size: {len(firmware_code):,} bytes")
    print(f"🏷️  Version: {version}")
    print(f"📝 Changelog: {changelog}")
    print(f"⚠️  Mandatory: {mandatory}")
    print()

    # Confirm upload
    response = input("Upload to server? (y/N): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled")
        return False

    # Upload to server
    print(f"📤 Uploading to {server_url}...")

    try:
        response = requests.post(
            f"{server_url}/api/firmware/upload",
            json={
                'version': version,
                'changelog': changelog,
                'code': firmware_code,
                'mandatory': mandatory
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {result.get('message')}")
                print()
                print("🎉 Firmware uploaded successfully!")
                print()
                print("Next steps:")
                print("1. Devices will check for updates within 1 hour")
                print("2. Monitor device serial consoles for update messages")
                print(f"3. Verify download URL: {server_url}/api/firmware/download")
                return True
            else:
                print(f"❌ Upload failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Server error: HTTP {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {server_url}")
        print("Make sure the web server is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_versions(server_url):
    """List all firmware versions on the server"""
    try:
        response = requests.get(f"{server_url}/api/firmware/versions", timeout=10)
        if response.status_code == 200:
            manifest = response.json()
            print(f"Current Version: {manifest.get('current_version')}")
            print()
            print("Available Versions:")
            print("-" * 80)
            for version in manifest.get('versions', []):
                print(f"  Version: {version['version']}")
                print(f"  Released: {version['released']}")
                print(f"  Changelog: {version['changelog']}")
                print(f"  Filename: {version['filename']}")
                print(f"  Mandatory: {version['mandatory']}")
                print("-" * 80)
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("=" * 80)
    print("Flight Portal - Firmware Upload Utility")
    print("=" * 80)
    print()

    # Get server URL
    default_server = "http://localhost:3100"
    server_url = input(f"Server URL [{default_server}]: ").strip() or default_server

    # Remove trailing slash
    server_url = server_url.rstrip('/')

    # Check server connectivity
    print(f"🔌 Connecting to {server_url}...")
    try:
        response = requests.get(f"{server_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is online")
        else:
            print(f"⚠️  Server returned HTTP {response.status_code}")
    except:
        print("❌ Cannot connect to server")
        sys.exit(1)

    print()

    # Choose action
    print("What would you like to do?")
    print("1. Upload new firmware")
    print("2. List existing versions")
    print("3. Exit")
    print()

    choice = input("Choice [1-3]: ").strip()
    print()

    if choice == '1':
        # Upload firmware
        firmware_file = input("Firmware file path: ").strip()
        if not firmware_file:
            print("❌ No file specified")
            sys.exit(1)

        version = input("Version (e.g., 3.1.0): ").strip()
        if not version:
            print("❌ Version required")
            sys.exit(1)

        changelog = input("Changelog: ").strip() or "No changelog provided"

        mandatory_input = input("Mandatory update? (y/N): ").strip().lower()
        mandatory = mandatory_input == 'y'

        print()
        success = upload_firmware(server_url, firmware_file, version, changelog, mandatory)
        sys.exit(0 if success else 1)

    elif choice == '2':
        # List versions
        success = list_versions(server_url)
        sys.exit(0 if success else 1)

    elif choice == '3':
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("❌ Cancelled by user")
        sys.exit(1)
