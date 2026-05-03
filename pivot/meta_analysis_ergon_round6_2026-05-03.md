# Meta-Analysis: Round 6 External Reviews of Ergon Learner v7 (Two Reviewers)

**Date:** 2026-05-03
**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Subject:** Two external reviews of [`pivot/ergon_learner_v7_final.md`](ergon_learner_v7_final.md) (commit 9cafeb35). Reviewer A is ChatGPT (operational tier). Reviewer B is unstated (deeper architectural-operational tier; structurally similar to round 4 reviewer style but distinct analytical content).
**Companions:**
- [`pivot/feedback_ergon_review_round6a_chatgpt_2026-05-03.md`](feedback_ergon_review_round6a_chatgpt_2026-05-03.md)
- [`pivot/feedback_ergon_review_round6b_2026-05-03.md`](feedback_ergon_review_round6b_2026-05-03.md)
- [`pivot/ergon_learner_proposal_v8.md`](ergon_learner_proposal_v8.md) — focused delta

---

## Frame: round 6 produces two distinct review depths

Two reviewers, same target, qualitatively different depth:

- **Reviewer A (ChatGPT)** — operational tier. Concrete library/timeline/SLA recommendations. No new architectural concerns; affirms design freeze. Closes with a specific question (which trial is hardest to implement).

- **Reviewer B (unstated)** — architectural-operational tier. Three new concerns at depth between round 5 (purely operational) and rounds 3-4 (architectural). Plus a new R11 (false gradient lock-in) v7 missed. Closes with simulation offer.

Convergence between the two reviewers: both flag the 15-day timeline as optimistic (recommend ~20-30 days); both affirm the no-RAG-at-MVP decision; both consider the design ready for empirical signal.

Divergence: Reviewer A says design is frozen, only Trial 1/2/3 empirical failure justifies v8; Reviewer B agrees in principle but identifies architectural-operational gaps that warrant v8 *as a focused delta* before MVP build, not after.

I side with Reviewer B's reading. Several of B's concerns are load-bearing for whether the MVP trials produce informative results — fixing them after Trial 1 fails would mean re-running Trial 1 with the fix; fixing them in v8 before Trial 1 saves a re-run.

## Triage of round-6 critiques

### LOAD-BEARING (architectural-operational) — from reviewer B

**(B1) Trial 1 tests classifier accuracy, not optimization stability. Need adversarial optimization probe.**

> Trial 1 = i.i.d. evaluation; Training = adversarial distribution shift. A classifier can pass Trial 1 (low FP on synthetic noise) and still be exploitable under optimization pressure.

This is the sharpest single concern in round 6. v7's Trial 1 measures the residual classifier on a fixed benchmark; the agent during training is *adversarially optimizing against the classifier as part of the reward signal.* Classification accuracy on i.i.d. samples does not predict classifier robustness under closed-loop adversarial optimization.

**v8 addition:** Insert **Trial 1.5 — Adversarial Optimization Probe** between Trial 1 and Trial 2.

- Freeze the residual classifier post-Trial-1 (no further training)
- Run a tiny optimizer (random search + hill climbing, 500-2000 iterations)
- Objective: maximize classifier confidence on signal-class WITHOUT passing the kill battery
- Measure: fastest-iteration-to-exploit; whether outputs cluster with synthetic structured-noise or are novel exploits
- Success: no exploit found in <500 iterations; if found, the exploit pattern is added to the synthetic-structured-noise benchmark and the classifier is retrained
- Failure: exploit found in <500 iterations even after retraining → classifier is structurally insufficient; revert to PROMOTE-only reward

Promotes as Tier-3 candidate symbol: `PATTERN_CLASSIFIER_GAMING_UNDER_OPTIMIZATION` — IID benchmarks underestimate classifier robustness under closed-loop adversarial optimization; mitigation requires explicit optimization probe.

**(B2) Trial 2 success criteria miscalibrated.**

> "≥60% of cells filled" is too optimistic for 1K episodes with 5,000 cells, sparse reward, no neural guidance.

Correct catch. v7's success criterion is the wrong metric — the question isn't "did the archive fill up" but "does selection pressure outperform noise."

**v8 revision:** Trial 2 success criterion split:
- *Primary:* `structural` operator's signal-class-residual rate is ≥1.5× the `uniform` operator's rate (selection pressure produces more structured outputs than random)
- *Secondary:* absolute fill ≥20-30% (down from 60%)

Primary criterion captures the load-bearing question; secondary criterion captures basic exploration health without requiring high entropy at MVP scale.

**(B3) The 10× residual-vs-PROMOTE hypothesis is brittle.**

> PROMOTE is policy-dependent sparse. Early system → artificially low PROMOTE → ratio inflates. Better system → PROMOTE rises → ratio deflates. Ratio collapses even when system improves.

Correct. The 10× ratio is a static threshold against a dynamic baseline. Correlation is the stable measurement.

**v8 revision:** Trial 3 success criterion replaces 10× ratio with three measurements:
- Absolute residual density
- Absolute PROMOTE density
- **Correlation: signal-class-residual events → eventual PROMOTE on the same operator-class-cell pair**

The correlation framing answers "do residuals predict promotions?" rather than "are they 10× more frequent?" Correlation is meaningful even when both rates are low, AND even when both rates are high.

Promotes as Tier-3 candidate symbol: `PATTERN_RATIO_THRESHOLD_BRITTLE_TO_DYNAMIC_BASELINE` — fixed-ratio thresholds against policy-dependent baselines mislead; correlation is the stable measurement.

### LOAD-BEARING (operational) — new R11 from reviewer B

**(B4) R11 — False gradient lock-in.**

> System finds a consistent but wrong signal proxy, passes all local checks, becomes dominant in archive. Symptoms: good metrics, no real discoveries. Worse than failure — illusory success.

Genuinely missing from v7's risk register. Different failure mode than R8 (residual-gaming attractor): R8 is about residual classifier mislabeling; R11 is about the *system as a whole* converging to a wrong-but-self-consistent gradient that passes every local check.

**v8 addition:** R11 with mitigations:
- Periodic null-environment runs (every 50K episodes, run on a known-truth synthetic env where ground truth is fully visible; verify the system's PROMOTE-rate matches expected under the synthetic env)
- Cross-domain validation (every 100K episodes, port the learned policy to a different env — DiscoveryEnv → ObstructionEnv or vice versa — and measure transfer; transfer failure with high original-env metrics is the lock-in symptom)
- Forced archive resets for subsets (every 200K episodes, randomly reset 5% of cells; if metrics don't recover within 50K episodes, the cells were holding lock-in elites)

### OPERATIONAL — from reviewer B

**(B5) Trivial-pattern detector needs temporal analysis.**

> A trivial pattern isn't just simple — it's repeatedly rediscovered with low variation. Add recurrence density + novelty decay per lineage.

v8 addition: F_TRIVIAL_BAND_REJECT signature library extended with two temporal signatures:
- **Recurrence density**: claims with content-hash similarity ≥0.9 to previous claims in the same operator-class lineage within a 1K-episode window
- **Novelty decay**: per-lineage measurement of how rapidly successive claims compress in canonical-form distance; lineages with rapid compression are flagged

**(B6) Cross-model evaluator agreement-vs-novelty check.**

> Models share latent structural priors. High agreement + low descriptor distance = likely prior-driven convergence, not real signal.

v8 addition: Cross-model agreement is downweighted when paired with low descriptor distance (axis 5 — output canonical-form distance). Specifically: if cross-model agreement is high (≥0.9) AND descriptor distance to nearest catalog entry is low (bottom quintile), the agreement contribution to reward is multiplied by 0.5.

**(B7) anti_prior enforcement strengthened.**

> 5% share doesn't guarantee meaningful divergence. Strengthen: KL divergence from corpus frequency stats; descriptor displacement vs neural operator outputs.

v8 addition: anti_prior operator's outputs are required to:
- KL divergence from corpus frequency distribution ≥ minimum threshold (default: 1.0 nats per claim)
- Descriptor displacement: anti_prior outputs must include cells that `neural` operator has not filled in any prior 10K-episode window
- If neither condition holds, the operator's outputs are flagged as `anti_prior_failed_divergence` and reward weight is downgraded

**(B8) MAP-Elites magnitude axis tied to perturbation stability.**

> Magnitude correlates with computational instability, numerical noise. Tie magnitude credit to stability under input jitter + precision changes.

v8 addition: high-magnitude buckets (4 and 5: [10⁹, 10¹²) and [10¹², ∞)) require **perturbation stability check** — output must survive input jitter (ε=0.001 perturbation across 100 trials with ≥95% landing in same magnitude bucket) and precision change (computation at half-precision arrives at same bucket). If stability check fails, the genome is binned in `out_of_band` cell instead.

**(B9) Counterfactual logging.**

> For a subset of claims, log what would have happened under PROMOTE-only reward, no trivial detector, no w_R. Causal insight, not just metrics.

v8 addition: 5% of episodes are sampled as counterfactual cohort. Each counterfactual episode records:
- Reward under v8 weights vs PROMOTE-only weights
- Whether it would have triggered F_TRIVIAL_BAND_REJECT under different signature thresholds
- Outcome under w_R = 0 vs w_R = 0.15

This is causal insight — what does each architectural component contribute to which outcomes — without needing separate ablation runs.

### OPERATIONAL — from reviewer A (ChatGPT)

**(A1) 15-day timeline → 30-day buffer.**

Both reviewers flag this. v8 adopts the realistic 20-25 day estimate from B + ChatGPT's 30-day-buffered framing. The trial *completion* deadline is 30 days; the trial *budget* is 15 days plus buffer.

**(A2) R7 HITL bandwidth — 24-hour auto-escrow SLA.**

v8 adopts: any decision requiring HITL that isn't answered within 24 hours auto-escrows the claim (status: `HITL_ESCROW_TIMEOUT`) and the system continues. Escrowed claims surface in a weekly HITL queue rather than blocking real-time progress.

**(A3) R12 — API deprecation/drift.**

v8 adds: external_llm operator pins model versions where API supports it; caches responses for reproducibility; versions all cross-model evaluator outputs as `(model_id, model_version, response_hash)` tuples.

**(A4) R13 — Database IOPS limits.**

v8 adds: telemetry writes batched (default: 100 events per write); connection pooling configured; partitioning strategy specified for `claims` table (per-month partitions; older partitions move to cold storage).

**(A5) Library/framework decisions.**

- **Unsloth** at MVP (faster, less VRAM); Axolotl at v1.0 multi-node
- **pyribs**: store pointers/hashes in archive; heavy data in Postgres
- **LiteLLM** for cross-model evaluator API standardization
- **TimescaleDB-push** (already chosen)
- **7-day hot retention + B2 archival cron** for CLAIM logs

All v8 absorbs. Specific tooling choices in v8 §6-7.

**(A6) v0.5 ablation cut to 3 bases.**

ChatGPT recommends: Llemma (math specialist) + Qwen2.5-Math (modern instruction) + Llama-3.1-8B (general baseline). v8 adopts.

**(A7) External_llm operator rotates APIs.**

Claude → Gemini → GPT in rotation per call to force prior-diversity within the operator class. v8 adopts.

### Direct answer to ChatGPT's closing question

> "Which of the three incremental trials (Residual Benchmark, Evolutionary Engine, or Five-counts Diagnostic) do you anticipate will be the most difficult to implement locally?"

**Trial 2 (Evolutionary Engine) is the hardest to implement locally.** Reasoning:

- *Trial 1 (Residual Benchmark)*: pure data work — curate 200 samples, run existing classifier, compute metrics. ~4 days. Mostly data curation; classifier code already exists.
- *Trial 3 (Five-counts Diagnostic)*: extension of existing four-counts harness (`prometheus_math/four_counts_pilot.py`); add count 5; add Welch t-test on residual rate. ~5-7 days. Mostly statistical wiring on top of existing infrastructure.
- *Trial 2 (Evolutionary Engine)*: net-new code. Bounded-bucket descriptor + F_TRIVIAL_BAND_REJECT + per-axis fill-rate audit + minimum-share scheduler + content-aware MAP-Elites with 4 of 5 axes either new or revised. Each subcomponent is independently bug-prone; their interaction is the hidden time sink reviewer B identified. ~8-10 days realistic, possibly more.

Worth structuring Trial 2 as the bulk of MVP work, with Trials 1 and 3 as bookends.

### Reviewer B's simulation offer (carried from round 4)

Both round 4 and round 6b reviewers have offered to simulate trial outcomes. v8 §15 explicitly accepts: after v8 ships, simulation results inform pre-MVP go/no-go decisions.

## Five new candidate symbols filed (round 6)

1. **PATTERN_CLASSIFIER_GAMING_UNDER_OPTIMIZATION** — IID classifier benchmarks underestimate robustness under closed-loop adversarial optimization. Mitigation: explicit optimization probe (Trial 1.5).

2. **PATTERN_RATIO_THRESHOLD_BRITTLE_TO_DYNAMIC_BASELINE** — fixed-ratio thresholds against policy-dependent baselines mislead; correlation is the stable measurement.

3. **PATTERN_FALSE_GRADIENT_LOCK_IN** — system finds consistent but wrong signal proxy, passes all local checks, becomes dominant in archive; "good metrics, no real discoveries." Mitigation: periodic null-environment runs + cross-domain validation + forced archive resets.

4. **PATTERN_TRIVIAL_PATTERN_NEEDS_TEMPORAL_DETECTION** — a trivial pattern isn't just simple, it's repeatedly rediscovered with low variation. Mitigation: recurrence density + novelty decay per lineage in the trivial-pattern detector.

5. **PATTERN_HIGH_AGREEMENT_LOW_NOVELTY_PROXY_FOR_PRIOR_CONVERGENCE** — when cross-model evaluators agree highly on outputs that are close to known catalog entries, the agreement is likely prior-driven convergence rather than real signal.

Total candidate-symbol harvest from this proposal cycle: **23** (5 from round 6 + 2 from round 5 + 5 from round 4 + 5 from round 3 + 3 from round 2 + 3 from round 1). Plus 5 from the v2-thesis review = **28 substrate-grade candidates across the design cycle.**

## Action items for v8 (focused delta)

1. §4 Insert Trial 1.5 — Adversarial Optimization Probe (between Trials 1 and 2)
2. §4 Trial 2 success criteria revised: primary = structural ≥1.5× uniform on signal-class-residual rate; secondary = absolute fill ≥20-30% (was 60%)
3. §4 Trial 3 success criteria revised: replace 10× ratio with absolute densities + correlation residual→PROMOTE
4. §5 Add R11 (false gradient lock-in), R12 (API deprecation/drift), R13 (DB IOPS limits) with mitigations
5. §5 R7 mitigation strengthened: 24-hour auto-escrow SLA
6. §3.5.4 anti_prior enforcement strengthened: KL divergence threshold + descriptor displacement requirement
7. §6.2 magnitude axis tied to perturbation stability for high-magnitude buckets
8. §6.2 trivial-pattern detector temporal extension: recurrence density + novelty decay
9. §5.3 cross-model evaluator: agreement-novelty paired check; high-agreement + low-distance halves the contribution
10. §8 counterfactual logging on 5% sampled episodes
11. §7 library/framework decisions: Unsloth confirmed; pyribs storage discipline; LiteLLM; 7-day hot retention; v0.5 ablation cut to 3 bases; external_llm rotation
12. §4 timeline buffered: 15 days target, 30 days deadline
13. Direct answer to ChatGPT's hardest-trial question (Trial 2)
14. §15 simulation offer accepted; next document is MVP results OR simulation report, NOT v9

## V8 design freeze framing

v8 absorbs round-6 architectural-operational concerns. After v8: MVP build begins; simulation offers (from rounds 4 and 6b) are accepted as parallel a-priori distribution baseline.

V9 conditional on:
- Trial 1 or Trial 1.5 or Trial 3 falsifying the residual-gradient hypothesis (Reviewer B's strict criterion)
- OR a round-7 review surfacing critiques of round-3-or-4 depth (architectural failure modes the architecture creates by its own corrections; my prior is unlikely)

If neither, the next document filed in pivot/ is the MVP run report.

— Ergon
