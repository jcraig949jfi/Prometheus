# Mnemosyne State — 2026-04-15
## Save point before session restart

---

## Identity
- **Role:** DBA & Data Steward (roles/Mnemosyne/RESPONSIBILITIES.md)
- **Machine:** M2 (SpectreX5)
- **Agora name:** Mnemosyne

## Connections (all verified working)

| Service | Host | Port | User | Status |
|---------|------|------|------|--------|
| LMFDB Postgres | devmirror.lmfdb.xyz | 5432 | lmfdb/lmfdb | READ-ONLY, 3.8M EC |
| prometheus_sci | 192.168.1.176 | 5432 | ingestor/CHANGE_ME_ingestor | LIVE, 691K rows |
| prometheus_fire | 192.168.1.176 | 5432 | ergon/CHANGE_ME_ergon | LIVE, empty |
| Redis | 192.168.1.176 | 6379 | password=prometheus | LIVE |
| DuckDB | charon/data/charon.duckdb | local | — | 14 tables, 134K objects |

Postgres superuser: postgres/prometheus on 192.168.1.176

Config files:
- ~/.prometheus/db.toml (connection details)
- ~/.prometheus/credentials.toml (passwords)

## What's Loaded in prometheus_sci

| Table | Rows | Source File |
|-------|------|------------|
| topology.knots | 12,965 | cartography/knots/data/knots.json |
| chemistry.qm9 | 133,885 | cartography/chemistry/data/qm9.csv |
| algebra.space_groups | 230 | cartography/spacegroups/data/space_groups.json |
| algebra.lattices | 26 | cartography/lattices/data/*.json |
| algebra.groups | 544,831 | cartography/groups/data/abstract_groups.json |
| core.data_source | 4 | provenance tracking |
| **TOTAL** | **691,937** | |

### Schema fix applied
- algebra.groups: order_val and exponent columns widened from INTEGER to NUMERIC
  (some group orders are 60+ digits, e.g. label "258623241511168180642964355153611979969197632389120000000000.a")

### Not yet loaded (Priority 2)
- physics.superconductors — need to find source CSV
- physics.materials — cartography/physics/data/materials_project_10k.json
- physics.codata — cartography/physics/data/codata/
- physics.pdg_particles — need to find source
- analysis.oeis — cartography/oeis/data/ (~50GB, 1,536 files)
- analysis.fungrim — cartography/fungrim/data/
- biology.metabolism — cartography/metabolism/data/ (~13GB)
- topology.polytopes — cartography/polytopes/data/

## prometheus_fire — Empty, Ready
All 11 tables exist with proper schemas. Ready for:
- results.ergon_runs, results.hypotheses, results.harmonia_bonds
- kill.taxonomy, kill.shadow_cells
- tensor.domain_features, tensor.domain_metadata
- xref.object_registry, xref.bridges
- meta.calibration, meta.ingestion_log

## Agora Status
- Mnemosyne registered and announced on agora:main
- Sent data audit, task claims, and loading completion announcement
- Other agents: Kairos (M2, offline), Claude_M1 (M1, offline)
- All agents on 2-minute polling loops

## Key Files I Created
- mnemosyne/README.md — workspace overview
- mnemosyne/STATE.md — this file
- mnemosyne/data_audit_20260415.md — complete inventory of all data sources
- mnemosyne/ingest_priority1.py — ingestion scripts (needs update for direct connection)
- docs/forensic_timeline_april_2026.md — forensic audit (committed to main, pushed)

## Git Status
- Branch: data-layer-architecture
- forensic_timeline committed and pushed to main via cherry-pick
- mnemosyne/ directory is new, not yet committed

## Next Steps
1. Load remaining Priority 2 tables (superconductors, materials, CODATA, OEIS, fungrim)
2. Migrate DuckDB tables to prometheus_fire (objects, landscape, known_bridges, etc.)
3. Set up Redis cache layer for tensor slices
4. Wire Harmonia/Ergon loaders to query Postgres with file fallback
5. Change default passwords (CHANGE_ME_* are still in use)
