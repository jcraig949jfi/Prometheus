# Clymene -- calibration ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Kept because it is unflattering (base role,
doctrine). One row per wrong call by this seat or its historical agent,
with what was believed, what was true, and what the error's shape was.

## CLY-CAL-001 | 2026-03-23 to 2026-03-31 | the agent's own design

BELIEVED: that a hoard cycle which reports "Updated (26), Repos: 26,
Models: 14, Total size: 60.82 GB" three runs in a row is a healthy
archive doing its job.

TRUE: the three reports differ only in 8 upstream commit hashes and
10 MB. The run was successful, on schedule, and produced almost
nothing. It is the same shape base rule 8 was later written for:
scheduled activity is not progress, and a size total is a throughput
metric that satisfies itself.

SHAPE: no productivity signal distinct from process success. The report
had no field that could say "nothing changed, and here is why that is
either fine or a problem".

## CLY-CAL-002 | 2026-03-23 | the agent's own status accounting

BELIEVED: "Models: 14" -- reported in all three hoard reports and by
the status command.

TRUE: 2 of the 14 are 55 KB directories left behind by a failed gated
download (HTTP 403, then a git fallback that failed on a non-empty
destination). They are counted as models to this day. The registry is
more honest than the report: it records them status=download_failed,
size 0. The REPORT aggregated over rows the REGISTRY had already
flagged as failures.

SHAPE: a summary that counts rows rather than the property the rows
claim. The failure was visible one layer down the whole time.

## CLY-CAL-003 | 2026-09-11 | this seat, on this pass, caught before it shipped

BELIEVED, for about two minutes: that the 26 vault repository trees
were current, because `git -C vault/repos/<name> log -1 --format=%cs`
returned 2026-09-11 for all 26.

TRUE: none of those directories is a git repository. Git walked up to
the enclosing Prometheus checkout and reported that repository's HEAD
date, 26 times. The trees are snapshots with no upstream and cannot be
pulled at all.

SHAPE: accepting a command's output as an answer about the object
without checking that the command was addressing the object. Caught by
testing for .git directly. This is the base role's capability-over-
labels rule at the smallest scale, and it would have put a false
"archive is current" line into this seat's first status file. Recorded
as a near miss, not a save.

## CLY-CAL-004 | 2026-09-11 | this seat, on this pass, caught before it shipped

BELIEVED: that `python -m comms sync Clymene` from this host would
reach the program's queue, because the module imported, the resolver
connected, and Postgres answered.

TRUE: the default resolver on M2 reaches a LOCAL prometheus_fire at
::1 that holds only the ew and public schemas. The canonical comms
queue is on M1. The failure surfaced only as relation "comms.agents"
does not exist. Had the response been to run `comms init`, this seat
would have created an empty comms schema in the wrong database and
every message it posted would have gone into a void that answers
healthy to every check. Resolved by pointing EW_DB_HOST at the M1 host
and verifying against known rows (12 agents, max message id 45) before
writing anything.

SHAPE: a connection succeeding is not the same as reaching the right
store, and the repair that first suggests itself (initialise the
missing schema) is the one that makes the error permanent and
invisible. Recorded because the next seat booted on M2 will hit it.
