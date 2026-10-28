from __future__ import annotations

from dataclasses import dataclass

from .model import DeviceFacts
from .profile import Match


@dataclass(frozen=True)
class MatchResult:
    level: str
    matched: tuple[str, ...]
    mismatched: tuple[str, ...]


def compare(expected: Match, actual: DeviceFacts) -> MatchResult:
    pairs = {
        "manufacturer": (expected.manufacturer, actual.manufacturer),
        "model": (expected.model, actual.model),
        "device": (expected.device, actual.device),
        "board": (expected.board, actual.board),
        "android": (expected.android, actual.android),
        "sdk": (expected.sdk, actual.sdk),
    }
    matched = []
    mismatched = []
    specified = 0
    for key, (want, got) in pairs.items():
        if not want:
            continue
        specified += 1
        if want.casefold() == got.casefold():
            matched.append(key)
        else:
            mismatched.append(key)

    if expected.fingerprint_contains:
        specified += 1
        if expected.fingerprint_contains.casefold() in actual.fingerprint.casefold():
            matched.append("fingerprint")
        else:
            mismatched.append("fingerprint")

    if mismatched:
        level = "mismatch"
    elif specified >= 4:
        level = "exact"
    elif specified:
        level = "related"
    else:
        level = "generic"
    return MatchResult(level, tuple(matched), tuple(mismatched))
