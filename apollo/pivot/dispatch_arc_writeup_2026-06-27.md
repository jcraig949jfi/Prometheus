# Apollo Branch C — the dispatch arc: 0.392 → 0.833, each wall a different missing capability

> **From:** Apollo (M2, Branch C) · **Date:** 2026-06-27
> **Scope:** the full journey from the Run 2 plateau through dispatch + 3 levers.
> **Doctrine:** every ceiling was a *capability* gap exposed by falsification — never
> "run longer." Each was diagnosed, the fix construct-validated before wiring, and the
> result reported as a failure-shape, not a verdict-line.

## Headline

`max_acc` (best single organism, full 120-task battery): **0.392 → 0.833.**
`max_routable_acc` (excl. canary's no-boolean tail): **0.657 → 1.000** — one evolved
organism now fully solves cross_tier + inference + synth. The remaining 0.167 is
canary's non-compare subtypes (count/order/other), a known primitive gap.

## The wall sequence (each a distinct bottleneck)

| stage | max_acc | wall that fell | the fix |
|---|---|---|---|
| Run 2 (gen 2668) | 0.392 | search operator | crossover (2026-06-16) |
| post-crossover | 0.558 | organism model (one fixed terminal) | DISPATCH: guarded multi-scorer routing |
| dispatch wired | 0.708 | branch assembly (parser+scorer co-location) | `dispatch_merge` (body+guard union) |
| + boolean lever | 0.708→0.833 | two missing/mis-guarded branches | boolean primitives + aggregate guard fix |

Each plateau looked like the previous fix had failed. It hadn't — the bottleneck had
*moved* to the next missing capability. Naming the new wall, not re-running the old
fix, is what advanced it.

## What each fix actually was

1. **Dispatch (commit 093f7d9d).** `best_acc` tracked one fixed-terminal pipeline against
   a battery needing ≥3 terminals — a measurement/organism-model ceiling. Guarded
   scorers (mutually-exclusive preconditions on semantic slots) let one organism route.
   Falsification G1–G4 passed (`dispatch_falsification.py`). Broke 0.392→0.558.

2. **Clean-routing pressure (093f7d9d).** Guarded-only mutation pool + ccs=0 for
   plain+guarded hybrids. Stripped Goodhart: archive 1825→188 cells; revealed the honest
   number (the old 0.558 was partly canary *guessing* via unconditional scorers, which
   the clean router correctly abstains from). Added `max_routable_acc` as the honest
   headline.

3. **`dispatch_merge` (commit d6cba3e7).** Wiring new branches exposed the recurring
   valley: single-step add_guard+insert adds a guarded SCORER without its PARSER
   transformer → the branch is decorative (its slot is never written). A body+guard
   *union* crossover co-locates both in one move (same shape as the 2026-06-16
   recombination finding). This was the actual enabler for every multi-branch lift.

4. **Boolean primitives (d6cba3e7).** canary's 20 compare/bool tasks had no solver.
   Two transformer+scorer pairs — `parse_comparison`→`score_by_comparison__g` (yes/no)
   and `parse_which_extreme`→`score_by_extreme_number__g` (which-larger). Construct-
   validated 20/20. With dispatch_merge: canary 10→30, max_acc 0.558→0.708.

5. **Aggregate guard fix (commit 48eb0102).** The aggregate branch keyed its guard on
   `quantities` — a slot NOTHING writes (the pipeline writes `counts`/`max_value`). So it
   never fired, was always decorative, and produced a **spurious lever-1 falsification**
   ("aggregate solves 0 synth"). The plain pipeline solves 15/15 two_stage_count.
   Re-guarding on `counts` lifted synth 15→30, max_acc 0.708→0.833, routable→1.000.

## Failure-shapes worth keeping (per doctrine)

- **Decorative branches are the dominant failure mode of dispatch.** A guarded scorer
  whose slot is never written contributes nothing but inflates the genome. Two separate
  instances (compare branch missing its parser; aggregate branch mis-guarded). Per-branch
  ablation is the detector; `dispatch_merge` + correct guard slots are the fixes.
- **A falsification can be an instrumentation artifact.** "Aggregate solves 0 synth" was
  real *as measured* but wrong *as a claim* — the guarded scorer I tested had the wrong
  guard slot. Lesson: when a capability "fails," check the harness (guard/slot/interface)
  before concluding the capability is absent. (Cf. Icarus interface-wall lessons.)
- **`best_acc` hid the result twice** (ccs-selected; and canary-guessing inflation).
  `max_acc` + `max_routable_acc` are the trustworthy headlines; archive cell counts are
  NOT (padding inflation persists).
- **The LLM barely contributed** in the production run (0.14 Granite mutations/gen; flat
  at deterministic numbers from gen 9). The wins were structural (operators + primitives
  + guards), discoverable by deterministic search. Open question whether `--mode llm`
  earns its GPU here.

## Current state (deterministic, validated)

Best single organism = 5-branch dispatcher solving canary 30/50, synth 30/30,
inference 20/20, cross_tier 20/20 = **100/120 = 0.833**; `max_routable_acc` = 1.000.
Genuine routing per per-branch ablation. Validation runs: `run_branch_c_dispatch_lever1fix/`.

Commits (main, not pushed): 093f7d9d · 1b9597f0 · d6cba3e7 · 48eb0102.

## Remaining upside (diminishing)

- canary non-compare tail: 5 count + 5 order + ~10 "other" subtypes (≈+20 canary →
  full-battery toward ~0.95). Each needs a small parser+guarded-scorer pair, same
  pattern. Order subtype may already be served by select_nth__g.
- A fresh `--mode llm --dispatch --crossover-frac 0.3` run to see whether Granite
  mutation discovers anything beyond deterministic (low prior, per the LLM-contribution
  finding) — judged on `max_acc` (now meaningful) + `max_routable_acc`.

## Reproduce

`cd apollo/src && python blackboard_evolve.py --gens 800 --pop 24 --dispatch
--crossover-frac 0.3` → watch `max_acc`/`max_routable_acc`/`portfolio_coverage` in
`run_branch_c/evolve_log.jsonl`.
