# Thesauros — Unified Data Plan

Consolidated from proposals by Mnemosyne, Harmonia, Agora (Claude_M1), and Charon. This is the single document the team should reference for data infrastructure decisions.

**Contributors:** Agora (architecture + migration plan), Harmonia (storage recommendation + science bottlenecks), Mnemosyne (data dictionary + inventory + migration execution), Charon (bridge work + battery needs)

---

## The Three-Tier Architecture

Everyone agrees on this structure. No dissent.

```
Postgres = truth    (queryable, joinable, indexed, durable)
Redis    = speed    (cached state, coordination, hot lookups)
Files    = archive  (static reference, model weights, backups)
```

### What We Have Now

| Tier | System | Size | Status |
|------|--------|------|--------|
| Postgres | lmfdb (5 tables) | 341 GB, 30M rows | LIVE, read-only |
| Postgres | prometheus_sci (14 tables) | ~855K rows | LIVE, 6 tables populated |
| Postgres | prometheus_fire (15 tables) | ~152K rows | LIVE, partially populated |
| Redis | 192.168.1.176:6379 | ~10 MB | LIVE, Agora streams + agent state |
| DuckDB | charon.duckdb | 1.2 GB, 1.1M rows | LEGACY, partially migrated |
| DuckDB | noesis_v2.duckdb | 19.5 MB, 52K rows | LEGACY, not migrated |
| Flat files | cartography/ | ~170 GB | Source data, partially loaded |

---

## Priority Actions (Ordered by Impact)

### Priority 1: Create lfunc Origin Index
**Impact:** Turns 90-second EC↔lfunc joins into ~1-second queries  
**Effort:** 1 command, ~30 min build time  
**Source:** Harmonia (identified as "single highest-leverage infrastructure change")  
**Blocked on:** Write access to lmfdb database (James)  

```sql
CREATE INDEX idx_lfunc_origin ON lfunc_lfunctions(origin);
```

We already have `idx_lfunc_conductor_numeric` (523 MB, built 2026-04-15). The origin index would be similar size. These two indexes together make lfunc queryable for both conductor-binned analysis and cross-table joins.

---

### Priority 2: EC ↔ lfunc Join Key
**Impact:** Unblocks BSD Phase 2, spectral analysis, and all EC↔L-function queries  
**Effort:** Investigation + materialized view, ~2 hours  
**Source:** Mnemosyne (P-001), Harmonia (BSD parity test took 1238s)  

Three strategies to try in order:
1. `trace_hash` matching (both tables have it — fast integer join)
2. `origin LIKE 'EllipticCurve/Q/%'` in lfunc (direct EC paths if they exist)
3. Parse ModularForm origin: level = conductor, weight = 2 → match by conductor + isogeny class

Once resolved, build a materialized view `bsd_joined` with EC algebraic invariants + L-function leading_term/zeros.

---

### Priority 3: DuckDB → Postgres Migration
**Impact:** Unblocks 10+ open problems (Harmonia), gives all agents access to zeros data  
**Effort:** ~3 hours (schema + data + validation)  
**Source:** Agora (MIGRATION_PLAN.md), Harmonia (zeros access is #1 bottleneck)  

#### New Schemas Needed in prometheus_fire

**`zeros` schema** (323K rows from DuckDB):
```sql
CREATE SCHEMA zeros;

-- 121K rows: per-object zeros with root number
CREATE TABLE zeros.object_zeros (
    object_id      BIGINT PRIMARY KEY,
    zeros_vector   DOUBLE PRECISION[],
    root_number    DOUBLE PRECISION,
    analytic_rank  SMALLINT
);

-- 185K rows: L-function zeros by conductor
CREATE TABLE zeros.dirichlet_zeros (
    id             BIGSERIAL PRIMARY KEY,
    object_id      BIGINT,
    conductor      BIGINT,
    degree         SMALLINT,
    zeros_vector   DOUBLE PRECISION[],
    n_zeros_stored SMALLINT,
    motivic_weight SMALLINT
);
CREATE INDEX idx_dirichlet_conductor ON zeros.dirichlet_zeros(conductor);

-- 17K rows: extended zero data
CREATE TABLE zeros.object_zeros_ext (
    object_id      BIGINT PRIMARY KEY
    -- columns TBD from DuckDB schema inspection
);
```

**`analysis` schema** (119K rows):
```sql
CREATE TABLE analysis.disagreement_atlas (
    object_id        BIGINT PRIMARY KEY,
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
    disagreement_type TEXT
);
```

**`noesis` schema** (52K rows, 18 tables from noesis_v2.duckdb):
- Bulk copy all tables. Preserve structure as-is (research state).

#### What Gets Dropped (Not Migrated)
| DuckDB Table | Rows | Reason |
|-------------|------|--------|
| elliptic_curves | 31K | Redundant with lmfdb.ec_curvedata (3.8M) |
| modular_forms | 102K | Redundant with lmfdb.mf_newforms (1.1M) |
| l_functions | 0 | Empty |
| failure_log | 0 | Empty |

#### What Goes to Redis Instead of Postgres
| DuckDB Table | Rows | Redis Structure | Memory |
|-------------|------|----------------|--------|
| graph_edges | 396K | Sets: `graph:neighbors:{id}` | ~20 MB |
| landscape | 119K | Hash + Sorted Set by curvature | ~12 MB |
| known_bridges | 17K | Hash + Set indexes (already in Postgres too) | ~3 MB |
| hypothesis_queue | 100 | Sorted Set: `hypothesis:queue` | <1 MB |

Total Redis memory: ~40 MB. Well within 512 MB limit.

---

### Priority 4: Signal Registry (New)
**Impact:** Centralizes Harmonia's specimen tracking, battery results, kill records  
**Effort:** Schema design + initial population, ~2 hours  
**Source:** Harmonia (needs battery re-audit capability)  

```sql
CREATE SCHEMA signals;

CREATE TABLE signals.specimens (
    specimen_id  BIGSERIAL PRIMARY KEY,
    claim        TEXT NOT NULL,
    status       TEXT NOT NULL,  -- 'ALIVE', 'KILLED', 'MARGINAL'
    interest     DOUBLE PRECISION,
    kill_test    TEXT,
    domain_a     TEXT,
    domain_b     TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    killed_at    TIMESTAMPTZ
);

CREATE TABLE signals.battery_results (
    id           BIGSERIAL PRIMARY KEY,
    specimen_id  BIGINT REFERENCES signals.specimens,
    test_name    TEXT NOT NULL,
    result       TEXT NOT NULL,  -- 'passed', 'failed', 'not_run'
    z_score      DOUBLE PRECISION,
    p_value      DOUBLE PRECISION,
    detail       JSONB,
    run_at       TIMESTAMPTZ DEFAULT now()
);
```

**Redis companion** (Harmonia's proposal):
```
specimen:{id} → hash {claim, status, interest, kill_test, tests_passed/failed/total}
specimen:{id}:battery → hash {F1: "passed|z=-4.28|p=0.0000", F2: "not_run", ...}
tensor:bond:{domain_a}:{domain_b} → hash {raw_rank, validated_rank, sv_0..n, energy_0..n, scorer, computed_at}
```

---

### Priority 5: Redis Tensor/Battery Cache
**Impact:** Eliminates redundant TT-Cross computation (5-30s per pair), enables instant battery re-audits  
**Effort:** ~2 hours implementation  
**Source:** Harmonia (bottleneck #2: null model computation, #3: battery re-audits)  

Cache structures from Harmonia's recommendation:
- `tensor:bond:{domain_a}:{domain_b}` — bond dimensions, singular values, energy fractions
- `feature:dist:{domain}:{feature}` — feature distribution stats for permutation nulls
- `specimen:{id}:battery` — per-specimen battery results for fast re-audit

---

### Priority 6: nf_fields → Local Postgres
**Impact:** Unblocks Lehmer, Brumer-Stark, Leopoldt tests  
**Effort:** Large pull from devmirror (22M rows), several hours  
**Source:** Harmonia (needed for 3+ open problems)  

The LMFDB devmirror has `nf_fields` with 22,178,569 rows. We don't have it locally. Pull via:
```bash
psql -h devmirror.lmfdb.xyz -U lmfdb -d lmfdb -c "\copy nf_fields TO 'nf_fields.csv' CSV HEADER"
```
Then load into local lmfdb database.

---

### Priority 7: Ingest Remaining Cartography Data
**Impact:** Fills empty prometheus_sci tables, enables new domain analysis  
**Effort:** ~1 hour per batch  
**Source:** Mnemosyne (P-006)  

**Batch A — Schema exists, just load:**
| Dataset | Target | Rows |
|---------|--------|------|
| CODATA constants | physics.codata | ~300 |
| Fungrim formulas | analysis.fungrim | ~1,000 |
| Small groups | algebra.groups (append) | ~500 |

**Batch B — Needs new tables:**
| Dataset | Rows | Notes |
|---------|------|-------|
| OEIS (full 394K) | 375K | Currently 50K partial load |
| Maass forms | 15K | New analysis table |
| Number fields | 9K | New algebra table |
| Exoplanets | 6,158 | New physics table |

---

### Priority 8: Cleanup
**Source:** Harmonia  

| Action | Size Freed | Risk |
|--------|-----------|------|
| Archive `Prometheus_data_backup/` to external | 36 GB | Low — it's a duplicate |
| Delete pickle caches after zeros migration | 1.8 GB | Low — regenerable |
| Delete DuckDB after full migration | 1.2 GB | Medium — verify all consumers first |
| Consolidate 66K JSONL logs to monthly | 11 GB | Low — aggregate, don't delete |
| Archive portrait/plot JSONs | ~12 GB | Low — visual data, not used for research |

---

## Materialized Views (After Join Key Resolved)

**`lfunc_typed`** — lfunc with proper types for fast analysis:
```sql
CREATE MATERIALIZED VIEW lfunc_typed AS
SELECT
    label,
    origin,
    conductor::numeric AS conductor,
    degree::int AS degree,
    motivic_weight::int AS motivic_weight,
    order_of_vanishing::int AS analytic_rank,
    self_dual::boolean AS self_dual,
    symmetry_type,
    leading_term::double precision AS leading_term,
    root_number,
    positive_zeros
FROM lfunc_lfunctions;
```

**`bsd_joined`** — EC algebraic invariants + L-function data:
```sql
-- Depends on P-001 join key resolution
CREATE MATERIALIZED VIEW bsd_joined AS
SELECT
    ec.lmfdb_label, ec.conductor::bigint, ec.rank::int, ec.analytic_rank::int,
    ec.regulator::double precision, ec.sha::int, ec.torsion::int,
    ec.manin_constant::int, ec.faltings_height::double precision,
    ec.bad_primes, ec.isogeny_degrees,
    lf.leading_term::double precision, lf.positive_zeros, lf.root_number
FROM ec_curvedata ec
JOIN lfunc_lfunctions lf ON <join_condition_tbd>;
```

---

## Known Data Quality Issues

1. **LMFDB all-text columns** — Every column is TEXT. Casts required. Conductor index mitigates for one column.
2. **Sha circularity at rank ≥ 2** — Computed assuming BSD. Cannot test BSD independently.
3. **Missing EC ingredients** — Omega, Tamagawa product, root_number not in ec_curvedata.
4. **LMFDB selection effects** — High-conductor ECs biased toward prime conductors. Stratify by bad_primes.
5. **abc_quality ≈ szpiro_ratio** — Both columns appear identical. Verify before using both.

---

## Constraints (Non-Negotiable)

From the database architecture doc — all agents must respect:

1. **Harmonia scoring is sacrosanct.** No changes that alter calibration results.
2. **File fallback at every phase.** If Postgres/Redis is down, loaders fall back to local files.
3. **Credentials never in code.** Config file or env vars only.
4. **DomainIndex interface unchanged.** `load_domains()` returns same objects regardless of backend.
5. **DuckDB stays as archive** until ALL consumers verified on Postgres.
6. **Data integrity above all.** A wrong number in the database is worse than no number.

---

## Summary: What Blocks Science

| Blocker | What It Blocks | Fix |
|---------|---------------|-----|
| No lfunc origin index | 90s EC↔lfunc joins | Priority 1 (1 command) |
| No EC↔lfunc join key | BSD Phase 2, spectral analysis | Priority 2 (investigation) |
| Zeros in DuckDB only | 10+ open problems, GUE analysis | Priority 3 (migration) |
| No signal registry | Battery re-audits, specimen tracking | Priority 4 (new schema) |
| No nf_fields locally | Lehmer, Brumer-Stark, Leopoldt | Priority 6 (large pull) |
