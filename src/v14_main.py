"""V14.4 production entry point, with an explicit developer-summary mode."""
import argparse
import logging
from pathlib import Path
from .main import choose_packages_gui, classify_inputs, run_pipeline
from .v14_report import TEMPLATE_SHA256, build_v14_report


DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "Post-MIC limit_EV3_20260911.xlsx"

def main(argv=None):
    parser = argparse.ArgumentParser(description="Build V14.4 reports directly from FATP archives.")
    parser.add_argument("packages", nargs="*", type=Path, help="MIC/PREMIC archives and optional RawData archive")
    parser.add_argument("--mic", type=Path); parser.add_argument("--premic", type=Path); parser.add_argument("--rawdata", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Developer override; production uses the packaged master")
    parser.add_argument("--summary", nargs="+", type=Path, help="Developer-only normalized V13.6 summaries")
    parser.add_argument("--output", type=Path, help="Required with --summary")
    parser.add_argument("--skip-template-hash-check", action="store_true", help="Synthetic/developer templates only")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        if args.summary:
            if not args.output:
                parser.error("--output is required with --summary")
            build_v14_report(args.template, args.summary, args.output, verify_hash=not args.skip_template_hash_check)
            return 0
        positional = args.packages or ([] if any((args.mic, args.premic, args.rawdata)) else choose_packages_gui())
        pmic, ppremic, prawdata = classify_inputs(positional)
        summaries = run_pipeline(args.mic or pmic, args.premic or ppremic, args.rawdata or prawdata, args.output_dir)
        for summary in summaries:
            suffix = summary.stem.removeprefix("summary_")
            build_v14_report(args.template, [summary], args.output_dir / f"report_{suffix}.xlsx")
        return 0
    except (ValueError, OSError) as error:
        logging.getLogger("aruba_fatp_v14").error("%s", error)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
