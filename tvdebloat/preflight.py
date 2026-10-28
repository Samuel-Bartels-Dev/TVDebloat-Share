from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
import sys

from .adb import Client
from .facts import read as read_facts
from .match import compare
from .profile import ProfileError, load as load_profile


@dataclass(frozen=True)
class Check:
    id: str
    status: str
    summary: str
    detail: str = ""
    remediation: str = ""


def run(client: Client | None = None, profile_path: str | Path | None = None) -> dict:
    checks: list[Check] = []

    checks.append(
        Check("python", "ok" if sys.version_info >= (3, 11) else "fail",
              f"Python {sys.version.split()[0]}",
              remediation="Install Python 3.11 or newer.")
    )

    adb = shutil.which("adb")
    checks.append(
        Check("adb", "ok" if adb else "fail",
              "ADB executable found" if adb else "ADB executable not found",
              detail=adb or "",
              remediation="" if adb else "Install Android platform-tools or set ADB=/path/to/adb.")
    )

    profile = None
    if profile_path:
        try:
            profile = load_profile(profile_path)
            checks.append(Check("profile", "ok", "Profile parsed", str(profile.path)))
        except ProfileError as exc:
            checks.append(Check("profile", "fail", "Profile invalid", str(exc),
                                "Fix the profile before using it on a TV."))

    if client is not None:
        try:
            facts = read_facts(client)
            checks.append(Check("device", "ok", "TV responded to ADB",
                                f"{facts.manufacturer} {facts.model}; Android {facts.android}; SDK {facts.sdk}"))
            if not facts.home:
                checks.append(Check("home", "fail", "Current Home could not be resolved",
                                    remediation="Do not debloat until Home state is understood."))
            else:
                checks.append(Check("home", "ok", "Current Home resolved", facts.home))

            if profile is not None:
                match = compare(profile.match, facts)
                status = "fail" if match.level == "mismatch" else ("warn" if match.level == "generic" else "ok")
                checks.append(Check(
                    "profile_match", status, f"Profile match: {match.level}",
                    f"matched={','.join(match.matched) or '-'} mismatched={','.join(match.mismatched) or '-'}",
                    "Choose a matching profile or build a new device profile." if status == "fail" else "",
                ))
        except Exception as exc:
            checks.append(Check("device", "fail", "TV query failed", str(exc),
                                "Check address, debugging, pairing, and network reachability."))

        try:
            disabled = client.packages(disabled=True)
            checks.append(Check("package_state", "ok", "Package state readable",
                                f"{len(disabled)} disabled packages"))
        except Exception as exc:
            checks.append(Check("package_state", "fail", "Package state unreadable", str(exc),
                                "Do not apply changes until package state can be read."))

    counts = {s: sum(c.status == s for c in checks) for s in ("ok", "warn", "fail")}
    return {"ready": counts["fail"] == 0, "counts": counts, "checks": [asdict(c) for c in checks]}
