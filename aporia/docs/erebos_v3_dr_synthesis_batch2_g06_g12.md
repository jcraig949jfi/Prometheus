# Erebos v3 DR Synthesis — Batch 2 (G06, G09, G10, G11, G12)

**Date:** 2026-05-27
**Source DRs:** `erebos_v2_2026-05-27/{06_g06_null_space, 07_g09_projection_collapse, 08_g10_boundary, 09_g11_exception_miner, 10_g12_invariant_substitution}_v2_design_audit.md`
**Agent (all 5):** `deep-research-pro-preview-12-2025`

This synthesis identifies cross-cutting themes, prior-art convergence, missing substrate capabilities, plugin-specific hotspots, and contrarian architectural alternatives across the 5 v2 design audits. Each section is grounded in direct quotes and citations from the source reports.

---

## A. CROSS-CUTTING THEMES

### A1. Naive aggregate statistics are the root failure mode — replace with persistence/posterior structures
**DRs raising it:** G06, G09, G10, G11 (4 of 5)
**Summary:** Every loader that produces a single scalar (alphabetical-pick, max/mean, Pearson chi-square, random 50% Lehmer ablation) is identified as load-bearing-wrong because the scalar washes out the structure that should drive the verdict. The consistent prescription is to replace each scalar with a distribution-aware object: persistence diagrams, posterior run-length distributions, exact/Monte-Carlo p-values, or Shapley attribution mass.
**Strongest quote (G10):** *"From a statistical perspective, if the differences $\Delta x_i$ are drawn from an exponential or half-normal distribution... the expected value of the maximum grows proportionally to $\log(N)$ or $\sqrt{\log(N)}$. Consequently, the threshold $3.0$ is discretization-dependent: as the resolution of the sweep increases (larger $N$), the expected ratio naturally inflates, leading to an asymptotic certainty of false positive 'sharp boundaries.'"*

### A2. Topological Data Analysis (persistent homology / Wasserstein / bottleneck) as the lingua franca
**DRs raising it:** G06, G09 (negation), G10 (3 of 5; G09 explicitly excludes TDA as a category error for distributed-invariant claims)
**Summary:** Persistent homology recurs as the recommended replacement for ad-hoc geometric heuristics: in G06 it picks the structurally-nearest void via Wasserstein distance on persistence diagrams; in G10 it provides scale-invariant boundary detection via bottleneck distance. G09's contrarian section confirms the same vocabulary in negative form by naming topological invariants as a domain where projection-based reductions fail.
**Strongest quote (G06):** *"A structural void in the Erebos ledger corresponds to a feature in the persistent homology that has an anomalously long lifespan (high persistence) but contains zero empirical ledger entries. To select the void 'structurally nearest' to the dense region, we rely on the Wasserstein distance between persistence diagrams."*

### A3. Selection bias / sampling artifact is the dominant failure of v1 results
**DRs raising it:** G06, G09, G10, G11 (4 of 5)
**Summary:** Every plugin produces empirical findings whose strongest contrarian critique is that the result is an artifact of the search/sampling/projection envelope, not a structural fact. The prescriptions converge on a single methodological move: re-run the test on an unbiased synthetic sample (Monte Carlo uniform reciprocal polynomials for G11, multi-scale octave sweeps for G10, Wasserstein-anchored void selection for G06, causal-context aware Shapley for G09) before promoting any finding.
**Strongest quote (G11):** *"The anomaly is not that non-Salem polynomials inherently 'prefer' to be degree-minima; rather, it is that Mossinghoff's algorithm only bothers to record a non-Salem polynomial *if* it is a degree-minimum. This is the textbook definition of collider bias or algorithmic selection bias."*

### A4. Plugins must distinguish their own operation from adjacent operations (taxonomic precision)
**DRs raising it:** G09, G12 (2 of 5, but both develop the theme at length)
**Summary:** G09 spends Section 5 separating ablation (G09) from stratification (G05), arguing that conflating them produces collider-induced false discoveries. G12 spends Section 3 separating identity substitution (G12) from analogy (G07) from functor (G21), arguing that category-theoretic vocabulary is the only way to keep the three operations from collapsing into each other.
**Strongest quote (G09):** *"In short: G09 removes data to test model complexity; G05 fixes data to test causal validity."*

### A5. Closed-loop verification on the parent dataset is mandatory before emission
**DRs raising it:** G06, G09, G11, G12 (4 of 5)
**Summary:** Every loader is told to add a re-test step: G06 must run the parent's bound test against generated void objects; G09 must retrain on the ablated dataset; G11 must hold out a degree-cohort and verify the stratifier survives; G12 must inject the substituted claim back into the parent's catalog and backpropagate-penalize the similarity matrix on failure. The pattern is: never emit a verdict from the analysis stage; always close the loop against the dataset that birthed the original claim.
**Strongest quote (G12):** *"If the original claim was verified against a database of elliptic curves, the substituted claim is immediately run against that exact same database. This verifies if B truly substitutes for A inside the *same dataset*. If the test fails, the similarity matrix weights are penalized via backpropagation, allowing the functor learning model to self-correct its geometric alignments."*

### A6. Causal structure (not correlation/proximity) gates the validity of every score
**DRs raising it:** G09, G11, G12 (3 of 5)
**Summary:** Pure data-driven scores — Shapley, mutual information, similarity-matrix cosine — are flagged as actively misleading without causal-graph context. cc-Shapley (Martin & Haufe 2026), Causal Mixture Models (Mameche et al. 2025), and discrete-latent causal identifiability (Lee & Gu 2026) are the named remedies; without them, collider bias and suppressor variables route the loader to false dominance / false stratifier discoveries.
**Strongest quote (G09):** *"Without causal context, Shapley-based single-coordinate isolation can incorrectly identify a suppressor or collider as the 'dominant' explanatory coordinate."*

### A7. Cross-domain generalization is asked of every plugin, with BSD as the canonical target
**DRs raising it:** G06, G09, G11, G12 (4 of 5 — G06 §5, G11 §6, G12 throughout; G09 implicit in domain-restriction discussion)
**Summary:** Every audit treats BSD (Birch & Swinnerton-Dyer) as the next-step generalization target beyond the current Mahler-measure / Mossinghoff context. The pattern: identify analogous dense-region/void/stratifier coordinates in elliptic-curve invariants (rank, conductor, Sha, isogeny degree, root number) and port the plugin's operator to that space. Knot theory (A-polynomial, hyperbolic volume, Boyd ratios) appears as the secondary cross-domain target.
**Strongest quote (G11):** *"Prediction: Stratifier 2 (Sha p-divisibility) will yield finding-worthy heterogeneity. Because elements of the Tate-Shafarevich group represent torsors that are locally soluble everywhere but fail to have global rational points, computational solvers will consistently timeout or 'kill' these curves, making Sha ≠ 1 a perfect hidden stratifier for algorithmic failure."*

---

## B. PRIOR ART CONVERGENCE (citations / methods that appear across 2+ DRs)

### B1. Persistent homology / Wasserstein-bottleneck distance
- **DRs:** G06 (§2 Wasserstein on persistence diagrams; Turner-Mileyko Fréchet mean), G10 (§2.2 Bottleneck distance, "Computing the Bottleneck Distance between Persistent Homology Transforms" 2026)
- **Specific shared method:** $W_p$ distance between persistence diagrams with $L_\infty$ matching; both DRs cite the Stability Theorem of Persistent Homology as the reason this beats brittle scalar ratios.

### B2. Vigneaux / Baudot / Bennequin information topology
- **DRs:** G06 (§2 measure-theoretic foundations for persistence-diagram metrics; §6 cohomological obstruction for structural-void promotion), and the same conceptual framework is implied by G10's stability arguments.
- **Specific shared method:** Information-topology cohomological obstruction as the rigor bar for promoting an empirical absence to a structural claim.

### B3. Particle Swarm Optimization for discrete adversarial generation
- **DRs:** G06 (§3.3 HogVul 2025-2026 PSO-driven discrete adversarial generation)
- (Single-DR citation but flagged here because it is the named primitive for adversarial object generation across discrete mathematical spaces, which G11's Monte Carlo sampling check §7.2 implicitly demands the same of.)

### B4. cc-Shapley (Martin & Haufe 2026) and causal-context attribution
- **DRs:** G09 (§1.1, §3.1, §4.1 as the primary attribution engine), implicitly referenced by G11 (§2.1 CMM addressing the same collider-bias problem in score-based discovery)
- **Specific shared method:** Interventional modification of Shapley/score-based attribution to eradicate spurious associations from conditioning on colliders.

### B5. Causal Mixture Models (Mameche et al. 2025)
- **DRs:** G11 (§2.1 primary stratifier discovery engine; §5.3 Decision Rule 3 with GES on PAGs), G09 (§5 implicit through stratification-vs-ablation distinction relying on causal-graph knowledge)
- **Specific shared method:** Multiple independent latent mixing variables, each affecting distinct sets of observed variables, jointly inferred via score-based causal discovery (Greedy Equivalence Search).

### B6. Mossinghoff dataset / Lehmer's conjecture / Salem-polynomial reciprocity (Smyth's theorem)
- **DRs:** G06 (§1 LMFDB and Mahler-measure context), G11 (§4 palindromic ≡ Salem analysis), G12 (§5 Mahler measure substitution attack)
- **Specific shared substrate:** All three DRs ground their adversarial / artifact analysis in the Mossinghoff search envelope; G11's Smyth-theorem argument is the prior art G06 and G12 both implicitly depend on when reasoning about why the "dense region" is shaped the way it is.

### B7. LMFDB and the conductor-bounded enumeration
- **DRs:** G06 (§1, §5 BSD generalization), G11 (§6.1 BSD stratifier candidates)
- **Specific shared substrate:** Both DRs use the LMFDB's $N \leq 500,000$–$1,000,000$ conductor bound as the canonical example of a sampling-artifact-vs-structural-void distinction.

### B8. Hierarchical Concept Embedding Models (HiCEM / HCEP, 2026)
- **DRs:** G12 (§1.1, §4.1)
- (Single-DR but the *type* of object — a learned dynamic similarity tensor over invariants — is implicitly demanded by the cross-domain generalization sections of G06, G11, and G12.)

### B9. Greedy Equivalence Search (GES) / Partial Ancestral Graphs (PAGs)
- **DRs:** G11 (§2.3 Ramsey & Andrews 2025 BF-BIC/BF-LRT for PAG search; §5.3 Decision Rule 3), G09 (§3 implicit when discussing causal-graph requirements)
- **Specific shared method:** Score-based search over PAG space with conditional-independence tests, to recover causal structure including discrete latents.

### B10. Functor / category-theoretic learning (Gavranovic & Crescenzi 2024)
- **DRs:** G12 (§1.2, §3.3, §6 contrarian)
- (Single-DR by exact citation, but the *operation* — structure-preserving morphism between domains — is the operation G07/G21 distinction work in G12 generalizes, and the operation G06 §5 BSD-generalization implicitly requires.)

---

## C. NEW SUBSTRATE-CAPABILITIES THE DRs DEMAND

### C1. A persistent-homology / TDA service across the ledger
- **First raised by:** G06 (§2, §4a Topological Void Selection Module)
- **Also demanded by:** G10 (§1.1, §2.2, §4.1 WTMM + bottleneck-distance dual engine)
- **Why v3 needs it:** Both plugins replace their core selection/detection scalar with persistence-diagram operations. v3 has no shared TDA layer; each plugin would reimplement Vietoris-Rips construction, persistence-diagram extraction, Wasserstein/bottleneck distance, and Fréchet-mean computation. The Turner-Mileyko algorithms and the recently-improved $\tilde{O}(n^5)$ 3D bottleneck integration (cited in G10 §2.2 from a 2026 paper) are nontrivial to implement correctly. A shared `prometheus_math.topology` module with PH primitives is the load-bearing missing capability.

### C2. A causal-graph / latent-class inference service
- **First raised by:** G09 (§1.1 cc-Shapley, §3.1 amortized causal Shapley)
- **Also demanded by:** G11 (§2.1 CMM, §5.3 GES on PAGs), G12 (§4.2 ATP-style unifier)
- **Why v3 needs it:** Three separate plugins assume the ability to (a) accept a causal graph as input, (b) compute interventional / counterfactual queries, and (c) run GES or related score-based search to *discover* latent stratifiers when no graph is supplied. v3's loaders all currently treat data as a flat feature table. A `prometheus_math.causal` module exposing cc-Shapley, CMM mixing-variable inference, and GES/PAG search is the load-bearing missing capability.

### C3. An adversarial / OOD object-generation primitive (per substrate-domain)
- **First raised by:** G06 (§3 SOS Transformer, Salem K3 generator, HogVul PSO)
- **Also demanded by:** G11 (§7.2 Monte Carlo uniform sampling check), G12 (§4 closed-loop re-test requires synthesized objects, not just existing catalog entries)
- **Why v3 needs it:** The contrarian-defense move ("re-sample without the original algorithm's bias") requires a generator that can deposit objects into specified regions of the parameter space — including void regions, uniform reciprocal-polynomial regions, and adversarial out-of-distribution regions. v3 has no per-domain generator API. The three generator classes named in G06 (Transformer-SOS, Salem-K3, PSO-discrete) suggest a 3-implementation foundation.

### C4. Multi-scale / scale-space sweep engine
- **First raised by:** G10 (§3 multi-octave $N=\{8,16,32,64,128\}$ sweep; §4.1 zoom-in re-evaluation)
- **Also implicit in:** G06 (§4a multi-resolution void search), G11 (§2.3 PAG with nonlinear basis at multiple resolutions)
- **Why v3 needs it:** G10's `phase_transition_below_resolution` and `multi_scale_boundary_inconsistent` kill patterns are impossible without a sweep engine that operates at multiple bandwidth octaves. A `prometheus_math.scale_space` module providing CWT-skeleton extraction and Hölder-exponent estimation across $a \in \{2^1, 2^2, 2^3, 2^4\}$ is the missing capability.

### C5. An automated-theorem-proving / unifier validity gate
- **First raised by:** G12 (§2 3-criterion validity gate, §4.2 REFACTOR-style unifier ATP subroutine)
- **Also implicit in:** G06 (§6 evidence bar for `universal_rejection` requires formal logical proof of contradiction)
- **Why v3 needs it:** G12's `type_mismatch_substitution` and `substitution_changed_test_semantics` kill patterns require type-checking against a dependently-typed signature and most-general-unifier (MGU) checks. G06's structural-void promotion requires a cohomological-obstruction proof. v3 has no Lean/Coq integration, no type-signature registry for mathematical operators, and no MGU engine. A `prometheus_math.atp` integration layer (even a thin wrapper around an existing prover) is the missing capability.

### C6. A learned, dynamic similarity / functor tensor over invariants
- **First raised by:** G12 (§1, §4.1 HiCEM background daemon)
- **Why v3 needs it:** G12 v1's hardcoded similarity matrix is identified as the entire load-bearing mechanism and simultaneously as the primary failure mode. Replacing it requires a continuously-updated embedding/tensor that ranks invariant-pair substitutability by a distinction-space metric $\rho(D_A, D_B)$ and supports backpropagated penalty from failed substitutions. This is a research-scale ML system v3 does not have; the contrarian section of G12 argues this tensor *is itself* the deliverable.

### C7. An exact / Monte-Carlo permutation test engine for sparse contingency tables
- **First raised by:** G11 (§3 Freeman-Halton, Monte-Carlo G-test, Williams correction)
- **Why v3 needs it:** Every contingency test in v3 currently uses asymptotic Pearson chi-square. G11 proves this is mathematically degenerate at the 8501:2:14 cell imbalances actually present in the Mossinghoff data. A `prometheus_math.contingency` module with Patefield-algorithm random-table generation, Freeman-Halton hypergeometric exact tests, and Monte-Carlo permutation G-tests is the missing capability.

### C8. A held-out validation cohort discipline (held-out by some non-trivial axis, not iid)
- **First raised by:** G11 (§5.3 rejection criterion: "fails to predict survival in degrees > 60")
- **Also demanded by:** G06 (§4d binomial CI for survival in void), G09 (§4.1 retrain-and-evaluate on ablated dataset)
- **Why v3 needs it:** The held-out is along structural axes (degree, conductor, dimension), not random iid. v3's ergon/learner corpus splits and validation tooling do not currently expose "split by degree band" or "split by conductor band" as first-class operations. A `prometheus_math.validation` discipline that enforces structural-axis held-outs is the missing capability.

---

## D. PLUGIN-SPECIFIC HOTSPOTS (one per plugin)

### D1. G06 NULL-SPACE — alphabetical first-absentee selection is the load-bearing bug
- **Quote:** *"The current v1 architecture of the G06 NULL-SPACE plugin relies on a naive alphabetical selection for its void `kill_pattern` via the first `KP_UNIVERSE` absentee. This methodology is critically flawed because it assumes the lexicographical ordering of pattern identifiers holds geometric or structural significance in the underlying mathematical space. It does not."* (§2)
- **Code-level change demanded:** Replace the first-absentee lookup with a Wasserstein-minimization scan over candidate voids:
  1. Embed all `KP_UNIVERSE` patterns into a metric feature-vector space (§4a).
  2. Compute persistence diagrams of the dense region and surrounding empty cells.
  3. Compute Fréchet mean of dense-region persistence diagram via Turner-Mileyko.
  4. For each candidate void, compute 1-Wasserstein (or $L_\infty$ bottleneck) distance from the Fréchet mean.
  5. Select the void minimizing this distance *and* enforcing strict zero local density in the Erebos ledger.
- **New kill patterns demanded (§4d):** `universal_rejection`, `void_was_sampling_artifact`, `void_object_generator_failed`. The third pattern requires the per-domain generators (C3) actually exist.

### D2. G09 PROJECTION-COLLAPSE — random 50% Lehmer ablation is the load-bearing bug
- **Quote:** *"The current v1 loader relies on `g09_lehmer_ablation`, which utilizes a deterministic 50% random subsample of the coordinate catalog. This approach is fundamentally feature-agnostic. By randomly dropping half the features, the loader tests the model's robustness to general information loss, but it completely fails the core objective of the G09 protocol: isolating the single highest-variance coordinate."* (§2)
- **Code-level change demanded:** Replace random subsampling with Shapley-ranked single-coordinate ablation (§4.1 pseudocode):
  1. `shapley_scores = compute_cc_shapley(claim.model, dataset, causal_graph)` — use cc-Shapley if causal graph supplied, else amortized TreeSHAP / FastShap.
  2. `dominant_coord = argmax(shapley_scores)`; compute `survival_mass = |max_score| / sum(|scores|)`.
  3. If `survival_mass >= 0.95`: short-circuit to `projection_collapse`.
  4. Else: drop only `dominant_coord`, retrain, compute `residual_power = ablated_perf / original_perf`.
  5. If `residual_power < 0.05`: `projection_collapse`. Else: new kill pattern `multi_coordinate_distributed`.
- **New kill pattern demanded (§4.2d):** `multi_coordinate_distributed` (replaces generic `residual_survival`), with the explicit semantic: "Dimensionality-reduction hypothesis testing is invalid for this claim."

### D3. G10 BOUNDARY — max/mean smoothness ratio with $N$-dependence is the load-bearing bug
- **Quote:** *"The current `smoothness_ratio` (which relies on the ratio of the maximum first difference to the mean first difference) missed the M=1.26 ITER-18 phase transition. This failure likely occurred because the transition at M=1.26 was an *informational* or *topological* phase shift, rather than a massive disruption in the amplitude of the first derivative."* (§1.4)
- **Code-level change demanded:** Replace the single-scalar ratio with a dual-engine multi-scale loader (§4.1):
  1. **Primary detector (BOCPD):** sweep parameter $M$ incrementally; compute posterior $P(r_t = 0 | M_{1:t})$; flag candidate when $> 0.95$.
  2. **Robustness verifier (WTMM):** apply CWT with Gaussian-derivative wavelet at scales $a \in \{2^1, 2^2, 2^3, 2^4\}$; trace modulus-maxima lines; compute Hölder exponent at candidate; confirm cliff when $h(t) < 1.0$ persists across all scales.
  3. **Multi-scale sweep engine:** auto-zoom from $N=8$ to $N=32$ to $N=128$ when boundary is candidate-detected.
- **New kill patterns demanded (§4.1 D):** `smooth_degradation`, `sharp_boundary_detected`, `multi_scale_boundary_inconsistent`, `phase_transition_below_resolution` (this last one is specifically the M=1.26 ITER-18 case).

### D4. G11 EXCEPTION-MINER — Pearson chi-square on sparse cells + human-supplied boolean cubes is the load-bearing bug
- **Quote:** *"The g11 loaders (v1/v2/v4) currently rely on the Pearson $\chi^2$ test to evaluate the over-representation of non-Salem cells at degree minima (yielding $\chi^2 = 191$). However, the contingency tables derived from the Mossinghoff real data are pathologically imbalanced, yielding cell counts such as $8501, 2, 14$.... Given the extremity of the $8501 : 2 : 14$ split, the reported $\chi^2 = 191$ is mathematically degenerate."* (§3)
- **Code-level change demanded:** Triple replacement (§5):
  1. **Statistical engine:** Likelihood-Ratio G-test for $E_{ij} \geq 5$ cells; Monte-Carlo permutation G-test (Patefield algorithm, $B = 10{,}000$ tables) when any $E_{ij} < 5$.
  2. **Feature set:** replace boolean cubes with `(degree, mod-p splitting patterns for first 20 primes, Galois group proxy, root angular-distribution moments)`. Fit 2-class and 3-class latent-class regression with BIC selection.
  3. **Stratifier discovery:** feed enriched features + survival + latent-class assignments into GES-on-PAGs; require m-separation; reject any stratifier that fails on a held-out degree-band (`degrees > 60`) as `out_of_sample_failure` rather than promoting it.
- **Contrarian-mandated additional check (§7.2):** Run the Monte Carlo Uniform Sampling check (1M random reciprocal polynomials uniformly sampled in coefficient box) and confirm the $\chi^2 = 191$ over-representation persists; if it vanishes, the original PROMOTE is a selection-bias artifact.

### D5. G12 INVARIANT-SUBSTITUTION — hardcoded similarity matrix + missing validity gate is the load-bearing bug
- **Quote:** *"The foundational vulnerability of G12 v1 is its reliance on a manually curated, hardcoded similarity matrix. The matrix is essentially doing all the work; the plugin merely executes string-level or AST-level swaps based on human intuition."* (§1)
- **Code-level change demanded:** Three-step replacement (§4):
  1. **Replace hardcoded matrix with HiCEM daemon:** continuous background process parsing the theorem/proof library; computes distinction-space metric $\rho(D_A, D_B)$ for all invariants; substitution proposed only when $\cos(\theta) > 0.95$.
  2. **Insert 3-criterion validity gate** (§2): (a) type checker → emits `type_mismatch_substitution`; (b) REFACTOR-style unifier ATP check (Most-General-Unifier on the predicate) → emits `substitution_changed_test_semantics`; (c) target-domain test-infrastructure existence check.
  3. **Closed-loop re-test on parent catalog:** the substituted claim is run against the exact same dataset that birthed the original claim; on failure, backpropagate penalty to the similarity-matrix weights.
- **Adversarial test case to wire in (§5):** the Mahler-measure → Dirichlet-regulator substitution attack. The v2 type checker must fail this with `type_mismatch_substitution` because `Reg(K)` requires `K ∈ NumField` while `P(x) ∈ ℤ[x]`.

---

## E. CONTRARIAN ALTERNATIVES

### E1. (G06 §6) All voids are sampling artifacts — invert the default
- **Source DR:** G06
- **Summary:** The contrarian position holds that high-dimensional discrete spaces are dominated by computational bounding boxes (conductor caps, crossing-number caps, runtime timeouts) and that *every* observed void should be assumed to be a sampling artifact until a formal logical proof of contradiction is supplied. This inverts G06's current default: instead of `void_detected → universal_rejection`, the default verdict becomes `void_detected → void_was_sampling_artifact` and the burden of proof shifts to cohomological obstruction (Vigneaux-Baudot-Bennequin information topology), topological-invariance conflict (Jones-polynomial mutual-exclusivity proofs), or analytic-zero guarantee (Sato-Tate / Lefschetz-fibration evaluation). G06's `universal_rejection` kill pattern is then never emitted from empirical absence alone — only from a generator that produces a formal contradiction proof. This is an architectural inversion: the substrate becomes a "structural-void proof engine" rather than a "void enumerator."

### E2. (G09 §6) Don't project at all — entire claim classes are projection-illegal
- **Source DR:** G09
- **Summary:** The contrarian position identifies three claim-classes where applying G09 projection is a *category error* and the loader should refuse to operate: (1) conditional independence claims in causal graphs (the relation is a property of the whole joint distribution and graph topology; ablating a coordinate from the conditioning set opens back-door paths and changes the meaning of the claim, not its truth value); (2) moment-equivalence claims (Prouhet-Tarry-Escott / Mossinghoff polynomial relations require *all* coordinates simultaneously; removing one shatters the moment equivalence); (3) distributed topological invariants (Jones polynomial, BSD rank — the invariant is a holistic property of every crossing / every prime, with no "highest-variance coordinate"). This implies v3 needs a *claim-class typing system* that gates which plugins are allowed to operate on which claim types — and G09 must be the first plugin to opt-out of an entire claim-class rather than emit a verdict.

### E3. (G10 §6) Sharp boundaries don't exist in sufficient dimensions — G10's value is the projection, not the detection
- **Source DR:** G10
- **Summary:** By Whitney embedding and manifold unfolding, any apparent cliff resolves into a smooth manifold in sufficient dimensions; every observed phase transition is a caustic / fold catastrophe of a chosen low-dimensional projection. This inverts G10's framing entirely: the boundary-detection algorithm is trivial; the *substantive scientific output* is the specific 1D projection axis $M \in [M_{\text{LEHMER}}, 1.50]$ that *forces* the high-dimensional complexity to collapse into a singular human-interpretable transition. v3 should refactor G10 from "boundary detector" to "epistemic-projection finder" — and immediately, G10 currently misses (a) rotational/manifold-aligned projections (a curved-manifold transition appears as chaotic noise to a linear 1D sweep) and (b) entangled/coupled projections (transitions visible only in covariance-matrix principal components, not raw variables). The contrarian roadmap: deprecate 1D sweep, build a projection-search engine.

### E4. (G12 §6) Publish the similarity matrix; deprecate the plugin
- **Source DR:** G12
- **Summary:** If the HiCEM-learned similarity matrix is doing all the load-bearing mathematical discovery, the G12 plugin's role degrades to "automated printing press" — it iterates the matrix to produce thousands of trivial substituted lemmas that clog the reasoning engine with low-signal combinatorial spam. The contrarian position deprecates G12 entirely and treats the learned similarity tensor as a *direct research artifact*: an interactive multidimensional geometric map of mathematics where human researchers (or downstream agents) read the latent-space gravitational pulls (e.g., "Mahler Measure" being pulled toward "Dirichlet Regulator") and craft the nuanced functor manually. The lesson generalizes: when a plugin's only function is mechanical iteration over a learned representation, the representation is the deliverable and the plugin is friction. This is a direct test of `feedback_substrate_passive_consumer_warning` — the substrate becomes "beautifully producing maps no model uses" unless the matrix is wired into Apollo/Rhea/Charon as a reasoning prior.

---

## CROSS-CUTTING META-OBSERVATION

Four of the five DRs (G06, G09, G10, G11) independently identify the same architectural pattern: a v1 loader picks the *first* / *random* / *aggregate* candidate from a structured space and treats the choice as if it were geometrically meaningful. The fix in every case is the same shape: replace the arbitrary choice with a *distance-minimizing* / *posterior-maximizing* / *attribution-ranked* selection that respects the underlying geometry. This is not five independent design errors — it is one repeated design-anti-pattern that v3's loader-base-class should refuse to allow at the type-system level. The synthesis points to a `prometheus_math.selection` discipline where every "pick one from a set" operation must declare its distance/posterior/attribution metric, and the default of "first lexicographic / first iterator / uniform random" is forbidden in the v3 loader contract.
