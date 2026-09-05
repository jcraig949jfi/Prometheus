-- VIVARIUM v0 -- the experimental execution queue.
--
-- Schema placeholder {schema} is substituted by viv.db.apply_migrations() so
-- the identical DDL can be applied to `viv` (production) and to a throwaway
-- test schema. Idempotent throughout.
--
-- THIS IS MUTABLE ORCHESTRATION STATE. It records what Vivarium was ASKED to
-- run and what mechanically happened. It is NOT the scientific record: SFE
-- holds the immutable ledger and PEW holds the authoritative fossil. The two
-- columns sfe_experiment_id and pew_reference are the only bridge, and they
-- are pointers, never copies.
--
-- v0 2026-09-05, Vivarium.

CREATE SCHEMA IF NOT EXISTS {schema};

CREATE TABLE IF NOT EXISTS {schema}.research_experiment_queue (
    experiment_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at        timestamptz NOT NULL DEFAULT now(),
    created_by        text        NOT NULL,
    source_reason     text        NOT NULL,
    source_evidence   jsonb       NOT NULL DEFAULT '{}'::jsonb,
    experiment_spec   jsonb       NOT NULL,
    spec_hash         text        NOT NULL,
    status            text        NOT NULL DEFAULT 'queued',
    priority          int         NOT NULL DEFAULT 100,
    not_before        timestamptz,
    claimed_by        text,
    claimed_at        timestamptz,
    started_at        timestamptz,
    finished_at       timestamptz,
    sfe_experiment_id text,
    pew_reference     text,
    result_summary    jsonb,
    error             text,

    -- At most ONE row may be non-null here, because a unique index below is
    -- built on it. v0 permits exactly one globally-running experiment and the
    -- DATABASE is what enforces that -- not the loop, which could be run twice
    -- by accident. A second worker's claim raises unique_violation.
    active_singleton  boolean GENERATED ALWAYS AS (
        CASE WHEN status IN ('claimed', 'running') THEN true
             ELSE NULL::boolean END) STORED,

    CONSTRAINT req_status_ck CHECK (status IN
        ('queued', 'claimed', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT req_spec_hash_ck CHECK (spec_hash ~ '^sha256:[0-9a-f]{64}$'),
    CONSTRAINT req_priority_ck CHECK (priority >= 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_req_single_active
    ON {schema}.research_experiment_queue (active_singleton);

CREATE INDEX IF NOT EXISTS ix_req_eligible
    ON {schema}.research_experiment_queue (priority, created_at)
    WHERE status = 'queued';

CREATE INDEX IF NOT EXISTS ix_req_status_finished
    ON {schema}.research_experiment_queue (status, finished_at DESC);

CREATE INDEX IF NOT EXISTS ix_req_spec_hash
    ON {schema}.research_experiment_queue (spec_hash);


-- Append-only operational history. UPDATE and DELETE are refused by trigger,
-- so the transition record cannot be tidied after the fact.
CREATE TABLE IF NOT EXISTS {schema}.research_experiment_events (
    event_id      bigserial PRIMARY KEY,
    experiment_id uuid        NOT NULL
                  REFERENCES {schema}.research_experiment_queue(experiment_id),
    occurred_at   timestamptz NOT NULL DEFAULT now(),
    actor         text        NOT NULL,
    event_type    text        NOT NULL,
    payload       jsonb       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_ree_experiment
    ON {schema}.research_experiment_events (experiment_id, event_id);


-- Worker liveness. Deliberately separate from the queue: "is Vivarium alive"
-- and "is an experiment running" are different questions and conflating them
-- is how a crashed worker starts looking like a busy one.
CREATE TABLE IF NOT EXISTS {schema}.worker_heartbeat (
    worker_id          text PRIMARY KEY,
    host               text NOT NULL,
    pid                int  NOT NULL,
    started_at         timestamptz NOT NULL DEFAULT now(),
    last_seen          timestamptz NOT NULL DEFAULT now(),
    current_experiment uuid,
    build              jsonb NOT NULL DEFAULT '{}'::jsonb
);


-- ---------------------------------------------------------------------------
-- The state machine, enforced in the database.
--
-- queued  -> claimed | cancelled
-- claimed -> running | failed
-- running -> completed | failed
-- completed / failed / cancelled -> NOTHING. Terminal rows are frozen whole,
-- which is what makes "a completed experiment can never be reclaimed" a
-- property of the schema rather than a property of the code that happens to
-- be running today.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION {schema}.enforce_queue_transition()
RETURNS trigger AS $$
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
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_req_transition
    ON {schema}.research_experiment_queue;
CREATE TRIGGER trg_req_transition
    BEFORE UPDATE ON {schema}.research_experiment_queue
    FOR EACH ROW EXECUTE FUNCTION {schema}.enforce_queue_transition();


CREATE OR REPLACE FUNCTION {schema}.refuse_event_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'vivarium: research_experiment_events is append-only (% refused)',
        TG_OP USING ERRCODE = 'raise_exception';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ree_append_only
    ON {schema}.research_experiment_events;
CREATE TRIGGER trg_ree_append_only
    BEFORE UPDATE OR DELETE ON {schema}.research_experiment_events
    FOR EACH ROW EXECUTE FUNCTION {schema}.refuse_event_mutation();
