#!/bin/bash

# Flight Portal Hostname Setup Script (Linux/Mac)
# Adds 'flightportal' to hosts file for easy access

HOSTNAME="flightportal"
IP="127.0.0.1"
HOSTS_FILE="/etc/hosts"
ENTRY="$IP    $HOSTNAME"

echo "======================================"
echo "Flight Portal Hostname Setup"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires root privileges."
    echo "Please run with sudo:"
    echo "  sudo ./setup-hostname.sh"
    exit 1
fi

# Check if entry already exists
if grep -q "$HOSTNAME" "$HOSTS_FILE"; then
    echo "Entry for '$HOSTNAME' already exists in $HOSTS_FILE"
    echo "Current entry:"
    grep "$HOSTNAME" "$HOSTS_FILE"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old entry
        sed -i.bak "/$HOSTNAME/d" "$HOSTS_FILE"
        echo "$ENTRY" >> "$HOSTS_FILE"
        echo "✓ Updated entry in $HOSTS_FILE"
    else
        echo "No changes made."
        exit 0
    fi
else
    # Add new entry
    echo "" >> "$HOSTS_FILE"
    echo "# Flight Portal Web Interface" >> "$HOSTS_FILE"
    echo "$ENTRY" >> "$HOSTS_FILE"
    echo "✓ Added entry to $HOSTS_FILE"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "You can now access the web interface at:"
echo "  http://flightportal:3100"
echo ""
echo "Or use the direct URL:"
echo "  http://localhost:3100"
echo ""
