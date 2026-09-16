# Daedalus -- status

Currency: 2026-09-16 12:05Z -- instance m2-d6ecd70b ACTIVE on M2 (base role
s3 requires this file; refreshed at least every four hours of activity).

## Where I am working

| | |
|---|---|
| machine | **M2 / SPECTREX5** (first boot of this seat off M1) |
| worktree | `D:\Prometheus-worktrees\daedalus-boot-2026-09-16` |
| branch | `daedalus/m2-d6ecd70b-boot-2026-09-16` |
| base_sha | `ccb26df01` |
| dirty | no (tracked) |
| comms | booted 11:41Z (`EW_DB_HOST=192.168.1.202`; incident c84e26826cc12217); 13 read; queue: #6 (Archaeon #223) open |

## What is running

| | |
|---|---|
| SFE on M2 | `https://192.168.1.191:8811`, schema **8**, build `726275da` (= the held candidate) at `ccb26df01`, ledger `eng_906356f7`; relocated under D-23 2026-09-16 11:48Z (`deploy/DEPLOYED_BUILD_M2.json`, receipt `deploy/M2_RELOCATE_2026-09-16/`). LIVE_VERIFIED: unit 481, harness 12/12, isolation 7/7, Harmonia's gate CONFORMANT with the twin's instance id. Verify twin, no consumer. |
| M2 supervisor | task `SFEngineM2Watchdog` -> pinned `D:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1`; state file beside it; bound 3, enforcement DEPLOYED |
| SFE on M1 | **NOT ANSWERING** since the 09-14 19:55 SKULLPORT reboot (Nestor #262/#263); 8811 times out from M2; no SSH/SMB path from here. Ledger `eng_8a37a5d3` at `D:\Prometheus-data\sfe` on M1, build `5380cb90` at `d5be5ec4b` (last known). Not restarted by me: no hand on M1, and `ccb26df01` says SFE moves to M2 carrying that ledger. |

## Engine health, plainly

M2: PRESENT, ACTIVE, VALID at rest, answering in ~20 ms; the two-day
outage (09-14 05:33 -> 09-16 11:48) was the launcher serving the canonical
checkout into serve.py's D-23 guard, ~600 refused relaunches, invisible
because a refusal never binds the port. M1: DOWN, unmeasured beyond a
connect timeout; both wired consumers (Vivarium, Archaeon) point at it.

## Open, in order

1. **Operator's call on the M1 -> M2 move** (`ccb26df01`): restart M1 now
   or leave it down; who copies the 640 MB ledger and how (no share
   reachable either way today); consumers re-point in-window or after.
   M2's layout/build/supervisor are the ones the migrated ledger would run
   on. Held; questions in chat and journal.
2. **Queue #6 (Archaeon #223)**: `spec_hash` / `committed_seq` (/`spec`)
   beside each row on `/v2/read/observations`. Next executable action.
3. M1 deploy window for the candidate, IF M1 stays production: restart
   onto `8c53d04e6`+, then `promote_candidate_contract.py` (Harmonia
   #256, authorised commit of `sfe_contract.json`), re-pin. Superseded
   by 1 if the move happens first.
4. Canonical-copy deletion on M2 (`var\engine.db`, `deploy\m2.key`) --
   separate, explicitly confirmed step after the service is seen healthy.
5. Same on M1 (F: copies, per 09-12 STATUS). D-WD-1 (M1 watchdog) is moot
   if M1 stops hosting the engine.

## Blocked on someone else

- Item 1 above (operator; and a session on M1 for anything M1-side).
- nk_landscape_v0: Archaeon's permutation-direction ruling; Vivarium's
  registration (comms 186) -- unchanged.
- `archaeon/tests/conftest.py` forces Postgres on the base-role self-check
  (prompt at `roles/Daedalus/prompts/2026-09-11_base_role/`) -- unchanged.
