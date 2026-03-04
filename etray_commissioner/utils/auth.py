"""Authentication utility for etray-commissioner."""

import hashlib
import json
import os

USERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "users.json"
)


def _hash_password(salt: str, password: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()


def authenticate(password: str) -> dict | None:
    """Checks the password against the users database.

    Args:
        password (str): The password to check.

    Returns:
        dict | None: The user dict (name, role) if matched, None otherwise.
    """
    with open(USERS_FILE) as f:
        data = json.load(f)

    for user in data["users"]:
        if _hash_password(user["salt"], password) == user["password_hash"]:
            return {"name": user["name"], "role": user["role"]}

    return None


def add_user(name: str, role: str, password: str):
    """Adds or updates a user in the users database.

    Args:
        name (str): The user's name.
        role (str): Either 'admin' or 'user'.
        password (str): The plaintext password to hash and store.
    """
    import os as _os

    salt = _os.urandom(16).hex()
    password_hash = _hash_password(salt, password)

    with open(USERS_FILE) as f:
        data = json.load(f)

    # Replace existing user with same name, or append
    for user in data["users"]:
        if user["name"] == name:
            user["role"] = role
            user["salt"] = salt
            user["password_hash"] = password_hash
            break
    else:
        data["users"].append(
            {"name": name, "role": role, "salt": salt, "password_hash": password_hash}
        )

    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)
