# Repository Guidelines

## Project Structure & Module Organization

`src/build_summary.py` is the current v12 Python implementation and stable command-line entry point. `tools/run_build_summary.bat` is the Windows launcher. Product behavior, usage, and version decisions live in `README.md`, `docs/usage.md`, `CHANGELOG.md`, and `docs/v13_spec_2026-09-08.md`; treat the V13 specification as authoritative for new architecture work. `data/manifests/` records input inventories, `data/snapshots/` documents validated datasets, and `data/outputs/` is reserved for reviewable generated artifacts. Keep raw factory CSV, WAV, and ZIP files out of this public repository.

## Build, Test, and Development Commands

Create an environment and install the only runtime dependency:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Run the current builder directly or through the Windows wrapper:

```powershell
python src/build_summary.py <raw-data-folder>
tools\run_build_summary.bat <raw-data-folder>
python -m py_compile src/build_summary.py
```

The first two commands generate `summary.xlsx` beside the selected input folder; the final command is a fast syntax check.

## Coding Style & Naming Conventions

Use Python 3.10+, four-space indentation, UTF-8 source, and standard-library modules where practical. Follow existing conventions: `snake_case` for functions and variables, `UPPER_SNAKE_CASE` for constants, and type hints for parser boundaries and structured returns. Prefer `pathlib.Path` over string path manipulation. Keep scanner, parser, matching, and workbook-writing responsibilities separable as V13 evolves. No formatter or linter is configured, so keep changes PEP 8-compatible and imports grouped consistently.

## Testing Guidelines

There is currently no automated test suite. At minimum, run `py_compile` and exercise affected flows with approved or synthetic MIC/PREMIC fixtures. Verify sheet names, numeric cell types, row alignment, result flags, and Online/Offline outputs against the locked V13 workbook contract. Record reusable sanitized fixtures or hashes under `data/`; never commit production identifiers or raw payloads.

## Commit & Pull Request Guidelines

Recent history uses short, imperative, scoped subjects such as `docs: align README with approved V13.4 snapshot`. Continue the `<scope>: <summary>` pattern (for example, `fix: preserve all retest runs`). Pull requests should state the contract or bug addressed, list validation commands and datasets, describe workbook changes, and link relevant issues. Include redacted screenshots or output summaries when spreadsheet layout changes, and call out any departure from the V13 specification.

