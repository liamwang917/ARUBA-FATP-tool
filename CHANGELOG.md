# Changelog

This file tracks the ARUBA FATP tool's version history. Filenames no longer embed version numbers; use this file plus git/PR history for version context.

## v13.3 — limit evaluation deferred, result semantics clarified (2026-09-09)

Documentation/specification revision only. Executable code remains v12.

Confirmed and locked for V13:

1. Main Station CSV is a six-column format: `item_key,index,value,low_limit,high_limit,error_code`.
2. `tsr_id` is a 15-digit timestamp (`YYYYMMDDHHMMSS` + tenths digit), e.g. `202607061915366` = 2026-07-06 19:15:36.6.
3. `station_id` is used to cross-check Test Type derived from the path; `tester_id` should also be cross-checked against the station/tester path component when available.
4. `sfis_get_mac` is a device MAC address and must remain text.
5. The reviewed Main Station sample contains 21 FR station-check points plus scalar `Sensitivity`, `THD`, `Phase`, `Noise`, and `SNR`.
6. Those Main Station values do **not** replace the detailed data sources. Detailed workbook sheets remain sourced from FR/Noise CSV and RawData as defined in section 7 of the spec.
7. The Main Station 21-point/scalar values are retained internally for traceability and future template integration, but V13 does not add a dedicated `Station_Check` sheet.
8. Main Station columns 4/5 are recognized as Low/High limits, but V13 does **not** evaluate or output limits. There is no `Station_Limits` sheet and no `Limit_Derived_Result`; a dedicated Limit Excel template will be integrated later.
9. Result semantics now use explicit-source fields only: `Path_Result`, `FR_File_Result`, and `APx_Section_Result`. The ambiguous `Station_Result` field is removed.
10. `FR_1_3` remains the historical compatibility sheet name in V13 even though the source is the detailed 80-point FR section.

## v13.2 — Main Station CSV sample confirmed (2026-09-09)

Documentation/specification revision only. No executable-code change.

Confirmed from a real MIC PASS Main Station CSV sample:

1. Main Station rows have six columns and columns 4/5 hold one- or two-sided station limits.
2. Main Station includes a 21-point one-third-octave FR set plus `Sensitivity`, `THD`, `Phase`, `Noise`, and `SNR` values.
3. `tsr_id` is 15 digits, not 14 digits.
4. `station_id=ARUBA_MIC` can cross-check the Test Type inferred from the path.
5. `sfis_get_mac` is a MAC address and must be governed as device-identifying metadata.
6. MIC/PREMIC are confirmed structurally identical apart from the Test Type name.

v13.3 supersedes the earlier v13.2 proposal to derive result state from station limits.

## v13.1 — spec gaps closed (2026-09-09)

Documentation-only revision of `docs/v13_spec_2026-09-08.md`. No change to the v13.0 core architecture and no change to executable code.

Added to the specification:

1. CSV classification rules — content signature is authoritative, filename token is fallback, unresolved files are marked `UNCLASSIFIED` and logged rather than guessed (spec 4.1).
2. Matcher configuration parameters with proposed defaults: `rawdata_max_time_delta_sec`, `rawdata_ambiguous_margin_sec`, `rawdata_pass_fail_mode`, `sn_normalisation` (spec 11.1). Each RawData file is consumed by at most one run (spec 11.2).
3. `Latest_Run` definition — group key `(Test_Type, Mode, SN)`, ordered by `Test_Time` then `Run_ID`, exactly one `TRUE` per group (spec 10.1).
4. `01_Metadata` column contract, including the station fields the 2026-09-07 review asked to preserve (spec 16).
5. Downstream behaviour for `UNMATCHED` / `AMBIGUOUS` runs — the row is kept and data cells left blank, so all sheets stay row-aligned (spec 17).
6. Workbook formatting and per-frequency statistics block: `N` / `Mean` / `Max` / `Min` / `Range` / `STDEV`, real Excel datetimes, freeze panes, AutoFilter, conditional formatting. Dashboard explicitly deferred (spec 18).
7. Data governance rules for this public repository (spec 19).
8. Regression-test fixture expectations (spec 20).
9. An open-questions section collecting every `PROPOSED` value that still needs confirmation against production data (spec 21).

Also marked `docs/review_2026-09-07.md` as historical and its suggested workbook layout as superseded, since it still listed `Sealing`, `Dashboard` and `Statistics` sheets that V13 does not use.

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
- `FR_1_3` ← FATP FR CSV detailed `FR`
- `FR_1_12` ← RawData `FR_1/12smooth`
- `THD` ← FATP FR CSV detailed `THD`
- `Phase` ← FATP FR CSV detailed `Phase`
- `Noise` ← FATP Noise CSV detailed spectrum
- `SNR` ← FATP Main Station CSV `SNR`
- RawData `FR_1/3smooth` is intentionally not used.

### Run / RawData matching

RawData is not assigned to Online or Offline based only on its path. Matching must use:

1. Same Test Type (`MIC` / `PREMIC`).
2. Exact SN.
3. PASS/FAIL as a supporting condition.
4. Nearest FATP timestamp within a configurable maximum tolerance.
5. `UNMATCHED` when no safe candidate exists.
6. `AMBIGUOUS` when Online/Offline candidates are equally plausible.

All retest runs are preserved. Add `Latest_Run` rather than deleting older runs.

Within a single run, if multiple same-type CSV files exist, select the latest timestamp and log the other candidates in Import Log.

### Result semantics

V13 keeps separate source-specific results:

- `Path_Result` — FATP path `PASS` / `FAIL` folder.
- `FR_File_Result` — FR filename `FR_PASS` / `FR_FAIL`.
- `APx_Section_Result` — CSV section-level `Test Result:` judgement.

Do not collapse them into one result field.

### Import / QC requirements

V13 Import Log must cover at least:

- Total runs / unique SN
- PASS / FAIL counts
- Main / FR / Noise CSV counts
- Missing / duplicate / malformed files
- Frequency-axis mismatches
- Missing / invalid SNR
- `station_id` / `tester_id` path cross-check conflicts
- Result-source disagreements
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
11. Integrate the dedicated Limit Excel template in a later version; do not implement limit evaluation in V13.

## v12 — current executable (`src/build_summary.py`)

Calculation-friendly version based on v9 logic.

- Writes Frequency/data values as real Excel numbers so pasted data participates in Excel's own Mean/Max/Min/STDEV.
- Keeps SN / Time / Result as text.
- Fixes the `FR_1_3` frequency bug present in earlier versions.
- SN parsing keeps only the `AP...` prefix up to the first underscore.

Known issue: FR/THD/Phase `Result` is derived from the FR filename (e.g. `FR_PASS`), which can disagree with the CSV's internal APx `Test Result:` field. V13 resolves this by preserving separate source-specific result fields.

## v9 and earlier

Earlier internal iterations preceding the snapshot first tracked in this repository (2026-09-07). Not individually preserved here.
