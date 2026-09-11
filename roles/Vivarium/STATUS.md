# VIVARIUM -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

**Currency: 2026-09-11 05:0x local.** Updated at least every four hours of
activity, per base role s3.

## Is Vivarium alive

Yes. Consumer `vivarium@m1`, pid 14236, started 2026-09-11 04:38:15 local,
running from the pinned detached worktree
`F:/Prometheus-worktrees/vivarium-consumer` at `35f32116e`.

Engine: `eng_8a37a5d305969034d488c43e` (relocated, schema 8).
Register: schema `viv` in `prometheus_fire`.

**The pinned SHA was advanced today and that was not routine.** The
consumer had been running a build predating `2e444f372`, the commit that
closes the window between the SFE commit and the boundary flag -- a fix I
had already reported to Archaeon as closed. See the post-mortem I-6.

## Queue, at last reading

    completed  430     cancelled  492
    queued      92     failed      64
    running      1

Campaign in flight: `cs-h5-1`, arm `map`, `eca_rule_eval_v1`. 256 rules
admitted; 13 terminal at rules 143-155 and awaiting Archaeon's
re-admission, so the map completes at 243 of 256 without them.

## Conformance state: NOT WIRED

The consumer runs against the engine **without** the four-state
conformance gate required by WORKING_CONTRACT s8 and by the operator's
directive in `INBOX_ARCHAEON_CONFORMANCE_WIRING_2026-09-11.md`.
Archaeon's half is on main; mine is not written. C3-3 waits on it. This
is the seat's top item.

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
