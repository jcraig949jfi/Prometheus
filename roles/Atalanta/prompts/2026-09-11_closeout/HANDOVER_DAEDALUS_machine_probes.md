# HANDOVER to Daedalus -- two scheduled tasks failing every five minutes, on both machines

From: Atalanta (retiring)
To: Daedalus, copy Archaeon
Kind: report
Base: origin/main at the commit carrying roles/Atalanta/RETIREMENT_2026-09-11.md,
measured on SPECTREX5 (M2) 2026-09-11.

The operator routed this on 2026-09-11: "whoever owns machine/runtime
infrastructure gets the two PrometheusMachineProbe failures. Do not let
Atalanta chase those probes merely because she found them."

It comes to you because you own SFEngineM2Watchdog on this same host and
are the nearest infrastructure owner; the M1 probe's registry row says
OWNER UNCLAIMED. IF THIS IS NOT YOUR LANE, SAY SO and ask Archaeon to
assign it. Atalanta is retired and will not follow up either way. This is
not a delegation; it is evidence being put where someone can act on it.

## What is happening

PrometheusMachineProbeM1 and PrometheusMachineProbeM2. Both are registered
DEAD in roles/base-role/MONITORS.md, and both are in fact RUNNING and
failing. Measured on M2 today:

    State               Ready
    Trigger             PT5M  (every five minutes)
    LastRunTime         2026-09-11 12:02:32
    LastTaskResult      0x80070002
    NextRunTime         2026-09-11 12:07:31
    NumberOfMissedRuns  0
    Action              pythonw.exe D:\Prometheus\scripts\machine_probe.py
                        --machine M2 --interval 60
    WorkingDirectory    D:\Prometheus   (the canonical checkout)
    RunAs               James, LogonType Interactive

Zero missed runs: it fires reliably and fails reliably. 288 failures per
day per host, on two hosts. For scale, the agent writing this note managed
354 failures in seven days and is being retired over it.

It also violates D-23 section 6 independently of the failure: the action
runs from the canonical checkout rather than a pinned worktree.

## Cause: UNRESOLVED. Two hypotheses eliminated, so you do not re-run them

1. ELIMINATED -- "the script is missing". The M1 registry row attributes
   0x80070002 to "file not found; cwd is the canonical checkout".
   scripts/machine_probe.py EXISTS at the exact invoked path, 11,055
   bytes, tracked since af828e1a7, present both in the canonical checkout
   and in a fresh worktree. Whatever is not found, it is not the script.

2. ELIMINATED -- "the bare exe name hits a Windows Store App Execution
   Alias stub". This was my hypothesis and it had two confirming
   measurements: the `pythonw.exe` on PATH IS a 0-byte reparse point at
   ...\AppData\Local\Microsoft\WindowsApps\pythonw.exe, and a real
   interpreter does exist at ...\AppData\Local\Programs\Python\Python312.
   I then tested it rather than filing it: a direct CreateProcess on the
   bare name "pythonw.exe" with UseShellExecute=false and
   WorkingDirectory=D:\Prometheus SUCCEEDED, exit 0. Hypothesis falsified
   by its own author before publication. Two confirming measurements were
   not worth one discriminating test.

## The discriminating test, which is yours to run and not mine

Either: run the registered action under the task's own principal and
capture the launch error rather than the result code; or re-register one
probe with an ABSOLUTE interpreter path (and, per D-23 s6, a pinned
worktree working directory) and observe whether the result code changes.
If it changes, the resolution path was the cause after all and my
CreateProcess test did not reproduce the scheduler's context. If it does
not, the cause is inside machine_probe.py or its environment and the
result code is the process's own.

I did not run it. Triggering, re-registering or disabling another seat's
scheduled task is outside my lane, and the ruling that retired me was
explicit that finding a thing is not a claim on it.

## Why it is worth your time rather than a cleanup ticket

This is the live instance of the failure this seat was retired for. The
registry says DEAD, which reads as "not running"; it is running, on
schedule, forever, producing nothing, with no alarm route and no owner.
The census found 18 of 30 registered loops with no alarm route at all
(roles/Atalanta/CENSUS_LOOP_RISK_2026-09-11.md), so nothing about these
two is exceptional except that they are still firing.

Whatever the cause turns out to be, the probes are also a clean first test
case for proposed base rule 10 if Archaeon adopts it: a bounded loop would
have parked them after N failures and posted once to a named seat, instead
of accumulating an uncounted number of identical failures on two machines
since whenever this started.
