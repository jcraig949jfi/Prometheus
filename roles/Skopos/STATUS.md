# Skopos -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11T17:00Z (written on the adoption pass). Next update: on
the next pass, or within four hours of any activity.

    seat state        BLOCKED on SKOPOS-XL-01 (operator decision:
                      revive re-premised / park / retire)
    four words        PRESENT (code, data and this directory committed)
                      not ACTIVE (last run 2026-04-01, 163 days ago)
                      not PRODUCTIVE (lifetime: 1 entity scored,
                        5 rows, 0 Titan prompts)
                      VALID -- not applicable; nothing adjudicated
    seated            2026-09-11, first time since 2026-04-01
    machine           M2 (the D: host)
    worktree          Prometheus-worktrees/skopos-base-role
    branch            skopos/base-role-adopt-2026-09-11
    base_sha          363120e08665af062d40810183624fa23ed19698
    dirty             no tracked changes outside this seat's paths

## What ran on this pass

Nothing executable of this seat's own. No scorer run, no database write, no
report generated. Read-only measurement of the historical artifacts, plus
the seat directory and the two base-role register rows.

## Loops this seat owns

One, SkoposScoreCycle, registered in roles/base-role/MONITORS.md on this
pass. State DORMANT since 2026-04-01. NOT relaunched: its upstream, its
invoker and its consumer are all dead (base rule 9 -- upstream liveness is
a launch precondition), and the seat is BLOCKED. It had no freshness record
and none was added, because adding instrumentation to a loop that must not
run is decoration.

## Open blockers

    SKOPOS-XL-01  operator  revive re-premised / park / retire.
                  Seat's recommendation: PARK. Reason in
                  RESPONSIBILITIES.md section 5, and it argues against
                  this seat's own revival.

## Nearest honest summary

An agent whose job was to notice what matters could not notice that it had
stopped working, and published a number 5x in its own favour for ten days
while a health check said OK. That is the finding. The seat has nothing
else to report and is not asking for work.
