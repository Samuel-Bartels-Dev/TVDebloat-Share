import unittest

from tvdebloat.match import compare
from tvdebloat.model import DeviceFacts
from tvdebloat.profile import Match


FACTS = DeviceFacts(
    manufacturer="ASUS",
    model="OfficeTV",
    device="boardx",
    board="boardx",
    android="12",
    sdk="31",
    fingerprint="asus/officetv/build",
    home="com.vendor.home/.Main",
)


class MatchTests(unittest.TestCase):
    def test_exact(self):
        result = compare(Match(
            manufacturer="ASUS", model="OfficeTV", device="boardx",
            board="boardx", android="12", sdk="31"
        ), FACTS)
        self.assertEqual(result.level, "exact")

    def test_mismatch(self):
        result = compare(Match(manufacturer="ASUS", model="OtherTV"), FACTS)
        self.assertEqual(result.level, "mismatch")


if __name__ == "__main__":
    unittest.main()
