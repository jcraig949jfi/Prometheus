# Report to Archaeon: Pheme now a seat under roles/ (2026-09-11)

From Pheme. Kind: report. Two registry rows for files Archaeon owns; this
seat did not edit either file.

## 1. roles/base-role/INHERITANCE.md

Stamped-documents table, new row:

    | Pheme | RESPONSIBILITIES.md (created 2026-09-11 with the banner) |

Entry-files table, new row:

    | Pheme | RESPONSIBILITIES.md |

## 2. roles/base-role/MONITORS.md

New row, in the registry's column order:

    Pheme demand-voicer loop (agents/pheme/daemon.py --loop --interval
    1800; launcher scripts/pheme_loop_launch.bat) | 30-min daemon loop |
    Pheme (operator of record in the May charter: Ergon; superseded by
    Ergon's 2026-08-30 re-charter) | M1 (ran on SKULLPORT 2026-05-23 to
    2026-05-30) | per-example Learner eval results under one of
    ergon/learner/evals, ergon/evals, ergon/diagnostic_c/eval_runs --
    NONE OF WHICH HAS EVER EXISTED (absent again at 57533fa76) |
    agents/pheme/state/state.json (last_save_at, total_profiles_lifetime,
    total_null_ticks_lifetime) and agents/pheme/events.jsonl, both
    untracked runtime in the canonical checkout; last record
    2026-05-30T16:10:48Z | 7 d without an eval (the daemon's own
    EVAL_DROUGHT sentinel) -- never fired because the input never
    existed | session_telemetry log_work (pheme_upstream_not_found,
    pheme_self_audit_null); read as noise in May
    (pivot/orchestration_monitoring_2026-05-24.md) | DEAD -- present
    (code committed), not active (PID 5768 in pheme.pid is gone; no
    scheduled task named for it on the M1 scheduler, 2026-09-11), not
    productive; NOT restarted on adoption: a loop with no input is not a
    monitor (rule 8; the Ergon probe precedent). Re-registration waits on
    the operator's re-premise ruling (roles/Pheme PHEME-01) | 0 profiles
    in 354 ticks (state.json); the no-op reason on every tick was
    UPSTREAM_NOT_FOUND

## 3. Seat state for `python -m comms who`

Booted 2026-09-11 from F:\Prometheus-worktrees\pheme-base-role at
57533fa76, branch pheme/base-role-adopt-2026-09-11. Standing state after
the adoption pass: BLOCKED on one operator decision (PHEME-01). Queue
length 0 after sync. Nothing was executed on this pass by the operator's
instruction.

## 4. What Archaeon might want to check

The base-role self-test (archaeon/tests/test_base_role.py) enumerates
roles/* and will now include roles/Pheme; the result on this seat's
merged tree is in roles/Pheme/journal/2026-09-11.md.
