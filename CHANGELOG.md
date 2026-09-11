# Changelog

## v14.0 — report-template analysis / preservation contract (2026-09-11)

Started a new V14 draft line from the validated V13.6 `main` baseline.

This revision is documentation/design only. No V13.6 parser behavior and no user Excel template formatting/formulas/charts are changed.

Locked initial V14 decisions:

- treat the supplied workbook as an immutable report master and populate a copy later;
- preserve all worksheet names/order/visibility, formatting, merges, charts, conditional formatting, print settings, formulas and external-link relationships until explicitly approved otherwise;
- record the exact 11-sheet / 8-chart template structure and SHA-256 manifest without committing the binary workbook to the public repository;
- map V13.6 normalized FR/RawData/THD/Phase/Noise/SNR/Sensitivity outputs to the existing report sheets;
- leave SNR/Sensitivity formula-vs-Main-Station semantics, hidden RawData column-C behavior, Metadata placement, row-capacity behavior, and legacy external-link treatment as explicit open items before implementation.

See `docs/v14_report_template_spec_2026-09-11.md`.

This file tracks the ARUBA FATP tool's version history. Filenames no longer embed version numbers; use this file plus git/PR history for version context.

## v13.6 — real-data feedback revision (2026-09-10)

Implemented after the first real-data execution of the V13.5 baseline. V13.6 now provides the generic archive reader, source-specific timestamps, complete Main Station Metadata capture, simplified RawData sheets, and independent Sensitivity output described below.

Confirmed decisions:

1. Archive input is no longer ZIP-only. V13.6 requires `.zip`, `.7z`, `.tar`, `.tar.gz`, and `.tgz` support through a generic archive-reader abstraction. RAR is not required.
2. `Test_Time` is source-file based, not globally `test_start_time` based:
   - Metadata → Main Station CSV filename
   - FR/THD/Phase → selected FR CSV filename
   - Noise → selected Noise CSV filename
   - RawData sheets → matched RawData CSV filename
   - SNR/Sensitivity → Main Station CSV filename
3. For a 15-digit filename token such as `202609101633182`, `Test_Time` uses the first 14 digits (`20260910163318`). The full token remains an opaque identifier; the final digit is not interpreted as tenths of a second.
4. Main Station `test_start_time` / `test_end_time` parsing must support real production fractional-second formats.
5. `02_FR_original` and `04_FR_1_12` are simplified to:

   ```text
   SN
   Test_Time
   RawData_Match_Status
   <frequency data...>
   ```

   These sheets no longer display `Path_Result`, `FR_File_Result`, `RawData_Result`, or `RawData_PF_Mismatch`.
6. `RawData_Result` / mismatch information may remain internal or in Metadata for traceability, but not on sheets 02/04.
7. `Sensitivity_dBFS` is removed from `08_SNR`.
8. New sheet `09_Sensitivity` is added with the same Main Station item-result pattern as SNR:

   ```text
   SN
   Test_Time
   Path_Result
   Result
   Sensitivity_dBFS
   Sensitivity_Source_Status
   ```

9. `08_SNR` becomes:

   ```text
   SN
   Test_Time
   Path_Result
   Result
   SNR_dB
   SNR_Source_Status
   ```

10. `01_Metadata` must capture the complete Main Station Column-A → Column-C key/value set, not only a fixed whitelist. Header keys are the union of all Main Station item keys across runs; missing run values are blank.
11. Existing result/limit rules remain unchanged: no APx Section Result parsing, no Import Log worksheet, no built-in statistics, no limit evaluation, no dashboard, RawData remains optional with `NOT_PROVIDED` behavior.
12. V13.6 regression tests must cover real-format timestamps, source-specific `Test_Time`, 7Z/TAR input, complete Metadata A→C capture, 02/04 exact columns, `09_Sensitivity`, and the nine-sheet contract.

## v13 implementation (2026-09-09)

Implemented the v13.5 direct-ZIP pipeline with shared MIC/PREMIC scanning, Online/Offline discovery, Main Station and detailed curve parsers, optional RawData matching, retest selection, runtime QC, and the then-locked eight-sheet workbook writer. Added synthetic regression tests, Windows launcher support, and GitHub Actions CI. V12 remains available in `src/build_summary.py` during regression validation.

The real-data execution on 2026-09-10 produced the v13.6 feedback above; the v13.5 implementation is therefore a baseline, not the final V13.6 implementation.

## v13.5 — RawData input made optional (2026-09-09)

Confirmed decisions:

1. `RawData_RD` is an optional enrichment source, not a required V13 input.
2. At least one FATP package must be supplied: MIC, PREMIC, or both.
3. If RawData is not supplied, FATP summary generation continues normally.
4. Runs are not labeled `UNMATCHED` when RawData is absent; use `NOT_PROVIDED`.
5. RawData-derived frequency values remain blank when RawData is absent.
6. Absence of RawData is a supported operating mode, not a QC error.

## v13.4 — snapshot-locked workbook contract (2026-09-09)

Confirmed at that stage:

- no `00_Import_Log` worksheet;
- no APx/Section Result parsing;
- no built-in N/Mean/Max/Min/Range/STDEV blocks;
- THD/Phase/Noise/SNR item Result from Main Station Column B;
- limit evaluation deferred;
- detailed FR/THD/Phase/Noise sources retained.

V13.6 supersedes the v13.4/v13.5 workbook details by adding `09_Sensitivity`, simplifying 02/04, changing Test_Time semantics, and expanding Metadata capture.

## v13.3 — limit evaluation deferred, result semantics clarified (2026-09-09)

Main Station station-check data were kept separate from detailed sources and limit evaluation/output was deferred.

## v13.2 — Main Station CSV sample confirmed (2026-09-09)

Confirmed six-column Main Station format, station/tester identifiers, device metadata, and station-check measurement items.

Later revisions supersede the earlier timestamp/result interpretations.

## v13.1 — spec gaps closed (2026-09-09)

Added recursive discovery, RawData matching model, retest handling, Metadata contract, QC expectations, data governance, and synthetic regression-test expectations.

## v13 — architecture/spec phase

Core V13 direction:

- direct compressed-package input;
- MIC/PREMIC shared parser pipeline;
- Online/Offline separated outputs;
- independent optional RawData pool;
- standardized Excel workbook output;
- no Sealing sheet.

## v12 — retained regression executable (`src/build_summary.py`)

Legacy folder-based calculation-friendly version retained for comparison until V13.6 validation is complete.

## v9 and earlier

Earlier internal iterations preceding the snapshot first tracked in this repository (2026-09-07). Not individually preserved here.

