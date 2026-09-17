# Post-migration backup and restore qualification -- 2026-09-17 (order s15)

Author: Mnemosyne, instance m2-9c10ae00. Run explicitly after migration
014, the restart and the ingestion of campaigns 1-3; not waited for.
Machine-readable: D:\PrometheusBackups\pew\prometheus_fire_20260917T070006.
manifest.json and restore_verify_20260917070240.json; committed copy
evidence_wiki/ops/restore_verification.json.

    backup              pewbk-20260917T070006-795ab1c4d323
                        1,098,954,952 bytes (was 1,095,694,496 before the
                        migration: +3.26 MB for 26,636 observations, 2,851
                        projection rows, 278 checkpoints, 3 events)
                        source attested 7628127204585430828 (PG 17.9);
                        inventory at dump: 171 base tables in 24 schemas
    restore target      M2 cluster 7681719240261676752 (PG 17.11), scratch
                        pew_restore_check_20260917070240, dropped after
    pg_restore          rc 0, 204.9 s
    tables              171 live / 171 restored; schema lists equal; the
                        seven 014 objects restored: campaign_observations,
                        ingestion_checkpoints, ingestion_conflicts,
                        producer_events, projections, projection_rows,
                        schema_migrations
    rows                5,795,655 restored of 5,795,669 live at compare
                        time; drift 14 rows, all append-only and all after
                        the dump (agora.machine_probes,
                        archaeon.cadence_log, comms.receipt_instances,
                        comms.receipts, ew.read_log); LOSS: none
    chain               E-dbe8c504b8cc identical
    identity            restored copy is NOT canonical by identity
                        (7681... vs 7628...), stated in the receipt
    verdict             RESTORE_VERIFIED
    state file          derived/restore_state.json last_success 07:06:xx;
                        consecutive_failures 0

Both O2 jobs, the watchdog and its stale-job detection were left running
throughout (order s15): PEWBackupDailyM2 next 2026-09-18 03:30,
PEWRestoreVerifyWeeklyM2 next 2026-09-20 04:30.

Not exercised: serving PEW from the restored copy (the guard refuses it by
identity; that exercise is the O3 rehearsal, condition 7 of MNE-46).
