-- 008 (DRAFT): START BUNDLES, INTERVENTION RECEIPTS, GATE RECEIPTS.
--      (Vivarium, 2026-09-17; START_BUNDLE_SCHEMA.md, INTERVENTION_RECEIPT_SCHEMA.md,
--       PREREQUISITE_GATE_RECEIPT.md)
-- Additive. Nothing here is read by the executor; everything is recorded
-- beside the attempt. Vivarium fills four bundle sub-keys; the rest is verbatim.

CREATE TABLE IF NOT EXISTS {schema}.start_bundle (
    bundle_hash   text PRIMARY KEY,                  -- 'sha256:' || hex over canonical JSON
    bundle_version text NOT NULL,
    bundle        jsonb NOT NULL,
    declared_by   text  NOT NULL,
    first_seen    timestamptz NOT NULL DEFAULT now()
);

-- The producer's enqueue-time bundle part rides on the row, unhashed column,
-- hashed content (bundle_hash_declared on the attempt points at it).
ALTER TABLE {schema}.research_experiment_queue
    ADD COLUMN IF NOT EXISTS bundle_declared jsonb;

ALTER TABLE {schema}.execution_attempt
    ADD CONSTRAINT execution_attempt_bundle_fk
        FOREIGN KEY (bundle_hash) REFERENCES {schema}.start_bundle(bundle_hash);

CREATE TABLE IF NOT EXISTS {schema}.intervention_receipt (
    receipt_id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id        uuid  NOT NULL REFERENCES {schema}.execution_attempt(attempt_id),
    step_id           uuid  REFERENCES {schema}.execution_step(step_id),
    intervention_id   text  NOT NULL,
    intervention_kind text  NOT NULL,
    writer            text  NOT NULL CHECK (writer IN ('executor','engine','producer')),
    intended          jsonb NOT NULL,
    realised          jsonb NOT NULL,
    logical_time      jsonb,
    target            jsonb NOT NULL,
    supplied          jsonb NOT NULL DEFAULT '[]'::jsonb,
    source_ids        jsonb NOT NULL DEFAULT '[]'::jsonb,
    result            text  NOT NULL CHECK (result IN ('APPLIED','PARTIAL','NOT_APPLIED','REJECTED','UNKNOWN')),
    reason            text,
    post_ref          jsonb,
    recorded_at       timestamptz NOT NULL DEFAULT now(),
    UNIQUE (attempt_id, intervention_id)
);

CREATE TABLE IF NOT EXISTS {schema}.gate_receipt (
    receipt_id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id      uuid  NOT NULL REFERENCES {schema}.execution_attempt(attempt_id),
    step_id         uuid  REFERENCES {schema}.execution_step(step_id),
    gate_id         text  NOT NULL,
    phase           text  NOT NULL,
    condition       text  NOT NULL,
    measurement_ref jsonb NOT NULL,
    measured        jsonb NOT NULL,
    rule            jsonb NOT NULL,
    reference       jsonb NOT NULL,                 -- as RESOLVED at evaluation: a literal, or the measured value a ref pointed at
    result          text  NOT NULL CHECK (result IN ('PASS','FAIL','NOT_EVALUABLE')),
    action_taken    text,                           -- NULL = evaluated, action not yet recorded (crash between the two)
    definition_ref  text  NOT NULL,
    evaluated_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS gate_receipt_by_attempt ON {schema}.gate_receipt (attempt_id, evaluated_at);

-- Receipts are append-only.
CREATE OR REPLACE FUNCTION {schema}.receipt_append_only() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'VIV30: receipts are never deleted' USING ERRCODE = 'VIV30';
    END IF;
    IF TG_TABLE_NAME = 'gate_receipt' AND OLD.action_taken IS NULL AND NEW.action_taken IS NOT NULL
       AND NEW.measured = OLD.measured AND NEW.result = OLD.result THEN
        RETURN NEW;                                  -- the one legal update: recording the action after evaluation
    END IF;
    RAISE EXCEPTION 'VIV31: receipts are append-only' USING ERRCODE = 'VIV31';
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS intervention_receipt_append_only ON {schema}.intervention_receipt;
CREATE TRIGGER intervention_receipt_append_only BEFORE UPDATE OR DELETE ON {schema}.intervention_receipt
    FOR EACH ROW EXECUTE FUNCTION {schema}.receipt_append_only();
DROP TRIGGER IF EXISTS gate_receipt_append_only ON {schema}.gate_receipt;
CREATE TRIGGER gate_receipt_append_only BEFORE UPDATE OR DELETE ON {schema}.gate_receipt
    FOR EACH ROW EXECUTE FUNCTION {schema}.receipt_append_only();
