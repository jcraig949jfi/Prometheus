# Daedalus -- status

Currency: 2026-09-17 19:35Z -- instance m2-d6ecd70b ACTIVE on M2. SFE 9.0.1 IS PRODUCTION (deployed 17:01:12Z). Campaign 3 CLOSED; Campaign 4 gated (Archaeon's launch_gate.py RED at 19:11Z). My G1 proof run is IN FLIGHT on a scratch engine (ends ~00:00Z). Pre-C4 FREEZE is pending: nothing else touches 8811 without an order.
(base role s3 requires this file; refreshed at least every four hours of activity).

## Where I am working

| | |
|---|---|
| machine | **M2 / SPECTREX5** |
| worktree | `D:\Prometheus-worktrees\daedalus-boot-2026-09-16` |
| branch | `daedalus/m2-d6ecd70b-boot-2026-09-16` (merged forward to main at `070672546`) |
| dirty | no (tracked); some local receipt dirs deleted under `deploy/LONG_RUN_2026-09-17/` are intentional |
| comms | `EW_DB_HOST=192.168.1.202`; last post #374 (C4 gate response); queue: #6 (Archaeon #223), #7 (Archaeon #266) open, both superseded by later posts |

## What is running

| | |
|---|---|
| **SFE PRODUCTION on M2** | `https://192.168.1.191:8811`, **9.0.1**, schema 9, build `sha256:699ca0f9...2264cc` at `b0d752183`, ledger `eng_906356f7` at `D:\Prometheus-data\sfe\engine.db`; pin `deploy/DEPLOYED_BUILD_M2.json`; receipts `deploy/RELEASE_9_0_1_2026-09-17/` and `docs/point_release_2026-09/SFE_901_REPAIR_RECEIPT.md`. Cert for clients: `SerendipityFoundryClient/config/m2.crt`. Registration OPEN. |
| supervisor | task `SFEngineM2Watchdog` -> pinned `D:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1`; state file beside it |
| contract | `roles/Harmonia/contracts/sfe_contract.json` regenerated against 9.0.1 and landed (routes identical, gate 0); Harmonia's PROMOTION for 699ca0f9 still pending (Vivarium reads INCOMPLETE_PROCEED until then) |
| **G1 long run (scratch)** | `deploy/longrun_load.py --worlds 30 --gens 1000 --producers 1 --gen-pause 0.5 --reader-pause 0.5`, port 9041, ledger under `D:\Prometheus-data\sfe-scratch\`, started 19:24Z, ~4.5 h, out `deploy/LONG_RUN_2026-09-17/accept901/R0L_campaign_rate_4h_writer_paced_reader/`. Ends with kill + relaunch + anchor verify. |
| SFE on M1 | RETIRED; ledger `eng_8a37a5d3` is an archive on SKULLPORT. Nothing M1-side is mine. |

## Engine health, plainly

9.0.1 on production since 17:01Z: 0 5xx, checkpointer alive (runs > 4,000,
errors 0, WAL 0 at rest, max seen 26 MB), A6 journal not degraded. The
9.0.1 repair (pool + autocheckpoint off + checkpointer thread + journal off
the response path) removed the request-path WAL choke measured on the
previous build; acceptance 0 5xx / 0 calls > 5 s in four regimes, 12-24x
throughput. Known property: under a SATURATING never-pausing writer the WAL
grows for the run (3.4 GB / 20K gens) and restart cost scales with it
(0.5-9.7 s); at campaign rate it plateaus at 8 MB.

## Open, in order

1. **G1 for Archaeon's C4 gate**: the campaign-rate run must outlast the
   prior defect's onset (840 s). Running (above). When it lands: append it
   FIRST in the acceptance table of `SFE_901_REPAIR_RECEIPT.md` (the gate's
   parser takes the first "campaign_rate" regime), regenerate
   `ACCEPTANCE_TABLE.txt`, re-run `archaeon/campaign4/launch_gate.py`, post.
2. **P3 restart window** for Archaeon's rehearsal S4/S5: on request, any
   10-minute window; I run the supervised restart on 8811 and write timings.
3. **Freeze pin** for Campaign 4 (joint packet): build 699ca0f9 at
   b0d752183, schema 9, contract as landed. HEAD engine source is now
   `f6a77c86...` (attestation cold-scan fix, NOT deployed); production stays
   699ca0f9 unless the operator orders a 9.0.2 window (13 s outage +
   contract regen). Recommendation: after C4.
4. Cross-seat before C4 (mine to confirm, theirs to do): Vivarium treats a
   500 `database is locked` as retryable-with-key; Archaeon's runner uses
   >= 30 s engine timeouts; fixtures that register on production moved to a
   scratch engine (Mnemosyne #373: done); backups via the SQLite backup API
   (runbook section added).
5. Canonical-copy deletion on M2 (`var\engine.db`, `deploy\m2.key`) --
   after the freeze, explicitly confirmed.
6. `deploy/adopt_m1_ledger.py`: unused (M1 ledger stays an archive); keep.

## Closed today (receipts)

- Point release 9.0 (schema 9, +4 routes) and 9.0.1 (WAL choke) deployed;
  `docs/point_release_2026-09/` holds review, delta, migration, deployment,
  restart, long-run, benchmark, release packet, repair receipt, two review
  packets. Tests 512.
- C4 P1: `cmp4-archaeon` = `cli_6354da5b5955a711dcc0b2af` minted on 8811,
  credential placed at Archaeon's `archaeon/campaign4/config.local.json`
  (gitignored). P2 (B1 grant) is Vivarium -> that id, per Vivarium #372.
- qualify_v9.py 8->9-only shapes gated on the backup's schema; A6 journal
  day-rollover test + cold-scan-across-days fix; backup runbook note.

## Blocked on someone else

- Harmonia: promote the regenerated contract for 699ca0f9.
- Vivarium: issue the B1 grant to cli_6354da5b; then Archaeon's S3.
- Archaeon: name the S4 restart window.
- nk_landscape_v0: Archaeon's permutation-direction ruling -- unchanged.
- `archaeon/tests/conftest.py` forces Postgres on the base-role self-check
  (prompt at `roles/Daedalus/prompts/2026-09-11_base_role/`) -- unchanged.
