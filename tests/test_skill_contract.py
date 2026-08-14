#!/usr/bin/env python3
"""Structural contracts for routing, prompt evals, and source expectations."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "apple-liquid-glass"
SKILL_MD = SKILL / "SKILL.md"
EVALS = ROOT / "tests" / "skill_evals.json"
SOURCE_CHECK = SKILL / "scripts" / "check_sources.py"
SOURCE_EXPECTATIONS = SKILL / "scripts" / "source_expectations.json"


class TestPromptEvalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL_MD.read_text()
        cls.data = json.loads(EVALS.read_text())
        cls.cases = cls.data["cases"]

    def test_eval_schema_and_ids(self):
        self.assertEqual(1, self.data["schema_version"])
        self.assertGreaterEqual(len(self.cases), 12)
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)), "eval case IDs must be unique")
        for case in self.cases:
            for field in (
                "id", "prompt", "should_trigger", "route",
                "expected_references", "expected_outcomes",
            ):
                self.assertIn(field, case, f"{case.get('id')} missing {field}")
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["expected_outcomes"])

    def test_positive_and_negative_boundaries_exist(self):
        positive = [case for case in self.cases if case["should_trigger"]]
        negative = [case for case in self.cases if not case["should_trigger"]]
        self.assertGreaterEqual(len(positive), 8)
        self.assertGreaterEqual(len(negative), 4)
        self.assertTrue(all(case["expected_references"] for case in positive))
        self.assertTrue(all(not case["expected_references"] for case in negative))

    def test_every_major_route_has_a_positive_eval(self):
        routes = {case["route"] for case in self.cases if case["should_trigger"]}
        required = {
            "review", "migration", "appkit", "design", "navigation",
            "presentations", "widgets", "icons", "accessibility",
            "performance", "sources",
        }
        self.assertFalse(required - routes, f"routes without evals: {sorted(required - routes)}")

    def test_expected_references_are_directly_routed(self):
        for case in self.cases:
            for reference in case["expected_references"]:
                with self.subTest(case=case["id"], reference=reference):
                    self.assertTrue((SKILL / reference).exists())
                    self.assertIn(reference, self.skill_text)

    def test_description_states_positive_and_negative_scope(self):
        frontmatter = self.skill_text.split("---", 2)[1]
        description = re.search(r"(?m)^description:\s*(.+)$", frontmatter).group(1)
        for term in ("Liquid Glass", "SwiftUI", "UIKit", "AppKit", "WidgetKit"):
            self.assertIn(term, description)
        self.assertLessEqual(len(description), 700)
        self.assertIn("Do not use", description)
        self.assertIn("non-Apple glassmorphism", description)

    def test_interface_metadata_matches_skill(self):
        metadata = (SKILL / "agents" / "openai.yaml").read_text()
        short_description = re.search(r'short_description: "([^"]+)"', metadata)

        self.assertIsNotNone(short_description)
        self.assertGreaterEqual(len(short_description.group(1)), 25)
        self.assertLessEqual(len(short_description.group(1)), 64)
        self.assertIn("$apple-liquid-glass", metadata)
        self.assertIn("smallest correct Liquid Glass change", metadata)


class TestProgressiveDisclosure(unittest.TestCase):
    def test_long_references_have_contents(self):
        for reference in (SKILL / "references").glob("*.md"):
            lines = reference.read_text().splitlines()
            if len(lines) <= 100:
                continue
            with self.subTest(reference=reference.name):
                self.assertIn("## Contents", lines[:20])

    def test_framework_references_are_selective(self):
        text = SKILL_MD.read_text()
        self.assertIn("Do not load SwiftUI guidance for a pure UIKit or AppKit task.", text)
        self.assertNotIn("in addition, not instead", text)


class TestSourceExpectations(unittest.TestCase):
    def test_manifest_is_valid_offline(self):
        subprocess.run(
            [sys.executable, str(SOURCE_CHECK), "--offline"],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_volatile_api_families_are_covered(self):
        data = json.loads(SOURCE_EXPECTATIONS.read_text())
        ids = {source["id"] for source in data["sources"]}
        required = {
            "swiftui-glass-effect",
            "swiftui-glass-container",
            "swiftui-toolbar-minimization",
            "swiftui-toolbar-restoration",
            "swiftui-toolbar-safe-area-adjustment",
            "swiftui-toolbar-overflow-menu",
            "swiftui-toolbar-visibility-priority",
            "uikit-glass-effect",
            "appkit-glass-effect-view",
            "appkit-corner-configuration",
            "widgetkit-accented-rendering",
        }
        self.assertFalse(required - ids, f"untracked API families: {sorted(required - ids)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
