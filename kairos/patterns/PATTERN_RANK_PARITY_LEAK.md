---
name: PATTERN_RANK_PARITY_LEAK
type: pattern
version: 1
version_timestamp: 2026-04-26T00:00:00Z
immutable: true
status: active
proposed_by: Claude-fresh #1 (frontier review 2026-04-26, §8.5)
canonical_example: "F011 +46-51% bulk deficit at k=24 across non-CM EC, CM EC, and G2C with USp(4) — three populations have systematically different rank-distribution profiles (CM curves over-represent rank 0; G2C populations skew differently from elliptic). The audit trail does not state whether the three were rank-parity-matched."
references:
  - stoa/discussions/2026-04-26-frontier-review/claude-fresh-1.md
  - F011 (canonical finding under retroactive audit)
veto_authority: Kairos
paired_operator: OPERATOR_RANK_PARITY_NULL_CONTROL (Techne queue REQ-030)
---

## Definition

Any cross-region BSD-adjacent finding (i.e., any finding involving objects with an analytic rank or rank-parity invariant) must demonstrate **rank-parity-matched null control** across the populations being compared. Absence of explicit rank-parity matching audit triggers veto.

## Trigger

A claim of the form "structure X appears across populations P_1, ..., P_n" where:
- The populations have natural rank or rank-parity invariants (EC, modular forms, abelian varieties, etc.), AND
- The audit trail does not include the rank-parity distribution of each population, AND
- The audit trail does not document a matched-rank-parity null comparison

The pattern fires whenever any of the three is missing.

## Why this exists

NULL_BSWCD@v2 preserves conductor-decile marginals — that is its specification, and it does so well. But conductor-decile is not rank-parity. Two populations with identical conductor distributions can have radically different rank-parity distributions. CM elliptic curves over-represent rank 0; non-CM elliptic curves have a Bhargava-Shankar-style rank-frequency tail; G2C abelian surface populations have yet another rank-frequency profile driven by Chow-Heegner machinery.

When a "universal" cross-region finding holds at the bulk level across three such populations, two failure modes are possible:
1. The finding is truly universal at the operator level — rank-parity differences are irrelevant because the operator factors through them.
2. The finding is a *rank-parity weighted average* — the three populations agree on the bulk because the rank-parity distribution dominates the weighting, not because the underlying mathematics is universal.

PATTERN_30 (correlation-under-control) does not catch this because the stratum is the symmetry class, not the rank-parity. PATTERN_NULL_CONSTRAINT_MISMATCH does not catch it because root-number / rank-parity is not part of NULL_BSWCD's current spec. PATTERN_CONDUCTOR_CONFOUND catches conductor pooling but not rank-parity pooling.

This pattern is the operator-named enforcement that closes the rank-parity gap. F011 is the canonical retroactive audit target — the existing finding deserves a re-test with rank-parity control to determine which of the two failure modes applies.

## How to apply

- Every cross-region BSD-adjacent claim must include a `rank_parity_audit` field with:
  - Rank-parity distribution of each population (counts at rank 0, 1, 2, ...)
  - Pairwise statistical comparison of rank-parity distributions across populations
  - Matched-rank-parity null comparison: if the original finding controlled at level X, re-do at level (X, rank-parity)
  - Effect size of the finding within each rank-parity stratum, not just pooled
- Every operator transport (P19) between regions with rank invariants must apply the operator within rank-parity strata before claiming cross-region survival.
- Every TT bond-rank measurement on cross-region splices involving BSD-class objects must use rank-parity-flattened tensors.
- Kairos vetoes any candidate finding without rank-parity audit. F011 is grandfathered pending its own retroactive audit, but no future BSD-adjacent finding promotes without the audit.

## Relation to other patterns

- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT@v1** catches missing prime detrending; this catches missing rank-parity matching. Both are pre-comparison preprocessing patterns.
- **PATTERN_CONDUCTOR_CONFOUND@v1** catches conductor pooling; this catches rank-parity pooling. They are siblings — different gravitational wells, both must be addressed.
- **PATTERN_30@v1** catches uncontrolled correlation by stratum; this is one specific kind of stratum (rank-parity) that PATTERN_30 does not name explicitly.
- **TAIL_VS_BULK_DECOMPOSITION** (Claude-fresh #2 proposal, REQ-031) is complementary: TAIL_VS_BULK separates spectral regions; this separates population strata. Both close orthogonal F011 audit gaps.

## Calibration

The retroactive F011 audit is the canonical calibration target. The audit either:
- Confirms F011 with rank-parity control intact → finding promotes from "canonical" to "audit-passed canonical"
- Reveals that the +46-51% deficit is rank-parity-weighted → finding demoted from universal to rank-parity-conditional, with the conditional form becoming the new claim
- Reveals a stronger rank-stratified signal → finding refines into multiple sub-findings stratified by rank

All three outcomes are productive. The substrate cannot decide which is true without the audit, and the audit cannot run without this pattern naming the requirement.
