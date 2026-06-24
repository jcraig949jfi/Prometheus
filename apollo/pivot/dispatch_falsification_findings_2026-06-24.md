# Dispatch falsification — PASSED: routing is real, genuine, and assembled by ordinary mutation

> **From:** Apollo (M2, Branch C) · **Date:** 2026-06-24
> **Builds on:** `dispatch_design_2026-06-22.md`, `diagnose_0558_findings_2026-06-22.md`
> **Artifacts:** `scripts/dispatch_falsification.py`,
> `pivot/dispatch_falsification_result_2026-06-23.json`
> **Verdict:** G1=PASS G2=PASS G3=PASS G4=PASS → **Road A validated; wire it in.**

## One-line result

A single organism with **mutually-exclusive precondition-guarded scorers** solves a
mixed 2-terminal battery that no single-terminal pipeline can (1.00 vs θ=0.70);
ordinary mutation assembles it in a few steps (5/5 seeds, gens 1–6) where the
single-terminal control **structurally cannot** (0/5); and per-branch ablation
proves it's **genuine routing, not tail-ordering**. Dispatch is the R3 step and the
substrate already supports it — no new control-flow op, and (unlike crossover for
Run 2) **no bespoke combining operator is needed**.

## The gates

| Gate | What it tests | Result |
|---|---|---|
| **G1 construct validity** | hand dispatcher vs specialists on mixed battery | dispatcher **1.00** (inf 1.0 / xt 1.0); inf-specialist 0.70, xt-specialist 0.625 — neither solves both. **PASS** |
| **G2 necessity** | 6000 random single-terminal pipelines | θ_single = **0.70**; **0** single-terminal organisms solve both types ≥0.9 → the >θ region is routing-only. **PASS** |
| **G3 discovery A/B** | seed 2 specialists; can the search assemble a router? | control 0/5; **treatment_merge 5/5** (gens [1,1,1,1,1]); **treatment_mutate_only 5/5** (gens [1,3,2,1,6]). **PASS** |
| **G4 Goodhart audit** | is the discovered router genuine? | per-branch ablation: nulling each guard collapses **exactly its own type** (select_nth__g → xt 1.0 drop / inf 0; deriv__g → inf 1.0 / xt 0); surface-perturbation (shuffle candidates) holds at 1.0; no-branch type → **branch-fire-rate 0.0** (graceful abstention, no misroute). **PASS** |

## The two things that make this trustworthy (not a clean-sweep mirage)

1. **Per-branch ablation is the anti-Goodhart core.** The PoC's risk was a degenerate
   "always run the last scorer" organism passing by tail-ordering. The mutually-
   exclusive guards (`derived_facts>0 AND ordered==0` etc.) plus the ablation result
   — each branch load-bearing for exactly one type, zero cross-effect — show the
   routing is real, not an ordering artifact.
2. **mutate_only (no merge operator) also discovers it, 5/5.** This is the actionable
   wiring answer. Run 2 needed a *bespoke crossover* to cross a valley; dispatch does
   **not** — ordinary `append_guarded_scorer` mutation grows the router in a few
   coordinated steps (gens 1–6). So wiring is cheap: guarded atoms + multi-scorer-
   tail support + one mutation move. (merge still helps — it's instant — but isn't
   required.)

## Honest caveats (failure shapes, per doctrine)

1. **Ingredients-seeded regime.** G3 seeds the two *specialists* (same discipline as
   the recombination A/B). It proves "given specialists, the search assembles a
   genuine router," NOT de-novo discovery of the specialists themselves — that is a
   separately-validated capability (recombination found the cross_tier solver de
   novo). The gens-[1,3,2,1,6] spread for mutate_only shows it's not the trivial
   gen-1 merge, but it's still the easy regime.
2. **θ_single = 0.70 includes incidental cross-coverage** (the inf-specialist
   accidentally solves 8/20 xt). The routing gap (1.0 vs 0.70) and "0 single-terminal
   solve both" are solid; the literal "+0.30" overstates the clean routing margin.
3. **2-type battery only.** The real battery is 4 subsets needing ≥3 terminals.
   Dispatch over 3+ mutually-exclusive guards (add aggregate, etc.) and guard-
   collision as the type-count grows is the next scale-up — untested here.
4. **canary still excluded** — it needs a boolean primitive (separate gap from the
   0.558 diagnosis); dispatch alone doesn't touch it.

## What to wire into `src/blackboard_evolve.py` (next build)

1. **Guarded scorer atoms** in `REGISTRY` (mutually-exclusive preconditions on
   semantic slots — never `problem_text` surface): `select_nth__g`,
   `score_by_derivability__g`, `score_by_aggregate__g` (+ others as terminals grow).
2. **Relax the organism constraint** in `fitness()` / seed / mutation from "exactly
   one scorer, must be last" → "≥1 scorer; answer from the fired guard(s)."
3. **`append_guarded_scorer` mutation move** (G3 shows this alone suffices); keep an
   optional dispatch-merge for speed.
4. **Metric re-instrumentation** (the 0.558 diagnosis step 1): log oracle/portfolio
   coverage + per-subset alongside best_acc. With dispatch, best_acc should rise
   *toward* portfolio coverage on the real battery — success = convergence.
5. **Carry the G4 guards into the loop**: per-branch ablation on dispatchers + the
   `branch_fire_rate` abstention check, so a degenerate router can't graduate.

Then a short deterministic run on the **full 4-subset battery** to confirm a single
evolved dispatcher lifts best_acc past 0.558 (target ≈ portfolio coverage 0.758,
minus the canary floor) before any GPU/llm run.

## WIRED INTO THE SUBSTRATE — and it breaks the 0.558 ceiling (2026-06-24)

Dispatch is now wired into `src/blackboard_evolve.py` (behind `--dispatch`):
guarded scorer atoms (`select_nth__g`, `score_by_derivability__g`,
`score_by_aggregate__g`, mutually-exclusive semantic-slot guards); `fitness()`
relaxed to "≥1 scorer anywhere"; `descriptor()` keyed on the **scorer SET** (so a
router is a distinct cell); `add_guard` mutation move; seeds use guarded scorers in
dispatch mode; portfolio-coverage + per-subset + `max_acc` + in-loop per-branch
`dispatch_audit` logged every gen.

**Deterministic validation run (600 gens, pop 24, full 4-subset battery, no LLM):**

| metric | before (xover plateau) | dispatch run |
|---|---|---|
| **max_acc** (best single organism) | 0.558 | **0.683** (first break gen 131; settled ~gen 500) |
| portfolio coverage | 0.758 (gen-400 archive) | 0.742 |
| per-subset (portfolio) | — | canary 0.44 / synth ~0.7 / inference 1.0 / cross_tier 1.0 |

The ceiling-breaking organism is a multi-branch dispatcher
(`parse_rules→parse_ordinal→parse_names_and_relations→forward_chain→
relations_from_facts→op_build_ordering→…→score_by_aggregate__g→select_nth__g`),
acc **0.683** — the **+0.125 = exactly the inference-routing payoff** (20 inference
tasks, 0.25→1.0). best_acc (single organism) now approaches portfolio coverage, as
predicted: dispatch makes the two converge.

### Honest caveats on the wiring run

1. **`best_acc` was hiding the result.** `best` is ccs-selected and trailed the
   highest-acc organism; added `max_acc` (best single organism by accuracy) — that's
   the honest ceiling-break number. Without it the run looked stuck at 0.517.
2. **2-branch dispatchers only TIE 0.558**, because guarded `select_nth__g` (fires
   only when `ordered`>0) loses the incidental synth/canary hits that the old
   *unconditional* `select_nth` got for free. Beating the ceiling needed a 3-branch
   dispatcher with a genuine aggregate sub-pipeline — assembled by ~gen 500, not 80.
   (The 0.558 baseline was partly luck; dispatch trades luck for genuine routing.)
3. **Winners still mix plain + guarded scorers**, so some routing is override-based
   (tail-ordering) not purely mutually-exclusive. The eval is honest (acc = exact
   answer match) so 0.683 is real, but the `genuine_routing` audit flag is often
   False — clean-routing pressure isn't in the fitness yet.
4. **Archive inflation persists** (1825 cells / 1622 "distinct shapes") — the
   scorer-set descriptor + op-duplication Goodhart hole. `max_acc` and
   `portfolio_coverage` are the trustworthy numbers, NOT the shape count.
5. **canary still capped ~0.44** — needs the boolean primitive (separate gap).
6. **Deterministic only.** The production `--mode llm --dispatch` run is the next
   GPU commitment — gate it on this result, watch `max_acc` past 0.683 and whether
   `genuine_routing` dispatchers emerge.

### Wiring artifacts

`src/blackboard_evolve.py` (uncommitted), validation run
`run_branch_c_dispatch_smoke/` (checkpoint gen 600).

## CLEAN-ROUTING PRESSURE (2026-06-24) — strips the Goodhart, reveals the honest number

Caveat 2-3 above (hybrids tie 0.558, mix plain+guarded) were addressed by adding
clean-routing pressure: in dispatch mode mutation draws scorers from the GUARDED pool
only (plain scorers can't enter), and `fitness()` zeroes ccs for any plain+guarded
hybrid. Result of the 600-gen deterministic re-run:

- **Hybrids eliminated** — top-20 by acc are all guarded-only. Archive deflated
  **1825 → 188 cells** (the plain-scorer-variant inflation collapsed — a real Goodhart
  reduction, not just cosmetic).
- **Honest per-subset (best clean dispatcher vs old single-terminal):**

| | full battery | **routable-only (excl canary)** | inference |
|---|---|---|---|
| clean dispatcher (guarded-only) | 0.542 | **0.786** | **20/20** |
| old single-terminal (select_nth) | 0.558 | 0.657 | 5/20 |

**The full-battery drop (0.558→0.542) is NOT a regression — it's de-Goodharting.**
The old organism scored 21/50 canary by *unconditional guessing* on compare/bool
tasks that are genuinely unsolvable (no boolean op); the clean router correctly
abstains (10/50) and instead wins where reasoning is real: inference 5/20→**20/20**,
routable-only **0.657→0.786 (+0.129)** — the genuine R3 payoff. canary inflates the
headline by rewarding guessing.

- **New honest metric:** `max_routable_acc` (best single organism over non-canary
  subsets) logged every gen = **0.786**. This is what the LLM run should be judged on,
  NOT full-battery `max_acc`.
- **Still owed:** the winner lacks `parse_box_items`/`op_aggregate_quantities`, so its
  `score_by_aggregate__g` branch is decorative (synth only 15/30, `genuine_routing`
  False). A dispatcher that assembles the aggregate sub-pipeline should push routable
  acc higher; 600 deterministic gens didn't get there. And canary stays ~0.2-0.44
  until the boolean primitive lands.

Validation runs: `run_branch_c_dispatch_smoke/` (pre-clean, 0.683 inflated),
`run_branch_c_dispatch_clean/` (post-clean, 0.542 full / 0.786 routable).

## Reproduce

`python apollo/scripts/dispatch_falsification.py` → standalone gates.
`cd apollo/src && python blackboard_evolve.py --gens 600 --pop 24 --dispatch` →
full-battery deterministic run; watch `max_acc` and `portfolio_coverage` in
`run_branch_c/evolve_log.jsonl`.
