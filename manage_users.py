#!/usr/bin/env python3
"""Script to add users and set their passwords for parts-commissioner.

Usage:
    python manage_users.py
"""

import sys

import questionary
from prompt_toolkit.styles import Style

from parts_commissioner.utils.auth import add_user

STYLE = Style([("pointer", "bold fg:ansiblue"), ("highlighted", "bold fg:ansigreen")])


def main():
    questionary.print("\nParts Commissioner — Add User\n", style="bold fg:ansigreen")

    name = questionary.text("Username:", qmark=">>", style=STYLE).unsafe_ask().strip()
    if not name:
        questionary.print("   Name cannot be empty.", style="bold fg:ansired")
        sys.exit(1)

    role = questionary.select(
        "Role:", choices=["user", "admin"], style=STYLE, qmark=">>"
    ).unsafe_ask()

    password = questionary.password("Password:", qmark=">>", style=STYLE).unsafe_ask()

    confirm = questionary.password(
        "Confirm password:", qmark=">>", style=STYLE
    ).unsafe_ask()

    if password != confirm:
        questionary.print("   Passwords do not match.", style="bold fg:ansired")
        sys.exit(1)

    add_user(name, role, password)
    questionary.print(
        f"   User '{name}' ({role}) saved successfully.", style="bold fg:ansigreen"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        questionary.print("\n   Interrupted.", style="bold fg:ansired")
        sys.exit()
