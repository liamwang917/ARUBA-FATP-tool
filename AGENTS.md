# Repository Guidelines

## Project Structure & Module Organization

`src/build_summary.py` is the current v12 implementation and stable entry point; keep V12 available until V13 regression testing is complete. `tools/run_build_summary.bat` is the Windows launcher. Documentation lives in `README.md`, `docs/`, and `CHANGELOG.md`. Data inventories and sanitized validation records belong under `data/manifests/` and `data/snapshots/`; reviewable generated artifacts may go under `data/outputs/`.

## V13 Source of Truth and Branch Policy

`docs/v13_spec_2026-09-08.md` is authoritative for all V13 behavior. Reference it for details; do not redesign the approved workbook architecture unless the user explicitly requests it. Current V13 development must remain on `work/v13-architecture-20260908`. Never merge to `main` automatically.

## V13 Input and Workbook Contract

At least one FATP package is required: `ARUBA_MIC.zip`, `ARUBA_PREMIC.zip`, or both. `RawData_RD.zip` is optional. When it is absent, processing continues normally: this is not an error, `RawData_Match_Status` is `NOT_PROVIDED` (never `UNMATCHED`), and RawData-derived values remain blank.

Do not parse or use APx/Section Test Result fields, and do not create `APx_Section_Result` or `Section_Result`. Also do not create `00_Import_Log`, statistical blocks (N/Mean/Max/Min/Range/STDEV), dashboards/charts, station-limit sheets, or `Limit_Derived_Result`.

For `05_THD`, `06_Phase`, `07_Noise`, and `08_SNR`, derive `Result` from Main Station CSV column B: `1` = `PASS`, `0` = `FAIL`, and missing/invalid = blank. Use the Main Station SNR value directly; never calculate a substitute when the item is missing.

## Build, Test, and Development Commands

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
python src/build_summary.py <raw-data-folder>
python -m py_compile src/build_summary.py
```

The builder writes `summary.xlsx` beside the input folder. The final command performs a syntax check.

## Coding Style & Naming Conventions

Use Python 3.10+, four-space indentation, UTF-8, PEP 8-compatible formatting, and grouped imports. Follow existing conventions: `snake_case` functions and variables, `UPPER_SNAKE_CASE` constants, type hints at parser boundaries, and `pathlib.Path` for paths. Keep scanner, parser, matcher, and workbook-writing responsibilities separable.

## Testing and Data Safety

Every behavior change must add or update automated tests when applicable. Run relevant tests plus targeted MIC/PREMIC regression checks against the locked workbook contract. Tests must use synthetic or redacted fixtures. Never commit real production ZIP, CSV, WAV, XLSX, DUT serial numbers, MAC addresses, operator/tester IDs, or other factory-sensitive data.

## Commit, Pull Request, and Completion Guidelines

Use short scoped commits such as `docs: clarify optional RawData behavior`. Pull requests should identify the contract or bug addressed, link issues, and describe validation and workbook changes.

Before completing a coding task, run relevant tests; confirm no production/private data is staged; then report changed files, test commands and results, known limitations, and the commit SHA.

