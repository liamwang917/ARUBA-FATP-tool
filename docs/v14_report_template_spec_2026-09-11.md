# V14 Report Template Integration Specification — draft v14.0

Date: 2026-09-11

## Status

V13.6 on `main` remains the validated production data-normalization pipeline.

V14 is a **report-template integration phase**. This document records the analyzed structure of the user-supplied workbook:

`Post-MIC limit_EV2_20260902-2.xlsx`

The V14 branch is:

`work/v14-report-template-20260911`

This phase is intentionally **analysis/contract only**. Do not change the V13.6 parser/data contract and do not merge V14 to `main` until the report-template mapping has been validated with the user.

## 1. Non-negotiable template preservation rule

The supplied workbook is the visual/report master.

Until the user explicitly approves a change, V14 must not alter the template's:

- worksheet names, order, or hidden/visible state;
- row heights or column widths;
- merged cells;
- fonts, fills, borders, alignments, or number formats;
- chart objects, positions, styles, titles, series, or axes;
- conditional formatting;
- print/page settings;
- defined names / AutoFilter;
- formulas or external-link relationships;
- existing limit tables.

Implementation must work on a **copy** of the template. The original template is never modified in place.

If implementation later requires changing any item above, stop and request explicit approval first.

## 2. Template identity

- Filename: `Post-MIC limit_EV2_20260902-2.xlsx`
- Size: 5,422,338 bytes
- SHA-256: `5c24f2dbd1cc5350421c902369e7e250718f1fc20aa04f6e2f89ffe633527315`
- Worksheets: 11
- Charts: 8
- Hidden worksheets: 2
- External workbook links: 1 legacy workbook relationship

The binary workbook is not committed to this public repository at this stage. The manifest records its structure and hash only.

## 3. Worksheet contract — exact names/order/state

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

Do not add columns or move the existing data area without explicit approval.

### 4.3 Limit sheets

`Audio Limit for EV` and `Audio Limit for EV3` contain fixed product-limit tables for:

- Frequency Response;
- THD;
- Phase;
- Noise Floor;
- SNR;
- Sensitivity.

`Audio Limit_Sigma` is formula-driven and references the measurement/statistics sheets.

The current workbook also contains a legacy external workbook link used by some frequency-reference formulas. Preserve that relationship unchanged during the V14 analysis phase.

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

Charts already reference the template's existing data regions. V14 must populate data without moving or rebuilding charts unless separately approved.

## 6. Proposed V13.6 → template source mapping

This is the working mapping for V14. No workbook modification is approved yet.

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
| `01_Metadata` | no direct template destination yet |

### Curve-sheet row mapping

For the curve sheets, the intended data-region mapping is:

- SN → column A;
- Test_Time → column B;
- Result/context → column C where the existing template already has a third context column;
- frequency values → column D onward by matching frequency header, not by blind positional shifting.

The exact Result source used in column C must remain consistent with V13.6 semantics and be finalized per sheet before implementation.

### RawData hidden sheets

For `Frequency Response_1_12` and `Frequency Response_orignal`, V13.6 currently supplies:

- SN;
- Test_Time;
- RawData_Match_Status;
- frequency values.

The template's existing A/B/C behavior must be preserved; any decision to place `RawData_Match_Status` in column C requires user approval before implementation.

## 7. Important semantic differences that require explicit user approval

These are analysis findings, not approved changes.

### 7.1 SNR

The current template computes SNR in column B from Frequency Response at 1 kHz minus Noise Floor at 1 kHz.

V13.6 instead treats Main Station `SNR` as the authoritative scalar value.

Do not change the existing SNR formula or replace it with V13.6 SNR until the user explicitly selects the desired V14 behavior.

### 7.2 Sensitivity

The current template derives Sensitivity from the Frequency Response 1 kHz value.

V13.6 separately provides Main Station `Sensitivity`.

Do not change the existing Sensitivity formula or replace it with V13.6 Sensitivity until explicitly approved.

### 7.3 Metadata

The template has no dedicated Metadata sheet equivalent to V13.6 `01_Metadata`.

Do not add a new worksheet to the report template without explicit approval.

## 8. V14 implementation principle

V14 should be additive:

1. V13.6 continues to parse archives and produce normalized data.
2. V14 takes normalized V13.6 data and populates a **copy of the approved report template**.
3. V14 writes only to approved data-input regions.
4. Template formulas/charts/limits/styles remain owned by the template.
5. V14 must validate frequency headers before writing.
6. If a source frequency is not found in the template header, do not shift data; log/report the mismatch.
7. Missing source values remain blank rather than being synthesized.
8. The existing V13.6 summary output remains available as a regression/debug artifact until V14 is validated.

## 9. V14 initial acceptance criteria

Before any V14 report generator is considered ready:

- the template copy opens successfully in Excel;
- all 11 sheet names/order/states match the master;
- hidden sheets remain hidden;
- all 8 charts remain present;
- no row/column/merge/style change is introduced;
- no formula/external-link change is introduced unless explicitly approved;
- V13.6 regression tests remain green;
- report-data writes are frequency-keyed and do not shift columns;
- no production workbook or factory-sensitive data is committed to the public repository.

## 10. Open items before implementation

1. Decide whether V14 SNR uses the template's current calculated formula or V13.6 Main Station SNR.
2. Decide whether V14 Sensitivity uses the template's current FR-at-1k formula or V13.6 Main Station Sensitivity.
3. Confirm column-C content for the two hidden RawData sheets.
4. Decide whether `01_Metadata` remains only in V13.6 summary or is represented somewhere in the report.
5. Confirm how many DUT rows V14 must support relative to the template's existing fixed formula/chart ranges.
6. Decide whether the legacy external workbook link should remain permanently or be internalized in a later approved revision.

Until these items are resolved, V14 remains a template-preservation/design PR only.
