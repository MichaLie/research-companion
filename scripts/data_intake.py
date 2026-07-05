#!/usr/bin/env python3
"""
data_intake.py — snapshot the data the day it arrives.

WHAT THIS DOES (plain language):
  Walks data/raw/ (or a directory you name), computes a SHA-256 checksum and
  basic shape (size; rows x columns for delimited text files) for every file,
  and writes logs/data-manifest.md. On re-runs it compares against the
  previous manifest and marks each file UNCHANGED / CHANGED / NEW / MISSING.

WHY IT MATTERS:
  "The data changed under us" should be a detectable fact, not an argument.
  Run this at intake (Phase 1) and any time you're suspicious; the fresh-eyes
  reviewer also uses it to confirm the analysis ran on the data you think it did.

USAGE:
  python scripts/data_intake.py            # snapshots data/raw/
  python scripts/data_intake.py data/clean # or any other directory
"""

import csv
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "logs" / "data-manifest.md"
DELIMITED = {".csv", ".tsv", ".txt"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def shape(path: Path) -> str:
    """Rows x columns for delimited text files; '-' for everything else."""
    if path.suffix.lower() not in DELIMITED:
        return "-"
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
            first = next(reader, [])
            rows = 1 + sum(1 for _ in reader) if first else 0
        return f"{rows} rows x {len(first)} cols (incl. header)"
    except Exception:
        return "unreadable as delimited text"


def previous_hashes() -> dict:
    """Parse filename -> sha256 out of the existing manifest, if any."""
    if not MANIFEST.exists():
        return {}
    hashes = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `(.+?)` \| ([0-9a-f]{64}) \|", line)
        if m:
            hashes[m.group(1)] = m.group(2)
    return hashes


def main() -> None:
    target = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "data/raw")
    if not target.is_dir():
        sys.exit(f"No directory at {target}. Put input data in data/raw/ (or pass a path).")

    old = previous_hashes()
    files = sorted(p for p in target.rglob("*") if p.is_file() and not p.name.startswith("."))
    seen = set()
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT))
        seen.add(rel)
        digest = sha256(p)
        if rel not in old:
            status = "NEW"
        elif old[rel] != digest:
            status = "**CHANGED**"
        else:
            status = "unchanged"
        rows.append((rel, digest, f"{p.stat().st_size:,} B", shape(p), status))
    missing = [rel for rel in old if rel not in seen]

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(f"# Data manifest — snapshot of {target.relative_to(ROOT)}\n\n"
                f"*Last run: {stamp}. A CHANGED checksum means the file is not the file "
                f"it was at the previous snapshot — find out why before trusting anything computed from it.*\n\n"
                f"| file | sha256 | size | shape | status |\n|---|---|---|---|---|\n")
        for rel, digest, size, shp, status in rows:
            f.write(f"| `{rel}` | {digest} | {size} | {shp} | {status} |\n")
        for rel in missing:
            f.write(f"| `{rel}` | — | — | — | **MISSING** (was in previous snapshot) |\n")

    changed = sum(1 for r in rows if r[4] == "**CHANGED**")
    print(f"Manifest written to {MANIFEST}: {len(rows)} files "
          f"({changed} changed, {len(missing)} missing since last snapshot).")
    if changed or missing:
        print("ATTENTION: the data is not what it was. Investigate before proceeding.")


if __name__ == "__main__":
    main()
