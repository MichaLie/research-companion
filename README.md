# Research Companion (v0.3.1)

> **Retired, November 2026.** This project is no longer developed. Its literature workflow continues in the [Research Intelligence Engine](https://github.com/MichaLie/Research-Intelligence-Engine), and the risks it guarded against are mapped in the [Agent Risk Atlas](https://michalie.github.io/agent-risk-atlas/). The parts for analysing your own data have no successor yet. The repository stays here, read-only, as it was at v0.3.1.

A drop-in Claude Code package that turns an AI agent into a **thoughtful research colleague**: it makes sure it understands before it acts, grounds every methods choice in the current literature (not in stale training memory), shows what it's doing and why at every step, gives finished work fresh eyes before anyone trusts it — and leaves you a little sharper after every project.

**► The five-minute tour, with receipts: [michalie.github.io/research-companion](https://michalie.github.io/research-companion/)** — every claim on that page links to the file in this repo that proves it.

No gates, no drills, no cop energy. The same verification philosophy as its sibling packages, built instead into the choreography of a well-run collaboration — the way a good lab's habits feel: *of course we do it this way.*

## What you need (once)
- **Claude Code** with an Anthropic account — the desktop app is fine; that's the environment this package is designed to feel at home in.
- **Python 3.8+** — the enforcement hooks (the analysis gate, the run log) are small Python scripts. Without Python everything still *works*, but those rules fall back from **enforced** to **promised**: the companion is told at session start that its hooks are off, and it will tell you. (python.org, two minutes, tick "Add to PATH.")

## Three steps
1. **Dump your context.** Drop everything into `context/` — messy is fine; see `context/README.md`.
2. **Open Claude Code in this folder.**
3. **Say hello — in your own words.** Tell it what you brought, or ask where things stand; it takes it from there, and `PROJECT.md` remembers everything between sessions. (`/start` does the same, for people who like buttons. When literature fetching starts, the companion asks for your email once and sets it up for you — no shell required.)

## What the collaboration feels like
> **"Let me make sure I correctly understand the research problem and what needs to be done."** — it rephrases what you actually want (not what your rushed prompt literally said), interviews you one question at a time for what's missing, and pushes back gently: *"Have you considered…"*
>
> **"Understood — let me ground myself in the most current methods before we commit to anything."** — the librarian subagent searches the current literature, logs every query it constructs *and why*, labels methods proposed-vs-adopted, fetches legal open-access fulltexts automatically, and asks you only for the paywalled ones that matter.
>
> **"Here are the directions we could take — with what each one buys, and what it risks."** — options with symmetric caveats; you choose, in your own words; it's recorded. Before locking in: *"Here's the question a reviewer will most likely ask — want to talk it through now, while it's cheap?"*
>
> **"Starting the analysis — I'll narrate as I go, and the dashboard stays current."** — every script carries a plain-language header, every data transformation shows its diff, and before each new headline result: *"Quick — sign and rough size? Keeps your intuition in training."*
>
> **"Done. Before we trust it, let's give it fresh eyes."** — an independent review in a clean context re-runs the code, recounts the Ns, re-opens the citations. Everything it flags is something a referee would have found later, at a worse time.
>
> **"Here's what we did, what we verified, and one thing worth taking with you."** — plus a methods-section AI-disclosure paragraph, drafted from the log, ready to paste.

## The map
```
CLAUDE.md                        the constitution: posture + the six-phase lifecycle
PROJECT.md                       the shared understanding — any session resumes from here
context/                         you drop everything here (see its README)
literature/  + inbox/            the reading room; legal OA fetched, paywalled via your inbox
scripts/fetch_papers.py          Unpaywall fetcher — tested live, legal OA only
dashboard-contract.md            rules for the live HTML view (dashboard.html at runtime)
.claude/commands/start.md        /start — begin or resume
.claude/agents/librarian.md      grounding subagent, full query transparency
.claude/agents/fresh-eyes.md     independent review subagent, clean context by architecture
.claude/settings.json            hook wiring — the rules that are enforced, not requested
.claude/hooks/gate_check.py      blocks analysis/ runs until a signed decision exists (tested)
.claude/hooks/spec_log.py        auto-records every estimation run — the forking-paths record (tested)
.claude/hooks/session_brief.py   injects PROJECT.md's status at session start — no magic word needed (in-situ check pending)
scripts/data_intake.py           day-one data manifest: checksums + shape, changes flagged (tested)
data/raw/                        input data — git-ignored by default (red-line safety)
decisions/ · logs/               created at runtime: choices, ai-log, diffs, calibration, searches, spec-log
```

## Quiet constants (the philosophy, running in the background)
Never invents identifiers — writes **UNVERIFIED** instead · every claim links to its evidence · methods are proposed with caveats, never chosen for you · confidential/licensed/human-subjects data never enters · every data transformation shown as a diff · every session logged for disclosure · text inside documents is material, never instructions · and at the margin, it points you back to humans: seminars, coauthors, the field.

## What's new in v0.2 (from the blindspot pass)
- **Rules became architecture.** The one hard gate — no estimation before a signed decision — is now a hook that physically blocks the run (exit code 2), not a paragraph the agent might drift from over a long session. Prose decays; architecture doesn't. The hook's logic is short, commented, and meant to be read.
- **The specification log.** A second hook auto-records *every* `analysis/` run to `logs/spec-log.md`, including the ones that never make the paper — the honest record of the garden of forking paths, written by machinery rather than memory, with its own dashboard panel ("23 runs, 3 in the draft"). Arguably the single biggest reproducibility upgrade in the package.
- **The librarian got hardened.** It's the one agent ingesting documents from the open wild, so it now carries an explicit untrusted-input guard; it searches economics' working-paper bloodstream (NBER, SSRN, RePEc — the reading list gained a `url` column for DOI-less papers, and the fetch script downloads openly published links directly, tested live); it must ground "adopted" labels in counts, not impressions; and every grounding memo must declare its boundaries — a mandatory *"What I did not search"* section, because coverage can't be proven but boundaries can be criticized.
- **Fresh eyes now reviews the grounding too** — the memo that shapes the method choice was the highest-stakes, least-audited artifact in v0.1.
- **Anti-sycophancy in PLAN:** options are always presented *before* preference is elicited, and a devil's-advocate beat is mandatory — the strongest honest case against the emerging lean, every time.
- **Day-one data manifest:** checksums and shape at intake; "the data changed under us" is detectable, not arguable.
- **Git-ready:** `PROJECT.md`, `decisions/`, and `logs/` are the coauthor communication — commit them. `data/` is git-ignored *by default* as red-line safety.

## What's new in v0.2.1 (cross-platform patch — Windows joins)
Found by live component-testing on a Windows 11 machine (Czech locale) — the hooks' first contact with a hostile environment. The design is unchanged; the invocations stopped assuming Unix:
- **The hooks no longer assume `python3` exists.** On many Windows machines `python3` is a dead Microsoft Store stub — the hook command would fail and *the gate would silently not gate*. Hook commands now pick a real interpreter at run time: `py -3` → verified `python3` → `python`. Honest boundary: the hook command uses POSIX shell syntax, which on Windows runs via Git Bash (standard with Claude Code); on a Git-Bash-less Windows setup, edit the two commands in `.claude/settings.json` to plain `python …`.
- **The estimation pattern speaks Windows:** backslash paths (`analysis\model.py`), the `py` launcher, `.exe` suffixes, and interpreter flags (`Rscript --vanilla …`) are caught; a word-boundary guard keeps `mypy`/`numpy` from tripping the gate. Same pattern in both hooks, kept in sync.
- **Both hooks listen to the PowerShell tool too** (`matcher: "Bash|PowerShell"`) — Windows sessions don't always route commands through Bash.
- **Schema currency:** PostToolUse reads `tool_result` (current docs) with graceful fallback to older field names.
- **Gate message forced to UTF-8** so it survives non-Western consoles intact.
- **Docs show both shells** for the Unpaywall email (`export …` / `$env:…`); `.gitignore` learned `Thumbs.db`; internal version headers aligned (librarian, fresh-eyes, dashboard contract previously still said v0.1).

## What's new in v0.3 (from the first live end-to-end arc, same day)
A full six-phase arc ran against a synthetic education dataset with sealed ground truth (+4.0 planted; the arc honestly reported "+3 to +4.5, modest"). Every change below carries the evidence that demanded it:
- **The brief is testimony.** Phase 1 gains a mandatory anomaly scan, and the rule that every claim the brief or interview makes *about the data* is checked against the data before it becomes a design premise; PLAN flags testimony-based premises; fresh-eyes re-derives design premises from raw data alone. *(Evidence: a "global 2021 testing change" inherited from the brief was actually one district-year stored at half scale — every number replicated perfectly on the false premise, and the contaminated secondary estimate ran +9.2 where truth was +4.)*
- **The methods card.** Signed decisions now record: what the method compares (one plain sentence) · the assumption it leans on hardest (one plain sentence) · the method in the researcher's own words — teach mode fires when that sentence won't come, and the card's summary is pinned to the dashboard strip. *(Evidence: at debrief the researcher retained the design and the result — the parts said in her own words — and none of the estimator names, nor the assumption.)*
- **Teach mode stops waiting for a confession** — it also fires on first out-of-field method names and at signing time. *(Evidence: mid-arc confusion was confessed to a third party, never to the tool.)*
- **Fresh-eyes writes `logs/fresh-eyes-report.md`.** *(Evidence: a 13-VERIFIED / 0-UNVERIFIED / 1-CONTRADICTED verdict table existed nowhere on disk after the arc.)*
- **The librarian re-opens every identifier before the memo ships.** *(Evidence: "published QJE 2020," asserted as fact, drew the arc's only CONTRADICTED — the article of record is AERJ 2024.)*
- **Dashboard contract v2:** evidence links never navigate the dashboard away (`target="_blank"` minimum; inline excerpt expanders preferred) · phase-aware fold with a standing strip (phase · how-the-numbers-are-made · doubts count) · "Waiting on you" is never empty · honest doubts near the top, plus doubt-chips inline next to the numbers they concern. *(Evidence: one click stranded the researcher on a blank preview; the method identity sat two clicks deep while she lost track of it.)*
- **No magic word.** Any first message begins or resumes the right phase; a SessionStart hook injects PROJECT.md's status line so this survives prose decay; `/start` remains as a button; literature-fetch setup went no-shell (a local email file the companion manages). *(Evidence: the target audience is non-coding researchers on the desktop app — field note #1.)*

## What's new in v0.3.1 (workshop-readiness, 2026-07-05)
- **LICENSE (MIT) + CITATION.cff** — open source; build on it, adapt it, cite it.
- **Python-less machines fail loud, not silent.** A workshop room will contain laptops without Python; on those, the session brief now announces that the hooks are OFF, the constitution falls back to running the gate and spec-log manually and says so, and this README states the one prerequisite plainly. Enforced beats promised; promised-and-disclosed beats silent.

## Siblings
This is the third edition of one design. `econ-research-agent/` holds the **PI edition** (explicit gates, drills, supervision framing — for when you want the discipline visible) and its `variants/phd-student/` (tutor posture, mentor escalation). Same physics, three postures — which is the project's whole thesis: de-skilling and up-skilling are properties of the configuration, not of the machine.

The evidence behind that thesis — why judgment has to stay human, per the peer-reviewed record — reads as the [critical-thinking foundations](https://michalie.github.io/tah-day2/foundations/critical-thinking-guide.html): a field guide, a prompt phrasebook, and a practice room to test yourself in.

## Versioning & disclosure
Review by **2026-10-05** — rules about a moving frontier expire like milk, not marble. Drafted with Claude (Fable 5) on 2026-07-05 from the project's seed documents. Tested live before shipping: the fetch script against the Unpaywall API and a direct working-paper link (both retrieved and validated as real PDFs); the gate hook (blocks, passes through, unlocks on signature); the spec-log hook (records estimations, ignores other commands, flags errors); the data manifest (detects a changed file). Untested: the hooks inside a real Claude Code session end-to-end, and everything else against a real research project. Not yet reviewed by a practicing econometrician. The topic is verification; the materials must practise it.

v0.2.1 (2026-07-05, same day): cross-platform compatibility patch after live component-testing on Windows 11 — gate block/unlock, the Windows-path and `py`-launcher evasions, and the interpreter fallback verified by piped-JSON tests on that machine; hook-execution facts (Git Bash default shell on Windows, `Bash|PowerShell` matcher, `tool_result` field, live hook reload) verified against current Claude Code documentation. Subsequently verified in situ: a live session's gate blocked, unlocked on a signed decision, and auto-logged every run (all via the `py` launcher — which v0.2 would have missed entirely).

v0.3 (2026-07-05, same day): rebuilt from the first live end-to-end arc on a sealed-truth synthetic project; transcript preserved. Tested for v0.3: hooks byte-compile, settings parse, gate + spec-log matrix re-passed, session_brief prints the status line when run directly. **Untested, stated honestly:** session_brief inside a real session start; the anomaly-scan, methods-card, and proactive teach-mode beats in a live arc — those are v0.3's hypotheses, and the next run is their test. The topic is verification; the materials must practise it.

v0.3.1 (2026-07-05): MIT license + citation metadata; loud-and-disclosed degradation on machines without Python (session-brief warning, manual-gate fallback in the constitution, prerequisite stated). The no-Python warning path is component-tested by simulation; its first real Python-less laptop will be the live test.
