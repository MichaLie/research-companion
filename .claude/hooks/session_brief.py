#!/usr/bin/env python3
"""
session_brief.py — the session wakes up already knowing where the project stands.

WHAT THIS DOES (plain language):
  Runs once when a Claude Code session starts in this project. It prints the
  STATUS line of PROJECT.md; Claude Code adds a SessionStart hook's output to
  the session's context. The effect: no magic word is needed to begin or
  resume — the researcher's first message, in their own words, lands in a
  session that already knows the current phase.

WHY A HOOK AND NOT A PARAGRAPH:
  CLAUDE.md asks the agent to read PROJECT.md at the start; this hook makes
  the one crucial line arrive even if that request decays over versions and
  sessions. Same philosophy as the gate: prose decays, architecture doesn't.

HONEST STATUS: component-tested (prints the right line when run directly);
  not yet observed inside a live session start — verify on first use.
"""

import sys
from pathlib import Path


def main() -> None:
    # Project root = two levels above .claude/hooks/.
    root = Path(__file__).resolve().parent.parent.parent
    project = root / "PROJECT.md"
    if not project.exists():
        sys.exit(0)  # nothing to brief — never block a session over it
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    for line in project.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("**STATUS:**"):
            print(
                f"[research-companion] Where the project stands, per PROJECT.md -> {line} "
                f"(full shared understanding in PROJECT.md; lifecycle and posture in CLAUDE.md; "
                f"no /start needed — the researcher's first message begins or resumes the right phase)"
            )
            break
    sys.exit(0)


if __name__ == "__main__":
    main()
