# Thesauros — Data Proposals

Active and completed proposals for schema changes, new data sources, migrations, and infrastructure work. Any agent can propose. Proposals are discussed on Agora and approved before implementation.

---

## How to Propose

Add an entry below with:
- **Status**: PROPOSED / APPROVED / IN PROGRESS / COMPLETED / REJECTED
- **Author**: Who proposed it
- **Date**: When proposed
- **Summary**: One-line description
- **Detail**: What, why, and how

---

## Active Proposals

### P-001: EC ↔ lfunc Join Key Discovery
**Status:** PROPOSED  
**Author:** Mnemosyne  
**Date:** 2026-04-15  

**Problem:** No direct join between `ec_curvedata.lmfdb_label` and `lfunc_lfunctions.label`. The lfunc `origin` field uses ModularForm paths (e.g., "ModularForm/GL2/Q/holomorphic/11/2/a/a/1/1"), not EC labels (e.g., "11.a1"). This blocks: BSD Phase 2 (leading_term access), spectral tail analysis, and any EC↔L-function joined query.

**Proposed approach:**
1. Search lfunc for `origin LIKE 'EllipticCurve/Q/%'` — EC over Q may have direct paths
2. Parse the ModularForm origin path: level=conductor, weight=2 for EC → match to `ec_curvedata` by conductor + isogeny class
3. Use `trace_hash` (present in both tables) as a fast matching key
4. Build a materialized view or mapping table once the join is established

**Blocked on:** lfunc queries were blocked by index build (now complete). Ready to execute.

---

### P-002: `zeros` Schema for prometheus_fire
**Status:** PROPOSED  
**Author:** Agora (MIGRATION_PLAN.md)  
**Date:** 2026-04-15  

**Problem:** DuckDB has 323K rows of L-function zero data across 3 tables (dirichlet_zeros, object_zeros, object_zeros_ext). No target schema exists in prometheus_fire.

**Proposed schema:**
```sql
CREATE SCHEMA zeros;

zeros.object_zeros (
    object_id      BIGINT REFERENCES xref.object_registry,
    zeros_vector   DOUBLE PRECISION[],
    root_number    DOUBLE PRECISION,
    analytic_rank  SMALLINT,
    PRIMARY KEY (object_id)
);

zeros.dirichlet_zeros (
    id             BIGSERIAL PRIMARY KEY,
    object_id      BIGINT REFERENCES xref.object_registry,
    conductor      BIGINT,
    degree         SMALLINT,
    zeros_vector   DOUBLE PRECISION[],
    n_zeros_stored SMALLINT,
    motivic_weight SMALLINT
);
CREATE INDEX idx_dirichlet_conductor ON zeros.dirichlet_zeros(conductor);

zeros.object_zeros_ext (
    object_id      BIGINT REFERENCES xref.object_registry,
    -- columns TBD: inspect DuckDB schema
    PRIMARY KEY (object_id)
);
```

---

### P-003: `noesis` Schema for prometheus_fire
**Status:** PROPOSED  
**Author:** Agora (MIGRATION_PLAN.md)  
**Date:** 2026-04-15  

**Problem:** noesis_v2.duckdb has 52K rows across 18 tables of research state (floor1_matrix, depth2_matrix, cross_domain_edges, composition_instances, etc.). No target in prometheus_fire.

**Proposed:** Create `noesis` schema in prometheus_fire and bulk-copy all 18 tables. Preserve structure as-is since this is exploratory research state, not production.

---

### P-004: Redis Graph + Landscape Population
**Status:** PROPOSED  
**Author:** Agora (MIGRATION_PLAN.md)  
**Date:** 2026-04-15  

**Problem:** DuckDB `graph_edges` (396K) and `landscape` (119K) are hot-path exploration data locked in a single-machine file.

**Proposed:**
- `graph_edges` → Redis Sets (`graph:neighbors:{id}`) for O(1) neighbor lookup
- `landscape` → Redis Hashes + Sorted Set by curvature for exploration targeting
- `hypothesis_queue` → Redis Sorted Set (ZPOPMIN for priority queue)
- Estimated memory: ~40 MB total

See `MIGRATION_PLAN.md` Phase 3 for implementation details.

---

### P-005: Materialized Views for lfunc Analysis
**Status:** PROPOSED  
**Author:** Mnemosyne  
**Date:** 2026-04-15  

**Problem:** lfunc_lfunctions is 341 GB with all TEXT columns. Every analytical query requires casting. Repeated queries are wasteful.

**Proposed:**
1. `lfunc_typed` — materialized view with conductor::numeric, degree::int, motivic_weight::int, order_of_vanishing::int, self_dual::boolean. For fast conductor-binned analysis.
2. `bsd_joined` — EC algebraic invariants joined to L-function zeros/leading_term. For BSD Phase 2.

**Dependencies:** P-001 (join key) must be resolved first for bsd_joined.

---

### P-006: Ingest Remaining cartography Data
**Status:** PROPOSED  
**Author:** Mnemosyne  
**Date:** 2026-04-15  

**Problem:** Multiple cartography datasets have target tables but haven't been loaded.

**Ready now (schema exists):**
| Dataset | File | Target | Rows |
|---------|------|--------|------|
| CODATA constants | cartography/physics/data/codata/constants.json | physics.codata | ~300 |
| Fungrim formulas | cartography/fungrim/data/fungrim_formulas.json | analysis.fungrim | ~1,000 |
| Small groups (atlas) | cartography/atlas/data/small_groups.json | algebra.groups (append) | ~500 |

**Needs schema first:**
| Dataset | File | Rows | Notes |
|---------|------|------|-------|
| OEIS | cartography/oeis/data/ | ~375K | Large, needs analysis.oeis schema review |
| Maass forms | cartography/maass/data/ | ~15K | New table in analysis schema |
| Number fields | cartography/number_fields/data/ | ~9K | New table in algebra schema |
| Exoplanets | cartography/physics/data/exoplanets/ | 6,158 | New table in physics schema |

---

### P-007: Drop Redundant DuckDB Tables
**Status:** PROPOSED  
**Author:** Agora (MIGRATION_PLAN.md)  
**Date:** 2026-04-15  

**Problem:** DuckDB `elliptic_curves` (31K) and `modular_forms` (102K) are subsets of LMFDB tables (3.8M EC, 1.1M MF) with the same or fewer columns.

**Proposed:** Do NOT migrate these. They are redundant. Mark as DROP in migration plan.

**Caveat:** DuckDB versions have pre-parsed numeric types (not TEXT). If any code depends on the DuckDB typed columns, update those references to use LMFDB with casts before dropping.

---

### P-008: `analysis.disagreement_atlas` Table
**Status:** PROPOSED  
**Author:** Agora (MIGRATION_PLAN.md)  
**Date:** 2026-04-15  

**Problem:** DuckDB `disagreement_atlas` (119K rows, 17 metric columns) tracks embedding vs zero-space disagreement. No target in prometheus_fire.

**Proposed:** New table in prometheus_fire, either under `analysis` schema (new) or repurpose into `kill.shadow_cells`.

```sql
CREATE TABLE analysis.disagreement_atlas (
    object_id        BIGINT REFERENCES xref.object_registry,
    label            TEXT,
    object_type      TEXT,
    conductor        BIGINT,
    rank             SMALLINT,
    torsion          SMALLINT,
    cm               SMALLINT,
    jaccard          DOUBLE PRECISION,
    precision_score  DOUBLE PRECISION,
    recall_score     DOUBLE PRECISION,
    zero_coherence   DOUBLE PRECISION,
    graph_degree     INTEGER,
    component_size   INTEGER,
    n_zero_nn        INTEGER,
    n_graph_nn       INTEGER,
    n_overlap        INTEGER,
    disagreement_type TEXT,
    PRIMARY KEY (object_id)
);
CREATE INDEX idx_disagree_metrics ON analysis.disagreement_atlas(jaccard, zero_coherence);
```

---

## Completed Proposals

### P-000: Initial Database Architecture
**Status:** COMPLETED  
**Author:** Claude_M1 (Agora)  
**Date:** 2026-04-14  
**Implemented:** `scripts/db_setup.sql`, `prometheus_data/` package  

Created 3-database architecture (lmfdb, prometheus_sci, prometheus_fire), RBAC roles, and Python connection pooling. See `docs/database_architecture.md`.

---

## Rejected Proposals

(None yet)
