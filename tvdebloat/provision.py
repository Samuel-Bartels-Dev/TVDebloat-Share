from __future__ import annotations

from pathlib import Path
from .adb import Client
from .engine import apply, preview
from .preflight import run as preflight
from .verify import run as verify


def run(client: Client, profile_path: str | Path, apply_changes: bool = False) -> dict:
    checks = preflight(client, profile_path)
    if not checks["ready"]:
        return {"mode": "blocked", "preflight": checks}

    plan = preview(client, profile_path)
    result = {"mode": "apply" if apply_changes else "preview", "preflight": checks, "preview": plan}
    if not apply_changes:
        result["next_step"] = "Review the preview and rerun with --apply only after approval."
        return result

    result["apply"] = apply(client, profile_path)
    result["verify"] = verify(client)
    return result
