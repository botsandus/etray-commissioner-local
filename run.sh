#!/bin/bash
# Launches etray-commissioner.

if ! command -v etray-commissioner &>/dev/null; then
    echo "etray-commissioner not found. Running install.sh first..."
    "$(dirname "${BASH_SOURCE[0]}")/install.sh"
    echo "Please open a new terminal and run: etray-commissioner"
    exit 0
fi

etray-commissioner
