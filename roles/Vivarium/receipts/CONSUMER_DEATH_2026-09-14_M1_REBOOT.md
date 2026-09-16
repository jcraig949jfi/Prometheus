# Receipt: consumer vivarium@m1 dead since the M1 reboot, unobserved 36 h

Instance Vivarium[m2-fce3fe0b], worktree D:\Prometheus-worktrees\vivarium-boot-2026-09-16,
branch vivarium/boot-2026-09-16, base_sha ccb26df01, dirty no. Written 2026-09-16 11:5x UTC.
Second occurrence of backlog C11 (first: receipts/CONSUMER_DEATH_2026-09-13_WT_CRASH.md).

## Measured (viv.worker_heartbeat and viv.research_experiment_queue on the canonical store, UTC)

    worker            vivarium@m1  pid 13460  host SKULLPORT  build fb7aa5bed (pinned F:\Prometheus-worktrees\vivarium-consumer)
    last heartbeat    2026-09-14 23:53:44Z   (19:53:44 local)
    M1 reboot         2026-09-14 ~23:55Z     (Nestor comms #262 19:38, #263 20:00 local: "back up, last boot 19:55")
    observed dead     2026-09-16 11:46Z      by this seat's boot, 35.9 h later
    park record       none (a dead process cannot park; rule 10 is in-process)
    stranded rows     0 (no row was current at the reboot: last_outcome IDLE, 9929 idle ticks)
    last row done     2026-09-14 23:27:07Z   8bc6b162 completed (cs-cce13105bd374c94)
    queued now        5 Archaeon tick rows, created 2026-09-15 03:27:10Z .. 20:12:09Z (oldest waiting 32.4 h)
    counters          cancelled 492  completed 579  failed 79  queued 5

## Why nobody saw it

The only reader of the MONITORS.md dormancy threshold is still a seat booting
(C11 (b), open since 09-14). Nestor announced the reboot on comms #262/#263 to
Daedalus and Vivarium; neither seat was online (Vivarium's last sync 09-14 06:05
local). A comms message to an offline seat is queued, not delivered.

## What is different from 09-13

Not a crash: an operator-ordered reboot with notice. The Task Scheduler task
`VivariumConsumer` is on-demand (interactive, no at-startup trigger), so the
reboot ended the process and nothing restarted it. C11 (a) "a logoff still kills
it" is exactly the class; a reboot is the largest logoff.

## Why it is NOT relaunched from this pass

Rule 9 (upstream liveness is a launch precondition) fails on every input, and
this seat has no hand on M1:

    M1 SFE   https://192.168.1.202:8811   connection refused (curl 000, 09-16 11:48Z)
    M1 PEW   http://192.168.1.202:8377    connection refused
    M1 shell no ssh (22 closed), no WinRM (5985/5986 closed); only 445 and 5432 answer
    M2 SFE   https://192.168.1.191:8811   LIVE since 11:48:31Z, but engine_instance_id
             eng_906356f7fb1da180131f9290, source hash 726275da (the A6+B3+C7 candidate),
             NOT eng_8a37a5d305969034d488c43e / 5380cb90 that every viv row, the
             B1 read scope and my conformance contract are keyed to. The gate would
             halt on engine identity, correctly.
    M2 PEW   http://192.168.1.191:8377    LIVE (mnemosyne-evidence-wiki, schema 4, up since ~11:38Z)
    M2 creds this worktree has no config.local.json; `viv.cli sfe-identity` reports
             production and test clients both unconfigured on M2

Operator commit ccb26df01 (09-15 17:17 local): "M1 is handed to Nestor and SFE
moves to M2 carrying M1's engine.db". The consumer follows the engine; where it
runs next and against which engine identity is the migration ruling this seat
needs before any launch (see the report to Archaeon and Daedalus).

## A hazard found while measuring this

On M2, `viv.cli` with no VIV_DB_HOST resolves db_host=localhost and reaches the
QUARANTINED M2 fork (db_system_id 7681719240261676752): `status` failed only
because the fork has no viv schema; `run` applies migrations at start and would
have CREATED it, then ticked an empty queue forever, green. viv/db.py has no
identity guard (comms/identity.py has one; comms boot refused the same
connection on this pass). Incident class c84e26826cc12217; fix in this pass.
