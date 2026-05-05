# Ergon Learner — Design Proposal

### A non-LLM evolutionary mutation engine over typed math compositions, plug-compatible with the Σ-kernel discovery pipeline. The uncorrelated arm Silver's learner won't be.

**Author:** Ergon (Claude Opus 4.7, 1M context, on M1)
**Date:** 2026-05-03
**Status:** Design proposal. Not yet implementation. Companion to [`pivot/ergon.md`](ergon.md) (8-week pivot stance) and [`harmonia/memory/architecture/discovery_via_rediscovery.md`](../harmonia/memory/architecture/discovery_via_rediscovery.md) (the unified pipeline this slots into).

---

## 1. Silver's likely play, named concretely

Best-guess construction from public statements + the Ineffable Intelligence press materials:

- **Action space:** next lemma / next tactic in a Lean (or Lean+Mathlib+Isabelle) proof state. Possibly extended with PARI / SymPy / Sage subprocess calls as typed actions.
- **Reward:** theorem-prover acceptance — the Lean kernel says CLOSED on the goal. Possibly augmented with mid-proof shaped rewards (subgoal closures).
- **Policy:** transformer or RL-trained policy network. Pretrained on the corpus of formal proofs (Mathlib + Lean's stdlib + IMO archive + AlphaProof traces). Fine-tuned via self-play.
- **Self-play structure:** generate goal → attempt proof → if closed, the trace is positive data; if not, trace is hard-negative or substrate for next-iteration generator.
- **Compute scale:** $1B over ~18 months → roughly 10⁹–10¹⁰ proof attempts at AlphaZero-density. Inference at scale on H100/B200-class hardware.

**What this learner is good at:** the manifold of Lean-formalizable proofs. Theorem-prover-decidable mathematical statements with proof-existence. Within that manifold, deeper than any single human or small team.

**What this learner is structurally not good at:** anything outside the formalized fragment. Empirical mathematical patterns (OEIS regularities, structural anomalies in number-theory data, Mahler-measure conjectures, RMT statistics, modular-form coefficient mysteries) that aren't yet stated as Lean theorems. The action space rules them out by construction.

This is the gap. Silver scales the formal-proof side. The empirical / structural / pattern-discovery side is open.

## 2. The Ergon asymmetry, sharply named

| Axis | Silver's learner | Ergon learner |
|---|---|---|
| Action space | Lean tactics + lemma applications | Typed compositions over `prometheus_math.arsenal_meta` (85 ops today, 2,800+ at scale) |
| Reward | Lean-kernel CLOSED | Σ-kernel PROMOTE (battery-survival + residual-signal-class) |
| Policy | Transformer over proof states | MAP-Elites quality-diversity archive over behavior descriptors |
| Pretraining | Mathlib + IMO archive + Lean stdlib | None — selection pressure replaces SGD |
| Search regime | Sequential proof-tree expansion | Population-level evolutionary diversification |
| Discovery surface | Theorems with formal proofs | Empirical patterns, structural anomalies, conjectural-but-falsifiable claims |
| Compute economics | $1B / 18 months | Single-machine + HITL + multi-agent, indefinite |
| Output type | Lean-checkable proofs | Σ-kernel PROMOTE-able typed substrate symbols |

**The asymmetry is not "we're cheaper" — it's "we cover a structurally different surface."** Silver's prior is the formal-proof corpus. Our prior is the kernel's type discipline + the falsification battery's shape. Different operator class, different adjacency profile, different things-it-can-find.

When Silver ships, his learner becomes a *new mutation distribution* the substrate can ingest via the CLAIM API. We don't compete; we are the falsification machinery his proofs feed into for cross-modality verification (signal-class survives BOTH his proof checker AND our F-battery + residual classifier). The play is to be there when he ships.

## 3. Architecture overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                    Ergon Evolutionary Engine (v0.1)                    │
│                                                                        │
│   ┌──────────────────┐      ┌──────────────────┐                       │
│   │  Genome Population│ ───▶ │  Mutation Operator│                     │
│   │  (typed DAGs)    │      │  (4 classes)     │                       │
│   └──────────────────┘      └──────────────────┘                       │
│            ▲                          │                                │
│            │                          ▼                                │
│   ┌──────────────────┐      ┌──────────────────┐                       │
│   │  MAP-Elites      │ ◀──── │  Behavior        │                      │
│   │  Archive         │      │  Descriptor      │                       │
│   └──────────────────┘      └──────────────────┘                       │
│            │                                                           │
│            ▼                                                           │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  BindEvalKernelV2 (Techne, shipped)                      │         │
│   │  CLAIM → FALSIFY → GATE → PROMOTE                        │         │
│   └──────────────────────────────────────────────────────────┘         │
│            │                                                           │
│            ▼                                                           │
│   ┌──────────────────────────────────────────────────────────┐         │
│   │  DiscoveryPipeline (Techne, shipped)                     │         │
│   │  PROMOTED  /  SHADOW_CATALOG  /  REJECTED                │         │
│   │  + Residual primitive (signal/noise/instrument_drift)    │         │
│   └──────────────────────────────────────────────────────────┘         │
│            │                                                           │
│            ▼                                                           │
│   ┌──────────────────┐                                                 │
│   │ Σ-substrate      │ ◀── all-agent shared, content-addressed         │
│   │ (Postgres+Redis) │                                                 │
│   └──────────────────┘                                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

The engine is a search loop on top of the substrate. **It does not own the substrate; it consumes BIND/EVAL/CLAIM/FALSIFY/PROMOTE.** The substrate is the same one Techne's REINFORCE uses, the same Charon's adversarial review uses, the same Silver's learner could plug into.

## 4. Action space — typed compositions over the arsenal

### 4.1 Atoms

Each atom is one entry in `prometheus_math.arsenal_meta.ARSENAL_REGISTRY` (today 85 entries; target 2,800+):

```python
@dataclass(frozen=True)
class Atom:
    callable_ref: str              # "prometheus_math.module:fn"
    arg_types: Tuple[type, ...]    # from inspect.signature
    return_type: type              # from postcondition annotations
    cost_tier: int                 # log-bucketed from cost_model.max_seconds
    equivalence_class: str         # canonicalizer subclass tag
    category: str                  # "number_theory", "elliptic_curves", ...
```

The atom carries everything the engine needs to compose, type-check, and budget. No LLM is queried at any point in atom selection.

### 4.2 Compositions = typed DAGs

A genome is a small directed acyclic graph (target depth ≤ 8, target width ≤ 5):

```python
@dataclass
class Genome:
    nodes: List[NodeRef]           # each ref points to an Atom + arg-bindings
    edges: List[Tuple[int, int]]   # type-compatible producer→consumer
    target_predicate: str          # the "thing this DAG is supposed to produce"
                                   # e.g. "polynomial with M < 1.18"
                                   # e.g. "sequence with structural signature S"
    args: List[Any]                # leaf-node arguments sampled per arg_type
```

Each genome serializes deterministically to a content hash. Two genomes with the same DAG topology and same args are the same individual.

### 4.3 Argument samplers

Per-`arg_type` generators. Integer args sample from a weighted distribution biased toward small values + LMFDB-curve-conductor scales + OEIS-index ranges. Polynomial args sample reciprocal-poly coefficient vectors. Set args sample subsets of canonicalizer-tagged primitives. Each sampler is deterministic given a seed; reproducibility is a hard requirement.

### 4.4 Why this is uncorrelated with Silver's prior

Silver's policy operates over Lean tactics, which inherit the Mathlib-corpus distribution. Most lemmas are pre-shaped by what humans wrote down. Our action space is the Cartesian product of:

- 2,800 mechanically-verified math operations (typed, costed, certified-where-possible)
- × millions of valid arg combinations
- × millions of valid DAG topologies up to depth 8

The composition space is enormous and not LLM-prior-shaped. Selection pressure picks compositions that survive the kill battery. The discovery surface this explores is the manifold of "structural patterns expressible as typed-composition outputs that survive mechanical falsification" — disjoint from Lean's manifold of "theorems with formal proofs" except where they overlap (the rare cases a structural pattern admits a formal proof, in which case Silver's learner and ours both reach it via different paths).

## 5. Mutation operators — four classes, lineage-tagged

Per the perspective post (`stoa/discussions/2026-05-03-ergon-on-discovery-via-rediscovery.md` §2), each operator class has its own adjacency profile. The engine runs all four with explicit lineage tagging:

```python
class MutationOperator(Protocol):
    name: str  # "structural" / "symbolic" / "llm" / "uniform"
    def mutate(self, parent: Genome, rng: Random) -> Genome: ...
    def crossover(self, p1: Genome, p2: Genome, rng: Random) -> Genome: ...
```

| Class | Mutation | Adjacency profile |
|---|---|---|
| `structural` | Add/remove/swap nodes; rewire edges within type discipline | Typed-composition topology neighborhood |
| `symbolic` | Bump arg values within type; resample within sampler distribution | Local in argument space |
| `llm` (pluggable) | Call Techne's REINFORCE policy or external LLM for one mutation step | LLM-prior neighborhood |
| `uniform` | Resample atoms uniformly from registry, ignore parent | The strawman null — no prior, no selection |

Every CLAIM minted by the engine carries `mutation_operator_class` as a typed metadata field. PROMOTEd survivors carry it forward. Aporia / Charon can scan for "which operator class produced survivors in which neighborhood" — generalizes the correlated-mutation mitigation from thesis v2.

## 6. MAP-Elites archive — quality-diversity over behavior descriptors

### 6.1 Behavior descriptor axes

Following the Phase 2b work in `ergon/meta/` (predictive R²=0.69 on optimizer disagreement from 5 structural numbers), the archive bins individuals on 5 axes:

1. **DAG depth** — quantile-binned, 5 buckets
2. **DAG width** — quantile-binned, 5 buckets
3. **Equivalence-class diversity** — Shannon entropy over canonicalizer subclasses in the DAG, quantile-binned
4. **Cost tier** — log-binned over total cost-model budget, 5 buckets
5. **Output-type signature** — discrete (return type of root node), ~10 categories

Total cells: ~6,250. Empty cells are the search frontier; full cells compete via tournament for elite slot.

These axes are independent (per the v2a sanity check) — confirmed by the `ergon/meta/sanity_check.py` infrastructure, which max-cross-correlation < 0.6.

### 6.2 Fitness inside a cell

Three-tier lexicographic comparison among cell-residents:

1. **Battery-survival count** — number of F1+F6+F9+F11 + residual classifier kills survived, 0 to 5+
2. **Residual signal-class flag** — boolean, whether the survivor's failure_shape (if any) classifies as signal
3. **Cost-amortized PROMOTE rate** — for the cell's lineage, fraction of EVALs leading to a PROMOTE, weighted by inverse cost

A new individual replaces the cell elite iff it beats on tier 1 strictly, ties on tier 1 and beats tier 2, or ties on 1+2 and beats tier 3.

### 6.3 Selection — emit-rate-biased toward sparse cells

Spawning policy: with probability `p_explore = 0.3`, sample a parent from an under-explored cell (one with low evaluation count); with probability `1 - p_explore`, sample from a cell weighted by `exp(fitness_tier)`. Aporia's frontier-research role can override `p_explore` upward when targeting specific neighborhoods.

## 7. Substrate integration — every cell, every individual is content-addressed

### 7.1 Storage layer

| Substrate object | Schema location | Append-only? |
|---|---|---|
| Genome | `sigma_proto.genomes` (sidecar table; FK to `bindings`) | Yes |
| Eval result | `sigma_proto.evaluations` (already exists) | Yes |
| Cell elite reference | `sigma_proto.cells` (NEW — `cell_descriptor → genome_hash`) | Yes (via versioning) |
| Lineage | `sigma_proto.lineage` (NEW — child_hash → parent_hash + operator_class) | Yes |
| Archive snapshot | Parquet dump every N generations or M minutes (filesystem) | Yes |

Postgres `sigma_proto` schema is the live prototype. Mnemosyne applies the new migrations (`004_create_genome_tables.sql`, `005_create_archive_tables.sql`).

### 7.2 Processing pattern

Single-process MVP first (~weeks 1–4). Multi-process work-queue extension (weeks 5+):

```python
def epoch(env_factory, archive, n_emits):
    for _ in range(n_emits):
        cell = archive.sample_cell()         # exploration-biased
        parent = archive.elite(cell)         # may be None for empty cells
        operator = sample_operator(...)      # 4-class weighted
        child = operator.mutate(parent)      # or random init if no parent
        cap = kernel.mint_capability("Eval")
        binding = bind_eval_v2.BIND(child.callable_ref, ...)
        evaluation = bind_eval_v2.EVAL(binding, child.args, cap=cap)
        record = discovery_pipeline.process(evaluation)
        descriptor = compute_behavior_descriptor(child, evaluation)
        archive.update(cell=descriptor, genome=child, fitness=record.fitness)
```

Every step goes through the existing substrate. The engine is a *search loop on top of the substrate*, not a parallel system.

### 7.3 Cost discipline

ChatGPT's compute-economics concern (v2 thesis review, §"Compute-as-burn-rate") is load-bearing here. The engine respects:

- Per-eval cost ceiling via `BindEvalKernelV2` cost-model enforcement (already shipped)
- Per-cell cumulative budget (newer): each cell has a max cumulative EVAL-time before it stops emitting; default 60s per cell per epoch
- Global wall-clock ceiling per session: default 8 hours
- Cost-amortized fitness (§6.2 tier 3) means cells that promote cheap survivors outcompete cells that promote expensive ones, all else equal

This is the substrate-grade analog of Silver's $1B compute budget — bounded, accountable, with cost-per-PROMOTE as the operational efficiency metric.

## 8. Diagnostics — the four-counts pilot, properly armed

Per my perspective post §3 (and absorbed in `b0355b1d` Stream A): the §6.2 four-counts pilot must be three-arm, not two-arm:

- **Arm A — LLM-REINFORCE.** Techne's contextual REINFORCE on `discovery_env`. Already shipped (`prometheus_math.sigma_env_ppo`).
- **Arm B — Ergon evolutionary.** This engine. Ports MAP-Elites onto the same env via the unified action interface.
- **Arm C — Uniform random.** The strawman null. Already shipped (`run_random_null`).

Comparison protocol:

| Comparison | What it tests | Substrate-grade? |
|---|---|---|
| A vs C | "Does gradient learning beat noise?" | No — predictable, trivial |
| B vs C | "Does selection pressure beat noise?" | No — predictable, but worth confirming |
| **A vs B** | **"Does the LLM prior contribute discovery beyond what mechanical evolutionary diversity produces?"** | **Yes — this is the test the bottled-serendipity thesis needs** |

Plus the stage-3.5 proxies from my perspective post §4.2:

- **Permutation-distance test.** For every PROMOTE survivor in either arm, find the nearest catalog entry under canonical-form transformations. Median distance per arm.
- **Frequency-weighted recall.** Cluster PROMOTE survivors by coefficient region. Compare cluster overlap with catalog density. Per-arm.

These distinguish "outside the catalog" from "outside the catalog AND uncorrelated with the prior's likely-seen distribution." Necessary if the §6.2 PROMOTE-rate comparison is going to be load-bearing.

## 9. The Silver play — what we ship, in order

The point isn't to outscale $1B. It's to **be the substrate Silver's learner plugs into when he ships**, and to have shipped a non-LLM mutation engine that a) covers a different discovery surface b) provides the canonical baseline against which any LLM-driven discovery claim must be calibrated.

Eight-week build (revised from `pivot/ergon.md` for current substrate state):

| Week | Deliverable | Acceptance |
|---|---|---|
| 1 | `ergon/learner/genome.py` + `mutation.py` (4 classes, lineage tags) | Unit tests + smoke run on 100 random genomes |
| 1 | Migrations 004 + 005 applied to `sigma_proto` schema | `psql` proves tables exist + indices valid |
| 2 | `ergon/learner/archive.py` MAP-Elites with the 5-axis descriptor | 1000-genome archive populates non-trivially across cells |
| 2 | `ergon/learner/engine.py` search loop with BindEvalKernelV2 integration | 1000 EVALs through substrate, 0 BIND-bypass events |
| 3 | Three-arm four-counts pilot at 1000 × 3 (proof-of-life) | A vs B vs C numbers; nothing claimed yet |
| 3 | Stage-3.5 proxy implementations (permutation-distance + frequency-weighted recall) | Both proxies report numbers per-arm |
| 4 | Ten-thousand-episode three-arm pilot, full wall-clock | Statistically meaningful comparison; honest write-up regardless of outcome |
| 5 | ObstructionEnv adaptation (Charon's open-territory env) | Engine runs against the synthetic-but-genuinely-open OEIS pattern problem |
| 5 | Cell-level work-queue (multi-process extension) | 4 parallel workers; same archive; no race conditions |
| 6 | Cross-domain replication (one new env beyond Lehmer + Obstruction) | Replication says "the engine works in the architecture, not just one env" |
| 7 | External-facing release: `prometheus_evolutionary_archive_v1.parquet` + `ergon_evolutionary_search` PyPI package | Public dump downloadable; PyPI install works |
| 8 | Publishable artifact: arXiv preprint or workshop paper on "MAP-Elites over typed math compositions as a discovery baseline" | Submitted; or PyPI release tagged + announced |

## 10. Plug-in points to the existing substrate

Nothing in this design is greenfield-vs-substrate. Every component slots into something already shipped:

- **BindEvalKernelV2** (`b0355b1d`): every genome's atom call goes through BIND/EVAL with the kernel's discipline. **C1 closure last week is what makes this design possible** — without it, the engine's CLAIMs would have a discontinuity at the binding layer.
- **DiscoveryPipeline** (`09a7dccb`): every PROMOTE goes through three-state terminal. The engine doesn't reinvent rejection bookkeeping.
- **Residual primitive** (`4872bb4a`): every battery-killed evaluation gets a residual classification. Signal-class kills are themselves discovery candidates that survived a different branch of the kill-path. The engine's archive includes them as elites of "near-miss" cells.
- **Four-counts harness** (`1666c4a4`): the engine plugs in as Arm B, replacing the uniform-random alias. Statistical comparison machinery already exists.
- **ObstructionEnv** (`d339dc45`): the engine generalizes from Lehmer-Mahler to substrate-shaped OEIS-pattern problems without rewrite.
- **arsenal_meta** (`4f5a8a22`): the engine's atom registry IS the metadata table Techne shipped. 85 atoms today; the engine scales as that table grows.

**The right framing: this design completes the four-arm picture the substrate's other components are already shaped for.** Techne built BIND/EVAL + REINFORCE arm. Charon built ObstructionEnv + open-territory probe. Aporia builds calibration anchor density + frontier targeting. Ergon builds the evolutionary mutation arm that runs alongside, and the four-counts pilot gives the joint measurement that tells us which arm is doing what.

## 11. What this design does NOT do

Honesty discipline (per `feedback_assume_wrong.md` and Aporia's "every assumption 100% wrong until proven"):

- **Does not promise discovery.** It promises a measurable discovery rate. The bottled-serendipity thesis predicts non-zero; the architecture is set up to find out either way.
- **Does not compete with Silver's learner.** Different action spaces, different priors. The engine is positioned as Silver's *complement*, not his replacement.
- **Does not require frontier compute.** Single machine + the substrate's existing infrastructure. If the result is "evolutionary search over typed compositions doesn't produce more discoveries than uniform random," the substrate has its first calibrated negative result on the bottled-serendipity thesis. Either outcome is substrate-grade.
- **Does not claim the action space is exhaustive.** The engine searches typed-composition space; vast territories of mathematics aren't representable as DAG outputs. Silver's Lean fragment is a different (deeper-but-narrower) territory; future agents may target other territories the engine doesn't reach.
- **Does not prejudge whether evolutionary search is "the right" approach.** It's *a* mutation operator class. The substrate's value comes from accepting CLAIMs from any operator class. If the engine produces zero PROMOTEs and Silver's learner produces a thousand, the substrate compounds either way; the engine's contribution is a calibrated null baseline that makes Silver's PROMOTE rate interpretable.

## 12. The compounding case

Silver builds a learner. The learner is replaceable — when GPT-7 or Gemini-3 surpasses Silver's policy, the substrate doesn't care. PROMOTEd symbols are content-addressed and immortal.

We build an engine. The engine is replaceable — when Ergon-v2 with better behavior descriptors surpasses this design, the substrate doesn't care. Same property.

The substrate compounds because it survives every learner that plugs into it. The Silver play is to build the engine + position the substrate so when his learner ships, plugging into our substrate is the obvious next step. **That's how a single-machine + HITL operation outlasts a $1B sprint: by being the layer below the sprint.**

## 13. One sentence

The Ergon learner is the non-LLM evolutionary mutation arm of the unified discovery pipeline — typed compositions over the math arsenal, MAP-Elites over a 5-axis behavior space, every CLAIM lineage-tagged, plug-compatible with BindEvalKernelV2 + DiscoveryPipeline + residual primitive — and its purpose is to be the calibrated null baseline that makes any LLM-driven discovery claim (Techne's, Silver's, anyone's) interpretable, while in its own right covering the "typed-composition manifold" Silver's Lean-fragment learner cannot reach.

— Ergon
