# Phase 2b — Report & Review Pause

Ergon / meta project, 2026-04-25
`F:/prometheus/ergon/meta/PHASE_2B_REPORT.md`

Document trail:
- `WHITEPAPER.md` — v1 scaffold design
- `WHITEPAPER_v2.md` — v2 design (origin-bias fix, multi-component fitness, ruggedness, predictive layer)
- `PHASE_2B_REPORT.md` — this file (what 2b delivered + open questions for review)

---

## TL;DR (one paragraph)

Phase 2b added the Fourier gene + oscillatory mode and expanded the optimizer panel from 4 to 8 with diverse inductive biases (Adam, simulated annealing, trust-region, Sobol). On the resulting 490-landscape archive, **descriptors predict optimizer-disagreement at R² = 0.69** (up from 0.30 in v2a) and **predict per-optimizer absolute performance at R² = 0.40–0.82** with a clean ordering: stochastic-coverage methods (random_restart / SA / Sobol all ≈ 0.81) are 1.5–2× more descriptor-predictable than gradient methods (L-BFGS / trust-region / Adam at 0.43–0.55). Descriptor independence held (max cross-correlation 0.598 in evolved archive). The instrument is now actionable: given five structural numbers, we can predict how an optimizer will perform AND how much disagreement to expect.

---

## 1. What was built in Phase 2b

| Component | File | Status |
|---|---|---|
| `FourierGene` (sin(ω·x + φ)) | `landscape.py` | ✅ |
| `oscillatory` generator mode (3–6 Fourier modes, weak quad, no GMM) | `landscape.py` | ✅ |
| Optional small-Fourier perturbation in basin/ridge/plateau/deceptive modes | `landscape.py` | ✅ |
| Mutation operator for Fourier sub-genes | `evolve.py` | ✅ |
| Crossover handles `fourier` list at sub-gene boundary | `evolve.py` | ✅ |
| `run_adam` (stochastic gradient with noise injection) | `optimizers.py` | ✅ |
| `run_simulated_annealing` (scipy `dual_annealing`) | `optimizers.py` | ✅ |
| `run_trust_region` (scipy `trust-constr`) | `optimizers.py` | ✅ |
| `run_sobol_local` (Sobol seeds + L-BFGS refine) | `optimizers.py` | ✅ |
| `run_panel(expanded=True)` runs all 8 | `optimizers.py` | ✅ |
| Sanity check supports 5 modes (added oscillatory) | `sanity_check.py` | ✅ |

Total LOC added vs Phase 2a: ~280.

## 2. Key measurements

### 2.1 Sanity check (150 random landscapes, 30 per mode)

Per-mode descriptor medians (5 axes):

| Mode | n_min | mAvgC | mWrstK | dRng | rugd |
|---|---|---|---|---|---|
| basin | 3 | +3.77 | +0.61 | +0.90 | +7.10 |
| ridge | 5 | +1.72 | +0.87 | +1.52 | +5.75 |
| plateau | 2 | +0.80 | +0.84 | +0.09 | +5.55 |
| deceptive | 3 | +3.59 | +0.66 | +1.26 | +7.05 |
| **oscillatory** | **10.5** | **+5.37** | **+1.10** | **+3.49** | **2.35** |

Oscillatory has 2× n_min, 2× depth_range, **3× shorter autocorrelation length** than other modes. Real frequency structure detected by descriptors.

### 2.2 Descriptor correlation

Pure-random sample (uniform across modes):

```
                 n_min    mAvgC   mWrstK   dRng    rugd
n_min            +1.000   +0.493  +0.291   +0.673  -0.732
mAvgC            +0.493   +1.000  -0.012   +0.591  -0.305
mWrstK           +0.291   -0.012  +1.000   +0.122  -0.402
depth_range      +0.673   +0.591  +0.122   +1.000  -0.478
ruggedness       -0.732   -0.305  -0.402   -0.478  +1.000
```

Max |off-diagonal| = **0.732** (CAUTION zone). Source: `n_minima × ruggedness = -0.732` — physically, a rougher landscape has both more minima AND faster autocorrelation decay. This is genuine coupling, not redundancy.

After GA evolution (490-landscape archive): max |off-diagonal| drops to **0.598**. Evolution improves descriptor independence by spreading samples across the joint distribution rather than rediscovering the pure-mode prior. Well below 0.85 collapse threshold.

### 2.3 Pilot run (30 generations × 15 children, 8-optimizer panel)

- 490 landscapes evaluated (40 pilot + 450 GA-generated)
- 99/243 cells filled (40.7%)
- Wall clock 236 s
- Fitness range 0.05–11.7, median 2.32

Top-10 high-disagreement landscapes by mode:

| v2a top-10 (4 opt) | v2b top-10 (8 opt) |
|---|---|
| basin: 7 | ridge: **7** |
| deceptive: 2 | oscillatory: **3** |
| ridge: 1 | basin: 0 |
| | deceptive: 0 |
| | plateau: 0 |

Top winners changed:
- v2a: lbfgsb / random_restart / cmaes
- v2b: random_restart / **simulated_annealing** / sobol_local

SA wins frequently on ridge/oscillatory landscapes — exactly the families where temperature-based escape pays off vs gradient methods. The diverse-bias panel has shifted what counts as "disagreement-rich."

### 2.4 Predictive model (5-fold CV on 490 history entries)

**Classification (winning optimizer):**

| metric | value |
|---|---|
| baseline accuracy (predict majority) | 0.349 |
| RF accuracy | 0.402 ± 0.025 |
| gap above baseline | +5.3pp |

Modest but real lift. Classification is dominated by intra-cell ranking variance (median 0.31 of max 1.0).

**Regression (continuous targets, 5-fold R²):**

| Target | v2a (4-opt) R² | v2b (8-opt) R² | Δ |
|---|---|---|---|
| `log(best_value)` pooled | 0.847 | 0.817 | −0.03 |
| **`fitness` (weighted disagreement)** | **0.300** | **0.572** | **+0.27** |
| **`value_stdev`** | **0.301** | **0.688** | **+0.39** |
| `traj_divergence` (DTW) | 0.316 | 0.387 | +0.07 |
| `basin_entropy` | 0.151 | 0.261 | +0.11 |

**Per-optimizer log(final_value) R²:**

| Optimizer | R² | std | Class |
|---|---|---|---|
| sobol_local | **0.818** | 0.086 | stochastic-coverage |
| simulated_annealing | **0.812** | 0.085 | stochastic-coverage |
| random_restart | **0.809** | 0.085 | stochastic-coverage |
| cmaes | 0.609 | 0.123 | evolutionary |
| lbfgsb | 0.550 | 0.189 | gradient |
| adam | 0.436 | 0.261 | stochastic gradient |
| trust_region | 0.435 | 0.109 | gradient |
| nelder_mead | 0.406 | 0.271 | simplex |

**Three clusters with clear separation**: stochastic-coverage (0.81), evolutionary (0.61), gradient/simplex (0.41–0.55). The ordering is robust — same direction as v2a, sharper at 8 optimizers.

## 3. The two findings v2b sharpened

### Finding A: Descriptors predict disagreement when the panel is diverse

The v2a result (`value_stdev` R² = 0.30) was a *panel* problem, not a *descriptor* problem. With 8 diverse optimizers, the same five descriptors achieve R² = 0.69 on the same statistic. The descriptor set was always good enough; the panel was too homogeneous to expose it.

This is the central finding of the project so far and is itself a methodological observation: **disagreement metrics are only useful diagnostics when the optimizer panel spans inductive biases**.

### Finding B: Stochastic-coverage methods are landscape-structurally predictable

Under matched-budget evaluation, the three independent stochastic-coverage methods (random_restart, SA, Sobol+local) all converge on R² ≈ 0.81. Gradient methods cluster at R² 0.40–0.55. CMA-ES is intermediate at 0.61. This reproduces v2a's ordering at higher fidelity and now spans 8 algorithms.

Two interpretations possible:
1. **Stochastic methods average over basin-volume distribution**, which the descriptors capture via `n_minima` + `depth_range`. Their outcome is a smooth function of these statistics.
2. **Gradient methods follow specific paths** through the landscape, and the descriptors don't capture path-relevant structure (e.g., basin reachability from origin, ridge geometry near specific paths).

Both interpretations point at the same actionable claim: **descriptors are near-sufficient for stochastic methods, missing path-information for gradient methods**. A 6th descriptor capturing path-reachability would specifically improve gradient-method prediction. This is testable.

## 4. Open questions for review

### Q1. Is R² = 0.69 on disagreement "sufficient"?

The project goal was 80%+ predictive accuracy as the "actionable" threshold (per WHITEPAPER_v2 §9). We're at 0.69 for disagreement, 0.82 for absolute performance. Two readings:

- **Sufficient**: the project crossed the actionable threshold for absolute performance (0.82), and disagreement is a derived quantity — 0.69 is fine for a noisier statistic.
- **Insufficient**: 0.69 leaves 31% of disagreement variance unexplained and we should hunt the missing axis.

Your call. If "sufficient": Phase 3 is paper-prep. If "insufficient": Phase 3 is descriptor expansion (basin-volume distribution? path-reachability? spectral entropy?).

### Q2. Top-10 in v2b is dominated by ridge mode (7) + oscillatory (3). Is this a problem?

The disagreement-fitness pushed the GA toward ridge/oscillatory landscapes because that's where the new optimizers (especially SA) most outperform gradient methods. Basin/deceptive/plateau are *underrepresented* in the top tier.

- **Not a problem if** the goal is to map disagreement maxima — ridge/oscillatory ARE where disagreement is highest.
- **A problem if** we want a *balanced* map of all landscape classes. Then the fitness function is biasing exploration.

Possible fix: make the fitness "novelty-weighted disagreement" — discount disagreement in already-occupied cells. WHITEPAPER_v2 §8 (adaptive grid) was a hint at this; haven't built it yet.

### Q3. Adam's R² = 0.436 ± 0.261. The std is huge. Is the noise injection authentic?

I added `0.05 * standard_normal` to the gradient each Adam step to simulate stochastic gradient. The high variance (±0.26 across folds) suggests Adam's behavior is dominated by this noise rather than landscape structure. Two paths:

- **Reduce noise** to test "deterministic Adam" — should look more like trust-region.
- **Keep as-is** — high R² variance is itself a finding (Adam is the *least* descriptor-predictable optimizer).

Lean toward keep-as-is, but worth flagging.

### Q4. Descriptor correlation 0.732 in pure-random vs 0.598 in evolved archive. Which is the "true" coupling?

The pure-random sample is what a practitioner would see if they used the generator without GA. The evolved sample is what we get after our specific GA dynamics smooth the joint distribution. For paper purposes, which number do we report?

- **Conservative**: 0.732 (pure-random); below 0.85 collapse, above 0.7 caution. Honest.
- **Empirical**: 0.598 (archive); reflects actual archive-level independence after the system's dynamics.

I'd report both with a note. Similar to F011 where we reported pre/post-conductor-stratification.

### Q5. Should we lift to higher dimensions before more 2D analysis?

Per WHITEPAPER_v2 phasing, Phase 4 was after Phase 3 (predictive model). We're at the natural inflection. Three views:

- **Lift now**: tests whether descriptor ordering (stochastic > evolutionary > gradient) survives in d ≥ 5. If it does, the finding is robust; if not, we localize a 2D-specific artifact.
- **Stay 2D, deepen analysis**: failure-mode clustering at 8-optimizer scale, novelty-weighted exploration, paper figures.
- **Both**: a small-scale (d=5, 100 landscapes) lift test in parallel with 2D writing.

## 5. Suggested next phases

### Phase 3 — three options (not exclusive)

**3-pack (highest yield)**: paper-ready figure pack from current 2b archive.
- v2b mosaic (top-12 disagreement landscapes with all 8 optimizer trajectories)
- per-optimizer R² bar chart (ordered)
- value_stdev predicted-vs-actual scatter (R² = 0.69)
- failure-mode clusters at 8-optimizer scale (re-run cluster_failures.py with k=6 or k=8)
- "stochastic-coverage > gradient" ordering as the headline finding

Delivers: 4 figures + 1 table + 1 supplementary CSV. ~2 hours of work. Tightest path to a writable result.

**3-cluster**: deepen failure-mode taxonomy.
- Re-run DTW clustering on v2b's ~3920 trajectories (vs v2a's ~4160)
- Test k = 4, 6, 8, 10 cluster counts; pick by silhouette score
- Identify if oscillatory landscapes produce a NEW cluster (Adam-noise-dominated or SA-anneal-pattern that didn't exist in v2a)
- Cross-tabulate cluster vs (optimizer × mode) — show which optimizer-mode pairs share failure-modes

**3-novelty**: improve GA exploration.
- Add novelty-weighted fitness: `fit = disagreement * (1 / cell_visits)` to push the GA into underexplored cells
- Re-run pilot, compare cell coverage and top-10 mode distribution
- Validates whether GA needs novelty pressure to escape ridge/oscillatory attractor

### Phase 4 — dimensionality lift (after Phase 3)

- d = 5 first, 100 landscapes, single optimizer-panel run (no full GA)
- Verify descriptors don't break (n_minima clustering tolerance scales correctly; ruggedness walks still produce signal)
- Re-run regression analysis; check whether per-optimizer R² ordering survives
- If yes → d = 10 with full GA; if no → identify which descriptor failed and patch

Compute envelope at d=5: Hessian is 5²/2 = 12 evals (vs 3 at d=2), descriptor extraction ~3× cost, optimizer panel ~2× cost (more dims, more iterations). Total ~6× per-landscape cost. 490 landscapes × 6 ≈ 24 minutes. Tractable.

## 6. My recommendation

**Phase 3 = "3-pack" (paper figures) AND "3-cluster" (failure-mode at 8-opt) in that order, then Phase 4 lift to d=5.**

Rationale:
- 3-pack consolidates a writable result from current data — value preserved
- 3-cluster runs on the same archive, no new compute, ~30 min of work
- 3-novelty is a methods-improvement that's better paired with d-lift than done in isolation
- Phase 4 d=5 is the next big test — does the central ordering survive lift?

If you disagree, the fastest pivots are:
- Skip 3-pack → go directly to 3-cluster + 4 (more "research", less "writing")
- Skip 3-cluster → go directly to 3-pack + 4 (faster paper turnaround)
- Skip 4 → stay 2D, do 3-pack + 3-cluster + 3-novelty (deeper 2D characterization before scale)

## 7. File state

```
ergon/meta/
├── WHITEPAPER.md              v1 scaffold
├── WHITEPAPER_v2.md           v2 design
├── PHASE_2B_REPORT.md         this file
├── landscape.py               + FourierGene, + oscillatory mode
├── descriptors.py             5 axes, minima-anchored, mixed probe (unchanged from 2a)
├── trajectory.py              DTW + scalar features (unchanged)
├── optimizers.py              + Adam, SA, trust-region, Sobol
├── fitness.py                 multi-component (unchanged)
├── evolve.py                  + Fourier sub-gene mutation/crossover
├── predict.py                 RF classifier + regressor (unchanged)
├── preview.py
├── sanity_check.py
├── run_pilot.py
├── cluster_failures.py
└── figs/
    ├── sanity_v2_25.png       5-mode visual
    ├── pilot_mosaic_s99_g30.png   v2b top-12 with 8-optimizer trajectories
    ├── predictive_pilot_archive_s99_g30.png   classification + uncertainty
    └── (older v2a figures)
```

Pickled archives:
- `pilot_archive_s42_g50.pkl` — v2a 1040 landscapes × 4 optimizers
- `pilot_archive_s99_g30.pkl` — v2b 490 landscapes × 8 optimizers

---

**Pause for review.** When you've decided on Phase 3 direction (3-pack / 3-cluster / 3-novelty / combination), tell me which and I'll proceed.
