# V14 report-template manifest

This manifest describes the current user-supplied V14 master workbook. The binary workbook is intentionally not committed to this public repository.

- Filename: `Post-MIC limit_EV3_20260911.xlsx`
- Size: 5,421,221 bytes
- SHA-256: `93af9584fa442b70c8d056921d33135db82656e772f9c84019adc46010c4eb7e`
- Original sheet count: 11
- Original chart count: 8
- Original hidden sheets: 2
- External workbook relationships: **0**
- Defined names: one AutoFilter database on `Frequency Response_1_3`

| # | Sheet | Original state | V14 target state | Used range | Formula cells | Charts |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | Audio Limit for EV | visible | visible | A1:V31 | 63 | 0 |
| 2 | Audio Limit for EV3 | visible | visible | A1:V32 | 63 | 0 |
| 3 | Audio Limit_Sigma | visible | visible | A1:V73 | 603 | 0 |
| 4 | Frequency Response_1_3 | visible | visible | A4:CE383 | 720 | 1 |
| 5 | Frequency Response_1_12 | hidden | **visible** | A26:CF305 | 720 | 1 |
| 6 | Frequency Response_orignal | hidden | **visible** | A26:CE305 | 720 | 1 |
| 7 | THD | visible | visible | A26:CF285 | 640 | 1 |
| 8 | Phase | visible | visible | A26:CE285 | 720 | 1 |
| 9 | Noise Floor | visible | visible | A26:ADW285 | 6400 | 1 |
| 10 | SNR | visible | visible | A26:B1000 | 500 | 1 |
| 11 | Sensitivity | visible | visible | A26:B1000 | 501 | 1 |
| 12 | Metadata | n/a | **new / visible / appended after Sensitivity** | generated from V13.6 `01_Metadata` | n/a | 0 |

## Locked V14.2 semantics

- `SNR` DUT values come directly from V13.6 Main Station SNR.
- `Sensitivity` DUT values come directly from V13.6 Main Station Sensitivity.
- `Frequency Response_1_12` becomes visible.
- `Frequency Response_orignal` becomes visible.
- RawData sheet column C = `RawData_Match_Status`.
- `Metadata` is appended after `Sensitivity` and follows V13.6 `01_Metadata`.
- Capacity policy = stop/warn if supported row capacity is exceeded; never silently truncate; do not auto-extend formulas/charts.
- External workbook links = none and must remain none.

## Existing fixed statistical ranges

- FR / FR 1/12 / Original / THD / Phase statistics use rows 40:986 (947 DUT rows).
- Noise statistics use rows 40:987 (948 DUT rows).
- SNR / Sensitivity statistics use rows 40:989 (950 DUT rows).

## Preservation note

Do not use this manifest as permission to regenerate the workbook from scratch. V14 must use the current master workbook as the copy source so all unlisted style, chart, print, relationship, and workbook metadata remain intact.

A V14 output is invalid if Microsoft Excel reports that the file needs recovery/repair or is corrupt.
