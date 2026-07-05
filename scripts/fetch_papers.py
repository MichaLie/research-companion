#!/usr/bin/env python3
"""
fetch_papers.py — pull LEGAL fulltexts for the reading list. (v0.3)

WHAT THIS DOES (plain language):
  Reads literature/reading-list.csv (columns: doi, url, title, why_it_matters,
  priority). For each row:
    - if it has a DOI: asks the Unpaywall API whether a free, legal
      open-access copy exists and downloads the best available PDF;
    - if it has no DOI but a direct url (economics runs on working papers —
      NBER, SSRN, RePEc — which often have no DOI and escape Unpaywall):
      attempts a direct download of that link.
  Everything lands in literature/, with an honest per-paper log in
  literature/fetch-log.md. Papers that can't be retrieved are listed for the
  researcher to fetch via institutional access and drop into literature/inbox/.

WHAT THIS DELIBERATELY DOES NOT DO:
  It never circumvents paywalls. Unpaywall (unpaywall.org, run by the
  nonprofit OurResearch) indexes only lawful open-access locations, and the
  direct-url path only downloads links the librarian found openly published.

SETUP (one time — any ONE of these):
  no shell needed:     put your email (one line) in literature/.unpaywall-email
                       — or simply ask the companion to set it up for you
  macOS/Linux:         export UNPAYWALL_EMAIL="you@university.edu"
  Windows PowerShell:  $env:UNPAYWALL_EMAIL = "you@university.edu"   (setx ... to persist)
  (free; the email is polite identification for the Unpaywall API)

USAGE:
  python scripts/fetch_papers.py                # process the whole reading list
  python scripts/fetch_papers.py 10.1234/abcd   # or fetch specific DOIs
"""

import csv
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import json
from pathlib import Path

API = "https://api.unpaywall.org/v2/{doi}?email={email}"
LIT_DIR = Path(__file__).resolve().parent.parent / "literature"
READING_LIST = LIT_DIR / "reading-list.csv"
FETCH_LOG = LIT_DIR / "fetch-log.md"
PAUSE_SECONDS = 1.0  # be polite to free services


def safe_filename(key: str) -> str:
    """Turn a DOI or title into a filesystem-safe PDF filename."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", key).strip("_")[:120] + ".pdf"


def lookup(doi: str, email: str) -> dict:
    """Ask Unpaywall about one DOI. Returns the parsed JSON record."""
    url = API.format(doi=urllib.parse.quote(doi, safe=""), email=urllib.parse.quote(email))
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)


def download(pdf_url: str, dest: Path) -> bool:
    """Download a PDF; returns True on success. Never raises past this function."""
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "research-companion/0.2"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
        # A real PDF is bigger than an error page and starts with %PDF.
        with open(dest, "rb") as f:
            head = f.read(5)
        return dest.stat().st_size > 10_000 and head == b"%PDF-"
    except Exception:
        return False


def main() -> None:
    # Non-Western consoles can garble UTF-8 in printed titles and messages.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    email = os.environ.get("UNPAYWALL_EMAIL", "").strip()
    if not email:
        # The no-shell path: the companion (or researcher) saves the email to a
        # one-line file that .gitignore keeps local.
        email_file = LIT_DIR / ".unpaywall-email"
        if email_file.exists():
            email = email_file.read_text(encoding="utf-8").strip()

    # DOIs from the command line, or rows from the reading list CSV.
    if len(sys.argv) > 1:
        rows = [{"doi": d, "url": "", "title": "", "priority": ""} for d in sys.argv[1:]]
    elif READING_LIST.exists():
        with open(READING_LIST, newline="", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f)
                    if (r.get("doi", "") or r.get("url", "")).strip()]
    else:
        sys.exit(f"No DOIs given and no {READING_LIST} found. The librarian creates that file in Phase 2.")

    needs_unpaywall = any((r.get("doi") or "").strip() for r in rows)
    if needs_unpaywall and ("@" not in email):
        sys.exit('DOI rows need the Unpaywall API. Provide your email first — simplest: save it (one line) to literature/.unpaywall-email, or ask the companion to. Shell alternative: export UNPAYWALL_EMAIL=... (bash/zsh) · $env:UNPAYWALL_EMAIL = ... (PowerShell).')

    LIT_DIR.mkdir(exist_ok=True)
    found, missing, errors = [], [], []

    for row in rows:
        doi = (row.get("doi") or "").strip()
        direct_url = (row.get("url") or "").strip()
        title = (row.get("title") or "").strip()
        try:
            if doi:
                rec = lookup(doi, email)
                best = rec.get("best_oa_location") or {}
                pdf_url = best.get("url_for_pdf") or best.get("url")
                if rec.get("is_oa") and pdf_url:
                    dest = LIT_DIR / safe_filename(doi)
                    # 'version' tells the researcher WHAT they are reading — a
                    # publishedVersion is the article of record; a submittedVersion
                    # is a preprint that may differ from the journal version.
                    version = best.get("version", "unknown")
                    host = best.get("host_type", "unknown")
                    if download(pdf_url, dest):
                        found.append((doi, title, version, host, dest.name))
                        print(f"  OK  {doi}  ({version}, via {host})")
                    else:
                        errors.append((doi, title, f"OA copy listed but download failed: {pdf_url}"))
                        print(f"  !!  {doi}  download failed — link logged for manual retrieval")
                else:
                    missing.append((doi, title))
                    print(f"  --  {doi}  no legal open-access copy — please drop the PDF into literature/inbox/")
            elif direct_url:
                dest = LIT_DIR / safe_filename(title or direct_url)
                if download(direct_url, dest):
                    found.append((direct_url, title, "working paper", "direct link", dest.name))
                    print(f"  OK  {title or direct_url}  (direct link)")
                else:
                    missing.append((direct_url, title))
                    print(f"  --  {title or direct_url}  direct download failed (some sites block scripts) — please use literature/inbox/")
        except Exception as e:
            errors.append((doi or direct_url, title, str(e)))
            print(f"  !!  {doi or direct_url}  error: {e}")
        time.sleep(PAUSE_SECONDS)

    # Write the honest log — every paper accounted for, nothing silent.
    with open(FETCH_LOG, "w", encoding="utf-8") as f:
        f.write("# Fulltext fetch log\n\n*Legal copies only: open access via Unpaywall, plus openly "
                "published working-paper links. Note the `version` column: a submittedVersion or "
                "working paper may differ from the article of record — cite accordingly.*\n\n")
        f.write("## Retrieved\n\n| DOI / link | Title | Version | Source | File |\n|---|---|---|---|---|\n")
        for d, t, v, h, fn in found:
            f.write(f"| {d} | {t} | {v} | {h} | {fn} |\n")
        f.write("\n## Not retrieved — please add to `literature/inbox/`\n\n| DOI / link | Title |\n|---|---|\n")
        for d, t in missing:
            f.write(f"| {d} | {t} |\n")
        f.write("\n## Errors (retry or retrieve manually)\n\n| DOI / link | Title | What happened |\n|---|---|---|\n")
        for d, t, e in errors:
            f.write(f"| {d} | {t} | {e} |\n")

    print(f"\nDone: {len(found)} retrieved · {len(missing)} need the inbox · {len(errors)} errors.")
    print(f"Log written to {FETCH_LOG}")


if __name__ == "__main__":
    main()
