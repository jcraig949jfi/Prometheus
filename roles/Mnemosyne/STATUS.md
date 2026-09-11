# Mnemosyne / PEW - status

Currency: 2026-09-11 15:00 local. Updated at least every four hours of activity.

## What is running

    PEW service      http://192.168.1.202:8377  (M1, SKULLPORT)
                     schema 4, ontology 7, contract pew.fossil.v2,
                     closure pew.closure.v0
    serving from     the pinned worktree mnemosyne-pew (host convention
                     F:\Prometheus-worktrees\mnemosyne-pew\evidence_wiki)
                     detached at e301547dd32d083903a4a727944daac663ea06a5
                     (advanced 2026-09-11 14:44 local from bc3c39eee after
                     the merged-tree tests; service pid 15616, started by
                     the watchdog, model ready 4.59 s after start)
                     main_worktree false, dirty false
    store            PostgreSQL 17, prometheus_fire, schema ew, M1-local
                     db_system_id 7628127204585430828 (M2 has its own)
    scheduled        MnemosyneEvidenceWikiWatchdog (5 min, singleton-guarded)
                     PEWBackupDaily 03:30, PEWRestoreVerifyWeekly Sun 04:30
                     all three run from the pinned worktree

## Last verified

    pew_battery 17/17 (E14 productive_not_present added), seam 12/12,
    closure 19/19, lineage 14/14 + 1 SKIP (no --peer-sfe-url),
    h0h5_refs 16/16 -- run 2026-09-11 14:50 local from the task worktree
    against the service at e301547dd; results committed with this file.
    Watchdog live tick: "ok  health 40ms  hybrid search 1426ms".
    Earlier today (03:48-13:33 local) the batteries graded PEW against a
    STALE ledger copy in the canonical checkout; the engine had moved to
    its off-tree location. Resolution is now config-driven (sfe_db_path in
    the untracked config.local.json), never a drive letter in code.
    Backup: verified-restorable; last RESTORE_VERIFIED against a scratch
    database, chain E-dbe8c504b8cc reconstructed byte-identical.

## Corpora indexed

    cs-h1h0-1-p1   24/24 completed rows -> 96 typed refs
    cs-c3-2       107/150 completed rows -> 428 typed refs
                  (43 still queued/running at index time)
    zero unresolved references, zero errors, zero ARTIFACT refs because
    artifact_locators was empty on every row.

## Changed today (second pass)

    watchdog        measures the property (authenticated hybrid search),
                    writes a last-success line, restarts a PRESENT but
                    non-answering service after 3 ticks, 300 s start grace;
                    6/6 tests on a fake service (evidence_wiki/tests/)
    service         embedding model warmed at startup under a lock; /health
                    async, reports search.ready; first hybrid search after
                    a cold start was 80 s, now 0 s at first request
    identity        per-agent scoped tokens; Kairos holds a READ-ONLY one
                    (R-4); value out of band, sha256 committed
    store guard     ew.db refuses a store that is not the named environment
                    (Hermes #69 accepted); M2 watchdog names m2-local-fork
    config note     "DB is never exposed to the LAN" annotated FALSE (B2)

## Open, and on whom

    OPERATOR  R-1 rotate PEW credentials that lived in git history; R-3
              rotate the archive key prefixes (low urgency, prefixes only,
              never committed). docs/CREDENTIAL_ROTATION_TRACKER.md.
    OPERATOR  D-15: append-only availability events as the canonical form
              for X5. Archaeon concurs. Gates the X5 BUILD, not the design.
    DAEDALUS  SFE /v2/audit/verify-anchor does not assert binds_session, so
              a real anchor from the correct experiment but the WRONG
              SESSION still verifies TRUE at the engine. PEW catches the
              common case with its own splice witness, which is a net and
              not a proof. PEW already consumes the field when present.
    DAEDALUS  Nothing prevents two engines sharing one engine_instance_id.
              Measured 2026-09-05: two clones of one engine.db, same id,
              divergent ledgers. Proposed: a writer lease.
    VIVARIUM  A witness to index, so WP-X5 can be built rather than designed.

## Not run, and said so

    X5 witness round trip: no witness exists yet.
    Cross-machine PEW qualification from M2 itself: all M2-labelled legs so
    far originated on M1.
