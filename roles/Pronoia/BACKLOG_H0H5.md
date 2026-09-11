# Pronoia -- backlog

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Built from 363120e08 in
Prometheus-worktrees/pronoia-base-role on M2.

PROVISIONAL, AND BELOW THE SCHEMA FLOOR, DELIBERATELY.
roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md requires
at least 20 items. This file has 9. That is not an oversight: this seat
has no charter and no lane, and 11 invented items would be a backlog
that looks like a mandate. The schema's own rule -- every item names the
artifact that proves it done -- is the reason the list is short. Each
row below is something this seat could actually finish. The list grows
to the floor when PRON-01 is answered, and not before.

Schema: ID | item | lane | milestone | size | blocked_on | evidence of done

## The rows

PRON-01 | Rule whether this seat exists and what it owns: fleet liveness instrumentation, or nothing | TOOLS | program | XL | operator decision NEW: "Pronoia was two programs (a dead research-scanner orchestrator and a live fleet-visibility loop). Re-charter it as the seat that owns the running-versus-producing distinction for every standing loop, park it, or retire it." | a line in archaeon/docs/expansion/DECISIONS.md, or an operator ruling committed under roles/Pronoia/prompts/

PRON-02 | Decide the disposition of the runnable untracked pronoia.py on M2, whose publish step commits and pushes to main from the canonical checkout | TOOLS | program | XL | operator decision NEW: "delete the untracked pronoia.py from the M2 canonical checkout, or neutralise its publish path, or leave it" | the file absent from the M2 root with the removal recorded in roles/Pronoia/journal/, or a committed note recording the operator's decision to leave it and why

PRON-03 | Populate last_work_attempt_at, last_work_success_at and health in Pronoia's Postgres heartbeat writer so "alive" and "working" become different observable facts | TOOLS | alpha | S | none for the patch; a host that can deploy to M4 for the effect | the diff to scripts/intelligence_loop.py committed, plus a query result in roles/Pronoia/journal/ showing the three columns non-NULL for agent_name='Pronoia'

PRON-04 | Answer whether Era 2's four-hourly dashboard push is dead or merely late, using the fields PRON-03 adds, with the INDETERMINATE branch stated | EVIDENCE | alpha | S | PRON-03 deployed and one day of rows | a dated readout committed under roles/Pronoia/ with the per-stage row counts, the eligible cycle count, and one of DEAD / LATE / INDETERMINATE

PRON-05 | Name the consumer of docs/portfolio_brief.md and docs/state.json, or record that none was found | EVIDENCE | alpha | S | none | a committed list of every reader found by path search and by asking the operator, or the explicit finding "no consumer located", dated, with the search commands

PRON-06 | Correct the two MONITORS.md rows this pass found stale and check the rest of the registry's freshness sources against their own queries rather than against their prose | TOOLS | beta | M | PRON-01 (this touches rows other seats own; without a charter this seat may only annotate its own) | a committed diff to roles/base-role/MONITORS.md plus a per-row table of asserted-state versus measured-state with the query used for each

PRON-07 | Write the instrument-failure note that Era 1 never left behind, so the next author of a liveness check reads it before repeating it | EVIDENCE | alpha | S | none | a committed file under roles/Pronoia/ enumerating the six Era 1 failures with the code line and the log evidence for each, linked from MONITORS.md's "how to feed a watchdog" section

PRON-08 | Add a cheat control to any liveness check this seat ships: inject a fabricated success and confirm the check observes it | TOOLS | alpha | M | PRON-01 | a committed test with negative, positive and cheat fixtures, in the shape of roles/Kairos/science/fixtures/

PRON-09 | Register the surviving on-disk-but-untracked-artifact class as a repository-wide question: how many other deleted-and-gitignored executables are runnable on a shared host | TOOLS | beta | M | PRON-01 | a committed census of root-level gitignored executables on M2 with, for each, whether it performs a mutating git operation

## Open operator decisions (the XL rows, gathered)

Two: PRON-01 and PRON-02. Both are stated in one sentence in the
blocked_on column above so the operator's queue is derivable from the
union of the seats' XL rows without reading this file's prose.

PRON-02 is the one with a clock on it. Everything else here can wait
indefinitely without the situation getting worse; a runnable script that
pushes to main from the canonical checkout cannot.
