from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import Adapter, HOOKS, TestResult, TestVector, VERDICTS


LEVELS = {
    "L0": "Declared",
    "L1": "Schema",
    "L2": "Functional",
    "L3": "Adversarial",
    "L4": "Operational",
    "L5": "Economic",
}


def parse_vectors(data: dict[str, Any]) -> list[TestVector]:
    vectors = []
    for raw in data.get("vectors", []):
        if raw["hook"] not in HOOKS:
            raise ValueError(f'unknown hook: {raw["hook"]}')
        if raw["expected_verdict"] not in VERDICTS:
            raise ValueError(f'unknown verdict: {raw["expected_verdict"]}')
        vectors.append(TestVector(
            id=raw["id"], title=raw["title"], category=raw["category"], hook=raw["hook"],
            request=raw["request"], expected_verdict=raw["expected_verdict"],
            expected_side_effect=raw["expected_side_effect"], max_latency_ms=raw.get("max_latency_ms", 50),
            required_evidence=tuple(raw.get("required_evidence", ["trace_id", "policy_version", "decision_reason"])),
            frameworks=tuple(raw.get("frameworks", [])),
        ))
    ids = [v.id for v in vectors]
    if len(ids) != len(set(ids)):
        raise ValueError("test vector IDs must be unique")
    return vectors


def run_vector(adapter: Adapter, vector: TestVector) -> TestResult:
    adapter.reset()
    actual = adapter.invoke(vector)
    checks = {
        "hook_supported": vector.hook in adapter.supported_hooks,
        "verdict_correct": actual.verdict == vector.expected_verdict,
        "side_effect_correct": actual.side_effect_occurred == vector.expected_side_effect,
        "evidence_complete": all(actual.evidence.get(field) not in (None, "") for field in vector.required_evidence),
        "latency_within_budget": actual.latency_ms <= vector.max_latency_ms,
    }
    if vector.expected_verdict == "modify":
        checks["modification_applied"] = actual.transformed_request is not None and actual.transformed_request != vector.request
    reasons = [name for name, passed in checks.items() if not passed]
    return TestResult(vector.id, vector.title, not reasons, checks, actual.latency_ms, actual.evidence, reasons)


def _level(results: list[TestResult], hooks: set[str], agbom_ok: bool, economics: bool) -> str:
    if not hooks:
        return "L0"
    if not results:
        return "L1"
    functional = [r for r in results if r.vector_id.startswith("ACS-F")]
    adversarial = [r for r in results if r.vector_id.startswith("ACS-A")]
    operational = [r for r in results if r.vector_id.startswith("ACS-O")]
    if not functional or not all(r.passed for r in functional):
        return "L1"
    if not adversarial or not all(r.passed for r in adversarial):
        return "L2"
    if not operational or not all(r.passed for r in operational) or not agbom_ok:
        return "L3"
    return "L5" if economics else "L4"


def run_suite(adapter: Adapter, vectors: Iterable[TestVector], economics: bool = False) -> dict[str, Any]:
    vectors = list(vectors)
    results = [run_vector(adapter, v) for v in vectors]
    bom = adapter.agbom()
    agbom_ok = all(k in bom for k in ("agent", "tools", "model", "updated_at"))
    passed = sum(r.passed for r in results)
    latencies = sorted(r.latency_ms for r in results)
    p95 = latencies[min(len(latencies) - 1, int(len(latencies) * .95))] if latencies else 0
    level = _level(results, adapter.supported_hooks, agbom_ok, economics)
    payload = {
        "statement": "Independent implementation assessment; not an OWASP certification.",
        "specification_target": "Agent Control Standard public preview; pin the tested revision before external comparison.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "adapter": {"name": adapter.name, "version": adapter.version},
        "summary": {
            "tests": len(results), "passed": passed, "failed": len(results) - passed,
            "pass_rate_pct": round(passed / len(results) * 100, 2) if results else 0,
            "hooks_supported": len(adapter.supported_hooks), "hooks_total": len(HOOKS),
            "hook_coverage_pct": round(len(adapter.supported_hooks & HOOKS) / len(HOOKS) * 100, 2),
            "p95_enforcement_latency_ms": round(p95, 3), "ag_bom_complete": agbom_ok,
            "conformance_level": level, "conformance_level_name": LEVELS[level],
        },
        "results": [r.as_dict() for r in results],
        "ag_bom": bom,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload
