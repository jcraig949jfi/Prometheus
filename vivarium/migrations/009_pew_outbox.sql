-- 009 (DRAFT): THE PEW OUTBOX -- durable, asynchronous, idempotent, ordered.
--      (Vivarium, 2026-09-17; roles/Vivarium/point_release/PEW_OUTBOX_DESIGN.md)
--
-- Written in the same transaction that closes an attempt; drained by a
-- separate one-shot deliverer; never by the consumer's tick path. A PEW
-- outage can no longer fail completed science or silently lose its fossil.

CREATE TABLE IF NOT EXISTS {schema}.pew_outbox (
    event_id          text PRIMARY KEY,               -- 'sha256:' || hex over (producer|stream|source ids|kind|payload_digest)
    producer          text        NOT NULL,
    stream            text        NOT NULL,
    sequence          bigint      NOT NULL,
    event_kind        text        NOT NULL CHECK (event_kind IN (
                          'WORLD_ANCHORED','ENCOUNTER_RECORDED','ATTEMPT_OPENED','STEP_COMPLETED',
                          'INTERVENTION_RECEIPTED','GATE_EVALUATED','ATTEMPT_TERMINATED','ATTEMPT_REPLAYED')),
    source_attempt    uuid        NOT NULL REFERENCES {schema}.execution_attempt(attempt_id),
    source_step       uuid        REFERENCES {schema}.execution_step(step_id),
    source_experiment uuid        NOT NULL REFERENCES {schema}.research_experiment_queue(experiment_id),
    payload           jsonb       NOT NULL,
    payload_digest    text        NOT NULL,
    created_at        timestamptz NOT NULL DEFAULT now(),
    state             text        NOT NULL DEFAULT 'PENDING'
                      CHECK (state IN ('PENDING','DELIVERED','REJECTED','PARKED')),
    attempts          integer     NOT NULL DEFAULT 0,
    last_attempt_at   timestamptz,
    last_http         integer,
    last_error        text,
    delivered_at      timestamptz,
    pew_reference     text,
    UNIQUE (producer, stream, sequence)
);
CREATE INDEX IF NOT EXISTS pew_outbox_pending ON {schema}.pew_outbox (producer, stream, sequence) WHERE state = 'PENDING';

-- Dense per-stream sequence, assigned at insert under an advisory lock on
-- (producer, stream) so two writers of one stream cannot interleave a gap.
CREATE OR REPLACE FUNCTION {schema}.pew_outbox_sequence() RETURNS trigger AS $$
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext(NEW.producer || '|' || NEW.stream));
    SELECT coalesce(max(sequence), 0) + 1 INTO NEW.sequence
      FROM {schema}.pew_outbox WHERE producer = NEW.producer AND stream = NEW.stream;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pew_outbox_sequence ON {schema}.pew_outbox;
CREATE TRIGGER pew_outbox_sequence BEFORE INSERT ON {schema}.pew_outbox
    FOR EACH ROW EXECUTE FUNCTION {schema}.pew_outbox_sequence();

-- Payload and identity never change; only delivery state does. Ordered
-- delivery: a row may become DELIVERED only if no lower sequence of its
-- stream is still PENDING (a gap is never created by delivering ahead).
CREATE OR REPLACE FUNCTION {schema}.pew_outbox_state_check() RETURNS trigger AS $$
DECLARE
    behind bigint;
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'VIV40: outbox rows are never deleted (a dropped event is a lost fossil)' USING ERRCODE = 'VIV40';
    END IF;
    IF NEW.payload <> OLD.payload OR NEW.payload_digest <> OLD.payload_digest OR NEW.event_id <> OLD.event_id
       OR NEW.sequence <> OLD.sequence OR NEW.event_kind <> OLD.event_kind THEN
        RAISE EXCEPTION 'VIV41: outbox identity and payload are immutable' USING ERRCODE = 'VIV41';
    END IF;
    IF NEW.state = 'DELIVERED' AND OLD.state <> 'DELIVERED' THEN
        SELECT count(*) INTO behind FROM {schema}.pew_outbox
         WHERE producer = NEW.producer AND stream = NEW.stream AND sequence < NEW.sequence AND state = 'PENDING';
        IF behind > 0 THEN
            RAISE EXCEPTION 'VIV42: % lower sequence(s) of this stream are still PENDING; delivery is in order', behind USING ERRCODE = 'VIV42';
        END IF;
    END IF;
    IF OLD.state IN ('DELIVERED','REJECTED') AND NEW.state <> OLD.state THEN
        RAISE EXCEPTION 'VIV43: a % row is terminal', OLD.state USING ERRCODE = 'VIV43';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pew_outbox_state_check ON {schema}.pew_outbox;
CREATE TRIGGER pew_outbox_state_check BEFORE UPDATE OR DELETE ON {schema}.pew_outbox
    FOR EACH ROW EXECUTE FUNCTION {schema}.pew_outbox_state_check();
