# Repository Guidelines

## Project Structure & Module Organization

`src/build_summary.py` is the retained V12 regression entry point. V13 implementation is modular under `src/`; `tools/run_build_summary.bat` is the Windows launcher. Documentation lives in `README.md`, `docs/`, and `CHANGELOG.md`. Public tests must use synthetic/redacted data only.

## V13 Source of Truth and Branch Policy

`docs/v13_spec_2026-09-08.md` is authoritative for all V13 behavior. The active contract is **V13.6**. Do not redesign the approved workbook architecture unless the user explicitly requests it. Current V13 development must remain on `work/v13-architecture-20260908`. Never merge to `main` automatically.

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
