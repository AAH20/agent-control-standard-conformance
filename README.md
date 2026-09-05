# Agent Control Standard Conformance Kit

[![CI](https://github.com/AAH20/agent-control-standard-conformance/actions/workflows/ci.yml/badge.svg)](https://github.com/AAH20/agent-control-standard-conformance/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://python.org)

**Executable Agent Control Standard (ACS) conformance testing, AI agent runtime security validation, adversarial side-effect verification, OpenTelemetry evidence checks, AgBOM inspection and transparent control economics.**

> **Independent project:** this is an implementation aid and research harness. It is not an OWASP project, official certification, endorsement, or substitute for reviewing the evolving specification. Results apply only to the pinned adapter, test pack, configuration and execution evidence.

## The assurance question

An agent platform can return `DENY` while the prohibited payment still occurs. A schema validator will miss that. This harness evaluates the decision **and the resulting system state**:

```text
Adversarial vector → Agent hook → Guardian policy → allow / deny / modify
                                               ↓
                  side-effect probe + trace evidence + AgBOM inspection
                                               ↓
                       reproducible conformance evidence bundle
```

## Quick start

```bash
python -m acs_conformance.cli run \
  --pack packs/core.json \
  --output report.json \
  --junit report.xml \
  --sarif report.sarif \
  --fail-below L3

python -m acs_conformance.cli economics fixtures/economics.json --output economics.json
```

The bundled refund-agent laboratory executes ten deterministic vectors and reaches `L5` only because it passes functional, adversarial and operational gates, exposes a complete AgBOM, and supplies the economics input. The level is an **independent project convention**, not an official ACS certification level.

## Executable test coverage

| Test area | What is verified |
|---|---|
| Allow | Authorized action reaches the side-effect ledger |
| Deny | Prohibited high-value refund never reaches the ledger |
| Modify | Sensitive value is actually transformed |
| Human approval | Scoped approval changes the decision correctly |
| Replay | Repeated action is denied without a duplicate effect |
| Bypass | Alternate execution path cannot skip policy |
| Identity | Incorrect token audience is rejected |
| Evidence | Trace, actor, hook, policy and rationale are present |
| Performance | Enforcement stays within the declared latency budget |
| Delegation | Cross-agent activity preserves correlation evidence |

## Independent assessment levels

| Level | Required evidence |
|---|---|
| L0 — Declared | Adapter declares runtime hooks |
| L1 — Schema | Test inputs and results are structurally valid |
| L2 — Functional | All functional allow, deny and modify vectors pass |
| L3 — Adversarial | Replay, bypass and identity-abuse vectors also pass |
| L4 — Operational | Telemetry, latency and AgBOM gates pass |
| L5 — Economic | L4 plus an explicit runtime-control cost model |

The runner does not average away a failed prerequisite: one failed vector holds the result below its corresponding level.

## Evidence bundle

Each execution produces:

- Adapter name and version
- Specification target notice
- Per-vector assertions and failure reasons
- Observed enforcement latency
- Side-effect outcome
- Policy, actor, hook and trace evidence
- Dynamic Agent Bill of Materials snapshot
- JUnit and SARIF outputs
- Canonical SHA-256 evidence digest

Cryptographic signing and trusted execution attestation are roadmap features. A digest alone proves consistency, not who executed the assessment.

## Adapter contract

Adapters expose four small operations:

```python
class Adapter:
    name: str
    version: str
    supported_hooks: set[str]

    def reset(self) -> None: ...
    def invoke(self, vector: TestVector) -> InvocationResult: ...
    def agbom(self) -> dict: ...
```

The roadmap prioritizes LangGraph, CrewAI, Microsoft Agent Framework, PydanticAI, OpenAI Agents SDK, Google ADK, FastMCP and A2A. New adapters must run against real observable side effects or explicitly identify simulated boundaries.

## Runtime-control economics

The calculator separates realized value from pipeline capacity:

```text
Cost per action       = (infrastructure + latency cost) / controlled actions
Expected loss reduced = probability × impact × demonstrated effectiveness
Net control benefit   = risk reduction + IR savings + assurance savings
                        + attributable revenue − all control costs
Control ROI           = net control benefit / all control costs
```

Direct revenue and finance-approved contributory attribution may enter net benefit. Capacity-enabled pipeline is reported separately and never treated as booked revenue. See [KPIs and unit economics](docs/KPIS_AND_UNIT_ECONOMICS.md).

## Standards boundary

The project is designed to track, not redefine:

- Agent Control Standard public preview
- OWASP Top 10 for Agentic Applications
- Model Context Protocol authorization requirements
- OpenTelemetry agent observability
- OCSF security-event mapping
- CycloneDX, SPDX and SWID Agent BOM work
- NIST Cyber AI Profile

Every external comparison must pin the ACS commit or release tested. `main` is not a stable conformance target.

## Benchmark design

The planned public benchmark measures:

- Mandatory hook coverage
- Unauthorized side-effect prevention
- Bypass and replay resistance
- Secret-redaction precision and recall
- Trace completeness and reconstruction success
- AgBOM freshness
- P50/P95/P99 enforcement latency
- Cost per 1,000 actions
- Analyst minutes per failed vector

Raw evidence, environment manifests and reproduction commands will accompany scores. See [benchmark methodology](benchmark/METHODOLOGY.md).

## Roadmap

- **v0.1:** executable core pack, refund lab, evidence reports and economics
- **v0.2:** FastMCP and LangGraph adapters; failure-injection pack
- **v0.3:** OpenTelemetry/OCSF validators and dynamic AgBOM diff tests
- **v0.4:** Kubernetes Job, signed evidence and release-policy integration
- **v1.0:** reproducible multi-framework public benchmark

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q acs_conformance tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before adding adapters or publishing comparison results.

## License and trademarks

Apache-2.0. OWASP and other product or standards names belong to their respective owners. References do not imply affiliation or endorsement.
