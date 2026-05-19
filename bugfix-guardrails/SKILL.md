---
name: bugfix-guardrails
description: >
  Use this skill when debugging, investigating, or fixing a non-trivial software
  issue where shallow action would be risky: production bugs, regressions, core
  service logic, accounting or budget logic, observability/logging behavior,
  concurrency/state machines, library abstractions, or any case where the user
  asks for root cause, proof, evidence, not just a patch, or says "patch not
  fix".
---

# Bugfix Guardrails

Use this skill to prevent known bad debugging and fixing behavior. The exact
correct procedure depends on the system, so this skill focuses on what not to do
and on lightweight checks that keep the session honest.

Related rationale and evaluation notes may exist in a local repository's
`learnings/` directory, but this public skill should not depend on private note
paths. Treat any such notes as optional background, not as required inputs.

## Scope Claim

This skill covers solution-quality bumps: preventing shallow or unsupported
fixes during non-trivial debugging.

It does not own the full debugging session. Use other project rules, skills, or
checklists for:

- production evidence workflow, such as SigNoz logs, traces, dashboards, time
  windows, and deployed-version proof;
- release/deploy sequencing, such as dirty state, commit-before-build, embedded
  hash, restart, and runtime verification;
- named tool and context-source loading, such as MCPs, plugins, `AGENTS.md`,
  `CLAUDE.md`, skill paths, dashboards, and docs;
- broad session phase control, such as when to stop at investigation, write a
  plan, implement, document, or deploy.

## Do Not

Do not start coding while these are unclear:

- exact symptom and expected behavior;
- source of truth for evidence;
- system invariant, contract, or design intent at risk;
- why the proposed change is more than a symptom patch;
- how the result will be checked.

Do not present a causal claim as fact without evidence. Label it as a hypothesis
until it has an observation, test, trace, log, fixture, dashboard query, or other
source of truth behind it.

Do not assume the location of the fix is the root cause. A bug can be triggered
in one place, exposed in another, and caused by a contract or state violation
elsewhere.

Do not use caps, resets, fallbacks, retries, or filters as the final fix unless
they are tied to the demonstrated mechanism or explicitly accepted as a
workaround.

Do not bypass library or module abstractions before checking their design intent,
upstream behavior, and existing callers.

Do not treat a passing check as proof unless it would have failed before the
fix, or unless it directly verifies the risky behavior.

Do not collapse complex failures into a fake single root cause. Keep trigger,
proximate cause, deeper cause, and contributing factors separate when needed.

## Minimum Checks

Before changing code, try to write down:

- symptom: what happened and what should have happened;
- evidence: where that is observed;
- risk: what invariant, contract, or design intent may be broken;
- candidate fix: why it addresses the mechanism rather than only the symptom;
- verification: what check would catch the bug or risky behavior.

If any item is unknown, investigate that item first. If the user wants speed over
certainty, state the missing item and label the action as a workaround.

## Useful Moves

- Reproduce or anchor the failure before fixing when practical.
- Use hypotheses with predictions instead of open-ended searching.
- Use bisection or input minimization when the failure boundary is unclear.
- Preserve module and library abstractions unless there is evidence they are
  wrong.
- Add or update a regression guard when practical.
- Check nearby callers, data shape, concurrency/state, config, compatibility,
  observability, and deployment implications.

## Reporting Back

When done, report the symptom/evidence, what was changed, why it is not merely a
symptom patch, what verification ran, and what risk remains.
