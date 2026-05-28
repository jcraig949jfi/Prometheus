# Plan: 15 More Gen Families — Path to 20 Total New Shapes
**Date:** 2026-05-28
**Author:** Techne (Claude Opus 4.7)
**Predecessors:** pivot/techne_5gen_plan_2026-05-27.md (k1/l1/m1/n1/o1)

## Goal

Take the substrate from 5 new gen families → **20 total new gen
families**. Sources:
- ChatGPT's original list: 2 unbuilt ideas (`m` compression, `l`
  formalization-skeleton)
- Sphinx reasoning-failure ontology: 13 categories translated into
  claim-emitting generator shapes

Total active gens after this batch: **55** (35 old + 5 first
round + 15 this round).

## The 15 new gens

### From ChatGPT's unbuilt remainder

#### `l2_formalization_skeleton`
Emit claims pre-formatted for Lean 4 autoformalization: typed
statement skeletons that aesop / simp can attempt to discharge.
Distinguished from k1: k1 traces typed paths; l2 emits the FULL
typed lemma statement in formal-skeleton form.

#### `m2_compression`
Emit records that SUBSUME multiple existing corpus records into
a single lemma-statement. Distinguished from c4 (generalization):
c4 widens one specific claim; m2 compresses many records that
share structure into a "for all X in catalog subset S, P(X)" form.

### From Sphinx Domain A (Formal Logic)

#### `p1_modus_ponens_chain`
Emit multi-hop deduction claims: "If P(X) and (P(X) → Q(X)), then
Q(X)" with each link grounded in a catalog computation. Shape: a
chain of 2-3 implications, not a single relation.

#### `u1_quantifier_swap`
Emit pairs of claims where ∀X∃Y vs ∃Y∀X order matters. Pure-shape
records exposing the substrate's sensitivity to quantifier order.

### From Sphinx Domain C (Arithmetic)

#### `q1_modular_varying_p`
Emit claims about catalog invariant behavior mod p as p varies
across primes. Distinguished from existing equal_mod_2: q1
emits the FULL family "invariant behaves like X mod p for p ∈ P"
and finds primes where structure changes.

### From Sphinx Domain G (Set Theory)

#### `r1_subset_relation`
Emit claims of form "S_1 ⊆ S_2" or "S_1 ∩ S_2 = ∅" over computable
catalog subsets defined by predicates. Tests set-relation reasoning
not present in existing pairwise-claim gens.

#### `w1_closure_under_operation`
Emit claims "Set S is closed under operation O" — for catalog
subsets, test whether applying an operation keeps you in the set.

### From Sphinx Domain H (Spatial / Metric)

#### `s1_triangle_inequality`
Emit claims testing "|f(X) - f(Z)| ≤ |f(X) - f(Y)| + |f(Y) - f(Z)|"
for triples of catalog objects and various invariant functions f.
Tests metric structure preservation.

### From Sphinx Domain K (Multi-Step)

#### `t1_multi_hop_deduction`
Emit claims requiring ≥2 catalog lookups + intermediate computation
to verify. Distinguished from a1 (one lookup) and h2 (one
triangulation): t1 chains hops explicitly with each step labeled.

### From Sphinx Domain F (Causal)

#### `v1_counterfactual_invariance`
Emit claims of form "If catalog object X had attribute A = a'
instead of a, then property P(X) would still hold." Substrate
analogue of causal counterfactual: vary one input, check robustness.

### From Sphinx Domain L (Uncertainty / Closed-World)

#### `x1_partial_information`
Emit claims that hold given a partial catalog view but may fail
with the full view. Tests substrate robustness to absence-of-evidence.

### From Sphinx Domain N (Analogical)

#### `y1_analogical_transfer`
Emit claims of form "Pattern P holds in domain D1 (knot); does P
hold via analogy in domain D2 (EC)?" — cross-domain transfer
claims grounded in catalogs.

### From Sphinx Domain D (Temporal / Ordering)

#### `z1_order_dependence`
Emit claims testing "f(g(X)) vs g(f(X))" for catalog operations.
When the two differ, the operations don't commute — a substrate-
meaningful structural fact.

### From Sphinx Domain I (Meta-Reasoning)

#### `aa1_confidence_calibration`
Emit meta-claims pairing each candidate record with a stated
confidence and a computable ground-truth precision. Distinguished
from n1 (verifier disagreement): aa1 emits SELF-confidence-VS-
ACTUAL-precision claims for a single record.

### From Sphinx Domain J (Common Sense)

#### `bb1_false_dichotomy`
Emit claims demonstrating that ≥3 distinct categories exist in
contexts where a binary distinction is commonly assumed. E.g.
"EC torsion isn't just {trivial, Z/n} — Z/2×Z/2n also occurs."

## Stage breakdown (TDD)

### Stage 17 — Plan + ClaimKind schema additions + v0 failing tests
Single commit:
- This document
- 15 new ClaimKind values in record_schema.py
- theseus/tests/test_new_gen_families_v2.py with 75 failing tests
  (5 per gen × 15 gens)

### Stage 18 — Implement stubs for ChatGPT remainder (l2, m2)
Two files (one commit), 10 tests green.

### Stage 19 — Implement Sphinx A/C stubs (p1, q1, u1)
Three files (one commit), 15 tests green.

### Stage 20 — Implement Sphinx G/H stubs (r1, s1, w1)
Three files, 15 tests green.

### Stage 21 — Implement Sphinx K/F stubs (t1, v1)
Two files, 10 tests green.

### Stage 22 — Implement Sphinx L/N/D stubs (x1, y1, z1)
Three files, 15 tests green.

### Stage 23 — Implement Sphinx I/J stubs (aa1, bb1)
Two files, 10 tests green.

### Stage 24 — Register all 15 in registry.py
One commit. list_active() should report 55 gens.

### Stage 25 — Isolation fires for all 15
Quick smoke fire per gen via `--only <gid> --batch-hours 0.05`.
Verify each emits its shape.

### Stage 26 — Validation report + commit
pivot/techne_15gen_validation_2026-05-28.md

## Success criteria

- **Minimum**: 12 of 15 emit SHAPE_NEW records (claim_kind not in
  the existing 31-template set after Stages 11-15)
- **Target**: 15 of 15 emit SHAPE_NEW. Templates count grows
  by ≥ 15. Total gen count = 55.
- **Failure**: < 12 of 15 emit SHAPE_NEW. Implementation reveals
  that several Sphinx categories don't translate to substrate
  claim shapes — would need re-think.

## Discipline

- Stub-level only this round. Real-quality iteration happens
  AFTER user picks which gens deserve the deep work (mirrors how
  k1/l1/m1/n1/o1 went stub → real over Stages 11-15).
- TDD red→green per stage. Don't ship a gen without its 5 tests.
- One commit per stage. Per memory `feedback_todo_hygiene.md`,
  check off as I go.
