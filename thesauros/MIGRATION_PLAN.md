# Thesauros — DuckDB to Postgres+Redis Migration Plan
## Named for: θησαυρός — treasury, storehouse. Where Prometheus keeps its data.

---

## Current State

### DuckDB: 2 databases, 1.3M total rows

**charon.duckdb** (1.1 GB, 14 tables, 1,242,918 rows):

| Table | Rows | Category | Destination |
|-------|------|----------|-------------|
| `objects` | 134,475 | Core registry (universal invariant vectors, type, conductor) | **Postgres** `prometheus_fire.xref.object_registry` |
| `elliptic_curves` | 31,073 | Type-specific EC data | **DROP** — redundant with `lmfdb.ec_curvedata` (3.8M rows, better coverage) |
| `modular_forms` | 102,150 | Type-specific MF data | **DROP** — redundant with `lmfdb.mf_newforms` (1.1M rows, better coverage) |
| `l_functions` | 0 | Empty | **DROP** |
| `dirichlet_zeros` | 184,830 | L-function zero vectors per object | **Postgres** `prometheus_fire.zeros.*` (analytical queries) |
| `object_zeros` | 120,649 | Zeros + root number + analytic rank | **Postgres** `prometheus_fire.zeros.*` |
| `object_zeros_ext` | 17,313 | Extended zeros from enrichment | **Postgres** `prometheus_fire.zeros.*` |
| `known_bridges` | 17,314 | Ground-truth correspondences | **Redis** Hash + Set indexes (hot-path O(1) lookup) + **Postgres** `prometheus_fire.xref.bridges` (durable record) |
| `graph_edges` | 396,150 | k-NN knowledge graph | **Redis** Sets (adjacency lists: `graph:neighbors:{id}`) |
| `landscape` | 119,464 | Spectral embedding coordinates, curvature, clusters | **Redis** Sorted Set by curvature + Hash per point |
| `disagreement_atlas` | 119,397 | Embedding vs zero-space disagreement metrics | **Postgres** `prometheus_fire.kill.shadow_cells` or new table |
| `hypothesis_queue` | 100 | Candidate discoveries | **Redis** Sorted Set by priority (ZPOPMIN to grab next) |
| `failure_log` | 0 | Empty | **Redis** Stream (merge with `agora:kills`) |
| `ingestion_log` | 3 | Provenance | **Postgres** `prometheus_fire.meta.ingestion_log` |

**noesis_v2.duckdb** (19.5 MB, 18 tables, 51,992 rows):

| Table | Rows | Destination |
|-------|------|-------------|
| `floor1_matrix` | 2,120 | **Postgres** new `prometheus_fire.noesis.*` schema |
| `depth2_matrix` | 19,049 | **Postgres** `prometheus_fire.noesis.*` |
| `tradition_hub_matrix` | 2,213 | **Postgres** `prometheus_fire.noesis.*` |
| `cross_domain_edges` | 20,502 | **Postgres** `prometheus_fire.noesis.*` |
| `composition_instances` | 4,962 | **Postgres** `prometheus_fire.noesis.*` |
| Other 13 tables | ~3,146 | **Postgres** `prometheus_fire.noesis.*` |

---

## Destination Architecture

### Redis (hot-path exploration state — shared across all agents)

```
Redis (WSL M1, localhost:6379)
│
├── graph:neighbors:{object_id}    SET of neighbor IDs (396K edges → ~134K sets)
│   └── SINTER for common neighbors, SISMEMBER for adjacency check
│
├── bridge:{source_id}:{target_id} HASH {type, verified, source_ref}
├── bridges:by_source:{id}         SET of bridge IDs
├── bridges:by_target:{id}         SET of bridge IDs  
├── bridges:by_type:{type}         SET of bridge IDs
│   └── O(1) "is this bridge known?" before wasting battery cycles
│
├── landscape:{object_id}          HASH {x, y, z, curvature, cluster_id, version}
├── landscape:by_curvature         SORTED SET (score=curvature, member=object_id)
├── landscape:by_cluster:{id}      SET of object IDs
│   └── ZREVRANGE for top-N highest-curvature exploration targets
│
├── hypothesis:queue               SORTED SET (score=priority, member=hypothesis_json)
│   └── ZPOPMIN to grab next hypothesis; SISMEMBER for dedup
│
└── agora:*                        STREAMS (already exist — add kills stream)
```

**Why Redis for these:**
- `graph_edges`: O(1) neighbor lookup, SINTER for common neighbors. Graph traversal is Redis's sweet spot.
- `known_bridges`: O(1) "does this bridge exist?" prevents agents re-discovering known correspondences.
- `landscape`: ZREVRANGE for "give me 50 highest-curvature points" in microseconds. Shared exploration map.
- `hypothesis_queue`: It's literally a priority queue. Sorted Sets are made for this.
- All of these are **hot-path exploration state** that every agent touches during research cycles. Currently locked in DuckDB on one machine.

**Memory estimate:** ~396K edges × ~50 bytes + 134K landscape hashes × ~100 bytes + 17K bridge hashes × ~200 bytes ≈ **40 MB**. Trivial for Redis.

### Postgres (analytical queries — durable, relational)

```
prometheus_fire (existing, M1:5432)
│
├── xref.object_registry           134K rows (from objects)
│   ├── object_id BIGSERIAL
│   ├── lmfdb_label TEXT UNIQUE
│   ├── object_type TEXT
│   ├── conductor BIGINT
│   ├── invariant_vector DOUBLE PRECISION[]   ← a_p for first 50 primes
│   ├── properties JSONB                      ← type-specific metadata
│   └── coefficient_completeness DOUBLE
│
├── xref.bridges                   17K rows (from known_bridges)
│   ├── source_object_id → object_registry
│   ├── target_object_id → object_registry
│   ├── bridge_type TEXT
│   ├── verified BOOLEAN
│   └── evidence_grade TEXT
│
├── zeros.object_zeros             121K rows (from object_zeros)
│   ├── object_id → object_registry
│   ├── zeros_vector DOUBLE PRECISION[]
│   ├── root_number DOUBLE
│   └── analytic_rank SMALLINT
│
├── zeros.dirichlet_zeros          185K rows (from dirichlet_zeros)
│   ├── object_id → object_registry
│   ├── zeros_vector DOUBLE PRECISION[]
│   └── conductor BIGINT (indexed for range queries)
│
├── zeros.object_zeros_ext         17K rows (from object_zeros_ext)
│   ├── object_id → object_registry
│   └── extended zeros columns
│
├── analysis.disagreement_atlas    119K rows
│   ├── object_id → object_registry
│   ├── jaccard, precision, recall DOUBLE
│   ├── zero_coherence DOUBLE
│   └── ... (17 metric columns)
│
├── noesis.*                       52K rows (new schema, from noesis_v2.duckdb)
│   ├── floor1_matrix, depth2_matrix, etc.
│   └── Full Noesis research state
│
└── meta.ingestion_log             (existing + 3 from DuckDB)
```

**New schema needed:** `zeros` (for the three zeros tables). The existing `db_setup.sql` doesn't have this. Also `noesis` for the v2 research state.

---

## What Gets Dropped

| Table | Rows | Reason |
|-------|------|--------|
| `elliptic_curves` | 31K | `lmfdb.ec_curvedata` has 3.8M with all the same columns and more |
| `modular_forms` | 102K | `lmfdb.mf_newforms` has 1.1M with all the same columns and more |
| `l_functions` | 0 | Empty, never populated |
| `failure_log` | 0 | Empty; merge concept into `agora:kills` stream |

Total dropped: 133K rows (all redundant or empty).

---

## Migration Phases

### Phase 1: Schema Creation (~30 min)
- Add `zeros` schema to `prometheus_fire` (3 tables)
- Add `noesis` schema to `prometheus_fire` (18 tables)
- Extend `xref.object_registry` with `invariant_vector` and `properties` columns if not present
- No data moved yet.

### Phase 2: Postgres Migration (~2 hours, parallelizable)

**Worker 1:** `objects` → `xref.object_registry` (134K rows)
- Map `id` → preserve as `object_id` (all other tables reference it)
- `lmfdb_label` → `source_key`, add `source_db='charon'`, `source_table='objects'`
- `invariant_vector DOUBLE[]` → `DOUBLE PRECISION[]` (direct)
- `properties JSON` → `JSONB` (direct, add GIN index)

**Worker 2:** Zeros tables → `zeros.*` (323K rows)
- `dirichlet_zeros` (185K) — direct copy, add conductor index
- `object_zeros` (121K) — direct copy
- `object_zeros_ext` (17K) — direct copy
- All reference `object_id` from Worker 1 (run after Worker 1 or defer FK)

**Worker 3:** `disagreement_atlas` → `analysis.disagreement_atlas` (119K rows)
- Direct copy of 17 metric columns
- Add index on `(jaccard, zero_coherence)` for shadow cell queries

**Worker 4:** Noesis v2 (52K rows, 18 tables)
- Bulk copy all 18 tables into `noesis.*` schema
- Preserve structure as-is (research state, not production)

### Phase 3: Redis Population (~1 hour)

**Worker 1:** `graph_edges` → Redis Sets (396K edges)
```python
for edge in graph_edges:
    r.sadd(f"graph:neighbors:{edge.source_id}", edge.target_id)
    r.sadd(f"graph:neighbors:{edge.target_id}", edge.source_id)  # undirected
```

**Worker 2:** `known_bridges` → Redis Hashes + Sets (17K)
```python
for bridge in known_bridges:
    key = f"bridge:{bridge.source_id}:{bridge.target_id}"
    r.hset(key, mapping={type, verified, source_reference})
    r.sadd(f"bridges:by_source:{bridge.source_id}", key)
    r.sadd(f"bridges:by_target:{bridge.target_id}", key)
    r.sadd(f"bridges:by_type:{bridge.bridge_type}", key)
```

**Worker 3:** `landscape` → Redis Hashes + Sorted Set (119K)
```python
for point in landscape:
    r.hset(f"landscape:{point.object_id}", mapping={
        coordinates, curvature, cluster_id, version
    })
    r.zadd("landscape:by_curvature", {point.object_id: point.curvature})
    r.sadd(f"landscape:by_cluster:{point.cluster_id}", point.object_id)
```

**Worker 4:** `hypothesis_queue` → Redis Sorted Set (100 rows, trivial)
```python
for hyp in hypothesis_queue:
    r.zadd("hypothesis:queue", {json.dumps(hyp): hyp.priority})
```

### Phase 4: Update Loaders + Validate (~1 hour)
- Update `harmonia/src/domain_index.py` to read from Postgres instead of DuckDB
- Update `charon/src/schema.py` references
- Update `prometheus_data/pool.py` `get_duckdb()` to log deprecation warning
- Run row count reconciliation: DuckDB counts vs Postgres+Redis counts
- Spot-check 100 random objects across both systems

### Phase 5: Archive DuckDB
- Keep `charon.duckdb` and `noesis_v2.duckdb` as read-only archives
- Do NOT delete until all consumers verified on new sources

---

## Object ID Strategy

DuckDB `objects.id` is referenced by all other tables (landscape, graph_edges, bridges, zeros, etc.). Two options:

**Option A (recommended): Preserve IDs.** Insert into `xref.object_registry` with the same integer IDs. Set the Postgres sequence to start above max(id). Simple, no remapping needed.

**Option B: Remap.** Let Postgres assign new IDs, build a mapping table, update all FKs. More work, no benefit.

Go with Option A.

---

## Dual-Write Period

During and after migration, both DuckDB and Postgres/Redis should be queryable. The `get_duckdb()` function in `pool.py` remains as fallback. New code should use Postgres/Redis. Old code continues to work until updated.

---

## Effort Estimate

| Phase | Time | Workers | Parallelizable? |
|-------|------|---------|-----------------|
| Schema creation | 30 min | 1 | No |
| Postgres migration | 2 hours | 4 (one per assignment) | Yes |
| Redis population | 1 hour | 4 (one per structure) | Yes |
| Loader updates + validation | 1 hour | 2 | Partially |
| **Total** | **~3 hours** | **4 workers** | **Phases 2+3 fully parallel** |

With 4 workers on M1, Phases 2 and 3 can run simultaneously. Realistic wall-clock: **half a day** including testing and validation.

---

## Dependencies

- Postgres running on M1 (confirmed)
- Redis running on WSL M1 (confirmed)
- `~/.prometheus/db.toml` with correct connection details
- `psycopg2` and `redis` Python packages (confirmed)
- DuckDB files accessible at current paths

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Object ID collision with existing `xref.object_registry` data | Check max ID in both before migration; sequence reset |
| Array column performance in Postgres | `DOUBLE PRECISION[]` is native; add GIN index on `invariant_vector` if needed |
| Redis memory pressure from 396K edge sets | ~40 MB total, well within Redis default 512 MB limit |
| Breaking Harmonia/Charon loaders | Dual-write period; `get_duckdb()` stays as fallback |
| Data loss during migration | DuckDB is read-only source; archive after, never delete during |
