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
- Current parser/tool version: `build_summary_windows_v12_calc`

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
src/                 Python source code
tools/               Windows launchers / helper scripts
docs/                Usage notes and engineering review notes
data/
  snapshots/         Versioned data snapshots that can be shared through GitHub
  manifests/         Dataset inventory / integrity information
  outputs/           Generated analysis outputs when practical
```

## Run

Requirements:

- Python 3.10+
- `openpyxl`

Install dependency:

```bash
py -3 -m pip install -r requirements.txt
```

Windows:

```text
tools\run_build_summary_v12_calc.bat
```

Or run directly:

```bash
python src/build_summary_windows_v12_calc.py <raw-data-folder>
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

See `docs/review_2026-09-07.md` for the full review.

## V13 priority backlog

1. Separate station result from APx section result.
2. Add import/data-QC log and missing-file checks.
3. Validate frequency axes for every DUT instead of only using the first header.
4. Preserve station metadata such as operator/station/test SW/timing.
5. Add automatic statistics: N / Mean / Max / Min / Range / STDEV.
6. Improve Excel usability: freeze panes, filters, widths, datetime, number formats and PASS/FAIL formatting.
7. Add optional dashboard/charts after the data model is stable.

## Data note

The source package contains about 46.2 MB of WAV binary recordings. The current ChatGPT GitHub connector can write repository text and Git objects, but it does not provide a practical local-file upload path for the full WAV set in one operation. The PR therefore tracks the WAV inventory/integrity separately and prioritizes the complete numerical CSV dataset, source code and review artifacts. Do not treat absence of WAV bytes in the branch as deletion of the original local dataset.

Because this repository is public, verify that DUT identifiers and factory test metadata are permitted for public disclosure before merging the data snapshot into `main`.
