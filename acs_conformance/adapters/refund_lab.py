from __future__ import annotations

from datetime import datetime, timezone

from ..models import HOOKS, InvocationResult, TestVector


class RefundAgentAdapter:
    """Deterministic lab adapter with a real in-memory side-effect ledger."""

    name = "refund-agent-lab"
    version = "0.1.0"
    supported_hooks = set(HOOKS)

    def __init__(self) -> None:
        self.ledger: list[dict] = []
        self.capabilities = {"refund.issue", "customer.read"}

    def reset(self) -> None:
        self.ledger.clear()

    def invoke(self, vector: TestVector) -> InvocationResult:
        request = dict(vector.request)
        policy = "refund-policy@1.0.0"
        verdict = "allow"
        transformed = None
        reason = "request within policy"
        amount = float(request.get("amount", 0))
        if request.get("replayed") or request.get("bypass_attempt"):
            verdict, reason = "deny", "replay or alternate-path bypass rejected"
        elif request.get("identity_audience") not in (None, "payments-api"):
            verdict, reason = "deny", "credential audience mismatch"
        elif request.get("contains_secret"):
            verdict, reason = "modify", "sensitive field redacted"
            transformed = {k: ("[REDACTED]" if k == "secret" else v) for k, v in request.items()}
        elif amount > 1000 and not request.get("human_approved"):
            verdict, reason = "deny", "refund exceeds autonomous transaction limit"

        side_effect = verdict == "allow" and request.get("operation") == "refund.issue"
        if side_effect:
            self.ledger.append({"amount": amount, "customer": request.get("customer")})
        evidence = {
            "trace_id": f"trace-{vector.id.lower()}", "policy_version": policy,
            "decision_reason": reason, "actor": "refund-agent", "hook": vector.hook,
            "side_effect_count": len(self.ledger), "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return InvocationResult(verdict, side_effect, evidence, float(request.get("simulated_latency_ms", 4.2)), transformed)

    def agbom(self) -> dict:
        return {
            "agent": "refund-agent", "model": "fixture-model@1", "tools": sorted(self.capabilities),
            "mcp_servers": ["payments-mcp"], "updated_at": datetime.now(timezone.utc).isoformat(),
        }
