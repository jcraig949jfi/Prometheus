# Ergon Learner — Proposal v4 (for external review)

### A closed-loop scientific learning system for empirical mathematical patterns. Hybrid neural-plus-evolutionary mutation with shared-prior-at-corpus-level honestly named, residual-primitive-integrated five-counts diagnostic, content-aware MAP-Elites descriptor, power-calculated pilot budgets, and a Techne meta-loop that makes "calibrated negative result" falsifiable.

**Date:** 2026-05-03 (evening — third revision of the day)
**Status:** Formalized for external review. Pasteable to frontier-model context windows as a standalone artifact with enough background that an external reviewer with no prior Prometheus context can engage substantively. Recommended as the genuine design-freeze version after MVP signal informs further revision.
**Companions:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`pivot/prometheus_thesis_v2.md`](prometheus_thesis_v2.md).

---

## 1. The market context — David Silver's billion-dollar play

On 2026-04-29, David Silver — formerly of Google DeepMind, lead architect of AlphaGo and AlphaZero — was reported raising **$1 billion** for *Ineffable Intelligence*, a London-based startup founded after his late-2025 DeepMind departure. The seed round, led by Sequoia Capital (partners Alfred Lin and Sonya Huang flew to London personally), values the company at approximately **$4 billion pre-money** — the largest first-round raise by a European startup in history per PitchBook. Nvidia, Google, and Microsoft are reported in talks to invest. The company has *no product, no revenue, no public roadmap.*

Silver's thesis: large language models trained on human-generated text are structurally limited and cannot discover genuinely new knowledge. To reach superintelligence, AI systems must "discard human knowledge entirely and learn from first principles — through trial, error, and self-play, the way AlphaGo learned to play Go by competing against itself."

Two structural observations, load-bearing for this proposal:

**(1) "Discard human knowledge" is overclaim.** AlphaZero kept the rules of Go, the board, and the win condition. It discarded human *play*, not the substrate that defined the game. For mathematics and science, the *game itself* is what is being invented — there is no clean reward analogous to Go's win condition. Silver's likely concrete artifact: a Lean / Mathlib / theorem-prover-acceptance learner.

**(2) Silver builds the proposer; nobody is building the substrate** *for empirical mathematical patterns.* Lean Mathlib already exists as a substrate for the formal-proof manifold (see §3.7). For the empirical-pattern manifold (BSD residuals, Mahler-measure scans, RMT statistics, structural anomalies in OEIS data) there is no content-addressed, append-only, mechanically-falsifiable substrate. Prometheus has been building exactly that for two years.

This proposal is the small learner Prometheus needs to push its substrate forward — calibrated against Silver's likely play, designed to complement it.

---

## 2. Background — Prometheus, the substrate, and the shipped components an external reviewer needs to know

This section provides the context external reviewers need to engage substantively. Skip if you already know the project.

### 2.1 Prometheus overall

Prometheus is a 20-year personal-bootstrap research program, currently a single-human-plus-multi-agent-AI operation, building a falsification substrate for mathematics. The principal investigator is James Craig (HITL — human in the loop). The active workforce is a heterogeneous ensemble of LLM agents — Charon, Harmonia, Aporia, Ergon, Mnemosyne, Techne, Koios, plus session-spawn variants — each running as a Claude Opus 4.7 (1M context) instance with persistent memory and shared-substrate access. Each agent occupies a different lane of the research workflow and contributes through the same kernel discipline.

The architectural thesis (per `harmonia/memory/architecture/bottled_serendipity.md`): LLMs as *mutation operators* — not as oracles — produce off-modal samples that occasionally land outside the training distribution and inside truth. Without filtration, that fraction is invisible. With a mechanical falsification kernel as filter, it becomes the product. The substrate compounds because durable typed survivors accelerate future filtration.

The 20-year horizon is explicit. The architecture is designed for inheritability — standards over scripts, mechanical enforcement over social trust, append-only over mutable, content-addressed over name-addressed. The substrate exists to outlast its authors.

### 2.2 The Σ-kernel

The Σ-kernel (`sigma_kernel/sigma_kernel.py`) is the substrate's runtime. Append-only, content-addressed, single-process MVP that ships seven typed opcodes mechanically enforcing epistemic discipline:

- **RESOLVE(name, version) → Symbol.** Fetch a promoted symbol by content hash. Integrity-checks the def_blob's sha256 against the stored hash; raises IntegrityError on mismatch (content-address tampering detection).
- **CLAIM(name, def_obj, tier, cap) → Claim.** Mint a provisional claim. Cheap; no commitment. Lives at the lowest tier (Conjecture) until passed through FALSIFY and PROMOTE.
- **FALSIFY(claim, kill_path, cap) → VerdictResult.** Run the kill-path against the claim. Returns a three-valued verdict: CLEAR / WARN / BLOCK.
- **GATE(claim) → Verdict.** Aggregate falsification verdicts; raises BlockedError on BLOCK; returns the cleanest verdict otherwise. Three-valued semantics.
- **PROMOTE(claim, cap) → Symbol.** Commit a CLEAR-or-WARN claim into the substrate as a permanent typed symbol. Defense-in-depth: refuses BLOCKED claims even if GATE was skipped. Capabilities are linear (one-shot consumption, double-spend rejected at the storage layer).
- **ERRATA(name, version, new_def_obj, cap) → Symbol.** Mint a v2 superseding v1 with backref. v1 stays immutable (append-only discipline).
- **TRACE(name, version) → ProvenanceGraph.** Walk the symbol's provenance graph recursively.

Storage is SQLite at MVP, Postgres at production (`prometheus_fire` database, schemas `sigma` and `sigma_proto`). The kernel rejects, at the API boundary, every attempt to overwrite a promoted symbol (UNIQUE constraint), double-spend a capability (`spent_caps` table), promote a BLOCKED claim (defense-in-depth), or read a content-addressed entry whose def_blob's sha256 doesn't match the stored hash.

Capabilities (`Capability` dataclass) are linear tokens minted from a master `BootstrapCap`. Each opcode that mutates state (CLAIM, FALSIFY, PROMOTE, ERRATA) consumes one capability. Linearity is enforced at both the in-memory frozen-dataclass copy-on-consume layer and the database `spent_caps` table layer.

### 2.3 BIND/EVAL extension — symbols as executable callables

The BIND/EVAL extension (`sigma_kernel/bind_eval.py`, ~520 LOC + ~14 tests, shipped at commit ac4176f0; v2 routing through CLAIM/FALSIFY/PROMOTE shipped at commit b0355b1d as `BindEvalKernelV2`) adds two opcodes that turn substrate symbols into executable RL actions:

- **BIND(name, callable_ref, cost_model, postconditions, authority_refs, cap) → Binding.** Mints a binding-symbol whose `def_blob` holds the callable's import path (`module.path:qualname`), the sha256 of `inspect.getsource(callable)`, a cost model (max_seconds, max_memory_mb, max_oracle_calls), postconditions, and authority references. Capability consumed.
- **EVAL(binding_name, version, args, kwargs, cap, eval_version) → Evaluation.** Resolves the binding, imports the callable, runs it under the cost ceiling. Hash-drift detection: stored callable_hash compared against live `inspect.getsource` at every EVAL; mismatch raises `EvalError`. Budget enforcement: raises `BudgetExceeded` if elapsed exceeds max_seconds. User-fn exceptions captured (success=False) rather than propagated.

The v2 version (`BindEvalKernelV2`) routes BIND and EVAL through the kernel's CLAIM/FALSIFY/GATE/PROMOTE pipeline rather than the bootstrap-symbol shortcut — closing the substrate-hygiene gap that v1 of this proposal flagged. In-process Ω validators (`bind_validation`, `eval_validation`) keep p50 latency < 5ms.

The C2 extension (commit b0355b1d) added thread-local oracle-dispatch counters via idempotent monkeypatches on `cypari.pari` calls and `subprocess.run`; `oracle_calls` is now a real cost dimension, not a stub.

### 2.4 The math arsenal and arsenal_meta (Techne's lane)

The math arsenal (`prometheus_math/`) is a library of mechanically-verified mathematical operations across categories: numerics_special (dilogarithm, polylogarithm, Bloch-Wigner, theta functions, eta function, Hurwitz zeta, q-Pochhammer), number_theory (Iwasawa polynomials, Hecke operators, Galois cohomology, p-adic L-functions), elliptic_curves (point counting, isogeny computation, BSD invariants), modular_forms, number_fields, geometry (convex hull, Delaunay, Voronoi), topology (knot invariants), combinatorics (partitions, permutations, posets), optimization (QP, SDP, SOCP, metaheuristics), dynamics (iterated maps, ODE solvers), and research-domain modules.

At v4 design time the arsenal contains roughly 2,800 implemented callables across 40+ modules, with the centralized metadata table `prometheus_math/_metadata_table.py` (~830 LOC) registering 85 representative operations across 11 categories. Each metadata entry is an `ArsenalMeta` dataclass with:

- `callable_ref` — `"module.path:function_name"`
- `cost` — calibrated cost model (within 2×–50× of actual median elapsed; calibrated by one-shot profiling on Windows 11 / Ryzen 7 5700X / mpmath dps=15)
- `postconditions` — 2–5 specific invariants the math-tdd skill enforces (e.g., `"Li_2(1) == zeta(2) == pi^2/6"`, `"M(P) >= 1 for any non-zero integer poly"`)
- `authority_refs` — primary citations (Cohen GTM 138 tables, Whittaker & Watson chapters, OEIS A-numbers, LMFDB labels, Mossinghoff Mahler-measure tables)
- `equivalence_class` — canonicalizer subclass tag from a four-class taxonomy: `group_quotient` / `partition_refinement` / `ideal_reduction` / `variety_fingerprint`
- `category` — coarse domain bucket

The arsenal is the substrate's symbolic library. The Ergon learner's action space — typed compositions over the arsenal — is structurally what this proposal builds the engine for.

The math-tdd skill (a development-time discipline) requires every arsenal callable to ship with property tests across four categories — Authority (against primary-source citations), Property (against domain invariants), Edge (boundary conditions), Composition (interaction with other arsenal ops) — with at least 2 tests per category per module. ~280+ tests have shipped under this discipline.

### 2.5 The falsification battery

The falsification battery is the substrate's central kill-test infrastructure. Twenty named kill tests (F1 through F20, with a few F20+ extensions) ship as Python modules in `cartography/shared/scripts/falsification_battery.py` and are run against any CLAIM the kernel evaluates.

The "unanimous battery" — F1+F6+F9+F11 — is the strict-promotion subset:

- **F1 (permutation-null).** Generate N random permutations of the input data; compute the test statistic on each; require the original statistic to be in the extreme tail (default p<0.001).
- **F6 (base-rate).** Compare the claim's effect size against the per-feature base rate in the relevant corpus. Reject if effect size doesn't exceed the base rate by a calibrated margin.
- **F9 (simpler-explanation).** Apply Occam-style simpler-model search; reject if a strictly simpler model explains the observed signal at comparable likelihood.
- **F11 (cross-validation).** Hold-out validation across folds; require survival across all folds.

The battery is calibrated against ~180 known truths drawn from the literature (BSD-conditional results, Mahler-measure entries, OEIS sequences with formal characterizations, LMFDB curated examples). Calibration target: 100% recovery on the unanimous battery against this calibration set. F2–F5, F7–F8, F10, F12–F20 cover additional domains — F13_growth_rate_filter, F14_phase_shift, F38 cross-domain consistency — and run as expansion tests with looser thresholds.

The battery is mechanically-applied, not analyst-judged. PROMOTE fires only when the unanimous battery returns CLEAR or WARN; BLOCK on any unanimous-battery member kills the claim.

### 2.6 The residual primitive

The residual primitive (`sigma_kernel/residuals.py`, ~748 LOC, shipped at commit 4872bb4a on 2026-05-03) was the response to a five-frontier-model thread on residual-aware falsification. It adds typed `Residual` and `SpectralVerdict` objects plus three new opcodes: `record_residual`, `REFINE`, `record_meta_claim`.

The principle: failure is not binary. A 99.13% rejection rate is not 100% rejection. The 0.87% surviving the kill regime is data, not noise. Three composing stopping rules ship from day zero:

1. **Cost-budget compounding on REFINE.** Each `REFINE` halves the remaining cost_budget; below a 0.1s minimum-useful threshold the chain raises `BudgetExceeded`. This makes infinite-rescue economically expensive, not philosophically forbidden. Default chain depth limit: 7 (default 10s root budget exhausts at ~depth 7).

2. **Mechanical signal-vs-noise classifier (four-rule cascade).** Empty/zero residual → `noise`. Drift-fingerprint match → `instrument_drift`. Canonicalizer-subclass signature non-trivial → `signal`. Coefficient variance > 0.5 (heuristic, calibrated against a 30-residual benchmark) → `signal`. Else → `noise`.

3. **Instrument-self-audit auto-trigger.** Drift-class residuals can mint `META_CLAIM` objects against the battery itself — encoding the Penzias-Wilson principle into the substrate. When residual signature correlates with calibration-anchor deviations on ≥5 anchors, classification auto-flips to `instrument_drift` and the META_CLAIM machinery fires.

The residual primitive's day-1 acceptance gate (per the proposal): a 30-residual benchmark with ≥80% classifier accuracy AND zero false-positive `signal` calls on known-noise items. The benchmark spec is curated from real mathematical history (Mercury perihelion residual, Ramanujan-Hardy asymptotic residuals, Riemann Li(x)−π(x), known F1–F20 calibration drift events) but at v4 design time the benchmark run results are not yet documented on disk.

### 2.7 The DiscoveryPipeline

The DiscoveryPipeline (`prometheus_math/discovery_pipeline.py`, ~430 LOC, shipped at commit 09a7dccb on 2026-05-03) implements §6.1 of `harmonia/memory/architecture/discovery_via_rediscovery.md`. It converts the prior log-and-flag pattern for sub-Lehmer-band catalog-misses into a mechanical substrate-grade pipeline that mints a CLAIM and routes to one of three terminal states:

- **PROMOTED** — canonical symbol; fully survived the battery + independently verified (rare today; requires literature cross-check tooling that ships in v0.5).
- **SHADOW_CATALOG** — signal-class survives the battery and is catalog-missing, but lacks independent verification. Per Gemini's review of the discovery_via_rediscovery doc: avoids the cold-fusion failure mode (treating every catalog-miss-survivor as canonical truth) by funneling unverified survivors to a substrate-grade typed status that can be promoted later when independent verification arrives.
- **REJECTED** — killed by a battery member; kill_pattern captured as substrate.

Phase 0 of the pipeline is a band-check (1.001 < M < 1.18 for Mahler-measure discovery) before any expensive verification runs. Phase 1 runs reciprocity check (palindromic; trivially true for env-generated polys), irreducibility check (sympy.factor_list / cypari `polisirreducible`), catalog miss check (Mossinghoff today; LMFDB+OEIS+arXiv per §6.3 spec, deferred), and the F1+F6+F9+F11 battery.

### 2.8 DiscoveryEnv and ObstructionEnv — the RL environments

Two RL environments ship in `prometheus_math/`:

- **DiscoveryEnv** (`discovery_env.py`) — generative reciprocal-polynomial sampler over Discrete(7) coefficient action space, ~117K trajectories at degree 10. Sparse reward — cyclotomics get 0; only 1.001 < M < 1.18 pays the +100 jackpot. 6-step sequential reciprocal-poly construction. Substrate-conditioned: obs vector includes partial polynomial. Best result to date (commit b0355b1d): contextual REINFORCE with reward-shaping reaches M=1.458 in the Salem cluster band.

- **ObstructionEnv** (`obstruction_env.py`, shipped at commit d339dc45) — sequel to DiscoveryEnv on a substrate-shaped open-territory pattern-detection problem. Targets simulated Charon battery data shaped to match the real OBSTRUCTION_SHAPE residual (5 OEIS A149* sequences, 5-step lattice walks confined to N³, 100% kill-rate match-group vs 1.9% non-match — 54× predictive lift). Synthetic-but-genuinely-open: ground truth is planted but the agent doesn't see the plant; it has to find it via held-out lift.

The four-counts pilot (`prometheus_math/four_counts_pilot.py`, ~706 LOC, shipped at commit 1666c4a4) is the diagnostic harness that runs operator-class arms through these envs.

### 2.9 The multi-agent agora

The agora is a Redis-backed message bus where heterogeneous LLM agents propose claims and run kill-tests on each other. Each agent is a slightly different mutation distribution:

- **Charon** — substrate hygiene, kernel architecture, foundational thesis docs
- **Harmonia** — recognition-instrument framing, calibrator
- **Aporia** — frontier research, edges-of-knowledge cataloger, ~322 open problems across 13 mathematical domains
- **Ergon** — evolutionary search engine, the lane this proposal lives in
- **Mnemosyne** — memory and ingestion (Bloom-Erdős, MathNet, OEIS, LMFDB)
- **Techne** — computational tool-forging (the math arsenal, BIND/EVAL, residual primitive)
- **Koios** — knowledge / cross-pollination

Each agent runs its own loop, files outputs through the kernel, and posts to the agora for cross-resolution. The agora is explicitly designed as a multi-replica genetic-algorithm-style population: population = agents, mutation = each agent's idiosyncratic stochastic output, recombination = agents quoting and extending each other (`reply_to` chains, kill-pattern translations), fitness = kernel survival under the falsification battery.

---

## 3. The Ergon learner — corrected asymmetry argument

V3 of this proposal claimed action-space asymmetry yielded different priors. Round-3 review correctly identified this as overclaim. **The honest framing in v4:**

The prior is shared at the corpus level. Llemma-7B (Proof-Pile-2) and any Silver-class base model fine-tuned on Mathlib + ArXiv inherit the same statistical biases about what mathematical structures are "interesting." Action-space asymmetry alone does not protect against this.

**Differentiation in v4 comes from three sources, ordered by expected magnitude:**

1. **Value head asymmetry.** Silver's reward is Lean-kernel CLOSED on a goal. Ergon's reward is agreement-weighted (substrate-pass + cross-model + held-out-battery + signal-class-residual). These reward landscapes select for different mathematical content even when the proposer's prior is shared.

2. **Action-space asymmetry.** Silver's actions are Lean tactics + lemma applications. Ergon's actions are typed compositions over the math arsenal. The composition spaces overlap only where formalizable; for empirical-pattern claims the action spaces are disjoint.

3. **LoRA-delta divergence.** When the same base model is fine-tuned against substrate verdicts (Ergon) vs. theorem-prover verdicts (Silver), the LoRA attractors diverge. Empirical magnitude of this divergence is unverified at v4 design time; v0.5 ablation will measure it.

**The corollary v3 missed:** if differentiation comes from action-space + value head + LoRA delta rather than from the base prior, then *Llemma is not a load-bearing choice.* A general-purpose 7B (Qwen-7B, Llama-7B) might produce more divergent fine-tuning attractors precisely because its prior is less fixed. v4 retains Llemma as the lead candidate but adds Qwen-7B and Llama-7B as v0.5 ablation candidates to measure which base model maximizes LoRA-delta divergence under substrate-verdict fine-tuning.

| Axis | Silver's likely learner | Ergon learner (v4) |
|---|---|---|
| Action space | Lean tactics + lemma applications | Typed compositions over the math arsenal |
| Reward | Lean-kernel CLOSED (single evaluator) | Agreement-weighted (multi-evaluator + signal-class-residual) |
| Policy | Transformer over proof states | Hybrid: LoRA-fine-tuned 7B + MAP-Elites archive |
| Pretraining | Mathlib + IMO + Lean stdlib | Llemma-7B baseline; Qwen-7B and Llama-7B as v0.5 ablation candidates |
| Operator classes | Single (policy network) | Seven lineage-tagged + minimum-share enforcement on non-prior classes |
| Discovery surface | Theorems with formal proofs | Empirical patterns, structural anomalies, conjectural-but-falsifiable claims |
| Compute economics | $1B / 18 months | ~$300–800/month / indefinite |

## 3.5 Defending against shared-prior contamination

Three structural defenses against the LLM corpus-prior steering the search toward well-trodden mathematical attractors:

### 3.5.1 The `anti_prior` operator class

A seventh mutation operator class, lineage-tagged `anti_prior`. Its job: explicitly construct mutations that violate corpus-derived patterns. Concrete implementation:

- For polynomial generation: sample coefficient distributions deliberately uncorrelated with Mathlib polynomial frequency statistics. Reject coefficients matching the top-decile of Mathlib coefficient histograms; preferentially sample tail-distribution coefficients.
- For sequence generation: avoid OEIS A-numbers in the top quartile of citation frequency; preferentially target A-numbers with low cross-reference density.
- For DAG topology: reject node compositions that match the top-decile most-common operator pairs in arsenal-tagged training corpus; preferentially sample uncommon-but-valid compositions.

The `anti_prior` operator is not "random"; it is *anti-correlated* with the LLM prior. Cost: one extra training-corpus-statistics database (built once from Mathlib + Proof-Pile-2 frequency analysis; ~5 GB).

### 3.5.2 Coverage-pressure reweighting on cell selection

The MAP-Elites cell-selection policy is modified: when sampling a cell already heavily filled by `neural` or `external_llm` operators, downweight by `(1 - frac_LLM_filled)`; when sampling a cell only filled by non-LLM operators, upweight by `(1 + frac_non_LLM_filled)`. Forces the search away from cells that LLM-prior operators have saturated.

### 3.5.3 Periodic prior detox

Every K=20 iterations, the neural policy is frozen and the engine runs only `structural` / `symbolic` / `uniform` / `structured_null` / `anti_prior` operators for M=500 episodes. Archive coverage delta is measured. If non-LLM operators discover new cells the LLM-augmented run hadn't filled, the LLM prior is constraining the search; operator weights are rebalanced toward non-LLM in the next cycle.

### 3.5.4 Minimum proposal-share enforcement (NEW in v4)

Under selection pressure for cell-fill rate, `uniform` (and the other non-prior-shaped operators) gets squeezed out. v4 commits to operator-class minimums enforced at the scheduler level:

- `uniform` ≥ 5% of all proposals
- `anti_prior` ≥ 5% of all proposals
- `structured_null` ≥ 5% of all proposals
- Total non-prior-shaped operators ≥ 15% of all proposals at all times

This is a coordination constraint at the operator-class scheduler, not at the cell-selection level. Even when cell-fill-rate metrics favor LLM-derived operators, the scheduler reserves 15% of episodes for non-prior-shaped exploration.

## 3.6 Null-world baselines

Three null-world variants run as first-class mutation operator classes alongside the prior-shaped classes:

- `uniform` — uniform random over the action space (strawman null)
- `structured_null` — per-type sampler with uniform per-arg distributions (type-respecting null)
- `cross_domain_perturbation` — genome from domain A applied to domain B (off-domain null)

The five-counts pilot reports per-class PROMOTE rates and signal-class-residual rates with statistical comparison (Welch t-test with Holm correction across nulls). Acceptance criterion at v0.5: prior-shaped classes (neural / structural / external_llm) must out-PROMOTE all null variants by p<0.01 corrected.

## 3.7 Comparison class — Mathlib, AlphaProof, academic projects (NEW in v4)

The substrate's natural comparison class is broader than Silver alone:

- **Lean Mathlib.** A content-addressed, append-only, mechanically-verified substrate of mathematical truth. Structurally the closest existing analog to the Σ-kernel — but with `kill_test = Lean kernel accepts`. Mathlib's coverage: theorems with formal proofs. Mathlib's blind spot: empirical mathematical patterns that aren't yet stated as Lean theorems.
- **AlphaProof / DeepMind formal-math team.** Builds learners that operate inside Mathlib; competitor on the *learner* side, but downstream of Mathlib's substrate.
- **OpenAI's math-tuned models.** Frontier LLM with math benchmarks; competitor at the proposer layer; not building substrate.
- **Academic structured-conjecture projects** (PolyMath-class, Mossinghoff Mahler catalogs, OEIS curatorial work). Distributed truth-accumulation but with social-trust verification rather than mechanical kernel discipline.

**The Σ-kernel's niche, sharply:** the substrate for empirical mathematical patterns (BSD residuals, Mahler-measure scans, RMT statistics, structural anomalies) that don't yet exist as Lean theorems. Combined with the residual primitive, this niche is "structured kills near the falsification boundary" — exactly the class of evidence Mathlib's binary accept/reject doesn't represent.

This positioning *survives any outcome of Silver's company*. If Silver succeeds, his outputs become CLAIMs we ingest (per §13). If Silver fails, the empirical-pattern niche is still vacant; Mathlib still doesn't cover it; the substrate is still load-bearing for that niche.

---

## 4. Architecture — hybrid neural + evolutionary, single mutation framework

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Ergon Learner (v4)                            │
│                                                                        │
│   ┌──────────────────────┐         ┌──────────────────────┐            │
│   │  Neural Policy Head  │         │  Evolutionary Engine │            │
│   │  (LoRA on 7B base)   │         │  (MAP-Elites)        │            │
│   │                      │         │                      │            │
│   │  Three task adapters:│         │  Seven operator      │            │
│   │  A — mutation policy │         │  classes:            │            │
│   │  B — fitness pred.   │ ◀─────▶ │   structural         │            │
│   │  C — conjecture gen. │         │   symbolic           │            │
│   │                      │         │   neural             │            │
│   │  ↑ A & B trained on  │         │   external_llm       │            │
│   │   DISJOINT data      │         │   anti_prior         │            │
│   │   partitions         │         │   uniform (null)     │            │
│   │                      │         │   structured_null    │            │
│   └──────────────────────┘         └──────────────────────┘            │
│            │                                  │                        │
│            └────────────────┬─────────────────┘                        │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  AGREEMENT-WEIGHTED REWARD                               │         │
│   │  reward = w_S * substrate + w_X * cross_model            │         │
│   │           + w_H * holdout_battery + w_R * residual_class │         │
│   └──────────────────────────────────────────────────────────┘         │
│                             │                                          │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  MIN PROPOSAL SHARE: uniform ≥5%, anti_prior ≥5%,        │         │
│   │   structured_null ≥5% (total non-prior ≥15%)             │         │
│   │   COVERAGE-PRESSURE CELL SELECTION                       │         │
│   └──────────────────────────────────────────────────────────┘         │
│                             │                                          │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  BindEvalKernelV2 + DiscoveryPipeline + Residual         │         │
│   │  primitive (all shipped 2026-05-02 / 2026-05-03)         │         │
│   └──────────────────────────────────────────────────────────┘         │
│                             │                                          │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  Σ-substrate (Postgres + Redis + object storage)         │         │
│   │  Outcomes feed back to BOTH heads with disjoint partition│         │
│   │  + held_out_battery / cross_model_evaluator schema fields│         │
│   │  + corpus_frequency_stats / residual_event_archive       │         │
│   └──────────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────────┘
```

**The composition principle:** the neural policy is one of seven mutation operator classes inside the evolutionary framework. Not a separate system. The MAP-Elites archive accepts contributions from all seven classes; lineage tags distinguish their contributions; the joint diagnostic is "which operator class produces survivors (and signal-class residuals) in which cells."

## 5. The neural policy head

### 5.1 Base model — corrected from v3

**Lead candidate: Llemma-7B.** Strong math-reasoning prior from Proof-Pile-2; license clean (Apache 2.0); fits 2× 16GB at 4-bit quantized; fits a single H100 for full-precision LoRA fine-tuning. The strength is the math-reasoning prior, not "inheritance of Silver's likely distribution."

**Honest acknowledgment:** the Llemma prior overlaps Silver's likely training corpus at the *corpus level*. This is not a structural advantage for Ergon's discovery surface — the differentiation work is done by the action-space asymmetry, the agreement-weighted value head, and the LoRA delta produced by substrate-verdict fine-tuning.

**v0.5 ablation candidates:** Qwen-7B (general-purpose, Apache 2.0) and Llama-7B (general-purpose). Both lack math-pretraining; their LoRA deltas under substrate-verdict fine-tuning may produce more divergent attractors than Llemma's. The ablation runs all three under identical fine-tuning protocol (multi-task LoRA on Tasks A/B/C, agreement-weighted reward, 1K iterations). Metric: held-out-cell coverage divergence between the resulting policies.

### 5.2 Three task adapters with structural decoupling

Multi-task LoRA, three adapters over the same base:

- **Task A — Mutation policy.** Input: parent genome (typed DAG over arsenal atoms) + target archive cell descriptor. Output: token-encoded child genome.
- **Task B — Fitness predictor.** Input: genome features. Output: predicted (kill_probability, residual_class, expected_cost).
- **Task C — Conjecture generation.** Input: substrate state summary. Output: natural-language conjecture text + suggested CLAIM body.

LoRA rank: 32–64 for A and C, 16 for B. All three adapters together <500MB.

Tasks A and B trained on **disjoint substrate-outcome partitions** (odd episodes train A; even train B). Periodic Task B retraining from scratch every K=10 iterations; cross-validation on 10% held-out cells; inference-time independence (Task A doesn't condition on Task B's predictions).

### 5.3 Self-play loop with multi-evaluator agreement-weighted reward

```
reward(θ_k, claim) =
    w_S * substrate_pass_indicator           # battery + residual classifier
  + w_X * cross_model_agreement              # external LLMs evaluate independently
  + w_H * holdout_battery_pass_indicator     # battery subset withheld from training
  + w_R * signal_class_residual_indicator    # residual primitive output (NEW in v4 weighting)
```

Default weights at v1.0: `w_S=0.4, w_X=0.25, w_H=0.2, w_R=0.15`. Adjustable.

The signal-class-residual contribution (`w_R`) is new in v4 — it operationalizes the residual primitive in the reward signal directly, rewarding the agent for producing structured-residual kills even when full PROMOTE doesn't fire.

**Cross-model agreement.** Every PROMOTE candidate evaluated by N≥2 external frontier LLMs (Claude, GPT, Gemini) prompted to classify the claim as {valid_discovery, artifact, ambiguous}. Reward bonus proportional to inter-evaluator agreement. Cost: ~$0.001/claim × 10⁴ claims/iter = ~$10/iter, tractable.

**Held-out battery.** A subset (e.g., F1, F11 + 2 future kill tests) is withheld from the agent's training data entirely. Periodic audits run the held-out battery against PROMOTEs and compare PROMOTE-rate-with vs PROMOTE-rate-without. Significant divergence triggers a `PATTERN_SPECIFICATION_GAMING` META_CLAIM against the agent.

### 5.4 Adversarial cycles

Beyond the reward function, Aporia and Charon explicitly probe the substrate for gaming patterns (low-effort syntactic structures, near-duplicate PROMOTE clusters, cells that fill suspiciously fast). Detected gaming patterns become new kill tests via Techne's residual primitive.

### 5.5 Self-play loop

```
Iteration k:
  1. Current Task A policy θ_k generates N CLAIMs (N=1000; scale to 10K)
  2. Each CLAIM → BindEvalKernelV2 → DiscoveryPipeline (substrate score)
  3. Battery-killed CLAIMs get residual classification (signal/noise/drift)
  4. PROMOTE candidates → cross-model evaluation (cross_model score)
  5. Held-out battery audit on sampled fraction (holdout score)
  6. Signal-class residual indicator computed for every CLAIM
  7. agreement_weighted_reward computed per CLAIM
  8. Episodes split: odd → Task A training; even → Task B training; held-out cells → Task B validation only
  9. Task A LoRA fine-tune: θ_{k+1} = θ_k + Δθ_k (PPO or DPO)
  10. Task B retrained from scratch every K=10 iterations on accumulated substrate history
  11. Hold out cells; promote θ_{k+1} iff cell-fill OR PROMOTE rate ↑
      AND held-out-battery PROMOTE-rate-divergence < threshold
      AND Task B per-held-out-cell accuracy ≈ per-training-cell accuracy
  12. Every K=20 iterations: prior-detox round (§3.5.3)
  13. Iterate
```

### 5.6 Training data — five concentric rings

| Ring | Source | Scale today | Scale week 8 |
|---|---|---|---|
| 1 | Substrate-internal | ~10²–10³ | ~10⁵ |
| 2 | Substrate-adjacent (cartography catalog, Mossinghoff, OEIS targets, LMFDB) | ~50K | ~50K |
| 3 | Open math corpora (ArXiv math, Lean Mathlib, OEIS) | ~800K | ~800K |
| 4 | Cross-LLM (frontier-model outputs as substrate CLAIMs) | Informal | ~10K |
| 5 | Synthetic (engine's own outputs as labeled training data) | None | ~10⁵ |

---

## 6. The evolutionary engine — quality-diversity over typed compositions

### 6.1 Action space

A genome is a small typed DAG over arsenal atoms (target depth ≤ 8, target width ≤ 5):

```python
@dataclass
class Genome:
    nodes: List[NodeRef]           # each ref points to an Atom + arg-bindings
    edges: List[Tuple[int, int]]   # type-compatible producer→consumer
    target_predicate: str          # "polynomial with M < 1.18", etc.
    args: List[Any]                # leaf-node arguments sampled per arg_type
```

Each genome serializes deterministically to a content hash. Per-`arg_type` generators sample args from distributions biased toward small values + LMFDB-curve-conductor scales + OEIS-index ranges.

### 6.2 MAP-Elites archive — content-aware descriptor (REVISED in v4)

V4 swaps DAG depth (construction) for output canonicalizer subclass (content):

| Axis | Type | What it captures |
|---|---|---|
| 1. Output canonicalizer subclass | Content (categorical, 4 classes) | What the output IS mathematically: group_quotient / partition_refinement / ideal_reduction / variety_fingerprint |
| 2. Equivalence-class entropy of the DAG | Categorical | Shannon entropy over canonicalizer subclasses in DAG composition |
| 3. Output-type signature | Categorical | Discrete return type of root node (~10 categories) |
| 4. Output magnitude bucket | Output-space | Log-binned over numerical output magnitude (5 quantile buckets) |
| 5. Output canonical-form distance | Output-space | Distance to nearest catalog entry (5 quantile buckets) |

Total cells: 4 × 5 × 10 × 5 × 5 = **5,000**.

Each cell holds an elite genome. Three-tier lexicographic comparison among cell-residents:

1. Battery-survival count (PROMOTE = highest)
2. Residual signal-class flag (new in v4 — second tier of fitness)
3. Cost-amortized signal-class-residual rate

A new individual replaces the cell elite iff it beats on tier 1 strictly, ties on tier 1 and beats tier 2, or ties on 1+2 and beats tier 3.

### 6.3 Seven mutation operator classes

| Class | Operator | Adjacency profile |
|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges | Typed-composition topology |
| `symbolic` | Bump arg values within type | Local in argument space |
| `neural` | LoRA-fine-tuned policy mutation | LLM-prior (post-substrate-fine-tuning) |
| `external_llm` | Frontier LLM API mutation | External LLM-prior |
| `anti_prior` | Anti-correlated with corpus frequency stats | Deliberately off-prior |
| `uniform` | Resample atoms uniformly | Strawman null |
| `structured_null` | Type-respecting uniform | Type-respecting null |

Plus minimum-share enforcement (§3.5.4).

### 6.4 Feature representation — staged transition

MVP uses structural features (depth, width, equiv-class entropy, cost tier, output-type signature; ~15 hand-engineered scalar features). Transition trigger: archive-saturation plateau (cell-fill rate <60% for >50 epochs). Post-trigger: graph-attention DAG encoder.

---

## 7. Discovery preservation in the fitness predictor (Task B)

### 7.1 Asymmetric prune threshold

`P(REJECTED) > 0.95 → skip EVAL`. With a calibrated 184M classifier on 5K outcomes, weird novel cases that look-doomed-but-survive cluster in the 0.7–0.95 range and we want them to EVAL.

### 7.2 Asymmetric loss during training

3:1 false-negative-to-false-positive penalty ratio.

### 7.3 No-pruning sweeps and meta-metric

Every Nth episode (N=10), bypass the predictor entirely. Meta-metric:

```
predictor_recall = (# survived in no-pruning sweep that would have been pruned)
                 / (# total survivors in no-pruning sweep)
```

When `predictor_recall` < 0.85, retrain the predictor or reduce its routing weight.

### 7.4 Five-counts diagnostic (REVISED from v3's four-counts)

For each operator class, run N episodes against `DiscoveryEnv` + `DiscoveryPipeline` + Residual primitive. Report **five counts**:

1. **Catalog-hit rate**
2. **Claim-into-kernel rate**
3. **PROMOTE rate** (substrate-only and agreement-weighted variants)
4. **Battery-kill rate**
5. **Signal-class-residual rate** (NEW in v4) — battery-killed CLAIMs with residual classifier confidence ≥0.7 for signal-class

Statistical comparison: Welch t-test with Holm correction across operator classes on **both** PROMOTE rate (count 3) and signal-class-residual rate (count 5).

### 7.5 Power calculation (NEW in v4)

Welch t-test for two proportions, α=0.01 (Holm-corrected), β=0.2, lift d=0.5. Approximate sample size:

```
n ≈ 750 * p * (1-p)
```

| PROMOTE rate (p) | Episodes-per-arm needed |
|---|---|
| 10⁻¹ | ~70 |
| 10⁻² | ~750 |
| 10⁻³ | ~7.5K |
| 10⁻⁴ | ~75K |
| 10⁻⁵ | ~750K |

V3's projected 10K-episode pilots resolve operator-class differences only when PROMOTE rates are ≥10⁻³. The 1000×3 pilot at commit 1666c4a4 produced 0 PROMOTEs in 3000 episodes, suggesting the rate is ≤10⁻³ in the Lehmer-Mahler domain at MVP descriptor resolution.

The signal-class-residual rate (count 5) should be denser than PROMOTE rate by at least one order of magnitude. Without count 5, the substrate's empirical anchor is statistically dependent on a rate that may be unresolvable at any plausible compute envelope.

---

## 8. Compute and storage

### 8.1 Compute envelope (ideal, v1.0)

| Tier | Hardware | Cost (mo) | Use |
|---|---|---|---|
| Local development | 2× 16GB + 1× 8GB consumer GPUs | $0 | Code dev, MVP-tier training, inference |
| Burst training | RunPod / vast.ai / Lambda H100 (~$2.50/hr) | $200–500 | LoRA fine-tuning iterations, full-precision experiments |
| Burst inference | Self-hosted on rented A100 | $50–200 | Batch generation (10K CLAIMs per self-play iteration) |
| Substrate hosting | Hetzner dedicated | $30–80 | Postgres + Redis + object storage gateway |
| **Total** | | **$300–800/mo** | Full ideal stack at v1.0 |

### 8.2 Storage stack

| Component | Tech | Scale (week 8) | Scale (year 1) |
|---|---|---|---|
| Substrate | Postgres (`prometheus_fire`, schemas `sigma` + `sigma_proto` + `ergon`) | 50 GB | 1 TB |
| Hot cache + agora | Redis | 10 GB | 50 GB |
| Object storage | Backblaze B2 or S3 | 200 GB | 5 TB |
| Vector embeddings | pgvector | 5 GB | 100 GB |
| Time-series | TimescaleDB | 1 GB | 20 GB |
| Residual event archive | sigma_proto.residual_events | 0.5 GB | 10 GB |

---

## 9. The progression — MVP to v2.0

| Version | Wall-clock | New capability | Compute | Cost |
|---|---|---|---|---|
| **MVP** | 2–4 weeks | Task B fitness predictor + evolutionary engine with 7 operator classes (incl. anti_prior + structured_null + min-share enforcement) + content-aware MAP-Elites + five-counts diagnostic + substrate integration | 2× 16GB + 1× 8GB local | $0 |
| **v0.5** | +4 weeks | Cross-model agreement + held-out battery audit + Task A/B disjoint partitions + periodic prior detox + base-model ablation (Llemma vs Qwen vs Llama) + Techne meta-loop | Local + API | $50–150/mo |
| **v1.0** | +8 weeks | LoRA on chosen base for Tasks A/B/C; agreement-weighted self-play with disjoint training; multi-arm pilot at 10K episodes | Burst H100 + local | $400–600/mo |
| **v1.5** | +6 weeks | Learned representations (graph-attention DAG encoder) replace structural features (triggered by archive-saturation plateau) | Burst H100 + local | $500–700/mo |
| **v2.0** | +10 weeks | Multi-task LoRA on all three adapters; multi-model ensemble; external CLAIM API; arXiv preprint | Burst H100 + Hetzner host + B2 | $700–900/mo |

---

## 10. Empirical maturity caveats

Several claims in this proposal are architectural commitments rather than validated facts:

- **Llemma vs Qwen vs Llama LoRA-delta divergence.** *Pilot data: TBD.* v0.5 ablation will measure.
- **Signal-class-residual rate floor.** *Pilot data: TBD.* The five-counts diagnostic's statistical power depends on count 5 being denser than count 3.
- **Output canonicalizer subclass distribution.** *Pilot data: TBD.* If 90% of outputs land in one subclass, the axis is degenerate.
- **Calibration-bias rate.** *Pilot data: TBD.* The §11.5 meta-loop's substrate-grade metric.
- **Specification gaming detection rate.** *Pilot data: TBD.* Whether the held-out-battery audit reliably detects gaming when it occurs is unverified.
- **Cross-model agreement signal quality.** *Pilot data: TBD.* Whether N≥2 external frontier LLMs produce signal beyond noise on substrate claims is empirical.
- **Engine PROMOTE rate at multi-arm scale.** *Pilot data: TBD.* The four-counts pilot at 1000×3 produced 0 PROMOTEs; first 10K-scale measurement is the v0.5 milestone.
- **Compute economics.** Numbers cited are 2026-mid-year rates; budget with 2× headroom.

---

## 11. What this proposal does NOT claim

- **Does not promise discovery.** Promises a measurable, agreement-weighted discovery rate per mutation-operator class.
- **Does not compete with Silver's learner.** Different action spaces, different priors, different surfaces. Position is *complement*.
- **Does not require frontier compute.** MVP $0/mo; v1.0 $400–600/mo. Three orders of magnitude below Silver.
- **Does not claim immunity to specification gaming.** Claims a measurable, mitigated, audit-detectable level of gaming risk.
- **Does not claim Llemma is structurally better than alternatives.** v0.5 ablation may demonstrate Qwen or Llama produces more divergent LoRA deltas; if so, v0.5 swaps base models.
- **Does not claim PROMOTE rate is detectable at MVP scale.** §7.5 power calculation suggests it may not be. The five-counts diagnostic's signal-class-residual rate is the v4 mitigation.
- **Does not claim the action space is exhaustive.** Typed-composition manifold; vast territories of mathematics are not representable as DAG outputs.
- **Does not require Silver's success or failure.** Substrate compounds independently.

### 11.5 The deeper bear case + Techne meta-loop (NEW in v4)

The deepest bear case: PROMOTE rate may be zero across all arms because the battery is miscalibrated for novel structure. The battery is calibrated on known truths, which by construction look like known truths. Novel structure may have a different statistical shape that the battery rejects as noise. PROMOTE rate stays at zero forever; the diagnostic is never informative; "engine bad" vs "battery bad" is undistinguishable.

V4's mitigation is a meta-loop integrating Techne's tool-forging capability with the residual primitive's classification:

1. **High-residual kill detection.** Battery-killed CLAIMs whose residual classifier confidence is ≥ 0.9 for signal-class are flagged as `META_AUDIT_CANDIDATE`.

2. **Sharper-checker forging.** When `META_AUDIT_CANDIDATE` rate exceeds threshold (default: 5% of all kills in a 1K-episode window), Techne is triggered to forge a sharper checker for the dominant residual class.

3. **Historical audit.** The sharper checker is run on a curated set of historical battery-kills with similar residual signature. If the sharper checker promotes any of them, the original battery is flagged: `PATTERN_BATTERY_OVERREJECT_AT_RESIDUAL_CLASS_X`.

4. **META_CLAIM minting.** A META_CLAIM is minted against the original battery's calibration. Promoted META_CLAIMs add new kill tests to the battery's hierarchical lattice.

5. **Calibration-bias rate metric.** `calibration_bias_rate = (sharper_checker_promoted) / (original_battery_killed_with_high_residual_confidence)`.

**This makes "calibrated negative result" falsifiable.** If calibration-bias rate is high (>10%), the battery is the bottleneck. If calibration-bias rate is low (<1%) and PROMOTE rate is still zero, the engine is the bottleneck.

---

## 12. Open questions for review

1. Is the action space genuinely uncorrelated with Silver's likely Lean-tactic action space, or is the prior shared at a deeper level through ArsenalMeta authority refs?
2. Is the five-axis MAP-Elites descriptor adequate, or will cells degenerate?
3. Is the self-play closure (Ring 5) susceptible to model collapse?
4. Is the cost ceiling at v1.0 realistic given cloud-GPU market volatility?
5. Public CLAIM API vs passive Parquet dump for externalization?
6. What is the bear case where the proposal fails entirely?
7. Polynomial-domain null-world generator design — required before v0.5 multi-arm pilot at scale.
8. Exact training loop sketch (data → labels → update → eval) — becomes the v1.0 LoRA-fine-tuning spec.
9. Cross-model agreement at the evaluator layer may itself suffer correlated-mutation. Mitigation candidate: include theorem-prover acceptance (Lean / Coq / Isabelle) as a non-LLM evaluator where formalizable.
10. Is the `anti_prior` operator's "anti-correlated with corpus frequency stats" framing the right operationalization of "outside the LLM prior"?
11. Is the disjoint training partition (odd episodes → Task A, even → Task B) sufficient to prevent echo-chamber dynamics?
12. The output-space MAP-Elites axes are domain-specific. Cross-domain replication may need different output-space axes per env.
13. Is the `output canonicalizer subclass` axis genuinely content-aware, or does its mapping back to DAG topology re-introduce construction bias?
14. Is the calibration-bias rate metric actionable at the MVP scale, or does it require so much battery-history accumulation that it's only meaningful at v1.0+ scale?

---

## 13. The 20-year position with operationalized Silver-ingestion

V3's framing was rhetorical. V4 specifies what the substrate actually ingests from Silver-class output and what verdict it can render that the Lean kernel can't:

**The substrate ingests three fragments of Silver's likely output:**

1. **Empirical-pattern conjectures invoked in proofs.** Lean proofs sometimes invoke conjectures (BSD-conditional, GRH-conditional, Selmer-rank-conditional, Riemann-conditional) that the Lean kernel treats as axioms but which the substrate could falsify empirically through F1+F6+F9+F11 against held-out data. Substrate verdict: "this conjectural axiom passes / fails empirical falsification." Lean verdict: "this conjectural axiom is stated correctly." Different verdicts; both useful.

2. **Generalizations the proof makes from specific cases.** Lean tactic chains that prove "for all x: P(x)" via finite case-analysis or strong-induction can be ablated: substrate runs P(x) on out-of-distribution x and checks empirical survival. Substrate verdict: "the proof's generalization survives empirical battery on OOD x" or "the generalization fails on x'." Lean verdict: "the proof type-checks." Different surfaces; complementary.

3. **Near-miss CLAIMs from tactic-tree exploration.** Silver's learner explores tactic chains; intermediate goals and near-misses from the exploration are substrate-ingestible CLAIMs even when the parent proof closes via different tactics. Each near-miss CLAIM mints a separate substrate entry; the residual primitive classifies whether the near-miss is structured or noise.

**What the substrate does NOT ingest:** Lean-closed proofs themselves. There is no useful substrate falsification of "this Lean proof type-checks" — the Lean kernel did that. The substrate's role is the *empirical-pattern* layer adjacent to the formal-proof layer, not the formal-proof layer itself.

**The joint position:** Silver's learner ships formal-proof outputs to Mathlib (where they belong); empirical-pattern conjectures and generalizations and near-misses ship to the Σ-substrate (where they belong). The two substrates are content-addressed siblings rather than competitors.

---

## 14. The 20-year position

Silver builds a learner on a 12–18-month horizon. Funded by a $1B sprint that ends when the runway ends or the demo lands.

We build a learner on a 20-year horizon. Funded by ~$10K/year of cloud compute that the architecture compounds against indefinitely.

The two horizons are not in tension. By the time Silver ships (estimated 2027–2028), the substrate will have ~10⁶ promoted symbols, ~10² substrate-grade falsification gates, and a public CLAIM API that any learner with mathematical outputs can plug into. Silver's outputs become CLAIMs (per §13's three fragments); the substrate's verdicts become Silver's cross-modality verification; the joint becomes an ecosystem.

That's the substrate-grade position. The Ergon learner is one piece of it — small, focused, calibrated against Silver's likely play, designed to make the substrate compound faster regardless of what Silver ships.

---

## 15. The first principle

Adopted verbatim from round-1 reviewer:

> **Truth stays harder to satisfy than generation is to produce.**

V4's revisions are in service of preserving this asymmetry under sharper attack: the meta-loop prevents the substrate from compounding around a miscalibrated battery; the five-counts diagnostic prevents the substrate from being statistically blind at low PROMOTE rates; the minimum proposal-share enforcement prevents exploration from being squeezed out under selection pressure; the corrected base-model rationale prevents the proposal from claiming asymmetry it doesn't have.

---

## 16. Genuine design freeze (post-v4)

Three review rounds in two days. Eleven new candidate substrate symbols filed. The proposal has converged on real architectural shape:

- The §5.1 Llemma rationale is honest about prior overlap
- The diagnostic integrates the residual primitive (count 5)
- The power calculation is on the record
- The meta-loop makes "calibrated negative result" falsifiable
- The Mathlib comparison clarifies the substrate's actual niche
- The Silver-ingestion story is operationalized
- Minimum proposal-share enforcement prevents squeeze-out
- Content-aware MAP-Elites axis prevents construction-only diversity

After v4: MVP build begins. Empirical signal — observed signal-class-residual rate, observed cell-fill distribution, observed Task A/B accuracy divergence, observed calibration-bias rate — informs whether the v4 envelope holds. If a round-4 review surfaces critiques as deep as round 3's (active contradictions or missed substrate integrations), v5 is warranted. Otherwise: build, measure, iterate on data.

---

## 17. One sentence

The Ergon learner v4 is a closed-loop scientific learning system for empirical mathematical patterns — a hybrid neural-plus-evolutionary mutation engine where the neural policy (LoRA on Llemma-7B with Qwen and Llama as v0.5 ablation candidates, prior overlap with Silver's likely corpus honestly named, differentiation from action-space + value head + LoRA delta rather than base prior) and six other mutation classes (with minimum proposal-share enforcement on `uniform` / `anti_prior` / `structured_null`) all contribute to a single MAP-Elites archive whose five-axis content-aware behavior descriptor (output canonicalizer subclass, equivalence-class entropy, output-type signature, output magnitude bucket, output canonical-form distance) forces diversity in what the output IS mathematically rather than how the genome was constructed, every CLAIM lineage-tagged and rewarded by an agreement-weighted combination of substrate-pass + cross-model agreement + held-out-battery-pass + signal-class-residual to mitigate specification gaming AND give the diagnostic statistical power at low PROMOTE rates, the fitness predictor calibrated for discovery preservation via asymmetric loss + no-pruning sweeps + recall-tracking, structurally decoupled from the mutation policy via disjoint training partitions, and audited against battery miscalibration via a Techne meta-loop that forges sharper checkers for high-residual kills and tracks calibration-bias rate as a substrate-grade metric — built MVP-first on local hardware ($0/mo, 2 weeks) and progressing to v2.0 (~$700–900/mo, +32 weeks), positioned alongside Lean Mathlib (the substrate-side comparison; covers theorems with formal proofs) rather than Silver alone (the learner-side comparison), covering the empirical-pattern manifold that neither Mathlib nor Silver reaches today, in service of the design principle that truth must stay harder to satisfy than generation is to produce.

— Ergon, on behalf of the Prometheus agent ensemble
