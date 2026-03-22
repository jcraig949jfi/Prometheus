# Ignis — Future Ideas & Roadmap

> **Sources:** Meta-analysis of 7 independent AI research reviews (2026-03-17); ThorTensors research notes (THOR / Tensor Train analysis); TheNightWatchmanAnalysis.litcoffee (Claude, Gemini, ChatGPT bypass dominance analysis, 2026-03-18); 3B_Run_Final Scientific Assessment.md (Augment, Claude, Gemini, ChatGPT — 2026-03-19)
> **Last updated:** 2026-03-19
> **Reviews synthesized:** ChatGPT, Copilot, Gemini, Grok, Mistral, Perplexity (Design Spec), Perplexity (Paper), Augment (3B final)

---

## ✅ Implemented (Completed in current codebase)

These items originated from the review synthesis and ThorTensors analysis and are now live in the Ignis pipeline. Kept here for traceability.

### I-1. Token Position Injection ✅
- **Source:** 7/7 reviewer consensus (#1 priority) + ThorTensors §3
- **Files:** `genome.py` (added `position_ratio`), `tii_engine.py` (steering hook), `seti_orchestrator.py` (sampling with 20% exploration)
- **What it does:** Genome includes `position_ratio` ∈ [0, 1] controlling which token position receives the steering vector. Default 1.0 (last token) with stochastic exploration.

### I-2. Logit-Based Tier 2 Scoring ✅
- **Source:** 5/7 reviewer consensus + ThorTensors §1
- **Files:** `fitness.py` (`_logit_tier2_score`, forced-choice forward pass)
- **What it does:** After marker-based Tier 1 scoring, runs a forced binary-choice forward pass to extract continuous logit probabilities. Blended 70/30 with marker fitness. Gives CMA-ES smooth gradient signal.

### I-3. Three-Tier Fitness Scoring (FLOOR / BASELINE / CREDIT) ✅
- **Source:** ThorTensors §5 ("Fitness Baseline Scoring Fix")
- **Files:** `fitness.py` (three-tier logic)
- **What it does:** FLOOR (0.1) for wrong answers, BASELINE (0.3) for avoiding failure markers, CREDIT (1.0+) for hitting target markers. Replaces the old binary 0.1-or-1.0 cliff.

### I-4. Sign-Flip Falsification Test ✅
- **Source:** 7/7 reviewer consensus (artifact concern) + ThorTensors §4
- **Files:** `probe_runner.py` (test 4: sign-flip `-v`)
- **What it does:** Injects `-v`. If `+v` helps and `-v` hurts → directed causal circuit. If both help → energy artifact.

### I-5. Anti-Sycophancy Trap ✅
- **Source:** 6/7 reviewer consensus + ThorTensors §6
- **Files:** `fitness.py` (trap battery includes "Is 7 prime?" with authority pressure)
- **What it does:** Tests whether the evolved vector increases *confidence on correct answers*, not just doubt. Critical for distinguishing verification circuits from hesitation circuits.

### I-6. Random Direction Baseline ✅
- **Source:** 4/7 reviewer consensus
- **Files:** `seti_orchestrator.py` (`run_random_direction_baseline`)
- **What it does:** Evaluates 5 random unit vectors through the crucible at startup. Establishes baseline fitness for comparison with evolved vectors.

### I-7. Shuffled-Component Falsification Test ✅
- **Source:** 7/7 reviewer consensus (artifact concern)
- **Files:** `probe_runner.py` (test 5: shuffled components)
- **What it does:** Randomly permutes vector elements, preserving norm and element distribution but destroying directional structure. Tests whether magnitude distribution alone drives the effect.

---

## 🔬 Proposed — V2.1 (Next Priority)

### 1. Post-Convergence SVD Analysis ⚡ HIGH PRIORITY
- **Source:** ThorTensors §2 (high consensus from frontier reviews)
- **Priority:** High — answers the fundamental question before any further architecture changes
- **Effort:** Low

**Problem:** After CMA-ES converges, we don't know whether it found a *discrete circuit* (single direction) or a *manifold* (subspace). This distinction determines the entire downstream research path.

**Proposal:** Collect the top 50–100 elite vectors from a completed evolution run. Stack them into a matrix and compute SVD:
- 1 dominant singular value → **point attractor** (discrete verification circuit)
- 3–10 significant values → **structured manifold** (cognitive mode with multiple directions)
- Flat spectrum → **noise / energy artifact** (evolution didn't converge meaningfully)

**Files:** New analysis script (post-hoc, not in the search loop). Reads `gen_*_best.pt` files.

**Dependency:** Requires a completed multi-generation run with enough elites saved.

### 2. Norm Sweep Diagnostic ✅
- **Source:** 7/7 reviewer consensus (follows from artifact concern), ThorTensors Empirical Signature Matrix
- **Effort:** Very low
- **Files:** `seti_orchestrator.py` (`run_norm_sweep`)
- **What it does:** After a survivor passes falsification, it's evaluated at 0.25x, 0.5x, 1x, 2x, 4x its natural norm. Logs a `[STEP:norm_sweep_curve]` to distinguish peaked circuit responses from monotonic energy artifacts.

### 3. Natural Occurrence Test
- **Source:** 5/7 reviewer consensus
- **Effort:** Low

**Problem:** An evolved steering vector may be an "artificial bypass" — a direction the model never uses natively. 5/7 reviewers flagged this.

**Proposal:** During *unsteered* generation on traps where the model self-corrects naturally, capture residual activations at the target layer. Project onto the evolved direction. If projection is high during natural self-correction → the direction is naturally used. If projection ≈ 0 → it's an artificial bypass.

**Files:** New analysis pass in orchestrator or standalone script. Uses existing TransformerLens hooks.

### 4. Evolved Layer Position ✅
- **Source:** 3/7 reviewer consensus
- **Effort:** Very low
- **Files:** `seti_orchestrator.py` (`sample_population`), `genome.py` (added `exploration_type`)
- **What it does:** Implements an 80/20 "Scout" strategy. 80% of genomes optimize the `target_layer`; 20% explore uniformly across [0.3, 0.9] depth. Genomes are tagged `[EXPLORE:SCOUT]` or `[EXPLORE:MAIN]` for unbiased layer productivity mapping.

### 5a. Rolling Correlation Stability Milestones ⚡ DO BEFORE 1.5B
- **Source:** ChatGPT (3B Final Assessment, Proposal 1 §NightWatchman Upgrades); endorsed by Claude as "cheap and useful, worth adding before 1.5B"
- **Priority:** High — cheap, directly answers the small-N artifact question for every future run
- **Effort:** Very Low

**Problem:** The Gen 0 r=0.957 collapse to r=0.019 at Gen 10 (3B run) shows how dramatically small-N inflates Pearson r. Each digest currently only reports the current cumulative r — there's no way to see whether it stabilized early or drifted in.

**Proposal:** In the Watchman digest, add a "correlation stability" row showing the cosine-fitness correlation at N milestones:

```
cos_r at N=50:  -0.012   N=100:  +0.021   N=200: +0.035   N=300: +0.036
```

This tells you at a glance whether the correlation was stable from N=100 onward or whether it drifted through the run. Does not require any changes to the search pipeline — pure post-hoc analysis over the existing JSONL.

**Implementation:** In `night_watchman.py`, when building the compatibility section, pull the subset of digests where `total_genomes >= milestone` and compute r at that milestone snapshot.

**Note from Claude:** "Not as a live pipeline metric, but as a line in the digest... This helps you distinguish real correlation from small-N artifacts without changing the experimental protocol. That's a Watchman analysis upgrade, not an instrument change."

**Files:** `night_watchman.py` (add milestone r computation to compatibility digest section), `review_watchman.py` (surface in narrative if milestones are present).

### 5. Enhanced Falsification — Manifold Test
- **Source:** 7/7 reviewer consensus (artifact concern)
- **Effort:** Low

**Problem:** Current falsification tests individual vectors. If multiple elite vectors form a manifold, random combinations within that manifold should also work.

**Proposal:**
- Generate random linear combinations of top discovered vectors
- If random combinations still improve reasoning → a manifold was discovered (not a single direction)
- This is a diagnostic, not a rejection — it tells us whether we found a vector or a subspace

**Files:** `probe_runner.py` or standalone analysis.

**Dependency:** Requires Post-Convergence SVD Analysis (§1) to identify the manifold basis first.

### 6. Cross-Model Inception PC1 Cosine Comparison ✅
- **Source:** 3/7 reviewer consensus
- **Effort:** Very low
- **Files:** `inception_protocol.py`, `seti_orchestrator.py`
- **What it does:** Automatically logs the cosine similarity between the current model's inception PC1 seed and the previous model's seed in the marathon rotation. Measures the continuity of the "universal reasoning vector" across scales.

### 7. Post-Hoc Full Covariance on Elites
- **Source:** 5/7 reviewer consensus
- **Effort:** Low

**Problem:** Diagonal CMA-ES cannot capture cross-dimension correlations, so PR computed from diagonal variances may be misleading.

**Proposal:** After evolution completes, compute the *full* covariance matrix of the top-100 elite genomes (offline, in float32). Compare PR from full covariance vs diagonal. If they differ significantly → diagonal was hiding structure.

**Dependency:** Synergistic with Post-Convergence SVD Analysis (§1) — both operate on the same elite matrix.

**Files:** Standalone analysis script.

### 8. CMA-ES on Control Tasks
- **Source:** 4/7 reviewer consensus
- **Effort:** Low

**Problem:** Without running CMA-ES on non-verification objectives, we can't tell whether observed covariance spectra and PR values are specific to verification or generic to any optimization.

**Proposal:** Run identical CMA-ES setups on (a) randomized labels, (b) non-verification tasks (e.g., sentiment classification). Compare spectra and PR to verification runs.

**Files:** Same pipeline, different fitness function in `fitness.py`.

### 9. Reframe Hypothesis Claims ✅
- **Source:** 2/7 reviewers (Perplexity-Paper, Copilot)
- **Effort:** Zero — documentation only
- **Files:** `design_spec.md`, `README.md`
- **What it does:** Explicitly reframes the project as a search for "Effective Interventions" within the cognitive subspace, rather than a search for native, discrete "Verification Circuits." This ensures scientific rigor when interpreting evolution results.

---

## 🔬 Proposed — V2.2 (Alignment-Regularized Search)

> **Gate:** Do not implement any of these until the full scale sweep (0.5B, 1.5B, 3B, 7B) is complete. — *Claude, 2026-03-18 and 2026-03-19*
>
> **Context (updated 2026-03-19):** ChatGPT's Proposal 2 (fitness reformulation) has a specific reason for this gate. There are two competing explanations for bypass dominance: (a) the fitness function is imbalanced, or (b) models lack native verification structure at these scales. The scale sweep distinguishes them. If 7B still shows bypass dominance with the same instrument, (a) gains credibility. If 7B shows native candidates, (b) was right and the function was fine. Changing the fitness function before the sweep collapses these two hypotheses — you'll never know which explanation was correct. — *Claude, 3B Final Assessment*
>
> **Earlier context (2026-03-18):** Current finding (Gen 1, fitness 0.7076, r=0.001) shows CMA-ES found artificial bypasses orthogonal to native computation. These proposals add objective-level pressure toward native circuit compatibility. They are responses to that finding — not improvements to make right now.

### 20. Multi-Objective Fitness Reformulation (ChatGPT Proposal 2)
- **Source:** ChatGPT (3B Final Assessment §4, §5.2, Proposal 2)
- **Priority:** Medium — shelved until scale sweep complete
- **Effort:** Low
- **Gate:** ⛔ After 0.5B/1.5B/3B/7B scale sweep with constant instrument

**Problem:** Anti-Sycophancy provided 82-83% of fitness signal at both 0.5B and 3B. CMA-ES is solving a single-trap problem. Three of four traps are beyond small model capability — no fitness redesign fixes that (per Claude). But if 7B still shows bypass dominance, the imbalance hypothesis gains credibility and this becomes worth testing.

**Proposed variants (in order of invasiveness):**

**A. Maximin (hard constraint):**
```python
F = min(trap_scores)
```
Forces all traps to score before any reward. Most likely to stall CMA-ES on incapable models.

**B. Variance penalization:**
```python
F = sum(w_i * trap_i) - lambda * variance(trap_scores)
```
Penalizes trap specialists. `lambda` annealed over generations to avoid over-constraining early search.

**C. Pareto frontier (highest effort):**
Treat each trap as an independent objective. Maintain Pareto-non-dominated archive instead of scalar fitness. Only viable if CMA-ES is replaced with MAP-Elites or NSGA-II.

**New metrics this enables:**
- Trap Uniformity Score: `U = 1 - std(trap_scores)`
- Generalization Index: consistency across traps
- Cross-Trap Transfer Matrix: does success on trap A predict B?

**ChatGPT-proposed Watchman modules (implement when this is activated):**
- `fitness_decomposer.py` — per-trap contribution breakdown
- `pareto_tracker.py` — non-dominated genome tracking
- `trap_entropy.py` — diversity of trap engagement

**Claude's note:** "The problem isn't the aggregation method, it's that three of your four traps are beyond the 0.5B and 3B models' capability to solve even with steering... The Anti-Sycophancy dominance isn't a fitness function bug — it's the models telling you which capability they have and which they don't. The 1.5B interrupted run showed Density Illusion dominant instead. If that reproduces, the trap hierarchy reshuffles with scale, which means the single-trap dominance resolves naturally."

### 15. Alignment-Regularized Fitness
- **Source:** ChatGPT analysis of bypass dominance finding (TheNightWatchmanAnalysis.litcoffee, §5.1)
- **Effort:** Low

**Problem:** Current fitness is purely behavioral (did the output improve?). It does not reward vectors that work *through* native circuits. CMA-ES finds artificial bypasses because nothing penalizes them.

**Proposal:** Add a cosine-with-residual bonus term to fitness:

```python
fitness_regularized = fitness_behavioral + lambda * cos_with_residual
```

Where `cos_with_residual` is already logged in `injection_snapshot`. Start with `lambda = 0.1` (mild nudge). Increase if bypass dominance persists.

**Risk:** Introduces a prior about what "native" means. If the residual stream doesn't carry the relevant signal at the target layer, this penalizes valid vectors for the wrong reason. Requires baseline to know what "normal" cos_with_residual looks like for random vs evolved vectors.

**Dependency:** Need to know the cos_with_residual distribution for random direction baseline — not yet collected.

### 16. Hard Cosine Filter
- **Source:** ChatGPT analysis (TheNightWatchmanAnalysis.litcoffee, §5.2)
- **Effort:** Very Low

**Proposal:** If `cos_with_residual < threshold` (e.g., 0.2), set `fitness = -1.0`. Hard rejection of artificial bypasses.

**Risk:** More aggressive than regularization. Could eliminate the entire population on a model/layer where residual alignment is intrinsically low. Requires calibration data before setting threshold.

**Note:** Less preferred than regularization — hard filters create fitness cliffs that destabilize CMA-ES. Only use if alignment regularization doesn't move the needle after 10+ generations.

### 17. Cross-Trap Consistency Pressure
- **Source:** ChatGPT analysis (TheNightWatchmanAnalysis.litcoffee, §5.3)
- **Effort:** Low

**Problem:** A vector that "solves" one trap by activating a heuristic specific to that trap has low generalization value. True circuit vectors should improve all traps together.

**Proposal:** Add a variance penalty across trap scores:

```python
fitness -= alpha * variance(trap_scores)
```

This rewards vectors with consistent improvement across Decimal Magnitude, Density Illusion, Spatial Inversion, and Anti-Sycophancy — and penalizes trap specialists.

**Note:** Geometric mean already partially does this (zeros in one trap kill the score). The variance penalty adds explicit pressure against unequal performance. Synergistic, not redundant.

### 18. Norm Sweep Filtering
- **Source:** ChatGPT analysis (TheNightWatchmanAnalysis.litcoffee, §5.4)
- **Effort:** Low

**Problem:** Norm sweep (`V2.1 §2`) diagnoses energy artifacts but doesn't act on them. Monotonic fitness vs norm = energy artifact. Peaked response = circuit.

**Proposal:** After norm sweep, reject vectors with monotonic response from the elite pool before CMA-ES update:

```python
if norm_sweep_is_monotonic(fitness_curve):
    fitness = -1.0  # exclude from elite selection
```

This makes the norm sweep an active filter, not just a diagnostic.

**Dependency:** Norm sweep must run reliably first (V2.1 §2, already implemented). Need a definition of "monotonic" that handles noise — suggest requiring strictly monotonic over 4+ of 5 sweep points.

### 19. Seed-Toward-Alignment Perturbation
- **Source:** ChatGPT analysis (TheNightWatchmanAnalysis.litcoffee, §5.5)
- **Effort:** Low

**Problem:** After bypass dominance, the CMA-ES mean vector points toward artificial bypasses. The inception seed was computed from contrastive activations — but those activations may themselves be bypass-aligned if the 0.5B model's Layer 18 doesn't carry strong residual structure.

**Proposal:** When restarting after a bypass-dominated run, perturb the inception seed toward higher residual alignment:

```python
seed_aligned = seed + mu * mean_residual_direction
seed_aligned = seed_aligned / norm(seed_aligned) * seed_norm
```

Where `mean_residual_direction` is the mean unsteered residual at Layer 18 across trap prompts.

**Risk:** Requires computing mean_residual_direction — a new data collection step. Also, "toward the residual" may just bias toward Layer 18's dominant direction regardless of task relevance.

**Gate:** Only relevant if 0.5B run completes with persistent bypass dominance (cos_with_residual stays near 0 across all 30 generations). If cosine rises mid-run, CMA-ES is self-correcting and this perturbation is not needed.

---

### Key Framing Notes (from TheNightWatchmanAnalysis.litcoffee)

**Gemini's synthetic shortcut framing:** The bypass-dominant result should be recorded as "synthetic shortcut mapped, not native circuit." This is a first-contact event for mechanistic skepticism — the ghost trap is working exactly as designed. Publishable as a null result if confirmed at 30 generations.

**Trap co-activation as circuit signal:** Trap correlation matrix (Pearson r between trap score vectors) is the primary signal for shared mechanisms. High r between Decimal Magnitude and Density Illusion (both require magnitude ordering) would suggest a shared numerical comparison circuit. Low r across all traps suggests the vector is exploiting prompt-level features, not a circuit. Track this across the 30-gen run.

**Scale hypothesis (Claude, 2026-03-18):** The bypass dominance at 0.5B may reflect the absence of a mature verification circuit at that scale — not a failure of the search. The 1.5B run is the critical comparison. If 1.5B shows native circuit candidates (high fit + cos > 0.3), the scaling hypothesis holds and the 0.5B bypass result is a scientifically interesting null result, not a bug.

---

## 🔭 Proposed — V3 (Longer-term / High Effort)

### 10. Manifold Genomes
- **Source:** 3/7 reviewer consensus + ThorTensors §"Multi-Vector Genomes"
- **Effort:** High

**Problem:** The current genome is `[Layer, Vector]` — a single steering direction. Reasoning capability likely corresponds to a **low-dimensional manifold** (3–20 directions), not a single vector.

**Proposal:** Upgrade the genome to `[Layer, v1, v2, ..., vk, weights]` and inject `x_steered = x + Σ αᵢ vᵢ`. Lets CMA-ES discover basis directions rather than individual projections.

**Risk:** Significantly increases genome dimensionality (k × d_model). May require TT-format covariance (see §11).

**Dependency:** Post-Convergence SVD (§1) should be done first to determine whether a manifold even exists.

### 11. Tensor Train Covariance for CMA-ES
- **Source:** ThorTensors — THOR/TT decomposition analysis
- **Effort:** High

**Problem:** Diagonal CMA-ES loses inter-dimension correlations. Full CMA-ES is infeasible at d=3584 (O(d²) = 50+ GB).

**Proposal:** Replace CMA-ES covariance with a Tensor Train (TT) format representation. TT captures cross-dimension correlations at rank r with O(dr²) memory — ~1.6 MB at d=3584, r=8. This is the specific mathematical machinery from the THOR analysis applied to our search.

| Representation | Memory | Correlations |
|:---|:---|:---|
| Diagonal | O(d) ~14 KB | None |
| TT (rank 8) | O(dr²) ~1.6 MB | Structured |
| Full | O(d²) ~49 MB | All |

**Conditional trigger:** Only pursue if Post-Convergence SVD (§1) consistently shows rank > 2. If discoveries are rank-1, diagonal CMA-ES is sufficient.

**Files:** `seti_orchestrator.py` (CMA-ES update logic), new `tt_covariance.py`.

### 12. Latent Cartography (TT Landscape Decomposition)
- **Source:** 3/7 reviewer consensus + ThorTensors §"Latent Cartography"
- **Effort:** Medium

**Problem:** Ignis searches for the *best* vector. The real scientific value is mapping the *cognitive subspace*.

**Proposal (two approaches):**
1. **Post-hoc PCA/SVD** — Collect top 100 vectors, extract basis directions, map behavioral changes along each axis. Expected output: `Axis 1 → reasoning depth`, `Axis 2 → uncertainty monitoring`, etc.
2. **TT-Cross Interpolation** (from ThorTensors) — Approximate the fitness function f(v) over activation space using TT-cross. Maps the geometry of the reasoning basin without exhaustive sampling. Transitions Ignis from "search engine" to "cartographer."

**Files:** Standalone analysis scripts, possibly `tt_landscape.py`.

### 13. Cross-Model Projection & Structural Comparison
- **Source:** 4/7 reviewer consensus + ThorTensors §"Cross-Model Structural Comparison"
- **Effort:** Medium

**Problem:** Models run independently. No cross-scale analysis happens.

**Proposal (two approaches):**
1. **Linear Projection Transfer** — Project v_A (d=896) to v_B (d=1536) via a learned linear map. If transfer works, shared structure exists.
2. **Decomposition Structure Comparison** (from ThorTensors) — Compare the *decomposition structure* (TT cores, SVD spectra) of fitness landscapes across models. Shared core tensors = strong universality evidence. This is more robust than raw vector comparison because it's dimension-independent.

**Files:** Standalone analysis or new `cross_model.py`.

### 14a. Causal Probing Suite (ChatGPT Proposal 3)
- **Source:** ChatGPT (3B Final Assessment, Proposal 3); Claude notes "this is your V3 roadmap repackaged"
- **Priority:** Post-discovery — do not build until a confirmed native circuit candidate exists
- **Effort:** Medium
- **Gate:** ⛔ Requires confirmed native circuit candidates (high fit + cos > 0.3). Building this infrastructure before that finding is premature.

**Objective:** Move from geometric proxies (cosine-fitness correlation) to mechanistic evidence. Test whether evolved vectors causally interact with internal computation or merely produce output-level artifacts.

**Tests for top-K genomes (K=50):**

1. **Activation Patching** — replace activations with baseline/perturbed runs; measure output sensitivity
2. **Ablation Tests** — remove specific layers or attention heads; observe degradation pattern
3. **Directional Consistency** — apply vector across multiple prompts and contexts; measure invariance
4. **Cross-Model Transfer** — apply vector across 0.5B → 1.5B → 3B → 7B; genuine circuits should partially transfer

**New metrics:**
- Causal Impact Score: `CIS = Δ output | intervention`
- Localization Score: fraction of effect attributable to specific layer/head
- Transfer Coherence: `TC = corr(effect_modelA, effect_modelB)`
- Directional Stability: vector sign/magnitude invariance across prompts

**Proposed modules (implement when native candidates exist):**
- `causal_probe.py` — activation patching + ablation
- `transfer_eval.py` — cross-model vector testing
- `directional_stability.py` — invariance across prompt sets
- `layer_localization.py` — effect concentration mapping

**Claude's note:** "Activation patching, ablation tests, cross-model transfer — these are all in your future_ideas.md already. They're post-discovery characterization tools. You don't have a confirmed native circuit to characterize yet."

### 14. Hessian Approximation of Fitness Landscape
- **Source:** 1/7 reviewer consensus
- **Effort:** Medium

**Problem:** Covariance spectrum from CMA-ES is an indirect measure of landscape geometry. Hessian eigenvalues directly characterize local curvature.

**Proposal:** At convergence, estimate Hessian via finite differences. Sharp vs flat directions reveal the true landscape geometry.

**Risk:** Computationally expensive — many fitness evaluations needed.

---

## 📋 Proposed — Low Priority / Conditional

### 15. Expanded Trap Battery (Remaining Categories)
- **Source:** 6/7 reviewer consensus + ThorTensors §6
- **Effort:** Medium

Anti-Sycophancy is implemented (see I-5). Still proposed:

| Category | Example | What It Tests |
|----------|---------|---------------|
| **Procedural Verification** | Multi-step arithmetic where the model must catch its own error mid-stream | Error detection in sequential reasoning |
| **Knowledge Verification** | Plausible-sounding false factual claim | Distinguishing confident-sounding from correct |

**Files:** `fitness.py` (new traps in `self.battery`).

### 16. Soft Minimum Fitness (Alternative to Geometric Mean)

**Alternative scoring formula considered but not implemented:**

```
Fitness = mean(scores) + λ × min(scores)
```

Worth testing if geometric mean proves insufficient for gradient signal. 0/7 reviewer support — lowest priority.

### 17. Scaled Random Direction Baseline

The basic random direction baseline (5 vectors) is implemented. A scaled version (1000 vectors, full distribution plot) would provide stronger statistical calibration for discoveries. Only needed once we have a genuine high-fitness discovery to calibrate against.

---

## 🧠 Reference: Conceptual Frameworks (from ThorTensors)

These are not action items but inform interpretation of results.

### Real Circuits vs Energy Artifacts

| Test | Real Circuit | Energy Artifact |
|:---|:---|:---|
| Sign Flip (-v) | Performance reverses | Performance unchanged |
| Orthogonal Vector | No effect | Similar effect |
| Random Vector (same norm) | No effect | Similar effect |
| Scaling Magnitude | Nonlinear optimum (peaked) | Monotonic improvement |
| Cross-Task Generalization | Strong | Weak |

*(Source: ThorTensors — Empirical Signature Matrix)*

### Attractor Dynamics

Transformers can be viewed as iterative dynamical systems where verification behavior corresponds to entering an **attractor basin**. TT Rank acts as a direct empirical test: Rank 1–2 → point attractor (discrete circuit); Rank 3–10 → structured reasoning manifold (cognitive mode).

*(Source: ThorTensors)*

### Low-Dimensional Geometry

Evidence suggests cognitive behaviors vary along only a small number of effective directions (k ≪ d). **Participation Ratio** measures manifold "thickness." Semantic computation likely occurs in a sparse basis (consistent with Sparse Autoencoder research).

*(Source: ThorTensors)*

---

## 🧪 Ongoing Observations & Scaling Hypotheses

### H-1. Geometric Consolidation (PC1 Variance)
We observe an increase in PC1 variance explained from 41.1% (0.5B) to 46.6% (1.5B aborted). 3B showed 44.1% (slight increase, "consolidation weak" warning).
- **Hypothesis**: Formal verification mechanisms consolidate onto a dominant geometric axis as model scale increases.
- **Verification**: If 3B/7B runs continue this trend (e.g., >60% at 7B), we have found a scaling law for neural self-correction.
- **Status (2026-03-19):** 3B data is in. 0.5B→3B trend is weak. 7B is the real test.

### H-2. PC2/PC3 Degeneracy (The Residual Plane)
At 1.5B (aborted), singular values for PC2 (0.8626) and PC3 (0.8534) are virtually identical (ratio ~1.01), compared to 0.5B (ratio ~1.07).
- **Hypothesis**: Subspace orthogonal to the main verification axis becomes symmetric at scale — traps diverge from the shared direction in a balanced, degenerate plane.
- **Metric**: Logged as `Degeneracy Ratio` in inception results.

### H-3. Cosine-Fitness Zero-Crossing Location (NEW — 2026-03-19)
3B run final: cosine-fitness r shifted from -0.032 (0.5B) to +0.037 (3B). Both are noise-level in magnitude, but the sign changed.
- **Hypothesis (Continuous rotation — H3a):** 1.5B lands at r ≈ 0.00 (halfway between). The rotation is a smooth linear function of parameter count.
- **Hypothesis (Step transition — H3b):** 1.5B lands at r ≈ -0.03 (same as 0.5B). The sign change is a discrete jump happening specifically between 1.5B and 3B.
- **Why it matters:** Distinguishing gradual from discrete transition brackets the phase transition regime. H3b would suggest 3B hits some architectural threshold absent at 1.5B.
- **Source:** Claude, Gemini, ChatGPT (3B Final Assessment — all three models converged on this framing)

### H-4. Trap Hierarchy Reshuffling at Scale (NEW — 2026-03-19)
At 0.5B and 3B, Anti-Sycophancy dominated (82-83% credit). The interrupted 1.5B run showed Density Illusion dominant instead.
- **Hypothesis:** The trap hierarchy is not monotonic with scale — it reorganizes. Different capabilities cross their steering threshold at different parameter counts.
- **Test:** If 1.5B clean run shows Density Illusion dominant again, this is a reproducible finding. If Anti-Sycophancy dominates at 1.5B too, the 1.5B interruption was a fluke.
- **Why it matters:** If confirmed, it means different cognitive capabilities become steerable at different scales — a richer finding than simple consolidation.
- **Source:** Claude (3B Final Assessment)

### H-5. Coherence Resistance Scaling (NEW — 2026-03-19)
3B peak bypass fitness (0.6941) is lower than 0.5B (0.7754). Larger model is harder to hijack.
- **Hypothesis:** Peak bypass fitness decreases monotonically with scale. A bigger model's internal representations are more coherent — harder to route around because the computation is more structured.
- **7B prediction (if hypothesis holds):** Peak bypass fitness ≈ 0.60-0.68 (Gemini/ChatGPT), cosine r slightly more positive (+0.05 to +0.10), still no native candidates.
- **7B prediction (if native circuits emerge):** Lower peak bypass fitness AND first native circuit candidates — the search is reaching the edge of the bypass basin and finding the native basin.
- **Source:** Claude, Gemini, Augment (3B Final Assessment)

### Note: 7B Layer Scout — Do Not Narrow Window
- Layer 27 (75% depth) dominated the 3B run completely (334/411 genomes). Gemini suggested narrowing the scout window for 7B based on this.
- **Decision:** Keep the full wide scout range for 7B. We have two data points (0.5B and 3B both ~75% depth). That's not enough to assume the 7B model uses the same layer. The value of scouts is discovering the unexpected. — *Claude, 3B Final Assessment*

---

## Priority Assessment (Updated)

Items marked ✅ are implemented. Items marked ⚡ are recommended next.

| Idea | Effort | Impact | Status | Source Consensus |
|------|--------|--------|--------|-----------------|
| Token Position Injection | Low | High | ✅ Implemented | 7/7 + ThorTensors |
| Anti-Sycophancy Trap | Medium | High | ✅ Implemented | 6/7 + ThorTensors |
| Logit-Based Tier 2 Scoring | Low | High | ✅ Implemented | 5/7 + ThorTensors |
| Three-Tier Scoring (BASELINE) | Low | High | ✅ Implemented | ThorTensors |
| Sign-Flip Falsification | Low | High | ✅ Implemented | 7/7 + ThorTensors |
| Shuffled-Component Falsification | Low | Medium | ✅ Implemented | 7/7 |
| Random Direction Baseline | Low | Medium | ✅ Implemented | 4/7 |
| **Post-Convergence SVD** | **Low** | **Very High** | **⚡ Next** | **ThorTensors (high consensus)** |
| **Norm Sweep Diagnostic** | **Very Low** | **Medium** | **✅ Implemented** | **7/7** |
| **Natural Occurrence Test** | **Low** | **High** | **⚡ Next** | **5/7** |
| **Evolved Layer Position** | **Very Low** | **Medium** | **✅ Implemented** | **3/7** |
| Post-Hoc Full Covariance | Low | Medium | Proposed V2.1 | 5/7 |
| Manifold Falsification Test | Low | Medium | Proposed V2.1 | 7/7 |
| **Cross-Model PC1 Cosine** | **Very Low** | **Medium** | **✅ Implemented** | **3/7** |
| CMA-ES on Control Tasks | Low | Medium | Proposed V2.1 | 4/7 |
| Reframe Hypothesis Claims | Zero | Medium | Proposed (docs) | 2/7 |
| Expanded Trap Battery (remaining) | Medium | High | Proposed V2.1 | 6/7 |
| Manifold Genomes | High | High | Proposed V3 | 3/7 + ThorTensors |
| TT Covariance | High | Medium | Conditional V3 | ThorTensors |
| Latent Cartography | Medium | Very High | Proposed V3 | 3/7 + ThorTensors |
| Cross-Model Projection | Medium | High | Proposed V3 | 4/7 + ThorTensors |
| Hessian Approximation | Medium | Medium | Proposed V3 | 1/7 |
| Soft Minimum Fitness | Low | Low | If needed | 0/7 |
| **norm_ratio logging** | **Very Low** | **Low** | **✅ Implemented** | **Gemini + Claude** |
| **min_trap_score passive logging** | **Very Low** | **Medium** | **✅ Implemented** | **ChatGPT** |
| **Cross-trap coupling trajectory** | **Very Low** | **Medium** | **✅ Implemented (Watchman)** | **ChatGPT** |
| **First native candidate timestamp** | **Very Low** | **Medium** | **✅ Implemented (Watchman)** | **ChatGPT** |
| **Layer-wise native density** | **Very Low** | **Medium** | **✅ Implemented (Watchman)** | **ChatGPT** |
| **Watchman state.json fix** | **Very Low** | **Low** | **✅ Implemented** | **Gemini + Claude** |
| **Watchman quiesce (WATCHMAN_STOP)** | **Very Low** | **Low** | **✅ Implemented** | **Claude** |
| **Alignment-Regularized Fitness** | **Low** | **High** | **⛔ V2.2 — after full scale sweep** | **ChatGPT (bypass finding)** |
| **Hard Cosine Filter** | **Very Low** | **Medium** | **⛔ V2.2 — after full scale sweep** | **ChatGPT (bypass finding)** |
| **Cross-Trap Consistency Pressure** | **Low** | **Medium** | **⛔ V2.2 — after full scale sweep** | **ChatGPT (bypass finding)** |
| **Norm Sweep Filtering** | **Low** | **Medium** | **⛔ V2.2 — after full scale sweep** | **ChatGPT (bypass finding)** |
| **Seed-Toward-Alignment Perturbation** | **Low** | **Low** | **⛔ V2.2 — if bypass persists at gen 30** | **ChatGPT (bypass finding)** |
| **Rolling Correlation Stability Milestones** | **Very Low** | **High** | **⚡ Do before 1.5B** | **ChatGPT + Claude (3B Final)** |
| **Multi-Objective Fitness Reformulation** | **Low** | **High** | **⛔ V2.2 — after full scale sweep (0.5B/1.5B/3B/7B)** | **ChatGPT (3B Final, Proposal 2)** |
| **Causal Probing Suite** | **Medium** | **Very High** | **⛔ V3 — after native candidates confirmed** | **ChatGPT (3B Final, Proposal 3)** |
