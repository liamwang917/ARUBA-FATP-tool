"""Command-line entry point for the V13.6 archive-to-workbook pipeline."""

import argparse
import logging
import sys
from pathlib import Path

from .archive_reader import ArchiveCsvReader, archive_stem, archive_suffix
from .config import MatchConfig
from .matcher import mark_latest_runs, match_rawdata
from .report import build_workbook
from .scanners import scan_fatp, scan_rawdata


def _logger(verbose: bool = False) -> logging.Logger:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")
    return logging.getLogger("aruba_fatp_v13")


def classify_inputs(paths: list[Path]) -> tuple[Path | None, Path | None, Path | None]:
    mic = premic = rawdata = None
    for path in paths:
        name = archive_stem(path).upper()
        if name == "ARUBA_MIC":
            mic = path
        elif name == "ARUBA_PREMIC":
            premic = path
        elif name == "RAWDATA_RD":
            rawdata = path
        else:
            raise ValueError(f"Unrecognized input package name: {path.name}")
    return mic, premic, rawdata


def run_pipeline(mic: Path | None, premic: Path | None, rawdata: Path | None,
                 output_dir: Path, config: MatchConfig | None = None,
                 logger: logging.Logger | None = None) -> list[Path]:
    logger = logger or _logger()
    config = config or MatchConfig()
    if not mic and not premic:
        raise ValueError("At least one FATP archive is required: ARUBA_MIC or ARUBA_PREMIC")
    packages = [("MIC", mic), ("PREMIC", premic)]
    for _, package in packages:
        if package and (not package.is_file() or not archive_suffix(package)):
            raise ValueError(f"FATP archive missing or unsupported: {package}")
    if rawdata and (not rawdata.is_file() or not archive_suffix(rawdata)):
        raise ValueError(f"RawData archive missing or unsupported: {rawdata}")

    runs = []
    for test_type, package in packages:
        if package:
            logger.info("Scanning %s", package)
            with ArchiveCsvReader(package, logger) as reader:
                runs.extend(scan_fatp(reader, test_type, logger))
    raw_records = None
    if rawdata:
        logger.info("Scanning optional RawData %s", rawdata)
        with ArchiveCsvReader(rawdata, logger) as reader:
            raw_records = scan_rawdata(reader, logger)
    else:
        logger.info("RawData archive not provided; RawData status will be NOT_PROVIDED")
    match_rawdata(runs, raw_records, config, logger)
    mark_latest_runs(runs)

    outputs = []
    for test_type, package in packages:
        if not package:
            continue
        for mode in ("Online", "Offline"):
            selected = [run for run in runs if run.test_type == test_type and run.mode == mode]
            if not selected:
                continue
            output = output_dir / f"summary_{test_type}_{mode}.xlsx"
            build_workbook(selected, output, logger)
            outputs.append(output)
            logger.info("Created %s", output)
    if not outputs:
        raise ValueError("No Online or Offline FATP runs were discovered in the supplied archive(s)")
    return outputs


def choose_packages_gui() -> list[Path]:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askopenfilenames(
            title="Select MIC/PREMIC archives; RawData is optional",
            filetypes=(
                ("Supported archives", "*.zip *.7z *.tar *.tar.gz *.tgz"),
                ("ZIP archives", "*.zip"),
                ("7Z archives", "*.7z"),
                ("TAR archives", "*.tar *.tar.gz *.tgz"),
            ),
        )
        root.destroy()
        return [Path(path) for path in selected]
    except Exception:
        return []


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build V13.6 ARUBA FATP Excel summaries directly from archives.")
    parser.add_argument("packages", nargs="*", type=Path,
                        help="MIC/PREMIC archives and optional RawData archive")
    parser.add_argument("--mic", type=Path, help="Path to ARUBA_MIC archive")
    parser.add_argument("--premic", type=Path, help="Path to ARUBA_PREMIC archive")
    parser.add_argument("--rawdata", type=Path, help="Optional path to RawData_RD archive")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd(), help="Workbook output directory")
    parser.add_argument("--rawdata-max-time-delta-sec", type=int, default=60)
    parser.add_argument("--rawdata-ambiguous-margin-sec", type=int, default=5)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    logger = _logger(args.verbose)
    try:
        positional = args.packages or ([] if any((args.mic, args.premic, args.rawdata)) else choose_packages_gui())
        pmic, ppremic, prawdata = classify_inputs(positional)
        mic, premic, rawdata = args.mic or pmic, args.premic or ppremic, args.rawdata or prawdata
        config = MatchConfig(args.rawdata_max_time_delta_sec, args.rawdata_ambiguous_margin_sec)
        run_pipeline(mic, premic, rawdata, args.output_dir, config, logger)
        return 0
    except (ValueError, OSError) as exc:
        logger.error("%s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


