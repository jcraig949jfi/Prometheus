# Pronoia -- calibration ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Kept because it is unflattering (base role,
doctrine). One row per wrong call by this seat or its historical
programs: what was believed, what was true, and the SHAPE of the error.

## PRON-CAL-001 | 2026-03-23 to 2026-04-01 | Era 1's audit, its central claim

BELIEVED: that a pipeline audit which reads each agent's captured stdout
and greps it for "429", "error" and a short-output condition is a
measurement of pipeline health, reportable as HEALTHY / DEGRADED /
UNHEALTHY.

TRUE: it measured the free-tier rate limits of five external APIs. The
status word returned UNHEALTHY 27 times and DEGRADED 10 times and
HEALTHY zero times in 37 runs, because a single "429" substring anywhere
in any one of six agents' logs forced the worst verdict for the whole
cycle. Nothing in 37 reports distinguished "the pipeline is failing"
from "arXiv throttled us again".

SHAPE: graded the self-report, never the property. The audit had access
to the artifacts -- the digest, the knowledge-graph counts, the brief --
and compared none of them to anything. This is base rule 2 ("verify the
property, never the label") at the orchestration layer, and it was
committed five months before that rule was written against three other
seats' evidence.

## PRON-CAL-002 | 2026-03-31 | Era 1's health report, on itself

BELIEVED, verbatim from
agents/pronoia/logs/health_intelligence_enhanced_2026-03-31_191441.md:

    ### PRONOIA
    - **Status**: HEALTHY
    - **Process Running**: Yes
    - **Recent Log Lines**: 0
    - **Errors**: 0

TRUE: zero log lines is not evidence of health; it is the absence of
evidence, and the report converted it into the strongest positive
verdict it had. Two other counters in the same block, "Errors: 0" and
"Warnings: 0", are derived from the same empty input and inherit the
same emptiness while reading as corroboration.

SHAPE: silence read as health, then triple-counted. This is the defect
base rule 7 exists to name ("a dead watchdog is itself a failed
instrument"), and these committed reports are the earliest dated
specimen of it in this repository.

## PRON-CAL-003 | 2026-05-23 to today | Era 2, the same error in a new language

BELIEVED: that a 60-second heartbeat thread dual-writing to Postgres,
with status='online' and a cycles_today counter in status_json, tells a
reader whether the Pronoia loop is doing its job. The commit that
shipped it is titled "Pronoia: dual-write heartbeat to Postgres (parity
with Apollo/Hephaestus)"; parity with two other agents was the stated
standard.

TRUE, measured 2026-09-11T16:58Z: the heartbeat has been writing
'online' every 60 seconds from pid 9620 on M4 while all five pronoia_*
work stages have written 0 rows since 2026-09-09, against 6 per day for
the five days before. The table it writes to already has
last_work_attempt_at, last_work_success_at and health. All three are
NULL and have never been written by this loop.

SHAPE: identical to PRON-CAL-002, four months later, by the same seat,
against a schema that had already been given the columns to prevent it.
The lesson did not transfer because it was never written down anywhere a
later author would look -- which is why PRON-07 exists in the backlog.

This is also the seat's standing conflict of interest in one row: the
instrument that would have caught this was this seat's own, and its
failure mode was to report this seat healthy.

## PRON-CAL-004 | 2026-09-11 | this seat, on this pass, first action of the session

BELIEVED: that the operator's wake directive "pull the latest from the
repo first" meant `git pull`, and that running it in D:\Prometheus was
the obvious way to start.

TRUE: D:\Prometheus is the canonical checkout (git rev-parse --git-dir
equals --git-common-dir), where D-23 section 1 forbids every mutating
git operation, and section 3 forbids `git pull` outright and states
that a wake directive saying "pull the latest first" MEANS fetch, record
origin/main, then worktree add. The command ran for about two minutes
before it was killed; the tree was then verified unchanged (HEAD
unmoved, no MERGE_HEAD, no index.lock) and the correct sequence
followed.

SHAPE: acted before reading the contract that governed the action. The
mitigating fact is not a defence: D-23 section 3 records that Atalanta
made the identical mistake earlier the same day (L-09) and concludes the
directive's WORDING is the defect. Two seats failing the same way on one
day is evidence about the instruction, not about the seats. The
non-mitigating fact is that this seat had the contract available and
started work before reading it.

CAUGHT BY: reading WORKING_CONTRACT.md section 3 while the pull was
still running in the background.

## PRON-CAL-005 | 2026-09-11 | this seat, caught before it shipped

BELIEVED, briefly, while drafting the Era 2 finding: that the M4 host
event on 2026-09-10 explained the productivity collapse, making the
finding uninteresting.

TRUE: it explains 09-10 and not 09-11. On 09-11 the host is demonstrably
back -- observability_canary wrote 8 rows, machine_health_m4 wrote 2,
agent_started wrote 1 -- and all five pronoia_* stages are still at
zero. The host event was a rival explanation that the data separates.

SHAPE: nearly accepted the first sufficient-looking cause and stopped.
The correction cost one query. Recorded because the base role's standard
is to test the simplest explanation first AND to report what separated
it, and because the INDETERMINATE branch that survives this correction
(the restarted process was under two hours old at measurement) is stated
in the finding rather than buried.
