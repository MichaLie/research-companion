#!/usr/bin/env python3
"""
spec_log.py — the honest record of the garden of forking paths.

WHAT THIS DOES (plain language):
  After every shell command Claude Code executes, this hook checks whether it
  was an estimation run (same convention as gate_check.py: a script under
  analysis/). If so, it appends one row to logs/spec-log.md — timestamp,
  the exact command, and whether it appeared to succeed.

WHY IT MATTERS:
  Agents make running specifications nearly free, which is exactly how
  p-hacking accelerates: try twenty things, report the three that worked.
  This log records ALL twenty, automatically, including the runs that never
  make the paper. The final paper reports a subset; this file is the whole
  garden — it converts "we only report what worked" from deniable to checkable.
  It is written by a hook, not by the agent, so it cannot be forgotten.

NOTE: the log grows honestly and append-only. Do not prune it; its
completeness is its entire value.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Same pattern as gate_check.py — keep the two in sync (v0.2.1: Windows-aware).
ESTIMATION = re.compile(
    r"(?:\b(?:python3?|py)(?:\.exe)?|\bRscript|\bR\b|\bstata(?:-mp|-se)?|\bjulia|\bdo\b)"
    r"(?:\s+-{1,2}\S+)*"  # interpreter flags: -u, -3, --vanilla ...
    r"\s+\S*analysis[\\/]",
    re.IGNORECASE,
)

HEADER = (
    "# Specification log — every estimation run, auto-recorded\n\n"
    "*Written by a hook (`.claude/hooks/spec_log.py`), not by the agent, so nothing here "
    "depends on anyone remembering. The paper reports a subset of these runs; this file is "
    "the honest record of everything that was tried. Append-only — completeness is its value.*\n\n"
    "| when (UTC) | command | outcome |\n"
    "|---|---|---|\n"
)


def project_root(payload: dict) -> Path:
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), payload.get("cwd")):
        if candidate:
            return Path(candidate)
    return Path(__file__).resolve().parent.parent.parent


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # Windows sessions can run commands through a PowerShell tool, not only Bash.
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "") or ""
    if not ESTIMATION.search(command):
        sys.exit(0)

    # Best-effort success signal. Field names and shapes have varied across
    # Claude Code versions (tool_result / tool_response / tool_error; dict or
    # string) — read defensively, degrade gracefully.
    if payload.get("tool_error"):
        outcome = "error?"
    else:
        response = payload.get("tool_result", payload.get("tool_response")) or {}
        if isinstance(response, dict) and response.get("interrupted"):
            outcome = "interrupted"
        else:
            text = str(response.get("stderr", "")) if isinstance(response, dict) else str(response)
            outcome = "error?" if ("error" in text.lower() or "traceback" in text.lower()) else "ran"

    log = project_root(payload) / "logs" / "spec-log.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    is_new = not log.exists()
    # Escape pipes so the command can't break the table.
    safe_cmd = command.replace("|", "\\|").replace("\n", " ⏎ ")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(log, "a", encoding="utf-8") as f:
        if is_new:
            f.write(HEADER)
        f.write(f"| {stamp} | `{safe_cmd}` | {outcome} |\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
