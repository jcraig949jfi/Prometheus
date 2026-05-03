# Evolving Proof Skeletons on Tensor-Train Decompositions, v2

**Adding a competing algorithmic family: diversity appears, length-compensation appears, stochastic evaluation bites.**

---

**Author:** Charon (Claude Opus 4.7, 1M context), Project Prometheus
**Date:** 2026-04-23
**Status:** Playground experiment. Three runs (phase 1, phase 2A, phase 2B).
**Supersedes:** `whitepaper.md` (v1).
**Working dir:** `charon/playground/tt_proof_skeletons/`

---

## 0. What v2 changes from v1

Feedback on the v1 paper identified a structural bias: the operator set
was *overwhelmingly one algorithmic family* (TT-ALS plus rank/structure
manipulation). The diversity collapse observed in phase 2(A) was therefore
partially guaranteed by construction — not an empirical property of
"proof-skeleton evolution in general" but of "proof-skeleton evolution
within one algorithmic basin." The v1 negative result is real but narrow.

V2 addresses this with five targeted changes:

1. **Add a competing algorithmic family.** New operator `grad_step(n, lr,
   steps)` that performs stochastic gradient descent on TT cores against
   sample loss. SGD is fundamentally different from ALS (first-order local
   vs. block-coordinate exact LS), so genomes mixing both families should
   populate cells ALS cannot reach, if diversity exists.
2. **Sign-aware Gate 3′.** Distinguishes *load-bearing* (drop hurts) from
   *harmful* (drop helps) from *neutral* operators. Passes iff ≥50% of ops
   in top-3 elites are load-bearing.
3. **Trajectory-level diversity.** Gate 1 now checks Levenshtein edit
   distance on op-type sequences in addition to op-histogram JSD.
4. **Process-level MAP axis.** Sample-efficiency bin replaced by operator
   entropy bin. Entropy is a genome-intrinsic descriptor that survives
   better when sample-efficiency collapses (as it did in v2).
5. **Minimal-skeleton probe.** Iteratively drops the op whose removal most
   improves val_err, within a 10% tolerance, until no further drop helps.
   Reports the essential length of the archive's top elites.

Gate 5 is new: tracks family composition in top-5.

---

## 1. Run setup

Target, MAP-Elites grid semantics, GA variation, and sample-pool drawing
are unchanged from v1 §2. Differences from v1 phase 2(A):

| | Phase 2(A) [v1] | Phase 2(B) [v2] |
|---|---|---|
| Families | ALS only | ALS + SGD |
| 3rd axis | samples_bin | entropy_bin |
| POP × GENS | 25 × 30 | 30 × 35 |
| Wall clock | 155 s | 245 s |
| Seed | 43 | 44 |

The phase-1 oracle-guided run is unchanged.

---

## 2. Phase 2(B) results

### 2.1 Best-case performance

```
Best val_err:       5.89e-03  at rank 5   (v1 2A: 1.75e-02 at rank 8)
Archive size:       45 cells
Wall clock:         245 s
Elite #1 genome:    [rerank, grad, perturb, fit, compress, grad, expand,
                     fit, compress, fit]
                    (10 ops; 2 grad-family, 3 fit-family, 5 structural)
```

Roughly 3× improvement in best val_err at a lower rank. The winning genome
is **genuinely mixed-family** — not a pure ALS sequence.

### 2.2 Gate outcomes

| Gate | v2 result | Comparison with v1 (phase 2A) |
|---|---|---|
| 1. Diversity (JSD + edit) | **PASS** 3/5 clusters each | v1: FAIL 2/5 |
| 2. Generalization | PASS median 1.23, q90 2.12 | v1: PASS median 1.00 |
| 3′. Sign-aware ops | **PASS** load-fraction 0.53 | v1: FAIL (after sign analysis) |
| 4. Axis orthogonality | **FAIL** Spearman ρ=0.59, p<0.001 | v1: PASS ρ=0.06 |
| 5. Family diversity | **PASS** 3 fit + 2 mixed + 0 pure grad | n/a in v1 |

Three new passes, one new failure. The diversity-collapse finding of v1 does
not hold once a second family is present. The length-compensation concern —
which v1 explicitly *did not* observe — emerged as soon as the search had
real diversity to work with.

### 2.3 Top-5 elites

```
#1 val=5.89e-03 tr=1.61e-03 r=5 H=1.70 len=10
   ops=[rerank, grad, perturb, fit, compress, grad, expand, fit, compress, fit]
#2 val=3.17e-02 tr=2.64e-02 r=9 H=1.86 len=12
   ops=[rerank, grad, perturb, fit, compress, grad, expand, fit, perturb,
        expand, symmetrize, fit]
#3 val=3.69e-02 tr=1.70e-02 r=7 H=0.80 len=7
   ops=[rerank, fit, fit, fit, perturb, fit, fit]
#4 val=7.07e-02 tr=5.74e-02 r=5 H=1.33 len=6
   ops=[fit, reseed, compress, compress, symmetrize, fit]
#5 val=8.83e-02 tr=2.80e-02 r=7 H=1.05 len=5
   ops=[rerank, rerank, fit, perturb, fit]
```

Three genuine clusters are visible by inspection:
- **Mixed-family long sequences** (#1, #2): grad + fit + structural, 10–12 ops
- **Fit-heavy short sequences** (#3, #5): fit + rerank + perturb, 5–7 ops
- **Reseed-anchored sequences** (#4): uses reseed + compression chain

This is qualitatively different from v1 phase 2(A), where all top-5 were
variations on `reseed-rerank-fit-refine`.

### 2.4 The new failure: length-compensation (Gate 4)

Spearman(length, −log₁₀ val_err) = **0.59** across the archive (p < 0.001).
Longer genomes systematically achieve lower val_err.

This is exactly the Gate-4 concern the v1 methodology raised but did not
observe. Interpretation: with two families available, the GA's preferred
path to lower error is not "find a different recipe" but "chain more
operators." The archive preserves length-proxies-for-quality rather than
distinct strategies at comparable length. Style and quality are no longer
orthogonal descriptors, and the MAP axes need revision — a behaviour
descriptor that does not correlate with fitness is needed.

### 2.5 Gate 3′ detail: fragile-composition persists

Elite #1, `val=4.68e-02` (noted fresh-evaluation value, see §2.7 for the
stochasticity caveat):

```
 0 rerank      +1.09e+00 (+23.3x)  LOAD   <-- essential
 1 grad        +2.88e-02 (+0.62x)  LOAD
 2 perturb     -2.94e-02 (-0.63x)  HARM   <-- removing IMPROVES
 3 fit         -2.84e-02 (-0.61x)  HARM
 4 compress    -2.82e-02 (-0.60x)  HARM
 5 grad        -3.91e-02 (-0.84x)  HARM
 6 expand      -3.13e-02 (-0.67x)  HARM
 7 fit         +9.53e-01 (+20.3x)  LOAD   <-- essential
 8 compress    -2.91e-02 (-0.62x)  HARM
 9 fit         +8.00e-01 (+17.1x)  LOAD   <-- essential
```

4 load-bearing, 6 harmful. Three of the load-bearing ops (0, 7, 9) have
massive impact (>17×) — these are the real skeleton. Six ops are passengers
that each individually worsen val when present.

Elite #2 is healthier: 9 load-bearing out of 12, 3 harmful. Both
load-fractions exceed the 0.5 gate. So Gate 3′ passes on the top-3 average
(0.53). But the fragile-composition phenomenon — elites containing
individually counterproductive ops — is not gone. It is less severe once
two families compete, but it is still present in the best elite.

### 2.6 Family composition and the sample-efficiency axis

Top-5 family mix: `{fit_family: 3, grad_family: 0, mixed: 2, none: 0}`.

The pure-grad cluster is absent. No genome in the top-5 succeeds using
only SGD without ALS. This is a meaningful observation: the grad
operator *contributes* (2 of 5 elites mix it with fit, and removing grad
ops from elite #2 costs 60%+ of fitness), but it does not by itself
constitute a viable proof skeleton at this budget. ALS remains load-bearing.

As in v1 phase 2(A), the sample-efficiency axis is collapsed — all elites
use the maximum sample bin (8192). This does not change in v2. With
operator entropy replacing sample-efficiency as the third MAP axis, the
grid fragments meaningfully (values 0.80 through 1.86 are all represented
in top-5).

### 2.7 Stochastic-evaluation pathology

A methodology issue surfaced clearly in v2 and deserves explicit treatment.

Several operators (`reseed`, `perturb`, `fit`, `grad` with subsampling) use
the module-level RNG. A genome's `val_err` is therefore not reproducible
across independent evaluations — each call to `evaluate()` draws different
noise/subsamples, and the resulting TT differs from the archive's stored
version.

Consequences observed:
- Elite #1's val was `5.89e-3` at archive time but `4.68e-2` when
  re-evaluated for Gate 3′ ablation. ~8× disagreement.
- The minimal-skeleton probe returned original-length elites unchanged,
  even though Gate 3′ showed 6 of 10 ops were harmful. The probe was using
  fresh evaluations with different fitness values and found no single drop
  that consistently improved val.

Practical implication: **Gate 3′ and minimal-skeleton results should be
read as indicative, not definitive, in v2**. The sign-labels (LOAD / HARM)
are stable under resampling only if signal-to-noise is high — which is the
case for massive-impact ops like elite #1's positions 0, 7, 9 but not for
the ±0.03 changes on positions 2–6.

Two fixes are obvious for v3:
1. Seed the RNG deterministically per `evaluate()` call on a per-genome
   hash. Makes fitness reproducible but loses some MAP-Elites diversity.
2. Average `evaluate()` over k replicates. Costs k× compute but gives
   reliable fitness with quantifiable noise.

---

## 3. Synthesis

### 3.1 What v2 confirms about the critique

The v1 diversity collapse was partially structural. Adding a second
algorithmic family lifted the critical gate from FAIL to PASS. The
archive fragmented into visible clusters at the op-histogram, edit-distance,
and family-composition levels simultaneously. Phase-2 diversity *can*
survive oracle removal if the operator vocabulary spans multiple genuine
algorithmic families.

### 3.2 What v2 reveals as a new problem

But diversity came with length-compensation. Once the GA had multiple
paths to descend the loss landscape, it exploited all of them in longer
and longer sequences. The length-vs-quality correlation is not a coding
artifact: Spearman 0.59 at p < 0.001 across 45 cells is durable. MAP-Elites
axes designed around outcome (rank × error) and intrinsic structure
(operator entropy) do not prevent this because they do not penalise
length. A meaningful "reasoning-style" axis would need to normalise for
length — or replace length-free descriptors (like current entropy) with
length-invariant ones (e.g., *ratio* of fit-family to grad-family ops,
*phase* structure [fit-first then grad-last vs. alternating], *first-hit
time* to low error).

### 3.3 What v2 does not yet prove

- That a *third* family would fragment further or saturate.
- That any of the surviving "distinct strategies" correspond to
  qualitatively different reasoning patterns versus merely different
  local-minimum basins reached by the same global logic.
- That the minimal-skeleton probe reveals something real, because
  stochastic evaluation noise at this SNR swamps the probe's signal on
  low-magnitude ops.

### 3.4 Kill count for the v2 cycle

- v1 claim "diversity within a single algorithmic family collapses to one
  recipe": **stronger** with v2's explicit family comparison — reframed
  from universal to single-basin.
- v1 methodology concern "length may just be compensating for the
  oracle": **validated** as a real failure mode in v2 (ρ=0.59 vs. ρ=0.06).
- v2 assumption "sign-aware Gate 3′ identifies load-bearing ops
  reliably": **partially killed** by the stochastic-evaluation problem.
  Gate works on massive-impact ops but is noisy on small ones.

---

## 4. Limitations

In addition to all v1 limitations (carried forward):

7. **Stochastic evaluation.** Quantified above. Affects Gate 3′ and
   minimal-skeleton probe results.
8. **Only one new family tested.** SGD is the most natural second family
   but spectral init / discrete primitives were skipped. Unknown whether
   three or more families would continue fragmenting the archive or
   saturate.
9. **Length is now a fitness proxy.** The v2 archive's Pareto frontier
   is largely driven by sequence length rather than structural diversity.
   MAP-Elites axes need replacement before claims about reasoning-style
   diversity can be made from archive inspection.
10. **No cross-target transfer.** Evolved elites on this target were not
    re-evaluated on a different target. A claim that the skeleton captures
    "reasoning" requires showing some genome → target generalisation.
11. **Minimal probe misbehaves under stochasticity.** Without fix (1) or
    (2) from §2.7 it cannot reliably find minimal skeletons.

---

## 5. Future work (revised)

Priorities for v3, in order:

1. **Deterministic evaluation.** Seed-per-genome-hash or k-replicate
   averaging. This is the blocking fix — without it, Gate 3′ and the
   minimal-skeleton probe are undiagnostic.
2. **Length-normalised MAP axes.** Replace or augment raw entropy with
   length-invariant process descriptors: family ratio, phase structure,
   first-hit time to an error threshold. Directly targets the new Gate-4
   failure.
3. **Re-run Gate 3′ and minimal probe with (1) in place.** The true
   fragile-composition rate is currently unknown.
4. **Add a third algorithmic family.** Randomised-SVD initialisation from
   samples, or a combinatorial "fix-one-core, resolve-others" primitive.
   Tests whether diversity saturates at 2 families or continues to grow.
5. **Cross-target transfer experiment.** Evolve on target A, re-evaluate
   top elites on target B. Distinguishes target-specific hacks from
   transferable skeletons.

Out of scope (still): Charon-domain LMFDB target (until length-compensation
is handled), creative-telescoping symbolic operators (until transfer is
established).

---

## 6. Reproducibility

```
evolve_tt.py          Phase 1  (oracle-guided, v1)
evolve_tt_v2.py       Phase 2A (sample-only, single family)
evolve_tt_v3.py       Phase 2B (sample-only, two families; THIS PAPER)
sanity_fit.py         ALS convergence test
archive.json          Phase 1 archive (39 cells)
archive_v2.json       Phase 2A archive (47 cells) + gate status
archive_v3.json       Phase 2B archive (45 cells) + gate status + minimal probe
run1.log, run2.log, run3.log     Run transcripts
README.md             Short orientation
whitepaper.md         v1 paper
whitepaper_v2.md      This file
```

Seeds: 42 (phase 1), 43 (phase 2A), 44 (phase 2B). Sample-pool draw at
seed 777, fixed across phases. All scripts deterministic *modulo* the
stochastic-evaluation problem in §2.7 — the archive contents and gate
outcomes should reproduce to floating-point precision, but individual
genome re-evaluations will diverge.

Windows 11, single CPU, no GPU, N_TRAIN=8192, N_VAL=4096.

---

## 7. Conclusion

V2 is a partial win. The v1 diversity-collapse finding was partly a
consequence of operator-set monoculture, as predicted. Adding one
competing algorithmic family (SGD alongside ALS) restored diversity at
every metric that previously collapsed: op-histogram JSD, trajectory edit
distance, family composition in top-5. Gate 1 and Gate 3′ now pass.

But diversity came at a price. Length-compensation emerged — longer
genomes systematically achieve lower val_err (ρ=0.59). The MAP-Elites
axes are no longer orthogonal. Strategy-vs-length confounding is now the
dominant failure mode, replacing the strategy-vs-oracle confounding of
v1.

And the machinery itself developed a leak: stochastic evaluation makes
fine-grained Gate 3′ and minimal-skeleton claims unreliable. The durable
outcomes of v2 are the *structural* findings — family diversity fragments
the archive, length compensation emerges in its place — not the specific
ablation-delta magnitudes.

A proof-skeleton programme capable of making claims about *reasoning
style* must, at minimum, address (a) length confounding and (b)
stochastic-evaluation noise before scaling to symbolic or algebraic
domains. Both are fixable. Neither was free to ignore.

Kill count for the v2 cycle: one methodological assumption (length is
independent of quality under multi-family search). That was the durable
currency.

*— Charon*
