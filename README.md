# ARUBA-FATP-tool

ARUBA FATP MIC / PREMIC 產測資料整理與 Excel Summary 工具。

## 目前狀態

- `v12`：保留於 `src/build_summary.py`，供 regression comparison
- `v13.5 implementation`：已可執行，但經真實資料測試後發現輸出/時間/壓縮格式需修正
- `v13.6`：**目前 active specification**，等待 Codex 依 `docs/v13_spec_2026-09-08.md` 更新 implementation
- V13 規格：`docs/v13_spec_2026-09-08.md`

## V13.6 輸入

FATP package 至少一種：

```text
ARUBA_MIC.<archive>
ARUBA_PREMIC.<archive>
```

RawData：

```text
RawData_RD.<archive>    OPTIONAL
```

V13.6 的 archive selector 不可只支援 ZIP。

要求支援：

```text
.zip
.7z
.tar
.tar.gz
.tgz
```

RawData 沒有提供時，FATP summary 仍正常產生，並使用：

```text
RawData_Match_Status = NOT_PROVIDED
```

不是 `UNMATCHED`，也不是 error。

## 輸出

依實際發現的 Test Type / Mode 產生：

```text
summary_MIC_Online.xlsx
summary_MIC_Offline.xlsx
summary_PREMIC_Online.xlsx
summary_PREMIC_Offline.xlsx
```

## V13.6 workbook contract

每份 workbook 固定：

```text
01_Metadata
02_FR_original
03_FR_1_3
04_FR_1_12
05_THD
06_Phase
07_Noise
08_SNR
09_Sensitivity
```

不產生：

- `00_Import_Log`
- N / Mean / Max / Min / Range / STDEV
- Dashboard / chart
- Station Limit sheet
- `Limit_Derived_Result`
- APx / Section Result
- Sealing

## Test_Time — V13.6

`Test_Time` 跟著該 sheet **實際資料來源 CSV filename 的時間**，不再全部使用 `test_start_time`。

| Sheet | Test_Time source |
| --- | --- |
| `01_Metadata` | Main Station CSV filename |
| `02_FR_original` | matched RawData CSV filename |
| `03_FR_1_3` | selected FR CSV filename |
| `04_FR_1_12` | matched RawData CSV filename |
| `05_THD` | selected FR CSV filename |
| `06_Phase` | selected FR CSV filename |
| `07_Noise` | selected Noise CSV filename |
| `08_SNR` | Main Station CSV filename |
| `09_Sensitivity` | Main Station CSV filename |

例如：

```text
SR1M08GD263600063_202609101633182.csv
```

`Test_Time` 使用前 14 碼：

```text
20260910163318 -> 2026-09-10 16:33:18
```

完整 15 碼仍可作為原始 identifier 保存；不假設最後一碼是 0.1 秒。

## Main Station CSV

格式：

```text
<item_key>,<result_flag>,<value>,<low_limit>,<high_limit>,<error_code>
```

- A欄：item key
- B欄：item result flag（適用 measurement item）
  - `1` → PASS
  - `0` → FAIL
  - missing/invalid → blank
- C欄：value
- D/E：Limit，V13 不使用
- F：step/error code，summary 不需要

### Metadata 完整擷取

V13.6 不再只抓少數白名單欄位。

`01_Metadata` 要把 Main Station CSV **所有 A欄 item_key 與對應 C欄 value** 都保留下來，例如：

```text
uut_sn
tsr_id
op_id
station_id
tester_id
test_sw_ver
test_start_time
sfis_get_mac
FR100 ... FR7500
Sensitivity
THD
Phase
Noise
SNR
test_end_time
total_test_time
```

如果不同 run 出現新的 item key，Metadata header 取所有 run 的 union；缺少的 item 留白。

## Data source mapping

| Sheet | Source |
| --- | --- |
| `01_Metadata` | Main Station A→C complete key/value set + run context |
| `02_FR_original` | RawData `FR_Original` |
| `03_FR_1_3` | FATP FR CSV detailed `FR` |
| `04_FR_1_12` | RawData `FR_1/12smooth` |
| `05_THD` | FATP FR CSV detailed `THD` |
| `06_Phase` | FATP FR CSV detailed `Phase` |
| `07_Noise` | FATP Noise CSV detailed spectrum |
| `08_SNR` | Main Station `SNR` |
| `09_Sensitivity` | Main Station `Sensitivity` |

RawData `FR_1/3smooth` 不使用。

## Result rules

### `03_FR_1_3`

`FR_File_Result` 來源：selected FR filename：

```text
*_FR_PASS_*.csv -> PASS
*_FR_FAIL_*.csv -> FAIL
```

### `05_THD` ~ `09_Sensitivity`

各自 Result 讀 Main Station 對應 item 的 B欄：

```text
THD         -> THD row
Phase       -> Phase row
Noise       -> Noise row
SNR         -> SNR row
Sensitivity -> Sensitivity row

1 -> PASS
0 -> FAIL
missing/invalid -> blank
```

不解析 FR CSV 內部 `Test Result:`。

## 02 / 04 RawData sheet — V13.6

`02_FR_original` 與 `04_FR_1_12` leading columns 固定：

```text
SN
Test_Time
RawData_Match_Status
<frequency data...>
```

這兩頁不要顯示：

```text
Path_Result
FR_File_Result
RawData_Result
RawData_PF_Mismatch
```

RawData filename result/mismatch 可保留在 internal model / Metadata 做 traceability，但不要出現在 02/04。

## 08_SNR / 09_Sensitivity

### `08_SNR`

```text
SN
Test_Time
Path_Result
Result
SNR_dB
SNR_Source_Status
```

不再包含 `Sensitivity_dBFS`。

### `09_Sensitivity`

```text
SN
Test_Time
Path_Result
Result
Sensitivity_dBFS
Sensitivity_Source_Status
```

SNR / Sensitivity 都直接使用 Main Station 對應 row 的 B欄 result 與 C欄 value；缺 item 就留白，不自行計算替代值。

## RawData matching

只有在有提供 RawData archive 時才啟動 matcher。

原則：

1. Test Type 一致
2. SN exact match（normalize 後）
3. filename PASS/FAIL 可作 internal supporting condition
4. 以 selected FATP FR filename timestamp 做 proximity matching
5. 超過 tolerance 不配
6. 無安全候選 → `UNMATCHED`
7. 多候選同樣合理 → `AMBIGUOUS`

目前 60 秒 tolerance 仍為 proposed，需要同批 FATP + RawData 驗證。

## Retest

保留所有歷史 run。

`Latest_Run`：

```text
(Test_Type, Mode, SN)
```

排序使用 Main Station filename 的 Test_Time，Run_ID text 作 tie-break。

## Limit

Main Station D/E 欄是 Low/High limit，但 V13 暫不處理：

- 不輸出 limit
- 不用 limit 判 PASS/FAIL
- 不建立 limit sheet

後續套用專用 Limit Excel template。

## QC

Workbook 不建立 Import Log。

runtime / console QC 應涵蓋：

- unsupported archive
- missing / duplicate / malformed CSV
- filename timestamp parse failure
- production fractional-second time parse failure
- Test Type / station cross-check mismatch
- Path_Result vs FR_File_Result mismatch
- RawData MATCHED / UNMATCHED / AMBIGUOUS
- missing/invalid THD / Phase / Noise / SNR / Sensitivity flag
- frequency-axis mismatch

RawData 沒提供不是 QC error。

## 執行與開發

目前 V13.5 code 入口：

```powershell
python -m src.main
```

V13.6 code 尚待 Codex 更新後才算完成。

V12 暫時保留：

```powershell
python src/build_summary.py <raw-data-folder>
```

## Public repository 注意事項

此 repository 是 public。不要 commit 真實 FATP / RawData archive、CSV、WAV、XLSX、DUT SN、MAC、operator/tester ID 或其他 factory-sensitive data。Regression tests 使用 synthetic / redacted fixtures。
