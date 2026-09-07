# Data snapshots

## 2026-09-07 current-progress package

Local source package reviewed in ChatGPT:

- File: `ARUBA_FATP_current_progress_2026-09-07.zip`
- SHA-256: `da5ec5114aa72066b6b35d1936c1c0b9f5fe80757938ff753da47ee96f1727aa`
- ZIP compressed size: 34,085,179 bytes
- Uncompressed payload: 49,061,446 bytes
- Files: 369

Payload composition:

| Type | Count | Uncompressed bytes |
| --- | ---: | ---: |
| WAV | 146 | 46,214,576 |
| CSV | 219 | 2,398,502 |
| XLSX | 1 | 434,960 |
| PY | 1 | 12,344 |
| TXT | 1 | 872 |
| BAT | 1 | 192 |

## Numerical CSV snapshot

A local exact ZIP containing all 219 CSV records was also generated during review:

- File: `raw_csv_snapshot_2026-08-26.zip`
- SHA-256: `2453bf0352f78cfe58b0684b2f5138e812f90671f0a1e7d189100450b3a06298`
- Compressed size: 471 KB
- Uncompressed CSV bytes: 2,398,502

## Existing workbook

- Original generated workbook: `raw data/summary.xlsx`
- SHA-256: `bf7121a723d57b2abae4e0c00758ae430d1aac7719bba19c66dbc662fc3abd86`
- Size: 434,960 bytes

Review copy generated during validation:

- `summary_review_test.xlsx`
- SHA-256: `543e7b66722947584a169a237307a1ed7ca3a816c11f59df3a5215343a2d5130`
- Size: 434,974 bytes

## Connector limitation

The ChatGPT GitHub connector available in this session can create/update UTF-8 repository files and Git objects, but its write actions do not accept a mounted local file path as a binary upload argument. For that reason the 146 WAV files, XLSX binaries, and local ZIP snapshot are **not represented as uploaded bytes in this branch**.

Their hashes/counts above are recorded so the exact local package can be verified when uploaded using Git/GitHub Desktop/Codex or another GitHub interface that accepts local binary files.

## Public-repository warning

The dataset contains DUT serial identifiers and FATP/factory test metadata. Confirm disclosure approval before copying the raw dataset into a public repository or merging it to `main`.
