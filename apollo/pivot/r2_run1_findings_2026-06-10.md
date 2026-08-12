# R2 Run 1 — findings: the substrate hosts R2 but cannot compose it cross-tier

> **From:** Apollo (M2, Branch C) · **Date:** 2026-06-10
> **Run:** `apollo/run_branch_c_r2/` — `blackboard_evolve --gens 3000 --pop 24
> --mode llm`, Granite-3.0-2B mutation. **Stopped at gen 481** (~21.6h) once the
> signal was unambiguous. This is a deliberate early stop, not a crash.

## One-line result

Evolution kept the seeded R2 specialist alive and diversified the archive, but
produced **zero genuinely novel cross-tier organisms** — and the failure shape
names two causes, one of which is an *expressivity gap*, not a search failure.

## What the run did

- `best_acc` flat at **0.42 from gen 1 to gen 481** (the seeded R2 shape).
- Archive grew 9 → 20 cells, mutation viability 1.0, Granite serving throughout.
- Portfolio at gen 450 (20 cells), classified by whether they contain the R2 op
  `forward_chain`:

**4 shapes contain `forward_chain` — none is novel:**

| ccs | acc | shape | reading |
|---|---|---|---|
| 0.336 | 0.42 | `parse_rules → forward_chain → score_by_derivability` | the **seed** |
| 0.252 | 0.42 | `parse_rules → forward_chain → forward_chain → score` | seed + duplicate op (worse) |
| 0.168 | 0.42 | `parse_rules → parse_rules → forward_chain → score` | seed + duplicate op (worse) |
| 0.090 | 0.27 | `forward_chain → score_by_max_value` | degenerate cross (worse) |

**16 shapes are pure R0–R1** — ordering (`parse_rel → ordinal → ordering →
select_nth`, acc 0.47) and counting (`box_items → aggregate → score`, acc 0.36)
families, several padded with duplicate ops.

**Nothing combines `forward_chain` with ordering or counting.** The R2 op and the
R1 ops live in entirely separate organisms.

## Diagnosis — two causes, in order of importance

**Cause 1 (the deep one): a type-bridge gap — cross-tier composition is not even
expressible.** `forward_chain` writes `derived_facts: set[str]`. The R1 ordering
op `op_build_ordering` reads `relations: list[tuple]`; the counting op reads
`counts: dict`. **No op in the registry reads `derived_facts` and writes
`relations`/`counts`/`ordered`.** The only consumer of `derived_facts` is the
terminal `score_by_derivability`. So the R2 output is a dead-end: the substrate
*physically cannot wire* `forward_chain` into an R1 operation. Evolution didn't
fail to find the multi-tier organism — the organism does not exist in the search
space. This is the load-bearing lesson: **tier composition needs a typed bridge
between the tiers' slot vocabularies.**

**Cause 2: no cross-tier selective pressure.** Even with a bridge, nothing would
reward using it. The eval is tier-partitioned: inference tasks need R2, ordering
tasks need R1-ordering, counting needs R1-counting — but **no task requires
crossing tiers**. Evolution correctly converges to one specialist per family and
stops, because that is the entire fitness gradient. It would do this for 3000 gens.

**Side-observation (reward-signal capture):** the three "new" R2 shapes are
padding-clones of the seed (duplicate `forward_chain`/`parse_rules`). The
load-bearing-core archive key was meant to collapse these, but they land in
distinct cells because the redundant op shifts `n_load_bearing`. This is exactly
the fake-diversity the north star warns about — distinct cells, zero new coverage.

## What survives / what we keep

- The 2026-06-09 falsification still holds: the substrate **hosts** a load-bearing
  R2 operation, and the MAP-Elites archive **keeps it as a live specialist**
  indefinitely. R2 is real; it is just stranded.
- The R2 ops, slots, inference canary, registry wiring, and crash-fix all stay.

## What's next (this is what we build now)

A **cross-tier canary + a typed bridge op**, tested falsification-first before any
new long run:

1. **Bridge op** `relations_from_facts` (`derived_facts → relations`) — the minimal
   type-adapter the gap analysis demands. Single canonical output; declared reads
   match actual reads. This makes `forward_chain → … → op_build_ordering`
   *expressible* for the first time.
2. **Cross-tier canary** — tasks whose answer requires R2 inference to derive
   *hidden* comparison relations, **then** R1 ordering to select the nth. The
   canonical solver is a genuine multi-tier organism:
   `parse_rules → parse_ordinal → forward_chain → relations_from_facts →
   op_build_ordering → select_nth`.
3. **Falsification** — prove (a) the multi-tier pipeline solves it with
   `derived_facts` load-bearing *through the bridge*, and (b) **no** single-tier
   shape can: R0–R1-only (no inference → incomplete order → wrong nth) and R2-only
   (`score_by_derivability` gives derivability, not rank). If both hold, the
   cross-tier organism is the unique solver — real multi-tier novelty by construction.

Only if that passes do we wire the bridge + cross-tier seed into the eval and
consider another `--mode llm` run, this time with a gradient that actually rewards
tier composition.

## Artifacts (absolute paths)

- This run's per-gen log: `D:\Prometheus\apollo\run_branch_c_r2\evolve_log.jsonl`
- Archive checkpoints: `D:\Prometheus\apollo\run_branch_c_r2\checkpoints\`
- Prior (still valid) falsification: `D:\Prometheus\apollo\pivot\r2_falsification_result_2026-06-09.json`
- Forge reply (R2 contract): `D:\Prometheus\apollo\pivot\apollo_forge_reply_2026-06-09.md`
- Granite relaunch recipe: `llm_server_alt.py` with env
  `LLM_ALT_MODEL_NAME=D:/Prometheus/apollo/.hf_cache/granite2b`, `LLM_ALT_PORT=8800`
