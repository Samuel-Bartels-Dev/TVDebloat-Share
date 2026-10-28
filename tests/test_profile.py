import tempfile
import unittest
from pathlib import Path

from tvdebloat.profile import load, ProfileError


class ProfileTests(unittest.TestCase):
    def test_loads_profile(self):
        text = """name = "ASUS Office"
status = "candidate"

[device]
manufacturer = "ASUS"
model = "X"

[packages]
disable = ["com.vendor.ads"]
keep = ["com.vendor.input"]
"""
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            f.write(text)
            path = Path(f.name)
        p = load(path)
        self.assertEqual(p.name, "ASUS Office")
        self.assertEqual(p.status, "candidate")
        self.assertEqual(p.disable, ("com.vendor.ads",))

    def test_rejects_bad_package(self):
        text = """name = "bad"
[device]
model = "x"
[packages]
disable = ["com.vendor.ads;reboot"]
"""
        with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
            f.write(text)
            path = Path(f.name)
        with self.assertRaises(ProfileError):
            load(path)


if __name__ == "__main__":
    unittest.main()
