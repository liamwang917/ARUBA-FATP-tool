# Changelog

This file tracks the ARUBA FATP tool's version history. Filenames no longer embed version numbers; use this file plus git/PR history for version context.

## v13 implementation (2026-09-09)

Implemented the v13.5 direct-ZIP pipeline with shared MIC/PREMIC scanning, Online/Offline discovery, Main Station and detailed curve parsers, optional RawData matching, retest selection, runtime QC, and the locked eight-sheet workbook writer. Added synthetic regression tests, Windows launcher support, and GitHub Actions CI. V12 remains available in `src/build_summary.py` during regression validation.

## v13.5 — RawData input made optional (2026-09-09)

This section records the v13.5 contract decision. Workbook shape remains the v13.4 snapshot-locked contract.

Confirmed decisions:

1. `RawData_RD.zip` is an optional enrichment source, not a required V13 input.
2. At least one FATP package must be supplied:
   - `ARUBA_MIC.zip`
   - `ARUBA_PREMIC.zip`
   - or both.
3. If RawData is not supplied, FATP summary generation continues normally.
4. Runs are not labeled `UNMATCHED` when RawData is absent. Instead:

   ```text
   RawData_Result         = blank
   RawData_Match_Status   = NOT_PROVIDED
   RawData_Time_Delta_s   = blank
   RawData_PF_Mismatch    = blank
   ```

5. `02_FR_original` and `04_FR_1_12` still retain one row per FATP run to preserve row alignment, but RawData-derived frequency cells remain blank.
6. RawData scanner/matcher executes only when `RawData_RD.zip` is supplied.
7. Absence of RawData is a supported operating mode, not a QC error.
8. FATP output workbook generation is independent of RawData presence.
9. Synthetic regression coverage should include a `RawData NOT_PROVIDED` case.

## v13.4 — snapshot-locked workbook contract (2026-09-09)

Documentation/specification revision only. Executable code remains v12.

This revision locks the workbook structure after reviewing an actual MIC Online output snapshot.

Confirmed decisions:

1. Remove the `00_Import_Log` worksheet. QC remains runtime/console/sidecar logging only.
2. Final workbook sheets are:

   ```text
   01_Metadata
   02_FR_original
   03_FR_1_3
   04_FR_1_12
   05_THD
   06_Phase
   07_Noise
   08_SNR
   ```

3. Remove `APx_Section_Result` / `Section_Result` completely. V13 does not parse FR CSV internal `Test Result:` fields.
4. `FR_File_Result` remains filename-derived (`FR_PASS` / `FR_FAIL`) but is displayed only in Metadata and FR-related sheets 02-04.
5. Sheets 05-08 do not display `FR_File_Result`. Their own `Result` comes from Main Station CSV column B for the corresponding item:
   - THD -> `THD` row
   - Phase -> `Phase` row
   - Noise -> `Noise` row
   - SNR -> `SNR` row
   - B=`1` -> PASS
   - B=`0` -> FAIL
   - missing item/flag -> blank
6. `08_SNR` uses Main Station CSV SNR value directly. Missing SNR remains blank; V13 does not calculate a replacement value.
7. Remove built-in `N / Mean / Max / Min / Range / STDEV` blocks. Statistics belong to the downstream Excel report template.
8. Keep Limit evaluation/output deferred to a later dedicated Limit Excel template.
9. `Station` uses the FATP path station folder; `tester_id` is a cross-check. `station_id` is used for Test Type cross-check.
10. `tsr_id` remains an opaque full-text `Run_ID`; `Test_Time` uses `test_start_time`.
11. RawData PASS/FAIL comes from RawData filename `FR_PASS / FR_FAIL` and is compared against `FR_File_Result` for `RawData_PF_Mismatch`.
12. RawData time matching uses the selected FATP FR timestamp as the intended anchor; the 60-second tolerance remains proposed until same-batch FATP/RawData validation is available.
13. MAC remains an internal/device identifier and is not required in the approved public-facing workbook snapshot.
14. No true production XLSX snapshot is committed to this public repository because the reviewed snapshot contains real DUT identifiers and factory metadata.

The next step is implementation against the active v13.5 contract rather than further workbook redesign.

## v13.3 — limit evaluation deferred, result semantics clarified (2026-09-09)

Documentation/specification revision only. Executable code remains v12.

Confirmed and locked for V13 at that stage:

1. Main Station CSV is a six-column format.
2. Main Station contains station-check FR/Sensitivity/THD/Phase/Noise/SNR data.
3. Detailed FR/THD/Phase/Noise workbook data continue to come from detailed FATP/RawData sources.
4. Limit evaluation/output is deferred.
5. `Station_Result` and `Limit_Derived_Result` were removed.
6. `FR_1_3` remains the historical compatibility sheet name.

v13.4 supersedes v13.3 result/output details by removing APx/Section Result parsing and removing the Import Log/statistics sheets/blocks.

## v13.2 — Main Station CSV sample confirmed (2026-09-09)

Documentation/specification revision only.

Confirmed from real MIC data:

- Main Station CSV has six fields per row.
- Main Station includes FR station-check points plus Sensitivity/THD/Phase/Noise/SNR.
- `station_id` can cross-check Test Type.
- `sfis_get_mac` is a MAC address and must remain text if retained.

Later revisions refine the interpretation of the second column and `tsr_id`; use v13.5 as the active contract.

## v13.1 — spec gaps closed (2026-09-09)

Documentation-only revision.

Added:

- recursive CSV classification/discovery;
- RawData matching model;
- retest / `Latest_Run` handling;
- Metadata contract;
- unmatched/ambiguous RawData behavior;
- QC expectations;
- data governance;
- synthetic regression-test expectations.

## v13 — architecture/spec phase

Core V13 direction:

- direct ZIP input;
- MIC/PREMIC shared parser pipeline;
- Online/Offline separated outputs;
- independent optional RawData pool;
- standardized Excel workbook output;
- no Sealing sheet.

## v12 — current executable (`src/build_summary.py`)

Calculation-friendly version based on earlier internal logic.

- Writes frequency/data values as Excel numbers.
- Keeps identifiers/result text as text.
- Fixes the earlier `FR_1_3` frequency issue.
- Still uses the legacy folder-based input/output model.

V13 behavior described above is not yet implemented in executable code.

## v9 and earlier

Earlier internal iterations preceding the snapshot first tracked in this repository (2026-09-07). Not individually preserved here.

