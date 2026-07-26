#!/usr/bin/env python3
"""Deterministically lint implementation-plan structure, selection, and ordering."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


DOCTRINE_REF_PATTERN = re.compile(
    r"\Ahttps://github\.com/shinya0x00/doctrine/blob/"
    r"[0-9a-f]{40}/DOCTRINE\.md\Z"
)
DEFERRED_WIRING_PATTERN = re.compile(
    r"\b(?:connect|wire|attach|register|integrat(?:e|ion))\b.{0,48}"
    r"\b(?:later|eventually|future|afterwards|subsequent\s+phase)\b|"
    r"\b(?:later|eventually|future|subsequent\s+phase)\b.{0,48}"
    r"\b(?:connect|wire|attach|register|integrat(?:e|ion))\b|"
    r"(?:接続|結線|登録|統合|組み込|取り付け).{0,24}"
    r"(?:後で|後から|後ほど|将来|後続(?:の)?(?:フェーズ|段階))|"
    r"(?:後で|後から|後ほど|将来|後続(?:の)?(?:フェーズ|段階)).{0,24}"
    r"(?:接続|結線|登録|統合|組み込|取り付け)",
    re.IGNORECASE,
)
NEGATED_DEFERRED_WIRING_PATTERN = re.compile(
    r"\b(?:no|without)\s+(?:future|later|eventual)\s+"
    r"(?:connection|wiring|attachment|registration|integration)"
    r"(?:\s+(?:remains?|is\s+(?:planned|allowed|required)))?\b|"
    r"\b(?:future|later|eventual)\s+"
    r"(?:connection|wiring|attachment|registration|integration)\s+"
    r"is\s+(?:not|never)\s+(?:planned|allowed|required)\b|"
    r"(?:後で|後から|後ほど|将来|後続(?:の)?(?:フェーズ|段階)).{0,24}"
    r"(?:接続|結線|登録|統合|組み込|取り付け)"
    r"(?:しない|しません|させない|"
    r"(?:する)?(?:工程|作業|手順|予定|余地)(?:は|を|が)?"
    r"(?:残さない|残っていない|禁止する)|"
    r"(?:は|を|が)?(?:残さない|残っていない|禁止する|不要である))",
    re.IGNORECASE,
)


def _deferred_wiring_paths(value: Any, path: str) -> list[str]:
    if isinstance(value, str):
        executable_text = NEGATED_DEFERRED_WIRING_PATTERN.sub("", value)
        return [path] if DEFERRED_WIRING_PATTERN.search(executable_text) else []
    if isinstance(value, list):
        return [
            match
            for index, item in enumerate(value)
            for match in _deferred_wiring_paths(item, f"{path}[{index}]")
        ]
    if isinstance(value, dict):
        return [
            match
            for item in value.values()
            for match in _deferred_wiring_paths(item, path)
        ]
    return []


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and any(
        not character.isspace() and unicodedata.category(character) != "Cf"
        for character in value
    )


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(_nonempty_string(item) for item in value)
    )


def lint_plan(plan: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["plan must be a JSON object"]

    for field in ("scope", "finished_state", "acceptance_condition"):
        if not _nonempty_string(plan.get(field)):
            errors.append(f"{field} must be a non-empty string")
    for field in (
        "allowed_paths",
        "validation",
        "stop_conditions",
        "invariants",
        "implementation_options",
        "remaining_diff",
        "next_fill_order",
    ):
        if not _nonempty_string_list(plan.get(field)):
            errors.append(f"{field} must be a non-empty list of non-empty strings")

    milestones = plan.get("milestones")
    if not isinstance(milestones, list) or not milestones:
        errors.append("milestones must be a non-empty list")

    implementation_options = plan.get("implementation_options")
    if _nonempty_string_list(implementation_options) and len(
        implementation_options
    ) != len(set(implementation_options)):
        errors.append("implementation_options must be unique")
    selected_implementation = plan.get("selected_implementation")
    if not _nonempty_string(selected_implementation):
        errors.append("selected_implementation must be a non-empty string")
    elif (
        isinstance(implementation_options, list)
        and implementation_options
        and selected_implementation not in implementation_options
    ):
        errors.append("selected_implementation must exactly match one implementation option")
    complexity_justification = plan.get("complexity_justification")
    if (
        complexity_justification != "none_observed"
        and not _nonempty_string_list(complexity_justification)
    ):
        errors.append(
            "complexity_justification must be 'none_observed' or a non-empty string list"
        )

    doctrine_ref = plan.get("doctrine_ref")
    if not _nonempty_string(doctrine_ref) or not DOCTRINE_REF_PATTERN.fullmatch(doctrine_ref):
        errors.append(
            "internal source reference must be an exact pinned commit URL"
        )
    if "unknowns" not in plan:
        errors.append("unknowns must be present")
    elif plan["unknowns"] != "none_observed" and not _nonempty_string_list(plan["unknowns"]):
        errors.append("unknowns must be 'none_observed' or a non-empty string list")
    if not isinstance(plan.get("runtime_change"), bool):
        errors.append("runtime_change must be boolean")

    deferred_paths = (
        sorted(
            {
                match
                for field in (
                    "selected_implementation",
                    "remaining_diff",
                    "validation",
                    "attachment_points",
                    "milestones",
                )
                for match in _deferred_wiring_paths(plan.get(field), field)
            }
        )
        if plan.get("runtime_change") is True
        else []
    )
    if deferred_paths:
        errors.append(
            "deferred wiring language is forbidden in active execution fields: "
            + ", ".join(deferred_paths)
        )

    if not isinstance(milestones, list) or not milestones:
        return errors
    if not all(isinstance(item, dict) for item in milestones):
        errors.append("every milestone must be an object")
        return errors

    ids = [item.get("id") for item in milestones]
    if not all(_nonempty_string(item) for item in ids):
        errors.append("every milestone.id must be a non-empty string")
    elif len(ids) != len(set(ids)):
        errors.append("milestone ids must be unique")
    kinds = [item.get("kind") for item in milestones]
    if not all(_nonempty_string(item) for item in kinds):
        errors.append("every milestone.kind must be a non-empty string")
    if isinstance(plan.get("next_fill_order"), list) and plan["next_fill_order"] != ids:
        errors.append("next_fill_order must exactly match milestone id order")

    if plan.get("runtime_change") is False:
        if plan.get("runtime_wiring") != "not_applicable":
            errors.append("non-runtime plans require runtime_wiring: not_applicable")
        if plan.get("attachment_points") not in (None, []):
            errors.append("non-runtime plans must not declare attachment_points")
        if not _nonempty_string_list(plan.get("acceptance_validation")):
            errors.append("non-runtime plans require concrete acceptance_validation")
        return errors

    if plan.get("runtime_change") is not True:
        return errors
    if plan.get("runtime_wiring") != "required":
        errors.append("runtime plans require runtime_wiring: required")

    attachments = plan.get("attachment_points")
    if not isinstance(attachments, list) or not attachments:
        errors.append("runtime plans require at least one attachment point")
        attachments = []
    allowed_paths = plan.get("allowed_paths") if isinstance(plan.get("allowed_paths"), list) else []
    attachment_names: list[str] = []
    for index, attachment in enumerate(attachments):
        if not isinstance(attachment, dict):
            errors.append(f"attachment_points[{index}] must be an object")
            continue
        for field in ("name", "allowed_path", "registration_point", "real_trigger", "oracle"):
            if not _nonempty_string(attachment.get(field)):
                errors.append(f"attachment_points[{index}].{field} must be a non-empty string")
        name = attachment.get("name")
        if _nonempty_string(name):
            attachment_names.append(name)
        path = attachment.get("allowed_path")
        if _nonempty_string(path) and path not in allowed_paths:
            errors.append(f"attachment_points[{index}].allowed_path is outside allowed_paths")
    if len(attachment_names) != len(set(attachment_names)):
        errors.append("attachment point names must be unique")

    first = milestones[0]
    if first.get("kind") != "walking_skeleton":
        errors.append("the first milestone must be kind: walking_skeleton")
    if first.get("real_wiring") is not True:
        errors.append("the walking skeleton must set real_wiring: true")
    if first.get("firing_evidence_required") is not True:
        errors.append("the walking skeleton must require observed firing evidence")
    if not _nonempty_string(first.get("evidence_owner")):
        errors.append("the walking skeleton must name its evidence_owner")
    connects = first.get("connects")
    if not _nonempty_string_list(connects):
        errors.append(
            "the walking skeleton must connect every declared attachment exactly once "
            "using a non-empty string list"
        )
    elif len(connects) != len(set(connects)) or set(connects) != set(attachment_names):
        errors.append("the walking skeleton must connect every declared attachment exactly once")
    depth = first.get("feature_depth")
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0:
        errors.append("walking_skeleton.feature_depth must be a non-negative integer")

    feature_indexes = [index for index, kind in enumerate(kinds) if kind == "feature_slice"]
    e2e_indexes = [index for index, kind in enumerate(kinds) if kind == "e2e_test"]
    if feature_indexes and (not e2e_indexes or e2e_indexes[0] > feature_indexes[0]):
        errors.append("an e2e_test milestone must precede the first feature_slice")
    verification_indexes = [index for index, kind in enumerate(kinds) if kind == "verification"]
    if not verification_indexes:
        errors.append("runtime plans require a verification milestone")
    elif feature_indexes and verification_indexes[-1] < feature_indexes[-1]:
        errors.append("final verification must follow feature fill")
    if kinds.count("prune_report") != 1 or kinds[-1] != "prune_report":
        errors.append("runtime plans require exactly one final prune_report milestone")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="JSON scratch plan to lint")
    args = parser.parse_args(argv)
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"verdict: blocked\nerror: {error}", file=sys.stderr)
        return 2

    errors = lint_plan(plan)
    if errors:
        print("verdict: repair_then_proceed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("verdict: proceed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
