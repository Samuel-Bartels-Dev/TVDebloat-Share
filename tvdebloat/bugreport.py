from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import platform
import subprocess

from .state import root


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def write(title: str, operation: str, error: str, expected: str = "", actual: str = "", device: dict | None = None) -> tuple[Path, Path]:
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "operation": operation,
        "error": error,
        "expected": expected,
        "actual": actual,
        "device": device or {},
        "repository": {
            "commit": _git("rev-parse", "HEAD"),
            "branch": _git("branch", "--show-current"),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    folder = root() / "reports"
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jp = folder / f"bug-{stamp}.json"
    mp = folder / f"bug-{stamp}.md"
    jp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    d = payload["device"]
    mp.write_text(f"""# {title}

## Operation
{operation}

## Expected
{expected}

## Actual
{actual}

## Error
```text
{error}
```

## Device
- Manufacturer: {d.get("manufacturer", "")}
- Model: {d.get("model", "")}
- Android: {d.get("android", "")}
- SDK: {d.get("sdk", "")}
- Fingerprint: {d.get("fingerprint", "")}

## Repository
- Commit: {payload["repository"]["commit"]}
- Branch: {payload["repository"]["branch"]}

## Redaction check
Remove IP addresses, SSIDs, MAC addresses, serial numbers, account data, credentials, tokens, and ADB keys before sharing.
""", encoding="utf-8")
    return jp, mp
