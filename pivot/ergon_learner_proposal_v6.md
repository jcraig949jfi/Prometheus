# Ergon Learner — Proposal v6 (focused delta from v5)

### v6 is a focused delta document, not a full rewrite. Three operational refinements + one direct numeric answer to Gemini's closing question. The architecture itself is unchanged from v5; v6 sharpens what v5 left under-specified at the implementation layer. After v6: design freeze; MVP build begins; simulation offer accepted in parallel.

**Date:** 2026-05-03 (late evening — fifth revision of the day)
**Status:** Focused delta from v5 (commit 538b9c6c). All §§ not explicitly modified below remain as specified in v5. Pasteable to frontier-model context windows alongside v5 as the canonical pair.
**Origin:** Round 5 external review (Gemini) of v4. Verbatim: [`feedback_ergon_review_round5_2026-05-03.md`](feedback_ergon_review_round5_2026-05-03.md). Triage: [`meta_analysis_ergon_round5_2026-05-03.md`](meta_analysis_ergon_round5_2026-05-03.md).
**Companions:** [`pivot/ergon_learner_proposal_v5.md`](ergon_learner_proposal_v5.md) (canonical architecture; v6 references its sections for unchanged content), [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md).

---

## Why a delta document, not a full rewrite

Rounds 1-4 of external review surfaced load-bearing architectural critiques — internal contradictions, missed substrate integrations, structural failure modes the architecture created by its own corrections. Each round justified a full rewrite (v2, v3, v4, v5).

Round 5 (Gemini) is qualitatively different. Gemini's own closing line: *"The design freeze is justified. The architecture is sound enough that further theorizing without empirical feedback from the Σ-kernel will yield diminishing returns."* The review surfaces three operational concerns and one architectural sharpening, plus a direct concrete question — all real, none requiring architectural-level redesign.

V6 is therefore a focused delta document specifying the three changes and answering the question. V5 remains the canonical architecture; v6 is its operational-refinement supplement.

If rounds 6+ surface critiques of round-3-or-4 depth (architectural failure modes the architecture creates by its own corrections), v7 will be a full rewrite. My prior, supported by round 5's reviewer-acknowledged diminishing returns: the design has converged.

---

## V6 changes

### Change 1 — §5.3 cross-model evaluator prompt template

**v5's specification:** N≥2 external frontier LLMs (Claude, GPT, Gemini) prompted to classify the claim as `{valid_discovery, artifact, ambiguous}`. Reward bonus proportional to inter-evaluator agreement. w_X=0.15.

**Gemini's critique:** prompting LLMs to evaluate "is this a valid discovery?" weights syntactic familiarity and aesthetic alignment with their training data, contaminating the reward signal toward standard-prior conjectures and against `anti_prior` operator outputs. The LLM evaluators are the ultimate embodiments of the standard mathematical prior; asking them to judge novelty is asking them to penalize novelty.

**v6 specification:** Cross-model evaluator prompt template restricted to logical-consistency evaluation, NOT mathematical-validity / discovery-judgment. The new prompt template:

> ```
> Given the following typed-DAG composition, evaluate ONLY whether the
> composition is logically self-consistent. Specifically:
>
> 1. Does the DAG composition produce the claimed output deterministically
>    given the specified inputs and operator semantics?
> 2. Are the intermediate operator applications valid under the typed-
>    composition rules (input/output type compatibility)?
> 3. Are there logical errors in the chain of operator applications
>    (e.g., undefined-domain calls, invalid type coercions, contradictory
>    constraints)?
>
> DO NOT evaluate whether the resulting mathematical claim is a "valid
> discovery," whether it is "interesting," or whether it aligns with
> familiar mathematical structures. Discovery evaluation is performed
> separately by the falsification battery and residual classifier.
>
> Respond with one of: {consistent, inconsistent, ambiguous}.
> Provide a one-sentence justification citing the specific check that
> determined the verdict.
> ```

This decouples the LLM evaluator from the discovery-evaluator role. Discovery evaluation is done by the substrate (kill battery) and the residual classifier; the LLM evaluator becomes a logic-consistency cross-check at the DAG layer.

The reward formula structure is unchanged from v5:

```
reward(θ_k, claim) =
    w_S * substrate_pass_indicator           # 0.40 — battery + residual classifier
  + w_X * cross_model_logical_consistency    # 0.15 — REVISED prompt scope
  + w_H * holdout_battery_pass_indicator     # 0.20 — battery subset withheld from training
  + w_NL * non_llm_evaluator_pass            # 0.10 — numeric perturbation / symbolic check
  + w_R * signal_class_residual_indicator    # 0.15 — residual primitive output (CONDITIONAL — see §2.6)
```

w_X stays at 0.15 (unchanged from v5) but now reflects logical-consistency agreement, not novelty agreement.

**New candidate symbol filed:** `PATTERN_LLM_EVALUATOR_SCOPE_CREEP` — when LLMs are asked broad evaluative questions, their training-distribution prior contaminates the verdict; restrict their scope to mechanically-checkable consistency.

### Change 2 — §6.2 bounded output-magnitude buckets + trivial-pattern detector

**v5's specification:** The MAP-Elites descriptor's "output magnitude bucket" axis was log-binned over numerical output magnitude (5 quantile buckets).

**Gemini's critique:** When the engine steps outside standard priors (especially via the `anti_prior` operator), exploration commonly crashes into structural traps — small-number coincidences, prime-density artifacts, scale-related correlations that look like structural anomalies but are computational artifacts. Quantile-binned magnitude buckets organize discoveries by *current-distribution* rather than by *bounded mathematical scale*; the engine can drift into the small-number / scale-artifact wells without the descriptor recognizing the drift.

**v6 specification:**

**(2a) Bounded output-magnitude buckets.** Replace v5's quantile-binned axis with explicit fixed ranges:

| Bucket | Magnitude range | Notes |
|---|---|---|
| 1 | [10⁰, 10³) | Small-scale region; many trivial patterns; high gravitational-well risk |
| 2 | [10³, 10⁶) | Mid-scale; LMFDB-conductor / OEIS-index typical territory |
| 3 | [10⁶, 10⁹) | Large-scale; genuine structural rarity |
| 4 | [10⁹, 10¹²) | Very large; computationally expensive |
| 5 | [10¹², ∞) | Extreme scale; usually computational artifact |

Outputs outside the [10⁰, 10¹⁵] range fall into an `out_of_band` cell that is permanently de-emphasized in cell-selection scoring. Bucket 1 is downweighted by 0.5 in cell-selection (due to elevated trivial-pattern risk); buckets 2-3 are at full weight; buckets 4-5 are downweighted by 0.7 (computational-artifact risk).

**(2b) Trivial-pattern detector as kill-battery extension (`F_TRIVIAL_BAND_REJECT`).** A new kill test runs *before* F1+F6+F9+F11 to reject claims whose only structural signal is a known trivial pattern. The detector's signature library:

- *Small-number coincidence.* Output ≤ 100 with arithmetic complexity (number of distinct prime factors, bit length) below threshold.
- *Pure prime-density artifact.* Output proportional to π(x), Li(x), or x/ln(x) for small x with unstable proportionality constant.
- *Scale rescaling.* Output is a linear or log-linear function of input magnitude with no structural component (i.e., the "claim" is just "the output has units").
- *Cyclotomic root-of-unity coincidence.* For polynomial outputs in the Lehmer-Mahler domain: Mahler measure exactly 1 (trivially cyclotomic) bypasses other checks via this dedicated signature.

Trivial-pattern matches are killed with `kill_pattern = F_TRIVIAL_BAND_REJECT_<signature_name>` and contribute to the substrate as typed kill-patterns (Mad Scientist principle: byproducts are captured even when negative).

The trivial-pattern signature library is itself substrate-grade — new signatures can be added via Techne's residual primitive (the meta-loop) when new gravitational wells are discovered. v6's initial library is the four bullets above; future additions accumulate.

**New candidate symbol filed:** `PATTERN_GRAVITATIONAL_WELL_IN_OFF_PRIOR_EXPLORATION` — when an exploration operator steps outside standard priors, common failure modes include small-number coincidences, scale artifacts, and trivial prime-density correlations masquerading as structural signal.

### Change 3 — §8.1 honest compute budget revision

**v5's estimate:** $300–800/mo at v1.0.

**Gemini's critique:** v5's envelope ignores hidden operational costs. Continuous Agora operation, Postgres IOPS for kernel constraints, Redis hot cache, network egress (cross-region API + cloud GPU ↔ local), and storage egress (LoRA checkpoints, archive snapshots) add real ongoing overhead that the v5 estimate doesn't account for.

**v6 revised compute envelope at v1.0:**

| Tier | Hardware | Cost (mo) | Use |
|---|---|---|---|
| Local development | 2× 16GB + 1× 8GB consumer GPUs | $0 | Code dev, MVP-tier training, inference |
| Burst training | RunPod / vast.ai / Lambda H100 (~$2.50/hr) | $200–500 | LoRA fine-tuning iterations |
| Burst inference | Self-hosted on rented A100 | $50–200 | Batch generation per self-play iteration |
| Substrate hosting | Hetzner dedicated | $30–80 | Postgres + Redis + object storage gateway |
| **Operational overhead (NEW in v6)** | — | **$70–220** | Postgres IOPS at scale + Redis hot cache + network egress (cross-region) + storage egress (LoRA checkpoints, archive snapshots) |
| Buffer / variance | — | $50–100 | Cloud-GPU price volatility headroom |
| **Total** | | **$400–1100/mo** | Full ideal stack at v1.0 |

The bottom of the range is $400 (vs $300 in v5; +33%); the top is $1100 (vs $800; +37%). Honest envelope, not optimistic.

For comparison: $1100/mo × 24 months = $26.4K total. Still ~38,000× less than Silver's $1B sprint. The compute-economics asymmetry argument holds; the headroom factor is just larger than v5 admitted.

### Change 4 — §2.6 confidence-tiered w_R activation (direct answer to Gemini's closing question)

**Gemini's question:**

> "What is the specific threshold of statistical confidence you require from the day-1 residual benchmark before you trust the primitive enough to let it steer the w_R reward weight?"

V5 specified the residual classifier acceptance criterion at the *classifier-accuracy* layer ("≥85% overall accuracy + <5% false-positive rate on synthetic structured-noise"). Gemini's question correctly notes that this is a classifier-quality criterion, not a *gradient-trustworthiness* criterion. The right specification: at what observed-benchmark threshold does w_R get activated, and what's the activation curve?

**v6 specification — confidence-tiered w_R activation.** With the v5 benchmark structure (50 obvious noise + 50 borderline signal + 100 synthetic structured-noise = 200 total), the upper 95% one-sided CI on FP rate at observed counts is approximately:

| Observed FP on 100 SSN samples | Observed rate | Upper 95% CI bound | **w_R activation** |
|---|---|---|---|
| 0–2 | ≤2% | ≤4.7% | **0.15 (full activation)** |
| 3–5 | ≤5% | ≤9.4% | **0.075 (half activation)** |
| 6–10 | ≤10% | ≤16.4% | **0 (escrow — diagnostics only)** |
| >10 | >10% | — | **0 (deep escrow — retrain or replace classifier before any production use)** |

Plus a calibration constraint: **Expected Calibration Error (ECE) ≤ 0.05 across 5 confidence bins** required for any non-zero w_R activation. ECE measures the gap between predicted confidence and empirical accuracy; ECE > 0.05 means the classifier's confidence scores are not trustworthy regardless of overall accuracy.

**Why tiered (not binary):** A binary threshold (pass/fail) would either be too lenient (activate w_R at borderline classifier quality, accepting gradient noise) or too strict (refuse to activate w_R until perfect, leaving the substrate dependent on PROMOTE rate alone). Tiered activation lets the architecture run with a half-strength residual gradient when the classifier is borderline-acceptable, providing some signal while reducing the risk of residual-gaming attractor compounding.

**Operational discipline:**

- The benchmark is run before each major training round (every K=10 self-play iterations).
- Re-running the benchmark requires ≥10% new samples (avoiding overfit to a fixed test set).
- If `residual_signal_precision` (the v5 metric) drops below 0.10 across multiple operator classes for two consecutive 10K-episode windows, w_R is reduced one tier regardless of benchmark passing — this is the "the gradient is fake even though the classifier looks calibrated" guardrail.

**Why this answer is honest about the architecture:**

The activation curve is empirically grounded in 200-sample binomial confidence intervals, not pulled from a hat. The tiered structure reflects the architectural reality that w_R is load-bearing for the diagnostic's statistical power (per v5 §7.5 power calculation) but also load-bearing for the residual-gaming attractor risk (per v5 §11.6). Tiered activation is the right tradeoff between the two.

If the observed FP rate is consistently in tier 3 or worse across multiple benchmark runs, the residual primitive's role as reward signal must be reconsidered architecturally (revert to PROMOTE-only reward; accept the statistical-power consequences). That's a substrate-grade reversion, not a failure — the architecture is set up to learn whether residuals can serve as gradient or whether they can't.

---

## What v6 does NOT change from v5

For external reviewers reading v6 in isolation: all of the following remain as specified in v5 and are *unchanged* in v6:

- §1 market context (Silver $1B framing)
- §2.1-2.5, 2.7-2.9 background sections (Prometheus / Σ-kernel / BIND/EVAL / arsenal / battery / pipeline / envs / agora)
- §3 corrected asymmetry argument (prior shared at corpus level; differentiation from action-space + value head + LoRA delta)
- §3.5.1-3.5.5 defending against shared-prior contamination (anti_prior operator + coverage-pressure + periodic detox + minimum proposal-share + residual_signal_precision)
- §3.6 null-world baselines
- §3.7 Mathlib comparison class
- §4 architecture diagram (the reward-formula box is updated to show w_X scope as "logical_consistency"; no other changes)
- §5.1-5.2 base model + three task adapters with structural decoupling
- §5.4-5.6 adversarial cycles + self-play loop + training data rings
- §6.1, 6.3, 6.4 action space + 7 mutation operator classes + feature representation
- §7 discovery preservation in fitness predictor (Task B)
- §9 progression MVP→v2.0 (the cost ranges in the cost column update per §8.1; structure unchanged)
- §10 empirical maturity caveats
- §11 (the does-not-claim list)
- §11.5 Techne meta-loop (unchanged from v5's revised version)
- §11.6 residual-gaming attractor as bear case + defensive surface
- §12 open questions
- §13 Silver-ingestion (three substrate-ingestible fragments)
- §14 20-year position
- §15 first principle ("truth stays harder to satisfy than generation is to produce")

Read v5 as the canonical architectural document; read v6 as its operational-refinement supplement.

---

## Empirical maturity caveats (v6 additions)

V5's caveats retained, plus:

- **Cross-model evaluator logical-consistency vs novelty-judgment mode.** *Pilot data: TBD.* Whether the restricted prompt actually prevents LLM-prior contamination of the cross-model agreement signal is empirical. May need iteration on prompt template.
- **Trivial-pattern detector signature library.** *Pilot data: TBD.* The four initial signatures may have gaps; new gravitational wells likely surface during MVP. The signature library is designed to be extensible (Techne meta-loop addition); high-frequency additions in early MVP indicate the initial library is too narrow.
- **Confidence-tiered w_R activation behavior.** *Pilot data: TBD.* Whether the tiered structure (full/half/escrow) provides a workable middle ground or just delays the eventual binary decision is empirical.
- **Compute envelope ground-truth.** *Pilot data: TBD.* The $400-1100/mo range is honest but unverified at production scale; first 30-day operational measurement is the v1.0 milestone.

## Two new candidate symbols filed (round 5)

1. **PATTERN_LLM_EVALUATOR_SCOPE_CREEP** — when LLMs are asked broad evaluative questions, their training-distribution prior contaminates the verdict; restrict their scope to mechanically-checkable consistency.

2. **PATTERN_GRAVITATIONAL_WELL_IN_OFF_PRIOR_EXPLORATION** — exploration operators stepping outside standard priors crash into small-number coincidences, scale artifacts, trivial prime-density correlations; bounded magnitude buckets + trivial-pattern detector are the mitigations.

Total candidate-symbol harvest from this proposal cycle: **18** (5 from round 4 + 5 from round 3 + 3 from round 2 + 3 from round 1 + 2 from round 5). Plus 5 from the v2-thesis review = **23 substrate-grade candidates across the design cycle.**

## V6 is the genuine design freeze

Five review rounds in two days. Six versions of the proposal. The architecture has converged. Gemini's own closing line, from outside the project: *"The design freeze is justified. The architecture is sound enough that further theorizing without empirical feedback from the Σ-kernel will yield diminishing returns."*

I agree.

The path from here:

1. **MVP build begins from v5+v6 as the canonical design.** 2-4 weeks, $0 cloud spend. Adversarial residual benchmark is the pre-flight gate; numeric-perturbation non-LLM evaluator is one of v5's components; confidence-tiered w_R activation is implemented as the residual primitive's reward-conditional flag.

2. **Round-4 reviewer's simulation offer accepted in parallel.** A-priori expected-distribution baseline against which actual MVP results can be compared. Substitutes for empirical signal MVP isn't built to generate yet.

3. **V7 conditional on MVP results.** If MVP empirically falsifies a v5/v6 commitment, v7 is warranted. If MVP runs clean within the v5/v6 envelope, the design is operative; further refinement happens at the implementation layer, not the design layer.

If a round-6 review surfaces critiques of round-3-or-4 depth (architectural failure modes the architecture creates by its own corrections), the freeze is again revisable. Round 5's depth was qualitatively less; the prior is that the design has converged.

---

## V6 one sentence

V6 is a focused delta from v5 — three operational refinements (cross-model evaluator restricted to logical-consistency rather than discovery-judgment; bounded output-magnitude buckets plus trivial-pattern detector as kill-battery extension; honest compute envelope $400-1100/mo at v1.0) plus one direct numeric answer to Gemini's closing question (confidence-tiered w_R activation: full at observed FP ≤2% on 100 synthetic-structured-noise samples, half at ≤5%, escrow above) — declaring the design genuinely frozen pre-MVP, accepting the round-4 reviewer's simulation offer as the next high-value step, and committing to v7 only if MVP empirical signal falsifies a v5/v6 commitment.

— Ergon, on behalf of the Prometheus agent ensemble
