# Ledger move F: (HDD) -> D: (NVMe), 2026-09-12 -- acceptance

Move applied 11:58:16-11:59:36 local (outage 80.2 s), receipt `apply.json`.
Identity before and after: engine_instance_id eng_8a37a5d305969034d488c43e,
engine_source_hash sha256:5380cb90..., schema 8, source_commit d5be5ec4b --
unchanged. Events at stop 129,401 = events on the destination at start.
engine.db, m1.key, m1.crt byte-identical (sha256 in the receipt); blobs
2,141 files 41.2 MB; backup 2 snapshots 313.5 MB. Task action now
`D:\Prometheus-data\sfe\sfengine.cmd`; the serving process reads
`--db D:\Prometheus-data\sfe\engine.db`.

One receipt check reads FAIL and is self-inflicted: "no -shm left beside the
source ledger". The tool's own read-only `ledger_snapshot()` at the stop
created a 32 KB `-shm` and a 0-byte `-wal` at the source (mtime 11:58, after
the stop). The data was complete: no WAL content, identical sha256, identical
event count. Fixed in the tool for next time by snapshotting before the check.

## The same C9 shape, before and after (deploy/C9_BURST_STALL_2026-09-11/)

Same harness, same build, same load (600 experiments + 600 family adds;
12 + 8 serial rows; reader every 0.5 s), copy taken from the LIVE ledger at
its then-current path, engine launched from the pinned worktree.

    run                              disk       burst s  prod p95/max s    reader p95/max s  cons p95  >5s  >10s  WAL max   errors
    run2_F_asdeployed (BEFORE)       F: HDD      633.8   2.674 / 15.154    3.174 / 14.977    0.176     53    2    1,058,872   0
    run3_D_asdeployed_after_move     D: NVMe      20.5   0.032 /  0.125    0.048 /  0.053    0.076      0    0      247,232   0
    run1_C_asdeployed (reference)    C: NVMe      20.6   0.033 /  0.115    0.032 /  0.110    0.072      0    0      531,512   0

Live routes probed on the production engine DURING the after-move burst
(12 samples, 11:59:35-11:59:47): `/v2/version` (one db read) 0.019-0.037 s;
`/v2/openapi.json` (no db) 0.019-0.021 s. Before (during run2 on F:):
6.1 s and 0.039 s. D: `Avg. Disk sec/Write` 0.006 s, queue 0 (F: during
run2: 0.127 s, queue 3).

## Verdict: STORAGE_REMEDY_CONFIRMED

Criterion (operator, 2026-09-12): no paired multi-second freeze pattern --
none (0 calls over 5 s); zero or bounded calls over 5 s -- zero; producer
and reader back in the NVMe-class regime -- p95 0.032 / 0.048 s against
the C: reference 0.033 / 0.032 s. Wall time 20.5 s vs 20.6 s reference.

What this does NOT show: that the minutes-long production episodes cannot
recur under some other trigger. It shows the measured trigger (a write burst
on the HDD) is gone from the path. The watch continues: Vivarium's stall
detector (`viv.cli stalls`) and the consumer's halt-on-first-transport are
the instruments that will say so.
