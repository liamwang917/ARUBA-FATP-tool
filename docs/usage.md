# Usage

V13.6 reads FATP archives and optional RawData archives directly. Do not extract them first.

## Setup

Install Python 3.10+ and dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Supported archive formats

V13.6 requires:

```text
.zip
.7z
.tar
.tar.gz
.tgz
```

RAR is not required.

## Inputs

Supply MIC, PREMIC, or both:

```text
ARUBA_MIC.<archive>
ARUBA_PREMIC.<archive>
```

At least one FATP archive is required.

RawData is optional:

```text
RawData_RD.<archive>
```

If RawData is not supplied, processing continues normally and RawData-derived sheets remain aligned but blank with `RawData_Match_Status = NOT_PROVIDED`.

## Windows launcher

`tools\run_build_summary.bat` is the user-facing launcher.

V13.6 implementation must update the file-selection dialog so it is not limited to ZIP and allows the supported archive extensions above.

## Output workbooks

Reports are created only for discovered Test Type/mode combinations, for example:

```text
summary_MIC_Online.xlsx
summary_MIC_Offline.xlsx
summary_PREMIC_Online.xlsx
summary_PREMIC_Offline.xlsx
```

Each V13.6 workbook contains exactly:

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

## Important V13.6 output rules

`Test_Time` comes from the filename timestamp of the source CSV used by each sheet, not globally from Main Station `test_start_time`.

`02_FR_original` and `04_FR_1_12` start with:

```text
SN
Test_Time
RawData_Match_Status
```

and do not display `Path_Result`, `FR_File_Result`, `RawData_Result`, or `RawData_PF_Mismatch`.

`08_SNR` contains only SNR-specific information; Sensitivity is written to `09_Sensitivity`.

`01_Metadata` captures all Main Station Column-A item keys and their Column-C values across the imported runs.

Runtime QC warnings are printed to the console; they do not add an Import Log worksheet.

## Matching controls

Current matching defaults remain configurable:

```text
--rawdata-max-time-delta-sec 60
--rawdata-ambiguous-margin-sec 5
```

## V12

V12 remains temporarily available as:

```powershell
python src/build_summary.py <raw-data-folder>
```

for regression comparison until V13.6 real-data validation is complete.
