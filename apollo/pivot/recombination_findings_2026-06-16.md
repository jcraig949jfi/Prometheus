# Recombination — findings: the Run 1+2 plateau was a search-operator failure

> **From:** Apollo (M2, Branch C) · **Date:** 2026-06-16
> **Builds on:** `RESUME_apollo_2026-06-15.md`, `r2_run1_findings_2026-06-10.md`
> **Artifacts:** `pivot/recombination_falsification_result_2026-06-16.json`,
> `pivot/recombination_ab_result_2026-06-16.json`

## One-line result

A **crossover operator** reaches a load-bearing multi-tier organism that
single-step mutation provably cannot — and in a controlled A/B it discovers that
organism **de novo in 4/5 seeds while single-step discovers it in 0/5**. The
Run 1 (gen 481) and Run 2 (gen 2668) plateaus were a **search-operator** failure,
not a substrate or eval failure. Both earlier diagnoses (expressibility, gradient)
were necessary but not sufficient; the missing piece was an operator that can make
a multi-op jump in one move.

## The diagnosis being tested

Run 2 plateaued at best_acc 0.392 for 2668 gens: the substrate *hosts* the
cross-tier organism (falsification 2026-06-10) and the eval *rewards* it
(cross-tier canary), yet evolution never assembled a novel multi-tier organism —
it only kept the **seeded** one alive. Diagnosis: the mutation operator is
single-step. Building the 6-op multi-tier pipeline from ancestors needs several
coordinated inserts that are each individually neutral or harmful — a fitness
valley single-step hill-climbing won't cross.

## Experiment 1 — falsification (does crossover cross the valley?)

`scripts/recombination_falsification.py`. Two **plausible** parent shapes, each a
known control from the cross-tier falsification, whose one-point splice IS the
validated cross-tier organism:

- `P1 = parse_rules → parse_ordinal → forward_chain → relations_from_facts → score_by_derivability`
  (has inference + bridge, but the WRONG terminal → gives derivability, not rank)
- `P2 = parse_names_and_relations → parse_ordinal → op_build_ordering → select_nth`
  (R1 ordering; parses relations from names → none present on this canary → empty order)
- `splice(P1[:4], P2[2:]) = parse_rules → parse_ordinal → forward_chain → relations_from_facts → op_build_ordering → select_nth`

| Gate | Result |
|---|---|
| **G1 construct validity** | acc(P1)=0.30, acc(P2)=0.30 (≈chance 0.25); acc(splice)=**1.00**, comp_lift +1.00; `derived_facts` & `relations` both load-bearing |
| **G2 the valley** | 117 / 92 single-edit neighbors of P1 / P2 — best neighbor acc stays **0.30** (first step has zero gradient); solver not in either 1-edit neighborhood; **8000 random single-step walks (depth 4) reached the solver 0 times** |
| **G3 crossover** | 2000 crossover ops → **6.1% solve rate**, best_acc 1.00, 53 solver-shape hits; vs single-step 0% |

**Verdict: YES.** One splice crosses a ≥1-edit fitness valley that single-step
mutation cannot. The search-operator bottleneck is the real cause.

## Experiment 2 — empirical A/B (does it discover de novo?)

`scripts/recombination_ab.py`. Both arms start from the SAME *ingredients*
seeding (the two splice-parents but NOT the pre-assembled cross-tier solver) and
run the SAME deterministic single-step mutation. Only difference: the operator.

- **control**: `crossover_frac = 0.0` (single-step only — the Run 1+2 regime)
- **treatment**: `crossover_frac = 0.3` (single-step + recombination)
- 5 seeds × 400 gens, pop 24. Metric: gen of first de-novo multi-tier solver
  (not a seed; contains an R2 inference op + an R1 ordering op; solves the
  cross-tier subset ≥0.9).

| seed | control | treatment (first-novel gen) |
|---|---|---|
| 20260616 | not discovered | **gen 55** |
| 1 | not discovered | **gen 18** |
| 7 | not discovered | not discovered |
| 42 | not discovered | **gen 23** |
| 101 | not discovered | **gen 23** |
| **total** | **0 / 5** | **4 / 5** |

The shortest organism crossover discovered de novo (seeds 20260616, 1) is the
**exact** validated cross-tier solver
`parse_rules → forward_chain → relations_from_facts → parse_ordinal →
op_build_ordering → select_nth`, with lineage `[seed:COMP_R2, …, xover:…]` —
assembled by a crossover op, not present at seed time. Treatment best_acc rose to
**0.52–0.55** (vs control ~0.42 and Run 2's 0.392), a real capability gain: the
cross-tier subset is now solved.

## Honest caveats (failure shapes, per doctrine)

1. **Padding inflation persists.** Treatment archives blew up to 81–87 cells with
   "56–58 distinct load-bearing cores," but the *shortest* solver is one canonical
   organism; the rest are duplicate-op / reorder variants whose redundant op
   shifts the load-bearing core into a fresh cell. This is the SAME Goodhart
   fake-diversity flagged in Run 1 (r2_run1_findings §side-observation). **Report
   the discovery as "crossover found the solver core single-step couldn't," NOT
   "56 inventions."** The load-bearing-core archive key still doesn't collapse
   op-duplication; that's an open instrumentation debt.
2. **Crossover is stochastic — 1/5 miss (seed 7).** Random cut points mean 400
   gens at frac=0.3 doesn't guarantee the right splice every seed. The operator
   raises discovery probability; it doesn't make it certain. Levers: higher
   crossover_frac, more gens, or smarter cut-point selection (splice at
   type-compatible slot boundaries instead of uniformly).
3. **Tested in deterministic mode**, to isolate the operator from LLM variance.
   The falsification proved valley-crossing is mutation-type independent, but the
   production `--mode llm` regime is not yet confirmed end-to-end.

## What was wired (all in `src/blackboard_evolve.py`)

- `recombine(pa, pb)` — one-point splice (prefix of pa body + suffix of pb;
  child always ends in pb's terminal scorer).
- Reproduction loop: `--crossover-frac` of offspring produced by recombination of
  two random archive occupants (composes with both deterministic and llm mutation).
- `--seed-variant ingredients` — seeds the two splice-parents, not the solver, so
  cross-tier discovery is genuinely de novo.
- Per-gen `novel_multitier` signal + `novel_discovery.jsonl` event log (memoized
  cross-tier eval so a large archive stays cheap).

## What's next (decision pending)

The operator is validated and wired. The open call is the **production
`--mode llm` run with crossover** — confirm the effect holds with Granite
mutation in the loop and watch for discovery *beyond* this one solver. That is a
multi-day GPU commitment (Run 2 was ~122h); scope/duration is James's call.
Granite is up on :8800, ready.
