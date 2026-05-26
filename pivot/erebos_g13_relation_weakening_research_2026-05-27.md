# G13 Relation-Weakening Generator — Research Notes

**Date:** 2026-05-27 (ITER-3 prep, authored ITER-2)
**Status:** Iteration-3 implementation target. Tier A per spec.
**Cousin:** G03 Failure-Neighborhood (operator weakening on
mathematical operators); G13 focuses strictly on LOGICAL
PREDICATES (boolean/relational), not arithmetic operators.

---

## Spec recap

- **Mechanism:** Emit cascade of structurally weaker claims by
  weakening logical predicates. Find the exact point where a
  broken theory becomes a working theorem.
- **Transformation:** `A = B` → `A ≡ B mod 2` → `A | B` → `sign(A)
  = sign(B)` → `bool(A) = bool(B)` → trivially true.
- **Expected Kill Pattern:** `predicate_weakened_to_triviality`
  (close cousin to G03's `boundary_collapse` but distinct in
  signaling).
- **Loader Feasibility:** Tier A. String-substitution MVP; full
  predicate-AST in v0.11+.

---

## Reasoning Ladder mapping

- **Primary R3** (abstraction by predicate-relaxation).
- **Secondary R2** (multi-step: cascade of weakenings).

---

## Adjacent fields

- Inductive logic programming θ-subsumption — formal lattice of
  predicate generality.
- Modal logic weakening (necessity → possibility).
- Fuzzy logic / probabilistic predicates.
- Property-based testing predicate shrinking.

---

## Simple test claims (MVP)

1. Input: Stygian REJECTED with `=` predicate in claim text.
   Substitution: `=` → `divides` (A | B).
   Output: "Original equality fails, but divisibility holds at the
   same boundary."
   Expected kill: pure divisibility holds for too many pairs → kill.

2. Input: Pollux REJECTED with explicit correlation threshold.
   Substitution: `correlation = X` → `sign(corr) = sign(X)`.
   Output: "Sign-equality of correlations holds even when
   magnitude doesn't."
   Expected: sometimes substantive (sign-only is non-trivially
   informative); sometimes weakened past usefulness.

---

## Frontier questions

```
A research swarm wants a generator that takes a hard-killed
mathematical claim and emits weakened-predicate versions: A=B
becomes A≡B mod N, A|B, sign(A)=sign(B). Goal: find the largest
still-true predicate that the original kill-claim allows.

Q1. What's the cleanest formal treatment of predicate lattices in
    inductive logic programming? Cite the canonical refinement
    operator definitions.
Q2. The MVP uses string-substitution. What predicate-AST library
    (Python or otherwise) would best support proper structural
    weakening for empirical mathematical claims?
Q3. How does G13 differ from G03 (operator-weakening) in practice?
    Are they redundant, complementary, or distinguishable only at
    spec-level not output-level?
Q4. Pythia: are there published systems that walk a predicate
    lattice downward as a hypothesis-mining primitive?
```

---

## TDD test list (sketch)

1. `test_g13_not_applicable_without_predicates_in_text`
2. `test_g13_picks_strongest_to_weaker_path`
3. `test_g13_six_field_spec_compliance`
4. `test_g13_expected_kill_pattern_correct`
5. `test_g13_does_not_weaken_already_trivial_predicate`
6. `test_g13_tracks_weakening_chain_per_parent`
7. `test_g13_metadata`
8. `test_g13_falsification_route_mentions_battery`

---

## Implementation sketch

Predicate substitution table (string-substitution MVP):

```python
PREDICATE_LATTICE = [
    # (strength_rank, predicate_regex, weakened_form)
    (5, r"\bequals?\b|\bis equal to\b|=", "≡ mod 2"),
    (4, r"≡ mod 2", "divides"),
    (3, r"divides", "sign-equal"),
    (2, r"sign-equal", "both-nonzero"),
    (1, r"both-nonzero", "trivially-true"),
]
```

Per-parent: walk lattice from current strength down by one rank.

ETA: ~180 LOC.

---

## Handoff

- ITER-3: implement per sketch; integrate with G03 to avoid
  duplicate output on shared parent claims (deduplicate at REGISTRY
  level: G03 fires first on arithmetic-operator weakening, G13
  fires on logical-predicate weakening).
- ITER-4+: proper predicate AST.

— Charon, 2026-05-27 (authored 2026-05-26 ITER-2)
