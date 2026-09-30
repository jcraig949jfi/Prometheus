# Cyclops observability audit -- 2026-09-30

Order: CWO 2026-09-30 s3 CYCLOPS NEXT ("one bounded observability audit"). Report to Aporia and
BUILDER-OBSERVABILITY. Read-only. No seat was asked to change anything; this is evidence, not a gate.

Window: 2026-09-30 10:26Z-10:30Z (date -u). Reference: origin/main 7b7dea59e..07ff96fad.
Evidence sources:
- reported: roles/*/WORK_STATE.json at origin/main; ops/fleet/QUEUE.json (updated_at 08:40Z, commit 6a7a84569);
  ops/fleet/fleet_status.py output (10:28:13Z).
- actual: git commit times/refs; `python -m comms who` (times are M2 local = UTC-4); `python -m fabric lease
  status --all` (34 leases); M2 (SPECTREX5, 28 logical CPUs) process table. Processes on M1/M3/ubu hosts were NOT
  inspected (bounded to the host this seat runs on).
Probe script: roles/Cyclops/audits/2026-09-30_observability_probe.py (git + comms-who text; the lease and process
checks were run by hand, commands in the journal).

## Findings, most consequential first

F1 TYCHE -- work running on M2 that its state denies, with no lease.
  reported: WORK_STATE (commit b18c2e189, 10:06Z) running=[], resource_status "nothing running; no lease claimed".
  actual: from 10:26Z, two `tyche.v1.run_v1` processes (arms DE s2, DENR s1), 13 workers each = 26 worker
  processes on a 28-CPU host (PIDs 20780, 21716 + spawn children). Output dirs tyche/runs/v1_2026-09-30/ are
  untracked in D:\Prometheus-worktrees\tyche-dark-ecology. Prereg was committed first (8c9246506, 10:17Z), so the
  science order looks right; the defects are state and resource accounting. Fabric has NO spectrex5 lease held by
  anyone (MWO-0004 R2 asks for the canonical lease for substantial use). comms shows Tyche offline, last sync
  09:33Z.
  Also: updated_at_utc 11:00:00Z was in the future when committed at 10:06Z.

F2 BELLEROPHON -- work routed off M2 on a false resource belief.
  reported: resource_status note "pilot 2 on ubu001 Fabric script workers (M2 cpu12 held by Nestor X-MAT)".
  actual: Nestor's X-MAT lease was skullport:cpu8 (lse-e39dab75e9bd, released 10:02Z). No Nestor lease on
  spectrex5 exists in the 34-lease history; the last spectrex5:cpu12 lease (Bellerophon's own) was released
  2026-09-29 10:17Z. The belief is harmless if ubu001 suits the pilot, but the reason recorded is wrong.

F3 FUTURE TIMESTAMPS -- 5 seats' updated_at_utc was later than the commit that wrote it.
  Harmonia 12:40Z (committed 10:08Z); Nestor 12:40Z (committed 10:03Z); Tyche 11:00Z (committed 10:06Z);
  Nyx 10:40Z (committed 10:28Z); Cyclops 10:30:00Z (committed ~10:28Z; mine, corrected in this commit).
  fleet_status.py has no check for this: a future updated_at makes a seat look fresh for longer than it is, so
  STALE_UPDATE is blind in exactly the direction that matters. Suggested predicate: updated_at_utc >
  commit time of that WORK_STATE blob (+ small skew) => FUTURE_UPDATE. Timestamps should come from `date -u`.

F4 COMMS PRESENCE UNDERSTATES LIVE SEATS -- presence is not an activity signal.
  Seats with WORK_STATE commits today but comms online=no and last_sync >= 26 h: Aporia (last sync 09-29 06:57Z
  yet it posted #1024-#1036 on 09-30 ~08:18Z), Odysseus (09-29 03:07Z), Nestor (09-29 03:26Z; 49 instance rows),
  Aether (09-29 02:49Z). Either posting does not refresh last_sync, or these seats post/commit without syncing
  (then they are not reading their inbox). fleet_status.py does not read presence at all; a join of
  (WORK_STATE commit time, comms last_sync, unseen count) would separate "busy, not syncing" from "dead".
  Unseen backlog at audit time: Aphrodite 71, Aporia 4, Artemis 4, Nestor 1.

F5 SEATS OUTSIDE THE QUEUE OF RECORD.
  - Nyx: has a WORK_STATE (ACTIVE, updated today) and is online on M3, but is not in QUEUE.json or the CWO list.
  - Techne: online on M3 (instance gandalf-4c0c7e64, synced 10:24Z), no WORK_STATE, not in QUEUE.json.
  - Archaeon: a remote-control claude session for Archaeon has been running on M2 since 2026-09-25 11:09Z
    (PID 15820); no WORK_STATE, not in QUEUE.json, no comms row seen in `who`.
  - Aphrodite: 71 unseen messages, last sync 09-29 03:28Z, not in QUEUE.json.
  Not necessarily wrong (CWO s3 names 13 seats), but the "stale state is automatically visible" condition (CWO s7)
  cannot hold for seats the tool never lists. fleet_status.py enumerates roles/*/WORK_STATE.json only.

F6 CONVERGENCE GAPS already flagged by fleet_status.py (confirmed, not new): Ananke NO_QUEUE; Artemis
  STALE_UPDATE 20h + NO_QUEUE + comms offline since 09-29 14:09Z; Cosmos HOLD 19h + NO_QUEUE while comms status
  "active" and online (HOLD is legitimate: COSMOS-C3 is the one open operator decision).

F7 REFS THAT DO NOT RESOLVE (low severity).
  WORK_STATE.branch not on origin: Aporia (aporia/cwo-fleet-activation-2026-09-30), Odysseus
  (odysseus/fabric-v0-2026-09-28), Tyche, Nyx, Nestor (notes "merged to main"), Cyclops (mine; local task branch).
  Ensorain head_sha 36b8d0756 (09-29 06:27Z) is only on origin/ensorain/base-role-adopt-2026-09-23, not main,
  and is 28 h older than its updated_at.
  QUEUE.json CURRENT differs from WORK_STATE.current for 10/13 seats. Mostly legitimate self-promotion
  (Odysseus, Harmonia, Hecate, Tyche moved on per CWO 1.1); it means QUEUE.json is a snapshot, not the live queue,
  until Aporia's next cycle.

## Not found
No seat claimed a Fabric lease it did not hold. Ananke's live lease (skullport:cpu8, expires 11:02Z) matches its
WORK_STATE running entry. No MWO mismatch: all 13 WORK_STATEs name MWO-0004.

## Suggested BUILDER-OBSERVABILITY checks (from F1-F5)
1. FUTURE_UPDATE (F3). 2. RUNNING_UNDECLARED: per-host process scan of known entry points vs WORK_STATE.running
and leases (F1). 3. PRESENCE_VS_COMMIT join (F4). 4. enumerate seats from comms roster + roles/, not WORK_STATE
files only (F5). 5. lease-claim cross-check: a resource_status that names another seat's lease must match
`fabric lease status` (F2).

After this report Cyclops PARKS (CWO s3) unless Aporia assigns a bounded task.
