# Erebos v3 — Deep Research Synthesis (Batch 1: G01–G05)

**Source DRs:** `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/{01..05}_*.md`
**Agent:** deep-research-pro-preview-12-2025 (all 5 reports)
**Synthesis date:** 2026-05-27
**Scope:** Structured cross-cutting extraction over the v2 design audits for G01 INTERSECTION, G02 CONTRAST, G03 FAILURE-NEIGHBORHOOD, G04 SURVIVOR-TIGHTENING, G05 CONFOUND-SWAP.

---

## A. CROSS-CUTTING THEMES

### Theme A1 — Static syntactic heuristics are catastrophically wrong on mathematical catalogs
**Raised by:** G01, G02, G03, G04, G05 (all five)
**Summary:** Every single v1 plugin is anchored on a hardcoded, syntactic, magnitude-or-symbol-based heuristic (Boolean set-intersection in G01, uniform label-shuffle in G02, `arith_equality → arith_asymptotic` ladder in G03, `M ∈ [1.30, 1.50]` in G04, `argmax|value|` in G05). The DRs converge that in deterministic mathematical catalogs the structural geometry of the data (codimension, exchangeability, density, topology, DAG) is what gates validity, and a rigid syntactic rule will systematically misfire — false positives in dense regions, false negatives in sparse ones, in the same plugin.
**Strongest quote (G05 §3.1):**
> "The magnitude of a mathematical covariate has absolutely no correlation with its topological position in a causal Directed Acyclic Graph. … In number theory, a polynomial's trace or its discriminant might possess massive scalar values, while the actual causal driver — such as a specific symmetry group or a binary Galois property — may be represented as a 0 or 1."

### Theme A2 — Permutation/exchangeability nulls break on deterministic substrates
**Raised by:** G02, G05 (explicit); G01, G03 (implicit — both reject sample-based randomization in favor of structural alternatives)
**Summary:** The single most repeated mathematical objection is that the standard non-parametric null (uniform shuffle of labels) is *algebraically invalid* in arithmetic geometry: shuffling a Root Number produces L-functions that cannot exist; shuffling Salem labels mixes degree-incompatible polynomials; shuffling causal labels on the integer 7 is undefined. Both G02 and G05 demand replacement of exchangeability with structural probabilistic heuristics (Cohen-Lenstra, GUE/Random Matrix Theory, Topos-Causal pullbacks, Haar measure on p-adic groups).
**Strongest quote (G02 §6):**
> "If a G02 loader were to shuffle the Root Number labels across a database of elliptic curves to create a 'permutation null,' it would be creating mathematically impossible objects (e.g., an elliptic curve with a root number of +1 but an odd analytic rank). The permutation null generates a universe that violently contradicts the fundamental theorems of arithmetic. … The null space is not 'random noise'; it is algebraically invalid."

### Theme A3 — Replace single-shot pass/fail verdicts with curves / surfaces / phase diagrams
**Raised by:** G02, G03, G04 (explicit); G01 (the Mahler-shift profile is the same idea)
**Summary:** Every loader is being told to abandon binary verdicts and emit a 1D or 2D continuous shape — predicate survival curves over weakening depth (G03), threshold sweeps and joint G02×G04 phase diagrams (G02, G04), Mahler-measure distribution shifts across intersection sets (G01). The geometry of the curve (slope, hazard function, change-points, plateau width) becomes the verdict, not a single p-value. This converts each plugin from a classifier into a topology-emitter.
**Strongest quote (G03 §3.3):**
> "If $S(D_0) = 0.01$ and $S(D_1) = 0.99$ (a massive drop in survival), the predicate is highly brittle. The curve's shape tells us that the original claim was likely a numerical artifact … If the curve decays slowly — surviving ε-proximity, surviving absolute bounding, and only collapsing at Depth 4 — the curve's shape indicates a deep, structural truth."

### Theme A4 — Data-driven calibration against the local density of the catalog
**Raised by:** G02, G03, G04 (explicit); G05 (implicit — RKHS propensity in functional spaces is the same principle)
**Summary:** Every threshold, epsilon, band, and significance level in v1 is a magic number. The DRs collectively insist on local, catalog-aware calibration: G02 wants Bayes-optimal thresholds at the moderate-deviation scale $\sqrt{\log n/n}$; G03 demands ε scaled to the Dobrowolski curve $(\log\log d/\log d)^3$; G04 demands information-optimal band selection via Gaussian-process surrogates with EIG acquisition; G05 demands functional propensity in an RKHS rather than scalar matching. The shared pattern: the loader must *first measure* the local distributional/algebraic geometry of the slice it is operating on, *then* pick its decision boundary.
**Strongest quote (G03 §2.3):**
> "Define $\epsilon = k \cdot \Delta M_{median}$, where $k$ is calibrated such that the expected baseline trivial fraction is exactly 0.5 (the median). This ensures the epsilon band always captures exactly one standard deviation of local neighbor claims, regardless of whether the predicate is operating in the dense regions of large Mahler measures or the sparse frontier near Lehmer's record."

### Theme A5 — Multiple-comparison / cherry-picking discipline is missing everywhere
**Raised by:** G02 (explicit, primary), G03 (Hazard-function corrections), G04 (Synthetic Null Calibration), G01 (`max(divergence over binaries)` is the same disease)
**Summary:** Several v1 loaders implicitly take a maximum over a search space (max divergence over binaries in G02; max trivial-fraction over thresholds in G04; argmax over covariates in G05) and report it as if it were a single test. The DRs demand FDR control (Benjamini-Hochberg q-values), Westfall-Young Max-T joint nulls, conformal selective inference, and Synthetic Null Calibration. The shared insight: the *search procedure itself* is part of the null distribution and must be permuted along with the data.
**Strongest quote (G04 §4):**
> "If the natural distribution of the underlying data is heavily clustered near the tightened threshold … the tightened bound will appear to survive robustly. However, this survival is an artifact of the base rate, not an indicator of a strict causal or structural boundary. The tightening falsely promotes the claim."

### Theme A6 — Effect size and *load-bearing-ness* must be reported alongside significance
**Raised by:** G01 (codimension drop, cross-fibration nullification), G02 (Cohen's $h$, Hedges' $g$, `trivial_effect_size` kill), G03 (hazard-function magnitudes), G04 (Excess Rate vs synthetic null)
**Summary:** A statistically significant result on a million-row catalog can be mathematically trivial. The DRs converge on the requirement that v2 emit a standardized magnitude metric (arcsine-transformed proportion delta, log-odds, codimension change, hazard rate, excess rate) and *kill claims that pass significance but fail effect-size*. This is a direct anti-narrative-inflation lock-in: large-N catalogs make everything significant; only effect size separates trivial overlap from structural intersection.
**Strongest quote (G02 §4 New Kill Patterns):**
> "REJECTED: trivial_effect_size. The flag passed all statistical significance tests ($p < 10^{-5}$) because the catalog size is massive, but was killed because Cohen's $h < 0.10$ (the absolute difference in survival fraction is mathematically uninteresting)."

### Theme A7 — Plugins should compose / route to each other; v1's plugin isolation is wrong
**Raised by:** G03 (explicit routing to G13 strengthening), G04 (joint G02+G04 phase mapper), G05 (proposes new sibling G05b REVEAL-SUPPRESSOR)
**Summary:** Three of the five DRs independently propose that the v1 architecture's "each plugin emits its own verdict" model is brittle, because the right tool is sometimes a *different* tool. G03 wants pre-classification routing to G13 when the predicate is p-adic / disjunctive / measure-theoretic. G04 wants joint phase-space mapping with G02. G05 wants a new dual plugin (`G05b REVEAL-SUPPRESSOR`) to catch the inverse problem. This implies v3 needs a meta-router / plugin-graph layer above the individual plugins.
**Strongest quote (G03 §6.4):**
> "If the predicate operates over Galois conjugates, Diophantine geometries, or Berkovich spaces, immediately suspend G03 and route to G13 for p-adic/topological strengthening. … If the predicate is evaluating measure-theoretic convergence rates, route to G13 for structural model strengthening prior to evaluating the convergence inequality."

---

## B. PRIOR ART CONVERGENCE (Citations across 2+ DRs)

### B1 — Kohlenbach proof mining / uniform boundedness (Neri & Pischke 2024–2026)
- **Cited by:** G03 (§4.1, primary), G02 (implicit via "extracting bounds over finitely additive probability spaces" methodology)
- **Why convergent:** Both reports use Kohlenbach's uniform-boundedness principle as the formal-logic analog of empirical weakening/null-replacement on mathematical catalogs. arXiv 2024–2026 papers by Neri/Pischke/Oliva.

### B2 — NOTEARS continuous-DAG optimization (Zheng et al., Xu 2024, Niu et al. 2024)
- **Cited by:** G05 (§3.2, primary), G02 (§1b — Berrett et al. conditional permutation also leans on DAG conditioning), G04 (§5 EIG over GP surrogate is the same continuous-relaxation pattern)
- **Why convergent:** All three plugins need a way to discover graph structure from observational catalogs; NOTEARS is the unanimously-cited modern primitive. The matrix-exponential acyclicity constraint $h(W) = \text{tr}(e^{W \circ W}) - d = 0$ is the load-bearing equation.

### B3 — Westfall-Young Max-T permutation + Benjamini-Hochberg FDR
- **Cited by:** G02 (§1a + §3, primary), G04 (§3 Multi-Band Strategies relies on FDR-equivalent sequential testing), G01 (§4.3 Permutation Null is the single-binary case of Max-T)
- **Why convergent:** The triad of "Westfall-Young joint null + BH FDR + 2024 Rousseeuw Prize award to Benjamini and Hochberg" appears as the consensus multiple-testing solution across three plugins. Imperative for any plugin that does a sweep.

### B4 — Empirical-Bernstein / Self-Normalized concentration (Chugg et al. 2024–2025, Martinez-Taboada & Ramdas 2024, Foygel Barber 2024–2025)
- **Cited by:** G04 (§1 — primary "Strong-vs-Weak Bound Ladder"), G02 (§4c — Empirical Bernstein for confidence sequences in effect-size reporting), G05 (§5.2 — for stratum-comparison confidence intervals)
- **Why convergent:** The "exchangeable-variable Bernstein" thread is the modern replacement for naive Hoeffding bounds whenever any v2 plugin needs a tail bound on a permutation-based estimator.

### B5 — Synthetic Null Calibration / Knockoffs (Zhou 2026, DenAdel et al. 2025)
- **Cited by:** G04 (§4 — primary), G02 (§1c — stratified permutation is structurally the same trick), G05 (§5 — Stratification is mathematically isomorphic)
- **Why convergent:** All three reports recommend constructing a synthetic dataset that preserves marginals but breaks the structural link, then re-running the *exact same pipeline* on both. The "excess rate" framing recurs verbatim.

### B6 — Dixit & Kala 2025 (p-adic Weil height bounds on Lehmer)
- **Cited by:** G03 (§2.2 + §6.1 — primary, used for ε-calibration AND for strengthening case), G01 (§3.1 — codimension drop test on Mahler measure indirectly leans on the same Lehmer-region density model)
- **Why convergent:** The Lehmer / Mossinghoff / Dobrowolski / Dixit-Kala chain is the canonical concrete substrate for ANY v2 plugin claim being tested in the polynomial domain.

### B7 — Topos Causal Models / category-theoretic causality (Mahadevan 2025)
- **Cited by:** G05 (§7 — primary, used to dissolve the "intervening on integer 7" objection), G01 (§5.2 — Morphic Pullback Composer relies on the same categorical pullback machinery from sheaf theory)
- **Why convergent:** Both plugins independently land on "do-calculus = subobject classifier pullback in a topos." This is a substantial convergence and suggests v3 should adopt categorical primitives as a first-class abstraction.

### B8 — Sheaf-theoretic gluing / Causal Abstraction Networks (arXiv:2605.01879, arXiv:2509.25236)
- **Cited by:** G01 (§1.2 — primary), G05 (§2.3 — Riemann-Surface causal operators are a special case of sheaf gluing on critical-line manifolds)
- **Why convergent:** Local-to-global compatibility via sheaf restriction is the modern alternative to Boolean conjunction / scalar PSM whenever the catalog has non-trivial topology.

---

## C. NEW SUBSTRATE-CAPABILITIES THE DRs DEMAND

These are capabilities Erebos v3's architecture (as described in the v2 design audit prompts) does not currently have, but which the DRs implicitly or explicitly assume.

### C1 — A NOTEARS-style continuous DAG-discovery service
- **First raised by:** G05 (§3.2 — primary)
- **Also assumed by:** G02 (conditional permutation), G04 (EIG over GP surrogate)
- **Why v3 needs it:** Three plugins independently require knowing the causal/dependency graph of catalog covariates before they can decide what to control for, condition on, or permute within. A shared substrate-level DAG-discovery service (probably wrapping NOTEARS-MLP on continuous embeddings of discrete invariants) is load-bearing. Without it, each plugin re-invents the wheel and gets it wrong.

### C2 — A `CatalogProfile` primitive carrying local density, gap distribution, and Galois/topological stratification
- **First raised by:** G03 (§2.2–2.3 — primary, for ε calibration)
- **Also assumed by:** G02 (Bayes-optimal threshold at $\sqrt{\log n/n}$), G04 (Synthetic Null Calibration needs the marginal distribution), G01 (cross-fibration nullification needs the catalog's fiber decomposition)
- **Why v3 needs it:** The DRs converge on calibration-from-local-density. There is no current substrate object that exposes "for this slice of the catalog, here is the local density, the median gap, the stratification by degree/Galois group/conductor, and the natural scaling factor." Building this once and sharing it across plugins is mandatory.

### C3 — A `SyntheticNullEngine` that preserves covariate marginals but breaks the target link
- **First raised by:** G04 (§4 — primary, SNC)
- **Also assumed by:** G02 (stratified + conditional permutation), G05 (suppressor-variable detection via knockoffs)
- **Why v3 needs it:** Every v2 plugin needs to compare a real-data verdict against a synthetic-null verdict to detect performative results. The engine must implement at minimum: (a) knockoff features per DenAdel 2025, (b) marginal-preserving label swaps per Zhou 2026 SNC, (c) conditional shuffles per Berrett-style inverse-conditional-permutation.

### C4 — A `StructuralProbabilityNullEngine` for arithmetic-geometry domains
- **First raised by:** G02 (§6 — primary, contrarian section)
- **Also assumed by:** G05 (§2.3 Riemann-Surface Causal Operators, §7 Topos pullbacks)
- **Why v3 needs it:** When the substrate is L-functions, modular forms, class groups, BSD curves, etc., the permutation null is algebraically invalid. v3 needs a plugable arithmetic-heuristic-null backend implementing Cohen-Lenstra weighting, GUE / Haar p-adic spacing, and Yu-Wei / Eisenstein heuristics. This is a *different abstraction* than C3 — C3 is empirical/distributional; C4 is algebraic/structural.

### C5 — A `PluginRouter` (meta-orchestrator above individual plugins)
- **First raised by:** G03 (§6.4 — explicit route-to-G13 logic)
- **Also assumed by:** G04 (§6 joint G02+G04 phase mapper), G05 (§6 proposal of sibling plugin G05b)
- **Why v3 needs it:** Three plugins propose composition/routing patterns that the v1/v2 architecture cannot express. v3 needs a pre-classifier that inspects each emitted claim and decides: (a) which plugins should fire, (b) which should be suppressed (G03 wrongly applied to a p-adic claim), (c) which should fire jointly with a sibling (G02+G04 phase diagram), (d) whether a dual plugin should be triggered on null results (G05b on G05 nulls).

### C6 — A `WeakeningLadderRegistry` parameterized by domain
- **First raised by:** G03 (§5.3 — primary, per-domain ladder selection: Proof-Theoretic for Mahler, Continuous-Model-Theory for BSD, Modal-Interval for Diophantine)
- **Also assumed by:** G01 (lattice/sheaf/model-theory intersection formalisms are dual to weakening ladders)
- **Why v3 needs it:** v1/v2 hardcodes a single ladder (`arith_equality → ... → arith_asymptotic`). G03 demands a registry of three+ ladders selected by domain. v3 must expose `LadderRegistry.get(domain, predicate_kind)` returning a callable that yields the next weakened (or strengthened) predicate.

### C7 — A `SurvivalCurve` / `PhaseDiagram` emission protocol
- **First raised by:** G03 (§3 — primary, Predicate Survival Curves)
- **Also assumed by:** G02 (calibrated threshold sweeps), G04 (multi-band sweep + joint phase mapper)
- **Why v3 needs it:** v2 plugins currently emit a flat `{verdict, p_value, payload}`. The DRs demand 1D/2D emission objects with prescribed shape (depth, operation, trivial_fraction, hazard) — and downstream consumers (router, learner, dashboard) need a stable schema for them.

### C8 — Functional / categorical embedding service for discrete mathematical objects
- **First raised by:** G05 (§2.2 — RKHS for modular-form coefficient sequences; §3.3 — Geometric Transformer for continuous embedding before NOTEARS)
- **Also assumed by:** G01 (Morphic Pullback Composer), G03 (Continuous Model Theory ladder over Banach spaces)
- **Why v3 needs it:** Almost every modern method the DRs cite requires the discrete mathematical object to first be embedded in a continuous latent space (RKHS, Banach, smooth manifold). v3 needs a shared embedding service that maps `(polynomial | knot | modular_form | L-function) → continuous_latent_vector` with provenance and reversibility.

---

## D. PLUGIN-SPECIFIC HOTSPOTS

### D1 — G01 INTERSECTION COMPOSER
- **Load-bearing-wrong code:** Naive set-theoretic key intersection short-circuited to `erebos_g01_intersection_pending` with no statistical bound check on the joint distribution of the intersected set. The composer treats string-equal keys as structural intersection.
- **Demanded code-level change (G01 §4):** Replace the symbolic intersection with `run_joint_mahler_distribution_profile(P1, P2)`. The loader must:
  1. Materialize $P_{1 \cap 2}$ on the actual catalog (Mossinghoff).
  2. Compute the joint Mahler-measure distribution shift vs $P_{1 \cup 2}$.
  3. Run an $L_1$-norm-preserving random permutation null on the coefficients.
  4. Apply a 3-tier kill protocol: over-constraint ($|P_{1 \cap 2}| < 3$), trivial containment ($P_{1 \cap 2} \equiv P_i$), null-hypothesis failure ($p > 0.01$).
  All of {codimension drop test, permutation-invariant subgroup test, cross-fibration nullification} should be added as triviality detectors *upstream* of the kill protocol.

### D2 — G02 CONTRAST
- **Load-bearing-wrong code:** "Reports the strongest result" across `salem | smyth | deg_parity` after a single-step, unconditional label shuffle. This is a max-of-three test reported as if it were a single test.
- **Demanded code-level change (G02 §4):**
  1. Replace the single-shuffle null with `westfall_young_max_t_permutation` that computes $T_{max}^{(b)} = \max_m D_m^{(b)}$ across a sweep $m \in [1.1, 1.4]$ step 0.01.
  2. Push every binary's global p-value through `benjamini_hochberg_fdr` and only promote $q < 0.05$.
  3. Emit Cohen's $h$ (arcsine-transformed proportion delta) alongside p-value; kill if $h < 0.10$ even with $p < 10^{-5}$.
  4. Add three new kill patterns: `fwer_max_t_null`, `fdr_multiple_comparisons`, `trivial_effect_size`.
  5. For arithmetic-geometry substrates (L-functions, modular forms, class groups), short-circuit the permutation null entirely and call `arithmetic_heuristic_null(domain)` instead.

### D3 — G03 FAILURE-NEIGHBORHOOD
- **Load-bearing-wrong code:** Hardcoded `arith_equality → arith_strict_inequality → arith_nonstrict_inequality → arith_bounded → arith_asymptotic` ladder, single-step descent, static $\epsilon = 0.05$, fixed `trivial_fraction ≥ 0.95 → boundary_collapse` decision rule. The reported `weakening_too_strict` at trivial-fraction 0.0065 IS the symptom.
- **Demanded code-level change (G03 §5):**
  1. Replace single-step descent with `generate_survival_curve(claim, ladder, catalog, epsilon)` walking N depths and producing per-depth `{depth, operation, trivial_fraction, survival_rate}`.
  2. Compute $\epsilon$ via `compute_dynamic_epsilon(catalog, predicate_domain, target_claim)` — for Mahler this is $(\log\log d / \log d)^3$ Dobrowolski scaling × the median-gap of the local stratum.
  3. Replace the static `trivial_fraction ≥ 0.95` rule with three curve-shape rules: `Hazard $h(D_1) > 0.85 \Rightarrow$ boundary_collapse`; `S(D_3) > 0.98 \Rightarrow$ flag_substrate_error`; `S(D_1) > 0.8 \wedge h(D_4) > 0.9 \Rightarrow$ robust_asymptotic_promote`.
  4. Implement `LadderRegistry` with at minimum: Proof-Theoretic Uniformity (Mahler), Continuous Model Theory (BSD), Modal Interval (Diophantine).
  5. Add a pre-classifier that routes p-adic / disjunctive / measure-theoretic claims to G13 STRENGTHENING instead of weakening them.

### D4 — G04 SURVIVOR-TIGHTENING
- **Load-bearing-wrong code:** Hardcoded bands like `M ∈ [1.30, 1.50]` at threshold $M = 1.40$; isolated per-band verdict with no comparison against the natural base-rate density of the catalog. Performative tightening is the dominant failure mode.
- **Demanded code-level change (G04 §5):**
  1. Replace hardcoded bands with `gaussian_process_eig_band_selector(claim, B_space)` using Expected Information Gain to find the inflection point.
  2. Wrap every band evaluation in `synthetic_null_calibration(D_true, D_null)` — generate knockoff dataset with identical marginals, run the *exact same tightening pipeline*, report Excess Rate $\Delta_{survival} = S(D_{true}) - S(D_{null})$.
  3. Sweep $K$ bands via Fixed-Budget Thresholding Bandit (Successive Rejects / Track-and-Stop); emit survival vector.
  4. Add four new kill patterns: `strict_threshold_violation`, `tightening_is_performative` (SNC $\Delta \approx 0$), `band_choice_arbitrary` (variance across $K$ bands ≈ 0), `effect_only_at_specific_band` (localized resonance).
  5. Implement `g02_g04_joint_phase_mapper` that varies contrast and threshold simultaneously and emits a 2D Empirical-Bernstein-adjusted significance surface.

### D5 — G05 CONFOUND-SWAP
- **Load-bearing-wrong code:** `argmax|value|` heuristic that selects the highest-magnitude numeric covariate in the payload as the candidate confounder. PSM-style matching is wrongly contemplated; collider bias and mediator misidentification are not guarded.
- **Demanded code-level change (G05 §5):**
  1. Delete `argmax|value|`. Replace with `notears_mlp_dag_discovery(X)` on continuous-embedded covariates.
  2. Traverse the resulting CPDAG and select the minimal adjustment set $Z$ via Pearl's backdoor criterion (common ancestors of $T$ and $Y$, strictly excluding descendants/colliders).
  3. Reject PSM entirely on deterministic catalogs. Use exact categorical stratification instead — partition by discrete states of $Z_{confound}$, compute per-stratum survival fraction.
  4. Add two new kill patterns: `confound_identified_as_partial` (signal reduced but residual), `confounder_set_not_minimal` (DAG analysis reveals $X$ is a downstream proxy).
  5. Spawn sibling plugin `G05b REVEAL-SUPPRESSOR` that triggers on null findings of any plugin, runs cc-Shapley values on the NOTEARS DAG, and emits `hidden_signal_revealed` when suppression geometry is found.
  6. Frame all interventions categorically as subobject-classifier pullbacks (Topos Causal Model) rather than physical interventions, so the entire framework survives the "you can't intervene on the integer 7" objection.

---

## E. CONTRARIAN ALTERNATIVES (Substantially-different architectural paths)

### E1 — Strengthening-First, Not Weakening-First (G03 §6)
Instead of routing failed claims to a weakening ladder, Erebos should default-route to a *strengthening* ladder (the G13 plugin slot), and only fall back to weakening when strengthening fails. The justification: in three concrete substrate cases (p-adic conjugate bounds, disjunctive interval analysis, measure-theoretic σ-additivity) the v2 G03 weakening operation actively *destroys* the load-bearing structure of the claim, while strengthening (adding a localized constraint, splitting via RDD disjunctive logic, transitioning to finite-additivity Fraïssé structures) preserves the proof. The architectural implication is significant: the *Failure-Neighborhood* concept itself may be wrong-headed — failure should first be interpreted as *under-constraint*, not *over-constraint*, and weakening is a last resort.

### E2 — Phase-Space Topology as Primary Output, Verdicts as Secondary Projection (G04 §6, with G03 §3 support)
Rather than each plugin emitting a verdict (PROMOTED / KILLED / pending), Erebos v3 should emit *topological objects* — survival curves, phase diagrams, hazard fields — and treat verdicts as a *projection* taken by a downstream consumer (the learner, the router, the dashboard). The G04 contrarian section makes this explicit via the joint G02+G04 phase mapper that emits a 2D "Solid/Liquid/Gas" classification surface with a Gaussian-process-fitted Critical Boundary contour. This inverts the v1/v2 contract: instead of plugins delivering decisions, they deliver geometry. The learner-side benefit is large — gradient information replaces categorical labels, and the bypass-as-global-attractor failure mode is far harder to hit because the loss surface itself becomes the output.

### E3 — Adversarial Pessimist Composition (G01 §5.3)
Drop "intersection" / "union" / "weakening" as the composition primitives and replace them with an *adversarial game*. The Pessimist sub-agent is trained to construct explicit counterexamples that satisfy Parent 1 but maximally violate Parent 2. The "intersection" is defined dynamically as the set of constraints the Pessimist *cannot* break. This is a categorically different architecture: composition becomes a min-max game over a generator/critic pair (inspired by the Optimist/Pessimist split in TxGraffiti, arXiv:2411.09158 / arXiv:2507.17780). The implication for v3: every composition plugin (G01, G02, G04 joint, G05b) becomes a two-player game with shared substrate machinery, and the kill_patterns become game-theoretic outcomes (Pessimist found exploit; Pessimist exhausted budget; equilibrium reached at margin ε).

### E4 — Categorical / Topos-Theoretic Substrate Replaces Statistical Substrate (G05 §7, with G01 §5.2 support)
Rather than statistical inference over a database, Erebos v3 could be re-grounded in Topos Causal Models (Mahadevan 2025) where interventions are subobject-classifier pullbacks and claims are morphisms in a Grothendieck topos. The G05 contrarian section argues this is the only framework in which "intervening on the integer 7" is well-defined, and the G01 Morphic Pullback Composer arrives at the same machinery from a different direction (categorical pullbacks as the right intersection primitive). The implication for v3: instead of `claim.payload` being a JSON blob over numeric features, it becomes an object in a category with prescribed morphisms; instead of plugins running statistical tests, they apply functors. This is the most architecturally radical of the four contrarian directions and would require a substantial rebuild of the substrate's type system, but it dissolves several philosophical objections to causal inference on Platonic objects.

---

## Appendix — Quick-Reference Matrix (DR coverage by theme)

```
Theme           G01   G02   G03   G04   G05
A1 syntactic     X     X     X     X     X
A2 perm-null     X*    X     X*    X*    X
A3 curves       X*    X     X     X     X*
A4 calibration   X*    X     X     X     X*
A5 multi-comp    X     X     X*    X     X*
A6 effect-size   X     X     X     X     X*
A7 routing       -     -     X     X     X
                       (X* = implicit / via different mechanism)

Capability       First-DR   Also-assumed-by
C1 NOTEARS DAG   G05        G02, G04
C2 CatalogProf   G03        G02, G04, G01
C3 SyntheticNull G04        G02, G05
C4 StructNull    G02        G05
C5 PluginRouter  G03        G04, G05
C6 LadderReg     G03        G01
C7 SurvCurve     G03        G02, G04
C8 EmbedSvc      G05        G01, G03
```

---

## Synthesis Notes

- **Convergence quality:** Five DRs run by the same agent over five different plugins independently converged on the same seven themes and the same eight required substrate capabilities. This is unusually strong cross-document agreement and suggests the themes are properties of the *substrate* (mathematical-catalog inference) rather than artifacts of the agent or the prompt template.
- **Strongest single recommendation:** Implement C1 (NOTEARS DAG service) + C2 (CatalogProfile) + C3 (SyntheticNullEngine) as substrate primitives first; almost every other plugin-level recommendation depends on them.
- **Biggest architectural risk:** Theme A7 (routing) plus contrarian E1 (strengthening-first) imply v3 needs a meta-router *before* the individual plugin upgrades land — otherwise each plugin will route to siblings that do not yet exist or that still encode v1 heuristics.
- **Watch for narrative inflation:** The categorical / topos-theoretic framing (B7, E4) is mathematically beautiful and convergent across two DRs, but the same DRs use it primarily as a *philosophical defense* against the "intervening on integer 7" objection rather than as a load-bearing computational primitive. v3 should adopt the categorical *vocabulary* (pullback, subobject classifier) only where it produces a behavior delta, not as a coat of paint on existing statistical machinery.
