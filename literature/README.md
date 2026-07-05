# literature/ — the project's reading room

- **Fetched fulltexts** land here automatically: `scripts/fetch_papers.py` retrieves **legal open-access copies only**, via the Unpaywall API (a nonprofit index of lawful OA locations — publisher OA, university repositories, PubMed Central, arXiv). Nothing here circumvents a paywall.
- **`reading-list.csv`** is created by the librarian in Phase 2: doi, url, title, why_it_matters, priority. The `url` column is the fallback for economics' working-paper bloodstream (NBER, SSRN, RePEc), where papers often have no DOI — the script downloads those directly when the link is openly published.
- **`fetch-log.md`** accounts for every paper honestly: retrieved (with *version* — a `submittedVersion` is a preprint that may differ from the article of record; cite accordingly) · no OA copy found · errors.
- **`inbox/`** is yours: when a paper matters and has no open-access copy, the agent will ask you to retrieve it through your institutional access and drop the PDF here. It reads whatever appears.

One-time setup for automatic fetching — **the no-shell way:** tell the companion your email and ask it to save it; it lands in `literature/.unpaywall-email` (one line, stays local, git-ignored). Shell people can use an environment variable instead:
```
export UNPAYWALL_EMAIL="you@university.edu"      # macOS/Linux (bash/zsh)
$env:UNPAYWALL_EMAIL = "you@university.edu"      # Windows PowerShell (setx ... to persist)
```
(Unpaywall is free; the email is polite identification, nothing more.)
