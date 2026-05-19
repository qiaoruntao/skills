# Session Formats And Provider Notes

Prefer CCHV's API over direct parsing. This reference is for fallback inspection and for understanding what CCHV normalizes.

## Local Service

CCHV may be run directly or managed by a process supervisor such as PM2. This
skill assumes the REST API is available locally and does not require a specific
installation path.

The service commonly watches provider storage roots such as:

- `~/.claude/projects`
- `~/.codex/sessions`
- `~/.codex/archived_sessions`
- `~/.local/share/opencode`

The auth token is intentionally not documented here. Resolve it from
`CCHV_TOKEN` or pass it explicitly with the helper script's `--token` flag.

## CCHV REST API

Base URL: `http://127.0.0.1:3727`

Headers for `/api/*`:

```text
Authorization: Bearer <token>
Content-Type: application/json
```

Useful endpoints:

- `GET /health`
- `POST /api/detect_providers` with `{}`
- `POST /api/scan_all_projects`
- `POST /api/load_provider_sessions`
- `POST /api/load_provider_messages`
- `POST /api/search_all_providers`

`/health` is public; `/api/*` requires auth.

## Provider Storage

Claude Code:

- Default root: `~/.claude/projects/`
- Project folders encode project paths, for example `-Users-example-projects-app`.
- Sessions are usually JSONL files named `<uuid>.jsonl`.
- Raw records can include `type`, `sessionId`, `uuid`, `parentUuid`, `timestamp`, `message`, `content`, `attachment`, `isSidechain`, and metadata fields.
- Some records are not chat messages, such as `queue-operation` or `attachment`.

Codex CLI:

- Default roots: `~/.codex/sessions/` and `~/.codex/archived_sessions/`
- Active sessions are nested by date, for example `~/.codex/sessions/YYYY/MM/DD/rollout-...jsonl`.
- Archived sessions may be flat JSONL files.
- Raw records are JSONL with top-level `type`, `timestamp`, and `payload`.
- Observed raw record types include `session_meta`, `response_item`, `event_msg`, and `turn_context`.
- `payload` carries fields such as `cwd`, `id`, `instructions`, `role`, `content`, `kind`, `message`, `model`, and sandbox/approval metadata.

Gemini CLI:

- Observed roots: `~/.gemini/history/` and `~/.gemini/tmp/<project>/chats/`.
- CCHV may expose sessions as JSON files such as `session-YYYY-MM-DDTHH-MM-<id>.json`.

OpenCode:

- Observed root: `~/.local/share/opencode/`.
- CCHV exposes project/session paths as URI-like identifiers, for example `opencode://...`.
- Storage may be SQLite-backed; use the API rather than treating session ids as local file paths.

Antigravity:

- Observed root: `~/.gemini/antigravity`.
- CCHV expects state under `brain/` and token monitor data under `.token-monitor/rpc-cache/v1/` when available.

Cline, Cursor, Aider, ForgeCode:

- CCHV supports these providers, but availability depends on local data.
- Aider scans can be slow because it may inspect project directories; use explicit provider filters and shell/API timeouts.
- ForgeCode may use `~/.forge/.forge.db` and URI-like session identifiers.

## Example Provider Availability

Provider availability is environment-specific. A local CCHV instance may return
projects for any subset of the supported providers. Use `detect_providers` or
the bundled `providers` command to inspect the current machine instead of
assuming fixed counts.

## Normalized API Shapes

Project objects commonly include:

- `name`
- `path`
- `provider`
- `last_modified`
- `session_count`
- `message_count`

Session objects commonly include:

- `actual_session_id`
- `session_id`
- `file_path`
- `first_message_time`
- `last_message_time`
- `last_modified`
- `message_count`
- `project_name`
- `provider`
- `summary`
- `has_tool_use`
- `has_errors`
- `storage_type`

Message objects commonly include:

- `uuid`
- `sessionId`
- `parentUuid`
- `type`
- `role`
- `timestamp`
- `provider`
- `content`
- `toolUse`
- `toolUseResult`

For provider-specific raw content, inspect the message JSON instead of assuming field names.
