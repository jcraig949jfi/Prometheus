# G04 Survivor-Tightening Generator — Research Notes

**Date:** 2026-05-27 (ITER-3 prep, authored ITER-2)
**Status:** Iteration-3 implementation target. Tier B per spec
(charon-state: A-MVP via string substitution).
**Cousin:** G14 Relation-Strengthening (predicate-strengthening);
G04 focuses on QUANTITATIVE BOUNDS (epsilon-tightening).

---

## Spec recap

- **Mechanism:** Inverse of G03. Turn vague correlations into
  load-bearing, brittle structures until they break.
- **Input:** PROMOTED claim with high variance / fuzziness in its
  battery sub-tests.
- **Transformation:** Inject strict bounding constants OR additional
  filters. `correlation > 0` → `correlation > 0.9` → `correlation
  > 0.95 AND variance bounded by ε`.
- **Expected Kill Pattern:** `strict_threshold_violation` (the
  tightened constraint snaps at some object the original claim
  covered).
- **Loader Feasibility:** Tier A-MVP via string substitution +
  threshold-injection; Tier B for proper parameter binding.

---

## Reasoning Ladder mapping

- **Primary R6** (self-correction via adversarial bound search).
- **Secondary R3** (abstraction: tightened form is a refined
  abstraction).

---

## Adjacent fields

- Adversarial ML boundary attacks (FGSM, PGD) — analog: find the
  edge example that breaks a tightened claim.
- Property-based testing minimization — Hypothesis's shrinking
  finds minimal failing examples.
- Statistical equivalence testing (TOST, F16) — the formal
  inverse: how tight can the bound be while still showing
  equivalence?
- Concentration inequalities (Hoeffding, Bernstein) — give the
  tightness budget.

---

## Simple test claims (MVP)

1. Input: Pollux PROMOTED with `correlation = 0.85` claim.
   Tighten: `correlation > 0.85` → `correlation > 0.90`.
   Output: "Pollux pair survives at the stricter 0.90 threshold."
   Expected: kill — Pollux likely fails at 0.90 for some pairs;
   shows the exact boundary.

2. Input: Stygian UNVERIFIED with F18 STABLE sub-test.
   Tighten: add additional filter "AND subset bootstrap variance <
   0.05".
   Output: "F18 stability survives even under tighter bootstrap
   variance bound."
   Expected: depends on the data.

---

## Frontier questions

```
A research swarm wants a generator that takes a survived claim and
emits tightened versions (correlation > 0 becomes correlation >
0.9, etc.) until the claim breaks. Goal: find the maximal-true
tightness.

Q1. Adversarial ML literature has formal frameworks for boundary
    attacks. Which of them transfer most directly to mathematical
    claim tightening?
Q2. Hypothesis library's shrinking and our G04 tightening look
    mirror-symmetric. Is there a unified primitive that does both?
Q3. How does G04 differ from G14 Relation-Strengthening? In
    practice they will fire on overlapping claims; is the right
    answer to merge them, run them in parallel, or have them
    consume strictly different parent kinds?
Q4. Concentration inequalities (Hoeffding etc.) give a-priori
    tightness budgets. Should G04 consult these to derive
    candidate tightness levels rather than walking a fixed table?
Q5. Pythia: are there published systems doing automatic claim-
    tightening as a hypothesis-mining primitive?
```

---

## TDD test list (sketch)

1. `test_g04_not_applicable_without_promoted_inputs`
2. `test_g04_picks_max_tightening_below_break_point`
3. `test_g04_six_field_spec`
4. `test_g04_expected_kill_pattern`
5. `test_g04_does_not_loosen_an_already_loose_bound`
6. `test_g04_metadata`

---

## Implementation sketch

```python
class SurvivorTighteningGenerator:
    id = "g04_survivor_tightening"
    name = "Survivor Tightening"
    spec_phase = 1
    feasibility_tier = "B"
    reasoning_tier = "R6"
    expected_kill_pattern = "strict_threshold_violation"

    # Quantitative tightening table per coordinate kind
    TIGHTENING_LADDER = {
        "correlation": [0.30, 0.50, 0.70, 0.85, 0.90, 0.95, 0.99],
        "p_value":     [0.10, 0.05, 0.01, 0.001, 0.0001],
        "effect_size": [0.10, 0.20, 0.50, 0.80],
        # ...
    }
```

ETA: ~220 LOC, complementary to G14 + G09.

---

## Handoff

- ITER-3: implement string-substitution MVP per sketch.
- ITER-4+: tie to composition-aware loader so the tightened
  claim actually gets battery-tested with the new threshold.

— Charon, 2026-05-27 (authored 2026-05-26 ITER-2)
