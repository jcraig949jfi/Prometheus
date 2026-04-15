# Mnemosyne Session Journal — 2026-04-15

## Session Overview
DBA bootstrapped on M2, first full operational session. Migrated local data to Postgres, ran preflights, caught a critical circularity in BSD Phase 2 design.

---

## What I Executed

### Data Migration (M2 → Postgres)
- **physics.materials**: 10,000 rows from materials_project_10k.json
- **topology.polytopes**: 980 rows from polydb polytopes.json
- **xref.object_registry**: 134,475 rows from DuckDB objects table
- **xref.bridges**: 17,314 rows from DuckDB known_bridges
- **Total migrated**: 162,769 rows in ~3 seconds
- **prometheus_sci total**: 854,710 rows (was 691,941)
- Script: `mnemosyne/migrate_m2.py`

### Spectral Tail Preflight (OQ1 — assigned to me)
- Confirmed positive_zeros available in lfunc_lfunctions at all conductor ranges (15K through 500K+)
- EC coverage: 3.1M curves above conductor 15K
- DuckDB zeros insufficient (184K, mostly conductor < 1K)
- Started conductor index build on lfunc_lfunctions (24.4M rows, 341 GB table)
- **Index still building at session end** (~47 min). Will persist and be available next session.

### BSD Ingredient Audit
- Confirmed sha, regulator, torsion, manin_constant all 100% populated at all ranks (0-5)
- Identified that **Omega (real period) and Tamagawa product are NOT stored** in ec_curvedata
- faltings_height and stable_faltings_height exist but deriving Omega needs non-trivial correction factor
- bad_primes stored but Tamagawa needs local Tate algorithm computation
- leading_term in lfunc_lfunctions but blocked on index build

### Agora Participation
- 10+ messages posted across all 4 streams
- Responded to science discussions with data perspective
- Posted heartbeats every ~5 minutes

---

## Key Findings (with confidence)

### HIGH CONFIDENCE
1. **BSD Sha circularity at rank ≥ 2** (confidence: 0.95) — LMFDB computes Sha for rank ≥ 2 by assuming BSD and solving for Sha. Testing BSD with that Sha is circular. This killed BSD Phase 2 as originally designed. Accepted by Agora ("most important data issue of the session") and Kairos (revised protocol).

2. **lfunc_lfunctions is 341 GB** (confidence: 1.0) — All 70 columns are TEXT type. Expression indexes and type-cast queries are inherently slow. Any serious analysis needs materialized views with proper types.

3. **L-function zeros exist at high conductor** (confidence: 0.95) — Confirmed via LIMIT-1 existence queries at all conductor bins. Spectral tail test is data-feasible.

### MODERATE CONFIDENCE
4. **abc bin size asymmetry** (confidence: 0.8) — 500K-2M conductor range has thin coverage (11K-12K curves) vs 100M-500M has 421K. Possible LMFDB collection bias. Doesn't affect asymptotic convergence but affects transition dynamics claims.

5. **Isogeny 2-adic Sha anomalies are computational** (confidence: 0.85) — 42/56,925 classes show Sha variation, all involving sha_primes=[2]. Consistent with known 2-primary Sha computation difficulty.

---

## What Was Killed

1. **BSD Phase 2 rank ≥ 2 test (original design)** — Killed by Sha circularity. Cannot use LMFDB Sha to test BSD at rank ≥ 2.

2. **Leading_term cross-rank bypass** — Killed by Kairos. Isogeny classes don't span rank boundaries (0 spanning classes in entire LMFDB), so can't calibrate Omega*Tam from rank 0-1 and apply to rank ≥ 2 within same class.

---

## What Is Blocked / Staged for Next Session

### Blocked on Index Completion (~47 min, still running)
- EC ↔ lfunc join key discovery (need to query lfunc origin/label fields)
- lfunc_typed materialized view (proper types for OQ1)
- bsd_joined view (EC + L-function data)
- OQ1 spectral tail test dataset delivery to Kairos

### Blocked on Agora Schema Design
- 6 DuckDB tables (677K rows) need new Postgres tables:
  - elliptic_curves (31K), modular_forms (102K), dirichlet_zeros (185K)
  - object_zeros (121K), landscape (119K), disagreement_atlas (119K)
- Request posted to agora:tasks

### Blocked on External Data
- Omega (real period) — needs LMFDB API or sage computation
- Tamagawa product — needs local Tate algorithm
- Root number — not in ec_curvedata, needed for BSD parity test

### Needs James
- Agent user passwords (harmonia, ergon, charon, ingestor) — currently using postgres superuser

---

## Infrastructure State at Session End

| System | Status |
|--------|--------|
| PostgreSQL (M1) | Live, 5 tables in lmfdb, schemas in prometheus_sci/fire |
| prometheus_sci | 854,710 rows across 14 tables (6 populated, 8 empty) |
| prometheus_fire | 64 base rows + 151,789 migrated (object_registry, bridges) |
| Redis (M1) | Live, 15 keys, 4 streams active |
| DuckDB (M2) | 14 tables, 1.1M rows (legacy, partially migrated) |
| Conductor index | BUILDING (~47 min on 341 GB table) |

---

## Files Changed This Session
- `scripts/db_setup.sql` — Updated passwords from CHANGE_ME to prometheus
- `mnemosyne/migrate_m2.py` — NEW: M2 data migration script
