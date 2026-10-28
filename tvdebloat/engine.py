from __future__ import annotations

from pathlib import Path

from .adb import Client
from .backup import capture
from .facts import read as read_facts
from .match import compare
from .profile import load as load_profile
from .safety import SafetyError, assert_safe
from .state import create as create_recovery, load as load_recovery, save as save_recovery


class ApplyError(RuntimeError):
    pass


def preview(client: Client, profile_path: str | Path) -> dict:
    profile = load_profile(profile_path)
    facts = read_facts(client)
    match = compare(profile.match, facts)
    findings = assert_safe(client, profile)
    installed = set(client.packages())
    disabled = set(client.packages(disabled=True))

    return {
        "profile": profile.name,
        "profile_path": str(profile.path),
        "match": {
            "level": match.level,
            "matched": list(match.matched),
            "mismatched": list(match.mismatched),
        },
        "device": facts.as_dict(),
        "disable": [
            {
                "package": package,
                "installed": package in installed,
                "already_disabled": package in disabled,
            }
            for package in profile.disable
        ],
        "warnings": [
            {"package": f.package, "reason": f.reason}
            for f in findings if f.severity == "warn"
        ],
        "ready": match.level != "mismatch",
    }


def apply(client: Client, profile_path: str | Path, allow_candidate: bool = False) -> dict:
    profile = load_profile(profile_path)
    if profile.status != "validated" and not allow_candidate:
        raise ApplyError(
            "profile is not validated; use the guided pilot workflow for a first-device test"
        )
    plan = preview(client, profile.path)
    if not plan["ready"]:
        raise ApplyError("live TV does not match the selected profile")

    installed = set(client.packages())
    disabled_before = set(client.packages(disabled=True))
    backup_path = capture(client, profile.name)
    recovery = create_recovery(client.target.serial, profile.path, sorted(disabled_before))

    changed = []
    missing = []
    for package in profile.disable:
        if package not in installed:
            missing.append(package)
            continue
        if package in disabled_before:
            continue
        client.disable(package)
        changed.append(package)

    disabled_after = set(client.packages(disabled=True))
    failed = [p for p in changed if p not in disabled_after]
    if failed:
        for package in reversed(changed):
            if package in disabled_after and package not in disabled_before:
                client.enable(package)
        raise ApplyError(f"packages did not remain disabled: {', '.join(failed)}; attempted rollback")

    recovery.changed = changed
    recovery_path = save_recovery(recovery, profile.path)
    return {
        "profile": profile.name,
        "changed": changed,
        "missing": missing,
        "backup": str(backup_path),
        "recovery": str(recovery_path),
    }


def restore(client: Client, profile_path: str | Path) -> dict:
    profile = load_profile(profile_path)
    recovery = load_recovery(client.target.serial, profile.path)
    restored = []
    for package in recovery.changed:
        if package not in recovery.initially_disabled:
            client.enable(package)
            restored.append(package)
    return {"profile": profile.name, "restored": restored}
