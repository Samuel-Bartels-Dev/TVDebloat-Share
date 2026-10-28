from __future__ import annotations

from pathlib import Path
import json
import re

from .profile import load


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    return value.strip("-") or "unknown"


def render_profile(name: str, status: str, device: dict, disable: list[str], keep: list[str], notes: list[str]) -> str:
    lines = [
        f'name = {json.dumps(name)}',
        f'status = {json.dumps(status)}',
        "",
        "[device]",
    ]
    for key in ("manufacturer", "model", "device", "board", "android", "sdk"):
        lines.append(f"{key} = {json.dumps(str(device.get(key, '')))}")
    fingerprint = str(device.get("fingerprint", ""))
    lines.append(f"fingerprint_contains = {json.dumps(fingerprint)}")
    lines += ["", "[packages]", "disable = ["]
    lines += [f"  {json.dumps(x)}," for x in disable]
    lines += ["]", "", "keep = ["]
    lines += [f"  {json.dumps(x)}," for x in keep]
    lines += ["]", "", "notes = ["]
    lines += [f"  {json.dumps(x)}," for x in notes]
    lines += ["]", ""]
    return "\n".join(lines)


def initialize(discovery_path: str | Path, vendor: str, model: str, name: str, root: str | Path = "profiles") -> Path:
    data = json.loads(Path(discovery_path).read_text(encoding="utf-8"))
    device = data["device"]

    keep = sorted({
        p["package"]
        for p in data.get("packages", [])
        if p.get("protected") or any(h in {"input", "remote", "setup"} for h in p.get("hints", []))
    })
    notes = [
        "Generated from live discovery. Candidate only.",
        "Review every package before adding it to disable.",
        "Pilot validation and reboot test are required before promotion.",
    ]

    folder = Path(root) / slug(vendor) / slug(model)
    folder.mkdir(parents=True, exist_ok=True)
    profile_path = folder / "profile.toml"
    if profile_path.exists():
        raise FileExistsError(f"profile already exists: {profile_path}")

    profile_path.write_text(
        render_profile(name, "candidate", device, [], keep, notes),
        encoding="utf-8",
    )
    notes_path = folder / "NOTES.md"
    notes_path.write_text(
        "# Device notes\n\n"
        "Record package research, physical validation, reboot behavior, and firmware-specific findings here.\n",
        encoding="utf-8",
    )
    return profile_path


def promote(profile_path: str | Path) -> Path:
    path = Path(profile_path)
    text = path.read_text(encoding="utf-8")
    profile = load(path)
    if 'status = "candidate"' not in text:
        raise ValueError("profile is not in candidate state")
    text = text.replace('status = "candidate"', 'status = "validated"', 1)
    path.write_text(text, encoding="utf-8")
    return path
