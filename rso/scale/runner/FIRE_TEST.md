# C-013-T022 -- session-independent local runner: the fire test

Packet: ops/campaigns/C-013/tasks/C-013-T022/TASK.json. Conditions:
ops/campaigns/C-013/escalations/NEW_Eupalamus_2026-10-10_1_RESPONSE.md. Design:
rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md s3.1-s3.8 and s4. Built by Eupalamus[harry1-93a529ba]
(claude-opus-5-5, Q2) on harry1 (M4), 2026-10-10.

**Verdict: PASS, 13/13 criteria** (run `fire-1`, manifest `b472c5f4...`; FIRE_RESULT.json under
evidence/FIRE_20261010_fire-1/).

The test killed the worker mid-epoch. It then killed the supervisor and its replacement worker mid-epoch. The
launching process killed itself, and the launching Claude session had ended. A different Claude session relaunched
the job from the last verified checkpoint. The final run digest equals the uninterrupted control's:

    run digest      1ab5132a36686f6e56591763f2b64c863ff22df0f29079e22746daff2fa4c846
    control digest  1ab5132a36686f6e56591763f2b64c863ff22df0f29079e22746daff2fa4c846

The job owns its state, not the conversation: everything needed to resume is in the run directory, and the
resuming session received nothing except one command line.

## 1. What was run

- **Engine.** Aether AETH-01 kernel, read only (s4 below). Lattice 128x128, B_balanced physics
  (Aether/observatory/aeth02_falsifiers.py:46-51), random_soup initial state.
- **Partitions.** Two seed partitions (p0: seed 0x5C011701 / rng 0xA37E01; p1: +1 / +1). Each partition is one
  checkpoint chain.
- **Epochs.** 16 epochs of 240 ticks per chain, a checkpoint after every epoch, and a trace line every 20 ticks.
- **Replay sampling.** s3.8 replay on the first resumption, then 1 in 4 (`replay_every` 4).
- **Code.** Pinned detached worktree C:\Prometheus-worktrees\eupalamus-runner-pinned at d72fb0eb9 (WORKING_CONTRACT
  s6). runner_paths_dirty = false.
- **Run directory.** C:\Prometheus-runs\C-013-T022\fire-1, outside Git (3.3 MB, of which 2.85 MB is checkpoint
  objects). The small records are copied to evidence/FIRE_20261010_fire-1/; checkpoint bytes are not.

Three Claude sessions took part. Two were disposable headless helper sessions (`claude -p`, claude-haiku-4-5), each
told to run exactly one command:

| Phase | Session (CLAUDE_CODE_SESSION_ID[:8]) | What it did (FIRE_LOG.jsonl) |
|---|---|---|
| start | `124bd1dc` (helper A) | 09:08:15Z created the run and launched a detached supervisor (pid 12316, `breakaway_from_job: true`). It saw worker 14616 computing, then hard-killed its own process (SIGTERM = TerminateProcess). Session A then ended |
| kill | `93a529ba` (this seat) | 09:08:46Z: launcher 16972 dead, session A's harness pid 4944 dead, supervisor alive, 5 progress rows in the next 3 s (the job outlived its launcher and its session). Killed worker 14616 in fire-p0 epoch 5 at tick 40/240. The supervisor recorded WORKER_LOST rc 15 and spawned worker 12864, whose resume check replayed epoch 4 (VALID, 5.5 CPU-s). At 09:08:55Z killed supervisor 12316 and worker 12864 in epoch 5 at tick 20/240. Heads unchanged for 5 s; no live supervisor, no live lease |
| resume | `07fac962` (helper B) | 09:09:36Z checked that nothing was running and relaunched (supervisor 2228). Worker 15416 resumed fire-p0 at head 4 (resume check VALID; replay not sampled for this resumption, see s6) and was computing epoch 5 within 2 s |
| verify | `93a529ba` (this seat) | Waited for FINAL_ACCOUNT.json (09:12:35Z) and for the supervisor to exit. Ran the control in one process from GENESIS only (control.py:13), compared, and wrote FIRE_RESULT.json |

## 2. Criteria (rso/scale/runner/fire_test.py:200 phase_verify)

| Criterion | Result |
|---|---|
| launcher dead, supervisor alive, job kept computing after the launcher died | PASS (5 progress rows in 3 s) |
| launching session gone (its harness pid not alive) | PASS (pid 4944) |
| worker killed mid-epoch | PASS (epoch 5, tick 40) |
| supervisor and its replacement worker killed mid-epoch | PASS (epoch 5, tick 20) |
| nothing ran while the job was down | PASS (heads unchanged for 5 s) |
| resume ran in a different session from the launch | PASS (07fac962 != 124bd1dc) |
| resumed from the published checkpoint, not from genesis | PASS (fire-p0 resumed at head 4; fire-p1 had not started) |
| every resume check VALID | PASS (2 of 2) |
| every epoch published exactly once | PASS (32 PUBLISHED, positions 1..16 per chain, 0 DUPLICATE/STALE/INVALID) |
| final run digest == control | PASS |
| final engine state digest == control, per chain | PASS (p0 4237ae76..., p1 c38a3107...) |
| wasted work accounted | PASS (2 interrupted attempts; see s3) |
| <= 1 CPU core-hour | PASS (286 CPU-s, s3) |

## 3. Wasted work and resources (FINAL_ACCOUNT.json; account.py:63)

| Class | CPU-s | Note |
|---|---|---|
| productive (32 published epochs) | 167.34 | |
| verification (s3.8 replay at resume) | 5.50 | one replay of epoch 4 |
| interrupted (2 attempts, both fire-p0 epoch 5) | >= 1.45 | metered to the last PROGRESS row: 40 + 20 = 60 ticks; the remainder is unmetered, a lower bound, never zero (rso/slice001/ledger.py:7-30 semantics) |
| rejected | 0 | |
| supervisors (2) | 1.06 | SUPERVISOR_CPU rows, so the killed supervisor is still charged |
| phase drivers | 1.05 | they only poll; the verify driver's CPU is the control's |
| control | 109.45 | uninterrupted replay of both chains |
| **total** | **285.86** | 0.079 core-hour. With the rehearsal and test suites, this packet used under 0.2 core-hour |

GPU 0, cloud USD estimated 0, billed 0 (two fields, never merged). Concurrency: compute never exceeded two
processes (supervisor + one worker). The control ran only after the supervisor had exited. The phase driver sleeps
between polls.

The price of the two losses was 60 ticks of lost epoch work plus one 240-tick verification replay. With
checkpoint_every = 1 epoch, the most a loss can cost is one epoch.

## 4. The runtime-agnostic interface (engine.py:38) and the first client

`init(params) / step(state, n) / save_state(state) -> bytes / load_state(params, bytes) / digest(state)`, plus
`probe()`, which returns the EnvironmentSpec. Engines are looked up by Moonshot runtime identity {name, version}
(engine.py:110, the same strictness as moonshot/epoch/runtime.py:67-75). Two engines are registered:
- `rso.runner.toy` v1 (a pure-Python hash chain, used by the tests);
- `rso.runner.aether_kernel` v1 (aether.py:64).

Adding an engine means one class and one registry line. The runner never looks inside a state.

The Aether client imports, read only, and without copying or editing:
- the kernel `gpu_step` (Aether/test/reference/gpu_aeth01.py:111), loaded by file path under a private module name
  so that Aether's `test` package cannot shadow the standard library's;
- `build_initial` (Aether/observatory/aeth01_run.py:47);
- `state_digest` (Aether/observatory/aeth01_observatory.py:154).

Its step loop is the driver's own (aeth01_run.py:136-142). tests/test_engine.py `test_matches_kernel_run_world`
checks the adapter's state digest against `run_world` itself.

Aether was notified (comms #2006). No Aether file is changed by this packet.

## 5. Format alignment with C-012 (Themis; moonshot/nf/INTERFACE_CONTRACT.md v0.2, moonshot/epoch/model.py)

Identity is aligned by construction: the runner calls Moonshot's code instead of restating it.

| Record | Runner | C-012 | Status |
|---|---|---|---|
| genesis | moonshot.epoch.genesis.v1 via `M.make_genesis` (run.py:73) | model.py:53-66 | SAME (Moonshot's code) |
| SPEC | `M.derive_spec`; the publisher re-derives it and refuses a mismatch (run.py:181) | model.py:69-74; contract :108-113 (publisher check) | SAME |
| MANIFEST, work_id, epoch_digest | `M.execute` with the engine wrapped as a Moonshot runtime (worker.py:32) | model.py:77-106; contract :26-30 | SAME. The trace is canonical lines {t, d} with no clock, host or attempt data (runtime.py:1-4) |
| epoch verification | `M.verify_epoch` on publish and on resume | model.py:109-143 | SAME |
| uninterrupted reference | `M.replay_chain` (control.py:13) | model.py:146-153 | SAME |
| objects | sha256-addressed directory, write-once, verified on read (store.py:105) | `objects(sha256 PK, content)`, contract :65 | DIVERGES in transport only: local directory vs Postgres. Same key. Large checkpoints need the architecture's s3.6 store either way (contract :57-60 "DESIGN ITEM") |
| chain head | HEAD.json {head_index, head_epoch_digest, head_checkpoint_sha256, generation, state OPEN/HALTED/COMPLETE} | `chains` row, contract :66-69 | SAME fields and generation rule (+1 on every head move). Enforced by a host-local lock file, not a database trigger |
| publish guard | advance only if OPEN, generation = expected, head_index = k-1 and head checkpoint = manifest input; else DUPLICATE / DISAGREEMENT (halt) / STALE; INVALID on bad bytes; HALTED (run.py:181) | `publish(...)`, contract :83-92 | SAME classification. DIVERGES: an extra STALE when the caller no longer holds the partition lease (local fencing; Fabric's attempt fencing plays this role in C-012) |
| lineage | publications.jsonl, one row per head advance, reconciled from HEAD after a kill (run.py:144) | `publications`, contract :72-74 | SAME content. Rejected rows are not written here: a rewind is not implemented (see contests) |
| attempt classification | outcomes.jsonl, one row per publication attempt | `attempts`, contract :75-76 | SAME role. Local attempt ids instead of Fabric attempt ids |
| validations | RESUME_CHECK rows (bytes / round_trip / replay / environment) in events.jsonl | `validations`, contract :95-100 | PARTIAL. A replay mismatch halts the chain (= MISMATCH -> contest). No separate validator identity |
| contests | contests.jsonl + HEAD state HALTED | `contests`, `resolve_contest`, contract :77-78, :101-105 | DIVERGES: halt only. No resolver, no UPHELD/OVERTURNED, no rewind; a halted chain waits for a human or a C-012 resolver |
| progress events, accounting | START / PROGRESS / END / RESUME_CHECK / REFUSED in a per-partition shard (architecture s3.7 option a) | attempt accounting outside the canonical trace, contract :75-76 | ALIGNED in spirit. Rows use the RSO ledger's START/END semantics; option (b), rows in the C-012 attempts table, once the runner moves onto NF transport |
| run manifest, final account | rso.runner.run_manifest.v1, FINAL_ACCOUNT.json | not in C-012 (the Observatory layer above it, architecture s3.0) | NEW |
| leases | host-local LEASE.json per partition (lease.py:45) | Fabric lease row only; Moonshot keeps no lease table, contract :21-22 | DIVERGES by design (escalation response: Fabric lease optional). On NF transport, Fabric's one-live-attempt invariant replaces it |

Moving to Fabric/NF transport keeps the manifest, genesis, SPEC, MANIFEST and checkpoint bytes unchanged. Only
three layers swap:
- objects -> `moonshot.put_object`;
- publish -> `moonshot.publish`;
- lease -> the Fabric attempt.

## 6. Field decisions (rso-builder-role s2.7) and known limits

- FD-T22-1. **Reuse Moonshot's identity code instead of mirroring it.** Uncertainty: a Moonshot change could move
  the runner's digests. This is reversible. Revisit if moonshot.epoch.model's identity changes (that would be a
  C-008 contract change, which Themis gates).
- FD-T22-2. **The lease is host-local, not a Fabric lease** (optional per the response). It is a fence plus pid
  liveness, with a 30 s TTL across hosts. Revisit when the runner moves onto Fabric transport.
- FD-T22-3. **Lineage lives in JSONL plus HEAD.json, not Postgres**, so no database is needed to run.
  Reversible.
- FD-T22-4. **Replay sampling is the first resumption plus 1 in replay_every**, deterministic in (manifest_id,
  chain, k).

  In this run, the cross-session resumption (worker 15416 at head 4) was NOT replayed: epoch 4 had already been
  replayed by worker 12864, and the 1-in-4 sample fell elsewhere. That resumption was checked by bytes, round-trip
  and environment, and the final digest equalling the control covers it end to end. `replay_every: 1` makes every
  resumption replay.
- FD-T22-5. **Detach.** The supervisor is started through an intermediary that exits at once, with flags
  DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB on Windows (breakaway granted here), and
  `start_new_session` on POSIX. The POSIX path is written but was NOT exercised in this packet (harry1 is Windows).
- FD-T22-6. **The run directory is outside Git** (C:\Prometheus-runs\). Git gets the manifest, the records and the
  digests, never checkpoint bytes (directive s9).

Limits, stated plainly:
- **No automatic relaunch.** A job that dies stays down until someone runs `launch`. Any session or a host
  scheduler can do it, and `launch` is idempotent because there is one supervisor per run. A scheduled
  `python -m rso.scale.runner launch <run_dir>` (Task Scheduler / systemd timer) would close that gap. It is not
  built here.
- **One host.** The store, lease and lock are local. A cross-host run needs the s3.6 store and NF transport.
- **No recovery from bad state.** INVALID at resume (corrupt bytes, round-trip failure, environment mismatch)
  stops the run as BLOCKED, with no rewind to k-1. A contest halts it, with no resolver.
- **No checkpoint retention policy.** Every epoch checkpoint is kept. At 2048^2 that is about 20 MiB per epoch,
  so a week-long run needs one.
- **CPU only.** The Aether GPU/CuPy path is untouched (CHECKPOINT_REPLAY_SURVEY.md s4: unchecked).

## 7. How to run it again (any session; from a pinned worktree)

    git -C <canonical> worktree add --detach <root>-worktrees/<seat>-runner-pinned <sha>
    cd <pinned worktree>
    python -m rso.scale.runner.fire_test start  --run-dir <D>      # session A: returns by killing itself
    python -m rso.scale.runner.fire_test kill   --run-dir <D>      # any session; waits <= 180 s for session A to end
    python -m rso.scale.runner.fire_test resume --run-dir <D>      # session B (must differ from A)
    python -m rso.scale.runner.fire_test verify --run-dir <D>      # any session; writes FIRE_RESULT.json
    python -m rso.scale.runner.fire_test evidence --run-dir <D> --out <repo dir>

`--rehearsal` on `start` uses a 64x64 lattice and 6 epochs. A rehearsal with every phase in one session
(C:\Prometheus-runs\C-013-T022\rehearsal-1, not committed) passed 11/11 mechanical criteria and failed the 2
session criteria, as designed.

The runner by itself:

    python -m rso.scale.runner create <D> --spec spec.json
    python -m rso.scale.runner launch | status | account | control | verify <D> [chain]

Tests: `python -m unittest discover -s rso/scale/runner/tests -t .` (35 OK). Mutation check:
`python rso/scale/runner/tests/mutation_check.py` (13/13 killed; evidence/MUTATION_TABLE.json). RED first:
evidence/RED_20261010.txt (commit f669c3806).
