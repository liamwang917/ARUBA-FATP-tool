"""RawData matching and retest selection."""

import logging
from collections import defaultdict
from datetime import datetime

from .config import MatchConfig
from .models import RawRecord, TestRun


def match_rawdata(runs: list[TestRun], records: list[RawRecord] | None,
                  config: MatchConfig, logger: logging.Logger) -> None:
    if records is None:
        for run in runs:
            run.rawdata_match_status = "NOT_PROVIDED"
        return
    for run in runs:
        run.rawdata_match_status = "UNMATCHED"
        if not run.sn or not run.fr_timestamp:
            logger.warning("RawData unmatched: missing SN or FR timestamp for %s", run.run_path)
            continue
        candidates = [record for record in records if not record.consumed
                      and record.test_type == run.test_type
                      and record.sn == run.sn.strip().upper()
                      and record.timestamp is not None]
        ranked = []
        for record in candidates:
            delta = abs((record.timestamp - run.fr_timestamp).total_seconds())
            if delta <= config.rawdata_max_time_delta_sec:
                pf_penalty = 0 if not run.fr_file_result or record.result == run.fr_file_result else 1
                ranked.append((pf_penalty, delta, record.source, record))
        ranked.sort(key=lambda item: (item[0], item[1], item[2]))
        if not ranked:
            logger.warning("RawData UNMATCHED for %s", run.run_path)
            continue
        best = ranked[0]
        if len(ranked) > 1 and ranked[1][0] == best[0] and ranked[1][1] - best[1] <= config.rawdata_ambiguous_margin_sec:
            run.rawdata_match_status = "AMBIGUOUS"
            logger.warning("RawData AMBIGUOUS for %s", run.run_path)
            continue
        record = best[3]
        record.consumed = True
        run.rawdata_match_status = "MATCHED"
        run.rawdata_result = record.result
        run.rawdata_time_delta_s = best[1]
        run.rawdata_pf_mismatch = bool(record.result and run.fr_file_result and record.result != run.fr_file_result)
        run.raw_fr_original = record.fr_original
        run.raw_fr_1_12 = record.fr_1_12
        if run.rawdata_pf_mismatch:
            logger.warning("RawData_Result disagrees with FR_File_Result for %s", run.run_path)


def mark_latest_runs(runs: list[TestRun]) -> None:
    groups: dict[tuple[str, str, str], list[TestRun]] = defaultdict(list)
    for run in runs:
        groups[(run.test_type, run.mode, run.sn.strip().upper())].append(run)
    for grouped in groups.values():
        valid = [run for run in grouped if run.sn]
        if not valid:
            continue
        latest = max(valid, key=lambda run: (run.start_time or datetime.min, run.run_id))
        latest.latest_run = True

