from __future__ import annotations

from .adb import Client
from .facts import read as read_facts


def run(client: Client) -> dict:
    facts = read_facts(client)
    installed = client.packages()
    disabled = client.packages(disabled=True)
    return {
        "reachable": True,
        "device": facts.as_dict(),
        "installed_count": len(installed),
        "disabled_count": len(disabled),
        "physical_checks_required": [
            "Home",
            "HDMI/input switching",
            "remote",
            "Settings",
            "network",
            "Bluetooth if required",
            "required office apps",
            "sleep/wake",
            "reboot",
        ],
    }
