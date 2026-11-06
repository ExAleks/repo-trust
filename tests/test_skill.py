import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "repo-trust"


class FrontmatterTests(unittest.TestCase):
    def test_skill_md_has_valid_frontmatter(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md must start with frontmatter")
        end = text.index("\n---", 3)
        fm = yaml.safe_load(text[4:end])
        self.assertEqual(fm["name"], "repo-trust")
        self.assertIn("description", fm)
        self.assertGreater(len(fm["description"]), 100)


class LayoutTests(unittest.TestCase):
    def test_every_referenced_file_exists(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        import re
        for rel in re.findall(r"`(?:references|templates)/([\w.-]+)`", text):
            target = (SKILL / "references" / rel).exists() or (SKILL / "templates" / rel).exists()
            self.assertTrue(
                target,
                f"SKILL.md references {rel} but the file is missing",
            )

    def test_no_broken_reference_links(self):
        for ref in (SKILL / "references").glob("*.md"):
            text = ref.read_text(encoding="utf-8")
            import re
            for rel in re.findall(r"`templates/([\w.-]+)`", text):
                self.assertTrue(
                    (SKILL / "templates" / rel).exists(),
                    f"{ref.name} references templates/{rel} which is missing",
                )


class TemplateTests(unittest.TestCase):
    def test_ci_templates_are_valid_yaml(self):
        for f in (SKILL / "templates").glob("ci-*.yml"):
            if f.name == "ci-release.yml":
                continue  # covered by its own test
            raw = f.read_text(encoding="utf-8")
            raw = raw.replace("{{DEFAULT_BRANCH}}", "main").replace("{{PROJECT_NAME}}", "app")
            data = yaml.safe_load(raw)
            self.assertIn("jobs", data, f"{f.name} has no jobs")
            self.assertEqual(
                data.get("permissions"), {"contents": "read"},
                f"{f.name} must keep least privilege",
            )

    def test_release_template_needs_write(self):
        raw = (SKILL / "templates" / "ci-release.yml").read_text(encoding="utf-8")
        raw = raw.replace("{{PROJECT_NAME}}", "app")
        data = yaml.safe_load(raw)
        self.assertEqual(data.get("permissions"), {"contents": "write"})

    def test_dependabot_ecosystems_are_known(self):
        data = yaml.safe_load((SKILL / "templates" / "dependabot.yml").read_text(encoding="utf-8"))
        known = {
            "github-actions", "pip", "npm", "cargo", "gomod", "maven",
            "nuget", "gradle", "docker", "terraform", "devcontainers",
        }
        for entry in data["updates"]:
            self.assertIn(entry["package-ecosystem"], known)

    def test_templates_have_no_leftover_placeholders_after_substitution(self):
        for f in (SKILL / "templates").glob("*.yml"):
            raw = f.read_text(encoding="utf-8")
            raw = raw.replace("{{DEFAULT_BRANCH}}", "main").replace("{{PROJECT_NAME}}", "app")
            # ${{ github.* }} is valid GitHub Actions syntax, not a placeholder
            import re
            leftovers = [m for m in re.findall(r"\{\{\s*([A-Z_]+)\s*\}\}", raw)]
            self.assertEqual(
                leftovers, [], f"{f.name} still has unsubstituted placeholders: {leftovers}",
            )


class ReadmeTests(unittest.TestCase):
    def test_install_section_covers_major_agents(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for agent in ("Claude Code", "Codex", "Cursor", "OpenCode", "Copilot"):
            self.assertIn(agent, text, f"README install section misses {agent}")


if __name__ == "__main__":
    unittest.main()
