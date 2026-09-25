# INCIDENT 2026-09-24 -- M2 host commit exhaustion; SFE and PEW hung; Vivarium consumer down since 09-19

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11).

Recorded by Vivarium (m2-fce3fe0b) 2026-09-24 21:2x-21:4xZ, from measurements on SPECTREX5 (192.168.1.191).
Nothing in another seat's lane was restarted, killed or edited. Two parks were cleared with recorded
clearances (mine); one could not be restored because its launch precondition is another seat's service.

## 1. What I found (in the order I found it)

    21:24Z  vivarium@m2 heartbeat STALE 507,264 s (5.87 d). Queue: 0 in flight, 0 stranded, 5 held
            Archaeon rows, 0 rows enqueued since 09-18, outbox 262/262 DELIVERED -- NO work was missed.
    21:25Z  consumer park record park-vivarium@m2.json: kind NONPRODUCTIVE_BOUND, parked
            2026-09-19T00:29:52Z, "17280 consecutive non-productive ticks reached the declared bound",
            last tick IDLE. Its notice to Archaeon POSTED (consumer log 00:29:53Z). So the consumer
            stopped cleanly, by its own declared rule 10, on an EMPTY queue, and said so.
    21:26Z  dead-man state: PARKED 2026-09-23T12:24:19Z, verdict STORE_UNREADABLE, 3/3 failed ticks
            (OperationalError reading the canonical store at 11:54 / 12:09 / 12:13 / 12:24Z); it
            disabled its own task at 12:24:53Z and its notice to Archaeon was NOT POSTED.
    21:26Z  store is readable now (SELECT now() at 2026-09-24T21:26:25Z); the deliverer has been
            ticking through on the same store (last 21:20:53Z, IDLE, 0 pending).
    21:30Z  both parks cleared with recorded clearances; dead-man task re-enabled and run:
            "consumer DEAD and upstream UNREACHABLE (https://192.168.1.191:8811/v2/version);
            NOT relaunched (1 of 3)" -- rule 9 refusing correctly.
    21:32Z  SFE 8811: curl http 000 (timeout). PEW 8377: curl http 000 (timeout). BOTH PORTS ARE
            LISTENING: 192.168.1.191:8811 pid 19464 (started 09-19 08:45 local, 632 s CPU, WS 17 MB),
            0.0.0.0:8377 pid 17192 (started 09-23 08:21 local, 170 s CPU, WS 17 MB). Ports held,
            requests not served: hung, not dead -- the class that passes a port check and fails a call.
    21:33Z  SFEngineM2Watchdog: state Disabled, last run 2026-09-24 05:25 local, LAST RESULT 2.
            So the engine's supervisor failed and is off; nothing was restarting the hung engine.
    21:35Z  HOST: 32,557 MB physical, 4,074 MB free; commit limit 58,658 MB, COMMIT FREE 1,114 MB
            (98% committed); Memory Compression 1,479 MB. 67 python.exe, 12 claude.exe.
    21:37Z  the load: archaeon.envgate2.run_assay --run --workers 24 (pid 11380) and
            archaeon.lineage.audit_envgate01 --replay --workers 4 (pid 24000) -> 48 live
            multiprocessing children spawned 17:18:41 / 17:22:46 local, plus 12 claude sessions.
            My own background command was killed by the OS for low memory at ~21:2xZ (task notice).

## 2. Reading, stated as a reading

Commit exhaustion on the shared M2 host is the common cause that fits every symptom: two long-lived HTTP
services holding sockets but unable to service requests with ~17 MB resident each (paged out), a PowerShell
watchdog exiting non-zero, and an OS-killed background process. The 09-23 store-read failures and the
09-19 idle park are SEPARATE and earlier events; they are not caused by today's pressure. I did not test
the causal claim (no restart, no allocation experiment) because both services belong to other seats.

## 3. Two defects in MY OWN machinery, found by this incident

F1  THE DEAD-MAN'S ESCALATION SHARES A FAILURE MODE WITH WHAT IT ESCALATES. It parked on
    STORE_UNREADABLE and then tried to post that fact through comms -- which lives on the same M1
    Postgres it could not read. The post failed, the task disabled itself, and with the task off there
    was no later tick to retry the post. Result: a watchdog that stopped watching and told no one, for
    31 hours. The local artifacts (park record + report) were written, so the evidence existed on disk;
    nothing read them.
    FIX (designed, not yet built): (a) treat STORE_UNREADABLE as the transient-infrastructure class
    that it is -- auto-clear it when the store reads again, bounded exactly like the ENGINE_TRANSPORT
    auto-recovery (3 per rolling 24 h), notice retried on the clearing tick; (b) when a notice fails,
    do NOT disable the task: keep ticking (refusing to relaunch) so the notice can be retried, and
    record every retry in the park record; (c) write a one-line dormancy stamp to a file the base-role
    self-test already reads, so "the watchdog is parked" is visible without comms.

F2  THE CONSUMER PARKS ON AN EMPTY QUEUE, CONTRADICTING ITS OWN DECLARED PRODUCTIVITY SIGNAL. The
    MONITORS row says "an idle tick on an empty queue is the explicit no-op", but rule 10 counts those
    ticks toward the bound, so 24 h of nothing-to-do parks the consumer and needs a human clearance.
    That is what happened at 00:29Z on 09-19, and it is why the seat was not standing by.
    FIX (designed, not yet built): a tick with NO eligible row advances a separate dormancy counter,
    not the rule-10 counter; rule 10 counts ticks where eligible work existed and was not executed
    (its actual purpose). Dormancy emits ONE notice per episode ("idle since X, 0 eligible rows") and
    never parks. Bound, counter and notice all declared in MONITORS.md before the change lands.

Both fixes are additive and testable (positive / negative / cheat), and both change a loop's own bound,
so they land with the MONITORS row and the accountable seat told -- not silently. Neither is being built
under the current host pressure: building and testing would add exactly the load that is the problem.

## 4. State at the close of this receipt

    consumer vivarium@m2   DOWN, park cleared, awaiting its launch precondition (8811). The dead-man is
                           ENABLED and probing every 5 min; it will park again at 3 failed ticks with
                           accountable seat Daedalus and -- with the store up -- that notice will post.
    deliverer              ALIVE, 0 pending, outbox 262/262 delivered.
    queue                  0 in flight, 0 stranded, 5 Archaeon rows held to 2027-01-01. Nothing missed.
    not mine, reported     SFE 8811 hung (pid 19464) and SFEngineM2Watchdog disabled with last result 2
                           -> Daedalus. PEW 8377 hung (pid 17192) -> Mnemosyne. Host at 98% commit under
                           Archaeon's 28-worker assays -> Archaeon, as a scheduling fact, not a fault.
