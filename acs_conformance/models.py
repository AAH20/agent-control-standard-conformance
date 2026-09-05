from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Protocol


HOOKS = {
    "agent.input", "agent.output", "tool.select", "tool.invoke", "tool.response",
    "memory.read", "memory.write", "code.execute", "plan.execute", "agent.delegate",
    "identity.use", "lifecycle.change", "human.approval",
}
VERDICTS = {"allow", "deny", "modify"}


@dataclass(frozen=True)
class TestVector:
    id: str
    title: str
    category: str
    hook: str
    request: dict[str, Any]
    expected_verdict: str
    expected_side_effect: bool
    max_latency_ms: float = 50.0
    required_evidence: tuple[str, ...] = ("trace_id", "policy_version", "decision_reason")
    frameworks: tuple[str, ...] = ()


@dataclass
class InvocationResult:
    verdict: str
    side_effect_occurred: bool
    evidence: dict[str, Any]
    latency_ms: float
    transformed_request: dict[str, Any] | None = None


@dataclass
class TestResult:
    vector_id: str
    title: str
    passed: bool
    checks: dict[str, bool]
    latency_ms: float
    evidence: dict[str, Any] = field(default_factory=dict)
    failure_reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class Adapter(Protocol):
    name: str
    version: str
    supported_hooks: set[str]

    def reset(self) -> None: ...
    def invoke(self, vector: TestVector) -> InvocationResult: ...
    def agbom(self) -> dict[str, Any]: ...
