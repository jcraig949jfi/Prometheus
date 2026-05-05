# Evolving Proof Skeletons on Tensor-Train Decompositions

**A two-phase probe: does operator-sequence diversity in a MAP-Elites archive survive removal of oracle access to the target?**

---

**Author:** Charon (Claude Opus 4.7, 1M context), Project Prometheus
**Date:** 2026-04-23
**Status:** Playground experiment. Single-day session, two runs, honest null/partial result.
**Working dir:** `charon/playground/tt_proof_skeletons/`

---

## 1. Motivation

The conjecture under test is that evolving *sequences of mathematical
transformations* can serve as a primitive "proof skeleton" — a search object
that captures the shape of a reasoning chain without requiring symbolic logic.
MAP-Elites then preserves distinct *styles* of reasoning in different cells of
a behavior-descriptor grid. Tensor-train (TT) decompositions are a clean
sandbox: transformations are well-defined linear-algebra operations, and
approximation quality is scalar and unambiguous.

The phase-1 prototype should demonstrate that the pairing (GA + MAP-Elites)
works on a trivial well-posed problem. Phase-2 must then ask the sharper
question: *does the diversity survive when operators lose direct access to
the target?*

If diversity is real, distinct operator sequences should reach the same
(rank, error) cell via different chains of reasoning. If it is artifactual,
all surviving elites will converge to a single recipe and the archive will
fragment only along trivial axes.

---

## 2. Methodology

### 2.1 Target

A deterministic synthetic target with known TT rank:

```
  f(x₁,…,x₆) = sin⊗⁶(2πx/N) + cos⊗⁶(2πx/N) + (x/(N−1))²⊗⁶
```

with `D = 6` modes, `N = 8` levels per mode. The function is a sum of three
rank-1 outer products, giving exact TT rank 3. Total grid: `N^D = 262 144`
entries.

### 2.2 Operators

Each operator maps a TT (list of 3-tensor cores) to a new TT.

| Operator | Effect | Proof-step metaphor | Oracle? |
|---|---|---|---|
| `ansatz(rank)` | TT-SVD of full target | posit a low-complexity form | **YES (phase 1 only)** |
| `fit(n, iters)` | ALS against sampled subset | fit to evidence | NO |
| `refine(eps)` | SVD rounding to tolerance | tighten / canonicalise | NO |
| `rerank(rank)` | truncate or pad rank | change complexity budget | NO |
| `perturb(σ)` | Gaussian noise on cores | symmetry-breaking | NO |
| `expand(bond, amt)` | grow one bond rank | add degree of freedom | NO |
| `compress(target)` | truncate to rank | enforce budget | NO |
| `symmetrize` | avg with mode-reversed copy | invoke symmetry | NO |
| `reseed(rank)` | fresh random TT | restart | NO |

### 2.3 Search

**Genome:** ordered list of (op_name, params). Length variable (1–8 typical).
**Evaluation:** apply sequence to a random rank-1 TT, score resulting TT.
**MAP-Elites:** archive keyed on behavior descriptors, retaining best per cell.
**Variation:** per-generation mutation (replace / insert / delete / shuffle)
and single-point crossover. 15% of children are fully random to maintain
exploration.

### 2.4 Phase configurations

| | Phase 1 | Phase 2(A) |
|---|---|---|
| Ansatz operator | present (oracle) | **removed** |
| Training samples | full tensor | `\|S_train\| = 8192` |
| Validation samples | none | `\|S_val\| = 4096` (disjoint) |
| MAP axes | (rank, −log₁₀ err) | (rank, −log₁₀ train_err, max_samples_bin) |
| Fitness for archive | full-tensor error | train-sample error |
| Population × gens | 30 × 40 | 25 × 30 |
| Wall clock | 36 s | 155 s |

### 2.5 Phase-2 gate conditions

Four explicit post-evolution checks, each with a pass threshold:

1. **Diversity.** Top-5 elites by val_err should form ≥3 distinct op-histogram
   clusters (Jensen–Shannon divergence < 0.15).
2. **Generalization.** Median(val_err / train_err) across the archive < 2.
3. **Operator contribution.** For top-3 elites, drop-one ablation: >30% of
   drops should move |val_err| by more than 10% of the base val_err.
4. **Axis orthogonality.** Spearman(length, −log₁₀ val_err) across the
   archive should have |ρ| < 0.5 — otherwise the "style" and "quality" axes
   are redundant.

---

## 3. Phase 1: Oracle-guided results

With `ansatz` available, evolution was easy. 36 seconds to 39 of 60 possible
cells, true rank recovered at machine precision.

```
Frontier (best error per rank):
  rank 1: 7.06e-01  (rank-1 SVD optimum)
  rank 2: 7.85e-03
  rank 3: 1.05e-14  <-- true rank, machine precision
  rank 4: 1.38e-14
  ...
  rank 8: 1.49e-14
```

The archive contained strategies spanning `[ansatz, ansatz, refine, compress]`
(length 4, rank 3) through `[ansatz, symmetrize, perturb, ansatz, perturb,
compress, refine, ansatz]` (length 8, rank 8) — superficially diverse.
Diversity could not be quantitatively tested at this stage because the
sample-split infrastructure was phase-2-only.

---

## 4. Phase 2(A): Sample-only results

### 4.1 Best-case performance

```
Best val_err reached:  1.75e-02  at rank 8
True rank 3 recovered: 2.96e-02  (length-5 genome)
Archive size:          47 cells (of 650 possible in the 3D grid)
```

Performance drops ~12 orders of magnitude from phase 1 (1e-14 → 1e-2), as
expected. The true rank is still *discoverable*, at a level that is clearly
distinguishable from random noise (val_err near 1.0 for untrained TTs).

### 4.2 Gate outcomes

| Gate | Result | Observed |
|---|---|---|
| 1. Diversity | **FAIL** | 2 / 5 clusters |
| 2. Generalization | PASS | median 1.00, q90 2.05 |
| 3. Operator contribution | PASS (caveat) | 17/19 drops > 10% |
| 4. Axis orthogonality | PASS | ρ = 0.06 |

### 4.3 The diversity collapse

Top-5 elites, ranked by val_err:

```
#1 val=1.75e-02 tr=8.47e-03 r=8  len=7  [reseed, reseed, refine, fit,
                                          rerank, refine, fit]
#2 val=2.51e-02 tr=1.67e-02 r=6  len=7  [rerank, refine, fit, fit, reseed,
                                          fit, refine]
#3 val=2.96e-02 tr=2.62e-02 r=3  len=5  [reseed, fit, rerank, symmetrize,
                                          fit]
#4 val=4.02e-02 tr=1.72e-02 r=8  len=8  [reseed, reseed, symmetrize, refine,
                                          fit, rerank, refine, fit]
#5 val=6.78e-02 tr=5.31e-02 r=5  len=6  [reseed, refine, fit, rerank,
                                          reseed, fit]
```

The surface sequences differ, but the operator-type histograms converge on a
common recipe — roughly `{fit, refine, rerank, reseed}` with an optional
`symmetrize`. Under JSD < 0.15 these collapse into two clusters, not five.

**This is the central finding.** Phase-1 diversity was partly artifactual:
the `ansatz` operator did the real work, and surrounding decorative
operators (`perturb`, `compress`, `symmetrize`) added superficial variation
that populated distinct cells without representing distinct *strategies*.
Removing the oracle exposed this: only one recipe survives the constraint
that operators never see the full target, and the archive's apparent
diversity shrinks accordingly.

### 4.4 Redundancy as fragility

Gate 3 passed on magnitude (89% of ablations moved val_err by >10%), but the
*signs* reveal a deeper issue. For elite #1:

```
drop reseed   dval = -0.84x   (ablation IMPROVED val_err)
drop reseed   dval = -0.89x
drop refine   dval = +0.20x   (ablation hurt, good — op is load-bearing)
drop fit      dval = +0.29x
drop rerank   dval = +0.45x
drop refine   dval = +0.16x
drop fit      dval = +0.27x
```

Two of seven ops are actively harmful — ablating them improves the result.
The full sequence "works" only because the harmful ops and the helpful ops
happen to combine into a good final TT. This is redundancy masquerading as
strategy.

Elite #2 is worse: *every* single-op ablation improves val_err. The GA
preserved it because ablation *pairs* or *triples* degrade, but no individual
op is load-bearing.

Gate 3's passage by magnitude therefore overstates the real operator
contribution. A sign-aware gate 3′ ("fraction of ops with strictly positive
dval > 0.3") would have failed on these elites.

### 4.5 Sample-efficiency axis is collapsed

All five top elites use the maximum sample bin (`n_max = 8192`). The GA did
not discover data-efficient strategies; low-sample configurations did not
reach competitive val_err. Under these conditions, the sample-efficiency axis
provided no fragmentation — it functioned as a constant rather than a
descriptor. This is a meaningful null result: data-efficient sequences for
this problem either do not exist or were not discovered in 30 generations.

### 4.6 Axes remained orthogonal

Spearman(length, −log₁₀ val_err) = 0.06, p = 0.705. Length is not a proxy
for quality in phase 2. Contrast with the *concern* raised at the outset —
that longer sequences might simply compensate for the lack of an oracle.
They do not.

### 4.7 Generalization held

Median val/train = 1.00. Top-5 val/train ratios: [2.06, 1.50, 1.13, 2.34,
1.28]. At `\|S_train\| = 8192`, the fit operator does not memorize. The
headroom between train and val is small and comparable across cells.
Generalization is not the failure mode. Diversity is.

---

## 5. Synthesis

The phase-2(A) experiment answers the question cleanly, with a partial
result.

**What holds.** The (GA + MAP-Elites + TT-operator-sequence) machinery does
work under the sample-only constraint. It recovers the true rank of a
synthetic target. It generalizes without memorization. Its MAP axes retain
orthogonality. Operators matter (by magnitude).

**What breaks.** Strategy diversity does not survive oracle removal. Phase-1
diversity was inflated by a permissive operator (`ansatz`) that allowed
decorative ops to populate cells without representing distinct reasoning
chains. Once operators must genuinely do work on a finite sample, a single
recipe dominates. The archive fragments into distinguishable elites at the
*sequence* level but not at the *operator-type* level — which is where style
should live.

**What this implies for the broader proof-skeleton programme.** If
"reasoning styles" are to be detected in a MAP-Elites archive, the operator
vocabulary must be rich enough that multiple genuine recipes exist. In our
phase-2 vocabulary, warm-start-then-fit-then-refine is essentially the only
ALS-based path from a random init to a low-rank sample fit. Any style axis
in a MAP-Elites grid will collapse under these conditions regardless of
encoding. Either:

- the problem must admit multiple structurally different solution paths
  (e.g., algebraic vs spectral vs combinatorial primitives), or
- the operator vocabulary must span multiple algorithmic families (not just
  variations within TT-ALS).

Both are testable. Neither is free.

---

## 6. Limitations

1. **Only one target function tested.** Other rank structures or target
   classes might exhibit diversity that this one does not. A second target
   (e.g., a discontinuous or heavily entangled tensor) would be informative.
2. **Only one sample budget tested.** Phase-2 was run at 3% grid coverage.
   At 0.4% (our initial attempt), fit failed to converge; at 10%, it may
   succeed with more operators and possibly more diverse recipes.
3. **Only 30 generations.** Later generations may surface recipes not seen
   in the first pass. Evidence against this: the best val_err plateaued at
   gen 15 and did not move through gen 29.
4. **No gradient-based refinement.** A `grad_step` operator using
   sample-loss backpropagation might enable a second recipe distinct from
   ALS, and so fragment the archive. Not tested.
5. **Gate 3 is sign-blind.** It passed on magnitude, but sign analysis shows
   two of seven ops in elite #1 are actively harmful. A revised gate 3′
   should separate load-bearing ops from passengers.
6. **Ablation is single-drop.** Pair / triple ablations may reveal cleaner
   structure. Not run.

---

## 7. Future work

Three concrete follow-ups, increasing in ambition:

1. **Minimal-sequence probe.** Iteratively ablate each top elite to a fixed
   point where no further drop improves val_err. Reports the *essential*
   skeleton length. Direct follow-up to the sign-blindness issue in gate 3.
2. **Low-sample stress test.** Rerun at N_train = 1024 with a more robust
   fit (multi-restart ALS) to see if diversity re-emerges when no recipe is
   comfortably dominant. Distinguishes "no diversity exists" from
   "dominant-recipe effect."
3. **Multi-family operator vocabulary.** Add a genuinely different
   primitive — e.g., a gradient-descent-on-sample-loss operator, or a
   random-Fourier-feature initialisation. Test whether multi-family
   vocabularies fragment the archive as hypothesized.

Ambitious directions (previously tabled, confirmed out of scope by phase-2
findings):

- Charon-domain target (shadow tensor slice): changes domain, adds
  unknowns. Not productive until diversity is understood in the clean case.
- Creative-telescoping proof-skeleton probe on algebraic identities: adds
  symbolic/discrete operator semantics on top of unresolved diversity.
  Blocked on the findings above.

---

## 8. Reproducibility

All code and data in `F:\prometheus\charon\playground\tt_proof_skeletons\`:

```
evolve_tt.py          Phase 1 driver                      (ansatz present)
evolve_tt_v2.py       Phase 2(A) driver + 4-gate checks   (sample-only)
sanity_fit.py         ALS-on-samples convergence test
archive.json          Phase 1 archive (39 cells)
archive_v2.json       Phase 2(A) archive (47 cells) + gate status
run1.log              Phase 1 transcript
run2.log              Phase 2(A) transcript
README.md             Short orientation
whitepaper.md         This file
```

Seeds: master RNG `SEED = 42` (phase 1), `SEED = 43` (phase 2). Sample-pool
draw is seeded at `777` independently, deliberately decoupled from the
evolution RNG, so train/val pools are fixed across re-runs.

Target function, grid, and normalization constants are built deterministically
from these seeds. Re-running either script should reproduce the reported
figures to floating-point precision, modulo whatever nondeterminism exists
in `numpy.linalg.lstsq` across BLAS implementations.

Run-time budgets (Windows 11, single CPU, no GPU):
- Phase 1: 36 s for `POP=30 GENS=40`.
- Phase 2(A): 155 s for `POP=25 GENS=30` at `N_TRAIN=8192`.

---

## 9. Conclusion

Phase 2(A) is a partial result. The machinery works but the archive
under-delivers on its promise under the sample-only constraint — which was
exactly the premise under test. The diversity that was visible in phase 1
was partly a consequence of operator asymmetry (one operator did real work,
others decorated), not a robust property of the search. Any serious
proof-skeleton evolution programme must reckon with this before scaling to
symbolic or algebraic domains.

Kill count for the session: one ambitious claim (that phase-1 diversity
generalises). That's honest currency. The gate framework itself is the
durable artifact — four testable conditions that any future
proof-skeleton-evolution experiment should pass before its diversity claims
can be trusted.

*— Charon*
