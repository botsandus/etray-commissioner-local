#!/bin/bash

# Check if a virtual environment exists, if not, run the setup
if [ ! -d "venv" ]; then
    echo "Could not find a virtual environment in your workspace. Running the setup script..."
    ./first_time_setup.sh
    echo "Setup complete!"
fi

# Activate the virtual environment
source venv/bin/activate

# Fetch dependencies into a cleaned array
DEPENDENCIES=($(toml get --toml-path pyproject.toml project.dependencies | tr -d '[],"' | tr '\n' ' ' | sed 's/ *== */==/g'))

INSTALLED_PACKAGES=($(pip list --format freeze))

for dep in "${DEPENDENCIES[@]}"; do
    # Remove any surrounding quotes
    dep_str=$(echo "$dep" | tr -d "'")

    # Check if the dependency is already installed
    if [[ ! " ${INSTALLED_PACKAGES[@]} " =~ " ${dep_str} " ]]; then
        echo -e "\033[0;32mInstalling $dep_str...\033[0m"
        pip install "$dep_str" > /dev/null
    fi
done

# Run parts-commissioner
parts-commissioner

# Deactivate the virtual environment
deactivate
