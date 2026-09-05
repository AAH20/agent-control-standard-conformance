from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def write_json(report: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(report, indent=2) + "\n")


def junit(report: dict[str, Any]) -> str:
    summary = report["summary"]
    suite = ET.Element("testsuite", name="acs-conformance", tests=str(summary["tests"]), failures=str(summary["failed"]))
    for result in report["results"]:
        case = ET.SubElement(suite, "testcase", name=result["vector_id"], classname="acs.conformance", time=str(result["latency_ms"] / 1000))
        if not result["passed"]:
            failure = ET.SubElement(case, "failure", message=", ".join(result["failure_reasons"]))
            failure.text = json.dumps(result["checks"], sort_keys=True)
    return ET.tostring(suite, encoding="unicode")


def sarif(report: dict[str, Any]) -> dict[str, Any]:
    failed = [r for r in report["results"] if not r["passed"]]
    return {
        "version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {"driver": {"name": "ACS Conformance Kit", "informationUri": "https://github.com/AAH20/agent-control-standard-conformance"}},
            "results": [{"ruleId": r["vector_id"], "level": "error", "message": {"text": f'{r["title"]}: {", ".join(r["failure_reasons"])}'}} for r in failed],
        }],
    }
