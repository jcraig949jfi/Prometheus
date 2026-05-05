---
name: PATTERN_BASE_RATE_NEGLECT
type: pattern
version: 1
version_timestamp: 2026-04-26T00:00:00Z
immutable: true
status: active
proposed_by: ChatGPT (frontier review 2026-04-26, §8.5)
canonical_example: "Vibe-maths article (Sci Am 2026): 'Amateur with ChatGPT solved Erdős primitive sets' — failed to report how many Erdős problems were attempted before the success."
references:
  - stoa/discussions/2026-04-26-frontier-review/chatgpt.md
  - stoa/discussions/2026-04-26-aporia-on-amateur-vibe-maths-erdos-result.md
veto_authority: Kairos
---

## Definition

Any cross-region correlation, anomaly, or success claim must report its **base rate** across the full corpus and within each matched stratum. The denominator is mandatory; absence triggers veto.

## Trigger

A claim of the form "X is statistically significant" or "X is a discovered structure" without:
- Number of total trials / objects searched
- Per-stratum denominator across all matched-null strata
- Survival rate (passes / total trials), not just count of passes

## Why this exists

PATTERN_SELECTION_BIAS@v1 catches obvious cherry-picking but does not force *explicit* denominator accounting across all strata. PATTERN_30@v1 catches uncontrolled correlation but does not force base-rate disclosure. The vibe-maths article is the canonical failure mode: a single Erdős problem was solved via ChatGPT prompting, but the article never reported how many *other* Erdős problems were attempted before the success. Without that denominator, the success rate is undefined and the claim collapses to anecdote.

In Prometheus's P21 (curated-corpus empirical sweep) operations, this is the dominant false-positive risk: stratify a corpus, find an "interesting" stratum, report the anomaly without the base rate of similar anomalies in the other strata.

## How to apply

- Every P21 sweep result must be filed with `total_trials`, `per_stratum_denominators`, and `survival_rate` fields. No exceptions.
- Every cross-region operator-transport claim (P19) must report how many other (operator, region) pairs were tested and what their hit rate was.
- Every battery-survival claim must report the base-rate prior of similar findings surviving the same battery.
- Kairos vetoes any candidate finding lacking these fields. Re-submission requires the missing denominators.

## Relation to other patterns

- **PATTERN_SELECTION_BIAS@v1** catches multiple-comparison cherry-picking; this catches *missing denominator* even when only one comparison was made.
- **PATTERN_30@v1** catches uncontrolled correlation; this is upstream — the denominator must exist before the correlation can be controlled.
- **PATTERN_NARRATIVE_INFLATION@v1** catches load-bearing-step elision; this catches denominator elision specifically.

## Calibration

The vibe-maths article (Sci Am 2026) is the canonical anchor. Any future article-style result narrating "AI solved problem X" without denominator triggers this pattern automatically. Synthetic anchors: take any known-true-positive from `aporia/calibration/battery_calibration.jsonl`, strip the denominator, and the claim should be killed.
