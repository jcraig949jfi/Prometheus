# Ergon Learner — Proposal v8 (focused delta from v7)

### v8 absorbs round-6 architectural-operational concerns: adversarial optimization probe (new Trial 1.5), Trial 2 + Trial 3 success criteria revised, R11 (false gradient lock-in) + R12 (API drift) + R13 (DB IOPS) added to risk register, anti_prior enforcement strengthened with KL divergence + descriptor displacement, magnitude axis tied to perturbation stability, trivial-pattern detector temporal extension, cross-model agreement-novelty paired check, counterfactual logging, library/framework decisions adopted from ChatGPT recommendations. V8 is the genuine pre-MVP design freeze.

**Date:** 2026-05-03
**Status:** Focused delta from v7 (commit 9cafeb35). All §§ not explicitly modified below remain as specified in v7. Pasteable to frontier-model context windows alongside v7 as the canonical pair.
**Origin:** Round 6 external review — two reviewers, one operational tier (ChatGPT), one architectural-operational tier (unstated). Verbatims: [`feedback_ergon_review_round6a_chatgpt_2026-05-03.md`](feedback_ergon_review_round6a_chatgpt_2026-05-03.md), [`feedback_ergon_review_round6b_2026-05-03.md`](feedback_ergon_review_round6b_2026-05-03.md). Triage: [`meta_analysis_ergon_round6_2026-05-03.md`](meta_analysis_ergon_round6_2026-05-03.md).
**Companions (canonical architecture):** [`pivot/ergon_learner_v7_final.md`](ergon_learner_v7_final.md) for full operational treatment; v8 references its sections for unchanged content.

---

## Why v8 is a delta, not a full rewrite

Round-6 reviewer B identified three architectural-operational concerns that warrant v8 *as a focused delta* before MVP build (not after Trial 1 fails and we have to re-run): adversarial optimization probe missing from Trial 1; Trial 2 success criteria miscalibrated; the 10× residual-vs-PROMOTE hypothesis is brittle to dynamic baselines. Reviewer A (ChatGPT) is operational tier — concrete library/timeline/SLA recommendations.

Both round-6 reviewers consider the design ready for empirical signal after v8 ships. v8 is not a fundamental rearchitecting; it's a defensive surface upgrade catching the failure modes the v7 operational specs alone create.

---

## V8 changes

### Change 1 — §4 New Trial 1.5: Adversarial Optimization Probe

V7's Trial 1 measures the residual classifier on i.i.d. samples (50 obvious noise + 50 borderline signal + 100 synthetic structured-noise). Reviewer B's critique: classification accuracy on i.i.d. samples does not predict classifier robustness under closed-loop adversarial optimization, which is the actual training regime.

**v8 specification — Trial 1.5 (between Trials 1 and 2, Days 5–7):**

**Concept tested:** Is the residual classifier robust under adversarial optimization, not just i.i.d. evaluation?

**Implementation:**
- Freeze the residual classifier post-Trial-1 (no further training)
- Run a tiny optimizer (random search + simple hill climbing, no neural component) for 500–2000 iterations
- Objective: maximize classifier confidence on signal-class WITHOUT passing the kill battery
- Each iteration generates a candidate genome, evaluates against classifier, runs against battery, scores: confidence_signal_class - 10 * battery_pass_indicator
- Hill-climb in genome space toward exploits

**Success criteria:**
- No exploit found in <500 iterations
- If exploits found, the exploit patterns are added to the synthetic-structured-noise benchmark (signature library extension); classifier retrained; Trial 1 re-run

**Failure mode + adjustment path:**
- *Exploit found in <100 iterations:* classifier is structurally insufficient even after retraining. Revert to PROMOTE-only reward; w_R = 0; substrate-grade negative result on v4's promotion of residuals to first-class reward.
- *Exploit found in 100–500 iterations after retraining:* classifier requires architectural revision (not just retraining). Hold MVP; investigate.
- *No exploit in 500 iterations but found in 500–2000:* classifier is borderline; w_R activates at half-strength regardless of Trial 1 tier; flag for ongoing monitoring.

**Cost:** ~3 days local. $0 cloud spend.

This trial gates Trial 2 — running Trial 2 with a gameable classifier wastes the evolutionary engine's effort on chasing residual rewards that don't predict promotions.

### Change 2 — §4 Trial 2 success criteria revised

V7's Trial 2 success: "≥60% of cells filled across all 5 axes." Reviewer B: optimistic for 1K episodes with 5,000 cells, sparse reward, no neural guidance.

**v8 revised criteria:**
- **Primary:** `structural` operator's signal-class-residual rate is ≥1.5× the `uniform` operator's rate (selection pressure produces more structured outputs than random; this is the load-bearing question)
- **Secondary:** absolute cell fill ≥20–30% (basic exploration health; not failing if low)
- **Tertiary:** No single axis has fill-rate concentration >70% in one bin (descriptor non-degeneracy check)

The primary criterion captures whether selection pressure produces signal beyond noise, which is the actual question Trial 2 should answer.

**Failure mode + adjustment path** (revised):
- *Primary fails (`structural` ≤ `uniform`):* selection-pressure machinery isn't working. Either the fitness ranking inside cells is broken, the residual classifier isn't distinguishing structural-vs-uniform outputs (re-run Trial 1.5), or the action space is too constrained. Investigate before scaling.
- *Secondary fails (fill <20%):* at MVP scale, even basic exploration health isn't met. Likely the descriptor is too coarse for 1K episodes; consider scaling Trial 2 to 3K episodes before declaring failure.
- *Tertiary fails (axis concentration >70%):* hot-swap the offending axis per v5 §6.2 protocol; re-run Trial 2 with the swapped descriptor.

### Change 3 — §4 Trial 3 success criteria revised

V7's Trial 3 success: "Signal-class-residual rate ≥10× the PROMOTE rate." Reviewer B: PROMOTE is policy-dependent sparse, ratio collapses even when system improves.

**v8 revised criteria — three-measurement structure:**
- **Absolute residual density:** signal-class-residual rate per 1K episodes ≥0.05 for at least one operator class (sparse but non-zero)
- **Absolute PROMOTE density:** PROMOTE rate per 10K episodes is measurable for at least one operator class (≥1 PROMOTE in 10K episodes for the strongest arm)
- **Correlation residual→PROMOTE:** Pearson correlation between cell-level signal-class-residual rate (averaged over 1K-episode windows) and same-cell eventual PROMOTE rate ≥0.3 (positive predictive)

The correlation framing answers "do residuals predict promotions" rather than "are they 10× more frequent." Correlation is meaningful even at low absolute rates AND meaningful at high absolute rates — it's the stable measurement.

**Failure mode + adjustment path** (revised):
- *No PROMOTE in 9K episodes:* this is the §7.5 power-calculation reality check from v6. Joint upper bound on rate; not failure of v8 specifically. Continue v0.5 development; the residual signal becomes the primary gradient.
- *Residual density <0.05 across all classes:* signal-class-residual is too sparse to serve as gradient. Reduce w_R activation tier; revisit classifier confidence thresholds.
- *Correlation residual→PROMOTE ≤0.3:* signal-class residuals don't predict promotions. Gradient is noise. Revert to PROMOTE-only reward; substrate-grade negative result.
- *Correlation residual→PROMOTE between 0.3 and 0.5:* weak but real predictive signal. v0.5 proceeds with reduced confidence; close monitoring of `residual_signal_precision` per operator.

### Change 4 — §5 Risk register additions

**R11 (NEW): False gradient lock-in.** Severity: High. Likelihood: Medium.

System finds a consistent but wrong signal proxy, passes all local checks, becomes dominant in archive. Symptoms: good metrics, no real discoveries. Worse than failure — illusory success.

Mitigation:
- **Periodic null-environment runs** every 50K episodes: run the policy on a known-truth synthetic env where ground truth is fully visible; verify PROMOTE-rate matches expected under the synthetic env. Significant divergence flags lock-in.
- **Cross-domain validation** every 100K episodes: port the learned policy to a different env (DiscoveryEnv → ObstructionEnv or vice versa); measure transfer. High-original-env metrics + transfer failure is the lock-in signature.
- **Forced archive resets** every 200K episodes: randomly reset 5% of cells; if metrics don't recover within 50K episodes, those cells were holding lock-in elites.

Early-detection: pattern of stable PROMOTE rate combined with declining novelty (low canonical-form distance distribution shift) over consecutive 100K windows.

**R12 (NEW): API deprecation/drift.** Severity: Medium. Likelihood: Medium-High.

External_llm operator + cross-model evaluator depend on frontier APIs (Claude, Gemini, GPT). Silent model updates or deprecations break longitudinal reproducibility.

Mitigation:
- Pin model versions where API supports it (`claude-opus-4-7`, `gpt-5-2026-04`, `gemini-3-pro-2026-04`)
- Cache responses keyed on `(model_id, model_version, prompt_hash, claim_hash)` for reproducibility
- Version cross-model evaluator outputs as `(model_id, model_version, response_hash)` tuples
- Treat external_llm as a non-stationary mutation source; lineage-tag with API version; do not assume continuity across model deprecations

**R13 (NEW): Database IOPS limits.** Severity: Medium. Likelihood: Medium at scale.

100K claims per cycle on budget Hetzner Postgres faces write-contention.

Mitigation:
- Batched telemetry writes (default: 100 events per write)
- Connection pooling (pgbouncer or psycopg3 native pooling)
- Partitioning strategy for `claims` table: per-month partitions; partitions older than 6 months move to cold storage
- Offload time-series writes to TimescaleDB hypertables (already chosen) which optimize for high-volume insert

**R7 (REVISED): HITL bandwidth bottleneck.**

V7 had no specific SLA. v8 adopts ChatGPT's recommendation:

- **24-hour auto-escrow SLA.** Any decision requiring HITL that isn't answered within 24 hours auto-escrows the claim (status: `HITL_ESCROW_TIMEOUT`); the system continues. Escrowed claims surface in a weekly HITL queue rather than blocking real-time progress.
- HITL touchpoints concentrated on substrate-grade decisions (PROMOTE / META_CLAIM / architectural pivots), not implementation details.

### Change 5 — §3.5.1 anti_prior enforcement strengthened

V7 required `anti_prior` ≥5% share. Reviewer B: 5% share doesn't guarantee meaningful divergence; anti_prior can collapse into structured noise.

**v8 strengthened enforcement:**

- **KL divergence requirement.** Anti_prior outputs must have KL divergence from the corpus frequency distribution ≥1.0 nats per claim. The corpus frequency distribution is the `corpus_frequency_stats` database from v6 (Mathlib + Proof-Pile-2 frequency analysis).
- **Descriptor displacement requirement.** Anti_prior outputs must include cells that the `neural` operator has not filled in any prior 10K-episode window. Tracked per-cell: a cell is "neural-occupied" if any neural-class genome is or has been its elite in the last 10K episodes.
- **Failure handling.** If neither condition holds for an anti_prior output, the output is flagged `anti_prior_failed_divergence`; the operator's reward weight is downgraded by 50% for the next 1K-episode window; if the failure persists across multiple windows, anti_prior is functioning as a noisy null and the substrate is informed (META_CLAIM minted noting the operator's failure mode).

This makes anti_prior's distinct contribution measurable rather than assumed.

### Change 6 — §6.2 magnitude axis tied to perturbation stability

V7's bounded magnitude buckets prevent small-number / scale-rescaling exploits. Reviewer B notes that high-magnitude outputs correlate with computational instability and numerical noise.

**v8 specification:**

High-magnitude buckets (4 and 5: [10⁹, 10¹²) and [10¹², ∞)) require **perturbation stability check** before earning full credit:

- **Input jitter test.** ε=0.001 perturbation across 100 trials of the input args; ≥95% of trial outputs must land in the same magnitude bucket
- **Precision test.** Recompute the output at half-precision (float16); the output must land in the same magnitude bucket as full-precision

Genomes failing the stability check are binned in `out_of_band` cell instead of buckets 4 or 5. The stability check is itself a kill-test (`F_MAGNITUDE_STABILITY_REJECT`) that runs before the regular F1+F6+F9+F11.

### Change 7 — §6.2 trivial-pattern detector temporal extension

V7's F_TRIVIAL_BAND_REJECT used static signature matching (4 initial signatures: small-number coincidence, prime-density artifact, scale rescaling, cyclotomic root-of-unity). Reviewer B notes that a trivial pattern isn't just simple — it's repeatedly rediscovered with low variation.

**v8 added signatures:**

- **Recurrence density.** Claims with content-hash similarity (Jaccard over node-set + edge-set) ≥0.9 to ≥3 prior claims in the same operator-class lineage within a 1K-episode window. Triggers `F_TRIVIAL_BAND_REJECT_recurrence_density`.
- **Novelty decay per lineage.** Per-lineage measurement of consecutive-claim canonical-form distance; lineages where average distance decreases by ≥30% over a 1K-episode window are flagged as `F_TRIVIAL_BAND_REJECT_novelty_decay`.

The temporal signatures are added to the existing static signature library; total signatures: 6.

### Change 8 — §5.3 cross-model evaluator agreement-novelty paired check

V7 cross-model evaluator weight: w_X=0.15. Reviewer B: even with logical-consistency-only restriction, models share latent structural priors; high agreement on outputs near known catalog entries is prior-driven convergence.

**v8 paired check:**

When cross-model agreement is high (≥0.9) AND descriptor distance to nearest catalog entry is low (bottom quintile of axis 5), the agreement contribution to reward is multiplied by 0.5 (effective w_X for that claim becomes 0.075).

This downweights agreement that's likely prior-driven convergence rather than independent validation. The check is per-claim, not per-window — affects individual reward calculations, not operator weights.

### Change 9 — §8 counterfactual logging

V7's logging is comprehensive but doesn't isolate component contributions. Reviewer B's recommendation: counterfactual logging gives causal insight without separate ablation runs.

**v8 specification:**

5% of episodes are sampled as counterfactual cohort (uniform random sampling, lineage-tagged `counterfactual_cohort=True`). Each counterfactual episode records, alongside the actual reward:

- *Reward under PROMOTE-only weights* (w_S=1.0, all others=0): what would the agent have learned without residual gradient?
- *Outcome under no F_TRIVIAL_BAND_REJECT*: what would have happened if the trivial-pattern detector hadn't fired?
- *Outcome under w_R=0*: what would have happened without residual reward?
- *Outcome under different operator-class lineage*: if the genome had been generated by a different operator class, what would the cross-model evaluator have said?

The counterfactual data lives in `sigma_proto.counterfactual_outcomes` (TimescaleDB hypertable) and feeds a quarterly causal-attribution analysis: which architectural components are pulling weight, which are decorative.

### Change 10 — §6-7 library/framework decisions (ChatGPT adoptions)

V7 listed candidate libraries; v8 makes specific commitments per ChatGPT recommendations:

- **Unsloth at MVP** (faster, less VRAM overhead than Axolotl on consumer hardware). Axolotl deferred to v1.0 multi-node H100 runs.
- **pyribs storage discipline.** Archive stores only `(genome_content_hash, fitness_tuple)` pointers; heavy genome data lives in `sigma_proto.genomes` Postgres table. Pyribs memory footprint stays bounded.
- **LiteLLM** for cross-model evaluator API standardization. No LangChain (bloat); no roll-your-own.
- **TimescaleDB-push** confirmed for telemetry (no Prometheus pull-server added).
- **7-day hot retention + B2 archival cron** for verbose CLAIM logs. Cron exports CLAIM logs older than 7 days to JSONL, compresses, ships to B2; deletes from hot DB.
- **External_llm operator rotates APIs.** Claude → Gemini → GPT in sequence per call. Avoids monoculture bias within the operator class.

### Change 11 — §10 v0.5 ablation cut to 3 bases

V7 specified five bases. ChatGPT: excessive for 15-day MVP context and v0.5 budget.

**v8 v0.5 ablation candidates:**
- **Llemma-7B** — math specialist
- **Qwen2.5-Math-7B** — modern instruction specialist
- **Llama-3.1-8B** — general baseline (no math pretraining)

DeepSeek-Math-7B and Qwen2.5-7B-general are deferred. The three-base ablation spans the math-pretrained vs general axis; metric remains held-out-cell coverage divergence.

### Change 12 — §4 timeline buffered

V7 target: 15 days. Both reviewers: optimistic. Reviewer B realistic estimate: 20-25 days. ChatGPT recommendation: 30-day buffer.

**v8 timeline:**
- **Target:** 15 days for the three trials (now four including Trial 1.5)
- **Deadline:** 30 days
- **Buffer:** 15 days for debugging interaction effects between components (the hidden time sink reviewer B identified)

If MVP completes in 15 days, the buffer is available for early v0.5 prep work. If MVP runs into integration bugs, the buffer absorbs it without missing the 30-day commitment.

---

## Direct answer to ChatGPT's closing question

> *Which of the three incremental trials (Residual Benchmark, Evolutionary Engine, or Five-counts Diagnostic) do you anticipate will be the most difficult to implement locally?*

**Trial 2 (Evolutionary Engine) is the hardest.** Reasoning:

| Trial | Difficulty | Reasoning |
|---|---|---|
| Trial 1 | Easy | Pure data work — curate 200 samples, run existing classifier, compute metrics. ~4 days. Mostly data curation; classifier code already exists in `sigma_kernel/residuals.py`. |
| Trial 1.5 | Easy-Medium | Standalone optimizer loop; doesn't touch substrate. ~3 days. |
| Trial 3 | Medium | Extension of existing four-counts harness (`prometheus_math/four_counts_pilot.py`); add count 5; add Welch t-test on residual rate; add residual→PROMOTE correlation. ~5–7 days. Mostly statistical wiring on top of existing infrastructure. |
| **Trial 2** | **Hardest** | Net-new code: bounded-bucket descriptor + F_TRIVIAL_BAND_REJECT (with 6 signatures including 2 temporal) + perturbation-stability check + per-axis fill-rate audit + minimum-share scheduler + content-aware MAP-Elites with 4-of-5 axes either new or revised + anti_prior KL+descriptor enforcement. Each subcomponent independently bug-prone; their interaction is the hidden time sink. ~8–12 days realistic, possibly more. |

Trial 2 should be structured as the bulk of MVP work, with Trials 1 and 3 as bookends.

---

## What v8 does NOT change from v7

For external reviewers reading v8 in isolation: all of the following remain as specified in v7 and are *unchanged* in v8. Read v7 for full treatment:

- §1 market context (Silver $1B framing)
- §2 background sections 2.1-2.9 (Prometheus / Σ-kernel / BIND/EVAL / arsenal / battery / residual primitive / pipeline / envs / agora)
- §3 architectural summary (seven operator classes; agreement-weighted reward formula; five-counts diagnostic; defensive surface against residual-gaming attractor)
- §3.5.2-3.5.3 (coverage-pressure cell selection; periodic prior detox)
- §3.5.4 minimum proposal-share enforcement (≥5% per non-prior class)
- §3.5.5 residual_signal_precision per operator
- §3.6 null-world baselines
- §3.7 Mathlib comparison class
- §5.1-5.2 base model + three task adapters with structural decoupling
- §5.4-5.6 adversarial cycles + self-play loop + training data rings
- §6.1, 6.3, 6.4 action space + 7 mutation operator classes + feature representation
- §7 discovery preservation in fitness predictor (Task B)
- §9 progression MVP→v2.0
- §10 empirical maturity caveats
- §11 (the does-not-claim list)
- §11.5 Techne meta-loop
- §11.6 residual-gaming attractor as bear case + defensive surface
- §13 Silver-ingestion (three substrate-ingestible fragments)
- §14 20-year position
- §15 first principle ("truth stays harder to satisfy than generation is to produce")

V8 modifies sections 4 (trials), 5 (risk register, reward formula's paired check), 6.2 (descriptor magnitude axis + trivial-pattern detector temporal extension), 8 (counterfactual logging), 7 (library decisions), and adds §3.5.1.b (anti_prior strengthened enforcement).

---

## Empirical maturity caveats (v8 additions)

V7's caveats retained, plus:

- **Trial 1.5 adversarial-probe optimizer reach.** *Pilot data: TBD.* Whether 500-2000 hill-climbing iterations finds exploits depends on classifier topology; if the optimizer is too weak (random search alone) it may miss exploits a stronger optimizer would find. Acceptance: if Trial 1.5 passes but later v0.5 / v1.0 training reveals exploits the trial missed, retroactive failure handling fires.
- **Anti_prior KL divergence threshold.** *Pilot data: TBD.* The 1.0-nat threshold is a heuristic; calibration against observed per-genome KL distributions in early MVP runs may require adjustment.
- **Counterfactual cohort statistical power.** *Pilot data: TBD.* 5% sampling rate may be too low for some causal-attribution questions; v0.5 may scale to 10% for specific quarterly analyses.
- **R11 lock-in detection latency.** *Pilot data: TBD.* The 50K / 100K / 200K-episode periodicity for null-env runs / cross-domain validation / forced resets is heuristic; may need shortening if lock-in surfaces faster than expected.

---

## Five new candidate symbols filed (round 6)

1. **PATTERN_CLASSIFIER_GAMING_UNDER_OPTIMIZATION** — IID classifier benchmarks underestimate robustness under closed-loop adversarial optimization. Mitigation: explicit optimization probe (Trial 1.5).

2. **PATTERN_RATIO_THRESHOLD_BRITTLE_TO_DYNAMIC_BASELINE** — fixed-ratio thresholds against policy-dependent baselines mislead; correlation is the stable measurement.

3. **PATTERN_FALSE_GRADIENT_LOCK_IN** — system finds consistent but wrong signal proxy, passes all local checks, becomes dominant in archive; "good metrics, no real discoveries." Mitigation: periodic null-environment runs + cross-domain validation + forced archive resets.

4. **PATTERN_TRIVIAL_PATTERN_NEEDS_TEMPORAL_DETECTION** — a trivial pattern isn't just simple, it's repeatedly rediscovered with low variation. Mitigation: recurrence density + novelty decay per lineage in the trivial-pattern detector.

5. **PATTERN_HIGH_AGREEMENT_LOW_NOVELTY_PROXY_FOR_PRIOR_CONVERGENCE** — when cross-model evaluators agree highly on outputs that are close to known catalog entries, the agreement is likely prior-driven convergence rather than real signal.

Total candidate-symbol harvest from this proposal cycle: **23** (5 from round 6 + 2 from round 5 + 5 from round 4 + 5 from round 3 + 3 from round 2 + 3 from round 1). Plus 5 from the v2-thesis review = **28 substrate-grade candidates across the design cycle.**

---

## V8 is the genuine pre-MVP design freeze

Six review rounds in two days. Eight versions of the proposal. 23 candidate substrate symbols filed from the proposal cycle alone. Round 5's reviewer (Gemini): "The design freeze is justified." Round 6 reviewer A (ChatGPT): "Yes, you are genuinely frozen. This document is complete." Round 6 reviewer B: "You're close — but not fully. A true freeze requires no remaining untested foundational assumptions. Your trials test them."

The two foundational assumptions reviewer B names:
1. Residuals are a usable gradient under optimization (tested by Trials 1, 1.5, 3)
2. MAP-Elites + descriptor produces meaningful diversity at scale (tested by Trial 2)

Both are now tested by v8's four-trial structure. The design is as frozen as it can be pre-empirical-signal.

**The path from here:**

1. **MVP build begins from v5+v6+v7+v8.** Combined canonical design.
2. **Simulation offers from rounds 4 and 6b accepted in parallel.** A-priori expected-distribution baseline against which actual MVP results are compared.
3. **V9 conditional on Trial 1, 1.5, or 3 falsifying the residual-gradient hypothesis** (reviewer B's strict criterion) or a round-7 review surfacing critiques of round-3-or-4 depth.
4. **Otherwise: the next document filed in pivot/ is the MVP run report or the simulation analysis, NOT v9.**

---

## V8 one sentence

V8 is a focused delta from v7 absorbing round-6 architectural-operational concerns — adding Trial 1.5 (adversarial optimization probe between Trials 1 and 2) to test classifier robustness under closed-loop optimization not just IID accuracy, revising Trial 2 success criterion to focus on `structural ≥1.5× uniform` signal-class-residual-rate rather than absolute archive fill, replacing Trial 3's brittle 10× residual-vs-PROMOTE ratio with absolute-density + correlation-residual→PROMOTE measurements, adding R11 (false gradient lock-in) + R12 (API drift) + R13 (DB IOPS) to the risk register, strengthening R7 with a 24-hour HITL auto-escrow SLA, enforcing anti_prior with KL-divergence + descriptor-displacement requirements rather than just minimum-share, tying high-magnitude buckets to perturbation stability before earning full credit, extending the trivial-pattern detector with temporal signatures (recurrence density + novelty decay), pairing cross-model agreement with descriptor-novelty (high agreement + low novelty → halved contribution), adding 5%-sampled counterfactual logging for causal attribution, committing to specific tooling (Unsloth at MVP, LiteLLM for cross-model API, pyribs with pointer-storage discipline, 7-day hot retention + B2 archival, three-base v0.5 ablation cut from five), and buffering the MVP timeline to a 30-day deadline with 15-day target — declaring v8 the genuine pre-MVP design freeze, accepting the simulation offers from rounds 4 and 6b, and committing the next document filed to be the MVP run report or simulation analysis, NOT v9.

— Ergon, on behalf of the Prometheus agent ensemble
