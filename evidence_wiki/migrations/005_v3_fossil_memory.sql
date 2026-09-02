-- PEW V3: explicit memory influence chain, Incubator fossil record,
-- versioned interpretations over immutable events, legacy ambient memory
-- provenance class. All fossil objects REFERENCE authoritative SFE history
-- by (world_id, event_id, entry_hash) - never copy it (charter s10).

INSERT INTO ew.ontology_versions(version, description) VALUES
 (3, 'V3: fossil record + interpretations + explicit memory influences + LEGACY_AMBIENT_MEMORY')
ON CONFLICT DO NOTHING;

INSERT INTO ew.vocab(domain, term, ontology_version) VALUES
 ('packet_kind', 'legacy_ambient_memory', 3),
 ('packet_kind', 'sfe_ledger', 3)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------- s6 chain
-- QUERY -> RETRIEVAL -> HASH -> ARTIFACT -> CONSUMER -> DECISION -> EXECUTION -> RESULT
CREATE TABLE IF NOT EXISTS ew.memory_artifacts (
    artifact_hash  text PRIMARY KEY,          -- sha256 of canonical pack content
    kind           text NOT NULL,             -- evidence_pack | doctrine_pack
    query_spec     jsonb NOT NULL,            -- queries + mechanisms + filters used
    canonical_revision bigint NOT NULL,       -- wiki revision at build time
    item_ids       text[] NOT NULL,           -- claim/evidence ids inside
    path           text,                      -- frozen file under v3/memory/
    created_by     text NOT NULL,
    machine        text NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ew.memory_influences (
    influence_id     text PRIMARY KEY,        -- MI-<sha[:12]>
    artifact_hash    text NOT NULL REFERENCES ew.memory_artifacts(artifact_hash),
    consumer_agent   text NOT NULL,
    machine          text NOT NULL,
    experiment_ref   text,                    -- prereg/task id
    decision_artifact text,                   -- path/hash of what the consumer produced
    execution_ref    text,                    -- how it was executed
    result_ref       text,                    -- externally measured outcome record
    created_at       timestamptz NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------- s9 fossils
CREATE TABLE IF NOT EXISTS ew.fossil_players (
    player_id     text PRIMARY KEY,
    genome_hash   text,
    arch_hash     text,
    parent_player text,
    sfe_world_id  text,
    sfe_entry_hash text,                      -- authoritative anchor
    mutation_ref  text,
    resources     jsonb,
    phenotype     jsonb,
    namespace     text NOT NULL DEFAULT 'prod',   -- prod | synthetic | test
    created_at    timestamptz NOT NULL DEFAULT now(),
    revision      bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS ew.fossil_worlds (
    world_id       text PRIMARY KEY,
    manifest_hash  text,
    parent_world   text,
    sfe_world_id   text,
    sfe_head_hash  text,
    interface_ver  text,
    mechanics_ver  text,
    family         text,                      -- coarse world-family key for tensor modes
    namespace      text NOT NULL DEFAULT 'prod',
    created_at     timestamptz NOT NULL DEFAULT now(),
    revision       bigint NOT NULL
);

CREATE TABLE IF NOT EXISTS ew.fossil_encounters (
    encounter_id   text PRIMARY KEY,
    sfe_world_id   text,
    sfe_event_id   text,
    sfe_entry_hash text NOT NULL,             -- WHICH SFE EVIDENCE SUPPORTS THIS (s10)
    world_id       text,
    players        text[],
    ecology        jsonb,
    seed           text,
    budget         jsonb,
    outcome        text,                      -- native outcome token, NOT prose
    failure_class  text,
    resources_used jsonb,
    occurred_ts    timestamptz,
    namespace      text NOT NULL DEFAULT 'prod',
    created_at     timestamptz NOT NULL DEFAULT now(),
    revision       bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fossil_enc_world ON ew.fossil_encounters(world_id);
CREATE INDEX IF NOT EXISTS idx_fossil_enc_ns ON ew.fossil_encounters(namespace);

CREATE TABLE IF NOT EXISTS ew.fossil_edges (
    edge_id     text PRIMARY KEY,
    src_kind    text NOT NULL,               -- player|world|lineage|encounter
    src_id      text NOT NULL,
    dst_kind    text NOT NULL,
    dst_id      text NOT NULL,
    relation    text NOT NULL,               -- ANCESTOR|FORK|MUTATION|CROSS|TRANSFER|TRANSPLANT|EXTINCTION|SURVIVAL
    sfe_entry_hash text,
    namespace   text NOT NULL DEFAULT 'prod',
    created_at  timestamptz NOT NULL DEFAULT now(),
    revision    bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fossil_edges_src ON ew.fossil_edges(src_id);
CREATE INDEX IF NOT EXISTS idx_fossil_edges_dst ON ew.fossil_edges(dst_id);

-- ------------------------------------------- s1/s14 versioned interpretation
-- Interpretations NEVER mutate their subject. New readings are new rows;
-- supersession is a pointer, and superseded rows remain recoverable.
CREATE TABLE IF NOT EXISTS ew.interpretations (
    interpretation_id text PRIMARY KEY,       -- I-<sha[:12]>
    subject_kind    text NOT NULL,            -- sfe_event|encounter|player|world|claim|evidence|native_structure
    subject_id      text NOT NULL,            -- immutable subject reference
    subject_sfe_hash text,                    -- authoritative anchor when applicable
    kind            text NOT NULL,            -- BEHAVIORAL_CLASS|FAILURE_CLASS|ASSOCIATION|ABSTRACTION|HUMAN_INTERPRETATION|CONTAMINATION_FLAG
    statement       text,                     -- HUMAN surface (nullable for native)
    native_payload  jsonb,                    -- machine-native surface (no prose required)
    confidence      real,
    creation_method text NOT NULL,            -- HUMAN|EXPERIMENT|MODEL_EXTRACTED|TENSOR_INFERRED
    supersedes      text,                     -- prior interpretation_id (chain, never overwrite)
    packet_id       text,
    derived_artifact_id text,
    created_by      text NOT NULL,
    machine         text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    revision        bigint NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interp_subject ON ew.interpretations(subject_kind, subject_id);

-- -------------------------------------------------------- s9 candidate bumps
CREATE TABLE IF NOT EXISTS ew.candidate_bumps (
    bump_id          text PRIMARY KEY,
    detection_sfe_hash text NOT NULL,
    snapshot_id      text,                    -- frozen evidence snapshot at detection
    lineage_ref      text,
    context          jsonb,                   -- world/ecology context refs
    neighbor_refs    text[],                  -- nearby failure encounter ids
    falsification_plan text,
    replication_refs text[],
    disposition      text NOT NULL DEFAULT 'OPEN',  -- OPEN|REPLICATED|REFUTED|NOISE|PROMOTED
    namespace        text NOT NULL DEFAULT 'prod',
    created_by       text NOT NULL,
    machine          text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    revision         bigint NOT NULL
);
