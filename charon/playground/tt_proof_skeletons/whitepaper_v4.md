# Evolving Proof Skeletons on Tensor-Train Decompositions, v4

**Transfer test collapses the thesis. α-sweep invalidates Gate 4. Two kills that matter more than every PASS in v3.**

---

**Author:** Charon (Claude Opus 4.7, 1M context), Project Prometheus
**Date:** 2026-04-23
**Status:** Playground experiment. Seven runs total, plus a retrospective
rerun, a cross-target transfer test, and a parsimony α-sweep.
**Supersedes:** `whitepaper.md` (v1), `whitepaper_v2.md` (v2),
`whitepaper_v3.md` (v3).
**Working dir:** `charon/playground/tt_proof_skeletons/`

---

## 0. Why v4 supersedes v3

V3 reported five passing gates, a 4-operator fully-load-bearing skeleton,
and a monotone-improving trajectory across phases 1–3B. The paper
concluded the machinery produced "reproducible, irreducible skeletons"
and framed the next questions as transferability and α-sweep.

Both experiments have now been run. Both land honest kills on v3's
headline claims:

1. **Transfer test:** 0 / 10 phase-3B top elites achieve a meaningful fit
   on a different target (Legendre-like rank-4). Median B/A ratio 107×;
   every elite is functionally useless outside the target it was evolved
   against. The 4-op "skeleton" fares no better than the 13-op chain.
2. **α-sweep:** Increasing parsimony pressure does not reduce Gate 4's
   ρ(length, val_err) correlation. It *increases* it, from ρ=0.15 (p=0.31)
   at α=0 to ρ=0.57 at α=0.02. Gate 4 in its current form does not
   measure what v2/v3 claimed it did.

V3's machinery is still valid and reproducible. Its *interpretation* is
not. The "proof skeleton" framing is falsified on this target.

---

## 1. The transfer experiment

### 1.1 Setup

Target A (all prior phases):
```
f(x_1,...,x_6) = sin^{⊗6}(2πx/N) + cos^{⊗6}(2πx/N) + (x/(N-1))^{2 ⊗6}
True TT rank = 3. Sinusoidal + polynomial basis.
```

Target B (new):
```
f(x_1,...,x_6) = sum of 4 Legendre-like polynomial outer-products
True TT rank = 4. Orthogonal-polynomial basis on [-1, 1].
```

Same D=6, N=8 grid. Same sample indices X_TRAIN, X_VAL (only the F values
differ). Top-10 elites from phase 3B (`archive_v5.json`) are re-evaluated
on target B deterministically. No re-evolution, no fine-tuning. Just:
take the sequence that worked on A, apply it to B, measure val_err.

### 1.2 Results

```
# rank_A len  val_A     val_B     B/A    fgr     first 4 ops
1  6    8    7.77e-03  1.19e+00  153    0.67   [compress, cross, reseed, reseed, ...]
2  4   11    8.19e-03  1.39e+00  169    0.40   [grad, refine, symmetrize, refine, ...]
3  4    4    8.99e-03  1.63e+00  181    1.00   [reseed, symmetrize, fit, fit]
4  5    7    9.21e-03  8.55e-01   93    0.67   [compress, cross, perturb, reseed, ...]
5  8   13    1.07e-02  1.16e+00  108    0.40   [reseed, compress, symmetrize, compress, ...]
6  3    7    1.18e-02  1.17e+00   99    0.67   [cross, reseed, fit, rerank, ...]
7  4    6    1.23e-02  1.10e+00   89    0.67   [grad, refine, reseed, fit, refine, fit]
8  8    7    1.26e-02  3.70e+00  293    0.67   [cross, perturb, rerank, rerank, ...]
9  7    9    1.39e-02  1.47e+00  106    1.00   [reseed, compress, refine, fit, ...]
10 6    9    1.68e-02  1.28e+00   76    0.40   [reseed, compress, symmetrize, compress, ...]
```

All val_B > 0.85. val_B > 1.0 means the TT prediction is worse than zero
(the predictions point in the wrong direction relative to target). 9 of
10 elites are in this regime. Median B/A ratio = 107×.

### 1.3 What this means

The operators that were "fully load-bearing" on target A are fully
ineffective on target B. Four observations:

1. **Length does not predict transferability.** The 4-op skeleton (#3)
   and the 13-op chain (#5) both fail. Transfer is roughly uniform across
   length.
2. **Family composition does not predict transferability.** fgr=1.00
   (all-fit) and fgr=0.40 (mixed) elites both fail. The worst (elite #8)
   and third-best (elite #3) both have fgr values in the mid range.
3. **The clean minimal skeleton is NOT the most transferable.** Elite #3's
   `[reseed, symmetrize, fit, fit]` had val_A=9e-3, val_B=1.63 — one of
   the worst transfers.
4. **"Load-bearing under ablation" ≠ "captures generalizable structure."**
   Every operator in the phase-3B top-3 is strictly needed for the
   sequence to hit val_A ≈ 8e-3, but the sequence as a whole contains no
   information that generalises to a different function.

The reason, structurally, is that the operators' *effect* is parameter-
specific. `fit(n=8192, iters=2)` on target A produces a TT whose core
values solve LS against A's F array. The same genome run on B produces
cores solving LS against B's F array — but the INTERMEDIATE states
(produced by `rerank`, `reseed`, `compress`, etc.) no longer lie on A's
loss surface. Ops that were good warm-start or good rank-budget on A
become uncorrelated with good-on-B.

### 1.4 What the playground has actually shown

Not: *proof-skeletons of mathematical reasoning*.
Actually: *evolved numerical recipes specific to one F-valued tensor*.

This is closer to "the GA found a sequence of (ALS, SGD, SVD) operations
that happens to produce a good fit on this one function" than to "the
GA found a reasoning chain that decomposes tensors in general." The
operators are algorithmic primitives, and the genome specifies a
particular schedule of them tuned to one target's loss surface.

That is still an interesting artefact — the search does find non-trivial
schedules that perform well on one target — but it is not the
proof-skeleton programme as originally framed. Transfer is the test that
distinguishes the two, and the test failed cleanly.

---

## 2. The α-sweep: Gate 4 is broken

### 2.1 Setup

Six values of the parsimony penalty α in `adjusted = train_err + α · length`,
each with POP=20, GENS=20, two-family (fit + grad). Seeds reset between
runs so each α starts from matched initial conditions.

### 2.2 Results

| α | ρ(length, −log₁₀ val_err) | p | best_val | mean_len |
|---|---|---|---|---|
| 0.000 | **+0.15** | 0.31 | 3.79e-03 | 6.7 |
| 0.001 | +0.47 | 0.001 | 4.98e-03 | 6.6 |
| 0.002 | +0.55 | <0.001 | 8.88e-03 | 6.3 |
| 0.005 | +0.53 | <0.001 | 8.88e-03 | 6.3 |
| 0.010 | +0.51 | <0.001 | 9.42e-03 | 5.7 |
| 0.020 | +0.57 | <0.001 | 1.59e-02 | 4.3 |

Three surprises:

1. **α=0 has the lowest ρ.** With no parsimony pressure, length is
   essentially uncorrelated with val_err (p=0.31, not significant).
2. **Any positive α makes ρ worse.** The correlation jumps immediately to
   0.47 at α=0.001 and stays in 0.5–0.57 range for all larger α.
3. **Mean length responds to α as expected.** 6.7 at α=0 → 4.3 at α=0.02.
   Parsimony does shorten genomes, but it does so by pruning *short-and-
   mediocre* cells less aggressively than *long-and-good* cells,
   strengthening the length→fitness relationship in the surviving
   archive.

### 2.3 What Gate 4 actually measured

Gate 4 was formulated as: "ρ(length, val) should be small, otherwise
axes are redundant and the GA is compensating by chaining ops."

The α-sweep reveals that ρ in a parsimony-filtered archive reflects the
filter's admission logic more than the GA's search dynamics. At α=0,
archives contain many length-error combinations at each (rank, err_bin,
fgr_bin) cell — the cell-best is chosen on raw train_err, and there is
no systematic length pressure. ρ is small because the *filter* does not
shape the length distribution.

Adding parsimony means "a shorter genome with comparable train_err wins
the cell over a longer one." The surviving cells are then length-minimal
for their quality class. Since short genomes can't reach as low val_err
as long ones (expressive-power ceiling), the archive's length and
val_err become systematically coupled.

Gate 4 with parsimony filtering measures the coupling *induced by the
filter*, not the coupling *produced by the search*. Turning parsimony on
to "weaken length-compensation" strengthens the metric meant to detect it.
That is a construct-validity failure, not a tuning issue.

### 2.4 What should replace Gate 4

Two candidates, neither yet tested:

- **ρ measured on population, not archive.** Track (length, val) for
  every genome evaluated during evolution, not just the cell-best ones.
  This separates GA dynamics from filter artefacts.
- **Normalise val_err by length before archiving.** Define adjusted
  success = val_err^(1/length) or similar, and measure ρ on that. Any
  residual correlation would be dynamics-driven.

Both are out of scope for this paper; noted for future work.

---

## 3. Revised synthesis across all experiments

The full table of phases, now with transfer and α-sweep columns:

| Phase | Best val_A | Gate set | Diagnoses | Transfer (val_B) |
|---|---|---|---|---|
| 1 (oracle) | 1.05e-14 | n/a | oracle artefact | n/a |
| 2A (1-fam) | 1.75e-02 | FAIL Gate 1 | diversity collapse | n/a |
| 2B (2-fam, stoch) | 5.89e-03 | FAIL Gate 4 | length compensation | n/a |
| 2B det rerun | — | (gates re-scored) | v2 fragility 50% noise | n/a |
| 3A (det + parsimony) | 1.34e-03 | PASS all | — | not tested |
| 3B (+ cross) | 7.77e-03 | PASS all | "skeleton quality" | **0 / 10 transfer** |
| α-sweep | — | — | Gate 4 metric broken | — |

The "monotone improvement across phases" story in v3 holds on *within-
target* metrics only. Once a second target is introduced, the phase-3B
elites do no better than random genomes would on the new target. The
phase-1-through-3B progression is a progression in *target-A-specific
fit quality*, not in any claim about reasoning, skeletons, or
transferability.

### 3.1 What's real

- The machinery works. Deterministic evaluation gives reproducible
  fitness. MAP-Elites archives fragment into diverse operator sequences
  under multi-family vocabularies.
- Numerical optimization on a fixed sample set can be done via evolved
  operator sequences, and the sequences can look short and clean (4 ops
  for a rank-4 fit).
- The gate framework produced three genuine kills across the sequence
  (v1 claim about diversity generalising, v2 claim about fragility being
  real, v3 claim about ρ being suppressible). Each kill was useful even
  when the resulting paper had to be rewritten.

### 3.2 What's not real

- "Proof skeletons" as a descriptor for these sequences. The transfer
  result is definitive: no capture of cross-target structure.
- "Reasoning style diversity" as a claim that can be supported by
  operator-histogram or edit-distance clustering in this setup.
- "Length-compensation suppressed by parsimony" — the α-sweep shows the
  opposite direction.

### 3.3 What we actually learned

1. **Deterministic evaluation is mandatory.** V2's stochastic fitness was
   50× noisier than its archive suggested. Every claim about sequence-
   level structure needs reproducible fitness, not one-shot lucky draws.
2. **Target-specific ops don't compose into transferable strategies.** A
   sequence of `fit/grad/rerank/compress/reseed` calls produces a result
   that's only meaningful on the target it was fit against. The
   operators' semantics are parameter-specific, not structural.
3. **Parsimony is not the right tool for length-compensation.** It
   reshapes the archive in ways that correlate length with quality. A
   different instrument is needed if length-compensation is the target
   of the diagnosis.
4. **Gate validity needs its own scrutiny.** A gate that passes after a
   fix may be measuring something different than the gate that failed
   before the fix.

---

## 4. What a genuine proof-skeleton programme would require

V4's kill suggests the core premise — that GA + MAP-Elites on TT
transformation sequences produces mathematical reasoning primitives — is
not achievable with this operator vocabulary. The operators are
numerical-optimization primitives, not reasoning primitives. Their
effect depends on target values, not on target structure.

For the programme to produce transferable skeletons, the operator
vocabulary would need to include transformations whose effect is defined
*structurally*, not value-wise. Candidates:

- **Basis-change operators.** Fourier, wavelet, Legendre transforms on
  the cores. These preserve rank and structural properties regardless of
  target.
- **Symmetry operators.** Permute modes, invoke group actions, enforce
  invariance under a declared symmetry. Target-agnostic.
- **Rank-flow operators.** Moves that change the rank profile (not just
  maximum rank) in specified ways — e.g., distribute bond dimension or
  rebalance.
- **Gauge-fixing operators.** Canonicalise the TT into a specific form
  (left-canonical, mixed-canonical, vidal). Target-agnostic structural
  operations.

A genome built from these would describe a *schedule of structural
transformations*. Whether such a schedule can approximate a target as
well as a value-tuned one is an open question. But *if* it could, it
would be target-structure-driven rather than target-value-driven, and
the transfer test would not obliterate it.

That is a larger programme than this playground. The most concrete
immediate step would be an augmented operator set with at least one
target-value-free operator, and a transfer test comparing its behavior
to the value-based v3 operators.

---

## 5. Final limitations + future work

Limitations above the playground level:

1. The transfer test used one target B. A broader test set would confirm
   that the failure is general, not B-specific.
2. α-sweep used POP=20, GENS=20 — smaller than v3's budget. Larger
   budgets might shift the ρ values but probably do not reverse the sign
   of the α-effect.
3. The "parameter-space diversity" concern from v3 was not addressed —
   but if operators are target-specific at the parameter level, the
   diversity debate is moot.

Honest future work:

1. **Target-agnostic operator vocabulary.** Design and test a genome
   from basis-change + symmetry + gauge operators only. Transfer test
   should show sequences that fit A and B at comparable error. Or,
   equivalently, confirm that target-agnostic sequences cannot fit
   value-based targets at all — which would be a clean negative result
   on a second dimension.
2. **Population-level ρ as a Gate-4 replacement.** Measure ρ over every
   evaluated genome, not archive-admitted ones. Test whether the
   construct-validity failure diagnosed above survives a correct metric.
3. **Multi-target transfer matrix.** Evolve on A, test on {B, C, D}
   with varying basis and rank. Track which elites generalise to some
   targets and not others, if any.

Out of scope: symbolic / creative telescoping / proof verification — all
blocked on the transfer failure.

---

## 6. File inventory and reproducibility

```
evolve_tt.py             Phase 1 (oracle, 1-family + ansatz)
evolve_tt_v2.py          Phase 2A (1-family, stochastic eval)
evolve_tt_v3.py          Phase 2B (2-family, stochastic eval)
evolve_tt_v4.py          Phase 3A/3B (deterministic + parsimony)
sanity_fit.py            ALS convergence diagnostic
rerun_gates.py           Deterministic re-score of v2/v3 archives
transfer_test.py         Cross-target evaluation on Legendre B
alpha_sweep.py           Parsimony α sweep

archive.json             Phase 1 archive (39 cells)
archive_v2.json          Phase 2A archive (47 cells)
archive_v3.json          Phase 2B archive (45 cells)
archive_v4.json          Phase 3A archive (70 cells) + gates + minimal probe
archive_v5.json          Phase 3B archive (64 cells) + gates + minimal probe
transfer_B.json          Transfer-test results, 10 elites on target B
alpha_sweep.json         α-sweep ρ values

run1..5.log, transfer_B.log, alpha_sweep.log   run transcripts
rerun_gates.log          retrospective deterministic rerun

whitepaper.md            v1
whitepaper_v2.md         v2
whitepaper_v3.md         v3 (superseded)
whitepaper_v4.md         This file
```

Master seeds per phase: 42 (P1), 43 (P2A), 44 (P2B), 45 (P3A/P3B).
Sample pool seed = 777 invariant across all phases. Alpha-sweep reuses
seed 45 per run, resets between α values.

Target A and Target B are deterministic given D=6, N=8. Their definitions
are in `evolve_tt_v4.py` (A) and `transfer_test.py` (B).

Wall clocks: P1 36s, P2A 155s, P2B 245s, P3A 785s, P3B 367s, rerun
~20min, transfer ~1min, α-sweep ~15min total.

All v3-era archive claims should be read as target-A-specific. Transfer
and α-sweep results override v3 interpretations where they conflict.

---

## 7. Conclusion

The phase-3 machinery works: deterministic, reproducible, able to
evolve compact sequences of TT operators that achieve good fits on a
fixed target. The skeletons it produces are short (4 ops) and every
operator is individually load-bearing under ablation.

What the machinery *doesn't* do: produce sequences whose structure
transfers to a different target. What v4 adds to the story is that
this is a structural property of the operator vocabulary, not a
tunable parameter. Target-value-based operators produce target-
specific skeletons, even when the skeleton looks clean.

Parsimony as a tool for length-compensation is the wrong tool. The
α-sweep shows ρ grows under parsimony rather than shrinks — a
construct-validity failure in v3's Gate 4 analysis.

The honest kill count for the v4 cycle:

- v3 claim "reproducible irreducible skeletons indicate something
  generalisable": **killed outright.** Transfer test shows zero of
  ten elites transfer. The skeletons encode target values, not target
  structure.
- v3 claim "parsimony compresses Gate 4's length-error correlation":
  **killed by α-sweep.** The relationship is roughly the opposite.
  Gate 4 as formulated with parsimony filtering measures the filter,
  not the search.

What survives the v4 cycle:

- Deterministic evaluation via genome-hash seeding is the correct
  methodology.
- MAP-Elites + GA can produce diverse operator sequences when the
  vocabulary spans multiple algorithmic families. Diversity is real,
  even if what it diversifies is target-specific.
- The gate framework itself remains useful — it produced three
  successive kills that each tightened the claim space.

Kill count for this playground: four substantial claims buried in
their own falsification trails. That is the playground's real output.
The proof-skeleton programme, as framed, does not generalise on this
setup. A serious version would need a structurally-defined operator
vocabulary, not a value-tuned one.

*— Charon*
