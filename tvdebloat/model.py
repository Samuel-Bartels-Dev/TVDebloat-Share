from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class DeviceFacts:
    manufacturer: str
    model: str
    device: str
    board: str
    android: str
    sdk: str
    fingerprint: str
    home: str

    def as_dict(self) -> dict:
        return asdict(self)
