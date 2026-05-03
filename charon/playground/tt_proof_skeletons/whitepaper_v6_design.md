# Phase 6 Design Document: Distributional Training over Targets

**A pre-run proposal for the experiment that would actually test whether the operator class supports transferable proof skeletons.**

---

**Author:** Charon (Claude Opus 4.7, 1M context), Project Prometheus
**Date:** 2026-04-25
**Status:** *Design document, awaiting review.* Not yet run.
**Working dir:** `charon/playground/tt_proof_skeletons/`
**Companion to:** `whitepaper_v5.md` §9 (sketch). This document expands
that sketch into a full design ready for execution after review.

---

## TL;DR

V5 robustly demonstrated that no fitness-signal modification *tested
so far* (parsimony, two-target averaging, deterministic eval, multi-
family vocabulary) restores transfer of evolved TT operator sequences
to a held-out target. V5's revised framing puts the blame on the
training regime — the GA evolves procedures that solve specific
F-instances rather than functions over F — but does not establish
that the operator class is structurally limited.

V6 tests the program-class hypothesis directly. It evolves genomes
under a fitness signal computed across a *batch of randomly-drawn
targets from a parametric family*, holds out an independent batch from
the same family for transfer evaluation, and compares the result to a
budget-matched single-target baseline.

**If V6 succeeds:** v5's "vocabulary is the wall" framing is wrong;
distributional training was the missing ingredient.
**If V6 fails:** the case for vocabulary-level revision strengthens,
and v7 explores functional-genome / structured-anchoring routes.

---

## 1. Background

This is the seventh experiment in the proof-skeleton playground sequence.
Prior experiments and their outcomes:

| Phase | Result |
|---|---|
| 1 (oracle) | TT-SVD via `ansatz` operator — machine precision; structurally trivial. |
| 2A (1-family) | Diversity collapse: one ALS recipe dominates. |
| 2B (2-family stochastic) | Diversity restored; eval was noisy. |
| 2B det rerun | ~50% of v2's "fragility" was eval noise. |
| 3A (det + parsimony) | All gates pass on target A. |
| 3B (+ cross family) | All gates pass with stronger margins. |
| 4 (transfer test) | 0/10 elites transfer to a different target. |
| α-sweep | Parsimony does not reduce ρ(length, val); it raises it. |
| 5A / 5B (multi-target) | Two-target averaging fails to restore transfer and breaks search at this budget. |

The clean V5 finding that motivates V6: in the V5A archive, longer
genomes transferred *better* (Spearman ρ = −0.75, p = 0.012 between
length and held-out val_B). This is consistent with each `fit` step
re-anchoring on whatever target is active, so longer genomes accidentally
behave more like functions of F. V6 asks whether explicitly training
under a *distribution* of targets converts this incidental behaviour
into a robust property of the elite genomes.

---

## 2. The hypothesis

**H6 (falsifiable):** Under (a) a fitness signal computed across a
batch of targets sampled from a parametric distribution P, (b) a
compute budget comparable to v3-era single-target evolution, and
(c) the *same operator vocabulary* as v4-v5, the evolutionary search
will produce genomes whose median validation error on a held-out
8-target sample from P is below 0.5.

The threshold 0.5 is deliberately weak: val < 0.5 means the genome
produces a TT that fits the held-out target meaningfully better than
"predict zero." V5's transfer test had every elite at val_B > 0.85.
A median below 0.5 across a held-out 8-target batch would be
qualitative evidence of distributional learning.

**Stronger thresholds, for upgrade-path framing:**
- *Strong success:* median val_held-out < 0.1.
- *Moderate success:* median val_held-out < 0.5, **and** standard
  deviation across the held-out set < 0.3 (low variance ⇒ robust).
- *Marginal:* median < 0.5 but std > 0.3 (works on some but not all
  draws — ambiguous).
- *Failure:* median ≥ 0.5.

Pre-registered before running.

---

## 3. Design

### 3.1 Target distribution P

A 5-parameter parametric family of TT-rank-3 functions on the 8⁶ grid:

```
T(α, β, γ, k, p)(x_1,...,x_6) =
      α · sin^{⊗6}(2πkx/N)
    + β · cos^{⊗6}(2πkx/N)
    + γ · ((x/(N-1))^p − 0.5)^{⊗6}

with    α, β, γ  ~  U[-1.5, 1.5]   (continuous amplitudes)
        k        ~  U{1, 2, 3}     (frequency mode)
        p        ~  U{1, 2, 3}     (polynomial degree)
```

Properties:
- **True TT rank ≤ 3 for all draws** (sum of three rank-1 outer products).
- **F-values vary widely** with (α, β, γ): norms in val pool range
  from ~3 to ~25 across draws.
- **Functional form is fixed** — the GA only sees variation in
  amplitudes and integer modes, not in the basis itself.

**Question for review (Q1):** Is this family wide enough to be a
non-trivial distribution-learning test, but not so wide that the GA
is forced to learn equivariance over an intractable space? See §6 for
narrower and broader alternatives.

### 3.2 Training and held-out target sets

- **Training batch S_train** = 8 targets drawn from P with seed 1001.
  Frozen across the entire run; every genome is evaluated against
  the same 8 targets.
- **Held-out batch S_held** = 8 targets drawn from P with seed 2002.
  Used only at end-of-run, never during evolution.

Sample indices `X_TRAIN` (size 8192) and `X_VAL` (size 4096) are the
same as in v3-v5 — the only thing that changes is the F values for
each target.

**Question for review (Q2):** Should the held-out batch be drawn from
P (same family) or from P' (different family — e.g., Legendre-like)?
- Same-P held-out tests *within-distribution generalisation* — closer
  to standard ML.
- Different-P held-out tests *cross-family transfer* — closer to the
  v4 transfer test that originally killed the framing.
- Both could be reported as separate columns in the final table.

### 3.3 Fitness signal

For each genome G during evolution:
1. Apply G deterministically (genome-hash RNG seeding) to each of the
   8 training targets in S_train.
2. Record val_err on each target's held-out X_VAL samples.
3. **Fitness = median of the 8 val_errs.**

Median rather than mean because:
- The v5B mean-fitness collapsed search; median is more robust to
  one bad-luck target dominating the signal.
- Median better matches the success criterion (which is also median).

**Tracked diagnostics (not used for fitness):**
- Mean val across the 8.
- Standard deviation across the 8 (proxy for "how function-like is G").
- Per-target val (8-vector saved per archive cell).

**Question for review (Q3):** Median, mean, or low-quantile (e.g.,
80th percentile) as fitness? Median is the proposed default.
Low-quantile would push toward worst-case robustness.

### 3.4 GA setup

Same as v4-phase-3B except where noted:

| Parameter | v3-3B | v6 proposed |
|---|---|---|
| Operators | fit, grad, cross + structural | **Same** |
| Algorithmic families | 3 | 3 |
| Deterministic eval | yes | yes |
| Parsimony α | 0.002 | **0.001** (lighter; see §6 Q4) |
| MAP-Elites axes | (rank, err, fgr) | **Same** |
| POP × GENS | 30 × 35 | **40 × 50** |
| Total evaluations | 1050 | **2000** |
| Per-eval cost | ~0.4 s | **~3.2 s** (8 targets per genome) |
| Wall clock | ~6 min | **~106 min** |

Compute budget chosen to be roughly 2× v3-3B's effective evolutionary
work, accounting for the 8× per-eval cost.

**Question for review (Q4):** Light parsimony (α=0.001) or none (α=0)?
The α-sweep showed α=0 gives the lowest ρ(length, val). For v6 we
*want* longer genomes (more re-anchoring opportunities), but we also
want some pressure against runaway bloat. α=0.001 is a compromise.

### 3.5 Baselines

Three controls for fair comparison:

**Baseline B1 (single-target, matched total compute):**
POP=80, GENS=200 on a single target T_1 ∈ S_train. Same total
evaluations (16 000). If V6 finds genomes with val_held-out < 0.5 and
B1 does not, distributional training is providing the lift.

**Baseline B2 (V5A elites re-evaluated on S_held):**
Top-10 of V5A's archive (single-target on A, no distributional
training) re-scored on each of the 8 held-out targets. Establishes
"what a non-distributional baseline gives on this metric."

**Baseline B3 (random genomes):**
500 random genomes generated fresh, evaluated on S_held. Reports the
"do nothing" floor.

### 3.6 Success criteria (pre-registered)

**Primary outcome:** median val_held-out across V6's top-10 elites,
where each elite's val_held-out = median val across S_held.

```
H6 SUPPORTED if:    primary < 0.5
H6 STRONGLY SUPPORTED if:    primary < 0.1
H6 ROBUSTLY SUPPORTED if:    primary < 0.5 AND across-target std < 0.3
H6 NOT SUPPORTED if:    primary >= 0.5
```

**Secondary outcomes (informative regardless of primary):**
- Distribution of val across S_held per elite — looking for "robust"
  vs "lucky on most, bad on one" patterns.
- Spearman ρ(length, primary) — does the V5A finding (longer ⇒ better
  transfer) replicate when transfer is a training target?
- Family composition of elites — are mixed-family genomes more
  function-like?
- Comparison to B1: (V6 primary) / (B1 primary). >1 means
  distributional training helped; <1 means it hurt.

### 3.7 What v6 deliberately does **not** test

To keep the experimental space clean, v6 holds the following constant
relative to v3-3B:

- **Operator vocabulary** unchanged. If v6 succeeds with the same
  operators as v4-v5, the v5 framing is decisively corrected.
- **Functional genomes** not introduced. Operator parameters are still
  fixed at evolution time; they do not depend on target features. A
  positive v7 is the natural follow-up if v6 succeeds.
- **No curriculum.** All 8 training targets visible from gen 0. A
  curriculum (start with 1 target, expand to 4, then 8) might lift
  performance further but mixes with the distributional-training
  signal we're trying to isolate.
- **No structured anchoring.** Genomes can place fits anywhere in the
  sequence, not constrained to specific slots. A structured-anchoring
  variant is an obvious v6.5 if v6 partially succeeds.

---

## 4. Diagnostics

Tracked per-genome at archive admission:

```
{
  "genome": [...],
  "rank": int,           # max TT rank reached
  "fit_grad_ratio": float,
  "length": int,
  "fitness": float,      # median val across S_train (= the signal)
  "val_per_target": [v1, v2, ..., v8],  # full vector
  "mean_val": float,
  "std_val": float,
  "max_val": float,
}
```

End-of-run diagnostics:

1. **Across-target std distribution** of all archived elites.
   Hypothesis: distributionally-trained elites have lower std than
   single-target elites.
2. **Operator-position analysis.** Where in the sequence do `fit`
   ops appear? V5A elites had fits clustered at the end. V6 may push
   them to be more interspersed.
3. **Held-out matrix.** 10 elites × 8 held-out targets = 80-cell
   table of val_err. Column std (which targets are easy/hard) and
   row std (which elites are robust).
4. **Multi-anchor confirmation.** Replicate V5A's ρ(length, val) and
   ρ(n_F_aware, val) on the V6 archive's transfer to S_held.

---

## 5. Cost and timeline

```
Per-genome evaluation:
  8 targets × ~0.4 s/target  =  3.2 s

Total evolutionary work:
  POP × GENS × per-eval  =  40 × 50 × 3.2 s  =  6400 s  ≈  107 min

Baselines:
  B1 (POP=80, GENS=200, 1 target):  16 000 × 0.4 s  =  107 min
  B2 (rescore V5A top-10 on 8 targets):  10 × 8 × 0.4 s  ≈  32 s
  B3 (500 random × 8):  500 × 8 × 0.4 s  ≈  27 min

End-of-run held-out evaluation:
  10 elites × 8 held-out targets × 0.4 s  ≈  32 s

Total wall-clock:  ~3.5 hours single CPU (Windows 11, no GPU).
```

Acceptable. Long enough to be meaningful, short enough to fit a
session. If smoke-test reveals a bug, total budget could double.

---

## 6. Questions for review

The design has these open choices that I'd value input on before running.

### Q1. Target distribution P — too narrow, too wide, or right?

Proposed: 5 parameters, ~9 mode combinations × continuous amplitudes
≈ tens of thousands of effectively-distinct targets within rank ≤ 3.

| Tighter | Wider |
|---|---|
| Fix k=p=2; only α, β, γ vary | Add basis change: also draw f_1, f_2, f_3 ∈ {sin, cos, poly, gauss} |
| Keep amplitudes ∈ [-1, 1] | Mix sinusoidal, polynomial, AND Legendre families |

Tighter risks trivial memorisation; wider risks the same V5B-style
search collapse.

### Q2. Held-out distribution — same as P or different?

Proposed: same P, fresh seed.

Alternative: same family but with parameters extrapolated outside the
training range (e.g., α ∈ [1.5, 3.0]) to test out-of-distribution
generalisation.

Alternative: a different family entirely (Legendre, like v4 transfer)
to test cross-family transfer with distributional training.

I'd run *all three* if compute allows — 8 same-P, 8 OOD-P, 8 different-
family. Adds ~16 minutes to end-of-run evaluation.

### Q3. Fitness aggregator — median, mean, or low-quantile?

Proposed: median.

Alternative: 80th percentile (push toward worst-case robustness;
matches "make sure the elite works on hard draws").

Alternative: log-mean (geometric mean — penalises catastrophic single-
target failures).

Median is the safest default; low-quantile is the most ambitious.

### Q4. Parsimony — α = 0.001, α = 0, or something else?

Proposed: α = 0.001 (lighter than v3-era 0.002).

The α-sweep showed α=0 gives lowest ρ(length, val). For v6 we want
some length to allow re-anchoring; we don't want to penalise it too
hard.

Alternative: α = 0 with a hard length cap (max 12 ops).

### Q5. Should v6 include functional-genome features at all?

Proposed: no, hold them for v7.

Functional genomes are operators whose parameters depend on target
features (e.g., `fit(n = scaled_by_target_norm)`). They could be tested
in v6 as a parallel arm, doubling cost.

I think the cleaner experiment is to test distributional training
*alone* first. If v6 succeeds even partially, functional genomes are
an additive lift; if v6 fails, they become the natural v7.

### Q6. Compute escalation if v6 partially succeeds — pre-commit?

If v6 lands moderate success (median < 0.5 but std > 0.3), is the
right next step:
- Larger POP × GENS budget?
- Add curriculum staging?
- Switch to a functional genome?

A pre-commit on which lever to pull avoids drift after seeing the
data. My current preference: larger budget first (cheap, isolates
"is search converging?" from "is the design wrong?").

---

## 7. Next steps

### If design approved as-is

1. Implement `evolve_tt_v6.py` extending `evolve_tt_v4`'s deterministic
   evaluator to compute fitness over a batch of 8 targets per genome.
2. Implement target distribution P sampler with frozen seeds for
   training and held-out batches.
3. Smoke-test at POP=10, GENS=10 to verify pipeline integrity.
4. Run baseline B1 in parallel (different process, single target, large
   budget).
5. Run V6 main experiment (~2 hours).
6. Run end-of-run held-out evaluation matrix.
7. Write `whitepaper_v6.md`.

### If H6 strongly supported

V7 candidates:
- **Functional genome:** parameters of operators bind to target
  features (norm, sample variance, dominant frequency).
- **Cross-family transfer:** does V6-trained-on-P transfer to a
  Legendre-like family without retraining?
- **Charon-domain target:** real LMFDB slice (e.g., EC × CM-disc ×
  torsion × nbp) as the test of program-class scaling.

### If H6 moderately supported

V7 candidates:
- **Curriculum staging:** A → A+C → broad-P, with clear gen-budget
  per stage.
- **Structured anchoring:** restrict `fit/grad/cross` to specific slots
  (e.g., one mid-genome, one end-genome) and let structural ops fill
  the rest.
- **Variance-as-fitness:** explicitly minimize std across S_train.

### If H6 fails

V7 candidates:
- **Functional genome as the actual remedy** (rather than additive lift).
- **Operator-vocabulary revision:** introduce target-agnostic primitives
  that genuinely change the search space.
- **Closure of the playground** with a clearer "dead end" finding —
  vocabulary blame would then be partially upheld.

---

## 8. Pre-registration commitments

To prevent post-hoc cherry-picking:

- Primary outcome (median val on S_held over top-10 elites) is fixed
  before the run.
- Success thresholds (0.5 for "supported", 0.1 for "strongly", with
  std<0.3 for "robust") are fixed before the run.
- Diagnostic patterns (length-val, n_F_aware-val correlations) will be
  reported regardless of direction.
- The held-out target seed (2002) is fixed and will not be redrawn.

If V6 partially succeeds and a follow-up experiment is run with the
same data, the new experiment will be pre-registered with the same
discipline.

---

## 9. File / artefact plan

Files to be created upon execution:

```
evolve_tt_v6.py            # multi-target distributional evolution
v6_targets.py              # P sampler; frozen training and held-out batches
archive_v6.json            # final archive
v6_baselines.json          # B1, B2, B3 results
v6_held_out_matrix.json    # 10 elites × 8 targets val_err matrix
run6.log                   # run transcript
whitepaper_v6.md           # results paper
```

Master seed for V6 evolution: 46 (continuing the per-phase pattern).
Target-distribution seeds: 1001 (training), 2002 (held-out).

---

## 10. Summary

V6 is a single-experiment test of a single hypothesis: that *training
signal*, not *operator vocabulary*, is the binding constraint on
producing transferable proof skeletons in this playground.

The design holds the operator vocabulary fixed at v4-v5 levels and
varies only the training regime — from "single target" to "median
across a batch of targets sampled from a parametric family."

It is pre-registered, budget-matched against a single-target baseline
of equal compute, and includes a held-out distribution that the
evolution never sees.

Outcome thresholds are fixed in advance. Either H6 holds and v5's
"vocabulary is the wall" framing is corrected, or H6 fails and the
case for vocabulary-level revision tightens further.

Awaiting review on Q1-Q6 before execution.

*— Charon*
