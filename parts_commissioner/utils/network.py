import subprocess
import time

import nmcli

connection_name = "Parts commissioner"


def configure_connection(ip_address: str) -> None:
    """Modify and activate a network connection using nmcli.

    If the specified connection does not exist, a new one is created.

    Args:
        ip_address (str): The IP address to set for the connection.

    Raises:
        nmcli._exception.NmcliException: If there is an error with nmcli operations.
    """
    try:
        nmcli.connection.modify(
            connection_name,
            {
                "ipv4.addresses": f"{ip_address}/24",
                "ipv4.method": "manual",
            },
        )
        # Bring the connection up
        nmcli.connection.up(connection_name)

    except nmcli._exception.NotExistException:
        # Create a new connection if it does not exist
        nmcli.connection.add(
            conn_type="ethernet",
            name=connection_name,
            autoconnect=True,
            ifname="*",  # Applies to all interfaces
            options={
                "ipv4.addresses": f"{ip_address}/24",
                "ipv4.method": "manual",
            },
        )
        nmcli.connection.up(connection_name)
        time.sleep(5)


def turn_off_connection() -> None:
    """Deactivate a network connection using nmcli.

    Deactivates the network connection with the globally defined connection name.

    Raises:
        nmcli._exception.NmcliException: If there is an error during deactivation.
    """
    nmcli.connection.down(connection_name)


def ping_device(ip: str) -> bool:
    """Ping a device to check if it is reachable.

    Uses the system's `ping` command to send an ICMP echo request.

    Args:
        ip (str): The IP address of the device to ping.

    Returns:
        bool: True if the device is reachable, False otherwise.
    """
    try:
        # Use the `ping` command with 1 packet and a timeout of 1 second
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception as e:
        print(f" - Error during ping: {e}")
        return False


def increment_ip(ip_address: str) -> str:
    """Increment the last octet of an IP address by 10.

    If the IP address is in the 172.16.0.x range, it is set to 172.16.0.2.
    If the last octet exceeds 255, it wraps around to 0.

    Args:
        ip_address (str): The IP address to be incremented.

    Returns:
        str: The updated IP address.

    Raises:
        ValueError: If the provided IP address is None.
    """
    if ip_address is None:
        raise ValueError("IP address cannot be None")

    parts = list(map(int, ip_address.split(".")))

    # Check if the IP is in the 172.16.0.x range
    if parts[0] == 172 and parts[1] == 16 and parts[2] == 0:
        return "172.16.0.2"

    parts[-1] += 10

    if parts[-1] > 255:
        parts[-1] = 0  # Reset to 0 if it exceeds 255

    return ".".join(map(str, parts))
