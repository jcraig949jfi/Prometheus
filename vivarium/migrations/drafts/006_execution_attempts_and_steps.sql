-- 006 (DRAFT -- point release; NOT applied until the coordinated window):
--      EXPLICIT ATTEMPTS AND DESIGN-KEYED STEPS beneath the queue row.
--      (Vivarium, 2026-09-17; roles/Vivarium/point_release/EXPERIMENT_TRANSACTION_MODEL.md)
--
-- This file lives under migrations/drafts/ so viv.db.apply_migrations, which
-- globs migrations/*.sql (non-recursive), cannot pick it up. Promotion into
-- migrations/ is the deploy act, in the window, after Stage 3 review.
--
-- WHAT IS ABSORBED. Archaeon's campaign runner (archaeon/campaign2/runner.py)
-- proved over campaigns 1-3: numbered attempts never renamed (L-013), a
-- parent attempt for resumes (C3 slot 09 a04 replayed 29 steps), a step key
-- that CONTAINS the design digest (L2-021: the one replay defect in three
-- campaigns was a step key without the design), replayed vs recomputed on
-- the receipt, and a receipt after every step (L-012, rec 3). Here those are
-- rows and triggers, not conventions.
--
-- ADDITIVE. No existing column changes meaning. Old rows are backfilled by
-- 007 (separate, reversible) with attempt_number 1 and NO steps.

CREATE TABLE IF NOT EXISTS {schema}.execution_attempt (
    attempt_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id     uuid        NOT NULL
                      REFERENCES {schema}.research_experiment_queue(experiment_id),
    attempt_number    integer     NOT NULL CHECK (attempt_number >= 1),
    parent_attempt_id uuid        REFERENCES {schema}.execution_attempt(attempt_id),
    design_digest     text        NOT NULL,          -- == the row's spec_hash at open (trigger)
    bundle_hash       text,                          -- START_BUNDLE_SCHEMA.md; NULL = UNKNOWN (pre-release)
    bundle_hash_declared text,                       -- the producer's enqueue-time bundle hash
    worker_id         text        NOT NULL,
    claim_grant       jsonb       NOT NULL DEFAULT '{}'::jsonb,
    opened_at         timestamptz NOT NULL DEFAULT now(),
    closed_at         timestamptz,
    terminal_state    text        CHECK (terminal_state IN ('COMPLETED','FAILED','CANCELLED','STRANDED')),
    termination       jsonb,                         -- TERMINATION_ENVELOPE.md
    receipt_digest    text,
    of_record         boolean     NOT NULL DEFAULT false,
    UNIQUE (experiment_id, attempt_number)
);

-- I3: at most one OPEN attempt per row; at most one of_record.
CREATE UNIQUE INDEX IF NOT EXISTS execution_attempt_one_open
    ON {schema}.execution_attempt (experiment_id) WHERE terminal_state IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS execution_attempt_one_of_record
    ON {schema}.execution_attempt (experiment_id) WHERE of_record;

-- I4 + I5: dense numbering; design_digest equals the row's spec_hash at open;
-- a parent attempt belongs to the same row and is terminal.
CREATE OR REPLACE FUNCTION {schema}.execution_attempt_open_check() RETURNS trigger AS $$
DECLARE
    row_hash text;
    prev_n   integer;
    parent_exp uuid;
    parent_terminal text;
BEGIN
    SELECT spec_hash INTO row_hash FROM {schema}.research_experiment_queue WHERE experiment_id = NEW.experiment_id;
    IF row_hash IS NULL THEN
        RAISE EXCEPTION 'VIV10: attempt for unknown experiment %', NEW.experiment_id USING ERRCODE = 'VIV10';
    END IF;
    IF NEW.design_digest <> row_hash THEN
        RAISE EXCEPTION 'VIV11: attempt design_digest % does not equal the row spec_hash % (a changed spec is a new row, never a new attempt)',
            NEW.design_digest, row_hash USING ERRCODE = 'VIV11';
    END IF;
    SELECT coalesce(max(attempt_number), 0) INTO prev_n FROM {schema}.execution_attempt WHERE experiment_id = NEW.experiment_id;
    IF NEW.attempt_number <> prev_n + 1 THEN
        RAISE EXCEPTION 'VIV12: attempt_number % is not the next number (% attempts exist)', NEW.attempt_number, prev_n USING ERRCODE = 'VIV12';
    END IF;
    IF NEW.parent_attempt_id IS NOT NULL THEN
        SELECT experiment_id, terminal_state INTO parent_exp, parent_terminal
          FROM {schema}.execution_attempt WHERE attempt_id = NEW.parent_attempt_id;
        IF parent_exp IS DISTINCT FROM NEW.experiment_id THEN
            RAISE EXCEPTION 'VIV13: parent attempt belongs to another row' USING ERRCODE = 'VIV13';
        END IF;
        IF parent_terminal IS NULL THEN
            RAISE EXCEPTION 'VIV14: parent attempt is still open; a NEW ATTEMPT opens only after a terminal one' USING ERRCODE = 'VIV14';
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS execution_attempt_open_check ON {schema}.execution_attempt;
CREATE TRIGGER execution_attempt_open_check BEFORE INSERT ON {schema}.execution_attempt
    FOR EACH ROW EXECUTE FUNCTION {schema}.execution_attempt_open_check();

-- Attempts are never deleted and never renumbered.
CREATE OR REPLACE FUNCTION {schema}.execution_attempt_immutable() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'VIV15: attempts are never deleted' USING ERRCODE = 'VIV15';
    END IF;
    IF NEW.attempt_number <> OLD.attempt_number OR NEW.experiment_id <> OLD.experiment_id
       OR NEW.design_digest <> OLD.design_digest OR NEW.opened_at <> OLD.opened_at THEN
        RAISE EXCEPTION 'VIV16: attempt identity columns are immutable' USING ERRCODE = 'VIV16';
    END IF;
    IF OLD.terminal_state IS NOT NULL AND NEW.terminal_state IS DISTINCT FROM OLD.terminal_state THEN
        RAISE EXCEPTION 'VIV17: a terminal attempt is never reopened or re-terminated' USING ERRCODE = 'VIV17';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS execution_attempt_immutable ON {schema}.execution_attempt;
CREATE TRIGGER execution_attempt_immutable BEFORE UPDATE OR DELETE ON {schema}.execution_attempt
    FOR EACH ROW EXECUTE FUNCTION {schema}.execution_attempt_immutable();

CREATE TABLE IF NOT EXISTS {schema}.execution_step (
    step_id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id           uuid        NOT NULL REFERENCES {schema}.execution_attempt(attempt_id),
    step_key             text        NOT NULL,       -- 'idem:' || left(sha256(design_digest || kind || parts), 32)
    step_kind            text        NOT NULL,
    parts                jsonb       NOT NULL DEFAULT '[]'::jsonb,
    status               text        NOT NULL CHECK (status IN ('NEW','REUSED','REPLAYED','RECOMPUTED','FAILED')),
    replay_of_step       uuid        REFERENCES {schema}.execution_step(step_id),
    recomputed_from_step uuid        REFERENCES {schema}.execution_step(step_id),
    idempotency_key      text,
    started_at           timestamptz NOT NULL DEFAULT now(),
    completed_at         timestamptz,
    result               jsonb,
    result_digest        text,
    error                text,
    UNIQUE (attempt_id, step_key)
);

-- I1: the step key CONTAINS the design digest -- recomputed here from the
-- attempt's own design_digest and refused if it differs. The producer-side
-- derivation (viv/stepkey.py, shared with Archaeon's runner) is:
--     'idem:' || left(encode(sha256(convert_to(design_digest || '|' || step_kind || '|' || canonical(parts), 'UTF8')), 'hex'), 32)
-- canonical(parts) = the JSON text of `parts` with sorted keys and no whitespace
-- (jsonb::text is canonical for arrays of scalars, which is what parts are).
CREATE OR REPLACE FUNCTION {schema}.execution_step_key_check() RETURNS trigger AS $$
DECLARE
    dd text;
    expected text;
    prior_exp uuid;
    prior_key text;
BEGIN
    SELECT design_digest INTO dd FROM {schema}.execution_attempt WHERE attempt_id = NEW.attempt_id;
    expected := 'idem:' || left(encode(sha256(convert_to(dd || '|' || NEW.step_kind || '|' || NEW.parts::text, 'UTF8')), 'hex'), 32);
    IF NEW.step_key <> expected THEN
        RAISE EXCEPTION 'VIV20: step_key % is not derived from this attempt''s design digest (expected %); a key without the design cannot enter',
            NEW.step_key, expected USING ERRCODE = 'VIV20';
    END IF;
    -- I2: REUSED/REPLAYED point at a prior step with the SAME key in an attempt of the SAME row.
    IF NEW.status IN ('REUSED','REPLAYED') THEN
        IF NEW.replay_of_step IS NULL THEN
            RAISE EXCEPTION 'VIV21: % requires replay_of_step', NEW.status USING ERRCODE = 'VIV21';
        END IF;
        SELECT a.experiment_id, s.step_key INTO prior_exp, prior_key
          FROM {schema}.execution_step s JOIN {schema}.execution_attempt a ON a.attempt_id = s.attempt_id
         WHERE s.step_id = NEW.replay_of_step;
        IF prior_key IS DISTINCT FROM NEW.step_key OR prior_exp IS DISTINCT FROM
           (SELECT experiment_id FROM {schema}.execution_attempt WHERE attempt_id = NEW.attempt_id) THEN
            RAISE EXCEPTION 'VIV22: replay_of_step must name a prior step with the same key in the same row (never another design)' USING ERRCODE = 'VIV22';
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS execution_step_key_check ON {schema}.execution_step;
CREATE TRIGGER execution_step_key_check BEFORE INSERT ON {schema}.execution_step
    FOR EACH ROW EXECUTE FUNCTION {schema}.execution_step_key_check();

CREATE INDEX IF NOT EXISTS execution_step_by_attempt ON {schema}.execution_step (attempt_id, started_at);
CREATE INDEX IF NOT EXISTS execution_step_by_key ON {schema}.execution_step (step_key);

-- The provenance envelope beside the row (IDENTITY_TRANSLATION_CONTRACT.md s2).
CREATE TABLE IF NOT EXISTS {schema}.provenance_envelope (
    experiment_id    uuid PRIMARY KEY REFERENCES {schema}.research_experiment_queue(experiment_id),
    envelope_version text  NOT NULL,
    envelope         jsonb NOT NULL,
    factors          jsonb NOT NULL DEFAULT '{}'::jsonb,
    recorded_at      timestamptz NOT NULL DEFAULT now()
);
