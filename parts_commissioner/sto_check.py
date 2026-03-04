#!/usr/bin/env python3
"""Module to perform STO switch check via wired connection."""

import subprocess

import questionary

from parts_commissioner.roboteq_motor_controller import NUC_IP

ROS_TOPIC = "/base_motors/estop_state"


def check():
    """Opens a new terminal to monitor the STO topic and prompts the user to toggle the switch."""
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
        f'"balena exec -it $(balena ps -q -f name=ros) '
        f"bash -c 'ros2 topic echo {ROS_TOPIC}'\"; read -p 'Press Enter to close...'"
    )

    subprocess.Popen(["gnome-terminal", "--", "bash", "-c", cmd])

    confirmed = questionary.confirm(
        "   Did the STO switch toggle correctly?"
    ).unsafe_ask()

    if confirmed:
        questionary.print(
            "   - STO check passed!", style="bold ansigreen"
        )
    else:
        questionary.print(
            "   - STO check failed. Please investigate before proceeding.",
            style="bold ansired",
        )
