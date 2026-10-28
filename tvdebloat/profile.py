from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib


PACKAGE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+$")


@dataclass(frozen=True)
class Match:
    manufacturer: str = ""
    model: str = ""
    device: str = ""
    board: str = ""
    android: str = ""
    sdk: str = ""
    fingerprint_contains: str = ""


@dataclass(frozen=True)
class Profile:
    path: Path
    name: str
    match: Match
    disable: tuple[str, ...]
    keep: tuple[str, ...]
    notes: tuple[str, ...]


class ProfileError(ValueError):
    pass


def _packages(values, field: str) -> tuple[str, ...]:
    seen = []
    for value in values or []:
        if not isinstance(value, str) or not PACKAGE_RE.fullmatch(value):
            raise ProfileError(f"{field}: invalid package name: {value!r}")
        if value not in seen:
            seen.append(value)
    return tuple(seen)


def load(path: str | Path) -> Profile:
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ProfileError(f"profile does not exist: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProfileError(f"cannot parse profile {path}: {exc}") from exc

    device = data.get("device", {})
    packages = data.get("packages", {})
    return Profile(
        path=path,
        name=str(data.get("name") or path.parent.name),
        match=Match(
            manufacturer=str(device.get("manufacturer", "")),
            model=str(device.get("model", "")),
            device=str(device.get("device", "")),
            board=str(device.get("board", "")),
            android=str(device.get("android", "")),
            sdk=str(device.get("sdk", "")),
            fingerprint_contains=str(device.get("fingerprint_contains", "")),
        ),
        disable=_packages(packages.get("disable", []), "packages.disable"),
        keep=_packages(packages.get("keep", []), "packages.keep"),
        notes=tuple(str(x) for x in data.get("notes", [])),
    )
