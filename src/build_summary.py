"""
ARUBA FATP microphone test-data summary builder.

Current version: v12 ("calculation-friendly" variant).
Version history and the V13 backlog are tracked in CHANGELOG.md;
this file is intentionally not renamed per version so tooling and
launcher paths stay stable across releases.
"""

import csv
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from openpyxl import Workbook

SHEETS = [
    "FR_original",
    "FR_1_3",
    "FR_1_12",
    "THD",
    "Phase",
    "Noise",
    "Sealing",
]

# Exact-match section names for Online CSVs
ONLINE_EXACT_SECTIONS = {"fr", "thd", "phase", "noise", "sealing"}

# Prefix-match section names for RawData_RD CSVs
RAWDATA_RD_PREFIX_SECTIONS = {"fr_original", "froriginal", "fr_1/12smooth", "fr1/12smooth"}


def normalize(s: str) -> str:
    s = (s or "").replace("（", "(").replace("）", ")").replace("：", ":")
    return re.sub(r"\s+", "", s).lower()


def coerce_excel_value(value):
    """
    Convert CSV text to Excel-friendly numeric values when possible.
    This lets pasted data participate in AVERAGE / MAX / MIN / STDEV.
    Non-numeric strings stay as text.
    """
    if value is None:
        return ""
    s = str(value).strip()
    if s == "":
        return ""
    if re.fullmatch(r"AP[^_]*", s, re.IGNORECASE):
        return s
    if s.upper() in {"PASS", "FAIL", "NA"}:
        return s
    if re.fullmatch(r"\d{14}", s):
        return s
    try:
        if re.fullmatch(r"[+-]?\d+", s):
            return int(s)
        if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+)", s):
            return float(s)
        return float(s)
    except Exception:
        return s


def read_csv_rows(path: Path) -> List[List[str]]:
    encodings = ["utf-8-sig", "utf-8", "cp950", "big5", "latin1"]
    for enc in encodings:
        try:
            with path.open("r", encoding=enc, newline="") as f:
                return list(csv.reader(f))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"Unable to decode {path}")


def first_nonempty_cell(row: List[str]) -> str:
    for cell in row:
        if str(cell).strip() != "":
            return str(cell)
    return ""


def extract_sn_only(text: str) -> str:
    """
    Keep only AP... up to the first underscore.
    Examples:
      AP2644631900004_20260325090902 -> AP2644631900004
      AP2644631900004_FR_20260325090839.csv -> AP2644631900004
    """
    stem = Path(text).stem
    m = re.search(r"(AP[^_]*)", stem, re.IGNORECASE)
    if m:
        return m.group(1)
    return stem.split("_", 1)[0]


def parse_sn_time_from_filename(file_name: str) -> Tuple[str, str]:
    stem = Path(file_name).stem
    sn = extract_sn_only(stem)
    m = re.search(r"(\d{14})", stem)
    time_str = m.group(1) if m else ""
    return sn, time_str


def parse_time_from_filename(file_name: str) -> str:
    m = re.search(r"(\d{14})", Path(file_name).stem)
    return m.group(1) if m else ""


def find_file(folder: Path, keyword: str) -> Optional[Path]:
    keyword_n = keyword.lower()
    matches = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".csv" and keyword_n in p.name.lower()]
    matches.sort(key=lambda p: p.name)
    return matches[0] if matches else None


def row_tail_from_col_b(row: List[str]) -> List[str]:
    tail = list(row[1:])
    while tail and str(tail[-1]).strip() == "":
        tail.pop()
    return tail


def is_online_section_header(label_norm: str) -> bool:
    return label_norm in ONLINE_EXACT_SECTIONS


def is_rawdata_rd_section_header(label_norm: str) -> bool:
    if label_norm in RAWDATA_RD_PREFIX_SECTIONS:
        return True
    return False


def find_section_values_exact(
    rows: List[List[str]],
    section_name: str,
    data_label: str,
    frequency_label: str = "Frequency(Hz):",
    test_result_label: Optional[str] = None,
) -> Tuple[Optional[str], List[str], List[str]]:
    """
    For Online CSVs:
    section_name must match exactly after normalization.
    This prevents 'FR' from accidentally matching 'Frequency(Hz):'.
    """
    section_n = normalize(section_name)
    data_n = normalize(data_label)
    freq_n = normalize(frequency_label)
    test_n = normalize(test_result_label) if test_result_label else None

    in_section = False
    test_result_value: Optional[str] = None
    frequency_values: List[str] = []
    data_values: List[str] = []

    for row in rows:
        label = first_nonempty_cell(row)
        label_n = normalize(label)

        if label_n == section_n:
            in_section = True
            test_result_value = None
            frequency_values = []
            data_values = []
            continue

        if not in_section:
            continue

        # Stop only when another real section header starts
        if label_n and is_online_section_header(label_n):
            break

        if test_n and label_n == test_n:
            # Need the B column value, not the first non-empty value after label
            test_result_value = row[1].strip() if len(row) > 1 else ""
        elif label_n == freq_n:
            frequency_values = row_tail_from_col_b(row)
        elif label_n == data_n:
            data_values = row_tail_from_col_b(row)
            if frequency_values or data_values:
                break

    return test_result_value, frequency_values, data_values


def find_section_values_prefix(
    rows: List[List[str]],
    section_prefix: str,
    data_label: str,
    frequency_label: str = "Frequency(Hz):",
    test_result_label: Optional[str] = None,
) -> Tuple[Optional[str], List[str], List[str]]:
    """
    For RawData_RD CSVs:
    section name is matched by prefix (e.g. FR_Original..., FR_1/12smooth...).
    """
    section_prefix_n = normalize(section_prefix)
    data_n = normalize(data_label)
    freq_n = normalize(frequency_label)
    test_n = normalize(test_result_label) if test_result_label else None

    in_section = False
    test_result_value: Optional[str] = None
    frequency_values: List[str] = []
    data_values: List[str] = []

    for row in rows:
        label = first_nonempty_cell(row)
        label_n = normalize(label)

        if label_n.startswith(section_prefix_n):
            in_section = True
            test_result_value = None
            frequency_values = []
            data_values = []
            continue

        if not in_section:
            continue

        if label_n and is_rawdata_rd_section_header(label_n):
            break

        if test_n and label_n == test_n:
            test_result_value = row[1].strip() if len(row) > 1 else ""
        elif label_n == freq_n:
            frequency_values = row_tail_from_col_b(row)
        elif label_n == data_n:
            data_values = row_tail_from_col_b(row)
            if frequency_values or data_values:
                break

    return test_result_value, frequency_values, data_values


def fr_result_from_filename(name: str) -> str:
    upper = name.upper()
    if "PASS" in upper:
        return "PASS"
    if "FAIL" in upper:
        return "FAIL"
    return "NA"


def ensure_headers(ws):
    ws.cell(row=1, column=1, value="SN")
    ws.cell(row=1, column=2, value="Time")
    ws.cell(row=1, column=3, value="Result")


def set_frequency_header_if_empty(ws, frequency_values: List[str], start_col: int = 4):
    if not frequency_values:
        return
    existing = [ws.cell(row=1, column=i).value for i in range(start_col, start_col + len(frequency_values))]
    if any(v not in (None, "") for v in existing):
        return
    for i, v in enumerate(frequency_values, start=start_col):
        ws.cell(row=1, column=i, value=coerce_excel_value(v))


def append_row(ws, sn: str, time_str: str, result: Optional[str], values: List[str], start_col: int = 4):
    row_idx = ws.max_row + 1 if ws.max_row >= 1 else 2
    if row_idx == 1:
        row_idx = 2
    ws.cell(row=row_idx, column=1, value=sn)
    ws.cell(row=row_idx, column=2, value=time_str)
    ws.cell(row=row_idx, column=3, value=result if result is not None else "")
    for i, v in enumerate(values, start=start_col):
        ws.cell(row=row_idx, column=i, value=coerce_excel_value(v))


def process_online_folder(folder: Path, wb: Workbook):
    sn = extract_sn_only(folder.name)

    fr_csv = find_file(folder, "fr")
    noise_csv = find_file(folder, "noise")
    sealing_csv = find_file(folder, "sealing")

    if fr_csv:
        rows = read_csv_rows(fr_csv)
        fr_time = parse_time_from_filename(fr_csv.name)
        fr_result = fr_result_from_filename(fr_csv.name)

        _, fr_freq, fr_vals = find_section_values_exact(rows, "FR", "Data (dBFS):")
        _, thd_freq, thd_vals = find_section_values_exact(rows, "THD", "Data (%):")
        _, phase_freq, phase_vals = find_section_values_exact(rows, "Phase", "Data (Deg):")

        set_frequency_header_if_empty(wb["FR_1_3"], fr_freq)
        set_frequency_header_if_empty(wb["THD"], thd_freq)
        set_frequency_header_if_empty(wb["Phase"], phase_freq)

        append_row(wb["FR_1_3"], sn, fr_time, fr_result, fr_vals)
        append_row(wb["THD"], sn, fr_time, fr_result, thd_vals)
        append_row(wb["Phase"], sn, fr_time, fr_result, phase_vals)

    if noise_csv:
        rows = read_csv_rows(noise_csv)
        noise_time = parse_time_from_filename(noise_csv.name)
        noise_result, noise_freq, noise_vals = find_section_values_exact(
            rows, "Noise", "Data (dB(A)V):", test_result_label="Test Result:"
        )
        set_frequency_header_if_empty(wb["Noise"], noise_freq)
        append_row(wb["Noise"], sn, noise_time, noise_result or "", noise_vals)

    if sealing_csv:
        rows = read_csv_rows(sealing_csv)
        sealing_time = parse_time_from_filename(sealing_csv.name)
        sealing_result, sealing_freq, sealing_vals = find_section_values_exact(
            rows, "Sealing", "Data (dBFS):", test_result_label="Test Result:"
        )
        set_frequency_header_if_empty(wb["Sealing"], sealing_freq)
        append_row(wb["Sealing"], sn, sealing_time, sealing_result or "", sealing_vals)


def process_rawdata_rd_folder(folder: Path, wb: Workbook):
    csvs = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".csv" and "fr" in p.name.lower()]
    csvs.sort(key=lambda p: p.name)
    for fr_csv in csvs:
        rows = read_csv_rows(fr_csv)
        sn, time_str = parse_sn_time_from_filename(fr_csv.name)
        result = fr_result_from_filename(fr_csv.name)

        _, orig_freq, orig_vals = find_section_values_prefix(rows, "FR_Original", "Data (dBFS):")
        _, sm12_freq, sm12_vals = find_section_values_prefix(rows, "FR_1/12smooth", "Data (dBFS):")

        set_frequency_header_if_empty(wb["FR_original"], orig_freq)
        set_frequency_header_if_empty(wb["FR_1_12"], sm12_freq)

        append_row(wb["FR_original"], sn, time_str, result, orig_vals)
        append_row(wb["FR_1_12"], sn, time_str, result, sm12_vals)


def build_summary(root_dir: Path, output_path: Path):
    wb = Workbook()
    default_ws = wb.active
    wb.remove(default_ws)

    for s in SHEETS:
        wb.create_sheet(title=s)
    for s in SHEETS:
        ensure_headers(wb[s])

    online_dir = root_dir / "Online"
    rawdata_rd_dir = root_dir / "RawData_RD"

    if online_dir.exists() and online_dir.is_dir():
        subfolders = [p for p in online_dir.iterdir() if p.is_dir()]
        subfolders.sort(key=lambda p: p.name)
        for folder in subfolders:
            process_online_folder(folder, wb)

    if rawdata_rd_dir.exists() and rawdata_rd_dir.is_dir():
        process_rawdata_rd_folder(rawdata_rd_dir, wb)

    wb.save(output_path)


def choose_folder_gui() -> Optional[str]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select the main raw data folder (contains Online and RawData_RD)")
        root.destroy()
        return folder or None
    except Exception:
        return None


def main():
    if len(sys.argv) >= 2:
        root_dir = Path(sys.argv[1])
    else:
        selected = choose_folder_gui()
        if not selected:
            print("No folder selected.")
            sys.exit(1)
        root_dir = Path(selected)

    if not root_dir.exists() or not root_dir.is_dir():
        print(f"Folder not found: {root_dir}")
        sys.exit(1)

    output_path = root_dir / "summary.xlsx"
    build_summary(root_dir, output_path)
    print(f"Done: {output_path}")


if __name__ == "__main__":
    main()
