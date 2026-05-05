# Ergon Architecture — v8 Design Freeze

**Date:** 2026-05-03
**Status:** Design frozen. MVP build starts 2026-05-04. v9 is conditional on Trial 1, 1.5, or 3 falsifying the residual-gradient hypothesis OR a round-7 review surfacing critiques of round-3-or-4 depth.

## What v8 is

v8 is a focused delta from v7 (commit 9cafeb35), produced after a round-6 external review with two reviewers — one operational tier (ChatGPT), one architectural-operational tier. Both round-6 reviewers consider the design ready for empirical signal after v8 ships. v8 is not a fundamental rearchitecting; it's a defensive surface upgrade catching the failure modes the v7 operational specs alone create.

The design proceeded through six rounds of frontier-model review (round 1 → v2; round 2 → v3 with design-freeze recommendation; round 3 → v4 correcting internal contradictions; round 4 → v5 full architectural treatment; round 5 → v6 operational refinements via Gemini; round 6 → v7 final + v8 focused delta). Each round paired verbatim reviews with meta-analyses; commits preserve both for substrate-grade traceability.

## The four-trial structure

The MVP runs four sequential trials (one is named 1.5 because it was inserted between 1 and 2 in v8). Each gates the next.

### Trial 1 (Days 1–4) — Adversarial Residual Benchmark

**Concept tested:** Is the residual classifier accurate enough to serve as reward signal?

**Method:** Run `sigma_kernel/residuals.py:_classify_residual` on 200 curated samples spanning obvious noise (50), borderline signal (50), and synthetic structured-noise (100). Compute overall accuracy, per-class FP rate, and Expected Calibration Error across 5 confidence bins.

**Acceptance:** ≥85% accuracy; ≤5% FP on synthetic structured-noise (target ≤2% for full w_R activation); ECE ≤0.05.

**Failure path:** If FP >10%, halt MVP; revert to PROMOTE-only architecture; substrate-grade negative result on residuals-as-reward.

### Trial 1.5 (Days 5–7) — Adversarial Optimization Probe

**Concept tested:** Is the residual classifier robust under closed-loop adversarial optimization, not just i.i.d. evaluation?

This trial was added in v8 because reviewer B (round 6) identified that classification accuracy on i.i.d. samples does not predict classifier robustness under the actual training regime, which is closed-loop adversarial optimization.

**Method:** Freeze the residual classifier post-Trial-1 (no further training). Run a tiny optimizer (random search + simple hill climbing, no neural component) for 500–2000 iterations. Objective: maximize classifier confidence on signal-class WITHOUT passing the kill battery. Each iteration generates a candidate genome, evaluates against classifier, runs against battery, scores: `confidence_signal_class - 10 * battery_pass_indicator`.

**Acceptance:** No exploit found in <500 iterations.

**Failure paths:**
- Exploit in <100 iterations → classifier structurally insufficient even after retraining; revert to PROMOTE-only reward; substrate-grade negative result on v4's promotion of residuals to first-class reward
- Exploit in 100–500 after retraining → classifier requires architectural revision; hold MVP
- No exploit in 500 but found in 500–2000 → classifier borderline; w_R activates at half-strength regardless of Trial 1 tier

This trial gates Trial 2. Running Trial 2 with a gameable classifier wastes the evolutionary engine's effort on chasing residual rewards that don't predict promotions.

### Trial 2 (Days 8–17) — Evolutionary Engine with Bounded Buckets

**Concept tested:** Does Ergon's MAP-Elites with bounded buckets, F_TRIVIAL_BAND_REJECT, and minimum-share enforcement produce more structured outputs than uniform random?

**Method:** 1K episodes, 5 operator classes (no neural yet — that's v0.5+). Compare to 1K-episode uniform-only baseline. Measure: signal-class-residual rate per operator; cell-fill distribution per axis; F_TRIVIAL_BAND_REJECT trigger rate; descriptor non-degeneracy.

**Acceptance (revised in v8 from v7):**
- **Primary:** `structural` operator's signal-class-residual rate ≥1.5× the `uniform` operator's rate (selection pressure produces more structured outputs than random; this is the load-bearing question)
- **Secondary:** Absolute cell fill ≥20–30% (basic exploration health; not failing if low)
- **Tertiary:** No single axis has fill-rate concentration >70% in one bin (descriptor non-degeneracy check)

The v7 spec asked for ≥60% cell fill across all 5 axes; reviewer B flagged this as optimistic for 1K episodes with 5,000 cells, sparse reward, no neural guidance. The revised primary captures whether selection pressure produces signal beyond noise — which is the actual question Trial 2 should answer.

This is the bulk of MVP work — ~10 days for ~6 net-new components plus their interaction effects (round-6b reviewer flagged interaction effects as the hidden time sink).

### Trial 3 (Days 18–22) — Five-Counts Diagnostic

**Concept tested:** Does the five-counts diagnostic distinguish operator classes at affordable budget?

**Method:** Extend existing `prometheus_math/four_counts_pilot.py` to five counts (adding signal-class-residual rate as count 5). Run 3K episodes × 3 arms (uniform, structural, symbolic) — 9K total episodes. Welch t-test + Holm correction on BOTH PROMOTE rate AND signal-class-residual rate.

**Acceptance (revised in v8 from v7):**
- **Absolute residual density:** signal-class-residual rate per 1K episodes ≥0.05 for at least one operator class
- **Absolute PROMOTE density:** PROMOTE rate per 10K episodes is measurable for at least one operator class (≥1 PROMOTE in 10K episodes for the strongest arm)
- **Correlation residual→PROMOTE:** Pearson correlation between cell-level signal-class-residual rate and same-cell eventual PROMOTE rate ≥0.3

The v7 spec asked for "Signal-class-residual rate ≥10× the PROMOTE rate." Reviewer B flagged: PROMOTE is policy-dependent sparse, ratio collapses even when system improves. The correlation framing answers "do residuals predict promotions" rather than "are they 10× more frequent" — meaningful even at low absolute rates AND meaningful at high absolute rates. It's the stable measurement.

## MVP code structure

```
ergon/learner/
├── README.md                 — entry point
├── MVP_PLAN.md               — day-by-day execution
├── genome.py                 — Genome dataclass; typed DAG over arsenal atoms
├── archive.py                — MAP-Elites archive with content-aware 5-axis descriptor
├── descriptor.py             — Behavior descriptor (hot-swappable per v5 §6.2)
├── scheduler.py              — Operator-class scheduler with minimum-share enforcement
├── reward.py                 — Agreement-weighted reward (substrate + cross-model + holdout + non-LLM + residual)
├── triviality.py             — F_TRIVIAL_BAND_REJECT signature library (4 static + 2 temporal)
├── stability.py              — Magnitude perturbation-stability check
├── operators/
│   ├── structural.py         — DAG topology mutation
│   ├── symbolic.py           — Argument-value mutation
│   ├── anti_prior.py         — Anti-correlated with corpus frequency stats
│   ├── uniform.py            — Strawman null
│   └── structured_null.py    — Type-respecting null
├── trials/
│   ├── trial_1_residual_benchmark.py
│   ├── trial_1_5_optimization_probe.py
│   ├── trial_2_evolutionary_engine.py
│   └── trial_3_five_counts_diagnostic.py
└── tests/                    — pytest suites per module
```

## Library commitments (v8 §10)

Adopted from ChatGPT round-6a recommendations:

- **PyTorch 2.x** — primary ML
- **Hugging Face Transformers + PEFT + TRL + bitsandbytes** — LoRA stack (v0.5+)
- **Unsloth** — LoRA training at MVP (faster, less VRAM than Axolotl)
- **vLLM** — inference serving (v0.5+)
- **pyribs** — MAP-Elites archive (with pointer-storage discipline; heavy data in Postgres)
- **DEAP** — genetic operator implementations
- **LiteLLM** — cross-model evaluator API standardization (v0.5+)
- **scipy.stats** — Welch t-test, Holm correction, Expected Calibration Error
- **PostgreSQL + pgvector + TimescaleDB** — substrate storage
- **Redis 7+** — agora message bus
- **structlog + Grafana** — observability

## Five-axis descriptor (MAP-Elites behavior characteristics)

The archive cells are keyed on a 5-axis descriptor:

1. **Canonicalizer subclass** — group_quotient / partition_refinement / ideal_reduction / variety_fingerprint (per Charon's canonicalizer.md)
2. **DAG entropy** — structural complexity of the genome's typed-action DAG
3. **Output-type signature** — the type signature of the genome's terminal output
4. **Bounded magnitude bucket** — discrete bins over output magnitude (5 bins: tiny, small, medium, large, [10⁹, 10¹²), [10¹², ∞))
5. **Canonical-form distance** — distance between the genome's output and its canonical-form representation

Total cells: 5,000.

The descriptor is **hot-swappable** per v5 §6.2: per-axis fill-rate audit every 1K episodes; if any axis exceeds 70% concentration in one bin, swap the offending axis with a pre-specified replacement candidate from `descriptor_config.toml`.

## Reward function (v8)

Agreement-weighted across five evaluators:

```
r = w_S * substrate_verdict     # PROMOTE/WARN/BLOCK from kernel
  + w_C * cross_model_agreement # 5-evaluator vote (v0.5+)
  + w_H * holdout_battery       # held-out subset of F1+F6+F9+F11 (v0.5+)
  + w_N * non_llm_evaluator     # numeric perturbation for Lehmer-Mahler (v0.5+)
  + w_R * residual_signal       # signal-class confidence from residual classifier
```

w_R activation is tier-conditioned on Trial 1 outcomes: full at ≥85% accuracy + ≤2% FP on structured-noise; half at ≥85% accuracy + 2-5% FP; zero at <85% accuracy or >5% FP. Trial 1.5 (adversarial probe) provides additional gating.

At MVP scope, only `substrate_verdict` and `residual_signal` are active. Cross-model, holdout, and non-LLM evaluators are deferred to v0.5.

## Six anti-gaming patterns (v8)

These are surfaces an RL agent will route to if not closed:

1. **Magnitude axis bucketing** — bounded buckets prevent agents from inflating magnitude for free reward
2. **Magnitude perturbation stability** — buckets 4 and 5 require ε=0.001 jitter test (≥95% same bucket across 100 trials) AND half-precision recompute test
3. **Trivial-band rejection (F_TRIVIAL_BAND_REJECT)** — 4 static signatures (small-number coincidence, prime-density artifact, scale rescaling, cyclotomic root-of-unity coincidence) + 2 temporal signatures (recurrence density, novelty decay)
4. **Anti-prior with KL + descriptor enforcement** — KL divergence ≥1.0 nat per claim against corpus frequency stats; descriptor-displacement check
5. **Minimum-share enforcement** — uniform ≥5%, anti_prior ≥5%, structured_null ≥5%; total non-prior ≥15%
6. **Counterfactual logging** — 5% sampled episodes flagged `counterfactual_cohort=True`; record reward under v8 weights vs PROMOTE-only; outcome under no F_TRIVIAL_BAND_REJECT; outcome under w_R=0

The counterfactual logging is the substrate's defense against silent reward-shaping drift — even if the active reward function gets gamed, the counterfactual cohort's outcomes are reproducible and audit-able.

## Where to find more

- v8 spec: `pivot/ergon_learner_proposal_v8.md`
- v7 full operational treatment: `pivot/ergon_learner_v7_final.md`
- v5 architectural canonical: `pivot/ergon_learner_proposal_v5.md`
- Round-6 reviews: `pivot/feedback_ergon_review_round6a_chatgpt_2026-05-03.md`, `pivot/feedback_ergon_review_round6b_2026-05-03.md`
- Round-6 meta-analysis: `pivot/meta_analysis_ergon_round6_2026-05-03.md`
