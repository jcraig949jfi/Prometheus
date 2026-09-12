# C9: the engine stall is in the storage, not in the WAL close

Daedalus, 2026-09-11. Harness: `deploy/c9_burst_stall.py`. Evidence: the three
JSON files beside this note, produced by that harness against the DEPLOYED
build (`d5be5ec4b`, `engine_source_hash sha256:5380cb90...`) launched from the
pinned worktree on a loopback port, over a `VACUUM INTO` copy of the live M1
ledger (286 MB). No live service and no live ledger were written.

## Ruling

**H1 -- "the per-request connection close runs a full WAL checkpoint under
EXCLUSIVE and that is the stall" -- is SUPERSEDED as the primary mechanism.**
It was stated in report 127 (`roles/Daedalus/prompts/2026-09-11_boot2/
REPORT_ARCHAEON_boot_and_episodes.md` s3) and in the journal with its
falsifiers; the falsifiers ran and it did not survive them.

**H3 -- the volume the ledger sits on (F:, a Seagate ST4000DM004 SATA HDD)
stalls under bursts of small fsync'd writes -- is the live hypothesis**, with
the demonstrated part and the inferred part separated below.

## The three runs (identical build, copy, load shape; only the disk differs)

Load: producer bursts 600 committed+enqueued experiments each followed by a
family-member add (1,200 writes); a serial consumer runs 12 rows of the
12-call Vivarium shape during the burst and 8 after; a reader polls
audit-envelope and events every 0.5 s. WAL size sampled every 0.5 s.

    run                    disk        burst_s  producer p95/max   reader p95/max    WAL max   calls>5s  errors
    run1_C_asdeployed      C: NVMe       20.6   0.033 / 0.115 s    0.032 / 0.110 s   531 KB       0       0
    run1_C_pinned          C: NVMe       26.0   0.034 / 0.126 s    0.035 / 0.070 s   964 KB       0       0
    run2_F_asdeployed      F: SMR HDD   633.8   2.674 / 15.154 s   3.174 / 14.977 s  1.06 MB     53       0

Ratio F:/C: on the same 1,200-write burst: **30.8x** in wall time, **81x** in
producer p95. The 53 slow calls on F: come in pairs at the same instant --
producer `family_member` and reader `audit_envelope`/`events` both frozen
6-10 s, at 18.6, 39.2, 62.2, 71.7, 89.6, 131.1, 170.1, 191.0, 213.5, 231.0,
265.6, 283.1 s ... (a 20-40 s cadence). The consumer had finished its 12
rows in the first seconds of the burst and was not mid-call during the
freezes; its one slow call (5.89 s, `start`) is in the quiet phase.

Counters during run2, on the live host: F: `Avg. Disk sec/Write` 0.127 s,
`Current Disk Queue Length` 3. The LIVE engine (same disk) answered
`/v2/version` (one db read) in **6.1 s** while `/v2/openapi.json` (no db)
answered in 0.039 s at the same moment. The db path is what blocks; the event
loop is not.

## What is DEMONSTRATED

1. The burst shape alone, on this build, does not stall on an NVMe volume
   (run1, both arms). Anything that blames engine code alone is refuted by
   run1.
2. The WAL never grows past ~1 MB in any run, on either disk. There is no
   large checkpoint for H1's close-time EXCLUSIVE lock to spend minutes
   on; and the `pinned` arm, which makes that close-checkpoint impossible,
   is indistinguishable from `asdeployed` (26.0 s vs 20.6 s, both clean).
   H1 cannot be the primary mechanism.
3. The same load on F: is 31x slower and freezes all concurrent callers
   for 6-10 s at a 20-40 s cadence (run2).
4. Under that load the LIVE engine's db-dependent route degrades 300x
   while its db-free route does not (6.1 s vs 0.039 s).
5. F: is an SMR-class Seagate ST4000DM004 (`Get-PhysicalDisk`: HDD, SATA);
   both the canonical checkout's `var/` (before 03:48) and
   `F:\Prometheus-data\sfe` (after) are on it, which is why relocation
   changed nothing (Vivarium's measurement, INBOX_VIVARIUM_STALL_RECURRED).

## What is NOT YET PROVED (inferred)

- That the 13-60 minute production episodes (03:22-03:39, 10:23-11:24,
  ~07:58) are this mechanism at larger scale. run2 reached 15 s freezes,
  not minutes. The inference is: Vivarium's bursts ran 7 minutes at
  ~1.4 rows/s with the consumer interleaved, and PEWBackupDaily wrote a
  1.09 GB pg_dump to the same volume 03:32-03:36 and sha256'd ~3 GB of
  dumps to 03:40 (episode 1 ended 03:39:44) -- a fuller drive cache than
  my 10-minute burst produced. Plausible, not measured. Episode 2 has no
  co-located bulk write identified.
- That SMR band-rewrite ("media cache exhaustion") specifically is the
  drive-level cause, rather than plain HDD seek latency under fsync
  storms. The 20-40 s cadence of 6-10 s freezes is the SMR signature; the
  drive was not instrumented and the distinction does not change the
  remedy (the ledger must not live on this volume).
- That the 17 `database is locked` 500s in the production log were the
  30 s busy handler expiring behind disk IO. Consistent with run2 (writes
  queue behind the freeze) and with the 33-53 s durations of Vivarium's
  500 rows; not reproduced, because run2 never reached 30 s.

## Two corrections to my own earlier statements, kept beside them

- Journal 18:2x: "`VACUUM INTO` alone took ~10 min there". WRONG. The
  harness measured 3.2 s (`vacuum_into_s`); I had read the copy's mtime,
  which was the last checkpoint during the run. The run itself took 671 s.
- Journal: "6-10 s freezes hitting every client at once". Overstated: the
  producer and reader froze together at the same instants; the consumer
  was not running during the burst's freezes (see above).

## What this changes

The remedy is placement, not code: the ledger (and its blobs and WAL)
belong on a non-SMR volume. That is a copy and a restart in a deploy window
-- NOT done in this step, by the operator's instruction. A6/B3/C7 remain
code items for the same window; none of them is the fix for this.
