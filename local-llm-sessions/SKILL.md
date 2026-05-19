---
name: local-llm-sessions
description: Read, list, search, and fetch local AI coding assistant conversation history from Claude Code, Codex CLI, Gemini CLI, OpenCode, Antigravity, Cline, Cursor, Aider, and ForgeCode. Use when Codex needs to inspect local LLM sessions, compare provider history, recover prior conversation content, list recent sessions, fetch message transcripts, or understand raw local session storage formats.
---

# Local LLM Sessions

## Core Rule

Use the local CCHV server API first. It normalizes multiple providers into the same project/session/message shape and avoids fragile direct parsing of vendor-specific files.

Default local service:

- URL: `http://127.0.0.1:3727`
- Optional PM2 process name: `cchv-server`
- Auth token source: `CCHV_TOKEN` environment variable, or pass `--token`

If the API is unavailable and the user manages CCHV with PM2, start or inspect it with:

```bash
pm2 status cchv-server
pm2 logs cchv-server --lines 100
```

Do not scan every provider by default. Use provider filters and request timeouts; some providers can be slow on large local trees.

## Quick Start

Use the bundled script for routine reads:

```bash
python3 skills/public/local-llm-sessions/scripts/cchv_sessions.py providers
python3 skills/public/local-llm-sessions/scripts/cchv_sessions.py projects --provider codex
python3 skills/public/local-llm-sessions/scripts/cchv_sessions.py sessions --provider claude --project-path '<project path>'
python3 skills/public/local-llm-sessions/scripts/cchv_sessions.py messages --provider codex --session-path '<session file path>' --transcript
```

When installed as a Codex skill, use the installed skill path instead of the
repository path above.

Prefer `--transcript` when the user wants readable conversation content. The default transcript is a human/debug view: it skips developer/system boilerplate, permission blocks, app context, progress/attachment records, and truncates huge tool outputs.

Use these transcript controls when debugging interaction quality:

- `--forensic`: preserve boilerplate and full tool output.
- `--no-tools`: show only human/assistant text and thinking, hiding tool calls/results.
- `--no-thinking`: hide thinking blocks.
- `--max-tool-chars 0`: do not truncate tool blocks.

Use raw JSON when they need exact fields, complete tool payloads, or provider-specific metadata.

## API Workflow

1. Resolve auth token.
2. Check `GET /health`.
3. List projects for one provider:
   `POST /api/scan_all_projects` with `{"activeProviders":["codex"]}`.
4. Pick a project `path`.
5. List sessions:
   `POST /api/load_provider_sessions` with `{"provider":"codex","projectPath":"...","excludeSidechain":false}`.
6. Pick a session `file_path`.
7. Fetch messages:
   `POST /api/load_provider_messages` with `{"provider":"codex","sessionPath":"..."}`.

Provider ids observed in CCHV: `claude`, `codex`, `gemini`, `antigravity`, `opencode`, `cline`, `cursor`, `aider`, `forgecode`.

## Message Handling

Normalized messages commonly include:

- `provider`
- `type`
- `role`
- `timestamp`
- `uuid`
- `sessionId`
- `parentUuid`
- `content`
- `toolUse`
- `toolUseResult`
- provider-specific extras such as `data`, `usage`, or `toolUseID`

When building transcripts:

- Preserve ordering returned by the API.
- Include timestamps and provider when useful.
- Treat `content` as JSON-like: it may be a string, object, list of text blocks, or null.
- Default to the human/debug transcript for understanding how the user and model interacted.
- Filter environment boilerplate unless the user asks for forensic reconstruction.
- Include tool calls/results only when the user asks for tool activity or when they explain the answer; otherwise consider `--no-tools`.
- Avoid dumping huge sessions verbatim; summarize or page unless the user asks for full content.

## Raw Format Reference

Read `references/session-formats.md` when direct file inspection is necessary, the CCHV API is unavailable, or you need provider-specific storage details.
