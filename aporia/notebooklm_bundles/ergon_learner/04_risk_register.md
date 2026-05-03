# Ergon Risk Register — R1 through R13

**Date:** 2026-05-03 (v8 design freeze)
**Source:** `pivot/ergon_learner_proposal_v8.md` §5 + companions

The risk register is the substrate's mechanical pre-mortem on the MVP. Each risk has severity, likelihood, mitigation, and (where applicable) the trial that directly tests it. R11–R13 were added in v8 from round-6 reviewer surfacing.

## R1 — Residual classifier benchmark fails

**Severity:** High (gates Trial 2; affects entire reward architecture)
**Likelihood:** Medium

The residual classifier is supposed to provide a dense gradient signal beyond the binary PROMOTE/BLOCK reward. If Trial 1 shows FP >10% on synthetic structured-noise, the classifier is too brittle to serve as reward.

**Mitigation:**
- Trial 1 directly tests with 200 curated samples
- Failure path: revert to PROMOTE-only architecture; w_R = 0; substrate-grade negative result on v4's promotion of residuals to first-class reward
- Recovery is structural, not operational — the architecture explicitly contemplates this failure mode

## R2 — PROMOTE rate too sparse

**Severity:** High (would invalidate the absolute-rate measurement in Trial 3)
**Likelihood:** Medium-High

PROMOTE is the strongest signal but also the rarest. If 9K episodes produces zero PROMOTEs across all three arms, the experiment can't distinguish operator classes on PROMOTE rate.

**Mitigation:**
- Power calculation in v6 §7.5 derives expected PROMOTE rate per arm
- Five-counts diagnostic in Trial 3 mitigates by adding signal-class-residual rate (denser signal) as the primary measurement
- Correlation residual→PROMOTE is the stable measurement that works at any density
- Failure path: if zero PROMOTE, shift to residual signal as primary gradient; v0.5 development continues

## R3 — Cross-model contamination

**Severity:** Medium (affects v0.5 evaluator architecture, not MVP)
**Likelihood:** Low at MVP scope

Cross-model agreement evaluator depends on multiple frontier APIs. If models share training data (likely for Claude/GPT/Gemini), agreement is correlated rather than independent.

**Mitigation:**
- Not load-bearing at MVP (no cross-model evaluator in scope)
- v0.5 design includes diversity scoring per evaluator
- LiteLLM standardization isolates model-specific bias

## R4 — anti_prior generates structured noise

**Severity:** Medium (affects Trial 2 primary criterion)
**Likelihood:** Medium

The `anti_prior` operator is designed to produce outputs anti-correlated with corpus frequency. If "anti-correlated" maps to "structured noise that classifies as signal," the classifier confidence inflates without real discovery.

**Mitigation:**
- `residual_signal_precision` per-operator tracks; anti_prior's signal rate is compared to its actual PROMOTE rate
- v8 KL+descriptor enforcement strengthens: KL divergence ≥1.0 nat per claim check + descriptor-displacement requirement
- F_TRIVIAL_BAND_REJECT signature library includes patterns specifically targeting structured-noise-from-anti-correlation

## R5 — Descriptor degeneracy

**Severity:** Medium (Trial 2 tertiary acceptance criterion would fail)
**Likelihood:** Medium

If one or more of the 5 descriptor axes pins to a single value (e.g., output_type_signature collapses because all DAGs return the same type), the archive degenerates from 5,000 cells to fewer effective dimensions.

**Mitigation:**
- Per-axis fill-rate audit every 1K episodes (Day 15 of MVP)
- Hot-swap protocol active from Day 15: per-axis pre-specified replacement candidates in `descriptor_config.toml`
- Tertiary acceptance criterion catches this: no single axis >70% concentration

## R6 — Compute overrun

**Severity:** Low (MVP only; load-bearing at v0.5)
**Likelihood:** Low at MVP

MVP runs at $0/month cloud spend. Could exceed budget if scale grows or if external APIs are accidentally invoked.

**Mitigation:**
- MVP commits to $0/mo
- Not load-bearing until v0.5
- v0.5 will add cost monitoring + circuit breakers before any external API integration

## R7 — HITL bandwidth bottleneck (REVISED in v8)

**Severity:** Medium-High (could block real-time progress if bandwidth is exceeded)
**Likelihood:** Medium

Human-in-the-loop decisions could pile up faster than they can be reviewed. Originally v7 had no SLA; v8 adopts ChatGPT round-6a recommendation.

**Mitigation:**
- **24-hour auto-escrow SLA.** Any decision requiring HITL that isn't answered within 24 hours auto-escrows the claim (status: `HITL_ESCROW_TIMEOUT`); the system continues
- Escrowed claims surface in a weekly HITL queue rather than blocking real-time progress
- Active from Day 1

## R8 — Residual-gaming attractor

**Severity:** High (would invalidate residual signal entirely)
**Likelihood:** Medium

RL agents will route to whatever the reward function makes cheap. If signal-class confidence is rewarded without battery survival, the agent learns to produce confidence-inflating-but-substantively-empty outputs.

**Mitigation:**
- **Five-layer defensive surface per v5 §11.6:**
  1. Trial 1.5 adversarial optimization probe (active gate before Trial 2)
  2. F_TRIVIAL_BAND_REJECT static + temporal signatures
  3. Magnitude perturbation-stability check
  4. Counterfactual logging cohort (5% of episodes)
  5. Periodic null-environment runs (R11 mitigation; v0.5)

## R9 — Llemma LoRA saturation

**Severity:** Medium (affects v1.0 LoRA training, not MVP)
**Likelihood:** Medium

LoRA training on Llemma-7B might saturate with limited training data, producing a model that's worse than the base.

**Mitigation:**
- Not load-bearing at MVP (no LoRA in scope)
- v1.0 design includes three-base ablation (Llemma + Qwen2.5-Math + Llama-3.1-8B) to detect single-base saturation
- v0.5 will add LoRA performance monitoring

## R10 — Trivial-pattern detector misses real wells

**Severity:** Medium (false negative on F_TRIVIAL_BAND_REJECT lets gameable patterns through)
**Likelihood:** Medium

The 6 trivial-pattern signatures (4 static + 2 temporal) might not catch all known trivial patterns. False negative would let agents discover gameable wells.

**Mitigation:**
- F_TRIVIAL_BAND_REJECT signature library is **extensible via Techne meta-loop** (v0.5)
- New patterns can be added as signatures without architectural change
- Counterfactual logging cohort lets us measure what F_TRIVIAL_BAND_REJECT would catch retroactively
- Real-time alert: `f_trivial_reject_anomalous` (rate outside [5%, 30%])

## R11 — False gradient lock-in (NEW in v8)

**Severity:** High (illusory success; worse than failure)
**Likelihood:** Medium

System finds a consistent but wrong signal proxy, passes all local checks, becomes dominant in archive. Symptoms: good metrics, no real discoveries.

**Mitigation:**
- **Periodic null-environment runs** every 50K episodes: run policy on a known-truth synthetic env where ground truth is fully visible; verify PROMOTE-rate matches expected. Significant divergence flags lock-in.
- **Cross-domain validation** every 100K episodes: port learned policy to a different env (DiscoveryEnv → ObstructionEnv or vice versa); measure transfer. High-original-env metrics + transfer failure is the lock-in signature.
- **Forced archive resets** every 200K episodes: randomly reset 5% of cells; if metrics don't recover within 50K episodes, those cells were holding lock-in elites.
- Early-detection: pattern of stable PROMOTE rate combined with declining novelty (low canonical-form distance distribution shift) over consecutive 100K windows.

Not in MVP scope (deferred to v0.5).

## R12 — API deprecation/drift (NEW in v8)

**Severity:** Medium (affects longitudinal reproducibility, not MVP)
**Likelihood:** Medium-High

External LLM operator + cross-model evaluator depend on frontier APIs (Claude, Gemini, GPT). Silent model updates or deprecations break longitudinal reproducibility.

**Mitigation:**
- Pin model versions where API supports it (`claude-opus-4-7`, `gpt-5-2026-04`, `gemini-3-pro-2026-04`)
- Cache responses keyed on `(model_id, model_version, prompt_hash, claim_hash)` for reproducibility
- Version cross-model evaluator outputs as `(model_id, model_version, response_hash)` tuples
- Treat external_llm as a non-stationary mutation source; lineage-tag with API version

Not load-bearing at MVP (no external APIs).

## R13 — Database IOPS limits (NEW in v8)

**Severity:** Medium (affects scale, not MVP correctness)
**Likelihood:** Medium at scale

100K claims per cycle on budget Hetzner Postgres faces write-contention.

**Mitigation:**
- Batched telemetry writes (default: 100 events per write)
- Connection pooling (pgbouncer or psycopg3 native pooling)
- Partitioning strategy for `claims` table: per-month partitions; partitions older than 6 months move to cold storage
- Offload time-series writes to TimescaleDB hypertables (already chosen)
- Applied from Day 1

## Risk taxonomy summary

**Architectural risks** (would force v9 design change): R1, R8, R11
**Operational risks** (mitigated by infrastructure): R2, R5, R7, R10, R13
**Scale risks** (load-bearing at v0.5+): R3, R6, R9, R12
**Quality risks** (would degrade signal): R4

## What v8 added vs v7

R11, R12, R13 are new in v8. R7 was revised (added 24h auto-escrow SLA). The other ten risks are unchanged.

## Where to find more

- v8 risk register source: `pivot/ergon_learner_proposal_v8.md` §5
- v7 risk register: `pivot/ergon_learner_v7_final.md` §5
- Round-6 reviewer source for R11/R12/R13: `pivot/feedback_ergon_review_round6b_2026-05-03.md`
