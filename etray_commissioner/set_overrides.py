#!/usr/bin/env python3
"""Module to set Robot Manager overrides via wired connection."""

import os

import questionary
import requests
import yaml
from rich.console import Console

from etray_commissioner.roboteq_motor_controller import NUC_IP

RM_OVERRIDES_ENDPOINT = "/api/v1/config/overrides"
RM_SERVICES_ENDPOINT = "/api/v1/system/services"
EXPECTED_VARS_FILE = os.path.join(
    os.path.dirname(__file__), "config", "rm_overrides.yaml"
)


def _get_overrides():
    try:
        res = requests.get(f"http://{NUC_IP}{RM_OVERRIDES_ENDPOINT}", timeout=10)
        if res.ok:
            return res.json()
    except (requests.ConnectionError, requests.Timeout):
        pass
    return None


def _set_overrides(overrides):
    try:
        res = requests.put(
            f"http://{NUC_IP}{RM_OVERRIDES_ENDPOINT}", json=overrides, timeout=6
        )
        return res.ok
    except (requests.ConnectionError, requests.Timeout):
        return False


def _restart_service(service):
    try:
        res = requests.post(
            f"http://{NUC_IP}{RM_SERVICES_ENDPOINT}/{service}/docker-restart",
            timeout=30,
        )
        if service == "robot-manager" and res.status_code in [500, 502]:
            return True
        return res.ok
    except requests.ConnectionError as e:
        return "Connection aborted" in str(e)
    except requests.Timeout:
        return False


def configure():
    """Sets Robot Manager overrides via wired connection to the NUC."""
    num_sections_str = questionary.text(
        "Number of tower sections:",
        validate=lambda x: x.isdigit() and int(x) > 0 or "Enter a valid number",
    ).unsafe_ask()
    num_sections = int(num_sections_str)

    with Console().status("[bold cyan] Getting current overrides...", spinner="dots"):
        current = _get_overrides()

    if current is None:
        questionary.print(
            "\n   - Failed to get overrides."
            " Make sure the robot is connected via wired cable.\n",
            style="bold ansired",
        )
        return

    with open(EXPECTED_VARS_FILE, "r") as f:
        expected = yaml.safe_load(f)

    expected["NUM_TOWER_SECTIONS"] = num_sections
    current.update(expected)

    with Console().status("[bold cyan] Setting overrides...", spinner="dots"):
        ok = _set_overrides(current)

    if not ok:
        questionary.print("   - Failed to set overrides!", style="bold ansired")
        return

    questionary.print("   - Overrides set successfully!", style="bold ansigreen")

    with Console().status("[bold cyan] Restarting services...", spinner="dots"):
        ros_ok = _restart_service("ros_prod")
        rm_ok = _restart_service("robot-manager")

    if not ros_ok or not rm_ok:
        questionary.print("   - Failed to restart services!", style="bold ansired")
        return

    questionary.print("   - Services restarted successfully!", style="bold ansigreen")
