# Loose Files — Data Not Yet in Any Database

Files in cartography/ and elsewhere that are source data but not yet loaded into Postgres.
Updated 2026-04-16 with verified file paths, sizes, and row counts.

## Current prometheus_sci State

| Table | Rows | Status |
|-------|------|--------|
| topology.knots | 12,965 | LOADED |
| topology.polytopes | 980 | LOADED |
| chemistry.qm9 | 133,885 | LOADED |
| algebra.space_groups | 230 | LOADED |
| algebra.lattices | 26 | LOADED (partial — full file has ~1000) |
| algebra.groups | 544,831 | LOADED |
| physics.materials | 10,000 | LOADED |
| physics.codata | 0 | **EMPTY — data file exists** |
| physics.superconductors | 0 | **EMPTY — data file exists** |
| physics.pdg_particles | 0 | **EMPTY — data file exists** |
| analysis.fungrim | 0 | **EMPTY — data file exists** |
| analysis.oeis | 0 | **EMPTY — data files exist** |
| biology.metabolism | 0 | **EMPTY — data files exist** |

---

## Ready to Ingest (schema exists, data file found, verified)

| Target Table | Source File | Rows | Size | Format |
|-------------|------------|------|------|--------|
| **physics.codata** | `cartography/physics/data/codata_constants.json` | 356 | 52 KB | JSON array: {name, value, uncertainty, unit} |
| **physics.pdg_particles** | `cartography/physics/data/pdg/particles.json` | 226 | ~100 KB | JSON array: {name, mass_GeV, width_GeV, charge, spin, ...} |
| **physics.superconductors** | `cartography/physics/data/superconductors/aflow_canonical_superconductors.csv` | 2,012 | ~500 KB | CSV: query_name, sc_class, aflow_compound, aflow_sg, ... |
| **analysis.fungrim** | `cartography/fungrim/fungrim_formulas.json` | 3,130 | 1.6 MB | JSON array: {id, type, symbols, module, formula_text} |
| **biology.metabolism** | `cartography/metabolism/data/*.json` (109 files) | 109 models | 256 MB | One JSON per BiGG model: reactions, metabolites, genes |
| **algebra.lattices** (reload) | `cartography/lattices/data/lattices_full.json` | ~1,000 | 6.8 MB | JSON: labels, dimensions, determinants, class_numbers |

Total: ~5,833 rows + 109 metabolism models to fill 6 empty tables.

---

## Needs New Schema (no table exists)

### High Value (would enable new science)

| Domain | Source File | Rows | Size | Suggested Table | Notes |
|--------|------------|------|------|----------------|-------|
| Physics | `cartography/physics/data/exoplanets/confirmed_exoplanets.csv` | 6,158 | 700 KB | physics.exoplanets | NASA Exoplanet Archive |
| Physics | `cartography/physics/data/gravitational_waves/gwtc_params.csv` | 219 | 13 KB | physics.gw_events | LIGO/Virgo/KAGRA |
| Physics | `cartography/physics/data/pulsars/*.csv` | 4,351 | 5.3 MB | physics.pulsars | ATNF Pulsar Catalogue |
| Topology | `charon/data/mahler_measures.json` | ~2,977 | 1.2 MB | topology.mahler_measures | Computed from knot Alexander polynomials |
| Analysis | `cartography/oeis/data/oeis_formulas.jsonl` | ~375K | 60 MB | analysis.oeis | OEIS sequences with formulas |
| Analysis | `cartography/oeis/data/oeis_crossrefs.jsonl` | ~375K | 62 MB | analysis.oeis_crossrefs | OEIS cross-reference graph |
| Combinatorics | `cartography/findstat/data/findstat_enriched.json` | ~500 | 194 KB | analysis.findstat | FindStat mathematical statistics |

### Medium Value (domain-specific)

| Domain | Source File | Rows | Size | Suggested Table |
|--------|------------|------|------|----------------|
| Algebra | `cartography/number_fields/data/number_fields.json` | ~9K | 1.8 MB | algebra.number_fields_local |
| Algebra | `cartography/atlas/data/small_groups.json` | ~500 | 1.1 MB | algebra.groups (append) |
| Topology | `cartography/knots/data/knotinfo_3d.csv.tar.gz` | ~12K | 45 MB | topology.knots_extended |
| Physics | `cartography/physics/data/superconductors/cod_canonical_superconductors.csv` | ~2K | ~500 KB | physics.superconductors (append) |

### Large / Specialized (needs investigation)

| Domain | Path | Size | Notes |
|--------|------|------|-------|
| Formal math | `cartography/mathlib/data/` | 138 MB | Lean Mathlib4 declarations |
| Formal math | `cartography/metamath/data/` | 49 MB | Metamath set.mm proofs |
| Crystallography | `cartography/physics/data/cod_crystals_bulk.json` | large | COD crystal structures |
| Chemistry | `cartography/physics/data/pubchem_50k.csv` | ~50K | PubChem compounds |
| Topology | `cartography/topology/data/` | 28 MB | Various topological datasets |
| Algebra | `cartography/isogenies/data/graphs/` | 662 MB | Isogeny graph data |

---

## Explicitly NOT Source Data (Do Not Ingest)

| Path | Size | What It Is |
|------|------|-----------|
| cartography/convergence/data/ | ~400 GB | Research outputs: signatures, formulas, bridges, exploration results |
| harmonia/results/ | 3 MB | Falsification test outputs |
| ergon/results/ | 65 MB | MAP-Elites checkpoints, shadow maps |
| forge/ | 95 MB | Hypothesis generation output |
| agents/hephaestus/ | 235 MB | Forged hypotheses, logs |
| noesis/ | 49 MB | Exploration results (migrated to prometheus_fire.noesis) |
| charon/data/dirichlet_raw_cache.pkl | 1.8 GB | Precomputed cache (regenerable, delete after migration verified) |
| Prometheus_data_backup/ | 36 GB | Full duplicate of repo |
| cartography/v2/*_results.json | ~50 files | One-shot research script outputs |
