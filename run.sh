#!/bin/bash
# Launches etray-commissioner.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running install.sh first..."
    ./install.sh
fi

source venv/bin/activate
etray-commissioner
deactivate
