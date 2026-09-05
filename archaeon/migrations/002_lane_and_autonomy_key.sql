-- 002: key autonomy on WHY a row exists, and give the quota a lane.
--      (Archaeon, 2026-09-05, found by the cadence tests)
--
-- Migration 001 had two defects, both surfaced by trying to test it.
--
-- DEFECT 1: autonomy was keyed on the literal string 'archaeon' in
-- created_by. That is a NAME, and autonomy is not a name -- it is the fact
-- that no human chose this experiment. source_reason already records exactly
-- that: 'weak_signal' and 'exploration' are Archaeon's own decisions, 'human'
-- is a person's. Keying the constraint on source_reason means a second
-- Archaeon instance running under a different created_by handle (a hostname, a
-- service account) still consumes the same quota, which is the whole point of
-- the cap. Under 001 it would have escaped it entirely by being called
-- something else.
--
-- DEFECT 2: there was exactly one quota namespace, so a test could not
-- exercise the cap without either consuming production's six proposals for the
-- day or colliding with them. A cadence mechanism that cannot be tested
-- against a real database without corrupting production is a mechanism that
-- will not be tested. `lane` fixes that: the quota, the unique index and the
-- serializing gate are all per-lane. Production is lane 'prod' (the default,
-- so every existing row keeps its meaning); tests use a unique lane each.
--
-- Re-runnable: every statement is guarded.

ALTER TABLE archaeon.experiment_queue
    ADD COLUMN IF NOT EXISTS lane text NOT NULL DEFAULT 'prod';

COMMENT ON COLUMN archaeon.experiment_queue.lane IS
 'Quota namespace. Production is ''prod''. The daily cap, the four-hour separation and the serializing gate are ALL scoped to a lane, so a test lane can exercise the real database mechanism without consuming or colliding with production quota.';

-- --------------------------------------------------- autonomy by source_reason
ALTER TABLE archaeon.experiment_queue
    DROP CONSTRAINT IF EXISTS ordinal_presence;
ALTER TABLE archaeon.experiment_queue
    DROP CONSTRAINT IF EXISTS autonomous_reason;

ALTER TABLE archaeon.experiment_queue
    ADD CONSTRAINT ordinal_presence CHECK (
        (source_reason IN ('weak_signal', 'exploration')
         AND day_ordinal IS NOT NULL)
        OR (source_reason = 'human' AND day_ordinal IS NULL));

-- ------------------------------------------------ the cap, now lane-scoped
DROP INDEX IF EXISTS archaeon.uq_archaeon_day_ordinal;
CREATE UNIQUE INDEX IF NOT EXISTS uq_archaeon_day_ordinal
    ON archaeon.experiment_queue (lane, utc_day, day_ordinal)
    WHERE source_reason IN ('weak_signal', 'exploration');

CREATE INDEX IF NOT EXISTS ix_archaeon_queue_lane_day
    ON archaeon.experiment_queue (lane, utc_day, source_reason);

-- ------------------------------------------------------ the gate, per lane
ALTER TABLE archaeon.cadence_gate
    ADD COLUMN IF NOT EXISTS lane text;

UPDATE archaeon.cadence_gate SET lane = 'prod'
 WHERE lane IS NULL AND gate_id = 'singleton';

-- The production gate keeps its historical id so an in-flight process that
-- still holds the old row is not orphaned; new lanes get a gate row per lane.
INSERT INTO archaeon.cadence_gate (gate_id, lane, note)
VALUES ('lane:prod', 'prod',
        'Per-lane serializing gate. Take FOR UPDATE before evaluating cadence.')
ON CONFLICT (gate_id) DO NOTHING;

-- ------------------------------------------------------- cadence log gains lane
ALTER TABLE archaeon.cadence_log
    ADD COLUMN IF NOT EXISTS lane text NOT NULL DEFAULT 'prod';
