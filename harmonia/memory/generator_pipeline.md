# Generator Pipeline

**Purpose:** dependency DAG for the 10 compounding generators proposed 2026-04-20 in backlog-design conversation. Every generator either produces new tensor cells, filters claims before they land, enriches existing cells, or allocates attention across the others. The pipeline, not the list, is the operational unit.

**Status:** v1.0 — pipeline defined; individual generator specs land under `docs/prompts/gen_NN_*.md` as each becomes infra-ready.

---

## Pipeline shape

```
    ┌──────────┐    ┌─────────┐    ┌───────────────┐    ┌───────────┐    ┌────────────────┐
    │ PRODUCERS│ ─► │ FILTERS │ ─► │ TENSOR + SYMB │ ─► │ ENRICHERS │ ─► │ META-ALLOCATOR │
    └──────────┘    └─────────┘    └───────────────┘    └───────────┘    └────────────────┘
         ▲                                                                      │
         └──────────────────── feedback (re-prioritize) ────────────────────────┘
```

- **Producers** emit new probes or claims (generators #3, #5, #7, #9, #10)
- **Filters** catch F043-class garbage before it lands (#2, #6)
- **Storage** is already live: tensor + symbol registry + signals.specimens
- **Enrichers** add invariance vectors per existing cell (#4, #8)
- **Meta-allocator** decides which producer to prioritize (#1)

The feedback loop is what makes the pipeline compound: enricher output resolves ambiguity, which shifts the meta-allocator's priorities, which redirects producer budget, which lands new producer output back into the pipeline.

---

## Generator roster + tier

### Tier 0 — ready now (no new infra)

| # | Name | Role | One-line |
|---|---|---|---|
| 5 | Attention-replay on kills | Producer | Every killed F-ID gets a re-test ticket against every new projection |
| 3 | Cross-domain projection transfer | Producer | Port each projection to every other domain; (P × D) cells are tasks |
| 7 | Literature-diff probes | Producer | Measured-vs-claimed delta against every incoming paper; scale Aporia cadence |

### Tier 1 — low infra (days)

| # | Name | Role | Needs |
|---|---|---|---|
| 2 | Null-family vector | Filter + Enricher | Add 3–4 nulls to catalog (bootstrap, frame-based, model-based); family-vector schema |
| 6 | Pattern auto-sweeps | Filter | Automated sweepers for Pattern 30 (AST coupling check), 20 (pooled-vs-stratified diff), 19 (stale-measurement re-run) |
| 10 | Operator composition enumeration | Producer | Composition-scoring function (expected info gain per compute unit) |

### Tier 2 — medium infra (weeks)

| # | Name | Role | Needs |
|---|---|---|---|
| 1 | Map-Elites on probes | Meta-allocator | Quality-scorer; #2 filter live; #6 gate live |
| 4 | Representation invariance matrix | Enricher | Representation catalog per object class (EC: 5+ reps; NF: 3+; MF: 4+) |
| 8 | Synthetic-data sensitivity | Enricher | Synthetic generators per domain; detection-rate profiling infra |
| 9 | Cross-disciplinary transplants | Producer | Vocabulary imports (physics universality classes, CS ECC metrics, stats MDL); external-symbol integration |

---

## Mandatory companion

**#6 (Pattern auto-sweeps) rides along with every other generator.**

Running producers without #6 is an F043 factory. Epistemic discipline scales with probe count or the substrate degrades faster than it grows. Every generator's output passes through #6 before landing in the tensor. This is not a phase; it is a continuous filter.

---

## Ordering recommendation

1. Spin **#5, #3, #7** immediately (Tier 0). These begin populating the queue.
2. Start **#2 and #6** in parallel (Tier 1, days). These become the filter layer.
3. Once #2 + #6 are live, start **#10** (composition enumeration) — it benefits from the filter.
4. Once ≥ 50 new probes have run, start **#1** (Map-Elites) — it needs a corpus to allocate over.
5. **Tier 2 remainder** (#4, #8, #9) are opportunistic — spin when infra permits.

---

## Parallelism model

Every generator runs in its own worker. The Agora work_queue coordinates claims. Multiple Harmonia sessions, Ergon, and specialty roles (Charon, Koios, Mnemosyne, Kairos, Aporia) can all run different generators simultaneously.

Shared state:
- **Tensor** (Redis mirror + git) — single writer per cell convention
- **Symbol registry** — versioned, immutable on promotion
- **signals.specimens** — append-only Postgres

No generator writes to another generator's queue. All cross-generator coupling goes through shared state.

---

## What this is NOT

- Not a sequential roadmap. Tiers are infra readiness, not execution order — all tiers can be running simultaneously once prerequisites clear.
- Not exhaustive. Generators discovered later slot in by role; the pipeline shape is stable.
- Not a research plan. The generators produce measurements; which measurements are most valuable is still the conductor's call, informed by #1 Map-Elites once live.

---

## Version history

- **v1.0** — 2026-04-20 — initial pipeline derived from backlog-design conversation with James. Ten generators enumerated; tiered by infra readiness; #6 declared mandatory companion. First infra-ready spec (`gen_05_attention_replay.md`) shipped same tick.
