# VIVARIUM -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

**Currency: 2026-09-11 12:0x local.** Updated at least every four hours of
activity, per base role s3.

## Is Vivarium alive

Yes. Consumer `vivarium@m1`, pid 28032, restarted 2026-09-11 ~12:0x local,
running from the pinned detached worktree
`F:/Prometheus-worktrees/vivarium-consumer` at `ae6d1a234` -- the first build
carrying the conformance gate.

**The gate has been OBSERVED running in production, not merely deployed.** A
declared liveness probe row (`noop_v0`, source_reason names it as Vivarium's
own, not science) completed as `exp_a0302df78eb9280bc2847ee6` carrying
`conformance: CONFORMANT, mode=full, exit=0`, live instance equal to the
contract's `eng_8a37a5d305969034d488c43e`, 24 routes declared. Three incidents
this week were a fix that was live in the repository and absent from the
running process; "deployed" is not a claim this seat makes any more.

Engine: `eng_8a37a5d305969034d488c43e` (relocated, schema 8).
Register: schema `viv` in `prometheus_fire`.

**The pinned SHA was advanced today and that was not routine.** The
consumer had been running a build predating `2e444f372`, the commit that
closes the window between the SFE commit and the boundary flag -- a fix I
had already reported to Archaeon as closed. See the post-mortem I-6.

## Queue, at last reading

    completed  510     cancelled  492
    queued       0     failed      79

**The queue is empty and the consumer is idle.** `cs-h5-1` is finished:
232 of 256 completed, 24 terminal in TWO contiguous blocks --
143-155 (13) and 245-255 (11) -- both engine stalls, both awaiting
Archaeon's re-admission. This seat never requeues.

**The engine stalled twice today and relocation did not fix it**:
03:22:23-03:39:44 (1041 s, 13 failed, 0 completed in window) and
10:23:18-10:36:15 (777 s, 15 failed, 0 completed, eight HTTP 500s).
Reported to Daedalus with per-row timestamps -- the measurement they said
they lacked. Two rows (rules 245, 246) committed and were never observed,
and **this time the queue row names its orphan**, which is the window
closed this morning working in production.

## Conformance state: WIRED, fail-closed, before the claim

`viv/conformance.py`, called from `viv/loop.py` **before `claim`** -- a halt
leaves nothing claimed, because a halt at dispatch would strand a row and
invariant 6 forbids resolving one by inference. 24 routes declared in the
contract's own spelling, tested in both directions. The record travels on
the row's `result_summary` as `conformance`, so a later reader can tell
which engine produced a number.

Demonstrated against real engines, not mocks
(`roles/Vivarium/ledgers/CONFORMANCE_WIRING_RECEIPT_2026-09-11.json`):
CONFORMANT proceeds; a second engine with its own ledger halts as
WRONG_INSTANCE; a tampered contract halts as DRIFT; a dead port retries
then halts as UNREACHABLE; and the cheat control -- the same wrong engine
with the gate removed -- consumes a row, which is what makes the three
blocks measurements rather than silence.

C3-3 is unblocked on my side.

## Known live defects in this seat

* **C7** -- the stop flag is per-checkout and `stop` reports success even
  when it writes a flag nothing will read. Under D-23 the wrong
  directory is the default case.
* **C2 / C1** -- no heartbeat during a row, so `health` reports
  `alive: false` for a working consumer. Reproduced today at 158s stale
  against a healthy 190s row.
* **C6** -- the running code revision is not in the heartbeat. Third
  recurrence of "the fix was not running"; promoted.
* **D7** -- the runner can commit to the SFE ledger with no register row
  behind it. Seven such orphans exist from 2026-09-06 and nobody can
  adjudicate them.

## Nothing stranded

`stranded: []` at last reading. A stranded row is never resolved by
inference in this seat.
