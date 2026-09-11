"""V14.5 RC production entry point, with an explicit developer-summary mode."""
import argparse
import logging
from pathlib import Path
from .main import choose_packages_gui, classify_inputs, run_pipeline
from .v14_report import build_v14_report, verify_template


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = REPO_ROOT / "templates" / "Post-MIC limit_20260911.xlsx"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "report"
RC_NAME = "ARUBA FATP V14.5 RC"

def main(argv=None):
    parser = argparse.ArgumentParser(description="Build V14.5 RC reports directly from FATP archives.")
    parser.add_argument("packages", nargs="*", type=Path, help="MIC/PREMIC archives and optional RawData archive")
    parser.add_argument("--mic", type=Path); parser.add_argument("--premic", type=Path); parser.add_argument("--rawdata", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Developer override; production uses the packaged master")
    parser.add_argument("--summary", nargs="+", type=Path, help="Developer-only normalized V13.6 summaries")
    parser.add_argument("--output", type=Path, help="Required with --summary")
    parser.add_argument("--skip-template-hash-check", action="store_true", help="Synthetic/developer templates only")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("aruba_fatp_v14")
    try:
        if args.summary:
            if not args.output:
                parser.error("--output is required with --summary")
            logger.info("%s developer summary mode", RC_NAME)
            build_v14_report(args.template, args.summary, args.output, verify_hash=not args.skip_template_hash_check)
            logger.info("Created %s", args.output)
            return 0
        positional = args.packages or ([] if any((args.mic, args.premic, args.rawdata)) else choose_packages_gui())
        if not positional and not any((args.mic, args.premic, args.rawdata)):
            raise ValueError("No archive selected. Select ARUBA_MIC and/or ARUBA_PREMIC; RawData_RD is optional")
        pmic, ppremic, prawdata = classify_inputs(positional)
        mic, premic, rawdata = args.mic or pmic, args.premic or ppremic, args.rawdata or prawdata
        logger.info("%s", RC_NAME)
        logger.info("Selected inputs: MIC=%s | PREMIC=%s | RawData=%s", mic or "not selected", premic or "not selected", rawdata or "not selected")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory: %s", args.output_dir.resolve())
        verify_template(args.template)
        summaries = run_pipeline(mic, premic, rawdata, args.output_dir, logger=logger)
        reports = []
        for summary in summaries:
            suffix = summary.stem.removeprefix("summary_")
            report = args.output_dir / f"report_{suffix}.xlsx"
            try:
                build_v14_report(args.template, [summary], report, logger=logger)
            except (ValueError, OSError) as error:
                raise ValueError(f"V14.5 report generation failed for {summary.name}: {error}") from error
            reports.append(report)
        logger.info("Generated files:")
        for path in [*summaries, *reports]:
            logger.info("  %s", path.name)
        return 0
    except (ValueError, OSError) as error:
        logger.error("%s", error)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
