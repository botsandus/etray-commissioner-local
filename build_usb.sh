#!/bin/bash
# Run this on the development machine to prepare the offline package.
# It downloads all dependencies as wheels into deps/.
# Copy the entire folder to a USB stick.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Downloading all dependencies into deps/..."
mkdir -p deps
pip wheel . --wheel-dir deps/

echo ""
echo "Done. Copy this entire folder to a USB stick."
echo "On the target machine, run: ./install.sh"
