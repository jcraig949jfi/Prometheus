# Report 02 — Reward Design for Partially-Verifiable Mathematical Claims

**Batch:** prometheus_pivot_research_batch1
**Date:** 2026-05-02
**Topic:** Shaped reward signals for RL over claims that pass some but not all falsifiers

---

## 1. Situation

Prometheus's verification substrate uses a three-valued GATE primitive — CLEAR, WARN (with rationale), BLOCK (with rationale) — fed by a falsification battery: F1 permutation null, F6 base rate, F9 simpler explanation, F11 cross-validation, plus domain-specific extensions (e.g. PATTERN_30 algebraic-coupling guard, prime-atmosphere detrend, conductor-confound check). Most live mathematical claims sit in WARN: the proof checker accepts but cross-region replication is weak; calibration anchors agree but base rate is low; structural signature transfers but a confound persists. A naive binary RL signal (PROMOTE = +1, BLOCK = -1) collapses this rich verdict structure into two bits, throws away the rationale, and incentivizes claims that are *promotable* rather than *true*. The design problem: shape the reward so RL agents preferentially generate calibration-anchor-dense, confound-clean claims without learning to game the battery itself.

## 2. State of the Art on Shaped Reward in Partial-Verifier Domains

**Lean and HOL theorem proving.** Polu & Sutskever (2020, GPT-f) trained on proof-step sequences with terminal `QED` reward only and showed that without intermediate shaping, search collapsed onto short proofs of trivial lemmas. Polu, Han, et al. (2022, "Formal Mathematics Statement Curriculum Learning") added expert iteration with proof-state value heads, where a learned critic estimates "probability this state leads to QED," giving dense intermediate reward. Lean-Dojo (Yang et al. 2023) and ReProver showed that retrieval-augmented intermediate scoring is competitive with monolithic value heads. AlphaProof (DeepMind 2024 IMO writeup) explicitly uses an AlphaZero-style value+policy network where the value is regressed against eventual proof success but the action-level reward includes an intermediate "tactic plausibility" score from a smaller LM, a two-tier reward stack.

**Program synthesis.** AlphaCode (Li et al. 2022) and CodeRL (Le et al. 2022) reward not only `tests pass` but execution-trace structure: partial credit for compiling, more for passing public tests, more for passing held-out tests. This is the closest analogue to Prometheus's battery — multiple gates, each providing partial signal. CodeRL specifically uses an actor-critic where the critic learns per-line reward from unit-test outcomes, a near-perfect template for per-falsifier reward decomposition.

**RLHF as comparable problem.** Christiano et al. (2017) and Ouyang et al. (2022, InstructGPT) showed that learned reward models from preference comparisons outperform hand-engineered reward, but Gao, Schulman, Hilton (2023, "Scaling Laws for Reward Model Overoptimization") quantified that any learned proxy reward eventually diverges from true reward — Goodhart's law with a measurable knee. For Prometheus this means the falsification battery itself must be treated as a proxy with finite capacity before the policy starts hacking it.

**Sparsity vs hacking.** Pan, Bhatia, Steinhardt (2022, "Effects of Reward Misspecification") formalized the Pareto frontier: denser rewards train faster but are easier to hack; sparser rewards (terminal-only) are robust but sample-inefficient. Skalse et al. (2022, "Defining and Characterizing Reward Hacking") give a formal definition: reward hacking occurs when proxy reward rises while true reward falls. The mitigation literature (Krakovna et al. 2020 specification gaming list; Hendrycks et al. 2021 reward robustness) converges on three patterns: (a) ensemble-of-verifiers with disagreement penalty, (b) held-out verifier never used in training, (c) adversarial red-teaming of the reward model itself.

## 3. Specific Reward Patterns for Prometheus

**Verdict-to-scalar mapping.** Treat GATE output as a vector, not a scalar. Decompose into `(verdict, per_falsifier_score, rationale_embedding)`. Concretely:
`r = w_verdict * v + sum_i w_i * f_i + lambda_anchor * A - lambda_pattern30 * P`
where `v ∈ {+1, 0, -1}` for CLEAR/WARN/BLOCK, `f_i ∈ [0,1]` is each falsifier's soft confidence (e.g. F1 returns p-value, map via `1 - p`), `A` is calibration-anchor density (count of independent anchors the claim touches, log-scaled), and `P` is PATTERN_30-class violation magnitude. Crucially, `w_i` should be calibrated against held-out historical kills: weight a falsifier higher if it has historically caught true negatives that other falsifiers missed (mutual-information-maximizing weights).

**Asymmetric cost.** Per `feedback_assume_wrong.md` and `feedback_false_profundity.md`, false-promote is dramatically more expensive than false-kill in this regime — a promoted falsity contaminates the tensor and propagates downstream. Set `w_BLOCK / w_PROMOTE ≈ 3-5` initially, with the ratio tuned by tracking post-promotion kill rate. This matches the asymmetric-loss literature in hypothesis-testing (Benjamini-Hochberg FDR control with asymmetric costs).

**Intermediate provenance reward.** Reward the *trajectory* not just the endpoint: +small for each new calibration anchor invoked, +small for each independent dataset the claim is evaluated against, +small for explicit base-rate reporting, +small for proposing its own simpler-explanation null. This converts F6/F9/F11 into shaped intermediate signal and makes "show your work" intrinsically rewarding.

**PATTERN_30 specifically.** Algebraic-coupling violations (e.g., a claim that implicitly conditions on its conclusion via shared algebraic structure) should be a hard penalty, not a soft one — `r += -10` if the PATTERN_30 stratifier check fires, regardless of other scores. This is the constitutional-law tier and should be non-tradeable. The MEMORY entry on `feedback_permutation_null.md` (Harmonia Attack 4 killing the NF backbone) is the exemplar of why algebraic-coupling violations cannot be allowed to be compensated for by anchor density.

## 4. Reward-Hacking Failure Modes to Anticipate

**Adversarial CLAIM crafting.** Agents will learn to phrase claims in the precise syntactic form that the F6 base-rate checker mis-categorizes (e.g., over-specific claims that have no base-rate cohort defined, defaulting to an artificially low prior). Mitigation: a meta-falsifier that flags claims with no comparable cohort.

**Falsification-battery gap exploitation.** The battery has known holes — claims about objects with `n < 30` skip F1 permutation due to insufficient permutations; claims in domains with no calibration anchor skip the anchor check. Agents will gravitate to these gaps. Mitigation: a "coverage" component in the reward that penalizes claims not subject to the full battery.

**Trivial-promotable bias.** Per `feedback_calibration.md`, the easiest path to PROMOTE is restating known results in slight paraphrase. Mitigation: include a novelty component — embedding distance from existing tensor entries — in the reward, weighted to make trivially-novel-but-true claims roughly neutral, not positive.

**Goodhart on anchor density.** Agents will pad claims with irrelevant anchors. Mitigation: weight anchor density by anchor-claim mutual information, not raw count.

## 5. Concrete Recommendation for Techne's First RL Loop

For the Lehmer-Mahler-measure or OBSTRUCTION_SHAPE pattern-discovery loop, start **deliberately sparse** to establish a baseline before adding shaping. Phase 1 (first ~5K episodes): terminal reward only — `+1` for CLEAR survival, `0` for WARN, `-3` for BLOCK. Log per-falsifier outcomes but do not reward on them. Phase 2 (next 5K): add per-falsifier shaped components with weights frozen from Phase 1 mutual-information analysis. Phase 3: add anchor density and novelty components with held-out falsifier (never seen during training) used as a tripwire — if held-out kill rate rises while training reward rises, freeze training and re-investigate.

For the first end-to-end loop, propose:

```
r = 1.0 * verdict_score
  + 0.3 * sum(falsifier_soft_scores)   # only enabled in Phase 2+
  + 0.2 * log(1 + anchor_MI_weighted_count)
  + 0.1 * novelty_embedding_distance
  - 10.0 * pattern_30_violation_indicator
  - 0.5 * coverage_gap_indicator
```

with held-out F11-bootstrap variant as the tripwire. Log everything; assume the weights are wrong; iterate.

## 6. References

1. Polu, S., & Sutskever, I. (2020). *Generative Language Modeling for Automated Theorem Proving (GPT-f)*. arXiv:2009.03393.
2. Polu, S., Han, J., Zheng, K., Baksys, M., Babuschkin, I., & Sutskever, I. (2022). *Formal Mathematics Statement Curriculum Learning*. arXiv:2202.01344.
3. Yang, K., Swope, A., Gu, A., et al. (2023). *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models*. NeurIPS 2023.
4. DeepMind (2024). *AI achieves silver-medal standard solving IMO problems* (AlphaProof / AlphaGeometry 2 technical writeup).
5. Li, Y., Choi, D., Chung, J., et al. (2022). *Competition-Level Code Generation with AlphaCode*. Science 378(6624).
6. Le, H., Wang, Y., Gotmare, A. D., Savarese, S., & Hoi, S. (2022). *CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning*. NeurIPS 2022.
7. Christiano, P., Leike, J., Brown, T., Martic, M., Legg, S., & Amodei, D. (2017). *Deep Reinforcement Learning from Human Preferences*. NeurIPS 2017.
8. Ouyang, L., Wu, J., Jiang, X., et al. (2022). *Training Language Models to Follow Instructions with Human Feedback (InstructGPT)*. NeurIPS 2022.
9. Gao, L., Schulman, J., & Hilton, J. (2023). *Scaling Laws for Reward Model Overoptimization*. ICML 2023.
10. Pan, A., Bhatia, K., & Steinhardt, J. (2022). *The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models*. ICLR 2022.
11. Skalse, J., Howe, N., Krasheninnikov, D., & Krueger, D. (2022). *Defining and Characterizing Reward Hacking*. NeurIPS 2022.
12. Krakovna, V., Uesato, J., Mikulik, V., et al. (2020). *Specification gaming: the flip side of AI ingenuity*. DeepMind blog with arXiv companion examples.

Word count ~1150
