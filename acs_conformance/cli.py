from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import RefundAgentAdapter
from .economics import calculate
from .exporters import junit, sarif, write_json
from .runner import parse_vectors, run_suite


def main() -> None:
    parser = argparse.ArgumentParser(prog="acs-conformance", description="Independent Agent Control Standard conformance testing")
    subs = parser.add_subparsers(dest="command", required=True)
    run = subs.add_parser("run", help="Run executable conformance vectors")
    run.add_argument("--pack", default="packs/core.json")
    run.add_argument("--adapter", choices=["refund-lab"], default="refund-lab")
    run.add_argument("--output", default="acs-conformance-report.json")
    run.add_argument("--junit")
    run.add_argument("--sarif")
    run.add_argument("--fail-below", choices=["L0", "L1", "L2", "L3", "L4", "L5"], default="L0")
    econ = subs.add_parser("economics", help="Calculate runtime-control unit economics")
    econ.add_argument("inputs")
    econ.add_argument("--output", default="acs-economics.json")
    args = parser.parse_args()
    if args.command == "economics":
        write_json(calculate(json.loads(Path(args.inputs).read_text())), args.output)
        return
    vectors = parse_vectors(json.loads(Path(args.pack).read_text()))
    report = run_suite(RefundAgentAdapter(), vectors, economics=True)
    write_json(report, args.output)
    if args.junit:
        Path(args.junit).write_text(junit(report) + "\n")
    if args.sarif:
        write_json(sarif(report), args.sarif)
    levels = ["L0", "L1", "L2", "L3", "L4", "L5"]
    if levels.index(report["summary"]["conformance_level"]) < levels.index(args.fail_below):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
