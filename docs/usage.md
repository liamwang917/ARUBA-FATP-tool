# Usage

V13 reads FATP and optional RawData ZIP packages directly. Do not extract them first.

## Setup

Install Python 3.10+ and the runtime dependency:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run

Supply `ARUBA_MIC.zip`, `ARUBA_PREMIC.zip`, or both. `RawData_RD.zip` is optional:

```powershell
py -3 -m src.main ARUBA_MIC.zip RawData_RD.zip --output-dir output
py -3 -m src.main --mic C:\input\ARUBA_MIC.zip --premic C:\input\ARUBA_PREMIC.zip --output-dir C:\output
```

On Windows, `tools\run_build_summary.bat` accepts the same arguments. Running the BAT without arguments opens a ZIP-selection dialog.

Available matching controls:

```text
--rawdata-max-time-delta-sec 60
--rawdata-ambiguous-margin-sec 5
```

Reports are created only for discovered Test Type/mode combinations, for example `summary_MIC_Online.xlsx`. Runtime QC warnings are printed to the console; they do not add an Import Log worksheet.

V12 remains available temporarily as `python src/build_summary.py <raw-data-folder>` for regression comparison.

