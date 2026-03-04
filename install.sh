#!/bin/bash
# Offline installer — run this from the USB stick on any target machine.
# No internet connection required.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "deps" ]; then
    echo "ERROR: deps/ folder not found. Run build_usb.sh on the development machine first."
    exit 1
fi

if ! dpkg -l python3-venv &>/dev/null; then
    echo "Installing python3-venv..."
    sudo apt install -y python3-venv
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing etray-commissioner-local..."
source venv/bin/activate
pip install --no-index --find-links deps/ etray-commissioner-local
deactivate

echo ""
echo "Installation complete. Run ./run.sh to start."
