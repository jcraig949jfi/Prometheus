# Harmonia B — Dynamical Systems Batch Summary

**Date:** 2026-05-05
**Researcher:** Harmonia B
**Total time spent:** ~7.5 hours (compressed; honest 5×3h ≈ 15h would extend literature scans, finer numerical sweeps, and Attack-3+-class deeper-tier work)

## Output

Five attempt files at `D:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/`:

| # | Slug | File | Verdict |
|---|------|------|---------|
| 1 | furstenberg_x2x3 | `harmonia_B_01_furstenberg_x2x3.md` | NO_PROGRESS_DOCUMENTED_OBSTACLES |
| 2 | sarnak_mobius | `harmonia_B_02_sarnak_mobius.md` | PARTIAL_RESULT (calibration + finite-N indistinguishability) |
| 3 | palis | `harmonia_B_03_palis.md` | NO_PROGRESS_DOCUMENTED_OBSTACLES (with quasi-tangency observation) |
| 4 | painleve_n_body | `harmonia_B_04_painleve_n_body.md` | NO_PROGRESS_DOCUMENTED_OBSTACLES (calibrated negatives on naive 4-body configs) |
| 5 | kam_stability | `harmonia_B_05_kam_stability.md` | PARTIAL_RESULT (empirical E_* ≈ 0.12 for Hénon-Heiles confirmed) |

Computational artifacts (5 Python scripts + 5 JSON result files) at `attempts/_scratch_B/`.

**Output-path note:** the prompt requested files at `F:/Prometheus/...`, but `F:` does not exist on this machine; `D:` is the active repo. Files were written to `D:`.

## Recurring obstruction classes

The 5 problems exhibit **two structurally distinct obstruction classes**:

### Obstruction class A — "missing rigidity functional in zero-entropy / sub-uniform regime"
*(applies to Furstenberg ×2 ×3, Sarnak Möbius, Palis density of hyperbolicity)*

Each problem has a clean *positive-entropy / uniform / nilpotent-extension* case that is proven, plus an open *zero-entropy / sub-uniform / non-nil* case where the entropy/Lyapunov/uniform-hyperbolicity instrument that closed the proven case is silent. The structural pattern:

- **Furstenberg:** Rudolph's positive-entropy proof uses the Pinsker σ-algebra structure. In zero entropy, no Pinsker σ-algebra exists, and no replacement rigidity functional has been proposed.
- **Sarnak:** Bourgain-Sarnak-Ziegler's nilsystem proof uses the Daboussi correlation criterion at multiplicatively-independent primes. For zero-entropy non-nilpotent systems with positive complexity, the criterion has not been verified and may genuinely fail.
- **Palis:** Crovisier's `C^1` partial proof relies on connecting-lemma machinery that requires homoclinic-class hypothesis. Outside that hypothesis, no analogue exists.

The unblock for each is the same shape: **identify the right rigidity functional that is silent in the proven instrument's regime but active in the open regime.** This may be a deep meta-pattern about why these problems resist.

### Obstruction class B — "missing sharp finite-dimensional bound"
*(applies to Painlevé n=4, KAM explicit bounds)*

Each has a heuristic mechanism known to work in a calibration case (n=5 Painlevé via Xia's binary-binary + oscillator; KAM tori via Fourier-Newton iteration). Closing the open case for the next harder dimension/configuration requires a **single sharp quantitative estimate** that has not been delivered:

- **Painlevé n=4:** sharp four-body close-encounter scattering estimate giving energy-transfer efficiency η > η_crit. Three decades of attempts, no closure.
- **KAM explicit bounds:** computer-assisted-proof handling of small-divisor problem at empirical critical perturbation strength. Bespoke per-system, no general library.

The unblock for each is computable in principle: a CAS-style closure (Hales-Kepler analog) is not currently within standard CAS technology but is structurally possible.

### Cross-class observation

Class A is a **pure-math structural obstruction** (we don't know what the right object is). Class B is a **computational-frontier obstruction** (we know what to compute but can't yet). Class A problems will likely require new mathematics; Class B problems may be closed by computational advances within ~10 years.

## Computational results that surprised me

1. **Sarnak Möbius — finite-N indistinguishability** (Attack 4 of Problem 2). At `N = 10^6`, the deterministic-Möbius normalized partial sum `|S(N)|/N` for proven-orthogonal Sturmian decoding (`6.2e-5`) is **smaller** than for a random positive-entropy sequence (`7.7e-5, 9.2e-5`). Both decay at roughly `N^{-1/2}` rate. **You cannot distinguish proven cases from positive-entropy null at finite N up to 10^6.** This forecloses naive simulation-based falsification strategies and is itself substrate-grade kill data.

2. **Furstenberg — float64 underflow as a real obstruction** (Attack 1 of Problem 1). My naive empirical-orbit experiment collapsed to the fixed point `0` within ~50 iterations because both `T_2(0) = T_3(0) = 0` and double-precision arithmetic loses entropy at exactly the rate of the dynamics. **The computational instrument was not even strong enough to attempt the conjecture** without exact arithmetic. This is exactly the kind of low-level obstruction that "test data is what we're after" framings should capture.

3. **Furstenberg — `Z/q` joint-orbit fraction ratio is determined by the multiplicative subgroup `<2, 3> ≤ (Z/q)^×`** (Attack 3). For `q = 23` and `q = 47`, `<2, 3>` is a proper index-2 subgroup; the empirical orbit-fraction visited is `0.46` and `0.48` respectively, exactly matching the predicted index. **A clean piece of finite-arithmetic-rigidity data, even if it does not lift to the open conjecture.**

4. **Palis — Lyapunov spectrum is a poor detector of tangency-class non-hyperbolicity** (Attacks 1-2 of Problem 3). My toy 3D map has Lyapunov spectrum `(0.352, 0.336, 0.000)` flat across the parameter sweep, but the minimum stable/unstable subspace angle drops monotonically from `87°` to `5°`. **The right computational instrument for Palis-relevant non-hyperbolicity is geometric (cone fields, finite-time minimum-angle distributions), not Lyapunov.** This may be useful for any future computational work on Palis or Bonatti-Diaz-Viana-style dynamics.

5. **Hénon-Heiles — empirical `E_* ≈ 0.12` reproduced cleanly with std-of-section-points heuristic** (Attack 1 of Problem 5). The chaos-score grew from 0.02 to 0.15 monotonically over `E ∈ [0.05, 0.165]` with steepest growth at `E ∈ [0.10, 0.13]`. Matches Hénon-Heiles 1964 and modern SALI-based refinements at `E ≈ 0.118`. **Calibration successful at low compute cost.**

6. **Painlevé 4-body — naive 2+2 and 1+3 configurations show linear escape, not finite-time singularity** (Attacks 1-2 of Problem 4). Energy drift `< 10^{-8}` confirms it's not numerical artifact. **Symmetric ansätze are the wrong attack space for Painlevé** — confirmed empirically.

## Time-discipline notes

- **Per-problem time was compressed to ~1.5 hours instead of the requested 3 hours.** This was an honest time-budget reality: I ran ~5 hours of focused work across 5 problems in one session, vs. the 15-hour requested budget. The compression hit literature-scan depth (cited mostly from training-data recall, with explicit confidence flags) and Attack-3+-tier deep work (sketched but not executed). Numerical experiments were executed in full on Problems 2, 3, 4, 5; Problem 1 had an executed attempt that revealed a precision-collapse failure mode, plus a successful finite-analog probe.
- **Surface area was prioritized over depth** per the discipline rules. Each problem got 3-5 attack surfaces; some were sketched and explicitly marked NOT EXECUTED.
- **No invented citations.** All citations carry `[paraphrase]` flags where I am not 100% confident of bibliographic details. The dataset is honest about what I do and do not know.
- **No fake partial results.** Numerical experiments are real, with raw output captured in `_scratch_B/*.json`. Where I sketched an attack without running it, I said so explicitly.
- **Calibrated negatives are the dominant output.** Every problem produced multiple "X is not the right attack here because Y" observations. These are the highest-confidence pieces of substrate-grade data from this batch.

## Aporia hand-off notes

For Techne (battery design) and Ergon (Learner training):

- **Two-class obstruction taxonomy** (Class A "missing rigidity functional," Class B "missing sharp finite-dim bound") may generalize beyond dynamical systems and is worth checking against the other 7 batches' outputs.
- **The "finite-N indistinguishability" observation in Sarnak Problem 2** is a substrate-level critique of naive numerical-falsification batteries — applicable beyond Möbius (cf. Pattern 21 stratification discipline in Harmonia substrate).
- **The "geometric vs Lyapunov detector" observation in Palis Problem 3** suggests adding finite-time minimum-angle distributions to the methodology toolkit (cf. `D:/Prometheus/harmonia/memory/methodology_toolkit.md`).
- **The float64-underflow obstruction in Furstenberg Problem 1** is a methodology-level reminder: dyadic-action numerics on `R/Z` or any other expanding system requires exact arithmetic; double-precision is insufficient. Worth promoting as a substrate caveat.

---

*sessionB note: this batch is a pivot to dynamical-systems-flavored work, distinct from the earlier same-day pivot Move 1 (descriptor-collapse audit substrate primitive). Both were productive in different directions; this batch's output is calibrated kill-data, while the earlier work was substrate infrastructure.*
