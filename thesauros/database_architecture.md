# Prometheus Database Architecture

## Overview

Three Postgres databases on M1 + Redis cache. One Python package (`prometheus_data/`)
provides unified access from both machines. Code goes through GitHub, data lives in
Postgres, big files stay on the share.

```
                          M1 (devmirror.lmfdb.xyz)
    +-----------------------------------------------------------------+
    |                                                                 |
    |  Postgres 5432                          Redis 6379              |
    |  +------------------+                   +------------------+    |
    |  | lmfdb (existing) |                   | tensor slices    |    |
    |  | 612 tables, RO   |                   | domain metadata  |    |
    |  +------------------+                   | kill lookups     |    |
    |  | prometheus_sci   |                   +------------------+    |
    |  | normalized data  |                                           |
    |  +------------------+                                           |
    |  | prometheus_fire  |                                           |
    |  | working data, RW |                                           |
    |  +------------------+                                           |
    |                                                                 |
    +-----------------------------------------------------------------+
         ^                                     ^
         | psycopg2 (pooled)                   | redis-py
         |                                     |
    +----+-------------------------------------+----+
    |         prometheus_data package               |
    |  config.py | pool.py | cache.py | loaders.py  |
    +-----------------------------------------------+
         ^                          ^
         |                          |
    +---------+              +-----------+
    | Harmonia |              |   Ergon   |
    | (M1/M2)  |              |  (M1/M2)  |
    +---------+              +-----------+
```

---

## 1. Databases

### 1.1 lmfdb (existing, read-only)

The LMFDB PostgreSQL mirror. 612 tables. Do not modify.

- **Host:** devmirror.lmfdb.xyz:5432
- **User:** lmfdb (read-only)
- **Key tables consumed by Prometheus:**

| Table | Rows | Key Columns |
|-------|------|-------------|
| ec_curvedata | 3,824,372 | conductor, rank, analytic_rank, torsion, regulator, cm, num_bad_primes, class_size, faltings_height, szpiro_ratio |
| mf_newforms | 1,141,510 | level, weight, dim, char_order, char_parity, analytic_rank, trace_hash |
| artin_reps | 798,140 | Dim, Conductor, Galn, Galt, Indicator |
| g2c_curves | 66,158 | cond, disc_sign, analytic_rank, aut_grp_id, end_alg, st_group, torsion_subgroup |
| nf_fields | 22,178,569 | degree, disc_abs, class_number, regulator, class_group |

### 1.2 prometheus_sci (new, read-only for agents)

Normalized scientific data from non-LMFDB sources. Each scientific domain family
gets its own schema. Populated by ingestion scripts from JSON/CSV/share files.

**Schemas and tables:**

#### core
```sql
core.data_source (
    source_id    SERIAL PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    origin_url   TEXT,
    file_path    TEXT,
    loaded_at    TIMESTAMPTZ DEFAULT now(),
    row_count    INTEGER,
    checksum     TEXT
)
```

#### topology
```sql
topology.knots (
    knot_id          SERIAL PRIMARY KEY,
    name             TEXT UNIQUE NOT NULL,
    crossing_number  SMALLINT,
    determinant      INTEGER,
    alexander_coeffs DOUBLE PRECISION[],
    jones_coeffs     DOUBLE PRECISION[],
    conway_coeffs    DOUBLE PRECISION[],
    signature        SMALLINT,
    source_id        INTEGER REFERENCES core.data_source
)

topology.polytopes (
    polytope_id   SERIAL PRIMARY KEY,
    name          TEXT,
    dimension     SMALLINT,
    n_vertices    INTEGER,
    n_edges       INTEGER,
    n_facets      INTEGER,
    f_vector      INTEGER[],
    is_simplicial BOOLEAN,
    source_id     INTEGER REFERENCES core.data_source
)
```

#### physics
```sql
physics.superconductors (
    sc_id            SERIAL PRIMARY KEY,
    material_formula TEXT,
    tc               DOUBLE PRECISION,
    spacegroup       TEXT,
    sc_class         TEXT,
    source_id        INTEGER REFERENCES core.data_source
)

physics.materials (
    mat_id                    SERIAL PRIMARY KEY,
    material_id               TEXT UNIQUE,
    band_gap                  DOUBLE PRECISION,
    formation_energy_per_atom DOUBLE PRECISION,
    spacegroup_number         SMALLINT,
    density                   DOUBLE PRECISION,
    volume                    DOUBLE PRECISION,
    nsites                    INTEGER,
    source_id                 INTEGER REFERENCES core.data_source
)

physics.codata (
    constant_id  SERIAL PRIMARY KEY,
    name         TEXT UNIQUE NOT NULL,
    value        DOUBLE PRECISION,
    uncertainty  DOUBLE PRECISION,
    unit         TEXT,
    source_id    INTEGER REFERENCES core.data_source
)

physics.pdg_particles (
    particle_id  SERIAL PRIMARY KEY,
    name         TEXT,
    pdg_id       INTEGER,
    mass_gev     DOUBLE PRECISION,
    charge       DOUBLE PRECISION,
    spin         DOUBLE PRECISION,
    lifetime_s   DOUBLE PRECISION,
    is_stable    BOOLEAN,
    source_id    INTEGER REFERENCES core.data_source
)
```

#### chemistry
```sql
chemistry.qm9 (
    mol_id          SERIAL PRIMARY KEY,
    smiles          TEXT,
    homo            DOUBLE PRECISION,
    lumo            DOUBLE PRECISION,
    homo_lumo_gap   DOUBLE PRECISION,
    zpve            DOUBLE PRECISION,
    polarizability  DOUBLE PRECISION,
    n_atoms         SMALLINT,
    source_id       INTEGER REFERENCES core.data_source
)
```

#### algebra
```sql
algebra.space_groups (
    sg_id             SERIAL PRIMARY KEY,
    number            SMALLINT UNIQUE,
    symbol            TEXT,
    point_group_order SMALLINT,
    crystal_system    TEXT,
    lattice_type      TEXT,
    is_symmorphic     BOOLEAN
)

algebra.lattices (
    lattice_id     SERIAL PRIMARY KEY,
    label          TEXT UNIQUE,
    dimension      SMALLINT,
    determinant    DOUBLE PRECISION,
    level          INTEGER,
    class_number   INTEGER,
    kissing_number INTEGER,
    source_id      INTEGER REFERENCES core.data_source
)

algebra.groups (
    group_id         SERIAL PRIMARY KEY,
    label            TEXT UNIQUE,
    order            INTEGER,
    exponent         INTEGER,
    n_conjugacy      INTEGER,
    is_abelian       BOOLEAN,
    is_solvable      BOOLEAN,
    source_id        INTEGER REFERENCES core.data_source
)
```

#### analysis
```sql
analysis.fungrim (
    formula_id   SERIAL PRIMARY KEY,
    fungrim_id   TEXT UNIQUE,
    formula_type TEXT,
    module       TEXT,
    n_symbols    SMALLINT,
    formula_text TEXT,
    source_id    INTEGER REFERENCES core.data_source
)

analysis.oeis (
    seq_id       SERIAL PRIMARY KEY,
    oeis_id      TEXT UNIQUE,
    name         TEXT,
    first_terms  BIGINT[],
    growth_rate  DOUBLE PRECISION,
    entropy      DOUBLE PRECISION,
    is_monotone  BOOLEAN,
    source_id    INTEGER REFERENCES core.data_source
)
```

#### biology
```sql
biology.metabolism (
    model_id         SERIAL PRIMARY KEY,
    bigg_id          TEXT UNIQUE,
    n_reactions      INTEGER,
    n_metabolites    INTEGER,
    n_genes          INTEGER,
    n_compartments   SMALLINT,
    frac_reversible  DOUBLE PRECISION,
    source_id        INTEGER REFERENCES core.data_source
)
```

### 1.3 prometheus_fire (new, read-write)

Working database for enriched data, cross-references, and all operational results.

#### xref
```sql
xref.object_registry (
    object_id    BIGSERIAL PRIMARY KEY,
    source_db    TEXT NOT NULL,       -- 'lmfdb', 'sci', 'fire'
    source_table TEXT NOT NULL,
    source_key   TEXT NOT NULL,
    object_type  TEXT NOT NULL,       -- matches gene_schema.DOMAINS
    UNIQUE (source_db, source_table, source_key)
)

-- Index for reverse lookups
CREATE INDEX idx_object_type ON xref.object_registry(object_type);

xref.bridges (
    bridge_id        BIGSERIAL PRIMARY KEY,
    source_object_id BIGINT REFERENCES xref.object_registry,
    target_object_id BIGINT REFERENCES xref.object_registry,
    bridge_type      TEXT NOT NULL,
    evidence_grade   TEXT,            -- 'theorem', 'conjecture', 'statistical'
    confidence       DOUBLE PRECISION,
    provenance       TEXT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (source_object_id, target_object_id)
)
```

#### tensor
```sql
tensor.domain_features (
    object_id    BIGINT NOT NULL,
    domain       TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    value        DOUBLE PRECISION,
    PRIMARY KEY (object_id, feature_name)
)

-- Partitioned index for fast domain slice reads
CREATE INDEX idx_domain_feature ON tensor.domain_features(domain, feature_name);

tensor.domain_metadata (
    domain         TEXT PRIMARY KEY,
    n_objects      INTEGER,
    n_features     SMALLINT,
    feature_names  TEXT[],
    build_timestamp TIMESTAMPTZ
)
```

#### results
```sql
results.ergon_runs (
    run_id       TEXT PRIMARY KEY,
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    n_generations INTEGER,
    n_tested     BIGINT,
    n_cells      INTEGER,
    max_depth    SMALLINT,
    seed         BIGINT,
    config       JSONB
)

results.hypotheses (
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
)

-- Index for finding survivors
CREATE INDEX idx_hyp_depth ON results.hypotheses(survival_depth DESC);
CREATE INDEX idx_hyp_run ON results.hypotheses(run_id);

results.harmonia_bonds (
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
)
```

#### kill
```sql
kill.taxonomy (
    kill_id          SERIAL PRIMARY KEY,
    hypothesis_type  TEXT,
    failure_mode     TEXT,
    f_test           TEXT,
    domain           TEXT,
    description      TEXT,
    constraint_added TEXT,
    created_at       TIMESTAMPTZ DEFAULT now()
)

kill.shadow_cells (
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
)

-- Indices for shadow analysis
CREATE INDEX idx_shadow_gradient ON kill.shadow_cells(gradient_score DESC);
CREATE INDEX idx_shadow_dead ON kill.shadow_cells(best_depth, n_tested);
CREATE INDEX idx_shadow_pair ON kill.shadow_cells(domain_a, domain_b);
```

#### meta
```sql
meta.calibration (
    cal_id          SERIAL PRIMARY KEY,
    theorem_name    TEXT,
    expected_result TEXT,
    observed_result TEXT,
    passed          BOOLEAN,
    data_scale      TEXT,
    checked_at      TIMESTAMPTZ DEFAULT now()
)

meta.ingestion_log (
    log_id      SERIAL PRIMARY KEY,
    source_name TEXT,
    table_name  TEXT,
    rows_loaded INTEGER,
    duration_s  DOUBLE PRECISION,
    status      TEXT,
    error       TEXT,
    loaded_at   TIMESTAMPTZ DEFAULT now()
)
```

---

## 2. Roles and Users

```sql
-- Roles
CREATE ROLE prometheus_read;
CREATE ROLE prometheus_write;

-- Users (passwords set via ALTER USER on M1)
CREATE USER harmonia  IN ROLE prometheus_read;
CREATE USER ergon     IN ROLE prometheus_write;
CREATE USER charon    IN ROLE prometheus_write;
CREATE USER ingestor  IN ROLE prometheus_write;

-- prometheus_sci: read-only for all prometheus users
GRANT CONNECT ON DATABASE prometheus_sci TO prometheus_read, prometheus_write;
GRANT USAGE ON SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    TO prometheus_read;
GRANT SELECT ON ALL TABLES IN SCHEMA core, topology, physics, chemistry, algebra, analysis, biology, meta
    TO prometheus_read;

-- prometheus_fire: read for readers, read-write for writers
GRANT CONNECT ON DATABASE prometheus_fire TO prometheus_read, prometheus_write;
GRANT USAGE ON SCHEMA xref, tensor, results, kill, meta TO prometheus_read;
GRANT SELECT ON ALL TABLES IN SCHEMA xref, tensor, results, kill, meta TO prometheus_read;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA xref, tensor, results, kill, meta
    TO prometheus_write;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA xref, tensor, results, kill, meta
    TO prometheus_write;
```

---

## 3. Redis Cache Strategy

### What Gets Cached

| Key Pattern | Value | TTL | Purpose |
|-------------|-------|-----|---------|
| `tensor:slice:{domain}:{feature}` | Raw float32 bytes | 1 hour | Ergon tensor slices |
| `tensor:meta:{domain}` | JSON | 1 hour | Domain boundaries, feature list |
| `tensor:build_ts` | ISO string | 1 hour | Last tensor build time |
| `kill:all` | JSON array | 10 min | All kill records for pre-filter |
| `domain:{name}:features` | Raw float32 bytes | 4 hours | Harmonia DomainIndex tensors |
| `domain:{name}:meta` | JSON | 4 hours | n_objects, n_features |
| `shadow:{cell_key}` | JSON | None | Shadow archive cells (persistent) |

### Configuration

```
maxmemory 512mb
maxmemory-policy allkeys-lru
bind 0.0.0.0
requirepass <set-on-m1>
save 300 10          # RDB snapshot every 5 min if 10+ keys changed
```

### Size Estimates

- 7 domains x 7 features x 10K objects x 4 bytes = ~2 MB (current)
- 43 domains x 10 features x 50K objects x 4 bytes = ~86 MB (expanded)
- 3.8M EC x 16 features x 4 bytes = ~244 MB (full EC — fits in 512 MB)
- Shadow archive: ~5K cells x 200 bytes = ~1 MB

---

## 4. Connection Management

### Configuration File: `~/.prometheus/db.toml`

```toml
[lmfdb]
host = "devmirror.lmfdb.xyz"
port = 5432
dbname = "lmfdb"
user = "lmfdb"
password = "lmfdb"

[sci]
host = "devmirror.lmfdb.xyz"
port = 5432
dbname = "prometheus_sci"
user = "harmonia"

[fire]
host = "devmirror.lmfdb.xyz"
port = 5432
dbname = "prometheus_fire"
user = "ergon"

[redis]
host = "devmirror.lmfdb.xyz"
port = 6379
db = 0

[local]
duckdb_path = "charon/data/charon.duckdb"
share_path = "C:\\prometheus_share"
```

Passwords stored in `~/.prometheus/credentials.toml` (gitignored) or via
environment variables `PROMETHEUS_SCI_PASSWORD`, `PROMETHEUS_FIRE_PASSWORD`,
`PROMETHEUS_REDIS_PASSWORD`.

### Connection Priority

```
env var > ~/.prometheus/db.toml > hardcoded defaults
```

### Pool Settings

| Database | Min Conn | Max Conn | Idle Timeout |
|----------|----------|----------|--------------|
| lmfdb | 1 | 3 | 300s |
| prometheus_sci | 1 | 3 | 300s |
| prometheus_fire | 1 | 5 | 300s |

---

## 5. Data Flow

### Ingestion (one-time + periodic refresh)

```
Source files                     Ingestion target
──────────────────────────────────────────────────
LMFDB Postgres (existing)   --> stays as-is, query directly
cartography/knots/data/     --> prometheus_sci.topology.knots
cartography/physics/data/   --> prometheus_sci.physics.superconductors
                                prometheus_sci.physics.materials
C:\prometheus_share\...     --> prometheus_sci.* (various)
charon.duckdb tables        --> prometheus_fire.xref.* (migrated)
kill_taxonomy.db            --> prometheus_fire.kill.taxonomy
shadow_*.json               --> prometheus_fire.kill.shadow_cells
```

### Runtime (per Ergon hypothesis)

```
1. tensor_executor checks Redis for tensor:slice:{domain}:{feature}
   HIT  -> numpy.frombuffer(cached_bytes)
   MISS -> query prometheus_fire.tensor.domain_features
           or compute from prometheus_sci/lmfdb
           -> cache to Redis
           -> return numpy array

2. Kill taxonomy check from Redis kill:all
   HIT  -> check hypothesis against cached patterns
   MISS -> query prometheus_fire.kill.taxonomy
           -> cache to Redis

3. Result written to prometheus_fire.results.hypotheses (batched)
4. Shadow archive updated in Redis shadow:{cell_key}
   Periodic flush to prometheus_fire.kill.shadow_cells
```

### Harmonia Bridge

```
1. Read Ergon archive from prometheus_fire.results
   or from local JSON file
2. TT-Cross exploration using DomainIndex loaded via prometheus_data.loaders
   (which reads from prometheus_sci/lmfdb, cached in Redis)
3. Bond results written to prometheus_fire.results.harmonia_bonds
```

---

## 6. Migration Path

### Phase 0: Infrastructure
- Install Redis on M1
- Run `scripts/db_setup.sql` as Postgres superuser on M1
- Create `~/.prometheus/db.toml` on both machines
- Verify connectivity from M2

### Phase 1: Centralize Connections
- Ship `prometheus_data/config.py` and `prometheus_data/pool.py`
- Update `charon/src/config.py` to import from `prometheus_data`
- Replace hardcoded connection strings in ~15 files
- **Test:** all existing loaders still work

### Phase 2: Populate PrometheusSci
- Write `prometheus_data/migrate.py` with per-domain ingest functions
- Load all cartography/share JSON/CSV into PrometheusSci tables
- Record provenance in `core.data_source`
- **Test:** row counts match existing loader outputs

### Phase 3: Populate PrometheusFire
- Migrate `kill_taxonomy.db` (SQLite) to `kill.taxonomy`
- Migrate shadow archive JSON to `kill.shadow_cells`
- Build `xref.object_registry` from LMFDB + PrometheusSci
- Migrate DuckDB operational tables to Fire
- **Test:** kill taxonomy queries return same results

### Phase 4: Wire Harmonia Loaders
- Update `domain_index.py` loaders to query Postgres with file fallback
- Each loader: try `prometheus_sci` -> try local file -> raise
- **Test:** 7-theorem calibration at 100.000%

### Phase 5: Wire Ergon
- `tensor_builder.py` uses `prometheus_data.loaders`
- Tensor slices cached to Redis
- Results persisted to `prometheus_fire.results`
- Shadow archive flushed to `prometheus_fire.kill.shadow_cells`
- **Test:** throughput >= 5 hyp/s, same survival patterns

### Phase 6: Deprecate DuckDB (future)
- DuckDB becomes optional local cache
- Rebuild on demand from Postgres
- Remove direct DuckDB imports from Harmonia/Ergon

---

## 7. Constraints

- **Harmonia is sacrosanct.** No scoring behavior changes. Calibration check after every phase.
- **Phoneme framework is unvalidated.** No phoneme mappings in schema design. Features are raw values.
- **File fallback at every phase.** If Postgres/Redis is down, loaders fall back to local files.
- **DomainIndex interface unchanged.** `load_domains()` returns the same objects regardless of backend.
- **Credentials never in code.** Config file or env vars only. LMFDB `lmfdb/lmfdb` is the sole exception (public mirror).
