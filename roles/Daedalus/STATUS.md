# Daedalus -- status

Currency: 2026-09-16 12:45Z -- instance m2-d6ecd70b ACTIVE on M2; operator 12:0xZ: the SFE ecosystem runs on M2 from now; M1 runs a different ecosystem (base role
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
| SFE on M1 | **RETIRING** (operator 2026-09-16: Postgres + Redis shared; every other service on ONE machine; the engine's machine is M2). Stopped ~09-15 20:15Z for the move; not to be restarted. Its ledger `eng_8a37a5d3` (`D:\Prometheus-data\sfe` on M1, last build `5380cb90`) is the production identity and comes to M2 by `adopt_m1_ledger.py`. The M1 task gets disabled by whoever next has a hand on M1. |

## Engine health, plainly

M2: PRESENT, ACTIVE, VALID at rest, answering in ~20 ms; the two-day
outage (09-14 05:33 -> 09-16 11:48) was the launcher serving the canonical
checkout into serve.py's D-23 guard, ~600 refused relaunches, invisible
because a refusal never binds the port. M1: DOWN, unmeasured beyond a
connect timeout; both wired consumers (Vivarium, Archaeon) point at it.

## Open, in order

1. **Adopt M1's ledger on M2** -- waiting on the operator to land M1's
   `D:\Prometheus-data\sfe` (engine.db, blobs/, backup/; NOT m1.key) at
   `D:\Prometheus-data\sfe-from-m1` on M2. Tool ready:
   `deploy/adopt_m1_ledger.py --check` then `--apply` (identity eng_8a37a5d3,
   schema 8, >= 129,401 events, >= 2,141 blobs; twin ledger moved to
   `sfe-twin-rollback`, never deleted; restores on any post-start failure).
   Then Harmonia's `promote_candidate_contract.py --base https://192.168.1.191:8811`
   (#256 step 2-3, commit authorised), re-pin, post URL + /v2/version +
   contract state (= "step 4" both consumers are waiting on: Vivarium #288,
   Archaeon #284). Ruling #270: production is the ledger, wherever it runs.
2. **Next candidate** `adb7952ff` (#223: spec_hash/committed_seq on
   `/v2/read/observations`, hash `4dbcd3fd`): CODE_FIXED, 483 tests, deploy
   in the window AFTER 1; contract unaffected (response-only). Queue #6
   stays open until Archaeon reads it live.
3. Archaeon's M2 credential: after 1, Archaeon registers a new client on the
   migrated engine; Vivarium grants it the viv- scope engine-side; I verify
   (`deploy/verify_read_grant.py`). No token crosses a host.
4. Canonical-copy deletion on M2 (`var\engine.db`, `deploy\m2.key`) --
   separate, explicitly confirmed step.
5. Watchdog: `D:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1` is a pinned
   copy; when the tracked script changes, redeploy by copy + receipt.
6. Closed as moot by the topology ruling: D-WD-1 (M1 watchdog); F: canonical-
   copy retirement on M1 (M1's data dir is the SOURCE of the move, then dead).

## Blocked on someone else

- Item 1 above: the operator lands the M1 data dir on M2 (no share reachable either way). Nothing M1-side is mine any more.
- nk_landscape_v0: Archaeon's permutation-direction ruling; Vivarium's
  registration (comms 186) -- unchanged.
- `archaeon/tests/conftest.py` forces Postgres on the base-role self-check
  (prompt at `roles/Daedalus/prompts/2026-09-11_base_role/`) -- unchanged.
