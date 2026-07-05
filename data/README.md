# data/ — input data lives here

- **`raw/`** — the data as it arrived, never edited in place. The moment files land here, run `python scripts/data_intake.py`: it writes checksums and shape to `logs/data-manifest.md`, so "the data changed under us" is detectable from day one. Cleaned/derived data goes in sibling folders (`data/clean/` etc.), each transformation shown as a watched diff.
- **Red lines apply here hardest:** confidential microdata, human-subjects data, and licensed datasets never enter this workspace or any external tool. The `.gitignore` excludes `data/` from version control by default so nothing is pushed to a remote by accident — remove that exclusion only deliberately, only for fully public data.
