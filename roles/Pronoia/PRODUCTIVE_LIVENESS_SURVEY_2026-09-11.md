# Productive-liveness survey -- first specimen pass

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11, measured 17:38Z. Built from 213873bc1 in
Prometheus-worktrees/pronoia-base-role on M2 (SPECTREX5).
Raw rows: roles/Pronoia/science/ledgers/liveness_survey_2026-09-11.json
Instrument: roles/Pronoia/science/liveness_survey.py (a reader; it writes
to no database), classifying with the same derive_health() the Pronoia
loop now uses, so the survey and the instrument cannot drift apart.

BOUNDED, as instructed. This is the heartbeat estate (36 rows) plus three
M2 scheduled tasks whose registry rows could be checked from this host.
It is not a repository audit. Nothing here was restarted, stopped or
repaired.

## The levels, and which ones a heartbeat can actually carry

    L0  process / heartbeat evidence     readable from the table
    L1  eligibility / input evidence     NOT readable from the table
    L2  work-attempt evidence            readable (a column exists)
    L3  work-success evidence            readable (a column exists)
    L4  artifact / state transition      NOT readable from the table
    L5  downstream consumption           NOT readable from the table

The survey script prints L1, L4 and L5 as UNOBSERVED rather than
inferring them. Every L1/L4/L5 finding below was established by hand with
its own command, recorded beside it. The point of the exercise is not to
demand L0-L5 everywhere; it is to find places where an upstream level is
being used as evidence for a downstream claim.

## The headline numbers

    rows in agora.agent_heartbeats                          36
    rows whose status column says the word 'online'         34
    ... of those, whose heartbeat is more than 1 h old      32
    rows carrying NO work evidence of any kind (L2 and L3)  34
    rows whose work evidence is self-contradictory           1
    rows that can be shown PRODUCTIVE                        0

THE LAST LINE IS CORRECTED DOWNWARD FROM THE INSTRUMENT'S OWN OUTPUT, and
the correction is against this seat's interest. liveness_survey.py reports
1 productive row (HealthCheck-M4) because it assumes a one-hour cadence
where a row does not declare one. HealthCheck-M4 is a five-minute probe
whose heartbeat was 42 minutes old. Re-run at its true cadence it is
STALLED:

    HealthCheck-M4   cadence 5 min   -> stalled
                     cadence 15 min  -> stalled
                     cadence 1 h     -> productive   (the assumed value)

So the honest count of demonstrably-productive agents in the heartbeat
estate is ZERO, and the assumed-cadence default is a real weakness of the
instrument, recorded here rather than left to flatter the result. The two
cadence-independent verdicts (NO_WORK_OBSERVED, INCOHERENT) are unaffected.

## Specimen table

Every specimen is something currently REPRESENTED as ACTIVE, PRESENT or
ONLINE. "claimed" is what the system says about itself; "derived" is what
its own evidence supports.

    specimen              claimed   hb age   L2      L3      derived
    ------------------    -------   ------   -----   -----   ----------------
    Pronoia (M4)          online      0.0h   ABSENT  ABSENT  no_work_observed
    MachineProbe-M4       online      0.0h   ABSENT  PRESENT incoherent
    HealthCheck-M4        offline     0.7h   PRESENT PRESENT stalled (at true
                                                             cadence)
    Elenchus (M2)         online      1.4h   ABSENT  ABSENT  no_work_observed
    Apollo (M2)           online   2648.6h   ABSENT  ABSENT  no_work_observed
    Talos (SKULLPORT)     online   2497.7h   ABSENT  ABSENT  no_work_observed
    Atalanta (SKULLPORT)  online   2497.5h   ABSENT  ABSENT  no_work_observed
    Aporia (M1)           online   2787.4h   ABSENT  ABSENT  no_work_observed
    ...28 more rows, all ABSENT/ABSENT

    scheduled task                    registry   measured
    ------------------------------    --------   --------------------------
    SFEngineM2Watchdog                ACTIVE     ACTIVE, and correctly built
    MnemosyneEvidenceWikiWatchdogM2   ACTIVE     ACTIVE, unverifiable by its
                                                 own registered rule
    PrometheusMachineProbeM2          DEAD       DEAD, wrong cause recorded

## Counterexamples

Each is a case where an upstream level was used as evidence for a
downstream claim. Commands are in journal/2026-09-11.md s5.

### C1  ONLINE -> therefore alive.  32 of 36 rows.  ARCHITECTURAL.

The status column is a stored string that nothing ever downgrades.
write_heartbeat() upserts it; when a process dies nothing writes
'offline', so the last word each process said about itself persists
forever. Thirty-two rows assert 'online' with heartbeats between 1.4 and
2,787 hours old. Aporia, Clio-test and Calliope have been "online" for
116 days.

This is the whole fleet's liveness signal, and it is not one. The base
role already ruled that "old Agora heartbeat 'online' fields are labels
whose meaning has expired"; this is that ruling with a number on it.

### C2  ONLINE -> therefore working.  Pronoia.  LOCAL instance of C1.

Measured in the adoption pass and unchanged: pid 9620 on M4 beating every
60 s with status='online' while all five pronoia_* stages wrote 0 rows
for 62 hours. Patched this pass (PRON-03); not yet deployed.

### C3  NO LOG LINES -> therefore dormant.  ARCHITECTURAL, and it fires
###     in the FALSE-ALARM direction.

roles/base-role/MONITORS.md registers MnemosyneEvidenceWikiWatchdogM2
with freshness source `evidence_wiki/derived/watchdog.log` and a dormancy
threshold of "15 min without a log line".

Measured: the log's last line is 2026-09-04T12:38, SEVEN DAYS old. By its
own registered rule the watchdog has been dormant for a week.

It has not. The scheduled task last ran 2026-09-11 13:35:01 with result
0, and the service it guards answers HTTP 200 (probed independently from
this host). The log is silent because the script only writes on FAILURE
and restart.

So a healthy watchdog and a dead watchdog produce the IDENTICAL
observable: nothing. The registry row itself predicted this -- it says
"NEEDS a last-success line when the service answers, not only when it
restarts" -- which makes this a known defect that has not been repaired,
not a discovery. What is new is that it is not unique: the SFEngine M2
watchdog logs only on failure too. Two of two watchdogs inspected.

### C4  SCHEDULER FIRED + EXIT 0 -> therefore the job did its work.

The registry gets this one RIGHT, and it is included as the control that
shows the registry is not uniformly wrong: PrometheusMachineProbeM2 is
registered DEAD, and it is dead -- it fires every 5 minutes and returns
0x80070002 (ERROR_FILE_NOT_FOUND) every time, most recently 13:32:32.

But the recorded CAUSE is wrong. MONITORS.md says "file not found; cwd is
the canonical checkout". Measured: scripts/machine_probe.py is PRESENT,
and the task's "Start In" is set to the repository root, so the script
path resolves. The missing file is the interpreter: the task runs
`pythonw.exe` unqualified, and the only pythonw.exe on this user's PATH
is the per-user WindowsApps execution alias
(AppData/Local/Microsoft/WindowsApps), which does not resolve in a
scheduled task's security context.

Correct verdict, wrong diagnosis -- which matters, because anyone acting
on the recorded cause would go and fix a working directory. Not repaired:
the row's owner is unclaimed and this is not this seat's lane.

### C5  THE POSITIVE CONTROL.  One instrument in the estate is built right.

SFEngineM2Watchdog does what every other specimen here fails to do: it
verifies the PROPERTY, not the label.

    $probe = curl -s -m 5 --cacert m2.crt https://192.168.1.191:8811/v2/version
    if ($LASTEXITCODE -eq 0 -and $probe -match '"api"\s*:\s*"v2"') { exit 0 }

It matches the response BODY, not merely a 200 or an exit code; it
restarts on failure, re-probes, and exits 1 if the restart did not take.
Its registered freshness source is the TASK RESULT rather than its log,
which is the correct source given that the log is failure-only.

Verified independently from this host: the endpoint returns
{"api":"v2","schema_version":4,...}, and the watchdog's log shows it
genuinely restarting the engine twice today (12:47, 12:55).

This is the template the invariant in section 6 generalises. It is also
the reason this survey does not conclude "the fleet is broken": one
specimen shows the correct pattern is cheap and already in use here.

### C6  SUCCESS WITHOUT AN ATTEMPT.  MachineProbe-M4.  LOCAL.

The only row in the estate that writes last_work_success_at without ever
writing last_work_success_at's precondition: last_work_attempt_at is
NULL. derive_health returns INCOHERENT at every cadence.

This is not an accusation about the writer; the usual cause is exactly
what it looks like, a writer that records its good news and not its
attempts. It is recorded because the cheat control in
test_productive_liveness.py was written to catch this class BEFORE the
estate was read, and then the class turned out to have a real member.

### C7  THE CAPABILITY EXISTS AND IS UNREACHABLE FROM THE TREE.
###     ARCHITECTURAL, and the most consequential finding here.

agora.agent_heartbeats has had last_work_attempt_at, last_work_success_at,
health, last_persist_ok_at, persist_fail_streak and run_id all along.

    git grep -l 'last_work_success_at' origin/main
        -> only roles/Pronoia/* documents written by this seat today

No tracked Python writes those columns. No tracked SQL creates them. The
two rows that populate them (MachineProbe-M4, HealthCheck-M4) are written
by code that exists only on M4 and is not in the repository.

So the fleet's one correct pattern is invisible to every seat that reads
the tree, and 34 of 36 agents use the tracked writer, which until this
pass could not populate the columns even if a caller wanted to. The
schema was ahead of the code by months and nobody could see it.

## 5. Local bugs versus repeated architectural patterns

    LOCAL (one site, one owner, small fix)
      C2  Pronoia's heartbeat writer            patched this pass, undeployed
      C4  MachineProbeM2's interpreter path     unclaimed owner; not repaired
      C6  MachineProbe-M4 success-without-       M4-local code, not in tree
          attempt

    ARCHITECTURAL (repeats across independent implementations)
      C1  status is a write-once label with no expiry and no downgrade
          path.  32 of 36 rows.  Every daemon that ever booted.
      C3  monitors log only failures, so silence is ambiguous between
          health and death.  2 of 2 watchdogs inspected.
      C7  the schema carries work-state capability that no tracked code
          can reach.  34 of 36 rows use the writer that lacked it.

The test that separates them: C2, C4 and C6 are one site each and a
different person would not have made the same mistake. C1, C3 and C7 were
made independently by different authors at different times against
different infrastructure -- including twice by this seat, four months
apart, in different languages (calibration LEDGER PRON-CAL-002 and
PRON-CAL-003). That is the signature of a missing invariant rather than a
missing fix.

## 6. The smallest reusable invariant the specimens justify

Offered as a recommendation, not installed. One sentence:

    A STATUS IS NOT EVIDENCE. A claim that something is working is only
    admissible together with the TIMESTAMP OF THE OBSERVATION that
    justifies it and the CADENCE that observation was due at; the verdict
    is then DERIVED from those, never stored as a word.

Why this one and not a larger framework: it is the minimum that kills C1,
C2, C3 and C6 simultaneously, and it is already executable and tested --
derive_health() is 60 lines, takes only timestamps, and is proven to
degrade on wall-clock alone (test_T4). It requires no new service, no new
table and no new daemon. C5 shows the pattern already works in this
fleet.

What it does NOT cover, said plainly: L1, L4 and L5. Eligibility,
artifacts and consumption are not inferable from a heartbeat and this
invariant does not pretend to reach them. A monitor obeying it can still
be measuring the wrong thing productively. That is a different and
larger problem and one afternoon's specimens do not justify a design for
it.

RECOMMENDED SCOPE IF ADOPTED: new and repaired writers only. Backfilling
34 dead rows would manufacture work to make a monitor green, which is the
thing this seat is forbidden to do. The correct treatment of the 32 stale
'online' rows is that readers stop trusting the word, not that someone
rewrites the rows.

## 7. What this survey does NOT establish

- Not that the fleet is broken. 34 rows with no work evidence is a
  statement about the INSTRUMENTATION, not about whether those agents
  ever did useful work. Most of them are seats that were correctly shut
  down months ago and whose row was simply never updated.
- Not that any of these agents should be restarted. Nothing here is an
  argument for reviving anything.
- Not that derive_health's thresholds are right. They were fixed before
  the data was read (test_stall_multiple_is_not_tuned_to_let_era2_pass
  guards that), and the HealthCheck-M4 case above shows the assumed
  cadence is a real source of error.
- Not that L5 was examined anywhere. No specimen in this table has a
  demonstrated downstream consumer, including Pronoia's own dashboard.
  That gap is PRON-05 and it is unanswered.
