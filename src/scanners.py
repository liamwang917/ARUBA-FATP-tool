"""Recursive FATP and RawData ZIP scanners."""

import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import PurePosixPath

from .models import RawRecord, TestRun
from .parsers import (
    normalize, parse_fr, parse_noise, parse_rawdata, parse_station,
    result_from_filename, timestamp_from_name,
)
from .zip_reader import ZipCsvReader


def _path_context(name: str) -> tuple[str, str, str] | None:
    parts = PurePosixPath(name).parts
    lower = [part.lower() for part in parts]
    mode_index = next((i for i, part in enumerate(lower) if part in {"online", "offline"}), None)
    if mode_index is None:
        return None
    result_index = next((i for i in range(mode_index + 1, len(parts) - 1)
                         if lower[i] in {"pass", "fail"}), None)
    if result_index is None or result_index + 1 >= len(parts) - 1:
        return None
    station = parts[result_index - 1] if result_index > mode_index else ""
    run_dir = "/".join(parts[:result_index + 2])
    return parts[mode_index].title(), station, parts[result_index].upper(), run_dir


def _is_fr(name: str) -> bool:
    stem = PurePosixPath(name).stem.upper()
    return bool(re.search(r"(?:^|_)FR_(?:PASS|FAIL)(?:_|$)", stem))


def _is_noise(name: str) -> bool:
    return "NOISE" in PurePosixPath(name).stem.upper()


def _select_latest(names: list[str], kind: str, run_path: str, logger: logging.Logger) -> str:
    if not names:
        logger.warning("Missing %s CSV in %s", kind, run_path)
        return ""
    ranked = sorted(names, key=lambda name: (timestamp_from_name(name) is not None,
                                             timestamp_from_name(name) or datetime.min,
                                             name))
    if len(names) > 1:
        logger.warning("Duplicate %s CSV candidates in %s; selected %s", kind, run_path, ranked[-1])
    return ranked[-1]


def scan_fatp(reader: ZipCsvReader, test_type: str, logger: logging.Logger) -> list[TestRun]:
    groups: dict[str, list[str]] = defaultdict(list)
    contexts = {}
    for name in reader.csv_names:
        context = _path_context(name)
        if context:
            mode, station, path_result, run_dir = context
            groups[run_dir].append(name)
            contexts[run_dir] = (mode, station, path_result)
    runs: list[TestRun] = []
    for run_dir in sorted(groups):
        mode, station, path_result = contexts[run_dir]
        names = groups[run_dir]
        rows_by_name = {name: reader.read_rows(name) for name in names}
        main_candidates = [name for name, rows in rows_by_name.items()
                           if any(row and normalize(row[0]) == "uut_sn" for row in rows)]
        fr_candidates = [name for name in names if _is_fr(name)]
        noise_candidates = [name for name in names if _is_noise(name) and name not in fr_candidates]
        main_name = _select_latest(main_candidates, "Main Station", run_dir, logger)
        fr_name = _select_latest(fr_candidates, "FR", run_dir, logger)
        noise_name = _select_latest(noise_candidates, "Noise", run_dir, logger)
        run = TestRun(test_type, mode, station, path_result, run_dir,
                      main_csv=main_name, fr_csv=fr_name, noise_csv=noise_name)
        if main_name:
            station_data = parse_station(rows_by_name[main_name], main_name, logger)
            for key, value in station_data.items():
                setattr(run, key, value)
            expected = f"ARUBA_{test_type}"
            if station_data["station_id"] and station_data["station_id"].upper() != expected:
                logger.warning("Path Test Type %s disagrees with station_id %s in %s",
                               test_type, station_data["station_id"], main_name)
            if run.tester and normalize(run.station) != normalize(run.tester):
                logger.warning("Path Station %s disagrees with tester_id %s in %s",
                               run.station, run.tester, main_name)
        if fr_name:
            run.fr_file_result = result_from_filename(fr_name)
            run.fr_timestamp = timestamp_from_name(fr_name)
            curves = parse_fr(rows_by_name[fr_name])
            run.fr, run.thd, run.phase = curves["fr"], curves["thd"], curves["phase"]
            for label, curve in (("FR", run.fr), ("THD", run.thd), ("Phase", run.phase)):
                if not curve.values:
                    logger.warning("Missing or malformed detailed %s section in %s", label, fr_name)
            if run.fr_file_result and run.path_result != run.fr_file_result:
                logger.warning("Path_Result %s disagrees with FR_File_Result %s in %s",
                               run.path_result, run.fr_file_result, run_dir)
        if noise_name:
            run.noise = parse_noise(rows_by_name[noise_name])
            if not run.noise.values:
                logger.warning("Missing or malformed detailed Noise section in %s", noise_name)
        if run.start_time is None and main_name:
            logger.warning("Unparseable or missing test_start_time in %s", main_name)
        runs.append(run)
    return runs


def _raw_test_type(name: str) -> str:
    parts = {part.upper() for part in PurePosixPath(name).parts}
    if "PREMIC" in parts:
        return "PREMIC"
    if "MIC" in parts:
        return "MIC"
    return ""


def _sn_from_name(name: str) -> str:
    stem = PurePosixPath(name).stem
    match = re.search(r"(AP[^_]+)", stem, re.IGNORECASE)
    return (match.group(1) if match else stem.split("_", 1)[0]).strip().upper()


def scan_rawdata(reader: ZipCsvReader, logger: logging.Logger) -> list[RawRecord]:
    records = []
    for name in sorted(reader.csv_names):
        test_type = _raw_test_type(name)
        if not test_type or not _is_fr(name):
            continue
        curves = parse_rawdata(reader.read_rows(name))
        if not curves["fr_original"].values and not curves["fr_1_12"].values:
            logger.warning("Empty or malformed RawData sections in %s", name)
        records.append(RawRecord(
            test_type=test_type, sn=_sn_from_name(name), timestamp=timestamp_from_name(name),
            result=result_from_filename(name), source=name,
            fr_original=curves["fr_original"], fr_1_12=curves["fr_1_12"],
        ))
    return records

