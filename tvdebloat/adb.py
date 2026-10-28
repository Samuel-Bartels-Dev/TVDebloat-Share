from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import subprocess


class AdbError(RuntimeError):
    pass


@dataclass(frozen=True)
class Target:
    host: str
    port: int = 5555

    @property
    def serial(self) -> str:
        return f"{self.host}:{self.port}"


class Client:
    def __init__(self, target: Target, adb: str | None = None):
        self.target = target
        self.adb = adb or os.environ.get("ADB") or shutil.which("adb")
        if not self.adb:
            raise AdbError("adb was not found; install Android platform-tools or set ADB=/path/to/adb")

    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(
            [self.adb, "-s", self.target.serial, *args],
            text=True,
            capture_output=True,
        )
        if proc.returncode:
            detail = (proc.stderr or proc.stdout).strip()
            raise AdbError(detail or f"adb command failed: {' '.join(args)}")
        return proc

    def connect(self) -> None:
        proc = subprocess.run(
            [self.adb, "connect", self.target.serial],
            text=True,
            capture_output=True,
        )
        text = (proc.stdout + proc.stderr).lower()
        if proc.returncode or ("connected" not in text and "already connected" not in text):
            raise AdbError((proc.stdout + proc.stderr).strip() or f"could not connect to {self.target.serial}")

    def shell(self, command: str) -> str:
        return self._run("shell", command).stdout.replace("\r\n", "\n").rstrip()

    def prop(self, name: str) -> str:
        return self.shell(f"getprop {name}").strip()

    def packages(self, disabled: bool = False) -> list[str]:
        cmd = "pm list packages -d --user 0" if disabled else "pm list packages --user 0"
        out = self.shell(cmd)
        if not any(line.startswith("package:") for line in out.splitlines()) and "--user 0" in cmd:
            out = self.shell("pm list packages -d" if disabled else "pm list packages")
        return sorted({
            line.split(":", 1)[1].strip()
            for line in out.splitlines()
            if line.startswith("package:")
        })

    def resolve_home(self) -> str:
        out = self.shell(
            "cmd package resolve-activity --brief "
            "-a android.intent.action.MAIN -c android.intent.category.HOME"
        )
        lines = [x.strip() for x in out.splitlines() if x.strip()]
        return lines[-1] if lines else ""

    def home_activities(self) -> list[str]:
        out = self.shell(
            "cmd package query-activities --brief "
            "-a android.intent.action.MAIN -c android.intent.category.HOME"
        )
        return [x.strip() for x in out.splitlines() if "/" in x]

    def disable(self, package: str) -> str:
        return self.shell(f"pm disable-user --user 0 {package}")

    def enable(self, package: str) -> str:
        return self.shell(f"pm enable --user 0 {package}")
