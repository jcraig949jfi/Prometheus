# Evolving Optimization Landscapes

**A Meta-Math Instrument for Problem-Structure Research**

Ergon / meta project — initial design, 2026-04-23
`F:/prometheus/ergon/meta/WHITEPAPER.md`

---

## 1. Problem statement

Optimization research usually asks **"Which algorithm solves this problem?"**
This project inverts the question:

> **Given a family of problems, which structures make them hard, and why do optimizers disagree?**

Rather than evolving *solutions* on a fixed landscape, we evolve the *landscapes themselves*, binned by measurable structural properties, and measure how a panel of canonical optimizers responds. The artifact produced is not a better solver but a **map of problem-space with optimizer-behavior overlays** — a diagnostic instrument, not a generator.

---

## 2. Why this is useful

Fitness-landscape analysis, benchmark suites (CEC, BBOB), and no-free-lunch work have separately given us:

- catalogs of specific hard problems (Rastrigin, Rosenbrock, Schwefel…)
- statistical measures of landscape ruggedness (FLA literature)
- empirical rankings of optimizers on fixed corpora

What's missing is a **continuous-parameter, structure-labelled manifold** of landscapes across which we can ask:

1. *Which descriptor combinations cause algorithm A to fail while B succeeds?*
2. *Do different failure modes cluster in descriptor space?*
3. *Can we synthesize adversarial landscapes for specific solvers?*
4. *What structural axes are actually independent vs redundant?*

Answering (4) first gates the rest. Pilot results below show one axis we naïvely chose (basin Shannon entropy) is algebraically bounded by another (count of minima), forcing us to replace it before continuing.

---

## 3. Architecture

```
          ┌──────────────────────────────────────────────────┐
          │  tensor-parameterized landscape f: R^d -> R       │
          │    gene = {quad, ridges, gmm, mode}               │
          └───────────────┬──────────────────────────────────┘
                          │ evaluate(x)
                          ▼
┌─────────────────┐   multi-start   ┌────────────────────┐
│ descriptors.py  │◀───L-BFGS-B─────│ landscape.py       │
│ (4 scalars)     │                 │ (gene definitions) │
└───────┬─────────┘                 └────────────────────┘
        │ cell key
        ▼
┌─────────────────┐     Lorentzian barriers, Gaussian pits,
│ MAP-Elites      │     anisotropic quadratic, typed modes
│ 3×3×3×3 = 81    │
└───────┬─────────┘
        │ select parents, mutate/crossover
        ▼
┌─────────────────┐   L-BFGS-B, Nelder-Mead, CMA-ES, random-restart
│ optimizer panel │◀─── runs on each landscape with fixed budget
└───────┬─────────┘
        │ traces + final values
        ▼
┌─────────────────┐
│ disagreement    │   fitness = stdev across optimizers
│ fitness         │
└─────────────────┘
```

### 3.1 Landscape representation

`f(x) = x^T A x / 2  +  Σ_i ridge_i(x)  +  Σ_j gauss_j(x)`

- **Quadratic:** `A` stored as upper-triangle of a symmetric `d×d` matrix. Eigenvalues sampled uniformly, with a tunable probability of one near-zero eigenvalue (produces near-singular conditioning that kicks second-order methods).
- **Ridge:** anisotropic barrier along a unit direction `u`:
  - Lorentzian (primary): `a / (1 + ((u·x - b)/w)^2)` — sharp barrier, creates separability obstruction.
  - Logistic (secondary): `a / (1 + exp(-((u·x - b)/w)^2))` — smooth; used for plateau boundaries.
- **Gaussian component:** signed, axis-aligned: `w · exp(-½ Σ_k (x_k - c_k)^2 / σ_k^2)`.
  - Positive `w` creates a **basin** (subtracted from `f`), negative `w` creates a **hill**.

### 3.2 Generator modes (exploration, not descriptor)

Four explicit modes with distinct priors:

| Mode | Quad eigenvalue range | Ridge prior | GMM prior | Purpose |
|---|---|---|---|---|
| basin | 0.1–0.8 | none | 4 wide pits | generic multi-basin |
| ridge | 0.3–1.0 | 2–3 Lorentzians, amp 0.8–3.5 | 2 small | separability barriers |
| plateau | 0.01–0.1 (near-flat) | 1–2 logistic, soft | 0–2 small | flat regions |
| deceptive | 0.8–1.5 (strong bowl) | optional | hill near center + pit offset | gradient-methods misled |

Mode is part of the genome (determines mutation bias) but **is not part of the MAP descriptor**. This separates *how we explore* from *how we organize what we found*.

### 3.3 Descriptors (4 scalars per landscape)

All computed at fixed cost from a single multi-start L-BFGS-B sweep of `N=40` random starts.

1. **`n_minima`** — count of distinct basins after hierarchical clustering of endpoints at tolerance 0.1.
2. **`mean_curvature`** — `trace(Hessian(0))/d` via 4-point central differences.
3. **`log_conditioning`** — `log10(κ(Hessian(0)))` clamped to [0, 8].
4. **`depth_range`** — `max_i f(x_i*) − min_i f(x_i*)` across discovered minima. (Replaced `basin_entropy`, which correlated +0.94 with `n_minima`; `depth_range` correlation is +0.63, below the 0.85 collapse threshold.)

### 3.4 MAP-Elites grid

- **3 bins per axis, quantile-based** → 81 cells.
- Bin edges fit from a pilot sample of ~160 random landscapes; re-fittable as the archive grows.
- Cell size chosen for **full inspectability**: each elite can be visually checked on a 9×9 contour mosaic.

### 3.5 Optimizer panel (next phase)

Four canonical methods, each with matched budget:

| Optimizer | Character |
|---|---|
| L-BFGS-B | quasi-Newton, smooth-landscape specialist |
| Nelder-Mead | simplex, derivative-free, plateau-robust |
| CMA-ES | evolutionary, adapts covariance to anisotropy |
| random-restart + local search | baseline; weak but unbiased |

Each run records: final value, trajectory (subsampled), iterations, budget used, final basin ID.

### 3.6 Fitness for MAP-Elites placement

`fitness = stdev(final_value_across_optimizers)`

This biases the archive toward landscapes that **discriminate optimizers** rather than toward hard problems per se. (Alternative: "hard for all" fitness would collapse to Rastrigin-like pathologies.)

---

## 4. What pilot results have already settled

From 160 random landscapes (40 per mode):

### Correlation structure (locked)

```
                 n_min   curv    logK    depth_range
n_min            +1.000  +0.192  -0.221  +0.627
curv             +0.192  +1.000  +0.053  +0.151
logK             -0.221  +0.053  +1.000  -0.194
depth_range      +0.627  +0.151  -0.194  +1.000
```

- First-three pairwise max correlation: **0.22** — n_minima, mean_curvature, log_conditioning are independent.
- Depth_range correlation with n_minima: 0.63, below threshold.
- **Archive will not collapse.**

### Mode separability

| mode | n_min median | curv median | curv range | logK median |
|---|---|---|---|---|
| basin | 3 | +0.06 | [-1.2, +3.6] | +0.50 |
| ridge | 4 | +2.27 | [-15.2, +27.6] | +0.77 |
| plateau | 1 | +0.03 | [-0.2, +0.3] | +1.30 |
| deceptive | 3 | +0.71 | [-8.2, +5.3] | +0.56 |

Modes produce distinct descriptor signatures. Ridges create the widest curvature swings (Lorentzian spikes). Plateaus have the lowest curvature magnitude and the highest log-conditioning (flat regions = ill-conditioned bowls).

### Pure-random cell coverage: 41/81 (51%)

Evolution has roughly half of the grid to discover — a healthy exploration target. Uniform random sampling won't saturate the archive.

---

## 5. What's next (phases 2-4)

### Phase 2 — optimizer panel + disagreement measurements

- `optimizers.py`: wrap four solvers with matched budget, record traces.
- `evolve.py`: MAP-Elites GA with type-preserving mutation (each sub-gene has its own Gaussian perturbation scale).
- `run_pilot.py`: 50 generations × 20 children = 1000 landscapes × 4 optimizers = 4000 optimizer runs (~1-2h on one CPU).

Pre-registered expectation: the archive will preferentially fill cells with **moderate n_minima + high conditioning + wide depth_range**, because that's where gradient methods diverge most from derivative-free methods.

### Phase 3 — taxonomy of failure

Pick 5–10 high-disagreement elites. For each:

- Overlay four optimizer trajectories on the landscape contour.
- Compute Hessian spectrum at each discovered minimum.
- Measure gradient-norm along each trajectory vs iteration count.
- Cluster failure modes (basin-trapping, plateau-stalling, ridge-sliding, saddle-lingering).

Produces a failure-mode taxonomy **grounded in observable landscape structure** rather than algorithmic introspection.

### Phase 4 — lift to higher dimensions (only after phase 3)

With the 2D instrument calibrated, scale to `d = 5, 10, 20` using:

- low-rank or TT parameterization of the quadratic `A`.
- rank-constrained ridge directions (avoid combinatorial explosion of parameter space).
- descriptor generalizations validated against the 2D "ground truth" visuals.

---

## 6. Design principles

1. **Instrument first, generator second.** We're building a diagnostic lab, not a benchmark factory. Interpretability over expressivity at every decision point.
2. **Descriptor independence is non-negotiable.** The 0.94 correlation between `n_minima` and `basin_entropy` would have made half the archive degenerate; swapping to `depth_range` (corr 0.63) was the first substantive fix.
3. **Modes in the genome, not the descriptor.** If modes leaked into the cell key, archive structure would reflect generator assumptions rather than measured outcomes.
4. **2D before higher-d.** Every descriptor and every archive cell must be *visible* during development. When we lift to `d=10`, we're lifting proven axes — not guessing new ones under cover of dimensionality.
5. **Fitness selects for disagreement, not difficulty.** Hardness-only would find pathologies; disagreement finds *discriminating* landscapes, which is what optimizer research actually needs.

---

## 7. Open questions for the paper

- Is there a canonical low-dimensional coordinate (say 2-3 PCA axes over descriptors + optimizer-outcome features) on which all known test-function pathologies lie? If yes, what's its structure?
- Does the "disagreement" fitness converge to a finite set of **failure archetypes**, or does it keep unfolding new ones as the GA explores?
- Can we build a predictive mapping `(descriptors) → (which optimizer wins here)` with >80% accuracy from trained on the MAP archive? If so, that's a deployable meta-optimizer.
- Are there descriptor combinations that **guarantee** certain optimizers fail? If yes, those are actionable theoretical predictions.

---

## 8. Current file inventory

```
ergon/meta/
├── WHITEPAPER.md              ← this file
├── landscape.py               ← gene classes, modes, samplers
├── descriptors.py             ← 4 descriptors, quantile binning, correlation check
├── preview.py                 ← 12-random-landscape contour mosaic
├── sanity_check.py            ← pre-optimizer descriptor independence audit
└── figs/
    ├── preview_7.png          ← 12 random landscapes
    └── sanity_21.png          ← 4 modes × 3 samples each, labelled
```

Lines of code: ~500 (two source files + two CLI scripts). No external heavy dependencies beyond numpy / scipy / matplotlib.

---

## 9. Why this belongs in Prometheus

The broader Prometheus thesis holds that **structure in the search space is where findings live**, not in the solutions themselves. The F011 arc (April 2026) demonstrated this for L-function zero statistics: identifying *which families* of L-functions show compression was more informative than measuring *how much* any one family compressed.

Evolving Optimization Landscapes is the same instinct applied to optimization: stop optimizing harder, start asking which structures make optimization hard. The MAP-Elites archive *is* the finding.

---

*Status: Phase 1 complete. Awaiting green light to wire optimizers (Phase 2).*
