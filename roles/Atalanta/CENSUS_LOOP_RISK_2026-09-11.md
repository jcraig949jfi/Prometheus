# Census: which registered loops carry the Atalanta structural risk

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. ATALANTA-04 question 4, on the operator's ruling.
INSPECT ONLY: no file, row, task or process belonging to another seat was
modified. Built from origin/main 05b1134e6 in
D:\Prometheus-worktrees\atalanta-base-role.

Population: all 30 rows of roles/base-role/MONITORS.md at 05b1134e6,
enumerated programmatically, not sampled. Eligible count = 30; examined
= 30.

## 1. The risk predicate, stated before the data

A loop carries the Atalanta risk if it CAN run indefinitely while
producing zero domain output. That requires all three of:

    C1  its input is bound by GUESS (a path, name or endpoint the
        consumer's own author chose) rather than by a producer's
        declaration -- so it cannot tell its own misconfiguration from
        its producer's death
    C2  nothing BOUNDS its consecutive no-ops: no self-park, no
        automatic dormancy, no stop
    C3  its alarm has no ACCOUNTABLE RECIPIENT: no named seat, no
        delivery, no defined outcome if nobody responds

Any one control present and working bounds the failure. All three absent
is the Atalanta shape.

Grades: C1/C2 are graded VERIFIED only where this seat read the source
today. Where it did not, the cell reads NOT_EXAMINED -- not "absent".
"Nothing fired" and "nothing could have fired" are different facts and
both are reported.

## 2. Control C3 across the whole population (determinable for all 30)

Read from the registry's alarm-route column. Three classes:

    ROUTED_ACTING    something automatically CHANGES on the alarm
    ROUTED_PASSIVE   a status file and/or "the operator": a destination,
                     not an obliged recipient with a defined outcome
    UNROUTED         "none", "none yet", "none routed", "--"

    UNROUTED                                                18 of 30
    ROUTED_PASSIVE                                           9 of 30
    ROUTED_ACTING                                            3 of 30

The three ROUTED_ACTING, and what makes them real:

    SFEngine            Vivarium's consumer HALTS on UNREACHABLE
                        (conformance gate). A machine acts.
    Vivarium consumer   stranded-row check; a defined artifact is
                        produced and a row cannot be silently resolved.
    comms queue         the operator's broadcast view, plus the queue
                        itself is the delivery mechanism.

The nine ROUTED_PASSIVE (ArchaeonTick, Hermes mailer, Hephaestus jobs,
Apollo mining, KairosClaimLint, ArachneSwarm, IcarusDaemon,
PolyhymniaDaemon, Ludus) all name a STATUS FILE and/or "the operator".
This is the same class of destination as Atalanta's own alarm, which
wrote 305 failure rows into a table nobody queried for three months.
KairosClaimLint is the strongest of the nine because it also posts ATTACK
findings to a claim's owner via comms; it is a borderline case listed
conservatively as passive because the DORMANCY alarm itself still routes
to a status file.

## 3. Control C2 where the source was read today (VERIFIED)

Four daemons share one May-era template. In all four the anti-silence
branch emits and falls through: no return, no exit, no parked flag, and
the condition is `>=` so it re-fires every subsequent tick forever.

    agents/atalanta/daemon.py:547     threshold 50, no stop   VERIFIED
    agents/pheme/daemon.py:495        threshold 50, no stop   VERIFIED
    agents/polyhymnia/daemon.py:442   threshold 50, no stop   VERIFIED
    agents/talos/daemon.py:615        threshold 50, no stop   VERIFIED

Rows those four alarms actually wrote into
agora.intelligence_outputs, every one success=false (raw:
roles/Atalanta/ledgers/telemetry_census_2026-09-11.md):

    pheme_self_audit_null            305
    atalanta_self_audit_null         305
    polyhymnia_self_audit_null        23
    talos_self_audit_null              8
    TOTAL                            641

641 alarm rows, all flagged as failures, written 2026-05-23 to 05-29,
never queried by any seat that this seat can find. C2 absent and C3
absent, together, in four agents, quantified.

## 4. The live subset: loops that are running RIGHT NOW and producing nothing

This is the part of the census that is not history.

### 4.1 PrometheusMachineProbeM1 and PrometheusMachineProbeM2

Registry state: DEAD for both. Measured on this host today (M2, G1):

    State           Ready
    Trigger         PT5M  (every five minutes)
    LastRunTime     2026-09-11 12:02:32
    LastTaskResult  0x80070002
    NextRunTime     2026-09-11 12:07:31
    NumberOfMissedRuns 0
    Action          pythonw.exe D:\Prometheus\scripts\machine_probe.py
                    --machine M2 --interval 60
    WorkingDirectory D:\Prometheus  (the canonical checkout)

This is the Atalanta shape, live. It fires on schedule, fails identically
every time, has no alarm route, has no owner (the M1 row says OWNER
UNCLAIMED), and nothing bounds it. Atalanta managed 354 failures in seven
days at one per thirty minutes; a five-minute trigger produces 288 per
day per host.

CAUSE: UNRESOLVED, and two hypotheses are eliminated rather than left
hanging.

    ELIMINATED  "the script is missing" -- the registry row attributes
                0x80070002 to "file not found; cwd is the canonical
                checkout". scripts/machine_probe.py EXISTS at the exact
                invoked path (G1, both in the canonical checkout and in
                this worktree, 11,055 bytes, tracked since af828e1a7).
    ELIMINATED  "the bare exe name resolves to a Windows Store App
                Execution Alias stub". The alias at
                ...\WindowsApps\pythonw.exe is indeed a 0-byte reparse
                point (G1) and a real interpreter exists at
                ...\Programs\Python\Python312 -- so this seat expected
                this to be the cause. It then TESTED it: a direct
                CreateProcess on the bare name "pythonw.exe" with
                UseShellExecute=false and WorkingDirectory=D:\Prometheus
                SUCCEEDED, exit 0 (G1). Hypothesis falsified by its own
                author before publication.

    The discriminating next test belongs to the row's owner: run the
    registered action under the task's own principal and capture the
    launch error, or re-register with an absolute interpreter path and
    observe whether the result code changes. This seat did not run it,
    because changing or triggering another seat's scheduled task is
    outside its lane.

### 4.2 The other ACTIVE loops with no alarm route

    MnemosyneEvidenceWikiWatchdog      ACTIVE, UNROUTED
    MnemosyneEvidenceWikiWatchdogM2    ACTIVE, UNROUTED
    SFEngineM2Watchdog                 ACTIVE, UNROUTED
    PEWBackupDaily                     ACTIVE, UNROUTED
    PEWRestoreVerifyWeekly             ACTIVE, UNROUTED
    PrometheusBackupWeekly             ACTIVE, UNROUTED

These are NOT the Atalanta shape and should not be reported as such. A
backup or a watchdog has a real product per run, so a no-op is not a
legitimate success for it; C1 does not apply because the input is the
thing being backed up or probed. Their exposure is C3 only: if they
start failing, the failure has nowhere to go. The Mnemosyne watchdog row
already carries its own sharper version of this, noted by its owner --
it logs when it RESTARTS the service but not when the service answers,
so its silence is ambiguous between health and death.

Two of the six carry a documented sub-risk worth naming for their owners:
PrometheusBackupWeekly runs from the canonical checkout (allowed, read
only, per the row), and the Mnemosyne watchdog restarts without notifying
-- an automatic remediation with no record of how often it fires is a
loop that can hide a permanent fault as a stable rhythm.

## 5. The historical set: loops that already exhibited the failure

    AtalantaPrimitiveHunterLoop  354/354 null, 305 alarms, 0 output
    PhemeDemandVoicerLoop        354/354 null, 305 alarms, 0 profiles
    TalosCorpusDaemon            160 of 170 ticks null, 8 alarms
    PolyhymniaDaemon             250 null ticks after saturation, 23 alarms
    CoeusRebuildTrigger          input stopped 2026-03-27, unrouted
    ClymeneHoardCycle            input gate reads, no host, unrouted
    EosDaemon                    dormant since 2026-05-17, unrouted
    AletheliaReport              no host, unrouted
    Elenchus shadow loop         input stopped 2026-09-01, alarm route
                                 explicitly "none -- THIS IS THE DORMANT
                                 WATCHDOG"
    Portfolio brief producer     dormant since 2026-09-09, found only
                                 because a seat went looking

Atalanta and Pheme are the maximal pair: launched in the same commit, the
same night, ticking within a second of each other, both 354/354, both 305
alarms. They are one failure that was deployed twice, not two failures.

## 6. Counts

    registered loops                                    30
    with no alarm route at all                          18
    with a route to a status file or "the operator"      9
    with a route where something automatically acts       3
    verified to have an alarm that cannot stop the loop   4
    alarm rows written by those four, all success=false 641
    currently firing and failing every run                2  (the probes)
    currently ACTIVE with no alarm route                  7

## 7. What this census does not establish

- C1 and C2 are NOT_EXAMINED for the 26 loops whose source this seat did
  not read. The four VERIFIED cases are the four that share one template;
  a template defect is not evidence about loops built from other
  templates, and this census does not claim it is.
- The C3 classification is read from prose in the registry, written by
  each loop's own owner. A row that says "none yet" may have an informal
  route its owner knows about. The fix for that ambiguity is a structured
  field, not a better reading.
- The two probes' failure cause is unresolved (section 4.1). The census
  reports a live failing loop and two eliminated hypotheses, not a
  diagnosis.
