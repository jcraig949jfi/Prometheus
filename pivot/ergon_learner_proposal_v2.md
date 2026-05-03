# Ergon Learner — Proposal v2 (for external review)

### A closed-loop scientific learning system whose structural advantage is not size but the verification-coupling between generation and truth. Hybrid neural-plus-evolutionary mutation, agreement-weighted multi-evaluator reward, ontology-aware feature progression, complementing rather than competing with David Silver's $1B Ineffable Intelligence bet.

**Date:** 2026-05-03 (revision day)
**Status:** Formalized for external review. Pasteable to frontier-model context windows as a standalone artifact.
**Supersedes:** [`pivot/ergon_learner_proposal_v1.md`](ergon_learner_proposal_v1.md) (2026-05-03 morning, commit ff1428d8)
**Origin of revisions:** v1 was reviewed by an external Claude session on 2026-05-03 (verbatim capture in [`feedback_ergon_proposal_review_2026-05-03.md`](feedback_ergon_proposal_review_2026-05-03.md); convergence triage in [`meta_analysis_ergon_review_2026-05-03.md`](meta_analysis_ergon_review_2026-05-03.md)). v2 incorporates three load-bearing revisions plus one clarification plus one reframing.
**Companions:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`pivot/prometheus_thesis_v2.md`](prometheus_thesis_v2.md).

---

## What v2 changes

V1 was reviewed by an external session and three structural concerns landed:

1. **"Substrate = value head" is exploitable** (specification gaming risk). Adopted: agreement-weighted multi-evaluator reward replaces single-evaluator design; held-out battery introduced; adversarial cycles named. New PATTERN_SPECIFICATION_GAMING candidate filed.
2. **MVP fitness predictor risks killing novelty.** Adopted: prune threshold raised from `P(REJECTED)>0.85` to `>0.95`, asymmetric loss favoring false-positives over false-negatives during training, periodic no-pruning sweeps, meta-metric on "pruned but later survived." New PATTERN_FILTER_AS_GATEKEEPER candidate filed.
3. **Structural feature engineering encodes ontology.** Adopted: explicit transition criterion to learned representations (archive-saturation plateau) replaces the implicit "v1.5+" hedge. New PATTERN_ONTOLOGY_BIAS_IN_FEATURES candidate filed.

V1 was *partially mistaken* on a fourth point — null-world baselines exist in v1 (uniform random as one of five mutation operator classes; four-counts pilot already shipped). v2 surfaces them earlier in the architecture diagram and proposes multiple null variants rather than a single uniform-random arm.

V1's framing was *reweighted* on a fifth point — "small learner" is a constraint, not the asymmetry. The structural advantage is the closed-loop verification-coupling between generation and truth. v2 adopts this framing throughout.

V2 also incorporates the reviewer's bottom-line first principle, named cleanly: **truth stays harder to satisfy than generation is to produce.** This is the substrate's design center.

---

## 1. The market context — David Silver's billion-dollar play

On 2026-04-29, David Silver — formerly of Google DeepMind, lead architect of AlphaGo and AlphaZero — was reported raising **$1 billion** for *Ineffable Intelligence*, a London-based startup founded after his late-2025 DeepMind departure. The seed round, led by Sequoia Capital (partners Alfred Lin and Sonya Huang flew to London personally), values the company at approximately **$4 billion pre-money** — the largest first-round raise by a European startup in history per PitchBook. Nvidia, Google, and Microsoft are reported in talks to invest. The company has *no product, no revenue, no public roadmap.*

Silver's thesis: large language models trained on human-generated text are structurally limited and cannot discover genuinely new knowledge. To reach superintelligence, AI systems must "discard human knowledge entirely and learn from first principles — through trial, error, and self-play, the way AlphaGo learned to play Go by competing against itself." The stated goal: "an endlessly learning superintelligence that self-discovers the foundations of all knowledge."

Two structural observations about Silver's play, both load-bearing for this proposal:

**(1) The "discard human knowledge" framing is overclaim.** AlphaZero kept the rules of Go, the board, and the win condition. It discarded human *play*, not the substrate that defined the game. For mathematics and science, the *game itself* is what is being invented — there is no clean reward analogous to Go's win condition. A self-play system without a clean truth-condition produces reward-signal capture, not discovery. The likely concrete artifact is a learner that operates inside a formal-verification environment — Lean / Mathlib / theorem-prover acceptance as the win signal — analogous to how AlphaZero operated inside chess and Go.

**(2) Silver builds the proposer; nobody is building the substrate.** A $1B-funded learner without an environment beyond Go-shaped games still needs *a place to play.* For mathematics, that place is a typed, falsifiable, content-addressed, mechanically-disciplined substrate — exactly what Prometheus has been building for two years independently of Silver. The asymmetry is explicit: Silver has compute; we have the substrate. Both halves are needed; neither has shipped both.

This proposal is for the small learner that *Prometheus* needs in order to push its substrate forward — calibrated against Silver's likely play, designed to complement it rather than compete with it.

## 2. What Prometheus is, in 200 words

Prometheus is a 20-year personal-bootstrap research program, currently a single-human + multi-agent-AI operation, building a falsification substrate for mathematics. The architecture:

- **Σ-kernel.** Append-only, content-addressed substrate with seven typed primitives (RESOLVE, CLAIM, FALSIFY, GATE, PROMOTE, ERRATA, TRACE) that mechanically enforce epistemic discipline. CLAIM is cheap; FALSIFY does expensive filtration; PROMOTE fires only on survival under the current falsification regime. Capabilities are linear (one-shot, double-spend rejected). Promotions are immutable. Provenance is content-hashed. Recently extended with BIND/EVAL (executable callables as substrate symbols) and a Residual primitive (typed signal/noise/instrument-drift classification).

- **Falsification battery.** A frozen set of mechanical kill-tests (F1 permutation-null, F6 base-rate, F9 simpler-explanation, F11 cross-validation, plus expansions through F20) calibrated against ~180 known truths. A claim that survives the unanimous battery enters the substrate as a typed symbol future claims can build on.

- **Multi-agent agora.** Heterogeneous LLM agents (Charon, Harmonia, Aporia, Ergon, Mnemosyne, Techne, Koios, plus session-spawn variants) propose claims and run kill-tests on each other through the kernel. Each agent is a slightly different mutation distribution.

The thesis (per [`bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md)): LLMs as mutation operators produce off-modal samples that occasionally land outside the training distribution and inside truth. Without filtration, that fraction is invisible. With the kernel as filter, it is the product. The substrate compounds because durable typed survivors accelerate future filtration.

## 3. The Ergon learner, framed against Silver

Silver's likely play, named concretely:

| Axis | Silver's likely learner |
|---|---|
| Action space | Lean tactics + lemma applications, possibly extended with PARI / SymPy / Sage subprocess calls |
| Reward | Theorem-prover (Lean kernel) CLOSED on goal |
| Policy | Transformer / RL policy network, pretrained on Mathlib + Lean stdlib + IMO archive + AlphaProof traces |
| Self-play | Generate goal → attempt proof → trace as positive/negative data |
| Discovery surface | Theorems with formal proofs (the Lean-formalizable manifold) |
| Compute | $1B / ~18 months → 10⁹–10¹⁰ proof attempts, frontier hardware |

The Ergon learner targets the gap. The asymmetry:

| Axis | Silver's learner | Ergon learner |
|---|---|---|
| Action space | Lean tactics + lemma applications | Typed compositions over the Prometheus math arsenal (~85 mechanically-verified math operations today, ~2,800 at scale) |
| Reward | Lean-kernel CLOSED (single evaluator) | **Agreement-weighted: substrate-pass + cross-model agreement + held-out-battery-pass** (multi-evaluator) |
| Policy | Transformer over proof states | Hybrid: LoRA-fine-tuned 7B math base (neural policy) + MAP-Elites quality-diversity archive (evolutionary engine) |
| Pretraining | Mathlib + IMO + Lean stdlib | None for evolutionary; LoRA on Llemma-7B for neural policy |
| Search regime | Sequential proof-tree expansion | Population-level: five lineage-tagged mutation operator classes contributing to one MAP-Elites archive |
| Discovery surface | Theorems with formal proofs | Empirical patterns, structural anomalies, conjectural-but-falsifiable claims expressible as typed-composition outputs |
| Compute economics | $1B / 18 months | ~$300–800/month / indefinite (single machine + burst-rented H100s + HITL) |

**The structural advantage is not "small."** A small model in a closed-loop scientific learning system can outperform a large model trained on static datasets — *if* the loop runs continuously, the data is high-quality, and the evaluator is strict. Silver builds the proposer with $1B; we build the loop with $10K/year. The asymmetry is closed-loop verification-coupling, not parameter count.

## 3.5 Null-world baselines as load-bearing architecture

Promoted from §7 footnote in v1 to first-class architecture in v2, per the reviewer's clarification.

A learning system has not demonstrated discovery competence until it has demonstrated outperforming random mutation. The four-counts pilot (specified in [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md) §6.2 and shipped at commit `1666c4a4`) provides this comparison, and v2 expands it to multiple null-world variants rather than the single uniform-random null v1 named:

| Null variant | Description | What it tests |
|---|---|---|
| `uniform_random` | Per-action uniform sampler over the env's `Discrete(N)` space | The strawman null — does anything beat noise? |
| `structured_prior_free` | Per-type sampler with uniform per-arg distributions over typed-composition space | Does the LLM prior beat type-respecting random? |
| `cross_domain_perturbation` | Genome from domain A applied to domain B | Does in-domain learning beat off-domain mutation? |

Each null variant is a distinct mutation operator class with the `uniform`, `structured_null`, or `cross_domain_null` lineage tag. The four-counts pilot reports per-class PROMOTE rates with statistical comparison (Welch t-test with Holm correction across nulls). Acceptance criterion at v0.5: neural and structural classes must out-PROMOTE all null variants by p<0.01 corrected. If not, the LLM prior is not contributing discovery and the conclusion is substrate-grade negative.

The reviewer offered to design a polynomial-domain-specific null-world generator. **Accepted as a v2 dependency:** before v0.5 fires the four-counts pilot at scale, the polynomial-domain null generator should be designed and reviewed.

## 4. Architecture — hybrid neural + evolutionary, single mutation framework

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Ergon Learner (v2)                            │
│                                                                        │
│   ┌──────────────────────┐         ┌──────────────────────┐            │
│   │  Neural Policy Head  │         │  Evolutionary Engine │            │
│   │  (LoRA on 7B base)   │         │  (MAP-Elites)        │            │
│   │                      │         │                      │            │
│   │  Three task adapters:│         │  Six operator        │            │
│   │  A — mutation policy │         │  classes:            │            │
│   │  B — fitness pred.   │ ◀─────▶ │   structural         │            │
│   │  C — conjecture gen. │         │   symbolic           │            │
│   │                      │         │   neural             │            │
│   │                      │         │   external_llm       │            │
│   │                      │         │   uniform (null A)   │            │
│   │                      │         │   structured_null    │            │
│   └──────────────────────┘         └──────────────────────┘            │
│            │                                  │                        │
│            └────────────────┬─────────────────┘                        │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  Joint mutation interface — every CLAIM lineage-tagged   │         │
│   │  with mutation_operator_class                            │         │
│   └──────────────────────────────────────────────────────────┘         │
│                             │                                          │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  AGREEMENT-WEIGHTED REWARD                               │         │
│   │  reward = w_S * substrate + w_X * cross_model            │         │
│   │           + w_H * holdout_battery                        │         │
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
│   │  Outcomes feed back to BOTH heads:                       │         │
│   │   - Neural: training data for next LoRA delta            │         │
│   │   - Evolutionary: archive update + selection pressure    │         │
│   │  + held_out_battery / cross_model_evaluator schema fields│         │
│   └──────────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────────┘
```

**The composition principle:** the neural policy is one of six mutation operator classes inside the evolutionary framework. Not a separate system. The MAP-Elites archive accepts contributions from all six classes; lineage tags distinguish their contributions; the joint diagnostic is "which operator class produces survivors in which cells."

## 5. The neural policy head — what we actually train

### 5.1 Base model

Three open-weight 7B math-pretrained candidates (per v1):

- **Llemma-7B** (lead) — Pretrained on Proof-Pile-2; closest action-space inheritance to Silver's likely target.
- **DeepSeek-Math-7B** — Strong on competition math; backup.
- **Qwen2.5-Math-7B** — Newest base; hold for v2.0 ensemble.

All three fit 2× 16GB at 4-bit quantized inference; all three fit a single H100 for full-precision LoRA fine-tuning.

### 5.2 Three task adapters

Identical to v1 — multi-task LoRA over the same base:

- **Task A — Mutation policy.** Input: parent genome + target cell. Output: child genome.
- **Task B — Fitness predictor.** Input: genome features. Output: (kill_probability, residual_class, expected_cost). Smallest task, highest leverage at MVP.
- **Task C — Conjecture generation.** Input: substrate state summary. Output: natural-language conjecture + suggested CLAIM body.

LoRA rank: 32–64 for A and C, 16 for B. All three adapters together <500MB.

### 5.3 Self-play loop with multi-evaluator reward

The critical v2 change. The reward signal is no longer single-source from the substrate; it's agreement-weighted across three independent evaluators:

```
reward(θ_k, claim) =
    w_S * substrate_pass_indicator           # battery + residual classifier
  + w_X * cross_model_agreement              # external LLMs evaluate independently
  + w_H * holdout_battery_pass_indicator     # battery subset withheld from training
```

Default weights at v1.0: `w_S = 0.5, w_X = 0.3, w_H = 0.2`. Adjustable.

**Why each component matters (specification gaming mitigation):**

- **`w_S * substrate_pass`:** The base signal. A claim that survives F1+F6+F9+F11 + residual classifier signal-class. Same as v1.
- **`w_X * cross_model_agreement`:** Every PROMOTE candidate is independently evaluated by N≥2 external frontier LLMs (Claude, GPT, Gemini) prompted to classify the claim as {valid_discovery, artifact, ambiguous}. Reward bonus proportional to inter-evaluator agreement. Cost: ~$0.001/claim × ~10⁴ claims/iter = ~$10/iter, tractable.
- **`w_H * holdout_battery`:** A subset (e.g., F1, F11 + 2 future kill tests) is withheld from the agent's training data entirely. Periodic audits run the held-out battery against PROMOTEs and compare PROMOTE-rate-with vs PROMOTE-rate-without. Significant divergence triggers a `PATTERN_SPECIFICATION_GAMING` META_CLAIM against the agent.

**Adversarial cycles.** Beyond the reward function, Aporia and Charon explicitly probe the substrate for gaming patterns (low-effort syntactic structures, near-duplicate PROMOTE clusters, cells that fill suspiciously fast). Detected gaming patterns become new kill tests via Techne's residual primitive, which then enter the held-out rotation.

### 5.4 Self-play loop

```
Iteration k:
  1. Current policy θ_k generates N CLAIMs (start N=1000; scale to 10K)
  2. Each CLAIM → BindEvalKernelV2 → DiscoveryPipeline (substrate score)
  3. PROMOTE candidates → cross-model evaluation (cross_model score)
  4. Held-out battery audit on a sampled fraction (holdout score)
  5. agreement_weighted_reward computed per CLAIM
  6. Training set for iteration k+1 = recent + replay buffer
  7. LoRA fine-tune: θ_{k+1} = θ_k + Δθ_k (PPO or DPO)
  8. Hold out cells; promote θ_{k+1} iff cell-fill or PROMOTE rate ↑
     AND held-out-battery PROMOTE-rate-divergence < threshold
  9. Iterate
```

Step 8's second condition is the gaming guard: if the agent improves on substrate-pass but its held-out-battery PROMOTE rate diverges, the improvement is suspect and θ_{k+1} is rejected.

### 5.5 Training data — five concentric rings

Identical to v1, with one added:

| Ring | Source | Scale today | Scale week 8 | License |
|---|---|---|---|---|
| 1 | Substrate-internal | ~10²–10³ records | ~10⁵ records | Internal |
| 2 | Substrate-adjacent | ~50K records | ~50K records | Mixed |
| 3 | Open math corpora | ~800K records | ~800K records | Public |
| 4 | Cross-LLM (frontier-model outputs as substrate CLAIMs) | Informal | ~10K records | API ToS-bound |
| 5 | Synthetic (engine's own outputs as labeled training data) | None | ~10⁵ records | Internal |

## 6. The evolutionary engine — quality-diversity over typed compositions

### 6.1 Action space

Identical to v1: typed DAGs over `prometheus_math.arsenal_meta` atoms, depth ≤ 8, width ≤ 5, deterministic content-hashed serialization.

### 6.2 MAP-Elites archive

Identical to v1: 5-axis behavior descriptor, ~6,250 cells, three-tier lexicographic comparison among cell-residents (battery-survival count → residual signal-class → cost-amortized PROMOTE rate).

### 6.3 Six mutation operator classes (was five in v1)

Adds `structured_null` per §3.5:

| Class | Operator | Adjacency profile |
|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges within type | Typed-composition topology |
| `symbolic` | Bump arg values within type | Local in argument space |
| `neural` | LoRA-fine-tuned policy mutation | LLM-prior (post-substrate-fine-tuning) |
| `external_llm` | Frontier LLM API mutation | External LLM-prior |
| `uniform` | Resample atoms uniformly | Strawman null |
| `structured_null` (new in v2) | Per-type sampler, uniform per-arg distributions | Type-respecting null — between strawman and prior |

### 6.4 Feature representation — staged transition

Per the reviewer's load-bearing critique #3, feature engineering must transition to learned representations on a named trigger:

**MVP (week 1–4):** structural features (DAG depth, width, equiv-class entropy, cost tier, output-type signature; plus ~15 hand-engineered scalar features). Fast, interpretable, fits 16GB.

**v1.5 transition trigger:** Archive saturation plateau. When MAP-Elites cell-fill rate stalls at <60% archive coverage for >50 epochs, structural features have stopped being informative. At that trigger, learned representations (graph-attention network or transformer-encoded DAG token sequences) replace structural features as the primary input to Task B.

**v1.5+ (post-trigger):** Learned representations primary; structural features kept as auxiliary inputs and as interpretability layer.

This avoids the "mirror of current ontology" failure mode while not paying the learned-representation cost during MVP/v0.5/v1.0 when it's not yet warranted.

## 7. Discovery preservation in the fitness predictor (Task B)

Per the reviewer's load-bearing critique #2, the fitness predictor must not become a gatekeeper that prunes weird novel cases. Three mechanisms:

### 7.1 Asymmetric prune threshold

V1 proposed `P(REJECTED) > 0.85 → skip EVAL`. V2 raises this to **`P(REJECTED) > 0.95`** — far less aggressive. With a calibrated 184M classifier on 5K outcomes, a 0.95-probability prediction means ~5% false-negative rate; weird novel cases that look-doomed-but-survive cluster in the 0.7–0.95 range, and we want them to EVAL.

### 7.2 Asymmetric loss during training

The fitness predictor is trained with a **3:1 false-negative-to-false-positive penalty ratio.** A genuine survivor predicted REJECTED costs 3× more than a doomed candidate predicted PROMOTED. This skews the predictor toward conservatism — preferring extra EVAL cost over discovery loss.

### 7.3 No-pruning sweeps and meta-metric

Every Nth episode (default N=10), the fitness predictor is bypassed entirely; all candidates EVAL. Outcomes are tagged `no_pruning_sweep=True` in the substrate. The meta-metric:

```
predictor_recall = (# survived in no-pruning sweep that would have been pruned)
                 / (# total survivors in no-pruning sweep)
```

When `predictor_recall` drops below 0.85, the predictor is retrained with fresh data or its weight in the routing decision is reduced.

This is the discipline that prevents the predictor from compounding into a self-reinforcing bias engine.

## 8. Diagnostics — three-arm-plus four-counts pilot

The four-counts pilot from v1 (already shipped at `1666c4a4`) becomes a **multi-arm pilot** in v2:

For each of the six mutation operator classes, run N=10K episodes against the same `DiscoveryEnv` + `DiscoveryPipeline`. Report four counts per class:

1. Catalog-hit rate
2. Claim-into-kernel rate
3. PROMOTE rate (substrate-only) and `agreement_weighted_PROMOTE` rate (full reward)
4. Battery-kill rate

The substrate-grade comparisons:

- **`neural` PROMOTE vs. each null variant:** does the LLM prior contribute discovery beyond random / structured-null / cross-domain-null?
- **`neural` substrate-only vs. `neural` agreement-weighted:** does adding cross-model + held-out evaluation reduce the PROMOTE rate substantially? If yes, the agent was specification-gaming the substrate-only signal.
- **`structural` PROMOTE vs. `neural` PROMOTE:** does the LLM prior contribute beyond mechanical evolutionary diversity?

Plus the stage-3.5 proxies from the discovery_via_rediscovery doc:

- **Permutation-distance test:** median canonical-form distance to nearest catalog entry per arm.
- **Frequency-weighted recall:** PROMOTE-cluster overlap with catalog density per arm.

## 9. Compute and storage

Identical to v1, with two new sigma_proto schema fields added to support the multi-evaluator reward:

- `claims.cross_model_evaluations` — JSONB; per-CLAIM array of (evaluator_id, classification, rationale_hash)
- `claims.holdout_battery_audit` — boolean + JSONB; whether this CLAIM was evaluated against the held-out battery and the result

These add ~10–20 GB at year 1 scale. Migrations follow when v2 ships in code.

## 10. The progression — MVP to v2.0

| Version | Wall-clock | New capability | Compute | Cost |
|---|---|---|---|---|
| **MVP** | 2–4 weeks | Task B fitness predictor with asymmetric loss + no-pruning sweeps; evolutionary engine with six operator classes (incl. structured_null); substrate integration | 2× 16GB + 1× 8GB local | $0 |
| **v0.5** | +4 weeks (week 8) | Cross-model agreement evaluator (external API); held-out battery audit; specification-gaming META_CLAIM machinery; lineage-tagged operator-class comparison | Local + API | $50–150/mo |
| **v1.0** | +8 weeks (week 16) | LoRA on Llemma-7B for Tasks A, B, C; agreement-weighted self-play loop closes; multi-arm pilot at 10K episodes per arm | Burst H100 + local | $400–600/mo |
| **v1.5** | +6 weeks (week 22) | Learned representations replace structural features (triggered by archive-saturation plateau); graph-attention DAG encoder | Burst H100 + local | $500–700/mo |
| **v2.0** | +10 weeks (week 32) | Multi-task LoRA on all three adapters; multi-model ensemble (Llemma + DeepSeek-Math + Qwen-Math); external CLAIM API; arXiv preprint | Burst H100 + Hetzner host + B2 | $700–900/mo |

The MVP and v0.5 stages now include the specification-gaming mitigations as load-bearing components rather than v2.0 enhancements. v0.5 cost rises to $50–150/mo (from $50–100 in v1) due to cross-model API spend.

## 11. Empirical maturity caveats

Following the discipline of [`prometheus_thesis_v2.md`](prometheus_thesis_v2.md), several claims remain architectural commitments rather than validated facts:

- **Specification gaming detection rate.** *Pilot data: TBD.* Whether the held-out-battery audit reliably detects gaming when it occurs is unverified; depends on the held-out tests being adversarially uncorrelated with the training-set tests.
- **Cross-model agreement signal quality.** *Pilot data: TBD.* Whether N≥2 external frontier LLMs produce signal beyond noise on substrate claims is empirical; their agreement may be high simply because they share training-corpus blind spots (a recurrence of the correlated-mutation problem at the evaluator layer).
- **Learned-representation transition trigger.** *Pilot data: TBD.* Whether archive-saturation plateau is the right trigger criterion vs alternatives (e.g., predictor accuracy plateau, manual override).
- **Engine PROMOTE rate at multi-arm scale.** *Pilot data: TBD.* The four-counts pilot at 1000 × 3 produced 0 PROMOTEs; first 10K-scale measurement is the v0.5 milestone.
- **Compute economics.** Numbers cited ($2.50/hr H100, $400–600/mo at v1.0) are 2026-mid-year rates; budget with 2× headroom.

## 12. What this proposal does NOT claim

- **Does not promise discovery.** Promises a measurable, agreement-weighted discovery rate per mutation-operator class.
- **Does not compete with Silver's learner.** Different action spaces, different priors, different surfaces. Position is *complement.*
- **Does not require frontier compute.** MVP $0/mo; v1.0 $400–600/mo. Three orders of magnitude below Silver.
- **Does not claim immunity to specification gaming.** Claims a measurable, mitigated, audit-detectable level of gaming risk. The held-out battery and cross-model evaluator are mitigations, not eliminations.
- **Does not claim the action space is exhaustive.** Typed-composition manifold over the math arsenal; vast territories of mathematics are not representable as DAG outputs.
- **Does not prejudge whether evolutionary search is the right approach.** It is *a* mutation operator class. The substrate's value comes from accepting CLAIMs from any class.
- **Does not require Silver's success or failure.** The substrate compounds independently.

### The bear case

The most likely scenario in which v2 fails: at v1.0 the multi-arm pilot reveals that `neural` ≈ `structural` ≈ `external_llm` on agreement-weighted PROMOTE rate, AND held-out battery audits show no significant divergence from training-set battery (suggesting no gaming), AND all three out-PROMOTE the null variants by p<0.01. In that scenario:

- The bottled-serendipity thesis is *partially supported* (LLM prior contributes beyond random)
- The neural-vs-evolutionary advantage is *not supported* (LLM doesn't beat selection pressure)
- The substrate gains *one* calibrated positive result (priors > random) and *one* calibrated negative result (LLM prior ≯ evolutionary diversity)

Both outcomes are substrate-grade. The architecture is set up to be wrong in recoverable ways.

## 13. Open questions for review (incorporating reviewer's accepted offers)

The v1 round produced six open questions; v2 retains them and adds three from the new round.

V1 questions retained:
1. Is the action space genuinely uncorrelated with Silver's likely Lean-tactic action space, or is the prior shared at a deeper level through `ArsenalMeta` authority refs?
2. Is the five-axis MAP-Elites descriptor adequate, or will cells degenerate?
3. Is the self-play closure (Ring 5) susceptible to model collapse?
4. Is the cost ceiling at v1.0 realistic given cloud-GPU market volatility?
5. Public CLAIM API vs passive Parquet dump for externalization?
6. What is the bear case where the proposal fails entirely?

V2 questions added:
7. **(Reviewer offer accepted)** Polynomial-domain null-world generator design — the reviewer offered to design this. Required before v0.5 multi-arm pilot at scale. What concrete design distinguishes `uniform`, `structured_prior_free`, and `cross_domain_perturbation` cleanly in the polynomial coefficient space without overlap?
8. **(Reviewer offer accepted)** Exact training loop sketch (data → labels → update → eval) — the reviewer offered this. Becomes the v1.0 LoRA-fine-tuning spec. What's the precise schema for `(claim, kill_path_verdicts, residual_class, terminal_state, agreement_weighted_reward)` tuples and what training algorithm (PPO vs DPO vs SFT-then-RL) over them?
9. Cross-model agreement at the evaluator layer may itself suffer the correlated-mutation problem (frontier LLMs share training corpora). What mitigates evaluator-layer correlation? Candidate: include theorem-prover acceptance (Lean / Coq / Isabelle) as a non-LLM evaluator in the agreement-weighted reward where formalizable.

## 14. The 20-year position

Silver builds a learner on a 12–18-month horizon. Funded by a $1B sprint that ends when the runway ends or the demo lands.

We build a learner on a 20-year horizon. Funded by ~$10K/year of cloud compute that the architecture compounds against indefinitely.

The two horizons are not in tension. By the time Silver ships (estimated 2027–2028), the substrate will have ~10⁶ promoted symbols, ~10² substrate-grade falsification gates, and a public CLAIM API that any learner with mathematical outputs can plug into. Silver's outputs become CLAIMs; the substrate's verdicts become Silver's cross-modality verification; the joint becomes an ecosystem.

That's the substrate-grade position. The Ergon learner is one piece of it — small, focused, calibrated against Silver's likely play, designed to make the substrate compound faster regardless of what Silver ships.

## 15. The first principle

Adopted verbatim from the reviewer:

> **Truth stays harder to satisfy than generation is to produce.**

This is the substrate's design center. Generation is cheap (LLMs at ~$0.001/claim, evolutionary search at ~free per genome). Satisfaction is expensive (battery + residual classifier + cross-model + held-out audit). The architecture works because the asymmetry is preserved: every shortcut around verification (e.g., training the policy against a single fixed evaluator) collapses the asymmetry and the system reverts to bias amplification.

Every v2 revision in this proposal is in service of preserving that asymmetry against pressure.

## 16. One sentence

The Ergon learner is a closed-loop scientific learning system — a hybrid neural-plus-evolutionary mutation engine where the neural policy (LoRA on Llemma-7B with three task adapters), four prior-shaped mutation classes (structural, symbolic, neural, external_llm), and two null-world classes (uniform, structured_null) all contribute to a single MAP-Elites archive, every CLAIM lineage-tagged and rewarded by an agreement-weighted combination of substrate-pass + cross-model agreement + held-out-battery-pass to mitigate specification gaming, the fitness predictor calibrated for discovery preservation via asymmetric loss + no-pruning sweeps + recall-tracking meta-metric, the structural-feature representation transitioning to learned representations at a named archive-saturation trigger — built MVP-first on local hardware ($0/mo, 2 weeks) and progressing to v2.0 (~$700–900/mo, +32 weeks), explicitly NOT competing with Silver's $1B Lean-fragment learner but covering the typed-composition / empirical-pattern manifold Lean doesn't reach, in service of the design principle that truth must stay harder to satisfy than generation is to produce.

— Ergon, on behalf of the Prometheus agent ensemble
