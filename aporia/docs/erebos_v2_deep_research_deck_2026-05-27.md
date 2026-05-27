# Erebos v2 Deep-Research Deck — 22 unblocked-plugin audits

**Date:** 2026-05-27
**Purpose:** Drive a Gemini Deep Research pass over each of the 22 non-infrastructure-blocked Erebos generators. Output goes to `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/`. Each prompt asks for mathematical foundations, prior-art audit, alternative formulations, and v2 design suggestions specific to that plugin's cognitive archetype.

## Doctrine — applies to ALL 22 prompts below

Project Prometheus is a multi-agent mathematical research substrate. Doctrine constraints below CHANGE how you should answer:

1. **NO paper-publishing framing.** Findings are substrate inputs (training-corpus filters, primitive registrations, plugin v2 designs, work-queue entries). Not papers, not blog posts.
2. **Anti-gravitational-well.** Every LLM has gradient toward conventional framings (GNNs, RL, contrastive learning, LLM-augmented siblings, "ensemble methods"). Resist them. Surface alternatives explicitly.
3. **Primary-source anchored.** Cite primary sources with arXiv IDs / DOIs / journal references. Distinguish announced-not-published from peer-reviewed.
4. **Distinct coordinates (HARD-5).** Never collapse mathematically-distinct invariants into a single named field. Mahler measure ≠ Salem class ≠ palindromic ≠ degree-minimum, even though they are correlated in the Mossinghoff catalog.
5. **Date everything.** 2024-2027 work especially — give month and year of each cited result.
6. **Bet, don't hedge.** Take positions; "depends on the goal" without picking one is rejected.
7. **Distinguish failure modes.** Pass/fail is impoverished. Every recommendation must name the *shape* of the failure the recommendation would prevent or detect.

## Shared context — Erebos overview

Erebos is a 25-archetype hypothesis-generator cluster inside the Charon swarm of Prometheus. Each plugin commits to a six-field contract: input/provenance, transformation, output claim, falsification route, expected kill pattern, loader feasibility. Plugins emit `ComposedClaim` objects that go into a `kill_ledger.jsonl` and (when a `CompositionLoader` matches) get routed to a real battery for empirical verdict.

As of v0.26: 25/25 plugin REGISTRY; 22 composition loaders covering 17/25 plugins; 470 tests; 9 substrate finding docs. Mahler-spectrum domain is well-instrumented (Mossinghoff catalog n=8596). Seven triangulated phenomena include Salem-class moderation of Lehmer-bound survival, phase transition at M=1.26, and 1/log(N) decay of minimum-Mahler-by-degree.

Substrate doctrine: every reasoning act must leave behind navigable residue (the kill_ledger). Plugins without composition loaders emit unfalsifiable claims. The substrate's job is constrained-invention-with-memory, not text continuation.

---

### Prompt 1: G01 Intersection — v2 design audit

```text
You are an expert reviewer in combinatorial mathematics, set-theoretic reasoning, and automated hypothesis generation.

G01 INTERSECTION COMPOSER: takes two PROMOTED substrate rows (typically from different BL-C-* problem families) and emits the intersection claim — "the property that both PROMOTED parents satisfy is the load-bearing structure, NOT either parent in isolation." Expected kill_pattern: `intersection_is_trivial` (the intersection collapses to a tautology like 'both involve integers').

Current v1 implementation: takes two PROMOTED Stygian rows; computes intersection of (claim_payload, kill_vector) keys; emits a composed_id like `EREBOS-G01-stygian_p1_x_stygian_p2`. NO composition loader exists — G01 emissions short-circuit to `erebos_g01_intersection_pending`.

YOUR TASK — be specific and adversarial:

1. INTERSECTION MATHEMATICS. What is the right mathematical object for "the structural intersection of two empirical claims"? Survey 3 candidate formalisms (lattice-theoretic meet, sheaf-theoretic glueing, intersection of zero-loci in some moduli space, modular intersection on a stack, intersection-of-models in model theory). For each, give one published 2024-2026 result that uses it for cross-domain hypothesis generation, AND name the failure mode that formalism predicts.

2. PRIOR ART AUDIT. Who has built automated "intersection of two empirical observations" engines in the last 3 years? Specifically: in automated theorem proving, in scientific discovery (alpha-fold style structural-property miners), in combinatorial chemistry "scaffold-merging" systems. Name 3 systems, their intersection operator, and what they kill_pattern-equivalently call when intersection fails to be informative.

3. THE TRIVIALITY DETECTOR. The hardest empirical question for G01 is: when is an intersection trivial vs structural? Both 'integers' and 'cohomology degree' are valid intersections of many claim pairs. Propose 3 concrete tests that would distinguish trivial intersections from informative ones, anchored in the Mossinghoff catalog or BSD elliptic curve catalog as concrete instances.

4. v2 LOADER DESIGN. Specify the falsification route for a Mahler-context G01 emission. The loader's input is (composed_id, parent_row_1, parent_row_2). What does it compute? Be concrete: what predicate must it test on the Mossinghoff catalog, what permutation null does it use, what verdict thresholds apply?

5. CONTRARIAN ALTERNATIVE. Three plugin re-formulations Erebos is NOT currently considering. Each should be falsifiable against the next 100 Mahler-context emissions.

6. WHAT G01 WILL NEVER CATCH. Name the specific class of cross-claim structural relationship G01 (as currently framed) is BLIND to. Concrete examples preferred.

Constraints: cite 5+ primary sources from 2024-2026 with arXiv IDs. Length: long enough to be useful, short enough to be readable. Speak in failure shapes, not in success modes.
```

---

### Prompt 2: G02 Contrast — v2 design audit

```text
You are an expert reviewer in statistical comparison methods, permutation tests, and empirical falsification design.

G02 CONTRAST: takes a parent BL-C-* problem and partitions its catalog by a binary categorical flag (e.g., Salem-class vs non-Salem on Mossinghoff). Emits "the survival fraction under the parent's bound test diverges between the two partitions by more than permutation-null chance." Expected kill_pattern: `permutation_null` (the divergence is within shuffled noise).

Current v1 loaders: g02_lehmer_salem, g02_lehmer_smyth, g02_lehmer_degree_parity (three Mahler-context loaders all using the shared run_binary_split_permutation_null kernel with n_perm=1000, p95 threshold). LIVE FINDING (ITER-4): salem-vs-non-salem at threshold M_LEHMER returns REJECTED with kill_pattern=permutation_null; at threshold M=1.30 returns PROMOTED with observed_divergence=0.997 vs null_p95=0.024.

YOUR TASK:

1. PERMUTATION NULL ALTERNATIVES. The current loader uses single-step shuffle of labels. Survey 3 more powerful alternatives published 2024-2026: (a) Westfall-Young max-T permutation, (b) conditional permutation (Berrett et al.), (c) hierarchical / stratified permutation. For each, name the failure mode it would catch that the v1 simple shuffle misses.

2. THE THRESHOLD-CHOICE PROBLEM. The Salem moderation effect is invisible at M_LEHMER and dominant at M=1.30. Current design picks a SINGLE threshold per loader. Propose a principled threshold-selection methodology — citing prior art — that maximizes discriminating power. Bonus: a Bayes-optimal threshold criterion, with citation.

3. MULTIPLE-COMPARISONS DISCIPLINE. We currently run g02 with 3 different binaries (salem, smyth, deg_parity) and report the strongest result. This is a classic multiple-comparisons trap. Propose the right correction (FDR, Bonferroni, hierarchical) AND argue against the naive choice. Cite at least 2 papers from 2024-2026 on multiple-comparisons in scientific discovery.

4. v2 LOADER DESIGN. Specify g02 v2 with: (a) calibrated threshold sweep + max-T null; (b) multi-binary-aware FDR; (c) effect-size reporting beyond observed_divergence (e.g., Hedges g, Cohen h, or domain-specific equivalents). What new kill_patterns does v2 emit that v1 cannot?

5. WHEN IS A BINARY THE WRONG ABSTRACTION? G02 currently only handles BINARY splits. Propose 3 specific cases where the right test is a continuous covariate (e.g., regression-coefficient ≠ 0 instead of group-difference ≠ 0). Predict what the binary-only design would miss.

6. CONTRARIAN: A SUBSTRATE WHERE PERMUTATION NULL IS WRONG. Name a specific catalog / domain (BSD, knots, modular forms, NF) where permutation-null is the WRONG inferential framework, and propose what would replace it.

Constraints: cite 6+ primary sources from 2024-2026.
```

---

### Prompt 3: G03 Failure-Neighborhood — v2 design audit

```text
You are an expert reviewer in arithmetic comparison ladders, weakening-strengthening operations on logical predicates, and asymptotic / asymptotic-equivalent calculus.

G03 FAILURE-NEIGHBORHOOD: takes a REJECTED claim with a detectable arithmetic comparison operator (= / < / ≤ / O()) and weakens it ONE STEP DOWN the ladder (= → within ε; strict-< → non-strict-≤; bounded → asymptotically-bounded). Emits the weakened claim. Expected kill_pattern: `boundary_collapse` (weakened too permissive; trivially true).

Current v1 loader: g03_lehmer_neighborhood — measures fraction of Mossinghoff entries in epsilon-band [M_Lehmer ± 0.05]. Decision rule: trivial_fraction ≥ 0.95 → boundary_collapse; ≤ 0.02 → weakening_too_strict; else PROMOTED. LIVE FINDING: trivial_fraction = 0.0065 → REJECTED with weakening_too_strict.

YOUR TASK:

1. THE WEAKENING LADDER ITSELF. The current ladder is hardcoded: arith_equality → arith_strict_inequality → arith_nonstrict_inequality → arith_bounded → arith_asymptotic. Survey published taxonomies of "comparison-operator weakening" from logic / model theory / interval analysis. Name 3 alternative ladders and what they capture that the current one misses.

2. EPSILON-BAND CALIBRATION. Why EPSILON_BAND = 0.05? Propose a data-driven calibration: epsilon should be tied to the catalog's natural density scale (e.g., median gap between consecutive entries, or 1-sigma of M distribution). Cite a published methodology.

3. MULTI-STEP WEAKENING. Current loader walks ONE step. Propose v2 that walks N steps, builds a survival-curve over weakening-depth, and detects WHERE on the ladder the predicate becomes trivial. What does this curve's shape tell us?

4. PROOF-MINING ANALOGS. G03 echoes proof-mining techniques in formal logic. Name 2 published proof-mining systems (2024-2026, e.g., Kohlenbach school, Lean / Coq tactic libraries) that do operator-weakening for quantitative bound extraction. What does Erebos's substrate-grade version add or miss compared to those?

5. v2 LOADER DESIGN. Specify g03 v2 with: (a) data-driven epsilon; (b) multi-step weakening curve; (c) per-domain ladder selection (Mahler-context uses a different ladder than BSD-context). Concrete decision rules.

6. CONTRARIAN: WHEN IS WEAKENING THE WRONG MOVE? Propose 3 substrate cases where the right move is STRENGTHENING the predicate (G13's job), not weakening, and G03 wrongly applies. How would we route claims to the right one?

Constraints: cite 5+ primary sources 2024-2026.
```

---

### Prompt 4: G04 Survivor-Tightening — v2 design audit

```text
You are an expert reviewer in bound-tightening, parameter-band restriction, and threshold-search methodologies for empirical conjecture testing.

G04 SURVIVOR-TIGHTENING: takes a PROMOTED claim and tightens its operative threshold or parameter band. Sister to G14 Relation-Strengthening but at the threshold layer. Expected kill_pattern: `strict_threshold_violation` (the tightened bound fails on objects the original bound survives).

Current v1 loaders: g02_g04_lehmer_tightened, g02_g04_lehmer_band_high (M ∈ [1.30, 1.50] @ threshold M=1.40). LIVE FINDING: Salem-class moderation extends into band [1.30, 1.50] with observed=0.3766 > null_p95=0.1953.

YOUR TASK:

1. THE STRONG-VS-WEAK BOUND LADDER. Survey published taxonomies for "tightening a numerical bound." Examples: Cauchy → Hadamard for matrix bounds; Hoeffding → Bernstein → empirical-Bernstein for concentration. Name 3 taxonomies, cite primary sources 2024-2026.

2. INFORMATION-OPTIMAL BAND SELECTION. The current loader uses hardcoded bands [M_LEHMER, 1.30] and [1.30, 1.50]. Propose a principled "where to tighten" methodology — anchored in published work on bandit selection / experiment design / sequential testing. The methodology should rank candidate bands by EXPECTED INFORMATION GAIN about the parent claim's true tightness.

3. MULTI-BAND STRATEGIES. Current loader fires on a SINGLE band. Propose v2 with: (a) sweep of K bands; (b) per-band verdict + global meta-verdict; (c) detection of "the right band" (the band at which the survival difference is maximal). Cite the relevant statistical machinery.

4. CONTRARIAN — WHEN TIGHTENING IS PERFORMATIVE. Tightening a bound can falsely PROMOTE if the natural distribution clusters near the tightened threshold. Propose a "null-tightening" calibration: tighten using random subsets of the same SIZE and compare. Reference published synthetic-null methodologies.

5. v2 LOADER DESIGN. Concrete spec for g04 v2 with: (a) information-optimal band; (b) null-tightening calibration; (c) new kill_patterns (`tightening_is_performative`, `band_choice_arbitrary`, `effect_only_at_specific_band`).

6. CROSS-PLUGIN INTERACTION. G02 contrast and G04 tightening operate on the same underlying effect (Salem moderation) at different thresholds. Propose a JOINT g02+g04 loader that emits a phase diagram instead of single verdicts.

Constraints: cite 5+ primary sources 2024-2026.
```

---

### Prompt 5: G05 Confound-Swap — v2 design audit

```text
You are an expert reviewer in causal inference, confounder identification, propensity score matching, and stratification on mathematical objects.

G05 CONFOUND-SWAP: identifies the highest-magnitude numeric covariate in a PROMOTED claim's payload as the candidate confound; emits "the apparent signal collapses when the confound is randomized or held constant." Expected kill_pattern: `complete_signal_collapse` (parent was a shadow of the confound).

Current v1 status: PLUGIN EXISTS but NO COMPOSITION LOADER. Emissions short-circuit to `erebos_g05_confound_swap_pending`. Picks confound by argmax |value| (sorted-key MVP).

YOUR TASK:

1. CONFOUNDER IDENTIFICATION FOR MATHEMATICAL OBJECTS. Standard PSM / IPW techniques assume sample populations. Mossinghoff catalog entries are "objects" not "samples." Survey 3 published 2024-2026 methodologies for confounder adjustment on discrete mathematical catalogs (BSD curves, knots, modular forms). Name the systems, their adjustment operator, and their kill_pattern equivalent.

2. ARGMAX-|VALUE| IS A BAD HEURISTIC. The current MVP picks the highest-magnitude covariate. Why is this wrong, and what would published causal-discovery methodology recommend instead (PC algorithm, NOTEARS, conditional-independence testing)? Pick one, name its primary citation, and explain how to adapt it to math-object catalogs.

3. STRATIFICATION VS RANDOMIZATION VS PSM. Three different "control for confound" operations with different statistical guarantees. For Mossinghoff context, which would catch a Salem-class confound on Lehmer survival? Which would falsely identify Salem-class as the cause? Be specific.

4. v2 LOADER DESIGN. Specify g05 v2 with: (a) data-driven confounder identification (NOT argmax|value|); (b) stratified or PSM-adjusted re-test of parent claim; (c) per-stratum survival fractions + meta-verdict. New kill_patterns: `confound_identified_as_partial`, `confounder_set_not_minimal`.

5. THE INVERSE-CONFOUND PROBLEM. G05 currently looks for "X is a confound." Propose the dual: "Z is a SUPPRESSOR (apparent absence of signal is suppressed by Z)." Cite suppressor-variable methodology and propose plugin slot.

6. CONTRARIAN: WHEN ALL OF G05's MOVES ARE WRONG. Causal inference on mathematical objects may be category-theoretically ill-defined — there is no "intervention" on the integer 7. Engage this objection seriously and either rebuild G05 or argue why it survives.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 6: G06 Null-Space — v2 design audit

```text
You are an expert reviewer in negative-space analysis, void detection in scientific catalogs, and adversarial-region generation.

G06 NULL-SPACE: identifies a VOID region in the substrate's kill_pattern landscape (a known kill_pattern from the universe that appears ZERO times in the live Erebos ledger); emits "the relation that holds in the dense region survives in the void with probability >10%." Expected kill_pattern: `universal_rejection` (void is structurally empty, not sampling artifact).

Current v1 status: PLUGIN EXISTS, NO LOADER. Picks dense kp via modal kill_pattern; void kp via first KP_UNIVERSE absentee (alphabetical).

YOUR TASK:

1. VOID DETECTION IN SCIENTIFIC CATALOGS. Survey 2024-2026 work on "absence detection" in catalogs of discrete mathematical objects (cosmological void analysis in survey data; mathematical object enumeration gaps; "missing entries" detection in knot tables). Name 3 systems, their void-detection operator, and false-positive characterization.

2. THE ALPHABETICAL SELECTION IS A BUG. Current v1 picks the first KP_UNIVERSE entry that is absent (alphabetically). Propose a principled void-selection methodology — anchored in published distance-in-kill-space metrics or topological-distance methods. The chosen void should be "structurally nearest" to the dense region, not arbitrary.

3. VOID-OBJECT GENERATION. The hardest part: G06 needs to construct mathematical objects that LIVE IN THE VOID to test the relation. Survey published methods for adversarial / out-of-distribution math object generation: e.g., random Salem polynomial generators, BSD curve generators in low-conductor sparse regions. Name 3 published generators 2024-2026.

4. v2 LOADER DESIGN. Specify g06 v2 with: (a) topological void selection; (b) void-object generation primitive (per-domain); (c) re-running parent's bound test on generated void objects; (d) statistical machinery for "the parent survives at rate X% in the void." New kill_patterns: `void_was_sampling_artifact`, `void_object_generator_failed`.

5. CROSS-DOMAIN VOID GENERALIZATION. G06's MVP is Mahler-context only. Propose what BSD-context void detection would look like (e.g., low-rank low-conductor cells). What is the analog of "the dense region" in BSD?

6. CONTRARIAN: ALL VOIDS ARE SAMPLING ARTIFACTS. Argue (steelman) that any void in a catalog is sampling-driven, not structural. Then propose the EVIDENCE BAR a void must clear to be promoted from "sampling artifact" to "structural void."

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 7: G09 Projection-Collapse — v2 design audit

```text
You are an expert reviewer in feature ablation, projection methods, single-coordinate signal isolation, and dimensionality-reduction-based hypothesis testing.

G09 PROJECTION-COLLAPSE: takes a complex Erebos composition and isolates the SINGLE highest-variance coordinate, projecting the claim onto it. Emits ">95% of the predictive power of complex claim C is captured by single variable T." Expected kill_pattern: `residual_survival` (dropped coordinates STILL carry predictive power; complex claim is genuinely complex).

Current v1 loader: g09_lehmer_ablation — deterministic 50% subsample of Mossinghoff; compare full-vs-ablated survival fraction. LIVE: REJECTED with residual_survival (sampling doesn't change verdict).

YOUR TASK:

1. PROJECTION METHODOLOGIES. Survey 2024-2026 published methods for "isolating the dominant explanatory coordinate" in scientific claims (Shapley value attribution, integrated gradients, dimensional ablation, PCA-projection, dropout-based feature importance). Name 3, with citations, and explain when each is misleading.

2. THE 50%-ABLATION CHOICE. Current loader uses random 50% catalog subsample. This is FEATURE-AGNOSTIC ablation — it doesn't isolate any specific coordinate. Propose v2 that does feature-specific ablation: identify candidate "single dominant coordinate," DROP IT, re-test parent claim. Concrete decision rules.

3. SHAPLEY-VALUE INTEGRATION. Propose a g09 v2 that uses Shapley-value attribution on a parent's feature set to rank coordinates by their contribution to the claim's survival. Cite the relevant Shapley-attribution-in-scientific-discovery papers from 2024-2026.

4. v2 LOADER DESIGN. Concrete spec: (a) per-coordinate ablation sweep; (b) Shapley-style attribution; (c) "single dominant" detection criterion (e.g., 95% of survival mass attributed to one coordinate); (d) new kill_pattern `multi_coordinate_distributed` (no single dominant coord).

5. CROSS-PLUGIN INTERACTION. G09 vs G05 — both ablate-like operations. G09 drops a coord; G05 stratifies on a confound. Propose a precise distinction that explains when each is the right move.

6. CONTRARIAN: COMPLEX CLAIMS THAT G09 SHOULD NOT PROJECT. Some substrate claims are intrinsically multi-coordinate (e.g., conditional independence claims). For these, projection is a category error. Identify 3 such claim types in the Mossinghoff / BSD / knot context.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 8: G10 Boundary — v2 design audit

```text
You are an expert reviewer in boundary detection, heteroskedasticity diagnostics, threshold-sweep analysis, and phase-transition detection.

G10 BOUNDARY: takes a claim with strange heteroskedasticity over scale; sweeps a threshold and predicts SMOOTH degradation. Expected kill_pattern: `smooth_degradation` (boundary is gradual, not a cliff). Sister loader: `sharp_boundary_detected` when smoothness_ratio > threshold.

Current v1 loader: g10_lehmer_threshold_sweep — sweeps M ∈ [M_LEHMER, 1.50] in 8 steps; computes max(|first_diff|) / mean(|first_diff|); threshold = 3.0. LIVE FINDING (ITER-10): smoothness_ratio = 6.71; detects documented Salem cluster boundary at M=1.30. Calibration test (ITER-11): SMOOTH_THRESHOLD=3.0 sits cleanly between synthetic uniform (~1) and synthetic cliff (>>3).

YOUR TASK:

1. PHASE-TRANSITION DETECTION METHODS. Survey 2024-2026 work on detecting phase transitions in scientific catalog data (statistical physics methods like Binder cumulant, finite-size scaling; ML methods like change-point detection with Bayesian online inference). Name 3 methods, citations, and which would catch the M=1.26 ITER-18 phase transition that the current smoothness_ratio missed.

2. THE max/mean RATIO IS A WEAK STATISTIC. It's threshold-discretization-dependent and breaks on small N. Propose 3 better alternatives: (a) Bayesian change-point inference; (b) bottleneck distance from persistent homology on the survival curve; (c) wavelet-based singularity detection. For each, cite primary source 2024-2026 and predict empirical lift vs current statistic.

3. MULTI-SCALE BOUNDARY DETECTION. Current loader sweeps a SINGLE scale. Propose v2 that sweeps multiple scales (e.g., octaves of band-width) and detects scale-invariant boundaries vs scale-specific. Cite the relevant scale-space literature.

4. v2 LOADER DESIGN. Concrete spec: (a) Bayesian change-point primary detector; (b) wavelet singularity detector for robustness; (c) multi-scale sweep; (d) new kill_patterns: `multi_scale_boundary_inconsistent`, `phase_transition_below_resolution`.

5. INSTRUMENT VALIDATION VS NEW MATH. The G10 finding doc explicitly frames the result as instrument validation (detected a documented boundary). When would G10 find something the catalog does NOT document? Propose 3 concrete tests where G10's smoothness statistic could surface non-tautological structure.

6. CONTRARIAN: PHASE TRANSITIONS ARE PROJECTION ARTIFACTS. In sufficient dimensions, all "boundaries" become smooth. Argue that G10's value is the choice of PROJECTION, not the boundary detection itself. What boundary projection would G10 currently miss?

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 9: G11 Exception-Miner — v2 design audit

```text
You are an expert reviewer in survivor-bias analysis, hidden-stratifier discovery, contingency table methods, and minority-cell anomaly detection.

G11 EXCEPTION-MINER: finds the "hidden property H" that distinguishes survivors of a high-kill cohort. Expected kill_pattern: `out_of_sample_failure` (the hypothesized H doesn't predict survival on held-out objects).

Current v1 loaders: g11_mahler_boolean_cube (Salem×Smyth×degeven cube with M<1.30 survival → tautologically Salem-class); g11_v2_lehmer_degree_minima (orthogonal degree_minimum survival → chi²=191, non-Salem cells over-represented 59-77×); g11_v3_direct_min_verification (catalog flag vs independent argmin); g11_v4_palindromic_cube (palindromic-flag cube → P(salem|palindromic)=0.9999, catalog-equivalent).

LIVE FINDINGS: non-Salem cells carry degree-minima at 59-77× expected rate (PROMOTED chi²=191); palindromic ≡ Salem-class in Mossinghoff.

YOUR TASK:

1. HIDDEN-STRATIFIER DISCOVERY METHODS. Survey 2024-2026 published methods for "discover the hidden categorical that explains observed heterogeneity" — latent-class regression, finite mixture models, causal-discovery for structural-equation models. Name 3 methods, primary sources, and predict which would catch the degree-minima concentration in Mossinghoff.

2. CHI² ON SPARSE CELLS. v1/v2/v4 all use Pearson chi² with a guard for E<1 cells. Real Mossinghoff cells are extreme: 8501 vs 2 vs 14. Chi² approximation breaks down here. Propose 3 alternatives: (a) Fisher exact extension to k cells; (b) Monte Carlo permutation chi²; (c) likelihood-ratio G-test. Cite each.

3. THE PALINDROMIC ≡ SALEM EQUIVALENCE. The ITER-19 finding is a substrate-grade observation, not a theorem. Is it a Mossinghoff enumeration artifact or a deeper mathematical fact? Survey 2024-2026 work on Salem polynomial structure that could explain (or refute) the equivalence. Cite Lehmer-conjecture-related papers.

4. v2 LOADER DESIGN. Specify g11 v5: (a) likelihood-ratio G-test primary; (b) latent-class regression on a richer feature set (degree, mod-p reduction patterns, Galois group structure, root-distribution shape); (c) automatic stratifier discovery (NOT human-supplied boolean cubes). Concrete decision rules.

5. CROSS-DOMAIN STRATIFIER GENERALIZATION. Salem-class is a Mahler-context flag. What is the BSD analog? The knot analog? Propose 3 specific stratifiers per domain and predict which would yield finding-worthy heterogeneity.

6. CONTRARIAN: THE DEGREE-MINIMA FINDING IS A SELECTION-BIAS ARTIFACT. Argue (steelman) that the chi²=191 result is driven by how Mossinghoff selected degree-minima, NOT a real mathematical structure. What additional check would conclusively distinguish?

Constraints: 7+ primary sources 2024-2026.
```

---

### Prompt 10: G12 Invariant-Substitution — v2 design audit

```text
You are an expert reviewer in mathematical invariant substitution, type-class transfer, and structural mapping between mathematical domains.

G12 INVARIANT-SUBSTITUTION: takes a claim whose payload references invariant A; substitutes invariant B (where A and B share a similarity profile via the substrate's pre-computed similarity matrix). Emits "the same claim shape holds with B substituted for A." Expected kill_pattern: `invariant_swap_collapses` (B is not actually substitutable for A in this claim's domain).

Current v1 status: PLUGIN EXISTS with similarity matrix (R3, abstraction tier), NO COMPOSITION LOADER. Emissions short-circuit.

YOUR TASK:

1. THE SIMILARITY MATRIX IS DOING ALL THE WORK. v1's similarity matrix is hardcoded (degree ~ conductor; Mahler measure ~ regulator). Survey 2024-2026 published methods for AUTOMATIC similarity discovery between mathematical invariants — concept-embedding methods (KEPLER, KEPLER+, etc.), category-theoretic functor learning, type-theoretic structural similarity. Cite 3.

2. WHEN SUBSTITUTION IS VALID. The substitution validity requires: (a) types match; (b) the claim's predicate respects the substitution; (c) the test infrastructure exists in the target domain. Propose a 3-criterion validity check before G12 emits. Cite published "valid substitution detection" methods.

3. SUBSTITUTION VS ANALOGY (G07) VS FUNCTOR (G21). All three plugins move structure across invariants/domains. Define the precise mathematical distinction (G12 = identity substitution within same type; G07 = pattern-level mapping across domains; G21 = morphism-preserving functor). Cite category-theoretic foundations.

4. v2 LOADER DESIGN. Specify g12 v2 with: (a) learned similarity matrix (not hardcoded); (b) per-claim substitution validity gate; (c) substituted-claim re-test on the original parent's catalog (verifying B substitutes for A inside the same dataset). New kill_patterns: `type_mismatch_substitution`, `substitution_changed_test_semantics`.

5. SUBSTITUTION ATTACKS. Adversarial: pick a substitution G12 v1 would naively make and explain why it's mathematically invalid. Use Mahler-context invariants as concrete examples.

6. CONTRARIAN: G12 IS WORSE THAN MANUAL. If the similarity matrix is the load-bearing piece, why build a plugin? Argue the substrate should JUST publish the similarity matrix as a research artifact and skip the plugin. Engage seriously.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 11: G13 Relation-Weakening — v2 design audit

```text
You are an expert reviewer in predicate logic, weakening transformations on relational structures, and quantifier-relaxation methods.

G13 RELATION-WEAKENING: sister plugin to G03 but on LOGICAL predicates (NOT arithmetic operators). Walks predicate-strength one step DOWN (e.g., strict-equality → ≤; universal → existential; sum → bounded-sum). Expected kill_pattern: `predicate_collapses_to_trivial`.

Current v1 status: PLUGIN EXISTS, uses shared _predicate_lattice with G14, NO COMPOSITION LOADER.

YOUR TASK:

1. PREDICATE-LATTICE LITERATURE. Survey 2024-2026 published predicate-lattice frameworks (cylindrical algebraic decomposition for real-closed fields; abstract interpretation lattices; modal-logic strength orderings). Name 3, with citations, that map onto G13's "one step weaker" notion.

2. SEMANTIC VS SYNTACTIC WEAKENING. The current implementation is syntactic (regex on the claim text). Semantic weakening is harder. Propose 3 semantic-weakening methodologies — model-checking-based, abstract-interpretation-based, theorem-proving-tactic-based. Cite primary sources.

3. THE WEAKENING-TARGETS PROBLEM. Some predicates are "natural to weaken" (strict-< → ≤). Others are not (e.g., palindromic predicate has no obvious weakening). Propose taxonomy of "weakening-natural" vs "weakening-resistant" predicates.

4. v2 LOADER DESIGN. Specify g13 v2 with: (a) semantic weakening via SMT solver (e.g., Z3) given a formal predicate; (b) Mahler-context loader: take Lehmer's bound, weaken predicate, re-test on Mossinghoff; (c) new kill_patterns: `predicate_unrelaxable`, `weakened_form_trivial_on_target`.

5. INTERACTION WITH PROOF MINING. Kohlenbach-school proof mining produces quantitative versions of qualitative theorems by relaxing universal quantifiers to bounded ones. G13's weakening ladder echoes this. Propose direct interaction: when G13 produces a weakening, route it through proof-mining tactics to compute quantitative bounds.

6. CONTRARIAN: WEAKENING IS USUALLY USELESS. Argue (steelman) that "weakened claim survives" is rarely substrate-grade because the weakened claim usually has degenerate truth values. Propose threshold criteria for "informative weakening."

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 12: G14 Relation-Strengthening — v2 design audit

```text
You are an expert reviewer in predicate-strengthening, conjecture-tightening methodologies, and "stronger statement" discovery in mathematical research.

G14 RELATION-STRENGTHENING: sister to G13 (walks predicates UP the strength ladder). Expected kill_pattern: `strengthening_breaks` (the strengthened form fails empirically). R8 tier (representation shift).

Current v1 status: PLUGIN EXISTS, NO LOADER.

YOUR TASK:

1. STRENGTHENING IS HARDER THAN WEAKENING. Strengthening can produce mathematically meaningless statements (e.g., "all primes are 2" is a "stronger" form of "some primes are 2" but false). Survey published "safe strengthening" methodologies that guarantee the stronger form is at least well-typed.

2. THE INVERSE-OF-G13 SHORTCUT. G14 could naively be implemented as inverse-of-G13. Argue that this is wrong: strengthening has different failure modes than weakening (specifically, fragility to outliers). Cite the relevant statistical-robustness literature.

3. CONJECTURE-LIFTING IN PUBLISHED MATHEMATICS. Survey 2024-2026 published work where strengthening an existing conjecture yielded a finding (e.g., "Lehmer's conjecture implies X strictly bounded by Y, not just Y±ε"). Name 3 such conjecture-strengthenings, their author, and what the strengthening tested.

4. v2 LOADER DESIGN. Specify g14 v2 with: (a) safe-strengthening type guard; (b) Mahler-context loader: take a PROMOTED bound, strengthen by ε, re-test; (c) new kill_patterns: `strengthening_fails_at_extremes`, `strengthening_holds_only_on_subset`.

5. STRENGTHENING-AS-REGION-DETECTION. G14's "strengthening fails on extremes" is implicitly identifying the extremal region where the parent claim is tight. This connects to G16 anti-anchor + G18 minimal-counterexample. Propose explicit G14-G16-G18 cross-plugin loop.

6. CONTRARIAN: G14 PRODUCES MATHEMATICAL JUNK. Strengthened claims that empirically survive are EITHER (a) genuinely true stronger statements, or (b) the parent claim was understated. Distinguish operationally. When G14 produces (b), the right move is to UPGRADE THE PARENT, not promote a new G14 claim.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 13: G15 Cross-Generator MI — v2 design audit

```text
You are an expert reviewer in mutual-information estimation, cross-detector correlation analysis, and meta-analysis of multi-source experimental data.

G15 CROSS-GEN MI: computes Shannon MI(plugin_id; kill_pattern) over the union of substrate kill_ledgers. Expected kill_pattern: `uncorrelated_residual_failures` (failures are plugin-independent; MI ≤ threshold). R5 (causal + R6 self-correction).

Current v1 + v2 loaders: g15_ledger_mi (raw), g15_v2_real_verdict_mi (control-flow filter). LIVE FINDING (ITER-13): v1 MI=1.41 nats inflated by 73.8% control-flow rows; v2 MI=0.16 (residual = Pollux's 3 normalization patterns).

YOUR TASK:

1. MI ESTIMATION ON SMALL SPARSE JOINT DISTRIBUTIONS. v1/v2 use plug-in Shannon estimator on (plugin × kill_pattern) cells. With 13 plugins × 21 kill_patterns and 420 obs, this is sparse and biased. Survey 2024-2026 corrected estimators (Miller-Madow, jackknife, KSG for continuous variables; Bayesian MI with Dirichlet priors). Recommend the right one with primary citation.

2. CONDITIONAL MI FOR CONFOUND CONTROL. The v2 filter removes control-flow rows but doesn't condition on parent-problem-id. Propose v3 that computes conditional MI MI(plugin; kill_pattern | parent_problem) — testing whether the plugin-pattern coupling persists AFTER controlling for which BL-C-* the claim came from.

3. CROSS-INSTRUMENT TRIANGULATION AS MI-EQUIVALENT. The substrate's 4-instrument Salem moderation triangulation is structurally what G15 should be DETECTING. Propose a refinement that automatically identifies "claims observed by ≥3 distinct plugins" as substrate-grade strong (per-plugin MI is fine; cross-plugin MI on the same claim is the substrate signal).

4. v2 LOADER DESIGN. Concrete spec for g15 v3: (a) Bayesian Dirichlet-prior Shannon MI; (b) conditional MI on parent_problem; (c) cross-plugin claim-counting; (d) new kill_pattern `triangulated_artifact` (multiple plugins agree but on a wrong claim).

5. THE CONTROL-FLOW FILTER IS PER-VERSION-FRAGILE. Hard-coded suffix list will rot as kill_patterns evolve. Propose a learned classifier for "is this kill_pattern bookkeeping?" using the kill_ledger itself as training data.

6. CONTRARIAN: MI IS THE WRONG STATISTIC. Argue (steelman) that MI over a small discrete joint is misleading and a SIMPLER statistic (e.g., chi-squared on the joint table) would be more interpretable. Engage seriously.

Constraints: 7+ primary sources 2024-2026.
```

---

### Prompt 14: G16 Anti-Anchor — v2 design audit

```text
You are an expert reviewer in adversarial example generation, anti-anchor / anti-canonical-example methodologies, and adversarial-band restriction tests.

G16 ANTI-ANCHOR: pushes a PROMOTED anchor's numeric parameter to an adversarial extreme (10× or 0.1×); restricts catalog to band around extreme; re-runs survival. Expected kill_pattern: `conjecture_survives_adversarial_attack` (the "break here" hypothesis fails — anchor validated). R5 + R8.

Current v1 loader: g16_lehmer_extremum. Refined ITER-19 with permutation null over band (500 catalog subsamples). LIVE: at adversarial_M=1.20, anchor survives in band; structurally_different from random subsamples = True.

YOUR TASK:

1. ADVERSARIAL-EXAMPLE GENERATION FOR MATHEMATICAL OBJECTS. Survey 2024-2026 work on generating adversarial inputs to mathematical conjectures (Salem polynomial generators that push parameters to extremes; BSD curve generators that explore sparse low-conductor cells). Name 3 systems, their adversarial generation method, primary citations.

2. THE 10× MULTIPLIER IS NAIVE. Why is 10× the right adversarial push? Propose data-driven adversarial-distance metrics: tail-percentile-based (push to 99th percentile of catalog distribution); structurally-equivalent-class-based (move to next degenerate class). Cite.

3. PERMUTATION-NULL OVER ADVERSARIAL BAND. The ITER-19 refinement adds a null over catalog subsamples of the SAME SIZE. Propose v2 that uses null over catalog subsamples STRATIFIED ON CONFOUNDS (e.g., subsample with same degree distribution). What does this gain?

4. v2 LOADER DESIGN. Concrete spec: (a) percentile-based adversarial value selection; (b) confound-stratified permutation null; (c) per-adversarial-direction (HIGH and LOW separately, with directional decision rules); (d) new kill_pattern `adversarial_band_empty_or_artifact`.

5. ADVERSARIAL-ATTACK SUITE INTEGRATION. Erebos sister agent Lethe handles cold-call LLM anti-anchor candidates. Propose explicit Lethe→G16 hand-off protocol where Lethe-flagged-but-not-yet-tested anchors get G16 numeric-extremum tests automatically.

6. CONTRARIAN: ADVERSARIAL TESTS PROVE THE WRONG THING. Argue (steelman) that "anchor survives 10× adversarial push" is weak evidence — the adversarial push may have left a structurally-similar regime. Identify 3 cases where a more sophisticated adversarial generator is needed.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 15: G17 Causal-Intervention — v2 design audit

```text
You are an expert reviewer in causal inference at Pearl's Rung 2 (intervention), label-shuffle null tests, and intervention-based correlation severance.

G17 CAUSAL-INTERVENTION: Pearl Rung 2 — applies a label-shuffle intervention to test whether a parent correlation survives the intervention. Expected kill_pattern: `correlation_survives_intervention` (intervention failed to sever; underlying correlation is structural).

Current v1 loader: g17_lehmer_label_shuffle at threshold M=1.30. ITER-18 refinement: multi-threshold sweep [1.20, 1.40] detecting phase transition at M=1.26. LIVE: independently reproduces ITER-4 Salem moderation finding (observed=0.997 vs null_p95=0.024).

YOUR TASK:

1. LABEL-SHUFFLE IS A WEAK INTERVENTION. Pearl's Rung 2 includes do-operator interventions that are stronger than label shuffles (e.g., counterfactual outcome prediction). Survey 2024-2026 published Pearl Rung 2 methodologies applicable to mathematical-catalog substrates. Name 3, citations.

2. THE MULTI-THRESHOLD SWEEP REVEALED A PHASE TRANSITION. The ITER-18 finding M=1.26 is a substrate-grade observation. Survey published methods for "automatic phase-transition detection in intervention curves" (e.g., causal-effect surface methods, bivariate change-point detection). Cite.

3. CROSS-PLUGIN INTERVENTION CHAINS. G17 currently does single-step intervention. Propose G17 v2 that chains interventions: intervene on A; re-test; if survives, intervene on B GIVEN A intervened; re-test. Cite causal-chain-discovery methodology.

4. v2 LOADER DESIGN. Concrete spec: (a) do-operator intervention beyond label shuffle (e.g., dropout-the-Salem-class-flag-from-the-prediction-pipeline); (b) automatic phase-transition detection in sweep; (c) cross-domain intervention transfer (BSD-context label-shuffle on rank-class binary); (d) new kill_pattern `intervention_chain_collapses_at_step_N`.

5. THE M=1.26 FINDING'S ROBUSTNESS. ITER-18 used 200 perms per sweep point (lower than canonical 1000). Propose a robustness check: refit at 0.005 resolution around M=1.26 with 1000 perms; what null hypothesis about the phase transition would the refit test?

6. CONTRARIAN: G17 ONLY VALIDATES KNOWN STRUCTURE. The Salem moderation effect was already known before G17 ran. Argue (steelman) that G17 is INSTRUMENT VALIDATION, not novel discovery. Then propose 3 tests where G17 would find novel structure.

Constraints: 7+ primary sources 2024-2026.
```

---

### Prompt 16: G18 Minimal-Counterexample — v2 design audit

```text
You are an expert reviewer in counterexample search, gradient-field methods for conjecture refutation, and region-restricted enumeration over mathematical catalogs.

G18 MINIMAL-COUNTEREXAMPLE: predicts where the minimal counterexample to an unverified conjecture lives (REGION R = modal kill_pattern in kill_ledger). Expected kill_pattern: `region_R_exhausted_without_counterexample` (prediction wrong; region had no counterexample).

Current v1 loader: g18_lehmer_degree_band — searches Mossinghoff degree-band [10, 36] for entries with M < M_LEHMER. ITER-10 substrate self-correction caught Lehmer × Φ_16 false-positive (2-ULP precision). Fixed with M_COMPARISON_EPSILON=1e-9.

YOUR TASK:

1. COUNTEREXAMPLE SEARCH METHODOLOGIES. Survey 2024-2026 published methods for "search for the minimal counterexample to a conjecture in a discrete mathematical catalog" — SMT-solver enumeration, parametrized search with gradient hints, neural-guided proof-counterexample synthesis. Name 3 systems, citations.

2. THE EPSILON FIX IS A BAND-AID. M_COMPARISON_EPSILON=1e-9 prevents ULP false-positives but doesn't address the underlying issue: cyclotomic extensions HAVE the same Mahler measure as their factors, so they are NOT counterexamples even at higher precision. Propose v2 that filters cyclotomic-extension cases STRUCTURALLY (factorization-aware lookup), not numerically.

3. GRADIENT-FIELD REGION PREDICTION. v1 picks the modal kill_pattern as predicted region. This is a crude heuristic. Propose v2 using: (a) per-degree minimum-Mahler trajectory; (b) kill-density Voronoi cells over (degree, M) space; (c) actual gradient computation on kill_pattern frequency surfaces. Cite primary sources.

4. v2 LOADER DESIGN. Concrete spec: (a) factorization-aware exclusion of cyclotomic extensions; (b) Voronoi-cell-based region prediction; (c) cross-degree-band sweep; (d) new kill_patterns: `prediction_was_in_excluded_cyclotomic_band`, `region_too_sparse_for_test`.

5. WHEN G18 SUCCEEDS IS A SUBSTRATE EVENT. G18 SUCCEEDING (finding a counterexample) would be a substrate-grade discovery (e.g., Lehmer's conjecture refuted). Propose the substrate's POST-SUCCESS protocol: how to triage, verify, externally audit.

6. CONTRARIAN: G18 IS BIASED TOWARD KNOWN-OPEN CONJECTURES. G18 only fires on UNVERIFIED claims with a kill_pattern density. Strong open conjectures (Lehmer, BSD) have rich kill-density landscapes; obscure conjectures don't. Argue (steelman) that G18 is structurally limited to famous conjectures and propose an enhancement that opens it to obscure ones.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 17: G19 Proof-Obligation — v2 design audit

```text
You are an expert reviewer in formal proof-obligation extraction, transitive dependency reasoning, and Lean/Coq/Isabelle proof-assistant integration.

G19 PROOF-OBLIGATION: decomposes a macro claim into the conjunction over its parent obligations (C true iff C_1 ∧ C_2 ∧ ...). Expected kill_pattern: `sub_claim_falsified` (any parent REJECTED ⇒ macro REJECTED).

Current v1 + v2 loaders: g19_ledger_transitivity (direct parents); g19_v2_recursive_obligations (BFS to leaves with cycle detection, depth cap 10).

YOUR TASK:

1. PROOF-OBLIGATION EXTRACTION IN MODERN PROOF ASSISTANTS. Survey 2024-2026 work on automatic proof-obligation extraction in Lean 4 / Coq / Isabelle (e.g., LeanInfer, ProofNet+, COPRA). Name 3 systems, their extraction operator, primary citations.

2. THE LEDGER-TRANSITIVITY APPROXIMATION IS WEAK. v1 + v2 use latest-verdict-in-ledger as the obligation truth. This is NOT a formal proof — it's empirical correlation. Propose v3 that integrates with Lean 4 for FORMAL obligation graphs: extract proof-tree dependencies, route each obligation through Lean tactics, fail if any cannot be discharged.

3. CYCLE DETECTION + DEPTH CAP ARE BAND-AIDS. v2's MAX_RECURSION_DEPTH=10 is arbitrary. Propose: (a) depth limit derived from the obligation graph's natural diameter; (b) cycle classification (legitimate self-reference vs pathological); (c) approximate cycle resolution (e.g., least-fixed-point computation).

4. v2 LOADER DESIGN. Concrete spec for g19 v3: (a) Lean 4 integration for formal obligation extraction; (b) graph-natural depth limits; (c) cycle classification + fixed-point resolution; (d) new kill_patterns: `obligation_unsatisfiable_in_lean`, `cycle_unresolvable`.

5. PROOF-MINING INTEGRATION. Kohlenbach proof mining extracts quantitative bounds from qualitative proofs. G19's obligation graph + proof-mining tactics = a quantitative substrate finding generator. Propose integration.

6. CONTRARIAN: G19 RE-IMPLEMENTS LEAN TACTICS POORLY. Argue (steelman) that G19's value is exactly the Lean integration, and without it G19 is a worse version of what Lean tactics already do.

Constraints: 7+ primary sources 2024-2026.
```

---

### Prompt 18: G20 Instrument-Disagreement — v2 design audit

```text
You are an expert reviewer in instrument-disagreement diagnostics, LLM cold-call vs deterministic battery comparison, and meta-epistemic substrate findings.

G20 INSTRUMENT-DISAGREEMENT: detects clashes between Lethe (LLM cold-call) verdicts and Stygian (code battery) verdicts on same-topic conjectures. Expected kill_pattern: `instrument_clash_detected`. **Vacuous-until-Lethe-v2** — current Lethe doesn't emit false-form-fired candidates against modern cascades.

Current v1 status: PLUGIN EXISTS, NO LOADER, NO LIVE EMISSIONS.

YOUR TASK:

1. INSTRUMENT-DISAGREEMENT METHODOLOGIES IN ML/SCIENCE. Survey 2024-2026 work on automated detection of disagreement between two scientific instruments (e.g., ensemble-disagreement uncertainty, predictive-distribution-overlap metrics). Name 3, citations.

2. THE VACUOUS-UNTIL-LETHE-V2 PROBLEM. G20 cannot fire until Lethe is upgraded. Propose: (a) a synthetic test bed using small-LLM cold-calls (e.g., gpt-4o-mini vs Mossinghoff battery); (b) a deliberately-corrupted-Stygian instrument to seed instrument disagreement for G20 to detect; (c) a different "disagreement" plugin that uses Pollux-vs-Stygian or Erebos-vs-Hecate as the two instruments.

3. CONCEPT-K EXTRACTION. v1 extracts shared topic-tokens (>= 6 chars) and picks alphabetically-first as "Concept K." This is naive. Propose: BERT-style semantic similarity for true topic alignment; tf-idf weighting; named-entity recognition for mathematical concepts. Cite primary sources.

4. v2 LOADER DESIGN. Concrete spec for g20 v2: (a) synthetic instrument-disagreement seeding (Pollux vs Stygian as MVP); (b) semantic Concept K extraction; (c) ablation-test loader (re-prompt LLM without Concept K, observe verdict shift); (d) new kill_patterns: `concept_K_extraction_failed`, `instrument_disagreement_explained_by_context`.

5. META-EPISTEMIC FINDING FRAMING. G20's outputs are claims about the AI's epistemics, not about math. Propose how the substrate should consume them: separate ledger? Routed to Aporia self-audit? Triaged by frontier reviewers?

6. CONTRARIAN: G20 IS A DISTRACTION. Argue (steelman) that meta-epistemic claims about LLM hallucinations are scientifically uninteresting compared to substrate-grade math claims, and G20 should be deprecated. Engage seriously.

Constraints: 5+ primary sources 2024-2026.
```

---

### Prompt 19: G22 Subgraph / Clique — v2 design audit

```text
You are an expert reviewer in graph clustering, clique detection, Louvain community detection, and master-property extraction from dense clusters of empirical claims.

G22 SUBGRAPH/CLIQUE: takes a dense cluster of PROMOTED claims with high Jaccard overlap in their datasets; intersects the logical predicates of the entire clique; emits "the clique is generated entirely by master property M." Expected kill_pattern: `counterexample_breaks_master_unification`.

Current v1 status: PLUGIN EXISTS (hand-rolled Louvain over kill_ledger), NO COMPOSITION LOADER.

YOUR TASK:

1. CLIQUE DETECTION ON CLAIM GRAPHS. Survey 2024-2026 published methods for clique / community detection on graphs of empirical claims (knowledge-graph clique mining, taxonomy-induction from claim co-occurrence, hierarchical Louvain variants). Name 3 systems, citations.

2. THE HAND-ROLLED LOUVAIN IS LIMITED. v1 uses a naive intersection. Modern Louvain has known issues (resolution-limit problem, degeneracy of solutions). Propose v2 using Leiden algorithm (Traag et al.) or stochastic block models. Cite.

3. MASTER PROPERTY EXTRACTION. Once a clique is detected, extracting the master property is essentially common-subexpression-finding on the claim predicates. Survey 2024-2026 work on this in: (a) program synthesis literature; (b) theorem-prover lemma discovery; (c) database query-pattern mining.

4. v2 LOADER DESIGN. Concrete spec for g22 v2: (a) Leiden community detection; (b) master-property extraction via shared-predicate mining; (c) counterexample search FOR the master property (find object satisfying M but violating a clique member); (d) new kill_patterns: `master_property_too_specific`, `clique_was_resolution_artifact`.

5. INTEGRATION WITH G18 + G06. G22 finds master properties; G18 finds counterexamples; G06 finds voids. Propose the joint loop: G22 produces M → G18 searches for counterexamples to M → G06 finds voids in M's domain. What's the substrate-grade end product?

6. CONTRARIAN: CLIQUES ARE OVER-CLUSTERED. The substrate's kill_ledger is too small to support reliable clique detection (420 paired obs at ITER-13). Argue (steelman) that G22 needs 10× more data before it can find non-tautological cliques.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 20: G23 Asymptotic Limit — v2 design audit

```text
You are an expert reviewer in asymptotic analysis, decay-law fitting (1/N, log, exp), and per-degree (or per-conductor) error-scaling diagnostics for mathematical catalogs.

G23 ASYMPTOTIC LIMIT: hypothesizes O(1/N) decay where N is object complexity (degree, conductor). Expected kill_pattern: `error_term_does_not_decay` (no 1/N decay observed).

Current v1 loader: g23_lehmer_degree_decay — log-log fit of (M_min(N) - M_LEHMER) vs N. ITER-17 refinement: multi-law fit comparing {1/N, 1/log(N), 1/sqrt(N), exp(-N/10)} with best-fit selection by R². LIVE FINDING: 1/log(N) is best-fit law with R²=0.54.

YOUR TASK:

1. THE 1/log(N) FINDING — IS IT NOVEL? Survey 2024-2026 work on the asymptotic decay rate of "smallest known Mahler measure at degree N" or related quantities (Smyth's bound asymptotics; Schinzel-Zassenhaus bounds; recent computational catalogs of Mossinghoff successors). Has anyone reported 1/log(N) as the empirical decay law? Distinguish announced vs peer-reviewed.

2. THE LOG-LOG FIT MASKS STRUCTURE. ITER-17 reports slope=-0.21 R²=0.25 for log-log of (M_min - M_LEHMER) vs degree. This is a poor fit. Survey 2024-2026 work on broken power-law detection, kink-point regression, and non-stationary decay-law identification.

3. ALTERNATIVE COMPLEXITY MEASURES. v1 uses polynomial DEGREE as complexity N. Survey alternatives: (a) coefficient height (max |coefficient|); (b) sum-of-coefficient-magnitudes; (c) effective degree (degree minus cyclotomic factor contributions); (d) Mahler-of-derivative. Cite primary sources for each.

4. v2 LOADER DESIGN. Concrete spec for g23 v2: (a) broken power-law detector; (b) multi-complexity-measure sweep; (c) bootstrap confidence intervals on best-fit law parameters; (d) new kill_patterns: `decay_law_changes_at_complexity_K`, `complexity_measure_dependent_finding`.

5. CONNECTION TO LEHMER'S CONJECTURE. The 1/log(N) decay is what Lehmer's conjecture WOULD predict if M_Lehmer is truly the infimum: the minimum-Mahler-at-degree-N curve converges sub-polynomially to the floor. Cite the canonical Lehmer-conjecture literature on expected asymptotic behavior. Has the literature directly tested 1/log(N) vs 1/sqrt(N)?

6. CONTRARIAN: THE BEST-FIT LAW IS SAMPLING-DRIVEN. Argue (steelman) that 1/log(N)'s R²=0.54 advantage over 1/N's R²=0.51 is statistical noise, not a real decay law difference. Propose the bootstrap procedure that would resolve this with substrate-grade confidence.

Constraints: 7+ primary sources 2024-2026, with at least 2 specifically on Lehmer-conjecture-asymptotic-bounds literature.
```

---

### Prompt 21: G24 Symmetry / Twist — v2 design audit

```text
You are an expert reviewer in mathematical symmetry-preserving transformations, polynomial symmetry audits, SageMath / PARI implementation correctness, and catalog-data consistency verification.

G24 SYMMETRY/TWIST: applies known symmetry transformations (x → -x sign flip; x → 1/x reciprocal) to catalog entries and verifies the invariant (Mahler measure) is preserved. Expected kill_pattern: `symmetry_breaking` (catalog or compute pipeline bug if any entry's twisted Mahler differs).

Current v1 + v2 loaders: g24_lehmer_x_flip (200/200 pass); g24_v2_reciprocal_audit (200/200 pass; 89 informative non-palindromic + 111 trivial palindromic).

YOUR TASK:

1. COMPLETE SYMMETRY-AUDIT SUITE. G24 currently covers 2 symmetries (sign-flip + reciprocal). Survey 2024-2026 published mathematical-symmetry-audit suites — what complete set of monic-integer-polynomial symmetries preserves Mahler measure? Beyond x → -x and x → 1/x, what about: (a) Galois conjugation; (b) cyclotomic-factor extraction; (c) shift x → x + a for integer a (this CHANGES M); (d) scaling x → cx for rational c. Name 5 symmetries, classify each as Mahler-preserving / breaking.

2. CATALOG-CONSISTENCY AUDITS BEYOND MAHLER. Mossinghoff catalog contains other fields (salem_class, is_smyth_extremal, lehmer_witness, degree_minimum). G24 only audits Mahler measure. Propose v2 that audits each catalog field under each Mahler-preserving symmetry. New kill_patterns per field.

3. THE TOLERANCE=1e-6 IS TIGHTER THAN STORED PRECISION. Mossinghoff stores Mahler measures at ~14 significant digits. Audit at 1e-6 is wasteful — most legitimate variation will be at lower digits. Propose calibration: tolerance should be tied to per-entry computational precision (e.g., reported error bars from PARI).

4. v2 LOADER DESIGN. Concrete spec for g24 v3: (a) full Mahler-preserving symmetry suite; (b) per-symmetry audit of ALL catalog fields; (c) calibrated tolerance; (d) Galois-orbit closure check; (e) new kill_patterns: `field_not_invariant_under_symmetry_X`, `precision_limit_reached`.

5. INSTRUMENT VALIDATION VS DISCOVERY. G24 v1/v2 results (200/200 pass) are pure instrument validation, not discovery. Propose 3 G24 tests that would surface NEW mathematics (e.g., a symmetry that is conjectured-but-not-proven Mahler-preserving — would PROMOTING G24 on that symmetry constitute substrate-grade evidence?).

6. CONTRARIAN: G24 IS REDUNDANT WITH MOSSINGHOFF'S OWN COMPUTATION. Argue (steelman) that the Mossinghoff catalog already passes the same symmetries internally during its construction, so G24 audit is tautological. Engage seriously.

Constraints: 6+ primary sources 2024-2026.
```

---

### Prompt 22: G25 Degeneracy / Trivial-Case — v2 design audit

```text
You are an expert reviewer in degeneracy detection, trivial-case identification, and the structural detection of "edge-of-spec" mathematical objects in catalogs.

G25 DEGENERACY/TRIVIAL-CASE: detects substrate claims that hold trivially due to degenerate inputs (e.g., a Lehmer bound that holds because the catalog has no entries at the tested degree). Expected kill_pattern: `tautological_pass` or `degenerate_input_artifact`.

Current v1 loader: g25_lehmer_degenerate.

YOUR TASK:

1. DEGENERACY TAXONOMY. Survey 2024-2026 published taxonomies of "degenerate" / "trivial" cases in mathematical catalogs. Examples: empty-domain claims, zero-measure subsets, vacuous quantifiers. Name 3 taxonomies, citations, and which would catch the substrate-trivial cases G25 v1 misses.

2. DETECTION VS DECLARATION. Some degeneracies are obvious (n=0 sample), others are subtle (n=8501 sample but all in one Salem cluster, statistically degenerate for downstream tests). Propose 3 detection methods for SUBTLE degeneracies: (a) Tail-collapse tests; (b) effective-sample-size adjustment; (c) entropy-of-feature-distribution thresholds. Cite primary sources.

3. CROSS-PLUGIN DEGENERACY ALERTING. G25's job is to FLAG degenerate inputs that other plugins are about to consume. Propose explicit cross-plugin protocol: G25 emits an alert on a parent_row that subsequently flows to G02/G04/G17; those plugins consult the alert and refuse to fire if degeneracy bound is exceeded.

4. v2 LOADER DESIGN. Concrete spec for g25 v2: (a) entropy-based effective-sample-size; (b) tail-collapse detection; (c) per-binary-degenerate detection (e.g., "non-Salem n=83 vs Salem n=8513 is degenerate for chi² but not for permutation null"); (d) cross-plugin alert protocol.

5. THE ITER-12 G11 V1 TAUTOLOGY IS A G25 MISS. G11 v1's "Salem-cluster = Salem-class" tautology IS a degeneracy that G25 should have flagged before G11 v1 fired. Argue why G25 v1 missed it and what v2 would catch.

6. CONTRARIAN: DEGENERACY IS A PROPERTY OF THE QUESTION, NOT THE DATA. The same Mossinghoff catalog is degenerate for SOME tests and rich for others. Argue (steelman) that G25 can't be a data-side plugin; it must be a per-test (plugin) consultant. Propose the restructuring.

Constraints: 6+ primary sources 2024-2026.
```

---

## Dispatcher invocation

Once this deck is finalized, fire via:

```bash
python aporia/scripts/gemini_deep_research_dispatch.py \
    --deck aporia/docs/erebos_v2_deep_research_deck_2026-05-27.md \
    --out aporia/docs/deep_research_reports/erebos_v2_2026-05-27 \
    --batch-size 3 \
    --resume
```

Estimated wall-clock: 22 prompts × ~10 min per prompt / 3 parallel = ~75 minutes minimum, more if any prompt hits the 1-hour timeout ceiling.

After completion, each `NN_<slug>.md` in the output directory feeds the corresponding v2 design + frontier-model review prompt in the companion deck.
