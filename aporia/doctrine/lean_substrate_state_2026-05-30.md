# Lean interaction substrate — state as of 2026-05-30

**Filed:** 2026-05-30
**Owner:** Ergon
**Scope:** Honest current state of the Lean-interaction substrate, what it
buys us, what it does not yet buy us, what was committed (and what is still
work-in-flight outside this repo).

## TL;DR (committed in `d576dc98` on 2026-05-29)

Three layers + a Mathlib bridge, 36/36 tests green on a Windows host:

- **Layer 0** at `agents/_shared/external_tools/subprocess_session.py`:
  generic stateful JSON-over-stdio subprocess client.
- **Layer 1** at `agents/_shared/external_tools/lean_runtime/`: typed Lean
  client over `lake exe repl` (typed inputs/outputs, env- and proof-state
  threading, graceful crash surfacing as `SessionCrashed`).
- **Layer 2** at `agents/_shared/proof_search/`: proof-system-agnostic BFS
  engine with pluggable `CandidateGenerator` and `Scorer`, plus a
  `LeanProofSystem` adapter and a `walk_1_bridge` for record parsing.
- **Mathlib bridge** at `external_deps/mathlib_repl/`: thin Lake project that
  declares path-deps on `repl` + `mathlib4`. From this directory,
  `lake exe repl` brings up a REPL with all of Mathlib importable.

End-to-end demonstration: the engine drives a search through a Mathlib-using
proof (`([1,2,3] : List Nat).length = 3`) and closes it from a candidate pool.
Cold Mathlib import ≈ 5 minutes; warm import ≈ 15-20 s.

## What this substrate actually buys us (behaviour deltas)

- **Walk-Z BFS becomes runnable end-to-end on this machine.** Before this
  work, the BFS-utility test of the 4 trained heads (PRM v0, GBT next-macro,
  GBT sibling-ranker, per-kind Ridge) was blocked on having any Python-driven
  Lean client at all. It is no longer blocked on that.
- **Cross-agent reuse is real, not aspirational.** The next agent that needs
  to talk to Isabelle, Coq, Z3, or any line-oriented JSON tool inherits
  Layer 0 and most of Layer 2 unchanged, and replaces one
  `LeanProofSystem`-shaped adapter.
- **Three Windows-specific failure modes are permanently retired.** UTF-8
  pipe corruption on Lean's `∀ ∃ → λ`, cmd.exe-wrapper-only `Popen.kill()`
  that orphans `lake.exe → repl.exe`, and `shell=True` mangling of `python.exe`
  stdin all have explicit test-coverage and explicit fixes baked into Layer 0.
  Every future agent on Windows inherits these without having to debug them.

## What this substrate does NOT yet buy us

I want to be flat about this, because the gap between "substrate exists" and
"Walk-Z hypothesis tested" is load-bearing.

- **It does not yet run a single real walk_1 theorem end-to-end.** A walk_1
  record names a theorem in Mathlib (e.g. `Quiver.Path.toList_injective`)
  but does not include the *type-string* of the theorem. To re-enter the
  initial proof state inside `lake exe repl`, we need that type-string. Two
  routes were proposed (`#check` introspection vs a Lean-side helper); neither
  is built.
- **The four trained heads are not yet wired as `Scorer` callables.** The
  engine has a `Scorer` slot, and `test_02b_scorer_routes_to_efficient_proof`
  proves the slot works against a mock score function. The actual model
  artifacts (PRM v0 Ridge, GBT classifiers, per-kind Ridge) still live in
  `ergon/daedalus/walk_z/z2_model/` and `z3_training/` as pickled / json
  artifacts and have never been imported into the `proof_search` package.
- **No session pool.** Every test that touches Mathlib pays the ~5-minute
  cold-import cost. Running BFS over 50+ walk_1 theorems sequentially in
  the current architecture would mean 50× cold imports — unacceptable.
- **No AutoLeanServer watchdog.** Crashes surface cleanly as `SessionCrashed`
  but the engine just returns; it does not auto-restart and resume. Long
  batch runs would die on the first crash.
- **Candidate-generation strategy is unsettled.** The walk_1 bridge can emit
  `[winning_tactic] + [counterfactual_siblings]` per step (≈ 4 candidates),
  but the engine currently has no logic for "which subset of the cross-step
  pool is valid at which node." A simple "try every tactic at every node"
  works for unit tests; for 50+ multi-step proofs it would explode.

## Cross-pollination feedback in flight (not absorbed)

While I was AFK, Moros (`charon/agents/moros/daemon.py`) auto-ran adversarial
frontier-LLM critique on the doctrine doc. Two artifacts:

- `pivot/feedback_external_tool_interaction_primitives_2026-05-28_2026-05-28.md`
- `pivot/meta_analysis_external_tool_interaction_primitives_2026-05-28_2026-05-28.md`

Per `feedback_llm_convergence_is_gravity_amplifier`, frontier convergence
on a critique is a warning signal that the framing matches their training
corpus, not validation that the critique is right. I have not pulled
anything from those artifacts into the substrate. They are notes to be
re-read with skepticism alongside the next-steps doc, not directives.

## Repo state

- Branch: `main`, up to date with `origin/main` as of the last
  `pull --rebase` from Techne's auto-commit loop (HEAD = `d576dc98` for
  the substrate commit; Techne has continued firing on top of it).
- Tracked: substrate source, doctrine, scripts, bridge `lakefile.toml`
  + `lean-toolchain`.
- Gitignored: `external_deps/repl/` (cloned), `external_deps/mathlib4/`
  (cloned), `external_deps/mathlib_repl/.lake/` (build outputs),
  `external_deps/mathlib_repl/lake-manifest.json`.
- Reproducibility: `scripts/build_lean_repl.bat` and
  `scripts/build_mathlib_repl.bat` rebuild both clones from scratch.
- Out of scope for the substrate but worth noting: Techne's auto-loop
  has continued through Fire #233+ while this work was happening, ~360M
  lifetime kills, 89 consecutive 0-promoted at last check.

— Ergon, 2026-05-30
