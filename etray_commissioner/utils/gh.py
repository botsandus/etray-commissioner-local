"""This module provides functions for interacting with Github cli tool"""

import subprocess


def is_gh_installed() -> bool:
    """Checks if the Github cli tool is installed.

    Returns:
        bool: True if gh is installed.
    """
    proc = subprocess.run(
        ["dpkg", "-s", "gh"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def is_user_logged_into_gh() -> bool:
    """Checks if the user is logged into the Github cli tool.

    Raises:
        RuntimeError: Raises an error if gh is not installed.
        RuntimeError: Raises an error if github.com cannot be reached.

    Returns:
        bool: True if the user is logged into gh.
    """
    if not is_gh_installed():
        raise RuntimeError(
            "gh is not installed! Please run the following commands to install it\n\n"
            "\tsudo apt install gh\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    ping_github_proc = subprocess.run(
        ["ping", "-c1", "-w5", "github.com"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if ping_github_proc.returncode != 0:
        raise RuntimeError(
            "Github could not be reached. Do you have a stable internet connection?"
        )

    gh_auth_proc = subprocess.run(
        ["gh", "auth", "status"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return gh_auth_proc.returncode == 0


def get_latest_release(repo: str) -> str:
    """Returns the name of the latest release from the given Github repository.

    Args:
        repo (str): The name of the Github repository.

    Raises:
        RuntimeError: raises an error if gh is not installed.
        RuntimeError: raises an error if the user is not logged into gh.
        RuntimeError: raises an error if the release could not be retrieved.

    Returns:
        str: _description_
    """
    if not is_gh_installed():
        raise RuntimeError(
            "gh is not installed! Please run the following commands to install it\n\n"
            "\tsudo apt install gh\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    if not is_user_logged_into_gh():
        raise RuntimeError(
            "You are not logged into gh! Please run the following commands to login\n\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    proc = subprocess.run(
        ["gh", "release", "view", "--json", "tagName", "-q", ".tagName", "-R", repo],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())

    return proc.stdout.strip()


def download_release(
    repo: str, release_name: str, destination: str, files_to_download: list[str] = None
):
    """Downloads files from a given release in a given Github repository.

    Args:
        repo (str): The name of the repository.
        release_name (str): The name of the release.
        destination (str): Where the files should be saved.
        files_to_download (list[str], optional): If not None, only the
            specified files will be download. Defaults to None.

    Raises:
        RuntimeError: raises an error if gh is not installed.
        RuntimeError: raises an error if the user is not logged into gh.
        RuntimeError: raises an error an error occurred while downloading.
    """
    if not is_gh_installed():
        raise RuntimeError(
            "gh is not installed! Please run the following commands to install it\n\n"
            "\tsudo apt install gh\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    if not is_user_logged_into_gh():
        raise RuntimeError(
            "You are not logged into gh! Please run the following commands to login\n\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    args = ["gh", "release", "download", "-R", repo, release_name, "-D", destination]
    if files_to_download is not None:
        for file in files_to_download:
            args += ["-p", file]

    proc = subprocess.run(
        args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())


def download_repo(repo: str, destination: str):
    """Downloads the latest version of a given Github repository.

    Args:
        repo (str): The name of the repository.
        destination (str): Where the files should be saved.

    Raises:
        RuntimeError: raises an error if gh is not installed.
        RuntimeError: raises an error if the user is not logged into gh.
        RuntimeError: raises an error an error occurred while downloading.
    """
    if not is_gh_installed():
        raise RuntimeError(
            "gh is not installed! Please run the following commands to install it\n\n"
            "\tsudo apt install gh\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    if not is_user_logged_into_gh():
        raise RuntimeError(
            "You are not logged into gh! Please run the following commands to login\n\n"
            "\tgh auth login --web\n"
            "\tgh auth setup-git\n\n"
        )

    proc = subprocess.run(
        ["gh", "repo", "clone", repo, destination],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
