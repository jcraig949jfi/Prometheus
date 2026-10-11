# Z80 Atlas as a third RSO engine: adapter contract and known-answer smoke test (C-016-T021)

Author: Cadmus[harry1-abbe9ede], claude-sonnet-5-5 (Q2), headless on harry1. Written 2026-10-11. Read-only against the
Z80 Atlas lane; no file under `archaeon/`, `prometheus/z80atlas/` or `roles/Archaeon/` was edited. No large experiment.

## 1. Verdict

**Compatible, with a different unit of observation from Ares and Ensorain.** Z80 Atlas has a native generation
boundary with provenance bookkeeping already built in, so the question "can the Observatory tell inheritance from
environmental reconstruction or seeded copying" has a concrete native form. The known-answer smoke test passes
(section 7). The contract below is for a later adapter packet; nothing here is an adapter.

What the engine does NOT give for free, in one line each: no checkpoint/resume of a running population (section 4),
no per-organism "lawful reference" below the planted programs in `tasks.py`, and a ~1e-5 lottery prior that random
founders are already exact self-copiers (section 5), which any heredity claim must be measured against.

## 2. Owner, pin, entry points

- **Two Z80 Atlas trees exist.** `archaeon/z80atlas/` (Archaeon, M2; byte VM, SplitMix64 from `proteus.foundry.prng`,
  engine with provenance) and `prometheus/z80atlas/` (older tree; `random.Random`, pickle-resumable `World`; last
  touched by Bellerophon[ubu005] for the BEL-48H repairs). This contract uses the **archaeon** tree: it has the
  generation boundary, the founder-origin provenance (DF-017) and the frozen positive controls. The prometheus tree is
  not assessed here beyond `rso/scale/CHECKPOINT_REPLAY_SURVEY.md` rows 22 and 86.
- **Owner:** Archaeon (`roles/Archaeon/`, last commit on the tree `863d34a55`, 2026-09-24). The lane is closed behind
  operator rulings 1-4 (`archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md`). Whether Archaeon is
  currently ACTIVE was not checked; a use of the engine beyond reading should be routed through Palamedes to that seat.
- **Pin:** `origin/main` = `f76db470c7ccde81e12005b6d8010078028823ae` (2026-10-11); `archaeon/z80atlas` last changed at
  `863d34a55`. Grammar digest recorded in the smoke result (`grammar_digest`); the scheduler itself refuses to run if it
  differs from `campaign/GRAMMAR_FROZEN.json` (`archaeon/z80atlas/CAMPAIGN_CONTRACT.md`).

| What | Entry point |
|---|---|
| Byte VM, one organism, one run | `archaeon/z80atlas/vm.py:27` `execute(tape, nbr, inputs, step_cap, copy_prim, energy, pc0, allow_nbr_write)`; returns `nbr_window`, `nbr_mask`, `writes_nbr`, `reads_nbr`, `exec_foreign`, `outputs`, `executed` (`vm.py:132-137`) |
| Address space | `vm.py` header: own tape `[0,G)`, neighbour window `[128,128+G)` (`vm.py:19` `NBR`), sandbox elsewhere |
| Spec factory | `archaeon/z80atlas/grammar.py:68` `make(...)`; frozen constants `grammar.py:33` `FROZEN` |
| One run = pure function of (spec, seed) | `archaeon/z80atlas/engine.py:159` `run(spec, seed)` |
| Generation boundary (ENDOGENOUS_COPY) | `engine.py:317-338`: parent executes with neighbour window; `copy_min_frac` 0.9 of window bytes must be written by the parent (`engine.py:319-324`); child = window + `copy_noise` (`engine.py:332`) |
| Birth bookkeeping and ancestry | `engine.py:216` `place(...)` (`anc`, `gen`, `lin`, `parent`) |
| Donor / reconstruction predicate | `engine.py:26` `donor_contributes(occupied, res, phys)` |
| Founder origin classes | `engine.py:17` `ORIGIN_RANDOM / ORIGIN_SEEDED / ORIGIN_TRANSPLANTED`; stamped at `engine.py:179-195` |
| Integrity halt | `engine.py:434` births == endogenous births or `AssertionError` |
| Neighbour-dependence probe | `engine.py:341-348` |
| Known planted programs | `archaeon/z80atlas/tasks.py:68` `WITNESS`, `:81` `replicator(copy_prim)`, `:90` `task_then_replicate` |
| Tasks, fresh cases | `tasks.py:41` `cases`, `:53` `score_case` |
| Positive controls | `grammar.py:229` `positive_controls`, `:241` `control_verdict` |
| Matched controls | `grammar.py:183` `matched_controls` (reproduction flipped endogenous <-> EXTERNAL; accessibility flips) |
| Transplants (same / physics / world / environment swap) | `scheduler.py:246-262` |

## 3. Generation-boundary semantics (what a "generation" is here)

- A parent is a byte string of length `G` (32 or 64). An organism's tape is executable and self-modifiable.
- Reproduction is endogenous where declared: a child exists only because the parent's own execution wrote bytes into the
  neighbour window (>= 90% of `G` for COPY/OVERWRITE/CONSTRUCTIVE/PAIR; >= 1 byte for PARTIAL, rest randomised by the
  RNG at `engine.py:326-330`). The runner never copies for it, and `run()` raises if a birth is runner-provided
  (`engine.py:434`). Under EXTERNAL physics the runner does the reproducing: that is the matched control, not heredity.
- Copy noise `FROZEN["copy_noise"]` = 0.004 per written byte plus background mutation 0.02 per organism per epoch.
- The child's tape is the window, so inheritance is byte-exact when the noise misses. The smoke test found that one
  flipped byte in the planted heritable program kills its function (seed 16_021_100, generation 3, fidelity .9688,
  child_solves 0.0). Fidelity and function are separate endpoints.
- "Function" is a task score: `score_case(task, outputs, inputs, params)`; fresh inputs per (run, epoch, cell).
- Reset and restart: one run is a pure function of (spec, seed) and writes nothing itself (`engine.py` header). There is
  no interrupt/resume of a population inside `run()`: state lives in locals of one function
  (`rso/scale/CHECKPOINT_REPLAY_SURVEY.md` row 4: "state in locals of `engine.py:159-251`", adapter cost M).
  Restart-from-seed is cheap and replay is verified (two PYTHONHASHSEED values, per the survey and per this packet's
  smoke). A "reset" control is therefore a re-run from the same seed, or a transplant of final tapes into a fresh world
  (`scheduler.py:246`), not a checkpoint.

## 4. What the three controls look like natively

The question to PREPARE: can a heritable computational structure transmit a functional capability across generations,
and can the Observatory tell inheritance from environmental reconstruction or seeded copying?

| Alternative | Native signature | Where it is already measured |
|---|---|---|
| **Inheritance** (the claim) | child bytes written by the parent's own execution; window fraction >= .9; `donor_contributes` False; child solves the task; the child reproduces in turn (>= 2 generations) | `place()` ancestry; `vm.execute` fields; smoke `H` |
| **Environmental reconstruction** | the function is in the neighbour or previous occupant, not in the parent: parent reads/executes neighbour memory (`reads_nbr`, `exec_foreign` > 0) or leaves window bytes unwritten and kept (`donor_contributes` True); competence collapses with a zeroed neighbour | `engine.py:26`, `:341-348` (`dependence`); smoke `ENV` |
| **Seeded copying** | founder stamped `seeded_replicator` or `transplanted_lineage`; every descendant carries that founder in `anc`; counted in `births_endo_inserted`, never in `spontaneous_replication` | `engine.py:17,179-195,216`; smoke `engine_seeded` vs `engine_random` |
| **Non-heritable competence** | function present, `writes_nbr` == 0, no child | smoke `NH` |
| **Partial / constructed transmission** | a program that writes only a short function into the window is refused by `copy_min_frac` under ENDOGENOUS_COPY (it would pass under ENDOGENOUS_PARTIAL with the remaining bytes randomised, a different physics) | smoke `CON` (window_frac 0.0938 for 3 of 32 bytes) |
| **Lottery** (the control the engine needs and the Observatory must not drop) | random 32-byte vmcopy tapes are exact self-copiers at 9.6e-6, 99% input-gated, 85% only when the input byte is 128 (`archaeon/z80atlas/census/RESULTS.json`, `pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md` s0) | Archaeon's COPIER-CENSUS-01, preregistered |

The census result is the reason "heredity was observed" is not by itself a finding here: the prior of a random founder
already being a copier is small but nonzero, and the 72 h campaign's one clean replicating world was consistent with it.
An Observatory run must compare against the census prior or against the matched EXTERNAL-reproduction arm.

## 5. Which registry entries apply (`python -m rso.registry.registry for-adapter`)

| Entry | Applies? | Scope limit hit |
|---|---|---|
| exec-binding | yes | flat inventories only (P-FLAT): one run = one node, no nesting. A population run with transplant children is nested lineage and needs its own check. |
| custody-keeper | yes | bytes, not truth. Register the pinned engine files and each run's JSON. |
| mutation-runner | yes for the adapter and any detector code | CHALLENGED; it cannot tell a behavioural kill from a freeze-hash kill. The smoke's `H_broken` is a hand-made mutant, not a mutation-runner run. |
| receipt-canonical | yes, with encoding | refuses floats. Fidelity, scores and telemetry are floats; encode as integer counts or fixed-point strings. Births, generations, window-byte counts are ints. |
| budget-ledger | yes | declared estimates only. The smoke is <1 s. |
| witness-driver-ares | pattern only | imports Ares; names multi-boundary and cross-episode designs outside its scope. A population with a generation boundary is such a design. |
| ruler-binary-retention | NO | the endpoint is not a binary retained bit with a chance bound; lineage observations are dependent. Do not reuse its authority here. |
| stratified-holm-analysis | partly | binary counts per stratum (e.g. "lineage reached generation >= k", per world stratum) fit; CHALLENGED; `analyze.py` trusts the runner's `discovery` field and this engine's provenance flags would need re-deriving from bytes, not trusted. |

New scope limits found by this packet, to add to `not_qualified_for` when an adapter lands: no registry entry covers a
population with a generation boundary; the ruler assumes independent observations and lineages are not.

## 6. Resource and replay facts relevant to an adapter

- Replay: `engine.run(spec, seed)` reproduced byte-identically under two PYTHONHASHSEED values
  (survey row 68 and this packet: `cmp` identical for hash seeds default and 77).
- Cost: the two 60-epoch, N = 64 `run()` calls inside the smoke take well under one second together. The
  72 h campaign was 24 workers (`CAMPAIGN_CONTRACT.md`); nothing here approaches that.
- The campaign evidence bundle (13.75 GB, outside the repo, sha256-manifested) was not touched.

## 7. Known-answer smoke test

`rso/z80/smoke/smoke_heredity.py`; result `rso/z80/smoke/smoke_result.json`. Command from the repo root, one process:

    python -m rso.z80.smoke.smoke_heredity rso/z80/smoke/smoke_result.json

Result on harry1 (Python 3.12.10): ALL_PASS, 11 checks, exit 0, output sha256 prefix `7529dd6a03398275`. Re-run: byte-identical
file; also byte-identical under `PYTHONHASHSEED=77`. Checks (all known answers, no randomness except SplitMix64 seeds
16_021_001 and 16_021_100 fixed in the file):

| Check | Known answer |
|---|---|
| `H_born_each_generation`, `H_function_transmitted`, `H_exact_copy_without_noise` | the planted `task_then_replicate(ECHO_forced)` writes 32/32 bytes, the child equals the parent, and it solves ECHO and reproduces for 3 generations |
| `H_noise_run_born_and_exact_copies_function_ok` | with frozen copy noise every child is born at fidelity >= .9, and every exact copy carries the function; generation 3 lost one byte and the function (recorded) |
| `H_no_donor_material` | `donor_contributes` False for the heritable parent |
| `NH_no_child` | the same function without a replicator writes 0 bytes, no child |
| `CON_refused_by_copy_min_frac` | a 3-byte constructor reaches window fraction .094 < .9: no ENDOGENOUS_COPY birth |
| `ENV_function_is_environmental` | `JP 128` with an ECHO program in the neighbour: scores 1.0 with the live neighbour and below .5 with a zero neighbour, writes nothing, `donor_contributes` True |
| `detector_sensitive_to_broken_copy` | corrupting the copy-loop offset byte makes the detector say not heritable (the check can fail) |
| `seeded_run_is_inserted_not_clean` | `engine.run` with `init=seeded_replicator`: 3443 endogenous births, all inserted-ancestry, 0 clean, `spontaneous_replication` False, `inserted_lineage_replication` True |
| `random_run_has_no_replication` | `engine.run` with `init=random`, same size and seed: 0 endogenous births |

Honest limits of the smoke test:

- The planted programs are mine, built from `tasks.py` pieces. The test shows that the detector reads the engine's own
  fields correctly on programs with known behaviour. It does not show that the detector is right on evolved organisms.
- The VM-level boundary replays the `ENDOGENOUS_COPY` gate by hand (`copy_min_frac`, `copy_noise`) instead of calling
  a function, because `run()` has no callable for one boundary. If `engine.py:317-338` changes, the smoke test must be
  re-derived; the custody-keeper registration of `engine.py` would flag it.
- `engine_seeded` and `engine_random` are one seed each (16_021_001), 60 epochs, N = 64. They check the provenance
  fields, not a rate.
- ENV uses one environmental-dependence mechanism (executing neighbour code). Reconstruction through `SEAL` snapshots
  or through unwritten kept bytes is covered only by `donor_contributes` reading its inputs, not by a constructed case.
- I did not run `positive_controls()` through `control_verdict` (`grammar.py:229,241`); those are the engine's own
  positive controls and need full-length runs.

## 8. Recommended next step (for an adapter packet, not done here)

1. Treat one `run(spec, seed)` as the observation unit and the generation boundary as the object; extend the exec-binding
   inventory so each run is a flat node and transplants are separate launches with `from_run` recorded.
2. Endpoint: per-lineage generation depth with function present, at integer resolution, against both the matched
   EXTERNAL arm and the census prior (section 4).
3. Reproduce `matched_controls` and the transplant arms (`scheduler.py:246-262`) before any claim; they are what separates
   inheritance from reconstruction at population level.
4. Ask Archaeon whether a callable single-boundary function can be exposed, so the smoke does not replay the gate by hand.
