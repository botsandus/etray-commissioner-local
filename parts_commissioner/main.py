#!/usr/bin/env python3
"""Main module for the parts commissioner application."""

import pathlib
import sys

import questionary
from appdirs import AppDirs
from prompt_toolkit.styles import Style

import parts_commissioner.options.main as main_options
from parts_commissioner import (
    gen6_psu,
    image_generation,
    lidar_configurator,
    roboteq_motor_controller,
    rs232,
    set_overrides,
    sto_check,
    teensy,
    teltonika,
    vna_sensor,
)
from parts_commissioner.robosense_config import SENSOR_TYPES
from parts_commissioner.utils import fetch_update
from parts_commissioner.utils.auth import authenticate

QUESTIONARY_STYLE = Style(
    [("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")]
)


def robosense_menu():
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
            break  # Return to the main menu
        else:
            lidar_configurator.configure_mode(robosense_choice)


def toggle_menu():
    """Main menu for selecting parts to commission."""
    while True:
        choice = questionary.select(
            "What parts would you like to commission?",
            choices=["Robosense", *main_options.PARTS_OPTIONS],
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if choice == "Robosense":
            robosense_menu()  # Open the Robosense submenu

        elif choice == main_options.OS1_Lidars:
            lidar_configurator.configure_mode("OS1")

        elif choice == main_options.IMAGE_GENERATION:
            image_generation.configure()

        elif choice == main_options.VNA_SENSOR:
            vna_sensor.configure_vna()

        elif choice == main_options.BASE_ROBOTEQ_MOTOR_CONTROLLER:
            roboteq_motor_controller.flash()

        elif choice == main_options.BASE_ROBOTEQ_MOTOR_CONTROLLER_REMOTE:
            roboteq_motor_controller.flash_remote()

        elif choice == main_options.TELTONIKA:
            teltonika.flash()

        elif choice == main_options.RS232:
            rs232.flash()

        elif choice == main_options.TEENSY:
            teensy.flash()

        elif choice == main_options.GEN6_PSU_FIRMWARE:
            gen6_psu.flash()

        elif choice == main_options.SET_OVERRIDES:
            set_overrides.configure()

        elif choice == main_options.STO_CHECK:
            sto_check.check()

        elif choice == "Exit":
            sys.exit()  # Exit the application

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
    module_name = "parts-commissioner"
    fetch_update.check(module_name)

    data_dir_path = AppDirs(module_name).user_data_dir
    pathlib.Path(data_dir_path).mkdir(parents=True, exist_ok=True)

    questionary.print("You are using Parts Commissioner!\n", style="bold fg:ansigreen")

    login()

    try:
        toggle_menu()
    except KeyboardInterrupt:
        questionary.print("   - Interrupted by user!", style="bold fg:ansired")
        sys.exit()


if __name__ == "__main__":
    run()
