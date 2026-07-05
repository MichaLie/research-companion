#!/usr/bin/env python3
"""
gate_check.py — the package's ONE hard gate, enforced by architecture.

WHAT THIS DOES (plain language):
  Before Claude Code executes any shell command, this hook looks at it.
  If the command runs an estimation script (convention: code living in
  analysis/), it checks whether decisions/ contains at least one signed
  decision — a .md file with the line "status: SIGNED", recording the
  researcher's choice in their own words. If not, the command is BLOCKED
  (exit code 2) and Claude is told why.

WHY A HOOK AND NOT A PARAGRAPH:
  Instructions in CLAUDE.md are requests; over a long session an agent can
  drift from them. A PreToolUse hook that exits 2 is a guarantee — the
  estimation physically does not run. Prose decays; architecture doesn't.

THE CONVENTION (adjust freely — this file is meant to be read and edited):
  - Estimation code lives in analysis/  →  that's what the pattern below keys on.
  - A signed decision = any decisions/*.md containing "status: SIGNED".
  - v0.2 keeps it coarse: ANY signed decision unlocks analysis. A finer
    per-analysis mapping is possible; start coarse, tighten if needed.

CROSS-PLATFORM (v0.2.1):
  The pattern also catches Windows habits — backslash paths (analysis\\model.py),
  the `py` launcher, `.exe` suffixes, interpreter flags — and commands arriving
  via the PowerShell tool, not just Bash. Added after live component-testing on
  a Windows 11 machine, where the original pattern silently missed all of these.
"""

import json
import os
import re
import sys
from pathlib import Path

# What counts as running an estimation: invoking an interpreter on a script
# under analysis/ (slash or backslash — Windows paths count). Transparent and
# editable — if your lab uses a different layout or runner, change this ONE
# pattern. spec_log.py carries the same one; keep the two in sync.
ESTIMATION = re.compile(
    r"(?:\b(?:python3?|py)(?:\.exe)?|\bRscript|\bR\b|\bstata(?:-mp|-se)?|\bjulia|\bdo\b)"
    r"(?:\s+-{1,2}\S+)*"  # interpreter flags: -u, -3, --vanilla ...
    r"\s+\S*analysis[\\/]",
    re.IGNORECASE,
)


def project_root(payload: dict) -> Path:
    """Find the project root: env var from Claude Code, else the session cwd,
    else two levels above this script (.claude/hooks/ -> project)."""
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), payload.get("cwd")):
        if candidate:
            return Path(candidate)
    return Path(__file__).resolve().parent.parent.parent


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unreadable input -> never block by accident

    # Windows sessions can run commands through a PowerShell tool, not only Bash.
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "") or ""
    if not ESTIMATION.search(command):
        sys.exit(0)  # not an estimation run -> allow

    decisions = project_root(payload) / "decisions"
    if decisions.is_dir():
        for memo in decisions.glob("*.md"):
            try:
                if "status: SIGNED" in memo.read_text(errors="ignore"):
                    sys.exit(0)  # a signed decision exists -> allow
            except OSError:
                continue

    # Non-Western Windows consoles can garble UTF-8; force it so the gate
    # message reaches Claude (and the researcher) intact.
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(
        "GATE (this is the collaboration's one hard rule, not a malfunction): "
        "scripts in analysis/ run only after a signed decision exists in decisions/ — "
        "a .md containing the line 'status: SIGNED' with the researcher's choice and "
        "one-line rationale in their own words. Present the options (Phase 3), let the "
        "researcher choose, record it, then re-run. The gate's logic is plainly written "
        "in .claude/hooks/gate_check.py and can be adjusted — but never silently bypassed.",
        file=sys.stderr,
    )
    sys.exit(2)  # exit 2 = block the command; stderr is shown to Claude


if __name__ == "__main__":
    main()
