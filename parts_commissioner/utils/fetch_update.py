"""This module checks for updates to the target tool."""

from importlib.metadata import version

import questionary

from parts_commissioner.utils import gh


def check(module_name: str):
    """Checks if the current version of the module is up to date.

    Update checks are skipped silently when gh is not installed or the user
    is not authenticated. Only authenticated users (admins) see update prompts.
    """
    if not gh.is_gh_installed():
        return

    try:
        if not gh.is_user_logged_into_gh():
            return
    except RuntimeError:
        return

    questionary.print("\nChecking for updates...\n", style="fg:ansiyellow")

    current_version = version(module_name)

    try:
        latest_version = gh.get_latest_release(f"botsandus/{module_name}")[1:]
    except RuntimeError as e:
        questionary.print(
            f"Could not fetch the latest version: {e}", style="fg:ansired"
        )
        questionary.print(
            f"You can continue to use the current version ({current_version}), "
            "but it is not guaranteed to be the latest.\n",
            style="fg:ansiyellow",
        )
        return

    if current_version == latest_version:
        questionary.print(
            f"You are running the latest version of {module_name}: {current_version}\n",
            style="fg:ansigreen",
        )
    else:
        questionary.print(
            f"You are running {current_version}. "
            f"The latest version is {latest_version}. "
            "Please update by running: ",
            end="",
            style="fg:ansired",
        )
        questionary.print(f"\n - pipx upgrade {module_name}", style="bold fg:ansired")
        questionary.print(
            "You can continue to use the current version, "
            "but you may be missing critical features "
            "and/or bug fixes!\n",
            style="fg:ansiyellow",
        )
