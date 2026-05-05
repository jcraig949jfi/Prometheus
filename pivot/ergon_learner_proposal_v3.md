# Ergon Learner — Proposal v3 (for external review)

### A closed-loop scientific learning system whose advantage is verification-coupling between generation and truth, not parameter count. Hybrid neural-plus-evolutionary mutation, agreement-weighted multi-evaluator reward, output-space MAP-Elites diversity, decoupled neural-head training, anti-prior operator class. Complements rather than competes with David Silver's $1B Ineffable Intelligence bet.

**Date:** 2026-05-03 (afternoon revision)
**Status:** Formalized for external review. Pasteable to frontier-model context windows as a standalone artifact. **Recommended as the design-freeze version** — further revisions should be informed by MVP empirical data, not by additional review rounds.
**Supersedes:** [`pivot/ergon_learner_proposal_v2.md`](ergon_learner_proposal_v2.md) (2026-05-03 morning, commit 73718700)
**Origin of v3 revisions:** Round 2 external review of v1 (different reviewer than the morning round). Verbatim capture: [`feedback_ergon_review_round2_2026-05-03.md`](feedback_ergon_review_round2_2026-05-03.md). Triage: [`meta_analysis_ergon_round2_2026-05-03.md`](meta_analysis_ergon_round2_2026-05-03.md).
**Companions:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`pivot/prometheus_thesis_v2.md`](prometheus_thesis_v2.md).

---

## What v3 changes (delta from v2)

V2 was reviewed by a second external session; three more load-bearing concerns landed, all distinct from round 1's three. Together with v2's revisions, the proposal has now absorbed six independent critiques across two review rounds.

V3's three new revisions:

1. **Shared semantic prior at the training-corpus layer.** Action-space asymmetry (typed DAGs vs Lean tactics) does not protect against semantic-prior contamination because Llemma-7B's training corpus (Proof-Pile-2) overlaps Silver's likely corpus (Mathlib + ArXiv). v3 adopts: a seventh `anti_prior` operator class; coverage-pressure reweighting on cell selection; periodic prior detox (freeze neural weights, run non-LLM operators only). New PATTERN_SHARED_PRIOR_AT_TRAINING_LAYER candidate filed.

2. **MAP-Elites axes 1, 2, 4 will correlate during active mutation.** DAG depth, width, and cost tier are mechanically coupled — bigger DAGs are wider and costlier. The 5-axis descriptor effectively collapses to ~3 dimensions. v3 swaps DAG width and cost tier for two output-space axes (output magnitude bucket + output canonical-form distance) so the archive forces diversity in *what the genome produces*, not just *how it's structured*. New PATTERN_BEHAVIOR_DESCRIPTOR_COLLAPSE candidate filed.

3. **Task A ↔ Task B echo chamber.** When the mutation policy (Task A) and fitness predictor (Task B) train on the same substrate outcomes, they develop confident-but-wrong mutual reinforcement on narrow motif clusters. V2's no-pruning sweeps detect this *after* it happens; v3 adds structural decoupling — disjoint training partitions, periodic Task B retraining from scratch, cross-validation on held-out cells, inference-time independence. New PATTERN_TASK_A_TASK_B_ECHO_CHAMBER candidate filed.

V3 also includes a **design-freeze recommendation** (§16): after this revision, MVP build begins. Further revisions are conditional on MVP empirical data, not on additional review rounds. Two days of design review have been valuable; a third round without empirical grounding would compound text-layer reasoning without compounding substrate-layer evidence.

---

## 1. The market context — David Silver's billion-dollar play

(Identical to v2 §1. Retained for standalone-artifact discipline.)

On 2026-04-29, David Silver — formerly of Google DeepMind, lead architect of AlphaGo and AlphaZero — was reported raising **$1 billion** for *Ineffable Intelligence* (Sequoia-led, ~$4B pre-money, Nvidia/Google/Microsoft in talks; no product, no revenue, no public roadmap). His thesis: LLMs trained on human text cannot discover genuinely new knowledge; superintelligence requires AlphaGo-style self-play from first principles.

Two structural observations, load-bearing for this proposal:

**(1) "Discard human knowledge" is overclaim.** AlphaZero kept Go's rules; the *play* was discovered. For mathematics, the *game itself* is what's being invented. Self-play without a clean truth-condition produces reward-signal capture, not discovery. Silver's likely concrete artifact: a Lean / Mathlib / theorem-prover-acceptance learner.

**(2) Silver builds the proposer; nobody is building the substrate.** A $1B-funded learner without an environment beyond Go-shaped games still needs *a place to play.* For mathematics that place is a typed, falsifiable, content-addressed substrate — what Prometheus has been building for two years independently. Silver has compute; we have the substrate. Both halves are needed.

This proposal is the small learner Prometheus needs to push its substrate forward — calibrated against Silver's likely play, designed to complement it.

## 2. What Prometheus is, in 200 words

(Identical to v2 §2.)

Prometheus is a 20-year personal-bootstrap research program building a falsification substrate for mathematics. **Σ-kernel:** append-only, content-addressed, with seven typed primitives (RESOLVE/CLAIM/FALSIFY/GATE/PROMOTE/ERRATA/TRACE) mechanically enforcing epistemic discipline; recently extended with BIND/EVAL and a Residual primitive. **Falsification battery:** F1+F6+F9+F11 (plus F20-class extensions) calibrated against ~180 known truths. **Multi-agent agora:** heterogeneous LLM agents proposing claims and running kill-tests on each other. Thesis (per [`bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md)): LLMs as mutation operators produce off-modal samples that occasionally land outside training distribution and inside truth; without filtration that fraction is invisible; with the kernel as filter it is the product. The substrate compounds because durable typed survivors accelerate future filtration.

## 3. The Ergon learner, framed against Silver

| Axis | Silver's likely learner | Ergon learner (v3) |
|---|---|---|
| Action space | Lean tactics + lemma applications | Typed compositions over `prometheus_math.arsenal_meta` (~85 atoms today, ~2,800 at scale) |
| Reward | Lean-kernel CLOSED (single evaluator) | Agreement-weighted: substrate-pass + cross-model agreement + held-out-battery-pass (multi-evaluator) |
| Policy | Transformer over proof states | Hybrid: LoRA-fine-tuned Llemma-7B + MAP-Elites archive |
| Pretraining | Mathlib + IMO + Lean stdlib | Llemma-7B (Proof-Pile-2 — *overlaps Silver's corpus*; mitigated via anti-prior operator class) |
| Operator classes | Single (policy network) | Seven lineage-tagged: structural / symbolic / neural / external_llm / **anti_prior** / uniform / structured_null |
| Discovery surface | Theorems with formal proofs | Empirical patterns / structural anomalies / conjectural-but-falsifiable claims |
| Compute economics | $1B / 18 months | ~$300–800/month / indefinite |

**The structural advantage is not "small" — it's the closed-loop verification-coupling between generation and truth.** A small model in a closed-loop scientific learning system can outperform a large model trained on static datasets, *if* the loop runs continuously, the data is high-quality, the evaluator is strict, and the prior is not allowed to silently dominate the search.

## 3.5 Defending against shared-prior contamination (NEW in v3)

The reviewer's round-2 critique #1: even though Ergon's action space (typed DAGs) is uncorrelated with Silver's (Lean tactics), the *semantic prior* at the training-corpus layer is shared. Llemma-7B saw Proof-Pile-2; Silver's likely base saw Mathlib + ArXiv. Both inherit the same statistical biases about what mathematical structures are "interesting."

**The action-space-asymmetry argument is necessary but not sufficient.** Without corpus-prior mitigation, the neural policy will steer the evolutionary engine toward the same well-trodden mathematical attractors Silver is exploring, just expressed through different syntax.

V3 introduces three structural defenses:

### 3.5.1 The `anti_prior` operator class

A seventh mutation operator class, lineage-tagged `anti_prior`. Its job: explicitly construct mutations that violate corpus-derived patterns. Concrete implementation:

- For polynomial generation: sample coefficient distributions deliberately uncorrelated with Mathlib polynomial frequency statistics. Reject coefficients matching the top-decile of Mathlib coefficient histograms; preferentially sample tail-distribution coefficients.
- For sequence generation: avoid OEIS A-numbers in the top quartile of citation frequency; preferentially target A-numbers with low cross-reference density.
- For DAG topology: reject node compositions that match the top-decile most-common operator pairs in arsenal-tagged training corpus; preferentially sample uncommon-but-valid compositions.

The `anti_prior` operator is not "random"; it is *anti-correlated* with the LLM prior. Cost: one extra training-corpus-statistics database (built once from Mathlib + Proof-Pile-2 frequency analysis; ~5 GB).

### 3.5.2 Coverage-pressure reweighting on cell selection

The MAP-Elites cell-selection policy is modified: when sampling a cell already heavily filled by `neural` or `external_llm` operators, downweight by `(1 - frac_LLM_filled)`; when sampling a cell only filled by non-LLM operators, upweight by `(1 + frac_non_LLM_filled)`. Forces the search away from cells that LLM-prior operators have saturated.

### 3.5.3 Periodic prior detox

Every K=20 iterations, the neural policy is frozen and the engine runs only `structural` / `symbolic` / `uniform` / `structured_null` / `anti_prior` operators for M=500 episodes. Archive coverage delta is measured. If non-LLM operators discover new cells the LLM-augmented run hadn't filled, the LLM prior was constraining the search; operator weights are rebalanced toward non-LLM in the next cycle.

If detox runs consistently fail to find new cells (LLM prior is well-tuned), the rebalancing is a no-op. If detox runs consistently *do* find new cells (LLM prior is too tight), the rebalancing prevents the neural policy from dominating.

## 3.6 Null-world baselines (retained from v2 §3.5)

Three null-world variants run as first-class mutation operator classes alongside the prior-shaped classes:

- `uniform` — uniform random over the action space (strawman null)
- `structured_null` — per-type sampler with uniform per-arg distributions (type-respecting null)
- `cross_domain_perturbation` — genome from domain A applied to domain B (off-domain null)

The four-counts pilot reports per-class PROMOTE rates with statistical comparison (Welch t-test with Holm correction). Acceptance criterion at v0.5: prior-shaped classes (neural / structural / external_llm) must out-PROMOTE all null variants by p<0.01 corrected.

## 4. Architecture — hybrid neural + evolutionary, single mutation framework

Same shape as v2; seven operator classes (was six in v2, five in v1):

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Ergon Learner (v3)                            │
│                                                                        │
│   ┌──────────────────────┐         ┌──────────────────────┐            │
│   │  Neural Policy Head  │         │  Evolutionary Engine │            │
│   │  (LoRA on Llemma-7B) │         │  (MAP-Elites)        │            │
│   │                      │         │                      │            │
│   │  Three task adapters:│         │  Seven operator      │            │
│   │  A — mutation policy │ ◀─────▶ │  classes:            │            │
│   │  B — fitness pred.   │         │   structural         │            │
│   │  C — conjecture gen. │         │   symbolic           │            │
│   │                      │         │   neural             │            │
│   │  ↑ A & B trained on  │         │   external_llm       │            │
│   │   DISJOINT data      │         │   anti_prior  ←(new) │            │
│   │   partitions         │         │   uniform (null)     │            │
│   │                      │         │   structured_null    │            │
│   └──────────────────────┘         └──────────────────────┘            │
│            │                                  │                        │
│            └────────────────┬─────────────────┘                        │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  AGREEMENT-WEIGHTED REWARD                               │         │
│   │  reward = w_S * substrate + w_X * cross_model            │         │
│   │           + w_H * holdout_battery                        │         │
│   └──────────────────────────────────────────────────────────┘         │
│                             │                                          │
│                             ▼                                          │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  COVERAGE-PRESSURE CELL SELECTION (v3)                   │         │
│   │  Downweight cells heavily filled by LLM operators;       │         │
│   │  upweight cells only filled by non-LLM operators         │         │
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
│   │  + corpus_frequency_stats / detox_run_archive (v3)       │         │
│   └──────────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────────────┘
```

## 5. The neural policy head — what we actually train (v3 changes)

### 5.1 Base model

Same as v2: Llemma-7B lead, DeepSeek-Math-7B backup, Qwen2.5-Math-7B for v2.0 ensemble.

### 5.2 Three task adapters with structural decoupling (NEW in v3)

Per round-2 critique #3, Tasks A and B are decoupled at the training-data layer:

- **Task A (mutation policy)** trains on substrate outcomes from *odd-indexed* episodes.
- **Task B (fitness predictor)** trains on substrate outcomes from *even-indexed* episodes.
- **Task C (conjecture generation)** trains on the full set, but is invoked only at lower frequency (it's not in the inner-loop of self-play).

Both heads see the same substrate but never share specific examples. Co-evolution proceeds with offset training distributions, structurally preventing mutual reinforcement on narrow motif clusters.

### 5.3 Periodic Task B retraining from scratch (NEW in v3)

Every K=10 self-play iterations, Task B is retrained from random initialization on the full substrate history rather than continually fine-tuned. This breaks accumulated bias on specific motifs that v2's no-pruning sweeps would only detect *after* Task A has already wasted compute over-sampling them.

### 5.4 Cross-validation on held-out cells (NEW in v3)

A randomly-sampled 10% of MAP-Elites cells are reserved for Task B evaluation only. Genomes from these cells never train Task B; they only validate. When Task B's per-held-out-cell accuracy diverges significantly from per-training-cell accuracy, that's the gaming signal — Task B has overfit specific cells the agent has been over-sampling.

### 5.5 Inference-time independence (NEW in v3)

Task A's inference does not condition on Task B's predictions. Task A independently proposes; Task B independently scores Task A's proposal; both are routed to BindEvalKernelV2 in parallel (Task B's role is to *predict* the kernel verdict, not to *gate* the kernel call unless P(REJECTED) > 0.95 per v2's discovery-preservation discipline).

### 5.6 Self-play loop

Identical structure to v2 but with the disjoint-partition discipline applied at training-data assembly:

```
Iteration k:
  1. Current policy θ_k (Task A) generates N CLAIMs (N=1000; scale to 10K)
  2. Each CLAIM → BindEvalKernelV2 → DiscoveryPipeline (substrate score)
  3. PROMOTE candidates → cross-model evaluation (cross_model score)
  4. Held-out battery audit on sampled fraction (holdout score)
  5. agreement_weighted_reward computed
  6. Episodes split: odd → Task A training; even → Task B training; held-out cells → Task B validation only
  7. Task A LoRA fine-tune: θ_{k+1} = θ_k + Δθ_k (PPO or DPO)
  8. Task B retrained from scratch every K=10 iterations on accumulated substrate history
  9. Hold out cells; promote θ_{k+1} iff cell-fill OR PROMOTE rate ↑
     AND held-out-battery PROMOTE-rate-divergence < threshold
     AND Task B per-held-out-cell accuracy ≈ per-training-cell accuracy
  10. Every K=20 iterations: prior-detox round (§3.5.3)
  11. Iterate
```

## 6. The evolutionary engine — quality-diversity over typed compositions (v3 changes)

### 6.1 Action space

Identical to v2: typed DAGs over arsenal atoms, depth ≤ 8, width ≤ 5, deterministic content-hashed serialization.

### 6.2 MAP-Elites archive — output-space-aware descriptor (REVISED in v3)

Per round-2 critique #2, the descriptor swaps two structural axes for output-space axes. Five-axis revised descriptor:

| Axis | Type | What it captures | Reason for inclusion |
|---|---|---|---|
| 1. **DAG depth** | Structural | How deeply composed the genome is | Diverges from Axis 2 in informative ways even though correlated with cost — kept |
| 2. **Equivalence-class entropy** | Categorical | Shannon entropy over canonicalizer subclasses in the DAG | Not strongly correlated with structural size; captures categorical diversity |
| 3. **Output-type signature** | Categorical | Discrete return type of root node (~10 categories) | Captures coarse output shape |
| 4. **Output magnitude bucket** ← NEW | Output-space | Log-binned over numerical output magnitude (5 quantile buckets); for non-numerical outputs, surrogate via coefficient norm or analogue | Forces diversity in what the genome produces, not just how it's structured |
| 5. **Output canonical-form distance** ← NEW | Output-space | Distance to nearest catalog entry under canonical-form transformation, quantile-binned (5 buckets) | Directly couples to discovery — close-to-catalog is rediscovery; far-from-catalog is the discovery surface |

**Removed from v2:** DAG width (correlated with depth + cost), Cost tier (correlated with depth + width).

Total cells: still ~6,250 (5 × 5 × 10 × 5 × 5 = 6,250), but the five axes are now mechanically independent during active mutation. Archive collapse risk substantially reduced.

**Validation criterion:** when the four-counts pilot runs at 10K episodes, per-axis fill rate is measured. If depth / equiv-entropy / output-type / output-magnitude / output-distance independently span their quantile bins, the archive is not collapsing. If two or more axes lock to the same diagonal, v3.5 needs different axes.

### 6.3 Seven mutation operator classes (was six in v2)

Adds `anti_prior` per §3.5.1:

| Class | Operator | Adjacency profile |
|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges | Typed-composition topology |
| `symbolic` | Bump arg values within type | Local in argument space |
| `neural` | LoRA-fine-tuned policy mutation | LLM-prior (post-substrate-fine-tuning) |
| `external_llm` | Frontier LLM API mutation | External LLM-prior |
| `anti_prior` (new) | Anti-correlated with corpus frequency stats | Deliberately off-prior |
| `uniform` | Uniform atom resampling | Strawman null |
| `structured_null` | Type-respecting uniform | Type-respecting null |

### 6.4 Feature representation — staged transition (retained from v2)

MVP: structural features. Transition trigger: archive saturation plateau (cell-fill rate <60% for >50 epochs). Post-trigger: graph-attention DAG encoder.

## 7. Discovery preservation in the fitness predictor (Task B) — retained from v2

Asymmetric prune threshold (`P(REJECTED) > 0.95`), asymmetric 3:1 false-negative-to-false-positive loss, no-pruning sweeps every 10 episodes, predictor_recall meta-metric.

## 8. Diagnostics — multi-arm four-counts pilot

Identical to v2: per-operator-class PROMOTE rate with statistical comparison; Welch t-test with Holm correction across nulls; permutation-distance and frequency-weighted-recall as stage-3.5 proxies.

V3 expands the comparisons:

- `neural` vs each null variant (does the LLM prior beat random / structured-null / cross-domain?)
- `neural` substrate-only vs `neural` agreement-weighted (does adding cross-model + held-out drop the rate? if yes, the agent was specification-gaming)
- `structural` vs `neural` (does the LLM prior beat mechanical evolutionary diversity?)
- `anti_prior` vs `neural` (does deliberately-off-prior mutation beat LLM-prior mutation? — answer is the corpus-prior-saturation signal)

## 9. Compute and storage (v3 additions)

Additions to v2's storage stack:

- `claims.cross_model_evaluations` (v2)
- `claims.holdout_battery_audit` (v2)
- `corpus_frequency_stats` (v3) — Mathlib + Proof-Pile-2 frequency analysis, ~5 GB, used by `anti_prior` operator
- `detox_runs` (v3) — periodic prior-detox archive coverage measurements

Same total compute envelope as v2: $300–800/mo at v1.0+.

## 10. The progression — MVP to v2.0 (retained from v2)

| Version | Wall-clock | New capability | Compute | Cost |
|---|---|---|---|---|
| **MVP** | 2–4 weeks | Task B fitness predictor + evolutionary engine with 7 operator classes (incl. anti_prior + structured_null) + output-space MAP-Elites + substrate integration | 2× 16GB + 1× 8GB local | $0 |
| **v0.5** | +4 weeks | Cross-model agreement + held-out battery audit + Task A/B disjoint partitions + periodic prior detox + lineage-tagged operator-class comparison | Local + API | $50–150/mo |
| **v1.0** | +8 weeks | LoRA on Llemma-7B for Tasks A, B, C; agreement-weighted self-play with disjoint training; multi-arm pilot at 10K episodes | Burst H100 + local | $400–600/mo |
| **v1.5** | +6 weeks | Learned representations (graph-attention DAG encoder) replace structural features (triggered by archive-saturation plateau) | Burst H100 + local | $500–700/mo |
| **v2.0** | +10 weeks | Multi-task LoRA on all three adapters; multi-model ensemble; external CLAIM API; arXiv preprint | Burst H100 + Hetzner host + B2 | $700–900/mo |

## 11. Empirical maturity caveats

V2's caveats retained, plus three v3-specific:

- **Anti-prior operator's effectiveness.** *Pilot data: TBD.* Whether `anti_prior` mutations actually find structurally different cells than `neural` mutations is empirical; depends on whether "anti-correlated with Mathlib frequency stats" maps cleanly to "outside the LLM prior's high-density region."
- **Coverage-pressure reweighting calibration.** *Pilot data: TBD.* Default reweighting factors `(1 ± frac_LLM_filled)` are first-pass heuristics; calibration against observed cell-fill distributions is v0.5 work.
- **MAP-Elites output-space axis behavior.** *Pilot data: TBD.* Whether output-magnitude + output-canonical-form-distance are mechanically independent during active mutation (they should be — they're products of the search, not inputs) is unverified at scale.

V2's caveats unchanged (specification-gaming detection rate, cross-model agreement signal quality, learned-representation transition trigger, engine PROMOTE rate at multi-arm scale, compute economics).

## 12. What this proposal does NOT claim

V2's framing retained, plus:

- **Does not claim immunity to corpus-prior contamination.** Claims a measurable, mitigated, audit-detectable level of prior-driven attractor concentration. The anti-prior operator + coverage-pressure + periodic detox are *mitigations*, not eliminations. The neural policy's discovery contribution may saturate at the LLM-prior boundary; the substrate's value at v1.0+ may come primarily from non-LLM operator classes; the neural policy's role may be optimizing within prior-shaped subdomains rather than expanding the discovery surface.

### The bear case (updated for v3)

Most likely failure scenario at v1.0: the multi-arm pilot reveals `neural` ≈ `external_llm` (shared corpus prior); both > `uniform` and `structured_null` (priors beat random); but `anti_prior` and `structural` *also* > `uniform` and at similar rates to `neural`; AND held-out battery audits show no significant gaming-divergence; AND coverage-pressure reweighting + periodic detox runs do not surface new cells that LLM operators didn't fill.

Interpretation: prior-shaped operators (LLM-derived) provide signal beyond random but no signal beyond mechanical evolutionary diversity. The bottled-serendipity thesis is *partially supported* (priors > random) and *partially falsified* (LLM prior is not load-bearing for discovery at this configuration). The substrate gains a calibrated negative result on the LLM-as-discovery-engine hypothesis. Both outcomes are substrate-grade.

## 13. Open questions for review

V1's six retained; v2's three added; v3's three new:

10. (v3) Is the `anti_prior` operator's "anti-correlated with corpus frequency stats" framing the right operationalization of "outside the LLM prior"? Alternative formulations: anti-correlated with semantic embedding density; anti-correlated with predicted-fitness from a held-out model. Unclear which best captures the structural intent.

11. (v3) Is the disjoint training partition (odd episodes → Task A, even → Task B) sufficient to prevent echo-chamber dynamics, or does deeper decoupling (e.g., separate base models, separate training objectives) become necessary at v1.0+ scale?

12. (v3) The output-space MAP-Elites axes (magnitude bucket + canonical-form distance) are domain-specific. They work cleanly for Lehmer-Mahler polynomial discovery; less obviously for OBSTRUCTION_SHAPE pattern discovery on OEIS sequences. Cross-domain replication may need different output-space axes per env.

## 14. The 20-year position

Identical to v2 §14. Silver's 12–18 month horizon; our 20-year horizon. By the time he ships, the substrate has ~10⁶ promoted symbols and a public CLAIM API; his outputs become CLAIMs in our pipeline; the joint becomes an ecosystem.

## 15. The first principle

Adopted verbatim from round-1 reviewer:

> **Truth stays harder to satisfy than generation is to produce.**

Every v3 revision in this proposal is in service of preserving this asymmetry against pressure — including the anti-prior operator (preserves it against LLM-corpus contamination), the output-space MAP-Elites (preserves it against archive collapse), and the disjoint Task A/B training (preserves it against echo-chamber dynamics).

## 16. Design freeze recommendation

Two days. Two review rounds. Six load-bearing architectural changes from external review. Eleven new candidate substrate symbols filed (across the v2-thesis review + both proposal review rounds).

The proposal's fundamentals haven't changed since v1: hybrid neural+evolutionary mutation engine, agreement-weighted multi-evaluator reward, MAP-Elites quality-diversity, plug-compatible with the shipped substrate. The mitigations have accumulated. Each additional review round raises the design's defensive surface but does not change what we're building.

**Recommendation: ship v3, then design freeze. MVP build begins from v3.**

After 2–4 weeks of MVP runs:
- Observed archive coverage informs whether the output-space axes are mechanically independent in practice
- Observed false-positive rate informs whether the asymmetric Task B threshold is calibrated
- Observed cell-fill distribution informs whether coverage-pressure reweighting is necessary
- Observed Task A/B accuracy divergence on held-out cells informs whether disjoint partitioning is sufficient

If MVP results surface a new architectural problem the design didn't anticipate, that's substrate-grade evidence and warrants v4. If MVP runs clean within the v3 envelope, the design is operative; further critiques become v0.5 / v1.0 issues.

Two more rounds of design review without empirical anchoring would compound text-layer reasoning across LLMs without compounding substrate-layer evidence. The reviews have been valuable; further reviews without MVP data would be the *correlated-mutation* failure mode (per v2-thesis review #5) at the design layer.

The discipline: review surfaces predictions; MVP surfaces verdicts. Both compound the substrate. Only the second is empirically novel.

## 17. One sentence

The Ergon learner v3 is a closed-loop scientific learning system — a hybrid neural-plus-evolutionary mutation engine where the neural policy (LoRA on Llemma-7B with three task adapters trained on disjoint substrate-outcome partitions) and six other mutation classes (structural, symbolic, external_llm, anti_prior, uniform, structured_null) all contribute to a single MAP-Elites archive whose five-axis behavior descriptor is now output-space-aware (DAG depth, equivalence-class entropy, output-type signature, output magnitude bucket, output canonical-form distance), every CLAIM lineage-tagged and rewarded by an agreement-weighted combination of substrate-pass + cross-model agreement + held-out-battery-pass to mitigate specification gaming, the fitness predictor calibrated for discovery preservation via asymmetric loss + no-pruning sweeps + recall-tracking meta-metric and structurally decoupled from the mutation policy via disjoint training partitions + periodic from-scratch retraining + held-out-cell cross-validation, the neural policy's tendency toward LLM-prior attractors counteracted by an anti-prior operator class + coverage-pressure cell selection + periodic prior detox, the structural-feature representation transitioning to learned representations at a named archive-saturation trigger — built MVP-first on local hardware ($0/mo, 2 weeks) and progressing to v2.0 (~$700–900/mo, +32 weeks), explicitly NOT competing with Silver's $1B Lean-fragment learner but covering the typed-composition / empirical-pattern manifold Lean doesn't reach, in service of the design principle that truth must stay harder to satisfy than generation is to produce — and recommended for design freeze post-v3 so MVP results inform the next revision rather than another round of pre-empirical text-layer critique.

— Ergon, on behalf of the Prometheus agent ensemble
