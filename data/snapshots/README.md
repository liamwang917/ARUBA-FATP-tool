# Data snapshots

此目錄記錄已用於設計、驗證與 review 的本機資料包版本、大小、檔案數與 SHA-256。

> Repository 目前為 public。原始 CSV/WAV/ZIP 可能包含 DUT SN 與 FATP/factory metadata，因此目前只提交 aggregate inventory / hash，不直接把敏感 raw bytes 推入 public repository。

## 2026-09-08 — V13 architecture inputs

### ARUBA_MIC.zip

- Purpose: V13 MIC FATP path / Online-Offline / retest / duplicate-file architecture validation
- ZIP size: `328,061,370` bytes
- SHA-256: `10b79be3b21d10635026a54f15b17665d078a17dc79a7331d8659507ffaba8b6`
- ZIP file entries: `3,580`
- Uncompressed payload: `474,525,194` bytes
- CSV: `2,148`
- WAV: `1,432`

Observed characteristics used by the V13 design:

- Online and Offline are nested below additional month/date/station/result/run folders, so V13 must use recursive path discovery rather than a fixed depth.
- Same SN may have multiple historical test runs; V13 must preserve all runs and mark `Latest_Run` instead of globally deduplicating by SN.
- Some runs can contain multiple same-type FR CSV files; V13 selects the latest timestamped candidate within that run and logs the alternatives.
- MIC and PREMIC are expected to use the same FATP structure; only Test Type differs.

### RawData_RD.zip

- Purpose: V13 FR original / 1-12 smooth mapping and MIC/PREMIC RawData-pool design
- ZIP size: `3,396,862` bytes
- SHA-256: `72385ff92756effe8fe36bb6775e5ab1283e85b713117b8915ce415edb571ead`
- ZIP non-directory entries: `1,689`
- Uncompressed payload: `19,586,132` bytes
- CSV: `1,683`
- macOS metadata / non-CSV entries: `6`

Validated mapping:

| RawData subtree / section | V13 use |
| --- | --- |
| `RawData_RD/MIC/**/*.csv` | MIC RawData pool |
| `RawData_RD/PREMIC/**/*.csv` | PREMIC RawData pool |
| `FR_Original` | summary `FR_original` |
| `FR_1/12smooth` | summary `FR_1_12` |
| `FR_1/3smooth` | intentionally not used |

RawData does not itself provide a reliable Online/Offline assignment. V13 therefore matches RawData to FATP TestRun records using Test Type + SN + supporting PASS/FAIL + nearest timestamp within a configurable tolerance. Unsafe matches remain `UNMATCHED` or `AMBIGUOUS`.

### ARUBA_PREMIC.zip

Not yet supplied in the current ChatGPT session. The V13 contract assumes its FATP path/data structure is identical to MIC except for the top-level Test Type naming, per project requirement. When a real PREMIC ZIP is supplied, use it for regression validation without creating a separate parser unless the format actually diverges.

## 2026-09-07 — original current-progress package

Local source package reviewed in ChatGPT:

- File: `ARUBA_FATP_current_progress_2026-09-07.zip`
- SHA-256: `da5ec5114aa72066b6b35d1936c1c0b9f5fe80757938ff753da47ee96f1727aa`
- ZIP compressed size: `34,085,179` bytes
- Uncompressed payload: `49,061,446` bytes
- Files: `369`

Payload composition:

| Type | Count | Uncompressed bytes |
| --- | ---: | ---: |
| WAV | 146 | 46,214,576 |
| CSV | 219 | 2,398,502 |
| XLSX | 1 | 434,960 |
| PY | 1 | 12,344 |
| TXT | 1 | 872 |
| BAT | 1 | 192 |

### Numerical CSV snapshot

A local exact ZIP containing all 219 CSV records was generated during review:

- File: `raw_csv_snapshot_2026-08-26.zip`
- SHA-256: `2453bf0352f78cfe58b0684b2f5138e812f90671f0a1e7d189100450b3a06298`
- Compressed size: `481,437` bytes
- Uncompressed CSV bytes: `2,398,502`

### Existing workbook

Review copy generated during validation:

- `summary_review_test.xlsx`
- SHA-256: `543e7b66722947584a169a237307a1ed7ca3a816c11f59df3a5215343a2d5130`
- Size: `434,974` bytes

## Raw-data publication policy for this repository

Because this repository is public, do not commit individual raw FATP CSV/WAV/ZIP bytes unless disclosure is explicitly approved. Aggregate hashes, counts, sizes, synthetic fixtures and redacted samples are preferred for public development and regression testing.
