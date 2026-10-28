from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


@dataclass
class Recovery:
    target: str
    profile: str
    profile_sha256: str
    created_at: str
    initially_disabled: list[str]
    changed: list[str]


def root() -> Path:
    return Path.home() / ".tvdebloat"


def _safe_target(target: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in target)


def profile_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_for(target: str, profile: Path) -> Path:
    digest = hashlib.sha256(str(profile).encode()).hexdigest()[:12]
    return root() / "recovery" / f"{_safe_target(target)}-{digest}.json"


def save(record: Recovery, profile_path: Path) -> Path:
    path = path_for(record.target, profile_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(record), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def create(target: str, profile: Path, initially_disabled: list[str]) -> Recovery:
    return Recovery(
        target=target,
        profile=str(profile),
        profile_sha256=profile_hash(profile),
        created_at=datetime.now(timezone.utc).isoformat(),
        initially_disabled=sorted(set(initially_disabled)),
        changed=[],
    )


def load(target: str, profile: Path) -> Recovery:
    data = json.loads(path_for(target, profile).read_text(encoding="utf-8"))
    return Recovery(**data)
