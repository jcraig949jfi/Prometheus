# Lineage record — Apollo type-bridge metabolic cycle

> **T0 → diagnosis → intervention → T1 → reproduction.** The record is the deliverable;
> the accuracy number is not. An improvement that cannot be replayed is not inheritance.
>
> **Ran by:** Apollo (M2) · **Date:** 2026-08-19 · **Prereg:** `PREREGISTRATION.md`,
> written and committed before any arm executed · **Raw:** `RESULT.json`, `cells/*.json`
> **Mode:** deterministic only, no API, no new architecture.

---

## The five stages

### T0 — the recorded failure (2026-06-10)

`apollo/run_branch_c_r2/`, 481 generations, `--mode llm` with Granite. `best_acc` **flat at
0.42 from generation 1 to generation 481**. Archive grew 9 → 20 cells; **zero** cross-tier
organisms. The four shapes containing `forward_chain` were the seed and three
padding-clones of it. `forward_chain` and the R1 ordering ops lived in entirely separate
organisms and never met.

### Diagnosis (2026-06-10) — a type-bridge gap

`forward_chain` writes `derived_facts: set[str]`. `op_build_ordering` reads
`relations: list[tuple]`. **No operator read `derived_facts` and wrote `relations`.** The
only consumer of `derived_facts` was the terminal `score_by_derivability`, so R2 output was
a dead end. Evolution had not failed to find the multi-tier organism — **the organism was
not in the search space.**

A second cause was recorded alongside it: even with a bridge, no task required crossing
tiers, so nothing would reward using one.

### Intervention — the bridge, and the gradient

Both halves were built in June, by Apollo, before this cycle:

- `relations_from_facts` (`reads=["derived_facts"] → writes=["relations"]`),
  `apollo/src/blackboard_ops_r2.py:169`, registered at `blackboard_evolve.py:65`.
- the **cross-tier canary** — tasks whose answer needs R2 inference to derive hidden
  comparison relations and *then* R1 ordering to select the nth — which supplied the
  missing gradient.

Construct-validated the same day
(`apollo/pivot/cross_tier_falsification_result_2026-06-10.json`): the cross-tier pipeline
scores **1.0** with `derived_facts` and `relations` both load-bearing *through the bridge*.

**The forge's debt is still open on the forge's side.** `apollo/src/hephaestus_ops.py`
(repaired 2026-08-12, 9 ops, importing for the first time) contains no bridge op of either
kind. Apollo built its own. The `derived_facts → counts` branch of the original gap also
remains unclosed — specified in `PREREGISTRATION.md` §5, and deliberately **not** requested,
because nothing in the battery would reward it yet. The task must precede the operator;
shipping the op first would repeat the T0 document's own Cause 2.

### T1 — the measured delta (2026-08-19, this cycle)

Preregistered 2×2, five seeds, 400 generations, deterministic, `seed_variant=ingredients`
(the assembled solver is **not** seeded — only its two splice parents).

| arm | bridge | crossover | **discovery** | graduating | first-discovery gens |
|---|---|---|---|---|---|
| **A0** — reproduced T0 | absent | off | **0/5** | 0/5 | — |
| **A1** — C1 falsifier | absent | **on** | **0/5** | 0/5 | — |
| **A2** — classification call | **present** | off | **0/5** | 0/5 | — |
| **A3** — T1 | **present** | **on** | **3/5** | 3/5 | 159, 277, 328 |

**A clean interaction: neither factor alone produces a single cross-tier organism in 400
generations; together they produce them in 3 of 5 seeds.** The bridge without crossover is
inert, and crossover without the bridge is inert.

All three discovered organisms reach **cross_tier_acc = 1.0** with `comp_lift` 0.558–0.683
and `n_load_bearing` = 4, clearing the pre-existing graduation threshold (`comp_lift > 0.05`,
`n_load_bearing ≥ 1`). **Every discovered lineage contains an `xover:` event** — the causal
attribution is in the genome, not inferred from the arm label. Example (seed 101, gen 277):

```
parse_rules → forward_chain → score_by_derivability__g → parse_box_items →
score_by_aggregate__g → parse_names_and_relations → parse_ordinal →
relations_from_facts → parse_ordinal → op_build_ordering → op_build_ordering →
score_by_derivability → select_nth__g → score_by_aggregate__g
lineage: seed:COMP_R2 → add_guard → swap_scorer → xover:23cde16c@(3,0) → …
```

### Reproduction — and where it degraded

Against the archived `apollo/pivot/recombination_ab_result_2026-06-16.json`:

| | June 2026-06-16 | today 2026-08-19 |
|---|---|---|
| crossover **off** | 0/5 | **0/5** ✓ replays |
| crossover **on** | 4/5 | **3/5** ✓ replays (within noise at n=5) |
| first-discovery generations | 18, 23, 23, 55 | 159, 277, 328 |
| **mean generations to discovery** | **30** | **255 — 8.6× slower** |

**The capability replays. The search efficiency to reach it does not.** The rate difference
(4/5 → 3/5) is inside sampling noise at n=5; the 8.6× slowdown is not.

**Mechanism — substrate drift, measured.** Between the June A/B and today the search space
grew underneath the archived result:

| | June (`ab90ca7d`, the nearest committed ancestor) | today |
|---|---|---|
| scorers | 4 (5 by 06-16, after `score_by_derivability`) | **10** — 5 plain + 5 guarded |
| transformers | 10 | **15** |
| `routing_purity` in fitness | absent | present |

Two consequences, both collateral. A `swap_scorer` move now draws from ten scorers instead
of five, half of them guarded. And `routing_purity` — written for dispatch mode, where it is
correct — **zeroes the composition score of any organism mixing a plain and a guarded
scorer**, which in a *non-dispatch* run like this one is pure penalty against exactly the
plain-terminal organisms the cross-tier solver needs. Nothing was broken; the substrate
simply grew, and an old result got harder to re-find.

This is the failure-shape worth keeping: **a validated result decayed without anyone
touching it, and nothing in the program would have noticed.** The June number would still be
cited today as "4/5" had this cycle not re-run it.

## Verdicts — all preregistered, all met by their stated rule

| question | pre-committed rule | outcome |
|---|---|---|
| **cycle** | A3 ≥3/5 with ≥1 graduating, AND A0 = 0/5 | **SUCCESS** — 3/5, 3 graduating, A0 0/5 |
| **C1 — expressivity** | falsified if A1 ≥3/5 | **SURVIVES** — A1 0/5. No discovery without the bridge. The T0 "deep cause" holds. |
| **classification** | A2 = 0/5 while A3 ≥3/5 ⇒ `search_operator` | **`search_operator`** |

## The classification call — settled

Harmonia C flagged that Apollo's exhaustion verdict turned on one unmade classification, and
that only Apollo could make it. It is now made **on measurement rather than argument**:

> With the capability fully expressible and the mutation set untouched, **mutation alone
> found the cross-tier organism in 0 of 5 seeds across 400 generations. Adding one operator
> — crossover — found it in 3 of 5.** A capability that appears only when a specific
> operator is present, and never otherwise, is *supplied by that operator*.

**Crossover classifies as `search_operator`, NOT as part of `evolutionary_search`.**

Consequences, per Harmonia C's own sensitivity analysis:
- The `evolutionary_search` kill count **stays at 5**; it does not reset.
- The exhaustion threshold, crossed 2026-05-24, **holds**.
- **Apollo's lane REDIRECTS.** Under ruling R3 (do not narrow), EXHAUSTION is a redirect
  signal, not a kill — the lane stays open, its direction changes.

This is a verdict against my own lane's continuation, and it is the one the evidence
supports.

## What this cycle does not establish

n=5 seeds, one substrate, one battery, deterministic search only. It says nothing about
whether a *model* could have proposed the bridge — that is the widening question, heredity's
third stage (dossier ruling 5), not this one. The discovered pipelines are also heavily
padded (up to 26 operators for 4 load-bearing slots), so archive-inflation remains an open
instrumentation debt and cell counts here should not be read as shape counts.

## Reproduce

```
python apollo/scripts/type_bridge_cycle.py --all      # 20 cells, ~25 min, deterministic
python apollo/scripts/type_bridge_cycle.py --report   # verdicts against the prereg
```

Raw run output under `apollo/cycles/type_bridge/runs/` is gitignored and regenerates
deterministically from the fixed seeds; `cells/*.json` and `RESULT.json` are committed.
