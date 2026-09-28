# ARC3 compute queue (Ensorain, M2)

Lease convention: the shared host-lease-file + comms-record convention of roles/Ananke/research/lease.py
(~/ananke_runs/leases/<res>.json on the host; subject "LEASE ACQUIRE <HOST> <res>: <owner> until <UTC>"). Ensorain
posts the comms record under its own name; no private mechanism.

| id | thread | workload | waits on | status |
|----|--------|----------|----------|--------|
| Q1 | T01 LM01 | frozen campaign v0.3.1 (768ea8ce9): 1,968 worlds, 8 workers BELOW_NORMAL, <1 GB RAM, ~9 h wall -> lease cpu8, TTL 11 h, renew before expiry | (a) the operator's gate phrase "LAUNCH WTP-LM01 using frozen prereg <prefix>" (ruling 2026-09-26 item 6; the ARC3 directive lacks it); (b) M2 CPU: Bellerophon multi-day campaign (12 workers, active_runtime_v1 budget, cap 60 h; 37.7 h active at 2026-09-28T06:23Z; comms #738) | QUEUED 2026-09-28T06:25Z |

Queue-health check before Q1 launches (Block Q): premise, ruler and prerequisites unchanged since the freeze; the
Block B adversarial review is read; the freeze verifies.

## Log
- 2026-09-28T06:25Z Q1 queued. Host census: Bellerophon supervisor pid 11852 with 12 workers at 100% CPU, total 47%,
  15.2 GB free. There is no lease file on M2; its notice #738 serves as its declaration. Not contending.
- 2026-09-28T06:55Z Q1 still queued. Bellerophon: 38.2 h active of its 60 h cap (done 3,647). One-shot queue checks are
  scheduled for 2026-09-28 20:07Z and 2026-09-29 05:07Z (session-only). Each launches ONLY if Bellerophon has finished
  AND the operator's gate phrase is recorded. Pre-launch additions (no frozen change): the adversarial review and the
  pre-data adjudication addendum G1-G9 are committed; the freeze still verifies.
