# Data Expansion Plan — Incremental Domain Growth

## Principle

Harmonia's `domain_index.py` loaders are the single source of truth for data access.
Ergon gets data by calling Harmonia's `load_domains()`. Changes flow:

```
Share CSVs / Postgres / DuckDB
    → Harmonia loaders (domain_index.py)
        → DomainIndex objects
            → Ergon tensor_builder
```

Code goes through GitHub. Big data lives on the share (`C:\prometheus_share`).
Both machines see the same domains through the same code path.

## Phase 1: CSV Fallback for Postgres Loaders (safe, no behavior change)

**Goal:** `load_ec_rich` and `load_artin` currently require live Postgres on M1.
Add fallback to `C:\prometheus_share\lmfdb_local\` CSVs so they work when M1
is offline. Same schema, same normalization, same output.

**Files changed:** `harmonia/src/domain_index.py` only (two functions).

**Risk:** Zero — fallback only activates when Postgres is unreachable. Existing
behavior unchanged when M1 is online.

## Phase 2: Upgrade DuckDB Domains with Share Data

**Goal:** Replace charon's small extracts (10K EC, 10K MF) with the full LMFDB
exports on the share (3.8M EC, 1.1M MF, 66K G2).

Options:
  a) Import CSVs into charon.duckdb (preserves existing loader code)
  b) Add CSV-reading path to existing loaders (try DuckDB first, fall back to CSV)

Option (b) is safer — doesn't modify the DuckDB file, and loaders auto-upgrade
when the share is available.

**Domain-specific notes:**

| Domain | Current | Share | Upgrade |
|--------|---------|-------|---------|
| elliptic_curves | 10K (charon) | 3.8M (ec_curvedata.csv) | Many more columns available (regulator, sha, faltings_height, etc.) |
| modular_forms | 10K (charon) | 1.1M (mf_newforms.csv) | Hecke orbit data, analytic rank, trace hash |
| genus2_curves | 10K (cartography JSON) | 66K (g2c_curves.csv) | Full LMFDB schema |
| artin_reps | None in Ergon | 798K (artin_reps.csv) | New domain — dimension, conductor, Galois type |

**Risk:** Medium — more data changes feature distributions. Battery thresholds
calibrated on 10K objects may need re-tuning on 3.8M. Run calibration check
(7 known theorems) after each upgrade.

## Phase 3: Wire Ergon to Harmonia's Loaders

**Goal:** Replace Ergon's `tensor_builder.py` hand-rolled loading code with
calls to `harmonia.src.domain_index.load_domains()`.

**What changes:**
- `tensor_builder.py` becomes thin: call `load_domains()`, convert torch→numpy,
  build the feature index
- `ACTIVE_DOMAINS` and `ACTIVE_FEATURES` auto-generated from what loads successfully
- `gene_schema.py` vocabulary expanded or dynamically built from loaded domains

**Risk:** Medium — Ergon's feature extraction (computed features like log_conductor,
ap_kurtosis, n_bad_primes) doesn't exist in Harmonia's loaders. Need to either:
  a) Add computed features to Harmonia's loaders, or
  b) Keep a small computed-feature layer in Ergon on top of Harmonia's raw features

## Phase 4: New Domains

Add domains that exist on the share but aren't in any loader yet:
- `cartography/physics/` (660 MB) — superconductors, materials
- `cartography/maass/` (335 MB) — Maass forms with full coefficient data
- `cartography/mathlib/` — Lean proof library metadata

Each new domain needs:
1. A loader function in `domain_index.py`
2. An entry in `DOMAIN_LOADERS`
3. NO phoneme mapping (see phoneme_warning.md)
4. Validation that it loads correctly and features are finite/normalizable

## Constraints

- **Do not extend DOMAIN_PHONEME_MAP** for new domains. The phoneme framework
  is an unvalidated construction. New domains should be accessible via the
  `distributional` scorer, not phoneme-based scoring.
- **Calibration check after each phase.** Run the 7 known theorems at the
  new data scale. If accuracy drops, the upgrade introduced a regression.
- **Feature admission.** New features from richer CSVs should pass the 5-gate
  admission test before being treated as valid coordinates. Raw inclusion is fine
  for Ergon's evolutionary search, but survivors promoted to Harmonia need validated
  features.
