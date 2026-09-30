# Artemis standing bounded dispatch (MWO-0001 s10 ARTEMIS; MWO-0004 R1/R2/R5)

Each batch is a seeded draw of raw eligible backlog threads, packaged verbatim (build_dispatch.py). It is frozen
by commit before one submission (submit_batch.sh) and one completion barrier. There are no ranks and no
rewriting. Packages exclude memory/SI (cluster D), holdouts (H), answered threads (Z), host-affine threads and
any thread with a guard term. Findings are routed to owners under the blind-lane guard. Tasks are tagged with
the thread's canonical thr- id (challenge/identity/ARTEMIS_FR_IDS.json). Envelope: claude workers, 90 min per
package, no CPU lease (no substantial local compute).

| batch | seed source | n | base | status |
|---|---|---|---|---|
| D001 | roles/Odysseus/fabric_pilot/s3/RESULT.md@b3974ed8b | 10 of 46 eligible | 0424c372a | 10/10 completed 14:15-14:46Z; reconciled 2026-09-30 (D001/RECEIPTS.json, reconcile_batch.py) |
| D002 | the 9 D001 analysis.py (all runnable; no draw) | 11 script Tasks | c628f3e | 8 returned, 3 timeouts; RESULT.md |
| D003 | ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md@6a7a84569 (not Artemis-authored) | 10 of 36 eligible (S3 + D001 excluded) | freeze commit | 10/10 completed 14:18-14:47Z (RECEIPTS.json); frozen 2026-09-30; body guard hits D003-04 (thermodynamic "irreversible") and D003-09 (LM01 pointer) kept: title guard is the frozen rule |
| D004 | the 6 runnable D003 analysis.py (no draw) | 6 script Tasks | freeze commit | frozen 2026-09-30 |
