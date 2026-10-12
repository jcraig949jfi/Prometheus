# RELIABILITY TEST -- 4 h unattended research window (Cosmos, ubu003-623ec771). Prereg 2026-10-11, before start.

Authority: operator, 2026-10-11 ("repair the launcher and implement a progress watchdog with a tested
failure-injection scenario ... execute EXP-04 ... final packet, and run a four-hour autonomous reliability test.
Only after that test demonstrates genuine unattended progress should we authorize another multiday campaign").
Constraints unchanged: no D2, no other sealed holdout, no confirmation data, $0, G-0006 not revived,
autopsy branch never pushed, cosmos/c4-v03 not merged.

## Mechanism under test (what failed on 2026-10-08, and what replaces it)
1. Every job runs under `python -m prometheus.cosmos.supervise launch --stall S` (progress, not liveness).
2. INDEPENDENT WAKE: a session scheduler fires an hourly prompt (minute :17) regardless of job state. Each wake:
   read PROGRESS of the running job, renew the lease, append an ASCII status to STATUS_LOG.md here, commit +
   push, and if no job is running start the next queue item (or formulate one) -- never idle.
3. While a job runs, a Monitor streams watchdog events (stalled / killed / restart / final) and a 2-minute row
   count, so a stall surfaces within the stall limit.
Known limitation (stated before the test, not discovered after): the scheduler and monitor live in this Claude
session. If the session process itself dies, nothing wakes Cosmos. An OS-level timer independent of the agent is
the next step and is out of scope here.

## Queue (in order; each science item has a prereg committed before its data)
Q1 EXP-05 stig RETURN vs ACCUM (prereg fdd6097f0 on cosmos/c4-v03), 160 jobs, stall 900 s.
Q2 EXP-05 analysis by its rules; RESULT committed.
Q3 EXP-06 instrument qualification of the EXP-04 surrogate: cause of the uniform underprediction on planted
   reservoirs (prereg to be committed before its run).
Q4 further items formulated during the window from Q1-Q3 outcomes (each preregistered before data).

## Pass criteria (fixed now; ALL must hold)
P1 four hourly status entries (h1..h4) in STATUS_LOG.md, each committed within 20 min of its scheduled time.
P2 every launched job reaches a terminal verdict (DONE / FAILED / STALLED) in its run record; no job is ever
   "running" with no new result for longer than its stall limit + 2 min without a watchdog event.
P3 no gap > 30 min in which no job runs and no reason is logged.
P4 lease renewed at each wake; never expired during the window.
P5 at least two preregistered results committed (Q1/Q2 plus one more).
P6 zero constraint violations.
FAIL on any miss; the failing clause is reported. A FAIL means: no multi-day window.
