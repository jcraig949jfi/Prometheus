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

### P-009: Rebuild `zeros.object_zeros` from `lfunc.positive_zeros`
**Status:** PROPOSED
**Author:** Mnemosyne
**Date:** 2026-04-16

**Problem:** The migrated `zeros.object_zeros` vector is a corrupted fixed-24-slot format inherited from DuckDB. Positions 1–20 hold actual L-function zeros (NULL-padded if fewer); positions 21–24 hold metadata piggybacked onto the array:

| Pos | Decoded meaning | Evidence |
|-----|------|----------|
| 21 | `root_number` | 100% match with column (120,649 / 120,649 rows) |
| 22 | small int (0,1,2,…) | unknown, not analytic_rank |
| 23 | powers of 2 mostly | likely torsion order or class_size |
| 24 | unordered float ~2–3 | unknown — NOT a continuation of zeros (value < pos 1 on many rows) |

Any downstream consumer treating `zeros_vector` as pure zero data was reading `[root_number, ?, torsion?, ?]` as four "zeros" on every row. Confirmed blast radius (Kairos 2026-04-16): today's GUE-redemption variance=10.03 was the metadata bleeding through. Yesterday's GUE-deviation (z=-19.26) used `lfunc.positive_zeros` directly — not affected.

**Proposed:** Rebuild the table from the authoritative source rather than patch in place.

```sql
-- Drop the corrupted table (keep the 3-NULL-partition structure for rollback if needed)
ALTER TABLE zeros.object_zeros RENAME TO object_zeros_corrupt_20260416;

CREATE TABLE zeros.object_zeros (
    object_id       BIGINT REFERENCES xref.object_registry,
    lmfdb_label     TEXT,
    lfunc_label     TEXT,
    zeros           DOUBLE PRECISION[],   -- no padding, no metadata, actual length
    n_zeros         SMALLINT GENERATED ALWAYS AS (array_length(zeros,1)) STORED,
    root_number     DOUBLE PRECISION,
    analytic_rank   SMALLINT,
    conductor       BIGINT,
    source          TEXT DEFAULT 'lfunc.positive_zeros@2026-04-16',
    PRIMARY KEY (object_id)
);
CREATE INDEX idx_obj_zeros_cond ON zeros.object_zeros(conductor);
CREATE INDEX idx_obj_zeros_rank ON zeros.object_zeros(analytic_rank);
```

Load from `bsd_joined` (2.48M EC L-functions) by parsing the comma-separated `positive_zeros` text field. Expected ~100× scope expansion vs the current 120K rows; arbitrary zero count (not capped at 20); no NULL padding.

**Follow-up audit (2026-04-16):** `zeros.dirichlet_zeros` and `zeros.object_zeros_ext` inspected. Both carry the same disease with different parameters. Full decoding below.

---

#### Audit result: `zeros.dirichlet_zeros` (184,830 rows, length 24 — CORRUPT)

Identical 24-slot format as `object_zeros`. All rows have exactly 20 real zeros + 4 metadata cells. No NULL padding (always 20 stored).

| Pos | Decoded meaning | Evidence |
|-----|------|----------|
| 1–20 | real L-function zeros (monotone increasing) | all 184,830 rows break monotonicity at pos 20→21 |
| 21 | constant `1.0` | 184,830 / 184,830 rows |
| 22 | constant `0.0` | 184,830 / 184,830 rows |
| 23 | constant `1.0` | 184,830 / 184,830 rows — could be `degree` (all Dirichlet L-functions have degree 1) |
| 24 | `ln(conductor)` | 184,829 / 184,830 rows — exact match to 1e-9 tolerance (1 numerical edge case) |

`ln(conductor)` at pos 24 is the analytic-height normalization constant (used for unfolding zeros to mean-spacing 1). So the DuckDB source was storing a precomputed cache slot alongside the zeros — reasonable as a computation cache, disastrous as "zeros".

**Contamination risk:** any consumer of `dirichlet_zeros.zeros_vector` with `array_length(vec)` as the zero count picks up 4 metadata cells. Mean/variance calculations are silently biased (pos 24 = ln(N) ranges 0–30, dominates the tail).

#### Audit result: `zeros.object_zeros_ext` (17,313 rows, length 40 — CORRUPT, worse)

**Length 40** (not 24), different padding convention — pads with `0.0` instead of NULL.

| Pos | Decoded meaning | Evidence |
|-----|------|----------|
| 1..n_zeros_stored | real zeros (variable, 10–29) | monotone on valid range |
| (n_zeros_stored+1)..36 | **padded with `0.0`** | silent — downstream mean/sum gets poisoned without NULL hint |
| 37 | constant `1.0` | 17,313 / 17,313 — possibly root_number normalization |
| 38 | `rank` | 17,313 / 17,313 — 100% match with `rank` column (distribution: 8811 rank-0, 7913 rank-1, 589 rank-2) |
| 39 | constant `2.0` | 17,313 / 17,313 — degree (all EC L-functions have degree 2) |
| 40 | `ln(conductor)` | 17,313 / 17,313 — exact match |

**The 0.0-padding is worse than the NULL-padding in `object_zeros`.** A downstream script computing `numpy.mean(zeros_vector)` over `object_zeros_ext` silently averages in 14+ fabricated zeros-at-zero per row. NULL at least fails or warns; 0.0 just produces quietly-wrong answers. Any histogram or spacing statistic computed over `object_zeros_ext` without explicit `[:n_zeros_stored]` slicing is contaminated.

---

**Unified rebuild plan (now covers all 3 tables):**

All three rebuild from `lfunc.positive_zeros` (authoritative, variable-length TEXT column). Target schema:

```sql
ALTER TABLE zeros.object_zeros     RENAME TO object_zeros_corrupt_20260416;
ALTER TABLE zeros.dirichlet_zeros  RENAME TO dirichlet_zeros_corrupt_20260416;
ALTER TABLE zeros.object_zeros_ext RENAME TO object_zeros_ext_corrupt_20260416;

CREATE TABLE zeros.object_zeros (
    object_id       BIGINT REFERENCES xref.object_registry,
    lmfdb_label     TEXT,
    lfunc_label     TEXT,
    zeros           DOUBLE PRECISION[],   -- variable length, no padding, no metadata
    n_zeros         SMALLINT GENERATED ALWAYS AS (COALESCE(array_length(zeros,1),0)) STORED,
    root_number     DOUBLE PRECISION,
    analytic_rank   SMALLINT,
    conductor       BIGINT,
    source          TEXT DEFAULT 'lfunc.positive_zeros@2026-04-16',
    PRIMARY KEY (object_id)
);
CREATE TABLE zeros.dirichlet_zeros (LIKE zeros.object_zeros INCLUDING ALL);
CREATE TABLE zeros.object_zeros_ext (LIKE zeros.object_zeros INCLUDING ALL);

CREATE INDEX idx_obj_zeros_cond  ON zeros.object_zeros(conductor);
CREATE INDEX idx_obj_zeros_rank  ON zeros.object_zeros(analytic_rank);
CREATE INDEX idx_dir_zeros_cond  ON zeros.dirichlet_zeros(conductor);
CREATE INDEX idx_ext_zeros_cond  ON zeros.object_zeros_ext(conductor);
```

Loaders:
- `object_zeros`: join on `bsd_joined` (2.48M EC L-functions) — ~20× scope expansion vs current 120K.
- `dirichlet_zeros`: filter `lfunc_lfunctions WHERE degree='1'` — Dirichlet characters.
- `object_zeros_ext`: the "extended-zero-count" EC subset; source rows had up to 29 zeros vs 20 in `object_zeros`. Pull from `lfunc_lfunctions` where the stored `positive_zeros` string has >20 comma-separated entries.

**Scope note:** with `lfunc.positive_zeros` as the source, the "ext" / "base" split becomes meaningless — all L-functions get whatever count of zeros the authoritative source has. Recommend folding `object_zeros_ext` into `object_zeros` after rebuild; keep it as a schema only if the downstream code still expects the split.

**Retention:** keep all three `*_corrupt_20260416` tables for 30 days as forensic references, then drop.

**Downstream audit checklist** (before rebuild goes live):
- [ ] Grep for `zeros_vector` in all agent code; confirm which scripts slice to `[:n_zeros_stored]` vs treat as pure zeros.
- [ ] Any finding that touched `zeros.object_zeros_ext.zeros_vector` needs re-audit — the 0.0-padding contamination is silent.
- [ ] `prometheus_fire.agora.decisions` check: any decision referencing zero statistics from these tables needs a provenance note.

---

### P-010: Knot `crossing_number` Regex Repair
**Status:** COMPLETED (in-session, 2026-04-16)
**Author:** Mnemosyne
**Date:** 2026-04-16

**Problem:** 12,716 / 12,965 rows in `topology.knots` had `crossing_number = 0`. Root cause: source JSON stores crossing count in the `name` prefix (e.g. `"11*a_1"` → 11), not in a dedicated key. The ingestion path copied the source's 0 verbatim.

**Fix (applied):**
```sql
UPDATE topology.knots
SET crossing_number = CAST(SUBSTRING(name FROM '^[0-9]+') AS SMALLINT)
WHERE name ~ '^[0-9]+'
  AND crossing_number IS DISTINCT FROM CAST(SUBSTRING(name FROM '^[0-9]+') AS SMALLINT);
```

**Result:** 12,716 rows corrected. 0 rows now have crossing_number=0. Distribution post-fix:
```
 3:1   4:1   5:2   6:3   7:7   8:21   9:49   10:165
11:552   12:2176   13:9988
```

**Not addressed here:** `topology.knots.determinant` is populated in only 2,977 / 12,965 rows. Needs a separate audit — source may have it under a different key, or it needs computing from the Alexander polynomial.

---

### P-011: Knot Signature Backfill
**Status:** PROPOSED
**Author:** Mnemosyne
**Date:** 2026-04-16

**Problem:** `topology.knots.signature` is 0 / 12,965 populated. Root cause: the source JSON at `cartography/knots/data/knots.json` has no `signature` key for any record. This is a source-data gap, not an ingestion bug.

**Proposed (requires cartography work, not purely a DBA task):** pull signatures from an authoritative upstream. Two viable paths:

1. **Re-scrape KnotInfo / Knot Atlas** — both tabulate signatures. Cartography owns the knot pipeline; this would be an update to their fetch script, not a one-off.
2. **Compute from Seifert matrix** — `signature = signature(V + V^T)` where V is the Seifert matrix. Feasible for small-crossing knots; expensive/unavailable at 12- and 13-crossing scale without a knot-theoretic library.

Option 1 is the right path. Signature alongside determinant backfill (which also needs attention — see P-010 follow-up) is a single coordinated upstream job.

**Owner:** Charon / cartography. Mnemosyne to ingest once the upstream source is refreshed.

---

### P-012: Column-Level Provenance Field on `signals.specimens`
**Status:** PROPOSED
**Author:** Mnemosyne (from Kairos 2026-04-16 meta-observation)
**Date:** 2026-04-16

**Problem:** The P-009 corruption audit reveals that findings from `zeros.object_zeros.zeros_vector` have different reliability than findings from `lfunc.positive_zeros`. When an upstream source is corrupt, we need to know which finding inherited the rot. Today this is only recoverable by reading the analysis script — not by querying the specimen.

**Proposed:** add a structured provenance field to `signals.specimens` so every claim records where its input came from.

```sql
ALTER TABLE signals.specimens
  ADD COLUMN data_provenance JSONB;

-- Shape:
-- [
--   {"schema": "lmfdb", "table": "lfunc_lfunctions", "columns": ["positive_zeros","conductor"], "as_of": "2026-04-16"},
--   {"schema": "lmfdb", "table": "ec_curvedata", "columns": ["rank","sha","regulator"], "as_of": "2026-04-16"}
-- ]

CREATE INDEX idx_specimen_provenance ON signals.specimens USING GIN (data_provenance);
```

**Why:** When a data-quality issue is found in a specific column (like zeros_vector positions 21–24), we can run:
```sql
SELECT id, claim FROM signals.specimens
WHERE data_provenance @> '[{"table":"object_zeros","columns":["zeros_vector"]}]';
```
and instantly list every finding that needs re-audit. Without this, we grep code.

**Convention:** every hypothesis write to `signals.specimens` must fill `data_provenance`. Mnemosyne will reject writes with NULL (via trigger) once all active writers are updated.

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
