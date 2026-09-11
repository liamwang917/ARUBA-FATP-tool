# V14 report-template manifest — V14.5 clean packaged master

This manifest describes the user-approved clean V14.5 report template intended to be
versioned and bundled with the tool.

- Filename: `Post-MIC limit_20260911.xlsx`
- Size: 859,035 bytes
- SHA-256: `a556aa066b9412fb17512bb4f992d26909676c5bc53a138616e2cebef2925724`
- Original sheet count: 11
- Original chart count: 8
- Hidden sheets: 0
- External workbook relationships: **0**
- Defined names: one AutoFilter database on `Frequency Response_1_3`

| # | Sheet | State | Used range | Formula cells | Charts |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | Audio Limit for EV | visible | A1:V31 | 63 | 0 |
| 2 | Audio Limit for EV3 | visible | A1:V32 | 63 | 0 |
| 3 | Audio Limit_Sigma | visible | A1:V73 | 603 | 0 |
| 4 | Frequency Response_1_3 | visible | A4:CE383 | 720 | 1 |
| 5 | Frequency Response_1_12 | visible | A26:CF305 | 720 | 1 |
| 6 | Frequency Response_orignal | visible | A26:CE305 | 720 | 1 |
| 7 | THD | visible | A26:CF121 | 640 | 1 |
| 8 | Phase | visible | C26:CE39 | 720 | 1 |
| 9 | Noise Floor | visible | C26:ADW39 | 6400 | 1 |
| 10 | SNR | visible | A26:B1000 | 8 | 1 |
| 11 | Sensitivity | visible | A26:B1000 | 9 | 1 |
| 12 | Metadata | generated / visible | generated from V13.6 `01_Metadata` | n/a | 0 |

## Clean-master status

The production DUT / RawData values previously present in rows 40+ were removed from
the release template. `Frequency Response_1_12` and
`Frequency Response_orignal` are already visible in the template.

The clean master intentionally retains the workbook structure, formulas, charts,
styles, limit blocks, print settings, frequency axes, and placeholders required by
the V14.5 writer.

## Locked V14.5 semantics

- `SNR` DUT values come directly from V13.6 Main Station SNR.
- `Sensitivity` DUT values come directly from V13.6 Main Station Sensitivity.
- RawData sheet column C = `RawData_Match_Status`.
- `Metadata` is appended after `Sensitivity` and follows V13.6 `01_Metadata`.
- Global data/statistics capacity = **947 DUTs**.
- Frequency-axis mismatch is fatal; no interpolation/resampling/partial mapping.
- External workbook links = none and must remain none.
- Remove stale `xl/calcChain.xml` in generated reports and request full Excel recalculation.
- Approved runtime formula correction:
  - `Frequency Response_1_3!D35 = D28+D32`
  - `Frequency Response_1_3!D36 = D28-D32`
- Preserve Metadata `test_start_time` / `test_end_time` to millisecond precision.
- DUT chart legends on the six curve charts show SN only.
- Noise Floor chart plotting starts at 100 Hz while worksheet data remain 0–7990 Hz.
- The stale FilterDatabase remains intentionally untouched.

## Preservation rule

Do not regenerate the template from scratch. V14.5 copies this approved workbook and
performs only the locked surgical OOXML updates.

A generated report is invalid if Microsoft Excel reports repair/recovery/corruption.
