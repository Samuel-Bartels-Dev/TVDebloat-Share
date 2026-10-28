from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re

from .adb import Client
from .facts import read as read_facts
from .policy import is_protected

HINTS = {
    "telemetry": re.compile(r"(analytics|telemetry|log|feedback|metrics|stats)", re.I),
    "recommendations": re.compile(r"(recommend|launcherx|discover|content|promo|adservice|ads)", re.I),
    "voice": re.compile(r"(assistant|speech|voice|hotword|alexa)", re.I),
    "setup": re.compile(r"(setup|provision)", re.I),
    "remote": re.compile(r"(remote|bluetooth|bt)", re.I),
    "input": re.compile(r"(input|hdmi|tuner|tvservice|tv\.service|tis)", re.I),
}


@dataclass(frozen=True)
class PackageObservation:
    package: str
    disabled: bool
    protected: bool
    hints: tuple[str, ...]


def discover(client: Client) -> dict:
    installed = client.packages()
    disabled = set(client.packages(disabled=True))
    observations = []
    for package in installed:
        hints = tuple(name for name, rx in HINTS.items() if rx.search(package))
        observations.append(PackageObservation(
            package=package,
            disabled=package in disabled,
            protected=is_protected(package),
            hints=hints,
        ))
    return {
        "device": read_facts(client).as_dict(),
        "packages": [asdict(x) for x in observations],
        "guidance": {
            "disable_candidates": "Review packages with telemetry/recommendations hints; do not auto-disable.",
            "keep_candidates": "Treat protected/input/remote/setup packages as keep/review unless device evidence says otherwise.",
            "unknown": "Unknown packages require investigation before classification.",
        },
    }


def write(result: dict, path: str | Path) -> Path:
    path = Path(path)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
