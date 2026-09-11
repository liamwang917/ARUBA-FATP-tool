# V14 Report Template Integration Specification — draft v14.1

Date: 2026-09-11

## Status

V13.6 on `main` remains the validated production data-normalization pipeline.

V14 is a **report-template integration phase** based on:

`Post-MIC limit_EV2_20260902-2.xlsx`

The V14 branch is:

`work/v14-report-template-20260911`

This phase remains analysis/contract only. Do not change the V13.6 parser/data contract and do not merge V14 to `main` until the report-template behavior has been validated with the user.

## 1. Non-negotiable template preservation rule

The supplied workbook is the visual/report master.

Unless explicitly approved below, V14 must not alter the template's:

- existing worksheet names or order;
- row heights or column widths;
- merged cells;
- fonts, fills, borders, alignments, or number formats;
- chart objects, positions, styles, titles, series, or axes;
- conditional formatting;
- print/page settings;
- defined names / AutoFilter;
- existing limit tables.

Implementation must work on a **copy** of the template. The original template is never modified in place.

Approved exceptions in V14.1:

1. `Frequency Response_1_12` changes from hidden to visible.
2. `Frequency Response_orignal` changes from hidden to visible.
3. A new Metadata worksheet is added to the report.
4. SNR data rows use V13.6 Main Station SNR values instead of the template's legacy calculated SNR formula.
5. Sensitivity data rows use V13.6 Main Station Sensitivity values instead of the template's legacy FR-at-1k formula.

No other layout/style/formula/chart changes are approved.

## 2. Template identity

- Filename: `Post-MIC limit_EV2_20260902-2.xlsx`
- Size: 5,422,338 bytes
- SHA-256: `5c24f2dbd1cc5350421c902369e7e250718f1fc20aa04f6e2f89ffe633527315`
- Original worksheets: 11
- Original charts: 8
- Original hidden worksheets: 2
- External workbook links: 1 legacy workbook relationship

The binary workbook is not committed to this public repository at this stage. The manifest records its structure and hash only.

## 3. Worksheet contract

### Original master state

1. `Audio Limit for EV` — visible
2. `Audio Limit for EV3` — visible
3. `Audio Limit_Sigma` — visible
4. `Frequency Response_1_3` — visible
5. `Frequency Response_1_12` — hidden
6. `Frequency Response_orignal` — hidden
7. `THD` — visible
8. `Phase` — visible
9. `Noise Floor` — visible
10. `SNR` — visible
11. `Sensitivity` — visible

Important: `Frequency Response_orignal` is intentionally recorded with the template's current spelling. Do not rename it.

### Approved V14 target state

- `Frequency Response_1_12` → visible
- `Frequency Response_orignal` → visible
- add one new Metadata sheet
- all other existing worksheet names/order/states remain unchanged

The exact Metadata sheet name/order is still an open item; recommendation is `Metadata` appended after `Sensitivity` so all existing sheet positions remain untouched.

## 4. Template calculation/report layout

### 4.1 Frequency Response / THD / Phase / Noise data sheets

The main curve sheets use the existing report pattern:

- row 27: frequency axis;
- rows 28 onward: statistics / sigma / derived limit calculations;
- row 39: production-data frequency header;
- row 40 onward: production DUT data;
- columns A/B/C in the existing curve sheets represent run identification/context;
- column D onward contains frequency-domain measurements.

The template already contains formula blocks for Mean / MAX / MIN / STDEV / sigma / derived limit calculations. V14 must not recreate or restyle these blocks.

### 4.2 Scalar sheets

`SNR` and `Sensitivity` currently use:

- row 27: reference frequency;
- rows 28–36: statistical/limit calculations;
- row 39: scalar header;
- row 40 onward: DUT data;
- column A: SN;
- column B: scalar value.

The statistics/limit formulas in rows 28–36 stay in place.

Approved V14 change:

- SNR row 40 onward column B is populated from V13.6 `08_SNR.SNR_dB`.
- Sensitivity row 40 onward column B is populated from V13.6 `09_Sensitivity.Sensitivity_dBFS`.
- the legacy per-DUT formulas in SNR/Sensitivity row 40 onward are replaced by source values only in the generated report copy.

### 4.3 Limit sheets

`Audio Limit for EV` and `Audio Limit for EV3` contain fixed product-limit tables for Frequency Response, THD, Phase, Noise Floor, SNR, and Sensitivity.

`Audio Limit_Sigma` is formula-driven and references the measurement/statistics sheets.

The current workbook contains a legacy external workbook link used by frequency-reference formulas in `Audio Limit for EV` and `Audio Limit for EV3`. Preserve that relationship for now; whether it should be internalized is still open.

## 5. Existing chart contract

The template contains one chart on each of:

- `Frequency Response_1_3`
- `Frequency Response_1_12`
- `Frequency Response_orignal`
- `THD`
- `Phase`
- `Noise Floor`
- `SNR`
- `Sensitivity`

Charts must not be moved or rebuilt.

## 6. V13.6 → template source mapping

| V13.6 normalized source | Template destination |
| --- | --- |
| `03_FR_1_3` | `Frequency Response_1_3` |
| `04_FR_1_12` | `Frequency Response_1_12` |
| `02_FR_original` | `Frequency Response_orignal` |
| `05_THD` | `THD` |
| `06_Phase` | `Phase` |
| `07_Noise` | `Noise Floor` |
| `08_SNR` | `SNR` |
| `09_Sensitivity` | `Sensitivity` |
| `01_Metadata` | new Metadata sheet |

### Curve-sheet row mapping

For the curve sheets:

- SN → column A;
- Test_Time → column B;
- Result/context → column C;
- frequency values → column D onward by matching frequency header, never by blind positional shifting.

For `Frequency Response_1_3`, THD, Phase, and Noise, column C follows the corresponding V13.6 Result semantics.

### RawData sheets

`Frequency Response_1_12` and `Frequency Response_orignal` are now approved to be visible.

V13.6 supplies SN, Test_Time, RawData_Match_Status, and frequency values.

Column-C content is still open. Recommendation: use `RawData_Match_Status` in column C because it explains blank rows (`NOT_PROVIDED`, `UNMATCHED`, `AMBIGUOUS`) without inventing PASS/FAIL.

## 7. Approved scalar semantics

### 7.1 SNR

V14 uses V13.6 Main Station SNR as authoritative.

Do not calculate V14 DUT SNR from FR@1k - Noise@1k.

The template's statistics/limit formulas continue to operate on the populated scalar data region.

### 7.2 Sensitivity

V14 uses V13.6 Main Station Sensitivity as authoritative.

Do not derive V14 DUT Sensitivity from FR@1k.

The template's statistics/limit formulas continue to operate on the populated scalar data region.

## 8. Metadata

Metadata is approved for inclusion in the template report.

Source: V13.6 `01_Metadata`.

Requirements:

- preserve the complete V13.6 Metadata field set;
- do not remove identifiers/context fields merely to fit the visual template;
- missing values remain blank;
- IDs/MAC-like values remain text-safe;
- adding Metadata must not alter any existing sheet layout or chart.

Recommended implementation: append one new `Metadata` sheet after `Sensitivity`, using the V13.6 Metadata table structure. Exact sheet name/order/style remains to be confirmed by the user before implementation.

## 9. V14 implementation principle

1. V13.6 continues to parse archives and produce normalized data.
2. V14 populates a **copy of the approved report template**.
3. V14 writes only to approved data-input regions.
4. Existing template charts/limits/styles stay owned by the template.
5. V14 validates frequency headers before writing.
6. If a source frequency is not found in the template header, do not shift data; report the mismatch.
7. Missing source values remain blank rather than being synthesized.
8. Existing V13.6 summary output remains available as a regression/debug artifact until V14 is validated.

## 10. Capacity / fixed-range finding

The template uses fixed statistics ranges:

- Frequency Response / FR 1/12 / Original / THD / Phase: generally row 40 through row 986 → 947 DUT rows.
- Noise Floor: row 40 through row 987 → 948 DUT rows.
- SNR / Sensitivity: row 40 through row 989 → 950 DUT rows.

V14 must not silently truncate data.

Before implementation, select one policy:

A. **Fixed-capacity policy (recommended for first V14):** if any output exceeds the template's supported row count, stop that report with a clear error/warning and do not silently omit rows.

B. Dynamic-extension policy: extend formulas/chart ranges/styles for additional rows. This changes template formulas/ranges and therefore requires explicit approval and more regression testing.

## 11. External-link finding

The master workbook contains one legacy external workbook relationship. `Audio Limit for EV` and `Audio Limit for EV3` contain formulas that reference cells in an external `[1]Frequency Response` workbook.

This can produce an Excel "Update Links" dependency when the original external source is unavailable.

Current policy: preserve it unchanged.

Open decision: keep the external dependency permanently, or later replace those references with equivalent internal template references after validation.

## 12. V14 acceptance criteria

Before any V14 report generator is considered ready:

- generated report is based on a copy of the master;
- all original sheet names/order remain unchanged;
- `Frequency Response_1_12` and `Frequency Response_orignal` are visible;
- the approved Metadata sheet is present;
- all 8 existing charts remain present and unchanged;
- existing row/column dimensions, merges, styles, conditional formatting, and print settings remain unchanged;
- SNR/Sensitivity DUT data use V13.6 Main Station values;
- statistics/limit blocks remain functional;
- V13.6 regression tests remain green;
- report-data writes are frequency-keyed and do not shift columns;
- no production workbook or factory-sensitive data is committed to the public repository.

## 13. Remaining open items before implementation

1. RawData sheets column C: use `RawData_Match_Status` (recommended) or leave blank?
2. Metadata sheet exact name/order/style: recommended `Metadata` appended after `Sensitivity`, using V13.6 Metadata table structure.
3. Capacity policy: fixed-capacity stop/warn vs dynamic formula/chart extension.
4. Legacy external workbook link: preserve permanently vs later internalize after validation.

No other product/data-semantic conflict was found in the current template analysis.
