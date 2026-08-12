# Apollo — RESUME (2026-06-15, updated 2026-06-16)

Context-reset resume doc. Read this + the linked artifacts to pick up exactly
where we left off. Apollo = evolutionary composition substrate (Branch C);
goal = evolve multi-tier reasoning organisms from forge R-atoms.

## 2026-06-16 UPDATE — recombination operator VALIDATED

The recombination experiment ran and the result is decisive. See
`D:\Prometheus\apollo\pivot\recombination_findings_2026-06-16.md`.

- **Falsification (PASSED):** a crossover operator reaches a load-bearing
  multi-tier solver single-step mutation cannot (8000 random single-step walks →
  0 hits; crossover → 6.1%/pair). `recombination_falsification_result_2026-06-16.json`.
- **A/B (PASSED):** from ingredients-seeded starts (parents seeded, solver NOT),
  crossover discovers the novel multi-tier solver **de novo in 4/5 seeds**;
  single-step in **0/5**. `recombination_ab_result_2026-06-16.json`.
- **The Run 1+2 plateau was a search-operator failure** — not substrate, not eval.
- **Wired into `src/blackboard_evolve.py`:** `recombine()`, `--crossover-frac`,
  `--seed-variant ingredients`, per-gen `novel_multitier` signal.
- **Caveats (honest):** padding inflation persists (56 "cells" ≈ 1 real core +
  duplicate-op variants); crossover is stochastic (1/5 miss); only deterministic
  mode tested so far.
- **Granite is UP on :8800** (run_recomb/granite.pid).
- **PRODUCTION RUN LAUNCHED 2026-06-16** (James approved full multi-day run):
  `run_branch_c_xover/`, `blackboard_evolve --gens 3000 --pop 24 --mode llm
  --crossover-frac 0.3 --seed-variant default --checkpoint-every 50`. PID in
  `run_branch_c_xover/evolve.pid` (20956). ~118s/gen → ~4 days to gen 3000.
  Detached via Start-Process (survives session). Watch signals: `novel_multitier`
  in `run_branch_c_xover/evolve_log.jsonl` (>0 = genuine de-novo solver beyond the
  seeded one — the thing Run 2 never produced) and `best_acc` rising above 0.392.
  First-discovery events → `run_branch_c_xover/novel_discovery.jsonl`.

## Live state (as of 2026-06-15)

- **Run 2 is STOPPED (killed per user decision 2026-06-15).** Actual run dir is
  `D:\Prometheus\apollo\run_branch_c_xt\` (NOT under `pivot/`). `blackboard_evolve
  --mode llm --gens 3000 --pop 24 --checkpoint-every 50`. Reached **gen 2668/3000**
  (final log entry 6:59 AM, elapsed ~440000s / ~122h) before the process
  terminated. best_acc 0.392 flat throughout — conclusion unchanged, so the run
  was killed rather than ridden to 3000. The evolve process and the Granite
  server (port 8800) were both already gone when checked; nothing left to stop.
- Durable artifacts: per-gen log `run_branch_c_xt/evolve_log.jsonl` (final line
  gen 2668); archive snapshots `run_branch_c_xt/checkpoints/` every 50 gens.
- To restart inference next session: bring Granite back up on :8800 via
  `src/llm_server_alt.py` (Granite-3.0-2B, ~2.7GB VRAM) — it is NOT currently
  running.

## The headline result (this is the finding)

**best_acc has been flat at 0.392 since gen 1. No novel cross-tier organism has
emerged beyond the seeded one.** At gen 2650 the bridge/forward_chain shapes are:
the seed (`parse_rules→parse_ordinal→forward_chain→relations_from_facts→
op_build_ordering→select_nth`, ccs 0.343, lb=7), padding-clones (double
forward_chain / double parse_rules), no-op-bridge shapes (relations_from_facts
appended to an R0-R1 ordering pipeline where derived_facts is empty so it's
skipped), and degenerate crosses (acc 0.29). **Nothing genuinely new.**

This is the same plateau as Run 1 — but now it falsifies a sharper claim. Run 1
showed cross-tier composition was neither expressible nor rewarded. We fixed
both (bridge op + cross-tier canary, both validated). Run 2 proves expressibility
+ gradient are **necessary but NOT sufficient**: the search still doesn't assemble
the 6-op multi-tier organism de novo. The bottleneck has moved from the
substrate/eval to the **search operator**.

## Why (working diagnosis — verify on resume)

The mutation operator is single-step: Granite proposes ONE `insert_step` per
offspring (`mutate_llm` in `blackboard_evolve.py`). Building a novel 6-op
multi-tier pipeline from R0-R1 ancestors requires several coordinated inserts
that are each individually neutral or harmful until the whole chain is present —
a fitness valley single-step hill-climbing won't cross. The seed survives because
it's pre-assembled; nothing else reaches that depth. (MAP-Elites keeps the seed
as a live specialist, so it never dies — but also never gets improved on.)

## Next levers (pick on resume — do NOT just run longer)

1. **Recombination/crossover** — splice load-bearing sub-pipelines from two
   archive cells (e.g. an R2 prefix + an R1-ordering suffix) so multi-op jumps
   happen in one mutation. This directly targets the valley-crossing problem.
2. **Building-block seeding / curriculum** — seed partial multi-tier fragments
   (e.g. `forward_chain→relations_from_facts`) as reusable macros the mutator can
   insert atomically.
3. **Stagnation-triggered exploration** — Run 1+2 both flatlined from gen 1; the
   ROADMAP P0 stagnation monitor was never built. Detect plateau → inject novelty.

Recommended first: (1) recombination. It's the smallest change that attacks the
measured cause. Falsification-first: design a canary where the ONLY way to the
answer is recombining two existing archive shapes, prove a crossover operator
finds it and single-step mutation can't.

## Decisions pending James

- ~~Let Run 2 finish or kill now.~~ **RESOLVED 2026-06-15: kill now** (James).
  Both processes were already terminated when checked; final state gen 2668,
  best_acc 0.392 flat. The finding stands on the full run.
- Greenlight the recombination experiment as the next build. **← now the live
  next step** (search-operator bottleneck is the measured cause; see above).
- Forge side: `apollo/pivot/apollo_forge_reply_2026-06-09.md` (R2 typed-transformer
  contract) is filed and awaiting the operator; not blocking.

## File map (absolute paths)

- Substrate: `D:\Prometheus\apollo\src\blackboard.py`, `blackboard_evolve.py`,
  `blackboard_ops_r2.py` (R2 ops + `relations_from_facts` bridge)
- Canaries: `apollo\scripts\inference_canary.py`, `apollo\scripts\cross_tier_canary.py`
- Falsifications (both PASSED): `apollo\scripts\r2_falsification.py`,
  `apollo\scripts\cross_tier_falsification.py`; results in `apollo\pivot\*_result_*.json`
- Findings: `apollo\pivot\r2_run1_findings_2026-06-10.md` (the tier-bridge lesson)
- Granite relaunch: `llm_server_alt.py` with env
  `LLM_ALT_MODEL_NAME=D:/Prometheus/apollo/.hf_cache/granite2b`, `LLM_ALT_PORT=8800`
- Memory: `project_apollo_r2_falsification_20260609.md`

## Copy-paste restart prompt

> You're Apollo. Resume from `D:\Prometheus\apollo\pivot\RESUME_apollo_2026-06-15.md`.
> Read it plus `r2_run1_findings_2026-06-10.md` and the latest checkpoint in
> `run_branch_c_xt/checkpoints/`. First: report Run 2's current gen + whether any
> novel cross-tier organism finally appeared beyond the seed (check the newest
> checkpoint for bridge-using shapes that aren't the seed/padding/no-op). Then we
> decide: recombination operator experiment vs. let it ride. Granite should be up
> on :8800; the evolve job is `run_branch_c_xt/`.
