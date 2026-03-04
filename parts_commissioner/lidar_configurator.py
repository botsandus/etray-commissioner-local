#!/usr/bin/env python3
"""Module to configure Lidar sensors."""

import questionary
from prompt_toolkit.styles import Style

from parts_commissioner.options.configuration_types import AUTOMATIC, GO_BACK, MANUAL
from parts_commissioner.OS1 import configure_os1
from parts_commissioner.robosense import configure_robosense

QUESTIONARY_STYLE = Style(
    [("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")]
)


def configure_sensors(mode: str, sensor_type: str, configuration_type: str) -> bool:
    """Configures the Lidars.

    Args:
        mode (str): The configuration mode (Manual or Automatic).
        sensor_type (str): The type of sensor to configure.
        configuration_type (str): The type of configuration (Robot or Individual).

    Returns:
        bool: True if the configuration is successful, False otherwise.
    """
    if sensor_type in ["Helios", "Bpearl"]:
        return configure_robosense(mode, sensor_type, configuration_type)
    elif sensor_type == "OS1":
        return configure_os1(mode, sensor_type, configuration_type)
    else:
        questionary.print(" - Not yet implemented!", style="bold fg:ansired")
        return False


def configure_mode(sensor_type: str) -> bool:
    """Configures the mode options for the Lidar Sensor.

    Args:
        sensor_type (str): The type of sensor to configure.

    Returns:
        bool: True if the configuration is successful, False otherwise.
    """
    while True:
        choice = questionary.select(
            "How would you like to configure the sensors?",
            choices=[MANUAL, AUTOMATIC, GO_BACK],
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if choice == GO_BACK:
            break

        if sensor_type in ["Helios", "Bpearl"]:
            return configure_robosense_mode(choice, sensor_type)
        elif sensor_type == "OS1":
            return configure_os1_mode(choice, sensor_type)
        else:
            questionary.print(" - Not yet implemented!", style="bold fg:ansired")
            return False


def configure_robosense_mode(choice: str, sensor_type: str) -> bool:
    """Configures the mode options for Robosense sensors.

    Args:
        choice (str): The selected configuration mode.
        sensor_type (str): The type of sensor to configure.

    Returns:
        bool: True if the configuration is successful, False otherwise.
    """
    if choice in [MANUAL, AUTOMATIC]:
        configuration_type = questionary.select(
            "What would you like to do?",
            choices=["Robot", "Individual", GO_BACK],
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if configuration_type != GO_BACK:
            success = configure_sensors(choice, sensor_type, configuration_type)
            return success
    return False


def configure_os1_mode(choice: str, sensor_type: str) -> bool:
    """Configures the mode options for OS1 sensors.

    Args:
        choice (str): The selected configuration mode.
        sensor_type (str): The type of sensor to configure.

    Returns:
        bool: True if the configuration is successful, False otherwise.
    """
    if choice in [MANUAL, AUTOMATIC]:
        configuration_type = questionary.select(
            "What would you like to do?",
            choices=["Block-stack", "Pick-face", GO_BACK],
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if configuration_type != GO_BACK:
            success = configure_sensors(choice, sensor_type, configuration_type)
            return success
    return False
