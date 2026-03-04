#!/usr/bin/env python3
"""Module to perform STO switch check via wired connection."""

import subprocess

import questionary

from etray_commissioner.roboteq_motor_controller import NUC_IP
from etray_commissioner.utils.logger import get_logger, log_path

ROS_TOPIC = "/base_motors/estop_state"
_log = get_logger()


def check():
    """Monitors the STO topic in a new terminal and asks user to verify the toggle."""
    _log.info("Starting STO check")

    questionary.print(
        "\n   Opening STO topic monitor in a new terminal...",
        style="bold fg:ansicyan",
    )
    questionary.print(
        "   Toggle the STO switch and watch the topic output.\n",
        style="bold fg:ansicyan",
    )

    cmd = (
        f"ssh -oStrictHostKeyChecking=no -t root@{NUC_IP} "
        f'"/usr/bin/balena exec -it \\$(/usr/bin/balena ps -q -f name=ros) '
        f"bash -c 'source /opt/ros/kilted/setup.bash && ros2 topic echo {ROS_TOPIC}'\""
        "; read -p 'Press Enter to close...'"
    )

    subprocess.Popen(["gnome-terminal", "--", "bash", "-c", cmd])

    confirmed = questionary.confirm(
        "   Did the STO switch toggle correctly?"
    ).unsafe_ask()

    if confirmed:
        _log.info("STO check passed")
        questionary.print("   - STO check passed!", style="bold ansigreen")
    else:
        _log.error("STO check failed - user reported toggle did not work correctly")
        questionary.print(
            "   - STO check failed. Please investigate before proceeding.",
            style="bold ansired",
        )
        questionary.print(f"   See log: {log_path()}", style="fg:ansiyellow")
