from __future__ import annotations

from .adb import Client
from .facts import read as read_facts


def inventory(client: Client) -> dict:
    installed = client.packages()
    disabled = client.packages(disabled=True)
    return {
        "device": read_facts(client).as_dict(),
        "installed_count": len(installed),
        "disabled_count": len(disabled),
        "installed": installed,
        "disabled": disabled,
    }
