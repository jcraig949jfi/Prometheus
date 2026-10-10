# FINAL LABEL RULES (DATED AMENDMENT, WRITTEN BEFORE THE SYNTHESIS)

C-015, 2026-10-10. Written in response to independent review v2 (reviews/INDEPENDENT_REVIEW_RESULTS_v2_ADDENDUM.md,
process MAJOR): four of the eight final fields had no frozen definition. This fixes the mapping BEFORE the synthesis
states any of them.

**Disclosure.** All E1 / E2 / E3-KP / E3-ID / AR-1 outcomes are already known when this is written. The rules below
therefore only map gate states to labels. They contain no outcome threshold that could be tuned.

## Rule G (gated fields)
**A field's value is INSTRUMENT_UNVALIDATED when the experiment that defines it did not run because a frozen gate was
not met.**
- It is never NO: a field that was not run is not a tested negative (directive: "Any field may be YES, NO,
  INCONCLUSIVE, or INSTRUMENT_UNVALIDATED as appropriate").
- The rendering names the gate and the first failing link upstream.

| Field | Defining experiment (EXPERIMENT_PLAN s2) | Gate | State | Value |
|---|---|---|---|---|
| COMPOSITIONAL_DISCOVERY | E3 2x2 lifetime screen. An organism discovers a stone autonomously AND uses it to discover a dependent mechanism, with an ablation-verified dependency | TFS1_INSTRUMENT_QUALIFIED = YES AND E2 complete (A1-B.11) | not met (KP NO) | INSTRUMENT_UNVALIDATED |
| DEVELOPMENTAL_INHERITANCE | E4 consolidated library -> fresh descendant, with a common-residual acquisition contrast | E3 passes; E4 barred on these worlds (E1 NO, R5 = 0) | not met | INSTRUMENT_UNVALIDATED |
| SECOND_ORDER_ACQUISITION | E4 / E3 dependency test: acquisition made possible only by an acquired mechanism | as above | not met | INSTRUMENT_UNVALIDATED |
| ECONOMIC_ADVANTAGE | E5 scaling 1x / 4x / 16x on QUALIFIED treatments, with the certified-mechanism rate rising | qualified treatment exists (plan s2: "Only for qualified treatments") | not met (no treatment qualified; the E2 4x skip is recorded as a declared deviation) | INSTRUMENT_UNVALIDATED |

## Fields already defined by frozen rules (restated, unchanged)

| Field | Value | Frozen basis |
|---|---|---|
| WORLD_DEMAND_QUALIFIED | NO | E1_ADDENDUM_D |
| REACHABILITY_ATLAS_COMPLETE | YES | A1-B.9. Rendered as "an atlas of the composition step given supplied foundry stones on foundry-selected families" |
| TFS1_INSTRUMENT_QUALIFIED | NO, so TFS1_REACHABILITY_INSTRUMENT = FAIL | A1-A, A3 |
| FRONTIER_ARCHIVE_EFFECT | INCONCLUSIVE (INCONCLUSIVE_CENSORED) | A1-B.6, A2.3. Cause: descriptor unvalidated on 10 / 15 families. Direction in both informative clusters: archive arm BELOW both comparators (descriptive) |

## Declared deviation: the E2 4x escalation
The prereg s B trigger (FRONTIER INCONCLUSIVE) fired, and 4x was NOT run. Reasons:
1. More budget cannot resolve the descriptor censoring (10 / 15 families unvalidated; 2 / 5 clusters).
2. The plan's scaling rule (s2 / E5) applies only to qualified treatments, and none qualified.

The earlier ledger reason ("cannot change a label") is withdrawn as inaccurate: the descriptive co-labels could have
changed.
