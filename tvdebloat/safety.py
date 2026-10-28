from __future__ import annotations

from dataclasses import dataclass

from .adb import Client
from .policy import is_protected
from .profile import Profile


SETUPWRAITH = "com.google.android.tungsten.setupwraith"
TV_INPUT_PERMISSION = "android.permission.TV_INPUT_HARDWARE"


class SafetyError(RuntimeError):
    pass


@dataclass(frozen=True)
class Finding:
    package: str
    severity: str
    reason: str


def component_package(component: str) -> str | None:
    component = (component or "").strip()
    if "/" not in component:
        return None
    package = component.split("/", 1)[0]
    return None if package == "android" else package


def _setupwraith_owns_wifi(client: Client) -> bool | None:
    try:
        out = client.shell("dumpsys wifi")
    except Exception:
        return None
    owners = [token.split("=", 1)[1] for token in out.split() if token.startswith("cname=")]
    if not owners:
        return None
    return any("setupwraith" in owner for owner in owners)


def _requests_input_hardware(client: Client, package: str) -> bool | None:
    try:
        out = client.shell(f"dumpsys package {package}")
    except Exception:
        return None

    requested = False
    inside = False
    saw_block = False
    for raw in out.splitlines():
        line = raw.strip()
        if line == "requested permissions:":
            inside = True
            saw_block = True
            continue
        if inside and raw and not raw.startswith((" ", "\t")):
            break
        if inside and line == TV_INPUT_PERMISSION:
            requested = True
            break
    if saw_block:
        return requested

    if "android.media.tv.TvInputService" in out:
        return True
    return None


def _handler_packages(client: Client, action: str, mime: str | None = None) -> set[str]:
    command = f"cmd package query-activities --brief -a {action}"
    if mime:
        command += f" -t {mime}"
    try:
        out = client.shell(command)
    except Exception:
        return set()
    result = set()
    for line in out.splitlines():
        package = component_package(line.strip())
        if package:
            result.add(package)
    return result


def inspect(client: Client, profile: Profile) -> list[Finding]:
    findings: list[Finding] = []
    disable = set(profile.disable)

    for package in profile.disable:
        if is_protected(package):
            findings.append(Finding(package, "block", "protected Android/TV middleware package"))

    home = component_package(client.resolve_home())
    if home and home in disable:
        alternatives = {
            component_package(x)
            for x in client.home_activities()
        } - {None, home} - disable
        if not alternatives:
            findings.append(Finding(home, "block", "current Home would be disabled with no confirmed alternative"))

    if SETUPWRAITH in disable:
        owns = _setupwraith_owns_wifi(client)
        if owns is True:
            findings.append(Finding(
                SETUPWRAITH, "block",
                "saved Wi-Fi appears owned by SetupWraith; disabling it may remove network access",
            ))
        elif owns is None:
            findings.append(Finding(
                SETUPWRAITH, "warn",
                "could not determine saved Wi-Fi ownership",
            ))

    input_handlers = _handler_packages(
        client,
        "android.intent.action.VIEW",
        "vnd.android.cursor.item/channel",
    )
    settings_handlers = _handler_packages(client, "android.settings.SETTINGS")

    for package in profile.disable:
        drives_inputs = _requests_input_hardware(client, package)
        if drives_inputs is True:
            findings.append(Finding(package, "block", "package provides TV input hardware/services"))
        elif drives_inputs is None:
            findings.append(Finding(package, "warn", "could not determine TV input role"))

        if package in input_handlers:
            findings.append(Finding(package, "block", "package handles TV input/channel intents"))
        if package in settings_handlers:
            findings.append(Finding(package, "block", "package handles Android Settings"))

    keep = set(profile.keep)
    conflicts = keep & disable
    for package in sorted(conflicts):
        findings.append(Finding(package, "block", "profile lists package in both keep and disable"))

    return findings


def assert_safe(client: Client, profile: Profile) -> list[Finding]:
    findings = inspect(client, profile)
    blockers = [f for f in findings if f.severity == "block"]
    if blockers:
        details = "; ".join(f"{f.package}: {f.reason}" for f in blockers)
        raise SafetyError(details)
    return findings
