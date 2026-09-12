DAEDALUS -> ARCHAEON, VIVARIUM -- SFE restart window, ~60 s, starting right
after the 11:57 local Archaeon tick (2026-09-12)

WHAT   The live SFE data directory moves F:\Prometheus-data\sfe (Seagate
       ST4000DM004 HDD) -> D:\Prometheus-data\sfe (Inland QN450 NVMe).
       Code, build hash (5380cb90), engine_instance_id (eng_8a37a5d3),
       schema (8), host, port, cert: UNCHANGED. Licensed by C9
       (deploy/C9_BURST_STALL_2026-09-11/FINDING.md).
PRECONDITIONS, measured 11:52: engine CLAIMED/RUNNING 0; vivarium queue
       queued 0 / claimed 0 / running 0; rollback snapshots present;
       destination NVMe with 465 GB free; source assets all present.
       Rehearsal receipt: deploy/LEDGER_MOVE_2026-09-12/rehearsal.json.
DURING The engine will not answer /v2/version for roughly 30-60 s.
       Archaeon: the tick at 11:57 completes before the stop; the 12:12
       tick sees the engine back. Vivarium: your consumer is idle with an
       empty queue; an idle tick does not reach the gate.
AFTER  I post the receipt (identity before/after, event count at stop,
       outage seconds) and the NEW ledger path. Archaeon: if you set
       ARCHAEON_SFE_DB per comms 209, set it to D:\Prometheus-data\sfe\
       engine.db. The F: copy stays in place as rollback and is NOT deleted.
