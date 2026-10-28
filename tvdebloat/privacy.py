from __future__ import annotations

import re
from .adb import Client

KNOWN = {
    "com.google.android.katniss": ("voice", "Google Assistant / voice search"),
    "com.google.android.speech.pumpkin": ("voice", "offline speech/hotword model"),
    "tv.inscape.tvclient.inscapeacr": ("acr", "Inscape automatic content recognition"),
    "com.skyworth.aisense": ("acr", "Skyworth/Coocaa automatic content recognition"),
    "tv.samba.ssm.ui": ("acr", "Samba TV automatic content recognition"),
    "com.tcl.logkit": ("telemetry", "TCL logging component"),
    "com.google.android.feedback": ("telemetry", "Google feedback reports"),
    "com.google.android.apps.tv.netoscope": ("telemetry", "Google TV network diagnostics"),
    "com.google.android.partnersetup": ("telemetry", "Google partner attribution/setup"),
}
HINT = re.compile(r"(?:^|\.)(acr|analytics|assistant|alexa|hotword|inscape|privacy|speech|telemetry|tracker|tracking|voice)", re.I)


def audit(client: Client, limit: int = 25) -> dict:
    installed = client.packages()
    disabled = set(client.packages(disabled=True))
    candidates = [p for p in installed if p in KNOWN]
    candidates += [p for p in installed if p not in candidates and HINT.search(p)]
    entries = []
    for package in candidates[:limit]:
        category, note = KNOWN.get(package, ("unknown", "matched by package name only"))
        entries.append({
            "package": package,
            "category": category,
            "note": note,
            "state": "disabled" if package in disabled else "enabled",
        })
    return {
        "entries": entries,
        "unprobed_name_matches": max(0, len(candidates) - limit),
        "warning": "A candidate match is evidence to investigate, not automatic permission to disable.",
    }
