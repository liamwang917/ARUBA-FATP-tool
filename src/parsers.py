"""V13 Main Station and detailed curve parsers."""

import logging
import re
from datetime import datetime
from pathlib import PurePosixPath

from .models import Curve


SECTION_NAMES = {"fr", "thd", "phase", "noise", "sealing", "fr_original", "fr_1/12smooth", "fr_1/3smooth"}


def normalize(value: object) -> str:
    text = str(value or "").replace("（", "(").replace("）", ")").replace("：", ":")
    return re.sub(r"\s+", "", text).lower()


def parse_datetime(value: object) -> datetime | None:
    text = str(value or "").strip()
    for fmt in ("%Y%m%d%H%M%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def timestamp_from_name(name: str) -> datetime | None:
    matches = re.findall(r"(?<!\d)(\d{14})(?!\d)", PurePosixPath(name).stem)
    return parse_datetime(matches[-1]) if matches else None


def result_from_filename(name: str) -> str:
    upper = PurePosixPath(name).stem.upper()
    if re.search(r"(?:^|_)FR_PASS(?:_|$)", upper):
        return "PASS"
    if re.search(r"(?:^|_)FR_FAIL(?:_|$)", upper):
        return "FAIL"
    return ""


def coerce_number(value: object) -> object:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        number = float(text)
        return int(number) if number.is_integer() else number
    except ValueError:
        return text


def flag_result(value: object) -> str:
    text = str(value or "").strip()
    return "PASS" if text == "1" else "FAIL" if text == "0" else ""


def parse_station(rows: list[list[str]], source: str, logger: logging.Logger) -> dict:
    items: dict[str, list[str]] = {}
    for index, row in enumerate(rows, 1):
        if not row or not str(row[0]).strip():
            continue
        if len(row) < 3:
            logger.warning("Malformed Main Station row %s:%d", source, index)
            continue
        if len(row) != 6:
            logger.warning("Main Station row does not have six columns %s:%d", source, index)
        items[normalize(row[0])] = row
    metadata_keys = {
        "sn": "uut_sn", "run_id": "tsr_id", "operator": "op_id",
        "station_id": "station_id", "tester": "tester_id",
        "sw_version": "test_sw_ver", "start_time": "test_start_time",
        "end_time": "test_end_time", "total_test_time_s": "total_test_time",
        "mac": "sfis_get_mac",
    }
    result = {key: (items.get(source_key, ["", "", ""])[2] or "").strip()
              for key, source_key in metadata_keys.items()}
    result["start_time"] = parse_datetime(result["start_time"])
    result["end_time"] = parse_datetime(result["end_time"])
    result["total_test_time_s"] = coerce_number(result["total_test_time_s"])
    result["item_results"] = {}
    for key in ("thd", "phase", "noise", "snr"):
        row = items.get(key)
        result["item_results"][key.upper()] = flag_result(row[1]) if row and len(row) > 1 else ""
        if row is None:
            logger.warning("Missing Main Station item %s in %s", key.upper(), source)
        elif len(row) < 2 or flag_result(row[1]) == "":
            logger.warning("Invalid Main Station %s result flag in %s", key.upper(), source)
    for key in ("sensitivity", "snr"):
        row = items.get(key)
        result[key] = coerce_number(row[2]) if row and len(row) > 2 else ""
    result["snr_present"] = "snr" in items
    return result


def _row_label(row: list[str]) -> str:
    return normalize(next((cell for cell in row if str(cell).strip()), ""))


def parse_curve(rows: list[list[str]], section: str, data_labels: tuple[str, ...]) -> Curve:
    target = normalize(section)
    accepted = {normalize(label) for label in data_labels}
    in_section = False
    frequencies: list[float] = []
    values: list[float] = []
    for row in rows:
        label = _row_label(row)
        if label == target:
            in_section = True
            continue
        if not in_section:
            continue
        if label in SECTION_NAMES and label != target:
            break
        tail = [coerce_number(cell) for cell in row[1:] if str(cell).strip()]
        if label == "frequency(hz):":
            frequencies = [value for value in tail if isinstance(value, (int, float))]
        elif label in accepted:
            values = [value for value in tail if isinstance(value, (int, float))]
            break
    if not frequencies or len(frequencies) != len(values):
        return Curve()
    return Curve(frequencies, values)


def parse_fr(rows: list[list[str]]) -> dict[str, Curve]:
    return {
        "fr": parse_curve(rows, "FR", ("Data (dBFS):",)),
        "thd": parse_curve(rows, "THD", ("Data (%):",)),
        "phase": parse_curve(rows, "Phase", ("Data (Deg):",)),
    }


def parse_noise(rows: list[list[str]]) -> Curve:
    return parse_curve(rows, "Noise", ("Data (dB(A)V):", "Data (dBFS):"))


def parse_rawdata(rows: list[list[str]]) -> dict[str, Curve]:
    return {
        "fr_original": parse_curve(rows, "FR_Original", ("Data (dBFS):",)),
        "fr_1_12": parse_curve(rows, "FR_1/12smooth", ("Data (dBFS):",)),
    }

