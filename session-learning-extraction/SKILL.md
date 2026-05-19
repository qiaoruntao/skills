---
name: session-learning-extraction
description: >
  Use this skill when the user asks to read, review, analyze, compare, or learn
  from past Codex, Claude, or other LLM sessions to extract reusable lessons,
  bumpy interaction patterns, best practices, rules, checklists, or future
  skills. This skill owns the analysis workflow after session access is
  available; pair it with local-llm-sessions when local transcripts must be
  fetched.
---

# Session Learning Extraction

Use this skill to turn session history into durable operational learning. The
goal is not to summarize transcripts. The goal is to find repeated friction or
success patterns and convert them into future behavior.

Related working notes may exist in a local repository's `learnings/` directory,
but this public skill should not depend on private note paths. Treat any such
notes as optional background, not as required inputs.

## Scope Claim

This skill covers extracting and organizing reusable lessons from past AI
sessions.

It does not own:

- raw session access or transcript parsing; use `local-llm-sessions` for that;
- implementing the eventual fix skill/checklist;
- scoring sessions for its own sake;
- archiving or moving unrelated KB files.

## Do Not

Do not dump raw transcripts unless the user explicitly asks. Session review
should produce synthesized patterns, representative examples, and actionable
next steps.

Do not treat every correction as a durable lesson. Promote only repeated,
costly, or clearly reusable patterns.

Do not mix unrelated bump categories into one fix. Split categories when each
one needs a different rule, checklist, or skill.

Do not overfit to one session. If the pattern appears only once, mark it as a
candidate or test case rather than a proven rule.

Do not make a numeric bumpy score the main output unless the user specifically
asks for scoring. Identification and resolution opportunities matter more.

Do not create a strict universal pipeline when the correct future procedure is
not known. Prefer "what to avoid", success/failure conditions, and lightweight
preflight checks.

## Review Procedure

1. Define the review scope.
   Why: vague sampling creates vague conclusions.
   What to do: record provider(s), max sessions, project roots, time window, and
   whether sidechains/subagents are included.

2. Read human turns first.
   Why: user corrections reveal friction most directly.
   What to do: look for redirection, repeated questions, "not the case",
   "prove it", "why", "patch not fix", tool corrections, and process
   complaints.

3. Classify bumps by type.
   Why: each bump type needs a different durable solution.
   What to do: separate at least direction, evidence, tool, process, scope,
   memory, and solution-quality bumps.

4. Group by task family.
   Why: reusable fixes usually attach to task families, not individual sessions.
   What to do: group examples such as production debugging, deploy/release,
   project memory, named-source handling, and causal fix quality.

5. Convert clear-goal bumps into contracts.
   Why: a future session can check a contract before acting.
   What to do: write goal, failure looks like, success looks like, preflight
   check, possible procedure, verification, and where to encode.

6. Split resolution files when needed.
   Why: non-trivial bump families need independent thinking and iteration.
   What to do: create one focused note per category when it may become a skill,
   checklist, or project rule.

7. Promote behavior only after choosing the right home.
   Why: learnings explain why; skills change runtime behavior.
   What to do: keep rationale/history in `learnings/`; put reusable agent
   behavior in `skills/`; put broad repo behavior in `AGENTS.md`; put
   system-specific facts in project docs.

## Output Shape

For a review pass, report:

- review scope;
- recurring bump categories;
- representative examples without transcript dumps;
- clear-goal resolution candidates;
- proposed files or skills to create/update;
- open uncertainties.

For each category note, use:

```text
Problem:
Goal:
Failure looks like:
Success looks like:
Dreaming check:
Procedure or guardrails:
Candidate durable asset:
```

## Linkage Rule

When a learning produces a skill:

- the learning links forward to the skill path;
- the skill links back to the learning path;
- the learning records rationale, examples, and validation history;
- the skill stays short and only contains runtime behavior.
