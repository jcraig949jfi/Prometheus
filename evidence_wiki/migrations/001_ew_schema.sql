-- Evidence Wiki canonical substrate (schema ew in prometheus_fire)
-- Idempotent: CREATE ... IF NOT EXISTS throughout. Append-only discipline is
-- enforced by the service layer; the schema records, it does not adjudicate.
-- V0 2026-09-01, Mnemosyne.

CREATE SCHEMA IF NOT EXISTS ew;

CREATE SEQUENCE IF NOT EXISTS ew.canonical_revision_seq;

CREATE TABLE IF NOT EXISTS ew.ontology_versions (
    version      int PRIMARY KEY,
    description  text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);

-- Versioned vocabularies (claim_status / evidence_type / relation_type /
-- creation_method / epistemic_class / write_stage / outcome_canonical).
CREATE TABLE IF NOT EXISTS ew.vocab (
    domain            text NOT NULL,
    term              text NOT NULL,
    ontology_version  int  NOT NULL REFERENCES ew.ontology_versions(version),
    retired           boolean NOT NULL DEFAULT false,
    PRIMARY KEY (domain, term)
);

-- L0 references: fossils stay in git/disk; we hold URIs + hashes.
CREATE TABLE IF NOT EXISTS ew.source_packets (
    packet_id       text PRIMARY KEY,             -- SP-<sha256[:12]>
    uri             text NOT NULL,                -- repo-relative path or external URI
    content_sha256  text,                         -- file hash at registration (null if unhashable)
    git_commit      text,
    kind            text NOT NULL,                -- review_packet|ledger|journal|code|dataset|doc|derived_view
    registered_by   text NOT NULL,
    machine         text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    revision        bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS ew.agents (
    agent_id     text PRIMARY KEY,
    display_name text,
    kind         text                              -- seat|daemon|human|external
);

CREATE TABLE IF NOT EXISTS ew.experiments (
    experiment_id text PRIMARY KEY,               -- X-<sha256[:12]>
    agent_id      text,
    project       text,
    title         text NOT NULL,
    substrate     text,
    packet_id     text REFERENCES ew.source_packets(packet_id),
    git_commit    text,
    run_ref       text,
    submitted_by  text NOT NULL,
    machine       text NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now(),
    revision      bigint NOT NULL
);

-- Claims are versioned and append-only: a correction is a NEW version row
-- plus a CORRECTS/SUPERSEDES relation. Historical rows are never mutated.
CREATE TABLE IF NOT EXISTS ew.claims (
    claim_id         text NOT NULL,               -- C-<sha256[:12]>
    version          int  NOT NULL DEFAULT 1,
    text_canonical   text NOT NULL,
    source_wording   text,                        -- exact source phrasing, never discarded
    status           text NOT NULL,               -- vocab claim_status (as adjudicated by the SOURCE)
    claim_ceiling    text,                        -- scope limits stated by the source
    agent_id         text,
    experiment_id    text,
    packet_id        text REFERENCES ew.source_packets(packet_id),
    source_span      text,
    creation_method  text NOT NULL,               -- HUMAN|EXPERIMENT|MODEL_EXTRACTED|TENSOR_INFERRED
    write_stage      text NOT NULL DEFAULT 'SUBMITTED',
    ontology_version int  NOT NULL,
    submitted_by     text NOT NULL,
    machine          text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    revision         bigint NOT NULL,
    PRIMARY KEY (claim_id, version)
);

CREATE TABLE IF NOT EXISTS ew.evidence (
    evidence_id      text PRIMARY KEY,            -- E-<sha256[:12]>
    claim_id         text,                        -- primary claim it bears on
    evidence_type    text NOT NULL,               -- vocab evidence_type
    verdict_source   text,                        -- adjudication in SOURCE vocabulary
    outcome_canonical text,                       -- CONFIRMED|REFUTED|NULL_RESULT|MIXED|NA
    metric_text      text,                        -- verbatim numbers
    gate             text,
    negative         boolean NOT NULL DEFAULT false,
    substrate        text,
    packet_id        text NOT NULL REFERENCES ew.source_packets(packet_id),
    source_span      text,
    source_quote     text NOT NULL,               -- VERBATIM; provenance-deficient rows are rejected upstream
    experiment_id    text,
    agent_id         text,
    creation_method  text NOT NULL,
    write_stage      text NOT NULL DEFAULT 'SUBMITTED',
    ontology_version int  NOT NULL,
    submitted_by     text NOT NULL,
    machine          text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    revision         bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS ew.relations (
    relation_id      text PRIMARY KEY,            -- R-<sha256[:12]>
    src_type         text NOT NULL,               -- claim|evidence|experiment|hypothesis
    src_id           text NOT NULL,
    relation_type    text NOT NULL,               -- vocab relation_type
    dst_type         text NOT NULL,
    dst_id           text NOT NULL,
    epistemic_class  text NOT NULL,               -- OBSERVED|INFERRED|HYPOTHESIZED
    creation_method  text NOT NULL,               -- HUMAN|EXPERIMENT|MODEL_EXTRACTED|TENSOR_INFERRED
    confidence       real,
    rationale        text,
    packet_id        text REFERENCES ew.source_packets(packet_id),  -- required for OBSERVED
    source_span      text,
    derived_artifact_id text,                     -- required for TENSOR_INFERRED
    ontology_version int  NOT NULL,
    submitted_by     text NOT NULL,
    machine          text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    revision         bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ew_rel_src ON ew.relations(src_id);
CREATE INDEX IF NOT EXISTS idx_ew_rel_dst ON ew.relations(dst_id);
CREATE INDEX IF NOT EXISTS idx_ew_rel_type ON ew.relations(relation_type);

-- Canonical dimension dictionaries + source-term mappings (source wording preserved).
CREATE TABLE IF NOT EXISTS ew.dim_terms (
    dimension        text NOT NULL,   -- mechanism|failure_class|substrate_class|consumer|intervention|outcome|agent|evidence_type
    term_id          text NOT NULL,
    label            text NOT NULL,
    definition       text,
    ontology_version int  NOT NULL,
    PRIMARY KEY (dimension, term_id)
);
CREATE TABLE IF NOT EXISTS ew.term_mappings (
    dimension        text NOT NULL,
    source_term      text NOT NULL,
    term_id          text NOT NULL,
    mapped_by        text NOT NULL,
    creation_method  text NOT NULL,
    packet_id        text,
    ontology_version int  NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (dimension, source_term, ontology_version)
);

-- L3: sparse coordinates, deterministically generated per view version.
CREATE TABLE IF NOT EXISTS ew.coordinates (
    coord_id       bigserial PRIMARY KEY,
    view_name      text NOT NULL,
    view_version   int  NOT NULL,
    evidence_id    text NOT NULL REFERENCES ew.evidence(evidence_id),
    coords         jsonb NOT NULL,               -- {"mode": "term_id", ...} shape documented per view
    value          real NOT NULL DEFAULT 1,
    generator_version text NOT NULL,
    revision       bigint NOT NULL,
    UNIQUE (view_name, view_version, evidence_id)
);

CREATE TABLE IF NOT EXISTS ew.snapshots (
    snapshot_id        text PRIMARY KEY,          -- SN-<sha256[:12]>
    view_name          text NOT NULL,
    view_version       int  NOT NULL,
    filter_spec        jsonb NOT NULL,
    canonical_revision bigint NOT NULL,
    coord_count        int NOT NULL,
    content_sha256     text NOT NULL,             -- hash of sorted coordinate lines
    path               text NOT NULL,             -- coordinate file under evidence_wiki/derived/
    created_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ew.derived_artifacts (
    artifact_id        text PRIMARY KEY,          -- DA-<sha256[:12]>
    kind               text NOT NULL,             -- cp|tucker|tt|embedding_index|bm25_index|graph_index|wiki_render
    snapshot_id        text REFERENCES ew.snapshots(snapshot_id),
    source_schema_version int NOT NULL,
    ontology_version   int NOT NULL,
    compiler_version   text NOT NULL,
    params             jsonb NOT NULL,
    path               text,
    repro_sha256       text,
    canonical_revision bigint NOT NULL,
    created_at         timestamptz NOT NULL DEFAULT now()
);

-- Predicted/missing cells and candidate relations. status never leaves
-- HYPOTHESIZED by mutation; only new EVIDENCE rows can carry a tested outcome.
CREATE TABLE IF NOT EXISTS ew.hypotheses (
    hypothesis_id  text PRIMARY KEY,              -- H-<sha256[:12]>
    kind           text NOT NULL,                 -- MISSING_CELL|CANDIDATE_RELATION
    view_name      text,
    coords         jsonb,
    statement      text NOT NULL,
    score          real,
    method         text NOT NULL,                 -- cp|tucker|tt|graph_lp|embedding|marginal
    derived_artifact_id text,
    basis          jsonb,
    status         text NOT NULL DEFAULT 'HYPOTHESIZED',
    submitted_by   text NOT NULL,
    machine        text NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    revision       bigint NOT NULL
);

-- Write ledger: idempotency + attribution (gate G13/G15).
CREATE TABLE IF NOT EXISTS ew.write_log (
    write_id        bigserial PRIMARY KEY,
    idempotency_key text UNIQUE,
    endpoint        text NOT NULL,
    machine         text NOT NULL,
    agent           text NOT NULL,
    payload_sha256  text NOT NULL,
    accepted        boolean NOT NULL,
    reject_reason   text,
    result_object_id text,
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- Read telemetry (A15).
CREATE TABLE IF NOT EXISTS ew.read_log (
    read_id     bigserial PRIMARY KEY,
    endpoint    text NOT NULL,
    machine     text,
    agent       text,
    query       jsonb,
    result_count int,
    latency_ms  real,
    created_at  timestamptz NOT NULL DEFAULT now()
);
