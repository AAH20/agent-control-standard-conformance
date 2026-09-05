# Public benchmark methodology

## Principles

Results must be reproducible, version-pinned, side-effect aware and comparable only within equivalent deployment classes. Vendors receive a correction window for factual configuration errors, but cannot suppress valid failures.

## Required publication artifacts

- Framework, adapter, policy and commit identifiers
- Infrastructure and model manifest
- Full test-vector pack and ground truth
- Raw JUnit, SARIF and JSON output
- Downstream side-effect evidence
- Latency sample count and distribution
- Known exclusions and conflicts of interest
- Reproduction command and evidence digest

## Scorecard

Security gates are pass/fail. Performance metrics are reported independently and never compensate for a prohibited side effect. An overall percentage may summarize coverage, but failed critical controls remain prominent.

No product may be labeled “ACS certified” by this project. Use “tested with Agent Control Standard Conformance Kit, version X, against pack Y.”
