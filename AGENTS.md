# Repository Guidelines

## Project Structure & Module Organization

`src/build_summary.py` is the retained V12 regression entry point. V13 implementation is modular under `src/`; `tools/run_build_summary.bat` is the Windows launcher. Documentation lives in `README.md`, `docs/`, and `CHANGELOG.md`. Public tests must use synthetic/redacted data only.

## Version Source of Truth and Branch Policy

`docs/v13_spec_2026-09-08.md` remains authoritative for the validated V13.6 data-normalization pipeline on `main`.

V14 report-template work is governed by `docs/v14_report_template_spec_2026-09-11.md` and must remain on `work/v14-report-template-20260911` until the user explicitly approves merge. Never merge V14 to `main` automatically.

Do not redesign V13.6 parsing behavior as part of V14 template work unless the user separately approves it.

## V13.6 Input Rules

At least one FATP archive is required: MIC, PREMIC, or both. RawData is optional. When RawData is absent, processing continues normally and `RawData_Match_Status = NOT_PROVIDED`; do not label it `UNMATCHED`.

The archive selector/reader must not be ZIP-only. V13.6 requires support for:

```text
.zip
.7z
.tar
.tar.gz
.tgz
```

Use a generic archive-reader abstraction. RAR is not required.

## V13.6 Workbook Contract

Exactly these sheets are allowed:

```text
01_Metadata
02_FR_original
03_FR_1_3
04_FR_1_12
05_THD
06_Phase
07_Noise
08_SNR
09_Sensitivity
```

Do not create Import Log, statistics blocks, dashboards/charts, station-limit sheets, `Limit_Derived_Result`, APx/Section Result, or Sealing.

`02_FR_original` and `04_FR_1_12` leading columns must be exactly:

```text
SN
Test_Time
RawData_Match_Status
```

followed by frequency data. Do not display `Path_Result`, `FR_File_Result`, `RawData_Result`, or `RawData_PF_Mismatch` on those sheets.

`08_SNR` must not contain Sensitivity. `09_Sensitivity` is a separate sheet.

For THD, Phase, Noise, SNR, and Sensitivity, derive `Result` from Main Station CSV Column B: `1=PASS`, `0=FAIL`, missing/invalid=blank. Use the corresponding Column C value directly; never calculate substitute SNR/Sensitivity values.

## Test_Time and Metadata Rules

`Test_Time` follows the actual source CSV filename timestamp for each sheet. Do not globally use Main Station `test_start_time`.

- Metadata/SNR/Sensitivity → Main Station filename time
- FR/THD/Phase → selected FR filename time
- Noise → selected Noise filename time
- RawData sheets → matched RawData filename time

For a 15-digit filename token such as `202609101633182`, use the first 14 digits for `Test_Time` and preserve the full token as an opaque identifier when needed. Do not assume the last digit is fractional seconds.

Main Station `test_start_time` / `test_end_time` parsing must support production fractional seconds.

`01_Metadata` must capture the complete Main Station Column-A item key to Column-C value set. Do not use a small whitelist. Across runs, build the header as the union of first-seen item keys; missing values are blank. Preserve IDs/MAC-like values as text when numeric coercion could lose fidelity.

## Build, Test, and Development Commands

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
python -m src.main
python -m unittest discover -s tests -v
```

V12 remains available at `src/build_summary.py` until V13.6 regression validation is complete.

## Testing and Data Safety

Every behavior change must add/update automated tests when applicable. V13.6 tests must include multi-archive input, production-style fractional-second timestamps, source-specific Test_Time, complete Metadata A→C capture, 02/04 exact columns, `09_Sensitivity`, and exact nine-sheet output.

Never commit real production ZIP/7Z/TAR/CSV/WAV/XLSX, DUT serial numbers, MAC addresses, operator/tester IDs, or other factory-sensitive data. Use synthetic/redacted fixtures only.

## Completion Guidelines

Before completing a coding task:

1. run relevant tests;
2. inspect generated synthetic XLSX structure;
3. confirm no production/private data is staged;
4. report changed files;
5. report test commands/results;
6. report known limitations;
7. report commit SHA;
8. do not merge to main.

## V14 Template Preservation Rules

The user-supplied report workbook is an immutable master during the current V14 design phase.

Do not alter worksheet names/order/visibility, formatting, row heights, column widths, merges, charts, conditional formatting, print settings, formulas, external links, or existing limit tables without explicit user approval.

V14 implementation must eventually populate a copy of the approved template and write only to approved data regions. Do not regenerate the workbook from scratch.

The binary template is not committed to this public repository at this stage. Use the manifest/hash in `data/templates/v14_template_manifest_2026-09-11.md` to identify the analyzed workbook.


## V14.4 Workbook Integrity Rules

For the approved V14 report master:

- clear legacy DUT data-region contents before writing new DUT data;
- frequency-axis mismatch is fatal; never resample/interpolate/shift/partially map;
- use column C mapping from the V14 spec exactly;
- global statistical capacity is 947 DUTs; chart coverage is separate and must not truncate statistics;
- remove stale calcChain and request full recalculation on Excel open;
- do not use openpyxl or LibreOffice load/save round-trip to populate the approved master;
- preserve protected OOXML chart/drawing/style/theme/printer parts byte-for-byte;
- apply the explicitly approved `Frequency Response_1_3!D35=D28+D32` and `D36=D28-D32` correction, but do not repair other unrelated template defects;
- preserve Metadata `test_start_time` / `test_end_time` fractional seconds to millisecond precision;
- preserve original worksheet dimension bounds unless actual written data require expansion; do not shrink/reset them unnecessarily;
- treat any Excel repair/recovery/corrupt warning as a failed output.

Do not merge V14 to main unless the user explicitly approves it.


## V14 End-to-End User Workflow

V14 is integrated into the V13.6 run. Normal users select only the FATP archive inputs (MIC/PREMIC and optional RawData). They must not be required to manually select V13.6 summary XLSX files or browse for the report template on every run.

The production delivery package must locate its approved local template automatically from a fixed packaged/configured location, validate its identity, then produce the final V14 report(s) in the same run.

Intermediate V13.6 summaries may remain available for debug/regression, but they are not a required manual input step.


## Noise Floor chart log-axis fix

The only approved chart-content change in V14.5 is to remove 0–90 Hz from the plotted Noise Floor chart series because the X axis is logarithmic and starts visually at 100 Hz.

Keep Noise worksheet data/statistics at 0–7990 Hz. Keep chart type/style/position/axes/formatting unchanged. Update only Noise chart X/Y source ranges to start at 100 Hz (column N in the approved master). Do not modify the other seven charts.


## SN-only DUT chart legends

For the six curve charts (FR_1_3, FR_1_12, FR_original, THD, Phase, Noise Floor), each DUT series title must reference only its SN cell in column A. Do not include Test_Time or Result/status in the legend.

Do not alter plotted data, chart formatting, axes, positions, or non-DUT limit/statistics series. SNR and Sensitivity chart labels remain unchanged.
