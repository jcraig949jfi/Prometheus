# Tee-up: the DISPATCH / routing capability (Apollo's R3 step)

> **From:** Apollo (M2, Branch C) · **Date:** 2026-06-22
> **Builds on:** `diagnose_0558_findings_2026-06-22.md` (the wall = no dispatch)
> **PoC (G1 PASSED):** `scripts/dispatch_poc.py`
> **Status:** design + validated construct. Awaiting James's go on the architecture
> fork before the falsification + A/B build.

## Why dispatch (the bottleneck, restated)

The 0.558 diagnosis showed the archive already holds specialists that solve
synth/inference/cross_tier — but `best_acc` can't exceed ~0.56 because one linear
pipeline has one terminal and the battery needs ≥3. The missing capability is
**conditional dispatch**: a single organism that routes to the right sub-strategy
per task type. In ladder terms (`project_reasoning_ladder_v01`): the archive holds
R0/R1/R2 specialist atoms; **assembling them under a router is the R3 step**, and
the linear-pipeline/single-terminal organism model can't express it. This is the
bottleneck having moved a third time: Run 2 → search-operator (crossover) →
**dispatch**.

## Key finding: dispatch is ALREADY nearly expressible (no new control-flow op)

`BlackboardOp` carries a `precondition` and `on_fail="skip"`. A scorer whose
precondition fails is skipped and leaves `selected_answer` untouched. So a pipeline
of **precondition-guarded scorers** is a dispatcher: only the scorer whose guard
matches the task type writes the answer. No `if`-op, no `switch`-primitive, no
second evolutionary layer — just (a) guarded scorer atoms and (b) relaxing the
"exactly one terminal, must be last" organism constraint.

### G1 construct validity — PASSED (`dispatch_poc.py`)

Mixed battery = 20 inference + 20 cross_tier tasks (needs 2 different terminals):

| organism | overall | inf | xt |
|---|---|---|---|
| inference-specialist (`…→score_by_derivability`) | 0.70 | 20/20 | 8/20 |
| cross_tier-specialist (`…→select_nth`) | 0.625 | 5/20 | 20/20 |
| **DISPATCHER** (shared transforms + guarded `score_by_derivability` + guarded `select_nth`) | **1.00** | 20/20 | 20/20 |

A single dispatching organism reaches 1.0 where the best single-terminal pipeline
caps at 0.70. **The capability is real and expressible in the current substrate.**

### Subtlety the PoC surfaced (the Goodhart surface to close)

**20/40 tasks fire BOTH guards.** Cross_tier tasks populate `derived_facts` (via
`forward_chain`) *and* `ordered` (via `op_build_ordering`), so the derivability and
select_nth guards aren't mutually exclusive. The dispatcher scored 1.0 only because
`select_nth` is ordered LAST and overwrites — i.e. correctness leaned on
**tail-ordering, not genuine routing**. A design that ships this naively would
reward a degenerate "always run the last scorer" organism. The design MUST make
guard arbitration explicit and verify each branch is independently load-bearing.

## Minimal substrate changes

1. **Guarded scorer atoms** (new `ROLE_SCORER` registry entries, hand-authored —
   these are the new R-atoms the search composes):
   - `select_nth__if_ordered` — precond `len(ordered) > 0`
   - `score_by_derivability__if_facts` — precond `len(derived_facts) > 0` **and**
     `len(ordered) == 0` (mutual-exclusion clause closes the overlap from the PoC)
   - `score_by_aggregate__if_quantities` — precond `len(quantities) > 0`
   Guards key on **semantic slot population**, never on `problem_text` surface
   features (that would be memorization — see G-guard 3).
2. **Relax the organism constraint** in `fitness()`/seed/mutation from "exactly one
   scorer, must be last" → "**≥1 scorer; `selected_answer` is taken from the fired
   scorer(s)**." Arbitration rule (pick ONE, document it):
   - *Recommended:* **mutually-exclusive guards** so order is irrelevant and routing
     is genuine (the `… and len(ordered)==0` clause above). Cleanest to verify.
   - *Fallback:* keep `run_pipeline`'s last-match-wins and let the search order
     guards — but then per-branch ablation (G-guard 2) is mandatory to prove the
     ordering isn't a degenerate "last scorer does everything."
3. **Mutation operators:** allow inserting guarded scorers in the tail region and
   allow multi-scorer tails (today mutation assumes a single trailing scorer).

## Falsification design (`dispatch_falsification.py` — to build)

Mirrors the recombination falsification structure.

- **G1 construct validity** — DONE (`dispatch_poc.py`): dispatcher 1.0 vs best
  single-terminal θ≈0.70 on the mixed battery. Fold in as the construct gate.
- **G2 necessity (the valley):** search single-terminal pipelines (all
  compositions up to depth D, single trailing scorer) on the mixed battery; prove
  **none exceed θ**. Then the (1.0 − θ) region is reachable *only* by routing —
  the dispatch analogue of "the solver is in neither 1-edit neighborhood."
- **G3 discovery (A/B):** seed the two SPECIALIST sub-pipelines (NOT the
  dispatcher). Both arms run identical mutation.
  - control: guarded-scorer atoms + multi-scorer tails **disabled** (Run-2 regime)
  - treatment: **enabled**
  - 5 seeds × N gens, balanced 50/50 battery. Metric: gen of first organism with
    overall ≥0.9 **and both per-type ≥0.9** (so a type-skew router can't pass).
    Predict treatment K/5, control 0/5.

## Goodhart guards (occupy R3 only if these hold — ladder doctrine)

1. **Per-type accuracy always reported**, never just overall. A router that ignores
   a type shows as that type stuck at chance. Battery balanced 50/50 so overall
   can't be gamed by skew.
2. **Per-branch dataflow ablation** (reuse `dataflow_fitness`): null one guarded
   scorer → its task-type acc must collapse while the other type is unaffected =
   genuine routing. If nulling a branch doesn't hurt → decorative/overlap artifact
   (the tail-ordering trap), REJECT.
3. **Guard-robustness (adversarial):** paraphrase / shuffle / pad the task surface;
   the precondition must still route correctly because it reads semantic slots, not
   surface features. A guard that keys on `problem_text` length or a keyword is
   memorization — REJECT. (This is the executing-lens analogue: the verifier
   perturbs the input and re-checks routing.)
4. **Tier-predicted failure:** an R3 dispatcher should fail when given a task type
   it has no branch for (graceful: leaves `selected_answer` empty / chance), NOT by
   silently misrouting. Confirm the failure shape matches "no matching guard."

## Dependency / sequencing

- **Fold in the metric re-instrumentation first** (diagnosis step 1): report
  oracle/portfolio coverage + per-subset alongside `best_acc`. With dispatch, a
  single organism can finally cover multiple subsets, so **`best_acc` should rise
  toward portfolio coverage** — success = the two converging. Without the metric
  fix we can't see dispatch working.
- **Cost:** PoC + falsification + A/B are deterministic, CPU-only, no GPU/LLM —
  runnable today in minutes. The production `--mode llm` run stays parked until
  dispatch is validated AND the metric is fixed (a blind relaunch replateaus at
  0.558).

## The architecture fork (James's call)

The diagnosis named two roads; this design commits to **Road A** as the cheaper,
more falsifiable first step:

- **Road A — dispatch primitive (one organism routes).** Guarded multi-scorer
  organisms, above. Smallest substrate change, reuses existing precondition
  machinery, directly testable, and it's a genuine new *capability* (R3) rather
  than a measurement change. **Recommended.**
- **Road B — dispatched portfolio (separate learned router over specialists).** A
  second evolutionary layer mapping problem → specialist-id. Heavier, larger
  Goodhart surface (the router can memorize), and it externalizes the capability
  instead of evolving it. Defer unless Road A's falsification fails.

**Decision needed:** approve Road A (then I build `dispatch_falsification.py` +
the guarded-scorer atoms + metric re-instrumentation and run the deterministic
A/B), or redirect to Road B.

## Reproduce

`python apollo/scripts/dispatch_poc.py`
