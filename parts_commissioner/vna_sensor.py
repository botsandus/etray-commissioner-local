"""Module to configure VNA sensor over serial connection."""

import os
import re
import time

import questionary
from prompt_toolkit.styles import Style
from serial import Serial, SerialException

import parts_commissioner.options.vna as vna_options

QUESTIONARY_STYLE = Style(
    [("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")]
)

# Default configuration Constants
BAUD_RATE = 115200
PORT = "/dev/ttyVNA"

FREQUENCIES = [5000, 5700, 6250, 7000, 7800, 25000]
CAN_MODE = "CAN"

GAIN1 = 50
GAIN2 = 50
GAIN_THRESHOLD = 150
CAN_BUS_RATE = "500 kBit"

FRONT_NODE_ID = 101
REAR_NODE_ID = 102

FREQ_REGEX = r"\x1b\[04;18H([\d\s]+)"

CAN_MODE_REGEX = r"\x1b\[04;18H([\s\w]+)"
CAN_NODE_ID_REGEX = r"\x1b\[05;18H([\d\s]+)"
CAN_BAUDRATE_REGEX = r"\x1b\[06;18H([\d\s\w]+)"

GAIN1_REGEX = r"\x1b\[07;18H([\d\s]+)"
GAIN2_REGEX = r"\x1b\[08;18H([\d\s]+)"
GAIN_THRESHOLD_REGEX = r"\x1b\[09;18H([\d\s]+)"


MODULE_DIR = os.path.dirname(__file__)


def create_dev_rules():
    """Create the dev rules for the cable."""
    dev_rules_path = os.path.join(MODULE_DIR, "config", "01-vna.rules")
    target_path = "/etc/udev/rules.d/01-vna.rules"

    # check if path is present
    if not os.path.exists(target_path):
        os.system(f"sudo cp {dev_rules_path} {target_path}")
        os.system("sudo udevadm control --reload-rules")
        os.system("sudo udevadm trigger")
        questionary.print(
            " - The dev rules have been created for the VNA.\n",
            style="bold ansigreen",
        )


class VNASensorConfigurator:
    """Class to configure a VNA sensor over serial connection."""

    def __init__(
        self,
        node_id,
    ):
        self.node_id = node_id
        self.ser = None
        create_dev_rules()

    def connect(self):
        """Establish serial connection to the sensor."""
        try:
            self.ser = Serial(PORT, BAUD_RATE, timeout=1)
            questionary.print(
                f"\n - Connected to the sensor on {PORT} at {BAUD_RATE} baud\n",
                style="bold fg:ansigreen",
            )
            time.sleep(2)  # Wait for the connection to stabilize
        except SerialException as e:
            questionary.print(
                f" - Error connecting to sensor: {e}", style="bold fg:ansired"
            )
            raise e

    def write_to_device(self, command: str):
        """Writes a command to the serial device and waits for the specified delay.

        Args:
            command (str): Command to write to the device.
        """
        self.ser.write(command.encode("utf-8"))
        time.sleep(0.5)

    def read_from_sensor(self) -> str:
        """Reads the whole buffer from the serial."""
        buffer = ""
        while True:
            if self.ser.in_waiting > 0:
                buffer = self.ser.read_all().decode("utf-8", "ignore")
                break
            time.sleep(0.1)

        return buffer

    def check_for_page(self, page_name: str, timeout=4) -> bool:
        """Reads from the sensor until a specific page_name is found
        or timeout occurs.

        Args:
            page_name (str): Name of the page to look for.
            timeout (int): Timeout in seconds.

        Returns:
            bool: True if page_name is found, False otherwise.
        """
        end_time = time.time() + timeout
        buffer = ""

        while time.time() < end_time:
            buffer += self.read_from_sensor()
            if page_name in buffer:
                return True

        questionary.print(
            f" - Read for Prompt '{page_name}'\n{buffer}", style="bold fg:ansired"
        )
        questionary.print(
            f" - Prompt '{page_name}' not found within {timeout} seconds.",
            style="bold fg:ansired",
        )
        return False

    def _set_calibration_param(self, menu_option: int, value: int):
        """Helper to set calibration parameters.

        Args:
            name (str): Name of the parameter.
            menu_option (int): Menu option to select.
            value (int): Value to set.
        """
        self.write_to_device(f"{menu_option}")  # Select configuration option
        self.write_to_device(f"{value}\n")  # Set the parameter value

    def close_connection(self):
        """Closes the serial connection."""
        if self.ser:
            self.write_to_device("\n\n")
            self.ser.close()

    def parse_frequency_data(self, sensor_buffer: str) -> None | list[int]:
        """Parses frequency data from the sensor's terminal output.

        Args:
            sensor_buffer (str): Sensor terminal output.

        Returns:
            frequencies [int]: list of frequencies.
        """
        frequency_pattern = re.compile(FREQ_REGEX)  # Info on row 04
        matches = frequency_pattern.findall(sensor_buffer)
        if not matches:
            return None

        frequencies = [int(num) for num in matches[0].split()]
        return frequencies

    def parse_can_configs(self, sensor_buffer: str) -> None | list[str, int, str]:
        """Parses can mode, node ID and baudrate from the sensor's terminal output.

        Args:
            sensor_buffer (str): Sensor terminal output.

        Returns:
            list(str, int, str): [can_mode, node_id, baudrate]
        """
        can_mode_pattern = re.compile(CAN_MODE_REGEX)  # Info on row 04
        node_id_pattern = re.compile(CAN_NODE_ID_REGEX)
        baudrate_pattern = re.compile(CAN_BAUDRATE_REGEX)

        # Extract the can mode, node ID and baudrate from sensor_buffer
        can_mode_match = can_mode_pattern.search(sensor_buffer)
        node_id_match = node_id_pattern.search(sensor_buffer)
        baudrate_match = baudrate_pattern.search(sensor_buffer)
        if not node_id_match or not baudrate_match or not can_mode_match:
            return None

        # Clean and return the extracted values
        can_mode = can_mode_match.group(1).strip()
        node_id = int(node_id_match.group(1).strip())
        baudrate = baudrate_match.group(1).strip()

        return [can_mode, node_id, baudrate]

    def parse_calibration_configs(self, sensor_buffer: str) -> None | list[int]:
        """Parses gain_1, gain_2, and threshold from the calibration
            config terminal output.

        Args:
            sensor_buffer (str): Sensor terminal output.

        Returns:
            list (int): [gain_1, gain_2, threshold]
        """
        gain_1_pattern = re.compile(GAIN1_REGEX)  # Info on row 07
        gain_2_pattern = re.compile(GAIN2_REGEX)  # Info on row 08
        threshold_pattern = re.compile(GAIN_THRESHOLD_REGEX)  # Info on row 09

        # Extract the gain_1, gain_2, and threshold from the sensor_buffer
        gain_1_match = gain_1_pattern.search(sensor_buffer)
        gain_2_match = gain_2_pattern.search(sensor_buffer)
        threshold_match = threshold_pattern.search(sensor_buffer)
        if not gain_1_match or not gain_2_match or not threshold_match:
            return None

        # Clean and return the extracted values
        gain_1 = int(gain_1_match.group(1).strip())
        gain_2 = int(gain_2_match.group(1).strip())
        threshold = int(threshold_match.group(1).strip())
        return (gain_1, gain_2, threshold)

    def configure_frequencies(self) -> bool:
        """Configures sensor frequencies.

        Returns:
            bool: True if configuration is successful, False otherwise.
        """
        self.write_to_device("1")  # Command to navigate to frequency config

        if not self.check_for_page("Frequency Config"):
            questionary.print(
                " - Could not access frequency config page.", style="bold fg:ansired"
            )
            return False

        for i, freq in enumerate(FREQUENCIES):
            self.write_to_device(f"{i + 1}")  # Select frequency slot
            self.write_to_device(f"{freq}\n")  # Set frequency value
        self.ser.reset_input_buffer()

        # Verify frequency configuration
        raw_buffer = self.read_from_sensor()
        configured_frequencies = self.parse_frequency_data(raw_buffer)
        if configured_frequencies != FREQUENCIES:
            questionary.print(
                " - Frequency configuration mismatch.", style="bold fg:ansired"
            )
            return False
        self.write_to_device("\n")  # Exit to main menu
        self.ser.reset_input_buffer()
        return True

    def configure_can_bus(self) -> bool:
        """Configures the Can Mode, CAN-Bus Node ID and Baud Rate.

        Returns:
            bool: True if configuration is successful, False otherwise.
        """
        self.write_to_device("5")  # Navigate to CAN configuration page

        if not self.check_for_page("CAN Config"):
            questionary.print(
                " - Could not access CAN configuration page.", style="bold fg:ansired"
            )
            return False

        # Set CAN Mode
        self.write_to_device("1")  # Select Mode configuration
        self.write_to_device("1")  # Set the mode to -> 1. CAN, 2. CANOpen

        # Set CAN Node ID
        self.write_to_device("2")  # Select Node ID configuration
        self.write_to_device(f"{self.node_id}\n")  # Set the Node ID

        # Set CAN Bus Rate
        self.write_to_device("3")
        self.write_to_device("2")
        self.ser.reset_input_buffer()

        # Validating Settings...
        raw_buffer = self.read_from_sensor()
        configured_can = self.parse_can_configs(raw_buffer)
        if configured_can is None:
            questionary.print(" - Failed to parse CAN config.", style="bold fg:ansired")
            return False

        expected_config = [CAN_MODE, self.node_id, CAN_BUS_RATE]
        if configured_can != expected_config:
            questionary.print(" - CAN configuration mismatch.", style="bold fg:ansired")
            questionary.print(
                f" - Expected Config: {expected_config}", style="bold fg:ansired"
            )
            questionary.print(
                f" - Configured Config: {configured_can}", style="bold fg:ansired"
            )
            return False

        self.write_to_device("\n")  # Exit to main menu
        self.ser.reset_input_buffer()
        return True

    def configure_calibration(self) -> bool:
        """Configures sensor calibration parameters.

        Returns:
            bool: True if configuration is successful, False otherwise.
        """
        self.write_to_device("2")  # Navigate to Calibration config page

        if not self.check_for_page("Calibration Config"):
            questionary.print(
                " - Could not access Calibration configuration page.",
                style="bold fg:ansired",
            )
            return False

        # Set Gain 1, Gain 2, and Threshold
        self._set_calibration_param(1, GAIN1)
        self._set_calibration_param(2, GAIN2)
        self._set_calibration_param(3, GAIN_THRESHOLD)

        self.write_to_device("s")  # save gains
        self.ser.reset_input_buffer()

        # Validating Settings...
        raw_buffer = self.read_from_sensor()
        configured_calib = self.parse_calibration_configs(raw_buffer)
        if configured_calib is None:
            questionary.print(
                " - Failed to parse Calibration config.", style="bold fg:ansired"
            )
            return False

        expected_calib_config = [GAIN1, GAIN2, GAIN_THRESHOLD]
        if configured_calib != tuple(expected_calib_config):
            questionary.print(
                " - Calibration configuration mismatch.", style="bold fg:ansired"
            )
            questionary.print(
                f" - Expected Config: {expected_calib_config}",
                style="bold fg:ansired",
            )
            questionary.print(
                f" - Configured Config: {configured_calib}", style="bold fg:ansired"
            )
            return False

        self.write_to_device("\n")  # Exit to main menu
        self.ser.reset_input_buffer()
        return True

    def configure_sensor(self):
        """Main method to configure the VNA sensor."""
        try:
            self.connect()

            if not self.configure_frequencies():
                questionary.print(
                    " - Failed to configure frequencies.", style="bold fg:ansired"
                )
                return

            questionary.print(
                " - Frequencies configured successfully.", style="bold fg:ansigreen"
            )

            if not self.configure_can_bus():
                questionary.print(
                    " - Failed to configure CAN-Bus settings.",
                    style="bold fg:ansired",
                )
                return

            questionary.print(
                " - CAN-Bus configured successfully.", style="bold fg:ansigreen"
            )

            if not self.configure_calibration():
                questionary.print(
                    " - Failed to configure calibration settings.",
                    style="bold fg:ansired",
                )
                return

            questionary.print(
                " - Calibration configured successfully.", style="bold fg:ansigreen"
            )

            # save configuration
            self.write_to_device("\n")
            questionary.print(
                "\n - Configuration completed successfully.\n",
                style="bold fg:ansigreen",
            )

        except SerialException as e:
            questionary.print(
                f" - Error configuring sensor: {e}", style="bold fg:ansired"
            )
        except KeyboardInterrupt:
            questionary.print(
                " - Configuration interrupted by user.", style="bold fg:ansired"
            )
        finally:
            self.close_connection()


def configure_vna():
    """Configures the VNA sensor."""
    while True:
        choice = questionary.select(
            "Which side of the sensor do you want to configure to?",
            choices=vna_options.VNA_OPTIONS,
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if choice == vna_options.FRONT:
            VNASensorConfigurator(FRONT_NODE_ID).configure_sensor()

        elif choice == vna_options.REAR:
            VNASensorConfigurator(REAR_NODE_ID).configure_sensor()

        elif choice == vna_options.GO_BACK:
            return
        else:
            questionary.print(" - Not yet implemented!", style="bold fg:ansired")
