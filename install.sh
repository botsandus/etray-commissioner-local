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

echo "Installing etray-commissioner..."
source venv/bin/activate
pip install --no-index --find-links deps/ etray-commissioner-local
deactivate

# SSH key setup for NUC access
if [ -f "ssh/dexory_shared.key" ]; then
    echo "Setting up SSH key for NUC access..."
    mkdir -p ~/.ssh
    cp ssh/dexory_shared.key ~/.ssh/dexory_shared.key
    chmod 600 ~/.ssh/dexory_shared.key

    SSH_CONFIG="$HOME/.ssh/config"
    if ! grep -q "dexory_shared.key" "$SSH_CONFIG" 2>/dev/null; then
        cat >> "$SSH_CONFIG" <<'EOF'

Host 172.16.0.*
    Port 22222
    ForwardAgent yes
    User root
    IdentityFile ~/.ssh/dexory_shared.key
EOF
        chmod 600 "$SSH_CONFIG"
        echo "SSH config updated."
    else
        echo "SSH config already set up."
    fi
fi

echo ""
echo "Installation complete. Run ./run.sh to start."
