#!/usr/bin/env python3
"""Module to configure the Roboteq Motor Controller."""

import re
import subprocess
import sys

import questionary
from rich.console import Console

NUC_IP = "172.16.0.1"
ROBOT_REGEX = r"arri-[1-9]\d*$"


def is_device_available(device_hostname: str, timeout: int = 10) -> bool:
    """Pings the ip address of the device.

    Args:
        device_hostname (str): the name of the device
        timeout (int): the timeout for the ping
    Returns:
        bool: True if the device is reachable, False otherwise.
    """

    proc = subprocess.run(
        ["ping", "-c 1", "-w", str(timeout), device_hostname],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def flash():
    """Flashes the Roboteq Motor Controller via wired connection to the NUC."""
    flash_result = True

    with Console().status(
        "[bold cyan] Waiting for the device to be available...", spinner="dots"
    ):
        if not is_device_available(NUC_IP):
            questionary.print(
                "\n   - The NUC is not reachable."
                " Make sure the robot is connected via wired cable.\n",
                style="bold ansired",
            )
            flash_result = False

    # Clear the spinner
    sys.stdout.write("\0337\033[3F\033[K\0338")
    sys.stdout.flush()

    if not flash_result:
        return

    with Console().status(
        "[bold cyan] Flashing the motor driver firmware...", spinner="dots"
    ):
        proc = subprocess.run(
            [
                "ssh",
                "-oStrictHostKeyChecking=no",
                "-t",
                f"root@{NUC_IP}",
                "balena exec -it $(balena ps -q -f name=ros) "
                "bash -c 'cd /opt/auto_ws/install/roboteq_driver/"
                "share/roboteq_driver/firmware && "
                "chmod +x 4gen_SBLG_only_firmware_upgrade.sh && "
                "./4gen_SBLG_only_firmware_upgrade.sh'",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    if "No DFU capable USB device available" in proc.stdout:
        questionary.print(
            "\n   - Roboteq Motor Controller is not detected.\n"
            "   - This can happen if the motor controller has "
            "recently been flashed, reboot the robot to continue.\n",
            style="bold ansired",
        )
        return

    if proc.returncode != 0:
        questionary.print(
            "  - Failed to flash the motor driver firmware!", style="bold ansired"
        )

    questionary.print(
        "   - The motor driver firmware has been flashed successfully!",
        style="bold ansigreen",
    )


def flash_remote():
    """Flashes the Roboteq Motor Controller via Tailscale (remote)."""
    robot_name = questionary.text(
        "Which robot would you like to configure?",
        validate=lambda name: (
            True
            if re.search(ROBOT_REGEX, name) or name == "arri-commissioning"
            else "Please enter a valid robot name e.g., arri-79, or arri-commissioning"
        ),
        default="arri-",
        qmark=">>",
    ).unsafe_ask()

    flash_result = True

    with Console().status(
        "[bold cyan] Waiting for the device to be available...", spinner="dots"
    ):
        if not is_device_available(robot_name):
            questionary.print(
                "\n   - The robot is not reachable."
                " Make sure the robot is connected to the network.\n",
                style="bold ansired",
            )
            flash_result = False

    # Clear the spinner
    sys.stdout.write("\0337\033[3F\033[K\0338")
    sys.stdout.flush()

    if not flash_result:
        return

    with Console().status(
        "[bold cyan] Flashing the motor driver firmware...", spinner="dots"
    ):
        proc = subprocess.run(
            [
                "ssh",
                "-oStrictHostKeyChecking=no",
                "-t",
                f"root@{robot_name}.velociraptor-tuna.ts.net",
                "balena exec -it $(balena ps -q -f name=ros) "
                "bash -c 'cd /opt/auto_ws/install/roboteq_driver/"
                "share/roboteq_driver/firmware && "
                "chmod +x 4gen_SBLG_only_firmware_upgrade.sh && "
                "./4gen_SBLG_only_firmware_upgrade.sh'",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    if "No DFU capable USB device available" in proc.stdout:
        questionary.print(
            "\n   - Roboteq Motor Controller is not detected.\n"
            "   - This can happen if the motor controller has "
            "recently been flashed, reboot the robot to continue.\n",
            style="bold ansired",
        )
        return

    if proc.returncode != 0:
        questionary.print(
            "  - Failed to flash the motor driver firmware!", style="bold ansired"
        )

    questionary.print(
        "   - The motor driver firmware has been flashed successfully!",
        style="bold ansigreen",
    )
