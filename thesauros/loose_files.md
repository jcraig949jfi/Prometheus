# Loose Files — Data Not Yet in Any Database

Files in cartography/ and elsewhere that are source data but not yet loaded into Postgres or DuckDB.

## Ready to Ingest (schema exists, just needs loading)

| Domain | File | Size | Rows (est) | Target Table | Origin |
|--------|------|------|------------|-------------|--------|
| Physics | cartography/physics/data/codata/constants.json | 58 KB | ~300 | physics.codata | NIST CODATA 2022 |
| Analysis | cartography/fungrim/data/fungrim_formulas.json | 1.6 MB | ~1,000 | analysis.fungrim | fungrim.org |
| Algebra | cartography/atlas/data/small_groups.json | 1.1 MB | ~500 | algebra.groups (append) | GAP Small Groups Library |

## Needs Schema Design

### Large Datasets

| Domain | Path | Size | Rows (est) | Origin |
|--------|------|------|------------|--------|
| Analysis | cartography/oeis/data/ | 390 MB | ~375K sequences | oeis.org bulk download |
| Analysis | cartography/maass/data/ | 676 MB | ~15K forms | LMFDB Maass forms |
| Topology | cartography/genus2/data/ (9 files) | 1.1 GB | ~66K curves | LMFDB genus-2 + Siegel modular forms |
| Algebra | cartography/isogenies/data/graphs/ | 662 MB | 3,000+ primes | Computed isogeny graphs |
| Biology | cartography/metabolism/data/ | 256 MB | ~110 models | BiGG Models database |
| Physics | cartography/physics/data/basis_sets/ | 292 MB | — | Basis Set Exchange |
| Formal math | cartography/mathlib/data/ | 138 MB | — | Lean Mathlib4 |
| Formal math | cartography/metamath/data/ | 49 MB | — | Metamath set.mm |

### Small Datasets

| Domain | Path | Size | Rows (est) | Origin |
|--------|------|------|------------|--------|
| Algebra | cartography/number_fields/data/number_fields.json | 1.8 MB | ~9K | LMFDB number fields |
| Algebra | cartography/local_fields/data/ | 4.5 MB | — | LMFDB local fields |
| Algebra | cartography/lattices/data/lattices_full.json | 6.8 MB | ~1,000 | Lattice database |
| Combinatorics | cartography/findstat/data/findstat_enriched.json | ~200 KB | — | FindStat.org |
| Combinatorics | cartography/antedb/data/antedb_index.json | 3.2 MB | — | Antedb (algebra experiments) |
| Physics | cartography/physics/data/nist_asd/ | varies | 120+ elements | NIST Atomic Spectra |
| Physics | cartography/physics/data/exoplanets/confirmed_exoplanets.csv | 700 KB | 6,158 | NASA Exoplanet Archive |
| Physics | cartography/physics/data/gravitational_waves/gwtc_params.csv | 13 KB | 219 | LIGO/Virgo/KAGRA |
| Physics | cartography/physics/data/superconductors/ | varies | — | SuperCon + 3DSC databases |
| Physics | cartography/physics/data/chaos/ | 6.8 MB | — | Computed (logistic map, Feigenbaum) |
| Physics | cartography/physics/data/earthquakes/*.csv | 1.8 MB | — | USGS 1970-1974 |
| Physics | cartography/physics/data/snappy_manifolds.csv | — | — | SnapPy 3-manifolds |
| Finance | cartography/finance/data/ff*.json | 12 MB | — | Kenneth French data library + FRED |
| Topology | cartography/topology/data/ | 28 MB | — | Various topological datasets |

## Explicitly NOT Source Data (Do Not Ingest)

| Path | Size | What It Is |
|------|------|-----------|
| cartography/convergence/data/ | ~121 GB | Analytical results, battery runs, exploration output |
| harmonia/results/ | 3 MB | Falsification test outputs |
| ergon/results/ | 65 MB | MAP-Elites checkpoints, shadow maps |
| forge/ | 95 MB | Hypothesis generation output |
| agents/hephaestus/ | 235 MB | Forged hypotheses, logs |
| noesis/ | 49 MB | Exploration results |
| charon/data/dirichlet_raw_cache.pkl | 1.8 GB | Precomputed cache (regenerable) |

## Cache / Derived Files

| Path | Size | Purpose |
|------|------|---------|
| ergon/tensor.npz | — | Precomputed tensor (regenerable from DB) |
| cartography/convergence/data/concept_vectors.npy | — | Embedding vectors |
| cartography/lattices/data/theta_series_cache.json | — | Computed theta series |
