"""Data models shared by V13 scanners, parsers, matcher, and reports."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Curve:
    frequencies: list[float] = field(default_factory=list)
    values: list[float] = field(default_factory=list)


@dataclass
class RawRecord:
    test_type: str
    sn: str
    timestamp: Optional[datetime]
    result: str
    source: str
    fr_original: Curve = field(default_factory=Curve)
    fr_1_12: Curve = field(default_factory=Curve)
    consumed: bool = False


@dataclass
class TestRun:
    test_type: str
    mode: str
    station: str
    path_result: str
    run_path: str
    main_csv: str = ""
    fr_csv: str = ""
    noise_csv: str = ""
    sn: str = ""
    run_id: str = ""
    operator: str = ""
    tester: str = ""
    sw_version: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_test_time_s: object = ""
    sensitivity: object = ""
    snr: object = ""
    snr_present: bool = False
    item_results: dict[str, str] = field(default_factory=dict)
    fr_file_result: str = ""
    fr_timestamp: Optional[datetime] = None
    fr: Curve = field(default_factory=Curve)
    thd: Curve = field(default_factory=Curve)
    phase: Curve = field(default_factory=Curve)
    noise: Curve = field(default_factory=Curve)
    latest_run: bool = False
    rawdata_result: str = ""
    rawdata_match_status: str = "NOT_PROVIDED"
    rawdata_time_delta_s: object = ""
    rawdata_pf_mismatch: object = ""
    raw_fr_original: Curve = field(default_factory=Curve)
    raw_fr_1_12: Curve = field(default_factory=Curve)
    mac: str = ""

