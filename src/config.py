"""V13 configuration and locked workbook constants."""

from dataclasses import dataclass


SHEET_NAMES = (
    "01_Metadata",
    "02_FR_original",
    "03_FR_1_3",
    "04_FR_1_12",
    "05_THD",
    "06_Phase",
    "07_Noise",
    "08_SNR",
    "09_Sensitivity",
)

METADATA_CONTEXT_COLUMNS = (
    "Test_Type", "Mode", "SN", "Run_ID", "Test_Time", "Station",
    "Path_Result", "FR_File_Result", "Latest_Run", "RawData_Result",
    "RawData_Match_Status", "RawData_Time_Delta_s",
    "RawData_PF_Mismatch", "Main_CSV", "FR_CSV", "Noise_CSV",
)

SUPPORTED_ARCHIVE_SUFFIXES = (".zip", ".7z", ".tar", ".tar.gz", ".tgz")


@dataclass(frozen=True)
class MatchConfig:
    rawdata_max_time_delta_sec: int = 60
    rawdata_ambiguous_margin_sec: int = 5


