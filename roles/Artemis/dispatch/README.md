# Artemis standing bounded dispatch (MWO-0001 s10 ARTEMIS; MWO-0004 R1/R2/R5)

Each batch is a seeded draw of raw eligible backlog threads, packaged verbatim (build_dispatch.py). It is frozen
by commit before one submission (submit_batch.sh) and one completion barrier. There are no ranks and no
rewriting. Packages exclude memory/SI (cluster D), holdouts (H), answered threads (Z), host-affine threads and
any thread with a guard term. Findings are routed to owners under the blind-lane guard. Tasks are tagged with
the thread's canonical thr- id (challenge/identity/ARTEMIS_FR_IDS.json). Envelope: claude workers, 90 min per
package, no CPU lease (no substantial local compute).

| batch | seed source | n | base | status |
|---|---|---|---|---|
| D001 | roles/Odysseus/fabric_pilot/s3/RESULT.md@b3974ed8b | 10 of 46 eligible | 0424c372a | frozen |
