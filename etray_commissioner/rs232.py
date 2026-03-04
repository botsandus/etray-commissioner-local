#!/usr/bin/env python3
"""Module to flash the RS232 motor controller cable."""

import os
import subprocess

import questionary
from appdirs import AppDirs

from etray_commissioner.utils.git_fetch_repo import download_repo

MODULE_NAME = "etray-commissioner"
DATA_DIR = AppDirs(MODULE_NAME).user_data_dir
REPO_NAME = "auto-tower"
REPO_DIR = os.path.join(DATA_DIR, REPO_NAME)
MODULE_DIR = os.path.dirname(__file__)


def create_dev_rules():
    """Create the dev rules for the cable."""
    dev_rules_path = os.path.join(MODULE_DIR, "config", "99-dexory.rules")
    target_path = "/etc/udev/rules.d/99-dexory.rules"

    # check if path is present
    if not os.path.exists(target_path):
        os.system(f"sudo cp {dev_rules_path} {target_path}")
        os.system("sudo udevadm control --reload-rules")
        os.system("sudo udevadm trigger")
        questionary.print(
            " - The dev rules have been created for the RS232 cable.\n",
            style="bold ansigreen",
        )


def verify_usb_info():
    """Verify the USB information of the cable."""

    proc = subprocess.run(
        [r'lsusb -d 0403:6001 -vv | grep "iProduct\|iManufacturer"'],
        shell=True,
        check=False,
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        questionary.print(
            "  - Failed to get cable information after flashing.\n",
            style="bold ansired",
        )
    elif not proc.stdout:
        questionary.print(
            "  - The cable information is not available. "
            "This can happen if the cable is not connected\n",
            style="bold ansired",
        )
    elif "Roboteq Tower RS232" in proc.stdout:
        questionary.print(
            "  - The product id has been updated successfully.\n",
            style="bold ansigreen",
        )
    else:
        questionary.print(
            "  - The product id has not been updated.\n",
            style="bold ansired",
        )


def flash():
    """Flashes the RS232 motor controller cable."""

    # makes sure that the repo is up to date
    download_repo(REPO_NAME)

    create_dev_rules()

    # Flash the cable
    number_of_devices = questionary.text(
        "Enter the number of RS232 cables you want to flash:",
        validate=lambda number_of_devices: (
            True
            if number_of_devices.isdigit() and int(number_of_devices) > 0
            else "Please enter a valid number."
        ),
        qmark=">>",
    ).unsafe_ask()

    print()

    for device_idx in range(int(number_of_devices)):
        questionary.print("\n - First Flash ...\n", style="bold fg:ansigreen")
        os.system(f"cd {REPO_DIR}/roboteq_tower_driver/rs232_ftdi_eeprom && make flash")
        questionary.print("\n - Second Flash ...\n", style="bold fg:ansigreen")
        os.system(f"cd {REPO_DIR}/roboteq_tower_driver/rs232_ftdi_eeprom && make flash")

        verify_usb_info()

        if device_idx != int(number_of_devices) - 1:
            questionary.press_any_key_to_continue(
                "Disconnect the current cable and connect the next...\n"
            ).unsafe_ask()
