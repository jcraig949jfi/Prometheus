# G14 Relation-Strengthening Generator — Research Notes

**Date:** 2026-05-27 (ITER-3 prep, authored ITER-2)
**Status:** Iteration-3 implementation target. Tier A per spec.
**Cousin:** G04 Survivor-Tightening (bound-tightening); G14
focuses on PREDICATE-strengthening (sign-equal → magnitude-equal
→ exact-equality).

---

## Spec recap

- **Mechanism:** Inverse of G13. Push weak observational
  heuristics into strict mathematical laws until they break.
- **Transformation:** `sign(A) = sign(B)` → `|A - B| < ε` → `A =
  B mod N` → `A = B`.
- **Expected Kill Pattern:** `predicate_strengthened_past_truth`
  (the strengthened version no longer holds; the weak version was
  the maximal-true claim).
- **Loader Feasibility:** Tier A.

---

## Reasoning Ladder mapping

- **Primary R8** (open-ended conjecture formation: stronger claim
  is a sharper hypothesis).
- **Secondary R3** (abstraction in reverse: specializing).

---

## Adjacent fields

- ILP refinement operators (downward refinement = strengthening).
- Mathematical conjecture sharpening (e.g., Sato-Tate sym^k
  refinements).
- Abductive reasoning ("if the weak claim holds, what's the
  strongest claim that ALSO holds?").
- Symbolic regression with parsimony pressure inverted: search
  for the LONGEST formula that fits the data exactly.

---

## Simple test claims (MVP)

1. Input: Pollux PROMOTED with weak correlation claim.
   Strengthen: `correlation > threshold` → `correlation = exact
   value`.
   Output: "Survives at exact correlation 0.85 ± 0.01."
   Expected: kill — exact-equality fails; bounded-by-epsilon was
   the maximal-true form.

2. Input: G12 emitted substitution claim with "fungibility"
   wording.
   Strengthen: `fungibility` → `isomorphism`.
   Output: "Original and substituted invariants are isomorphic
   under the parent relation."
   Expected: usually false — fungibility is much weaker than
   isomorphism — but the kill identifies the exact failure boundary.

---

## Frontier questions

```
A research swarm wants a generator that takes a weakly-true
mathematical claim and emits successively-stronger versions
(sign-equal → magnitude-equal → exact-equal). Goal: find the
sharpest form that still survives.

Q1. ILP downward refinement operators are the formal analog.
    Which Popper / Aleph / Metagol features are most directly
    transferable to G14?
Q2. The strengthening lattice ends at "exact equality" but
    mathematical literature often has additional strengthenings
    (uniqueness, effective bounds, conditional-on-GRH). Should G14
    enumerate these explicitly?
Q3. Cross-reference: G04 Survivor-Tightening operates on
    quantitative bounds (epsilon-bounding). G14 operates on
    logical predicates. Are these the same generator in different
    notation, or genuinely different layers? Make the case.
Q4. Pythia: is there a published taxonomy of mathematical claim
    strengthenings used by automated theorem provers' "lemma
    sharpening" passes?
```

---

## TDD test list (sketch)

1. `test_g14_picks_weakest_to_stronger`
2. `test_g14_six_field_spec`
3. `test_g14_expected_kill_pattern`
4. `test_g14_does_not_strengthen_already_strict_predicate`
5. `test_g14_metadata`

---

## Implementation sketch

Inverse lattice of G13. Walk from current predicate strength UP
by one rank per emission.

ETA: ~180 LOC, complementary to G13 implementation.

---

## Handoff

- ITER-3: ship alongside G13 with shared PREDICATE_LATTICE
  constant (refactor G13 + G14 into a shared `_predicate_lattice.py`).
- ITER-4+: integrate with composition-aware loader so the
  strengthened claim actually gets battery-tested.

— Charon, 2026-05-27 (authored 2026-05-26 ITER-2)
