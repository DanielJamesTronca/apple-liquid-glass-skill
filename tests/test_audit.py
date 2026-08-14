#!/usr/bin/env python3
"""
Test suite for the apple-liquid-glass skill.

Covers the things that can actually break silently:
  - the audit script's signal/noise balance against known-good and known-bad code
  - manifest validity (a malformed plugin.json breaks installation)
  - SKILL.md structure and, critically, that every reference file it links exists
    (a broken link silently breaks progressive disclosure)

Run: python3 tests/test_audit.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "apple-liquid-glass"
SCRIPTS = SKILL / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
AUDIT = SCRIPTS / "audit_liquid_glass.py"

# Leads the bad fixture must surface at medium confidence or above.
EXPECTED_BAD = {
    "glass-on-button",
    "glass-in-toolbar",
    "glass-in-list-row",
    "hardcoded-foreground-on-glass",
    "clear-without-dimming",
    "custom-bar-background",
    "presentation-background",
    "magic-opacity",
    "glass-effect-id-no-animation",
    "glass-button-no-label",
}


def audit(path: Path, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(AUDIT), str(path), "--json", *args],
        capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout)


class TestAuditSignal(unittest.TestCase):
    def test_bad_fixture_surfaces_expected_leads(self):
        found = {f["check"] for f in audit(FIXTURES / "BadGlass.swift")["findings"]
                 if f["confidence"] in ("medium", "high")}
        missing = EXPECTED_BAD - found
        self.assertFalse(missing, f"audit missed leads in BadGlass.swift: {sorted(missing)}")

    def test_good_fixture_is_clean(self):
        """A medium+ finding on correct code is an audit bug, not a fixture bug."""
        noisy = [f for f in audit(FIXTURES / "GoodGlass.swift")["findings"]
                 if f["confidence"] in ("medium", "high")]
        self.assertEqual(
            [], noisy,
            "false positives on known-good code: "
            + ", ".join(f"{f['check']}@L{f['line']}" for f in noisy),
        )

    def test_every_finding_explains_itself(self):
        for f in audit(FIXTURES)["findings"]:
            self.assertTrue(f.get("inspect"), f"check {f['check']} has no inspect guidance")
            self.assertIn(f["confidence"], ("low", "medium", "high"))
            self.assertGreater(f["line"], 0)

    def test_confidence_filter_narrows_results(self):
        low = len(audit(FIXTURES)["findings"])
        high = len(audit(FIXTURES, "--min-confidence", "high")["findings"])
        self.assertLess(high, low, "--min-confidence had no effect")

    def test_deployment_target_detection_survives_absence(self):
        """Must not crash when no pbxproj exists — it degrades to a warning."""
        self.assertIsInstance(audit(FIXTURES)["deployment_targets"], dict)

    def test_multiple_deployment_targets_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "project.pbxproj").write_text(
                "IPHONEOS_DEPLOYMENT_TARGET = 18.0;\n"
                "IPHONEOS_DEPLOYMENT_TARGET = 26.0;\n"
            )
            self.assertEqual(
                ["18.0", "26.0"],
                audit(root)["deployment_targets"]["IPHONEOS"],
            )

    def test_compatibility_key_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plist = root / "Info.plist"
            plist.write_text("<key>UIDesignRequiresCompatibility</key><true/>")
            reported = audit(root)["compatibility_keys"]
            self.assertEqual([str(plist)], reported)


class TestScriptsHealthy(unittest.TestCase):
    def test_scripts_compile(self):
        subprocess.run(
            [sys.executable, "-m", "py_compile", str(AUDIT)],
            check=True,
            capture_output=True,
        )

    def test_audit_help_works(self):
        proc = subprocess.run([sys.executable, str(AUDIT), "--help"],
                              capture_output=True, text=True)
        self.assertEqual(0, proc.returncode)

class TestManifests(unittest.TestCase):
    def test_plugin_manifest_valid(self):
        data = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual("apple-liquid-glass", data["name"])
        for field in ("description", "version", "author", "license"):
            self.assertIn(field, data)

    def test_marketplace_manifest_valid(self):
        data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertIn("name", data)
        self.assertIn("name", data["owner"])
        self.assertTrue(data["plugins"], "marketplace lists no plugins")
        for plugin in data["plugins"]:
            self.assertIn("name", plugin)
            self.assertIn("source", plugin)

    def test_manifest_versions_agree(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(plugin["version"], entry.get("version"),
                         "plugin.json and marketplace.json versions have drifted")
        self.assertEqual(plugin["version"], codex["version"],
                         "Claude and Codex plugin versions have drifted")

class TestSkillStructure(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text()

    def test_frontmatter_uses_spec_fields_only(self):
        """Keep frontmatter portable across Agent Skills hosts."""
        self.assertTrue(self.text.startswith("---\n"))
        fm = self.text.split("---", 2)[1]
        allowed = {"name", "description"}
        keys = {line.split(":", 1)[0].strip()
                for line in fm.splitlines()
                if line.strip() and not line.startswith((" ", "\t", "#"))}
        self.assertTrue(keys <= allowed, f"non-spec frontmatter keys: {sorted(keys - allowed)}")

    def test_has_name_and_description(self):
        self.assertRegex(self.text, r"(?m)^name:\s*apple-liquid-glass\s*$")
        self.assertRegex(self.text, r"(?m)^description:\s*\S")

    def test_stays_concise(self):
        lines = len(self.text.splitlines())
        self.assertLess(lines, 250, f"SKILL.md grew to {lines} lines; move detail to references/")

    def test_current_bar_guidance_is_present(self):
        swiftui = (SKILL / "references" / "swiftui.md").read_text()
        for symbol in (
            "safeAreaBar(edge:alignment:spacing:content:)",
            "toolbarMinimizationRestoration(_:for:)",
            "toolbarMinimizationSafeAreaAdjustment(_:for:)",
        ):
            self.assertIn(symbol, swiftui)

    def test_linked_references_all_exist(self):
        import re
        linked = set(re.findall(r"references/([a-z0-9\-]+\.md)", self.text))
        self.assertTrue(linked, "SKILL.md links no reference files")
        for name in sorted(linked):
            with self.subTest(reference=name):
                self.assertTrue((SKILL / "references" / name).exists(),
                                f"SKILL.md links references/{name} but it does not exist")

    def test_no_orphan_reference_files(self):
        import re
        linked = set(re.findall(r"references/([a-z0-9\-]+\.md)", self.text))
        on_disk = {p.name for p in (SKILL / "references").glob("*.md")}
        self.assertEqual(set(), on_disk - linked,
                         f"reference files never linked from SKILL.md: {sorted(on_disk - linked)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
