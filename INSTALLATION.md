# Flight Portal Installation Guide

Complete installation guide for the restructured Flight Portal system with web-based configuration.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Hardware Setup](#hardware-setup)
3. [Web Interface Setup](#web-interface-setup)
4. [Device Code Setup](#device-code-setup)
5. [Network Configuration](#network-configuration)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

**Hardware:**
- Adafruit MatrixPortal M4
- 64x32 RGB LED Matrix Panel (P4)
- USB power supply (5V, 2A minimum)
- USB-C cable for MatrixPortal

**Software:**
- Python 3.8 or higher (for web interface)
- CircuitPython 7.x or higher (for device)
- pip (Python package manager)

## Web Interface Setup

### 1. Set Up Python Virtual Environment

```bash
cd web-interface
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Start the Web Server

```bash
python app.py
```

### 3. Access the Interface

Open browser: **http://localhost:3100**

### 4. Configure Settings

1. **WiFi Tab** - Enter your network credentials
2. **Location Tab** - Set geographic bounds for flight search
3. **Layouts Tab** - Select display layout
4. **Display Settings** - Adjust animation speeds

## Device Code Setup

### 1. Find Your Computer's IP Address

```bash
# Mac/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

Look for something like `192.168.1.100`

### 2. Update CONFIG_SERVER in code_v2.py

Edit line 36:
```python
CONFIG_SERVER = "192.168.1.100:3100"  # Use your IP
```

### 3. Copy to Device

Copy `code_v2.py` to your MatrixPortal as `code.py`

## Testing

Monitor device serial console at 115200 baud to verify:
- WiFi connection
- Config fetch from server
- Flight detection

## Troubleshooting

**Device can't fetch config:**
- Verify CONFIG_SERVER IP address
- Check firewall allows port 3100
- Ensure device and computer on same network

**No flights detected:**
- Verify geographic bounds are correct
- Check area has air traffic

For detailed instructions, see full documentation.
