import json
import tempfile
import unittest
from pathlib import Path

from acs_conformance.adapters import RefundAgentAdapter
from acs_conformance.economics import calculate
from acs_conformance.exporters import junit, sarif
from acs_conformance.models import TestVector as Vector
from acs_conformance.runner import parse_vectors, run_suite, run_vector

ROOT = Path(__file__).parents[1]


class ConformanceTests(unittest.TestCase):
    def setUp(self):
        self.adapter = RefundAgentAdapter()
        self.vectors = parse_vectors(json.loads((ROOT / "packs/core.json").read_text()))

    def test_pack_has_unique_vectors(self):
        self.assertEqual(len(self.vectors), len({v.id for v in self.vectors}))

    def test_unknown_hook_rejected(self):
        with self.assertRaises(ValueError): parse_vectors({"vectors":[{"id":"x","title":"x","category":"x","hook":"bad","request":{},"expected_verdict":"allow","expected_side_effect":False}]})

    def test_authorized_action_occurs(self):
        result = run_vector(self.adapter, self.vectors[0])
        self.assertTrue(result.passed)
        self.assertEqual(len(self.adapter.ledger), 1)

    def test_denied_action_has_no_side_effect(self):
        result = run_vector(self.adapter, self.vectors[1])
        self.assertTrue(result.passed)
        self.assertEqual(self.adapter.ledger, [])

    def test_modify_changes_request(self):
        result = run_vector(self.adapter, self.vectors[2])
        self.assertTrue(result.checks["modification_applied"])

    def test_replay_is_denied(self):
        result = run_vector(self.adapter, next(v for v in self.vectors if v.id == "ACS-A001"))
        self.assertTrue(result.passed)

    def test_bypass_is_denied(self):
        result = run_vector(self.adapter, next(v for v in self.vectors if v.id == "ACS-A002"))
        self.assertTrue(result.passed)

    def test_audience_mismatch_is_denied(self):
        result = run_vector(self.adapter, next(v for v in self.vectors if v.id == "ACS-A003"))
        self.assertTrue(result.passed)

    def test_missing_evidence_fails(self):
        class Broken(RefundAgentAdapter):
            def invoke(self, vector):
                result = super().invoke(vector); result.evidence.pop("trace_id"); return result
        result = run_vector(Broken(), self.vectors[0])
        self.assertFalse(result.passed)
        self.assertIn("evidence_complete", result.failure_reasons)

    def test_latency_budget_fails(self):
        vector = Vector("X", "slow", "operational", "tool.invoke", {"simulated_latency_ms":100}, "allow", False, 10)
        self.assertFalse(run_vector(self.adapter, vector).passed)

    def test_full_lab_reaches_l5(self):
        report = run_suite(self.adapter, self.vectors, economics=True)
        self.assertEqual(report["summary"]["conformance_level"], "L5")
        self.assertEqual(report["summary"]["pass_rate_pct"], 100)

    def test_digest_is_present(self):
        self.assertEqual(len(run_suite(self.adapter, self.vectors)["evidence_sha256"]), 64)

    def test_junit_contains_all_cases(self):
        output = junit(run_suite(self.adapter, self.vectors))
        self.assertEqual(output.count("<testcase"), len(self.vectors))

    def test_sarif_has_no_results_for_pass(self):
        output = sarif(run_suite(self.adapter, self.vectors))
        self.assertEqual(output["runs"][0]["results"], [])

    def test_economics_excludes_capacity_from_net_benefit(self):
        data = json.loads((ROOT / "fixtures/economics.json").read_text())
        first = calculate(data)
        data["additional_reviews"] = 100000
        second = calculate(data)
        self.assertEqual(first["net_control_benefit_p50"], second["net_control_benefit_p50"])


if __name__ == "__main__": unittest.main()
