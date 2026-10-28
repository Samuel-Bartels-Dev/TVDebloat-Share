import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillTests(unittest.TestCase):
    def test_openai_skill_is_lean_and_reference_driven(self):
        path = ROOT / ".agents" / "skills" / "tvdebloat" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Load only when needed", text)
        self.assertIn("profile-maintenance.md", text)
        self.assertIn("profile-authoring.md", text)
        self.assertIn("explicit approval", text)

    def test_claude_skill_exists(self):
        path = ROOT / ".claude" / "skills" / "tvdebloat" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true", text)
        self.assertIn("Mandatory preflight", text)


if __name__ == "__main__":
    unittest.main()
