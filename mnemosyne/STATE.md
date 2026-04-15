# Mnemosyne State — 2026-04-15 (Session 2 End)

---

## Identity
- **Role:** DBA & Data Steward (roles/Mnemosyne/RESPONSIBILITIES.md)
- **Machine:** M2 (SpectreX5)
- **Agora name:** Mnemosyne

## Connections

| Service | Host | Port | User | Status |
|---------|------|------|------|--------|
| LMFDB Postgres | 192.168.1.176 | 5432 | lmfdb/lmfdb | READ-ONLY, 3.8M EC, 24.4M lfunc |
| prometheus_sci | 192.168.1.176 | 5432 | postgres/prometheus | LIVE, 854K rows |
| prometheus_fire | 192.168.1.176 | 5432 | postgres/prometheus | LIVE, 152K rows |
| Redis | 192.168.1.176 | 6379 | password=prometheus | LIVE |
| DuckDB | charon/data/charon.duckdb | local | — | 14 tables, 134K objects |

**Note:** Agent users (harmonia, ergon, charon, ingestor) exist but password is not "prometheus". Using postgres superuser for now. James needs to update passwords.

## What's Loaded

### prometheus_sci (854,710 rows)

| Table | Rows | Source |
|-------|------|--------|
| algebra.groups | 544,831 | cartography/groups/data/abstract_groups.json |
| chemistry.qm9 | 133,885 | cartography/chemistry/data/qm9.csv |
| topology.knots | 12,965 | cartography/knots/data/knots.json |
| physics.materials | 10,000 | cartography/physics/data/materials_project_10k.json |
| topology.polytopes | 980 | cartography/polytopes/data/polytopes.json |
| algebra.space_groups | 230 | cartography/spacegroups/data/space_groups.json |
| algebra.lattices | 26 | cartography/lattices/data/*.json |
| core.data_source | 6 | provenance tracking |

### prometheus_fire (~152K rows)

| Table | Rows | Source |
|-------|------|--------|
| xref.object_registry | 134,475 | DuckDB objects |
| xref.bridges | 17,314 | DuckDB known_bridges |
| agora.messages | 60 | Agora bootstrap |
| agora.decisions | 3 | Agora bootstrap |
| agora.open_questions | 1 | Spectral tail OQ1 |
| meta.ingestion_log | 4 | M2 migration log |

### LMFDB Mirror (5 tables)

| Table | Rows | Size |
|-------|------|------|
| lfunc_lfunctions | 24,351,376 | 341 GB |
| ec_curvedata | 3,824,372 | — |
| mf_newforms | 1,100,000+ | — |
| artin_reps | 793,000+ | — |
| g2c_curves | 66,158 | — |

## In-Progress: Conductor Index Build

- `CREATE INDEX idx_lfunc_conductor_numeric ON lfunc_lfunctions ((conductor::numeric))`
- Started this session, ran ~47 min, still active (pid 27940, BufferIo)
- Table is 341 GB, all columns TEXT — expression index is I/O-bound
- **Should persist** and be available next session (Postgres index builds are transactional)
- Once done, enables: materialized views, join key discovery, OQ1 dataset

## Pending Work (Next Session)

### Blocked on Index Completion
1. Find EC ↔ lfunc join key (origin or label pattern matching)
2. Build lfunc_typed materialized view (proper types)
3. Build bsd_joined view (EC + L-function leading_term)
4. Deliver OQ1 spectral tail test dataset

### Blocked on Agora Schema Design
5. Migrate 6 remaining DuckDB tables (677K rows) — request posted to agora:tasks

### Blocked on External Data/Computation
6. Omega (real period) — not in ec_curvedata, needs sage or LMFDB API
7. Tamagawa product — not stored, needs local Tate algorithm
8. Root number — not in ec_curvedata, needed for BSD parity test

### Blocked on James
9. Agent user passwords (harmonia, ergon, charon, ingestor)

## Key Findings This Session

1. **BSD Sha circularity** — Rank ≥ 2 Sha computed assuming BSD. Testing BSD with it is circular.
2. **Leading_term bypass killed** — Isogeny classes don't span rank boundaries. Can't cross-calibrate.
3. **L-function zeros confirmed** at all conductor ranges for spectral tail test.
4. **abc_quality and szpiro_ratio** are precomputed columns in ec_curvedata.

## Files
- `mnemosyne/migrate_m2.py` — M2 migration script (executed successfully)
- `mnemosyne/STATE.md` — this file
- `mnemosyne/data_audit_20260415.md` — data inventory
- `roles/Mnemosyne/SESSION_JOURNAL_20260415.md` — full session journal
- `roles/Mnemosyne/RESPONSIBILITIES.md` — role definition
