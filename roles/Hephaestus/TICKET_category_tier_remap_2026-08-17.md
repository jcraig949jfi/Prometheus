# TICKET — CATEGORY_TIER remap to Canon v2.0 vocabulary

**Filed:** 2026-08-17 by Aporia, under Canon ratification §9(c) (James, "Do it").
**Owner:** Hephaestus (trap battery owner). **Priority:** next forge session; not probe-blocking.

## What

`agents/hephaestus/src/test_harness.py` maps ~90 trap categories to R1–R6 using the **2026-05-15
tier semantics** (cited at `test_harness.py:460` — e.g. R4 = search/planning, R5 =
causal/counterfactual). Canon v2.0 (`aporia/doctrine/reasoning_ladder.md`) makes the 05-27
testable-ladder semantics the only untagged meaning of an R-number (R4 = representation shift,
R5 = invariant detection).

## Required

1. Either **remap** CATEGORY_TIER to canonical rung semantics, or **tag** every emitted tier as
   `R<n>@trap` — remap preferred, tagging acceptable if remap is ambiguous for some categories.
2. Restate the headline claim wherever quoted: "+11pp R3 / +32pp R4" → "+11pp/+32pp on the trap
   battery's internal categories (`R3@trap`, `R4@trap`), E0 pending oracle re-measurement."
   The oracle re-measurement itself is already owed under L1 (probe lane) — this ticket does not
   duplicate it, only the labeling.
3. One-line note in `agents/hephaestus/STATUS.md` when done.

## Also flagged (not this ticket's scope)

`agents/icarus/ladder.py` still carries frozen v0.1 vocabulary while `tier_oracle.py` grades
against the canonical ruler — Icarus is dormant, so a banner comment suffices when it revives.
Erebos plugin `reasoning_tier` declarations are annotated against 05-15 semantics — dormant since
06-03, same treatment on revival.
