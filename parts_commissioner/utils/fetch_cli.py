"""The module contains copies the latest version of the cli repo."""

import glob
import os
import shutil
from typing import Optional

import questionary
from appdirs import AppDirs

from parts_commissioner.utils import gh

DATA_DIR = AppDirs("parts-commissioner").user_data_dir
CLI_DIR = os.path.join(DATA_DIR, "cli")
REPO_NAME = "botsandus/cli"
LATEST_VERSION = "v2.0.0"


def get_current_version() -> Optional[str]:
    """Retrieves the version of cli that is currently installed on the device.

    Raises:
        FileNotFoundError: if the data directory does not exist
        RuntimeError: if the cli directory contains more than 1 file/directory
        RuntimeError: if the cli directory contains a file instead of a
            directory

    Returns:
        Optional[str]: Returns the current version or None if it could not be retrieved.
    """
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(
            "The data directory for parts-commissioner "
            f"has not been created: {DATA_DIR}"
        )

    print(CLI_DIR)
    if not os.path.exists(CLI_DIR):
        return None

    dirs = os.listdir(CLI_DIR)
    number_of_dirs = len(dirs)
    if number_of_dirs == 0:
        return None

    if number_of_dirs > 1:
        raise RuntimeError(
            f"The cli directory ({CLI_DIR}) contains "
            "several folders/files. "
            "Please delete all the files/folders in this directory "
            "and rerun parts-commissioner "
            "to download the latest version of the cli."
        )

    path_to_dir = os.path.join(CLI_DIR, dirs[0])
    if not os.path.isdir(path_to_dir):
        raise RuntimeError(
            f"The cli directory ({CLI_DIR}) contains "
            "a file instead of a directory. "
            "Please delete the file in this directory "
            "and rerun parts-commissioner to download the "
            "latest version of the cli."
        )

    # The name of the directory corresponds to the version number
    return dirs[0]


def are_cli_installed() -> bool:
    """Checks if the cli are installed

    Returns:
        bool: True if they are installed, false otherwise.
    """
    return get_current_version() is not None


def download_latest() -> bool:
    """Downloads and unpacks the latest release of the cli from Github.

    Returns:
        bool: True if the release has been downloaded successfully. False otherwise.
    """
    try:
        if not os.path.isdir(DATA_DIR):
            questionary.print(
                " - The data directory for parts-commissioner does not exist. "
                "Please create the directory and rerun the command.",
                style="fg:ansired",
            )
            return False
        questionary.print(" - Fetching the latest release...", style="fg:ansiyellow")
        # LATEST_VERSION = gh.get_latest_release(REPO_NAME)
        questionary.print(
            f" - Downloading {LATEST_VERSION} of the cli...",
            style="fg:ansiyellow",
        )
        gh.download_release(
            REPO_NAME,
            LATEST_VERSION,
            DATA_DIR,
            [f"runner-scripts-{LATEST_VERSION}.tar.gz"],
        )
    except RuntimeError as e:
        questionary.print(
            f" - Could not download the latest version: {e}", style="fg:ansired"
        )
        return False

    # Find all downloaded files and move them to the destination
    files_to_archive = [f"runner-scripts-{LATEST_VERSION}.tar.gz"]
    unpack_dest = os.path.join(DATA_DIR, "cli", LATEST_VERSION)
    os.makedirs(unpack_dest, exist_ok=True)

    # Use glob to find all downloaded files
    downloaded_files = glob.glob(os.path.join(DATA_DIR, "*"))
    downloaded_filenames = [os.path.basename(f) for f in downloaded_files]

    # Check if all required files are present
    missing_files = [f for f in files_to_archive if f not in downloaded_filenames]
    if missing_files:
        raise FileNotFoundError(f" - Missing files: {', '.join(missing_files)}")

    # Move files to destination
    for file_name in files_to_archive:
        archive_path = os.path.join(DATA_DIR, file_name)
        shutil.move(archive_path, unpack_dest)

    questionary.print(" - Download successful!", style="fg:ansigreen")
    return True


def update_cli() -> Optional[str]:
    """Checks for and performs updates after asking for the user's permission.

    Returns:
        Optional[str]: The version of the cli that is currently installed.
    """
    questionary.print("\n - Checking for cli updates...", style="fg:ansiyellow")
    try:
        current_version = get_current_version()
    except RuntimeError:
        questionary.print(
            " - Could not retrieve the current version of the cli!",
            style="fg:ansired",
        )
        return

    try:
        # LATEST_VERSION = gh.get_latest_release(REPO_NAME)
        pass
    except RuntimeError as e:
        questionary.print(
            f" - Could not fetch the latest version: {e}", style="fg:ansired"
        )
        questionary.print(
            f" - You can continue to use the current version ({current_version}), "
            "but it is not guaranteed to be the latest.\n",
            style="fg:ansiyellow",
        )
        return current_version

    if current_version != LATEST_VERSION:
        if download_latest():
            questionary.print(" - Deleting the old version...", style="fg:ansiyellow")
            path_to_old_ver = os.path.join(CLI_DIR, current_version)
            shutil.rmtree(path_to_old_ver)
            current_version = LATEST_VERSION
        else:
            questionary.print(
                " - Could not download the latest version of the cli!",
                style="fg:ansired",
            )
            questionary.print(
                " - You can continue using the current version "
                "but you might be missing critical features/bug fixes.",
                style="fg:ansiyellow",
            )
    else:
        questionary.print(
            " - You already have the latest version of the cli.\n",
            style="fg:ansigreen",
        )

    return current_version
