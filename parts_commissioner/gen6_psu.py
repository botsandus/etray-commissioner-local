#!/usr/bin/env python3
"""Module to flash the Gen6 PSU firmware."""

import subprocess
import sys

import questionary
from rich.console import Console

from parts_commissioner import psu_initial_flash
from parts_commissioner.roboteq_motor_controller import NUC_IP, is_device_available


def flash():
    """Flashes the Gen6 PSU firmware via wired connection to the NUC."""
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
        "[bold cyan] Flashing the Gen6 PSU firmware...", spinner="dots"
    ):
        proc = subprocess.run(
            [
                "ssh",
                "-oStrictHostKeyChecking=no",
                "-t",
                f"root@{NUC_IP}",
                "balena exec -it $(balena ps -q -f name=firm) "
                "bash -c 'firmware_update -m firmware/manifest_gen6.json -y'",
            ],
            check=False,
            text=True,
            capture_output=True,
        )

    # Restore terminal state after SSH -t session
    subprocess.run(["stty", "sane"], check=False)

    if proc.returncode != 0:
        questionary.print(
            "  - Failed to flash the Gen6 PSU firmware!", style="bold ansired"
        )
        if questionary.confirm(
            "   Would you like to try the initial Teensy flash?"
        ).unsafe_ask():
            psu_initial_flash.flash()
        return

    questionary.print(
        "   - The Gen6 PSU firmware has been flashed successfully!",
        style="bold ansigreen",
    )
