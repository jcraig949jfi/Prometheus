# Daedalus -- status

Currency: 2026-09-16 17:40Z -- instance m2-d6ecd70b ACTIVE on M2; PRODUCTION LAUNCHED on M2 17:22Z on the operator's clearance (M2's own ledger; M1's does not move) (base role
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
| **SFE PRODUCTION on M2** | `https://192.168.1.191:8811`, schema 8, build `4dbcd3fd` at `dd10c9074`, ledger `eng_906356f7` at `D:\Prometheus-data\sfe\engine.db`; launched as production 2026-09-16 17:22Z on the operator's clearance (`deploy/DEPLOYED_BUILD_M2.json`, receipt `deploy/LAUNCH_M2_2026-09-16/`). Harness 12/12, isolation 7/7, contract gate 0 (also with both consumers' 25 routes). Cert for clients: `SerendipityFoundryClient/config/m2.crt`. |
| supervisor | task `SFEngineM2Watchdog` -> pinned `D:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1`; state file beside it; bound 3 |
| contract | `roles/Harmonia/contracts/sfe_contract.json` regenerated against this engine and landed by me under the operator's clearance (provenance block `landed`); previous kept in the launch dir |
| SFE on M1 | RETIRED. Ledger `eng_8a37a5d3` stays on SKULLPORT as an archive (operator: does not move). Not production. Nothing M1-side is mine. |

## Engine health, plainly

PRESENT, ACTIVE, VALID at rest, ~20 ms; no consumer registered on this
ledger yet (Vivarium and Archaeon relaunch on M2 next). Production history
on this ledger starts today; the M1 ledger's 617-world corpus, grant,
tokens and 5 queued rows are NOT here (retracted #270's refusal of (b)).

## Open, in order

1. Consumers onto M2 (theirs; my step-4 post is out): Vivarium registers
   as owner, re-issues the viv- scope, relaunches its consumer from an M2
   pinned worktree; Archaeon registers, gets the grant (Vivarium), reruns
   the gate, redeploys its tick (ARCH-51). I verify the grant engine-side
   (`deploy/verify_read_grant.py`) when asked.
2. Harmonia: regenerate/diff the contract at will; the 726275da staging is
   history. `verify_gate_states.sh` not run by me (needs her scratch fixture).
3. Canonical-copy deletion on M2 (`var\engine.db`, `deploy\m2.key`) --
   separate, explicitly confirmed step.
4. Watchdog script is a pinned copy; redeploy by copy + receipt on change.
5. `deploy/adopt_m1_ledger.py` stays as a tool, unused (the M1 ledger does
   not move); `sfe-twin-rollback` never created.

## Blocked on someone else

- nk_landscape_v0: Archaeon's permutation-direction ruling; Vivarium's
  registration (comms 186) -- unchanged.
- `archaeon/tests/conftest.py` forces Postgres on the base-role self-check
  (prompt at `roles/Daedalus/prompts/2026-09-11_base_role/`) -- unchanged.
