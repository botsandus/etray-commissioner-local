#!/usr/bin/env python3
"""Module to flash the Teltonika."""

import os

import questionary
from appdirs import AppDirs

from parts_commissioner.options import cli as cli_options

# from parts_commissioner.utils import gh
from parts_commissioner.utils.fetch_cli import (
    LATEST_VERSION,
    are_cli_installed,
    download_latest,
    update_cli,
)

DATA_DIR = AppDirs("parts-commissioner").user_data_dir
REPO_NAME = "botsandus/cli"


def flash():
    """Flashes the Teltonika router."""
    from parts_commissioner.main import QUESTIONARY_STYLE

    if not are_cli_installed():
        questionary.print(
            "The cli repo is not installed on this device. "
            "Attempting to install them...",
            style="ansiyellow",
        )
        if not download_latest():
            questionary.print(
                "Could not download the latest version of the cli repo!",
            )
            return

        # target_release = gh.get_latest_release(REPO_NAME)
        target_release = LATEST_VERSION

    else:
        target_release = update_cli()

    questionary.print(
        f" - CLI version: {target_release}\n",
        style="ansicyan",
    )

    choice = questionary.select(
        "Select an option:",
        choices=cli_options.CLI_OPTIONS,
        qmark=">>",
        style=QUESTIONARY_STYLE,
    ).unsafe_ask()

    if choice == cli_options.CANCEL:
        questionary.print("Operation cancelled.", style="ansired")
        return
    elif choice == cli_options.NEW_ROUTER:
        script_name = "new_router.sh"
    elif choice == cli_options.UPGRADE_ROUTER:
        script_name = "upgrade_router.sh"
    elif choice == cli_options.VALIDATE_ROUTER:
        script_name = "validate_router.sh"
    elif choice == cli_options.FIX_ROUTER:
        script_name = "validate_router.sh"
    else:
        questionary.print("Invalid option selected.", style="ansired")
        return

    cli_path = os.path.join(DATA_DIR, "cli", target_release)

    zip_file_name = f"runner-scripts-{LATEST_VERSION}.tar.gz"

    # run the script
    scripts_path = os.path.join(cli_path, "scripts")
    if os.path.exists(scripts_path):
        os.system(f"rm -r {scripts_path}")

    script_args = " --fix" if choice == cli_options.FIX_ROUTER else ""
    os.system(
        f"cd {cli_path} && mkdir scripts && "
        f"tar -xvzf {zip_file_name} -C scripts && "
        f"cd scripts && chmod +x {script_name} && "
        f"LOG_LEVEL=debug ./{script_name}{script_args}"
    )
