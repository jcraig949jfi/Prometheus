# Checkpoint / replay survey of native runtimes (C-013-T021)

Author: Cadmus[harry1-ec004941], claude-sonnet-5-5, 2026-10-10. Base: origin/main 9b1893d6f.
Method: code inspection (two read-only inspection passes, key citations re-spot-checked by Cadmus) plus tiny smoke
runs (<60 s, one process at a time, outputs in a temp dir outside the repo). No engine file or charter was changed.
Line numbers are at base 9b1893d6f and may drift by a few lines; paths are repo-relative.

Smoke environment on harry1: torch, sklearn and numba are NOT installed in the default interpreter, so Ananke,
Tyche and wm_mini were not run. "Verified" means a smoke run on harry1; "by design" means code reading only.
Theseus synth and Primordial were not run (cost / Redis dependence). Nothing here is a claim about GPU paths.

## 1. Survey table

Save/restore = can full state INCLUDING RNG be saved and restored today. "Easy" = no code exists, but state is
enumerable and an RNG state is exposed (a small change in the engine owner's code, not a redesign).

| Runtime | Loop (entry) | RNG | Full save/restore today | Replay deterministic from seed | Granularity / size | Main blocker |
|---|---|---|---|---|---|---|
| Ares | `ares/search.py:211` GA, loop :235 | one `np.random.default_rng(seed)` :219; state readable, never saved | N (easy). Job-level resume only (`ares/sweep.py:43-58`) | **Y, verified** (same hash twice, P=16 G=6, 11 s) | per generation; ~0.44 MB at P=128 plus ancestry/snaps that grow with G | all state is locals of one function; ancestry/snaps must be serialised |
| Ensorain | life `ensorain/e0/life.py:28`; GA `e0/evolve.py:79`; jobs `e0/arms.py:90-110` | many numpy Generators, seeds derived arithmetically (`arms.py:96`, `memories.py:250`, `world.py:20,43,52`); none saved | N. Only jsonl result rows (`arms.py:103-110`) | **Y per life, verified** (TT_TUNED, horizon 300, equal except `secs`); **full GA unknown** (not run) | life: small (TT cores + replay buffer); GA: ~32 genome dicts | no save code; GA state in locals; re-running a generation appends duplicate rows (`evolve.py:65-77`). `memories.audit` (:30-44) enumerates persistent attrs |
| Ananke / PTE | world `prometheus/ananke/engine.py:107`; GA `search.py:81`; cells `campaign.py` | world: stateless counter hash `rng.py:1-62` (only `ws` and tick `t`); GA: numpy Generator `search.py:84`, not saved | **partial**: `World.checkpoint()/restore()` (`engine.py:247-268`, in-memory dict, tensors + t/ws/genome); GA not; campaign resumes by cell (`campaign.py:195-240`) | **Y by design (integer-only; GPU/CPU/oracle bit agreement claimed `rng.py:3-5`); not run here** | world: per tick, tens of KB per world (Msum largest); GA pop ~23 KB; campaign: per cell | checkpoint is a CPU dict not a file; GA RNG not captured; conformance test `tests/test_conformance.py:118-129` skipped without CUDA; no torch on harry1 |
| z80atlas (`prometheus/z80atlas`) | `world.py:939` `run()`, `step():440` | 4+ `random.Random` (`world.py:162,174,867`, `tasks.py:90`, `coupling.py:50`) | **Y via pickle, verified** (tick-20 pickle 70,914 B; resumed == uninterrupted at tick 40; all rng states matched). No file save/load code; campaign resume per run (`scheduler.py:46-70`) | **Y, verified** (two PYTHONHASHSEED values) | per tick; ~71 KB at tick 20, grows with telemetry lists/lineage dicts | only a missing save/load wrapper; telemetry growth |
| z80atlas (`archaeon/z80atlas`) | `engine.py:159` `run()`, epoch loop :243 | single `SplitMix64` one-u64 state (`proteus/foundry/prng.py`), seeded by sha256 `seed_from` (`engine.py:161`) | N (easy). Job-level resume (`scheduler.py:386-397`) | **Y, verified** (two PYTHONHASHSEED values) | per epoch; small | dozens of locals incl. frozenset ancestry and the `World` env object (`engine.py:43`, holds its own rng) |
| SFE (`SerendipityFoundry/SerendipityFoundryEngine/sfe`) | ledger service, not an evolutionary loop | executors seed via sha256 (`executors.py:144`); one executor deliberately uses `os.urandom` (:425-434) | ledger checkpoint only: event index + head hash + table counts (`runtime.py:3447-3475`). Its own status file: "a world cannot yet be re-run from a checkpoint" | per executor (declared) | n/a | no simulation state exists to restore |
| Proteus (`proteus/foundry`) | pure VM `vm.py` `Player.run_tick`; no population loop | `SplitMix64`, caller-owned (`vm.py:155`) | **Y at organism level**: `lineage.checkpoint/restore` (`lineage.py:60-78`) -- but it does NOT include the caller's rng or Meter | **Y, verified** (checkpoint at tick 3 + manual rng restore matched original at every tick) | per tick per organism; tape <=256 words (few KB) | no world/population state or loop; checkpoint is sufficient only if the caller also saves `rng.state` |
| Tyche | `tyche/run_v0.py` loop :280-365 (v1/v2 `v1/run_v1.py`, `v2/run_v2.py`) | numpy Generator `run_v0.py:206`, `[world_seed, seed]` in v1/v2; sha256 lens ids | N. `passd_resume.py` rebuilds Pass-D inputs from committed logs only (lower bound, its own docstring :9-12) | **unknown, not run** (sklearn missing). v0 truncates on wall clock (`run_v0.py:361-365`); v1/v2 use unit budgets | per generation; large `cache`/`meta` | locals/closures in one `main()`; v0 wall-clock cap must become a counter; sklearn version float sensitivity |
| Crius | outer `crius/search.py:306`; lifetime `evaluate.py:142` | `random.Random` from string/tuple seeds (`search.py:261`, `evaluate.py:137`) | N. `Workspace.snapshot/restore` (`workspace.py:92,106`) and `BlockStore.snapshot/restore` (`artifacts.py:91,97`) exist for causal controls but the BlockStore snapshot omits invocations/edges/events/cost counters; no rng, population or `seen` saved | **Y, verified** (`candidates.jsonl` byte-identical over two 14 s runs) | per outer iteration (mu=8, lam=24); few KB population | ~200-line function with local state; pool rebuilt per call |
| Theseus synth | `theseus/synth/run_v0.py:341` generation loop | master numpy Generator :250; `Field.rng` (`ecology.py:44`); sha256-seeded collisions (`collide.py:48-49,121`) | N. No pickle/`bit_generator.state` anywhere in `theseus/synth` (grep) | **Y by design, not run**: set iteration explicitly sorted (`ecology.py:65,79`), BLAS pinned (`run_v0.py:36-38`) | per generation; state size not measured | state spread over `reg`, `active` set (:283), `tensor`, `field`, `archive`, ... in a ~700-line `main`; wall-clock guards (`run_v0.py:64,342`) can truncate |
| Theseus daemon | `theseus/daemon.py` | `time.time()` default seed (:631), uuid4 batch ids (:67-69) | N | **N** (wall-clock budget :206, time seeds) | wall-clock batch | non-deterministic by construction; not a replay target |
| Primordial | many runners; best candidate `primordial/metric/baseline.py` QD loop :101 | PCG64 mutation rng + archive sampler `arch.srng` (`archive.py:123`) | **partial**: pause state stores both `bit_generator.state` + gen counter every 25 gens (`baseline.py:50,96-105`); elite archive lives in Redis `pm:qd:<run>:c:*` (`archive.py:122`), not in the state dict; `save/restore_elites` (`archive.py:193,216`); job checkpoints `fabric/worker.py:271-295` | **Y only when sampler seeded** (`baseline.py` seeds it; `qd/e4_run.py:126` and e1/e2/e10 runners use `UNSEEDED`, `archive.py:103`) | per 25 generations; genome bytes per occupied cell (not measured) | needs Redis on 127.0.0.1:6390; hard-coded `C:/Users/jcrai/lab/pm-data/ckpt` unless `PM_CKPT_DIR`; resume refuses on code sha change. Not run |
| Aether | kernel `Aether/test/reference/gpu_aeth01.py` `gpu_step`; drivers `observatory/aeth01_run.py:116`, `aeth02_falsifiers.py:85` | counter-based splitmix of (seed, tick, pos, field) (`gpu_aeth01.py:86-106`): no RNG state; initial state from `default_rng` rebuilt from recipe (`aeth01_run.py:50,138`) | **Y, trivially**: state = 5 uint8 fields + seed + tick; resume params exist (`tick0` `aeth01_run.py:118`, `start_tick` `aeth02_falsifiers.py:86`) | **Y, verified** | per tick; 5*H*W bytes (20 KiB at 64^2, ~20 MiB at 2048^2) | none for the kernel. Orchestration (`aeth01_scale_orchestrate.py:355`) is separate; CuPy/GPU path not checked |
| p1_slice wm_mini | `docs/phase3/design/FABLE-5.1/prototype/p1_slice/reach.py:93-137` `search_lineage`; kernels `wm_mini.py` | none stateful: `khash` (`wm_mini.py:68`) of (seed, life, a, b); search hash indexed by loop counter | N, but **trivially resumable**: complete state = `(parent, fp, i)` per lineage | **Y by construction** (integer-only; `prange` writes per-lineage slots). Not run: numba missing | per proposal; n*4*8 bytes per lineage | the 200,000-step budget runs inside one `@njit` call (no mid-call checkpoint without splitting the loop); `cache=True` kernels write `__pycache__` into the repo unless `NUMBA_CACHE_DIR` set |

## 2. Findings

1. **Replay is the strong property; state capture is the weak one.** Every runtime that was run twice (Ares,
   Ensorain life, both z80atlas, Proteus, Crius, Aether) replayed identically from its seed. Only Aether (trivially),
   prometheus z80atlas (unmodified pickle) and Proteus (organism level, caller saves rng) can be checkpointed today
   without engine edits; only Ananke's World has first-party checkpoint code (in-memory; its test is skipped on CPU).
2. **Seed replay substitutes for checkpointing for short runs, not long ones.** Where a run is minutes (Ares,
   Ensorain life, z80atlas, Crius smoke) restart-from-seed is cheap. It fails the long-duration case (Theseus 4 h
   guard, Tyche v0 core-hour cap, Primordial pause/resume, multi-day z80atlas campaigns) -- the case the long-run
   execution architecture needs.
3. **Three RNG families, three adapter answers.** (a) Counter-based / stateless (Ananke world, Aether, wm_mini):
   checkpoint = arrays + tick; no RNG to save. (b) One-integer SplitMix64 (archaeon z80atlas, Proteus): trivially
   capturable; the caller must save it. (c) numpy Generator / `random.Random` (Ares, Ensorain, Tyche, Theseus, Crius,
   prometheus z80atlas): state readable (`bit_generator.state`, `getstate()`), but no engine calls it.
4. **Common blocker: state in locals of one large function** (Ares, Tyche, Theseus, Crius, archaeon z80atlas,
   Ensorain GA, wm_mini jit call). Under the rule that native runtimes keep their own state and semantics
   (roles/Cadmus/RESPONSIBILITIES.md s6), the adapter should not restructure these. Recommendation: use seed+budget
   replay as the RSO contract for short runs, and require a `save_state()/load_state()` pair (owned by the engine
   owner) only for engines onboarded for long runs.
5. **Wall-clock termination breaks exact replay** (Tyche v0 `run_v0.py:361-365`, Theseus guards, Ananke wave budget
   `campaign.py:831`): the budget must be a counter recorded in the receipt, and wall-clock fields excluded from digests.
6. **Receipts differ across identical replays** in non-scientific fields (Ares `elapsed_s`/receipt git sha +
   timestamp, Ensorain `secs`, Crius `elapsed_s`). A replay-equality check must hash a declared canonical subset.
7. **Unverified, explicitly:** Ananke replay and checkpoint equality (no torch here); Tyche, Theseus synth and wm_mini
   replay (not run); Ensorain full-GA replay; Primordial anything. Verifying them needs a host with torch / sklearn /
   numba / Redis (not harry1, which is thermally limited). These are NOT claimed.

## 3. Smoke runs performed (all outside the repo)

| Runtime | What was run | Result |
|---|---|---|
| Ares | `search.run("W1","present",Config(),P=16,G=6,eps=2,seed=1,log_every=2)` twice, JSON hash minus `elapsed_s`/`receipt` | identical, 11 s |
| Ensorain | `arms.run_one` TT_TUNED cap 1024 class_seed 1 inst_seed 1005 org_seed 3 horizon 300 energy0 1000, twice | equal except `secs` (first attempt with default energy died at step 20: uninformative) |
| z80atlas (prometheus) | `World(Config(ticks=40),1).run()` x2 under PYTHONHASHSEED 0 and 123; step 20, pickle, unpickle, step 20 more vs uninterrupted 40 | identical; pickle resume == uninterrupted; 3 rng states matched |
| z80atlas (archaeon) | `engine.run(positive_controls("early")[0], seed 1)` twice, PYTHONHASHSEED 5 and 77 | identical hash |
| Proteus | `generate(n=20)` twice; 6 ticks each with `SplitMix64(9)`; checkpoint at tick 3, restore + set rng manually | identical at every tick |
| Crius | `crius.search.run_search(... mu=4, lam=6 ...)` twice, ~14 s each | `candidates.jsonl` byte-identical (sha256 8e08344b...) |
| Aether | `F.run(64,30)` twice; `F.run(64,15)` then `F.run(64,15,fields=...,start_tick=16)` | digest 9618995400aec8c6... equal for all three (incl. split run) |
| Ananke, Tyche, wm_mini | attempted | **not run**: torch / sklearn / numba absent |
| Theseus, Primordial | not attempted | cost / Redis / writes to repo-relative or fixed dirs |

## 4. Next native runtimes for onboarding (adapter cost)

Cost scale: S = hours of glue, no engine change; M = a state-extraction shim or step-function wrapper; L = engine
refactor or GPU/Redis dependence. Candidates come from a top-level scan; "grep only" means the loop was not read.

| Rank | Runtime | Why it fits | Determinism / state | Adapter cost |
|---|---|---|---|---|
| 1 | Aether kernel (`Aether/test/reference/gpu_aeth01.py`) | model case: exact integer, per-tick state, resume params exist; split-run equivalence verified | fields + seed + tick | **S** (kernel); GPU/CuPy path unchecked |
| 2 | p1_slice wm_mini | the RSO's own demo runtime; stateless hash RNG | `(parent, fp, i)` | **S-M**: split the `@njit` budget loop into chunks; needs numba + `NUMBA_CACHE_DIR` |
| 3 | `herakles/evca` + `eca` | synchronous CA step over a uint8 array (`evca/core.py:207,213`), `default_rng(seed)` (:298,632) | array + tick | **S** (grep only) |
| 4 | archaeon z80atlas (Proteus SplitMix64) | one-u64 RNG, sha256 seeding, replay verified | state in locals of `engine.py:159-251` | **M**: extract ~a dozen lists + env; scope to z80atlas (the archaeon tree is large) |
| 5 | prometheus z80atlas `World` | pickle round-trip verified; per-tick step | pickle ~71 KB | **S-M**: save/load wrapper outside the engine |
| 6 | Crius | replay verified; lifetime `Workspace/BlockStore` snapshots exist | outer loop in one function; BlockStore snapshot incomplete | **M** |
| 7 | `ludus/arena` | documented determinism contract, `Replay` objects, `Random(seed)` episode loop (`arena/core.py:385-396`) | game state + rng | **M**; one `str.__hash__` risk at `atlas_of_worlds/deepen.py:193` when seed is None |
| 8 | Primordial `metric/baseline.py` | has pause state with both rng states | Redis archive + fixed ckpt dir | **L** (Redis decision) |

Not recommended: `sigma_kernel` (store/kernel, not a loop), `odysseus`, `collider`, `aethon` (empty), Theseus daemon
(non-deterministic by construction). Heavy, defer: Theseus synth, Tyche (state in closures, wall-clock cap, sklearn),
Ananke GA (needs a torch host; the World checkpoint is the best first-party example to imitate).
Not assessed (grep only): `genesis`, `nyx` (Nyx's lane: read-only), `ensorain` beyond e0/e1, `vivarium/viv/executors`
(toy executor with a `snapshot()`, useful only as a contract test), `alien_circuitry/ac01d` `c6_dsl.py` (pickle
checkpoint, RNG not saved), `incubation` census (no checkpoint code).

## 5. Field decisions recorded (rso-builder s2.7)

- Uncertainty: whether "deterministic replay" is judged on raw output or a canonical subset. Choice: canonical subset
  (`elapsed_s`, `secs`, receipt sha/timestamp excluded). Reversible: survey wording only. Revisit when a
  replay-equality check is specified in an RSO receipt schema.
- Uncertainty: "SFE/Proteus" identification. Choice: SFE = `SerendipityFoundry/.../sfe` (ledger service), Proteus =
  `proteus/foundry` (VM); the evolutionary loop that consumes Proteus' SplitMix64 is archaeon z80atlas. Revisit if
  Palamedes meant another tree.
- Smoke runs varied PYTHONHASHSEED and ran in-process twice; cross-host / cross-library determinism (BLAS, sklearn,
  CUDA) was not tested.
