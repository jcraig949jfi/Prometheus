"""
Charon DuckDB Schema — initialized from LMFDB field structures.

Schema emerged from data reconnaissance against the LMFDB PostgreSQL mirror.
Three invariants:
  1. Known correspondences reproduce as geometric proximity
  2. Every object carries full type-specific metadata
  3. Every object has a universal invariant vector (L-function Dirichlet coefficients)
"""

import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"

SCHEMA_SQL = """
-- ============================================================
-- Core object store: all mathematical objects live here
-- ============================================================
CREATE TABLE IF NOT EXISTS objects (
    id INTEGER PRIMARY KEY,
    lmfdb_label TEXT UNIQUE NOT NULL,
    object_type TEXT NOT NULL,              -- 'elliptic_curve', 'modular_form', 'l_function'
    conductor BIGINT,                       -- shared across types
    invariant_vector DOUBLE[],             -- universal coordinates: a_p for first 50 primes
    properties JSON,                        -- type-specific metadata (rank, torsion, level, etc.)
    ingested_at TIMESTAMP DEFAULT current_timestamp,
    coefficient_completeness DOUBLE         -- fraction of 50 primes with known a_p
);

-- ============================================================
-- Elliptic curves: type-specific fields from ec_curvedata + ec_classdata
-- ============================================================
CREATE TABLE IF NOT EXISTS elliptic_curves (
    object_id INTEGER PRIMARY KEY REFERENCES objects(id),
    lmfdb_label TEXT UNIQUE NOT NULL,
    lmfdb_iso TEXT NOT NULL,               -- isogeny class label
    cremona_label TEXT,                     -- Cremona label (Clabel)
    cremona_iso TEXT,                       -- Cremona isogeny class
    conductor BIGINT NOT NULL,
    ainvs DOUBLE[],                        -- Weierstrass coefficients [a1,a2,a3,a4,a6]
    rank SMALLINT,
    analytic_rank SMALLINT,
    torsion SMALLINT,
    torsion_structure INTEGER[],
    cm SMALLINT,                           -- CM discriminant (0 if no CM)
    regulator DOUBLE,
    sha INTEGER,                           -- analytic order of Sha
    degree BIGINT,                         -- modular degree
    isogeny_degrees INTEGER[],
    bad_primes INTEGER[],
    jinv_num DOUBLE,                       -- j-invariant numerator
    jinv_den DOUBLE,                       -- j-invariant denominator
    aplist INTEGER[],                      -- a_p for first 25 primes (from ec_classdata)
    anlist INTEGER[],                      -- a_n for n=0..20 (from ec_classdata)
    class_size SMALLINT,
    class_deg SMALLINT,
    manin_constant SMALLINT,
    optimality SMALLINT,
    semistable BOOLEAN,
    faltings_height DOUBLE,
    trace_hash BIGINT                      -- for fast matching
);

-- ============================================================
-- Modular forms: type-specific fields from mf_newforms + mf_hecke_nf
-- ============================================================
CREATE TABLE IF NOT EXISTS modular_forms (
    object_id INTEGER PRIMARY KEY REFERENCES objects(id),
    lmfdb_label TEXT UNIQUE NOT NULL,
    space_label TEXT,
    level INTEGER NOT NULL,
    weight SMALLINT NOT NULL,
    dim INTEGER,                           -- dimension of Hecke eigenvalue field
    hecke_orbit INTEGER,
    hecke_orbit_code BIGINT,               -- join key to hecke tables
    char_order INTEGER,
    char_parity SMALLINT,
    char_conductor INTEGER,
    char_orbit_label TEXT,
    fricke_eigenval SMALLINT,
    atkin_lehner_string TEXT,
    analytic_conductor DOUBLE,
    self_twist_type SMALLINT,
    is_cm BOOLEAN,
    is_rm BOOLEAN,
    is_self_dual BOOLEAN,
    sato_tate_group TEXT,
    traces DOUBLE[],                       -- tr(a_n) for n=1..1000 (from mf_newforms)
    ap_coeffs JSON,                        -- a_p algebraic coefficients (from mf_hecke_nf)
    ap_maxp INTEGER,                       -- max prime stored in ap_coeffs
    field_poly DOUBLE[],                   -- minimal polynomial of coefficient field
    related_objects TEXT[]
);

-- ============================================================
-- L-functions: shared invariant layer
-- ============================================================
CREATE TABLE IF NOT EXISTS l_functions (
    object_id INTEGER PRIMARY KEY REFERENCES objects(id),
    lmfdb_label TEXT UNIQUE NOT NULL,
    origin TEXT,                            -- path linking to source object
    degree SMALLINT,
    conductor BIGINT,
    motivic_weight SMALLINT,
    algebraic BOOLEAN,
    primitive BOOLEAN,
    self_dual BOOLEAN,
    rational BOOLEAN,
    central_character TEXT,
    lgroup TEXT,                            -- 'GL2', etc.
    analytic_conductor DOUBLE,
    root_analytic_conductor DOUBLE,
    order_of_vanishing SMALLINT,
    sign_arg DOUBLE,
    root_number TEXT,
    leading_term TEXT,
    gamma_factors JSON,
    spectral_parameters JSON,              -- mu_real, nu_real_doubled, etc.
    bad_primes INTEGER[],
    bad_lfactors JSON,
    euler_factors JSON,                    -- Euler factors at small primes
    dirichlet_coefficients JSON,
    z1 DOUBLE,                             -- first zero
    z2 DOUBLE,                             -- second zero
    z3 DOUBLE,                             -- third zero
    types TEXT[]                            -- ['EC'], ['CMF'], etc.
);

-- ============================================================
-- Known ground-truth correspondences (calibration set)
-- ============================================================
CREATE TABLE IF NOT EXISTS known_bridges (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES objects(id),
    target_id INTEGER REFERENCES objects(id),
    source_label TEXT NOT NULL,
    target_label TEXT NOT NULL,
    bridge_type TEXT NOT NULL,             -- 'modularity', 'langlands', 'galois'
    verified BOOLEAN DEFAULT TRUE,
    source_reference TEXT,                 -- provenance of the correspondence
    created_at TIMESTAMP DEFAULT current_timestamp,
    UNIQUE (source_id, target_id)
);

-- ============================================================
-- Geometric embedding (rebuilt each loop iteration)
-- ============================================================
CREATE TABLE IF NOT EXISTS landscape (
    object_id INTEGER PRIMARY KEY REFERENCES objects(id),
    coordinates DOUBLE[],                  -- spectral embedding position
    local_curvature DOUBLE,
    nearest_neighbors INTEGER[],           -- k-NN in embedding space
    cluster_id INTEGER,
    embedding_version INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- ============================================================
-- Candidate discoveries + hypothesis queue
-- ============================================================
CREATE TABLE IF NOT EXISTS hypothesis_queue (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES objects(id),
    target_id INTEGER REFERENCES objects(id),
    source_label TEXT,
    target_label TEXT,
    geometric_distance DOUBLE,
    invariant_distance DOUBLE,
    status TEXT DEFAULT 'pending',         -- 'pending', 'reviewed', 'confirmed', 'rejected'
    notes TEXT,
    discovered_at TIMESTAMP DEFAULT current_timestamp
);

-- ============================================================
-- Failure log (drives the closed loop)
-- ============================================================
CREATE TABLE IF NOT EXISTS failure_log (
    id INTEGER PRIMARY KEY,
    failure_type TEXT NOT NULL,            -- 'data_gap', 'encoding', 'embedding', 'genuine_negative', 'candidate'
    description TEXT,
    source_stage TEXT,                     -- 'ingest', 'organize', 'test', 'search'
    routed_to_stage TEXT,                  -- where the loop returns
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    logged_at TIMESTAMP DEFAULT current_timestamp
);

-- ============================================================
-- Ingestion metadata: track what we've pulled and when
-- ============================================================
CREATE TABLE IF NOT EXISTS ingestion_log (
    id INTEGER PRIMARY KEY,
    source_table TEXT NOT NULL,            -- 'ec_curvedata', 'mf_newforms', etc.
    query_params JSON,                     -- what filters were applied
    rows_fetched INTEGER,
    rows_inserted INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running'          -- 'running', 'completed', 'failed'
);

-- ============================================================
-- Sequences for auto-increment IDs
-- ============================================================
CREATE SEQUENCE IF NOT EXISTS objects_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS bridges_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS hypothesis_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS failure_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS ingestion_id_seq START 1;
"""

# The first 50 primes — our universal coordinate system
FIRST_50_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229
]


def init_db(db_path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Initialize the Charon DuckDB database with schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute(SCHEMA_SQL)
    return con


def get_db(db_path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Get a connection to the existing Charon database."""
    return duckdb.connect(str(db_path))


if __name__ == "__main__":
    con = init_db()
    tables = con.execute("SHOW TABLES").fetchall()
    print(f"Charon DB initialized at {DB_PATH}")
    print(f"Tables: {[t[0] for t in tables]}")
    con.close()
