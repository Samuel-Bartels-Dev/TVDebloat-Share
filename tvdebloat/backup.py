from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from .adb import Client
from .facts import read as read_facts
from .state import root


def capture(client: Client, profile_name: str) -> Path:
    payload = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "target": client.target.serial,
        "profile": profile_name,
        "device": read_facts(client).as_dict(),
        "packages": client.packages(),
        "disabled_packages": client.packages(disabled=True),
        "settings_global": client.shell("settings list global"),
        "settings_secure": client.shell("settings list secure"),
        "settings_system": client.shell("settings list system"),
    }
    folder = root() / "backups"
    folder.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in client.target.serial)
    path = folder / f"{safe}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
