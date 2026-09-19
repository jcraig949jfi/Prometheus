-- Atlas experiment index, migration 001 (2026-09-19).
-- Two tiers on the M1 canonical store (prometheus_fire):
--   tier 1 (the manifest): engine, machine, campaign, experiment
--   tier 2 (the detail):   run, artifact (pointers), param, outcome,
--                          lineage, commit links, flag
-- plus provenance (harvest_run) so every row names the extractor pass
-- that last wrote it, and a later pass can be diffed against an earlier one.
-- Atlas is the only writer. Nothing here copies bulk data: artifacts are
-- POINTERS (git path@commit, file@machine, pg table+filter) with a hash,
-- a size and the top-level field inventory.
-- Never edit this file after it has run; add 002_*.sql.

CREATE SCHEMA IF NOT EXISTS atlas;

CREATE TABLE IF NOT EXISTS atlas.schema_migrations (
    version      text PRIMARY KEY,
    applied_at   timestamptz NOT NULL DEFAULT now(),
    sha256       text NOT NULL,
    applied_by   text NOT NULL
);

-- provenance ---------------------------------------------------------------

CREATE TABLE IF NOT EXISTS atlas.harvest_run (
    harvest_id        bigserial PRIMARY KEY,
    harvester         text NOT NULL,           -- e.g. 'archaeon_campaigns'
    harvester_version text NOT NULL,           -- bumped whenever extraction changes
    atlas_sha         text,                    -- commit of the atlas/ code that ran
    machine_id        text,                    -- machine the harvester ran ON
    instance_tag      text,                    -- Atlas[<tag>]
    source_ref        text,                    -- git ref or path root read
    source_sha        text,                    -- resolved sha of source_ref
    started_at        timestamptz NOT NULL DEFAULT now(),
    finished_at       timestamptz,
    status            text NOT NULL DEFAULT 'RUNNING', -- RUNNING|DONE|FAILED
    counts            jsonb NOT NULL DEFAULT '{}'::jsonb,
    notes             text
);

-- tier 1 -------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS atlas.machine (
    machine_id   text PRIMARY KEY,             -- 'M1','M2','M3','M4'
    hostname     text,
    lan_ip       text,
    aliases      text[] NOT NULL DEFAULT '{}', -- instance-tag prefixes, drive roots
    roles        text,
    evidence     text,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE IF NOT EXISTS atlas.engine (
    engine_id    text PRIMARY KEY,             -- 'sfe','npe','vivarium',...
    name         text NOT NULL,
    kind         text NOT NULL,                -- ENGINE (executes) | RUNNER (drives an engine) | HARNESS
    code_paths   text[] NOT NULL DEFAULT '{}',
    owner_seats  text[] NOT NULL DEFAULT '{}',
    home_machine text REFERENCES atlas.machine(machine_id),
    status       text,
    notes        text,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE IF NOT EXISTS atlas.engine_instance (
    engine_instance_id text PRIMARY KEY,       -- e.g. eng_906356f7fb1da180131f9290
    engine_id    text NOT NULL REFERENCES atlas.engine(engine_id),
    machine_id   text REFERENCES atlas.machine(machine_id),
    base_url     text,
    source_hash  text,
    schema_version text,
    first_seen_at timestamptz,
    last_seen_at  timestamptz,
    evidence     text,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE IF NOT EXISTS atlas.seat_instance (
    instance_tag text PRIMARY KEY,             -- m2-411504ab, gandalf-6cd1348b
    seat         text,
    machine_id   text REFERENCES atlas.machine(machine_id),
    first_seen_at timestamptz,
    last_seen_at  timestamptz,
    n_commits    integer NOT NULL DEFAULT 0,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE IF NOT EXISTS atlas.campaign (
    campaign_key  text PRIMARY KEY,            -- '<program>' e.g. archaeon.cmp5, nestor.r8
    program       text NOT NULL,               -- family of the driver: archaeon.campaign, archaeon.frontier, nestor.round
    native_id     text NOT NULL,               -- as the driver writes it: cmp5, R8, CW01
    engine_id     text REFERENCES atlas.engine(engine_id),
    driver_seat   text,
    title         text,
    seed          text,
    status        text,
    started_at    timestamptz,
    ended_at      timestamptz,
    home_uri      text,                        -- pointer to the campaign's directory/report
    parent_campaign_key text,                  -- campaign it continues (declared or inferred)
    extract       jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);

CREATE TABLE IF NOT EXISTS atlas.experiment (
    experiment_key text PRIMARY KEY,           -- '<campaign_key>:<native_id>'
    campaign_key   text REFERENCES atlas.campaign(campaign_key),
    engine_id      text REFERENCES atlas.engine(engine_id),
    native_id      text NOT NULL,              -- C5-03, B-scatter.T000, E-R8-H1b-carrier-factorial
    slot           integer,
    title          text,
    question       text,
    purpose        text,                       -- engine | science | instrument | rehearsal | control ...
    driver_seat    text,
    status_native  text,                       -- verbatim disposition / verdict word(s)
    status_class   text,                       -- normalised: POSITIVE|WEAK_POSITIVE|NEGATIVE|NULL|INCONCLUSIVE|INVALID|FAILED|RUNNING|PLANNED|UNKNOWN
    claim_ceiling  text,
    prereg_digest  text,
    design_digest  text,
    seeds          text[] NOT NULL DEFAULT '{}',
    worlds         text[] NOT NULL DEFAULT '{}', -- world types / world ids
    organisms      text[] NOT NULL DEFAULT '{}', -- organism / representation labels
    machines       text[] NOT NULL DEFAULT '{}', -- derived from runs
    first_seen_at  timestamptz,                -- first commit or first run
    last_run_at    timestamptz,
    n_runs         integer NOT NULL DEFAULT 0,
    home_uri       text,                       -- pointer to the experiment's directory
    definition_uri text,                       -- prereg / spec
    result_uri     text,                       -- receipt / readout of record
    extract        jsonb NOT NULL DEFAULT '{}'::jsonb, -- small, named fields only
    inferred       jsonb NOT NULL DEFAULT '{}'::jsonb, -- field -> how it was inferred
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX IF NOT EXISTS experiment_campaign_idx ON atlas.experiment(campaign_key);
CREATE INDEX IF NOT EXISTS experiment_engine_idx   ON atlas.experiment(engine_id);
CREATE INDEX IF NOT EXISTS experiment_status_idx   ON atlas.experiment(status_class);

-- tier 2 -------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS atlas.run (
    run_key        text PRIMARY KEY,           -- '<experiment_key>#<native_run_id>'
    experiment_key text NOT NULL REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    native_run_id  text,                       -- a02, 30a2dd2de644d9fd50d8ca52, cell id
    attempt_no     integer,
    of_record      boolean,
    status         text,
    started_at     timestamptz,
    finished_at    timestamptz,
    duration_s     double precision,
    evaluations    bigint,
    machine_id     text REFERENCES atlas.machine(machine_id),
    machine_basis  text,                       -- how machine_id was decided (field, tag, path, ip)
    instance_tag   text,
    engine_instance_id text,
    engine_source_hash text,
    code_sha       text,                       -- workspace.base_sha or equivalent
    branch         text,
    worktree_path  text,
    dirty          boolean,
    resumed_from   text,
    extract        jsonb NOT NULL DEFAULT '{}'::jsonb,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX IF NOT EXISTS run_experiment_idx ON atlas.run(experiment_key);
CREATE INDEX IF NOT EXISTS run_machine_idx    ON atlas.run(machine_id);

CREATE TABLE IF NOT EXISTS atlas.artifact (
    artifact_uri   text PRIMARY KEY,           -- git:<path> | file://<machine>/<path> | pg://<db>/<table>?<filter> | http://...
    experiment_key text REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    run_key        text REFERENCES atlas.run(run_key) ON DELETE CASCADE,
    campaign_key   text REFERENCES atlas.campaign(campaign_key),
    role           text NOT NULL,              -- prereg|design|receipt|attempts|rows|record|readout|report|ledger|digest|log|db|blob_dir|pew|viv|spec|registry|other
    locator        text NOT NULL,              -- git|file|pg|http
    repo_path      text,
    git_ref        text,                       -- ref it was read from
    commit_sha     text,                       -- last commit touching repo_path on git_ref
    blob_sha       text,
    machine_id     text REFERENCES atlas.machine(machine_id), -- for file locators: the machine that holds it
    file_path      text,
    size_bytes     bigint,
    mtime          timestamptz,
    row_count      bigint,                     -- lines / rows / table rows matching the filter
    top_keys       text[],                     -- field inventory (top-level JSON keys) for recombing
    shape_hash     text,                       -- sha256 of the sorted key inventory
    present        boolean NOT NULL DEFAULT true,
    note           text,
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX IF NOT EXISTS artifact_experiment_idx ON atlas.artifact(experiment_key);
CREATE INDEX IF NOT EXISTS artifact_role_idx       ON atlas.artifact(role);
CREATE INDEX IF NOT EXISTS artifact_shape_idx      ON atlas.artifact(shape_hash);

CREATE TABLE IF NOT EXISTS atlas.param (
    experiment_key text NOT NULL REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    run_key        text NOT NULL DEFAULT '',   -- '' = experiment-level
    name           text NOT NULL,              -- dotted path in the source document
    value_text     text,
    value_num      double precision,
    value_json     jsonb,
    source_uri     text,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (experiment_key, run_key, name)
);

CREATE TABLE IF NOT EXISTS atlas.outcome (
    experiment_key text NOT NULL REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    run_key        text NOT NULL DEFAULT '',
    name           text NOT NULL,
    value_text     text,
    value_num      double precision,
    value_json     jsonb,
    source_uri     text,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (experiment_key, run_key, name)
);

CREATE TABLE IF NOT EXISTS atlas.lineage (
    child_key    text NOT NULL,                -- experiment_key (or campaign_key when level='campaign')
    parent_key   text NOT NULL,                -- may be unresolved: dangling parents are kept, see v_lineage_dangling
    relation     text NOT NULL,                -- parent|rerun|attempt|amendment|supersedes|replica|descendant|continues|seeded_by
    level        text NOT NULL DEFAULT 'experiment',
    basis        text NOT NULL,                -- DECLARED (field says so) | INFERRED (name/time/pattern)
    evidence     text,
    source_uri   text,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (child_key, parent_key, relation)
);

CREATE TABLE IF NOT EXISTS atlas.git_commit (
    sha          text PRIMARY KEY,
    authored_at  timestamptz,
    subject      text,
    seat         text,
    lane         text,
    instance_tag text,
    session      text,                         -- Claude-Session trailer
    ids          text[] NOT NULL DEFAULT '{}', -- experiment/backlog/decision ids found in the subject+body
    classes      text[] NOT NULL DEFAULT '{}', -- PREREG|RESULT|CORRECTION|AMENDMENT|SUPERSEDED|REPLICA|RETRACT|MERGE
    on_main      boolean,
    refs_seen    text[] NOT NULL DEFAULT '{}', -- refs (remote or machine-local) containing it
    seen_on_machine text REFERENCES atlas.machine(machine_id),
    n_paths      integer,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id)
);
CREATE INDEX IF NOT EXISTS git_commit_seat_idx ON atlas.git_commit(seat);

CREATE TABLE IF NOT EXISTS atlas.experiment_commit (
    experiment_key text NOT NULL REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    sha            text NOT NULL,
    link_basis     text NOT NULL,              -- PATH (touched the experiment dir) | ID (subject names it)
    n_paths        integer,
    last_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    PRIMARY KEY (experiment_key, sha, link_basis)
);

CREATE TABLE IF NOT EXISTS atlas.flag (
    flag_id        bigserial PRIMARY KEY,
    experiment_key text NOT NULL REFERENCES atlas.experiment(experiment_key) ON DELETE CASCADE,
    kind           text NOT NULL,              -- MISSED_SCIENCE|WEAK_SIGNAL|RERUN_OPPORTUNITY|DATA_GAP
    rule_id        text NOT NULL,
    rule_version   text NOT NULL,
    detail         text,
    evidence_uri   text,
    status         text NOT NULL DEFAULT 'OPEN', -- OPEN|TRIAGED|FOLLOWED|DISMISSED (humans/seats set these)
    first_harvest_id bigint REFERENCES atlas.harvest_run(harvest_id),
    last_harvest_id  bigint REFERENCES atlas.harvest_run(harvest_id),
    UNIQUE (experiment_key, kind, rule_id)
);

-- views --------------------------------------------------------------------

CREATE OR REPLACE VIEW atlas.v_manifest AS
SELECT e.experiment_key, e.campaign_key, e.engine_id, e.native_id, e.title,
       e.driver_seat, e.status_native, e.status_class, e.machines,
       e.first_seen_at, e.last_run_at, e.n_runs,
       (SELECT count(*) FROM atlas.artifact a WHERE a.experiment_key = e.experiment_key) AS n_artifacts,
       (SELECT count(*) FROM atlas.lineage l WHERE l.child_key = e.experiment_key)       AS n_parents,
       (SELECT count(*) FROM atlas.lineage l WHERE l.parent_key = e.experiment_key)      AS n_children,
       (SELECT count(*) FROM atlas.flag f WHERE f.experiment_key = e.experiment_key AND f.status = 'OPEN') AS n_open_flags,
       e.home_uri, e.result_uri
FROM atlas.experiment e;

CREATE OR REPLACE VIEW atlas.v_lineage_dangling AS
SELECT l.* FROM atlas.lineage l
WHERE l.level = 'experiment'
  AND NOT EXISTS (SELECT 1 FROM atlas.experiment e WHERE e.experiment_key = l.parent_key);

CREATE OR REPLACE VIEW atlas.v_machine_coverage AS
SELECT h.machine_id, h.harvester, max(h.finished_at) AS last_success_at,
       max(h.harvest_id) AS last_harvest_id
FROM atlas.harvest_run h WHERE h.status = 'DONE'
GROUP BY h.machine_id, h.harvester;

CREATE OR REPLACE VIEW atlas.v_shape_inventory AS
SELECT role, shape_hash, top_keys, count(*) AS n_artifacts
FROM atlas.artifact WHERE shape_hash IS NOT NULL
GROUP BY role, shape_hash, top_keys;
