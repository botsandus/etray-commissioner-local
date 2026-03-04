#!/usr/bin/env python3
"""Main module for the parts commissioner application."""

import pathlib
import sys

import questionary
from appdirs import AppDirs
from prompt_toolkit.styles import Style

import etray_commissioner.options.main as main_options
from etray_commissioner import (
    gen6_psu,
    lidar_configurator,
    roboteq_motor_controller,
    rs232,
    set_overrides,
    sto_check,
    teensy,
    teltonika,
    vna_sensor,
)
from etray_commissioner.robosense_config import SENSOR_TYPES
from etray_commissioner.utils import fetch_update
from etray_commissioner.utils.auth import authenticate
from etray_commissioner.utils.logger import get_audit_logger, get_logger

_log = get_logger()
_audit = get_audit_logger()

QUESTIONARY_STYLE = Style(
    [("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")]
)


def robosense_menu(user: dict):
    """Handles Robosense-related options."""
    sensor_types = [sensor.capitalize() for sensor in SENSOR_TYPES.keys()] + ["Go Back"]
    while True:
        robosense_choice = questionary.select(
            "Select Robosense option:",
            choices=sensor_types,
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if robosense_choice == "Go Back":
            break
        else:
            _audit.info(
                "user=%s role=%s action=Robosense/%s",
                user["name"], user["role"], robosense_choice,
            )
            lidar_configurator.configure_mode(robosense_choice)


def toggle_menu(user: dict):
    """Main menu for selecting parts to commission."""
    while True:
        choice = questionary.select(
            "What parts would you like to commission?",
            choices=["Robosense", *main_options.PARTS_OPTIONS],
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if choice == "Robosense":
            robosense_menu(user)

        elif choice == main_options.OS1_Lidars:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            lidar_configurator.configure_mode("OS1")

        elif choice == main_options.VNA_SENSOR:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            vna_sensor.configure_vna()

        elif choice == main_options.BASE_ROBOTEQ_MOTOR_CONTROLLER:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            roboteq_motor_controller.flash()

        elif choice == main_options.BASE_ROBOTEQ_MOTOR_CONTROLLER_REMOTE:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            roboteq_motor_controller.flash_remote()

        elif choice == main_options.TELTONIKA:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            teltonika.flash()

        elif choice == main_options.RS232:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            rs232.flash()

        elif choice == main_options.TEENSY:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            teensy.flash()

        elif choice == main_options.GEN6_PSU_FIRMWARE:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            gen6_psu.flash()

        elif choice == main_options.SET_OVERRIDES:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            set_overrides.configure()

        elif choice == main_options.STO_CHECK:
            _audit.info("user=%s role=%s action=%s", user["name"], user["role"], choice)
            sto_check.check()

        elif choice == "Exit":
            _audit.info("user=%s role=%s action=Exit", user["name"], user["role"])
            sys.exit()

        else:
            questionary.print("   - Not yet implemented!", style="bold fg:ansired")


def login() -> dict:
    """Prompts for a password and returns the authenticated user.

    Allows up to 3 attempts before exiting.

    Returns:
        dict: The authenticated user dict with 'name' and 'role'.
    """
    for attempt in range(3):
        password = questionary.password(
            "Enter your password:",
            qmark=">>",
        ).unsafe_ask()

        user = authenticate(password)
        if user:
            _log.info("Login successful: %s (%s)", user["name"], user["role"])
            questionary.print(
                f"   Welcome, {user['name']}!\n", style="bold fg:ansigreen"
            )
            return user

        remaining = 2 - attempt
        if remaining > 0:
            questionary.print(
                f"   Incorrect password. {remaining} attempt(s) remaining.",
                style="bold fg:ansired",
            )

    questionary.print("   Too many failed attempts. Exiting.", style="bold fg:ansired")
    sys.exit(1)


def run():
    """Entry point for the parts commissioner application."""
    module_name = "etray-commissioner-local"

    data_dir_path = AppDirs(module_name).user_data_dir
    pathlib.Path(data_dir_path).mkdir(parents=True, exist_ok=True)

    questionary.print("You are using Parts Commissioner!\n", style="bold fg:ansigreen")

    user = login()
    _audit.info("user=%s role=%s action=Login", user["name"], user["role"])

    if user.get("role") == "admin":
        fetch_update.check(module_name)

    try:
        toggle_menu(user)
    except KeyboardInterrupt:
        questionary.print("   - Interrupted by user!", style="bold fg:ansired")
        sys.exit()


if __name__ == "__main__":
    run()
