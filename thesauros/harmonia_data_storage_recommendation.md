# Data Storage Recommendation — Harmonia
## For the Prometheus data-layer-architecture migration
## 2026-04-16

---

## Current State: 277 GB across 7 storage backends

| Backend | Size | Files | Used by |
|---------|------|-------|---------|
| JSON flat files | ~170 GB | 29K+ | Cartography, LMFDB dump, all domains |
| JSONL logs | ~11 GB | 66K+ | Hephaestus, Ergon, cycle logs |
| DuckDB | 1.2 GB | 2 | Charon (spectral survey, zeros) |
| SQLite | 4.2 MB | 7 | Misc small DBs |
| Pickle | 1.8 GB | 2 | Dirichlet zeros cache, Artin cache |
| CSV/TSV | 130 MB | 76 | QM9, superconductors, exoplanets |
| PyTorch/NumPy | 3.1 GB | 100+ | Ignis checkpoints, isogeny graphs, concept vectors |
| Postgres (remote) | 341 GB+ | 5 tables | LMFDB mirror (192.168.1.176) |
| Redis (remote) | ~10 MB | streams+hashes | Agora communication |

---

## Recommendation: Three-tier architecture

### Tier 1: Postgres — The Source of Truth
**What goes here:** Anything that gets queried, joined, filtered, or aggregated.

| Data | Current location | Size | Priority |
|------|-----------------|------|----------|
| EC curves | Postgres (lmfdb) | 3.8M rows | Already there |
| L-functions | Postgres (lmfdb) | 24.4M rows, 341GB | Already there. NEEDS origin index. |
| Artin reps | Postgres (lmfdb) | 793K rows | Already there |
| Modular forms | Postgres (lmfdb) | 1.1M rows | Already there |
| Genus-2 curves | Postgres (lmfdb) | 66K rows | Already there |
| Number fields | devmirror only | 22M rows | **MIGRATE to local Postgres** — needed for Lehmer, Brumer-Stark |
| Knots | prometheus_sci | 12.9K rows | Already there |
| Materials | prometheus_sci | 10K rows | Already there |
| Space groups | prometheus_sci | 230 rows | Already there |
| Superconductors | prometheus_sci | ? rows | Already there |
| OEIS sequences | prometheus_sci | 50K+ rows | Already there. Full 394K from flat files pending |
| Dirichlet zeros | DuckDB (charon) | 184K rows | **MIGRATE** — blocks 10+ open problems |
| Object zeros | DuckDB (charon) | 121K rows | **MIGRATE** with Dirichlet |
| Modular forms (DuckDB) | DuckDB (charon) | 102K rows | **MIGRATE** |
| Elliptic curves (DuckDB) | DuckDB (charon) | 31K rows | **MIGRATE** (subset of Postgres EC) |
| Signal registry | NEW | 0 rows | **CREATE** — signals.specimens, signals.battery_results |
| Agora messages | prometheus_fire | growing | Already persisted via agora client |
| Kill taxonomy | prometheus_fire | planned | **CREATE** — from shadow archive data |

**Why Postgres:** Joins are the bottleneck. The BSD parity test took 1238s because lfunc lacks an origin index. The Lehmer scan worked only because devmirror has nf_fields. Every cross-domain question requires joining datasets. Postgres handles this; flat files and DuckDB don't.

**Critical index:** `CREATE INDEX idx_lfunc_origin ON lfunc_lfunctions(origin)` would cut EC-lfunc joins from ~90s to ~1s. This is the single highest-leverage infrastructure change.

### Tier 2: Redis — Hot State and Communication
**What goes here:** Agent state, real-time coordination, cached computation results, tensor slices for fast lookup.

| Data | Current location | Proposed use |
|------|-----------------|-------------|
| Agora streams | Redis (already) | Keep — communication backbone |
| Agent state/heartbeat | Redis (already) | Keep |
| Hypothesis alive/killed sets | Redis (already) | Keep |
| Leaderboards | Redis (already) | Keep |
| **Tensor bond cache** | Not cached | **NEW** — cache TT-Cross results as Redis hashes |
| **Battery profile cache** | Not cached | **NEW** — cache specimen battery results for fast re-audit |
| **Conductor-binned zero stats** | Not cached | **NEW** — pre-aggregate zero statistics by conductor range |
| **Feature distribution cache** | Not cached | **NEW** — cache domain feature distributions for permutation nulls |

**Why Redis for these:** TT-Cross builds take 5-30s per pair. Caching bond dimensions, singular values, and component scores in Redis means any agent can query "what's the NF-EC bond rank?" instantly. Same for battery profiles — when we add F40, we want to re-audit all specimens without recomputing the other 39 tests.

**Redis data model for tensor cache:**
```
tensor:bond:{domain_a}:{domain_b} → hash {
  raw_rank: 4
  validated_rank: 1
  sv_0: 31.62
  sv_1: 9.49
  energy_0: 0.874
  energy_1: 0.079
  scorer: cosine
  subsample: 1000
  computed_at: 2026-04-15T...
}
```

**Redis data model for specimen cache:**
```
specimen:{id} → hash {
  claim: "..."
  status: KILLED
  interest: 0.3
  kill_test: conductor_conditional
  tests_passed: 1
  tests_failed: 1
  tests_total: 39
}
specimen:{id}:battery → hash {
  F1_permutation: "passed|z=-4.28|p=0.0000"
  F2_subset: "not_run"
  ...
}
```

### Tier 3: Flat Files — Reference Data and Archives
**What stays as files:** Large static datasets that are loaded once, not queried interactively.

| Data | Size | Reason to keep as files |
|------|------|------------------------|
| LMFDB dump JSONs | 130 GB | Reference archive. Already in Postgres for querying. Files are backup. |
| Ignis checkpoints (.pt) | 3 GB | PyTorch model weights. Not queryable data. |
| OEIS stripped.txt | 77 MB | Full OEIS text dump. Load to Postgres, keep file as backup. |
| Genus-2/3 raw text | 150 MB | Raw curve data. Parse → Postgres, keep as backup. |
| Convergence/sleeper data | 2.1 GB | Fingerprint JSONs. Consider Postgres if search needed. |
| Isogeny graphs (.npz) | 662 MB | Sparse matrix graphs. Keep as NumPy files — Postgres isn't great for sparse matrices. |
| Concept vectors (.npy) | 20 MB | Dense vectors. Redis or flat file, not Postgres. |

---

## What to DELETE or ARCHIVE

| Data | Size | Action |
|------|------|--------|
| Prometheus_data_backup/ | 36 GB | **ARCHIVE** to external. It's a full duplicate. |
| Pickle caches | 1.8 GB | **DELETE after Postgres migration.** dirichlet_raw_cache.pkl is redundant once zeros are in Postgres. |
| DuckDB files | 1.2 GB | **DELETE after Postgres migration.** All data migrated. |
| SQLite utility DBs | 4.2 MB | **KEEP** — too small to matter, some agents depend on them. |
| 66K JSONL log files | 11 GB | **CONSOLIDATE** — daily logs should aggregate to monthly. Or load to Postgres logging table. |
| Portrait/plot JSONs | ~12 GB | **ARCHIVE** — visual data (ec_nfportraits, maass_portraits, g2c_plots). Not used for research. |

---

## Migration Priority Order

1. **DuckDB → Postgres** (1.2 GB, blocks 10+ open problems)
   - Dirichlet zeros, object zeros, modular forms, landscape, disagreement atlas
   - Mnemosyne has this on the task list already
   
2. **Create lfunc origin index** (0 new data, massive speedup)
   - Needs write access to lmfdb database
   - Turns 90s queries into 1s queries
   
3. **nf_fields → local Postgres** (pull from devmirror)
   - 22M rows with polynomial coefficients
   - Needed for Lehmer, Brumer-Stark, Leopoldt tests
   
4. **Signal registry schema** (new tables in prometheus_fire)
   - signals.specimens, signals.battery_results, signals.relationships
   
5. **Redis tensor/battery cache** (new Redis data structures)
   - Cache TT-Cross results, battery profiles, feature distributions
   
6. **OEIS full load** (394K sequences → Postgres)
   - Currently 50K in prometheus_sci, 394K in flat files
   
7. **Consolidate JSONL logs** (11 GB → Postgres or monthly archives)

---

## What I Use and What I Need

As the falsification engine, my bottlenecks are:

1. **Joins across datasets** — BSD parity needed EC × lfunc. Lehmer needed nf_fields. Every cross-domain test needs joins. Postgres solves this, flat files don't.

2. **Null model computation** — Permutation nulls need to sample and reshuffle thousands of times. Feature distributions cached in Redis would eliminate redundant computation.

3. **Battery re-audits** — When I add F40, I need to re-run it against all specimens. Battery profiles cached in Redis/Postgres make this instant instead of recomputing from scratch.

4. **Zero data access** — The spectral tail test, pair correlation, GUE deviation, and 8 CPNT problems ALL need L-function zeros. DuckDB → Postgres is the single most impactful migration for the science.

5. **Tensor state persistence** — TT-Cross builds are expensive. Caching bond dimensions and singular vectors means any agent can query tensor structure without rebuilding.

---

## Summary

```
Postgres = truth (queryable, joinable, indexed)
Redis    = speed (cached state, real-time coordination, hot lookups)  
Files    = archive (static reference, model weights, backups)
```

Phase out DuckDB entirely after migration. Phase out pickle caches. Keep flat files only for static reference and backup. Everything queryable goes to Postgres. Everything cached goes to Redis.
