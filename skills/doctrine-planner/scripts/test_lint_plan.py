#!/usr/bin/env python3
"""Regression tests for lint_plan.py."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import lint_plan as lint_plan_module
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

    def test_skeleton_connects_returns_a_finding_for_unhashable_items(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["milestones"][0]["connects"] = [{}]
        errors = lint_plan(plan)
        self.assertTrue(any("non-empty string list" in error for error in errors), errors)

    def test_required_string_list_fields_reject_malformed_values(self) -> None:
        fields = (
            "allowed_paths",
            "validation",
            "stop_conditions",
            "invariants",
            "implementation_options",
            "remaining_diff",
            "next_fill_order",
        )
        invalid_values = ([], [""], ["   "], [{}], "not-a-list")
        for field in fields:
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    plan = load_fixture("good-runtime.json")
                    plan[field] = value
                    errors = lint_plan(plan)
                    self.assertTrue(any(field in error for error in errors), errors)

    def test_control_mark_or_separator_only_strings_are_rejected(self) -> None:
        values = (
            "\u0000",
            "\u034f",
            "\ufe0f",
            "\u200b",
            "\ufeff",
            " \t\u0000\u034f\ufe0f\u200b\ufeff\n",
        )
        for value in values:
            with self.subTest(value=repr(value)):
                plan = load_fixture("good-runtime.json")
                plan["validation"] = [value]
                errors = lint_plan(plan)
                self.assertTrue(any("validation" in error for error in errors), errors)

    def test_composed_text_and_emoji_are_meaningful_strings(self) -> None:
        values = ("e\u0301", "❤\ufe0f", "👩\u200d💻")
        for value in values:
            with self.subTest(value=value):
                plan = load_fixture("good-runtime.json")
                plan["scope"] = value
                self.assertEqual(lint_plan(plan), [])

    def test_every_milestone_kind_must_be_a_meaningful_string(self) -> None:
        for value in (None, "", " \u200b"):
            with self.subTest(value=value):
                plan = load_fixture("good-runtime.json")
                plan["milestones"][1]["kind"] = value
                errors = lint_plan(plan)
                self.assertTrue(any("milestone.kind" in error for error in errors), errors)

    def test_natural_language_does_not_change_a_valid_runtime_verdict(self) -> None:
        prose_values = (
            "Connect the integration later.",
            "Connect the adapter now. Future features are out of scope.",
            "Connect the adapter after validation.",
            "後で接続する。",
            "検証後に接続する。",
            "次のフェーズで接続する。",
            "接続を後回しにする。",
        )
        for prose in prose_values:
            with self.subTest(prose=prose):
                plan = load_fixture("good-runtime.json")
                plan["implementation_options"].append(prose)
                plan["selected_implementation"] = prose
                plan["remaining_diff"][0] = prose
                plan["validation"][0] = prose
                plan["attachment_points"][0]["registration_point"] = prose
                plan["milestones"][1]["description"] = prose
                self.assertEqual(lint_plan(plan), [])

    def test_structured_first_milestone_rejection_remains_enforced(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["milestones"][0]["kind"] = "design"
        errors = lint_plan(plan)
        self.assertTrue(any("first milestone" in error for error in errors), errors)

    def test_structured_wiring_delay_remains_rejected(self) -> None:
        plan = load_fixture("good-runtime.json")
        plan["runtime_wiring"] = "deferred"
        errors = lint_plan(plan)
        self.assertTrue(any("runtime_wiring: required" in error for error in errors), errors)

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

    def test_deeply_nested_value_returns_a_finding_without_recursing(self) -> None:
        nested: object = "leaf"
        for _ in range(1200):
            nested = {"next": nested}
        plan = load_fixture("good-runtime.json")
        plan["validation"] = nested
        self.assertEqual(
            lint_plan(plan),
            ["validation must be a non-empty list of non-empty strings"],
        )

    def test_malformed_fill_order_does_not_compare_deep_values(self) -> None:
        nested_id: object = "leaf"
        nested_order: object = "leaf"
        for _ in range(1200):
            nested_id = {"next": nested_id}
            nested_order = {"next": nested_order}
        plan = load_fixture("good-runtime.json")
        plan["milestones"][0]["id"] = nested_id
        plan["next_fill_order"][0] = nested_order
        errors = lint_plan(plan)
        self.assertTrue(any("next_fill_order" in error for error in errors), errors)
        self.assertTrue(any("milestone.id" in error for error in errors), errors)

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

    def test_cli_deeply_nested_value_emits_a_bounded_finding(self) -> None:
        nested_json = '{"next":' * 1200 + '"leaf"' + "}" * 1200
        plan = load_fixture("good-runtime.json")
        plan["validation"] = "__DEEP_VALUE__"
        payload = json.dumps(plan).replace('"__DEEP_VALUE__"', nested_json, 1)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            result = subprocess.run(
                [sys.executable, str(LINTER), stream.name],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertIn(result.returncode, (1, 2), result.stderr)
        if result.returncode == 1:
            self.assertEqual(
                result.stdout,
                "verdict: repair_then_proceed\n"
                "- validation must be a non-empty list of non-empty strings\n",
            )
            self.assertEqual(result.stderr, "")
        else:
            self.assertEqual(result.stdout, "")
            self.assertEqual(
                result.stderr,
                "verdict: blocked\nerror: plan nesting exceeds supported depth\n",
            )
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_cli_blocks_json_loading_recursion_without_a_traceback(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as stream:
            stream.write("{}")
            stream.flush()
            stdout = StringIO()
            stderr = StringIO()
            with mock.patch.object(
                lint_plan_module.json,
                "loads",
                side_effect=RecursionError,
            ):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    returncode = lint_plan_module.main([stream.name])
        self.assertEqual(returncode, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(
            stderr.getvalue(),
            "verdict: blocked\nerror: plan nesting exceeds supported depth\n",
        )
        self.assertNotIn("Traceback", stdout.getvalue() + stderr.getvalue())

    def test_cli_blocks_lint_traversal_recursion_without_a_traceback(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as stream:
            json.dump(load_fixture("good-runtime.json"), stream)
            stream.flush()
            stdout = StringIO()
            stderr = StringIO()
            with mock.patch.object(
                lint_plan_module,
                "lint_plan",
                side_effect=RecursionError,
            ):
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    returncode = lint_plan_module.main([stream.name])
        self.assertEqual(returncode, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(
            stderr.getvalue(),
            "verdict: blocked\nerror: plan nesting exceeds supported depth\n",
        )
        self.assertNotIn("Traceback", stdout.getvalue() + stderr.getvalue())

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
