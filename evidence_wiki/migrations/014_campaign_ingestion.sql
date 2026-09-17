-- 014: campaign ingestion (Mnemosyne, 2026-09-17, PEW point release under the
--      operator's implementation order; contract
--      docs/point_release/PEW_CAMPAIGN_INGESTION_CONTRACT.md)
--
-- Measured before this migration: PEW held ZERO rows from SFE campaigns 1-3
-- (31 receipts of record, 1,265 reachability rows, 155 corridor rows, ~150
-- ledger rows, ~1,000 per-run rows on origin/main; no cmp* client in
-- ew.write_log, ever). This migration is the landing surface for a READER
-- over those committed files and for producer outboxes (Vivarium) that
-- post events. It adds; it rewrites nothing. Every old row keeps its
-- meaning: the new envelope columns on typed_refs are NULL for rows that
-- predate them (NULL = not applicable / not carried; the literal 'UNKNOWN'
-- is written only by a reader that KNOWS an owner exists and the value was
-- not supplied). Idempotent: every statement is IF NOT EXISTS; the
-- schema_migrations row is inserted ON CONFLICT DO NOTHING.
--
-- Raw vs projection (amendment 1 s2, order s5): ew.campaign_observations
-- and ew.producer_events hold what a producer WROTE, including any label
-- the producer itself assigned (level_as_written is Archaeon's level at
-- Archaeon's code identity, stored as sent). ew.projections /
-- ew.projection_rows hold what PEW DERIVED, versioned, with the definition,
-- thresholds and source code identity pinned; a rebuild never touches the
-- raw tables.

-- ---------------------------------------------------------------- guard
CREATE TABLE IF NOT EXISTS ew.schema_migrations (
    migration_id      text PRIMARY KEY,          -- '014'
    applied_at        timestamptz NOT NULL DEFAULT now(),
    applied_by        text,                       -- seat[instance] @ host
    applied_from      text,                       -- worktree + base sha
    revision_before   bigint,                     -- ew.canonical_revision_seq before
    backup_id         text,                       -- the O2 backup taken first
    restore_receipt   text,                       -- the restore proof that backup passed
    notes             text
);

-- ------------------------------------------- identity envelope on typed_refs
ALTER TABLE ew.typed_refs
    ADD COLUMN IF NOT EXISTS campaign_id          text,
    ADD COLUMN IF NOT EXISTS harness_id           text,   -- Archaeon's experiment id, shared-envelope name (Vivarium A1)
    ADD COLUMN IF NOT EXISTS execution_id         text,   -- Vivarium's row id
    ADD COLUMN IF NOT EXISTS design_id            text,   -- prereg_digest (Archaeon) or spec_hash (Vivarium), stated by design_kind
    ADD COLUMN IF NOT EXISTS design_kind          text,   -- 'prereg_digest' | 'spec_hash'
    ADD COLUMN IF NOT EXISTS attempt_id           text,
    ADD COLUMN IF NOT EXISTS step_id              text,
    ADD COLUMN IF NOT EXISTS foundry_profile      text,
    ADD COLUMN IF NOT EXISTS schedule_id          text,
    ADD COLUMN IF NOT EXISTS rng_identity         text,
    ADD COLUMN IF NOT EXISTS logical_time         integer,
    ADD COLUMN IF NOT EXISTS origin_kind          text;   -- 'producer' | 'reconstructed'

-- ------------------------------------------------- raw campaign observations
CREATE TABLE IF NOT EXISTS ew.campaign_observations (
    observation_id     text PRIMARY KEY,   -- 'CO-' || sha256(kind || canonical row json)[:32]: content-addressed;
                                           -- the same producer row anywhere is ONE observation
    kind               text NOT NULL,      -- reachability | corridor | ledger | receipt | attempt | design |
                                           -- run | generation | engine_record | artifact_ref | import
    -- identity envelope (order s4): UNKNOWN = owner exists, value not supplied; NULL = not applicable
    campaign_id        text NOT NULL,
    harness_id         text,
    execution_id       text,
    design_id          text,
    design_kind        text,
    attempt_id         text,
    attempt_number     integer,
    resumed_from_attempt integer,
    step_id            text,
    foundry_profile    text,
    schedule_id        text,
    rng_identity       text,
    world_id           text,
    engine_instance_id text,
    engine_source_hash text,
    arm                text,
    seed               integer,
    generation         integer,             -- logical time where the row is time-indexed
    -- stratification coordinates as the producer wrote them (order s7)
    cell               text,
    knobs_digest       text,
    regime             text,
    n_pop              integer,
    g_budget           integer,
    e_episodes         integer,
    strata             jsonb,               -- {cell, evaluator_family, foundry_profile, climber, operator, arm, budget_class, world_version, start_profile}
    -- typed measured subset (the fields every earned projection reads); the full row is in measured
    best_train_max     double precision,
    heldout            double precision,
    first_foothold_gen integer,
    first_solved_gen   integer,
    first_shelf_gen    integer,
    summit_candidate_gen integer,
    first_summit_gen   integer,
    stopped_on_solve   boolean,
    summit_censored    boolean,
    level_as_written   text,                -- the PRODUCER's label at the producer's code identity; never PEW's
    reached            boolean,
    source_cell        text,
    target_cell        text,
    source_competence  double precision,
    direct_reuse_best  double precision,
    edge_kind          text,
    -- termination / censoring facts (order s13) where the producer supplied them
    termination_reason text,
    horizon            integer,
    censored           boolean,
    censoring_reason   text,
    measured           jsonb NOT NULL,      -- the producer row, verbatim (numbers as written)
    definition_version text,                -- producer code identity that wrote the row (e.g. archaeon.wse.reachability@<blob sha>)
    producer_row_digest text NOT NULL,      -- sha256 of the canonical row json
    origin_kind        text NOT NULL DEFAULT 'producer',   -- 'producer' | 'reconstructed'
    source_commit      text NOT NULL,       -- git commit the file was read from
    source_path        text NOT NULL,
    source_line        integer,             -- line (jsonl) or index (json array); NULL for whole-file rows
    source_blob_sha    text,                -- git blob sha of the file
    reader_version     text NOT NULL,       -- ew.campaign_ingest.READER_VERSION
    ingest_run_id      text NOT NULL,
    recorded_at        timestamptz,         -- producer's recorded_at where present
    ingested_at        timestamptz NOT NULL DEFAULT now(),
    revision           bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS co_campaign_kind_idx   ON ew.campaign_observations(campaign_id, kind);
CREATE INDEX IF NOT EXISTS co_harness_idx         ON ew.campaign_observations(harness_id);
CREATE INDEX IF NOT EXISTS co_attempt_idx         ON ew.campaign_observations(attempt_id);
CREATE INDEX IF NOT EXISTS co_cell_idx            ON ew.campaign_observations(cell);
CREATE INDEX IF NOT EXISTS co_world_idx           ON ew.campaign_observations(world_id);
CREATE INDEX IF NOT EXISTS co_foundry_idx         ON ew.campaign_observations(foundry_profile);
CREATE INDEX IF NOT EXISTS co_source_idx          ON ew.campaign_observations(source_path, source_line);
CREATE INDEX IF NOT EXISTS co_strata_gin          ON ew.campaign_observations USING gin (strata);
CREATE INDEX IF NOT EXISTS co_measured_gin        ON ew.campaign_observations USING gin (measured);

-- ------------------------------------------------- ingestion checkpoints
CREATE TABLE IF NOT EXISTS ew.ingestion_checkpoints (
    producer          text NOT NULL,        -- 'archaeon' | 'vivarium' | ...
    stream            text NOT NULL,        -- a committed path ('archaeon/campaign3/REACHABILITY.jsonl') or an outbox stream name
    last_seq          bigint,               -- last line/index or producer seq ingested
    last_event_id     text,
    last_digest       text,                 -- content digest at last ingest (file blob sha or payload digest)
    source_commit     text,                 -- git commit for file streams
    reader_version    text,
    rows_seen         bigint NOT NULL DEFAULT 0,
    rows_new          bigint NOT NULL DEFAULT 0,
    gaps              jsonb NOT NULL DEFAULT '[]'::jsonb,   -- [{from, to, seen_at}] never healed by inference
    updated_at        timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (producer, stream)
);

-- Append-only: a producer row that arrives at an already-seen (stream, seq)
-- with a DIFFERENT digest, or a committed line whose content changed between
-- commits. Never an overwrite; the original observation stays.
CREATE TABLE IF NOT EXISTS ew.ingestion_conflicts (
    conflict_id       bigserial PRIMARY KEY,
    producer          text NOT NULL,
    stream            text NOT NULL,
    seq               bigint,
    stored_digest     text,
    offered_digest    text,
    stored_observation_id text,
    offered_at        timestamptz NOT NULL DEFAULT now(),
    source_commit     text,
    note              text
);

-- ------------------------------------------------- producer events (outbox)
-- The receiving half of Vivarium's producer-side outbox (amendment 6D, order
-- s14). kind is the producer's family name as text (WORLD_STARTED,
-- CAPABILITY_MEASURED, ...); PEW validates shape and identity, never meaning.
-- No family is pre-declared here: a family exists when a producer sends it.
CREATE TABLE IF NOT EXISTS ew.producer_events (
    event_id          text NOT NULL,        -- producer-minted stable id (Vivarium: sha(attempt, step, kind, n))
    producer          text NOT NULL,
    stream            text NOT NULL,
    seq               bigint NOT NULL,
    kind              text NOT NULL,
    logical_time      integer,
    actor             text,
    payload           jsonb NOT NULL,
    payload_digest    text NOT NULL,        -- sha256 of canonical payload json
    envelope          jsonb,                -- identity envelope as sent (campaign_id, harness_id, execution_id, ...)
    received_at       timestamptz NOT NULL DEFAULT now(),
    machine           text,
    agent             text,
    revision          bigint NOT NULL,
    PRIMARY KEY (event_id),
    UNIQUE (producer, stream, seq)
);
CREATE INDEX IF NOT EXISTS pe_kind_idx     ON ew.producer_events(kind);
CREATE INDEX IF NOT EXISTS pe_envelope_gin ON ew.producer_events USING gin (envelope);

-- ------------------------------------------------- projection registry
CREATE TABLE IF NOT EXISTS ew.projections (
    projection_name      text NOT NULL,
    projection_version   text NOT NULL,
    definition           text NOT NULL,     -- prose of the rule as pinned
    source_kinds         text[] NOT NULL,   -- campaign_observations.kind / producer_events.kind read
    source_code_identity text NOT NULL,     -- owner's code identity the rule is copied from (e.g. archaeon/wse/reachability.py@<blob sha>)
    thresholds           jsonb NOT NULL,    -- every number the rule uses
    owner_seat           text NOT NULL,     -- author/owner of the SCIENTIFIC definition (Archaeon for reach/corridor)
    builder_version      text NOT NULL,     -- ew.projections.BUILDER_VERSION
    built_at             timestamptz,
    evidence_count       bigint,
    rebuild_digest       text,              -- sha256 over the sorted projection rows; equal on rebuild
    limitations          text NOT NULL,
    status               text NOT NULL DEFAULT 'BUILT',   -- BUILT | SUPERSEDED | RETIRED (rows are never deleted)
    PRIMARY KEY (projection_name, projection_version)
);
CREATE TABLE IF NOT EXISTS ew.projection_rows (
    projection_name    text NOT NULL,
    projection_version text NOT NULL,
    row_key            text NOT NULL,
    payload            jsonb NOT NULL,
    evidence_ids       text[] NOT NULL,     -- campaign_observations.observation_id the row was derived from
    evidence_count     integer NOT NULL,
    built_at           timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (projection_name, projection_version, row_key)
);
CREATE INDEX IF NOT EXISTS pr_payload_gin ON ew.projection_rows USING gin (payload);

-- ------------------------------------------------- record the migration
INSERT INTO ew.schema_migrations (migration_id, applied_by, notes)
VALUES ('014', current_user, 'campaign ingestion: envelope, campaign_observations, checkpoints, conflicts, producer_events, projections; applied by ops/apply_migration.py which overwrites applied_by/applied_from/revision_before/backup_id/restore_receipt with the real values')
ON CONFLICT (migration_id) DO NOTHING;
