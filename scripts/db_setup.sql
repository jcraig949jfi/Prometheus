-- ============================================================
-- Prometheus Database Setup
-- Run on M1 as Postgres superuser (sudo -u postgres psql)
-- ============================================================

-- ============================================================
-- 1. ROLES
-- ============================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'prometheus_read') THEN
        CREATE ROLE prometheus_read;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'prometheus_write') THEN
        CREATE ROLE prometheus_write;
    END IF;
END $$;

-- prometheus_write inherits prometheus_read
GRANT prometheus_read TO prometheus_write;

-- ============================================================
-- 2. USERS (set passwords after creation)
-- ============================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'harmonia') THEN
        CREATE USER harmonia IN ROLE prometheus_read;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ergon') THEN
        CREATE USER ergon IN ROLE prometheus_write;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'charon') THEN
        CREATE USER charon IN ROLE prometheus_write;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ingestor') THEN
        CREATE USER ingestor IN ROLE prometheus_write;
    END IF;
END $$;

-- Set passwords (CHANGE THESE)
ALTER USER harmonia  WITH PASSWORD 'prometheus';
ALTER USER ergon     WITH PASSWORD 'prometheus';
ALTER USER charon    WITH PASSWORD 'prometheus';
ALTER USER ingestor  WITH PASSWORD 'prometheus';

-- ============================================================
-- 3. PROMETHEUS_SCI DATABASE
-- ============================================================

CREATE DATABASE prometheus_sci OWNER postgres;

\connect prometheus_sci

-- Schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS topology;
CREATE SCHEMA IF NOT EXISTS physics;
CREATE SCHEMA IF NOT EXISTS chemistry;
CREATE SCHEMA IF NOT EXISTS algebra;
CREATE SCHEMA IF NOT EXISTS analysis;
CREATE SCHEMA IF NOT EXISTS biology;
CREATE SCHEMA IF NOT EXISTS meta;

-- Core: provenance tracking
CREATE TABLE core.data_source (
    source_id    SERIAL PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    origin_url   TEXT,
    file_path    TEXT,
    loaded_at    TIMESTAMPTZ DEFAULT now(),
    row_count    INTEGER,
    checksum     TEXT
);

-- Topology
CREATE TABLE topology.knots (
    knot_id          SERIAL PRIMARY KEY,
    name             TEXT UNIQUE NOT NULL,
    crossing_number  SMALLINT,
    determinant      INTEGER,
    alexander_coeffs DOUBLE PRECISION[],
    jones_coeffs     DOUBLE PRECISION[],
    conway_coeffs    DOUBLE PRECISION[],
    signature        SMALLINT,
    source_id        INTEGER REFERENCES core.data_source
);

CREATE TABLE topology.polytopes (
    polytope_id   SERIAL PRIMARY KEY,
    name          TEXT,
    dimension     SMALLINT,
    n_vertices    INTEGER,
    n_edges       INTEGER,
    n_facets      INTEGER,
    f_vector      INTEGER[],
    is_simplicial BOOLEAN,
    source_id     INTEGER REFERENCES core.data_source
);

-- Physics
CREATE TABLE physics.superconductors (
    sc_id            SERIAL PRIMARY KEY,
    material_formula TEXT,
    tc               DOUBLE PRECISION,
    spacegroup       TEXT,
    sc_class         TEXT,
    source_id        INTEGER REFERENCES core.data_source
);

CREATE TABLE physics.materials (
    mat_id                    SERIAL PRIMARY KEY,
    material_id               TEXT UNIQUE,
    band_gap                  DOUBLE PRECISION,
    formation_energy_per_atom DOUBLE PRECISION,
    spacegroup_number         SMALLINT,
    density                   DOUBLE PRECISION,
    volume                    DOUBLE PRECISION,
    nsites                    INTEGER,
    source_id                 INTEGER REFERENCES core.data_source
);

CREATE TABLE physics.codata (
    constant_id  SERIAL PRIMARY KEY,
    name         TEXT UNIQUE NOT NULL,
    value        DOUBLE PRECISION,
    uncertainty  DOUBLE PRECISION,
    unit         TEXT,
    source_id    INTEGER REFERENCES core.data_source
);

CREATE TABLE physics.pdg_particles (
    particle_id  SERIAL PRIMARY KEY,
    name         TEXT,
    pdg_id       INTEGER,
    mass_gev     DOUBLE PRECISION,
    charge       DOUBLE PRECISION,
    spin         DOUBLE PRECISION,
    lifetime_s   DOUBLE PRECISION,
    is_stable    BOOLEAN,
    source_id    INTEGER REFERENCES core.data_source
);

-- Chemistry
CREATE TABLE chemistry.qm9 (
    mol_id          SERIAL PRIMARY KEY,
    smiles          TEXT,
    homo            DOUBLE PRECISION,
    lumo            DOUBLE PRECISION,
    homo_lumo_gap   DOUBLE PRECISION,
    zpve            DOUBLE PRECISION,
    polarizability  DOUBLE PRECISION,
    n_atoms         SMALLINT,
    source_id       INTEGER REFERENCES core.data_source
);

-- Algebra
CREATE TABLE algebra.space_groups (
    sg_id             SERIAL PRIMARY KEY,
    number            SMALLINT UNIQUE,
    symbol            TEXT,
    point_group_order SMALLINT,
    crystal_system    TEXT,
    lattice_type      TEXT,
    is_symmorphic     BOOLEAN
);

CREATE TABLE algebra.lattices (
    lattice_id     SERIAL PRIMARY KEY,
    label          TEXT UNIQUE,
    dimension      SMALLINT,
    determinant    DOUBLE PRECISION,
    level          INTEGER,
    class_number   INTEGER,
    kissing_number INTEGER,
    source_id      INTEGER REFERENCES core.data_source
);

CREATE TABLE algebra.groups (
    group_id         SERIAL PRIMARY KEY,
    label            TEXT UNIQUE,
    order_val        INTEGER,
    exponent         INTEGER,
    n_conjugacy      INTEGER,
    is_abelian       BOOLEAN,
    is_solvable      BOOLEAN,
    source_id        INTEGER REFERENCES core.data_source
);

-- Analysis
CREATE TABLE analysis.fungrim (
    formula_id   SERIAL PRIMARY KEY,
    fungrim_id   TEXT UNIQUE,
    formula_type TEXT,
    module       TEXT,
    n_symbols    SMALLINT,
    formula_text TEXT,
    source_id    INTEGER REFERENCES core.data_source
);

CREATE TABLE analysis.oeis (
    seq_id       SERIAL PRIMARY KEY,
    oeis_id      TEXT UNIQUE,
    name         TEXT,
    first_terms  BIGINT[],
    growth_rate  DOUBLE PRECISION,
    entropy      DOUBLE PRECISION,
    is_monotone  BOOLEAN,
    source_id    INTEGER REFERENCES core.data_source
);

-- Biology
CREATE TABLE biology.metabolism (
    model_id         SERIAL PRIMARY KEY,
    bigg_id          TEXT UNIQUE,
    n_reactions      INTEGER,
    n_metabolites    INTEGER,
    n_genes          INTEGER,
    n_compartments   SMALLINT,
    frac_reversible  DOUBLE PRECISION,
    source_id        INTEGER REFERENCES core.data_source
);

-- Grants for prometheus_sci
GRANT USAGE ON SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    TO prometheus_read;
GRANT SELECT ON ALL TABLES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    TO prometheus_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    GRANT SELECT ON TABLES TO prometheus_read;

-- Writers need INSERT for ingestion
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    TO prometheus_write;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    TO prometheus_write;
ALTER DEFAULT PRIVILEGES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    GRANT INSERT, UPDATE ON TABLES TO prometheus_write;
ALTER DEFAULT PRIVILEGES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    GRANT USAGE, SELECT ON SEQUENCES TO prometheus_write;

-- ============================================================
-- 4. PROMETHEUS_FIRE DATABASE
-- ============================================================

\connect postgres
CREATE DATABASE prometheus_fire OWNER postgres;

\connect prometheus_fire

-- Schemas
CREATE SCHEMA IF NOT EXISTS xref;
CREATE SCHEMA IF NOT EXISTS tensor;
CREATE SCHEMA IF NOT EXISTS results;
CREATE SCHEMA IF NOT EXISTS kill;
CREATE SCHEMA IF NOT EXISTS meta;

-- Cross-references
CREATE TABLE xref.object_registry (
    object_id    BIGSERIAL PRIMARY KEY,
    source_db    TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_key   TEXT NOT NULL,
    object_type  TEXT NOT NULL,
    UNIQUE (source_db, source_table, source_key)
);
CREATE INDEX idx_object_type ON xref.object_registry(object_type);

CREATE TABLE xref.bridges (
    bridge_id        BIGSERIAL PRIMARY KEY,
    source_object_id BIGINT REFERENCES xref.object_registry,
    target_object_id BIGINT REFERENCES xref.object_registry,
    bridge_type      TEXT NOT NULL,
    evidence_grade   TEXT,
    confidence       DOUBLE PRECISION,
    provenance       TEXT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (source_object_id, target_object_id)
);

-- Tensor data
CREATE TABLE tensor.domain_features (
    object_id    BIGINT NOT NULL,
    domain       TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    value        DOUBLE PRECISION,
    PRIMARY KEY (object_id, feature_name)
);
CREATE INDEX idx_domain_feature ON tensor.domain_features(domain, feature_name);

CREATE TABLE tensor.domain_metadata (
    domain          TEXT PRIMARY KEY,
    n_objects       INTEGER,
    n_features      SMALLINT,
    feature_names   TEXT[],
    build_timestamp TIMESTAMPTZ
);

-- Results
CREATE TABLE results.ergon_runs (
    run_id       TEXT PRIMARY KEY,
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    n_generations INTEGER,
    n_tested     BIGINT,
    n_cells      INTEGER,
    max_depth    SMALLINT,
    seed         BIGINT,
    config       JSONB
);

CREATE TABLE results.hypotheses (
    hyp_id          BIGSERIAL PRIMARY KEY,
    run_id          TEXT REFERENCES results.ergon_runs,
    hypothesis_id   TEXT,
    domain_a        TEXT,
    domain_b        TEXT,
    feature_a       TEXT,
    feature_b       TEXT,
    coupling        TEXT,
    conditioning    TEXT,
    null_model      TEXT,
    resolution      INTEGER,
    z_score         DOUBLE PRECISION,
    p_value         DOUBLE PRECISION,
    survival_depth  SMALLINT,
    kill_test       TEXT,
    fitness         DOUBLE PRECISION,
    generation      INTEGER,
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_hyp_depth ON results.hypotheses(survival_depth DESC);
CREATE INDEX idx_hyp_run ON results.hypotheses(run_id);

CREATE TABLE results.harmonia_bonds (
    bond_id              BIGSERIAL PRIMARY KEY,
    domain_a             TEXT,
    domain_b             TEXT,
    bond_dim             SMALLINT,
    surviving_rank       SMALLINT,
    top_singular_values  DOUBLE PRECISION[],
    wall_time_seconds    DOUBLE PRECISION,
    scorer_type          TEXT,
    source_run_id        TEXT,
    falsification_tests  JSONB,
    created_at           TIMESTAMPTZ DEFAULT now()
);

-- Kill tracking
CREATE TABLE kill.taxonomy (
    kill_id          SERIAL PRIMARY KEY,
    hypothesis_type  TEXT,
    failure_mode     TEXT,
    f_test           TEXT,
    domain           TEXT,
    description      TEXT,
    constraint_added TEXT,
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE kill.shadow_cells (
    cell_key       TEXT PRIMARY KEY,
    domain_a       TEXT,
    domain_b       TEXT,
    feature_a      TEXT,
    feature_b      TEXT,
    coupling       TEXT,
    n_tested       INTEGER DEFAULT 0,
    n_survived     INTEGER DEFAULT 0,
    best_depth     SMALLINT DEFAULT 0,
    mean_depth     DOUBLE PRECISION DEFAULT 0,
    depth_variance DOUBLE PRECISION DEFAULT 0,
    best_z         DOUBLE PRECISION DEFAULT 0,
    dominant_kill  TEXT,
    kill_counts    JSONB DEFAULT '{}',
    confidence     DOUBLE PRECISION DEFAULT 0,
    gradient_score DOUBLE PRECISION DEFAULT 0,
    last_updated   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_shadow_gradient ON kill.shadow_cells(gradient_score DESC);
CREATE INDEX idx_shadow_dead ON kill.shadow_cells(best_depth, n_tested);
CREATE INDEX idx_shadow_pair ON kill.shadow_cells(domain_a, domain_b);

-- Operational metadata
CREATE TABLE meta.calibration (
    cal_id          SERIAL PRIMARY KEY,
    theorem_name    TEXT,
    expected_result TEXT,
    observed_result TEXT,
    passed          BOOLEAN,
    data_scale      TEXT,
    checked_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE meta.ingestion_log (
    log_id      SERIAL PRIMARY KEY,
    source_name TEXT,
    table_name  TEXT,
    rows_loaded INTEGER,
    duration_s  DOUBLE PRECISION,
    status      TEXT,
    error       TEXT,
    loaded_at   TIMESTAMPTZ DEFAULT now()
);

-- Grants for prometheus_fire
GRANT USAGE ON SCHEMA xref, tensor, results, kill, meta TO prometheus_read;
GRANT SELECT ON ALL TABLES IN SCHEMA xref, tensor, results, kill, meta TO prometheus_read;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA xref, tensor, results, kill, meta
    TO prometheus_write;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA xref, tensor, results, kill, meta
    TO prometheus_write;

ALTER DEFAULT PRIVILEGES IN SCHEMA xref, tensor, results, kill, meta
    GRANT SELECT ON TABLES TO prometheus_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA xref, tensor, results, kill, meta
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO prometheus_write;
ALTER DEFAULT PRIVILEGES IN SCHEMA xref, tensor, results, kill, meta
    GRANT USAGE, SELECT ON SEQUENCES TO prometheus_write;

-- ============================================================
-- 5. pg_hba.conf ADDITIONS (add to M1's pg_hba.conf)
-- ============================================================
-- Allow prometheus users from M2's IP range:
--
-- # Prometheus users
-- host prometheus_sci  harmonia   0.0.0.0/0  scram-sha-256
-- host prometheus_sci  ergon      0.0.0.0/0  scram-sha-256
-- host prometheus_sci  ingestor   0.0.0.0/0  scram-sha-256
-- host prometheus_fire harmonia   0.0.0.0/0  scram-sha-256
-- host prometheus_fire ergon      0.0.0.0/0  scram-sha-256
-- host prometheus_fire charon     0.0.0.0/0  scram-sha-256
-- host prometheus_fire ingestor   0.0.0.0/0  scram-sha-256
--
-- Then: sudo systemctl reload postgresql

-- ============================================================
-- 6. VERIFICATION QUERIES
-- ============================================================
-- Run these after setup to verify:
--
-- \connect prometheus_sci
-- SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
--
-- \connect prometheus_fire
-- SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
--
-- Test from M2:
-- psql -h devmirror.lmfdb.xyz -U ergon -d prometheus_fire -c "SELECT 1"
