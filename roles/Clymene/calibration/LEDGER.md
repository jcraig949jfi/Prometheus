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

## CLY-CAL-005 | 2026-03-23 .. 03-31 | the agent's reports, mechanism located

BELIEVED: "Models: 14" and "Total size: 60.82 GB" described what Clymene
had archived.

TRUE: 3 of the 14 rows were models already sitting in a Hugging Face cache
under a different user profile on M1 and never copied into the vault; they
contributed 9.43 GiB, 15.5% of the headline total. 2 more were the gated
403 failures. 9 of 14 rows (64%) are models Clymene actually archived.

SHAPE: clymene.py line 575 writes len() of a registry query with no filter
on status. The registry knew the truth and the report did not ask it. A
summary that counts rows rather than the property the rows assert. Located
at the line, not inferred. Full working in
roles/Clymene/ledgers/HISTORICAL_RECONCILIATION_2026-09-11.md R-1, R-2.

## CLY-CAL-006 | 2026-03-22 .. 03-23 | a failure that turned green unrepaired

BELIEVED: THOR moved from [CLONE_FAILED] to "Updated" because something
got better.

TRUE: nothing repaired it. The failed clone left a .git directory behind,
so the next cycle's test `if dest.exists() and (dest/".git").exists()`
(line 249) routed THOR down the UPDATE branch instead of the CLONE branch;
`git pull` exited 0; the row was rewritten status=updated with a valid
commit hash and a 123 MB size that is the .git directory, not a working
tree. The checkout had failed on a path containing a colon, which is
illegal on Windows and could never succeed.

SHAPE: a status promoted by a code path that cannot observe the defect.
update_repo() (lines 203-215) returns True on a subprocess exit code and
never examines the artifact. The most dangerous kind of green: not a lie,
a measurement of the wrong layer.

## CLY-CAL-007 | 2026-03-23 .. 04-03 | the invisible no-op

BELIEVED, implicitly, by anyone reading the reports: the manifest's three
sections were three working stages.

TRUE: 0 of 8 datasets were ever acquired, and the report template emits
only Repos, Models and Total size. No Clymene report contains the word
"datasets". A declared, documented, schema-backed capability that never
ran once produced no signal of its absence anywhere in the output.

SHAPE: base rule 8 before it was written. A no-op with no reason attached
is indistinguishable from work, and the reporting surface had no slot in
which the gap could appear.

## CLY-CAL-008 | 2026-09-11 | this seat's own comparator, caught by its own control

BELIEVED for one reading: the vault contained a corrupted file. The tree
comparison flagged autogen-landing.jpg as a content mismatch.

TRUE: the upstream blob at that commit is a 131-byte Git LFS POINTER; the
file on disk is the smudged 269 KB image. Its sha256 equals the pointer's
oid exactly (149a1ab7...), so the file is correct and the mismatch was my
instrument comparing a pointer to its own resolved content. After the
correction the vault has ZERO content mismatches: every file that is
present is byte-correct.

SHAPE: a comparator that did not model one of the formats it was reading.
Caught because a single anomaly in an otherwise uniform result was chased
instead of reported. Recorded as a near miss: had it shipped, this seat
would have claimed corruption in an artifact that is intact, and the
direction of that error is the one that flatters an auditor.

## CLY-CAL-009 | 2026-09-11 | the status code from the wrong file

BELIEVED, and written into my own preregistered predicate: a model is
reproducible if a HEAD on "one sidecar-covered file" at the recorded
revision returns 200.

TRUE: for a STUB, the only sidecar-covered files are the public ones
(README, LICENSE, config) -- the files that download before the weights
are refused. Both meta-llama rows therefore returned 200 and were
classified REPRODUCIBLE while their weights return 401. A supplementary
probe that asks for a WEIGHT file shows three artifacts gated, not one.

WHAT IT COST, had it shipped: gemma-2-2b would have been reported
reproducible, the vault would have contained nothing irreplaceable, and
section 3 of the disposition ledger -- the only finding that argues FOR
this seat's continued existence -- would not exist. The error ran in the
direction of my stated recommendation, which is the direction I should
distrust most.

SHAPE: a green check taken from a different object than the one being
claimed about. Identical in form to CLY-CAL-006 (THOR's exit code) and to
the base role's own capability-over-labels rule, committed by this seat on
the same day it wrote that rule into its own file. Knowing the rule is not
the same as having an instrument that obeys it; only the control that
probes the actual object closes the gap.
