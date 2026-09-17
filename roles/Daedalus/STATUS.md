# Daedalus -- status

Currency: 2026-09-17 07:0xZ -- instance m2-d6ecd70b ACTIVE on M2. CAMPAIGN 3 IS RUNNING on the production engine: MIGRATION FREEZE (amendment s11) -- no engine route/schema/deploy change until it closes. Point-release Stage 0-2 written (docs/point_release_2026-09/SFE_POINT_RELEASE_REVIEW.md); #315 hold stays until C3 closes (base role
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

1. **Point release (amendment 1, s5)**: Stage 0-2 written, read-only:
   `SerendipityFoundry/SerendipityFoundryEngine/docs/point_release_2026-09/SFE_POINT_RELEASE_REVIEW.md`
   -- 11 MUST/SHOULD items (D1-D11), 2 REJECT, 3 DEFER; schema 8->9 nullable
   only; +4 routes; ONE deploy window after Campaign 3 closes. Next: Stage 3
   peer review (questions to Vivarium/Mnemosyne/Proteus/Archaeon/Harmonia in
   the review's Stage 3 section); then SFE_INTERFACE_DELTA.md; then code in
   this worktree, NOT deployed.
2. **Migration freeze** while Campaign 3 runs (amendment s11): exceptions
   only for critical defect / data loss / integrity / campaign-blocking,
   each recorded.
3. **#315 hold** on consumer relaunch stays until Campaign 3 closes; the
   #301/#314 conflict was resolved by fact (C1-C3 ran on eng_906356f7):
   production is M2's ledger. One superseding post when C3 closes.
4. Canonical-copy deletion on M2 (`var\engine.db`, `deploy\m2.key`) --
   after the freeze, explicitly confirmed.
5. `deploy/adopt_m1_ledger.py`: unused (M1 ledger stays an archive); keep.

## Blocked on someone else

- nk_landscape_v0: Archaeon's permutation-direction ruling; Vivarium's
  registration (comms 186) -- unchanged.
- `archaeon/tests/conftest.py` forces Postgres on the base-role self-check
  (prompt at `roles/Daedalus/prompts/2026-09-11_base_role/`) -- unchanged.
