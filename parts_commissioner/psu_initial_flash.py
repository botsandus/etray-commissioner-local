#!/usr/bin/env python3
"""Module to perform initial flash of the Gen6 PSU Teensy firmware."""

import subprocess
import sys

import questionary
from rich.console import Console

from parts_commissioner.roboteq_motor_controller import NUC_IP, is_device_available

HEX_FILE = "firmware-unified-psu-v2.0.1-78fc610-main-PRODUCTION.hex"


def flash():
    """Performs initial flash of the Gen6 PSU Teensy via the NUC."""
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

    questionary.print(
        "   Flashing the Gen6 PSU Teensy firmware...", style="bold fg:ansicyan"
    )
    proc = subprocess.run(
        [
            "ssh",
            "-oStrictHostKeyChecking=no",
            f"root@{NUC_IP}",
            "serial=$(udevadm info /dev/ttyACM0 | grep ID_USB_SERIAL_SHORT | cut -d= -f2) && "
            f'balena exec $(balena ps -q -f name=firm) '
            f'bash -c "cd firmware/teensy41/ && flash.sh TEENSY41 $serial {HEX_FILE}"',
        ],
        check=False,
        text=True,
        stdin=subprocess.DEVNULL,
    )

    if proc.returncode != 0:
        questionary.print(
            "  - Failed to perform the initial Teensy flash!", style="bold ansired"
        )
        if proc.stdout:
            questionary.print(proc.stdout, style="fg:ansired")
        if proc.stderr:
            questionary.print(proc.stderr, style="fg:ansired")
        return

    questionary.print(
        "   - The Gen6 PSU Teensy firmware has been flashed successfully!",
        style="bold ansigreen",
    )
