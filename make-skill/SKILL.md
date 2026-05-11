---
name: make-skill
description: >
  Create or revise a Codex skill when the user wants a new skill, wants to
  improve an existing skill, or wants a skill rewritten to be shorter, more
  decisive, and more reusable. Keep the workflow high-level and focus only on
  the minimum steps that change the skill's usefulness.
---

# Make Skill

Use this skill when writing or revising another skill. Keep it short. Skip
generic process and only keep the steps that materially improve trigger
quality or runtime behavior.

## Steps

1. Pin down the trigger and job.
   Why: a skill is only useful if it fires for the right requests and solves
   one clear job.
   What to do: write the `name` and `description` so they say when to use the
   skill, what outcome it owns, and what nearby requests should trigger it.

2. Keep only non-removable steps.
   Why: long skills decay into boilerplate and hide the actual decision path.
   What to do: reduce the workflow to the smallest set of steps that would have
   changed a bad outcome. Skip common engineering knowledge the model already
   knows.

3. Write each step as `Why` and `What to do`.
   Why: this keeps the skill concise without losing decision quality.
   What to do: for each remaining step, state the release-critical or
   task-critical reason first, then the concrete action.

4. Push details out unless they are core.
   Why: the main skill body should stay fast to load.
   What to do: keep `SKILL.md` high-level. Add scripts, references, or assets
   only when they remove repeated work or encode fragile logic.

5. Revise from real failure, not hypothetical completeness.
   Why: the best skills come from the exact place the previous version was too
   vague, too long, or too trusting.
   What to do: compare the skill against the last real task, remove steps that
   did not affect the outcome, and add the one that would have prevented the
   mistake.

## Rules

- Prefer fewer steps.
- Do not explain basics the model already knows.
- If a step does not change the decision, remove it.
- If a detail is only an example, keep it short or drop it.
