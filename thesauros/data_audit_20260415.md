# Data Audit — 2026-04-15
## What exists where, and what needs to move

---

## Active Databases

### LMFDB Postgres (M1, devmirror.lmfdb.xyz)
- **Status:** Running, read-only
- **ec_curvedata:** 3,824,372 rows (elliptic curves)
- **612 tables total** (full LMFDB mirror)
- **Access:** `lmfdb:lmfdb@devmirror.lmfdb.xyz:5432/lmfdb`

### DuckDB (local, charon/data/charon.duckdb)
- **Status:** Running, read-only recommended
- **Tables (14):**

| Table | Rows | Purpose |
|-------|------|---------|
| elliptic_curves | 31,073 | EC subset with zeros |
| modular_forms | 102,150 | Modular form metadata |
| dirichlet_zeros | 184,830 | Dirichlet L-function zeros |
| object_zeros | 120,649 | L-function zeros per object |
| object_zeros_ext | 17,313 | Extended zero data |
| known_bridges | 17,314 | Cross-domain bridges |
| landscape | 119,464 | Exploration landscape |
| disagreement_atlas | 119,397 | Disagreement tracking |
| objects | 134,475 | Unified object registry |
| graph_edges | 396,150 | Knowledge graph |
| hypothesis_queue | 100 | Queued hypotheses |
| ingestion_log | 3 | Load tracking |
| failure_log | 0 | Empty |
| l_functions | 0 | Empty |

### Redis (M1, 192.168.1.176:6379)
- **Status:** Running, 12 keys
- **Agora streams:** agora:main, agora:challenges, agora:tasks, agora:discoveries
- **Agent state:** agent:Mnemosyne, agent:Kairos, agent:Claude_M1

---

## Not Yet Created

### prometheus_sci (needs db_setup.sql on M1)
Target schemas: core, topology, physics, chemistry, algebra, analysis, biology, meta

### prometheus_fire (needs db_setup.sql on M1)
Target schemas: xref, tensor, results, kill, meta

---

## Data Files Available for Ingestion

### Priority 1: Direct schema matches in db_setup.sql

| Source | Target Table | Est. Rows | File Size |
|--------|-------------|-----------|-----------|
| cartography/knots/data/knots.json | topology.knots | ~2,977 | 92 MB |
| cartography/chemistry/data/qm9.csv | chemistry.qm9 | ~134K | 29 MB |
| cartography/spacegroups/data/space_groups.json | algebra.space_groups | 230 | small |
| cartography/lattices/data/*.json | algebra.lattices | ~1,000 | 6.8 MB |
| cartography/groups/data/groups.json | algebra.groups | ~1,000+ | 107 MB |
| cartography/fungrim/data/*.json | analysis.fungrim | ~1,000+ | 9.6 MB |
| cartography/physics/data/codata/ | physics.codata | ~300 | small |
| cartography/atlas/data/ | multiple | varies | 228 MB |

### Priority 2: Large datasets requiring schema design

| Source | Content | Est. Rows | File Size |
|--------|---------|-----------|-----------|
| cartography/oeis/data/ | OEIS sequences | ~375K | ~50 GB |
| cartography/maass/data/ | Maass forms | ~15K forms | 676 MB |
| cartography/genus2/data/ | Genus-2 curves | ~66K | 1.1 GB |
| cartography/isogenies/data/ | Isogeny graphs | ~3K primes | 662 MB |
| cartography/metabolism/data/ | Metabolic models | ~110 models | ~13 GB |

### Priority 3: Already in LMFDB (no ingestion needed)

| Data | LMFDB Table | Rows |
|------|-------------|------|
| Elliptic curves | ec_curvedata | 3,824,372 |
| Modular forms | mf_newforms | ~1.1M |
| Genus-2 curves | g2c_curves | ~66K |
| Artin representations | artin_reps | ~793K |
| L-functions | lfunc_lfunctions | ~24.2M |

### Priority 4: Large experimental data (cold storage candidates)

| Source | Content | Size |
|--------|---------|------|
| cartography/convergence/data/ | Experiment results | 121 GB |
| charon/data/dirichlet_raw_cache.pkl | Raw cache | 1.8 GB |

---

## Migration Plan

### Phase 1: Create databases (BLOCKED on James)
Run db_setup.sql on M1. Estimated: 5 minutes.

### Phase 2: Ingest Priority 1 files
Write Python ingestors for each P1 source. Target: 1 hour per table.
Total: ~8 tables, ~140K rows, trivial data volume.

### Phase 3: Wire LMFDB data
No ingestion needed — LMFDB is already in Postgres. Create views or
materialized views in prometheus_sci if cross-joins are needed.

### Phase 4: Ingest Priority 2 files
Larger datasets. Design schemas as needed. OEIS and metabolism are
the heavy lifts.

### Phase 5: DuckDB migration
Move DuckDB tables to prometheus_fire (objects, landscape,
disagreement_atlas, known_bridges, graph_edges). This eliminates
the DuckDB sync problem.
