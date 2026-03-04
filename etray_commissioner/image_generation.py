#!/usr/bin/env python3
"""Module to generate images for the Base NUC, workers, and screen UI."""

import os
import re

import questionary
from appdirs import AppDirs
from prompt_toolkit.styles import Style

import etray_commissioner.options.image_generation as image_generation_options
import etray_commissioner.options.workers as workers_options
from etray_commissioner.utils.git_fetch_repo import download_repo

ROBOT_REGEX = r"arri-[1-9]\d*$"
WORKERS_IDX_REGEX = r"^[1-9]|10$"
SCANNING_FACE_REGEX = r"SF[A-Z][0-9]\d*$"

QUESTIONARY_STYLE = Style(
    [("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")]
)

MODULE_NAME = "etray-commissioner"
DATA_DIR = AppDirs(MODULE_NAME).user_data_dir
REPO_NAME = "arri-os-images"
REPO_DIR = os.path.join(DATA_DIR, REPO_NAME)


def configure():
    """Toggles a list of image generation options."""

    while True:
        choice = questionary.select(
            "What parts would you like to commission?",
            choices=image_generation_options.IMAGE_GENERATION_OPTIONS,
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if choice == image_generation_options.NUC:
            generate_image()

        elif choice == image_generation_options.WORKERS:
            configure_workers()

        elif choice == image_generation_options.SCREEN_UI:
            generate_image(base=False)

        elif choice == image_generation_options.GO_BACK:
            break

        else:
            questionary.print("   - Not yet implemented!", style="bold fg:ansired")


def configure_workers():
    """Configures the menu for generating images for the workers."""

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=workers_options.WORKER_OPTIONS,
            style=QUESTIONARY_STYLE,
            qmark=">>",
        ).unsafe_ask()

        if choice == workers_options.INDIVIDUAL:
            worker_idx = questionary.text(
                "Which worker would you like to configure?",
                validate=lambda worker_idx: (
                    True
                    if re.search(WORKERS_IDX_REGEX, worker_idx)
                    else "Please enter a valid worker index e.g. from 1 to 10"
                ),
                qmark=">>",
            ).unsafe_ask()
            gen_worker_image([worker_idx])

        elif choice == workers_options.ALL_WORKERS:
            num_of_workers = questionary.text(
                "How many workers would you like to configure?",
                validate=lambda num_of_workers: (
                    True
                    if re.search(WORKERS_IDX_REGEX, num_of_workers)
                    else "Please enter a valid number of workers e.g. from 1 to 10"
                ),
                qmark=">>",
            ).unsafe_ask()
            gen_worker_image([str(i) for i in range(1, int(num_of_workers) + 1)])

        elif choice == workers_options.GO_BACK:
            break
        else:
            questionary.print("   - Not yet implemented!", style="bold fg:ansired")


def gen_worker_image(worker_list: list):
    """Generates the image for the workers.

    Args:
        worker_list (list): List of workers to generate images for.
    """

    # makes sure that the repo is up to date
    download_repo(REPO_NAME)

    questionary.print(
        "\n - The created image would appear here: ",
        style="bold ansiwhite",
    )
    questionary.print(
        f"    - {REPO_DIR}/worker/build/\n\n",
        style="bold ansiyellow",
    )
    for worker_idx in worker_list:
        os.system(f"cd {REPO_DIR}/worker && ./generate_images.sh {worker_idx}")


def generate_image(base=True):
    """Generates the image for the Base NUC or the Screen UI.

    Args:
        base (bool, optional): Flag to determine if the image is for the Base NUC.
            Defaults to True.
    """
    # makes sure that the repo is up to date
    download_repo(REPO_NAME)

    questionary.print(
        "\n - The created image would appear here: ",
        style="bold ansiwhite",
    )
    if base:
        questionary.print(
            f"    - {REPO_DIR}/base/output/\n\n",
            style="bold ansiyellow",
        )

        os.system(f"cd {REPO_DIR}/base && ./generate_image.sh")
    else:
        questionary.print(
            f"    - {REPO_DIR}/ui/output/\n\n",
            style="bold ansiyellow",
        )

        os.system(f"cd {REPO_DIR}/ui && ./generate_image.sh")
