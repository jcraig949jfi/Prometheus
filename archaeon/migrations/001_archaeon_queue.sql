-- 001: the Archaeon experiment queue and its cadence invariants.
--       (Archaeon, 2026-09-05, v0 build)
--
-- The queue is the seam between Archaeon and Vivarium. Archaeon writes; a
-- runner claims and completes. Cadence is enforced HERE, in the database,
-- because two Archaeon instances share exactly one database and nothing else
-- -- not a clock, not a lockfile, not a process.
--
-- THREE INDEPENDENT MECHANISMS enforce the cadence, so a bug in any one of
-- them does not silently lift the limit:
--
--   (a) day_ordinal + UNIQUE (utc_day, day_ordinal) WHERE created_by='archaeon'
--       with CHECK (day_ordinal < 6). A seventh autonomous proposal in one UTC
--       day has no ordinal left to take, and two instances racing for the same
--       ordinal collide on the unique index. This holds even if the
--       application code is wrong, and it is the mechanism of last resort.
--
--   (b) archaeon.cadence_gate, a single row taken with SELECT ... FOR UPDATE
--       at the start of every enqueue transaction. It serializes concurrent
--       enqueues so the four-hour check below cannot be evaluated by two
--       instances against the same stale state.
--
--   (c) an explicit four-hour check against max(created_at), evaluated inside
--       that serialized transaction using the DATABASE clock.
--
-- Human-created rows (created_by <> 'archaeon') are deliberately outside all
-- three: the partial unique index is scoped to 'archaeon', the ordinal is NULL
-- for them, and the gate is not taken. A human does not consume Archaeon's
-- autonomous quota.

CREATE SCHEMA IF NOT EXISTS archaeon;

-- --------------------------------------------------------------- the queue
CREATE TABLE IF NOT EXISTS archaeon.experiment_queue (
    proposal_id     text PRIMARY KEY,           -- AX-<sha[:12]>
    created_at      timestamptz NOT NULL DEFAULT now(),

    -- utc_day is DERIVED, never supplied. A caller passing its own local date
    -- is exactly the failure the project clock exists to prevent.
    utc_day         date GENERATED ALWAYS AS
                        ((created_at AT TIME ZONE 'UTC')::date) STORED,

    -- 0..5 for autonomous rows; NULL for human rows.
    day_ordinal     integer,

    created_by      text NOT NULL,              -- 'archaeon' | a human handle
    source_reason   text NOT NULL
                    CHECK (source_reason IN ('weak_signal', 'exploration',
                                             'human')),

    -- The SFE-compatible experiment specification, verbatim.
    spec            jsonb NOT NULL,
    spec_hash       text NOT NULL,

    -- Full archaeological provenance. Structure defined by
    -- archaeon/provenance.py; the NOT NULL is the point.
    source_evidence jsonb NOT NULL,

    -- Reproducibility handles, lifted out of source_evidence so they are
    -- queryable without unpacking jsonb.
    corpus_hash     text,
    config_fingerprint text,
    seed            numeric,                    -- exploration seed, else NULL

    -- Vivarium's side of the seam.
    status          text NOT NULL DEFAULT 'QUEUED'
                    CHECK (status IN ('QUEUED', 'CLAIMED', 'RUNNING',
                                      'DONE', 'FAILED', 'CANCELLED')),
    claimed_by      text,
    claimed_at      timestamptz,
    completed_at    timestamptz,
    result_ref      jsonb,

    CONSTRAINT ordinal_range CHECK (day_ordinal IS NULL
                                    OR (day_ordinal >= 0 AND day_ordinal < 6)),
    -- An autonomous row MUST carry an ordinal; a human row MUST NOT.
    -- Without this, an autonomous row could evade (a) by leaving it NULL.
    CONSTRAINT ordinal_presence CHECK (
        (created_by = 'archaeon' AND day_ordinal IS NOT NULL)
        OR (created_by <> 'archaeon' AND day_ordinal IS NULL)),
    CONSTRAINT autonomous_reason CHECK (
        created_by <> 'archaeon' OR source_reason IN ('weak_signal',
                                                      'exploration'))
);

-- (a) The hard daily cap. Partial, so only autonomous rows are constrained.
CREATE UNIQUE INDEX IF NOT EXISTS uq_archaeon_day_ordinal
    ON archaeon.experiment_queue (utc_day, day_ordinal)
    WHERE created_by = 'archaeon';

CREATE INDEX IF NOT EXISTS ix_archaeon_queue_status
    ON archaeon.experiment_queue (status, created_at);
CREATE INDEX IF NOT EXISTS ix_archaeon_queue_day
    ON archaeon.experiment_queue (utc_day, created_by);
CREATE INDEX IF NOT EXISTS ix_archaeon_queue_corpus
    ON archaeon.experiment_queue (corpus_hash);

-- ------------------------------------------------------------- (b) the gate
-- One row. Every autonomous enqueue takes it FOR UPDATE first, which turns
-- concurrent enqueues into a queue rather than a race.
CREATE TABLE IF NOT EXISTS archaeon.cadence_gate (
    gate_id     text PRIMARY KEY,
    note        text NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now()
);
INSERT INTO archaeon.cadence_gate (gate_id, note)
VALUES ('singleton',
        'Take FOR UPDATE before evaluating cadence. Serializes concurrent Archaeon instances.')
ON CONFLICT (gate_id) DO NOTHING;

-- ------------------------------------------------------- cadence audit trail
-- Every cadence DECISION, including the refusals. A refusal that leaves no
-- trace is indistinguishable from a cycle that never ran, and Archaeon would
-- then have no way to show it respected its own limits.
CREATE TABLE IF NOT EXISTS archaeon.cadence_log (
    log_id       bigserial PRIMARY KEY,
    decided_at   timestamptz NOT NULL DEFAULT now(),
    instance     text NOT NULL,             -- host/pid of the deciding process
    decision     text NOT NULL
                 CHECK (decision IN ('ADMITTED', 'REFUSED_DAILY_CAP',
                                     'REFUSED_MIN_SEPARATION',
                                     'REFUSED_RACE_LOST')),
    detail       jsonb NOT NULL,
    proposal_id  text REFERENCES archaeon.experiment_queue(proposal_id)
);
CREATE INDEX IF NOT EXISTS ix_archaeon_cadence_log_time
    ON archaeon.cadence_log (decided_at DESC);

COMMENT ON TABLE archaeon.experiment_queue IS
 'Archaeon -> Vivarium seam. source_reason weak_signal|exploration|human. Rows are PROBE REQUESTS, never scientific conclusions: source_evidence records which fossils triggered a proposal and which thresholds were crossed, and nothing in it may be read as a finding.';
COMMENT ON COLUMN archaeon.experiment_queue.day_ordinal IS
 '0..5 for created_by=archaeon; NULL for human rows. With uq_archaeon_day_ordinal this is a DATABASE-level cap of six autonomous proposals per UTC day that application code cannot evade.';
COMMENT ON COLUMN archaeon.experiment_queue.source_evidence IS
 'Archaeological provenance: triggering fossil rows and their SFE anchors, detector + version, values that crossed thresholds, the thresholds themselves, all candidates considered, the selection rule, and the exploration seed + candidate_set_hash when applicable.';
