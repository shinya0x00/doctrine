#!/usr/bin/env python3
"""Regression tests for lint_plan.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lint_plan import lint_plan


FIXTURES = Path(__file__).parent / "fixtures"
LINTER = Path(__file__).parent / "lint_plan.py"
INTERNAL_SOURCE_TOKENS = (
    "Safe-to-Fail Doctrine",
    "shinya0x00/doctrine",
    "doctrine_ref",
    "/DOCTRINE.md",
    "26397fca6878176195fcaaf3b3d4780df39c3164",
)


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class LintPlanTests(unittest.TestCase):
    def test_runtime_walking_skeleton_plan_passes(self) -> None:
        self.assertEqual(lint_plan(load_fixture("good-runtime.json")), [])

    def test_non_runtime_plan_passes_without_fake_wiring(self) -> None:
        self.assertEqual(lint_plan(load_fixture("good-non-runtime.json")), [])

    def test_known_design_first_order_is_rejected(self) -> None:
        plan = load_fixture("bad-design-first.json")
        self.assertEqual(
            plan["source_order"][0],
            "1. DESIGN.md／ADRで「self-host完了」と「external distribution未完成」を分離し、Doctrineと薄い入口の所有境界を決定する。",
        )
        errors = lint_plan(plan)
        self.assertTrue(any("first milestone" in error for error in errors), errors)

    def test_skeleton_must_connect_every_attachment(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["milestones"][0]["connects"] = []
        errors = lint_plan(plan)
        self.assertTrue(any("connect every declared attachment" in error for error in errors), errors)

    def test_plan_requires_implementation_selection_inputs(self) -> None:
        plan = load_fixture("good-runtime.json")
        for field in (
            "invariants",
            "implementation_options",
            "selected_implementation",
            "complexity_justification",
        ):
            with self.subTest(field=field):
                candidate = dict(plan)
                candidate.pop(field)
                errors = lint_plan(candidate)
                self.assertTrue(any(field in error for error in errors), errors)

    def test_selected_implementation_must_match_an_option(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["selected_implementation"] = "an unlisted alternative"
        errors = lint_plan(plan)
        self.assertTrue(any("exactly match one implementation option" in error for error in errors), errors)

    def test_implementation_options_must_be_unique(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["implementation_options"].append(plan["implementation_options"][0])
        errors = lint_plan(plan)
        self.assertTrue(any("implementation_options must be unique" in error for error in errors), errors)

    def test_complexity_justification_has_bounded_shape(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["complexity_justification"] = []
        errors = lint_plan(plan)
        self.assertTrue(any("complexity_justification" in error for error in errors), errors)

    def test_any_exact_source_commit_is_accepted(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["doctrine_ref"] = (
            "https://github.com/shinya0x00/doctrine/blob/"
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/DOCTRINE.md"
        )
        self.assertEqual(lint_plan(plan), [])

    def test_moving_or_wrong_sources_are_rejected(self) -> None:
        invalid_refs = (
            "https://github.com/shinya0x00/doctrine/blob/main/DOCTRINE.md",
            "https://github.com/shinya0x00/doctrine/blob/26397f/DOCTRINE.md",
            "https://github.com/example/doctrine/blob/"
            "26397fca6878176195fcaaf3b3d4780df39c3164/DOCTRINE.md",
            "https://github.com/shinya0x00/doctrine/blob/"
            "26397fca6878176195fcaaf3b3d4780df39c3164/README.md",
        )
        for doctrine_ref in invalid_refs:
            with self.subTest(doctrine_ref=doctrine_ref):
                plan = load_fixture("good-runtime.json")
                plan["doctrine_ref"] = doctrine_ref
                errors = lint_plan(plan)
                self.assertTrue(any("internal source reference" in error for error in errors), errors)

    def test_cli_success_does_not_project_internal_source_identity(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LINTER), str(FIXTURES / "good-runtime.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "verdict: proceed\n")
        self.assertEqual(result.stderr, "")

    def test_cli_failure_does_not_project_internal_source_identity(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LINTER), str(FIXTURES / "bad-design-first.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        combined = result.stdout + result.stderr
        for forbidden in INTERNAL_SOURCE_TOKENS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)

    def test_cli_source_error_does_not_project_internal_source_identity(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["doctrine_ref"] = "invalid"
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as stream:
            json.dump(plan, stream)
            stream.flush()
            result = subprocess.run(
                [sys.executable, str(LINTER), stream.name],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("internal source reference", result.stdout)
        for forbidden in INTERNAL_SOURCE_TOKENS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_cli_help_does_not_project_internal_source_identity(self) -> None:
        result = subprocess.run(
            [sys.executable, str(LINTER), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for forbidden in INTERNAL_SOURCE_TOKENS:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
