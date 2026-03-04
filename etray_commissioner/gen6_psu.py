#!/usr/bin/env python3
"""Module to flash the Gen6 PSU firmware."""

import subprocess
import sys

import questionary
from rich.console import Console

from etray_commissioner import psu_initial_flash
from etray_commissioner.roboteq_motor_controller import NUC_IP, is_device_available
from etray_commissioner.utils.logger import get_logger, log_path

_log = get_logger()


def flash():
    """Flashes the Gen6 PSU firmware via wired connection to the NUC."""
    _log.info("Starting Gen6 PSU firmware flash")

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
        _log.error(
            "Gen6 PSU flash failed (rc=%d). stdout: %s stderr: %s",
            proc.returncode,
            proc.stdout,
            proc.stderr,
        )
        questionary.print(
            "  - Failed to flash the Gen6 PSU firmware!", style="bold ansired"
        )
        questionary.print(f"   See log: {log_path()}", style="fg:ansiyellow")
        if questionary.confirm(
            "   Would you like to try the initial Teensy flash?"
        ).unsafe_ask():
            psu_initial_flash.flash()
        return

    _log.info("Gen6 PSU firmware flash successful")
    questionary.print(
        "   - The Gen6 PSU firmware has been flashed successfully!",
        style="bold ansigreen",
    )
