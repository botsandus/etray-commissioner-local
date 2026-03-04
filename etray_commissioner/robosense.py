import subprocess

import questionary
from prompt_toolkit.styles import Style

import etray_commissioner.utils.network as network
from etray_commissioner.options.configuration_types import AUTOMATIC, GO_BACK
from etray_commissioner.robosense_config import SENSOR_TYPES

QUESTIONARY_STYLE = Style(
    [("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")]
)


class RobosenseConfigurator:
    """A class to configure Robosense sensors."""

    def __init__(self, base_config, individual_config, boundary, target_url, mode):
        self.base_config = base_config
        self.individual_config = individual_config
        self.boundary = boundary
        self.target_url = target_url
        self.mode = mode

    def find_device_ip(self, default_ip: str) -> str | None:
        """Finds the first reachable device IP from a list of possible IPs.

        Args:
            default_ip (str): The default IP address to check first.

        Returns:
            str | None: The found IP address if reachable, otherwise None.
        """
        possible_ips = [
            config["device_ip_addr"] for config in self.individual_config.values()
        ]

        questionary.print(
            f"\n - Checking if the device is reachable at {default_ip}...",
            style="fg:ansicyan",
        )
        if network.ping_device(default_ip):
            return default_ip

        if self.mode == AUTOMATIC:
            questionary.print(
                "\n - Device not found at default IP. "
                "Switching to 172.16.0.100 network...\n",
                style="bold fg:ansiyellow",
            )
            try:
                network.configure_connection("172.16.0.100")
            except Exception as exc:
                questionary.print(
                    f"\n - Failed to configure network: {exc}",
                    style="bold fg:ansired",
                )
                return None

        else:
            questionary.press_any_key_to_continue(
                "\n - Device not found at default IP. "
                "Please switch to the 172.16.0.* range and press ENTER when ready."
            ).unsafe_ask()

        for ip in possible_ips:
            questionary.print(f" - Checking {ip}...", style="fg:ansicyan")
            if network.ping_device(ip):
                questionary.print(
                    f"\n - Device found at {ip}!", style="bold fg:ansigreen"
                )
                return ip

        return None

    def upload_configuration(self, device: str, target_ip: str) -> bool:
        """Uploads the configuration to the device after generating the curl command.

        Args:
            device (str): The name of the Robosense device to configure.
            target_ip (str): The IP address of the device to configure.

        Returns:
            bool: True if the configuration was uploaded successfully,
            False otherwise."""

        if device not in self.individual_config:
            questionary.print(f" - Invalid device: {device}")
            return False

        configuration = self.base_config
        configuration.update(self.individual_config[device])

        form_data = {**self.base_config, **configuration}

        data_parts = [
            f"--{self.boundary}\r\nContent-Disposition: form-data; name='{key}'\r\n\r\n"
            f"{value}\r\n"
            for key, value in form_data.items()
        ]

        data_parts.append(f"--{self.boundary}--\r\n")
        data_payload = "".join(data_parts)

        target_url = f"http://{target_ip}{self.target_url}"

        curl_command = (
            f"curl '{target_url}' -H 'Content-Type: multipart/form-data; "
            f"boundary={self.boundary}' "
            f"--data-raw $'{data_payload}'"
        )

        proc = subprocess.run(
            curl_command,
            shell=True,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return proc.returncode == 0

    def configure_sensor(self, selected_sensors: list, default_ip: str) -> (bool, list):
        """Executes the Robosense configuration task.

        Args:
            selected_sensors (list): List of sensors to configure.
            default_ip (str): Default IP address to start searching for devices.

        Returns:
            tuple: A tuple containing:
                - bool: True if all sensors are successfully configured, False if not.
                - list: A list of sensors that were not successfully configured.
        """
        questionary.press_any_key_to_continue(
            "\n - Connect your laptop to the front panel Ethernet port "
            "and press Enter when ready."
        ).unsafe_ask()

        all_successful = True  # Track overall success
        failed_sensors = []  # Track sensors that failed configuration

        for device in selected_sensors:
            if self.mode == AUTOMATIC:
                questionary.print(
                    "\n - Setting host network IP to 192.168.1.100 ...",
                    style="fg:ansicyan",
                )
                try:
                    network.configure_connection("192.168.1.100")
                except Exception as exc:
                    questionary.print(
                        f"\n - Failed to configure network: {exc}",
                        style="bold fg:ansired",
                    )
                    return False, selected_sensors
            else:
                questionary.press_any_key_to_continue(
                    "\n - Set your IP to 192.168.1.* range and press ENTER when ready."
                ).unsafe_ask()

            questionary.press_any_key_to_continue(
                f"\n - Please ensure all devices except {device} are powered off "
                "and press ENTER when ready."
            ).unsafe_ask()

            found_ip = self.find_device_ip(default_ip)

            if not found_ip:
                questionary.print(
                    f"\n - {device} not found on the network,"
                    "\n ---- Configuration Unsuccessful!! ---- ",
                    style="bold fg:ansired",
                )
                all_successful = False  # Mark as unsuccessful
                failed_sensors.append(device)  # Add to failed sensors list
                continue

            questionary.print(
                f"\n - Uploading configuration to {device} at {found_ip}...",
                style="bold fg:ansicyan",
            )
            if not self.upload_configuration(device, found_ip):
                questionary.print(f"\n - Failed to upload configuration to {device}.")
                all_successful = False  # Mark as unsuccessful
                failed_sensors.append(device)  # Add to failed sensors list
                continue

            questionary.print(
                f"\n - Configuration successfully uploaded to {device}",
                style="bold fg:ansigreen",
            )

        questionary.print(
            "\n - Ensure all disconnected devices are connected back to the robot.",
            style="bold fg:ansigreen",
        )

        if not all_successful:
            questionary.print(
                "\n - Summary of sensors that were not configured successfully:",
                style="bold fg:ansired",
            )
            for sensor in failed_sensors:
                questionary.print(f"   - {sensor}", style="fg:ansired")
        elif all_successful:
            questionary.print(
                "\n - All sensors configured successfully!",
                style="bold fg:ansigreen",
            )
        if self.mode == AUTOMATIC:
            # Turn off the Ethernet connection
            try:
                network.turn_off_connection()
            except Exception as exc:
                questionary.print(
                    f"\n - Failed to turn off network connection: {exc}",
                    style="bold fg:ansired",
                )

        return (
            all_successful,
            failed_sensors,
        )  # Return the overall success status and failed sensors


def configure_robosense(
    mode: str, sensor_type: str, configuration_type: str
) -> tuple[bool, list]:
    """Configures the Lidars.

    Args:
        mode (str): The configuration mode (Manual or Automatic).
        sensor_type (str): The type of sensor to configure.
        configuration_type (str): The type of configuration (Robot or Individual).

    Returns:
        tuple: A tuple containing:
            - bool: True if all sensors are successfully configured, False otherwise.
            - list: A list of sensors that were not successfully configured.
    """
    sensor_config = SENSOR_TYPES.get(sensor_type.lower())
    if not sensor_config:
        questionary.print(
            f" - Unknown Robosense sensor type: {sensor_type}",
            style="bold fg:ansired",
        )
        return False, []
    individual_config = sensor_config["individual_config"].keys()

    if configuration_type == "Individual":
        while True:
            choice = questionary.select(
                "Which sensor would you like to configure?",
                choices=list(individual_config) + [GO_BACK],
                style=QUESTIONARY_STYLE,
                qmark=">>",
            ).unsafe_ask()

            if choice == GO_BACK:
                return True, []  # No sensors were configured, so return success

            success, failed_sensors = RobosenseConfigurator(
                sensor_config["base_config"],
                sensor_config["individual_config"],
                sensor_config["boundary"],
                sensor_config["target_url"],
                mode,
            ).configure_sensor([choice], "192.168.1.200")

            return success, failed_sensors  # Return the result for the selected sensor

    elif configuration_type == "Robot":
        sensors_to_configure = sensor_config.get(
            "robot_default_config", list(individual_config)
        )
        success, failed_sensors = RobosenseConfigurator(
            sensor_config["base_config"],
            sensor_config["individual_config"],
            sensor_config["boundary"],
            sensor_config["target_url"],
            mode,
        ).configure_sensor(sensors_to_configure, "192.168.1.200")

        return success, failed_sensors  # Return the result for all sensors
