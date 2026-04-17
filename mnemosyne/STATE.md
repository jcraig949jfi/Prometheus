# Mnemosyne State — 2026-04-16 (Session 3 Update)

## NOTE TO MNEMOSYNE
Much has changed since 2026-04-15. This file reflects reality as of 2026-04-16. Trust this, not your session-2 memory.

---

## Identity
- **Role:** DBA & Data Steward (roles/Mnemosyne/RESPONSIBILITIES.md)
- **Machine:** M2 (SpectreX5)
- **Agora name:** Mnemosyne

## Connections

| Service | Host | Port | User | Status |
|---------|------|------|------|--------|
| LMFDB Postgres | 192.168.1.176 | 5432 | lmfdb/lmfdb | READ-ONLY, 30M+ rows, 6 indexes on lfunc, bsd_joined view |
| prometheus_sci | 192.168.1.176 | 5432 | postgres/prometheus | LIVE, 1,142,469 rows — zero empty tables |
| prometheus_fire | 192.168.1.176 | 5432 | postgres/prometheus | LIVE, ~600K rows |
| Redis | 192.168.1.176 | 6379 | password=prometheus | LIVE, graph/landscape/bridges/hypothesis populated |
| DuckDB | charon/data/charon.duckdb | local | — | FULLY MIGRATED — archive only, do NOT read from it |

**Password note:** Agent users (harmonia, ergon, charon, ingestor) were created with `CHANGE_ME_*` placeholder passwords in `scripts/db_setup.sql` and still have those. Keep using `postgres/prometheus` — it works across all three databases.

---

## What's Loaded (2026-04-16 state)

### prometheus_sci (1,142,469 rows — every table populated)

| Table | Rows | Source | Loader |
|-------|------|--------|--------|
| algebra.groups | 544,831 | cartography/groups/data/abstract_groups.json | mnemosyne/ingest_priority1.py |
| analysis.oeis | 394,454 | cartography/oeis/data/ (names + stripped + keywords) | thesauros/ingest_oeis.py |
| chemistry.qm9 | 133,885 | cartography/chemistry/data/qm9.csv | mnemosyne/ingest_priority1.py |
| algebra.lattices | 39,293 | cartography/lattices/data/lattices_full.json (key: "records") | thesauros/ingest_empty_tables.py (reload, was 26) |
| topology.knots | 12,965 | cartography/knots/data/knots.json | mnemosyne/ingest_priority1.py |
| physics.materials | 10,000 | cartography/physics/data/materials_project_10k.json | mnemosyne/migrate_m2.py |
| analysis.fungrim | 3,130 | cartography/fungrim/fungrim_formulas.json | thesauros/ingest_empty_tables.py |
| physics.superconductors | 2,012 | cartography/physics/data/superconductors/aflow_canonical_superconductors.csv | thesauros/ingest_empty_tables.py |
| topology.polytopes | 980 | cartography/polytopes/data/polytopes.json | mnemosyne/migrate_m2.py |
| physics.codata | 355 | cartography/physics/data/codata_constants.json | thesauros/ingest_empty_tables.py |
| algebra.space_groups | 230 | cartography/spacegroups/data/space_groups.json | mnemosyne/ingest_priority1.py |
| physics.pdg_particles | 226 | cartography/physics/data/pdg/particles.json | thesauros/ingest_empty_tables.py |
| biology.metabolism | 108 | cartography/metabolism/data/*.json (109 BiGG models) | thesauros/ingest_empty_tables.py |
| core.data_source | 6 | provenance tracking | — |

### prometheus_fire (~600K rows across 40+ tables, 8 schemas)

| Table | Rows | Source | Status |
|-------|------|--------|--------|
| xref.object_registry | 134,475 | charon.duckdb objects | migrated 2026-04-15 |
| xref.bridges | 17,314 | charon.duckdb known_bridges | migrated, also in Redis |
| zeros.object_zeros | 120,649 | charon.duckdb object_zeros | **NEW 2026-04-16** (P3 migration) |
| zeros.dirichlet_zeros | 184,830 | charon.duckdb dirichlet_zeros | **NEW 2026-04-16** |
| zeros.object_zeros_ext | 17,313 | charon.duckdb object_zeros_ext | **NEW 2026-04-16** |
| analysis.disagreement_atlas | 119,397 | charon.duckdb disagreement_atlas | **NEW 2026-04-16** |
| noesis.* (19 tables) | 51,992 | noesis/v2/noesis_v2.duckdb | **NEW 2026-04-16** (migrate_noesis_v2.py) |
| agora.messages | 107 | Agora streams | grows each session |
| agora.decisions | 3 | Agora decisions | — |
| agora.open_questions | 1 | OQ1 (spectral tail — RESOLVED as conductor confound) | can be marked resolved |
| meta.ingestion_log | 4 | Ingestion provenance | — |
| signals.specimens | 0 | Ready for population | schema created 2026-04-16 |
| signals.battery_results | 0 | Ready for population | schema created 2026-04-16 |
| results.hypotheses, results.ergon_runs, results.harmonia_bonds | 0 | Empty, schemas exist | — |
| kill.taxonomy, kill.shadow_cells | 0 | Empty, schemas exist | — |
| tensor.domain_features, tensor.domain_metadata | 0 | Empty, schemas exist | — |

### LMFDB Mirror (M1:5432, READ-ONLY)

| Table | Rows | Notes |
|-------|------|-------|
| lfunc_lfunctions | 24,351,376 | 341 GB. **6 indexes** built: origin, conductor_numeric (523 MB), conductor, degree, motivic_weight, order_of_vanishing |
| ec_curvedata | 3,824,372 | |
| mf_newforms | 1,141,510 | |
| artin_reps | 798,140 | |
| g2c_curves | 66,158 | |
| nf_fields | 2,400,000 | **PARTIAL** (10.8% of full 22,178,569) |
| **bsd_joined** | 2,481,157 | **NEW materialized view** (2026-04-16). EC + L-function joined via `lf.origin = 'EllipticCurve/Q/' || conductor || '/' || iso_letter`. 3 indexes. See `thesauros/bsd_joined_view.md`. |

### Redis (M1:6379, migrated from DuckDB 2026-04-16)

| Key Pattern | Type | Count | Purpose |
|-------------|------|-------|---------|
| graph:neighbors:{id} | Set | 96,210 | 396K adjacency edges |
| landscape:{id} | Hash | 119,464 | coords, curvature, cluster |
| landscape:by_curvature | Sorted Set | 119,464 | exploration priority queue |
| bridge:{src}:{tgt} | Hash | 17,314 | bridge metadata |
| bridges:by_source/target/type | Set | — | bridge indexes |
| hypothesis:queue | Sorted Set | 100 | pending hypotheses |
| agora:main, agora:challenges, agora:discoveries, agora:tasks | Stream | ~140+ msgs | team comms |

---

## Completed Since Last Session (2026-04-15 → 2026-04-16)

### Data ingestion
- All 6 empty prometheus_sci tables filled (codata, fungrim, pdg, superconductors, metabolism, lattices reload)
- OEIS 394K sequences loaded with computed features (growth_rate, entropy, is_monotone)
- Noesis v2 DuckDB migrated (19 tables, 52K rows)
- `bsd_joined` materialized view built (2.48M rows)

### Infrastructure
- `idx_lfunc_origin` built (complements the conductor_numeric index)
- DuckDB killed across the codebase:
  - `prometheus_data/pool.py` — `get_duckdb()` deprecated with warning
  - `harmonia/src/domain_index.py` — all 12 DuckDB calls replaced with Postgres/Redis
  - `ergon/tensor_builder.py`, `forge/v3/executor.py` — EC + MF loaders use lmfdb Postgres
  - 13 directories have `DUCKDB_NOTICE.md` for legacy script reference
- `signals` schema created in prometheus_fire (specimens + battery_results tables)
- `noesis` schema created in prometheus_fire

### Documentation
- `thesauros/data_dictionary.md` — 810 lines, every column, every source, every script
- `thesauros/unified_data_plan.md` — P1-P5 marked DONE, P6/P7 partial
- `thesauros/bsd_joined_view.md` — full column reference for the new view
- `thesauros/loose_files.md` — verified paths and row counts
- `thesauros/duckdb_legacy.md` — updated to reflect FULLY MIGRATED status

### Scripts added (thesauros/)
- `create_bsd_joined.py`, `migrate_p3_duckdb.py`, `migrate_p6_nffields.py`, `migrate_p7_cartography.py`
- `migrate_noesis_v2.py`, `ingest_empty_tables.py`, `ingest_oeis.py`

---

## Priority Scorecard (thesauros/unified_data_plan.md)

| Priority | Status |
|----------|--------|
| P1 — lfunc origin index | **DONE** |
| P2 — EC↔lfunc join key + bsd_joined | **DONE** |
| P3 — DuckDB → Postgres + Redis | **DONE** (854K rows, 61s) |
| P4 — Signal registry | **DONE** (schema ready, empty) |
| P5 — Redis tensor/battery cache | **DONE** (part of P3) |
| P6 — nf_fields full pull | PARTIAL (2.4M / 22M) |
| P7 — Cartography ingestion | **DONE** (all empty tables filled) |
| P8 — Cleanup | NOT STARTED |

---

## Pending Work for Next Session

### Small / mechanical
1. Complete `nf_fields` pull (remaining 19.8M rows — overnight streaming job, resume from row 2.4M)
2. Fix agent user passwords in scripts/db_setup.sql (harmonia, ergon, charon, ingestor still have CHANGE_ME_* placeholders)
3. Mark OQ1 spectral tail resolved in `agora.open_questions` (downgraded to MARGINAL, conductor confound)

### Medium / could be big
4. OEIS auxiliary data: crossrefs (62 MB), formulas (60 MB), programs (73 MB) — new tables in analysis schema
5. Additional datasets per `thesauros/loose_files.md`:
   - physics.exoplanets (6,158 rows from confirmed_exoplanets.csv)
   - physics.gw_events (219 from gwtc_params.csv)
   - physics.pulsars (4,351)
   - topology.mahler_measures (2,977 already computed in charon/data/mahler_measures.json)
   - analysis.findstat (FindStat mathematical statistics)

### Prometheus v2 infrastructure (if we go that direction)
6. `prometheus_fire.operators` schema for the Operator Telescope (see `docs/Prometheus_v2/0_Prometheus_v2_Base_Paper.md`)
7. Compute first 4 operators (Alexander-at-roots-of-unity for knots, Mahler measure, Hecke eigenvalues, splitting patterns)

---

## Key Findings From the 04-15/04-16 Sessions

1. **BSD Sha circularity** — Rank >= 2 Sha computed assuming BSD. Testing BSD with it is circular.
2. **NF backbone killed** — All 3 scorers (cosine, distributional, alignment) measure feature geometry only. Permutation null z=0. Harmonia + Ergon confirmed.
3. **AlignmentCoupling seed-dependent** — z=2.67 did not replicate across 10 seeds (6 returned flat 0.5). Retracted.
4. **OQ1 spectral tail killed** — Conductor confound. rho=-0.068 globally but p>0.05 in every conductor bin.
5. **abc strongly supported** — Szpiro ratio monotone decrease survives bad-prime stratification.
6. **Langlands GL(2)** — 100% match (10,880/10,880) within LMFDB range.
7. **Tensor measures feature geometry, not object-level coupling** — the single most important methodological finding.

---

## Files

- `mnemosyne/migrate_m2.py` — M2 migration script (ran 2026-04-15)
- `mnemosyne/ingest_priority1.py` — Priority 1 ingestion (ran 2026-04-15)
- `mnemosyne/STATE.md` — this file
- `mnemosyne/data_audit_20260415.md` — data inventory (partly stale, refer to thesauros/data_dictionary.md instead)
- `mnemosyne/README.md` — role intro
- `roles/Mnemosyne/SESSION_JOURNAL_20260415.md` — session 2 journal
- `roles/Mnemosyne/RESPONSIBILITIES.md` — role definition
- `thesauros/data_dictionary.md` — **authoritative** data reference
- `thesauros/unified_data_plan.md` — priority tracker
- `thesauros/bsd_joined_view.md` — bsd_joined column reference
- `thesauros/duckdb_legacy.md` — migration record
- `docs/Prometheus_v2/0_Prometheus_v2_Base_Paper.md` — local-only v2 vision paper
