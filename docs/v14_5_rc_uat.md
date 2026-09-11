# V14.5 RC operational UAT

Before the first run, place the approved master workbook here:

```text
templates/Post-MIC limit_EV3_20260911.xlsx
```

The tool verifies its approved SHA-256 automatically. Do not rename, edit, or substitute this file.

Double-click `tools/run_v14_report.bat`, then select `ARUBA_MIC` and/or `ARUBA_PREMIC` archives. `RawData_RD` is optional. The tool writes `summary_*.xlsx` and `report_*.xlsx` to its current output directory.

The master and factory inputs are local operational files. Do not add them to Git or a public delivery archive.
