#!/usr/bin/env python3
"""List and fetch local LLM sessions through the local CCHV server."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:3727"
BOILERPLATE_MARKERS = (
    "<permissions instructions>",
    "<app-context>",
    "<collaboration_mode>",
    "<apps_instructions>",
    "<skills_instructions>",
    "<plugins_instructions>",
    "# AGENTS.md instructions",
    "<environment_context>",
)
NOISE_TYPES = {"progress", "attachment", "queue-operation", "session_meta", "turn_context"}


def find_token() -> str | None:
    token = os.environ.get("CCHV_TOKEN")
    if token:
        return token.strip()

    return None


def request_json(base_url: str, path: str, token: str | None, body: dict[str, Any] | None, timeout: float) -> Any:
    url = base_url.rstrip("/") + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=data, headers=headers, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} for {path}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach CCHV at {base_url}: {exc}") from exc


def print_json(value: Any) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def content_to_text(content: Any, *, include_thinking: bool = True, include_tools: bool = True) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        stripped = content.strip()
        if stripped.startswith(("{", "[")):
            try:
                parsed, end = json.JSONDecoder().raw_decode(stripped)
                parsed_text = content_to_text(parsed, include_thinking=include_thinking, include_tools=include_tools)
                rest = stripped[end:].strip()
                return parsed_text + (("\n" + rest) if rest else "")
            except json.JSONDecodeError:
                pass
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = content_to_text(item, include_thinking=include_thinking, include_tools=include_tools)
                if text:
                    parts.append(text)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    if isinstance(content, dict):
        if content.get("thinking"):
            if not include_thinking:
                return ""
            return "[thinking] " + str(content["thinking"])
        if content.get("type") == "tool_use":
            if not include_tools:
                return ""
            name = content.get("name", "tool")
            tool_input = content.get("input")
            if tool_input is None:
                return f"[tool use] {name}"
            return f"[tool use] {name} " + json.dumps(tool_input, ensure_ascii=False)
        if content.get("type") == "tool_result":
            if not include_tools:
                return ""
            result_content = content.get("content")
            if result_content is not None:
                return "[tool result] " + content_to_text(
                    result_content,
                    include_thinking=include_thinking,
                    include_tools=include_tools,
                )
        text = content.get("text") or content.get("content")
        if text:
            return str(text)
    return json.dumps(content, ensure_ascii=False)


def is_boilerplate_message(msg: dict[str, Any], text: str) -> bool:
    role = msg.get("role")
    msg_type = msg.get("type")
    if role in {"developer", "system"}:
        return True
    if msg_type in NOISE_TYPES:
        return True
    return any(marker in text for marker in BOILERPLATE_MARKERS)


def compact_tool_text(text: str, max_chars: int) -> str:
    if max_chars <= 0 or not text.startswith(("[tool use]", "[tool result]")):
        return text
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + f"\n...[truncated tool output: {len(text) - max_chars} chars hidden]"


def print_transcript(
    messages: list[dict[str, Any]],
    *,
    forensic: bool,
    include_thinking: bool,
    include_tools: bool,
    max_tool_chars: int,
) -> None:
    for msg in messages:
        timestamp = msg.get("timestamp") or ""
        provider = msg.get("provider") or ""
        role = msg.get("role") or msg.get("type") or "message"
        text = content_to_text(
            msg.get("content"),
            include_thinking=include_thinking,
            include_tools=include_tools,
        ).strip()
        tool_use = msg.get("toolUse")
        tool_result = msg.get("toolUseResult")

        if include_tools and not text and tool_use:
            text = "[tool use] " + json.dumps(tool_use, ensure_ascii=False)
        if include_tools and not text and tool_result:
            text = "[tool result] " + json.dumps(tool_result, ensure_ascii=False)
        if not text:
            continue
        if not forensic and is_boilerplate_message(msg, text):
            continue
        if not forensic:
            text = compact_tool_text(text, max_tool_chars)

        print(f"## {timestamp} {provider} {role}".strip())
        print(text)
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("CCHV_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--token", default=find_token())
    parser.add_argument("--timeout", type=float, default=15.0)

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health")
    subparsers.add_parser("providers")

    projects = subparsers.add_parser("projects")
    projects.add_argument("--provider", action="append", dest="providers", required=True)

    sessions = subparsers.add_parser("sessions")
    sessions.add_argument("--provider", required=True)
    sessions.add_argument("--project-path", required=True)
    sessions.add_argument("--exclude-sidechain", action="store_true")

    messages = subparsers.add_parser("messages")
    messages.add_argument("--provider", required=True)
    messages.add_argument("--session-path", required=True)
    messages.add_argument("--transcript", action="store_true")
    messages.add_argument("--forensic", action="store_true", help="Preserve boilerplate and full tool output in transcript mode.")
    messages.add_argument("--no-thinking", action="store_true", help="Hide thinking blocks in transcript mode.")
    messages.add_argument("--no-tools", action="store_true", help="Hide tool use and tool result blocks in transcript mode.")
    messages.add_argument(
        "--max-tool-chars",
        type=int,
        default=1200,
        help="Truncate individual tool blocks in human transcript mode. Use 0 for no truncation.",
    )

    search = subparsers.add_parser("search")
    search.add_argument("query")
    search.add_argument("--provider", action="append", dest="providers")
    search.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()

    if args.command == "health":
        print_json(request_json(args.base_url, "/health", None, None, args.timeout))
    elif args.command == "providers":
        print_json(request_json(args.base_url, "/api/detect_providers", args.token, {}, args.timeout))
    elif args.command == "projects":
        print_json(
            request_json(
                args.base_url,
                "/api/scan_all_projects",
                args.token,
                {"activeProviders": args.providers},
                args.timeout,
            )
        )
    elif args.command == "sessions":
        print_json(
            request_json(
                args.base_url,
                "/api/load_provider_sessions",
                args.token,
                {
                    "provider": args.provider,
                    "projectPath": args.project_path,
                    "excludeSidechain": args.exclude_sidechain,
                },
                args.timeout,
            )
        )
    elif args.command == "messages":
        result = request_json(
            args.base_url,
            "/api/load_provider_messages",
            args.token,
            {"provider": args.provider, "sessionPath": args.session_path},
            args.timeout,
        )
        if args.transcript:
            print_transcript(
                result,
                forensic=args.forensic,
                include_thinking=not args.no_thinking,
                include_tools=not args.no_tools,
                max_tool_chars=args.max_tool_chars,
            )
        else:
            print_json(result)
    elif args.command == "search":
        print_json(
            request_json(
                args.base_url,
                "/api/search_all_providers",
                args.token,
                {"query": args.query, "activeProviders": args.providers, "limit": args.limit},
                args.timeout,
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
