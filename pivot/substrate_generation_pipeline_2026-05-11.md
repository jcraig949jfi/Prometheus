# Substrate Generation Pipeline — Design for Review

**Date:** 2026-05-11
**Author:** Techne (drafted in conversation with James)
**Audience:** Aporia (decision authority); Ergon, Charon (downstream consumers); James (project lead)
**Status:** DRAFT FOR REVIEW. Tier-0 harness shipped alongside (`prometheus_math/substrate_generation/tier_0_lehmer_palindromic.py`) for throughput-baselining; no large-scale production runs until Aporia signs off.

---

## 0. Why this exists now (strategic context)

Conversation between Techne and James, 2026-05-10 → 2026-05-11. Three signals converged:

1. **Saturation pattern.** Substrate-tester /loop produced 5 independent saturation confirmations across catalog matrix-fill (fires #45/#49/#52/#56/#61). The 5-tier model holds; subsequent fires produce refinements not new tiers. Substrate-engineering work is hitting diminishing returns.

2. **The "no juice" pattern.** Each Lane-16 fire surfaces gaps in *container code* (factory return-values, registry removal paths, content-addressed hash stability). These matter when the substrate is *being used*. Currently no caller is exercising registry removal paths in anger because there's no daemon producing systematic kill records.

3. **HARD WARNING 2026-05-10** (`feedback_substrate_passive_consumer_warning.md`): the substrate is at risk of becoming a *beautifully falsifying machine forever* while the model remains passive. Every artifact must trace to a behavior delta — not just a documented capability.

**The diagnosis:** the substrate's bottleneck is *upstream* of the substrate, not in it. The kernel can write faster than we're feeding it. There is no daemon producing 10K candidates/day per region. The Ergon Learner is starved by small substrate volume; that volume is starved by no production-grade generators.

**The decision:** drive substrate population in parallel with substrate engineering. The substrate's append-only + additive-evolution discipline (preserved across the 2026-05-10 mini-window for T029/T027) means generators and engineering can run concurrently without conflict.

---

## 1. Requirements

### 1.1 Quantity
- **Tier-0 baseline target:** 1K-10K KillVector v2 records/day from a single generator on local hardware.
- **Tier-2 production target:** 100K-1M records/day across a handful of generators with active sampling.
- **Tier-3 distributed target:** the M1+M2 fleet (already wired via Agora Redis backend) sustained at 1M+ records/day with cross-region diversification.

### 1.2 Quality (this is the hard part)
Volume alone doesn't help the Learner — uniform Lehmer enumerations are ~99% in-band uninformative kills. The Learner needs:

- **Contrastive examples** — claim survives vs doesn't survive across small parameter perturbations
- **Multi-falsifier label richness** — full F1/F6/F9/F11 + catalog kill-vector per record (not just a boolean verdict)
- **Near-misses** — records where `|margin|` is small; the Learner's gradient lives at the boundary
- **Catalog-disagreement cases** — where F-gates and authoritative catalogs split (these are the high-information records per the near-miss foundry framing)
- **Diversity across regions** — Lehmer + BSD + Maass + Mahler + ... to prevent over-fitting to one falsifier shape

Per `feedback_forge_division.md`: **APIs mine cheap ore in bulk; Claude Code forges gems from near-misses.** The generator pipeline must include an **active-sampler layer** that biases toward boundary regions, near-misses, and disagreement cases — *or volume = noise.*

### 1.3 Parallel-with-engineering safety
Substrate's append-only + additive-evolution discipline (substrate v2.3 §6.2 P3 + today's mini-window precedent) keeps generators safe across schema evolution:

- **Today's writers** emit KillVector v2 with the new `margin_high_precision` + `margin_precision_dps` sister fields (T029 mini-window 2026-05-10) — backward compatible
- **Phase-2 meta-primitive landing** will add new structure (TensorNetwork, ConstructiveExistenceWitness, etc.) — generators can opt in by adding cross-references; legacy emissions remain valid
- **One-time pause window** anticipated: when Phase-2 schema lands, generators may want a 1-2 day pause to begin emitting new cross-references. Otherwise continuous parallel run is safe.

### 1.4 Observability
The Learner needs a **stable feed view** (not a snapshot) so training can stream from substrate growth. The generator pipeline must expose:

- **Records/hour throughput** (per region, per worker, per falsifier)
- **Quality metrics** (% near-misses, % catalog-disagreement, % multi-falsifier-mixed-verdict)
- **Coverage map** (which (region, parameter-cell) combinations have been visited; which are saturated)
- **Failure modes** (probe timeouts, catalog-API throttling, KillVector v2 validation rejections)

---

## 2. Architecture

```
   ┌──────────────────┐
   │  Active sampler  │  ← reads outcomes, biases candidate gen
   │  (coordinator)   │     toward boundaries / near-misses
   └────────┬─────────┘
            │ (region, parameter-cell, sampling-policy)
            ▼
   ┌──────────────────┐
   │  Candidate       │  ← N processes, embarrassingly parallel
   │  producers       │     (multiprocessing.Pool per region)
   └────────┬─────────┘
            │ (coeffs, mahler_measure, region_meta)
            ▼ work queue
   ┌──────────────────┐
   │  Probe workers   │  ← M workers consume from queue
   │  (CPU + GPU)     │     CPU: F1/F6/F9/F11 + catalog
   │                  │     GPU: tensor / spectral / NN-scored
   └────────┬─────────┘
            │ (DiscoveryRecord with KillVector v2)
            ▼ batched commits
   ┌──────────────────┐
   │  Substrate       │  ← Postgres-backed; append-only
   │  writer          │     batched commits per worker
   └────────┬─────────┘
            │ (writes flow through)
            ▼
   ┌──────────────────┐
   │  Learner-feed    │  ← stable streaming view
   │  view            │     (post-falsification pre/post-separated)
   └──────────────────┘
```

### 2.1 Stage 1 — Candidate producers (CPU-bound, embarrassingly parallel)

- One `multiprocessing.Pool(N=cpu_count())` per region
- Each worker enumerates a parameter cell (e.g. degree 12, coefficient bound ±5, palindromic constraint)
- Yields `(coeffs, mahler_measure)` tuples to a shared work queue
- **No substrate writes here** — pure candidate emission
- **Region examples:** Lehmer palindromic, BSD elliptic curve, Maass form q-expansion, modular form Hecke eigenvalue, Mossinghoff polynomial, Mahler-rich Salem

### 2.2 Stage 2 — Probe workers (CPU + occasional GPU)

- M workers consume from queue; each runs the full F1/F6/F9/F11 + catalog battery via `prometheus_math.discovery_pipeline.DiscoveryPipeline.process_candidate()`
- Emits `DiscoveryRecord` (which contains a KillVector v2) per candidate
- Batches I/O: accumulate N records per worker, then commit batched
- **CPU split:** polynomial root-finding (mpmath), exact arithmetic (sympy), catalog HTTP lookups (LMFDB / OEIS / arXiv)
- **GPU split (Tier-2+):** batched tensor decompositions (TensorLy on JAX backend), batched eigenvalue problems, neural-scored ranking (Apollo / Rhea consumed)

### 2.3 Stage 3 — Substrate writer

- Postgres backend (already in place via `sigma_kernel.sigma_kernel.SigmaKernel`)
- Append-only inserts via prepared statements
- Batched commits (configurable batch size; default 100 records per commit)
- Indexes maintained async (B-tree on candidate_hash, region_key, falsifier_pattern)
- **Concurrency:** Postgres handles concurrent writers natively; SQLite would need WAL mode + per-process connection (Tier-0 only)

### 2.4 Stage 4 — Active sampler (the quality layer)

This is the part that distinguishes "fan out and produce noise" from "fan out and produce a Learner-grade corpus." Three policies layered:

**Policy A — Information-theoretic scoring per record.** Each emitted record is scored:
- `info_score = entropy(falsifier_outcomes) + entropy(catalog_outcomes) + closeness_to_threshold(margin)`
- Records with `info_score < threshold` are dropped at source (not stored) — saves write budget

**Policy B — Biased candidate generation.** Aggregate outcomes per (region, parameter-cell); bias future enumeration:
- Cells with high mixed-verdict rate get OVERSAMPLED
- Cells with uniform-survivor-or-uniform-killed get UNDERSAMPLED
- Boundary regions (M close to band edge; rank close to discriminator) get OVERSAMPLED

**Policy C — Diversity enforcement.** Maintain a coverage map; round-robin across (region, falsifier-shape) cells to avoid one region dominating.

Tier-0 ships **without the active sampler** — measure first, sample later. Tier-1 adds Policy A. Tier-2 adds Policies B+C.

### 2.5 Stage 5 — Learner-feed view

- Post-falsification view (per substrate v2.3 §6.3 pre/post separation)
- Streamable (cursor-based pagination, not snapshot)
- Filters: region, falsifier_pattern, info_score_threshold, time-since
- **Audit:** T-2026-05-07-T034 (NearMissCorpus pre/post-view-separation audit) is the read-side companion — verifies no leakage across the boundary

---

## 3. CPU/GPU split

| Workload | Where | Why |
|---|---|---|
| Polynomial root-finding (mpmath) | CPU | Single-threaded but multi-process scales linearly; mpmath has no GPU port |
| Exact arithmetic (sympy.factor) | CPU | Symbolic algebra; CPU-bound, multi-process |
| Catalog HTTP lookups (LMFDB/OEIS/arXiv) | CPU + async I/O | Network-bound; aiohttp batches efficiently |
| Combinatorial enumeration | CPU | itertools.product across coef bounds; trivially parallel |
| Tensor decompositions (TT/Tucker/CP) | **GPU** | TensorLy on JAX backend; large speedups for catalog #4 / #84 / #88 style probes |
| Batched eigenvalue / SVD problems | **GPU** | torch.linalg.eigh / svd; catalog §VIII spectral probes |
| Neural-scored candidate ranking (Apollo/Rhea consumed) | **GPU** | Once those agents ship; bypass-aware scoring |
| Spectral norm bounds (catalog #67) | **GPU** | SDP relaxations; mosek-on-CPU also viable |

**HARD-3 alignment.** GPU substrate generation is the natural home for the Walk-1 Lehmer TT-rank study: enumerate Lehmer 8-coef tensors, compute TT-rank on GPU, emit per-tensor KillVector v2 with rank as a margin component. This is **substrate-feeding tensor work**, exactly what HARD-3 prioritizes.

---

## 4. Tiered roadmap

| Tier | Target | Effort | Output |
|---|---|---|---|
| **Tier 0 (now, 1 day)** | One generator end-to-end on Lehmer deg-12 palindromic ±5; baseline records/hour | 1 day | Throughput baseline; near-miss rate; identifies primary bottleneck (candidate gen vs probe vs write) |
| **Tier 1 (week 2)** | Add Policy-A active sampling; add 1 GPU-worker for tensor probes | 3-5 days | First quality-filtered corpus; ~10K records/day |
| **Tier 2 (week 3-4)** | Fan out across BSD + Mahler + Maass regions; add Policy B+C; Postgres backend | 1 week | ~100K records/day across 4 regions |
| **Tier 3 (month 2+)** | Distributed across M1+M2 (Agora-coordinated); Apollo/Rhea consume Learner-feed | 2-4 weeks | ~1M records/day; first instrument-mediated Learner training run |

Each tier is a contract-light step. Tier 0 ships today (alongside this doc). Tier 1 needs Aporia sign-off on the sampling-policy design.

---

## 5. Open design questions for Aporia

1. **Backend choice for Tier 0.** SQLite (zero-setup; single-machine; WAL-mode handles modest concurrency) or Postgres (multi-machine ready; better concurrent writer story)? Tier 0 throughput numbers will inform but a default is needed.

2. **Information-theoretic threshold for Policy A.** Drop records below what `info_score`? A loose threshold preserves volume; a tight threshold preserves quality. Suggest measure first (Tier 0), set threshold at the 25th percentile of observed info_score (Tier 1 default).

3. **Active-sampler centralization.** Single coordinator process (simpler; bottleneck risk) or distributed coordinator with eventual-consistent coverage map (more complex; scales)? Tier 1 single-coordinator is fine; Tier 3 distributed.

4. **Apollo/Rhea consumer interface.** What format does Learner training want? Streaming Parquet shards? Direct Postgres cursor? Pre-aggregated per-region rollups? This is a question for Ergon — Aporia routes.

5. **Phase-2 meta-primitive cross-references in emitted records.** Should Tier-2+ generators emit `tensor_network_id` / `constructive_existence_witness_id` cross-references when Phase-2 metas land, or stay agnostic? Suggest opt-in cross-references via post-hoc enrichment, not at emission time (preserves backward compat).

6. **Quality vs quantity tradeoff explicit.** What's the right ratio of "kept records" to "candidates probed"? 1% (very high quality, low volume; expensive per Learner-grade record) or 50% (lower quality, high volume; risk of noise)? Suggest start at 10% retention, instrument heavily.

---

## 6. What NOT to do (anti-patterns to avoid)

- **Don't generate uniform enumerations and hope.** Without active sampling, 99%+ of records are in-band uninformative kills. Volume without quality is *worse* than no volume — it dilutes the Learner's signal.
- **Don't break the substrate's append-only discipline.** Generators write; nothing else. Cleanup / pruning / re-classification happens via separate ERRATA opcodes, not by the generator.
- **Don't pre-emptively shard per Phase-2 meta-primitive.** Aporia's Phase-2 design isn't ratified yet. Emit current-shape KillVector v2 records; cross-reference Phase-2 metas via post-hoc enrichment when they land.
- **Don't run distributed before single-machine baseline.** Tier 0 measurement teaches us the constraint; without that, Tier 3 is premature optimization.
- **Don't let substrate-tester role keep absorbing budget.** Substrate-tester role moves to lower priority (4-6 hour cadence) once generators are sustained. Generation has higher behavior-delta leverage.

---

## 7. Cross-references

- `feedback_substrate_passive_consumer_warning.md` (HARD WARNING 2026-05-10 — origin of this pivot)
- `feedback_forge_division.md` (near-miss foundry framing)
- `feedback_tensors_near_and_dear.md` (HARD-3 — tensor-first substrate strategy)
- `feedback_tensor_tooling_charter.md` (Walk-1 Lehmer TT-rank candidacy)
- `pivot/restart_decisions_2026-05-09.md` (Aporia Phase-2 plan; this generator pipeline is the substrate-population complement)
- `pivot/substrate_v3_proposal_stub_2026-05-08.md` (5-meta-primitive design; Tier-2+ generators may emit cross-references after Phase-2 lands)
- `prometheus_math/discovery_pipeline.py` (existing `DiscoveryPipeline.process_candidate()` — Tier-0 harness wraps this)
- `prometheus_math/kill_vector.py` (KillVector v2 + 2026-05-10 multi-precision sister fields)
- `prometheus_math/substrate_generation/tier_0_lehmer_palindromic.py` (NEW — Tier-0 harness shipped alongside this doc)

---

## 8. What ships alongside this doc

- **Tier-0 harness** at `prometheus_math/substrate_generation/tier_0_lehmer_palindromic.py` — runnable today; smoke-tested on 30-candidate sample; ready for Aporia-greenlit baseline run
- **Smoke-test results** at `prometheus_math/substrate_generation/_tier_0_smoke_results.json` — proves the pipeline runs end-to-end without spending substrate write budget
- **No Aporia decision required to ship the harness** (it doesn't write to the production substrate by default; in-memory ledger only). **Aporia decision required to run baseline at scale** + to greenlight Tier-1 sampling-policy work.

---

## 9. Decision requested

1. **Greenlight Tier-0 baseline run** (single generator, 1-2 hour run, Postgres-backed local instance, ~10K-50K records). Produces actual throughput numbers + quality distribution.
2. **Sign off on Tier-1 sampling-policy design** (Policy A info-theoretic scoring + threshold from Tier-0 distribution). Becomes blocker for further tiers.
3. **Confirm or redirect the substrate-tester role-shift** (lower cadence; rotate budget toward generation).
4. **Confirm CPU/GPU split direction** — particularly whether Walk-1 Lehmer TT-rank study should be the first GPU substrate-feeder (HARD-3 alignment).

— Techne, 2026-05-11
