# Mnemosyne / PEW — D-23 workspace compliance

Built from base `2627fe37cfc002926b9763f9f4ac7345b67caa5d` in
`F:\Prometheus-worktrees\mnemosyne-d23` on branch `mnemosyne/workspace-d23`
(tree clean at commit).

## Worktrees

    TASK    F:\Prometheus-worktrees\mnemosyne-d23    mnemosyne/workspace-d23
            base 2627fe37c -> integrated at 7c36278f2; removed after this lands.
    PINNED  F:\Prometheus-worktrees\mnemosyne-pew    detached @ 7c36278f2
            runs the PEW service and both scheduled jobs.

Nothing of mine remains under `F:\Prometheus\` or under a session scratchpad.

## Long-running processes moved (rule 6)

All three of my scheduled tasks previously executed out of the canonical
checkout. They now point at the pinned worktree:

    MnemosyneEvidenceWikiWatchdog  ...\mnemosyne-pew\evidence_wiki\scripts\ew_watchdog.ps1
    PEWBackupDaily                 ...\mnemosyne-pew\evidence_wiki\ops\pew_backup_daily.cmd
    PEWRestoreVerifyWeekly         ...\mnemosyne-pew\evidence_wiki\ops\pew_verify_weekly.cmd

The two `.cmd` wrappers are now path-relative (`%~dp0..`) rather than
hardcoding `F:\Prometheus\evidence_wiki`, so relocating the pinned worktree
needs a task-path change and never an edit to a committed file. The untracked
credential override `config.local.json` was carried across by hand and is
gitignored in the new location; it is never committed.

Restart was announced and took ~15s. The service now reports its own tree:

    GET /api/v1/health -> workspace {base_sha 7c36278f2363..., branch HEAD,
        worktree_path F:\Prometheus-worktrees\mnemosyne-pew\evidence_wiki,
        dirty false, main_worktree FALSE}

## Startup refusal (rule 1, rule d)

`evidence_wiki/ew/workspace.py` — the same git-dir vs git-common-dir test as
`archaeon/workspace.py`, deliberately identical so the two cannot drift into
disagreeing about what "canonical" means. Wired into every PEW entry point:
the service, `pew_backup`, `pew_restore_verify`, `index_candidate_sets`, and
all five batteries. Verified both directions: `is_main_worktree` is True for
`F:\Prometheus\evidence_wiki` and False for the worktree, and
`assert_not_canonical` raises on the former. Override `EW_ALLOW_CANONICAL=1`
is read-only and is recorded in the receipt whenever used.

## Canonical checkout: what I claimed and deleted (rule a)

14 files in the snapshot were mine.

DELETED (my own untracked scratch, all byte-identical to the version already
on main — redundant copies, the one permitted write, done once):

    evidence_wiki/integration/index_receipt_cs-c3-2.json
    evidence_wiki/integration/index_receipt_cs-h1h0-1-p1.json
    evidence_wiki/integration/rebuild_cs-h1h0-1-p1.json
    evidence_wiki/migrations/012_corpus_ref_kinds_and_axes.sql
    evidence_wiki/ops/index_candidate_sets.py   (stale pre-guard copy;
                                                 main's is newer)

CLAIMED (committed from this worktree):

    evidence_wiki/ops/restore_verification.json — the weekly restore-verify
    output, the only one of the 14 that differed from main.

LEFT ALONE, deliberately: the other 8 tracked files show as ` M` only because
the canonical checkout's HEAD is `vivarium/v0-2026-09-05`, a branch that no
longer exists on origin. Their content is byte-identical to `origin/main` and
was already claimed by `6bf553f87`. They are tracked files, not scratch;
deleting them would be a destructive mutation of the canonical working tree,
which rule 1 forbids. They resolve the moment the canonical checkout is moved
to main — which is not my write to make.

## Worktrees and branches cleaned (rule b)

    removed   ...\4fa7a285-...\scratchpad\sfe_pristine  (session temp; created
              for the 2026-09-05 split-brain proof, long outlived its session)
    deleted   local branch mnemosyne/evidence-wiki-v0 (remote deleted
              2026-09-10; merged into origin/main)
    remote    no branches of mine remain on origin

## A defect this migration exposed, and fixed

Moving the service surfaced a real bug in my watchdog: **it had no singleton
guard**. Its health probe used a 5-second timeout, but under host load PEW has
answered health in 7–15s, so a timed-out probe was read as "service is down"
and started another one. Three `ew.service` processes were live at once after
the move, fighting over port 8377 and the connection pool — each duplicate
making the next probe slower, so the watchdog manufactured the outage it
exists to prevent.

Fixed: the probe timeout is 20s, and before starting anything the watchdog
checks for a listener on 8377 and for any live `ew.service` process, logging
and exiting if either is present. Verified by firing the task three times
against a healthy service: still exactly one process.

This is the same class as Daedalus's R-F (no singleton guard on the SFE
launcher). Worth his attention; his restart discipline is a tree kill for the
same reason.

## Verification after the move

Against the service running from the pinned worktree:

    pew_battery      16/16
    seam_battery     12/12
    closure_battery  19/19   (C4a-d exercised for real; SFE was briefly down
                              mid-migration and the gates are now SKIP rather
                              than FAIL when a dependency is unavailable — an
                              absent dependency is not a broken mechanism, and
                              a skipped gate is never counted as a pass)
    lineage_battery  15/15
    h0h5_refs        16/16

One portability fix was needed: the batteries resolved SFE's ledger
(`var/engine.db`) relative to their own tree, and that file is RUNTIME state
that exists only where the engine runs — a worktree has none. They now honour
`PEW_SFE_DB`, then the tree-relative path, then the canonical location.
Reading the canonical checkout is permitted; the invariant forbids mutating
it, not reading it.
