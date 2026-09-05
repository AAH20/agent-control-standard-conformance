# KPI and unit-economics contract

Proposed pilot targets are gates, not observed customer results.

## Security effectiveness

| KPI | Formula | Proposed gate | Evidence source |
|---|---|---:|---|
| Unauthorized side-effect prevention | blocked prohibited effects / attempted prohibited effects | 100% for critical actions | Downstream state probe |
| Bypass resistance | blocked bypasses / attempted bypasses | 100% | Adversarial vectors |
| Replay rejection | rejected replays / attempted replays | 100% | Idempotency ledger |
| Modification correctness | exact approved transforms / modification decisions | 100% | Before/after payload digest |
| Evidence completeness | records with mandatory fields / records | ≥99.9% | OTel/OCSF validator |
| Reconstruction success | incidents correctly reconstructed / fixtures | ≥95% | Blind analyst exercise |
| Secret-redaction precision | correct redactions / all redactions | ≥99% | Labeled corpus |
| Secret-redaction recall | secrets redacted / all labeled secrets | 100% for high-impact classes | Labeled corpus |

## Reliability and developer experience

| KPI | Definition | Proposed gate |
|---|---|---:|
| Enforcement availability | successful decisions / eligible decisions | ≥99.99% |
| P99 enforcement latency | P99 added control latency | Workload-specific SLO |
| False-denial rate | safe actions denied / safe actions | <0.1% |
| Evidence-loss rate | expected events absent / expected events | <0.01% |
| Time to first passing run | install start → evidence bundle | <15 minutes |
| Adapter upgrade regression | failed prior vectors after upgrade / prior vectors | 0 critical regressions |

## Economics

| Measure | Formula | Guardrail |
|---|---|---|
| Cost per controlled action | infrastructure + latency cost / actions | Report volume and period |
| Cost per prevented action | total control cost / confirmed unsafe actions blocked | Do not count synthetic blocks |
| Productivity cost | latency cost per millisecond × added latency × actions | Establish workload-specific value |
| Expected loss reduction | annual probability × impact × demonstrated effectiveness | P10/P50/P90 only |
| Revenue-weighted days released | Σ value × days removed / term days | Timing, not created revenue |
| Capacity-enabled pipeline | extra reviews × qualification rate × average value | Never booked as revenue |
| Net control benefit | risk + IR + labor + attributable revenue − cost | Excludes capacity pipeline |

## Measurement protocol

Pin adapter, framework, policy, vector pack and infrastructure versions. Warm up before latency sampling. Publish sample counts and distribution, not just averages. Verify critical side effects at the destination system. Preserve failures and suppressed findings. Finance approves revenue attribution and loaded labor rates.
