# V14 Report Template Integration Specification — draft v14.5

Date: 2026-09-11

## Status

V13.6 on `main` remains the validated production data-normalization pipeline.

V14 is a **report-template integration phase** based on:

`Post-MIC limit_20260911.xlsx`

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

Approved exceptions in V14.4:

1. `Frequency Response_1_12` is visible in the clean packaged master and remains visible.
2. `Frequency Response_orignal` is visible in the clean packaged master and remains visible.
3. A new `Metadata` worksheet is appended after `Sensitivity`.
4. SNR data rows use V13.6 Main Station SNR values instead of the template's legacy calculated SNR formula.
5. Sensitivity data rows use V13.6 Main Station Sensitivity values instead of the template's legacy FR-at-1k formula.
6. Before writing new DUT data, the approved DUT data regions are cleared so no legacy production rows remain.
7. The stale `xl/calcChain.xml` part and its workbook relationship/content-type entry are removed because SNR/Sensitivity formula cells become literal values.
8. Workbook calculation properties are updated to request Excel recalculation on open: `calcMode="auto"`, `fullCalcOnLoad="1"`, and `forceFullCalc="1"`.
9. `Frequency Response_1_3!D35` is corrected to `=D28+D32` and `D36` is corrected to `=D28-D32`, so the 80 Hz upper/lower limits use Mean ± 10 sigma consistently with the row labels and neighboring frequencies.

No other layout/style/formula/chart changes are approved.

## 2. Template identity

- Filename: `Post-MIC limit_20260911.xlsx`
- Size: 859,035 bytes
- SHA-256: `a556aa066b9412fb17512bb4f992d26909676c5bc53a138616e2cebef2925724`
- Original worksheets: 11
- Original charts: 8
- Original hidden worksheets: 0
- External workbook links: **0 (confirmed removed in the new master template)**

The user-approved clean V14.5 template is versioned in this repository at `templates/Post-MIC limit_20260911.xlsx`. Legacy DUT / RawData production values have been removed. Its SHA-256 `a556aa066b9412fb17512bb4f992d26909676c5bc53a138616e2cebef2925724` is the packaged production template identity.

## 3. Worksheet contract

### Original master state

1. `Audio Limit for EV` — visible
2. `Audio Limit for EV3` — visible
3. `Audio Limit_Sigma` — visible
4. `Frequency Response_1_3` — visible
5. `Frequency Response_1_12` — visible
6. `Frequency Response_orignal` — visible
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

The Metadata sheet name/order is now **locked**: `Metadata`, appended after `Sensitivity`, so all original 11 sheet positions remain untouched.

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

The current master workbook has been reissued by the user with the legacy external workbook relationship removed. V14 must not recreate any external workbook dependency.

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

Column C is locked as follows:

- `Frequency Response_1_3` → V13.6 `FR_File_Result`.
- `THD` → V13.6 item `Result`.
- `Phase` → V13.6 item `Result`.
- `Noise Floor` → V13.6 item `Result`.
- `Frequency Response_1_12` → `RawData_Match_Status`.
- `Frequency Response_orignal` → `RawData_Match_Status`.

For report display, item pass/fail text is normalized to uppercase `PASS` / `FAIL`. Do not use `Path_Result` as the report-sheet column-C value.

### RawData sheets

`Frequency Response_1_12` and `Frequency Response_orignal` are now approved to be visible.

V13.6 supplies SN, Test_Time, RawData_Match_Status, and frequency values.

Column C is now **locked** to `RawData_Match_Status` because it explains blank rows (`NOT_PROVIDED`, `UNMATCHED`, `AMBIGUOUS`) without inventing PASS/FAIL.

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

- preserve the complete V13.6 Metadata field set and value precision;
- `Test_Time` remains the compact 14-digit filename timestamp used by the report;
- Main Station `test_start_time` / `test_end_time` must preserve production fractional seconds to millisecond precision (for example `2026-09-10 16:33:19.092`); do not truncate them to whole seconds;
- do not remove identifiers/context fields merely to fit the visual template;
- missing values remain blank;
- IDs/MAC-like values remain text-safe;
- adding Metadata must not alter any existing sheet layout or chart.

Locked implementation: append one new `Metadata` sheet after `Sensitivity`, using the V13.6 `01_Metadata` table structure. Do not insert Metadata between any of the original template sheets.

## 9. V14 implementation principle

1. V13.6 continues to parse archives and produce normalized data.
2. V14 automatically populates a **copy of the approved local report template** as part of the same V13.6 run; normal users do not manually select intermediate summary workbooks.
3. V14 writes only to approved data-input regions.
4. Existing template charts/limits/styles stay owned by the template.
5. V14 validates the complete source frequency axis against the destination row-39 template axis before writing.
6. Any frequency-axis mismatch is **fatal for that report**. Do not resample, interpolate, shift, partially map, or degrade-to-blank.
7. Before population, clear all prior DUT data cells in the approved data regions on the eight measurement sheets. Preserve rows 27–36 statistics/limit formulas and row 39 headers.
8. Missing source values remain blank rather than being synthesized.
9. Existing V13.6 summary output remains available as a regression/debug artifact until V14 is validated.
10. The implementation must preserve the Excel package surgically; it must not load and re-save the master workbook through a general spreadsheet round-trip library.

## 9.1 Clear-before-write rule

The current master contains legacy production DUT rows. They must never participate in a newly generated report.

Before writing new data, V14 must clear the prior DUT data region while preserving the template's statistics/limit/header areas:

- `Frequency Response_1_3`: clear DUT values from row 40 through the supported data range.
- `Frequency Response_1_12`: same.
- `Frequency Response_orignal`: same.
- `THD`: same.
- `Phase`: same.
- `Noise Floor`: same.
- `SNR`: clear the existing DUT/formula data rows that V14 replaces with Main Station scalar values.
- `Sensitivity`: same.

Only data-region cell content is cleared. Existing styles, row heights, column widths, formulas outside the data region, charts, drawings, limit blocks, printer settings, and workbook appearance remain unchanged.

## 9.2 Workbook-integrity implementation constraints

V14 template population must use a **surgical OOXML package approach** or another method proven to preserve all non-approved parts byte-for-byte.

For the V14 template path, do **not** use:

- openpyxl load/save round-trip;
- LibreOffice / soffice headless save/recalculation;
- full workbook regeneration from scratch.

These are not prohibited for unrelated synthetic summaries, but they are prohibited for modifying the approved V14 master template.

Required workbook-internal changes include:

- remove `xl/calcChain.xml`;
- remove the calcChain relationship from `xl/_rels/workbook.xml.rels`;
- remove the calcChain override from `[Content_Types].xml`;
- set `calcMode="auto"`, `fullCalcOnLoad="1"`, and `forceFullCalc="1"` in workbook calculation properties;
- add the `Metadata` worksheet relationship/content type correctly;
- update worksheet `<dimension>` refs whenever actual written cells extend beyond the original bound, including to earlier columns/rows. Preserve the original start cell unless a real write expands the used range left/up; never shrink an existing max row/column merely because current DUT data are smaller.

For written text, shared-string bookkeeping must remain valid. Using inline strings for newly written cells is acceptable if Excel opens cleanly and the package remains valid.

A package-level regression test must verify that protected parts remain byte-identical, especially:

- `xl/charts/*`
- `xl/drawings/*`
- `xl/styles.xml`
- `xl/theme/*`
- `xl/printerSettings/*`

## 10. Data capacity vs chart display capacity

The template's statistical formulas and charts have different capacities and must be treated separately.

### 10.1 Statistical/data capacity

The fixed statistics ranges are:

- Frequency Response / FR 1/12 / Original / THD / Phase: row 40 through row 986 → **947 DUT rows**.
- Noise Floor: row 40 through row 987 → 948 DUT rows.
- SNR / Sensitivity: row 40 through row 989 → 950 DUT rows.

Because one report uses the same DUT population across sheets, V14 uses **947 DUTs as the global data/statistics capacity**.

All imported DUT rows up to 947 must participate in the existing Mean / MAX / MIN / STDEV.P / sigma / limit formulas.

V14 must never truncate data simply because a chart visualizes fewer DUTs.

If DUT count exceeds 947:

- stop that report with a clear error/warning;
- do not silently omit rows;
- do not dynamically extend statistical formula ranges in V14.3.

### 10.2 Chart display capacity

The existing charts have smaller, fixed source ranges / enumerated series. They are a visualization layer only and do **not** define the statistical data capacity.

V14.3 policy:

- preserve all existing chart XML/ranges/series exactly;
- do not expand or rebuild charts;
- when DUT count is greater than the chart's existing display coverage but less than or equal to 947, the report remains valid;
- all DUT rows are still written and included in statistics;
- the chart shows only the subset supported by the existing template;
- surface a runtime/console warning that chart display coverage is smaller than the imported DUT count.

Do not use the raw chart `<c:ser>` count as a DUT-capacity number because charts may also contain non-DUT series such as limits/reference/statistical series.

## 11. External-link status

The replacement master template `Post-MIC limit_20260911.xlsx` has been verified to contain **no `xl/externalLinks/` relationship**.

V14 rule:

- do not add or recreate an external workbook link;
- all generated reports must remain self-contained with respect to workbook links.

## 12. V14 acceptance criteria

Before any V14 report generator is considered ready:

- generated report is based on a copy of `Post-MIC limit_20260911.xlsx`;
- all original sheet names/order remain unchanged, with only the approved appended `Metadata` sheet;
- `Frequency Response_1_12` and `Frequency Response_orignal` are visible;
- the approved Metadata sheet is present;
- all 8 existing charts remain present and unchanged;
- existing row/column dimensions, merges, styles, conditional formatting, and print settings remain unchanged;
- SNR/Sensitivity DUT data use V13.6 Main Station values;
- statistics/limit blocks remain functional;
- V13.6 regression tests remain green;
- report-data writes are frequency-keyed and do not shift columns;
- no production workbook or factory-sensitive data is committed to the public repository;
- generated XLSX opens in Microsoft Excel **without repair/recovery/corruption warning**;
- generated XLSX contains no external workbook links;
- no legacy DUT data remains after clear-before-write;
- frequency-axis mismatch fails the report before data population;
- `calcChain.xml` is absent from generated V14 output;
- Excel recalculates statistics/limits on open;
- protected chart/drawing/style/theme/printer parts remain byte-identical to the master where no approved change applies.

## 13. Locked V14.4 decisions before implementation

1. RawData sheets column C = `RawData_Match_Status`.
2. Metadata sheet name = `Metadata`; append it after `Sensitivity`; data structure follows V13.6 `01_Metadata`.
3. Data/statistics capacity = **947 DUTs globally**. Chart display capacity is separate and may be smaller; charts remain unchanged and may visualize only their existing subset. Never truncate statistical data to chart coverage.
4. External workbook links = none; do not recreate them.
5. SNR = V13.6 Main Station SNR value.
6. Sensitivity = V13.6 Main Station Sensitivity value.
7. `Frequency Response_1_12` and `Frequency Response_orignal` = visible in generated V14 reports.
8. Clear legacy DUT data regions before writing any new report data.
9. Column C = FR_File_Result for FR_1_3; item Result for THD/Phase/Noise; RawData_Match_Status for the two RawData FR sheets.
10. Frequency-axis mismatch is fatal; no resampling or partial mapping.
11. Remove stale calcChain and force full recalculation on open.
12. Do not use openpyxl/LibreOffice round-trip for the approved V14 master.
13. Preserve protected OOXML parts byte-for-byte.
14. Output is invalid if Microsoft Excel displays repair/recovery/corruption warnings.
15. `Frequency Response_1_3!D35 = D28+D32` and `D36 = D28-D32` are approved corrections.
16. Metadata `test_start_time` / `test_end_time` preserve millisecond precision.
17. Worksheet `<dimension>` refs must continue to cover all existing cells and must not be unnecessarily shrunk or reset to `A1`.

There are no remaining product-level semantic decisions blocking implementation. The next step is implementation/review focused on workbook integrity and preservation.


## 14. V14.3 clarification — statistics must use the full DUT population

The user explicitly confirmed that chart display coverage must not reduce the data population used for statistics.

Therefore:

- 947 DUTs remains the approved global data/statistics capacity;
- STDEV.P and all other existing statistical calculations use every populated DUT row within the fixed statistical range;
- chart coverage is intentionally allowed to be smaller than the data/statistics population;
- no data row is dropped merely to make chart and statistics row counts equal.


## 15. Known pre-existing template issues

The user has now explicitly approved correction of the former 80 Hz sigma-reference anomaly:

- `Frequency Response_1_3!D35` → `=D28+D32`
- `Frequency Response_1_3!D36` → `=D28-D32`

The remaining pre-existing issue stays outside V14's change scope:

1. The workbook's existing `_xlnm._FilterDatabase` range is stale/inconsistent with the current data extent. Preserve it unchanged unless the user separately approves a template-maintenance revision.

Do not silently clean up any other template behavior.


## 16. Final user workflow — end-to-end automatic report generation

V14 is not a separate manual post-processing utility. It is the final report layer of the existing V13.6 pipeline.

The normal user flow is:

```text
run_build_summary.bat / V14 launcher
        ↓
select ARUBA_MIC / ARUBA_PREMIC archive(s)
+ optional RawData archive
        ↓
V13.6 parsing / matching / normalized data generation
        ↓
V14 automatically loads the approved packaged report-template master
        ↓
V14 populates the report template
        ↓
final V14 report workbook(s) are written
```

The user must **not** be required to manually select V13.6 summary workbooks during normal operation.

V13.6 summary workbooks may still be generated/retained as debug or regression artifacts, but V14 must consume the normalized V13.6 data automatically within the same run.

### Template handling

The approved V14 template should be committed in the repository under a fixed path and bundled with the release, for example:

`templates/Post-MIC limit_20260911.xlsx`

Prefer committing a sanitized master with legacy DUT rows removed. Normal users do not browse for this file on each run, and a packaged EXE must embed or install this template automatically.

At runtime the tool must:

1. locate the expected template automatically;
2. verify its expected SHA-256 / approved-template identity;
3. fail with a clear installation/configuration error if the template is missing or incorrect;
4. never silently substitute another workbook.

A template file-picker may exist only as an explicit developer/debug override, not as the normal production workflow.

### Final output behavior

For every Test Type / Mode discovered by V13.6, V14 should directly create the corresponding final report, for example:

```text
report_MIC_Online.xlsx
report_MIC_Offline.xlsx
report_PREMIC_Online.xlsx
report_PREMIC_Offline.xlsx
```

Only reports for discovered Test Type / Mode combinations are produced.


## 17. Noise Floor chart log-axis warning — approved V14.5 fix

Microsoft Excel runtime validation showed one remaining chart warning on the `Noise Floor` worksheet:

`Negative or zero values cannot be plotted correctly on log charts.`

Cause:
- the Noise chart uses a logarithmic X axis;
- its X source currently includes 0 Hz;
- the chart X-axis visible minimum is already 100 Hz.

Approved fix:
- keep all Noise Floor worksheet data and statistics unchanged from 0–7990 Hz;
- keep the existing chart type, style, position, axes, formatting, and log scale unchanged;
- change only the Noise Floor chart series source ranges so plotted X/Y data start at 100 Hz instead of 0 Hz;
- for the approved master, 100 Hz is column N, so chart X ranges start at row-39 column N and each corresponding Y series starts at the same column;
- do not alter FR/THD/Phase/SNR/Sensitivity charts;
- do not remove or modify worksheet data below 100 Hz.

Acceptance:
- Microsoft Excel opens without the logarithmic-axis popup;
- Noise data/statistics remain unchanged;
- chart appearance remains otherwise unchanged.


## 18. DUT chart legend — SN only

User-approved chart-label cleanup for the six curve charts:

- `Frequency Response_1_3`
- `Frequency Response_1_12`
- `Frequency Response_orignal`
- `THD`
- `Phase`
- `Noise Floor`

Current DUT series titles reference columns A:C for each DUT row, which makes Microsoft Excel display concatenated legend text such as:

`SN Test_Time PASS/FAIL`

Approved behavior:

- every DUT series legend label must display **SN only**;
- use the row's column-A SN cell as the series title source;
- do not include Test_Time or PASS/FAIL/RawData status in the legend;
- do not alter the plotted X/Y values, series count, line/marker formatting, chart size/position, axes, or non-DUT limit/statistics series;
- apply this only to DUT-series titles;
- SNR and Sensitivity charts keep their existing metric/limit legend labels because they are not per-DUT curve legends.

Implementation example for a DUT on row 40:

- current series title reference: `'Frequency Response_1_3'!$A$40:$C$40`
- target series title reference: `'Frequency Response_1_3'!$A$40`

Repeat for each DUT series row on the six curve charts.


## 19. Pre-merge operational UAT gate

Snapshot validation is necessary but not sufficient for merge.

Before PR #4 can be considered merge-ready, the user must operate the actual Windows V14 tool end-to-end on real local archives.

### Required production user flow

Normal operation must be:

```text
double-click tools/run_v14_report.bat
        ↓
select ARUBA_MIC and/or ARUBA_PREMIC archive(s)
+ optional RawData_RD archive
        ↓
V13.6 normalization runs automatically
        ↓
approved local V14 template is found and SHA-256 verified automatically
        ↓
V14 report generation runs automatically
        ↓
summary_*.xlsx + report_*.xlsx are written
```

Normal users must not manually select:
- V13.6 summary workbooks;
- the V14 template on every run.

### Local template requirement

The clean template is intended to be versioned with the repository/tool at:

`templates/Post-MIC limit_20260911.xlsx`

The tool must:
- check that the file exists;
- verify the approved SHA-256;
- stop with a clear user-facing error if it is missing or incorrect;
- never silently bypass the check in normal production mode.

Developer-only overrides may remain available through CLI flags but must not be part of the normal BAT workflow.

### Operational acceptance checks

User UAT must cover at least:
- MIC only;
- PREMIC only;
- MIC + PREMIC together;
- RawData present;
- RawData absent;
- at least ZIP and one additional supported archive format if practical;
- correct automatic Online/Offline report discovery;
- correct output filenames;
- clear console/error messages;
- no manual intermediate-summary/template selection;
- generated reports open in Microsoft Excel without repair/recovery warnings;
- formulas recalculate;
- six curve legends show SN only;
- Noise Floor chart has no logarithmic-axis popup.

PR #4 must remain Draft and unmerged until the user explicitly confirms this operational UAT.


## 20. Repository-packaged template

The user has approved storing the V14 template in GitHub so the production tool/EXE can ship with it automatically.

Release policy:

- version the approved clean template binary at `templates/Post-MIC limit_20260911.xlsx`;
- legacy DUT / RawData production values are removed while the report structure, formulas, chart objects, styles and print settings remain the master contract;
- update `TEMPLATE_SHA256` and the manifest to the committed release-template SHA-256;
- the normal tool uses this repository-packaged template automatically;
- no template file picker in normal operation;
- a future EXE/package embeds or installs this template with the application;
- developer template override may remain available only as an explicit CLI option.

The template binary and its release SHA-256 become part of the versioned application contract.


### Clean packaged master — final identity

The final V14.5 operational-UAT master supplied on 2026-09-11 is:

- `Post-MIC limit_20260911.xlsx`
- size: 859,035 bytes
- SHA-256: `a556aa066b9412fb17512bb4f992d26909676c5bc53a138616e2cebef2925724`
- 11 original worksheets
- 8 charts
- 0 hidden worksheets
- 0 external workbook links
- legacy production DUT / RawData row values removed
- `Frequency Response_1_12` visible
- `Frequency Response_orignal` visible

The existing V14.5 writer continues to apply the previously validated runtime
safeguards for the FR_1_3 10-sigma formula correction, SN-only DUT chart legends,
Noise Floor >=100 Hz plotted source range, Metadata millisecond preservation and
Excel recalculation handling.


## PREMIC Online operational-UAT dimension defect

Real Windows UAT found that the clean packaged master has `Phase` and `Noise Floor`
worksheet dimensions starting at column C after legacy DUT data were removed
(`C26:CE39` and `C26:ADW39`). V14.5 writes SN/Test_Time into columns A/B.

A generated report must therefore expand the worksheet `<dimension>` start column
to A whenever populated data are written into columns A/B. Leaving the dimension at
C while cells A40/B40 and later exist outside that declared range is invalid output
and is treated as an Excel recovery-warning blocker.

The regression test must cover this clean-template condition.
