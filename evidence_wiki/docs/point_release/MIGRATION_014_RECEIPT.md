# Migration 014 receipt (campaign ingestion) -- 2026-09-17

Author: Mnemosyne, instance m2-9c10ae00. Machine-readable twin:
evidence_wiki/ops/migration_receipts/014_20260917T065006.json (canonical)
and 014_20260917T063645.json (rehearsal).

    migration           014_campaign_ingestion.sql
    sql sha256          ce3c35d65756adf5a8220d61b664848d2a602ff4a65d30c9421de07714da3a35
    kind                additive; IF NOT EXISTS throughout; guard row in
                        ew.schema_migrations; ON CONFLICT DO NOTHING
    schema constant     SCHEMA_VERSION 4 -> 5 (ew/__init__.py); seam
                        battery gate aligned in the same commit
    target              db_system_id 7628127204585430828, prometheus_fire,
                        PostgreSQL 17.9 on M1 (the canonical store; attested
                        by the identity guard on connect)
    applied at          2026-09-17 06:50:07 -0400
    applied by          Mnemosyne @ SPECTREX5, from
                        Prometheus-worktrees/mnemosyne-boot-2026-09-16 @
                        e98d2ee8c (dirty=False)
    revision before     21239 (ew.canonical_revision_seq)
    revision after      21239 (DDL only; no rows written by the migration)
    backup referenced   pewbk-20260917T064348-e96c599b614b, taken 06:46:28
                        -0400, 1,095,694,496 bytes, sha256 e96c599b614b...
                        f178635, ~4 minutes before the migration
    restore path        proven BEFORE the migration: that backup restored
                        into the M2 cluster (7681719240261676752, PG 17.11),
                        RESTORE_VERIFIED, 164/164 tables, loss {}, chain
                        identical (D:\PrometheusBackups\pew\
                        restore_verify_20260917064628.json)
    rehearsal           the same SQL applied first to a restored copy
                        (database pew_rehearsal on the M2 cluster,
                        environment m2-rehearsal), then the reader, the
                        projections, the batteries and the release check
                        were run against a service on that copy; second
                        apply -> already_applied (no-op)
    re-apply on prod    already_applied (no-op), confirmed
    objects after       ew tables 37 -> 44 (+ campaign_observations,
                        ingestion_checkpoints, ingestion_conflicts,
                        producer_events, projections, projection_rows,
                        schema_migrations); typed_refs 32 -> 44 columns
    old rows            untouched; new typed_refs columns NULL on every
                        pre-existing row (NULL = not carried, never UNKNOWN)
    recoverability      re-demonstrated AFTER the migration and after
                        ingestion: backup pewbk-20260917T070006-795ab1c4d323,
                        restore RESTORE_VERIFIED 171/171 tables, loss {}
                        (PEW_POST_MIGRATION_RESTORE_RECEIPT.md)
    rollback            the seven new objects can be dropped and the twelve
                        typed_refs columns removed without touching any
                        pre-existing row; not rehearsed (nothing depends on
                        them yet except this release's own reader)
