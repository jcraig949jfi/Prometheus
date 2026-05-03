# Ergon Learner — Final Design Writeup for External Review (v7, last design cycle pre-MVP)

### A consolidated, operational design document covering objective, shipped Prometheus tools, architectural summary (v5+v6 baked in), small incremental MVP trials, risk register, early-detection signals, library choices, framework borrow-vs-build, logging strategy, RAG analysis, and LLM ablation plan. **This is the last design-layer review round before MVP build.**

**Date:** 2026-05-03
**Status:** Final pre-MVP cycle. Pasteable to frontier-model context windows as a standalone artifact. Architectural commitments from v5+v6 are baked in; this document adds the MVP-execution layer, risk discipline, and tooling decisions that the prior versions left implicit.
**Companion canonical architectural docs:** [`pivot/ergon_learner_proposal_v5.md`](ergon_learner_proposal_v5.md), [`pivot/ergon_learner_proposal_v6.md`](ergon_learner_proposal_v6.md). Read v5 for full architectural treatment; this document summarizes and extends.

---

## 1. Objective

Build a small closed-loop scientific learning system for empirical mathematical patterns, plug-compatible with the Prometheus Σ-substrate, structurally complementary to David Silver's $1B Ineffable Intelligence bet on formal-proof self-play. The system's discovery surface — empirical patterns expressible as typed compositions over a mechanically-verified math arsenal, falsified by a calibrated kill battery — is disjoint from Lean Mathlib's formal-proof manifold. It does not compete with Silver; it is the substrate his outputs (and any other source of mathematical claims) plug into for cross-modality verification.

Design principle: **truth stays harder to satisfy than generation is to produce.** Every architectural component is in service of preserving this asymmetry under attack at every layer of the verification stack — proposer, evaluator, classifier, descriptor.

Scale target: ~$0/mo at MVP (local 2× 16GB + 1× 8GB), ~$400-1100/mo at v1.0 (burst H100 + Hetzner host + B2 object storage), 20-year compounding horizon with content-addressed promoted symbols outliving any specific learner.

---

## 2. What Prometheus already has (Σ-substrate inventory)

External reviewers can verify these are shipped and tested by checking the cited commits. Skip to §3 if already familiar.

| Component | Purpose | LOC | Tests | Commit |
|---|---|---|---|---|
| **Σ-kernel** (`sigma_kernel/sigma_kernel.py`) | Append-only content-addressed substrate runtime; 7 typed opcodes (RESOLVE/CLAIM/FALSIFY/GATE/PROMOTE/ERRATA/TRACE); linear capability tokens; SQLite + Postgres backends | ~1500 | extensive | shipped 2026-04-29 |
| **BIND/EVAL extension** (`sigma_kernel/bind_eval.py`) | Symbols-as-executable-callables; cost-model enforcement; hash-drift detection; v2 routes through CLAIM/FALSIFY/PROMOTE | ~520 + 14 tests | green | ac4176f0; v2 at b0355b1d |
| **Math arsenal** (`prometheus_math/`) | ~2,800 mechanically-verified math callables across 40+ modules (numerics_special, number_theory, elliptic_curves, modular_forms, geometry, topology, combinatorics, optimization, dynamics, plus research-domain modules) | ~30K LOC | ~280+ math-tdd tests | accumulated through wave 18 |
| **arsenal_meta** (`prometheus_math/_metadata_table.py`) | 85 ArsenalMeta entries with calibrated cost models (within 2×–50× of actual median), 2-5 specific postconditions per op citing primary authorities (Cohen GTM 138, Whittaker & Watson, OEIS, LMFDB, Mossinghoff), canonicalizer-subclass tags | ~830 | 10 tests | 4f5a8a22 |
| **Falsification battery** (`cartography/shared/scripts/falsification_battery.py`) | F1-F20 named kill tests; unanimous battery {F1, F6, F9, F11} calibrated to 100% recovery on ~180 known truths | ~3K | calibration set | accumulated |
| **Residual primitive** (`sigma_kernel/residuals.py`) | Typed Residual + SpectralVerdict; record_residual / REFINE / record_meta_claim opcodes; three composing stopping rules (cost-budget compounding; mechanical signal/noise classifier; instrument-self-audit auto-trigger) | ~748 | shipped tests | 4872bb4a |
| **DiscoveryPipeline** (`prometheus_math/discovery_pipeline.py`) | Three-state terminal pipeline (PROMOTED / SHADOW_CATALOG / REJECTED) implementing §6.1 of discovery_via_rediscovery doc | ~430 | shipped | 09a7dccb |
| **DiscoveryEnv** (`prometheus_math/discovery_env.py`) | Generative reciprocal-poly sampler over Discrete(7) coefficient action space; ~117K trajectories at degree 10; sparse reward; substrate-conditioned obs; best result M=1.458 in Salem cluster band | shipped | 16 tests | shipped |
| **ObstructionEnv** (`prometheus_math/obstruction_env.py`) | Sequel: synthetic-but-genuinely-open OBSTRUCTION_SHAPE pattern detection on simulated A149* data | shipped | included | d339dc45 |
| **Four-counts pilot harness** (`prometheus_math/four_counts_pilot.py`) | Multi-arm operator-class diagnostic with Welch t-test + Holm correction; 16 tests | ~706 | green | 1666c4a4 |
| **Multi-agent agora** | Redis-backed message bus; 7 agent lanes (Charon, Harmonia, Aporia, Ergon, Mnemosyne, Techne, Koios) | infrastructure | live | accumulated |

**Pre-MVP gaps that v7 must close:**
- Adversarial residual benchmark not yet run (per v5 §2.6 + v6 confidence-tiered activation)
- Five-counts diagnostic (v5 upgrade) needs `signal_class_residual_kill` count wired in (the pilot today reports four counts)
- Bounded output-magnitude buckets + trivial-pattern detector (v6 §6.2) need implementation
- Cross-model evaluator with logical-consistency-only prompt template (v6 §5.3) needs codification
- Genome / cells / lineage tables in `sigma_proto` schema (migrations 004 + 005) not yet applied

---

## 3. Architectural summary (v5+v6 baked in)

For full treatment see v5 and v6. This is the operational summary.

### Hybrid neural + evolutionary mutation engine

Seven mutation operator classes contributing to a single MAP-Elites archive:

| Class | Operator | Adjacency profile | Min share |
|---|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges within type discipline | Typed-composition topology | — |
| `symbolic` | Bump arg values within type | Local in argument space | — |
| `neural` | LoRA-fine-tuned policy mutation | LLM-prior (post-substrate-fine-tuning) | — |
| `external_llm` | Frontier LLM API mutation | External LLM-prior | — |
| `anti_prior` | Anti-correlated with corpus frequency stats | Deliberately off-prior | ≥5% |
| `uniform` | Resample atoms uniformly | Strawman null | ≥5% |
| `structured_null` | Type-respecting uniform | Type-respecting null | ≥5% |

Total non-prior-shaped operators: ≥15% of all proposals at all times (scheduler-enforced).

### Agreement-weighted reward (v6 specification)

```
reward(θ_k, claim) =
    w_S * substrate_pass_indicator           # 0.40 — battery + residual classifier
  + w_X * cross_model_logical_consistency    # 0.15 — DAG-consistency only, NOT discovery-judgment
  + w_H * holdout_battery_pass_indicator     # 0.20 — battery subset withheld from training
  + w_NL * non_llm_evaluator_pass            # 0.10 — numeric perturbation / symbolic / theorem-prover
  + w_R * signal_class_residual_indicator    # 0.15 — CONDITIONAL on adversarial benchmark passing
```

w_R activation tiered by adversarial residual benchmark FP-rate:
- ≤2% on 100 synthetic-structured-noise samples (95% upper CI ≤4.7%): full 0.15
- ≤5% (CI ≤9.4%): half 0.075
- ≤10%: 0 (escrow — diagnostics only)
- >10%: 0 (deep escrow — retrain or replace classifier)

Plus ECE ≤0.05 across 5 bins required for any non-zero w_R.

### Five-axis content-aware MAP-Elites descriptor (v6 specification)

5,000 cells: 4 × 5 × 10 × 5 × 5

1. **Output canonicalizer subclass** (4 categorical: group_quotient / partition_refinement / ideal_reduction / variety_fingerprint)
2. **Equivalence-class entropy of DAG** (5 quantile buckets)
3. **Output-type signature** (~10 categorical)
4. **Output magnitude bucket** (5 *bounded* ranges, NOT quantile-binned: [10⁰, 10³), [10³, 10⁶), [10⁶, 10⁹), [10⁹, 10¹²), [10¹², ∞); outside [10⁰, 10¹⁵] → out_of_band)
5. **Output canonical-form distance** (5 quantile buckets, distance to nearest catalog entry)

Per-axis fill-rate audit every 1K episodes; axes >70% concentration in one bin or |corr|>0.7 with another flagged for hot-swap.

### Five-counts diagnostic per operator class

For each operator class, run N episodes through `DiscoveryEnv` + `DiscoveryPipeline` + Residual primitive. Report:

1. Catalog-hit rate
2. Claim-into-kernel rate
3. PROMOTE rate (substrate-only and agreement-weighted variants)
4. Battery-kill rate
5. **Signal-class-residual rate** (battery-killed CLAIMs with residual classifier confidence ≥0.7 for signal-class)

Statistical comparison: Welch t-test with Holm correction across operator classes, on both PROMOTE rate AND signal-class-residual rate.

### Defensive surface against the residual-gaming attractor (v5 §11.6)

The architecture's bear case: system optimizes for looking like signal, not being signal. Five layered mitigations:

| Defense | Against which step of the attractor |
|---|---|
| Adversarial residual benchmark <5% FP on synthetic structured-noise | Classifier mislabeling noise as signal |
| Confidence abstention zone (≥0.85 only earns reward) | Mid-confidence residual gaming |
| Non-LLM evaluator (w_NL=0.10) | Cross-model agreement reinforcing shared bias |
| Meta-loop trigger fix (3% threshold + absolute-count fallback + scheduled fires) | Meta-loop dead zone |
| `residual_signal_precision` per operator (threshold 0.10) | Residuals high but meaningless |

---

## 4. Three small incremental MVP trials — early concept tests

The architecture is enormous if shipped all at once. The three-trial structure tests the load-bearing assumptions early, before any cloud spend, in a sequence where each trial gates the next.

### Trial 1 — Adversarial residual benchmark (Days 1–4)

**Concept tested:** Is the residual classifier accurate enough to serve as reward signal? (The single most load-bearing assumption per round-4 review.)

**Implementation:**
- Curate 200 benchmark samples: 50 obvious noise (FP-quantization, MC-seed jitter, Gaussian residuals at noise floor); 50 borderline signal (Mercury perihelion residual at low-confidence regime; Ramanujan-Hardy asymptotic residuals at marginal n; Riemann Li(x)−π(x) at x where the difference is hardest to distinguish from noise); 100 synthetic structured-noise (deliberately constructed to look like signal but be uncorrelated with truth).
- Run the v5 residual classifier (`sigma_kernel/residuals.py:_classify_residual`) on all 200 samples.
- Compute: overall accuracy; FP rate on synthetic structured-noise specifically; Expected Calibration Error across 5 confidence bins.

**Success criteria:**
- ≥85% overall accuracy
- ≤5% FP rate on synthetic structured-noise (target: ≤2% for full w_R activation)
- ECE ≤0.05

**Failure mode + adjustment path:**
- *FP rate >10%:* residual primitive cannot serve as reward signal at current calibration. Revert to PROMOTE-only reward; accept statistical-power consequences from §7.5 power calculation. Substrate-grade negative result on v4's biggest move.
- *FP rate 5-10%:* w_R activates at half-strength (0.075); proceed to Trial 2 with reduced gradient; revisit classifier calibration before scaling.
- *Overall accuracy <85% but FP on SSN ≤5%:* classifier is conservative on noise but inaccurate on borderline-signal — proceed to Trial 2 but flag for retraining; the safe direction (over-rejection of marginal signal) is acceptable for MVP.

**Cost:** ~4 days local. $0 cloud spend.

### Trial 2 — Evolutionary engine with bounded buckets and trivial-pattern detector (Days 5–10)

**Concept tested:** Does Ergon's MAP-Elites with bounded output-magnitude buckets and the F_TRIVIAL_BAND_REJECT extension fill cells differently from uniform random over the discovery_env action space? (Tests v6 §6.2.)

**Implementation:**
- Implement bounded-bucket version of MAP-Elites descriptor in `ergon/learner/archive.py`.
- Implement F_TRIVIAL_BAND_REJECT with the four initial signatures (small-number coincidence, prime-density artifact, scale rescaling, cyclotomic root-of-unity coincidence).
- Run the engine for 1K episodes WITHOUT neural policy — only `structural`, `symbolic`, `uniform`, `structured_null`, `anti_prior`. Compare to a 1K-episode uniform-only baseline.
- Measure: cell-fill distribution per axis; per-operator-class fill counts; F_TRIVIAL_BAND_REJECT trigger rate; signal-class-residual rate per operator class.

**Success criteria:**
- Cell-fill distribution: ≥60% of cells with at least one entry across all 5 axes
- No single axis with >70% concentration in one bin
- F_TRIVIAL_BAND_REJECT trigger rate: 5-30% of all kills (lower bound: detector is doing meaningful work; upper bound: detector isn't over-rejecting)
- `structural` operator's signal-class-residual rate is ≥1.5× the `uniform` operator's rate (selection pressure produces structured outputs)

**Failure mode + adjustment path:**
- *Cell-fill <60%:* descriptor is too coarse OR action space is too narrow. Investigate per-axis fill; flag axes with >70% concentration; potentially hot-swap to alternate axes (per v5 §6.2 hot-swap protocol).
- *F_TRIVIAL_BAND_REJECT trigger >30%:* detector is over-rejecting. Refine signatures; reduce stringency.
- *F_TRIVIAL_BAND_REJECT trigger <5%:* detector is ineffective. Either gravitational wells aren't an issue at this scale (good) or the four initial signatures don't cover the actual wells (bad). Investigate kill distribution.
- *`structural` rate ≤ `uniform` rate:* selection pressure isn't producing more-structured outputs. Indicates fitness ranking inside cells isn't working OR the residual classifier isn't distinguishing structural-vs-uniform outputs.

**Cost:** ~6 days local. $0 cloud spend.

### Trial 3 — Five-counts diagnostic on three-arm pilot (Days 11–15)

**Concept tested:** Does the five-counts diagnostic distinguish operator classes at a budget the project can afford? (Tests v5 §7.4-7.5; gates the entire diagnostic strategy.)

**Implementation:**
- Run the engine for 3K episodes per arm × 3 arms (`uniform` / `structural` / `symbolic`) — total 9K episodes. No neural policy yet (that's v0.5).
- Implement the five-counts diagnostic with Welch t-test + Holm correction (already exists in `four_counts_pilot.py`; needs the fifth-count addition).
- Report per-arm: catalog-hit rate, claim-into-kernel rate, PROMOTE rate (substrate-only + agreement-weighted), battery-kill rate, signal-class-residual rate.

**Success criteria:**
- Signal-class-residual rate ≥10× the PROMOTE rate (the v5 hypothesis that residuals are denser than promotions by construction)
- At least one operator class out-`signal_class_residual`s `uniform` at p<0.05 corrected (does selection pressure produce more structured residuals than noise?)
- `residual_signal_precision` measurable and >0 for at least one operator class

**Failure mode + adjustment path:**
- *Signal-class-residual rate ≈ PROMOTE rate:* residuals are not denser than promotions; the v5 statistical-power argument fails. Reconsider whether residuals as reward signal is workable.
- *No operator class beats `uniform` at p<0.05:* the engine isn't doing better than noise at MVP scale, or the diagnostic doesn't have power to detect at 3K episodes. Scale to 10K; if still no significance, the architecture doesn't have a usable gradient at this configuration.
- *`residual_signal_precision` is 0 across all classes:* signal-class residuals aren't predictive of downstream PROMOTE / META success. Gradient is fake; revert to PROMOTE-only.

**Cost:** ~5 days local. $0 cloud spend.

### Trials gate the v0.5 commitment

If all three trials pass within their success bands, v0.5 (cross-model agreement, held-out battery, non-LLM evaluator, base-model ablation, Techne meta-loop) is justified at $50-150/mo cloud spend. If any trial fails decisively, the v0.5 commitment is paused until the failure is understood.

**Total MVP time: 15 days, $0 cloud spend.** The trials together test the load-bearing assumptions of every layer of the architecture before any cloud commitment.

---

## 5. Risk register and early-detection signals

| Risk | Severity | Likelihood | Early signal | Mitigation |
|---|---|---|---|---|
| **R1: Residual classifier benchmark fails** | High | Medium | Trial 1 FP rate >5% on synthetic structured-noise | w_R activation tiered (v6); deep-escrow if FP >10%; revert to PROMOTE-only reward |
| **R2: PROMOTE rate too sparse to resolve** | High | High (consistent with 0/3000 result) | Trial 3 PROMOTE rate <10⁻³ | Five-counts diagnostic relies on residual-rate (denser by construction); §7.5 power calculation is the explicit acknowledgment |
| **R3: Cross-model evaluator contamination** | Medium | Medium | v0.5 cross-model agreement on `anti_prior` outputs is significantly lower than on `structural` outputs at constant DAG-consistency | v6 prompt restriction to logical-consistency-only; w_X reduced to 0.15; non-LLM evaluator at w_NL=0.10 provides independent signal |
| **R4: anti_prior generates structured noise** | Medium | High | `anti_prior` operator's residual_signal_precision is <50% of `structural`'s precision | Per-operator-class precision tracking (v5 §3.5.5); operator weight reduced if precision is consistently low; treat anti_prior as null baseline |
| **R5: MAP-Elites descriptor degeneracy** | Medium | Medium | Per-axis audit shows >70% concentration in one bin within first 10K episodes | Hot-swappable descriptor (v5 §6.2) with replacement candidates pre-specified per axis |
| **R6: Compute budget overrun** | Medium | Low at MVP, Medium at v1.0 | Monthly spend exceeds $1100 (v6 honest range upper bound) | 25-30% headroom buffer in v6 envelope; downscale H100 burst frequency before downscaling MVP loop frequency |
| **R7: HITL bandwidth bottleneck** | High | High | James can't keep up with cross-resolution requests; agent-team coordination drags | Automate cross-resolution where possible; concentrate HITL touchpoints on substrate-grade decisions (PROMOTE / META_CLAIM / architectural pivots), not implementation details |
| **R8: Residual-gaming attractor fires undetected** | High | Medium | residual_signal_precision <0.10 across multiple operators for >2 consecutive 10K windows | v5 §11.6 defensive surface (5 layered mitigations); if precision is structurally low, w_R activation drops one tier |
| **R9: Llemma LoRA delta saturates at corpus prior** | Medium | Medium-High | v0.5 ablation shows Llemma's held-out-cell coverage is ≤ Qwen's or Llama's | Pivot v1.0 base model to whichever ablation winner produces most divergent LoRA delta |
| **R10: Trivial-pattern detector misses real wells** | Medium | High | F_TRIVIAL_BAND_REJECT trigger rate <5% but downstream PROMOTE/META analysis reveals trivial patterns the detector missed | Signature library is extensible via Techne meta-loop; new signatures added as they're discovered; treat library as substrate-grade artifact that grows over time |

### Early-detection metrics dashboard

Real-time aggregation across the substrate; alerts when thresholds breach:

- `residual_signal_precision_per_operator` (per 10K episodes; alert if <0.10 for any operator across 2 windows)
- `meta_loop_fire_rate` (per 100K episodes; alert if 0)
- `cell_fill_distribution_max_concentration` (per axis; alert if >0.70)
- `cross_model_agreement_per_operator` (per 1K; alert if `anti_prior` < 0.5× `structural`'s rate at constant logical-consistency)
- `f_trivial_band_reject_trigger_rate` (per 1K; alert if outside [5%, 30%])
- `compute_spend_per_day` (alert if 30-day projection exceeds $1100)

---

## 6. Math libraries to include / expand

The current arsenal_meta has 85 ops across 11 categories. Pre-MVP additions and v0.5+ expansions:

### Already in arsenal (verify metadata coverage)

- `prometheus_math.numerics_special` (dilogarithm, polylogarithm, theta, eta, Hurwitz zeta, q-Pochhammer)
- `prometheus_math.number_theory` (Iwasawa polynomials, Hecke operators, Galois cohomology)
- `prometheus_math.elliptic_curves` (point counting, isogeny, BSD invariants, Mahler measure)
- `prometheus_math.modular_forms`
- `prometheus_math.number_fields`
- `prometheus_math.geometry` (convex hull, Delaunay, Voronoi via shapely soft-dep)
- `prometheus_math.topology` (knot invariants via snappy)
- `prometheus_math.combinatorics` (partitions, permutations, posets)
- `prometheus_math.optimization` (QP, SDP, SOCP, metaheuristics via scipy + cvxpy + pycma)
- `prometheus_math.dynamics` (iterated maps, ODE solvers via scipy)

### Pre-MVP: external library bindings (no code changes; metadata table additions)

- **PARI/GP** via `cypari` — already a hard dependency for several ops; expand metadata coverage to ~50+ PARI calls
- **SymPy** — symbolic algebra; expand metadata coverage to ~30 ops including factor_list, simplify, solve, integrate
- **mpmath** — arbitrary-precision; expand metadata coverage to ~20 ops (already used by special functions; just need consistent registration)
- **NumPy / SciPy** — already used; metadata for ~40 numerical primitives (FFT, eigendecomposition, solvers)

### v0.5: external API bindings (network-dependent, use sparingly)

- **LMFDB API** (`lmfdb.org/api`) — empirical reference data on elliptic curves, modular forms, number fields, etc. Wrap as substrate-conditioned lookup (results memoized in `sigma_proto.lmfdb_lookups`).
- **OEIS API** (`oeis.org/wiki/Main_Page`) — sequence reference. Wrap with caching.
- **KnotInfo** (`knotinfo.math.indiana.edu`) — knot invariants reference.

### v1.0+: deeper library integrations

- **SageMath** Python interface — broader algebra (varieties, schemes, lattice algorithms). Heavy install; considered for v1.0 only if specific arsenal gaps are identified.
- **Lean 4 + Mathlib** — for the "Silver-ingestion" cross-modality verification layer (§13 of v5). Specifically: verify whether a substrate-PROMOTEd empirical conjecture corresponds to an existing Mathlib statement.
- **TensorLy** — tensor decompositions, relevant for Charon's tensor work and possibly for the genome-encoding learned representations at v1.5.
- **NetworkX / igraph** — graph operations on DAG topologies and knot diagrams.

### v2.0+: corpus-scale ingestion (if RAG is added per §10)

- **ArXiv math abstracts** — ~500K records as Ring 3 training data
- **Lean Mathlib statements** — ~120K theorem statements
- **Proof-Pile-2** — Llemma's training corpus, useful for `anti_prior` operator's frequency-stats database
- **OpenWebMath** — 14B token math-pretraining corpus; useful for retrieval if RAG is added

---

## 7. Open-source tools and libraries to leverage

Concrete picks. The principle: borrow proven infrastructure; build only what's specific to the substrate's discipline.

### LLM training and inference

- **PyTorch 2.x** — primary ML framework
- **Hugging Face Transformers** — model loading, tokenization, generation
- **PEFT (Parameter-Efficient Fine-Tuning)** — LoRA implementation
- **TRL (Transformer Reinforcement Learning)** — PPO, DPO, SFT for the RL fine-tuning loop
- **bitsandbytes** — 4-bit/8-bit quantization (essential for fitting Llemma-7B on 16GB)
- **Axolotl OR Unsloth** — training pipeline; choice depends on hardware. Unsloth is faster on consumer hardware; Axolotl is more configurable for production runs.
- **vLLM** — high-throughput inference serving (essential for batch generation at v0.5+)

### RL infrastructure

- **CleanRL** — REINFORCE / PPO baselines (already used at MVP level)
- **stable-baselines3** — production RL algorithms; consider for v1.0
- **pyribs** — quality-diversity / MAP-Elites; this is the core MAP-Elites infrastructure
- **DEAP** — genetic algorithms (operator implementations for `structural` and `symbolic` mutations)

### Substrate infrastructure

- **PostgreSQL 16+** — substrate primary store
- **pgvector extension** — substrate symbol embeddings, nearest-neighbor mutation
- **TimescaleDB extension** — time-series for training metrics, per-cell statistics
- **Redis 7+** — agora message bus, hot cache
- **psycopg3** — PostgreSQL client
- **redis-py** — Redis client
- **alembic** — schema migrations

### Numeric / scientific

- **NumPy** — array operations
- **SciPy** — scientific computing primitives
- **scikit-learn** — Task B fitness predictor baseline (DeBERTa or simple MLP)
- **statsmodels** — Welch t-test, Holm correction, ECE calibration
- **scipy.stats** — confidence intervals on benchmark proportions

### Math

- **PARI/GP** via cypari — number-theory backbone (already heavily used)
- **SymPy** — symbolic computation
- **mpmath** — arbitrary precision
- **shapely** (soft) — geometric ops

### Logging / observability

- **structlog** — structured logging
- **prometheus-client** — metrics export to time-series store
- **Grafana** — dashboards (or vector / OTEL-compatible alternative)
- **OpenTelemetry** — distributed tracing across the agora

### Cloud / deployment

- **Hetzner / Vultr** — substrate dedicated hosting
- **Backblaze B2 OR S3** — object storage (LoRA checkpoints, archive snapshots)
- **RunPod / vast.ai / Lambda Labs** — burst H100 rental
- **Together AI / Anyscale** — managed inference endpoints (if needed)

### Build vs. borrow decision matrix

**Borrow (don't reimplement):**
- MAP-Elites archive: pyribs
- LoRA training: PEFT + TRL + Axolotl/Unsloth
- Inference serving: vLLM
- Genetic operators: DEAP
- Statistical tests: scipy.stats / statsmodels
- LLM tokenization / generation: Transformers
- Quantization: bitsandbytes
- Substrate storage: PostgreSQL + pgvector + TimescaleDB
- Message bus: Redis Streams
- Migrations: alembic
- Logging: structlog
- Dashboards: Grafana

**Build (substrate-specific):**
- The Σ-kernel (already built)
- Genome / typed-DAG representation specific to the arsenal
- The five-counts diagnostic harness (extension of existing four-counts)
- The agreement-weighted reward composition (specific weights, multi-evaluator orchestration)
- The Techne meta-loop (sharper-checker forging is substrate-specific)
- The trivial-pattern detector signature library (substrate-specific kill-test extension)
- Confidence-tiered w_R activation (specific to the residual primitive)
- The arsenal-frequency-statistics database for anti_prior (corpus-derived but built locally)

---

## 8. Logging and real-time analytics

Comprehensive logging is itself substrate-grade — every CLAIM, FALSIFY, PROMOTE, and ERRATA is content-addressed and append-only. The question is what additional telemetry layers serve operator monitoring.

### Core logging (always on)

- **Per-CLAIM provenance** (already in kernel): claim_id, def_blob, def_hash, lineage, mutation_operator_class, parent_claim_ids, args_hash, timestamp
- **Per-FALSIFY verdict** (already in kernel): claim_id, kill_test_id, verdict (CLEAR/WARN/BLOCK), rationale_hash, elapsed_seconds, oracle_calls
- **Per-PROMOTE event** (already in kernel): symbol_id, name, version, def_obj, provenance_chain
- **Per-Residual classification** (already in residuals.py): residual_id, classifier_confidence, classification (signal/noise/instrument_drift), failure_shape

### Operator-monitoring telemetry (new, for real-time analytics)

Tabled in TimescaleDB for time-series queries:

- `operator_per_window_metrics`: per-operator-class per-1K-episode aggregations of:
  - cell_fill_count
  - claim_into_kernel_rate
  - promote_rate (substrate-only and agreement-weighted)
  - battery_kill_rate
  - signal_class_residual_rate
  - residual_signal_precision (running 10K-episode window)
- `cell_fill_distribution`: per-cell historical occupancy, retire-rate, elite-replacement count
- `descriptor_audit_events`: per-1K-episode per-axis fill-rate audit results; flagged axes
- `meta_loop_fire_events`: timestamp, trigger_reason (threshold / absolute_count / scheduled), sharper_checker_outcome, calibration_bias_rate
- `compute_consumption`: per-iteration cost-tracking (BindEvalKernelV2 cost-model + actual elapsed + GPU hours)
- `training_loss_curves`: per-LoRA-iteration loss + held-out-cell-coverage delta
- `cross_model_evaluator_outputs`: per-claim per-evaluator logical-consistency verdicts; agreement statistics
- `holdout_battery_audit_results`: per-audit PROMOTE-rate-divergence signal

### Real-time alerts

Triggered by Prometheus-style metric thresholds, surfaced via a lightweight HITL dashboard:

| Alert | Trigger | Severity |
|---|---|---|
| `residual_classifier_failing` | residual_signal_precision <0.10 across 2 consecutive 10K windows | High — pause w_R or reduce tier |
| `meta_loop_dead` | meta_loop_fire_rate = 0 across 100K window | Medium — investigate trigger logic |
| `descriptor_axis_collapsed` | Per-axis fill-rate concentration >70% | Medium — schedule hot-swap |
| `compute_overspend` | 30-day projection >$1100 | Medium — scale down burst frequency |
| `f_trivial_reject_anomalous` | F_TRIVIAL_BAND_REJECT trigger rate <5% or >30% in any 1K window | Low — investigate signature library |
| `gaming_pattern_detected` | held-out-battery PROMOTE-rate divergence >threshold | High — pause learning, investigate spec gaming |
| `anti_prior_under_performing` | anti_prior's residual_signal_precision <50% of structural's | Low — operator is null-like, expected |

### Dashboards

Two layers:

- **Operator dashboard** (Grafana): time-series of all `operator_per_window_metrics`; per-cell heatmaps of archive fill; cost-spend trend; alert status board.
- **Substrate-growth dashboard** (custom): symbol count over time, PROMOTE rate, META_CLAIM rate, calibration_bias_rate, lineage graph statistics. This is the long-term substrate health signal.

---

## 9. RAG considerations

Should the architecture incorporate retrieval-augmented generation? My analysis:

**Pro-RAG arguments:**
- The substrate already accumulates ~10⁵+ promoted symbols by week 8; retrieval over them could provide policy context.
- pgvector embeddings of substrate symbols are already proposed (v6 §8.2 storage).
- LMFDB / OEIS / KnotInfo are ready-made retrieval corpora at v0.5.

**Anti-RAG arguments:**
- RAG biases generation toward retrieval-similar precedents — exactly the LLM-prior contamination v6 fights via the `anti_prior` operator and the cross-model logical-consistency restriction.
- At MVP scale, retrieval adds complexity without proven value.
- The substrate's content-addressed structure already provides better-than-RAG retrieval (deterministic, provenance-tracked) when needed; an additional embedding layer is redundant.

**Recommendation: NO RAG at MVP or v0.5.** v1.0 introduces a "calibration-anchor retrieval" component:

- Strictly within-substrate retrieval (pgvector over PROMOTEd symbols + SHADOW_CATALOG entries).
- Used only for the conjecture-generation task (Task C), not for mutation policy (Task A) or fitness prediction (Task B).
- Lineage-tagged: claims generated with retrieval context get `mutation_operator_class = neural_with_substrate_rag` distinct from `neural` (allows ablation comparison).

v2.0 may add limited corpus retrieval (Mathlib statements, ArXiv abstracts) but only if Task C's claim-quality on a held-out benchmark provably beats no-retrieval.

The principle: **retrieval is opt-in per task, lineage-tagged for ablation, and gated on demonstrated improvement over the no-retrieval baseline.** Don't let the convenience of RAG silently re-introduce the LLM-prior contamination the architecture is structured to fight.

---

## 10. Starter LLM strategy and ablation

### Lead candidates (7B class, fits 2× 16GB at 4-bit, fits H100 for full-precision LoRA)

| Model | Pretraining corpus | License | Strength |
|---|---|---|---|
| **Llemma-7B** | Proof-Pile-2 (Mathlib + ArXiv math + theorem proofs) | Apache 2.0 | Strong math-reasoning; closest to formal-proof distribution |
| **DeepSeek-Math-7B** | DeepSeek's math corpus + competition data | DeepSeek License | Strongest competition-math benchmarks |
| **Qwen2.5-Math-7B** | Qwen team's math-focused pretraining | Apache 2.0 | Newest; strong instruction-following |
| **Llama-3.1-8B (general)** | General pretraining (no specific math focus) | Meta License | General prior; useful as ablation baseline |
| **Qwen2.5-7B (general)** | General pretraining | Apache 2.0 | General prior; ablation baseline |

### v0.5 ablation plan

Run all five candidates under identical fine-tuning protocol:

- Multi-task LoRA (Tasks A, B, C) on substrate-verdict outcomes for 1K iterations
- Same agreement-weighted reward formula
- Same training data split
- Same hyperparameters (LoRA rank 32 for Tasks A/C, 16 for Task B; learning rate 1e-4; batch size depending on memory)

**Metric: held-out-cell coverage divergence between resulting policies.** The base model whose LoRA delta produces the most divergent operator-class lineage distribution from non-LLM operators wins. Expected: math-pretrained bases (Llemma, DeepSeek-Math, Qwen2.5-Math) will likely cluster; general bases (Llama, Qwen general) may diverge more — but at the cost of weaker baseline math capability. The ablation IS the empirical test of which trade-off matters.

### v1.0 production: pick the ablation winner

Production v1.0 uses the ablation winner. Backup base remains available for emergency fallback.

### v2.0 ensemble: multiple bases as different mutation distributions

Use 2-3 bases simultaneously, each as a distinct mutation operator (`neural_llemma`, `neural_deepseek`, `neural_qwen`). Each is a slightly different prior distribution; substrate's lineage tagging tracks which produces survivors in which cells.

### What about larger models?

- **InternLM-Math-20B** — won't fit 2× 16GB at usable quantization; requires multi-GPU or H100. Possibly considered at v1.5+.
- **DeepSeek-V3 / Qwen3-72B** — frontier-scale, only via API. Used as `external_llm` operator class, not as `neural` policy-base.
- **Frontier closed models (Claude, GPT, Gemini)** — only via API; constitute the cross-model evaluator + `external_llm` operator class.

---

## 11. Compute and storage envelope (v6 honest)

### Compute (v1.0 production target)

| Tier | Cost (mo) | Use |
|---|---|---|
| Local development | $0 | 2× 16GB + 1× 8GB consumer GPUs; MVP-tier training and inference |
| Burst training | $200–500 | RunPod / vast.ai / Lambda H100 (~$2.50/hr) for LoRA fine-tuning |
| Burst inference | $50–200 | Self-hosted on rented A100 for batch generation |
| Substrate hosting | $30–80 | Hetzner dedicated; Postgres + Redis + object storage gateway |
| **Operational overhead** | **$70–220** | Postgres IOPS at scale + Redis hot cache + network egress + storage egress |
| Buffer / variance | $50–100 | Cloud-GPU price volatility headroom |
| **Total** | **$400–1100/mo** | Full ideal stack at v1.0 |

24-month total: $9.6K – $26.4K. Three orders of magnitude below Silver's $1B.

### Storage

| Component | Tech | Scale at week 8 | Scale at year 1 |
|---|---|---|---|
| Substrate (kernel objects) | Postgres (`prometheus_fire`, schemas `sigma` + `sigma_proto` + `ergon`) | 50 GB | 1 TB |
| Hot cache + agora | Redis | 10 GB | 50 GB |
| Object storage | Backblaze B2 / S3 | 200 GB | 5 TB |
| Vector embeddings | pgvector | 5 GB | 100 GB |
| Time-series | TimescaleDB | 1 GB | 20 GB |
| Residual event archive | sigma_proto.residual_events | 0.5 GB | 10 GB |
| Corpus frequency stats (anti_prior) | sigma_proto.corpus_frequency_stats | 5 GB | 5 GB (static) |

---

## 12. Open questions for this final review round

The 18 open questions from prior rounds remain on the record (in v5/v6). This round adds questions specific to the operational dimensions James asked about:

### MVP execution

19. Are the three trial success criteria (§4) calibrated correctly? Specifically: is "≥10× signal-class-residual-rate vs PROMOTE rate" the right threshold for Trial 3, or should it be more / less stringent?

20. Is the 15-day MVP timeline realistic, or am I underestimating implementation time for the bounded-bucket descriptor + F_TRIVIAL_BAND_REJECT + five-counts diagnostic upgrade?

### Risk register

21. Is R7 (HITL bandwidth bottleneck) under-rated? In a multi-agent ensemble run, James's bandwidth IS the rate limit; if every architectural decision waits for HITL approval, the system stalls.

22. Are there risks I haven't named? Particularly: external dependencies (Hugging Face, RunPod, LMFDB API) that could disrupt the substrate's continuous operation.

### Library / framework

23. Should we use Axolotl or Unsloth for LoRA training? Unsloth is faster on consumer hardware (≥2× speedup claimed); Axolotl is more configurable. The MVP fitness predictor doesn't need either, but v1.0 LoRA on Llemma-7B does.

24. pyribs for MAP-Elites: any production-readiness concerns at the scale we'll run (~5K cells, ~10⁵ episodes per training cycle)?

25. Is there a better choice for the cross-model evaluator API orchestration than rolling our own? (e.g., LangChain / LiteLLM / DSPy)

### Logging

26. Should `operator_per_window_metrics` be Prometheus-pull or TimescaleDB-push? Prometheus is industry-standard but adds a new component; TimescaleDB-push reuses the substrate stack.

27. What's the right retention policy for verbose per-CLAIM logs? At 10⁵ CLAIMs per training cycle × 200 bytes per log = 20 MB per cycle. Manageable for years; the question is whether to compress/archive after N cycles.

### RAG

28. Is my "no RAG at MVP" recommendation correct, or is there a meaningful retrieval-augmentation use case I'm missing — particularly for Task C (conjecture generation) which is conceptually the most natural fit for retrieval?

29. If we do introduce RAG at v1.0+, what's the right approach to lineage-tag retrieval-augmented generations such that the ablation comparison is meaningful?

### LLM strategy

30. Is the v0.5 ablation across 5 bases excessive? Maybe 3 (Llemma, Qwen2.5-Math, Llama-3.1-8B) is enough to span the math-pretrained / general-pretrained axis.

31. Should we consider **DeepSeek-V3-Lite** or **Qwen3-MoE** mixture-of-experts models? They're more computationally efficient at inference but more complex to LoRA-fine-tune.

32. The "external_llm" operator class uses frontier LLMs via API. Should we standardize on one (e.g., Claude) or rotate (Claude / GPT / Gemini) per call to ensure prior-diversity within the operator class?

### Cross-cutting concerns

33. The architecture has accumulated 18 candidate substrate symbols across 5 review rounds. Should we promote any to canonical Tier-3 status before MVP, or hold all in candidate state until empirical signal?

34. Is the design genuinely frozen now, or am I rationalizing? What concrete signal would justify a v8?

---

## 13. The 20-year position (unchanged)

Silver builds on a 12-18-month horizon. We build on a 20-year horizon. By the time Silver ships, the substrate has ~10⁶ promoted symbols and a public CLAIM API. His Lean-closed proofs flow to Mathlib (where they belong); the empirical-pattern conjectures and generalizations and near-misses underlying them flow to the Σ-substrate (where they belong). The two substrates are content-addressed siblings.

Position survives any outcome of Silver's company — succeed, fail, pivot. The empirical-pattern niche is vacant; Mathlib doesn't cover it; the substrate is load-bearing for it.

---

## 14. The first principle

> **Truth stays harder to satisfy than generation is to produce.**

Every design commitment in this proposal is in service of preserving this asymmetry. Every architectural correction across v1→v6 was a defense against a specific way the asymmetry could be eroded. v7 is not an additional defense; it's the operational specification of what the defenses look like in production code.

---

## 15. Design freeze and MVP commencement

This is the last design-layer review round before MVP build begins. The architecture has been reviewed five times by external frontier models; 23 candidate substrate symbols have emerged; 18 open questions remain on the record from prior rounds; this round adds 16 more focused on operational dimensions.

**Commitment:** the next document filed in `pivot/` will be the MVP run report (Trial 1 / Trial 2 / Trial 3 outcomes), not v8 of this proposal.

If MVP empirical signal falsifies a v5/v6/v7 commitment, v8 is warranted. If MVP runs clean within the v7 envelope, the design is operative; further evolution happens at the implementation layer informed by observed system behavior, not at the design layer informed by additional text-layer review.

---

## 16. One sentence

The Ergon learner v7 is the consolidated final design pre-MVP — a closed-loop scientific learning system for empirical mathematical patterns that hardens v5+v6's defensive surface against the residual-gaming attractor, specifies the exact MVP execution as three small incremental trials gating each subsequent investment, registers ten architectural risks with explicit early-detection signals, lists the open-source libraries to borrow (PEFT + TRL + pyribs + DEAP + bitsandbytes + vLLM + Axolotl-or-Unsloth + PostgreSQL/pgvector/TimescaleDB + Redis), names the substrate-specific components to build (Σ-kernel + arsenal genome representation + five-counts diagnostic + Techne meta-loop + trivial-pattern detector + agreement-weighted reward orchestration), commits to no-RAG at MVP and limited within-substrate-only RAG at v1.0+ with strict lineage tagging, plans a five-base v0.5 LoRA ablation (Llemma + DeepSeek-Math + Qwen-Math + Llama-3.1 + Qwen-general) before v1.0 production base selection, specifies real-time analytics with eight alert classes, runs at $400-1100/mo at v1.0 (three orders of magnitude below Silver's $1B), and explicitly commits the next filed document to be MVP empirical results rather than v8 — in service of the design principle that truth must stay harder to satisfy than generation is to produce, at every level of the verification stack including the residual classifier itself.

— Ergon, on behalf of the Prometheus agent ensemble
