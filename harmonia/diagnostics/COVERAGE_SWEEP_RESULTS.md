# Coverage Sweep — hypothesis-class coverage across instruments

**Author:** Harmonia (coverage meta-instrument) · **Date:** 2026-06-22
**Doctrine:** "No '0 novel results' may be called terrain exhaustion (B1) until
hypothesis-class coverage is measured." A low-coverage instrument's "0 novel" is
a **B2** (expressiveness-ceiling) result, not flat terrain.
[feedback_distinguish_B1_B2, feedback_failure_signature_doctrine]

**Reusable module:** `D:\prometheus\harmonia\diagnostics\coverage_diagnostic.py`
**Runner:** `D:\prometheus\harmonia\diagnostics\run_coverage_sweep.py`
**Raw numbers (executed):** `D:\prometheus\harmonia\diagnostics\coverage_sweep_results.json`

All four instruments were measured from their **actual code vocabulary**, not a
description: `theseus/generators/a3_functional_identity.py` (operators),
`theseus/generators/a1_catalog_cross_product.py` (relations/invariants),
`apollo/src/primitive_types.py` (24 typed primitives),
`agents/icarus/ladder.py` (13 frozen rungs). The diagnostic was **run**
(executing lens); the numbers below are emitted, not asserted.

---

## Results table

| instrument | class size | coverage% (in-class) | in-class recall | out-of-class% | dominant ceiling axes | verdict |
|---|---:|---:|---:|---:|---|---|
| EC void-miner (catalog: 9 mined invariants) | 10 368 | 12% (2/16) | **100%** (2/2) | 88% | RELATION_OOV 5, CROSS_OBJECT 3, UNARY 2, DISTRIBUTIONAL 2, ARITY_GE_3 1, REAL_VALUED 1 | **B2_CEILING** |
| a3 cross-product (knot × EC) | 3 456 | 0% (0/5) | n/a | 100% | PROOF_DEAD, UNARY, CROSS_OBJECT, DISTRIBUTIONAL, REAL_VALUED | **B1_EXHAUSTED_BY_PROOF** |
| Apollo Frame-H primitive set | 24 | 50% (6/12) | 83% (5/6) | 50% | REAL_VALUED 2, COMPOSITIONAL 2, ARITY_GE_3 1, RELATION_OOV 1 | **MIXED_INCONCLUSIVE** |
| Icarus R0-R12 ladder | 13 | 83% (10/12) | 60% (6/10) | 17% | OTHER 2 (orthogonal axes) | **MIXED_INCONCLUSIVE** |

(The EC full-class read — counting BSD-rank-equality and parity as in-class-in-shape
but never offered an invariant — comes out **MIXED** under the strict separator,
because two in-class laws have recall < 1. The **catalog-class** read above, where
those two are out-of-class because their invariant was never mined, reproduces the
original audit's perfect-in/zero-out **B2_CEILING**. Both are emitted by
`coverage_diagnostic.py`; the difference is the honest one and is documented in the
module self-test.)

---

## Per-instrument failure shapes (not verdict lines)

**EC void-miner — B2_CEILING (regression reproduced).** Perfect in-class recall
(2/2) and zero of 14 out-of-class targets reachable, on a class expressing only
~12-25% of surveyed EC structure. The 75-88% it cannot see fails along six axes,
none fixable by adding integer invariants: relations-out-of-vocabulary,
cross-object pairing, unary properties, distributional laws, arity≥3, real-valued.
**The shadow is fully explained by two known facts** (`torsion | ∏c_p`, `rad(N)|N`).
Fix = widen the class (unary-property miner, real-valued lattice, cross-object
pairing, arity-3 relations), NOT more integer invariants.

**a3 cross-product — B1_EXHAUSTED_BY_PROOF (the contrast).** The product-measure
theorem (in `lattice_void_miner.py`, decision procedure validated 34/34) proves
that under cross-product pairing the joint distribution of
`(inv_a(knot), inv_b(EC))` is the **product of marginals**: every exact void is a
single-catalog set-fact, *never* a knot↔EC correspondence. The class is provably
degenerate. Its "0 novel" is a **structural certainty**, not an instrument shadow.
This is the useful contrast to EC: same shaped vocabulary, opposite verdict —
widening THIS class cannot help; the **pairing itself** must be replaced (the
same-object diagonal is the non-degenerate sibling, and that is the EC instrument).

**Apollo Frame-H primitives — MIXED_INCONCLUSIVE (honest).** 50% coverage, but
in-class recall is 83% — one capability the alphabet *can* type (2nd-order
theory-of-mind via `sally_anne_test`+`track_beliefs`) is wired as `any`/`any`
and unproven. The diagnostic **refuses to call this a clean ceiling**: where an
instrument misses laws it could express, "0 novel" is confounded by search
insufficiency, so neither B1 nor B2 is earned. The *shape* still leans ceiling-ward
— 6/12 out-of-class via REAL_VALUED (no continuous-optimization / simulation op),
COMPOSITIONAL (acyclic DAG → no recursion/fixpoint, no structure-mapping), ARITY≥3
(no joint graph+probability op), RELATION_OOV (no parsing). Actionable next step is
to **first** prove or kill the 2nd-order-ToM in-class capability, **then** re-read.

**Icarus R0-R12 ladder — MIXED_INCONCLUSIVE (broad, but climb-limited).** Highest
coverage (83%) and the only **broad** class — it spans pattern-response to
open-ended research. But in-class recall is 60%: rungs R8-R12 exist and are
falsification-testable yet **have not been reached/validated** (Icarus is at R5-R6).
This is *climb insufficiency*, not a ceiling — exactly the case the separator is
designed to flag rather than mislabel as B1. The only genuinely out-of-class
targets are **orthogonal** (ensemble/lens-breadth, calibration-as-graded-quality):
the 1-D ordinal ladder can't place them — they live in the orthogonal F/M/H
dimensions that are not in `ladder.py`. So the ladder is **not** a low-coverage
monoculture like EC; its open question is reaching the rungs it already defines.

---

## Cross-instrument reading

- **The EC B2 ceiling is NOT program-wide.** The reassessment hypothesis was
  "every instrument tops out at low coverage via similar axes → diversify
  hypothesis classes, don't find new terrain." The sweep **partially falsifies**
  that: EC is a narrow B2 ceiling, but a3-cross is dead-by-proof (a *different*
  failure), Apollo is a 50%-coverage substrate whose limit is partly unproven
  in-class capability, and Icarus is a broad ladder limited by *climb*, not
  expressiveness. **Three instruments, three distinct stall mechanisms.**
- **The shared axis across the math instruments is REAL_VALUED + CROSS_OBJECT.**
  EC and Apollo both lose capability to real-valued/continuous structure; EC and
  a3 both lose cross-object structure. If there is a single highest-leverage
  hypothesis-class widening, it is **admitting real-valued/tolerance relations**
  (opens EC's BSD/Szpiro axis and Apollo's optimization/simulation axis at once).
- **The diagnostic earns its keep by REFUSING two verdicts.** Apollo and Icarus
  both came back MIXED, not a forced B1/B2. That is the point: a clean ceiling
  read requires perfect in-class recall; without it, "0 novel" is confounded by
  search/climb insufficiency. The instrument distinguishes "the ruler is short"
  (B2) from "we haven't finished measuring with the ruler we have" (MIXED).

---

## Honest limits (falsification-first on this audit)

- **Curated target lists are illustrative, not canonical.** The exact coverage
  percentages (12%, 0%, 50%, 83%) would move under reasonable edits to the
  surveyed targets. The **robust** signal is the *structure*:
  **perfect-in-class-recall + zero-out-of-class on a narrow class = ceiling
  (B2)**; **a proof of class degeneracy = B1-by-proof**; **in-class recall < 1 =
  MIXED** (don't assign B1/B2 until search/climb is fixed). These survive edits
  to the lists; the percentages do not.
- **"Out of class" ≠ "instrument is broken."** Within its class each instrument
  is sound. The critique is of the fixed class, never the code.
- **Class size vs breadth are different things.** EC has 10 368 cells but is
  *narrow* (one claim shape); Icarus has 13 rungs but is *broad* (spans the
  reasoning range). The verdict logic keys on **breadth**, not raw size — a large
  monoculture is still a monoculture.
- **a3's PROOF-DEAD verdict is the strongest single result** because it does not
  depend on a curated list at all: the product-measure theorem is a proof, so the
  0% coverage is certified, not illustrative. It is the calibration anchor showing
  the diagnostic can express a B1 verdict that is *not* just "we found a lot."
- **Apollo class_size shown as 24/25** is the primitive *alphabet* (the binding
  constraint), not the chain space (which is unbounded). The narrow-breadth call
  reflects that all compositions are acyclic typed DAGs over that fixed alphabet.

---

*The instrument is the product; this measures the instrument. Re-run anytime:*
`PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/diagnostics/run_coverage_sweep.py`
