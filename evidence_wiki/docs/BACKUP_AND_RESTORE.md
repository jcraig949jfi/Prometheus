# PEW Backup, Restore, and Verification Policy

Frozen 2026-09-04. The interpretation/fossil layer is the only copy of what
Prometheus *believes* about its history — SFE holds only what happened.
Append-only protects against overwrite, not against a dead disk.

## What is backed up

    source        postgres@localhost/prometheus_fire (M1, SKULLPORT)
    scope         the whole database, schema `ew` included
    destination   F:\PrometheusBackups\pew\   (override: PEW_BACKUP_DIR)
    format        pg_dump custom (-Fc) --no-owner --no-privileges
                  compressed, selective-restore capable, restorable into a
                  scratch database owned by anyone
    retention     14 most recent dumps (override: PEW_BACKUP_KEEP), rotated
                  automatically; each dump keeps a sibling .manifest.json

Each manifest records: source DB identity, timestamp, format/options,
pg_dump version, byte size, sha256, dump duration, the exact restore command,
and — once verified — the restore verdict.

## Schedule (Task Scheduler, host M1)

    PEWBackupDaily            daily 03:30   ops\pew_backup_daily.cmd
    PEWRestoreVerifyWeekly    Sun   04:30   ops\pew_verify_weekly.cmd
    MnemosyneEvidenceWikiWatchdog  every 5 min (service liveness, pre-existing)

Logs: `F:\PrometheusBackups\pew\backup.log` and `verify.log`.

## Manual use

    python ops/pew_backup.py                 # dump + hash + manifest + rotate
    python ops/pew_backup.py --verify-only   # re-hash newest dump vs manifest
    python ops/pew_restore_verify.py         # scratch restore + PROOF
    python ops/pew_restore_verify.py --keep-scratch   # quarantine, no drop

## The verification policy (why this is not decoration)

A dump nobody has restored is decoration. `pg_restore` returning 0 is not
proof either. `ops/pew_restore_verify.py` therefore:

1. creates a throwaway database `pew_restore_check_<timestamp>` (never named
   like the live database; assertion-guarded),
2. restores the dump into it,
3. compares it against the LIVE database, read-only, on:
   - every `ew.*` base table's row count (27 tables) and the grand total,
   - the complete provenance chain of a named evidence record
     (`PEW_CHAIN_EVIDENCE`, default `E-dbe8c504b8cc` — the first real
     Harmonia end-to-end evidence): evidence -> claim -> packet -> encounter
     -> world -> players -> SFE anchor,
   - namespace census, a representative prod row and test row,
   - canonical revision, ontology registry, vocabulary size,
     object_namespace census, evidence-binding count,
   - the structural constraints that make the seam work: the fossil PK
     `(encounter_id, run_key)` and the evidence -> fossil foreign key,
4. writes the verdict into the dump's manifest,
5. drops the scratch database (unless `--keep-scratch`).

Verdict is `RESTORE_VERIFIED` only if the restore returned 0 AND no table is
missing AND no count differs AND the evidence chain is byte-identical AND the
sample set is byte-identical. Anything else is `RESTORE_NOT_VERIFIED`.

Standing rule: **if the newest dump carrying `verified_restore.verdict ==
RESTORE_VERIFIED` is more than 14 days old, treat the backup as unproven and
run the verifier before relying on it.** The weekly task exists to keep that
from happening; the rule exists for when the task silently stops.

## Restoring for real (disaster procedure)

1. Stop the PEW service (kill `python -m ew.service`; disable the watchdog
   task first, or it restarts the service mid-restore).
2. `createdb prometheus_fire_restored`
3. Run the manifest's `restore_command` against that database.
4. Run `ops/pew_restore_verify.py --dump <that dump>` to confirm the content.
5. Only then rename/point the service at it (`db_name` in `config.json`).

Restoring on top of the live database is deliberately NOT scripted: it is the
one operation that can destroy the thing being protected.

## Known limits (honest)

- Single host, single disk. `F:\PrometheusBackups` sits on the same machine
  as the database. This protects against database corruption, a bad
  migration, and accidental destruction — NOT against loss of M1 itself.
  Off-host copy is the obvious next step and is not done.
- No point-in-time recovery: these are nightly snapshots, not WAL archiving.
  Worst case loses up to one day of writes.
- The dump runs against a live database; it is transactionally consistent
  (pg_dump takes a snapshot) but does not quiesce writers.
