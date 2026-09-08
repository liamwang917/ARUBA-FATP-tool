# Usage

Current tool: `src/build_summary.py` (v12 logic, "calculation-friendly" variant based on v9 logic). See `CHANGELOG.md` for full version history and the v13 backlog.

## What it does

- Writes Frequency and data values as real Excel numbers when possible
- Keeps SN / Time / Result as text
- Lets pasted data calculate Mean / Max / Min / STDEV normally in Excel

## Carried over from earlier versions

- `FR_1_3` frequency bug fixed
- SN keeps only `AP...` before the first underscore
- Same `Online` / `RawData_RD` path rules
- Same section matching

## Note

Because values are numeric, Excel may display `80` instead of `80.000`, or `0` instead of `0.000`. This version is intended for calculation, not exact text appearance.

## Steps

1. Install Python 3.10+ and `openpyxl`:

   ```bash
   py -3 -m pip install -r requirements.txt
   ```

2. Windows — double-click:

   ```text
   tools\run_build_summary.bat
   ```

   Or run directly:

   ```bash
   python src/build_summary.py <raw-data-folder>
   ```

3. Choose the main raw-data folder. It must contain:

   - `Online/`
   - `RawData_RD/`

## Output

`summary.xlsx` is written inside the selected raw-data folder.
