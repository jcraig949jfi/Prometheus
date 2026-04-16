# DuckDB — Legacy Data Layer

**Path:** charon/data/charon.duckdb  
**Size:** 1.2 GB  
**Access:** Read-only recommended  
**Status:** Partially migrated to Postgres. Still serving Harmonia/Ergon directly.

## Tables

| Table | Rows | Migrated To | Status |
|-------|------|-------------|--------|
| objects | 134,475 | prometheus_fire.xref.object_registry | MIGRATED |
| known_bridges | 17,314 | prometheus_fire.xref.bridges | MIGRATED |
| elliptic_curves | 31,073 | — | NEEDS SCHEMA |
| modular_forms | 102,150 | — | NEEDS SCHEMA |
| dirichlet_zeros | 184,830 | — | NEEDS SCHEMA |
| object_zeros | 120,649 | — | NEEDS SCHEMA |
| landscape | 119,464 | — | NEEDS SCHEMA |
| disagreement_atlas | 119,397 | — | NEEDS SCHEMA |
| graph_edges | 396,150 | — | NEEDS SCHEMA |
| hypothesis_queue | 100 | — | Not a clean kill.taxonomy match |
| ingestion_log | 3 | — | — |
| failure_log | 0 | — | — |
| l_functions | 0 | — | — |

**677K rows in 6 tables await schema design from Agora.** Request posted to agora:tasks.

## Key Table Schemas (Unmigrated)

### elliptic_curves
Enriched EC data with ainvs, rank, torsion, regulator, sha, faltings_height, trace_hash, etc. Richer than what's in the LMFDB mirror (which has the same data but as raw text).

### modular_forms
Level, weight, dim, Hecke coefficients, Fricke eigenvalue, Sato-Tate group, field polynomial.

### dirichlet_zeros
Per-L-function zeros vectors with conductor, degree, motivic weight. Almost entirely conductor < 5K.

### object_zeros
Per-object zeros vectors, root number, analytic rank. Overlaps with dirichlet_zeros but keyed by object_id.

### landscape
Embedding coordinates, local curvature, nearest neighbors, cluster IDs. Exploration state.

### disagreement_atlas
Per-object disagreement metrics: Jaccard, precision, recall, zero coherence, graph degree.

## Other DuckDB Files

| Path | Purpose |
|------|---------|
| noesis/v2/noesis_v2.duckdb | Noesis exploration data |

## Other Databases (SQLite)

| Path | Purpose |
|------|---------|
| agents/aletheia/data/knowledge_graph.db | Knowledge graph |
| agents/clymene/data/vault_registry.db | Vault registry |
| agents/skopos/data/scores.db | Scoring data |
| forge/v3/kill_taxonomy.db | Kill taxonomy (candidate for prometheus_fire.kill.taxonomy) |

## Access

```python
import duckdb
conn = duckdb.connect('D:/Prometheus/charon/data/charon.duckdb', read_only=True)
conn.execute("SHOW TABLES").fetchall()
```
