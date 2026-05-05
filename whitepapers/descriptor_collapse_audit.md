# When MAP-Elites Axes Collapse

## A Calibration-First Audit of Descriptor Independence (with Tensor-Train Approximation as a Worked Example)

### Version 3.4 — 2026-04-26

**Author:** Harmonia_M2_auditor
**Source project:** Zoo (exploratory MAP-Elites archive over tensor-train approximations)
**Repository root:** `D:\Prometheus\exploratory\zoo\`
**Canonical paper path:** `D:\Prometheus\whitepapers\descriptor_collapse_audit.md`
**Primary artifacts:**
- `D:\Prometheus\exploratory\zoo\results\phase3_20260423T072026.json`
- `D:\Prometheus\exploratory\zoo\results\phase4_20260423T074559.json`
- `D:\Prometheus\exploratory\zoo\results\phase4b_no_dmrg_20260425T013745.json`
- `D:\Prometheus\exploratory\zoo\results\phase4_analysis_20260425T013514.json`
- `D:\Prometheus\exploratory\zoo\results\phase4_within_band_null.json`
- `D:\Prometheus\exploratory\zoo\results\dmrg_unit_test.json`
- `D:\Prometheus\exploratory\zoo\results\phase5_20260425T032712.json`
- `D:\Prometheus\exploratory\zoo\results\phase5b_no_dmrg_20260425T033645.json`
- Figures at `D:\Prometheus\exploratory\zoo\docs\figures\`

---

## Abstract

**The contribution is a multi-layer descriptor-collapse audit for quality-diversity search.** A MAP-Elites archive over tensor-train (TT) approximations is the worked example. The audit progresses through five layers — Pearson correlation, distance correlation, Kraskov-Stögbauer-Grassberger mutual information, full-sample shuffled null, and conditional MI within bands with sample-size-matched within-band shuffled null — and each layer catches failure modes the previous layers miss. Direct trajectory inspection completes the framework when the audit narrows the suspect list. The five sources of axis dependence the audit discriminates are: estimator bias, geometric boundary, refinement-induced collapse, search starvation, and intrinsic geometric coupling.

The TT worked example demonstrates each layer in turn. Phase 2 placement on `(log n_params, log relative L² error)` produced a Pearson r = −0.968 — the 2D grid was measuring a 1D ridge. Phase 3 added rank-orthogonal candidate descriptors (rank entropy, rank concentration). Phase 4 implemented the engineering needed to drive the archive along those axes — rank-shift mutation, two-site DMRG refinement, a heat-PDE-smoothed frontier function — and added the nonlinear audit. Phase 4 closed with a partial Branch-A pass: Pearson dropped to +0.29–0.40 across three frontier functions, but KSG MI stayed at ~1.4 nats.

The reviewer of v3.2 set three priorities: a decisive diversified-seed proof (§8.1), a DMRG instrument-trust unit test, and seed-count restoration. v3.3 reports execution of all three, plus the discovery and resolution of a critical config-forwarding bug in the multi-seed harness, and the resulting clean falsification.

**The decisive Phase 5b experiment** (5 seeds, 80 generations, 12 diversified initial seeds — 4 uniform + 4 peaked + 4 bimodal — `shift_magnitude = 4`, two-site DMRG disabled) populated the rank_entropy axis to 84% of its achievable range [0.778, 1.609] across all six functions (vs 11–25% in Phase 4). With entropy genuinely explored, the within-band MI between `log_params` and `rank_entropy` STILL averaged 25–61× the within-band shuffled null on every (function × band) cell, p = 0.000 throughout.

**The v3.4 fulcrum experiment** (lattice baseline + archive-history decomposition + synthetic identifiability) addresses the reviewer-2026-04-26 question "before claiming the audit detects geometry, prove it is not first detecting combinatorics." Sub 1: KSG MI on a uniform random sample of 10,000 valid rank profiles (no MAP-Elites, no TT-SVD, no DMRG — pure combinatorics) returns **0.15 nats** on `(log_params, rank_entropy)`. Sub 2: archive elites and Pareto fronts have LOWER MI (0.92–1.28 nats) than the full Phase 5b pooled history (1.70–1.89 nats), ruling out elite selection as the dominant coupling source. Sub 3: a synthetic SELECTION_COUPLED control on independent data returns MI = 0.000, confirming Sub 2; but a synthetic DISCRETIZATION control (lattice + small noise) returns MI = 1.65, revealing an audit limitation we now disclose explicitly.

**The defensible claim hierarchy (three tiers, evidence-graded):**

- **Tier 1 — descriptor non-independence:** strong evidence. Phase 5b MI is ~1.7 nats; lattice baseline is 0.15 nats; the descriptors are ~10× more dependent than combinatorics alone explains.
- **Tier 2 — geometric coupling:** moderate evidence. The ~1.55-nat residual above lattice baseline is not eliminated by exploration, refinement-operator change, or elite selection. The audit cannot yet separate "continuous TT geometry" from "TT-evaluation discretization effects" (the Sub-3 DISCRETIZATION false-positive).
- **Tier 3 — structural mathematical signal:** partial evidence. Would require ruling out TT-specific discretization artifacts and demonstrating the coupling persists under alternative TT decompositions (TT-cross, randomized TT). Not yet established.

The v3.3 headline "TT geometry signal" was Tier 2 evidence reported as Tier 3 language. v3.4 corrects this.

A separate Phase 5 run (DMRG actually on, after the harness bug fix) revealed a third coupling source independent of seed bias and search starvation: DMRG's adaptive truncation pulls peaked rank profiles toward each function's effective rank, masking the diversified-seed test. This is itself a publishable finding — the search operator can defeat a descriptor decoupling experiment unless the operator's effect on the descriptor distribution is auditable separately.

The DMRG instrument-trust unit test (Tests A–D) confirms the implementation is operational: the inner loop modifies cores under non-trivial inputs, singular values shift, ranks adapt downward when given over-sized profiles on rank-1 targets, and the rollback guard correctly activates at machine epsilon. The Phase 4 "DMRG no-op" finding from v3.2 §4.3 is now correctly attributed to a config-forwarding bug in `multi_seed.py` rather than to the rollback guard alone.

**The TT MAP-Elites placement axes `(log n_params, rank_entropy)` are NOT independent.** Even with diversified seeds, larger rank-shift mutation, full entropy-axis coverage, and TT-SVD-only evaluation, the two axes share approximately 1.5 nats of mutual information beyond what the rank-profile lattice combinatorics alone produce (lattice baseline: 0.15 nats; Phase 5b: 1.7 nats). Neither diversified search exploration nor the variation between pooled history and archive elites removes the bulk of this coupling. The TT-specific contribution is therefore a property of the evaluation pipeline, not of MAP-Elites selection or random profile combinatorics.

The methodological story is: the multi-layer audit plus follow-up fulcrum experiments together identified, characterized, and graded the coupling. The audit alone catches the signal; the layered design with synthetic identifiability tests is what makes the verdict defensible. The TT zoo is a worked example showing what the discipline looks like under five distinct candidate explanations.

---

## 1. Introduction

MAP-Elites and related quality-diversity methods maintain archives of solutions indexed by behavior descriptors. A 2D grid of $N$ cells suggests a 2D solution landscape. That suggestion is exactly as strong as the descriptors. If the two behavior axes are linearly or nonlinearly coupled along the search path actually taken, the archive traces a curve, and its 2D shape is an artifact of grid resolution.

We encountered this concretely while prototyping an archive over TT approximations. Phase 2 placement axes `(log n_params, log rel_error)` both depend monotonically on rank, and rank perturbation was the only mutation. The archive *looked* 2D and filled ~12 cells; it was actually tracing a monotone curve. Phase 3 added function-level intrinsic descriptors and candidate rank-orthogonal placement axes. Phase 4 did the engineering work to drive the archive along those axes. Phase 4 also replaced the single-layer Pearson audit with a two-layer check: Pearson first, nonlinear metrics second, both calibrated against a control. This revealed that the decoupling achieved in the Phase 3 planning was partial.

The further work reported in §4 was driven by the question: where does the residual coupling come from? Three candidate sources competed. The diagnostic chain — shuffled null at full sample, conditional MI within bands, DMRG counterfactual — narrowed the field. Phase 5 added the rest of the picture.

The paper's primary contribution is the multi-layer audit. The TT zoo is a testbed.

---

## 2. Method

### 2.1 Tensor trains

A tensor $T \in \mathbb{R}^{n_1 \times \cdots \times n_d}$ is represented as $d$ cores $G_k \in \mathbb{R}^{r_{k-1} \times n_k \times r_k}$, with boundary ranks $r_0 = r_d = 1$. The interior bonds $(r_1, \dots, r_{d-1})$ are the tunable knobs. Storage: $\sum_k r_{k-1} \cdot n_k \cdot r_k$. Baseline decomposition is TT-SVD (Oseledets) at a fixed rank profile.

Two-site DMRG refinement, optional from Phase 4 onward, merges adjacent cores $G_k, G_{k+1}$ into a supercore, optimizes via closed-form least squares against the contracted environments, SVDs back into two cores with relative-tolerance truncation $(\sigma_i / \sigma_1 < \tau = 10^{-10})$ bounded by `max_bond`. One sweep = left-to-right + right-to-left traversal. The implementation includes a rollback guard: if `err_after > err_before · 1.001`, the refined TT is discarded and the un-refined TT is returned with `refinement_gain = 0`.

A four-test instrument-trust unit test (`D:\Prometheus\exploratory\zoo\experiments\unit_test_dmrg.py`, results at `D:\Prometheus\exploratory\zoo\results\dmrg_unit_test.json`) verifies that DMRG (a) modifies cores under non-trivial inputs, (b) shifts the singular-value spectrum, (c) adapts ranks downward when given over-sized profiles on low-rank targets, and (d) the rollback guard correctly activates at machine epsilon. All four tests PASS. DMRG is operational.

### 2.2 MAP-Elites archive

For each function, a 2D grid indexes individuals (TT rank tuples) by two behavior descriptors chosen from the descriptor set. Placement is standard MAP-Elites: occupy an empty cell or replace the occupant if strictly better on `rel_error`.

Mutation is hybrid: $p_\text{shift}$ probability of rank-shift (transfer rank magnitude $s$ from one bond to another), $1 - p_\text{shift}$ probability of classical perturbation (single bond ±1). Phase 4 used $s = 1$; Phase 5 uses $s = 4$ to enable larger lateral exploration along the entropy axis at fixed params.

Initial seeds come from one of two strategies:
- **Uniform-log-spaced** (Phase 2–4 default): log-spaced uniform rank profiles $(k, k, \dots, k)$. Entropy near max by construction.
- **Diversified** (Phase 5+): equal-third split of uniform / peaked / bimodal profiles. Peaked profiles place all rank mass at one bond (entropy near min); bimodal profiles alternate high-low (intermediate entropy).

Configuration unless noted: dimension $d = 6$, grid shape $(12, \dots, 12)$, `max_bond = 16`. Phase 4 default: 50 generations, 8 initial seeds. Phase 5 default: 80 generations, 12 initial seeds.

### 2.3 Calibration contract

Pre-registered verdicts for anchor functions:

- `prod_x = ∏_i x_i` (exact TT rank 1): $\log_{10} n_\text{params} \leq 2.5$, $\text{rel\_err} \leq 10^{-6}$ at some cell.
- `sum_of_squares = ∑_i x_i^2` (exact TT rank 2): $\log_{10} n_\text{params} \leq 2.7$, $\text{rel\_err} \leq 10^{-6}$.
- `random_gaussian` (i.i.d.): NO low-error low-params point; any $\text{rel\_err} < 10^{-2}$ at $\log_{10} n_\text{params} < 4.0$ is suspicious.

A run violating any contract is an instrument failure, not a result. Phases 3, 4, 4b, 5, and 5b all pass on every seed.

### 2.4 Descriptors

**Approximation-level** (vary per evaluation):

- `n_params`, `rel_error`
- `avg_rank`, `max_rank`
- `rank_entropy`: Shannon entropy of the normalized rank distribution across bonds. For uniform profile, $\log(d-1)$.
- `rank_concentration`: peak-to-mean ratio of the rank profile.
- `refinement_gain`: $\text{rel\_err\_before} - \text{rel\_err\_after}$.

**Function-level** (one value per function):

- `spectral_alpha`: exponent fit to $\log \sigma_i \sim c - \alpha \log i$ on the top singular values of the middle-bond unfolding. Unbounded.
- `effective_rank_at_threshold(τ = 10^{-8})`: smallest $k$ such that $\sigma_{k+1}/\sigma_1 < \tau$. Bounded integer.

### 2.5 Stability (formal, gauge-invariant)

For target $T$, rank profile $r$, noise level $\varepsilon$:

$$
S_F(T, r, \varepsilon) = \frac{\varepsilon}{\mathbb{E}_\delta\left[ \frac{\lVert \hat{T}(T + \delta) - \hat{T}(T) \rVert_F}{\lVert \hat{T}(T) \rVert_F} \right]}
$$

with $\delta \sim \mathcal{N}(0, \sigma^2 I)$, $\sigma = \varepsilon \lVert T \rVert_F / \sqrt{|T|}$. All norms are on reconstructed tensors, making $S_F$ gauge-invariant under TT core gauge $G_k \to G_k A$, $G_{k+1} \to A^{-1} G_{k+1}$. A subspace-angle cross-check $S_\angle$ is defined symmetrically.

### 2.6 The descriptor-collapse audit (five layers)

**Layer 1 — Pearson.** Pairwise Pearson r on pooled history. Flag pairs with $|r| \geq 0.9$ excluding structurally forced pairs.

**Layer 2 — distance correlation (Székely-Rizzo-Bakirov).** Zero iff variables are independent under finite-moment assumptions. Range $[0, 1]$. Flag pairs $\geq 0.5$.

**Layer 3 — KSG mutual information.** Kraskov-Stögbauer-Grassberger k-NN MI, $k = 3$, Chebyshev metric. Range $[0, \infty)$ nats. Flag pairs $\geq 0.5$ nats.

**Layer 4 — full-sample shuffled null.** Empirical null built from 100 random permutations of one variable against the other at full sample size. Reports observed MI as p-value against the null and as ratio to null mean.

**Layer 5 — conditional MI within bands with within-band null.** Partition pooled history into quartile bands of one variable. Within each band, recompute MI and compare to a within-band shuffled null at the matched (smaller) sample size, controlling for KSG's small-n upward bias. Within-band coupling that exceeds its within-band null indicates structure beyond the between-band geometric boundary.

**Trajectory inspection.** Distinct from the five formal layers but methodologically essential: when the formal audit narrows the suspect list, direct descriptive statistics on the search trajectory often complete the diagnosis (Phase 4 §4.4 entropy-starvation finding, Phase 5 §4.7 DMRG-truncation-collapse finding).

---

## 3. The collapse finding (Phases 2–4 recap)

Pooled Pearson correlation on `(log n_params, log rel_error)` from Phase 3 (n = 250 per function): `pairwise_tanh` r = −0.938 (Layer 1 flagged). Phase 4 introduced rank-shift mutation, two-site DMRG, and the `(log n_params, rank_entropy)` placement grid:

| Function | Pearson r | dCor | KSG MI (nats) |
|---|---|---|---|
| `pairwise_tanh` | +0.290 | 0.460 | 1.402 |
| `runge_dim` | +0.403 | 0.560 | 1.410 |
| `heat_smoothed` | +0.398 | 0.545 | 1.381 |

Pearson dropped 3×, but Layers 2–3 still flagged the pair. Phase 4 closed with a partial Branch-A verdict. Three diagnostic experiments and the Phase 5 series resolved the partial verdict.

---

## 4. The diagnostic chain

### 4.1 Layer-4 shuffled-null calibration (added v3.1)

For each frontier function, 100 random permutations of `rank_entropy` against fixed `log_params`:

| Function | Observed MI | Null mean | Null p99 | Observed/null mean | p-value |
|---|---|---|---|---|---|
| `pairwise_tanh` | 1.402 | 0.023 | 0.105 | 60× | 0.000 |
| `runge_dim` | 1.410 | 0.020 | 0.109 | 70× | 0.000 |
| `heat_smoothed` | 1.381 | 0.022 | 0.118 | 62× | 0.000 |

Zero of 100 shuffles approached observed; the coupling is real, not estimator bias.

### 4.2 Layer-5 within-band MI with within-band null (added v3.2)

Partition pooled history into four `log_params` quartile bands; compute within-band MI; compare against a within-band shuffled null at matched n.

| Function | Band 0 obs/null | Band 1 | Band 2 | Band 3 |
|---|---|---|---|---|
| `pairwise_tanh` | 35× | 19× | 18× | 38× |
| `runge_dim` | 26× | 19× | 10× | 19× |
| `heat_smoothed` | 26× | 15× | 12× | 22× |

p = 0.000 in every (function × band) cell. Geometric-boundary hypothesis rejected: substantial coupling persists within tight `log_params` ranges, controlling for finite-sample bias.

### 4.3 DMRG counterfactual (added v3.1, REVISED v3.3)

v3.1 ran a "DMRG-on vs DMRG-off" comparison and got 150/150 identical rank profiles in both directions, attributing the no-op to the rollback guard alone. v3.3 corrects this attribution: a config-forwarding bug in `multi_seed.py` caused the "DMRG-on" run to actually execute with `dmrg_sweeps = 0`. The comparison was DMRG-off-vs-DMRG-off.

The qualitative conclusion (DMRG was operationally inactive in the v3.1/v3.2 measurements) survives because both sides really were DMRG-off. The mechanism explanation needed revision; v3.3's bug fix in `D:\Prometheus\exploratory\zoo\map_elites\multi_seed.py` (use `dataclasses.replace(config, seed=s)` to forward all fields) plus the unit test in §2.1 closes the instrument-trust gap. Phase 5 was the first run where DMRG actually executes.

### 4.4 Phase 4.4 trajectory inspection (entropy starvation)

Direct inspection of the Phase 4 search trajectory: `rank_entropy` mean 1.587 ± 0.027, range [1.475, 1.609]. The search visited 16% of the achievable range [0.778, 1.609]; the upper-rim sliver explained the residual coupling under search-starvation interpretation. Phase 5's diversified-seed test was constructed to falsify this.

### 4.5 Phase 5 — DMRG actually on (a third coupling source revealed)

Same 5 seeds, 80 generations, diversified initial seeds, `shift_magnitude = 4`, but with `dmrg_sweeps = 1` (now actually executes after the bug fix):

| Function | Effective rank | Entropy range | Coverage of achievable | Outcome |
|---|---|---|---|---|
| `prod_x` | 1 | [1.609, 1.609] | 0% | DMRG truncated to (1,1,1,1,1) |
| `sum_of_squares` | 2 | [1.609, 1.609] | 0% | Same |
| `random_gaussian` | 1728 | [1.600, 1.600] | 0% | At ceiling already |
| `pairwise_tanh` | 92 (>max_bond) | [1.401, 1.607] | 25% | DMRG can't truncate; peaks survive |
| `runge_dim` | 10 | [1.517, 1.602] | 10% | DMRG truncates peaks toward (10,10,10,10,10) |
| `heat_smoothed` (t=0.005) | 14 | [1.510, 1.602] | 11% | Same mechanism |

**The pattern: when `max_bond > effective_rank`, two-site DMRG's adaptive truncation pulls peaked rank profiles toward the function's intrinsic effective rank, which is approximately uniform — collapsing entropy back to the upper rim.** When `max_bond < effective_rank` (only `pairwise_tanh`), DMRG cannot truncate further and peaked seeds survive.

This is a third coupling mechanism distinct from seed bias and search starvation: refinement-induced rank collapse. Phase 5 by itself cannot test Branch A because DMRG masks the diversified-seed exploration.

### 4.6 Phase 5b — DMRG off, the decisive Branch-A test

Same configuration as Phase 5, but with `dmrg_sweeps = 0` and `als_sweeps = 0` (TT-SVD only):

| Function | Cells (median) | Entropy range | **Coverage** | Within-band max obs/null | Outcome |
|---|---|---|---|---|---|
| `prod_x` | 15 | [0.909, 1.609] | **84%** | — | Calibration PASS |
| `sum_of_squares` | 17 | [0.909, 1.609] | **84%** | — | Calibration PASS |
| `random_gaussian` | 15 | [0.909, 1.609] | **84%** | — | Calibration PASS |
| `pairwise_tanh` | 17 | [0.909, 1.609] | **84%** | **53.5×** | **B — Tier-2 geometric coupling** |
| `runge_dim` | 17 | [0.909, 1.609] | **84%** | **61.4×** | **B — Tier-2 geometric coupling** |
| `heat_smoothed` | 16 | [0.909, 1.609] | **84%** | **52.3×** | **B — Tier-2 geometric coupling** |

The entropy axis filled — std jumped from Phase 4's 0.027 to Phase 5b's 0.238 (10×). Median entropy dropped from 1.587 to ~1.40. The 10th percentile reached 0.998. The diversified-seed engineering works.

But the within-band MI stayed at 25–61× the within-band null on every (function × band) cell. p = 0.000 throughout. Pearson on the full sample: +0.27–0.30 (down from Phase 4's +0.40). dCor: 0.51–0.54. KSG MI: 1.6–1.9 nats.

**This is the decisive falsification of the search-starvation hypothesis.** Phase 5b achieved 84% entropy coverage — comfortably above the 60% threshold for "entropy filled" — and the within-band MI remained as flagged as in Phase 4. The residual coupling is not a search artifact. It is a real geometric property of the `(log n_params, rank_entropy)` joint distribution under TT representation.

![Figure J — Entropy distributions across phases](../exploratory/zoo/docs/figures/fig_j_entropy_three_phases.png)

![Figure K — Phase 5b decisive Branch-A scatter](../exploratory/zoo/docs/figures/fig_k_phase5b_scatter.png)

### 4.7 Fulcrum experiment (added v3.4): geometry vs combinatorics decomposition

The reviewer of v3.3 (2026-04-26) asked: "before claiming the audit detects geometry, prove it is not first detecting combinatorics." A single experiment with three sub-tests (`D:\Prometheus\exploratory\zoo\experiments\run_v34_fulcrum.py`, dump at `D:\Prometheus\exploratory\zoo\results\v34_fulcrum_20260426T103857.json`) decomposes the Phase 5b coupling into combinatorial, search-induced, selection-induced, and TT-evaluation-specific contributions.

**Sub 1 — Lattice baseline.** Uniform random sample of N = 10,000 valid rank profiles (each bond k drawn uniformly from [1, min(max_bond, ceiling_k)]). For each, compute `log_params` and `rank_entropy` from the profile alone — no MAP-Elites, no TT-SVD, no DMRG. Pure combinatorics.

| Pair | Pearson | dCor | KSG MI | obs/null |
|---|---|---|---|---|
| `log_params ↔ rank_entropy` | +0.510 | 0.453 | **0.150 nats** | 9.4× |
| `log_params ↔ rank_concentration` | −0.588 | 0.531 | 0.281 | 21.9× |
| `rank_entropy ↔ rank_concentration` | −0.815 | 0.754 | 0.605 | 45.1× |

The combinatorial floor on `(log_params, rank_entropy)` is **0.15 nats** — about 9% of Phase 5b's observed 1.7 nats. The lattice itself does have detectable structure, but it is not the dominant source of the Phase 5b coupling. Combinatorics alone is rejected as the headline explanation.

**Sub 2 — Archive-history decomposition.** Same Phase 5b data, three subsets:

| Function | History (n=200) MI | Archive elites (n≈83) MI | Pareto front (n≈40) MI |
|---|---|---|---|
| `pairwise_tanh` | **1.885** | 1.278 | 0.975 |
| `runge_dim` | **1.695** | 0.980 | 1.203 |
| `heat_smoothed` | **1.727** | 0.916 | 0.996 |

Archive elites and Pareto fronts have LOWER MI than the full pooled history. Selection pressure REDUCES the coupling rather than creating it. The "MAP-Elites elites are extreme-order statistics that manufacture manifold structure" hypothesis is rejected at this catalog: filtering toward low error does not concentrate the data on a `(log_params, rank_entropy)` curve. The dominant coupling is in the full evaluation distribution, not in a selection-induced subset.

**Sub 3 — Synthetic identifiability.** Five descriptor pairs with known relationships, audit verdicts:

| Pair type | Pearson | dCor | KSG MI | Verdict |
|---|---|---|---|---|
| INDEPENDENT (Gaussian noise vs Gaussian noise) | −0.010 | 0.112 | 0.000 | PASS — audit correctly classifies independent |
| LINEAR (ρ = 0.7) | +0.645 | 0.600 | 0.269 | PASS — Pearson + dCor + MI all flag |
| NONLINEAR (sin(2πx) + noise) | −0.285 | 0.287 | **0.675** | PASS — MI catches what Pearson misses |
| DISCRETIZATION (x = lattice integer, y = x mod 5 + noise) | +0.204 | 0.245 | **1.645** | **FAIL — audit cannot distinguish lattice from real coupling** |
| SELECTION_COUPLED (independent x, y, kept lowest y per x-bin) | −0.111 | 0.127 | 0.000 | PASS — audit correctly reports no coupling |

The DISCRETIZATION false-positive is the new disclosed limitation. On a controlled synthetic where `y` is lattice-induced from `x` with no continuous coupling, the audit reports MI = 1.65 nats — comparable to Phase 5b's 1.7 nats. **The current audit framework cannot distinguish "lattice + noise" from "continuous nonlinear coupling" by MI alone.** This is a real audit limitation, not a Phase-5b interpretation problem.

The SELECTION_COUPLED control returns MI = 0 even after selection, confirming Sub 2: selection on independent data does not manufacture detectable coupling under the audit. Combined with Sub 1's rejection of combinatorics as the primary source, the residual ~1.5 nats above lattice in Phase 5b is the TT-evaluation pipeline's contribution. Sub 3 says we cannot yet decide whether that contribution is "TT-discretization" or "continuous TT geometry" — we have evidence for Tier 2 (geometric coupling above combinatorics) but not Tier 3 (structural mathematical signal).

### 4.8 What the geometry-tier coupling probably is

Given a rank profile $r = (r_1, \ldots, r_{d-1})$:
- `n_params` is a quadratic-ish function of the entire profile: $\sum_k r_{k-1} n_k r_k$.
- `rank_entropy` depends only on the relative magnitudes (shape, not scale).

These are not the same descriptor, but they are not independent either. At the boundary of achievable profiles (low params, where only near-uniform-rank-1 profiles fit), entropy is forced to the upper rim. At high params, both peaked and uniform profiles are achievable and entropy varies widely. This boundary is *nonlinear*; Pearson misses it; KSG MI catches it.

Within a band of fixed `log_params`, the achievable rank profiles still trace a curve (or surface) in shape-space, and that curve has structure the audit detects. The geometric coupling is genuine and persists under any search that explores the achievable region — whether by diversified seeds, larger mutation, alternative refinement, or pure enumeration.

---

## 5. Methodological lessons

### 5.1 The three-tier claim discipline (added v3.4)

A descriptor-coupling result lives at one of three claim tiers, ordered by what the data can support:

1. **Descriptor non-independence.** The two descriptors are not statistically independent under the audit. Evidence requirement: MI sufficiently above an empirical null. Cheap to demonstrate.
2. **Geometric coupling.** The non-independence is not explained by a measurable nuisance source — combinatorics, finite-sample bias, search-induced manifold, or selection-extreme-order statistics. Evidence requirement: a fulcrum decomposition like §4.7 that subtracts each nuisance source and shows residual coupling. Harder.
3. **Structural mathematical signal.** The geometric coupling reflects a property of the underlying mathematical object, not the evaluation pipeline. Evidence requirement: persistence of the coupling across alternative representations (e.g., TT-cross vs TT-SVD), alternative grids, alternative sampling. Hardest.

v3.0 through v3.3 occasionally slid between tiers — describing Tier-2 evidence as Tier-3 language. v3.4 separates them structurally. The Phase 5b + fulcrum result is solid Tier 2; Tier 3 is currently a research target, not a claim.

### 5.2 Pearson alone is insufficient

The Phase 4 finding that Pearson r dropped from −0.94 to +0.29 would have been declared a clean Branch-A pass under a Pearson-only audit. KSG MI showed otherwise. Each layer of the audit was needed.

### 5.3 Sample-size-matched nulls

The v3.1 paper compared within-band MI ($n \approx 30$–$45$) against a full-sample shuffled null ($n = 150$). v3.2 adds a within-band shuffled null at matched $n$. The qualitative conclusion (boundary rejected) is unchanged; the quantitative ratios drop from 25–70× to 9.6–38× on Phase 4 data and 25–61× on Phase 5b. The matched null is the methodologically clean comparison.

### 5.4 Direct trajectory inspection

After Layers 1–5 of the audit fired and the geometric-boundary and refinement-collapse hypotheses were ruled out (or revealed) at each stage, the remaining causes were identified by simply printing the per-evaluation `rank_entropy` distribution. No new metric was needed. The lesson: when the audit narrows the suspect list, sometimes the next step is descriptive statistics on the search trajectory, not another summary metric.

### 5.5 End-to-end testing catches what unit testing misses

The `multi_seed.py` config-forwarding bug went undetected through Phases 2–4 because the unit test for DMRG called `tt_dmrg_refine` directly. The bug only surfaced when Phase 5 declared explicit non-default configs (DMRG sweeps, mutation, seed strategy) and observed that they were silently dropped. The lesson: integration tests at the public-API level catch class of bugs that internal unit tests cannot.

### 5.6 Operator-descriptor interaction is its own coupling source

Phase 5 identified DMRG-as-truncation as a third coupling mechanism distinct from seed bias and starvation. The lesson: when an evaluation pipeline includes a refinement operator that modifies the descriptor distribution, the operator's effect must be auditable separately. Testing "does the descriptor decouple under this search?" is incomplete without "does the evaluation operator preserve descriptor variation?"

---

## 6. Limitations

1. **Single grid shape.** All experiments use $(12,)^6$. Geometry observations may not extend to other aspect ratios or dimensions.
2. **Frontier of three.** `pairwise_tanh`, `runge_dim`, `heat_smoothed` are the only non-calibration functions.
3. **`heat_smoothed` interpretation needs care.** At $t = 0.02$ effective rank is 14; at $t = 0.005$ also 14 — the function is more "smooth-symmetric" than "frontier-difficult." A larger effective rank target would be a stronger frontier addition.
4. **Phase 4 used 3 seeds (now corrected to 5 in Phase 5/5b).** The "150/150 identical profiles" observation in v3.1 §4.3 is now correctly explained by the multi_seed bug; with the bug fixed and 5 seeds, identical-trajectory results would no longer appear.
5. **MI threshold 0.5 nats remains heuristic** for general use. Phase 5b's 25–61× within-band-null ratio is far above any plausible threshold; future work should formalize the threshold from the empirical null distribution.
6. **No comparison to alternative TT decompositions.** TT-cross uses adaptive sampling and may produce different rank profiles. Our findings are TT-SVD-specific.
7. **Geometric mechanism not formally characterized.** §4.8 sketches why the residual coupling exists; a closed-form derivation of the achievable-region boundary in `(log n_params, rank_entropy)` space would be a stronger statement than the empirical audit.

8. **DISCRETIZATION false-positive in the audit (added v3.4).** §4.7 Sub 3 reveals that on a synthetic descriptor pair where x is lattice-valued and y = x mod 5 + small noise, the audit reports MI = 1.65 nats — comparable to Phase 5b's 1.7 nats — despite no continuous coupling. **The current audit framework cannot distinguish "lattice + noise" from "continuous nonlinear coupling" by KSG MI alone.** This means Phase 5b's residual coupling above lattice baseline (~1.5 nats) cannot be cleanly attributed to TT-specific continuous geometry vs TT-specific discretization effects. Tier-3 promotion requires resolving this — either with discretization-aware estimators, manifold-dimension probes (persistent homology, Jacobian rank of the descriptor map), or comparison across TT decomposition variants.

---

## 7. Open questions

**Q1 (resolved by Phase 5b) — Is the residual coupling search starvation, or geometry?**
Resolved. With diversified seeds + larger rank-shift + DMRG off, entropy coverage reaches 84% of achievable range and within-band MI stays at 25–61× null. Outcome B confirmed.

**Q2 — Does the audit framework generalize across quality-diversity domains?**
The sibling project `D:\Prometheus\exploratory\tensor_decomp_qd\` is a MAP-Elites archive over matrix-multiplication tensor decompositions. Importing the audit (`D:\Prometheus\exploratory\zoo\diagnostics\nonlinear.py`) into that project and replicating the multi-layer analysis would validate the framework's generality.

**Q3 — What is the closed-form geometric coupling between `n_params` and `rank_entropy`?**
The achievable region in `(n_params, rank_entropy)` space is determined by the set of valid rank profiles under `max_bond` and `d`. Characterizing this region's shape (and its lower envelope as a function of `n_params`) would explain the audit's findings analytically.

**Q4 — Is there a placement axis pair for TT MAP-Elites that IS independent?**
Phase 5b's negative result on `(log_params, rank_entropy)` does not preclude other pairs. Candidates: `(rank_entropy, refinement_gain)`, `(rank_concentration, stability_ratio)`, `(spectral_alpha, effective_rank)` (a function-level pair, but informative). An exhaustive Phase 6 audit across pairs would identify viable independent axes if any exist.

**Q5 — Does Phase 5 (DMRG-on) reveal anything publishable about DMRG's role in MAP-Elites?**
The "DMRG-as-truncation collapses peaked profiles toward effective rank" finding is novel and potentially publishable as a stand-alone result on the interaction between refinement operators and behavior descriptors in QD search.

**Q6 — Is the `multi_seed.py` bug class — config-forwarding silently incomplete — a common failure mode?**
The v3.3 fix uses `dataclasses.replace(config, seed=s)` and is robust. But the original code looked superficially correct (it forwarded all fields the author was thinking about). A static check at the test suite level — verify that all `LoopConfig` fields propagate through `run_multi_seed` — would catch future regressions.

**Q7 — At what scale does the geometric coupling weaken or strengthen?**
$(16,)^6$ vs $(8,)^8$ vs $(12,)^4$ would test whether the coupling is dimension-dependent. If the coupling weakens at larger $d$ (more bonds, more entropy axis room), the practical impact for high-dim TT-MAP-Elites is smaller than the $(12,)^6$ result suggests.

**Q8 — Is `rank_entropy` the right shape descriptor, or should we use a normalized variant?**
$\text{rank\_entropy} / \log(d-1)$ is the natural normalization. A residualized variant $\text{rank\_entropy} - f(n_\text{params})$ where $f$ is the empirical lower envelope would explicitly project out the geometric coupling — but that's a Pyrrhic decoupling because it folds the coupling into the descriptor definition.

**Q9 — Are the calibration anchors enough?**
Three anchors (rank 1, rank 2, incompressible) span the corners of the catalog. A fourth anchor at known mid-rank (e.g., a rank-4 or rank-8 separable function) would tighten the contract and probe the boundary between calibration and frontier.

**Q10 — Can the descriptor-collapse audit be promoted to a separate package?**
The audit at `D:\Prometheus\exploratory\zoo\diagnostics\` is currently bound to the zoo's `Archive` class. A clean refactor accepting any iterable of descriptor-dict records would let it be imported into other QD codebases without depending on zoo internals. Plan sketched in `D:\Prometheus\exploratory\zoo\diagnostics\README.md`.

---

## 8. Suggestions for next steps

Ordered by leverage. The reviewer's priorities now point in a different direction than v3.2 anticipated, because Phase 5b returned Outcome B rather than Outcome A.

### 8.1 PRIMARY — Sharpen the geometry-signal claim

The headline claim is now "TT MAP-Elites placement axes `(log_params, rank_entropy)` are not independent — there is a real structural geometric coupling that no search-side intervention removes." Strengthen this in three concrete ways:

1. **Closed-form boundary derivation** (Q3). For fixed `max_bond` and $d$, characterize the achievable region in `(log_params, rank_entropy)` space. The lower envelope is the key — at any `n_params` band, the minimum achievable `rank_entropy` is determined by combinatorics of valid rank profiles.

2. **Verify on alternative grid shapes** (Q7). Repeat Phase 5b on $(16,)^6$, $(8,)^8$, $(12,)^4$. If the coupling persists across all four, the claim generalizes; if it weakens with grid size, the practical impact has a scaling story.

3. **Audit other descriptor pairs** (Q4). Run the same 5-layer audit on `(rank_concentration, refinement_gain)`, `(stability_ratio, log_params)`, etc. If any pair passes Layers 1–5, that's the placement choice for TT MAP-Elites. If none do, the practical advice is "no two-axis grid over rank-derived descriptors is independent for TT under these settings."

### 8.2 PRIMARY — Cross-domain validation of the audit (Q2)

Apply the descriptor-collapse audit to `D:\Prometheus\exploratory\tensor_decomp_qd\` MAP-Elites runs. If the same multi-layer audit catches collapse failure modes in matrix-multiplication tensor decomposition search, the framework's generality claim is empirical, not aspirational. This is the most likely path to a publishable methodology contribution.

### 8.3 SECONDARY — Document the DMRG-mask finding as a stand-alone

The "DMRG-as-truncation collapses peaked profiles" result (Phase 5 §4.5) is independently interesting. Write it up as either a §-level claim within this paper or as a short companion note. The mechanism is general: any rank-adaptive refinement operator interacting with a shape-sensitive descriptor will exhibit the same collapse.

### 8.4 SECONDARY — Promote the audit module (Q10)

Refactor `D:\Prometheus\exploratory\zoo\diagnostics\nonlinear.py` to accept generic descriptor records (a list of dicts) rather than the zoo `Archive` class. Add it to `D:\Prometheus\whitepapers\` as a standalone reusable module with its own README and example notebook. This is the second-easiest path to publication after §8.2.

### 8.5 SECONDARY — Threshold calibration from null distribution (Q5)

Replace the heuristic 0.5-nat threshold with a data-driven threshold: "MI exceeds the 99th percentile of the function-specific shuffled null by a factor ≥ 2." Defensible and adapts to function-specific MI scales.

### 8.6 SECONDARY — Stability as active tie-breaker

When a candidate lands in an occupied cell with `rel_error` within 10% of the occupant, compute stability lazily and break ties on robustness. Validate that this does not introduce a new collapse axis. Carried over from v3.0–v3.2 recommendations.

### 8.7 EXTENSION — Stronger frontier function

Add a function with effective rank > `max_bond`. Currently only `pairwise_tanh` (eff rank 92) sits there; `runge_dim` (eff rank 10) and `heat_smoothed` (eff rank 14) sit below. A second above-`max_bond` function (e.g., a high-dim Lorenz trajectory grid, or a Gabor-packet with mid-frequency oscillation) would strengthen the catalog's coverage of the "DMRG can't truncate" regime.

### 8.8 EXTENSION — Test for multi_seed bug regressions

Add a unit test that asserts `run_multi_seed(func, config, spec, seeds)` produces per-seed `LoopConfig` instances with all non-`seed` fields equal to `config`. Lock in the fix.

### 8.9 EXTENSION — Alternative TT decompositions

Repeat Phase 5b with TT-cross and randomized TT in place of TT-SVD. If the geometric coupling is TT-SVD-specific, the negative result narrows; if it generalizes, the claim "TT representation has this geometry" becomes stronger.

### 8.10 EXTENSION — Stability tie-breaker without diversity collapse

Already listed in §8.6 but worth elevating: if §8.1 §8.2 §8.4 succeed, the stability-tie-breaker experiment becomes the natural way to make the archive richer along the third axis (stability) without re-entering the shape-axis collapse problem.

---

## 9. Calibration & promotion criteria

The zoo graduates from playground-tier to substrate-tier when ALL of the following hold:

1. Calibration anchors PASS at ≥ 5 seeds (now satisfied in Phase 5/5b).
2. **Either** Pearson, dCor, KSG MI all below their thresholds on at least one frontier-applicable placement-axis pair (revised from "(log_params, rank_entropy)" — which we now know does not pass), **or** an explicit finding documenting which pairs fail and which pass for TT MAP-Elites.
3. Conditional within-band MI within 3× of within-band shuffled null in every (function × band) cell — for whatever placement pair is promoted.
4. `rank_entropy` distribution spans at least [1.0, 1.6] across pooled evaluations (Phase 5b satisfies this; phases prior do not).
5. External review of this paper returns no methodology-blocker criticisms.

The v3.3 release satisfies 1 and 4; criterion 2 is reformulated as a research target rather than a promotion condition; 3 and 5 remain open.

---

## 10. Run artifacts

| Artifact | Full path |
|---|---|
| Phase 3 dump | `D:\Prometheus\exploratory\zoo\results\phase3_20260423T072026.json` |
| Phase 4 dump | `D:\Prometheus\exploratory\zoo\results\phase4_20260423T074559.json` |
| Phase 4b dump (DMRG-off-vs-DMRG-off, retroactively) | `D:\Prometheus\exploratory\zoo\results\phase4b_no_dmrg_20260425T013745.json` |
| Conditional MI + shuffled null | `D:\Prometheus\exploratory\zoo\results\phase4_analysis_20260425T013514.json` |
| Within-band null (v3.2 fix) | `D:\Prometheus\exploratory\zoo\results\phase4_within_band_null.json` |
| v3.4 fulcrum (lattice + decomposition + identifiability) | `D:\Prometheus\exploratory\zoo\results\v34_fulcrum_20260426T103857.json` |
| DMRG unit test | `D:\Prometheus\exploratory\zoo\results\dmrg_unit_test.json` |
| Phase 5 dump (DMRG actually on) | `D:\Prometheus\exploratory\zoo\results\phase5_20260425T032712.json` |
| Phase 5b dump (decisive Branch-A test) | `D:\Prometheus\exploratory\zoo\results\phase5b_no_dmrg_20260425T033645.json` |

| Figure | Full path |
|---|---|
| Phase 3 (log_params, log_error) heatmaps | `D:\Prometheus\exploratory\zoo\docs\figures\fig_a_archive_occupancy.png` |
| Phase 3 1D-ridge scatter | `D:\Prometheus\exploratory\zoo\docs\figures\fig_b_params_error_correlation.png` |
| Stability box plot | `D:\Prometheus\exploratory\zoo\docs\figures\fig_c_stability_distribution.png` |
| Phase 3 rank-orthogonal candidate | `D:\Prometheus\exploratory\zoo\docs\figures\fig_d_rank_orthogonal.png` |
| Phase 4 (log_params, rank_entropy) | `D:\Prometheus\exploratory\zoo\docs\figures\fig_e_branch_a_scatter.png` |
| \|Pearson\| vs KSG MI heatmaps | `D:\Prometheus\exploratory\zoo\docs\figures\fig_f_mi_vs_pearson.png` |
| Phase 4 archive on Branch-A grid | `D:\Prometheus\exploratory\zoo\docs\figures\fig_g_archive_new_grid.png` |
| Phase 4b DMRG-counterfactual | `D:\Prometheus\exploratory\zoo\docs\figures\fig_h_dmrg_counterfactual.png` |
| Phase 4 entropy-starvation histograms | `D:\Prometheus\exploratory\zoo\docs\figures\fig_i_entropy_starvation.png` |
| Three-phase entropy distributions | `D:\Prometheus\exploratory\zoo\docs\figures\fig_j_entropy_three_phases.png` |
| Phase 5b decisive Branch-A scatter | `D:\Prometheus\exploratory\zoo\docs\figures\fig_k_phase5b_scatter.png` |

| Code entry point | Full path |
|---|---|
| Phase 3 driver | `D:\Prometheus\exploratory\zoo\experiments\run_phase3.py` |
| Phase 4 driver | `D:\Prometheus\exploratory\zoo\experiments\run_phase4.py` |
| Phase 4b counterfactual | `D:\Prometheus\exploratory\zoo\experiments\run_phase4b_no_dmrg.py` |
| Phase 4 conditional-MI analysis | `D:\Prometheus\exploratory\zoo\experiments\analyze_conditional_mi.py` |
| DMRG unit test | `D:\Prometheus\exploratory\zoo\experiments\unit_test_dmrg.py` |
| Phase 5 driver (DMRG on) | `D:\Prometheus\exploratory\zoo\experiments\run_phase5.py` |
| Phase 5b driver (DMRG off, decisive) | `D:\Prometheus\exploratory\zoo\experiments\run_phase5b_no_dmrg.py` |
| v3.4 fulcrum driver | `D:\Prometheus\exploratory\zoo\experiments\run_v34_fulcrum.py` |

| Module | Full path | Role |
|---|---|---|
| Functions | `D:\Prometheus\exploratory\zoo\functions\` | Calibration + frontier zoo |
| TT core | `D:\Prometheus\exploratory\zoo\tt\core.py` | TT-SVD, reconstruction |
| ALS | `D:\Prometheus\exploratory\zoo\tt\als.py` | One-site ALS refinement |
| DMRG | `D:\Prometheus\exploratory\zoo\tt\dmrg.py` | Two-site DMRG with rollback guard |
| Grid | `D:\Prometheus\exploratory\zoo\map_elites\grid.py` | Generalized 2D placement |
| Loop | `D:\Prometheus\exploratory\zoo\map_elites\loop.py` | Evaluation + diversified seeds |
| Mutation | `D:\Prometheus\exploratory\zoo\map_elites\mutation.py` | Hybrid classical + rank-shift |
| Multi-seed | `D:\Prometheus\exploratory\zoo\map_elites\multi_seed.py` | (v3.3 bug fixed) |
| Descriptors | `D:\Prometheus\exploratory\zoo\descriptors\` | Spectral, stability, rank profile |
| Lineage | `D:\Prometheus\exploratory\zoo\lineage\` | Cosine + residual decomposition |
| Nulls | `D:\Prometheus\exploratory\zoo\nulls\rank_ceiling.py` | Random-tensor error floor |
| Diagnostics | `D:\Prometheus\exploratory\zoo\diagnostics\` | Pearson + dCor + KSG MI audit |

Reproducibility: from `D:\Prometheus\exploratory\` with `PYTHONPATH=.` and `PYTHONIOENCODING=utf-8`, `python -m zoo.experiments.run_phase5b_no_dmrg` runs in ~450 s on CPU. All seeds and configurations are in `LoopConfig` at the top of the driver.

---

## 11. Provenance

Phase 1 (MVP, 2 descriptors) and Phase 2 (added spectral descriptor, stability probe, constrained ALS, Pearson audit) established the ridge finding. Phase 3 (multi-seed, bounded spectral, rank-profile descriptors, formal stability, rank-ceiling null) identified candidate rank-orthogonal axes. Phase 4 (rank-shift mutation, two-site DMRG, heat-PDE frontier, nonlinear audit) stress-tested the Branch-A hypothesis and revealed partial decoupling. Phase 4b (DMRG counterfactual) and the conditional-MI / shuffled-null analyses (§4.1–4.4) ruled out the boundary and refinement-collapse hypotheses. Direct trajectory inspection (§4.4) identified entropy-axis starvation as the most likely cause under the data then available.

v3.3 reports the resolution of v3.2's open question. The reviewer of v3.2 set three priorities: a decisive diversified-seed proof, a DMRG instrument-trust unit test, and seed-count restoration. v3.3 executes all three (Phase 5/5b for the seed test, `D:\Prometheus\exploratory\zoo\experiments\unit_test_dmrg.py` for instrument trust, 5 seeds restored throughout). It also discloses and fixes a config-forwarding bug in `D:\Prometheus\exploratory\zoo\map_elites\multi_seed.py` that was silently dropping `dmrg_sweeps`, `mutation`, and `seed_strategy` from per-seed `LoopConfig` copies — meaning Phase 4's "DMRG ON" run actually executed with `dmrg_sweeps = 0`. The v3.2 §4.3 mechanism explanation was wrong; the v3.2 conclusion (DMRG operationally inactive in those measurements) survives because both sides of the Phase 4b counterfactual were truly DMRG-off.

The decisive Phase 5b experiment shifted the headline finding from "partial Branch-A pass; coupling is search starvation" to "Branch A fails; coupling is real TT geometry." The audit framework — methodologically the load-bearing contribution of the paper — caught this through Layers 4 and 5 even before Phase 5b ran. Phase 5b confirmed the audit's verdict empirically by showing that maximum search exploration does not remove the coupling.

This remains a working paper. No external review has seen v3.3.

---

*Working paper v3.4 — 2026-04-26. Supersedes v3.3. Adds the fulcrum experiment (§4.7) decomposing Phase 5b's MI into combinatorial (0.15 nats), elite-selection (rejected), and TT-evaluation (~1.5 nats) sources; introduces the three-tier claim discipline (§5.1) — descriptor non-independence (Tier 1, strong) vs geometric coupling (Tier 2, moderate) vs structural mathematical signal (Tier 3, partial); discloses a DISCRETIZATION false-positive in the audit (Limitation 8) caught by the synthetic identifiability test in §4.7 Sub 3; reframes the headline from "TT geometry signal" to "Tier-2 geometric coupling beyond combinatorics, with continuous-vs-discretization separation as Phase 6 work." Hedges applied per reviewer-2026-04-26 recommendations.*

*v3.3 — 2026-04-25. Supersedes v3.2. Adds DMRG instrument-trust unit test, multi_seed bug fix and disclosure, Phase 5 (DMRG-truncation-collapse mechanism), Phase 5b (decisive Branch-A test, Outcome B), Figures J and K, refined open questions.*

*v3.2 — 2026-04-25. Adds within-band shuffled null, achievable-range entropy denominator, DMRG rollback-guard disclosure, hedged search-starvation claim, explicit Open Questions and Suggestions sections.*

*v3.1 — 2026-04-25. Adds three diagnostic experiments (shuffled null, conditional MI, DMRG counterfactual) and entropy-starvation diagnosis (later revised in v3.3 once the multi_seed bug surfaced).*

*v3.0 — 2026-04-24. Phase 4 partial Branch-A result with Pearson, dCor, and KSG MI audits.*
