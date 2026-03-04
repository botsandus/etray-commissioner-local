#!/bin/bash

if [ ! "$(dpkg -l python3-venv 2>/dev/null)" ]; then
    echo "Installing python3-venv"
    sudo apt install -y python3-venv
fi

if [ ! -d "venv" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv venv
else
    echo "Found a virtual environment in your workspace!"
fi

echo "Installing the project requirements"
source venv/bin/activate
pip install toml-cli
pip install -e .
deactivate
