import json
import tempfile
import unittest
from pathlib import Path

from tvdebloat.author import initialize, promote
from tvdebloat.profile import load


class AuthorTests(unittest.TestCase):
    def test_init_and_promote(self):
        discovery = {
            "device": {
                "manufacturer": "ExampleVendor",
                "model": "Model-A",
                "device": "device-a",
                "board": "board-a",
                "android": "12",
                "sdk": "31",
                "fingerprint": "example/model-a/build",
            },
            "packages": [
                {"package": "com.android.settings", "protected": True, "hints": []},
                {"package": "com.vendor.analytics", "protected": False, "hints": ["telemetry"]},
            ],
        }
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "discovery.json"
            source.write_text(json.dumps(discovery), encoding="utf-8")
            path = initialize(source, "examplevendor", "Model-A", "Example Model A", root=Path(d) / "profiles")
            profile = load(path)
            self.assertEqual(profile.status, "candidate")
            self.assertIn("com.android.settings", profile.keep)
            promoted = promote(path)
            self.assertEqual(load(promoted).status, "validated")


if __name__ == "__main__":
    unittest.main()
