-- 011: typed reference/presence index, idempotent publication, evidence axes
--      (Mnemosyne, 2026-09-09, H0-H5 iteration 1)
--
-- Brief: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md s4 C5, s3.
-- Base: docs/DESIGN_WP_X5_witness_and_lineage.md (accepted 2026-09-08).
--
-- REFERENCE-ONLY IS UNCHANGED. SFE is authoritative for bytes and observations.
-- PEW stores references, typed presence indexes, summaries and evidence links.
-- Nothing here copies scientific bytes; a digest plus a size is the whole
-- record of content. The five new object kinds are ADDITIONS to X5's index,
-- not a second mechanism.

-- ------------------------------------------------------------ typed refs
-- One table, one shape, a kind discriminator. Six tables of identical shape
-- would be six places to fix the next time availability semantics change.
CREATE TABLE IF NOT EXISTS ew.typed_refs (
    ref_id            text PRIMARY KEY,        -- R-<sha256[:12]> of the identity
                                               -- tuple below: idempotent by
                                               -- construction
    ref_kind          text NOT NULL,           -- WITNESS | COMPONENT |
                                               -- GENERATED_TASK | DECODER |
                                               -- SOURCE_SET | RECEIPT
    ref_subkind       text,                    -- e.g. WITNESS: PROGRAM_INPUT |
                                               -- CA_INITIAL_STATE | OTHER
    -- what it belongs to (optional: a source set may precede any encounter)
    encounter_id      text,
    run_key           text NOT NULL DEFAULT '',
    -- OBSERVATION IDENTITY, preserved verbatim (brief s4 C5, deliverable 3)
    sfe_world_id      text,
    sfe_observation_id text,
    sfe_event_seq     bigint,
    sfe_entry_hash    text,
    sfe_engine_instance_id text,
    -- where the authoritative content lives; PEW never holds it
    source_kind       text NOT NULL,           -- OBSERVATION | ARTIFACT
    source_id         text NOT NULL,
    selector          text,                    -- path/field within the source;
                                               -- NULL = the whole source
    content_digest    text NOT NULL,           -- sha256:<64hex> of the exact
                                               -- authoritative bytes
    content_bytes     bigint,
    -- five states, REQUIRED. NULL cannot distinguish "there is none" from
    -- "I could not look", and that distinction is the point (X5-a).
    availability      text NOT NULL,           -- PRESENT | EMPTY | TRUNCATED |
                                               -- ABSENT | UNAVAILABLE
    availability_note text,
    -- retrieval is scoped: a reference is served only to a requester that
    -- names the scope it was published under (deliverable 3)
    source_scope      text,
    visibility        text,                    -- producer's declared visibility
    origin            text,                    -- NATIVE | IMPORTED | GENERATED
    producer          jsonb,
    namespace         text NOT NULL DEFAULT 'prod',
    created_at        timestamptz NOT NULL DEFAULT now(),
    submitted_by      text,
    machine           text,
    revision          bigint NOT NULL
);
COMMENT ON TABLE ew.typed_refs IS
 'Content-addressed references to authoritative SFE observations/artifacts. Holds digest + size + availability, never bytes. ref_id is the content address of (ref_kind, ref_subkind, encounter_id, run_key, source_kind, source_id, selector, content_digest), so an identical re-assertion is the same row.';

CREATE INDEX IF NOT EXISTS idx_typed_refs_enc    ON ew.typed_refs(encounter_id, run_key);
CREATE INDEX IF NOT EXISTS idx_typed_refs_kind   ON ew.typed_refs(ref_kind, availability);
CREATE INDEX IF NOT EXISTS idx_typed_refs_source ON ew.typed_refs(source_id);
CREATE INDEX IF NOT EXISTS idx_typed_refs_obs    ON ew.typed_refs(sfe_observation_id);
CREATE INDEX IF NOT EXISTS idx_typed_refs_scope  ON ew.typed_refs(source_scope);

-- Availability is deliberately OUTSIDE the content address so a reference keeps
-- one identity when its reachability changes. An availability change is
-- therefore an append-only EVENT, never a row rewrite. (D-15 is the operator's
-- ruling on making this the canonical form; the table exists now because the
-- alternative -- rewriting an immutable row -- is not available to us.)
CREATE TABLE IF NOT EXISTS ew.ref_availability_events (
    event_id     bigserial PRIMARY KEY,
    ref_id       text NOT NULL REFERENCES ew.typed_refs(ref_id),
    availability text NOT NULL,
    note         text,
    observed_at  timestamptz NOT NULL DEFAULT now(),
    observed_by  text
);
CREATE INDEX IF NOT EXISTS idx_ref_avail_ref ON ew.ref_availability_events(ref_id, event_id DESC);

-- ------------------------------------------------------- publication outbox
-- Idempotent, retryable publication that NEVER reruns completed science.
-- recorded_in_sfe and indexed_in_pew are SEPARATE facts and are reported
-- separately: the durable observation existing in SFE is the producer's
-- assertion; the index existing in PEW is ours. A failed publication leaves
-- the first true and the second false, and is retried -- it never erases the
-- observation and never causes a re-execution.
CREATE TABLE IF NOT EXISTS ew.publication_outbox (
    publication_id  text PRIMARY KEY,          -- P-<sha256[:12]> of intent
    intent_digest   text NOT NULL,             -- content address of the payload
    target_kind     text NOT NULL,             -- TYPED_REF | ENCOUNTER | EVIDENCE
    target_id       text,                      -- filled once indexed
    encounter_id    text,
    run_key         text NOT NULL DEFAULT '',
    recorded_in_sfe boolean,                   -- producer's assertion (tri-state:
                                               -- NULL = not asserted)
    indexed_in_pew  boolean NOT NULL DEFAULT false,
    state           text NOT NULL,             -- PENDING | PUBLISHED | FAILED
    terminal_state  text,                      -- the spec's terminal state, kept
                                               -- across publication recovery
    attempts        integer NOT NULL DEFAULT 0,
    last_error      text,
    first_seen      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    submitted_by    text,
    machine         text
);
COMMENT ON TABLE ew.publication_outbox IS
 'Retry ledger for PEW publication. A row is keyed by the content address of the publication intent, so a retry of the same intent is the same row: retries are free of duplicate science. terminal_state preserves a mandatory-PEW spec state while publication is recovered.';
CREATE INDEX IF NOT EXISTS idx_outbox_state ON ew.publication_outbox(state, updated_at);

-- --------------------------------------------------------- evidence axes
-- Brief s4 C5: software maturity, connection evidence, scientific outcome and
-- reproduction are DIFFERENT QUESTIONS and are stored as separate fields. A
-- 1.0 implementation may carry a negative result; a passing test suite cannot
-- promote a connection to demonstrated-transfer. Keeping them in one column
-- would make exactly that conflation expressible.
ALTER TABLE ew.evidence
    ADD COLUMN IF NOT EXISTS software_stage      text,
    ADD COLUMN IF NOT EXISTS connection_evidence text,
    ADD COLUMN IF NOT EXISTS scientific_outcome  text,
    ADD COLUMN IF NOT EXISTS reproduction_state  text;

COMMENT ON COLUMN ew.evidence.software_stage IS 'planned|alpha|beta|1.0|1.1 -- maturity of the implementation ONLY.';
COMMENT ON COLUMN ew.evidence.connection_evidence IS 'conceptual|runnable|demonstrated-transfer -- what was actually shown end to end. A test suite never promotes this.';
COMMENT ON COLUMN ew.evidence.scientific_outcome IS 'not-run|inconclusive|supported-in-scope|meaningful-effect-not-supported|harmful-in-scope.';
COMMENT ON COLUMN ew.evidence.reproduction_state IS 'source-resolved|built|smoke-passed|benchmark-attempted|reproduced-in-scope|failed|blocked.';

INSERT INTO ew.ontology_versions(version, description) VALUES
 (6, 'V6: typed reference/presence index (witness, component, generated task, decoder, source set, receipt), idempotent publication outbox, separate software/connection/outcome/reproduction axes')
ON CONFLICT DO NOTHING;
