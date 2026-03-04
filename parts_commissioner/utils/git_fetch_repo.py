"""The module contains copies the latest version of auto_tower repo."""

import os
import subprocess
import sys

import questionary
from appdirs import AppDirs
from rich.console import Console

from parts_commissioner.utils import gh

MODULE_NAME = "parts-commissioner"
DATA_DIR = AppDirs(MODULE_NAME).user_data_dir


def download_repo(repo_name: str):
    """Downloads the latest version of the repo.

    Args:
        repo_name (str): The name of the repository to download.

    Raises:
        RuntimeError: If the data directory does not exist.
    """
    if not os.path.exists(DATA_DIR):
        raise RuntimeError(f"The {DATA_DIR} directory does not exist. ")

    repo_dir = os.path.join(DATA_DIR, repo_name)

    if os.path.exists(repo_dir):
        check_and_pull_changes(repo_name)

    else:
        with Console().status(
            "[bold cyan] Downloading the repository...", spinner="dots"
        ):
            gh.download_repo(f"botsandus/{repo_name}", repo_dir)


def run_terminal_cmd(command, repo_name: str):
    """Run a terminal command and return the output.
    Args:
        command (list): The command to run.
        repo_name (str): The name of the repository.

    Returns:
        str: The output of the command.
    """
    repo_dir = os.path.join(DATA_DIR, repo_name)

    result = subprocess.run(
        command,
        text=True,
        check=False,
        capture_output=True,
        cwd=repo_dir,
    )

    if result.returncode != 0:
        questionary.print(f"Error: {result.stderr.strip()}", style="bold ansired")
        sys.exit(1)

    return result.stdout.strip()


def check_and_pull_changes(repo_name: str):
    """Check if the local repository is up to date with the remote.

    Args:
        repo_name (str): The name of the repository.
    """
    try:
        # Fetch the latest changes from the remote
        questionary.print(" - Fetching latest changes...", style="bold ansicyan")
        run_terminal_cmd(["git", "fetch", "origin"], repo_name)

        # Determine branch and upstream info
        branch = run_terminal_cmd(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_name
        )
        upstream = f"origin/{branch}"

        # Get commit hashes for comparison
        local_commit = run_terminal_cmd(["git", "rev-parse", "HEAD"], repo_name)
        remote_commit = run_terminal_cmd(["git", "rev-parse", upstream], repo_name)

        # Check if the local repository is up to date with the remote
        if local_commit == remote_commit:
            questionary.print(
                " - The repository is up to date.\n", style="bold ansicyan"
            )
        else:
            questionary.print(
                " - The repository is not up to date.", style="bold ansicyan"
            )
            questionary.print(" - Pulling latest changes...", style="bold ansicyan")
            run_terminal_cmd(["git", "pull", "origin", branch], repo_name)

    except subprocess.CalledProcessError as e:
        questionary.print(f"Error: {e.stderr.strip()}", style="bold ansired")
