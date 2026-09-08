# Changelog

This file tracks the ARUBA FATP tool's version history. Filenames no longer embed version numbers; use this file plus git/PR history for version context.

## v13 — architecture/spec locked, implementation pending

The V13 data model and report contract were updated on 2026-09-08. Implementation is not yet complete.

### Input / package model

1. Read ZIP packages directly instead of requiring pre-extracted folders.
2. Support both `ARUBA_MIC.zip` and `ARUBA_PREMIC.zip` using one shared FATP scanner/parser because their path/data structures are identical except for the top-level Test Type name.
3. Support `RawData_RD.zip` as an independent RawData pool split by Test Type:
   - `RawData_RD/MIC/**/*.csv`
   - `RawData_RD/PREMIC/**/*.csv`
4. Discover Online / Offline recursively from paths; do not assume a fixed directory depth.

### Reports

Generate separate reports by Test Type and Mode:

- `summary_MIC_Online.xlsx`
- `summary_MIC_Offline.xlsx`
- `summary_PREMIC_Online.xlsx`
- `summary_PREMIC_Offline.xlsx`

Standard sheet layout:

```text
00_Import_Log
01_Metadata
02_FR_original
03_FR_1_3
04_FR_1_12
05_THD
06_Phase
07_Noise
08_SNR
```

`Sealing` is removed from V13.

### Data-source mapping

- `FR_original` ← RawData `FR_Original`
- `FR_1_3` ← FATP FR CSV `FR`
- `FR_1_12` ← RawData `FR_1/12smooth`
- `THD` ← FATP FR CSV `THD`
- `Phase` ← FATP FR CSV `Phase`
- `Noise` ← FATP Noise CSV
- `SNR` ← FATP Main Station CSV `SNR`
- RawData `FR_1/3smooth` is intentionally not used.

### Run / RawData matching

RawData is not assigned to Online or Offline based only on its path. Matching must use:

1. Same Test Type (`MIC` / `PREMIC`).
2. Exact SN.
3. PASS/FAIL as a supporting condition.
4. Nearest FATP FR timestamp within a configurable maximum tolerance.
5. `UNMATCHED` when no safe candidate exists.
6. `AMBIGUOUS` when Online/Offline candidates are equally plausible.

All retest runs are preserved. Add `Latest_Run` rather than deleting older runs.

Within a single run, if multiple same-type CSV files exist, select the latest timestamp and log the other candidates in Import Log.

### Result semantics

Keep these meanings separate:

- `Station Result` — FATP/filename/path-level judgement.
- `APx Section Result` — CSV section-level `Test Result:` judgement.

Do not collapse them until the FATP judgement logic is fully confirmed.

### Import / QC requirements

V13 Import Log must cover at least:

- Total runs / unique SN
- PASS / FAIL counts
- Main / FR / Noise CSV counts
- Missing / duplicate / malformed files
- Frequency-axis mismatches
- Missing / invalid SNR
- RawData matched / unmatched / ambiguous counts
- Empty RawData sections
- Same-run duplicate CSV selection decisions

### Remaining implementation priorities

1. Build ZIP reader and recursive path scanner.
2. Introduce shared `TestRun` / `RawRecord` models.
3. Implement MIC/PREMIC shared station/FR/noise parsers.
4. Implement RawData parser and matching engine.
5. Split report generation by Test Type + Mode.
6. Add SNR sheet and remove Sealing code paths.
7. Add Import Log / QC and frequency validation.
8. Add automatic N / Mean / Max / Min / Range / STDEV statistics.
9. Convert timestamps to real Excel datetime; add freeze panes, AutoFilter, widths, number formats and PASS/FAIL conditional formatting.
10. Add dashboard/charts only after the data model is stable.

## v12 — current executable (`src/build_summary.py`)

Calculation-friendly version based on v9 logic.

- Writes Frequency/data values as real Excel numbers so pasted data participates in Excel's own Mean/Max/Min/STDEV.
- Keeps SN / Time / Result as text.
- Fixes the `FR_1_3` frequency bug present in earlier versions.
- SN parsing keeps only the `AP...` prefix up to the first underscore.

Known issue: FR/THD/Phase `Result` is derived from the FR filename (e.g. `FR_PASS`), which can disagree with the CSV's internal APx `Test Result:` field. This is planned to be corrected in V13 by preserving both result meanings.

## v9 and earlier

Earlier internal iterations preceding the snapshot first tracked in this repository (2026-09-07). Not individually preserved here.
