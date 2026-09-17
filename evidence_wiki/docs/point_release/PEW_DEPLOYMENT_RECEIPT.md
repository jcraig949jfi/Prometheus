# PEW deployment receipt -- point release 2026-09-17

Author: Mnemosyne, instance m2-9c10ae00.

## Sequence (local time, -0400)

    06:26  reader dry run over origin/main (20,288 pending rows for C3)
    06:36  REHEARSAL: latest O2 dump restored into pew_rehearsal on the M2
           cluster (214 s); guard: named env connects, unnamed refused;
           014 applied (rehearsal), re-applied -> no-op; C3 ingested twice
           (20,288 new / 0 new); reach_level v1 + corridor_edge v1 built,
           rebuild equal; temp service on 8379: release check 14/15 (R0
           fails on the copy by design), batteries 17/17 12/12 19/19
           14/14+1 16/16; DEFECT FOUND: the service bound its port on the
           restored copy without a named env -> fixed (store attested
           before bind), re-tested: exit 1, nothing listening
    06:4x  release candidate committed e98d2ee8c, pushed, verified
    06:43  pre-migration backup pewbk-20260917T064348-e96c599b614b
    06:46  restore qualification of it: RESTORE_VERIFIED (164/164)
    06:50  migration 014 applied to the canonical store
    06:50  pin advanced 90b8e6806 -> e98d2ee8c; clean restart (pid 7632)
    06:5x  post-restart qualification: five batteries green; S2 cheat
           (fork) FAILS; guard/identity unit tests 13/13; ecology 7/7;
           minted 7/7
    06:53  Campaign 3 ingested (ING-20260917T065356-e98d2ee8): 20,288 new;
           again: 0 new; projections built; rebuild equal; release check
           15/15; s18 queries answered
    06:58  reader 1.1 (design factors in run strata; envelope refresh):
           0 new, 20,288 envelopes refreshed; repeat: 0/0
    06:58  Campaign 2 ingested (5,086 new; repeat 0); Campaign 1
           (1,262 new; repeat 0; 1,230 reconstructed attempt ids)
    07:00  post-migration backup pewbk-20260917T070006-795ab1c4d323;
           restore qualification RESTORE_VERIFIED 171/171
    07:0x  final code committed 8665b1bdf, pushed, verified; pin advanced;
           clean restart (pid 19480 at 07:07:30); requalification: five
           batteries green, release check 15/15, queries ok, three
           rebuild-checks equal, base-role self-test 11/11
    07:xx  rehearsal database dropped

## What is deployed

    pinned worktree    D:\Prometheus-worktrees\mnemosyne-pew, detached at
                       8665b1bdf653a35912b1fa450c6cbe7c3d401c34, clean
    service            pid 19480, started 2026-09-17 07:07:30 -0400 by the
                       watchdog from .venv-m2; 0.0.0.0:8377
    store              prometheus-canonical, db_system_id
                       7628127204585430828, 192.168.1.202:5432, attested
                       at 07:07:31 before the port was bound
    scheduled tasks    MnemosyneEvidenceWikiWatchdogM2 (5 min),
                       PEWBackupDailyM2 (03:30), PEWRestoreVerifyWeeklyM2
                       (Sun 04:30) -- all from the pinned worktree; the
                       watchdog's next ticks after the restart: ok
    untracked config   config.local.json in the pinned worktree
                       (canonical_db_host, backup_dir, backup_keep,
                       restore_target_host, sfe_verify_url/cacert/token,
                       sfe_db_path)

## Not deployed / not changed

    M1: nothing. The M1 service (dead since 09-15 17:11) and the M1
    backup jobs are untouched and not relied on. No client re-pointed.
    Canonical database not moved (O3 deferred).
