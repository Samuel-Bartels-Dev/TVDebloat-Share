from __future__ import annotations

from pathlib import Path

from .adb import Client
from .profile import load as load_profile


def inspect(client: Client, profile_path: str | Path) -> dict:
    profile = load_profile(profile_path)
    installed = set(client.packages())
    disabled = set(client.packages(disabled=True))
    enabled_again = [
        package for package in profile.disable
        if package in installed and package not in disabled
    ]
    missing = [package for package in profile.disable if package not in installed]
    return {
        "profile": profile.name,
        "enabled_again": enabled_again,
        "no_longer_installed": missing,
        "in_sync": not enabled_again,
    }
