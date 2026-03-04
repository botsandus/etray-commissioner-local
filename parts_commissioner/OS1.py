import difflib
import json
import re
import subprocess
import time

import questionary
import requests

import parts_commissioner.utils.network as network
from parts_commissioner.os1_config import SENSOR_TYPES


def find_os1_ip() -> str | None:
    """Finds the IP address of the OS1 device using the ouster-cli.

    Returns:
        str | None: The IP address of the OS1 device if found, otherwise None.
    """
    questionary.print(
        "\n - Looking for connected OS1 device using ouster-cli...",
        style="bold fg:ansicyan",
    )

    try:
        output = subprocess.check_output(["ouster-cli", "discover"], text=True)
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        if match:
            questionary.print(
                f"\n - OS1 device found at {match.group(1)}", style="bold fg:ansigreen"
            )
            return match.group(1)
        questionary.print("\n - OS1 device NOT found!", style="bold fg:ansired")
        questionary.print(
            "\n - Ensure the device is connected to the robot and powered on.\n",
            style="bold fg:ansired",
        )
    except Exception as e:
        questionary.print(f" - Error running ouster-cli: {e}", style="bold fg:ansired")
    return None


def send_network_override(ip_address, target_ip) -> bool:
    """Sends a network override request using HTTP PUT.

    Args:
        ip_address (str): The IP address of the OS1 device.
        target_ip (str): The target IP address to set on the device.

    Returns:
        bool: True if the network override is successful, False otherwise.
    """
    try:
        url = f"http://{ip_address}/api/v1/system/network/ipv4/override"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(f"{target_ip}/24")  # <-- Send raw string, not object

        response = requests.put(url, headers=headers, data=data, timeout=5)

        if response.status_code == 200:
            time.sleep(5)  # Give the sensor time to reconfigure itself
            questionary.print(
                "\n - Network override successful.", style="bold fg:ansigreen"
            )
            return True
        else:
            questionary.print(
                f" - Network override failed. Status {response.status_code}",
                style="bold fg:ansired",
            )
            return False

    except requests.RequestException as e:
        questionary.print(
            f" - Error sending network override: {e}", style="bold fg:ansired"
        )
        return False


def send_sensor_config(
    ip_address: str, sensor_type: str, configuration_type: str
) -> bool:
    """Sends a sensor configuration request dynamically composed from os1_config.py."""
    try:
        sensor_config = SENSOR_TYPES[sensor_type]["base_config"].copy()
        individual_config = SENSOR_TYPES[sensor_type]["individual_config"].get(
            configuration_type, {}
        )

        # Exclude target_ip which is not part of the sensor API schema
        cleaned_config = {
            k: v for k, v in individual_config.items() if k != "target_ip"
        }
        sensor_config.update(cleaned_config)

        url = f"http://{ip_address}{SENSOR_TYPES[sensor_type]['target_url']}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=sensor_config, timeout=5)

        if response.status_code == 204:
            questionary.print(
                "\n - Sensor configuration successful.", style="bold fg:ansigreen"
            )
            return True
        else:
            questionary.print(
                f"\n - Sensor configuration failed with {response.status_code}. "
                f"\n Response: {response.text}",
                style="bold fg:red",
            )
            return False
    except requests.RequestException as e:
        questionary.print(
            f"\n - Error sending sensor configuration: {e}", style="bold fg:ansired"
        )
        return False


def verify_sensor_config(
    ip_address: str, sensor_type: str, configuration_type: str
) -> bool:
    """Verifies if the sensor's configuration matches the expected one."""
    try:
        url = f"http://{ip_address}{SENSOR_TYPES[sensor_type]['target_url']}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            questionary.print(
                f" - Error fetching sensor configuration. "
                f"Status code: {response.status_code}"
                f"\n Response: {response.text}",
                style="bold fg:ansired",
            )
            return False

        try:
            sensor_config = json.dumps(response.json(), indent=4, sort_keys=True)
        except json.JSONDecodeError as e:
            questionary.print(
                f" - Error decoding sensor JSON: {e}", style="bold fg:ansired"
            )
            return False

        expected_config = SENSOR_TYPES[sensor_type]["base_config"].copy()
        individual_config = SENSOR_TYPES[sensor_type]["individual_config"].get(
            configuration_type, {}
        )
        cleaned_config = {
            k: v for k, v in individual_config.items() if k != "target_ip"
        }
        expected_config.update(cleaned_config)

        expected_config = json.dumps(expected_config, indent=4, sort_keys=True)

        if sensor_config == expected_config:
            questionary.print(
                "\n - Sensor configuration verified successfully.",
                style="bold fg:ansigreen",
            )
            return True
        else:
            questionary.print(
                " - Sensor configuration mismatch. Differences:",
                style="bold fg:ansired",
            )
            diff = difflib.unified_diff(
                expected_config.splitlines(),
                sensor_config.splitlines(),
                fromfile="Expected",
                tofile="Actual",
                lineterm="",
            )
            for line in diff:
                questionary.print(line, style="bold fg:ansiyellow")
            return False

    except requests.RequestException as e:
        questionary.print(
            f" - Error verifying sensor configuration: {e}", style="bold fg:ansired"
        )
        return False


def configure_os1(mode: str, sensor_type: str, configuration_type: str) -> bool:
    """Configures the OS1 sensor and verifies the configuration."""
    questionary.print(
        f"\n - Configuring {sensor_type} in {mode} mode with "
        f"{configuration_type} configuration.",
        style="bold fg:ansicyan",
    )

    questionary.press_any_key_to_continue(
        "\n - Connect your laptop to the front panel Ethernet port "
        "and press Enter when ready."
    ).unsafe_ask()

    unconfigured_ip = find_os1_ip()
    if not unconfigured_ip:
        return False

    host_ip = network.increment_ip(unconfigured_ip)

    if mode == "Automatic":
        questionary.print(
            f"\n - Switching to {host_ip} network...", style="bold fg:ansicyan"
        )
        network.configure_connection(host_ip)
    else:
        questionary.press_any_key_to_continue(
            f"\n - Please switch to the {host_ip} network and press ENTER when ready."
        ).unsafe_ask()

    if not network.ping_device(unconfigured_ip):
        questionary.print(
            f"\n - Failed to reach {unconfigured_ip}. Check network settings.\n",
            style="bold fg:ansired",
        )
        return False

    questionary.print(
        f"\n - Successfully connected to {unconfigured_ip}.",
        style="bold fg:ansigreen",
    )

    target_sensor_ip = SENSOR_TYPES[sensor_type]["individual_config"][
        configuration_type
    ]["target_ip"]
    if not send_network_override(unconfigured_ip, target_sensor_ip):
        return False

    newip = network.increment_ip(target_sensor_ip)
    network.configure_connection(newip)

    if not network.ping_device(target_sensor_ip):
        questionary.print(
            f"\n - Failed to reach sensor at new IP {target_sensor_ip}.",
            style="bold fg:ansired",
        )
        return False

    questionary.print(
        f"\n - Sensor now reachable at {target_sensor_ip}.",
        style="bold fg:ansigreen",
    )

    # --- Apply sensor configuration ---
    if not send_sensor_config(target_sensor_ip, sensor_type, configuration_type):
        return False

    # --- Verify sensor configuration ---
    if not verify_sensor_config(target_sensor_ip, sensor_type, configuration_type):
        questionary.print(
            "\n - Sensor configuration verification failed.\n",
            style="bold fg:ansired",
        )
        return False

    questionary.print(
        f"\n - {configuration_type} sensor configuration completed "
        "and verified successfully.\n",
        style="bold fg:ansigreen",
    )
    return True
