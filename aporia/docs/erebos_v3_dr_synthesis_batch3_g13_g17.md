# Erebos v3 — DR Synthesis Batch 3 (G13–G17)

**Source DRs (Gemini Deep Research, 2026-05-27):**
1. `11_g13_relation_weakening_v2_design_audit.md`
2. `12_g14_relation_strengthening_v2_design_audit.md`
3. `13_g15_cross_generator_mi_v2_design_audit.md`
4. `14_g16_anti_anchor_v2_design_audit.md`
5. `15_g17_causal_intervention_v2_design_audit.md`

**Scope:** Cross-cutting themes, prior-art convergence, substrate-capability demands, plugin-level code hotspots, and contrarian alternatives extracted from all 5 reports (Key Points + §§1–3 + §5/§6 contrarian).

---

## A. CROSS-CUTTING THEMES

### A1. "Syntactic / scalar shortcut → semantic / structural ground truth" is the v1→v2 backbone arc

Every one of the 5 DRs identifies the same architectural failure mode and prescribes the same shape of fix:

- **G13** rejects regex string-replacement weakening (`<` → `<=`) as "fundamentally brittle"; demands SMT-validated semantic implication checks via Z3 (`(=> N N') ∧ ¬(=> N' N)`) or abstract-interpretation Galois connections.
- **G14** rejects the naive "inverse of G13" inference (i.e. `<=` → `<`); demands refinement-type guards à la Dafny `Predicate Strengthening` + SMT habitation proofs to confirm the tightened domain is non-empty.
- **G15** rejects the plug-in MLE Shannon estimator on a sparse `13×21` table; demands Bayesian Dirichlet-prior smoothing (Jeffreys α=0.5, Perks α=1/|X||Y|) because the Miller-Madow bias (≈0.285 nats) currently exceeds the measured signal (0.16 nats).
- **G16** rejects the hard-coded `10×` multiplier as "mathematically naive and analytically dangerous"; demands empirical-CDF percentile pushes (e.g. F⁻¹(0.99)) or structural-equivalence-class boundary distances.
- **G17** rejects label-shuffle as a "weak intervention" that injects noise rather than performing graph surgery; demands explicit `do(X=x)` operator implementation that severs incoming edges.

The convergence is exact in form: **all five plugins currently encode a syntactic stand-in for what should be a structural / semantic operation, and all five v2 DRs prescribe replacing that stand-in with a 2024–2026-vintage formal-methods or estimator-theory primitive.**

### A2. Triangulation / chaining / cross-plugin loops beat single-plugin verdicts

Three of the five DRs explicitly propose multi-plugin or sequential composition:

- **G14** proposes the **G14↔G16↔G18 tripartite loop**: G14 strengthens → G18 minimizes counterexample → G16 promotes the original parent claim's bound as anti-anchor tight. "G14's failures are weaponized into tightness proofs."
- **G15** elevates `≥3 distinct plugins agreeing on the same kill_pattern` to a new substrate-grade signal class (`Cross-Plugin Claim Agreement`), explicitly modelled on multi-messenger astronomy / gravitational-wave cross-detector correlation.
- **G17** introduces sequential `do`-calculus chains (`do(A)` → `do(B | do(A))` → `do(C | do(A,B))`) and a new kill pattern `intervention_chain_collapses_at_step_N` mapping directly to Combinatorial Causal Bandits (Xiong & Chen).

Implicit in G13 and G16 as well: G13's proof-mining pipeline routes weakened claims into Kohlenbach-school Dialectica modules; G16's Lethe→G16 handoff protocol is a 5-stage async pipeline (Tag→Queue→Ingest→Parallel-fork→Feedback). The pattern is consistent: **substrate-grade evidence requires composition, not isolated plugin verdicts**, and v3 should formalize the message-passing contracts that make composition routine.

### A3. Phase transitions and tail/extremum regimes are the load-bearing geometry — not averages

Four of five DRs argue that the mathematically interesting events live at boundaries, not in the bulk:

- **G14** "tightening a predicate drastically increases the probability of encountering catastrophic counterexamples"; cites the 2024 Bunkbed Conjecture refutation (Gladkov-Pak-Zimin, planar graph with 7,222 vertices, failure margin ≈10⁻⁶⁵⁰⁰). Must shift from average-case sampling to **outlier-seeking adversarial sampling on the tightest 1%**.
- **G16** "naive 10× often pushes parameter past a structural phase transition into a degenerate state of matter"; cites Pesce-He-Caldarelli 2026 on second-order critical transitions in pruned networks.
- **G17** the entire G17 v2 specification is built around **automated phase-transition detection** at the empirically observed M=1.26 threshold; proposes GSADF (Generalized Supremum Augmented Dickey-Fuller), Phase Equilibrium Degree (PED), and MOSUM bivariate change-point detection.
- **G13** even the contrarian section invokes Kohlenbach proof-mining's metastable convergence as a phase-transition-on-quantifier-arithmetic-hierarchy phenomenon (Π₃⁰ → Π₂⁰ transition).

**Implication for Erebos v3:** every plugin that emits a scalar signal across a parameter sweep needs a phase-transition detector layered on top of it. The "interesting M" is rarely the endpoint; it is the tipping point in the curve.

### A4. The triviality / degeneracy / "trivially-true on empty domain" failure mode is universal

Every DR identifies a failure mode where the plugin's output is technically valid but mathematically void:

- **G13** `weakened_form_trivial_on_target` — relaxing `x<5` to `x<∞` yields zero variance over the test domain. "An informative weakening should target modest survival rate increase (10%→25%), not 10%→99.9%."
- **G14** `type_guard_failed` — the strengthened predicate's domain is empty ("all primes are 2"). SMT-witness-existence check required before empirical testing.
- **G15** the v1 MI=1.41 nats becomes 0.16 nats once control-flow bookkeeping is filtered — and 0.16 < the 0.285-nat Miller-Madow first-order bias. The "signal" was bookkeeping inflation.
- **G16** `adversarial_band_empty_or_artifact` — the 99th percentile may contain zero or only-degenerate objects; survival is meaningless. Loader must pre-check band density and confound variance.
- **G17** contrarian: G17 may merely be **instrument validation** — reproducing the known Salem moderation effect proves the apparatus works, not that nature was newly probed.

**Implication:** v3 needs a uniform `degeneracy_guard` precondition layer that every plugin must pass before its verdict is admitted. Triviality is the dominant false-positive vector across the entire battery.

### A5. Confound stratification is mandatory; unstratified nulls are Simpson's-Paradox vulnerable

Both G15 and G16 explicitly call this out; G17 implies it via the `parent_problem` mediator:

- **G15** Conditional MI on `parent_problem`: `I(plugin; kill_pattern | parent_problem)` to strip out the structural artifact that certain plugins are exclusively routed certain parent classes.
- **G16** confound-stratified permutation null: 500 random subsamples must match the anchor on degree distribution / spectral gap / rank / genus, otherwise survival could be a topological-shift artifact (cites Schäfer-Wetzel on phase-transition detection latching onto trivial order parameters).
- **G17** the `do`-calculus backdoor criterion (CIKA framework, Wang et al. 2026) is exactly confound separation via interventional surgery rather than statistical stratification.

This is the same hard posture that lives in James's `feedback_sampling_strategy_is_analysis.md` and `feedback_permutation_null.md` — sampling/null design **is** the analysis. v3 should hoist stratification metadata into the kill-ledger schema as a first-class column, not a per-plugin afterthought.

### A6. Formal methods (Lean 4, Z3, Dafny, SMT-LIB) cross multiple plugin boundaries

- G13 §2.3: SMT-LIB encoding + Z3 tactic combinators for semantic weakening validation.
- G14 §1: Dafny `Predicate Strengthening` directive + Z3 habitation witness.
- G14 §4(a): same Z3 stack for safe-strengthening type guard.
- G16 §6 Case 3: TorchLean / Lean 4 + IEEE-754 binary32 semantics + CROWN/LiRPA bound propagation to avoid floating-point overflow masquerading as conjecture survival.

This argues for a **shared SMT-bridge service** in Erebos v3 (one Z3 instance / one Lean kernel, exposed via JSON-RPC or similar) rather than each plugin importing and wrapping its own solver. Cuts memory, makes verification logs centrally inspectable, and aligns with the multi-instance substrate-tester coordination doctrine.

### A7. The "instrument vs. discovery" framing recurs as the meta-criterion

G16 and G17 both close with a contrarian observation that the plugin's empirical successes to date have been instrument-validation events, not discoveries:

- **G16**: surviving a 10× adversarial push proves robustness only in the trivial-degenerate-regime sense; needs `Lethe→G16` cold-call queue against genuinely unexplored objects.
- **G17**: reproducing the Salem moderation effect (observed=0.997 vs null_p95=0.024) was a **standard candle calibration**; the substrate-grade value lies in subsequent deployment against unknown latent structures (3 proposed tests: latent algorithmic alignment, cross-substrate transferability, emergent-capability tipping points).

**Implication:** every kill-ledger entry should carry a `discovery_class ∈ {calibration, replication, novel}` tag. v3 dashboards should separately report novel-discovery rate to avoid mistaking instrument health for substrate progress.

---

## B. PRIOR ART CONVERGENCE (citations / frameworks appearing across ≥2 DRs)

### B1. SMT solvers — Z3 (and SMT-LIB)
- G13 §2.3, §4.1: Z3 tactic-based semantic weakening verification.
- G14 §1, §4(a): Z3 as the engine behind Dafny `Predicate Strengthening` + habitation witnesses.
- G16 §6 Case 3 (implicit via CROWN/LiRPA neighbours): bound-propagation verifiers operating in the same SMT-adjacent regime.

### B2. Lean 4 / formal theorem-prover backbone
- G13 §2.3: cites Abouzaid et al. 2026 "First Proof" benchmark defined inside Lean's ecosystem.
- G14 §1: refinement-type frameworks (Dafny / Liquid Haskell) culturally co-located with Lean.
- G16 §1.2, §6 Case 3: CounterMath (Li et al. 2026) operates in Lean 4 with TorchLean SSA/DAG IR; cited again for IEEE-754 semantics.

### B3. Phase-transition / critical-phenomena physics literature
- G14 §2 (Bunkbed) and §5 (G14→G16→G18 loop): adversarial fragility framed as extremal phase fragility.
- G16 §2.1: Pesce-He-Caldarelli 2026 second-order critical transitions in pruned networks; Arnaboldi-Pesce phase transitions in high-dim learning.
- G17 §3: Deng et al. 2026 SpinFlow / Phase Equilibrium Degree (PED); Colchero Paetz 2026 SADF on charge density waves; Plomer et al. 2025 MOSUM bivariate change-point detection.

### B4. Mahler-measure / Lehmer's conjecture as the canonical worked example
- G13 §4.2: Mossinghoff polynomial database + Lehmer μ≈1.17628 used as the v2 demo loader.
- G14 §4(b): Mahler-context loader, Cats-Clark-Dombrowsky-Orvis 2025 quadratic-field Lehmer experiments.

This is a Prometheus-internal favourite that has now landed as the cross-plugin worked example. Suggests `prometheus_math/databases/knots.json.gz`-style on-disk Lehmer/Mossinghoff corpus deserves a stable `mahler_context` loader-API shared by G13 and G14.

### B5. Self-supervised log-anomaly / transformer-based log parsing
- G15 §5.2: LogBERT, ALogSCAN, LogMT (2024–2026) for replacing hard-coded `_bookkeeping` suffix lists.
- Indirectly relevant to G17's `intervention_chain_collapses_at_step_N` — the chain failure pattern is itself a log-sequence anomaly that the same model class could detect.

### B6. Combinatorial Causal Bandits / Mathematical Causal Graphs (CAMA, CIKA, CCB)
- G17 §2.1–2.3 + §4(d): Xiong-Chen CCB; CAMA framework MCG; CIKA do-operator simulator (Wang et al. 2026).
- G16 §5: Lethe agent role is structurally analogous to the LLM-as-interventional-simulator in CIKA — proposing untested anti-anchors that G16 verifies under controlled `do`-style adversarial pushes.

### B7. FunSearch / evolutionary program-search lineage
- G16 §1.1: Romera-Paredes et al. 2024 FunSearch + Nikoleit 2025 Co-FunSearch.
- G16 §1.3: GraphMind dueling Optimist/Pessimist agents (Davila 2024) — same program-search-not-instance-search philosophy.
- Implicit in G17's "LLM-as-interventional-simulator" thread.

### B8. Cousot abstract interpretation / Galois connections
- G13 §1.2 + §2.2: Ranzato 2025 "Best Correct Approximations"; Baldan et al. 2025 model checking as abstract interpretation.
- G14 §1: refinement-type subtyping is the type-theoretic shadow of the same Galois-connection algebra.

### B9. Kohlenbach proof mining / metastable convergence
- G13 §5: Kreisel/Kohlenbach-school Dialectica interpretation; Neri & Pischke 2024–2025 extensions to probability theory.
- G13 §6.2 contrarian: arithmetic-hierarchy descent (Π₃⁰→Π₂⁰) as the "useful weakening" criterion.
- G14 §3 Galvin tree log-concavity: same fragility-at-the-strengthened-boundary morality.

---

## C. NEW SUBSTRATE-CAPABILITIES THE DRs DEMAND

These are capabilities that do not currently exist in the Erebos v2 codebase (per the audits) and that the DRs collectively argue must be built for v3.

### C1. Shared SMT bridge service
A long-running Z3 (and ideally Lean 4) kernel exposed as an in-process service or sidecar to which G13, G14, and G16 (and any later plugin) can issue queries. Required for: (a) semantic-implication checks, (b) refinement-type habitation witnesses, (c) IEEE-754-aware bound propagation.

### C2. Bayesian / smoothed entropy & MI estimators as a substrate library
A `prometheus_math/info_theory/` module providing:
- Dirichlet-prior smoothed plug-in MI (α=0.5 Jeffreys, α=1/|X||Y| Perks).
- Decomposition-based CMI: `H(X,Z) + H(Y,Z) − H(X,Y,Z) − H(Z)` with Bayesian smoothing in every entropy term.
- Cramér's V + Fisher exact + Monte-Carlo permutation χ² as alternates (contrarian path from G15 §6).
- Miller-Madow / NSB / Chao-Shen first-order bias diagnostics emitted alongside every estimate.

### C3. Phase-transition detector library
Reusable kernels for:
- GSADF (Generalized Supremum ADF) explosiveness test on parameter sweeps.
- MOSUM bivariate (mean + variance) change-point detection.
- PED (Phase Equilibrium Degree) computation per Deng et al. 2026.
Plugins (G16, G17) should consume these via a uniform `detect_phase_transition(sweep, metric) -> Optional[TransitionPoint]` interface.

### C4. Confound-stratified permutation-null sampler
A `null_sampler(catalog, anchor, band, confounds, n=500)` utility that does Mahalanobis-distance nearest-neighbour matching in the confound vector space. Required by G15 (CMI conditioning on `parent_problem`) and G16 (degree distribution / spectral gap matching). Should emit the stratification dimensions into the ledger row.

### C5. Empirical-CDF / percentile-based parameter selection
A `select_adversarial_value(catalog, parameter, percentile)` helper for G16; same primitive useful for any plugin choosing extremal test points off a distribution rather than a hard multiplier.

### C6. Refinement-type / safe-mutation static analyzer
For G14 (and reusable by G13): a small AST-level pass that checks domain non-emptiness, ill-formed quantifier scopes, and trivial-tautology shapes **before** empirical evaluation begins. Cheap pre-filter; eliminates large classes of degenerate mutations at zero compute cost.

### C7. Sequential `do`-calculus engine
For G17 v2 and any future plugin doing causal chaining: a state object that tracks `applied_interventions: List[Intervention]` and exposes `intervene(node, value) -> post_intervention_distribution` along with chain-collapse detection. Map directly onto Combinatorial Causal Bandits search.

### C8. Self-supervised log/event-stream classifier
A small transformer (or even a token-bigram LM) trained on historical `kill_ledger` event sequences, replacing the hard-coded `_bookkeeping` suffix list in G15 (and reusable for G17 chain-collapse classification). Hot-reload trained checkpoints into the live pipeline.

### C9. Discovery-class ledger column + dashboard cut
Add `discovery_class ∈ {calibration, replication, novel}` to every ledger row. Substrate dashboards must separately report novel-discovery rate to avoid the G16/G17 contrarian failure mode (mistaking instrument validation for substrate progress).

### C10. Cross-plugin agreement counter
A `claim_id` × `kill_pattern` × `plugin_id.nunique()` aggregator emitting `triangulated` and `triangulated_artifact` flags when ≥3 plugins agree. This is the G15 v3 deliverable but should be made a generic substrate primitive consumable by every downstream filter.

### C11. Lethe→G16-style async cold-call queue
A priority message broker for `FLAG_UNTESTED` candidates with structural-IR payloads (TorchLean SSA/DAG format proposed). Generalizable to any agent-emits / plugin-validates pipeline; should be the substrate's standard `untested_candidates` topic.

### C12. Proof-mining / Dialectica routing module
Per G13 §5: a callable that consumes a weakened claim with arithmetic-hierarchy metadata (Π₃⁰→Π₂⁰ transition) and routes through a Kohlenbach-style witness-extraction tactic. Even a thin Lean 4 wrapper would unblock the G13→quantitative-bound output pipeline.

---

## D. PLUGIN-SPECIFIC HOTSPOTS (one per plugin; code-level change demanded)

### D1. G13 RELATION-WEAKENING — hotspot: `_predicate_lattice` traversal
**File-level change demanded:** Replace the regex-based weakening rules with an AST→SMT-LIB encoder + Z3 strict-implication validator.
- Current shape: regex string-replace on claim text (`<` → `<=`).
- v2 demand: `weaken(predicate_ast) -> Iterable[WeakenedAST]` where each candidate is admitted only if `Z3.check_sat((=> orig new) ∧ ¬(=> new orig)) == sat`.
- New kill patterns to add: `predicate_unrelaxable` (Z3 says no strict weakening exists), `weakened_form_trivial_on_target` (zero variance across test suite).
- Threshold criterion: weakening informative only if survival-rate jump is moderate (e.g. 10%→25%, not 10%→99.9%) **and** the arithmetic hierarchy descended (Π₃⁰→Π₂⁰).

### D2. G14 RELATION-STRENGTHENING — hotspot: the safe-strengthening type guard
**File-level change demanded:** Insert a pre-empirical SMT habitation check before any tightened predicate hits the evaluator.
- Specific guard: extract domain `D` from tightened `Φ'(x)`; call Z3 for a witness `w ∈ D` with `Φ'(w) = true`; reject with `type_guard_failed` if empty or trivial-witness (e.g. zero-vector).
- Then switch sampling: **do not use the same average-case distribution G13 used**. Mahler-context-loader-style: sort empirical data by proximity to the original bound, re-test only on the **top 1% nearest to bound saturation**.
- New kill patterns: `strengthening_fails_at_extremes` (passes 99% average, fails on adversarial 1%), `strengthening_holds_only_on_subset` (decision-tree-identified topological subset).
- Wire the `strengthening_fails_at_extremes` output into the G14→G18→G16 loop as `tightness_witness` events.

### D3. G15 CROSS-GENERATOR MI — hotspot: the MI estimator and the bookkeeping filter
**File-level change demanded:** Two-part rewrite.
1. Replace `Σ p log(p/p̂)` plug-in MI with the Bayesian Dirichlet-prior estimator (sample code in DR §4.1.a; uses Jeffreys α=0.5). Emit Miller-Madow first-order bias estimate alongside the value so the consumer can see when measured MI < expected bias.
2. Replace the hard-coded `_bookkeeping`/`_init` suffix filter with a learned classifier (LogBERT / ALogSCAN architecture trained on historical ledgers; threshold at PLL > 0.95 → drop as bookkeeping).
- Add Conditional MI: `I(plugin; kill_pattern | parent_problem)` with the same Bayesian smoothing across all four H terms.
- Add cross-plugin agreement aggregator emitting `triangulated_artifact` when ≥3 plugins agree on a structurally invalid claim.

### D4. G16 ANTI-ANCHOR — hotspot: `select_adversarial_value` (currently `M = 1.20` or `10.0`)
**File-level change demanded:** Three-part rewrite.
1. Replace the hard-coded multiplier with `catalog.get_distribution(param).percentile(99)` (and `.percentile(1)` for the LOW direction).
2. Bidirectional testing: run HIGH and LOW independently; require survival in **both** for `conjecture_survives_adversarial_attack`; tag asymmetric survival as `directionally_fragile`.
3. Confound-stratified permutation null: replace plain `catalog.sample(n=500)` with `sample_nearest_neighbor(anchor.confounds)` using Mahalanobis distance in the structural-invariant space (degree distribution, spectral gap, rank, genus).
- New kill pattern: `adversarial_band_empty_or_artifact` — emitted when the band's population density < `MIN_REQUIRED` or confound variance ≈ 0.
- Add the `Lethe → G16` async ingestion: poll a priority queue for `FLAG_UNTESTED` structural IR payloads, strip LLM justifications, fork HIGH/LOW in parallel, broadcast results back.

### D5. G17 CAUSAL-INTERVENTION — hotspot: `g17_lehmer_label_shuffle`
**File-level change demanded:** Rename and reimplement as `g17_structural_dropout_do_operator`.
- The label-shuffle randomizes class labels — a noise-injection operation. Replace with graph-surgery: severance of incoming edges to the target node (or fix to a constant value, e.g. `do(Salem_Flag = 0)` for all nodes).
- Add multi-threshold-sweep phase-transition detector: GSADF on the survival-metric series across `[1.20, 1.40]` at `ΔM = 0.01`; also compute PED continuously; flag the maximum PED-drop point as the transition (currently `M = 1.26`).
- Add a sequential-chain runner that applies `do(A)` → `do(B|do(A))` → `do(C|do(A,B))` and emits `intervention_chain_collapses_at_step_N`.
- Robustness check spec: narrow sweep `[1.235, 1.285]`, `ΔM = 0.005`, **1000** permutations per point (currently 200), explicit GSADF rejection of the smooth-and-homoscedastic null.
- Cross-domain transfer test: run the same M=1.26 sweep on the BSD-context rank-class binary; survival → universal scale-invariance.

---

## E. CONTRARIAN ALTERNATIVES

### E1. "Weakening is usually useless" (G13 §6)
**Steelman:** Mathematicians tune predicates to sit precisely at the truth/falsehood boundary. Mechanically weakening them produces trivially-true statements that survive evaluation only because they have collapsed to tautology. Abouzaid et al. 2026 "First Proof" benchmark documents this exact failure mode for LLM mathematicians: weakened conclusions are "overwhelmingly plausible but mathematically uninteresting." A weakened claim's survival is not discovery; it is constraint removal.

**Response prescription:** Threshold criteria are non-optional. (a) Non-triviality: `S_weakened ⊂ M` strictly. (b) Boundary proximity: information loss bounded — a 10%→99.9% survival-rate jump is degenerate; 10%→25% is informative. (c) Proof-theoretic tameness: weakening must descend the arithmetic hierarchy (e.g. Π₃⁰→Π₂⁰); if not, utility as a logical bridge is minimal. Without all three guards, G13 will mostly emit junk.

### E2. "Strengthening just upgrades understated parents, not novel theorems" (G14 §6)
**Steelman:** If a parent claim was lazily formulated (e.g. `n² > -5` instead of `n² ≥ 1`), G14's "successful strengthening" is mere database maintenance, not discovery. The system has not found a new bound; it has fixed a sloppy old one. Mistaking these for promotions inflates the substrate's discovery rate with bibliography hygiene.

**Response prescription:** Information-gain / gradient-of-bound diagnostics distinguish the cases. For continuous bounds: measure empirical residual distance from the parent bound — if residuals are strictly bounded away from zero (function never gets within 100 units of the bound), the parent was understated; G14 should silently `upgrade_parent_in_place`, not emit a discovery event. For discrete predicates (e.g. "graph is connected" → "graph is Hamiltonian"): check whether the verification dataset was biased — generate connected-non-Hamiltonian witness; if found, reject strengthening, preserve parent. Only after both diagnostics fail should the strengthened form be promoted as `novel`.

### E3. "MI is the wrong statistic; use Cramér's V" (G15 §6)
**Steelman:** Marinescu et al. 2025 prove the empirical-MI distribution under independence is a complex linear combination of χ² variables (gradient vanishes at the null; needs second-order δ-method), making p-values opaque. MI in nats has no natural scale — is 1.41 nats catastrophic or trivial? Cramér's V is bounded in [0,1] with universally understood thresholds (~0.05 negligible, ~0.80 massive) and stable under dimension changes. Exact tests (Fisher, Monte-Carlo permutation χ²) handle zero-inflation natively, no Dirichlet priors needed. For G15's specific regime (small N, discrete, sparse), the engineering simplicity and epistemological clarity of Cramér's V strictly dominate.

**Response prescription:** Run both. Emit Cramér's V + Monte-Carlo permutation χ² p-value alongside the Bayesian-smoothed MI. Let consumers choose; let convergence/divergence between the two metrics itself become a signal (when they disagree, it usually means MI smoothing is doing real work or distorting the result). Default the dashboard to Cramér's V for human-readability; reserve MI for the genuinely-information-theoretic downstream consumers (chain-rule decomposition, conditional analyses).

### E4. "Adversarial pushes prove the wrong thing" (G16 §6)
**Steelman:** Pushing a parameter to its extreme often relieves mathematical tension rather than exacerbating it. If a conjecture is `A(x) + B(x) = C(x)` and `x → ∞`, then `A` dominates and the conjecture degenerates to `A(x) ≈ C(x)` — trivially true at the boundary. Reporting "anchor survived adversarial push" then proves the conjecture is trivial in a degenerate boundary state, not that it is robust under stress. Specific failure regimes documented: (a) topological collapse in network pruning past the percolation threshold; (b) ferromagnetic→paramagnetic phase transitions in spin/tensor models; (c) IEEE-754 overflow/underflow masking the actual mathematical object.

**Response prescription:** Sophisticated, structure-preserving generators required — not scalar pushes. (a) Use Co-FunSearch evolutionary program search to navigate exactly on the critical manifold of the phase transition. (b) Use formally-verified rounding (TorchLean / IEEE-754 in Lean 4) plus CROWN/LiRPA bound propagation to ensure adversarial values stress the logic, not the compiler. (c) Make `adversarial_band_empty_or_artifact` the default outcome when the band's confound variance approaches zero — pessimistic priors over the "interesting" interpretation.

### E5. "G17 is instrument validation, not discovery" (G17 §7)
**Steelman:** Reproducing the known Salem moderation effect (observed=0.997 vs null_p95=0.024) is what high-energy physics calls "pointing the detector at the standard candle." It proves the apparatus is calibrated; it does not constitute a new finding about nature. ITER-18's substrate value is the empirical certification that the G17 statistical plumbing works — but until the loader is run against substrates whose ground truth is unknown, every "discovery" is a replication artifact. Risk: confusing the calibration arc for the discovery arc (echoes James's `feedback_resolution_dependent_truth_2026_05_04.md`).

**Response prescription:** Three concrete deployment targets to convert the instrument into a discovery engine: (1) latent algorithmic-alignment pathways — `do`-intervene on geometric syntax of a problem, observe if algebraic solution capability survives (CAMA framework MCG). (2) Cross-substrate causal transfer — project a code-generation causal chain onto an NLP logic puzzle; survival proves substrate-independent causal representations. (3) Emergent-capability tipping points — sequentially mask attention heads with `do(Head_i = 0)`, run MOSUM+PED across intervention depth; smooth degradation vs. percolation-threshold collapse is the discoverable phase question. Tag the ledger row `discovery_class = calibration` for all pre-deployment runs.

---

## SYNTHESIS — what v3 should commit to

The five DRs converge on a single architectural prescription with five surface manifestations:

> **Replace every syntactic / scalar / unstratified primitive in the v2 plugin layer with its 2024–2026-vintage structural / Bayesian / confound-stratified counterpart, expose them as shared substrate libraries (SMT bridge, info-theory module, phase-transition detector, confound-null sampler), and make composition (triangulation, sequential chains, cross-plugin loops) the default verdict pathway rather than a special case.**

The triviality / degeneracy / "trivially-true on empty domain" failure mode is the single dominant false-positive vector across G13–G17; the universal `degeneracy_guard` precondition layer (C6 + C9 above) is the highest-leverage one-time fix.

Phase-transition detection (C3) and confound-stratified nulls (C4) are the next two highest-leverage substrate primitives — each unlocks multiple plugins simultaneously and aligns with James's existing hard postures (`feedback_permutation_null.md`, `feedback_sampling_strategy_is_analysis.md`, `feedback_failure_signal_vector_field.md`).
