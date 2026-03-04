"""The module contains copies the latest version of the firmware-unified-psu repo."""

import glob
import os
import shutil
from typing import Optional

import questionary
from appdirs import AppDirs

from etray_commissioner.utils import gh

DATA_DIR = AppDirs("etray-commissioner").user_data_dir
REPO_DIR = os.path.join(DATA_DIR, "firmware-unified-psu")
REPO_NAME = "botsandus/firmware-unified-psu"


def get_current_version() -> Optional[str]:
    """Retrieves the version of the repo that is currently installed on the device.

    Raises:
        FileNotFoundError: if the data directory does not exist
        RuntimeError: if the repo directory contains more than 1 file/directory
        RuntimeError: if the repo directory contains a file instead of a
            directory

    Returns:
        Optional[str]: Returns the current version or None if it could not be retrieved.
    """
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(
            "The data directory for etray-commissioner "
            f"has not been created: {DATA_DIR}"
        )

    if not os.path.exists(REPO_DIR):
        return None

    dirs = os.listdir(REPO_DIR)
    number_of_dirs = len(dirs)
    if number_of_dirs == 0:
        return None

    if number_of_dirs > 1:
        raise RuntimeError(
            f"The directory ({REPO_DIR}) contains "
            "several folders/files. "
            "Please delete all the files/folders in this directory "
            "and rerun etray-commissioner "
            "to download the latest version of the repo."
        )

    path_to_dir = os.path.join(REPO_DIR, dirs[0])
    if not os.path.isdir(path_to_dir):
        raise RuntimeError(
            f"The directory ({REPO_DIR}) contains "
            "a file instead of a directory. "
            "Please delete the file in this directory "
            "and rerun etray-commissioner to download the "
            "latest version of the repo."
        )

    # The name of the directory corresponds to the version number
    return dirs[0]


def is_repo_installed() -> bool:
    """Checks if the repo are installed

    Returns:
        bool: True if they are installed, false otherwise.
    """
    return get_current_version() is not None


def download_latest() -> bool:
    """Downloads and unpacks the latest release of the repo from Github.

    Returns:
        bool: True if the release has been downloaded successfully. False otherwise.
    """
    try:
        if not os.path.isdir(DATA_DIR):
            questionary.print(
                " - The data directory for etray-commissioner does not exist. "
                "Please create the directory and rerun the command.",
                style="fg:ansired",
            )
            return False
        questionary.print(" - Fetching the latest release...", style="fg:ansiyellow")
        # latest_version = gh.get_latest_release(REPO_NAME)
        latest_version = "v1.0.7"
        questionary.print(
            f" - Downloading {latest_version} of the repo...",
            style="fg:ansiyellow",
        )
        gh.download_release(
            REPO_NAME,
            latest_version,
            DATA_DIR,
            ["*PRODUCTION.hex"],
        )
    except RuntimeError as e:
        questionary.print(
            f" - Could not download the latest version: {e}", style="fg:ansired"
        )
        return False

    # Find the latest archive file matching the pattern
    archive_pattern = os.path.join(DATA_DIR, "*PRODUCTION.hex")
    archive_files = glob.glob(archive_pattern)

    if not archive_files:
        raise FileNotFoundError(f" - No files matching the pattern {archive_pattern}")

    archive_path = archive_files[0]
    unpack_dest = os.path.join(DATA_DIR, f"{REPO_NAME.split('/')[1]}", latest_version)
    os.makedirs(unpack_dest, exist_ok=True)

    # move the archive to the destination
    shutil.move(archive_path, unpack_dest)

    questionary.print(" - Download successful!", style="fg:ansigreen")
    return True


def update_repo() -> Optional[str]:
    """Checks for and performs updates after asking for the user's permission.

    Returns:
        Optional[str]: The version of the repo that is currently installed.
    """
    questionary.print("\n - Checking for updates...", style="fg:ansiyellow")
    try:
        current_version = get_current_version()
    except RuntimeError:
        questionary.print(
            " - Could not retrieve the current version of the repo!",
            style="fg:ansired",
        )
        return

    try:
        # latest_version = gh.get_latest_release(REPO_NAME)
        latest_version = "v1.0.7"
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

    if current_version != latest_version:
        update = questionary.confirm(
            f" - You currently have {current_version}. "
            f"The latest version is {latest_version}. "
            "Would you like to update to the latest version?"
        ).unsafe_ask()
        if update:
            if download_latest():
                questionary.print(
                    " - Deleting the old version...", style="fg:ansiyellow"
                )
                path_to_old_ver = os.path.join(REPO_DIR, current_version)
                shutil.rmtree(path_to_old_ver)
                current_version = latest_version
            else:
                questionary.print(
                    " - Could not download the latest version of the repo!",
                    style="fg:ansired",
                )
                questionary.print(
                    " - You can continue using the current version "
                    "but you might be missing critical features/bug fixes.",
                    style="fg:ansiyellow",
                )
        else:
            questionary.print(
                " - You can continue using the current version "
                "but you might be missing critical features/bug fixes.",
                style="fg:ansiyellow",
            )
    else:
        questionary.print(
            " - You already have the latest version of the repo.\n",
            style="fg:ansigreen",
        )

    return current_version
