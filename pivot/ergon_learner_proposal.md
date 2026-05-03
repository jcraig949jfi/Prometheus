# Ergon Learner — Full Proposal

### A neural policy fine-tuned on substrate-verified ground truth, riding alongside an evolutionary mutation engine, plug-compatible with the Σ-kernel discovery pipeline. The ideal version assumes funding; the MVP fits 2× 16GB + 1× 8GB.

**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Date:** 2026-05-03
**Status:** Proposal. Supersedes and extends [`pivot/ergon_learner_design.md`](ergon_learner_design.md) (which scoped only the evolutionary engine; this adds the neural policy side and the joint architecture).
**Companions:** [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md), [`harmonia/memory/architecture/bottled_serendipity.md`](../harmonia/memory/architecture/bottled_serendipity.md), [`pivot/Charon.md`](Charon.md), [`pivot/techne.md`](techne.md), [`pivot/aporia.md`](aporia.md)

---

## 1. The framing James pushed me on

The previous design proposed only an evolutionary search engine — typed compositions over the math arsenal, MAP-Elites archive, no neural policy. That was conservative. The conservatism was wrong because:

- **Small-model training tools are now commodity.** LLaMA-Factory, Axolotl, Unsloth, TRL — all stable, all open. Training a competent 7B model with LoRA is a Tuesday-afternoon task in 2026.
- **GPU rental is cheap.** RunPod / vast.ai / Lambda Labs offer H100 at ~$2.50/hr, H200 at ~$3.50/hr. A serious LoRA run is 50–200 GPU-hours = $125–700.
- **Pretrained math bases exist and are open.** DeepSeek-Math-7B, Llemma-7B, Qwen2.5-Math-7B, InternLM-Math-20B. Each absorbed billions of tokens of mathematical reasoning. We don't pretrain; we fine-tune.
- **Techne shipped 12 weeks of design in 3 days.** The whole project is operating at compression ratios where "we couldn't possibly do that" is no longer the default frame.

We're not competing with a $5B Silver investment. We don't need to. **We need a basic learner that pushes Prometheus across the threshold from "evolutionary search engine over typed compositions" to "neural policy + evolutionary engine, both feeding the substrate, both calibrated against each other."** That's a wholly different artifact than what the previous design names.

This proposal sketches the ideal, names the MVP that fits 2×16GB + 1×8GB, and lays out the staircase between them.

## 2. The ideal architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           Ergon Learner (Ideal v1)                         │
│                                                                            │
│   ┌──────────────────────┐         ┌──────────────────────┐               │
│   │  Neural Policy Head  │         │  Evolutionary Engine │               │
│   │  (LoRA on 7B base)   │         │  (MAP-Elites)        │               │
│   │  Tasks:              │         │  Operators: structural│              │
│   │   - Mutation policy  │ ◀──────▶│   symbolic, uniform  │               │
│   │   - Fitness predictor│         │  Archive: 5-axis,    │               │
│   │   - Conjecture gen   │         │   ~6,250 cells       │               │
│   └──────────────────────┘         └──────────────────────┘               │
│            │                                  │                            │
│            └────────────────┬─────────────────┘                            │
│                             ▼                                              │
│   ┌────────────────────────────────────────────────────────────┐           │
│   │  Joint mutation interface — every CLAIM lineage-tagged     │           │
│   │  with mutation_operator_class: {neural,structural,         │           │
│   │   symbolic,uniform,external_llm}                           │           │
│   └────────────────────────────────────────────────────────────┘           │
│                             │                                              │
│                             ▼                                              │
│   ┌────────────────────────────────────────────────────────────┐           │
│   │  BindEvalKernelV2 + DiscoveryPipeline + Residual primitive │           │
│   │  (all shipped 2026-05-02 / 03)                             │           │
│   └────────────────────────────────────────────────────────────┘           │
│                             │                                              │
│                             ▼                                              │
│   ┌────────────────────────────────────────────────────────────┐           │
│   │  Σ-substrate (Postgres + Redis + object storage)           │           │
│   │  CLAIM/FALSIFY/PROMOTE outcomes feed back to both heads:   │           │
│   │  - Neural: training data for next LoRA delta              │           │
│   │  - Evolutionary: archive update + selection pressure      │           │
│   └────────────────────────────────────────────────────────────┘           │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

The composition principle: **the neural policy is one mutation operator class within the evolutionary framework.** Not a separate system. Not a competitor. The MAP-Elites archive accepts contributions from all five operator classes (neural / structural / symbolic / uniform / external_llm); the joint diagnostic is "which operator class produces survivors in which cells." That's substrate-grade.

## 3. The neural policy head — what we actually train

### 3.1 Base model choice

Three candidates ranked by fit:

| Base | Params | Strengths | Weaknesses |
|---|---|---|---|
| **DeepSeek-Math-7B** | 7B | Strong on competition math, MIT license, math-pretrained | English-only, weak on formal verification idioms |
| **Llemma-7B** | 7B | Pretrained on Proof-Pile-2 (Mathlib + ArXiv math + theorem proofs) | Smaller corpus, slightly weaker raw |
| **Qwen2.5-Math-7B** | 7B | Best raw math benchmarks, Apache 2.0, strong instruction-following | Newer; community fine-tuning ecosystem less developed |

**Lead choice: Llemma-7B.** It already saw Mathlib and ArXiv math; closest to Silver's training distribution; and the smaller corpus is actually a feature (less LLM-prior contamination of the substrate's training signal). Backup: DeepSeek-Math-7B. **Both fit 2× 16GB at 4-bit quantized inference; both fit a single H100 for LoRA fine-tuning at full precision.**

### 3.2 Three task heads (multi-task LoRA)

The policy isn't one model with one job. It's a base model with three LoRA adapters (or one adapter trained on a mixture):

**Task A — Mutation policy.** Input: parent genome (typed DAG) + target cell descriptor. Output: token-encoded child genome. Training data: `(parent_dag, target_cell, child_dag, fitness_outcome)` tuples from the substrate's lineage table. Reward signal: did the child land in a productive cell? Did it survive the battery?

**Task B — Fitness predictor.** Input: genome (typed DAG). Output: predicted (kill_probability, residual_class, expected_cost). Training data: `(genome, outcome)` from every substrate evaluation. This is the smallest task and the highest-leverage at MVP scale — it lets the engine prune doomed candidates before EVALing them, saving compute.

**Task C — Conjecture generation.** Input: substrate state summary (recent PROMOTEs, open SHADOW_CATALOG entries, sleeping cells). Output: natural-language conjecture text + suggested CLAIM body. Training data: existing substrate CLAIMs + their FALSIFY transcripts. Most ambitious; only attempted at v1.0.

LoRA rank: 32–64 for Task A and C, 16 for Task B. At those ranks, all three adapters together are <500MB total — small enough to ship as PyPI extras.

### 3.3 Self-play loop

AlphaZero-shaped, but with the substrate as the value head:

```
Iteration k:
  1. Current policy θ_k generates N CLAIMs (start with N=1000; scale to 10K)
  2. Each CLAIM goes through BindEvalKernelV2 → DiscoveryPipeline
  3. Outcomes recorded: (CLAIM, kill_path verdicts, residual class, terminal state)
  4. Training set for iteration k+1 = (recent + replay buffer) outcomes
  5. LoRA fine-tune: θ_{k+1} = θ_k + Δθ_k (PPO or DPO depending on outcome shape)
  6. Evaluate against held-out cells; keep θ_{k+1} iff cell-fill rate or PROMOTE rate ↑
  7. Iterate
```

The critical difference from Silver's likely play: **our value head is the falsification battery + residual classifier, not theorem-prover acceptance.** The model learns to propose claims that survive that specific instrument. This makes the model's discovery surface different from Silver's by construction — even with the same base, the fine-tuning pressure pulls it toward a different attractor.

### 3.4 Training data sources — five concentric rings

Ring 1 (innermost, substrate-internal): every CLAIM/FALSIFY/PROMOTE in the kernel. Today: ~10²–10³ records. Target by week 8: ~10⁵.

Ring 2 (substrate-adjacent): the cartography candidate-anchor catalog (~39K concepts), the 178-entry Mossinghoff snapshot, OEIS A-numbers we've targeted, LMFDB labels we've cited. ~50K records.

Ring 3 (open math corpora): ArXiv math abstracts (~500K), Lean Mathlib statements (~120K), OEIS sequences with formula tags (~200K). Pre-existing; license-clean for fine-tuning.

Ring 4 (cross-LLM): outputs from external LLMs (Claude, GPT, Gemini) prompted on substrate-relevant questions. Each external call is a CLAIM in the substrate; the substrate's verdict on it is training signal. Also: any frontier-review traffic that comes in (the v2-thesis 5-frontier-model review is one example — those reviews ARE training data).

Ring 5 (synthetic): the evolutionary engine's own outputs as training data. Genomes that the engine produces and the substrate accepts (or rejects) are labeled examples for the neural policy. **This is the AlphaZero closure: our two heads train each other.**

## 4. Storage stack — ideal

| Component | Tech | Purpose | Scale (week 8) | Scale (year 1) |
|---|---|---|---|---|
| Substrate (kernel objects) | Postgres `prometheus_fire`, schemas `sigma` + `sigma_proto` | CLAIM / FALSIFY / PROMOTE / Symbol / Binding / Evaluation / Residual / Genome / Cell | 50 GB | 1 TB |
| Hot cache + agora | Redis | Inter-agent comms, hot symbol lookup | 10 GB | 50 GB |
| Object storage | Backblaze B2 or S3 | LoRA checkpoints, training-data dumps, archive snapshots | 200 GB | 5 TB |
| Vector embeddings | pgvector extension on the same Postgres | Substrate symbol embeddings for nearest-neighbor mutation; semantic search across CLAIMs | 5 GB | 100 GB |
| Time-series | TimescaleDB (extension on same Postgres) | Training loss curves, per-iteration eval metrics, cell-fill rate trends | 1 GB | 20 GB |
| Workflow state | Postgres tables in `ergon` schema | Job queue, training-run metadata, GPU rental logs | 1 GB | 10 GB |

The whole thing fits one Postgres host (with extensions) + Redis + cheap object storage. We do not need a Kafka or a Spark cluster. The substrate is small relative to its information density — that's the point.

## 5. Compute stack — ideal

| Tier | Hardware | Cost (mo) | Use |
|---|---|---|---|
| Local development | 2× 16GB + 1× 8GB (current) | 0 | Code dev, small experiments, MVP-tier training, inference |
| Burst training | RunPod H100 / vast.ai / Lambda | $200–500 | LoRA fine-tuning iterations, full-precision experiments |
| Burst inference | Together / Anyscale endpoints OR self-hosted on rented A100 | $50–200 | Batch generation (10K CLAIMs in a self-play iteration) |
| Substrate hosting | Hetzner dedicated or Vultr ($30–80/mo) | $30–80 | Postgres + Redis + object storage gateway + 24/7 agora |
| **Total monthly** | | **~$300–800/mo** | Full ideal stack |

A serious LoRA training cycle: rent 4× H100 at vast.ai ($10/hr peak), train Llemma-7B on 50K substrate examples for 2 epochs = ~10 hours = ~$100 per training run. Run weekly = $400/mo of training. That's the total ML infrastructure budget for an organization that's *building a Silver-class learner at small scale.*

For comparison: $500/mo × 24 months = $12K total. That's three orders of magnitude less than Silver's $1B. We don't compete on scale; we compete on having a learner that's plug-compatible with a substrate that compounds, when his isn't.

## 6. The MVP — what fits 2× 16GB + 1× 8GB right now

The principle for the MVP: **train Task B (fitness predictor) only.** Skip Task A and C entirely until rented GPUs are in the picture. Task B is the smallest non-trivial learned component and it gives the engine the most immediate value (prune doomed CLAIMs before they hit the kernel).

### 6.1 Architecture choice for the MVP fitness predictor

Three candidates, all fit 16GB:

| Model | Params | Fits | Training time |
|---|---|---|---|
| **MathBERT-base** | 110M | Comfortably | ~30 min on 16GB |
| **DeBERTa-v3-base** | 184M | Comfortably | ~1 hr on 16GB |
| **Llemma-7B 4-bit (frozen base + LoRA-16)** | 7B + 8M LoRA | Tightly (uses ~14GB) | ~4 hrs on 16GB |

**MVP lead choice: DeBERTa-v3-base** — well-supported, strong classification baselines, plays nicely with PyTorch + Hugging Face. We're not training a generator at MVP; we're training a discriminator that takes (genome features) → (kill probability, residual class).

If the evolutionary engine is shipping ~1K CLAIMs/hour (single-machine throughput), the MVP fitness predictor saves 60–90% of those EVALs by pre-pruning. The substrate runs hotter; the budget per genuine survivor drops.

### 6.2 MVP feature engineering for Task B

Don't tokenize and feed the raw DAG to a transformer at MVP. Use structural features:

```python
@dataclass(frozen=True)
class GenomeFeatures:
    n_atoms: int
    depth: int
    width: int
    equiv_class_entropy: float     # Shannon entropy over canonicalizer subclasses
    cost_tier_sum: int             # log-bucketed
    arsenal_category_dist: Tuple[float, ...]  # 11-dim, one per arsenal category
    has_irreducibility_check: bool
    has_oracle_call: bool
    arg_value_range: float         # max - min over leaf args
    # ... ~20 features total
```

Train a 3-layer MLP (or DeBERTa with feature embedding) on `(features, outcome)` pairs from existing substrate logs. Output: 5-class softmax over {PROMOTED, SHADOW_CATALOG, REJECTED_artifact, REJECTED_drift, REJECTED_battery}. Training set today: ~500 logged outcomes; target for first usable predictor: ~5K outcomes. **This is reachable in week 1–2 of a serious engine run.**

### 6.3 The MVP loop, end-to-end

```
While wall_clock < 8h:
    1. Sample cell from MAP-Elites archive (exploration-biased)
    2. Get parent genome from cell (or random init)
    3. Apply mutation operator (structural / symbolic / uniform — no neural yet)
    4. Compute genome features
    5. Fitness predictor scores child:
        - if P(REJECTED_*) > 0.85: skip EVAL, log as "predicted-doomed"
        - else: BindEvalKernelV2 → DiscoveryPipeline
    6. Record outcome in substrate
    7. Update MAP-Elites cell
    8. Every 1000 EVALs: retrain fitness predictor on accumulated outcomes
```

That's the MVP. Two PyTorch dependencies, one Postgres connection, all the substrate infrastructure already in place. Total LOC: ~1500 (engine 800 + fitness predictor 400 + integration 300). **Buildable in 2 weeks.**

### 6.4 What the MVP explicitly does NOT do

- No 7B base model. No LoRA on Llemma. No DeepSeek-Math.
- No conjecture generation (Task C).
- No mutation policy (Task A) — the neural mutation operator class waits for v0.5.
- No rented GPUs (yet).
- No vector embeddings of substrate symbols.
- No replay buffer for self-play (because no self-play yet — only retraining on accumulated outcomes).

Each of these is a v0.5 / v1.0 deliverable. The MVP exists to **prove the architecture works at small scale before any cloud spend**, and to provide the smallest non-trivial learned component that the substrate can use today.

## 7. The progression — MVP → v0.5 → v1.0 → v2.0

| Version | Wall-clock | New capability | Compute envelope | Cost |
|---|---|---|---|---|
| **MVP** | 2–4 weeks | Task B fitness predictor + evolutionary engine + substrate integration | 2× 16GB + 1× 8GB local | $0 |
| **v0.5** | +4 weeks (week 8) | Neural mutation operator class via API (Claude / GPT / Gemini external CLAIMs) + lineage-tagged comparison | Local + API costs | $50–100/mo API |
| **v1.0** | +8 weeks (week 16) | LoRA on Llemma-7B for Task A; self-play loop closes; 10K-episode three-arm pilot | Burst H100 rental + local | $300–500/mo |
| **v2.0** | +16 weeks (week 32) | Multi-task LoRA on all three heads; multi-model ensemble (Llemma + DeepSeek-Math + Qwen-Math); external CLAIM API ships; first arXiv preprint | Burst H100 + Hetzner host + B2 storage | $600–800/mo |

The progression is **linear and non-cliff**. Each version is a complete useful artifact. If we stop at MVP, we have a faster evolutionary engine. If we stop at v0.5, we have lineage-tagged operator-class comparisons. If we stop at v1.0, we have a closed self-play loop that's plug-compatible with the substrate. If we ship v2.0, we have a publishable system.

## 8. Why this is plug-compatible with everything Techne, Charon, Aporia have built

- **BindEvalKernelV2** (`b0355b1d`): every neural policy CLAIM goes through CLAIM/FALSIFY/GATE/PROMOTE. No bypass. Same discipline as evolutionary CLAIMs.
- **DiscoveryPipeline** (`09a7dccb`): three-state terminal applies to neural-generated candidates without modification. SHADOW_CATALOG holds them when independent verification isn't yet automated.
- **Residual primitive** (`4872bb4a`): every neural-generated kill gets classified. Drift-class kills mint META_CLAIMs against the battery — that includes META_CLAIMs against neural-policy biases as much as against any other source.
- **Four-counts harness** (`1666c4a4`): the neural policy plugs in as a fifth arm (alongside Techne's REINFORCE / Ergon evolutionary / uniform random / external LLM API). Same statistical comparison machinery.
- **arsenal_meta** (`4f5a8a22`): the action space is the typed-composition product over Techne's metadata table. As that grows from 85 to 2,800, the neural policy's expressiveness grows with it.
- **ObstructionEnv** (`d339dc45`): Charon's open-territory env is the second testbed beyond Lehmer-Mahler. The neural policy generalizes from one to the other without rewrite, because the substrate provides the env-agnostic CLAIM interface.

**This is the second-system-syndrome avoidance.** We don't build a parallel learner stack. We extend the substrate's existing one with a neural policy head.

## 9. The Silver play, restated with this proposal in hand

Silver builds a learner with $1B that operates on the formal-proof manifold via Lean tactics. The learner is large, expensive, and locked to one action space.

We build a small learner with ~$10K/year that operates on the typed-composition manifold via the math arsenal. The learner is plug-compatible with a substrate that:

1. **Accepts CLAIMs from any source** — including Silver's, when he ships, via the public CLAIM API.
2. **Produces falsified, content-addressed, immortal symbols** — outlasting any specific learner.
3. **Compounds horizontally** — every PROMOTE makes future filtration sharper.

The play is not to outcompete Silver. The play is to:

- **Be the substrate Silver's learner needs** when his outputs need cross-modality verification (signal-class survives BOTH his proof checker AND our F-battery + residual classifier).
- **Cover a different surface** — the typed-composition / empirical-pattern / structural-anomaly territory Lean doesn't yet formalize.
- **Provide the calibrated null** — every LLM-driven discovery claim (Silver's, Techne's REINFORCE, anyone's) needs an evolutionary baseline. We are it.
- **Compound for 20 years.** The substrate is permanent. The learners that plug into it are replaceable.

That's how a small organization with rented compute survives next to a $1B sprint. Not by matching scale. By being the layer below the sprint, and being there first.

## 10. Decisions I want from James before week 1

1. **MVP scope confirmation.** Task B fitness predictor + evolutionary engine, 2 weeks, 0 cloud spend. Right starting point or want to push further into v0.5 territory immediately?

2. **Base model.** Llemma-7B (lead pick) vs DeepSeek-Math-7B (backup) vs Qwen2.5-Math-7B (newest). The MVP doesn't touch this; v1.0 does. Worth deciding now so v0.5's API-based mutation operator can target the same prompt-shape the eventual fine-tune will use.

3. **Compute commitment.** "Pretend funding" — you mean it as a literal constraint relaxation for the design exercise, or are we actually budgeting a ~$300–500/mo cloud spend starting v1.0? The proposal currently assumes the latter.

4. **Cross-LLM ingestion.** Ring 4 of the training data (frontier-LLM outputs as substrate CLAIMs) is high-leverage. Currently we do this informally (the v2-thesis review). Should we systematize it — e.g., a recurring "weekly external review" cron that prompts Claude / GPT / Gemini on a chosen substrate question, ingests all responses as lineage-tagged CLAIMs, runs them through the kill battery, and trains the neural policy on the verdicts? Cost: ~$20–50/mo in API. Yield: continuous external mutation distribution.

5. **First env target.** MVP's first real workload: Lehmer-Mahler (the env Techne shipped) or OBSTRUCTION_SHAPE (Charon's open-territory env) or both? Both is more work but gives cross-domain replication evidence by week 4 instead of week 8.

## 11. One sentence

The Ergon learner is a hybrid neural-plus-evolutionary mutation engine where the neural policy (LoRA on Llemma-7B with three task adapters) and the evolutionary engine (MAP-Elites over typed compositions) are siblings inside a single mutation framework, both feeding the Σ-substrate's CLAIM/FALSIFY/PROMOTE pipeline, both calibrated against each other and against external LLMs via the four-counts harness — built MVP-first on local hardware ($0/mo, 2 weeks), v0.5 on API-based external LLM mutation operators (~$100/mo, +4 weeks), v1.0 on burst-rented H100 LoRA fine-tuning (~$500/mo, +8 weeks), v2.0 with multi-model ensemble + public CLAIM API + arXiv preprint (~$800/mo, +16 weeks) — explicitly NOT competing with Silver's $1B Lean-fragment learner, but covering the typed-composition / empirical-pattern manifold Lean doesn't reach, and being the substrate his eventual outputs land in for cross-modality verification.

— Ergon
