# Apollo — STARTUP (read this first)

**Updated:** 2026-08-12 · **Identity:** see `roles/Apollo/CHARTER.md`

## 2026-08-12 — RESUMED after ~6wk break. llm2 run RESOLVED: kill condition fired.

Nothing is running (no python procs). All Apollo commits through `709c28f9` are on
`origin/main`. `roles/Apollo/` and most of `apollo/pivot/*` + `apollo/run_*` are still
UNTRACKED (working-tree only).

**`run_branch_c_dispatch_llm2/` COMPLETED** (gen 800, 86156s ≈ 24h, finished
2026-06-28 10:28). Verdict = the pre-registered kill condition below:

- `max_acc` **0.833**, `max_routable_acc` **1.000**, coverage 0.833
  (canary 0.6 / synth 1.0 / inference 1.0 / cross_tier 1.0) — **exactly the
  deterministic numbers.** Zero lift from Granite.
- Trajectory: 0.317 (g1) → 0.65 (g8) → 0.75 (g21) → **0.833 at gen 131**, then
  **669 gens of nothing** but archive padding (2860 cells / 2846 "shapes").
- 2152 LLM mutations (~2.7/gen — 19× the prior run's rate) still bought nothing.
  → **`--mode llm` does not earn its GPU in this regime. Run deterministic.**
- **Residual failure-shape:** gen-800 `dispatch_audit.genuine_routing = **false**`.
  Branches overlap instead of partitioning: `select_nth__g` drops canary 0.2 +
  synth 0.5 + cross_tier 1.0; `score_by_extreme_number__g` and
  `score_by_comparison__g` each drop canary 0.2 yet have empty `load_bearing_for`.
  The 0.833 is real; the *routing* is not clean. This is the open thread.

**Open moves (Apollo's read, awaiting James's call):**
1. **Clean-routing debt** — make guards mutually exclusive / add fitness pressure so
   genuine_routing=true. Falsifiable, cheap, deterministic. Highest signal.
2. **canary non-compare tail** — 5 count + 5 order + ~10 other → toward ~0.95.
   Mechanical (parser + guarded-scorer pair each), diminishing returns.
   NB `data/clean_canary_v01.json` has **no subtype field** — the 5/5/10 split is
   from prior analysis, not the data; re-derive before building.
3. **Commit the untracked pivot/role/run artifacts** so the arc is durable.
4. Bigger question: the whole arc's wins were structural, not evolutionary. Worth
   asking whether Branch C is now a hand-engineering loop wearing an evolution costume.

## 2026-06-27 — ARC TO 0.833, routable 1.0; fresh llm run live

Full writeup: `apollo/pivot/dispatch_arc_writeup_2026-06-27.md`. **max_acc 0.392 →
0.833; max_routable_acc → 1.000** (one organism fully solves cross_tier+inference+synth).

- **Lever 1 REVIVED (commit 48eb0102):** the "aggregate solves 0 synth" falsification was
  an instrumentation artifact — `score_by_aggregate__g` guarded on `quantities` (nothing
  writes it) instead of `counts` (what parse_box_items writes). Re-guarded on `counts` →
  synth 15→30, max_acc 0.708→0.833. LESSON: when a capability "fails," check the
  guard/slot/interface before believing the falsification.
- **Arc:** 0.392 (Run2) → 0.558 (dispatch) → 0.708 (boolean primitives + dispatch_merge)
  → 0.833 (aggregate guard fix). Each wall a distinct missing capability, never "longer."
- **Commits (main, not pushed):** 093f7d9d · 1b9597f0 · d6cba3e7 · 48eb0102 · 709c28f9.
- **LIVE: fresh llm dispatch run** `run_branch_c_dispatch_llm2/` (800 gens, ~22h, PID in
  evolve.pid=11092; Granite :8800 PID granite.pid=10488, Python312). Scoped to 800 (not
  3000) because deterministic converged by ~gen 400 and Granite barely contributes.
  Watch `max_acc` beating 0.833 + `dispatch_audit.genuine_routing`. If it just matches
  deterministic 0.833, conclusion = llm adds nothing here (kill, don't ride to 800).
- **Remaining (diminishing):** canary non-compare tail (5 count + 5 order + ~10 other →
  ~+20 canary, toward ~0.95) — each a small parser+guarded-scorer pair, same pattern.

## 2026-06-26 — LEVERS DONE: boolean primitives + dispatch_merge → max_acc 0.708

## 2026-06-26 — LEVERS DONE: boolean primitives + dispatch_merge → max_acc 0.708

Killed the flat llm run (gen 1377, plateaued at deterministic numbers since gen 9,
Granite barely used — 0.14 llm mutations/gen). Then worked the two levers
falsification-first:

- **Lever 1 ("aggregate sub-pipeline") FALSIFIED.** aggregate solves 0 synth. synth =
  15 nth_ranked (already routed by select_nth__g) + 15 two_stage_count (needs a COUNT
  branch, not aggregate; capped ~+9, guard-collision risk). Not pursued. `score_by_
  aggregate__g` rides decoratively (per-branch ablation: drops nothing).
- **Lever 2 (boolean primitives) DONE — commit d6cba3e7.** New `src/blackboard_ops_compare.py`:
  parse_comparison→score_by_comparison__g (Is X larger than Y → yes/no),
  parse_which_extreme→score_by_extreme_number__g (which is larger → pick number).
  New typed slots comparison/extreme_number. Construct-validated 20/20 compare canary.
- **`dispatch_merge` operator (the real enabler).** Body+guard UNION crossover (used in
  dispatch mode instead of single-suffix recombine). Single-step add_guard+insert
  couldn't co-locate a branch's PARSER + its guarded SCORER → decorative branches; merge
  brings both at once (same valley-crossing shape as the 2026-06-16 recombination
  finding). Wire: `--dispatch --crossover-frac 0.3`.
- **Result (deterministic 600 gens): max_acc 0.542 → 0.708 = portfolio coverage** — one
  organism now routes everything the archive solves (dispatch fully converged). canary
  10→30/50. Per-branch ablation = genuine routing on 4/5 branches (comparison +10,
  extreme +10, derivability +20, select_nth carries cross_tier+synth-nth+canary;
  aggregate decorative). Validation run: `run_branch_c_dispatch_lever2b/`.
- **Commits on main (not pushed):** 093f7d9d (dispatch wiring) · 1b9597f0 (llm mutator
  fix) · d6cba3e7 (lever 2 + dispatch_merge).
- **Remaining upside (diminishing):** count branch for synth two_stage_count (~+9, needs
  a collision-free guard on `counts`), remaining canary subtypes. Then a fresh
  `--mode llm --dispatch --crossover-frac 0.3` GPU run, judged on max_acc (now
  meaningful) + max_routable_acc. NOTE: prior llm run showed Granite barely contributes
  in this regime — consider whether the llm run is worth the GPU vs deterministic.

## 2026-06-22 — 0.558 wall DIAGNOSED (do this before relaunching)

The 0.558 plateau is **two stacked ceilings, neither is "run longer" and neither
implicates crossover.** Full writeup: `apollo/pivot/diagnose_0558_findings_2026-06-22.md`
(reproduce: `python apollo/scripts/diagnose_0558_wall.py`).

- **Ceiling 1 — measurement/organism-model.** `best_acc` scores ONE fixed-terminal
  linear pipeline against a heterogeneous 4-subset battery needing ≥3 terminals,
  so it *structurally* can't exceed ~0.56. The **archive-as-portfolio already
  covers synth 1.0 / inference 1.0 / cross_tier 1.0** (oracle coverage 0.758 vs
  single-best 0.558). The plateau was largely a metric artifact. Missing
  capability = **DISPATCH/routing** (the R3 step); the linear-pipeline/single-
  terminal organism model can't express it. (0.758 is an oracle upper bound — a
  real router must be learned.)
- **Ceiling 2 — canary substrate floor.** 29/50 canary tasks solved by ZERO
  organisms. No boolean-compare op + no yes/no terminal in the registry →
  comparison tasks inexpressible (H-express). Compounded by padded/truncated
  non-derivable answer strings in `data/clean_canary_v01.json` (H-eval data smell).

**Next steps (priority):** (1) re-instrument headline metric → oracle/portfolio
coverage + per-subset (~30 LOC); (2) **James architecture call**: routing/dispatch
primitive (one organism solves all) vs dispatched portfolio — the bottleneck moved
from search-operator to dispatch; (3) add boolean-compare op + yes/no terminal and
audit clean_canary_v01; (4) do NOT relaunch the long llm run as-is — it replateaus
at 0.558 against the same metric.

## 2026-06-22 — DISPATCH design teed up (awaiting Road A/B go)

Design doc: `apollo/pivot/dispatch_design_2026-06-22.md`. PoC (G1 PASSED):
`scripts/dispatch_poc.py`.

- **Dispatch is already expressible** via `BlackboardOp.precondition` + `on_fail=
  "skip"` — a pipeline of guarded scorers IS a dispatcher; no new control-flow op.
- **G1 validated:** a hand-built guarded multi-scorer organism scores **1.0** on a
  mixed inf+xt battery where the best single-terminal pipeline caps at **0.70**.
- **Goodhart surface found:** 20/40 tasks fire BOTH guards → naive version leans on
  tail-ordering, not real routing. Design closes it with mutually-exclusive guards
  + per-branch dataflow ablation + adversarial guard-robustness.
- **Recommended Road A** (dispatch primitive: guarded multi-scorer organisms; the
  R3 step) over Road B (separate learned router/portfolio). Cheaper, more
  falsifiable, evolves the capability rather than externalizing it.
- **On James's go:** build `dispatch_falsification.py` (G2 necessity + G3 A/B,
  deterministic/CPU-only) + guarded-scorer atoms + metric re-instrumentation, run
  the 5-seed A/B. Keep the production llm run parked until dispatch validated.

## 2026-06-24 — DISPATCH FALSIFICATION PASSED (G1-G4); wiring is next

Road A approved → built & ran `scripts/dispatch_falsification.py`. **All 4 gates
PASS.** Findings: `apollo/pivot/dispatch_falsification_findings_2026-06-24.md`;
artifact `pivot/dispatch_falsification_result_2026-06-23.json`.

- G1 dispatcher 1.00 (inf+xt) vs single-terminal ≤0.70. G2: 0/6000 single-terminal
  solve both. G3: control 0/5; treatment 5/5 — **`mutate_only` (no bespoke merge op)
  also 5/5 at gens [1,3,2,1,6]** → dispatch wiring is cheap, unlike crossover. G4:
  per-branch ablation = genuine routing (each guard load-bearing for exactly its
  type, zero cross-effect); surface-robust; no-branch type → abstains (fire-rate 0).
- **Caveats:** ingredients-seeded (specialists handed over, not de-novo); θ=0.70
  includes incidental coverage; 2-type battery only (real battery = 4 subsets, ≥3
  terminals — next scale-up); canary still needs a boolean primitive.
## 2026-06-24 — PRODUCTION DISPATCH LLM RUN LIVE (committed)

- **Committed:** `093f7d9d` (dispatch wiring) + `1b9597f0` (mutator guarded-scorer
  tolerance + crash-safe launcher) on main, NOT pushed.
- **Live run:** `run_branch_c_dispatch_llm/` — `run_dispatch_llm.py` → evolve gens=3000
  pop=24 mode=llm crossover=0.3 **dispatch=True**, seed 20260624, checkpoint-every 50.
  PID in `evolve.pid` (was 15144). **~112s/gen → ~4 days to gen 3000.** Granite up on
  :8800 (PID in `granite.pid`, was 13096, Python312 8-bit, 2.64GB VRAM).
- **CRITICAL ENV NOTE:** the server + run need **Python312**
  (`C:\Users\James\AppData\Local\Programs\Python\Python312\python.exe`) — it has
  torch 2.11+cu128 AND transformers 5.8.1. The default `python` (pythoncore-3.14) has
  torch but NOT transformers; launching the server with it crashes (ModuleNotFound).
- **Watch in `evolve_log.jsonl`:** `max_routable_acc` (honest headline, excl canary —
  deterministic hit 0.786; beat that = llm/Granite found richer dispatchers),
  `portfolio_coverage`, `n_dispatchers`, and `dispatch_audit.genuine_routing` (every
  10 gens). `crash.log` is written with flush on any death (no more blind deaths).
- **Restart if it dies:** bring Granite up (Python312, env LLM_ALT_MODEL_NAME=
  `.hf_cache\granite2b`, LLM_ALT_PORT=8800, LLM_ALT_LOAD_IN_8BIT=1), then
  `python312 scripts\run_dispatch_llm.py` via Start-Process (NOT shell-redirected).
- **Still owed (next levers):** aggregate sub-pipeline assembly (winner lacks
  parse_box_items → aggregate branch decorative), boolean primitive for canary,
  watch whether Granite mutation assembles genuine_routing dispatchers beyond the
  deterministic 0.786.

## 2026-06-24 — DISPATCH WIRED + BREAKS THE 0.558 CEILING (deterministic)

Wired into `src/blackboard_evolve.py` (behind `--dispatch`, UNCOMMITTED): guarded
scorer atoms (mutually-exclusive semantic-slot guards), `fitness()` relaxed to ≥1
scorer, `descriptor()` keyed on scorer-SET, `add_guard` mutation, dispatch-aware
seeds, and metrics: `portfolio_coverage`/per-subset/`max_acc`/in-loop `dispatch_audit`.

- **Deterministic 600-gen full-battery run: max_acc 0.558 → 0.683** (first break gen
  131, settled ~gen 500), portfolio coverage 0.742, per-subset inference 1.0 /
  cross_tier 1.0 / synth ~0.7 / canary 0.44. +0.125 = exactly the inference-routing
  payoff. Validation run: `run_branch_c_dispatch_smoke/` (checkpoint gen 600).
- **Honest caveats:** (1) had to add `max_acc` — `best_acc` is ccs-selected and hid
  the result; (2) 2-branch dispatchers only TIE 0.558 (guarded select_nth__g loses
  the unconditional select_nth's incidental synth/canary hits); needed 3-branch w/
  aggregate sub-pipeline; (3) winners mix plain+guarded scorers → some override-based
  routing, `genuine_routing` audit flag often False (no clean-routing fitness pressure
  yet); (4) archive inflation persists (1825 cells — trust max_acc/portfolio, not
  shape count); (5) canary still ~0.44 (needs boolean primitive); (6) deterministic
  only — production `--mode llm --dispatch` is the next GPU commitment.
- **NEXT:** decide whether to (a) launch the production `--mode llm --dispatch` run
  (watch max_acc>0.683 + genuine_routing emergence), (b) add clean-routing fitness
  pressure so guarded-only dispatchers win over plain+guarded hybrids, (c) add the
  boolean primitive for canary, and/or (d) commit the wiring. Findings:
  `apollo/pivot/dispatch_falsification_findings_2026-06-24.md`.

### (superseded plan — now done) NEXT BUILD was: wire guarded atoms + relax scorer
rule + add_guard + portfolio metric + G4 guards, then deterministic full-battery run.

This is the live "where we left off" doc. Read it, then the linked frontier docs,
then report state before acting.

---

## TL;DR of the current frontier

The **recombination (crossover) operator is validated, including in production
`--mode llm`.** That answered the Run 1/Run 2 question. Two things are now open:
1. The production run **died early at gen 443** (target was 3000) and needs
   relaunch/resume.
2. A **new plateau at `best_acc 0.558`** appeared right after crossover broke the
   old 0.392 plateau — that second wall is the next falsification target.

## The arc (how we got here)

- **Run 1 (gen 481) & Run 2 (gen 2668)** both flatlined at `best_acc 0.392`.
  Evolution kept the *seeded* cross-tier organism alive but never assembled a
  novel one. We fixed expressibility (tier-bridge op) and gradient (cross-tier
  canary) — necessary but **not sufficient**.
- **2026-06-16 falsification + A/B** (`apollo/pivot/recombination_findings_2026-06-16.md`):
  single-step mutation can't cross the multi-op fitness valley (0/8000 random
  walks; solver in neither 1-edit neighborhood). A one-point **crossover** can —
  de novo solver in **4/5 seeds** vs **0/5** single-step. The plateau was a
  **search-operator** failure, not substrate/eval. Wired `recombine()`,
  `--crossover-frac`, `--seed-variant ingredients`, per-gen `novel_multitier`
  signal into `apollo/src/blackboard_evolve.py`.
- **Production run launched 2026-06-16** (`apollo/run_branch_c_xover/`,
  `blackboard_evolve --gens 3000 --pop 24 --mode llm --crossover-frac 0.3
  --seed-variant default --checkpoint-every 50`, PID 20956, ~118s/gen).

## What the production run actually showed (logs read 2026-06-22)

- **Crossover broke the old plateau in production.** `best_acc 0.392 → 0.558 at
  gen 15`; `novel_multitier` climbed to **61** genuine de-novo cross-tier
  discoveries (first at gen 15, `cross_tier_acc 1.0`). This is exactly what Run 2
  never produced — the operator works end-to-end with Granite in the loop.
- **Process is DEAD.** Last log line is **gen 443** (~14h elapsed, written
  Jun 16 21:28). No python procs alive; PID 20956 gone. Stopped ~6 days ago, far
  short of 3000 gens. `console.log`/`.err` are **0 bytes** (background-redirect
  zeroing — see CHARTER hard rules), so cause of death is unrecorded. Last
  checkpoint: `run_branch_c_xover/checkpoints/branch_c_gen_000400.json`.
- **New plateau.** `best_acc` flat at 0.558 from gen 15 → 443.
- **Goodhart caveat persists.** 86 archive "cells"/"distinct shapes" are mostly
  duplicate-op variants of one canonical solver, not 86 inventions. Load-bearing-
  core archive key still doesn't collapse op-duplication (open instrumentation
  debt).

## Next levers (decide on resume — do NOT just run longer)

The 0.392 wall is down. The live question is the **0.558 wall**. Candidate moves:
1. **Diagnose the 0.558 plateau first** (falsification-first): is it an
   expressibility ceiling (substrate can't host the next-harder organism), an eval
   ceiling (battery doesn't reward it), or another operator gap? Don't assume —
   build the discriminating canary.
2. **Relaunch the production run** with a crash-resilient harness: resume from the
   gen-400 checkpoint, and capture console output via Python per-line flush (NOT
   shell redirect — that's why we have no death diagnostic).
3. **Fix the archive Goodhart hole** — collapse duplicate-op variants so
   `novel_multitier`/cell counts mean what they say before trusting them as a
   discovery signal.
4. **Smarter cut-point selection** for crossover (splice at type-compatible slot
   boundaries, not uniform) — the A/B had a 1/5 miss from random cuts.

## Resume mechanics

- **Granite LLM server** (needed for `--mode llm`): NOT running. Bring up on :8800
  via `apollo/src/llm_server_alt.py` with env
  `LLM_ALT_MODEL_NAME=D:/Prometheus/apollo/.hf_cache/granite2b`, `LLM_ALT_PORT=8800`
  (Granite-3.0-2B, ~2.7GB VRAM).
- **Substrate:** `apollo/src/blackboard.py`, `blackboard_evolve.py`,
  `blackboard_ops_r2.py` (R2 ops + `relations_from_facts` bridge).
- **Canaries / falsifications:** `apollo/scripts/{inference_canary,cross_tier_canary,
  r2_falsification,cross_tier_falsification,recombination_falsification,recombination_ab}.py`;
  results in `apollo/pivot/*_result_*.json`.

## Frontier docs to read (in order)

1. `D:\Prometheus\apollo\pivot\RESUME_apollo_2026-06-15.md` (prior resume)
2. `D:\Prometheus\apollo\pivot\recombination_findings_2026-06-16.md` (the finding)
3. `D:\Prometheus\apollo\pivot\r2_run1_findings_2026-06-10.md` (tier-bridge lesson)
4. Live logs: `D:\Prometheus\apollo\run_branch_c_xover\evolve_log.jsonl`,
   `novel_discovery.jsonl`, `checkpoints\branch_c_gen_000400.json`

## Memory anchors (auto-loaded; for cross-reference)

`project_apollo_recombination_validated_20260616`, `project_apollo_r2_falsification_20260609`,
`project_apollo_phase1_launched_20260529`, `project_apollo_blackboard_prototype_20260524`,
`project_reasoning_ladder_v01_20260524`, `feedback_failure_signature_doctrine`,
`feedback_background_output_capture`.

> The top-level `apollo/RESUME.md` is STALE (2026-05-15, pre-Branch C). Ignore it
> in favor of the `pivot/` docs and this file.
