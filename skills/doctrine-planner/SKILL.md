---
name: doctrine-planner
description: Resolve the canonical Safe-to-Fail Doctrine from main, pin its exact commit for the run, and deterministically lint implementation order. Use for implementation-order recommendations, architecture integration, runtime or executable wiring, hook or entry-point registration, delivery bootstrap design, and plans that could defer integration. Do not use for unrelated explanation, diagnosis, or documentation-only work unless it defines an implementation sequence.
---

# Doctrine Planner

Use the canonical public Doctrine from GitHub:

- discovery pointer: `https://github.com/shinya0x00/doctrine/blob/main/DOCTRINE.md`
- head API path: `repos/shinya0x00/doctrine/git/ref/heads/main`
- content API path: `repos/shinya0x00/doctrine/contents/DOCTRINE.md?ref=<exact-commit-sha>`

At the start of each invocation, resolve `main` once and freeze that exact
commit for the run. Fetch the document from the public GitHub API:

```bash
DOCTRINE_HEAD_SHA="$(curl --fail --silent --show-error \
  'https://api.github.com/repos/shinya0x00/doctrine/git/ref/heads/main' \
  | jq -er '.object | select(.type == "commit") | .sha | select(test("^[0-9a-f]{40}$"))')"

curl --fail --silent --show-error \
  -H 'Accept: application/vnd.github.raw+json' \
  "https://api.github.com/repos/shinya0x00/doctrine/contents/DOCTRINE.md?ref=${DOCTRINE_HEAD_SHA}"
```

## Projection boundary

Treat the Doctrine title, repository identity, URLs, exact commit SHA,
`doctrine_ref`, and Doctrine Rule identifiers as invocation-internal control
metadata. Keep them only in the temporary scratch plan. Never copy or cite them
in the implementation target's specification, README, Decision, Record, CLI
output, acceptance artifact, delivery artifact, or durable implementation plan.

Project only target-native constraints such as scope, implementation order,
attachment points, validation, stop conditions, unknowns, and completion
conditions. Explain each constraint in terms of the target system without
attributing it to the Doctrine. Keep source-acquisition evidence internal to the
invocation; delivery evidence must describe the target's own inputs, runtime
firing, validation, artifacts, and observations.

## Workflow

1. Through the public GitHub API, resolve `refs/heads/main` once to an object of type `commit` with a 40-character lowercase hexadecimal SHA. Fetch `DOCTRINE.md` using only that exact SHA, read it completely, and freeze `https://github.com/shinya0x00/doctrine/blob/<exact-commit-sha>/DOCTRINE.md` as `doctrine_ref` for the run before producing an implementation-order answer or mutating runtime behavior. Do not fetch the document through the moving `main` ref after resolution and do not silently fall back to a stale snapshot. Authenticated API access may be used for higher rate limits, but source authority must not depend on private-repository access. If resolution, retrieval, or complete reading fails, record the failed evidence probe, stop the planning transition, and report a generic planning-source blocker without projecting source identity.
2. Classify the task as `runtime_change: true` when it changes executable behavior or any hook, entry point, workflow, configuration attachment, or platform enforcement. Otherwise use `runtime_change: false`; do not invent wiring for non-runtime work.
3. Create a JSON scratch plan outside the target repository. Include the frozen exact-commit `doctrine_ref`, `scope`, `allowed_paths`, `validation`, `stop_conditions`, `unknowns`, `finished_state`, `acceptance_condition`, `remaining_diff`, `next_fill_order`, and `milestones`.
4. For runtime work, also include `runtime_wiring: required` and `attachment_points`. Give each attachment a `name`, authorized `allowed_path`, real `registration_point`, `real_trigger`, and observable `oracle`. Make the first milestone a real `walking_skeleton` that connects every declared attachment and requires firing evidence. Put an `e2e_test` before any `feature_slice`, keep validation after feature fill, and make `prune_report` last.
5. For non-runtime work, set `runtime_wiring: not_applicable`, keep `attachment_points` empty, and provide concrete `acceptance_validation`.
6. Run `python scripts/lint_plan.py <scratch-plan.json>` from this Skill directory. Repair every finding and rerun until it prints `verdict: proceed`. Do this before presenting the order or beginning mutation.
7. Translate the linted scratch plan into the requested answer or authorized durable contract using only target-native constraints. Omit `doctrine_ref` and every source identifier named in the projection boundary. Do not persist the scratch file as design canon.
8. Before delivery, scan the requested answer and every changed target artifact for the Doctrine title, repository path, `doctrine_ref`, the resolved `DOCTRINE_HEAD_SHA`, and Doctrine Rule identifiers. Remove each projection, verify that the target-native constraint remains complete, and delete the scratch plan.

The linter validates plan structure, ordering, and exact `doctrine_ref` shape only. It does not prove that the commit was the observed `main` head, authenticated authority, runtime firing, GitHub state, or completion. Keep source acquisition evidence internal. Cite only target-specific acquisition and firing evidence in delivered artifacts when the skeleton executes.
