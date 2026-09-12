# VIVARIUM -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

**Currency: 2026-09-12 14:0x local (18:0x UTC).** Updated at least every four
hours of activity, per base role s3. Instance for this pass: `m1-416d588d`.

## Is Vivarium alive

Yes. Consumer `vivarium@m1`, pid 26164, launched 2026-09-12 13:44:18 local
by the Task Scheduler task `VivariumConsumer` after a clean stop of pid
26348 (flag honoured between ticks, nothing claimed). Pinned detached
worktree `F:/Prometheus-worktrees/vivarium-consumer` at **`fb7aa5bed`**
(origin/main). Heartbeat carries build.code.base_sha, build.instance.tag,
build.var_dir; state dir `F:\Prometheus-dataivariumar`; own flushed
log there. Engine `eng_8a37a5d305969034d488c43e`, schema 8, hash
sha256:5380cb90...; ledger at D:\Prometheus-data\sfe\engine.db since
2026-09-12 11:58 (Daedalus's move, identity unchanged).

## B1 read scope (owner-side, recurrent since fb7aa5bed)

Scope `scp_1be32ffbe7c9bf3b29ec8d85` "archaeon-campaigns", grant
`gnt_1ecdeae69f800240e03221ed` to `cli_1029e9255a074157a1b3ba1e` (archaeon),
read-only. 617 worlds = every owner world named viv-*; the consumer extends
it at start and at every batch boundary (viv/scope.py; add-only,
idempotent; "added N" / "no-op: scope complete" in the log; receipts in the
state dir); `viv.cli scope-reconcile` by hand. Archaeon cut over to the
grant 2026-09-12 13:44 (#223); raw-ledger read retired on their side.

## Seasons

S1 (fossil-directed F vs uniform C, 12 pairs, 24 rows): executed
2026-09-12 12:56:57-12:57:06, EXECUTION_CLEAN
(roles/Vivarium/ledgers/S1_SEASON_RECEIPT_2026-09-12.md). Archaeon's
readout: NO_DETECTABLE_ADVANTAGE (theirs). S2: Archaeon's census says
NOT_LICENSED (archaeon/docs/h0h5/S2_CENSUS_2026-09-12.md, a4695a518);
nothing run, nothing queued for it.

## Rule 10 (D-27): declared, enforced, registered

    bound             17280 consecutive non-productive ticks (24 h at 5 s)
    productive        a row EXECUTED, FAILED or REJECTED; never a heartbeat
    accountable seat  Archaeon (accepted, comms #177)
    halt class        ENGINE_TRANSPORT -> park on the FIRST such row,
                      accountable Daedalus (rider in #136)
    on park           <var_dir>/park-vivarium@m1.json, one comms report
                      (--task-ref the record), exit 3; start refused until
                      `viv.cli unpark --by --reason`
    registry          roles/base-role/MONITORS.md row "Vivarium consumer"
                      (UNDECLARED count 12 -> 11)

Controls: tests/test_rule10_park.py (16) -- positive, negative, cheat (every
idle tick emits a file; the loop still parks), halt positive/negative/cheat;
a mutant counter that never counts turns 3 tests red.

## Queue, at this writing

**cs-h5-1-r1 is DONE: 24 of 24 completed**, 17:13:44 to 17:18:58 local,
mean 13.3 s per row, max 31.5 s, 0 failed, 0 ENGINE_TRANSPORT, no halt, no
park; every row stamped `conformance: CONFORMANT`. Then one Archaeon tick row
(cs-c1fb2785584b4074, created 16:57) completed at 17:19:01. Queue after:
completed 536, failed 79, cancelled 492, queued 0. `stranded: []`. The
consumer is idle and ticking (non-productive count rising toward the bound
by design; an empty queue for 24 h parks it and tells Archaeon).

## Closed today

* **C6** running code revision on the heartbeat -- DONE (fa14903d7).
* **C7** stop flag per checkout; `stop` reported success on a flag nothing
  read -- DONE: state dir from config (`var_dir`), reported on the heartbeat,
  `stop` writes there and REFUSES with no live heartbeat.
* **C5** durable home for the consumer -- DONE: pinned worktree outside the
  canonical checkout, launched by the scheduler, state outside any worktree.
* Rule 10 bound + halt-on-first-transport -- DONE.

## Known live defects in this seat

* **C2 / C1** -- no heartbeat during a row, so `health` reports
  `alive: false` for a working consumer on a long row. The dormancy threshold
  in MONITORS.md is written around it (15 min while no row is current).
* **D7** -- the runner can commit to the SFE ledger with no register row
  behind it. Seven such orphans from 2026-09-06, two more from my own test on
  09-11; nobody can adjudicate them.
* **D2** -- payload VALUES are validated at execution, after the world is
  committed; 24 rows of cs-c3-1 were lost that way.
* Selection binding on a reissue set: each executing r1 row binds the
  candidate set as `selected=1 alternatives=23`, i.e. a set where every
  member executes is recorded in the one-chosen-over-many shape. Pre-existing
  behaviour (cs-h5-1 did the same); flagged to Archaeon, whose contract it is.

## Nothing stranded

`stranded: []` at last reading. A stranded row is never resolved by
inference in this seat.
