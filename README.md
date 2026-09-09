# ARUBA-FATP-tool

ARUBA FATP 麥克風 / PREMIC 產測資料整理與分析工具。

## 目前狀態

- `v12`：目前可執行版本，位於 `src/build_summary.py`
- `v13`：架構與資料規格已收斂（現為 v13.3），尚未完成程式實作
- 最新 V13 規格：`docs/v13_spec_2026-09-08.md`（revision v13.3，2026-09-09）
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

目前 v12 的 FR / THD / Phase `Result` 仍由 FR filename 的 `PASS/FAIL` 推導；APx CSV section 內的 `Test Result:` 可能與 filename result 不同。V13 將不同來源的 result 分開保存。

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

### Main Station CSV 已確認資訊

實際 sample 已確認 Main Station CSV：

- 每列固定 6 欄：`item_key,index,value,low_limit,high_limit,error_code`
- `tsr_id` 為 15 位時間碼，例如 `202607061915366` = 2026-07-06 19:15:36.6
- `station_id=ARUBA_MIC`，可與 path 推出的 Test Type 交叉驗證
- `tester_id` 可與 FATP path 的 station/tester folder 交叉驗證
- `sfis_get_mac` 為 MAC address，必須當文字保存
- Main Station CSV 另外包含 21-point FR、Sensitivity、THD、Phase、Noise、SNR scalar/check values

同一個 sample 的 21-point FR、1 kHz THD/Phase/Noise 與詳細 FR/Noise CSV 對應值一致，因此 V13 把 Main Station 這些值定位成 station-check/scalar data，不拿它們取代詳細曲線來源。

### Limit scope

Main Station CSV 第 4/5 欄雖然是 Low/High limit，但 **V13 暫不做 Limit 判定與輸出**：

- 不建立 Station Limit sheet
- 不建立 `Limit_Derived_Result`
- 不用 limit 推導 PASS/FAIL
- 不把 limit 當作 Import Log 的工程 limit table
- 後續由專用 Limit Excel 模板另行整合

V13 只需辨識這兩欄的位置，保留未來擴充能力。

### Result 欄位

V13 不使用來源模糊的單一 `Station_Result`，改為保留明確來源：

- `Path_Result`：來自 FATP path 的 `PASS` / `FAIL` folder
- `FR_File_Result`：來自選定 FR filename 的 `FR_PASS` / `FR_FAIL`
- `APx_Section_Result`：來自 FR CSV section 內的 `Test Result:`

不同 result 來源若不一致，只記錄 QC，不自動覆蓋其中任何一個。

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
| `FR_1_3` | FATP FR CSV → detailed `FR` |
| `FR_1_12` | RawData_RD → `FR_1/12smooth` |
| `THD` | FATP FR CSV → detailed `THD` |
| `Phase` | FATP FR CSV → detailed `Phase` |
| `Noise` | FATP Noise CSV → detailed spectrum |
| `SNR` | FATP Main Station CSV → `SNR` |

`FR_1_3` 名稱在 V13 先保留相容性；目前實際來源仍是 FATP FR CSV 的 80-point detailed FR section。

## RawData matching 原則

RawData CSV 本身不一定帶有 Online / Offline 標記，因此 V13 不直接靠 RawData path 猜測 Mode。

匹配優先順序：

1. Test Type 必須一致：MIC 只配 MIC，PREMIC 只配 PREMIC。
2. SN 必須一致。
3. PASS / FAIL 作為輔助條件。
4. 比較 FATP timestamp，取時間差最近的 run。
5. 必須符合可設定的 maximum time tolerance。
6. 無可靠候選時標記 `UNMATCHED`。
7. Online / Offline 候選同樣合理時標記 `AMBIGUOUS`，不可自動猜測。

具體可調參數定義於規格第 11.1 節，集中在 `config.py`。

同一 SN 的歷史 retest 全部保留；另外標示 `Latest_Run`，不直接刪除舊 run。`Latest_Run` 以 `(Test_Type, Mode, SN)` 為分組鍵，依 `Test_Time` 排序。

同一個 test run 若存在多份同類 CSV，V13 預設選 timestamp 最新的一份，並把被忽略的候選寫入 `00_Import_Log`。

`UNMATCHED` / `AMBIGUOUS` 的 run 仍會在 `02_FR_original`、`04_FR_1_12` 保留一列，但 frequency 資料格留空白（不寫 0、不猜最近候選），以維持各 sheet 列數對齊。

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
- `station_id` vs path Test Type conflict
- `tester_id` vs path station/tester-folder conflict
- `Path_Result` / `FR_File_Result` / `APx_Section_Result` disagreement
- RawData matched / unmatched / ambiguous counts
- RawData PASS/FAIL mismatch
- Empty RawData sections

Limit values 不在 V13 QC / report scope 內。

## v13.3 收斂內容

v13.3 將 Main Station CSV 實際 sample 驗證結果與 Limit scope 正式鎖定：

- Main Station CSV 6 欄格式、15-digit `tsr_id`、`station_id`、`tester_id`、`sfis_get_mac` 已寫入規格
- Main Station 21-point FR / scalar THD / Phase / Noise 不取代 detailed FR/Noise CSV
- `FR_1_3` / `THD` / `Phase` / `Noise` 繼續使用 detailed source
- Main Station station-check values 保留於 parser/internal model，供後續 template integration 使用
- Limit evaluation/output 延後，不做 `Limit_Derived_Result`
- `Station_Result` 取消，改用明確來源的 `Path_Result` / `FR_File_Result` / `APx_Section_Result`
- 不新增 `Station_Check` / `Station_Limits` sheet

完整規則請見 `docs/v13_spec_2026-09-08.md`。

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

此 repository 目前為 public。原始 FATP / RawData 可能包含 DUT SN、MAC address、station、operator、tester、SW version 與其他 factory metadata。提交 raw CSV / WAV / ZIP 或生成 workbook 前請確認這些資料允許公開揭露。完整治理原則見規格第 19 節。
