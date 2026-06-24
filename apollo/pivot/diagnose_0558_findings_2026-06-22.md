# Diagnosis: the best_acc 0.558 wall is two stacked ceilings — neither is "run longer"

> **From:** Apollo (M2, Branch C) · **Date:** 2026-06-22
> **Builds on:** `RESUME_apollo_2026-06-15.md`, `recombination_findings_2026-06-16.md`
> **Artifacts:** `scripts/diagnose_0558_wall.py`, `pivot/diagnose_0558_result_2026-06-22.json`
> **Method:** falsification-first decomposition (H-express / H-eval / H-operator)

## One-line result

The 0.558 plateau is **not one wall and not a search failure**. It is two
independent ceilings stacked: (1) a **measurement/organism-model ceiling** —
`best_acc` scores a single fixed-terminal pipeline against a heterogeneous
4-subset battery, so it *structurally cannot* exceed ~0.56 however good the
search; and (2) a **hard substrate floor on the `canary` subset** — comparison/
boolean tasks have no solver in the primitive set, capping even an oracle
portfolio at 0.758. The crossover operator is **vindicated, not implicated**.

## The measurement: per-subset decomposition (gen-400 elite)

Battery = 120 tasks: `canary` 50 + `synth` 30 + `inference` 20 + `cross_tier` 20.
The single best organism (`parse_rules→forward_chain→parse_names_and_relations→
relations_from_facts→parse_ordinal→op_build_ordering→select_nth`, terminal
`select_nth`, acc **0.558**) scores:

| subset | elite acc | what it needs |
|---|---|---|
| cross_tier | **1.00** | `select_nth` terminal (elite is a cross_tier specialist) |
| synth | 0.70 | mixed |
| canary | 0.42 | a boolean/yes-no terminal (does not exist) |
| inference | **0.25 (chance)** | `score_by_derivability` terminal |

The elite gets `inference` at chance because it **can't** — it terminates in
`select_nth`, and inference tasks need `score_by_derivability`. One organism has
one terminal. A heterogeneous battery needs ≥3.

## Ceiling 1 — organism-model / measurement ceiling (the cause of the *plateau*)

**Oracle portfolio coverage** (a task counts as covered if *any* archive occupant
solves it): **91/120 = 0.758**, vs single-best 0.558 — a **+0.20** gap.

| subset | single best | archive portfolio |
|---|---|---|
| synth | 0.70 | **1.00** |
| inference | 0.25 | **1.00** |
| cross_tier | 1.00 | 1.00 |
| canary | 0.42 | 0.42 |

The archive **already contains specialists that fully solve synth, inference, and
cross_tier.** `best_acc` never moved past 0.558 because it tracks one organism,
and no single fixed-terminal pipeline can serve `inference` (needs
`score_by_derivability`) and `cross_tier` (needs `select_nth`) at once. **The
plateau was largely a measurement artifact** — the search was being judged by a
metric it structurally cannot move on a heterogeneous battery.

**Honest caveat:** 0.758 is an *oracle* upper bound — it assumes a perfect router
picking the right specialist per task. A real system would have to *learn* the
dispatch. So the actual missing capability is **DISPATCH / routing**, which the
current organism model (linear pipeline, single terminal, no branching) cannot
express. In ladder terms: the archive holds R0/R1/R2 specialist atoms; assembling
them under a router is the **R3 step**, and that step is not yet expressible.

## Ceiling 2 — hard substrate floor on `canary` (caps the portfolio at 0.758)

29/50 canary tasks are solved by **zero** archive organisms. Breakdown of canary
by type: **20 compare/bool** ("Is 39.09 larger than 51.59?" → yes/no), 20 "other"
(incl. "X is less than Y. Which is larger?"), 5 count, 5 order.

- **H-express (missing primitive):** the registry has 5 terminals — `select_nth`,
  `score_by_aggregate`, `score_by_derivability`, `score_by_max_entity`,
  `score_by_max_value` — and **none emit a yes/no answer**. There is no
  boolean-comparison transformer either. Comparison tasks are genuinely
  **inexpressible** in the current substrate.
- **H-eval (data-quality smell):** canary correct-answer strings are padded +
  truncated filler — e.g. `'No as stated as stated precise'`, `'Yes exactly
  specifically in th'` (cut at 30 chars). Even *with* a boolean op, a terminal
  would have to emit that exact arbitrary string, which is **not derivable from
  the input**. `data/clean_canary_v01.json` has a generator-quality problem worth
  auditing independently.

## Verdict on the three hypotheses

- **H-operator (crossover insufficient): REJECTED.** Crossover already built a
  portfolio covering 3/4 subsets fully. More search machinery is not the lever.
- **H-express: CONFIRMED, in two places.** (a) No routing/dispatch in the organism
  model → the +0.20 single-vs-portfolio gap. (b) No boolean primitive → the
  canary comparison floor.
- **H-eval: PARTIALLY CONFIRMED.** canary answer strings are padded/truncated and
  not input-derivable; this compounds the canary floor.

## Recommended next steps (priority order)

1. **Re-instrument the headline metric** from single-best-organism `best_acc` to
   **oracle/portfolio coverage + per-subset breakdown** (~30 LOC, log it every
   gen). Highest leverage, lowest cost: it reports the system's real capability
   (0.758, not 0.558) and stops judging the search by a metric it can't move.
2. **Architecture call (James):** is the goal one organism that solves everything
   (→ needs a **routing/dispatch primitive** — the R3 capability) or a dispatched
   **portfolio**? Either way the next build is dispatch, not a wider search over
   linear pipelines. This is the bottleneck having *moved again*: Run 2 → search
   operator (solved by crossover) → **dispatch / organism expressiveness**.
3. **canary substrate:** add a boolean-compare transformer + yes/no terminal and
   re-run — a clean expressibility experiment (can the search then assemble a
   comparison solver?). Independently, audit/regenerate `clean_canary_v01.json`'s
   padded answer strings.
4. **Do NOT relaunch the long llm run as-is.** It would replateau at 0.558 against
   the same metric. Fix the metric (step 1) and decide dispatch (step 2) first.

## Reproduce

`python apollo/scripts/diagnose_0558_wall.py` → console report +
`pivot/diagnose_0558_result_2026-06-22.json`.
