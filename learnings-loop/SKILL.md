---
name: learnings-loop
description: >
  Captures a structured learning after a completed task, or surfaces relevant
  past learnings before starting a new one. Each learning lives in its own
  topic-focused file in Main/learnings/. Before creating a new file, Claude
  checks for an existing file on the same topic and merges. No user input
  required in Capture Mode. /learnings-loop review surfaces past learnings
  before a task and validates them after. All output is a short narrative.
version: 0.6.0
---

## Overview

The Learnings Loop runs in two modes:

- **Capture** (default): Claude self-assesses the just-completed task, finds
  the right file to write to (merging if a similar one exists, creating if not),
  and narrates the result. No questions asked.
- **Review**: surfaces relevant past learnings as advice before a task, then
  asks for a one-word verdict after to validate or correct them.

Both modes produce output as a short story — one paragraph, no lists.

The learnings store is `Main/learnings/` — one `.md` file per topic,
named in kebab-case after the topic it covers.

---

## File Format

```markdown
# <Topic Title>

*Last updated: YYYY-MM-DD · Status: <unproven | proven | disproven> · Friction: <smooth | bumpy | blocked>*

## Next time
<One concrete action to avoid friction. The most important section.>

## Proved by
<The situation that validated this learning — what task, what happened, what confirmed it.
Write "Not yet validated in practice." if status is unproven.>

## What works
<The single most important insight that helped.>

## What doesn't work
<Main friction point or wrong turn. Omit this section entirely if friction was smooth.>

## History

### YYYY-MM-DD — <brief label, e.g. "first encounter (bumpy)">
<Approach: what was done, 1–2 sentences.>
*`id: <ISO-8601 timestamp>`*
```

History is newest-first. The top sections always reflect the latest understanding.

**Status rules:**
- New entry always starts as `unproven`.
- Becomes `proven` when Review Mode Phase B confirms the approach held up.
- Becomes `disproven` when a new capture corrects it (update the old file's
  status and `Proved by` to explain what didn't hold).

---

## Capture Mode

Run this after completing a task. Claude infers everything from the conversation.

### Step 1: Self-assess from the conversation

Extract:

- **topic**: subject domain as a noun phrase suitable for a file title
  (e.g. "Claude Code Plugin Installation", "TypeScript Refactor Patterns")
- **filename**: kebab-case of topic + `.md`
- **approach**: what was done — tools, files, key decisions (1–2 sentences)
- **friction_level**: inferred from redos, corrections, or wrong turns:
  - `smooth` — no significant backtracking
  - `bumpy` — at least one redo or correction needed
  - `blocked` — could not complete, or required major replanning
- **what_worked**: single most important insight that helped
- **what_didnt_work**: main friction point or wrong turn (omit if smooth)
- **next_time**: one concrete action to avoid the friction. Generalize one
  level above the exact incident so it applies to future similar work, not only
  this specific bug. Keep it specific enough to act on. If the first draft names
  a one-off file, version, command, or dependency, check whether the underlying
  lesson is about design intent, dependency boundaries, verification order, tool
  choice, or communication. The most important field. (omit if smooth)
- **tech_tags**: version-pinned stack labels inferable from context; omit if none
- **id**: from `date -u +"%Y-%m-%dT%H:%M:%SZ"`

### Step 2: Find or create the file

Scan `Main/learnings/` for existing files.

**If a file on the same topic exists**: update it.
1. Replace `## Next time` content with the new `next_time`.
2. Replace `## What works` content with the new `what_worked`.
3. Update or remove `## What doesn't work` (omit entirely if smooth).
4. Set `## Proved by` to "Not yet validated in practice." (new encounter
   resets proof — the old approach may have changed).
5. Update the frontmatter line: new date, `Status: unproven`, new friction.
6. Prepend a new history entry at the top of `## History`.

**If no similar file exists**: create `Main/learnings/<filename>.md` using
the full template. Status is always `unproven` on creation.

Run `mkdir -p Main/learnings` if needed.

### Step 3: Narrate (the story)

Write one short paragraph — 3 to 5 sentences, no headers, no bullet points.

- New file: open with **"Captured."**
- Existing file updated: open with **"Updated the [topic] learning."**

Tell the story: what the task was, how it went, what the key insight is.
If there was friction, name it in one sentence. End with the `next_time`
insight. Omit if smooth.

---

## Review Mode

### Phase A — Before the task: surface past learnings

#### Step 1: Scan the store

List all `.md` files in `Main/learnings/`. If absent or empty:

> "No learnings recorded yet. Complete a task and run /learnings-loop to
> start building the store."

Stop here.

#### Step 2: Filter and prioritise

1. Read files whose names suggest relevance to the current task. If unclear,
   read the 5 most recently updated.
2. Skip files with `Status: disproven`.
3. Rank by: `proven` first, then `unproven` ordered by recency. Drop files
   older than ~6 months with `Status: unproven` (stale theory, not worth
   surfacing without validation).

#### Step 3: Narrate (the story)

Write one paragraph under 100 words — no headers, no bullets.

Start with **"Before you begin."** Synthesize the top `## Next time` sections
into concrete advice. If the top learnings are `proven`, say so briefly — it
signals they're battle-tested. If they're `unproven`, flag them as first-
encounter theory. Do not list files — synthesize into guidance.

### Phase B — After the task: validate

Once the task is done, ask exactly one question:

> "Did the recalled approach hold up in practice? (yes / partially / no)"

- **yes**: update the relevant file — set `Status: proven` and write a brief
  `Proved by` note (this task, what confirmed it). Tell the user in one
  sentence.
- **partially** or **no**: run Capture Mode on the relevant file. Set the
  old file's `Status: disproven` and update its `Proved by` to explain what
  didn't hold. The new history entry corrects the guidance.

### Health check

Check `Friction: blocked` across the 10 most recently updated files. If
more than 4:

> **Health signal:** more than 40% of recent runs hit blockers. The underlying
> workflow may need attention — more learnings alone won't fix a broken process.

---

## Output rules (both modes)

- Never dump raw file content to the user.
- Never use bullet lists or headers in user-facing output.
- Never ask questions in Capture Mode.
- One question maximum, in Review Mode Phase B only.
- Keep all user-facing text to one or two short paragraphs.
- Never invent tech tags.
- Never delete files or history entries. Correct by updating top sections,
  prepending a history entry, and updating Status.
