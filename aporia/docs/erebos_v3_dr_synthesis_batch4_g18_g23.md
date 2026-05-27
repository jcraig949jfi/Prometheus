# Erebos v3 — DR Synthesis Batch 4 (G18, G19, G20, G22, G23)

**Synthesized:** 2026-05-27
**Source reports:** 5 Gemini Deep Research v2 design audits
**Plugins covered:** G18 Minimal-Counterexample, G19 Proof-Obligation, G20 Instrument-Disagreement, G22 Subgraph/Clique, G23 Asymptotic-Limit

This document extracts cross-cutting themes, convergent prior art, demanded substrate capabilities, plugin-specific code-level hotspots, and contrarian alternatives from the batch-4 Erebos v2 design audits.

---

## A. CROSS-CUTTING THEMES

### A1. Numerical heuristics are band-aids over structural/algebraic gaps
This is the single strongest cross-cutting theme — appearing explicitly in **G18, G19, G22, and G23** (4/5 reports), and implicitly in G20.

- **G18:** `M_COMPARISON_EPSILON=1e-9` is denounced as a "band-aid" — Mahler measure equality across cyclotomic extensions is algebraic, not numerical. The fix is structural: LLL factorization + cyclotomic stripping + exact symbolic measure on the irreducible non-cyclotomic core.
- **G19:** `MAX_RECURSION_DEPTH=10` is the same band-aid in a different costume — an arbitrary cap masking the absence of a natural graph-diameter computation or Lean termination check. The DR explicitly uses the word "band-aid."
- **G22:** Hand-rolled Louvain + arbitrary Jaccard threshold are denounced as topologically degenerate. Replace modularity with the **Constant Potts Model (CPM)** under Leiden, where the resolution parameter `γ` makes density thresholds *parameters of the model*, not magic numbers.
- **G23:** A single-slope log-log regression with `R²=0.25` masks regime changes — the fit is being globally averaged over data drawn from two structurally different populations (exhausted low-N, heuristic-sampled high-N).

**Substrate implication:** every v2/v3 loader must replace its tunable scalar thresholds with either (a) a structural classifier (cyclotomic / well-founded / SCC test), (b) a model-selection criterion (BIC, bootstrap CI), or (c) a parameter that is itself an axis of the result (CPM `γ`, BPL break-point `N_b`). Magic constants are a kill-pattern in their own right.

### A2. Sub-symbolic findings must be quarantined from substrate-grade ledgers
Appears in **G19, G20, G22** (and shadowed in G18).

- **G19:** Ledger-recorded "verdicts" are sociological consensus, not formal truth. The v3 architecture explicitly relegates the ledger to a *certificate store* — truth is mediated only by the Lean 4 kernel.
- **G20:** Meta-epistemic findings (e.g., "Lethe hallucinated on Kähler geometry") must be **quarantined** into Aporia's self-audit ledger. Allowing them to flow back into the primary mathematical corpus risks contaminating future Lethe pre-training with logged hallucinations.
- **G22:** Anti-unification yields "Master Properties" that are claims, not theorems; they must be passed to G18/G06 for falsification before being treated as substrate axioms.
- **G18:** A claimed minimal counterexample is *not* a discovery until Phase 1 (exact symbolic re-evaluation) → Phase 2 (Lean 4 formal proof) → Phase 3 (cryptographic embargo + external audit) completes.

**Substrate implication:** there are at least three tiers of epistemic objects the substrate must distinguish:
1. **Ledger attestations** (G20 instrument disagreements, G22 cliques) — Aporia-routed, never substrate-grade.
2. **Induced claims** (G22 LGGs, G18 candidate counterexamples) — substrate-tier candidates, must pass formal verification.
3. **Lean-kernel-discharged theorems** (G19, G18 Phase 2) — substrate-grade.

The current pipeline appears to under-distinguish (1) from (2). This is a substrate-architecture bug, not a plugin bug.

### A3. Vacuousness / data-sparsity is the dominant practical failure mode
**G20** is paralyzed (no live emissions because aligned Lethe doesn't hallucinate hard enough). **G22** is statistically suspect at N≈420 nodes (cliques are likely sparse-matrix artifacts; needs 10× scale). **G23** has only ~50 effective data points in the high-degree regime, half of which are heuristic estimates not exhaustions. **G18** can't fire on obscure conjectures because there's no kill-ledger density to gradient-descend on.

The DRs prescribe three independent mitigations:
- **Synthetic seeding** (G20: Pseudo-Lethe with small models; corrupted-Stygian; Pollux-vs-Stygian). (G18: LLM-driven adversarial weakened-conjecture mutation to seed a synthetic kill-ledger.)
- **Bootstrap statistical guards** (G23: 10k-iteration paired-residual bootstrap before declaring `R² advantage`). (G22: shatter-test under `γ` perturbation to detect resolution artifacts.)
- **Scale demand** (G22: 4,200+ nodes minimum). (G23: confidence intervals require the catalog to be re-stratified by `effective degree` and `length`, not just `N`.)

**Substrate implication:** the substrate needs a first-class **"sampling-context"** field on every emission (already a James-stamped doctrine per `feedback_sampling_strategy_is_analysis.md` — this batch reinforces it for four plugins simultaneously). Without it, a low-data clique is indistinguishable from a high-data clique in downstream consumers.

### A4. Neuro-symbolic verifier-in-the-loop is the convergent architecture
**G18** prescribes Lean 4 / Coq formalization in Phase 2. **G19** is *built* around verifier-in-the-loop (COPRA, ProofNet++, Pantograph). **G20** uses SymPy / Z3 as the deterministic side of the Lethe-vs-Stygian clash. **G22** routes anti-unified Master Properties through G18's adversarial falsifier (which itself terminates in Lean). **G23** doesn't directly invoke a kernel, but its bootstrap-CI gate is the statistical analog of the same pattern: "no claim without a verifier."

The implicit substrate architecture all 5 DRs are converging on:

```
  [stochastic proposer]  →  [structural / statistical filter]  →  [formal kernel]  →  [substrate]
   (LLM, heuristic,         (Leiden, anti-unification,            (Lean 4 /
    Pollux, Lethe)           bootstrap, factorization)             Stygian / Z3)
```

Every plugin in this batch occupies one or more positions in this pipeline. The substrate needs a **shared interface** between these stages — not five different ad-hoc handoffs.

### A5. Effective vs. nominal complexity — the right independent variable matters more than the right model
**G18:** `degree` is the wrong gradient-field axis; (degree, Mahler) joint space is right. Also `effective degree` (degree minus cyclotomic padding) is the right complexity for a polynomial.
**G22:** Jaccard overlap of *raw* datasets is the wrong edge weight; semantic similarity over MathBERT/MNER embeddings is the right one.
**G23:** Degree `N` is an imperfect proxy; the v2 loader sweeps `[N, H(P), L(P), N_eff]` and emits `complexity_measure_dependent_finding` if the best-fit law changes across them.
**G19:** Latest-ledger-verdict is the wrong truth proxy; Lean type-check is the right one.

**Substrate implication:** the substrate should treat "what is the right complexity coordinate?" as a *first-class research output*, not a setup parameter. G23's `complexity_measure_dependent_finding` kill pattern is the model — every plugin should emit something analogous when its result hinges on its choice of coordinate.

### A6. Two-population / regime-change detection is missing across the pipeline
**G23** explicitly demands broken power-law (BPL) regression with BIC selection of break-points. **G18**'s Voronoi tessellation of kill-density is essentially the same idea in 2D. **G22**'s shattering-under-γ-perturbation test detects regime boundaries in clique density. **G19**'s SCC + LFP iteration on cycles is regime detection on the proof-obligation graph.

None of the v1 loaders do this; all four are committing the **single-regime fallacy** — fitting a global model to a population that is in fact a mixture. This is a substrate-wide bug class, not a per-plugin issue.

### A7. Anti-unification / LGG as a first-class operator
G22 makes anti-unification central (Plotkin 1970). G18's "agentic substrate seeding" generates weakened-conjecture variants — which is anti-unification's dual (mutating around a center). G19's proof-obligation extraction is unification under types. G20's MNER Concept-K is anti-unification of two NL outputs.

**Substrate implication:** anti-unification belongs in `prometheus_math` or `techne/lib` as a first-class operator with the usual Math-TDD treatment (authority / property / edge / composition tests). Currently it's being re-derived in three different plugins with three different qualities.

---

## B. PRIOR-ART CONVERGENCE (citations appearing across 2+ DRs)

### B1. Lean 4 / Coq / formal verification kernels
Appears in **G18 (Phase 2), G19 (v3 architecture), G20 (Stygian role), G22 (downstream falsifier)** — 4/5.
- **Lean 4 / Mathlib** as the universal formal target.
- **Coq** mentioned in G18 (alongside Lean) and G19 (CIC argument).
- **Pantograph (2024)** — machine-to-machine Lean 4 interface — G19 makes it the v3 backbone; cited as the canonical answer to "how does Python orchestration talk to the kernel."

**Substrate implication:** the substrate needs *one* Lean-integration layer used by all four plugins. Currently each DR specifies its own.

### B2. Aletheia (Gemini Deep Think, 2026) and AlphaEvolve (DeepMind, 2025)
Appears in **G18 (counterexample search)** and shadowed in **G19 (neural-guided proof)** and **G20 (LLM-as-mutator argument)**.
- Aletheia: 700 Erdős conjectures, 4 solved end-to-end via Generator-Verifier-Reviser.
- AlphaEvolve: matrix-multiplication record, kissing-number configurations; LLM-as-mutator inside an evolutionary loop with rigorous evaluator.

These are the *same architectural pattern* G19's COPRA/ProofNet++ use — and the same pattern G20 prescribes for synthetic-clash seeding. Three plugins, one architecture (LLM-proposer + symbolic-verifier closed loop).

### B3. COPRA / ProofNet++ / Pantograph stack (2024–2026)
Cited primarily in **G19**, but the COPRA "Stateful Backtracking + Environment Feedback" pattern is what **G18** Phase 2 also requires for its post-success Lean formalization. **G22**'s Phase B (CSE + Weisfeiler-Lehman kernel for premise selection, from Wang et al. 2025/2026) cites the same theorem-prover-premise-selection literature COPRA inhabits.

### B4. Dobrowolski / Voutier / Smyth bounds on Mahler measure
**G18** (Section 2.1: Kronecker, Smyth, Breusch) and **G23** (Section 5.2: Dobrowolski's `1 + c (log log N / log N)^3` bound).
- These two reports independently arrive at the conclusion that classical Mahler-measure literature (Smyth bounds, Mossinghoff tables, Dobrowolski lower bound) is the canonical anchor — and that the v1 loaders are *ignoring* this literature in favor of ad-hoc numerical heuristics.

### B5. Mossinghoff polynomial tables (degree ≤ 44 exhausted, selectively to 54)
**G18** (kill-ledger seeding source) and **G23** (the catalog whose two-population structure breaks log-log regression). Both DRs note the boundary at `N=44` as the regime-change candidate.

### B6. Leiden algorithm + Constant Potts Model (Traag et al.)
**G22** (central proposal) and shadowed in **G18** (Voronoi-tessellation kill-density is structurally analogous to community detection on the search-space graph).

### B7. Kohlenbach proof mining
**G19** (Section 5: turning qualitative verification into quantitative bounds). Not directly cited in G18, but G18's "extract exact Mahler measure with interval arithmetic from a verified Lean proof" is operationally the same paradigm — quantitative extraction from a formal proof.

### B8. Ensemble disagreement as epistemic-uncertainty signal
**G20** (McAfee & Barnes ENSO 2025/26; Kurniawan et al. MLIP 2025/26). The MLIP paper's finding that ensemble disagreement *collapses* under OOD shift is *the* analytical frame for the "Vacuous-until-Lethe-v2" problem and applies equally well to G22's small-graph spurious-clique problem (low-data ensembles look confident-and-wrong).

---

## C. NEW SUBSTRATE-CAPABILITIES THE DRs DEMAND

Listed in roughly decreasing breadth (capabilities serving more plugins listed first).

### C1. A shared Lean 4 / Pantograph orchestration layer
**Serves:** G18 (Phase 2), G19 (entire v3), G22 (downstream falsifier), G20 (Stygian backend candidate).
- A Python/Rust orchestration class exposing: `load_environment(lean_source)`, `extract_dependency_tree(claim_id)`, `execute_tactic(tactic, env)`, `is_well_founded(cycle_nodes)`, `type_check(expr)`.
- Currently does not exist as a substrate-level service. G19 spends a full section spec'ing it; G18, G22, G20 will all reinvent it if it's not centralized.

### C2. An exact-algebra polynomial pipeline
**Serves:** G18 (cyclotomic stripping), G23 (effective-degree column).
- LLL factorization over ℚ[x], cyclotomic detection (monic, integer, reciprocal, degree = φ(k) for some k), monomial stripping, exact Mahler measure via Sturm sequences with rational arithmetic, interval arithmetic for upper-bound certification.
- Belongs in `prometheus_math` next to `derive_kill_signature`. Should be Math-TDD'd: authority tests against Lehmer's polynomial, property tests on cyclotomic products, edge tests on degree-1/2 boundary cases.

### C3. A registered anti-unification operator
**Serves:** G22 (LGG of cliques), G18 (weakened-conjecture mutation), G19 (proof-obligation unification), G20 (Concept-K extraction).
- Plotkin first-order syntactic generalization (FOSG), distance-guided variant from Cho et al. 2026, CSE + Weisfeiler-Lehman kernel from Wang et al. 2025/26.
- Per `feedback_operator_precedents.md`: anti-unification is the *resolution* (an inference move), while the *problem* is "find what these claims share." Don't confuse them.

### C4. Bootstrap / model-selection statistical primitives
**Serves:** G23 (paired-residual bootstrap for ΔR²), G22 (resolution-artifact shatter test), G20 (ablation-test loop), G18 (Voronoi cell density confidence).
- 10k-iteration paired-residual bootstrap with CI extraction, BIC for nested model selection, permutation null (already established for tensor coupling per `feedback_permutation_null.md`).
- Belongs in `prometheus_math/statistics/` as registered operators.

### C5. A two-tier (claim vs. theorem) emission protocol
**Serves:** G19, G20, G22 quarantine requirements.
- Every emission carries a `verification_tier ∈ {ledger_attestation, induced_claim, kernel_discharged}` and a `routing_destination` (Aporia for tier 1, G18-falsifier for tier 2, substrate for tier 3).
- This is the substrate-architecture-level fix for Theme A2.

### C6. A Mathematical-NER / MathBERT semantic-embedding service
**Serves:** G20 (Concept-K), G22 (semantic edge weights instead of Jaccard).
- LERT-BiGRU-IDCNN-CRF (F1 = 97.34%, Zheng et al. 2025) or AT-BSAC (F1 = 93.74%, Lai et al. 2024) as the MNER backbone.
- MathBERT or Llemma for embeddings.
- TF-IDF against Mathlib / arXiv-math corpus to penalize generic mathematical "stop-words" ("Equation", "Set", "Function").

### C7. A synthetic-seeding capability across plugins
**Serves:** G20 (Pollux-vs-Stygian, corrupted-Stygian, Pseudo-Lethe), G18 (weakened-conjecture LLM mutation), G22 (10× data demand).
- Generic "construct an adversarial-disagreement bench from a known-good corpus" service.
- Same architectural pattern as Harmonia's adversarial attack registry.

### C8. Broken-power-law / regime-change detection
**Serves:** G23 (kink-point regression), G18 (Voronoi as 2D regime detector), G22 (γ-sweep shatter test), G19 (SCC + LFP).
- A single library: iterate candidate break-points, fit independent OLS on each side, BIC-select.
- Emits `regime_change_at_X` kill patterns.

---

## D. PLUGIN-SPECIFIC HOTSPOTS (one per plugin)

### D1. G18 (`g18_lehmer_v2`) — Replace `M_COMPARISON_EPSILON` with structural factorization
**Concrete change demanded:**
```python
# CURRENT (v1 — band-aid):
if abs(candidate_mahler - known_mahler) < M_COMPARISON_EPSILON:
    return False  # not novel

# v2 — structural:
factors = factor_over_Q(candidate_poly)  # LLL or Cantor-Zassenhaus
non_cyclotomic = [f for f in factors if not is_cyclotomic(f)]
core_poly = product(non_cyclotomic)
if core_poly_matches_known_entity(core_poly):
    return KillPattern("known_entity_cyclotomic_extension")
exact_mahler = mahler_measure_exact(core_poly)  # Sturm sequences over ℚ
```
- New required helpers: `factor_over_Q`, `is_cyclotomic` (monic + integer + reciprocal + φ(k) degree check), `mahler_measure_exact`.
- New kill patterns: `prediction_was_in_excluded_cyclotomic_band`, `region_too_sparse_for_test`.
- The v1 Mossinghoff degree-band scan is replaced by a Voronoi-cell / gradient-ascent driver over the `(degree, Mahler)` plane.

### D2. G19 (`g19_v3_formal_obligations`) — Replace ledger transitivity with Pantograph type-check
**Concrete change demanded:**
```python
# CURRENT (v1):
def evaluate(claim):
    sub_verdicts = [ledger.latest_verdict(c) for c in claim.children]
    return all(sub_verdicts)

# v3 — formal:
def evaluate(claim_id, lean_source):
    env = pantograph.load_environment(lean_source)
    dag = pantograph.extract_dependency_tree(claim_id)
    sccs = dag.find_strongly_connected_components()
    for scc in sccs:
        if not resolve_fixed_point(scc, env):
            return KillPattern("cycle_unresolvable", scc)
    for obligation in dag.topological_sort():
        if not pantograph.execute_tactic(obligation.tactic, env).is_success():
            return KillPattern("obligation_unsatisfiable_in_lean", obligation.id)
    return Verified()
```
- Replace `MAX_RECURSION_DEPTH=10` with `O(|V|)` derived from `dag` size, or with Lean's native `maxRecDepth`.
- New kill patterns: `obligation_unsatisfiable_in_lean`, `cycle_unresolvable`, `type_mismatch_in_graph`.
- Existing `g19_ledger_transitivity` is demoted to a *certificate cache*, not a truth oracle.

### D3. G20 (`g20_instrument_disagreement_v2`) — Add ablation-test re-prompt loop
**Concrete change demanded:** the loader currently does not exist (Vacuous-until-Lethe-v2). Bootstrap with **Pollux-vs-Stygian** MVP (no LLM dependency), then layer on:
```python
def execute_ablation_test(original_prompt, concept_k, llm_model):
    ablated_prompt = remove_entity(original_prompt, concept_k)
    new_verdict, _ = llm_model.evaluate(ablated_prompt)
    return new_verdict
```
- Replace alphabetic-first ≥6-char token extraction with **LERT-BiGRU-IDCNN-CRF MNER** → TF-IDF weighting against Mathlib corpus → highest-weighted shared entity = Concept K.
- New kill patterns: `concept_K_extraction_failed`, `instrument_disagreement_explained_by_context`.
- All emissions route to Aporia self-audit ledger, *never* to the primary math substrate.

### D4. G22 (`g22_master_property_v2`) — Replace Louvain with Leiden + CPM + anti-unification
**Concrete change demanded:**
```python
# Phase A — community detection:
partition = leidenalg.find_partition(
    G,
    leidenalg.CPMVertexPartition,   # not ModularityVertexPartition
    resolution_parameter=0.85,       # explicit γ, not magic
)

# Phase B — master-property extraction:
asts = [parse_to_ast_with_CSE(claim) for claim in clique]
M = plotkin_anti_unify(asts)  # LGG, returns expression with bound variables X_i

# Phase D — kill patterns:
if count_variables(M) == 0 or depth(M) == depth(asts[0]):
    return KillPattern("master_property_too_specific")
if shatter_test(clique, gamma=0.90):
    return KillPattern("clique_was_resolution_artifact")
```
- New required helpers: `parse_to_ast_with_CSE` (Common Subexpression Elimination), `plotkin_anti_unify`, `shatter_test`.
- Integrate downstream with G18 (counterexample search on M) and G06 (boundary/void mapping when G18 finds an exception).
- **Hard constraint per Section 7 of DR:** treat all G22 outputs as low-confidence until the substrate has ~4,200+ nodes. Until then, every emission carries a `low_sample_size_warning`.

### D5. G23 (`g23_v2_asymptotic_diagnostics`) — Multi-complexity sweep + BPL + bootstrap CI
**Concrete change demanded:**
```python
# CURRENT (v1): single log-log fit on (N, y) → R²=0.25
# v2 — three concurrent upgrades:

# (1) Broken power-law detector
for N_break in range(10, max_N):
    fit_low = ols_log_log(data[data.N <= N_break])
    fit_high = ols_log_log(data[data.N > N_break])
    if BIC(broken) < BIC(single) - 10:
        emit_break_point(N_break, alpha_low, alpha_high)

# (2) Multi-complexity sweep
for complexity_col in ['N', 'H', 'L', 'N_eff']:
    for law in [inv_X, inv_log_X, inv_sqrt_X, exp_neg_X]:
        R2 = fit(data, complexity_col, law)
    record_best_law_per_column()
if best_law differs across columns:
    return KillPattern("complexity_measure_dependent_finding")

# (3) Bootstrap CI on ΔR² between competing laws
boot_deltas = [R2_A_b - R2_B_b for b in range(10000)
               on residual-resampled y]
if 0 in ci_95(boot_deltas):
    return KillPattern("statistically_indistinguishable")
```
- New required helpers: `effective_degree(P)` (subtract cyclotomic-factor degree — shared with G18 D1), `coefficient_height`, `polynomial_length`, `mahler_derivative`.
- New kill patterns: `decay_law_changes_at_complexity_K`, `complexity_measure_dependent_finding`, `statistically_indistinguishable`.
- The current `R² = 0.54 vs 0.51` margin is explicitly **not** safe — must survive bootstrap CI before promotion.

---

## E. CONTRARIAN ALTERNATIVES

### E1. G18 — "G18 is structurally biased toward famous conjectures"
The v1 G18 thrives on dense kill-pattern landscapes — exactly the regime that exists *only* for heavily-studied conjectures (Lehmer, RH, BSD). For obscure conjectures the Voronoi cell is one infinite blob and the gradient is identically zero. The DR's mitigation is "agentic substrate seeding" — use an LLM-as-mutator to generate weakened variants of the conjecture, kill them cheaply with SMT, log the kills as synthetic seeds, then bootstrap a synthetic kill-density topology. **Tension this exposes:** the substrate currently has no notion that some plugins are *only* applicable in data-dense regimes. Per `feedback_calibration_anchors_in_depth.md`, this is exactly the under-explored-territory problem — but going the other direction: G18 doesn't *generate* calibration anchors, it *consumes* them, and starves in their absence.

### E2. G19 — "G19 is a poor re-implementation of Lean's CIC; deprecate it as a logic engine"
The hardest steelman in the batch. The argument: macro-claim decomposition into a conjunction of obligations *is exactly* what the Calculus of Inductive Constructions does natively at the Lean kernel level. Macro claims are theorems; obligations are sub-goals; transitivity is function application. By managing this externally in Python with BFS-depth-limits and ledger verdicts, G19 introduces a "semantic gap" — any drift between its definition of transitivity and Lean's *is unsoundness*. The DR's conclusion: G19's *only* legitimate role is as a **social-to-formal bridge** (fetches distributed claims, translates to a Lean environment, asks the kernel "does this compile?", broadcasts the binary). Any attempt to do logic in G19 itself is reinventing — poorly — what Lean already does correctly. **Implication for substrate:** be ruthless about which plugins do *novel work* vs which are *I/O layers around existing kernels*. Pretending the second is the first is the substrate-passive-consumer trap per `feedback_substrate_passive_consumer_warning.md`.

### E3. G20 — "Studying LLM hallucinations is static on a broken TV"
The argument: when LLMs disagree with deterministic solvers, the reason is trivially the same — the LLM is a stochastic pattern-matcher operating outside its interpolation bounds. Spending compute on MNER + TF-IDF + ablation-test loops to identify *which mathematical noun* triggered the hallucination is a category error; the answer is always "noise." The DR's deprecation proposal: when Lethe and Stygian disagree, default natively to Stygian and discard Lethe's output as a failed heuristic branch. Reallocate G20's compute budget (MathBERT embeddings, LERT models, re-prompt loops) to pushing Stygian one node deeper into the formal proof tree. **My read:** this is the strongest steelman of the five — and it's exactly the kind of "is the meta-work paying its way?" question James's `feedback_substrate_passive_consumer_warning.md` demands. G20 must justify itself with a *behavior delta* in Lethe-v2's training, or it dies.

### E4. G22 — "Cliques at N≈420 are sparse-matrix artifacts, not laws"
At 420 nodes, even an Erdős–Rényi random graph yields high-modularity clusters; even Leiden+CPM cannot reliably distinguish them from real semantic cliques. The anti-unification of such a spurious clique yields either a tautology (`X = X`) or an over-specific artifact of small-sample variance — exactly the `master_property_too_specific` kill pattern. The DR claims **10× more data (≈4,200 nodes)** is the *minimum* before extracted Master Properties carry epistemic weight. **Substrate consequence:** G22 should be *gated* on substrate-scale, not just resolution parameter. Per `feedback_replicate_seeds.md`, the analog of "replicate across 5+ seeds before claiming significance" is "10×+ scale before claiming a clique."

### E5. G23 — "ΔR² = 0.03 is the failure-rate of heuristic search at high N, not a law of mathematics"
At degree ≤ 44, Mossinghoff's catalog is exhaustive; the `M_min(N)` curve drops sharply because we *actually find* the minimum. Above degree 54, simulated annealing / LLL / genetic algorithms underperform — they *don't find the true minimum*, so the curve artificially flattens. A `1/log N` model fits a flat tail slightly better than a `1/N` model does, and that's the entirety of the 0.03 R² advantage. The DR's resolution: the bootstrap CI on ΔR² will likely include zero — which means the apparent "discovery" of a `1/log N` law is the heuristic-search-failure-rate masquerading as mathematics. **This is the exact pattern of `feedback_false_profundity.md`** — and it's the fourth such candidate in this batch. The bootstrap-CI gate must be hardened into a substrate-level promotion barrier.

---

## Cross-cutting epilogue: what changed for batch 4

This batch (G18, G19, G20, G22, G23) is more pipeline-internal than batches 1–3 — fewer "find new math" plugins, more "verify, audit, and bound the things we've already found." The convergent message is uncompromising:

> **Stop using numerical thresholds as proxies for structural truths. Stop using ledger verdicts as proxies for formal proofs. Stop fitting one regime when the data has two. Stop trusting clusters from sparse graphs. And stop letting the substrate consume meta-epistemic findings as if they were mathematics.**

Each plugin individually argues a narrow version of this. Read together, they're arguing for the same architectural discipline — and the substrate either adopts it once and shares it across all five plugins, or it duplicates the fix five times badly.

---

## Appendix — citation count by source

| Source | G18 | G19 | G20 | G22 | G23 | Cross-DR |
|---|---|---|---|---|---|---|
| Lean 4 / Pantograph / COPRA | • | •• | • | • |  | 4 |
| Aletheia / AlphaEvolve | • | • | • |  |  | 3 |
| Leiden / CPM (Traag) |  |  |  | •• |  | 1 (referenced in G18 Voronoi) |
| Dobrowolski / Voutier / Smyth | • |  |  |  | • | 2 |
| Mossinghoff tables | • |  |  |  | • | 2 |
| Plotkin anti-unification | • |  | • | • |  | 3 |
| MathBERT / MNER (LERT-BiGRU) |  |  | • | • |  | 2 |
| Kohlenbach proof mining |  | • |  |  |  | 1 (operationally shadowed in G18) |
| Bootstrap / BIC / permutation |  |  | • | • | •• | 3 |
| Broken power-law (BPL) |  |  |  | • | •• | 2 |
| Ensemble disagreement (MLIP/ENSO) |  |  | •• |  |  | 1 (shadowed in G22) |
