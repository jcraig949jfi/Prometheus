# M2 (SPECTREX5) evidence roots -- inventory for the Atlas index

Currency: 2026-09-19 10:25 UTC (first pass; stat() only: os.listdir,
os.stat, os.walk. NO file was opened, hashed, locked or read. Counts
over 20,000 files per subtree were cut at 20,000; none reached it).
Owner of every root is the seat named; Atlas-M2 owns none of them.
Times are UTC from st_mtime. "newest" is the newest file mtime under
the subtree at the moment of the stat.

Legend for the registry (atlas/registry.json local_roots, host M2):
  LIVE     a service writes here now: stat-only, "no_hash": true; the
           SQLite ledger is NEVER opened (not even ro/immutable) while
           its -wal/-shm move; local_files's idle check decides, IDLE_S
           stays 900.
  ACTIVE   a bench writes here between runs: stat + small-file hashes;
           a file whose mtime is younger than IDLE_S is stat-only.
  IDLE     no write for more than a day: eligible for the collector's
           idle read-only ledger mode, still never for writing.
  EMPTY    exists, holds nothing; recorded as visible-and-empty, dated.

## 1. SFE (Serendipity Foundry Engine), owner Daedalus; engine instance eng_906356f7 (per Atlas)

    root                                   state   files   bytes         newest
    C:\Prometheus-data\sfe                 LIVE    335     111,007,772   2026-09-19T10:24Z
      engine.db                            LIVE    1       36,925,440    2026-09-18T23:15Z (main file)
      engine.db-shm / -wal                 LIVE    2       32,768 / 0    10:20Z / 10:24Z (moving)
      blobs/                               LIVE    306     7,543,998     2026-09-18T15:07Z
      backup/                              ACTIVE  15      58,949,632    2026-09-17T17:01Z
      incidents/                           ACTIVE  4       4,230,879     2026-09-18T23:15Z
      sfengine_m2.log                      LIVE    1       3,312,852     2026-09-19T10:20Z
      sfengine_m2_watchdog.{log,state.json} LIVE   2       1,247 / 423   2026-09-19T10:20Z
      sfengine_m2.cmd, watchdog.ps1        ACTIVE  2       1,138 / 6,654 09-17 / 09-16
      m2.crt, m2.key                       EXCLUDED (credential material; never listed as a source)
    D:\Prometheus-data\sfe                 IDLE    294     86,249,341    2026-09-17T23:12Z
      (the pre-NVMe ledger location; roles/base-role notes the move of
       the SFE ledger to C: on 2026-09-17; nothing has written here
       since 23:12Z that day -- candidate for the idle ledger mode)
    D:\Prometheus-data\sfe-scratch         IDLE    271     165,248,409   2026-09-17T22:56Z
    C:\Prometheus-data\sfe-archive-m1      EMPTY   0       0             -
    C:\Prometheus-data\sfe-scratch         EMPTY   0       0             -
    D:\Prometheus-worktrees\daedalus-sfengine\...\var   EMPTY (only .gitignore); the
      pinned engine worktree keeps its data out of tree

## 2. Archaeon frontier (Deep Frontier / Campaign 6 benches), owner Archaeon

    root: D:\Prometheus-worktrees\archaeon-wse-2026-09-16\archaeon\frontier\runs
    (git-ignored; Atlas #500: the SFE receipts name this worktree as
     workspace.worktree_path; RUN events point at runs/<family>/<spec>/
     RECEIPT.json)                         ACTIVE  230     852,169,338   2026-09-19T10:13Z

    family          files   bytes          newest
    B-scatter       74      215,920,417    2026-09-19T06:12Z
    C4-exapt        39      82,774,367     2026-09-19T08:51Z
    C5-flat         14      176,666,407    2026-09-19T10:04Z
    C6-blind        31      46,843,567     2026-09-19T08:06Z
    C6-unable       2       3,078,150      2026-09-19T00:39Z
    LIN-2d4fd1c7    2       12,951,727     2026-09-18T23:39Z
    LIN-ffc7ae5d    0       0              -            (EMPTY)
    P-boom          42      188,452,206    2026-09-19T09:42Z
    W-artifacts     26      125,482,497    2026-09-19T10:13Z

    root: ...\archaeon\frontier\logs        ACTIVE  7       31,010        2026-09-19T10:04Z
    loop_2026-09-18_epoch1.log; scheduler_2026-09-19_{a..f}.log

    root: D:\Prometheus-data\archaeon       IDLE    20      75,396        2026-09-17T00:51Z
    ABSENT: archaeon/frontier/{runs,logs} under the canonical checkout
    and under D:\Prometheus-worktrees\archaeon-boot-2026-09-16.

## 3. Vivarium (consumer on M2), owner Vivarium

    D:\Prometheus-data\vivarium            LIVE    129     24,878,083    2026-09-19T10:24Z
      var/                                 LIVE    90      586,407       2026-09-19T10:24Z
        (deadman/deliverer state json every 5 min; consumer logs)
      window/                              ACTIVE  31      233,649       2026-09-17T23:40Z
      backups/                             IDLE    1       24,041,802    2026-09-17T13:46Z
      prepare_m2-*.json (4), *.cmd (3)     ACTIVE  7       ~18 KB        09-16 .. 09-17
    D:\Prometheus-worktrees\vivarium-consumer\vivarium\var
      conformance_cache.json               ACTIVE  1       7,681         2026-09-18T23:15Z

## 4. Not present on M2 (dated observation, never "did not happen")

    C:\Prometheus-vault                    ABSENT  (BOOT_M2.md expected Harmonia frames here;
                                                    Harmonia's M2 instances may keep them elsewhere
                                                    -- ask Harmonia before recording a location)

## 5. What this inventory does NOT claim

- Nothing about the CONTENT of any file: no RECEIPT.json was read, no
  ledger counted, no log parsed. Those are collector passes with their
  own receipts (local_files on the registry rows; frontier_runs_m2 on the
  receipt tree), each landing as harvest_run rows with seat='Atlas-M2'.
- Nothing about correctness or completeness of any bench's output.
- Liveness words (LIVE/ACTIVE/IDLE) are a reading of mtimes at 10:25Z on
  2026-09-19 and expire; the registry row's mode, not this file, governs
  what a collector may open.
