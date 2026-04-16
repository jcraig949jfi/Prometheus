# Data Provenance — Where Everything Came From

Every dataset in the project traces back to a source. This document tracks origins so we never lose the chain.

## Mathematical Databases (External)

| Source | URL | What We Took | How | When |
|--------|-----|-------------|-----|------|
| LMFDB | devmirror.lmfdb.xyz | EC (3.8M), MF (1.1M), Artin (793K), G2C (66K), Lfunc (24M) | CSV dump via psql COPY | ~2026-04-14 |
| LMFDB API | lmfdb.org/api/ | Maass forms, number fields, local fields, genus-2 data | JSON API queries | Various |
| OEIS | oeis.org | ~375K integer sequences | Bulk download | Unknown |
| Fungrim | fungrim.org | ~1,000 mathematical formulas | JSON export | Unknown |
| FindStat | findstat.org | Combinatorial statistics | JSON API | Unknown |
| GAP | gap-system.org | Small groups (SmallGrp library) | Computed via GAP | Unknown |
| Antedb | antedb.org | Algebra experiment index | JSON download | Unknown |

## Scientific Databases (External)

| Source | URL | What We Took | How | When |
|--------|-----|-------------|-----|------|
| Materials Project | materialsproject.org | 10K materials | API query (fetch_materials_10k.py) | Unknown |
| KnotInfo | knotinfo.math.indiana.edu | 12,965 knots | Scraper (ingest_knotinfo.py) | Unknown |
| QM9 | — | 133,885 quantum molecules | CSV download | Unknown |
| PolyDB | polydb.org | 980 polytopes (15 collections) | JSON API | Unknown |
| NIST CODATA | physics.nist.gov | ~300 physical constants | JSON download | Unknown |
| NIST ASD | physics.nist.gov/asd | Atomic spectra (120+ elements) | Per-element JSON | Unknown |
| NASA Exoplanet Archive | exoplanetarchive.ipac.caltech.edu | 6,158 confirmed exoplanets | CSV download | Unknown |
| LIGO/Virgo/KAGRA | gwosc.org | 219 gravitational wave events | CSV download | Unknown |
| SuperCon | supercon.nims.go.jp | Superconductor materials | Various | Unknown |
| BiGG Models | bigg.ucsd.edu | ~110 metabolic models | JSON download | Unknown |
| Basis Set Exchange | basissetexchange.org | Quantum chemistry basis sets | JSON API | Unknown |
| USGS | earthquake.usgs.gov | Earthquake data 1970-1974 | CSV download | Unknown |
| SnapPy | snappy.math.uic.edu | 3-manifold census | CSV export | Unknown |

## Formal Mathematics

| Source | URL | What We Took | How | When |
|--------|-----|-------------|-----|------|
| Lean Mathlib4 | github.com/leanprover-community/mathlib4 | Theorem/definition index | Export tool | Unknown |
| Metamath | metamath.org | set.mm theorem database | Direct download | Unknown |

## Financial Data

| Source | URL | What We Took | How | When |
|--------|-----|-------------|-----|------|
| Kenneth French | mba.tufts.edu/pages/faculty/ken.french | FF 5 factors, 10 industry, momentum | CSV download | Unknown |
| FRED | fred.stlouisfed.org | Macro indicators | API | Unknown |

## Computed / Internal

| Dataset | Generator | Method | When |
|---------|-----------|--------|------|
| Isogeny graphs | cartography/isogenies/ scripts | Sage computation from EC data | Unknown |
| Lattice theta series | cartography/lattices/ scripts | Computed from lattice definitions | Unknown |
| Logistic map / Feigenbaum | cartography/physics/data/chaos/ scripts | Numerical computation | Unknown |
| DuckDB objects/bridges | charon/ pipeline | Aggregated from LMFDB + cartography | Various |
| Space groups | cartography/spacegroups/ | International Tables + computation | Unknown |

## Provenance Gaps

These datasets have unclear origins — the source URL or acquisition method isn't documented:

- `cartography/topology/data/` — 28 MB of topological datasets, origin unclear
- `cartography/chemistry/data/qm9.csv` — likely from MoleculeNet/QM9 but script not found
- Several `cartography/physics/data/superconductors/` subdatasets — mixed sources
- `cartography/lattices/data/lattices_scraped.json` — "scraped" from where?

**Action:** When loading any dataset with unknown provenance, record the best-guess origin in `core.data_source` and flag it for verification.
