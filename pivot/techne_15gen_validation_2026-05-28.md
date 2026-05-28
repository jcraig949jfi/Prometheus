# 15-Gen Stub Validation Report
**Date:** 2026-05-28 (Stage 26 of techne_15gen_plan_2026-05-28.md)

## Headline

**20 total new gen families now exist.** Substrate jumped from
35 active generators (Fire #141 era) to **55 active generators**
in two batches:
- 5 first batch (k1/l1/m1/n1/o1) — built stub → real over Stages 1-15
- 15 second batch (l2/m2/p1/q1/r1/s1/t1/u1/v1/w1/x1/y1/z1/aa1/bb1) —
  stub-level this round

The 26-template combinatorial ceiling has been moved decisively:
the substrate can now express ≥ 46 distinct claim shapes (26 old
+ 20 new), with the 15 new ones still at stub quality.

## Per-gen isolation-fire results (stub-level)

Each gen fired solo with `--only <gid> --batch-hours 0.01`. All
emitted their hand-coded entries then exhausted cleanly:

    l2  formalization_skeleton   4 records  (Lean 4 lemma skeletons)
    m2  corpus_compression       3 records  (universal-over-subset lemmas)
    p1  modus_ponens_chain       4 records  (3-hop implication chains)
    q1  modular_varying_p        3 records  (mod-p behavior across primes)
    r1  subset_relation          4 records  (⊆/=/∩ between catalog subsets)
    s1  triangle_inequality      4 records  (metric structure checks)
    t1  multi_hop_deduction      3 records  (catalog-grounded chains)
    u1  quantifier_swap          3 records  (∀∃ vs ∃∀ paired claims)
    v1  counterfactual_invariance 3 records (perturb input, check property)
    w1  closure_under_operation  4 records  (operation closure tests)
    x1  partial_information      3 records  (closed-world fragility)
    y1  analogical_transfer      3 records  (cross-domain analogies)
    z1  order_dependence         4 records  (operator commutativity)
    aa1 confidence_calibration   3 records  (self-conf vs ground precision)
    bb1 false_dichotomy          4 records  (≥3-category cases)

**Total: ~52 records across 15 new claim shapes.**

## Tests

- v0 tests for the first 5 gens (k1-o1):          26/26 green
- v1 tests for the first 5 gens (real behavior):  25/25 green
- v2 tests for the 15 new gens (this round):      75/75 green
- **Total: 126/126 green**

## Where the 15 new shapes come from

Two sources:

**From ChatGPT's original list (unbuilt remainder)**: 2
- l2 (formalization_skeleton) — Lean-ready lemma format
- m2 (corpus_compression) — subsume N records into 1 lemma

**From Sphinx's 105-category reasoning ontology**: 13, mapped
to specific Sphinx domains:
- A (Formal Logic): p1, u1
- C (Arithmetic): q1
- D (Temporal): z1
- F (Causal): v1
- G (Set Theory): r1, w1
- H (Spatial / Metric): s1
- I (Meta-Reasoning): aa1
- J (Common Sense): bb1
- K (Multi-Step): t1
- L (Uncertainty): x1
- N (Analogical): y1

## Success criteria check

From pivot/techne_15gen_plan_2026-05-28.md:
- **Minimum (12/15 SHAPE_NEW)**: ✓ EXCEEDED — 15/15
- **Target (15/15 SHAPE_NEW)**: ✓ MET
- Total gen count = 55 ✓
- 75 v2 tests green ✓

## Open: stub vs real (next-level work)

All 15 second-batch gens are STUB-LEVEL: they emit a small list of
hand-coded entries then exhaust. Like the first batch's stages
2-6 → 11-15, real-quality iteration is a follow-up:
- Need catalog integration (currently hand-coded)
- Need computation, not narration (currently the records DESCRIBE
  the claim shape; real gens should compute the answer)
- Need volume (3-4 records per gen → hundreds-thousands)

User decides which gens deserve the deep work. The cheap-to-real
ranking by my read:

1. r1 (subset_relation) — straightforward set-comparison over
   catalog subsets, similar to l1's bounded enumeration
2. s1 (triangle_inequality) — pick triples + check inequality on
   real catalog values; minutes of compute
3. q1 (modular_varying_p) — iterate primes + bucket catalog
   invariants mod p; mid-cost
4. t1 (multi_hop_deduction) — chain catalog lookups; needs the
   morphism registry from k1
5. w1 (closure_under_operation) — needs operation implementations
   per catalog
6-15. The meta / analogy / confidence gens (aa1, bb1, v1, x1, y1)
   are conceptually richer but require the substrate to introspect
   itself or generate synthetic analogies — harder to upgrade from
   stub.

## Recommended next moves

1. Run a normal `--bandit` fire with all 55 gens. Inspect which
   new gens get picked first (the explorer-prior + cooldown logic
   strongly favors low-saturation new entrants).
2. Pick the top-3 most-promising stubs for real-version upgrade
   (my pick: r1, s1, q1 — cheapest path to useful kills with
   evidence).
3. Eventually triage record samples from the new gens via the
   LLM-judge prompt.
