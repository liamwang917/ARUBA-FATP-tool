import csv
import io
import logging
import tempfile
import unittest
import zipfile
from pathlib import Path

from openpyxl import load_workbook

from src.config import MatchConfig, SHEET_NAMES
from src.main import run_pipeline


def csv_text(rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\r\n").writerows(rows)
    return stream.getvalue()


def main_rows(sn="APSYNTH001", run_id="RUN-SYNTH-001", start="20260909010101",
              thd="1", phase="1", noise="1", snr="1", include_snr=True,
              station_id="ARUBA_MIC", tester="ARUBA-MIC-01"):
    rows = [
        ["uut_sn", "", sn, "", "", ""],
        ["tsr_id", "", run_id, "", "", ""],
        ["op_id", "", "OP-REDACTED", "", "", ""],
        ["station_id", "", station_id, "", "", ""],
        ["tester_id", "", tester, "", "", ""],
        ["test_sw_ver", "", "SYNTH-1.0", "", "", ""],
        ["test_start_time", "", start, "", "", ""],
        ["test_end_time", "", start, "", "", ""],
        ["total_test_time", "", "12.5", "", "", ""],
        ["sfis_get_mac", "", "REDACTED", "", "", ""],
        ["Sensitivity", "1", "-31.5", "", "", ""],
        ["THD", thd, "0.5", "", "", ""],
        ["Phase", phase, "2.0", "", "", ""],
        ["Noise", noise, "-70", "", "", ""],
    ]
    if include_snr:
        rows.append(["SNR", snr, "38.25", "", "", ""])
    return rows


def fr_rows(axis=(100, 200), marker=0):
    return [
        ["FR"], ["Test Result:", "FAIL"], ["Frequency(Hz):", *axis],
        ["Data (dBFS):", -10 + marker, -11 + marker],
        ["THD"], ["Test Result:", "PASS"], ["Frequency(Hz):", *axis],
        ["Data (%):", 0.1, 0.2],
        ["Phase"], ["Test Result:", "FAIL"], ["Frequency(Hz):", *axis],
        ["Data (Deg):", 1.0, 2.0],
    ]


def noise_rows(axis=(100, 200)):
    return [["Noise"], ["Test Result:", "FAIL"], ["Frequency(Hz):", *axis],
            ["Data (dB(A)V):", -70, -71]]


def raw_rows(axis=(100, 200)):
    return [
        ["FR_Original"], ["Frequency(Hz):", *axis], ["Data (dBFS):", -9, -10],
        ["FR_1/12smooth"], ["Frequency(Hz):", *axis], ["Data (dBFS):", -9.5, -10.5],
        ["FR_1/3smooth"], ["Frequency(Hz):", *axis], ["Data (dBFS):", 999, 999],
    ]


def add_run(files, run="run1", timestamp="20260909010101", sn="APSYNTH001",
            run_id="RUN-SYNTH-001", path_result="PASS", fr_result="PASS",
            axis=(100, 200), test_type="MIC", mode="Online", **station_flags):
    station = f"ARUBA-{test_type}-01"
    base = f"{test_type}/{mode}/202609/20260909/{station}/{path_result}/{run}"
    station_flags.setdefault("station_id", f"ARUBA_{test_type}")
    station_flags.setdefault("tester", station)
    files[f"{base}/main_{timestamp}.csv"] = csv_text(main_rows(sn, run_id, timestamp, **station_flags))
    files[f"{base}/{sn}_FR_{fr_result}_{timestamp}.csv"] = csv_text(fr_rows(axis))
    files[f"{base}/{sn}_Noise_{timestamp}.csv"] = csv_text(noise_rows(axis))


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)


class V13PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.logger = logging.getLogger(f"test.{self.id()}")
        self.logger.addHandler(logging.NullHandler())

    def tearDown(self):
        self.temp.cleanup()

    def build(self, files, raw_files=None, config=None):
        mic = self.root / "ARUBA_MIC.zip"
        write_zip(mic, files)
        raw = None
        if raw_files is not None:
            raw = self.root / "RawData_RD.zip"
            write_zip(raw, raw_files)
        outputs = run_pipeline(mic, None, raw, self.root / "out", config, self.logger)
        self.assertEqual(len(outputs), 1)
        return load_workbook(outputs[0], data_only=False)

    def test_locked_workbook_and_not_provided_behavior(self):
        files = {}
        add_run(files, thd="0", phase="1", noise="bad", snr="0")
        wb = self.build(files)
        self.assertEqual(tuple(wb.sheetnames), SHEET_NAMES)
        metadata = wb["01_Metadata"]
        headers = [cell.value for cell in metadata[1]]
        row = dict(zip(headers, [cell.value for cell in metadata[2]]))
        self.assertEqual(row["RawData_Match_Status"], "NOT_PROVIDED")
        self.assertIsNone(row["RawData_Result"])
        self.assertEqual(wb["02_FR_original"]["F2"].value, "NOT_PROVIDED")
        self.assertIsNone(wb["02_FR_original"]["H2"].value)
        self.assertEqual(wb["05_THD"]["D2"].value, "FAIL")
        self.assertEqual(wb["06_Phase"]["D2"].value, "PASS")
        self.assertIsNone(wb["07_Noise"]["D2"].value)
        self.assertEqual(wb["08_SNR"]["D2"].value, "FAIL")
        self.assertEqual(wb["08_SNR"]["E2"].value, 38.25)
        forbidden = {"00_Import_Log", "Station_Limits"}
        self.assertFalse(forbidden.intersection(wb.sheetnames))
        self.assertNotIn("Section_Result", headers)
        self.assertNotIn("APx_Section_Result", headers)

    def test_missing_snr_is_blank_and_not_calculated(self):
        files = {}
        add_run(files, include_snr=False)
        wb = self.build(files)
        row = [cell.value for cell in wb["08_SNR"][2]]
        self.assertIsNone(row[3])
        self.assertIsNone(row[4])
        self.assertEqual(row[5], "Missing in Main Station CSV")

    def test_rawdata_matched_and_pf_mismatch(self):
        files = {}
        add_run(files)
        raw = {"RawData_RD/MIC/APSYNTH001_FR_FAIL_20260909010103.csv": csv_text(raw_rows())}
        wb = self.build(files, raw)
        headers = [cell.value for cell in wb["01_Metadata"][1]]
        row = dict(zip(headers, [cell.value for cell in wb["01_Metadata"][2]]))
        self.assertEqual(row["RawData_Match_Status"], "MATCHED")
        self.assertEqual(row["RawData_Result"], "FAIL")
        self.assertIs(row["RawData_PF_Mismatch"], True)
        self.assertEqual(wb["02_FR_original"]["H2"].value, -9)

    def test_rawdata_unmatched_and_ambiguous(self):
        files = {}
        add_run(files)
        far = {"RawData_RD/MIC/APSYNTH001_FR_PASS_20260909010300.csv": csv_text(raw_rows())}
        wb = self.build(files, far)
        self.assertEqual(wb["01_Metadata"]["S2"].value, "UNMATCHED")

        near = {
            "RawData_RD/MIC/APSYNTH001_FR_PASS_20260909010100.csv": csv_text(raw_rows()),
            "RawData_RD/MIC/APSYNTH001_FR_PASS_20260909010102.csv": csv_text(raw_rows()),
        }
        wb = self.build(files, near, MatchConfig(60, 5))
        self.assertEqual(wb["01_Metadata"]["S2"].value, "AMBIGUOUS")
        self.assertIsNone(wb["02_FR_original"]["H2"].value)

    def test_latest_run_duplicate_selection_and_axis_mismatch(self):
        files = {}
        add_run(files, run="old", timestamp="20260909010101", run_id="RUN-1")
        add_run(files, run="new", timestamp="20260909010201", run_id="RUN-2", axis=(100, 300))
        base = "MIC/Online/202609/20260909/ARUBA-MIC-01/PASS/old"
        files[f"{base}/APSYNTH001_FR_PASS_20260909010131.csv"] = csv_text(fr_rows(marker=5))
        wb = self.build(files)
        headers = [cell.value for cell in wb["01_Metadata"][1]]
        rows = [dict(zip(headers, [cell.value for cell in row])) for row in wb["01_Metadata"].iter_rows(min_row=2)]
        self.assertEqual(sum(row["Latest_Run"] == "TRUE" for row in rows), 1)
        self.assertEqual(next(row for row in rows if row["Latest_Run"] == "TRUE")["Run_ID"], "RUN-2")
        self.assertIn("20260909010131", next(row for row in rows if row["Run_ID"] == "RUN-1")["FR_CSV"])
        curve_rows = [[cell.value for cell in row[4:]] for row in wb["03_FR_1_3"].iter_rows(min_row=2)]
        self.assertEqual(sum(all(value is None for value in values) for values in curve_rows), 1)

    def test_requires_at_least_one_fatp_package(self):
        with self.assertRaisesRegex(ValueError, "At least one FATP input"):
            run_pipeline(None, None, None, self.root, logger=self.logger)

    def test_shared_mic_premic_pipeline_and_offline_discovery(self):
        mic_files = {}
        premic_files = {}
        add_run(mic_files)
        add_run(premic_files, test_type="PREMIC", mode="Offline", sn="APSYNTH002",
                run_id="RUN-SYNTH-PREMIC")
        mic = self.root / "ARUBA_MIC.zip"
        premic = self.root / "ARUBA_PREMIC.zip"
        write_zip(mic, mic_files)
        write_zip(premic, premic_files)
        outputs = run_pipeline(mic, premic, None, self.root / "out", logger=self.logger)
        self.assertEqual({path.name for path in outputs}, {
            "summary_MIC_Online.xlsx", "summary_PREMIC_Offline.xlsx"
        })
        wb = load_workbook(self.root / "out" / "summary_PREMIC_Offline.xlsx")
        self.assertEqual(wb["01_Metadata"]["A2"].value, "PREMIC")
        self.assertEqual(wb["01_Metadata"]["B2"].value, "Offline")


if __name__ == "__main__":
    unittest.main()

