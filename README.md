# ARUBA-FATP-tool

ARUBA FATP MIC / PREMIC 產測資料整理與 Excel Summary 工具。

## 目前狀態

- `v12`：目前可執行版本，位於 `src/build_summary.py`
- `v13`：規格已收斂到 **v13.4 snapshot-locked**，尚未開始程式實作
- V13 規格：`docs/v13_spec_2026-09-08.md`
- `docs/review_2026-09-07.md` 為 historical review，舊 workbook layout 已 superseded

## V13 輸入

```text
ARUBA_MIC.zip
ARUBA_PREMIC.zip
RawData_RD.zip
```

MIC / PREMIC 共用同一套 scanner/parser/report pipeline；Online / Offline 分開產出報告。

預計輸出：

```text
summary_MIC_Online.xlsx
summary_MIC_Offline.xlsx
summary_PREMIC_Online.xlsx
summary_PREMIC_Offline.xlsx
```

## V13 最終 workbook 契約

經實際 MIC Online 快照確認後，V13 workbook 不再有 `00_Import_Log` sheet。

標準分頁：

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

`Sealing` 已移除。

V13 不會在 summary 裡自行建立：

- Import Log worksheet
- N / Mean / Max / Min / Range / STDEV 統計區塊
- Dashboard / chart
- Station Limit sheet
- `Limit_Derived_Result`
- APx / Section Result

這些分析與 limit/report template 功能留給後續 Excel 報告模板處理。

## 資料來源

| Sheet | Source |
| --- | --- |
| `02_FR_original` | RawData `FR_Original` |
| `03_FR_1_3` | FATP FR CSV detailed `FR` |
| `04_FR_1_12` | RawData `FR_1/12smooth` |
| `05_THD` | FATP FR CSV detailed `THD` |
| `06_Phase` | FATP FR CSV detailed `Phase` |
| `07_Noise` | FATP Noise CSV detailed spectrum |
| `08_SNR` | Main Station CSV `SNR` scalar |

RawData `FR_1/3smooth` 不使用。

`FR_1_3` 為歷史相容名稱；目前實際內容仍是 FATP FR CSV 的 80-point detailed FR section。

## Result 規則

### Path_Result

來源：FATP ZIP path 的 `PASS` / `FAIL` folder。

### FR_File_Result

來源：選定 FR CSV filename：

```text
*_FR_PASS_*.csv -> PASS
*_FR_FAIL_*.csv -> FAIL
```

只保留在：

```text
01_Metadata
02_FR_original
03_FR_1_3
04_FR_1_12
```

### 05~08 的 Result

`05_THD`、`06_Phase`、`07_Noise`、`08_SNR` 不顯示 `FR_File_Result`。

各頁自己的 `Result` 直接讀 Main Station CSV 對應 item 的 **B 欄**：

```text
1 -> PASS
0 -> FAIL
沒有該 item / flag -> blank
```

對應項目：

```text
05_THD   -> THD row
06_Phase -> Phase row
07_Noise -> Noise row
08_SNR   -> SNR row
```

V13 不解析 FR CSV 內部 `Test Result:`，也不建立 `Section_Result` / `APx_Section_Result`。

## Main Station CSV

確認格式：

```text
<item_key>,<result_flag>,<value>,<low_limit>,<high_limit>,<error_code>
```

主要 metadata：

- `uut_sn`
- `tsr_id`
- `op_id`
- `station_id`
- `tester_id`
- `test_sw_ver`
- `test_start_time`
- `sfis_get_mac`
- `test_end_time`
- `total_test_time`

主要 measurement item：

- FR100 ... FR7500
- Sensitivity
- THD
- Phase
- Noise
- SNR

`Station` 取 FATP path 的 station folder，例如 `ARUBA-MIC-01`；`tester_id` 用來 cross-check。

`station_id=ARUBA_MIC / ARUBA_PREMIC` 用來與 path Test Type cross-check。

`tsr_id` 在 V13 當完整 opaque `Run_ID` 保存；`Test_Time` 使用 `test_start_time`。

## RawData matching

RawData 先依 MIC / PREMIC 分池，再匹配 FATP run。

匹配原則：

1. Test Type 一致
2. SN exact match（正規化後）
3. RawData filename 的 `FR_PASS/FR_FAIL` 作輔助條件
4. 以 selected FATP FR timestamp 做時間 proximity matching
5. 超過 tolerance 不配
6. 無安全候選 -> `UNMATCHED`
7. 多個同樣合理候選 -> `AMBIGUOUS`

`RawData_Result` 來源也是 filename `FR_PASS / FR_FAIL`。

`RawData_PF_Mismatch` 比較：

```text
RawData_Result vs FR_File_Result
```

不拿 RawData Result 跟 Path_Result 比。

目前 60 秒 matching tolerance 仍屬 **PROPOSED**，需要同批 FATP + RawData 再驗證。

## SNR

`08_SNR` 直接使用 Main Station CSV `SNR` item：

- B 欄 1/0 -> PASS/FAIL
- C 欄 -> SNR value
- 沒有 SNR row -> Result/value 留空

不自行計算替代 SNR。

## Limit

Main Station CSV D/E 欄是 Low/High limit，但 **V13 暫不處理**：

- 不輸出 limit
- 不用 limit 判定 PASS/FAIL
- 不建立 limit sheet

後續會套用專用 Limit Excel 模板。

## QC

雖然 workbook 不再有 Import Log sheet，程式仍應保留 runtime QC / console log，例如：

- missing Main / FR / Noise CSV
- duplicate FR CSV
- path Test Type vs `station_id` mismatch
- path Station vs `tester_id` mismatch
- Path_Result vs FR_File_Result mismatch
- RawData MATCHED / UNMATCHED / AMBIGUOUS
- invalid/missing THD / Phase / Noise / SNR result flag
- frequency-axis mismatch

QC 不新增 summary workbook 分頁。

## Retest

保留所有歷史 run，增加 `Latest_Run`。

分組：

```text
(Test_Type, Mode, SN)
```

排序：

1. `Test_Time = test_start_time`
2. `Run_ID` text tie-break

## Repository layout

```text
src/                 現有 v12 程式碼；V13 implementation 尚未開始
tools/               Windows launcher
docs/                使用說明 / historical review / V13 spec
data/
  snapshots/         package metadata / SHA-256
  manifests/         aggregate manifest
  outputs/           僅放可公開的輸出
CHANGELOG.md          版本歷史
requirements.txt     Python dependency
```

## 執行 v12

```bash
py -3 -m pip install -r requirements.txt
python src/build_summary.py <原始資料夾路徑>
```

> V12 仍是舊 folder-based tool。ZIP input、MIC/PREMIC shared pipeline、Online/Offline split、RawData matching、item-level 05~08 Result 等是 V13 implementation contract，目前尚未寫進 executable code。

## Public repository 注意事項

此 repository 是 public。Raw FATP / RawData 可能包含 SN、MAC、operator、station、tester 等 factory metadata，因此原始 CSV / WAV / ZIP 與真實 production workbook 不應直接提交，除非已確認可公開揭露。