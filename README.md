# ARUBA-FATP-tool

ARUBA FATP 麥克風產測資料整理與分析工具。

## 目前快照(Current snapshot)

- 快照日期:2026-09-07
- 來源資料集:2026-08-26 ARUBA MIC FATP 產測批次
- DUT 資料夾數:73
- 唯一序號(SN)數:73
- 原始 CSV 檔案數:219
- WAV 檔案數:146
- 既有 Excel 摘要檔:1 份
- 目前解析工具版本:v12(`src/build_summary.py`;詳見 `CHANGELOG.md`)

### 解析輸出涵蓋範圍

| 分頁 | 目前資料 |
| --- | ---: |
| FR_original | 0 筆(RawData_RD 目前為空) |
| FR_1_3 | 73 台 DUT × 80 個頻率點 |
| FR_1_12 | 0 筆(RawData_RD 目前為空) |
| THD | 73 台 DUT × 80 個頻率點 |
| Phase | 73 台 DUT × 80 個頻率點 |
| Noise | 73 台 DUT × 800 個頻率點 |
| Sealing | 0 筆(此資料集沒有 Sealing CSV) |

目前資料集中所有 73 台 DUT 的頻率軸都經過檢查,結果一致。

## 專案結構(Repository layout)

```text
src/
  build_summary.py         目前的解析器 / Excel 摘要產生器(v12 邏輯)
tools/
  run_build_summary.bat    Windows 執行捷徑
docs/
  usage.md                 使用說明
  review_2026-09-07.md     工程 review 報告 + V13 待辦清單(帶日期的歷史紀錄)
data/
  snapshots/               資料集組成、數量與 SHA-256 完整性紀錄
  manifests/               各資料集的清單 / 完整性紀錄(佔位用,尚未填入內容)
  outputs/                 若有收錄,存放產生的分析結果(佔位用,尚未填入內容)
CHANGELOG.md               版本歷史(v9 → v12)與 V13 待辦清單
requirements.txt           Python 相依套件
```

## 執行方式(Run)

完整使用說明請見 `docs/usage.md`。快速開始:

```bash
py -3 -m pip install -r requirements.txt
python src/build_summary.py <原始資料夾路徑>
```

Windows:

```text
tools\run_build_summary.bat
```

所選的原始資料夾必須包含:

```text
Online/
RawData_RD/
```

輸出結果會寫成 `summary.xlsx`,存放在所選的原始資料夾內。

## Review 中發現的重要結果判定問題

目前 73 個 FR 檔案的檔名都包含 `FR_PASS`,但檔案內部 FR 段落的 `Test Result:` 卻是 73 筆全部為 `Fail`。THD 和 Phase 段落內部的結果則是 `Pass`。

目前 v12 的實作是用 FR 檔名來判定 FR/THD/Phase 的 `Result` 欄位,所以就算內部 APx FR 段落回報 `Fail`,Excel 裡仍可能顯示 `PASS`。

如果檔名 PASS 代表的是產線站別(FATP station)的最終判定,而 APx 段落結果是另一套規格的判定,那這個現象可能是刻意設計。在確認站別判定邏輯之前,**不要**把這兩種意義混為一談。建議的 V13 設計是拆成兩欄:

- `Station Result`(站別結果)
- `APx Section Result`(APx 段落結果)

完整 review 請見 `docs/review_2026-09-07.md`,完整的 V13 待辦清單請見 `CHANGELOG.md`。

## 資料說明

原始資料包內含約 46.2 MB 的 WAV 錄音二進位檔案。這些二進位檔案**沒有存放在這個 repository 裡**——只有它們的數量、大小與 SHA-256 雜湊值記錄在 `data/snapshots/README.md`,用來驗證本機資料包是否一致。這裡沒有這些檔案,不代表本機的原始資料集已被刪除。

## 資料公開揭露說明

這個 repository 是公開的。截至 2026-09-08,目前收錄的檔案只記錄了整體數量、檔案大小總計與 SHA-256 雜湊值——沒有任何個別 DUT 序號或原始產測數值被寫進這個 repository。基於這點,已確認可以維持公開;未來若要提交原始 CSV/WAV 資料或個別序號,請重新檢視這則說明。
