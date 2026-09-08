build_summary_windows_v12_calc

Calculation-friendly version based on v9 logic.

What it does:
- Writes Frequency and data values as real Excel numbers when possible
- Keeps SN / Time / Result as text
- Lets pasted data into your template calculate Mean / Max / Min / STDEV normally

What stays the same:
- FR_1_3 frequency bug fixed
- SN keeps only AP... before the first underscore
- Same Online / RawData_RD path rules
- Same section matching

Note:
- Because values are numeric, Excel may display 80 instead of 80.000, or 0 instead of 0.000
- This version is intended for calculation, not exact text appearance

Usage:
1. Install Python 3.10+ and openpyxl
   py -3 -m pip install openpyxl

2. Double-click:
   run_build_summary_v12_calc.bat

3. Choose the main raw data folder containing:
   - Online
   - RawData_RD

Output:
- summary.xlsx inside the selected folder
