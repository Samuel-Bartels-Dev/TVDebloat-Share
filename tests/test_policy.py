import unittest

from tvdebloat.policy import is_protected


class PolicyTests(unittest.TestCase):
    def test_core_packages_are_protected(self):
        self.assertTrue(is_protected("android"))
        self.assertTrue(is_protected("com.android.systemui"))
        self.assertTrue(is_protected("com.android.settings"))

    def test_known_optional_provider_can_be_reviewed(self):
        self.assertFalse(is_protected("com.android.providers.calendar"))


if __name__ == "__main__":
    unittest.main()
