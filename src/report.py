"""Locked V13 workbook generation."""

import logging
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from .config import METADATA_COLUMNS, SHEET_NAMES
from .models import Curve, TestRun


FREQUENCY_LEADS = {
    "02_FR_original": ("SN", "Test_Time", "Path_Result", "FR_File_Result", "RawData_Result", "RawData_Match_Status", "RawData_PF_Mismatch"),
    "03_FR_1_3": ("SN", "Test_Time", "Path_Result", "FR_File_Result"),
    "04_FR_1_12": ("SN", "Test_Time", "Path_Result", "FR_File_Result", "RawData_Result", "RawData_Match_Status", "RawData_PF_Mismatch"),
    "05_THD": ("SN", "Test_Time", "Path_Result", "Result"),
    "06_Phase": ("SN", "Test_Time", "Path_Result", "Result"),
    "07_Noise": ("SN", "Test_Time", "Path_Result", "Result"),
}


def _metadata_row(run: TestRun) -> list[object]:
    values = {
        "Test_Type": run.test_type, "Mode": run.mode, "SN": run.sn,
        "Run_ID": run.run_id, "Test_Time": run.start_time, "Station": run.station,
        "Operator": run.operator, "Tester": run.tester, "SW_Version": run.sw_version,
        "Start_Time": run.start_time, "End_Time": run.end_time,
        "Total_Test_Time_s": run.total_test_time_s, "Sensitivity_dBFS": run.sensitivity,
        "SNR_dB": run.snr, "Path_Result": run.path_result,
        "FR_File_Result": run.fr_file_result, "Latest_Run": "TRUE" if run.latest_run else "FALSE",
        "RawData_Result": run.rawdata_result, "RawData_Match_Status": run.rawdata_match_status,
        "RawData_Time_Delta_s": run.rawdata_time_delta_s,
        "RawData_PF_Mismatch": run.rawdata_pf_mismatch if run.rawdata_pf_mismatch != "" else "",
        "Main_CSV": run.main_csv, "FR_CSV": run.fr_csv, "Noise_CSV": run.noise_csv,
    }
    return [values[column] for column in METADATA_COLUMNS]


def _curve_and_lead(run: TestRun, sheet: str) -> tuple[Curve, list[object]]:
    base = [run.sn, run.start_time, run.path_result]
    if sheet == "02_FR_original":
        return run.raw_fr_original, base + [run.fr_file_result, run.rawdata_result, run.rawdata_match_status, run.rawdata_pf_mismatch]
    if sheet == "03_FR_1_3":
        return run.fr, base + [run.fr_file_result]
    if sheet == "04_FR_1_12":
        return run.raw_fr_1_12, base + [run.fr_file_result, run.rawdata_result, run.rawdata_match_status, run.rawdata_pf_mismatch]
    mapping = {"05_THD": (run.thd, "THD"), "06_Phase": (run.phase, "PHASE"), "07_Noise": (run.noise, "NOISE")}
    curve, key = mapping[sheet]
    return curve, base + [run.item_results.get(key, "")]


def _write_curve_sheet(ws, runs: list[TestRun], sheet: str, logger: logging.Logger) -> None:
    lead = FREQUENCY_LEADS[sheet]
    axis = next((curve.frequencies for run in runs for curve, _ in [_curve_and_lead(run, sheet)] if curve.frequencies), [])
    ws.append(list(lead) + axis)
    for run in runs:
        curve, leading = _curve_and_lead(run, sheet)
        values: list[object] = []
        if curve.frequencies:
            if curve.frequencies == axis:
                values = curve.values
            else:
                logger.warning("Frequency-axis mismatch on %s for %s; values left blank", sheet, run.run_path)
        ws.append(leading + values)


def build_workbook(runs: list[TestRun], output_path: Path, logger: logging.Logger) -> None:
    wb = Workbook()
    wb.remove(wb.active)
    for name in SHEET_NAMES:
        wb.create_sheet(name)
    wb["01_Metadata"].append(list(METADATA_COLUMNS))
    for run in runs:
        wb["01_Metadata"].append(_metadata_row(run))
    for sheet in SHEET_NAMES[1:7]:
        _write_curve_sheet(wb[sheet], runs, sheet, logger)
    snr = wb["08_SNR"]
    snr.append(["SN", "Test_Time", "Path_Result", "Result", "SNR_dB", "SNR_Source_Status", "Sensitivity_dBFS"])
    for run in runs:
        status = "Present in Main Station CSV" if run.snr_present else "Missing in Main Station CSV"
        snr.append([run.sn, run.start_time, run.path_result, run.item_results.get("SNR", ""), run.snr, status, run.sensitivity])
    for ws in wb.worksheets:
        ws.freeze_panes = "A2"
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                if isinstance(cell.value, datetime):
                    cell.number_format = "yyyy-mm-dd hh:mm:ss"
        for column in ws.columns:
            letter = column[0].column_letter
            ws.column_dimensions[letter].width = min(28, max(10, max(len(str(cell.value or "")) for cell in column) + 2))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

