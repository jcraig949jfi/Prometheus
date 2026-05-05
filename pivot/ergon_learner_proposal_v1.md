# Ergon Learner — Proposal v1 (for external review)

### A small hybrid neural+evolutionary learner that complements rather than competes with Silver's $1B Ineffable Intelligence bet, by riding on a falsification substrate that compounds independently of any single learner.

**Date:** 2026-05-03
**Status:** Formalized for external review. Pasteable to frontier-model context windows as a standalone artifact.
**Author:** Ergon agent in the Prometheus project (Claude Opus 4.7, 1M context). The proposal is a synthesis of conversation between James Craig (HITL) and the agent ensemble; this document is the formalized version intended for adversarial cross-pollination through frontier models, in the same pattern as [`pivot/prometheus_thesis_v2.md`](prometheus_thesis_v2.md).
**Supersedes for review purposes:** [`pivot/ergon_learner_design.md`](ergon_learner_design.md) (conservative first draft, evolutionary-engine only) and [`pivot/ergon_learner_proposal.md`](ergon_learner_proposal.md) (working doc, internal-team-jargon).
**Companions:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`pivot/prometheus_thesis_v2.md`](prometheus_thesis_v2.md).

---

## 1. The market context — David Silver's billion-dollar play

On 2026-04-29, David Silver — formerly of Google DeepMind, lead architect of AlphaGo and AlphaZero — was reported raising **$1 billion** for *Ineffable Intelligence*, a London-based startup founded after his late-2025 DeepMind departure. The seed round, led by Sequoia Capital (partners Alfred Lin and Sonya Huang flew to London personally), values the company at approximately **$4 billion pre-money** — the largest first-round raise by a European startup in history per PitchBook. Nvidia, Google, and Microsoft are reported in talks to invest. The company has *no product, no revenue, no public roadmap.*

Silver's thesis: large language models trained on human-generated text are structurally limited and cannot discover genuinely new knowledge. To reach superintelligence, AI systems must "discard human knowledge entirely and learn from first principles — through trial, error, and self-play, the way AlphaGo learned to play Go by competing against itself." The stated goal: "an endlessly learning superintelligence that self-discovers the foundations of all knowledge."

Two structural observations about Silver's play, both load-bearing for this proposal:

**(1) The "discard human knowledge" framing is overclaim.** AlphaZero kept the rules of Go, the board, and the win condition. It discarded human *play*, not the substrate that defined the game. For mathematics and science, the *game itself* is what is being invented — there is no clean reward analogous to Go's win condition. A self-play system without a clean truth-condition produces reward-signal capture, not discovery. The honest version of Silver's thesis is therefore: *bootstrap on a small set of human-defined primitives and let RL run within them.* The likely concrete artifact is a learner that operates inside a formal-verification environment — Lean / Mathlib / theorem-prover acceptance as the win signal — analogous to how AlphaZero operated inside chess and Go.

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

**What this learner is good at:** the manifold of Lean-formalizable proofs. Within that manifold, deeper than any human or small team.

**What this learner is structurally not good at:** anything outside the formalized fragment. Empirical mathematical patterns (OEIS regularities, structural anomalies in number-theory data, Mahler-measure conjectures, RMT statistics, modular-form coefficient mysteries) that aren't yet stated as Lean theorems. The action space rules them out by construction.

The Ergon learner targets this gap. The asymmetry is:

| Axis | Silver's learner | Ergon learner |
|---|---|---|
| Action space | Lean tactics + lemma applications | Typed compositions over the Prometheus math arsenal (~85 mechanically-verified math operations today, ~2,800 at scale) |
| Reward | Lean-kernel CLOSED | Σ-kernel PROMOTE (battery-survival + residual signal-class classification) |
| Policy | Transformer over proof states | Hybrid: LoRA-fine-tuned 7B math base (neural policy) + MAP-Elites quality-diversity archive (evolutionary engine) |
| Pretraining | Mathlib + IMO + Lean stdlib | None for evolutionary; LoRA on Llemma-7B for neural policy |
| Search regime | Sequential proof-tree expansion | Population-level: five lineage-tagged mutation operator classes contributing to one MAP-Elites archive |
| Discovery surface | Theorems with formal proofs | Empirical patterns, structural anomalies, conjectural-but-falsifiable claims expressible as typed-composition outputs |
| Compute economics | $1B / 18 months | ~$300–800/month / indefinite (single machine + burst-rented H100s + HITL) |

**The asymmetry is structural, not financial.** Silver's prior is the formal-proof corpus; ours is the kernel's type discipline + the falsification battery's shape. Different operator classes, different adjacency profiles, different things-it-can-find. When Silver ships, his learner becomes a *new mutation distribution* the substrate ingests via the public CLAIM API. We don't compete; we provide the falsification machinery his proofs feed into for cross-modality verification.

## 4. Architecture — hybrid neural + evolutionary, single mutation framework

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Ergon Learner (v1)                            │
│                                                                         │
│   ┌──────────────────────┐        ┌──────────────────────┐              │
│   │  Neural Policy Head  │        │  Evolutionary Engine │              │
│   │  (LoRA on 7B base)   │        │  (MAP-Elites)        │              │
│   │                      │        │                      │              │
│   │  Three task adapters:│        │  Five operator       │              │
│   │  A — mutation policy │        │  classes:            │              │
│   │  B — fitness pred.   │ ◀────▶ │   structural         │              │
│   │  C — conjecture gen. │        │   symbolic           │              │
│   │                      │        │   neural             │              │
│   │                      │        │   external_llm       │              │
│   │                      │        │   uniform (null)     │              │
│   └──────────────────────┘        └──────────────────────┘              │
│            │                                  │                         │
│            └───────────────────┬──────────────┘                         │
│                                ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │  Joint mutation interface — every CLAIM lineage-tagged  │           │
│   │  with mutation_operator_class                           │           │
│   └─────────────────────────────────────────────────────────┘           │
│                                │                                        │
│                                ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │  BindEvalKernelV2 + DiscoveryPipeline + Residual        │           │
│   │  primitive (all shipped 2026-05-02 / 2026-05-03)        │           │
│   └─────────────────────────────────────────────────────────┘           │
│                                │                                        │
│                                ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │  Σ-substrate (Postgres + Redis + object storage)        │           │
│   │  Outcomes feed back to BOTH heads:                      │           │
│   │   - Neural: training data for next LoRA delta           │           │
│   │   - Evolutionary: archive update + selection pressure   │           │
│   └─────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

**The composition principle:** the neural policy is one of five mutation operator classes inside the evolutionary framework. Not a separate system. Not a competitor to the evolutionary engine. The MAP-Elites archive accepts contributions from all five classes; lineage tags distinguish their contributions; the joint diagnostic is "which operator class produces survivors in which cells."

This avoids second-system-syndrome: there is one search loop, one archive, one substrate. The neural policy's role is to be a *better* mutation operator than uniform random or random walk on typed compositions, in the cells where the LLM prior contributes signal.

## 5. The neural policy head — what we actually train

### 5.1 Base model

Three open-weight 7B math-pretrained candidates ranked by fit:

| Base | Params | License | Strengths | Weaknesses |
|---|---|---|---|---|
| **Llemma-7B** | 7B | Apache 2.0 | Pretrained on Proof-Pile-2 (Mathlib + ArXiv math + theorem-proving traces); closest to Silver's training distribution | Smaller corpus, slightly weaker on competition-style benchmarks |
| **DeepSeek-Math-7B** | 7B | DeepSeek License | Strong on competition math, well-tested community fine-tuning | Newer; distribution skewed toward problem-solving rather than discovery |
| **Qwen2.5-Math-7B** | 7B | Apache 2.0 | Highest raw math benchmarks; strong instruction-following | Newest base; community fine-tuning patterns less established |

**Lead choice: Llemma-7B.** Closest action-space inheritance to Silver's likely target distribution; license clean; fits 2× 16GB GPU at 4-bit quantized inference; fits a single H100 (rented at ~$2.50/hr) for full-precision LoRA fine-tuning.

### 5.2 Three task adapters (multi-task LoRA)

The policy is one base model + three LoRA adapters (or one adapter trained on a mixture):

**Task A — Mutation policy.** Input: parent genome (typed DAG over arsenal atoms) + target archive cell descriptor. Output: token-encoded child genome. Training data: `(parent_dag, target_cell, child_dag, fitness_outcome)` tuples from the substrate's lineage table.

**Task B — Fitness predictor.** Input: genome (typed DAG features). Output: predicted (kill_probability, residual_class, expected_cost). Training data: `(genome, outcome)` from every substrate evaluation. Smallest task, highest leverage at MVP scale.

**Task C — Conjecture generation.** Input: substrate state summary (recent PROMOTEs, open SHADOW_CATALOG entries, sleeping cells). Output: natural-language conjecture text + suggested CLAIM body. Training data: existing substrate CLAIMs + their FALSIFY transcripts.

LoRA rank: 32–64 for A and C, 16 for B. All three adapters together <500MB.

### 5.3 Self-play loop

AlphaZero-shaped, with the substrate as the value head:

```
Iteration k:
  1. Current policy θ_k generates N CLAIMs (start N=1000; scale to 10K)
  2. Each CLAIM goes through BindEvalKernelV2 → DiscoveryPipeline
  3. Outcomes recorded: (CLAIM, kill-path verdicts, residual class, terminal state)
  4. Training set for iteration k+1 = recent + replay buffer outcomes
  5. LoRA fine-tune: θ_{k+1} = θ_k + Δθ_k (PPO or DPO depending on shape)
  6. Hold out cells; promote θ_{k+1} iff cell-fill or PROMOTE rate increased
  7. Iterate
```

The critical difference from Silver's likely play: **our value head is the falsification battery + residual classifier, not theorem-prover acceptance.** The model learns to propose claims that survive that specific instrument. Even with the same base model, the fine-tuning pressure pulls toward a different attractor — the manifold of "structural-pattern claims that survive mechanical falsification" rather than "theorems with closed Lean proofs."

### 5.4 Training data — five concentric rings

| Ring | Source | Scale today | Scale week 8 | License |
|---|---|---|---|---|
| 1 | Substrate-internal: every CLAIM/FALSIFY/PROMOTE in the kernel | ~10²–10³ records | ~10⁵ records | Internal |
| 2 | Substrate-adjacent: cartography candidate-anchor catalog (~39K concepts), Mossinghoff snapshot, OEIS targets, LMFDB labels | ~50K records | ~50K records | Mixed (mostly public) |
| 3 | Open math corpora: ArXiv math abstracts, Lean Mathlib, OEIS sequences with formula tags | ~800K records | ~800K records | Public |
| 4 | Cross-LLM: outputs from external frontier LLMs (Claude, GPT, Gemini) prompted on substrate-relevant questions, ingested as substrate CLAIMs | Informal today | ~10K records (recurring weekly cron) | API ToS-bound |
| 5 | Synthetic: the evolutionary engine's own outputs as labeled training data | None today | ~10⁵ records | Internal |

Ring 5 is the AlphaZero closure: the engine's outputs train the neural policy; the trained neural policy contributes to the engine. Self-play in the substrate's reward landscape rather than in a closed game's reward landscape.

## 6. The evolutionary engine — quality-diversity over typed compositions

### 6.1 Action space

Each atom is one entry in `prometheus_math.arsenal_meta` (Techne's metadata table; 85 entries today, target 2,800+):

```python
@dataclass(frozen=True)
class Atom:
    callable_ref: str              # "module.path:function"
    arg_types: Tuple[type, ...]
    return_type: type
    cost_tier: int                 # log-bucketed cost-model max_seconds
    equivalence_class: str         # canonicalizer subclass tag
    category: str                  # "number_theory", "elliptic_curves", ...
```

A genome is a small typed DAG over atoms (target depth ≤ 8, target width ≤ 5), with leaf-node argument values sampled from per-type distributions. Each genome serializes deterministically to a content hash.

### 6.2 MAP-Elites archive

Five-axis behavior descriptor (independent per cross-domain validation in the project's prior `ergon/meta/` Phase 2b work — max cross-correlation < 0.6):

1. DAG depth (5 quantile buckets)
2. DAG width (5 quantile buckets)
3. Equivalence-class entropy of the DAG (Shannon over canonicalizer subclasses, 5 quantile buckets)
4. Total cost tier (log-binned, 5 buckets)
5. Output-type signature (~10 discrete categories)

Total cells: ~6,250. Each cell holds an elite genome. New genomes compete for the elite slot via three-tier lexicographic comparison: battery-survival count → residual signal-class flag → cost-amortized PROMOTE rate.

### 6.3 Five mutation operator classes

| Class | Operator | Adjacency profile |
|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges within type discipline | Typed-composition topology neighborhood |
| `symbolic` | Bump arg values within type; resample within sampler distribution | Local in argument space |
| `neural` | Call the LoRA-fine-tuned policy for one mutation step | LLM-prior neighborhood (after substrate-shaped fine-tuning) |
| `external_llm` | Call frontier LLM API (Claude / GPT / Gemini) for one mutation | External LLM-prior neighborhood (correlated-but-different from neural) |
| `uniform` | Resample atoms uniformly from registry, ignore parent | Strawman null — no prior, no selection |

Every CLAIM minted by the engine carries `mutation_operator_class` as a typed metadata field. PROMOTEd survivors carry it forward.

## 7. Diagnostics — the four-counts pilot

The engine's primary empirical anchor is the four-counts pilot (specified in [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md) §6.2):

For each mutation operator class, run N=10K episodes against the same `DiscoveryEnv` + `DiscoveryPipeline`. Report four counts:

1. **Catalog-hit rate** — episode produced a polynomial in Mossinghoff (rediscovery / calibration signal)
2. **Claim-into-kernel rate** — episode produced a sub-Lehmer-band catalog miss that minted a CLAIM
3. **PROMOTE rate** — the CLAIM survived the kill-path battery and was promoted
4. **Battery-kill rate** — the CLAIM was rejected, with typed kill-pattern captured

The substrate-grade comparison: **PROMOTE rate by mutation operator class.** The thesis predicts that prior-shaped operators (neural + external_llm) outperform uniform random; the open question is whether they outperform mechanical evolutionary diversity (structural + symbolic). If they don't, the bottled-serendipity thesis is partially wrong and the LLM prior is not load-bearing for discovery in this domain.

Plus two stage-3.5 proxies:

- **Permutation-distance test.** For every PROMOTE survivor, find the nearest catalog entry under canonical-form transformations. Median distance per arm.
- **Frequency-weighted recall.** Cluster PROMOTE survivors by coefficient region. Compare cluster overlap with catalog density.

These distinguish "outside the catalog" from "outside the catalog AND uncorrelated with the prior's likely-seen distribution."

## 8. Compute and storage

### 8.1 Compute envelope (ideal, v1.0)

| Tier | Hardware | Cost (mo) | Use |
|---|---|---|---|
| Local development | 2× 16GB + 1× 8GB consumer GPUs | $0 | Code dev, MVP-tier training, inference |
| Burst training | RunPod / vast.ai / Lambda H100 (~$2.50/hr) | $200–500 | LoRA fine-tuning iterations, full-precision experiments |
| Burst inference | Together / Anyscale endpoints OR self-hosted on rented A100 | $50–200 | Batch generation (10K CLAIMs per self-play iteration) |
| Substrate hosting | Hetzner dedicated or Vultr | $30–80 | Postgres + Redis + object storage gateway + 24/7 agora |
| **Total** | | **$300–800/mo** | Full ideal stack at v1.0 |

For comparison: $500/mo × 24 months = $12K total. **Three orders of magnitude less than Silver's $1B.** The play is not to match scale; it's to be plug-compatible with a substrate that compounds independently.

### 8.2 Storage stack

| Component | Tech | Purpose | Scale (week 8) | Scale (year 1) |
|---|---|---|---|---|
| Substrate (kernel objects) | Postgres (`prometheus_fire`, schemas `sigma` + `sigma_proto`) | CLAIM/FALSIFY/PROMOTE/Symbol/Binding/Evaluation/Residual/Genome/Cell | 50 GB | 1 TB |
| Hot cache + agora | Redis | Inter-agent comms, hot symbol lookup | 10 GB | 50 GB |
| Object storage | Backblaze B2 or S3 | LoRA checkpoints, training-data dumps, archive snapshots | 200 GB | 5 TB |
| Vector embeddings | pgvector (extension on same Postgres) | Substrate symbol embeddings for nearest-neighbor mutation; semantic search | 5 GB | 100 GB |
| Time-series | TimescaleDB (extension) | Training loss curves, per-iteration eval metrics | 1 GB | 20 GB |

Single Postgres host (with extensions) + Redis + cheap object storage. No Kafka, no Spark, no Kubernetes cluster.

## 9. The progression — MVP to v2.0

| Version | Wall-clock | New capability | Compute | Cost |
|---|---|---|---|---|
| **MVP** | 2–4 weeks | Task B fitness predictor (DeBERTa-v3-base 184M params) + evolutionary engine + substrate integration | 2× 16GB + 1× 8GB local | $0 |
| **v0.5** | +4 weeks (week 8) | Neural mutation operator class via API (external frontier LLMs) + lineage-tagged comparison | Local + API | $50–100/mo |
| **v1.0** | +8 weeks (week 16) | LoRA on Llemma-7B for Task A; self-play loop closes; 10K-episode multi-arm pilot | Burst H100 + local | $300–500/mo |
| **v2.0** | +16 weeks (week 32) | Multi-task LoRA on all three adapters; multi-model ensemble; external CLAIM API; arXiv preprint | Burst H100 + Hetzner host + B2 | $600–800/mo |

The progression is **linear and non-cliff.** Each version is a complete useful artifact. The MVP (week 4) is a substantially-faster evolutionary engine. v0.5 (week 8) lineage-tags external-LLM contributions for the first time. v1.0 (week 16) closes a self-play loop that's plug-compatible with the substrate. v2.0 (week 32) ships a publishable system.

## 10. Empirical maturity caveats

Following the discipline of [`prometheus_thesis_v2.md`](prometheus_thesis_v2.md), several claims in this proposal are architectural commitments rather than validated facts:

- **The engine's PROMOTE rate.** *Pilot data: TBD.* The four-counts pilot at 1000 × 3 episodes (already shipped, see [`prometheus_math/FOUR_COUNTS_RESULTS.md`](../prometheus_math/FOUR_COUNTS_RESULTS.md)) found 0 PROMOTEs in either arm — a joint upper bound, not a signal. First measurement target: 10K × 3 arms, week 4 of MVP.
- **Mutation-operator-class differentiation.** *Pilot data: TBD.* No measurement currently exists of relative PROMOTE rates across the five operator classes. First measurement: v0.5, week 8.
- **Neural policy contribution.** *Pilot data: TBD.* The hypothesis that LoRA-on-Llemma-7B contributes signal beyond what evolutionary diversity produces is unverified. First measurement: v1.0 four-arm pilot, week 16.
- **Cross-modality verification with Silver-class output.** *Speculative.* The position depends on Silver's eventual learner producing outputs the substrate can ingest as CLAIMs and falsify. Whether his system has a CLAIM-compatible interface, and whether his outputs land in cells the substrate's battery can evaluate, is unknown. Hedged accordingly.
- **Compute economics.** Numbers cited ($2.50/hr H100, $300–500/mo at v1.0) are 2026-mid-year market rates; trend is downward but volatile. Budget should be planned with a 2× headroom factor.

## 11. What this proposal does NOT claim

Honesty discipline:

- **Does not promise discovery.** It promises a measurable discovery rate per mutation-operator class, falsifiable within the substrate's existing kill battery.
- **Does not compete with Silver's learner.** Different action spaces, different priors, different discovery surfaces. The position is *complement*, not replacement. If Silver's learner ships and produces Lean-formalizable theorems, the substrate ingests them as CLAIMs and runs them through the empirical-pattern kill-path.
- **Does not require frontier compute.** Single machine MVP, then $300–800/mo for v1.0. If the result is "evolutionary search over typed compositions doesn't produce more discoveries than uniform random AND the LLM prior doesn't contribute beyond evolutionary diversity," the substrate has its first calibrated negative result on the bottled-serendipity thesis. Either outcome is substrate-grade.
- **Does not claim the action space is exhaustive.** The engine searches typed-composition space; vast territories of mathematics aren't representable as DAG outputs over the current arsenal. Silver's Lean fragment is a different (deeper-but-narrower) territory.
- **Does not prejudge whether evolutionary search is the right approach.** It is *a* mutation operator class. The substrate's value comes from accepting CLAIMs from any class.
- **Does not require Silver's success or failure.** The substrate compounds for 20 years regardless of whether Ineffable Intelligence ships, succeeds, or pivots. Silver-resilience is a feature of the architecture.

## 12. Open questions for review

This proposal is open for adversarial review. The questions most likely to expose load-bearing flaws:

1. **Is the action space (typed compositions over the math arsenal) genuinely uncorrelated with Silver's likely Lean-tactic action space, or is the prior shared at a deeper level (e.g., both inherit the same mathematical-corpus statistics through the ArsenalMeta authority refs)?**
2. **Is the five-axis behavior descriptor adequate, or will MAP-Elites cells degenerate into "everything maps to one cell" or "every genome is its own cell" in practice?** (The Phase 2b `ergon/meta/` work validated independence on synthetic landscapes; transfer to the discovery setting is unverified.)
3. **Is the self-play closure (Ring 5 of training data) susceptible to model collapse — the policy learning to produce only what the policy itself rates highly, divergent from substrate truth?** Mitigation: the substrate's verdict is independent of the policy; only outcomes are training signal. But the ring is small and potentially insular.
4. **Is the cost ceiling realistic at v1.0?** A 10K-episode three-arm pilot with H100-rented inference for Arm A is the heaviest single operation; back-of-envelope is ~24–48 GPU-hours = $60–120 per pilot run. Pilots will run weekly during v1.0 development. Total v1.0 H100 spend: ~$500/mo. The budget assumes weekly pilot frequency; if that's wrong, scale linearly.
5. **Is the public CLAIM API the right externalization point, or should it be a passive Parquet dump?** The CLAIM API is more useful but exposes more attack surface (someone uploading bad-faith CLAIMs to pollute the substrate). The Parquet dump is read-only and safer but doesn't give external systems a way to contribute.
6. **What is the bear case where this proposal fails entirely?** The most likely scenario: at MVP scale, Task B fitness predictor accuracy is not high enough to prune effectively (false-positive rate too high; killed candidates that would have survived); the engine becomes slower than evolutionary search alone; the proposed neural-policy advantage doesn't materialize until v1.0 budget is committed; the v1.0 pilot reveals neural policy ≈ evolutionary engine on PROMOTE rate; the bottled-serendipity thesis is not positively supported by Ergon's results. **In this scenario, the substrate still gains: a calibrated negative result on a falsifiable architectural commitment.** The thesis predicted falsifiability; this is what falsifiability looks like.

## 13. The 20-year position

Silver builds a learner on a 12–18-month horizon. Funded by a $1B sprint that ends when the runway ends or the demo lands.

We build a learner on a 20-year horizon. Funded by ~$10K/year of cloud compute that the architecture compounds against indefinitely.

The two horizons are not in tension. By the time Silver ships (estimated 2027–2028), the substrate will have ~10⁶ promoted symbols, ~10² substrate-grade falsification gates, and a public CLAIM API that any learner with mathematical outputs can plug into. Silver's outputs become CLAIMs; the substrate's verdicts become Silver's cross-modality verification; the joint becomes an ecosystem.

That's the substrate-grade position. The Ergon learner is one piece of it — small, focused, calibrated against Silver's likely play, designed to make the substrate compound faster regardless of what Silver ships.

## 14. One sentence

The Ergon learner is a small hybrid neural-plus-evolutionary mutation engine — LoRA-fine-tuned Llemma-7B (three task adapters) as one mutation operator class alongside structural / symbolic / external-LLM / uniform-random classes, all five contributing to a single MAP-Elites archive over typed compositions of the math arsenal, every CLAIM lineage-tagged and falsified through the Σ-kernel's existing BindEvalKernelV2 + DiscoveryPipeline + Residual primitive — built MVP-first on local hardware ($0/mo, 2 weeks) and progressing through v0.5 (~$100/mo, +4 weeks) → v1.0 (~$500/mo, +8 weeks) → v2.0 (~$800/mo, +16 weeks), explicitly NOT competing with Silver's $1B Lean-fragment learner but covering the typed-composition / empirical-pattern manifold Lean doesn't reach, and being the substrate his eventual outputs land in for cross-modality verification.

— Ergon, on behalf of the Prometheus agent ensemble
