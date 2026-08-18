# Seven Proposed PATTERN Preconditions for Kairos Catalog

**Date:** 2026-04-22
**Source:** Aporia, during the F011 characterization session (15 structural reframes)
**Status:** Proposed. Each pattern emerged from a cross-check that overturned a prior claim in today's work.

## Purpose

Kairos maintains a catalog of PATTERN preconditions (e.g. PATTERN_30 rearrangement, PATTERN_20 mixture artifact, PATTERN_BSD_TAUTOLOGY) that act as filters before an F-cell is promoted or demoted in the tensor. Each pattern formalizes a specific methodological trap that has been seen empirically.

During the session 2026-04-22 on F011 (GUE deficit → universality-triangle paper), seven new methodological traps surfaced. Each is proposed for formalization.

---

## 1. PATTERN_NULL_CONSTRAINT_MISMATCH

**Failure mode:** A statistic is compared to a null that has DIFFERENT sufficient-statistic constraints than the observation, producing spurious resolution-or-kill verdicts.

**Canonical example:** EC rank-0 gap1 variance (normalized by per-curve local-4-gap mean) compared to "pure GUE" at global normalization. The observation uses a LOCAL constraint; the null does not. Result: apparent 14% deficit was interpreted as finite-N universality correction, then retracted when matched-local null gave the opposite sign.

**Precondition:** Before promoting or killing an F-cell, verify that the null's own distribution has the SAME sufficient-statistic constraints as the observation. If observation uses local-k-gap normalization, null must too.

**Diagnosis test:** Does the null's own distribution show constraint-shape? If yes, matched-constraint null is required.

---

## 2. PATTERN_KILL_UNDER_CONSTRAINED

**Failure mode:** A kill verdict is asserted from a single test without checking (a) alternative null formulations, (b) cross-dataset reproduction, (c) gradient-AND-absolute-level consistency.

**Canonical example:** Ergon's first "mechanism (a) conductor-memory kill" based on 200K Q-decile analysis was overturned by Charon's wider log(N) span on BSD-1646 showing -2.19%/log(N) slope. The single test mispecified the kill conditions.

**Precondition:** No F-cell flipped to negative without 2/3 independent tests agreeing across (alt-null, cross-dataset, gradient-AND-absolute) axes.

**Operational test:** If only 1/3 tests have been run, KILL status is PROVISIONAL. Promote to DURABLE_KILL only after 2+ tests concur.

---

## 3. PATTERN_PREDICTION_LEVEL_MISMATCH

**Failure mode:** Pre-registered predictions are stated at the level of an estimator (regression coefficient) whose value depends on model parameterization, rather than at the level of a measurement (cell value, binary sign test). Changing the regression spec changes the coefficient, making pre-registration unfalsifiable.

**Canonical example:** Aporia's pre-registered V-GAMMA-SIXTH-ROOTS predictions were stated as "K=-3 × nonmax interaction coefficient gap1 ≈ +10pp, gap4 ≈ -20pp." Ergon's regression found +21pp and +3.9pp. Direction correct at shape-taxonomy level but magnitudes off because coefficients absorbed baseline patterns first.

**Precondition:** Pre-registered predictions must be at measurement level (cell value, binary direction test, ordinal correlation sign) not at regression-coefficient level.

**Better form:** "Sign of gap4-gap1 gradient in cell type X is NEGATIVE; in cell type Y is POSITIVE." Clean binary test, spec-invariant.

---

## 4. PATTERN_SELECTION_BIAS

**Failure mode:** A finding from a curated subset (BSD-verified curves, hand-picked extremes, stratified samples) can differ in SIGN from the finding in a random sample. Curated subsets concentrate in specific regimes of the underlying distribution.

**Canonical example:** BSD-1646 (curated rank-0 curves selected for Tier-0 BSD verification) showed nbp Spearman = +0.03 at gap1, while Ergon's random 150K LMFDB sample showed +1.000. The nbp-gap signal exists in the random population but is washed out in the curated subset. At nbp=1, BSD-1646 (n=10) showed +51% deficit; random (n=211) showed -5% — OPPOSITE SIGN.

**Precondition:** Before promoting a finding from curated data, cross-check on random sample of comparable size. If disagreement, state scope explicitly ("in random sampling, ...").

**Test format:** Each F-cell carries a "random cross-check status" field: agrees / disagrees / random-untested.

---

## 5. PATTERN_NORMALIZATION_SIGN_FLIP

**Failure mode:** A statistic can FLIP SIGN between two different normalizations that both look reasonable. The observation is the same; the sign-of-deviation-from-null depends on the normalization choice.

**Canonical example:** Rank-0 EC gap1 under 4-gap normalization showed +19% deficit vs matched null. Under 24-gap normalization (Ergon's Seed 2), the SAME DATA showed -7% excess. The "gap1 compression" we characterized under 4-gap was actually edge EXCESS getting constraint-transferred into an apparent bulk deficit within a 4-gap window.

**Precondition:** Test invariance under at least 2 different normalizations. If sign flips, frame the statistic as "result depends on normalization choice" rather than "the result is X."

**Extension:** If a TRUE signal exists, it should be detectable under MULTIPLE normalizations (perhaps with different magnitudes but same sign). Sign-flip statistics are frame-dependent phenomena.

---

## 6. PATTERN_LITERATURE_REFRAME

**Failure mode:** An "unexplained" void is called for a phenomenon that is actually predicted by existing theory under the correct null. The void-label is premature because the field-correct universality class hasn't been compared to.

**Canonical example:** The April-16 "14% GUE deficit" void for EC rank-0 L-functions. Under GUE null (Katz-Sarnak WRONG universality class for rank-0 EC), the observation looked like a mystery. Charon's literature check identified EC rank-0 as O+(2N) class (Iwaniec-Luo-Sarnak 2000, Young 2005). Part of the original "deficit" was explained by Katz-Sarnak edge repulsion; the bulk deviation remained as a genuine finding.

**Precondition:** Before promoting a "void" label, check whether the observation is predicted by existing theory under the family-correct universality class. "GUE mismatch" may be "O+(2N) match" if the correct class is substituted.

**Operational:** Every void entry carries a "family-correct universality checked?" flag. If null, resolve before void-status is durable.

---

## 7. PATTERN_MEASUREMENT_CHANNEL

**Failure mode:** Different RMT statistics (1-level density vs k-gap variance, local vs global normalization) expose different symmetry-class features. Using the WRONG statistic for the RIGHT question gives null results that look like "no structure" when structure lives in a different channel.

**Canonical example:** Our 24-gap normalization work on EC rank-0 vs rank-1 showed near-identical signatures (gap1-gap4 patterns differ by <5pp). Under 1-level density with unfolded z_1, the same curves differed by +249 z-score (ratio 1.72, matching Katz-Sarnak theory). Spacings are asymptotically universal across classes; 1-level density is symmetry-class-specific. The rank distinction lives in one channel, not both.

**Precondition:** For each question posed to the tensor, specify which measurement channel the answer lives in. "Rank distinction" lives in 1-level density; "bulk universality" lives in spacings. Don't use one to test the other.

**Extension:** F-axis features should be tagged with which measurement channel they operate in. Cross-channel tests are a separate class of F-cell.

---

## Integration Recommendation

Kairos catalog expansion with these seven patterns would formalize the session's methodological lessons. Each pattern has a clean canonical example from today's work.

Proposed file layout:
- `kairos/patterns/001_pattern_30_rearrangement.md` (existing)
- `kairos/patterns/002_pattern_20_mixture.md` (existing)
- `kairos/patterns/003_pattern_null_constraint_mismatch.md` (new)
- `kairos/patterns/004_pattern_kill_under_constrained.md` (new)
- `kairos/patterns/005_pattern_prediction_level_mismatch.md` (new)
- `kairos/patterns/006_pattern_selection_bias.md` (new)
- `kairos/patterns/007_pattern_normalization_sign_flip.md` (new)
- `kairos/patterns/008_pattern_literature_reframe.md` (new)
- `kairos/patterns/009_pattern_measurement_channel.md` (new)

Each canonical example is archived in Aporia's session journal `roles/Aporia/SESSION_JOURNAL_20260422.md` and in Charon's `charon/CHARON_SESSION_2026-04-22.md` + Ergon's `roles/Ergon/SESSION_JOURNAL_20260422.md`.

---

## Meta-Observation

These 7 patterns emerged from 15 structural reframes over ~7 hours of continuous work. Each reframe was triggered by a specific cross-check that revealed a methodological trap. The fact that patterns keep emerging at this rate suggests there are more methodological traps than the prior Kairos catalog captures. The void-detection + cross-check + consensus loop is EFFECTIVE at surfacing these traps.

Future sessions should:
1. Front-load pattern checks (use the patterns above as preconditions BEFORE running a new test).
2. Document additional patterns as they emerge.
3. Periodically cross-check Kairos catalog completeness against session artifacts.

---

*Drafted by Aporia, 2026-04-22, during F011 session stopping point. Routed to Kairos when online.*
