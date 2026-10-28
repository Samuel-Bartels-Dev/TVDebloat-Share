import unittest

from tvdebloat.safety import inspect
from tvdebloat.profile import Profile, Match
from pathlib import Path


class FakeClient:
    def resolve_home(self):
        return "com.vendor.home/.Main"

    def home_activities(self):
        return ["com.vendor.home/.Main"]

    def shell(self, command):
        if command == "dumpsys wifi":
            return "cname=com.google.android.tungsten.setupwraith"
        if command.startswith("dumpsys package "):
            return "requested permissions:\n  android.permission.INTERNET\n"
        if "query-activities" in command:
            return ""
        return ""


class SafetyTests(unittest.TestCase):
    def profile(self, disable):
        return Profile(
            path=Path("profile.toml"),
            name="x",
            status="candidate",
            match=Match(),
            disable=tuple(disable),
            keep=(),
            review=(),
            notes=(),
        )

    def test_blocks_only_home(self):
        findings = inspect(FakeClient(), self.profile(["com.vendor.home"]))
        self.assertTrue(any(f.severity == "block" and "Home" in f.reason for f in findings))

    def test_blocks_setupwraith_owned_wifi(self):
        findings = inspect(FakeClient(), self.profile(["com.google.android.tungsten.setupwraith"]))
        self.assertTrue(any(f.severity == "block" and "Wi-Fi" in f.reason for f in findings))


if __name__ == "__main__":
    unittest.main()
