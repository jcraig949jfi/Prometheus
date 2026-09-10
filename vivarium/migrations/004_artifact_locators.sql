-- 004: ARTIFACT LOCATORS -- the address book, and why it is its own column.
--      (Vivarium, 2026-09-09, H0-H5 iteration 1, contract C1)
--
-- A row has carried two kinds of fact since 001: the SEALED SPEC (everything
-- that can change the result, hashed into spec_hash) and PROVENANCE (who asked,
-- why, in which arm -- frozen by the trigger, never hashed, never projected
-- into an ExecutionRequest).
--
-- The artifact loader introduces a third, and pretending it is one of the first
-- two would be the mistake. ADDRESSING: digest -> {source_world,
-- source_artifact}, meaning "a copy of the bytes this spec already sealed can
-- be found here".
--
--   Not sealed input. The spec names the BYTES by digest. Two rows addressing
--   two different copies of byte-identical artifacts are the same experiment
--   and must hash the same, or an arm comparison would be destroyed by where
--   the producer happened to put a file.
--
--   Not provenance either. created_by and arm_id describe a decision, and
--   preflight would work identically with them deleted. Without an address
--   nothing resolves at all.
--
-- WHAT KEEPS THIS FROM REOPENING THE BLINDING HOLE. Preflight verifies every
-- resolved artifact against the digest inside spec_hash. So a locator has
-- exactly two possible effects and no third: the sealed bytes arrive, or the
-- attempt is rejected. It can change WHETHER an experiment runs, never WHAT it
-- computes. tests/test_h0h5_artifacts.py asserts that directly by running one
-- spec through two locators over byte-identical artifacts.
--
-- KEYED BY DIGEST, not by slot name, for two reasons: a dependency four levels
-- into a closure addresses the same way a root slot does, and an address book
-- keyed by digest cannot carry an entry the sealed spec never mentions.
--
-- FROZEN LIKE PROVENANCE. The 001 BEFORE UPDATE trigger freezes a terminal
-- row whole; this column is added to the same frozen set explicitly, so a
-- completed row's addresses are as immutable as its arm label. Re-addressing a
-- finished experiment would silently change what a receipt appears to describe.

ALTER TABLE {schema}.research_experiment_queue
    ADD COLUMN IF NOT EXISTS artifact_locators jsonb NOT NULL
        DEFAULT '{}'::jsonb;

COMMENT ON COLUMN {schema}.research_experiment_queue.artifact_locators IS
    'ADDRESSING (not sealed input, not provenance): digest -> {source_world, '
    'source_artifact}. Preflight verifies resolved bytes against the digest '
    'inside spec_hash, so a locator can only decide WHETHER a run happens, '
    'never WHAT it computes.';

-- An address book is an object keyed by content digests. Enforced in the
-- database and not only in Python, because a row written by another seat's
-- client is still a row this loop will try to execute.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint c
                   JOIN pg_class t ON t.oid = c.conrelid
                   JOIN pg_namespace n ON n.oid = t.relnamespace
                   WHERE c.conname = 'queue_artifact_locators_shape_ck'
                     AND t.relname = 'research_experiment_queue'
                     AND n.nspname = '{schema}') THEN
        ALTER TABLE {schema}.research_experiment_queue
            ADD CONSTRAINT queue_artifact_locators_shape_ck
            CHECK (jsonb_typeof(artifact_locators) = 'object');
    END IF;
END $$;

-- The rows that consume artifacts, for operators and for analysis. A row with
-- an empty address book is every row that existed before today, and it stays
-- exactly what it was.
CREATE OR REPLACE VIEW {schema}.artifact_consuming_rows AS
SELECT experiment_id, created_at, created_by, status, spec_hash,
       experiment_spec #>> '{work,kind}'      AS kind,
       artifact_locators,
       jsonb_object_keys(artifact_locators)   AS consumed_digest
FROM {schema}.research_experiment_queue
WHERE artifact_locators <> '{}'::jsonb;


-- The trigger is REPLACED, not duplicated, so one function governs the row.
-- The nine existing checks are preserved verbatim; artifact_locators joins
-- them. Re-addressing a row after it was claimed would let a second attempt
-- resolve different bytes than the first -- which the digest check would
-- catch, but the ROW would then be a record of two different resolutions
-- wearing one identity.
CREATE OR REPLACE FUNCTION {schema}.enforce_queue_transition()
RETURNS trigger AS $fn$
DECLARE
    legal boolean;
BEGIN
    IF OLD.status IN ('completed', 'failed', 'cancelled') THEN
        RAISE EXCEPTION
            'vivarium: experiment % is terminal (%) and is frozen; refusing UPDATE',
            OLD.experiment_id, OLD.status
            USING ERRCODE = 'raise_exception';
    END IF;

    IF NEW.experiment_spec IS DISTINCT FROM OLD.experiment_spec
       OR NEW.spec_hash IS DISTINCT FROM OLD.spec_hash
       OR NEW.created_at IS DISTINCT FROM OLD.created_at
       OR NEW.created_by IS DISTINCT FROM OLD.created_by
       OR NEW.source_reason IS DISTINCT FROM OLD.source_reason
       OR NEW.source_evidence IS DISTINCT FROM OLD.source_evidence THEN
        RAISE EXCEPTION
            'vivarium: the sealed request (spec, spec_hash, provenance) of % is immutable',
            OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    -- added 2026-09-06 (archaeon/003): the experimental-relation declaration
    IF NEW.family_id IS DISTINCT FROM OLD.family_id
       OR NEW.arm_id IS DISTINCT FROM OLD.arm_id
       OR NEW.replication_of IS DISTINCT FROM OLD.replication_of
       OR NEW.candidate_set_id IS DISTINCT FROM OLD.candidate_set_id
       OR NEW.request_key IS DISTINCT FROM OLD.request_key
       OR NEW.cadence_lane IS DISTINCT FROM OLD.cadence_lane
       OR NEW.cadence_day_ordinal IS DISTINCT FROM OLD.cadence_day_ordinal THEN
        RAISE EXCEPTION
            'vivarium: the experimental-relation declaration (family, arm, '
            'replication_of, candidate set, cadence) of % is immutable; a '
            'comparison may not be re-drawn after execution', OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    -- added 2026-09-09 (vivarium/004): the address book
    IF NEW.artifact_locators IS DISTINCT FROM OLD.artifact_locators THEN
        RAISE EXCEPTION
            'vivarium: the artifact address book of % is immutable; an '
            'experiment may not be re-addressed after admission',
            OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    IF NEW.status = OLD.status THEN
        RETURN NEW;                       -- annotation, not a transition
    END IF;

    legal := (OLD.status = 'queued'  AND NEW.status IN ('claimed', 'cancelled'))
          OR (OLD.status = 'claimed' AND NEW.status IN ('running', 'failed'))
          OR (OLD.status = 'running' AND NEW.status IN ('completed', 'failed'));

    IF NOT legal THEN
        RAISE EXCEPTION 'vivarium: illegal transition % -> % on %',
            OLD.status, NEW.status, OLD.experiment_id
            USING ERRCODE = 'raise_exception';
    END IF;

    RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;
