#!/usr/bin/env python3
"""Module to perform initial flash of the Gen6 PSU Teensy firmware."""

import subprocess
import sys

import questionary
from rich.console import Console

from etray_commissioner.roboteq_motor_controller import NUC_IP, is_device_available
from etray_commissioner.utils.logger import get_logger, log_path

HEX_FILE = "firmware-unified-psu-v2.0.1-78fc610-main-PRODUCTION.hex"
_log = get_logger()


def flash():
    """Performs initial flash of the Gen6 PSU Teensy via the NUC."""
    _log.info("Starting Gen6 PSU initial Teensy flash")

    with Console().status(
        "[bold cyan] Waiting for the device to be available...", spinner="dots"
    ):
        if not is_device_available(NUC_IP):
            _log.error("NUC not reachable at %s", NUC_IP)
            questionary.print(
                "\n   - The NUC is not reachable."
                " Make sure the robot is connected via wired cable.\n",
                style="bold ansired",
            )
            questionary.print(f"   See log: {log_path()}", style="fg:ansiyellow")
            return

    # Clear the spinner
    sys.stdout.write("\0337\033[3F\033[K\0338")
    sys.stdout.flush()

    questionary.print(
        "   Flashing the Gen6 PSU Teensy firmware...", style="bold fg:ansicyan"
    )
    proc = subprocess.run(
        [
            "ssh",
            "-oStrictHostKeyChecking=no",
            f"root@{NUC_IP}",
            "serial=$(udevadm info /dev/ttyACM0 | grep ID_USB_SERIAL_SHORT"
            " | cut -d= -f2) && "
            f"balena exec $(balena ps -q -f name=firm) "
            f'bash -c "cd firmware/teensy41/ && flash.sh TEENSY41 $serial {HEX_FILE}"',
        ],
        check=False,
        text=True,
        stdin=subprocess.DEVNULL,
    )

    if proc.returncode != 0:
        _log.error(
            "Initial Teensy flash failed (rc=%d). stdout: %s stderr: %s",
            proc.returncode,
            proc.stdout,
            proc.stderr,
        )
        questionary.print(
            "  - Failed to perform the initial Teensy flash!", style="bold ansired"
        )
        questionary.print(f"   See log: {log_path()}", style="fg:ansiyellow")
        return

    _log.info("Gen6 PSU initial Teensy flash successful")
    questionary.print(
        "   - The Gen6 PSU Teensy firmware has been flashed successfully!",
        style="bold ansigreen",
    )
