# ARUBA-FATP-tool

ARUBA FATP 麥克風 / PREMIC 產測資料整理與分析工具。

## 目前狀態

- `v12`：目前可執行版本，位於 `src/build_summary.py`
- `v13`：架構與資料規格已收斂（現為 v13.1），尚未完成程式實作
- 最新 V13 規格：`docs/v13_spec_2026-09-08.md`（revision v13.1，2026-09-09）
- `docs/review_2026-09-07.md` 為 V13 之前的 review，已標示為 historical；其 workbook layout 已被規格取代
- 最新資料快照與 SHA-256：`data/snapshots/README.md`

## v12 已驗證內容

2026-08-26 MIC FATP 資料集：

- DUT 資料夾：73
- Unique SN：73
- CSV：219
- WAV：146
- FR / THD / Phase：各 73 × 80 frequency points
- Noise：73 × 800 frequency points
- 73 台 DUT frequency axis 已確認一致

目前 v12 的 FR / THD / Phase `Result` 仍由 FR filename 的 `PASS/FAIL` 推導；APx CSV section 內的 `Test Result:` 可能與 filename result 不同。V13 將兩者分開保存。

## V13 目標架構

V13 改為直接讀 ZIP，不要求使用者先解壓縮，也不再假設 `Online` 下一層就是 DUT folder。

### 輸入來源

```text
ARUBA_MIC.zip
ARUBA_PREMIC.zip
RawData_RD.zip
```

MIC 與 PREMIC 的 FATP 路徑與 CSV 結構相同，只是最上層 Test Type 名稱不同，因此共用同一套 scanner/parser/report builder。

```text
ARUBA_MIC.zip
└─ .../Online|Offline/.../PASS|FAIL/.../*.csv

ARUBA_PREMIC.zip
└─ .../Online|Offline/.../PASS|FAIL/.../*.csv

RawData_RD.zip
└─ RawData_RD
   ├─ MIC/**/*.csv
   └─ PREMIC/**/*.csv
```

### RawData mapping

RawData 不預設屬於 Online 或 Offline，而是先依 Test Type 分池，再用 SN + PASS/FAIL + timestamp proximity 配對回 FATP test run。

| RawData CSV section | Summary sheet |
| --- | --- |
| `FR_Original` | `FR_original` |
| `FR_1/12smooth` | `FR_1_12` |
| `FR_1/3smooth` | 不使用 |

### 標準 Summary sheets

MIC / PREMIC、Online / Offline 四種報告共用相同 sheet template：

```text
00_Import_Log
01_Metadata
02_FR_original
03_FR_1_3
04_FR_1_12
05_THD
06_Phase
07_Noise
08_SNR
```

`Sealing` 已從 V13 規格移除。

### 預計輸出

```text
summary_MIC_Online.xlsx
summary_MIC_Offline.xlsx
summary_PREMIC_Online.xlsx
summary_PREMIC_Offline.xlsx
```

若此次沒有提供某個 Test Type 的 ZIP，則不產生該 Test Type 的報告。

## V13 資料來源對照

| Summary sheet | FATP / RawData source |
| --- | --- |
| `FR_original` | RawData_RD → `FR_Original` |
| `FR_1_3` | FATP FR CSV → `FR` |
| `FR_1_12` | RawData_RD → `FR_1/12smooth` |
| `THD` | FATP FR CSV → `THD` |
| `Phase` | FATP FR CSV → `Phase` |
| `Noise` | FATP Noise CSV |
| `SNR` | FATP Main Station CSV → `SNR` |

## RawData matching 原則

RawData CSV 本身不一定帶有 Online / Offline 標記，因此 V13 不直接靠 RawData path 猜測 Mode。

匹配優先順序：

1. Test Type 必須一致：MIC 只配 MIC，PREMIC 只配 PREMIC。
2. SN 必須一致。
3. PASS / FAIL 作為輔助條件。
4. 比較 FATP FR timestamp，取時間差最近的 run。
5. 必須符合可設定的 maximum time tolerance。
6. 無可靠候選時標記 `UNMATCHED`。
7. Online / Offline 候選同樣合理時標記 `AMBIGUOUS`，不可自動猜測。

具體可調參數（time tolerance、ambiguous margin、PASS/FAIL soft 或 strict、SN 正規化）定義於規格第 11.1 節，集中在 `config.py`。

同一 SN 的歷史 retest 全部保留；另外標示 `Latest_Run`，不直接刪除舊 run。`Latest_Run` 以 `(Test_Type, Mode, SN)` 為分組鍵，依 `Test_Time` 排序，規格第 10.1 節。

同一個 test run 若存在多份同類 CSV，V13 預設選 timestamp 最新的一份，並把被忽略的候選寫入 `00_Import_Log`。

`UNMATCHED` / `AMBIGUOUS` 的 run 仍會在 `02_FR_original`、`04_FR_1_12` 保留一列，但 frequency 資料格留空白（不寫 0、不猜最近候選），以維持各 sheet 列數對齊。規格第 17 節。

## Import / QC 要求

V13 的 Import Log 至少要記錄：

- Total runs / Unique SN
- PASS / FAIL counts
- Main / FR / Noise CSV found counts
- Missing / duplicate / malformed CSV
- Unclassified CSV
- Multiple same-type CSV selection
- Frequency-axis mismatch
- Missing / invalid SNR（`NaN`, empty 等不可當成 0）
- RawData matched / unmatched / ambiguous counts
- Empty RawData sections

## v13.1 新增定義

v13.1 不改動 v13.0 的核心架構，只把原本未收斂的細節補齊：

- CSV 分類規則（內容特徵優先、檔名為 fallback、無法判定則標 `UNCLASSIFIED`）—— 第 4.1 節
- matcher 可調參數與預設值、RawData 單一消費規則 —— 第 11.1 / 11.2 節
- `Latest_Run` 分組鍵與排序定義 —— 第 10.1 節
- `01_Metadata` 欄位契約（含 operator / tester / SW version / sensitivity 等）—— 第 16 節
- `UNMATCHED` / `AMBIGUOUS` 的下游寫入行為與列對齊規則 —— 第 17 節
- 統計區塊、時間型別、凍結窗格 / AutoFilter / 條件格式 —— 第 18 節
- 公開 repo 的資料治理原則 —— 第 19 節
- 尚需用實際資料確認的項目（標 `PROPOSED`）—— 第 21 節

## Repository layout

```text
src/                 現有 v12 程式碼
tools/               Windows launcher
docs/                使用說明、review、V13 specification
data/
  snapshots/         資料包版本、大小與 SHA-256
  manifests/         aggregate manifest / inventory
  outputs/           可公開保存的輸出結果
CHANGELOG.md          版本歷史與 V13 開發狀態
requirements.txt     Python dependencies
```

## 執行 v12

```bash
py -3 -m pip install -r requirements.txt
python src/build_summary.py <原始資料夾路徑>
```

Windows：

```text
tools\run_build_summary.bat
```

> v12 仍使用舊資料夾式 input；ZIP / MIC+PREMIC / Online+Offline / RawData matching / SNR sheet 是 V13 目標，不應誤認為已在 v12 實作。

## Public repository 注意事項

此 repository 目前為 public。原始 FATP / RawData 可能包含 DUT SN、station、operator、SW version 與其他 factory metadata。提交 raw CSV / WAV / ZIP 前請確認這些資料允許公開揭露。完整治理原則見規格第 19 節。
