-- 002: the queue becomes the SINGLE canonical pre-execution register.
--
-- ORIGIN AND ATTRIBUTION. The design here is ARCHAEON's, written independently
-- in archaeon/migrations/003_adopt_vivarium_queue.sql on 2026-09-06 in response
-- to the same operator directive. It is adopted essentially verbatim, and their
-- reasoning is preserved below rather than paraphrased. It is MOVED here, and
-- their 003 reduced to the retirement note in their own schema, because two
-- files owning one table's DDL is the seam problem this migration exists to
-- end. Vivarium owns the queue's schema; Archaeon owns what it writes into it.
--
-- TWO CORRECTIONS were needed to move it (both mechanical, neither a
-- disagreement):
--   * constraint-existence guards were keyed on conname ALONE, which is
--     unique per table but was being tested globally. Applied to a second
--     schema -- which every Vivarium test does -- the guard found production's
--     constraint and silently skipped creating the test schema's. Now keyed on
--     (conname, conrelid).
--   * `viv.` is now the {schema} placeholder, so the identical DDL applies to
--     production and to a throwaway test schema. An invariant that cannot be
--     tested against a real database is an invariant that will not be tested.
-- One addition: req_replication_not_self, and the execution_attempts view.
--
-- THE PARTITION THIS MIGRATION RESPECTS (Vivarium BOUNDARY_REVIEW §3):
--
--   SEALED EXECUTION INPUTS   experiment_spec, spec_hash
--       -> hashed; handed to the executor; nothing added here, ever.
--   PROVENANCE                created_by, source_reason, source_evidence,
--                             priority, not_before, and EVERY COLUMN BELOW
--       -> immutable, recorded, never visible to the execution path,
--          and NEVER part of spec_hash.
--   EXECUTION RESULT          status, timestamps, sfe_experiment_id,
--                             pew_reference, result_summary, error
--
-- Every column added here is PROVENANCE. Harmonia S14: "spec_hash is a fixed
-- point against an adversary who VARIES the spec, but not against one who makes
-- every spec identical" -- and since spec_hash is the substrate's grouping
-- surface, an arm label inside it would split the derived universe along the
-- arm boundary. So arm and family identity live in typed columns out here,
-- never in notes, world.name, experiment_kind, or any hashed field.

-- --------------------------------------------------------------- relations
-- Experimental-DESIGN facts, declared before execution. All nullable: none of
-- this is globally required, and a row that declares no family is a legitimate
-- ordinary experiment, not a deficient one.
ALTER TABLE {schema}.research_experiment_queue
    ADD COLUMN IF NOT EXISTS family_id         text,
    ADD COLUMN IF NOT EXISTS arm_id            text,
    ADD COLUMN IF NOT EXISTS replication_of    uuid,
    ADD COLUMN IF NOT EXISTS candidate_set_id  text,
    ADD COLUMN IF NOT EXISTS request_key       text;

COMMENT ON COLUMN {schema}.research_experiment_queue.family_id IS
 'Comparison/family identity, DECLARED BEFORE EXECUTION. Provenance, never hashed.';
COMMENT ON COLUMN {schema}.research_experiment_queue.arm_id IS
 'Arm within family_id. Provenance, never hashed. Two rows in different arms may have byte-identical specs and MUST: that is what makes the comparison a comparison rather than two different experiments.';
COMMENT ON COLUMN {schema}.research_experiment_queue.replication_of IS
 'A deliberate repeat SAYS it is a repeat. Distinguishes replication from accidental double submission.';
COMMENT ON COLUMN {schema}.research_experiment_queue.candidate_set_id IS
 'Membership of a candidate set registered BEFORE selection. The unchosen are cancelled, never deleted, which is the only class-A trace of a selection decision in the architecture (Harmonia S15).';
COMMENT ON COLUMN {schema}.research_experiment_queue.request_key IS
 'Requester-supplied idempotency key. A resubmission is refused; a deliberate replication supplies a NEW key and sets replication_of.';

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conname = 'req_arm_needs_family'
                      AND conrelid = '{schema}.research_experiment_queue'::regclass) THEN
        ALTER TABLE {schema}.research_experiment_queue
            ADD CONSTRAINT req_arm_needs_family
            CHECK (arm_id IS NULL OR family_id IS NOT NULL);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conname = 'req_replication_fk'
                      AND conrelid = '{schema}.research_experiment_queue'::regclass) THEN
        ALTER TABLE {schema}.research_experiment_queue
            ADD CONSTRAINT req_replication_fk FOREIGN KEY (replication_of)
            REFERENCES {schema}.research_experiment_queue(experiment_id);
    END IF;
    -- Vivarium addition: the one self-reference that makes the relation
    -- meaningless rather than merely wrong.
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conname = 'req_replication_not_self'
                      AND conrelid = '{schema}.research_experiment_queue'::regclass) THEN
        ALTER TABLE {schema}.research_experiment_queue
            ADD CONSTRAINT req_replication_not_self
            CHECK (replication_of IS NULL OR replication_of <> experiment_id);
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_req_request_key
    ON {schema}.research_experiment_queue (request_key)
    WHERE request_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_req_family
    ON {schema}.research_experiment_queue (family_id, arm_id);
CREATE INDEX IF NOT EXISTS ix_req_candidate_set
    ON {schema}.research_experiment_queue (candidate_set_id);

-- ------------------------------------------------------- candidate honesty
-- THERE IS DELIBERATELY NO candidate_set_size COLUMN.
--
-- The operator's rule is "never attest a candidate count that was not actually
-- registered before selection", and Vivarium cannot honestly attest a count it
-- never saw (it is handed one candidate by construction). A stored count is an
-- ATTESTATION and can be wrong. A count DERIVED from the registered rows
-- cannot: it is the register counting itself.
DROP VIEW IF EXISTS {schema}.candidate_sets;
CREATE VIEW {schema}.candidate_sets AS
    SELECT candidate_set_id,
           count(*)                                       AS registered,
           count(*) FILTER (WHERE status = 'cancelled')   AS cancelled,
           count(*) FILTER (WHERE status <> 'cancelled')  AS retained,
           count(*) FILTER (WHERE started_at IS NOT NULL) AS executed,
           min(created_at)                                AS registered_at,
           max(created_at)                                AS last_registered_at,
           count(DISTINCT created_by)                     AS registrars
      FROM {schema}.research_experiment_queue
     WHERE candidate_set_id IS NOT NULL
     GROUP BY candidate_set_id;

COMMENT ON VIEW {schema}.candidate_sets IS
 'Candidate-set sizes DERIVED from the register, never attested. registered = rows actually written before selection; retained = those not cancelled. A set whose rows were written across a wide created_at span was not registered atomically and its "before selection" claim is weaker -- which is why both timestamps are exposed.';

-- ------------------------------------------------------- Archaeon cadence
-- Cadence moves onto this table unchanged in MEANING: at most SIX autonomous
-- proposals per UTC day, at least FOUR HOURS apart, enforced by the database so
-- concurrent instances cannot evade it. The gate and the decision log stay in
-- the archaeon schema (they are Archaeon's, not the queue's).
--
-- Only a SELECTED row consumes quota. A candidate that is registered and then
-- cancelled has cadence_day_ordinal NULL: registering twenty candidates must not
-- consume twenty of the six daily slots, or candidate registration would be
-- unaffordable and the class-B -> class-A conversion would never be used.
ALTER TABLE {schema}.research_experiment_queue
    ADD COLUMN IF NOT EXISTS cadence_lane        text,
    ADD COLUMN IF NOT EXISTS cadence_day_ordinal integer;

ALTER TABLE {schema}.research_experiment_queue
    ADD COLUMN IF NOT EXISTS cadence_utc_day date
    GENERATED ALWAYS AS ((created_at AT TIME ZONE 'UTC')::date) STORED;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conname = 'req_cadence_ordinal_range'
                      AND conrelid = '{schema}.research_experiment_queue'::regclass) THEN
        ALTER TABLE {schema}.research_experiment_queue
            ADD CONSTRAINT req_cadence_ordinal_range
            CHECK (cadence_day_ordinal IS NULL
                   OR (cadence_day_ordinal >= 0 AND cadence_day_ordinal < 6));
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint
                    WHERE conname = 'req_cadence_lane_present'
                      AND conrelid = '{schema}.research_experiment_queue'::regclass) THEN
        ALTER TABLE {schema}.research_experiment_queue
            ADD CONSTRAINT req_cadence_lane_present
            CHECK (cadence_day_ordinal IS NULL OR cadence_lane IS NOT NULL);
    END IF;
END $$;

-- The hard daily cap, as a DATABASE property. Survives an application bug.
CREATE UNIQUE INDEX IF NOT EXISTS uq_req_cadence_day_ordinal
    ON {schema}.research_experiment_queue
       (cadence_lane, cadence_utc_day, cadence_day_ordinal)
    WHERE cadence_day_ordinal IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_req_cadence_lane_day
    ON {schema}.research_experiment_queue (cadence_lane, cadence_utc_day);

COMMENT ON COLUMN {schema}.research_experiment_queue.cadence_day_ordinal IS
 '0..5 for a SELECTED autonomous proposal; NULL for registered-but-cancelled candidates and for human rows. With uq_req_cadence_day_ordinal this caps autonomous execution at six per UTC day per lane at the DATABASE level.';

-- ------------------------------------------------------------------- views
-- "Never attempted" is COMPUTED, not stored. A failed row that never reached
-- `running` has no started_at, and that is already the exact discriminator --
-- so it is published as a view rather than encoded as a seventh state.
DROP VIEW IF EXISTS {schema}.execution_attempts;
CREATE VIEW {schema}.execution_attempts AS
SELECT experiment_id, status, spec_hash, request_key, family_id, arm_id,
       candidate_set_id, replication_of, sfe_experiment_id, pew_reference,
       created_at, started_at, finished_at, error,
       (started_at IS NOT NULL)                       AS crossed_execution_boundary,
       (status = 'failed' AND started_at IS NULL)     AS rejected_before_execution,
       (status = 'failed' AND started_at IS NOT NULL) AS failed_during_execution,
       (status IN ('claimed', 'running'))             AS holding_the_slot
  FROM {schema}.research_experiment_queue;

COMMENT ON VIEW {schema}.execution_attempts IS
 'Every attempted execution, and the distinction between "certainly never executed" (rejected while claimed) and "may have executed" (reached running). Computed from started_at; no seventh queue state exists or is needed.';

-- ------------------------------------------ extend the freeze to relations
-- Vivarium's BEFORE UPDATE trigger already freezes spec, spec_hash, created_at
-- and the three original provenance columns. The relation columns are the same
-- KIND of fact -- design declared before execution -- and a mutable family_id
-- or arm_id would let a comparison be re-drawn after its outcomes were visible,
-- which is precisely the retrospective grouping this whole contract exists to
-- prevent. cadence_day_ordinal is frozen for the same reason: a re-assignable
-- ordinal is not a cap.
--
-- The function is REPLACED rather than duplicated so one trigger governs the
-- row. The original six checks are preserved verbatim.
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
