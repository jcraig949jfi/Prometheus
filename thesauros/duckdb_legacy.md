# DuckDB — FULLY MIGRATED (2026-04-16)

**All DuckDB data has been migrated to Postgres and Redis.**  
**Do NOT write new code that imports duckdb. Use `prometheus_data.get_fire()` or `get_lmfdb()`.**  
**The .duckdb files are read-only archives. They will be deleted after all consumers are verified.**

## Migration Status

| DuckDB Table | Rows | Migrated To | Status |
|-------------|------|-------------|--------|
| objects | 134,475 | prometheus_fire.xref.object_registry | **DONE** |
| known_bridges | 17,314 | prometheus_fire.xref.bridges + Redis bridge:* | **DONE** |
| elliptic_curves | 31,073 | DROPPED (redundant with lmfdb.ec_curvedata 3.8M) | **DONE** |
| modular_forms | 102,150 | DROPPED (redundant with lmfdb.mf_newforms 1.1M) | **DONE** |
| dirichlet_zeros | 184,830 | prometheus_fire.zeros.dirichlet_zeros | **DONE** |
| object_zeros | 120,649 | prometheus_fire.zeros.object_zeros | **DONE** |
| object_zeros_ext | 17,313 | prometheus_fire.zeros.object_zeros_ext | **DONE** |
| landscape | 119,464 | Redis landscape:* + landscape:by_curvature | **DONE** |
| disagreement_atlas | 119,397 | prometheus_fire.analysis.disagreement_atlas | **DONE** |
| graph_edges | 396,150 | Redis graph:neighbors:* (96K adjacency sets) | **DONE** |
| hypothesis_queue | 100 | Redis hypothesis:queue (sorted set) | **DONE** |
| ingestion_log | 3 | prometheus_fire.meta.ingestion_log | **DONE** |
| failure_log | 0 | Empty, not migrated | N/A |
| l_functions | 0 | Empty, not migrated | N/A |

**noesis_v2.duckdb** (19 tables, 52K rows) -> prometheus_fire.noesis.* — **DONE**

## How to Access the Data Now

```python
# Postgres (zeros, objects, bridges, atlas, noesis)
from prometheus_data import get_fire
with get_fire() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM zeros.object_zeros LIMIT 10")
    cur.execute("SELECT * FROM xref.object_registry LIMIT 10")
    cur.execute("SELECT * FROM analysis.disagreement_atlas LIMIT 10")
    cur.execute("SELECT * FROM noesis.floor1_matrix LIMIT 10")

# Postgres (EC, MF, lfunc — the big LMFDB tables)
from prometheus_data import get_lmfdb
with get_lmfdb() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM ec_curvedata LIMIT 10")
    cur.execute("SELECT * FROM bsd_joined WHERE rank >= 2 LIMIT 10")

# Redis (graph, landscape, bridges, hypothesis queue)
from prometheus_data import get_redis
r = get_redis()
r.smembers("graph:neighbors:42")           # adjacency
r.zrevrange("landscape:by_curvature", 0, 50)  # top curvature points
r.hgetall("bridge:1:2")                    # bridge details
r.zpopmin("hypothesis:queue")              # next hypothesis
```

## Archive Files (Do Not Delete Yet)

| Path | Size | Purpose |
|------|------|---------|
| charon/data/charon.duckdb | 1.2 GB | Archive — all data migrated |
| noesis/v2/noesis_v2.duckdb | 19.5 MB | Archive — all data migrated |

These will be deleted after verifying all legacy scripts have been updated or retired.

## Other Legacy Databases (SQLite, not yet migrated)

| Path | Purpose |
|------|---------|
| agents/aletheia/data/knowledge_graph.db | Knowledge graph |
| agents/clymene/data/vault_registry.db | Vault registry |
| agents/skopos/data/scores.db | Scoring data |
| forge/v3/kill_taxonomy.db | Kill taxonomy (candidate for prometheus_fire.kill.taxonomy) |
