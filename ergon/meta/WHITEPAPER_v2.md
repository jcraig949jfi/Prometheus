# Evolving Optimization Landscapes — v2

**A Meta-Math Instrument for Problem-Structure Research**

Ergon / meta project — v2 design, 2026-04-23
`F:/prometheus/ergon/meta/WHITEPAPER_v2.md`

Supersedes `WHITEPAPER.md` (v1). v1 remains the record of the locked Phase-1 scaffold. v2 is the plan for Phases 2+ informed by review feedback.

---

## 0. What changed v1 → v2

| # | Upgrade | Why |
|---|---|---|
| 1 | **Descriptors evaluated at discovered minima**, not at origin | v1's `mean_curvature` and `log_conditioning` at `x=0` were measuring a random point in landscapes with scattered minima — potentially a *non-representative* value. |
| 2 | **Fitness becomes multi-component** (value stdev + trajectory divergence + basin-entropy + speed variance) | scalar stdev collapses too much; two landscapes with identical stdev can have very different failure structure. |
| 3 | **Fifth axis: ruggedness / correlation length** (global, not local) | all v1 descriptors were local or endpoint-based — no measure of multi-scale oscillation content. |
| 4 | **Optimizer panel spans paradigms** (add Adam, SA, trust-region, Sobol) | v1's L-BFGS / Nelder-Mead / CMA-ES / random-restart were all "classical continuous." Richer inductive-bias variety produces richer disagreement. |
| 5 | **Fourier gene family** added to landscape basis | v1's quadratic + ridge + GMM is smooth-localized-biased; sinusoidal terms introduce frequency structure that separates gradient methods from evolutionary methods. |
| 6 | **Trajectory geometry as first-class layer** | path length, path curvature, gradient-norm decay, stall-segment count — computed from stored traces and clustered to *derive* failure-mode taxonomy rather than define it manually. |
| 7 | **Adaptive grid resolution** | 3³³³ for visualization; internally subdivide high-occupancy / high-disagreement cells. |
| 8 | **Predictive-model layer** (`descriptors → optimizer winner`) | Validates descriptor sufficiency. Regions where the model is uncertain pinpoint axes that are missing. |
| 9 | Minor: domain-scale-aware clustering tol, mixed descriptor probes (L-BFGS + random), alternative 4th-axis (median basin gap) | fix subtle biases in Phase-1 pipeline. |

v1 descriptor-independence discipline, generator-mode/descriptor separation, and 2D-first microscope stance are **unchanged** — they were the right calls.

---

## 1. Problem statement (unchanged)

> **Given a family of problems, which structures make them hard, and why do optimizers disagree?**

v2 extends the framing from *mapping* to *predicting*: the archive is not just a record of findings but the training set for a learned `(structure → optimizer behavior)` model. When that model fails, its failures localize missing axes.

---

## 2. Architecture v2

```
                   ┌─────────────────────────────────────────────┐
                   │ GENE:                                        │
                   │   quad  +  ridges  +  gmm  +  fourier ←NEW   │
                   │   mode ∈ {basin, ridge, plateau,             │
                   │           deceptive, oscillatory ←NEW}       │
                   └───────────────┬─────────────────────────────┘
                                   │
                                   ▼
            ┌─────────────────────────────────────────────┐
            │ EVAL LAYER                                   │
            │   - multi-start L-BFGS-B (40 starts)         │
            │   - mixed probe: + 40 pure-random samples    │
            │     to de-bias descriptor extraction ←NEW    │
            └──┬──────────────────────────────────────────┘
               │
               ▼
     ┌──────────────────────────────────────────────────┐
     │ DESCRIPTORS v2 (5 axes, all independence-gated)  │
     │   1. n_minima                                     │
     │   2. minima-avg curvature      ←CHANGED from x=0 │
     │   3. minima-worst conditioning ←CHANGED from x=0 │
     │   4. depth_range (or median gap)                  │
     │   5. ruggedness / correlation length  ←NEW        │
     └──┬──────────────────────────────────────────────┘
        │  cell key (3×3×3×3×3 = 243 cells, quantile)
        ▼
     ┌─────────────────────────┐
     │ MAP-Elites              │───→ adaptive subdivision
     │ (81-cell coarse view)   │     in high-occupancy cells
     └──┬──────────────────────┘
        │
        ▼
     ┌───────────────────────────────────────────────────────┐
     │ OPTIMIZER PANEL v2  (8, matched budget per landscape) │
     │   L-BFGS-B   ←smooth 2nd-order                        │
     │   Nelder-Mead ←simplex                                │
     │   CMA-ES     ←evolutionary covariance adaptation      │
     │   Adam       ←stochastic gradient  ←NEW               │
     │   Simulated Annealing              ←NEW               │
     │   Trust-Region (scipy trust-constr)  ←NEW             │
     │   Sobol quasi-random + local refine ←NEW              │
     │   Random-restart local search (baseline)              │
     └──┬───────────────────────────────────────────────────┘
        │  per run: final x, final f, FULL trajectory,
        │  iters-to-ε-optimal, budget used, final basin
        ▼
     ┌─────────────────────────┐
     │ TRAJECTORY GEOMETRY     │ ←NEW, first-class output
     │   path_length           │
     │   path_curvature        │
     │   grad_norm_decay       │
     │   stall_segments        │
     │   → failure-mode cluster│
     └──┬──────────────────────┘
        │
        ▼
     ┌───────────────────────────────┐
     │ MULTI-COMPONENT FITNESS ←NEW  │
     │   f = w1·value_stdev          │
     │     + w2·traj_divergence      │
     │     + w3·basin_entropy        │
     │     + w4·speed_variance       │
     └──┬────────────────────────────┘
        │
        ▼
     ┌─────────────────────────────────────────────┐
     │ PREDICTIVE MODEL LAYER ←NEW                 │
     │   (descriptors) → (ranking of optimizers)    │
     │   random forest / GBM trained on archive     │
     │   out-of-bag uncertainty localizes           │
     │   descriptor insufficiency                   │
     └─────────────────────────────────────────────┘
```

---

## 3. Descriptor redesign

### 3.1 Why origin-anchored curvature/conditioning are wrong

A landscape with minima at `(3, -2)` and `(-1, 4)` measured via `Hessian(0)` yields a number that has **no necessary relationship** to either basin's local structure. v1 worked acceptably only because random rotation of the quadratic kept `x=0` close to the global bowl of the dominant quadratic term. Once landscapes become ridge-dominant or plateau-dominant, `Hessian(0)` is essentially random noise.

### 3.2 New definitions

- **`n_minima`** — unchanged.
- **`minima_avg_curvature`** — `(1/K) Σ_k trace(Hessian(x_k*)) / d` over the `K` discovered minima. Captures the *typical* basin sharpness in the regions an optimizer would actually reach.
- **`minima_worst_conditioning`** — `max_k log10(κ(Hessian(x_k*)))`. The worst-conditioned basin determines whether second-order methods will struggle somewhere.
- **`depth_range`** — `max_k f(x_k*) − min_k f(x_k*)`. (Unchanged.)
- **`ruggedness`** — autocorrelation length of `f` along random walks, OR spectral entropy of `f` sampled on a grid. Global structure; orthogonal by construction to minima-anchored measurements.

### 3.3 Alternative 4th axis (safety net)

If `depth_range` collapses with `n_minima` after the v2 redesign (current v1 correlation 0.63 may worsen), fall back to:

- **`median_basin_gap`** — `median_{i<j} | f(x_i*) − f(x_j*) |`. Similar motivation to depth_range but less sensitive to outlier basins.
- **`top_k_contrast`** — `(f_2nd_best − f_best) / |f_best|`. Measures "was the global optimum a clean win or barely edging out a competitor."

All three candidates get correlation-checked against {n_minima, minima_avg_curvature, minima_worst_conditioning, ruggedness} at v2 startup; the axis that minimizes max correlation is selected.

### 3.4 Mixed descriptor probe

v1 used only L-BFGS-B from 40 random starts to build the descriptor. This biases toward **gradient-friendly** structure — plateaus and ridges get underreported because local search fails on them.

v2: mix probe sources.

- 40 L-BFGS-B starts (unchanged): find true basins.
- 40 pure-random samples of `f` (no local search): estimate ruggedness + capture plateau/deceptive regions not reachable by gradient descent.
- For ruggedness specifically, generate 10 random walks of length 50; compute autocorrelation.

---

## 4. Landscape class expansion: Fourier gene

v1's three gene families (quadratic + ridges + GMM) all produce **smooth, locally-supported** structure. v2 adds a fourth:

### 4.1 Fourier gene

```
fourier(x) = Σ_k a_k · sin(ω_k · x + φ_k)
```

- `a_k`: amplitude (signed).
- `ω_k`: frequency vector in `R^d`.
- `φ_k`: phase.
- Typically 3–6 modes per landscape when the "oscillatory" generator mode is selected.

### 4.2 New generator mode: oscillatory

- Weak quadratic (eigenvalues 0.1–0.4) — lets the sinusoid dominate.
- No GMM by default.
- 3–6 Fourier modes with frequencies spanning low to Nyquist-ish.
- Optional small ridge for directional asymmetry.

This mode is where **CMA-ES vs L-BFGS-B** disagreement should spike: gradient methods get captured in nearest local minimum, evolutionary methods can tunnel.

### 4.3 Existing modes updated

`basin` / `ridge` / `plateau` / `deceptive` modes gain optional Fourier terms at low amplitude — a small high-frequency perturbation that tests whether a given method is *robust* to noise around its nominal structure.

---

## 5. Multi-component fitness

v1: `fitness = stdev(final_value_across_optimizers)` — one scalar.
v2: four complementary components.

### 5.1 Components

| Component | Definition | What it catches |
|---|---|---|
| `value_stdev` | stdev of final `f` across optimizers | v1 fitness; disagreement on *outcome* |
| `traj_divergence` | pairwise mean Fréchet distance (or DTW-lite) between trajectories | disagreement on *path* — same endpoint via very different routes |
| `basin_disagreement_entropy` | Shannon entropy over final-basin IDs | disagreement on *which answer* |
| `speed_variance` | variance of iterations-to-reach-ε-optimal | disagreement on *how fast* |

### 5.2 How MAP-Elites uses the 4-vector

Two viable strategies, both supported:

- **Weighted scalar** (default): `fitness = w1·value_stdev + w2·traj_divergence + w3·basin_entropy + w4·speed_variance`, with `w_i` chosen so each term contributes roughly comparable variance across a pilot sample. Simpler to drop into existing MAP-Elites.
- **Vector MAP-Elites**: each component is a separate quality axis; elite-per-cell stored for each axis. Produces four parallel archives that can be compared/intersected. More expressive; higher compute but small for a 81-cell grid.

v2 pilot runs the weighted scalar first; vector version is a flag.

### 5.3 The two landscapes with identical stdev

The motivating example: two landscapes where `stdev(final_value)` is the same, but in one, optimizers early-diverge-then-reconverge (same answer, different path), and in the other, they end in different basins entirely. v1 treats these identically. v2 differentiates via `traj_divergence` (high for the first) vs `basin_entropy` (high for the second).

---

## 6. Optimizer panel expansion

v1 had 4 methods, all classical continuous. v2 keeps them and adds 4 with distinct inductive biases.

| # | Optimizer | Library | Bias / Strength |
|---|---|---|---|
| 1 | L-BFGS-B | scipy | Smooth 2nd-order, exploits gradients |
| 2 | Nelder-Mead | scipy | Derivative-free simplex, plateau-tolerant |
| 3 | CMA-ES | `cma` package | Evolutionary, covariance adaptation |
| 4 | Random-restart + local | built-in | Weak unbiased baseline |
| 5 | **Adam** | custom | Stochastic gradient, first-order momentum |
| 6 | **Simulated Annealing** | scipy `dual_annealing` | Temperature-based basin escape |
| 7 | **Trust-region (trust-constr)** | scipy | Different curvature handling than L-BFGS |
| 8 | **Sobol + local refine** | scipy.stats.qmc | Structured quasi-random exploration |

All share a matched evaluation budget (default 500 function evaluations per run). Each records full trajectory + iteration count + final basin ID.

Trust-region and L-BFGS will often disagree in near-singular-conditioning regions; Adam and L-BFGS will diverge on rugged landscapes (Adam's momentum helps through saddle points); Sobol + local will beat random-restart on plateaus but lose to CMA-ES on anisotropic ridges. These predictions are all falsifiable after the v2 run.

---

## 7. Trajectory geometry layer

v1 stored traces but didn't analyze them beyond "final x and final f." v2 elevates trajectories to first-class objects.

### 7.1 Per-trajectory metrics

- **`path_length`** — `Σ_t ||x_{t+1} − x_t||`.
- **`path_curvature`** — mean turn angle between consecutive segments.
- **`grad_norm_decay`** — fit `||∇f(x_t)||` to `t^{-α}`; report `α`.
- **`stall_segments`** — count of consecutive iterations where `||x_{t+1} − x_t||` falls below `0.01 * box_scale`.

### 7.2 Failure-mode clustering

For a fixed landscape, pool trajectories from all 8 optimizers. Featurize each by (path_length, curvature, stall_segments, grad_decay, final_basin). Cluster in this feature space (k-means or hierarchical). The cluster IDs become **learned failure modes**:

- Cluster A: short path, high curvature, stall early → "basin-trapped"
- Cluster B: long path, low curvature, no stalls → "ridge-sliding"
- Cluster C: medium path, many stalls → "plateau-stalling"
- Cluster D: oscillatory path, final at origin → "saddle-lingering"

Cluster labels are then available as *additional features* for the predictive model in §9.

This is the Phase-3 taxonomy goal from v1, **promoted to automatic and continuous**.

---

## 8. Adaptive grid resolution

Coarse 3³³³ grid (81 cells — here 3⁵ = 243 if ruggedness lands as a real 5th axis, or we keep 4 primary MAP axes and track ruggedness as a non-binned metadata dimension; pilot will decide) stays the default for human inspection.

Internally, cells with >5 elites OR high-disagreement-variance get **subdivided** into 2³²² = 8 sub-cells dynamically. Subdivision triggers:

- a cell has been hit ≥ 5 times with disagreement-fitness in the top quartile.
- a cell's internal disagreement variance exceeds the cross-cell mean by 1.5×.

The top-level 81-cell view is always what gets visualized; subdivision is an internal promotion that gives MAP-Elites more resolution without breaking interpretability.

---

## 9. Predictive model layer (the big leverage)

### 9.1 Target

Train a model

```
(descriptors, mode) → optimizer_ranking
```

The response is a permutation over the 8 optimizers (or a top-1 winner). Predictors are the 5-dim descriptor vector + mode as a categorical.

### 9.2 Why this matters

The MAP archive is by construction the *training set*:

- Every cell's elite has been scored on 8 optimizers.
- Rankings are fully observed.
- Cells cover ~half the descriptor space after pure random sampling, more after GA.

A random-forest or GBM trained on this achieves one of three outcomes:

1. **High accuracy (≥80%)**: the descriptors are *sufficient* to predict optimizer behavior. The project graduates from "map" to "actionable rule." A practitioner could compute our 5 descriptors on their problem and get an optimizer recommendation.
2. **Mid accuracy (60–80%)**: descriptors explain *most* of the variance; the residual points at missing axes. Feature-importance on the model tells us which axis to refine.
3. **Low accuracy (<60%)**: either the landscape parameterization is too restrictive (optimizers disagree on randomness in the GMM sampling, not structure) or descriptors miss something fundamental. Diagnostic.

### 9.3 Implementation

- Split: 70% train / 15% val / 15% test, stratified by mode.
- Models: start with random forest (interpretable, OOB scoring, feature importance), then try GBM for higher ceiling.
- Uncertainty: OOB per-cell prediction disagreement pinpoints archive regions where the descriptors are *insufficient*. Those regions get sampled harder by the GA in the next generation — a closed-loop active-learning feedback.

### 9.4 What gets published

Not the model itself (this is diagnostic). The paper publishes:

- The archive (every elite).
- The descriptor correlation matrix.
- The predictive-model accuracy + feature-importance.
- The regions where the model fails, *as evidence of structural holes in the descriptor set*.

---

## 10. Phased rollout (v2)

**Phase 2a (this week)** — keep landscape basis + optimizer panel as v1, add:
- minima-relative descriptors
- ruggedness probe
- trajectory recording + first geometry metrics
- multi-component fitness scalar (equal weights)
- run first 50-gen × 20-child pilot

**Phase 2b** — add:
- Fourier gene + oscillatory mode
- expanded optimizer panel (Adam, SA, trust-region, Sobol)
- failure-mode clustering on pooled trajectories

**Phase 3** — predictive-model layer, closed-loop active learning.

**Phase 4** — lift to `d=5, 10, 20` using the calibrated 2D descriptors.

Gate between phases: a cell-coverage report + a descriptor-independence audit. If either degrades (coverage < 40% at end of a phase, max correlation > 0.85), the next phase is blocked.

---

## 11. Smaller fixes

- **Scale-aware clustering tolerance**: replace the hard-coded 0.1 with `0.025 * box_scale` (currently 4.0). For a `d=10` landscape with box 8, tolerance becomes 0.2, not 0.1.
- **Descriptor probe mix**: 40 L-BFGS + 40 random samples + 10 walks × 50 steps. Cost roughly 2× v1 per-landscape descriptor call — acceptable.
- **Clustering metric**: switch from single-linkage Euclidean to **single-linkage with Mahalanobis distance** using the observed basin covariance — avoids merging distinct-but-close basins in anisotropic landscapes.
- **Quantile edge recomputation**: refit edges every 100 landscapes (not just at startup). The pilot quantile is biased toward the generator's initial priors; as GA explores, the empirical distribution shifts.

---

## 12. Design principles (carried forward, with additions)

1. **Instrument first, generator second.** (v1, unchanged.)
2. **Descriptor independence is non-negotiable.** (v1; v2 extends to 5 axes, and adds the predictive-model test for *descriptor sufficiency*, which is a stricter criterion.)
3. **Modes in the genome, not the descriptor.** (v1, unchanged.)
4. **2D before higher-d.** (v1, unchanged.)
5. **Fitness selects for disagreement, not difficulty.** (v1; v2 breaks the disagreement scalar into 4 components so it can't be gamed by pathologies.)
6. **Trajectories are first-class data**, not just logs. (v2 new.)
7. **Descriptor sufficiency is empirically testable** via a predictive model; its failures localize missing axes. (v2 new.)
8. **Adaptive resolution without sacrificing interpretability** — coarse grid for humans, subdivision for machines. (v2 new.)

---

## 13. Open research questions

Unchanged from v1:

- Is there a canonical 2-3 dimensional coordinate (PCA over descriptors + outcome features) on which all known test-function pathologies lie?
- Does disagreement-fitness converge to a finite set of **failure archetypes**, or keep unfolding new ones?

New in v2:

- How many descriptor dimensions are needed to reach 80% predictive accuracy on optimizer ranking? (The 5-descriptor target is a *hypothesis* — it may be too few.)
- Are failure-mode clusters **universal across modes**, or does each mode's landscape class produce distinct failure modes?
- Does the Fourier frequency `ω` correlate with the optimizer that wins, in a way that suggests a spectral theorem for optimizer selection?
- Does the predictive model's uncertainty concentrate in specific generator modes, suggesting those modes are genuinely harder to characterize structurally?

---

## 14. Why this still belongs in Prometheus

The broader thesis: **structure in the search space is where findings live**, not in the solutions themselves. F011 (L-function zero compression) demonstrated this for number theory. Evolving Optimization Landscapes demonstrates it for optimization: the MAP archive *is* the finding.

v2 sharpens the claim: not just "here is an archive of landscape structures," but "here is a learned mapping from structure to solver behavior, with its failures labeled as hypotheses for additional structural axes." That's the move from observation to predictive theory.

---

## 15. File inventory (target for v2)

```
ergon/meta/
├── WHITEPAPER.md              ← v1 (scaffold)
├── WHITEPAPER_v2.md           ← this file
├── landscape.py               ← + Fourier gene, + oscillatory mode
├── descriptors.py             ← minima-relative, + ruggedness, + alternative 4th-axis
├── optimizers.py              ← NEW (8 solvers, matched budget)
├── trajectory.py              ← NEW (geometry metrics, failure-mode clustering)
├── evolve.py                  ← NEW (MAP-Elites GA, type-preserving mutation)
├── fitness.py                 ← NEW (multi-component, weighted scalar + vector modes)
├── predict.py                 ← NEW (RF / GBM layer)
├── preview.py                 ← v1, updated for new descriptors
├── sanity_check.py            ← v1, updated for 5-axis independence check
├── run_pilot.py               ← NEW (50-gen × 20-child pilot runner)
└── figs/
    ├── preview_*.png
    ├── sanity_*.png
    ├── archive_mosaic_*.png    ← NEW: 81-cell grid of elites
    ├── trajectory_clusters_*.png ← NEW: failure-mode dendrogram
    └── predictive_accuracy_*.png ← NEW: model ROC / confusion
```

Lines of code estimate: ~1500 for v2 (vs ~500 for v1), still a small self-contained project.

---

## 16. What's shipped (v1) vs what's new (v2)

**Already shipped (v1):**
- `landscape.py` with quad + ridges + GMM, 4 modes, Lorentzian ridges
- `descriptors.py` with 4 descriptors at `x=0`, quantile binning, correlation check
- Sanity check: 160 landscapes, 4-axis correlation + mode separability verified
- Pre-MAP coverage: 41/81 cells (51%) from random sampling

**v2 build order (gated by independence checks at each step):**

1. Minima-relative descriptors (§3.2) — replace origin-anchored calls
2. Ruggedness descriptor (§3.2) — add 5th axis, check correlation
3. Mixed descriptor probe (§3.4) — de-bias from gradient-friendly structure
4. Multi-component fitness (§5) — 4 terms, weighted-scalar default
5. Trajectory metrics + clustering (§7) — first-class failure taxonomy
6. Optimizer panel expansion (§6) — +4 methods with matched budget
7. Fourier gene + oscillatory mode (§4) — new landscape family
8. Pilot run 1: 50 gen × 20 children — first archive
9. Predictive-model layer (§9) — test descriptor sufficiency on archive
10. Adaptive subdivision (§8) — closed-loop refinement

Each step is ~1 session of work. Total: ~2 weeks of focused effort to reach a v2 paper-ready archive.

---

*Status: v1 scaffold locked. v2 design approved. Phase 2a (minima-relative descriptors + trajectory layer + multi-component fitness) begins next.*
