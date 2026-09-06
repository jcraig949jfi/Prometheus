# VIVARIUM — the short-term machine, and the unattended loop demonstrated

2026-09-06. Evidence: `roles/Vivarium/TEST_RESULTS_MACHINE_2026-09-06.txt`
(114 Vivarium tests, 145 Archaeon tests), plus the live transcripts below.

---

## 1. Entry points

**Daemon** — `vivarium/viv/daemon.py::Daemon.run()`, CLI
`python -m viv.cli run [--interval S] [--once] [--max-ticks N]
[--stop-when-idle] [--worker-id ID]`. Exit 0 normal, **exit 2 BLOCKED**
(verified: a restart over a stranded row returns 2).

**Tick** — `vivarium/viv/loop.py::Vivarium.tick(conn) -> TickReport`, CLI
`python -m viv.cli tick` (one tick, JSON out). At most ONE runnable item per
call. No loop, no sleep, no policy inside it.

**Health** — `python -m viv.cli health` (machine-readable JSON; exit 1 when
unhealthy) and `Vivarium.health()`. Reports queue counts, who holds the slot,
stranded ids, and every worker's liveness and counters.

**Errata** — `python -m viv.cli errata`.

## 2. Scheduler approach

Deliberately stupid, and the stupidity is the design:

    while running:
        report = viv.tick(conn)
        if report is IDLE or BUSY: sleep(interval)     # else immediately

* one tick executes at most one item; a productive tick is followed
  immediately by the next, so a backlog drains at the speed of execution and
  no faster. No batching, no burst.
* the idle interval is fixed. Adaptive backoff would make an experiment's wait
  depend on how quiet the queue has been, which is a scheduling decision.
* order is `(priority, created_at)` inside the claim statement and nowhere
  else. No reordering, no starvation handling, no result-dependent behaviour.
* stopping is cooperative (SIGINT/SIGTERM finish the current tick). A tick that
  raises is logged and the daemon continues — the queue is durable and the next
  tick re-reads it.
* `BLOCKED` is terminal for the process: it will not poll forever against a
  condition only an operator can clear.

## 3. The nine stages, each independently testable

`recover · claim · validate · build_request · dispatch · collect · fossilize ·
finalize · tick`, each a method with its own inputs and outputs.
`tests/test_stages.py` exercises every one on its own (26 tests);
`tests/test_daemon.py` covers the loop around them (8 tests). A failure now
names a stage.

## 4. Success E2E transcript (unattended, production)

Producer and consumer are separate OS processes. Neither Claude session touched
the item between the stages.

    $ python -m archaeon.producer.loop --once --lane e2e-viv
    ...
      "decision": "WROTE_WEAK_SIGNAL",
      "policy": "random.v0",
      "spec_hash": "sha256:a78661a0c5d442bca1033b3c7ab652eb088c02a1abcb350dafb83960afc3bc6f",
      "candidate_set_id": "cs-83b413379fe24ae8"

    # the daemon, already running and idle, picked it up on its own:
    [viv] daemon up worker=vivarium@e2e-viv schema=viv idle_interval=4.0s
    [viv] pew=OK ok schema_version=4 contract=pew.fossil.v2
    [viv] stage=claim experiment_id=5a2bcbab-973d-41d2-8d76-0ddfce944451 spec=a78661a0c5d4
    [viv] stage=dispatch experiment_id=5a2bcbab-… -> running sfe=exp_4211cf0204995b3f62d1c32d
    [viv] tick=EXECUTED t=1.96s experiment_id=5a2bcbab-…
          sfe_experiment_id=exp_4211cf0204995b3f62d1c32d
          pew_reference=pew:encounter/ENC-archaeon-608723c9dd6773c1:
                        exp_4211cf0204995b3f62d1c32d:wrk_04ac1466aceeb261ff9bea0f

PEW, read back independently:

    ENC-archaeon-608723c9dd6773c1   n_runs=1
      run_id          exp_4211cf0204995b3f62d1c32d:wrk_04ac1466aceeb261ff9bea0f
      outcome         SURVIVED
      failure_class   None
      sfe_event_id    evt_27568ab2da666a65def1ad0d
      sfe_entry_hash  sha256:fd90e0a3fed045706a6f6edaa32fee2c75cf2590236246355d863a8b5f475188
      producer.queue  {created_by: archaeon, source_reason: weak_signal,
                       experiment_id: 5a2bcbab-…, request_key: rk-fa287c49d66c4d19,
                       candidate_set_id: cs-83b413379fe24ae8}

The fossil points back at the queue row, and hence at the policy that proposed
it, without any of that having been inside the sealed spec.

## 5. Failure E2E transcript (same route)

A spec that satisfies the kind contract (both declared parameters present) but
whose `bits` is not binary. The engine's reference executor refuses it **after**
the world exists and the experiment is committed — so the boundary was crossed
and a fossil is owed.

    [viv] stage=claim experiment_id=80aeb85d-e6a5-4b0b-9760-ced6b9eb0e2e spec=2a416c61aac2
    [viv] stage=dispatch experiment_id=80aeb85d-… -> running sfe=exp_121c57beab05b16d8cb3af91
    [viv] tick=FAILED t=1.16s experiment_id=80aeb85d-…
          sfe_experiment_id=exp_121c57beab05b16d8cb3af91
          pew_reference=pew:encounter/ENC-viv-failure-control-2026-09-06:…
          failure_class=EXECUTOR_ERROR
          reason=executor raised: executor failed: invalid candidate

PEW:

    ENC-viv-failure-control-2026-09-06   n_runs=1
      outcome         FAILED           <- the WORK ITEM's terminal status, observed
      failure_class   EXECUTOR_ERROR
      resources_used  {work_id: wrk_9fab…, obs_id: None, attempted: true}
      sfe_event_id    evt_527c5ce20f7f0b73ab19776d   (EXPERIMENT_COMMITTED; binds exp_id)

`obs_id: None` is the honest part: no observation was made, no outcome rule was
run, and nothing about a measurement was invented. `attempted: true` is what
makes *failures per experiment executed* computable from the fossil record.

## 6. Crash / restart test

Run in a dedicated schema with identical DDL (`vivarium/crash_restart_demo.sh`),
because a second Vivarium daemon was concurrently consuming production and
would otherwise have claimed the item — see §10. Nothing is manufactured: the
stranded row comes from a real `kill -9` of a real worker between `mark_running`
and `finalize`.

    ### phase 1 -- SIGKILL the instant a row reaches `running`
      saw running: b3f9c26c-… exp_f1aff2d8c4d042edffded1f0
      D1 [viv] stage=dispatch b3f9c26c-… -> running sfe=exp_f1aff2d8c4d042edffded1f0
      SIGKILL sent

    ### state after the crash
      b3f9c26c-…  running  crossed=True   sfe=exp_f1aff2d8c4d042edffded1f0
      5491bc55-…  queued   crossed=False
      e9533562-…  queued   crossed=False

    ### phase 2 -- restart the SAME worker id
      D2 REFUSING TO START: b3f9c26c-… is running under this worker id.
         Inspect SFE (exp_f1aff2d8c4d042edffded1f0), then: vivarium release …
      D2 …They are stranded, not resumable… Vivarium will not guess.
      exit code 2

    ### phase 3 -- operator releases
      released b3f9c26c-… -> failed

    ### phase 4 -- restart
      D3 tick=EXECUTED 5491bc55-… sfe=exp_123ad6b3955e8be01c753c21
      D3 tick=EXECUTED e9533562-… sfe=exp_294cdc49f939457a96578ec3
      D3 queue empty and --stop-when-idle set

    ### final:  completed=2, failed=1
      b3f9c26c-…  failed  rejected_before_execution=False  failed_during_execution=True

Two crash properties worth naming. The claim is committed **before** dispatch,
so a crash leaves a visibly claimed row rather than a silently lost one. And
`sfe_experiment_id` is written at `mark_running`, **before** any result exists,
so a stranded row always names the SFE experiment an operator must inspect.

A graceful stop (SIGTERM) and a kill while idle both strand nothing — verified
on the live production daemon.

## 7. PEW records produced today

    ENC-archaeon-cbc38bab53fb6695        completed  (Archaeon producer -> e2e-autoconsumer)
    ENC-archaeon-608723c9dd6773c1        completed  (Archaeon producer -> vivarium@e2e-viv)
    ENC-viv-failure-control-2026-09-06   FAILED / EXECUTOR_ERROR
    enc_demo_family_7342e0ac             2 runs, the Tier 1 two-arm family

## 8. Queue states observed

`queued → claimed → running → completed` (success);
`queued → claimed → running → failed` (execution failure, fossilized);
`queued → claimed → failed` with `started_at IS NULL` (spec rejected, never
executed, correctly NOT fossilized); `queued → cancelled` (unchosen candidate);
`running` held across a crash until an operator released it to `failed`.
`viv.execution_attempts` distinguishes all of these without a seventh state.

Final production health: `queued_now: 0`, `slot_held_by: null`,
`stranded: []`, `completed: 10`, `failed: 3`, `cancelled: 318`.

## 9. Contamination handling for the 245 leaked rows

**Nothing was deleted.** Migration `003_register_errata.sql` adds:

* `viv.register_errata` — one row per declared incident, append-only by trigger;
* `viv.register_errata_rows` — the **enumerated** member rows, append-only;
* `viv.register_clean` — the register minus every excluded row. **This is what
  analysis reads.**
* `viv.candidate_sets` gains an `excluded` count, so a contaminated set
  announces itself rather than quietly shrinking.

Erratum 1 is declared over **246 rows** (the 245 cancelled plus the one that a
live cycle claimed and failed). Boundary: Archaeon's genuine Stage 0 batch is
the 06:55Z registration of 70 rows (commit `ecfef4d87`); every `archaeon` row
from 07:00Z onward falls inside a pytest window. Current state:
**331 rows, 85 clean, 246 excluded.**

Membership is **enumerated, not predicated**. A predicate would be re-evaluated
against a moving table and would silently capture future honest rows; a frozen
list of ids can be audited row by row for ever. It is also the only honest
option, because the contaminated rows are identical to real candidate
registrations in every column — only the timestamp separates them, and that is
itself the finding.

The exclusion had to live outside the rows in any case: the BEFORE UPDATE
trigger freezes terminal rows whole, so there is no flag to set on a cancelled
row. The constraint produced the right design.

Exclusion rule, also stored in the erratum and printed by `vivarium errata`:

> Analysis reads `viv.register_clean`. Never read
> `viv.research_experiment_queue` directly for candidate-set or selection
> analysis. A `candidate_sets` row with `excluded > 0` is contaminated and its
> counts are not a selection decision.

## 10. Remaining blockers to leaving both loops running unattended

1. **RESOLVED during this session — process ownership.** For part of the E2E,
   two Vivarium daemons were consuming production concurrently: mine
   (`vivarium@e2e-viv`) and `e2e-autoconsumer`, started by the Archaeon session
   to watch its own proposal execute. Its heartbeat `build` block identified it
   as this same codebase, so the architecture held — Archaeon was not executing
   anything, it had started Vivarium's daemon. The single-slot index made the
   overlap safe (one daemon simply reported BUSY), which is unplanned evidence
   that the guarantee works.

   The operator has since told Archaeon that **this session owns and starts
   Vivarium**, and Archaeon recorded the boundary in
   `roles/Archaeon/RESPONSIBILITIES.md` and `archaeon/docs/OPERATIONS.md`
   (commit `1097458e6`): it does not start, stop, restart or configure
   Vivarium, not even to demonstrate its own output; a proposal sitting
   `queued` is a fact to report, never a reason to start a consumer. Their note
   also records that their `pkill` matched only the shell wrapper, so the
   process outlived the cleanup — the same trap I hit stopping my own daemon,
   where `TaskStop` killed the wrapper and left the Python process polling.

   Verified now: **no Vivarium worker is live, the slot is free, the queue is
   empty and nothing is stranded.** What is still missing is mechanism rather
   than agreement — there is no singleton lock on the worker role and no
   supervisor, so the boundary is currently enforced by a written rule and not
   by the machine.

2. **A missing `VIV_PEW_TOKEN` costs an autonomous item.** This happened for
   real at 03:37Z: the first autonomous Archaeon item executed perfectly in SFE
   and was then failed, because its spec set `pew.required` and the daemon had
   no credential. One of Archaeon's six daily slots was spent on an environment
   variable. **Mitigated**, not fixed: the daemon now runs a PEW preflight at
   startup and logs `pew=OK` or a loud `WARNING pew=UNCONFIGURED`. A real fix
   is a systemd/scheduled-task unit that owns the environment.
3. **No process supervision.** Neither loop restarts on host reboot or on
   crash. Both are plain foreground processes. A Windows scheduled task (as SFE
   already uses) is the obvious next step and is not built.
4. **The SFE work lease is still not heartbeated** (`lease_s=120`, work item
   `max_attempts: 3`). Executions are ~1.5–2s today, so this has never fired,
   but a slow kind would lose its lease. Tier 2 item 10.
5. **`archaeon.probe.v0` still has no executor.** Archaeon's producer works
   around it honestly — it writes a declared `random.v0` policy draw over
   `evaluate_bitstring` and records the region-targeted probe it would have
   issued. I verified independently why no shortcut exists: the flagged
   `sfe.candidate_score.v0` corpus was scored by some other harness — candidate
   6926509 scores 0.42289 there and 0.33333 under the engine's 24-bit reference
   executor, and 0.42289 is not a multiple of 1/24 — so mapping a probe onto
   `evaluate_bitstring` would fabricate an execution that was not the one
   requested. I built and then **deleted** a `calibration` rung of my own on
   discovering Archaeon had already solved this better.
6. **Archaeon's `repeat` request is unbuilt** (their
   `INBOX_ARCHAEON_QUEUE_ADOPTION.md`): one queue row = one world = one
   observation, so no family can ever reach S17's ≥4-observations-per-world
   eligibility. Out of scope by instruction; it remains the blocker for F1.
7. **Log retention and rotation.** The daemon logs to stdout only; nothing
   captures or rotates it. `archaeon.cadence_log` also grows one row per cycle
   for ever (their note).
8. **PEW remains optional.** A spec with `pew: null` executes and is fossilized
   nowhere — three of today's runs. Tier 2 item 9, still deferred and still
   needing Mnemosyne.

Not proceeding to Tier 2. Not solving Stage 0 / F1 arm semantics. Not
generalizing `archaeon.probe.v0`.
