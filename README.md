# ARUBA-FATP-tool

ARUBA FATP microphone test-data整理與分析工具。

## Current snapshot

- Snapshot date: 2026-09-07
- Source dataset: 2026-08-26 ARUBA MIC FATP run
- DUT folders: 73
- Unique SN: 73
- Raw CSV files: 219
- WAV files: 146
- Existing Excel summary: 1
- Current parser/tool version: v12 (`src/build_summary.py`; see `CHANGELOG.md`)

### Parsed output coverage

| Sheet | Current data |
| --- | ---: |
| FR_original | 0 rows (RawData_RD currently empty) |
| FR_1_3 | 73 DUT × 80 frequency points |
| FR_1_12 | 0 rows (RawData_RD currently empty) |
| THD | 73 DUT × 80 frequency points |
| Phase | 73 DUT × 80 frequency points |
| Noise | 73 DUT × 800 frequency points |
| Sealing | 0 rows (no Sealing CSV in this dataset) |

All 73 DUT frequency axes checked in the current dataset are consistent.

## Repository layout

```text
src/
  build_summary.py         Current parser / Excel summary builder (v12 logic)
tools/
  run_build_summary.bat    Windows launcher
docs/
  usage.md                 How to run the tool
  review_2026-09-07.md     Engineering review + V13 backlog (dated historical record)
data/
  snapshots/               Dataset composition, counts, and SHA-256 integrity records
  manifests/               Per-dataset inventory / integrity manifests (placeholder)
  outputs/                 Generated analysis outputs, when checked in (placeholder)
CHANGELOG.md               Version history (v9 → v12) and the V13 backlog
requirements.txt           Python dependencies
```

## Run

See `docs/usage.md` for full usage notes. Quick start:

```bash
py -3 -m pip install -r requirements.txt
python src/build_summary.py <raw-data-folder>
```

Windows:

```text
tools\run_build_summary.bat
```

The selected raw-data folder is expected to contain:

```text
Online/
RawData_RD/
```

Output is written as `summary.xlsx` inside the selected raw-data folder.

## Important result-definition issue found during review

For the current 73 FR files, filenames contain `FR_PASS`, while the internal FR section `Test Result:` is `Fail` for all 73 records. THD and Phase section results are `Pass`.

The current v12 implementation derives the FR/THD/Phase `Result` column from the FR filename, so the Excel result can show `PASS` even when the internal APx FR section reports `Fail`.

This may be intentional if filename PASS represents the factory station final judgement and APx section result represents a different limit definition. Do **not** collapse the two meanings until the station logic is confirmed. Recommended V13 design:

- `Station Result`
- `APx Section Result`

See `docs/review_2026-09-07.md` for the full review and `CHANGELOG.md` for the complete V13 backlog.

## Data note

The source package contains about 46.2 MB of WAV binary recordings. These binaries are **not stored in this repository** — only their counts, sizes, and SHA-256 hashes are recorded in `data/snapshots/README.md` so the local package can be verified. Do not treat their absence from this repo as deletion of the original local dataset.

## Data disclosure note

This repository is public. As of 2026-09-08 the tracked files record only aggregate counts, file-size totals, and SHA-256 hashes of the local dataset — no individual DUT serial numbers or raw factory test values are checked into this repository. Keeping this public was confirmed acceptable on that basis; re-check this note before committing raw CSV/WAV data or per-unit serial numbers in the future.
