---
name: commit
description: >
  Commits code changes to a git repository using a Haiku subagent. Use this
  skill whenever the user wants to commit — phrases like "let's commit",
  "commit this", "commit the auth changes", "go ahead and commit", "time to
  commit", "push a commit", "save my changes to git". Also triggers when the
  user finishes describing a change and says something like "ok ship it" or
  "done, commit it". The skill handles staging the right files based on intent,
  updating .gitignore for files that shouldn't be tracked, and writing a
  commit message — the user doesn't need to think about any of that.
---

## Overview

When the user wants to commit, you gather context from the conversation and
the repo, then delegate all the git work to a Haiku subagent. Haiku inspects
repo state, stages the right files, updates `.gitignore` when appropriate,
writes a commit message, and commits. You relay the result.

## Step 1: Gather context

Run these two commands:

```bash
pwd
git branch --show-current
```

Then extract from the conversation:

- **intent** — the user's words about what they want to commit, verbatim or
  lightly paraphrased. This is the most important input: it tells Haiku which
  files belong in this commit and what the commit message should say.
- **need_commit_ref** — `true` if the conversation implies a follow-up that
  needs the commit SHA or message (e.g. "then we'll make a PR", "then push
  it", "I'll reference this commit"). Otherwise `false`.

## Step 2: Spawn Haiku subagent

Spawn an Agent with `model: "haiku"`. Pass this prompt with the bracketed
values filled in:

---

You are handling a git commit in the repo at **[repo_path]** on branch **[branch]**.

**User's intent:** "[intent]"

Follow these steps in order:

1. Run `git status` to see all staged, unstaged, and untracked files.

2. Based on the intent, decide which unstaged/untracked files belong in this
   commit and stage them with `git add`. Leave unrelated files alone. When a
   source file is clearly related to the intent, include it. When in doubt
   about an untracked file, ask yourself: "Would a developer expect this in a
   commit about [intent]?" If yes, stage it.

3. For untracked files that clearly should NOT be committed — build artifacts,
   compiled outputs, tmp files, logs, `.DS_Store`, credentials/secrets — add
   them to `.gitignore` instead of staging. Only gitignore things that are
   obviously not meant to be tracked; don't silently ignore files that might
   be intentional additions.

4. Run `git diff --staged --stat` to confirm what's staged.

5. Write a commit message that captures the intent:
   - Imperative mood: "Add", "Fix", "Update" — not "Added" or "Fixes"
   - Subject line ≤72 characters
   - If the change is substantial, add a blank line followed by a brief
     bullet list of what changed

6. Run `git commit -m "..."` with your message.

[If need_commit_ref is true:]
Return the short commit SHA (first 8 chars) and the commit message you used.

[If need_commit_ref is false:]
On success, reply only: "Committed successfully."
On failure, return the error exactly as-is — no retry.

---

## Step 3: Relay the result

- **Success, need_commit_ref false**: brief confirmation to the user.
- **Success, need_commit_ref true**: tell the user the SHA and message so they
  can use them in the follow-up (PR, push, etc.).
- **Failure**: surface the raw error. Do not retry — let the user decide how
  to proceed.
