#!/usr/bin/env python3
"""Module to flash the teensy."""

import glob
import os

import questionary

# from parts_commissioner.utils import gh
from parts_commissioner.utils.fetch_firmware_unified_psu import (
    DATA_DIR,
    REPO_NAME,
    download_latest,
    is_repo_installed,
    update_repo,
)

MODULE_DIR = os.path.dirname(__file__)


def create_dev_rules():
    """Create the dev rules for the cable."""
    dev_rules_path = os.path.join(MODULE_DIR, "config", "00-teensy.rules")
    target_path = "/etc/udev/rules.d/00-teensy.rules"

    # check if path is present
    if not os.path.exists(target_path):
        os.system(f"sudo cp {dev_rules_path} {target_path}")
        os.system("sudo udevadm control --reload-rules")
        os.system("sudo udevadm trigger")
        questionary.print(
            " - The dev rules have been created for the Teensy.\n",
            style="bold ansigreen",
        )


def flash():
    """Flashes the Teltonika router."""

    if not is_repo_installed():
        questionary.print(
            " - The repo is not installed on this device. "
            "Attempting to install them...",
            style="bold fg:ansiyellow",
        )
        if not download_latest():
            questionary.print(
                " - Could not download the latest version of the repo!",
            )
            return

        # target_release = gh.get_latest_release(REPO_NAME)
        target_release = "v1.0.7"

    else:
        target_release = update_repo()

    create_dev_rules()

    repo_path = os.path.join(DATA_DIR, f"{REPO_NAME.split('/')[1]}", target_release)

    # get the script name using glob
    script_name = glob.glob(f"{repo_path}/*PRODUCTION.hex")[0]

    # get the script name
    script_name = script_name.split("/")[-1]

    # run the script
    os.system(
        f"cd {MODULE_DIR}/config && "
        "./teensy_loader_cli --mcu=TEENSY41 -w -s -v "
        f"{repo_path}/{script_name}"
    )
