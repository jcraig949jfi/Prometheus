# Ergon MVP Plan — Day-by-Day

**Start:** 2026-05-04
**Target completion:** 2026-05-18 (Day 15)
**Deadline:** 2026-06-03 (Day 30; 15-day buffer for debugging interaction effects)

Per v8: design frozen; the next document filed in `pivot/` is the MVP run report or simulation analysis, NOT v9. v9 is conditional on Trial 1, 1.5, or 3 falsifying the residual-gradient hypothesis OR a round-7 review surfacing critiques of round-3-or-4 depth.

---

## Day 1–4 — Trial 1: Adversarial Residual Benchmark

**Goal:** Is the residual classifier accurate enough to serve as reward signal?

**Day 1 — Sample curation pass A: obvious noise (50 samples)**
- FP-quantization residuals (10 samples)
- MC-seed jitter residuals (10 samples)
- Gaussian residuals at noise-floor magnitude (10 samples)
- Uniform-distribution residuals from random polynomial draws (10 samples)
- Empty / zero residuals (10 samples)

**Day 2 — Sample curation pass B: borderline signal (50 samples)**
- Mercury perihelion residual at low-confidence regime (5 samples)
- Ramanujan-Hardy asymptotic residuals at marginal n (5 samples)
- Riemann Li(x)−π(x) at x where difference hardest to distinguish (5 samples)
- F1+F6+F9+F11 calibration drift events from the 180-known-truth set (15 samples)
- BSD-conditional residuals in the empirical-pattern domain (10 samples)
- Modular-form coefficient mystery residuals (10 samples)

**Day 3 — Sample curation pass C: synthetic structured-noise (100 samples)**
- High-coefficient-variance residuals from random polynomial draws (30 samples)
- Canonicalizer-subclass-matching residuals built from random hash collisions (30 samples)
- Fake-drift fingerprints from time-correlated noise (20 samples)
- Cyclotomic-near-miss residuals (M=1+ε for small ε) (20 samples)

**Day 4 — Run benchmark + report**
- Run `sigma_kernel/residuals.py:_classify_residual` on all 200 samples
- Compute: overall accuracy; per-class FP rate (especially synthetic structured-noise); ECE across 5 confidence bins
- Determine w_R activation tier per v8 §2.6 specification
- Output: `ergon/learner/trials/trial_1_results.json` + `ergon/learner/trials/TRIAL_1_REPORT.md`

**Acceptance:** ≥85% accuracy; ≤5% FP on synthetic structured-noise (target ≤2% for full w_R); ECE ≤0.05.

**Failure path:** If FP >10%, halt MVP; revert to PROMOTE-only architecture; substrate-grade negative result on residuals-as-reward.

---

## Day 5–7 — Trial 1.5: Adversarial Optimization Probe

**Goal:** Is the residual classifier robust under closed-loop adversarial optimization?

**Day 5 — Probe scaffold**
- Implement hill-climbing optimizer over genome space
- Frozen classifier (no further training during probe)
- Objective function: `confidence_signal_class - 10 * battery_pass_indicator`

**Day 6 — Run probe (500-2000 iterations)**
- 4 random restarts × 500 iterations each
- Log every candidate's (genome_hash, classifier_confidence, battery_pass)
- Detect exploits: signal-class confidence ≥0.85 + battery_pass=False

**Day 7 — Analyze + report**
- Cluster exploits with Trial 1's synthetic-structured-noise samples (K-means on feature embeddings)
- If exploits found: add to synthetic-structured-noise benchmark; retrain classifier; re-run Trial 1
- Output: `ergon/learner/trials/trial_1_5_results.json` + `TRIAL_1_5_REPORT.md`

**Acceptance:** No exploit found in <500 iterations.

**Failure path:** Exploit in <100 iterations → classifier structurally insufficient; revert to PROMOTE-only. Exploit in 100-500 after retraining → architectural revision needed; hold MVP.

---

## Day 8–17 — Trial 2: Evolutionary Engine with Bounded Buckets

**Goal:** Does Ergon's MAP-Elites with bounded buckets + F_TRIVIAL_BAND_REJECT + minimum-share enforcement produce more structured outputs than uniform random?

This is the bulk of MVP work — ~10 days for ~6 net-new components plus their interaction effects (the hidden time sink per round-6b review).

**Day 8 — Genome representation**
- Implement `Genome` dataclass over arsenal atoms (`prometheus_math.arsenal_meta`)
- Deterministic content hashing (sha256 over canonical DAG serialization)
- Type-checking against arg_type signatures

**Day 9 — Operators: structural + symbolic + uniform + structured_null**
- 4 operator implementations as `MutationOperator` protocol
- Lineage tagging on every mutation
- Tests for type-discipline preservation

**Day 10 — Operator: anti_prior with KL + descriptor enforcement**
- Build `corpus_frequency_stats` database (Mathlib + Proof-Pile-2 frequency analysis; ~5GB)
- Implement KL divergence ≥1.0 nat per claim check
- Implement descriptor-displacement check (cell not occupied by `neural` operator outputs in any prior 10K window — at MVP: relax to "cell not occupied by any prior-shaped operator")
- Failure flag: `anti_prior_failed_divergence`

**Day 11 — MAP-Elites archive + descriptor**
- pyribs-based archive with pointer-storage discipline (heavy data in Postgres)
- 5-axis descriptor: canonicalizer subclass + DAG entropy + output-type signature + bounded magnitude bucket + canonical-form distance
- Total cells: 5,000

**Day 12 — Magnitude perturbation-stability check**
- For magnitude buckets 4 and 5 ([10⁹, 10¹²) and [10¹², ∞)):
  - Input jitter test: ε=0.001 across 100 trials, ≥95% same bucket
  - Half-precision recompute test: same bucket
- Failures route to `out_of_band` cell; F_MAGNITUDE_STABILITY_REJECT kill-test

**Day 13 — Trivial-pattern detector (F_TRIVIAL_BAND_REJECT)**
- 4 static signatures: small-number coincidence, prime-density artifact, scale rescaling, cyclotomic root-of-unity coincidence
- 2 temporal signatures: recurrence density (Jaccard ≥0.9 to ≥3 prior in same lineage / 1K window), novelty decay (avg distance decrease ≥30% / 1K window)

**Day 14 — Operator-class scheduler with minimum-share enforcement**
- Cell-selection policy with coverage-pressure reweighting (cells filled by LLM operators downweighted at MVP — but no neural yet, so this is groundwork)
- Minimum-share enforcement: uniform ≥5%, anti_prior ≥5%, structured_null ≥5%; total non-prior ≥15%

**Day 15 — Per-axis fill-rate audit + cross-correlation**
- Every 1K-episode window: per-axis fill distribution; cross-correlation matrix
- Flag axes >70% concentration; flag axis pairs |corr|>0.7
- Hot-swap protocol: pre-specified replacement candidates per axis (descriptor_config.toml)

**Day 16 — Counterfactual logging hook**
- 5% sampled episodes flagged `counterfactual_cohort=True`
- Record: reward under v8 weights vs PROMOTE-only; outcome under no F_TRIVIAL_BAND_REJECT; outcome under w_R=0
- Storage: `sigma_proto.counterfactual_outcomes` TimescaleDB hypertable

**Day 17 — Run Trial 2 + report**
- 1K episodes, 5 operator classes (no neural yet)
- Compare to 1K-episode uniform-only baseline
- Measure: signal-class-residual rate per operator; cell-fill distribution per axis; F_TRIVIAL_BAND_REJECT trigger rate; descriptor non-degeneracy
- Output: `ergon/learner/trials/trial_2_results.json` + `TRIAL_2_REPORT.md`

**Acceptance:** Primary `structural ≥1.5× uniform` on signal-class-residual rate. Secondary fill ≥20-30%. Tertiary no axis >70% concentration.

---

## Day 18–22 — Trial 3: Five-Counts Diagnostic

**Goal:** Does the five-counts diagnostic distinguish operator classes at affordable budget?

**Day 18 — Five-counts harness extension**
- Extend existing `prometheus_math/four_counts_pilot.py` to five counts
- Add count 5: signal-class-residual rate (battery-killed CLAIMs with classifier confidence ≥0.7)
- Welch t-test + Holm correction on BOTH PROMOTE rate AND signal-class-residual rate

**Day 19 — Cell-level correlation tracking**
- Per-cell signal-class-residual rate (averaged over 1K-episode windows)
- Per-cell eventual PROMOTE rate
- Pearson correlation residual→PROMOTE per operator class

**Day 20 — Run pilot: 3K episodes × 3 arms (uniform, structural, symbolic)**
- 9K total episodes
- Track absolute residual density, absolute PROMOTE density, correlation per arm

**Day 21 — Analyze + report**
- Five counts per arm with statistical comparison
- Stage-3.5 proxies: permutation-distance + frequency-weighted recall (per v5 §7.4)
- Output: `ergon/learner/trials/trial_3_results.json` + `TRIAL_3_REPORT.md`

**Day 22 — Buffer day for trial 3 debugging**

**Acceptance:** Residual density ≥0.05 for ≥1 class; PROMOTE measurable for ≥1 class; correlation residual→PROMOTE ≥0.3.

---

## Day 23–30 — Buffer + reporting

**Day 23-27:** Reserved for debugging interaction effects across trials (the round-6b reviewer's hidden time sink).

**Day 28-29:** Synthesize MVP run report:
- Trial 1, 1.5, 2, 3 outcomes consolidated
- Compare against round-4 + round-6b reviewer simulations (received in parallel)
- Identify which v8 commitments held / were falsified
- Recommend v0.5 commitment OR v9 revision OR architectural pivot

**Day 30:** File `pivot/MVP_run_report_<date>.md` and `roles/Ergon/SESSION_JOURNAL_<date>.md`. Begin v0.5 if MVP greenlights.

---

## Risk-mitigation checklist (per v8 §5)

- [ ] R1 (residual classifier benchmark fails): Trial 1 directly tests; failure → revert to PROMOTE-only
- [ ] R2 (PROMOTE rate too sparse): power calculation in v6 §7.5; five-counts diagnostic mitigates
- [ ] R3 (cross-model contamination): not load-bearing at MVP (no cross-model evaluator yet at MVP scope)
- [ ] R4 (anti_prior generates structured noise): `residual_signal_precision` per-operator tracks; v8 KL+descriptor enforcement strengthens
- [ ] R5 (descriptor degeneracy): per-axis audit + hot-swap protocol active from Day 15
- [ ] R6 (compute overrun): MVP at $0/mo; not load-bearing until v0.5
- [ ] R7 (HITL bottleneck): 24-hour auto-escrow SLA active from Day 1
- [ ] R8 (residual-gaming attractor): five-layer defensive surface per v5 §11.6
- [ ] R9 (Llemma LoRA saturation): not load-bearing at MVP (no LoRA yet)
- [ ] R10 (trivial-pattern detector misses real wells): F_TRIVIAL_BAND_REJECT signature library extensible via Techne meta-loop
- [ ] R11 (false gradient lock-in): periodic null-env runs every 50K episodes (not in MVP scope; v0.5)
- [ ] R12 (API drift): not load-bearing at MVP (no external APIs)
- [ ] R13 (DB IOPS limits): batched telemetry writes (default 100 events/write); applied from Day 1

---

## Logging targets active from Day 1

- Per-CLAIM provenance (kernel default)
- Per-FALSIFY verdict (kernel default)
- Per-PROMOTE event (kernel default)
- Per-Residual classification (residual primitive default)
- `operator_per_window_metrics` (TimescaleDB hypertable; 1K-episode aggregates)
- `cell_fill_distribution` (per-cell historical occupancy)
- `descriptor_audit_events` (per-axis fill-rate audit results)
- `compute_consumption` per iteration

Real-time alerts active from Day 1 (per v7 §8):
- `residual_classifier_failing` (precision <0.10 across 2 windows)
- `descriptor_axis_collapsed` (>70% concentration)
- `f_trivial_reject_anomalous` (rate outside [5%, 30%])

---

## Non-MVP scope (deferred to v0.5+)

Per v8 progression:

- Cross-model agreement evaluator (LiteLLM-based; v0.5)
- Held-out battery audit (v0.5)
- Non-LLM evaluator (numeric perturbation for Lehmer-Mahler; v0.5)
- Periodic prior detox (v0.5)
- Techne meta-loop (v0.5)
- LoRA on Llemma-7B (v1.0)
- Three-base ablation (Llemma + Qwen2.5-Math + Llama-3.1-8B; v0.5)
- External_llm operator with API rotation (v0.5)
- v1.5 learned representations (graph-attention DAG encoder)
- v2.0 multi-model ensemble + arXiv preprint

— Ergon
