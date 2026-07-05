# Dashboard contract — the live view (companion edition, v0.3)

A single self-contained `dashboard.html`, regenerated after every significant step. Markdown and logs remain the source of truth; the dashboard is a *view*, never hand-edited. It exists so the researcher can understand — at a glance, in one pass, without opening a single log file — what is happening, why, and where they come in. Whenever the dashboard is regenerated, the companion says so **and says how to (re)open it** — a view nobody can find is not a view.

## Tone
This is a shared workbench, not a report card and not a surveillance feed. It informs and invites; it never scolds. But it also never decorates: a beautiful page that only *displays* progress teaches passive watching, and polish without evidence is exactly the fluency-without-truth problem this whole system exists to solve.

## The load-bearing rule
No element renders without an evidence link. A number links to its table and log; a citation links to the opened source; a check links to the test that produced it; a search result links to the query that found it (via `logs/search-log.md`). Anything unlinked renders as **UNVERIFIED** in the caution color. Decorative progress bars, unlinked checkmarks, and celebratory badges do not exist here.

## The link rule (learned live, first arc)
**An evidence link never navigates the dashboard away.** In embedded preview panels, a relative link to a raw `.md` strands the reader on a blank page with no way back. Minimum: every link carries `target="_blank"`. Preferred: inline expanders (`<details>`) that bring the quoted excerpt *into* the page — the evidence comes to the reader, which also serves readers for whom a raw markdown file is a dead end. The full-file path stays visible beside the excerpt for anyone who wants the source.

## The fold is phase-aware
The dashboard is regenerated after every significant step, so its ordering can serve the moment instead of a fixed table of contents. **Always first, in this order:**

1. **The strip** — one line: current phase · *how the headline numbers are made* (one plain sentence, from the decision's methods card) · count of open doubts. The live inferential frame, never more than a glance away. *(First-arc evidence: the researcher lost track of what statistics produced the numbers while the memo recording them sat two clicks deep.)*
2. **Waiting on you** — and it is **never empty**: when nothing is pending, it says what is anticipated next ("nothing right now — next likely ask: a 30-second prediction before the headline result"). A dead panel above the fold teaches people to stop looking; an anticipating one keeps the researcher a pilot. Items leave only by being done.
3. **Honest doubts** — the top-3 current uncertainties, plain language, each linked to what would resolve it. "None" is almost always a lie. Doubt-chips also appear inline, next to the specific numbers they concern — the caution belongs where the dazzle happens.

**Then, ordered by what the current phase needs** (all panels exist in every regeneration; the phase decides what sits high):

- *UNDERSTAND / GROUND:* the shared problem as currently phrased · Reading room (papers found, linked to the query that found them; fulltext vs abstract-only; proposed-vs-adopted labels).
- *PLAN:* options as presented · the emerging decision record (choice, researcher's own one-line rationale, methods card, dated).
- *ANALYZE:* the narration trail (each step, one plain sentence, linked to its artifact, diff, or log line) · **Everything we tried** (from `logs/spec-log.md`: specifications run vs results reported, the gap stated plainly — "23 runs, 3 in the draft").
- *FRESH EYES / CLOSE:* **Verification** (the verdict table from `logs/fresh-eyes-report.md`, linked; V/U/C counts; "no review yet" stated explicitly when true — silence must be distinguishable from omission) · **Your calibration** (predictions vs revealed results, running hit-rate — intuition in training) · **Disclosure, ready to paste** (drafted live from `logs/ai-log.md`).

Panels not named by the current phase follow below, in the order above. The plan & decisions record, once signed, may sit low — but its methods card sentence stays in the strip.

## Style
Readable in one pass by a colleague who doesn't code: structure, color, small diagrams, no walls of raw log. Honest cost note: legible HTML takes the agent 2–4× longer than markdown. Accepted — the return is that the work actually gets read.
