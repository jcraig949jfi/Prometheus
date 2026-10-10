# C-012-T003 two-node demonstration -- run Q20261010A (2026-10-10; window 08:41:09Z-08:55:31Z, reap 09:01:42Z)

OP-NF2 s5: Fabric task claim -> approved execution -> immutable evidence publication -> PostgreSQL chain update ->
independent replay -> durable receipt; racing workers with identical and conflicting results; PUBLISHED,
DUPLICATE, CONTESTED, STALE, INVALID and UNVALIDATED/VALIDATED distinguished; crash and lost-acknowledgement cases
repeated; no Git remote in claiming, executing or publishing.

Setup. Nodes ubu001 (192.168.1.218) and ubu002 (192.168.1.219), frozen Fabric v0.2 runtime 9c022347e at
~/fabric-runtime-moonshot, workers worker.<host>.moonshot (caps moonshot.epoch.v1, executor script only), canonical
Fabric schema `fabric` on M1. Approved executor: moonshot.epoch.fabric_exec at 55c74f7cb (main). Deliberately
unapproved commit for S6: 798f58456 (main; same executor code, not the chain's approved SHA). Publisher, validator,
resolver and coordinator ran on M2 (SPECTREX5) against Moonshot schema `moonshot_qual` (persistent: the evidence).
Window announced in comms #2008 (with a correction to #2003: Fabric's reaper marks stale instances offline and
expires dead leases when any worker runs).

Files:
- `RUN.json` -- every scenario, step, Fabric task/attempt (claim latency, run time, host), classification, contest,
  verdict, validation, receipt sha256, as recorded by the driver (`../run_two_node.py`).
- `DB_SUMMARY.json` -- the same run read back from `moonshot_qual` itself: outcomes, contests, validations, chain
  states, object bytes, and per publication its UNVALIDATED interval (published_at -> first validation).
- `receipts/<chain>.json` -- the canonical receipt bytes of each chain (each also stored content-addressed in
  moonshot_qual.objects with a 'receipt' event; sha256 in RUN.json).
- `preflight_before.json`, `preflight_after.json` -- Fabric queue/attempt/lease/instance state and node facts
  (FETCH_HEAD mtime of each node's canonical clone, runtime HEAD, approved commit present, worker processes).
- `audit.json` -- every attempt by a moonshot worker since the window opened, foreign claims, Fabric events by kind
  and by other actors.
- `node_logs/` -- the two workers' stdout logs.

Results (all measured; see the files):
| Scenario | What | Outcome |
|---|---|---|
| S1 | one epoch end to end, chain of 3 to COMPLETE | 3 PUBLISHED (ubu001, ubu002, ubu001), all VALIDATED; lineage equals the reference replay |
| S2 | 2 workers race every successor, identical results | each epoch 1 PUBLISHED + 1 DUPLICATE (x3) |
| S3 | 2 workers race, ubu002 faulty (flip_checkpoint) | PUBLISHED (ubu001) + DISAGREEMENT (ubu002) -> HALTED -> replay -> UPHELD -> COMPLETE |
| S4 | faulty host publishes; straggler on that lineage | faulty epoch 1 PUBLISHED; replay validation MISMATCH -> contest AUDIT_MISMATCH (CONTESTED) -> OVERTURNED (rewind); the 46 s straggler for epoch 2 -> STALE; honest chain COMPLETE at generation 5 |
| S5 | bytes disagree with their manifest (corrupt_trace) | INVALID (ubu001), head unmoved; then PUBLISHED (ubu002) |
| S6 | code the chain did not approve | executed by Fabric (cannot be prevented), REFUSED_UNAPPROVED by the publisher; then PUBLISHED |
| S7 | worker SIGKILLed mid-execution, x3 | each attempt abandoned by Fabric's reaper after 90-92 s (TTL-bound), retried on ubu001, PUBLISHED; Moonshot never saw the dead attempts |
| S8 | publisher process killed inside its transaction x3; lost acknowledgement x3 | kills: nothing committed (attempt unclassified), next pass PUBLISHED once; lost acks: PUBLISHED with replayed=true (the recorded answer) |

Database totals (DB_SUMMARY.json): attempts PUBLISHED 23, DUPLICATE 3, DISAGREEMENT 1, STALE 1, INVALID 1,
REFUSED_UNAPPROVED 1 (= the 30 Fabric tasks); contests 2 (DISAGREEMENT RESOLVED_UPHELD, AUDIT_MISMATCH
RESOLVED_OVERTURNED); validations VALIDATED 22, MISMATCH 1; chains COMPLETE 8; 119 objects, 45,971 bytes.
Every publication was UNVALIDATED for 0.01-193 s before its first validation.

No Git remote: the approved and the unapproved commit were staged (git fetch, 08:40Z) BEFORE the window; the
FETCH_HEAD mtime of each node's clone is identical before and after (ubu001 1791621606, ubu002 1791621619); the
worker logs contain no fetch; the coordinator uses no git.

Interference: audit.json -- 33 moonshot-worker attempts (30 tasks + 3 abandoned in S7), foreign claims 0, Fabric
events by other actors in the window 0. Side effects of Fabric's reaper (announced in #2008): worker.ubu001.{a,b,sci}
marked offline; Ananke's lease lse-7d61e3584398 (skullport:gpu0, expired 2026-10-07) expired.

Replay (DB_SUMMARY.json validations_detail, contests_detail): 23 validations on M2 (SPECTREX5, independent of both
executing nodes); 22 replay digests equal the published digest; the one that does not is S4's faulty epoch 1
(MISMATCH). Both contests were resolved by unanimous replays: S3's equal to the published digest (UPHELD), S4's
equal to the challenger (OVERTURNED).

Authentication, authorization, isolation (OP-NF2 s7) -- what this run did and did not establish:
- Authentication: NOT achieved. Every client -- the coordinator on M2 and the Fabric workers on the nodes -- logs in
  as the postgres superuser through the git-tracked default config; Fabric does not authenticate task submitters.
- Authorization: Moonshot acts through NOLOGIN roles (publisher, validator, resolver, coordinator, reader) -- bug
  containment while logins are superuser, not a boundary. Code approval IS enforced where Moonshot can enforce it:
  S6 shows unapproved code executed by Fabric and refused by the publisher on provenance (base_sha, worktree head);
  the coordinator tests also refuse another module with valid bytes and a test-namespace task aimed at a production
  chain.
- Isolation: the executor ran through Fabric's script executor (no shell, allow-listed environment: no database or
  network configuration in its env, pinned commit) as the node user; it imports no database/network/subprocess/git
  code (tested). It is NOT sandboxed: as the node user it could read the runtime checkout's credential config.
  promexec stays EXPERIMENTAL and unused. Resource bounds: wall_s per task only (no cgroups).
- Deterministic, approved, bounded executors only (OP-NF2 s7): yes -- synthetic.v1 epochs of 60 hash iterations.

Found while running (recorded, not hidden):
- the driver's pgrep/pkill patterns matched the ssh shell running them (start reported "already running"; stop and
  kill would have killed their own shell) -- fixed with the [f]abric pattern before any worker ran;
- `a && b && nohup c &` backgrounded the whole list and held the ssh channel open (the first start hung) -- the
  ubu001 worker it did start was stopped before any task was submitted;
- a Fabric v0.2 worker stopped by a signal does not deregister: its instance stays 'online' until a reaper runs 360 s
  later (DEF-ODY-017 class); my own stopped instances were cleaned by one fabric.store.reap() call (see the receipt).
