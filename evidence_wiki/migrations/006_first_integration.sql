-- 006: first-integration provenance (Harmonia handoff, 2026-09-03)
--
-- Defect this fixes: fossil_encounters.encounter_id was the PRIMARY KEY, but
-- Proteus mints encounter_id as a DETERMINISTIC function of
-- (organism_ids, world_binding_id, seed, checkpoint_ids) -- it identifies the
-- encounter SPECIFICATION, not the execution. Two executions of the same spec
-- therefore collided, and ON CONFLICT DO NOTHING dropped the second one while
-- the API still returned HTTP 200. That is a silent partial write.
--
-- Fix: the row key becomes (encounter_id, run_key) where run_key is the
-- execution identity (SFE exp_id/work_id pair, supplied as run_id). Existing
-- rows have no run_id; they collapse to run_key='' and stay unique exactly as
-- they are today. No row is rewritten, nothing is deleted.

ALTER TABLE ew.fossil_encounters
    ADD COLUMN IF NOT EXISTS run_id        text,
    ADD COLUMN IF NOT EXISTS episode_id    text,
    ADD COLUMN IF NOT EXISTS sfe_event_seq bigint,
    ADD COLUMN IF NOT EXISTS producer      jsonb;

-- run_key exists so the composite key is total: NULL run_id (all historical
-- Incubator rows) is a legitimate value meaning "producer sent no run identity".
ALTER TABLE ew.fossil_encounters
    ADD COLUMN IF NOT EXISTS run_key text
    GENERATED ALWAYS AS (coalesce(run_id, '')) STORED;

-- Re-runnable (fixed 2026-09-05, M1 bring-up): migrations/*.sql are re-applied
-- in full on every apply_migration(), and once 007 added
-- evidence_fossil_encounter_fk -- which depends on this primary key's index --
-- an unconditional DROP CONSTRAINT started failing with
-- DependentObjectsStillExist, so no machine could re-run the migration set.
-- Only rebuild the key when it is not ALREADY the composite one.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'ew.fossil_encounters'::regclass
          AND contype = 'p'
          AND pg_get_constraintdef(oid) = 'PRIMARY KEY (encounter_id, run_key)'
    ) THEN
        ALTER TABLE ew.fossil_encounters
            DROP CONSTRAINT IF EXISTS fossil_encounters_pkey;
        ALTER TABLE ew.fossil_encounters
            ADD CONSTRAINT fossil_encounters_pkey PRIMARY KEY (encounter_id, run_key);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_fossil_enc_run    ON ew.fossil_encounters(run_id);
CREATE INDEX IF NOT EXISTS idx_fossil_enc_ep     ON ew.fossil_encounters(episode_id);
CREATE INDEX IF NOT EXISTS idx_fossil_enc_players
    ON ew.fossil_encounters USING gin(players);
CREATE INDEX IF NOT EXISTS idx_fossil_enc_anchor ON ew.fossil_encounters(sfe_entry_hash);

-- Player/world version anchors the first integration needs to join evidence
-- back to the EXACT player and world that produced it. Columns already present
-- carry Proteus's organism identity (player_id = organism_id, genome_hash =
-- manifest hash); these add the producing-component versions Proteus ships in
-- its provenance block.
ALTER TABLE ew.fossil_players
    ADD COLUMN IF NOT EXISTS lineage_id   text,
    ADD COLUMN IF NOT EXISTS generation   integer,
    ADD COLUMN IF NOT EXISTS runtime_hash text,
    ADD COLUMN IF NOT EXISTS producer     jsonb;
CREATE INDEX IF NOT EXISTS idx_fossil_players_lineage ON ew.fossil_players(lineage_id);

ALTER TABLE ew.fossil_worlds
    ADD COLUMN IF NOT EXISTS world_binding_id text,
    ADD COLUMN IF NOT EXISTS seed_root        text,
    ADD COLUMN IF NOT EXISTS producer         jsonb;
