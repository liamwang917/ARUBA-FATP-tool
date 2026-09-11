"""Developer V14.4 template-report command line entry point."""
import argparse
import logging
from pathlib import Path
from .v14_report import build_v14_report

def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a V14.4 report from V13.6 summaries.")
    parser.add_argument("template", type=Path)
    parser.add_argument("summaries", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--skip-template-hash-check", action="store_true", help="Synthetic/developer templates only")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        build_v14_report(args.template, args.summaries, args.output, verify_hash=not args.skip_template_hash_check)
        return 0
    except (ValueError, OSError) as error:
        logging.getLogger("aruba_fatp_v14").error("%s", error)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
