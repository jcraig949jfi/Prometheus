# PEW Backup, Restore, and Verification Policy

Frozen 2026-09-04 (M1 single-host); REWRITTEN 2026-09-17 under operator
ruling MNE-D1 (roles/Mnemosyne/prompts/2026-09-17_point_release/
02_OPERATOR_RULING_MNE-D1.md): O2, an M2-OWNED nightly dump of the
canonical cluster with a weekly restore qualification into the M2
cluster, so that recoverability is proven INDEPENDENTLY of the machine
that holds the database. The 2026-09-04 arrangement is kept below as
"M1 jobs" and is no longer the only copy.

The interpretation/fossil layer is the only copy of what Prometheus
*believes* about its history; SFE holds only what happened. Append-only
protects against overwrite, not against a dead disk. Backup ownership and
database ownership are separate questions: independent recoverability
first, physical relocation (O3) second.

## What is backed up

    source        the CANONICAL cluster, prometheus_fire, PostgreSQL 17.9,
                  db_system_id 7628127204585430828, on M1 (SKULLPORT).
                  The source is ATTESTED by pg_control_system() identity
                  against comms/environments.json before a byte is
                  written; a dump of any other cluster is refused, not
                  labelled (cheat control on record: the M2 fork named as
                  source -> REFUSED, 0 files).
    scope         the whole database: ew, comms, viv, archaeon, agora,
                  sigma, noesis, zeros, charon_duckdb, xref ... (164 base
                  tables in 24 schemas on 2026-09-17; ~3.0 GB on disk,
                  ~1.1 GB as a dump)
    format        pg_dump custom (-Fc) --no-owner --no-privileges:
                  compressed, selective-restore capable, restorable into a
                  scratch database on ANOTHER cluster owned by anyone
    manifest      beside every dump: backup_id, source identity (db_system_id,
                  server version, size, schema/table inventory, ew canonical
                  revision, ew/comms row totals), backup host and machine,
                  pg_dump version, byte size, sha256, duration, retention,
                  workspace receipt, the exact restore command, and (once
                  verified) the restore verdict

## Where, and who owns it

    M2 jobs (O2, owner Mnemosyne, this ecosystem)
      PEWBackupDailyM2          daily 03:30  ops\pew_backup_daily_m2.cmd
      PEWRestoreVerifyWeeklyM2  Sun 04:30    ops\pew_verify_weekly_m2.cmd
      run from the PINNED worktree mnemosyne-pew (D-23 s6), interpreter
      .venv-m2 resolved through the common git dir, S4U principal;
      destination D:\PrometheusBackups\pew on M2 (config.local.json
      backup_dir; retention backup_keep = 14 dumps, ~15 GB); restore
      target the M2 local cluster 127.0.0.1 (config.local.json
      restore_target_host; PostgreSQL 17.11, restores a 17.9 dump)
      logs derived\backup_m2.log, derived\verify_m2.log in the pinned tree
      state derived\backup_state.json, derived\restore_state.json
    M1 jobs (2026-09-04, still registered on M1, UNOBSERVABLE from M2)
      PEWBackupDaily 03:30 / PEWRestoreVerifyWeekly Sun 04:30, destination
      F:\PrometheusBackups\pew on M1's own disk. Whether they still fire
      is not known from this ecosystem (MONITORS rows 16-17 UNLOCATED).
      They are not relied on.

Host-specific values (canonical_db_host, backup_dir, backup_keep,
restore_target_host) live in the untracked evidence_wiki/config.local.json,
never in code (WORKING_CONTRACT s9). Environment overrides: EW_DB_HOST,
PEW_BACKUP_DIR, PEW_BACKUP_KEEP, PEW_RESTORE_TARGET_HOST, PGBIN.

## Manual use (from a TASK worktree, never the pinned one)

    python ops/pew_backup.py                 # attest + dump + hash + manifest + rotate
    python ops/pew_backup.py --verify-only   # re-hash newest dump vs manifest
    python ops/pew_restore_verify.py         # scratch restore on the target + PROOF
    python ops/pew_restore_verify.py --keep-scratch    # quarantine, no drop
    python ops/pew_restore_verify.py --write-tracked   # refresh the committed
                                                       # ops/restore_verification.json

## The verification policy (why this is not decoration)

A dump nobody has restored is decoration; a restore only ever proven on
the source host is not independence; `pg_restore` returning 0 is not
proof. `ops/pew_restore_verify.py` therefore:

1. re-hashes the dump against its manifest (dump_intact),
2. creates a throwaway database `pew_restore_check_<timestamp>` ON THE
   TARGET cluster (never named like the live database; assertion-guarded),
3. restores the dump into it,
4. compares it against the LIVE canonical cluster, read-only, on:
   - the row count of EVERY base table in EVERY user schema (164 on
     2026-09-17) and the grand total, with the schema lists equal;
   - the complete provenance chain of a named evidence record
     (`PEW_CHAIN_EVIDENCE`, default `E-dbe8c504b8cc`, the first real
     Harmonia end-to-end evidence): evidence -> claim -> packet ->
     encounter -> world -> players -> SFE anchor;
   - a sample set (namespace census, prod/test rows, canonical revision,
     ontology registry, vocabulary, object_namespace, evidence bindings,
     the fossil PK and the evidence -> fossil FK, comms last message),
5. records BOTH cluster identities and server versions, and states
   whether the restored copy is canonical by identity (on M2 it is not:
   the target's db_system_id is 7681719240261676752; a restored copy is a
   copy, and every store-identity guard will refuse to treat it as the
   canonical store until O3 re-keys the registry -- that refusal is
   correct),
6. classifies count differences: restored <= live on a table is DRIFT
   (rows arrived on the live source after the dump; comms, read/write
   logs and machine probes always show a few), anything else is LOSS,
7. writes the verdict into the dump's manifest, a receipt beside the dumps
   (`restore_verify_<stamp>.json`, `restore_verify_latest.json`) and the
   state file, and drops the scratch database (unless `--keep-scratch`).

Verdict is `RESTORE_VERIFIED` only if the dump is intact AND the restore
returned 0 AND no table is missing AND the schema lists are equal AND
there is no LOSS AND the evidence chain is byte-identical. Sample
differences are reported beside the verdict (live drift is expected).
Anything else is `RESTORE_NOT_VERIFIED`.

## Alarms (operator ruling: "alert visibly on missed backup or failed
## restore qualification")

    failed backup        pew_backup.py posts one comms report to Mnemosyne
                         and increments consecutive_failures in the state
    failed qualification pew_restore_verify.py posts one comms report and
                         increments consecutive_failures
    MISSED (never ran)   a job that did not run cannot alarm; the M2
                         watchdog (scripts/ew_watchdog_m2.ps1) reads the
                         two state files' ages on every 5-minute tick:
                         backup older than 36 h, qualification older than
                         8 d -> a STALE log line per tick and ONE comms
                         report per stale day (exercised 2026-09-17 with a
                         fabricated 390 h old state: posted once, not on
                         the next tick)
    if comms is down     the state file and the watchdog log are the alarm
                         of record; MONITORS.md rows carry the thresholds

Standing rule: **if the newest dump carrying `verified_restore.verdict ==
RESTORE_VERIFIED` is more than 14 days old, treat the backup as unproven and
run the verifier before relying on it.**

## First O2 cycle, on record (2026-09-17)

    backup 1  pewbk-20260917T055050-fea46038fa3c  1,095,684,908 B  153 s  (hand-run, task worktree)
    restore   into 127.0.0.1 (M2, PG 17.11), scratch pew_restore_check_20260917055336,
              rc 0, 199 s, 164/164 tables, 5,765,459 / 5,765,473 rows (14 = drift,
              loss {}), chain identical, RESTORE_VERIFIED
    backup 2  pewbk-20260917T055922-1b1967c7670a  1,095,689,332 B  234 s  (the scheduled
              task PEWBackupDailyM2 itself, S4U, pinned worktree c46a882e9)
    receipts  D:\PrometheusBackups\pew\*.manifest.json, restore_verify_*.json;
              committed copy ops/restore_verification.json

## Restoring for real (disaster procedure)

1. Decide WHICH cluster becomes canonical. A restore never changes that on
   its own: comms/environments.json names the canonical environment by
   db_system_id and every client's guard refuses anything else.
2. Stop the PEW service and disable its watchdog task (or it restarts the
   service mid-restore).
3. On the chosen cluster: `createdb prometheus_fire_restored`, run the
   manifest's `restore_command` with `<TARGET_HOST>`/`<TARGET_DB>` filled
   in, then `ops/pew_restore_verify.py --dump <that dump>` against it.
4. Only then: update comms/environments.json (the new db_system_id), the
   service's config.local.json, every client's EW_DB_HOST -- and rotate
   credentials (tracker R-1) in the same window. This is O3; see
   docs/point_release/PEW_STORE_LOCATION_DISPOSITION.md and the ruling's
   seven conditions.

Restoring on top of the live database is deliberately NOT scripted: it is
the one operation that can destroy the thing being protected.

## Known limits (honest)

- No point-in-time recovery: nightly snapshots, not WAL archiving. Worst
  case loses up to one day of writes.
- The dump runs against a live database; it is transactionally consistent
  (pg_dump takes a snapshot) but does not quiesce writers, so the compare
  always shows a few rows of drift on append-only tables.
- Two hosts, still one site. The M2 copy protects against loss of M1; a
  loss of both machines is not covered (MNE-18, off-site copy, open).
- The restore qualification proves the DUMP restores on a 17.11 cluster;
  it does not exercise the service against the restored copy (the guard
  would refuse it by identity). That exercise is part of the O3 rehearsal.
