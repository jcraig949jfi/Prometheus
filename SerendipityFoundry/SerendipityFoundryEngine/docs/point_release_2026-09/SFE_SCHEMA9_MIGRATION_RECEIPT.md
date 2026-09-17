# SFE SCHEMA 9 MIGRATION RECEIPT (point release 2026-09)

    seat       Daedalus[m2-d6ecd70b]     engine  https://192.168.1.191:8811 (M2 production)
    ledger     eng_906356f7fb1da180131f9290 at D:\Prometheus-data\sfe\engine.db
    source     schema 8 (build 4dbcd3fd at dd10c9074)
    target     schema 9 (build bc8d3a0c at 1b9286292)
    migration  sfe/store.py Store._migrate_8_to_9 -- six ALTER TABLE ADD COLUMN,
               each PRAGMA table_info-guarded (idempotent), NO backfill, no
               row rewritten, no event touched. Runs inside the store's
               BEGIN IMMEDIATE at first open by the schema-9 build.

=======================================================================
1. WHAT CHANGES IN THE LEDGER (and what does not)
=======================================================================

    observations.logical_time INTEGER NULL
    worlds.manifest / manifest_schema / manifest_hash / labels / termination TEXT NULL
    meta.schema_version '8' -> '9'

    Untouched: every existing row's bytes; the events table and its hash
    chain (head_hash per world, entry_hash per event); idempotency_keys;
    blobs; sessions and tokens; budgets; read scopes and grants.
    Verification after the migration: events count identical; head_hash
    of a sample of worlds identical; verify-anchor on a sample of
    OBSERVATION_RECORDED events returns valid; every old world reads
    manifest_hash/labels/termination = null and every old observation
    reads logical_time = null (tests/test_sfe_v9_facts.py::
    test_old_schema_ledger_migrates_in_place_with_null_facts, and the
    post-restart qualification below).

=======================================================================
2. ROLLBACK / RECOVERY PROCEDURE (written BEFORE deployment, order s6)
=======================================================================

    The schema-8 build REFUSES to open a schema-9 ledger ("db schema
    version 9 is NEWER than this engine's 8; refusing to run"), so a
    rollback is never "run the old build on the migrated ledger". It is:

    R1  stop the service:
          $c = Get-NetTCPConnection -State Listen -LocalPort 8811
          $p = Get-CimInstance Win32_Process -Filter "ProcessId=$($c.OwningProcess)"
          Stop-Process -Id $c.OwningProcess -Force; Stop-Process -Id $p.ParentProcessId -Force
        (the pinned watchdog will try to relaunch within 5 min: do R2-R4
        inside that window, or `Disable-ScheduledTask SFEngineM2Watchdog`
        first and re-enable after)
    R2  put the verified pre-migration backup back:
          move D:\Prometheus-data\sfe\engine.db      -> engine.db.schema9-rolledback-<ts>
          move D:\Prometheus-data\sfe\engine.db-wal  -> (same suffix)   [if present]
          move D:\Prometheus-data\sfe\engine.db-shm  -> (same suffix)   [if present]
          copy D:\Prometheus-data\sfe\backup\engine.db.pre-schema9-<ts>.bak -> engine.db
        The backup was taken with the SQLite backup API and re-opened
        (integrity_check ok, event count == live count, instance id ==
        eng_906356f7) -- its sha256 is in POINT_RELEASE_2026-09-17/preflight.json.
        Any event written to the schema-9 ledger AFTER the migration is
        LOST by this step; the rolled-back file is kept beside it so those
        rows can be read (mode=ro) and re-posted if wanted.
    R3  re-pin the code:
          git -C D:\Prometheus-worktrees\daedalus-sfengine checkout --detach dd10c9074
    R4  start through the supervisor:
          powershell -NoProfile -ExecutionPolicy Bypass -File D:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1
        then confirm /v2/version reports schema 8, hash 4dbcd3fd, instance
        eng_906356f7; re-pin deploy/DEPLOYED_BUILD_M2.json by hand to the
        previous block (its `history` list carries both).
    R5  restore the previous contract:
          copy deploy/POINT_RELEASE_2026-09-17/sfe_contract.PREVIOUS_schema8.json
               -> roles/Harmonia/contracts/sfe_contract.json ; commit
    R6  post the rollback with the reason, on comms, to the same recipients
        as the deployment receipt.

    Partial-failure cases:
      - migration fails mid-way (the store raises at open): the ALTERs ran
        inside one transaction; SQLite rolls it back; the ledger is still
        schema 8; the schema-9 build exits non-zero; the watchdog keeps
        retrying and parks after 3 -> do R3+R4 (no R2 needed; verify with
        `SELECT value FROM meta WHERE key='schema_version'` first).
      - service up on schema 9 but an identity check FAILS (release_v9.py
        apply prints IDENTITY MISMATCH): STOP; do not regenerate the
        contract; diagnose from apply.json; R1-R6 if the ledger identity
        moved (it cannot: the id is a meta row the migration never writes).

=======================================================================
3. RECEIPT (filled by release_v9.py apply; numbers, not adjectives)
=======================================================================

    [appended below after the deployment]
