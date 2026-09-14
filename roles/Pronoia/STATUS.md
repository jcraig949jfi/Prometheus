# Pronoia -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11, written at the close of the adoption pass.
Built from 363120e08665af062d40810183624fa23ed19698 on branch
pronoia/base-role-adopt-2026-09-11 in
Prometheus-worktrees/pronoia-base-role, host M2 (SPECTREX5), dirty=false
at boot.

## 1. State

    SEAT           BLOCKED -- on an operator decision (PRON-01), not on
                   a seat. The adoption pass the operator assigned is
                   complete; there is no second assignment.

    ERA 1 CODE     RETIRED, and the retirement is only partly real.
                   pronoia.py was deleted from the tree 2026-04-23
                   (3b3c74bc0) and gitignored (.gitignore line 174). A
                   runnable 32,165-byte copy survives on M2 at the
                   repository root, untracked and invisible to any seat
                   reading the tree. Its publish step commits and pushes
                   to main from the canonical checkout, which D-23
                   forbids three ways. PRESENT, NOT ACTIVE, NOT
                   PRODUCTIVE, NOT VALID.

    ERA 2 LOOP     ALIVE AND NOT PRODUCING -- the finding of this pass.
                   scripts/intelligence_loop.py is running on M4 as pid
                   9620 and heartbeat-writing every 60 s with
                   status='online'. All five of its pronoia_* work
                   stages have written 0 rows since 2026-09-09, against
                   6 per day for the five days before. The newest
                   dashboard push on origin/main is 62.6 h old. PRESENT,
                   ACTIVE, NOT PRODUCTIVE; VALID is not yet answerable.

    HEARTBEAT      DEFECTIVE, and it is this seat's own code.
                   agora.agent_heartbeats has last_work_attempt_at,
                   last_work_success_at and health. Pronoia's writer
                   populates none of them; all three are NULL. That is
                   why "alive" and "working" are indistinguishable for
                   this loop, and it is a two-line fix in a file this
                   seat owns.

    REGISTRY       TWO ROWS CORRECTED on this pass, both annotated
                   rather than rewritten: the Era 2 loop's owner
                   (registered UNCLAIMED / Hermes lineage; the evidence
                   says Pronoia) and its input (registered as dead
                   May-era tables; both tables took writes minutes
                   before the measurement).

## 2. What was done on this pass, and what was not

DONE: worktree created from a recorded base SHA and the
canonical-checkout guard verified; base-role chain read; Era 1
archaeology performed from the 42 committed log files, the deleted
source at 3b3c74bc0^, and the surviving on-disk copy; Era 2 archaeology
performed from the source, the git auto-commit stream and the canonical
Postgres; roles/Pronoia/ created; own rows added to INHERITANCE.md and
MONITORS.md; comms boot and sync; journal, backlog, calibration ledger,
receipt.

NOT DONE, deliberately: no loop started, no loop stopped, no process on
M4 touched, no dashboard or brief regenerated, no email sent, no
scheduled task created, no file deleted (including the hazardous
untracked pronoia.py), no other seat's file rewritten, no claim
promoted. The operator's directive was bootstrap and registration only.

ONE CONTRACT BREACH BY THIS SEAT, self-reported: the pass opened with
`git pull` in the canonical checkout, before D-23 had been read. It was
killed before it reached a mutating step and the tree was verified clean
(no MERGE_HEAD, no index.lock, HEAD unmoved). The correct sequence
(fetch, record origin/main, worktree add) was then followed. Recorded as
PRON-CAL-003. Atalanta made the identical mistake earlier today (L-09),
which is evidence the wake directive's wording is the defect and not
either seat's reading of it; D-23 section 3 already says so.

## 3. The recommendation, if the operator wants one

The seat's own reading, offered because the base role says take a stand
and assume you are wrong.

DO NOT revive Era 1. The research-scanning chain was archived as a unit
by two program reviews, four of its six agents are BLOCKED or DORMANT
seats today, and its audit stage is falsified in detail in
RESPONSIBILITIES.md section 0.1. There is nothing to restart.

DO NOT re-charter this seat as an orchestrator. "Run the fleet's loops"
is the mission that produced both eras, and both eras optimised a
throughput metric that satisfied itself. A third attempt would be the
same shape.

THERE IS ONE NARROW THING WORTH DOING, it is small, and it is this
seat's own defect rather than a proposal about anyone else's work:

  (a) Make the heartbeat carry work state. Populate
      last_work_attempt_at, last_work_success_at and health in
      _start_pronoia_pg_heartbeat (scripts/intelligence_loop.py:79).
      The columns already exist and are NULL. Until they are written,
      no query anywhere in this program can distinguish a Pronoia that
      is working from a Pronoia that is merely alive, which is the exact
      condition measured today.

  (b) Then answer the question the fix makes answerable: is Era 2's
      four-hour dashboard push dead, or merely late? Today's evidence
      says dead (about 15 consecutive missed cycles, 0 of 5 stages
      across three days) but the restarted process was under two hours
      old at measurement and the INDETERMINATE branch is honestly open.
      A single field would close it.

Both need a host this seat cannot reach. (a) is a two-line change to a
committed file and could be made here and deployed by whoever owns M4;
(b) is a read, once (a) has run for a day.

IF THE ANSWER TO (b) IS "DEAD", the honest outcome is to record that,
stop the loop rather than leave a green heartbeat over a corpse, and
leave this seat PARKED. A dashboard nobody can trust is worse than no
dashboard, because its green state is consumed by the operator as
evidence about the fleet.

WHAT WOULD FALSIFY THIS RECOMMENDATION: a consumer who reads
docs/portfolio_brief.md or docs/state.json and would notice their
absence -- that would make Era 2 load-bearing and the repair urgent
rather than optional. This seat did not find such a consumer and did not
look hard, because the operator's directive did not extend to it. The
absence of a search is not the absence of a consumer, and this line
exists so that gap is not read as a finding.

## 4. Conflict of interest

Declared, and it is sharper than most.

This seat is reporting on the disposition of its own two historical
programs, and the substantive finding is a defect in its own currently
running code. A seat auditing its own loop has an obvious incentive to
report that loop healthy -- which is precisely what that loop's
heartbeat has been doing unaided for two and a half days.

The numbers chosen for section 0.1 of RESPONSIBILITIES.md are the
unflattering ones: 0 of 37 HEALTHY verdicts, 3 of 5 detectors that never
produced a finding, 1 detector that fired 27 times on another process's
memory, and this seat's own report card reading "HEALTHY / Recent Log
Lines: 0". The Era 2 finding is stated with its INDETERMINATE branch
open rather than closed in the direction that would make the finding
more impressive.

The calibration ledger opens with three rows against this seat,
including one for a contract breach committed during this very pass.

## 5. Next executable action

None without an operator decision. PRON-01 in
roles/Pronoia/BACKLOG_H0H5.md states it in one line: does this seat
exist, and if so does it own fleet liveness instrumentation or nothing.

If the operator says nothing, this seat stays BLOCKED, does not start a
loop, and does not invent work inside another lane. The Era 2 loop on M4
keeps running and keeps producing nothing; that is now recorded in
roles/base-role/MONITORS.md where the next seat to look will find it,
which is the only outcome this pass was authorised to produce.

---

# Addendum, 2026-09-11: first active mission

Built from 213873bc1 on branch pronoia/base-role-adopt-2026-09-11.
Seat state changed from BLOCKED to ACTIVE for this mission by the
operator's directive, and returns to BLOCKED on PRON-01 at its close.

## 6. If Pronoia disappeared tomorrow, what would tell Prometheus?

The operator asked, and warned that "the heartbeat would stop" is the
wrong answer. It is, and for a reason worth stating precisely rather than
conceding.

THE FAILURE OF THIS SEAT IS SILENT BY CONSTRUCTION. That is not modesty;
it is the structural property that makes the job dangerous. An auditor of
productive liveness produces verdicts and corrections. If it stops, no
verdict becomes wrong -- the existing ones simply stop being renewed, and
every row it would have corrected keeps asserting exactly what it
asserted before. Thirty-two rows in agora.agent_heartbeats have said
'online' for up to 116 days; if this seat vanished, they would go on
saying it, and nothing anywhere would change state. A dead Pronoia and a
working Pronoia that found nothing produce the identical observable,
which is C3 from the survey turned on its author.

So the answer cannot be a signal this seat emits. It has to be a
consequence in someone else's data:

  1. THE PRIMARY OBSERVATION, and the one this seat has now wired:
     the count of rows in agora.agent_heartbeats carrying a non-NULL
     last_work_success_at stops rising. It is 2 of 36 today, both written
     by untracked M4-local code. If this seat is doing its job that
     number climbs as writers adopt the patched write_heartbeat; if the
     seat stops, it freezes. It is a count anyone can take in one query,
     it lives in a database this seat does not own, and it cannot be
     faked by this seat writing about itself.

  2. roles/Pronoia/science/ledgers/liveness_survey_*.json stops gaining
     dated files. Registered in roles/base-role/MONITORS.md with a 30-day
     threshold, so the ABSENCE of the artifact is the alarm rather than
     the absence of a heartbeat. This seat is thereby subject to its own
     instrument, which it should be.

  3. The sharpest one, and the least comfortable: MONITORS.md rows go
     back to being written by the seats they describe, with nobody
     checking a row against the freshness source the row itself names.
     Two of two Pronoia-relevant rows were wrong on 2026-09-11 and two
     more were wrong or mis-caused in this mission's survey. If nobody is
     finding a wrong row every pass, either the registry has become
     correct or nobody is looking -- and those two are distinguishable
     only by someone taking the measurement.

THE HONEST COROLLARY. All three of those observations require a person or
a seat to go and look. None of them pages anybody. This seat has not
solved its own problem; it has made its failure detectable-on-inspection
rather than invisible, and it is saying so rather than claiming a
watchdog it does not have. A seat whose own dormancy is only visible to a
volunteer is exactly the shape base rule 7 names, and the correct fix is
an external consumer with a reason to care -- which is PRON-05 (name a
consumer), still unanswered.

## 7. Mission state at close

    PRON-02  CLOSED. Ghost actuator deleted from M2 after its evidence
             was committed. Content recoverable at
             git show 3b3c74bc0^:pronoia.py. Three untracked triggers
             remain and are now inert; reported, not removed.
    PRON-03  PATCHED AND TESTED, NOT DEPLOYED. 45 tests pass. The loop
             runs on M4, which this seat cannot reach. Until someone
             deploys it, Pronoia's own row still reads no_work_observed,
             and that is the truthful reading.
    SURVEY   DELIVERED. 36 rows, 7 counterexamples, 0 agents
             demonstrably productive, 3 architectural patterns and 3
             local bugs separated.
    SEAT     Returns to BLOCKED on PRON-01.
