-- Atlas migration 002 (2026-09-19): the model required by the charter
-- addendum (roles/Atlas/prompts/2026-09-19_charter_addendum/).
--
-- 001 lived about an hour and held only reference and commit rows (no
-- consumer existed). 002 keeps harvest_run, git_commit and seat_instance,
-- renames machine -> host, and replaces the experiment tables with:
--
--   identity   engine -> campaign -> experiment -> attempt -> segment
--   machines   host, engine_instance (explicit, mergeable across hosts)
--   ran        attempt, segment (execution facts live on these rows)
--   observed   fact(layer='OBSERVED')           + fact_evidence -> source
--   concluded  conclusion (verbatim / pointer; never overwritten)
--   atlas      atlas_class* fields and fact/edge/signal rows authored
--              'ATLAS_DERIVED' with method + version
--   relations  edge: one typed edge table for execution, scientific,
--              organism and provenance lineage (no parent_id columns)
--   sources    source (first-class pointer) + source_link (many-to-many)
--   defects    defect (+ edges AFFECTED_BY)
--   ideas      idea: scientific-lineage nodes (trajectories, lineages,
--              observations) that experiments test or originate from
--   integrity  identity_collision, field_conflict
--   surfacing  signal (the weak-signal / recomb layer; never a directive)
--
-- Keys are text and machine-independent, derived from native identifiers
-- (never filenames): an Atlas instance on another host computes the same
-- key for the same experiment and ENRICHES the row.

DROP VIEW IF EXISTS atlas.v_manifest, atlas.v_lineage_dangling, atlas.v_machine_coverage, atlas.v_shape_inventory;
DROP TABLE IF EXISTS atlas.experiment_commit, atlas.flag, atlas.lineage, atlas.outcome, atlas.param,
                     atlas.artifact, atlas.run, atlas.experiment, atlas.campaign, atlas.engine_instance CASCADE;

ALTER TABLE atlas.machine RENAME TO host;
ALTER TABLE atlas.host RENAME COLUMN machine_id TO host_id;
ALTER TABLE atlas.host ADD COLUMN IF NOT EXISTS os_env jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE atlas.host ADD COLUMN IF NOT EXISTS storage_roots text[] NOT NULL DEFAULT '{}';
ALTER TABLE atlas.engine RENAME COLUMN home_machine TO home_host;
ALTER TABLE atlas.seat_instance RENAME COLUMN machine_id TO host_id;
ALTER TABLE atlas.git_commit RENAME COLUMN seen_on_machine TO seen_on_host;
ALTER TABLE atlas.harvest_run RENAME COLUMN machine_id TO host_id;

-- controlled vocabularies live in one table so a new engine adds words, not columns
CREATE TABLE atlas.vocab (
    domain  text NOT NULL,   -- validity|edge_relation|edge_reason|lineage_kind|basis|fact_kind|fact_layer|fact_status|signal_kind|confidence|visibility
    term    text NOT NULL,
    meaning text,
    PRIMARY KEY (domain, term)
);

CREATE TABLE atlas.engine_instance (
    engine_instance_key text PRIMARY KEY,     -- native id (eng_906356f7...) or '<engine>@<host>:<code sha12>' when the engine mints none
    engine_id      text NOT NULL REFERENCES atlas.engine(engine_id),
    host_id        text REFERENCES atlas.host(host_id),
    native_id      text,
    version        text,
    schema_version text,
    source_hash    text,
    commit_sha     text,
    endpoint       text,                       -- base_url / port where historically recoverable
    process_desc   text,                       -- service/process description
    storage_root   text,
    first_seen_at  timestamptz,
    last_seen_at   timestamptz,
    basis          text,                       -- where the host/version came from
    seen_from_hosts text[] NOT NULL DEFAULT '{}',
    extract        jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE atlas.campaign (
    campaign_key   text PRIMARY KEY,           -- '<program>/<native>': archaeon.campaign/cmp5, nestor.cw01/cw01-2026-09-17
    program        text NOT NULL,              -- the driver family
    native_id      text NOT NULL,
    engine_id      text REFERENCES atlas.engine(engine_id),   -- primary engine; experiments may differ
    driver_seat    text,
    title          text,
    seed           text,
    reported_status text,
    started_at     timestamptz,
    ended_at       timestamptz,
    summary        text,
    seen_from_hosts text[] NOT NULL DEFAULT '{}',
    extract        jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE atlas.experiment (
    experiment_key  text PRIMARY KEY,          -- '<campaign_key>:<native_id>'
    campaign_key    text NOT NULL REFERENCES atlas.campaign(campaign_key),
    engine_id       text REFERENCES atlas.engine(engine_id),
    native_id       text NOT NULL,
    slot            integer,
    kind            text,                      -- experiment | perturbation | transformation | rehearsal | calibration | receipt_family
    title           text,
    question        text,                      -- verbatim where the source states one
    purpose         text,
    driver_seat     text,
    -- scientific coordinates (free text families; the vocabulary grows with engines)
    world_family    text,
    organism_family text,
    pressure_family text,
    search_family   text,
    ruler           text,
    seeds           text[] NOT NULL DEFAULT '{}',
    budget_summary  text,
    -- what someone concluded (verbatim) vs what Atlas classifies
    reported_disposition text,
    reported_conclusion  text,
    atlas_class          text,                 -- POSITIVE|WEAK_POSITIVE|NEGATIVE|NULL|INCONCLUSIVE|FAILED|RUNNING|PLANNED|UNKNOWN
    atlas_class_confidence text,               -- HIGH|MEDIUM|LOW
    atlas_class_method   text,                 -- rule id + version
    validity_state       text NOT NULL DEFAULT 'UNKNOWN',
    unresolved_interpretation text,
    result_summary  text,
    prereg_digest   text,
    design_digest   text,
    config_digest   text,
    first_seen_at   timestamptz,
    last_activity_at timestamptz,
    n_attempts      integer NOT NULL DEFAULT 0,
    hosts           text[] NOT NULL DEFAULT '{}',     -- derived from attempts
    seen_from_hosts text[] NOT NULL DEFAULT '{}',     -- which Atlas hosts saw evidence of it
    extract         jsonb NOT NULL DEFAULT '{}'::jsonb,
    inferred        jsonb NOT NULL DEFAULT '{}'::jsonb, -- field -> how it was inferred
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX ON atlas.experiment(campaign_key);
CREATE INDEX ON atlas.experiment(engine_id);
CREATE INDEX ON atlas.experiment(atlas_class);

CREATE TABLE atlas.attempt (
    attempt_key     text PRIMARY KEY,          -- '<experiment_key>#<native attempt id>'
    experiment_key  text NOT NULL REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    native_id       text,
    attempt_no      integer,
    of_record       boolean,
    reported_status text,
    validity_state  text NOT NULL DEFAULT 'UNKNOWN',
    rerun_reason    text,                      -- edge_reason vocabulary; the edge carries the detail
    started_at      timestamptz,
    finished_at     timestamptz,
    duration_s      double precision,
    host_id         text REFERENCES atlas.host(host_id),
    host_basis      text,
    instance_tag    text,
    operator_seat   text,
    engine_instance_key text REFERENCES atlas.engine_instance(engine_instance_key),
    branch          text,
    commit_sha      text,
    code_digest     text,
    config_digest   text,
    dirty           boolean,
    worktree_path   text,
    budget          jsonb NOT NULL DEFAULT '{}'::jsonb,
    result_summary  text,
    seen_from_hosts text[] NOT NULL DEFAULT '{}',
    extract         jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX ON atlas.attempt(experiment_key);
CREATE INDEX ON atlas.attempt(host_id);

CREATE TABLE atlas.segment (
    segment_key     text PRIMARY KEY,          -- '<attempt_key>@<native segment id>'
    attempt_key     text NOT NULL REFERENCES atlas.attempt(attempt_key) ON DELETE CASCADE,
    native_id       text,
    kind            text,                      -- chunk | step | epoch | phase | cell | job
    ordinal         integer,
    reported_status text,
    started_at      timestamptz,
    finished_at     timestamptz,
    host_id         text REFERENCES atlas.host(host_id),
    evaluations     bigint,
    digest          text,
    extract         jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX ON atlas.segment(attempt_key);

CREATE TABLE atlas.idea (
    idea_key        text PRIMARY KEY,          -- '<program>/<native>': nestor.cw01/T-X12, archaeon.frontier/LIN-cb15a0ad
    native_id       text NOT NULL,
    kind            text,                      -- trajectory | lineage | anomaly | observation | hypothesis | mechanism
    engine_id       text REFERENCES atlas.engine(engine_id),
    campaign_key    text REFERENCES atlas.campaign(campaign_key),
    title           text,
    question        text,                      -- verbatim
    world_family    text,
    organism_family text,
    pressure_family text,
    search_family   text,
    ruler           text,
    reported_status text,                      -- e.g. ACTIVE / stasis / OPEN
    origin_text     text,                      -- verbatim origin statement
    extract         jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE atlas.defect (
    defect_key      text PRIMARY KEY,          -- '<program>/<native>': nestor.cw01/CW01-D086, archaeon.campaign/cmp5/L5-001
    native_id       text NOT NULL,
    engine_id       text REFERENCES atlas.engine(engine_id),
    campaign_key    text REFERENCES atlas.campaign(campaign_key),
    category        text,
    severity        text,
    phase           text,
    title           text,                      -- verbatim, truncated at 1000
    reported_status text,
    reported_at     timestamptz,
    extract         jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE atlas.source (
    source_id       bigserial PRIMARY KEY,
    uri             text NOT NULL UNIQUE,      -- git:<ref>:<path>[#<record>] | file://<host>/<path> | pg://<db>/<schema.table>?<filter> | pew:<id> | ledger://<engine_instance>/<table>/<id>
    kind            text NOT NULL,             -- git_blob | file | log | engine_ledger | pg_rows | pew | url
    repo            text,
    ref             text,
    commit_sha      text,                      -- newest commit touching path on ref
    first_commit_sha text,                     -- oldest commit touching path on ref
    path            text,
    blob_sha        text,
    file_sha256     text,
    size_bytes      bigint,
    mtime           timestamptz,
    record_key      text,                      -- key inside the file (json path, id, line)
    line_start      integer,
    line_end        integer,
    byte_start      bigint,
    byte_end        bigint,
    time_start      timestamptz,
    time_end        timestamptz,
    engine_ledger_id text,
    pew_id          text,
    pg_ref          text,
    host_id         text REFERENCES atlas.host(host_id),  -- where the bytes physically are (NULL for git objects)
    local_path      text,
    visibility      text NOT NULL,             -- GIT_REMOTE | GIT_LOCAL:<host> | FS:<host> | PG:<host> | EXPECTED:<host> (referenced, not seen)
    row_count       bigint,
    top_keys        text[],
    shape_hash      text,
    present         boolean,                   -- true seen; false re-looked on the SAME host and gone; NULL not looked
    seen_from_hosts text[] NOT NULL DEFAULT '{}',
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX ON atlas.source(path);
CREATE INDEX ON atlas.source(shape_hash);

CREATE TABLE atlas.source_link (
    source_id    bigint NOT NULL REFERENCES atlas.source(source_id) ON DELETE CASCADE,
    entity_type  text NOT NULL,                -- engine|engine_instance|host|campaign|experiment|attempt|segment|idea|defect|conclusion
    entity_key   text NOT NULL,
    role         text NOT NULL,                -- definition|prereg|design|world|contract|result|receipt|rows|record|readout|report|log|ledger|digest|decision|state|registry|telemetry|package|other
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (source_id, entity_type, entity_key, role)
);
CREATE INDEX ON atlas.source_link(entity_type, entity_key);

CREATE TABLE atlas.fact (
    fact_id      bigserial PRIMARY KEY,
    fact_key     text NOT NULL UNIQUE,         -- deterministic: subject|kind|name|origin -> idempotent re-harvest
    layer        text NOT NULL,                -- RAN | OBSERVED | CONCLUDED
    kind         text NOT NULL,                -- fact_kind vocabulary
    subject_type text NOT NULL,
    subject_key  text NOT NULL,
    name         text NOT NULL,                -- dotted path or named measurement
    value_text   text,
    value_num    double precision,
    value_json   jsonb,
    band_low     double precision,
    band_high    double precision,
    unit         text,
    status       text NOT NULL DEFAULT 'REPORTED',  -- REPORTED|UNKNOWN|CONTRADICTORY|PARTIAL_EVIDENCE|UNRESOLVED|SUPERSEDED_INTERPRETATION
    author       text NOT NULL,                -- the seat that reported it, or ATLAS_DERIVED
    method       text NOT NULL,                -- harvester/version or query id/version
    stated_at    timestamptz,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX ON atlas.fact(subject_type, subject_key);
CREATE INDEX ON atlas.fact(kind, name);

CREATE TABLE atlas.fact_evidence (
    fact_id    bigint NOT NULL REFERENCES atlas.fact(fact_id) ON DELETE CASCADE,
    source_id  bigint NOT NULL REFERENCES atlas.source(source_id) ON DELETE CASCADE,
    locator    text NOT NULL DEFAULT '',        -- json path / line / record id inside the source
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (fact_id, source_id, locator)
);

CREATE TABLE atlas.conclusion (
    conclusion_id   bigserial PRIMARY KEY,
    conclusion_key  text NOT NULL UNIQUE,      -- subject|author|source|locator
    subject_type    text NOT NULL,
    subject_key     text NOT NULL,
    author          text NOT NULL,             -- seat (as written) or ATLAS_DERIVED
    disposition     text,                      -- verbatim word(s)
    text_verbatim   text,                      -- verbatim, truncated at 4000 (pointer holds the rest)
    stated_at       timestamptz,
    status          text NOT NULL DEFAULT 'STANDING', -- STANDING|SUPERSEDED_INTERPRETATION|RETRACTED|CONTRADICTORY|UNRESOLVED
    superseded_by   bigint REFERENCES atlas.conclusion(conclusion_id),
    source_id       bigint REFERENCES atlas.source(source_id),
    locator         text,
    method          text NOT NULL,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX ON atlas.conclusion(subject_type, subject_key);

CREATE TABLE atlas.edge (
    edge_id      bigserial PRIMARY KEY,
    src_type     text NOT NULL,                -- convention: src is the LATER / derived / affected thing
    src_key      text NOT NULL,
    dst_type     text NOT NULL,                -- dst is the EARLIER / parent / cause
    dst_key      text NOT NULL,
    relation     text NOT NULL,                -- edge_relation vocabulary
    lineage_kind text NOT NULL,                -- EXECUTION | SCIENTIFIC | ORGANISM | PROVENANCE
    reason       text NOT NULL DEFAULT 'UNKNOWN', -- edge_reason vocabulary
    basis        text NOT NULL,                -- DECLARED | INFERRED | ATLAS_DERIVED
    confidence   text NOT NULL DEFAULT 'MEDIUM',
    method       text NOT NULL,
    detail       text,                         -- verbatim delta / note where the source gives one
    source_id    bigint REFERENCES atlas.source(source_id),
    locator      text,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id),
    UNIQUE (src_type, src_key, dst_type, dst_key, relation)
);
CREATE INDEX ON atlas.edge(dst_type, dst_key);
CREATE INDEX ON atlas.edge(src_type, src_key);

CREATE TABLE atlas.entity_commit (
    entity_type  text NOT NULL,
    entity_key   text NOT NULL,
    sha          text NOT NULL,
    basis        text NOT NULL,                -- PATH | ID
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (entity_type, entity_key, sha, basis)
);

CREATE TABLE atlas.identity_collision (
    collision_key text PRIMARY KEY,            -- namespace|native_id|entity_type
    namespace    text NOT NULL,
    native_id    text NOT NULL,
    entity_type  text NOT NULL,
    candidates   jsonb NOT NULL,
    note         text,
    status       text NOT NULL DEFAULT 'OPEN',
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE atlas.field_conflict (
    entity_type  text NOT NULL,
    entity_key   text NOT NULL,
    field        text NOT NULL,
    value_kept   text,
    value_offered text,
    offered_by_harvest bigint REFERENCES atlas.harvest_run(harvest_id),
    noted_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (entity_type, entity_key, field, value_offered)
);

CREATE TABLE atlas.signal (
    signal_id    bigserial PRIMARY KEY,
    signal_key   text NOT NULL UNIQUE,         -- kind|rule|subject
    kind         text NOT NULL,                -- signal_kind vocabulary
    rule_id      text NOT NULL,
    rule_version text NOT NULL,
    subject_type text NOT NULL,
    subject_key  text NOT NULL,
    summary      text NOT NULL,
    evidence     jsonb NOT NULL DEFAULT '[]'::jsonb, -- [{type,key}|{source_id}] the rule used
    query        text,                         -- the SQL or method that produced it (ATLAS_DERIVED)
    status       text NOT NULL DEFAULT 'OPEN', -- OPEN|TRIAGED|FOLLOWED|DISMISSED (set by humans/seats)
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
