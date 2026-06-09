# Universal Data Source Catalog — Every Dataset for Charon
## Project Prometheus — 2026-04-11
## Goal: If mathematics is universal, the data should be too.

---

## STATUS KEY
- **FETCHED** — On disk, ready to wire
- **FETCHING** — Download in progress
- **READY** — Script written, needs to run
- **AVAILABLE** — Confirmed downloadable, script needed
- **BLOCKED** — Access issue or too large without sampling

---

## I. PHYSICS & COSMOLOGY

### Already Have
| Dataset | Objects | Size | Status | Location |
|---------|---------|------|--------|----------|
| CODATA 2022 | 286 fundamental constants | 104K | FETCHED | `physics/data/codata/` |
| PDG Particle Data | 226 particles (masses, widths) | 76K | FETCHED | `physics/data/pdg/` |
| Planck CMB | 83 binned power spectrum coefficients | 29K | FETCHED | `physics/data/planck/` |
| Materials Project | 10K crystals (band gaps, formation energies) | 4.6M | FETCHED | `physics/data/materials_project_10k.json` |

### Newly Fetched (2026-04-11)
| Dataset | Objects | Size | Status | Location |
|---------|---------|------|--------|----------|
| NIST Atomic Spectra (ASD) | 42,981 energy levels, 99 elements (neutral + ionized) | 7.4M | FETCHED | `physics/data/nist_asd/` |
| Basis Set Exchange | 776 quantum chemistry basis sets in JSON | 292M | FETCHED | `physics/data/basis_sets/` |
| 3DSC Superconductors | 13K+ superconductors with crystal structures + Tc | 109M | FETCHED | `physics/data/superconductors/3DSC/` |
| PDG Extended (hep-resources) | Extended particle data from GitHub | 213K | FETCHED | `physics/data/pdg_extended/` |

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| GWTC-4.0 (gravitational waves) | 218+ merger events (mass, spin, chirp mass) | ~100MB | JSON/HDF5 | [gwosc.org](https://gwosc.org/) | HIGH |
| USGS Earthquake Catalog | 2M+ events since 1900 (magnitude, depth, location) | ~500MB | CSV API | [earthquake.usgs.gov](https://earthquake.usgs.gov/earthquakes/search/) | HIGH |
| COD (crystallography) | 520K+ crystal structures | ~50GB full | CIF/ZIP, CC0 | [crystallography.net](https://www.crystallography.net/cod/) | MEDIUM (sample) |
| OQMD | 1.4M materials (formation energies, band gaps) | Large | API | [oqmd.org](https://oqmd.org/) | MEDIUM |
| CERN Open Data (simplified) | LHC collision events | CSV available | CSV | [opendata.cern.ch](https://opendata.cern.ch/) | MEDIUM |
| ERA5 Climate Reanalysis | Hourly global weather since 1940 | TB-scale | NetCDF | [cds.climate.copernicus.eu](https://cds.climate.copernicus.eu/) | LOW (sample) |
| SDSS Galaxy Spectra | 5.8M optical spectra | Huge | FITS/SQL | [sdss.org](https://www.sdss.org/) | LOW (sample) |
| NIST Spectral Lines | 180K transition lines | ~100MB | CSV | [physics.nist.gov/ASD](https://physics.nist.gov/PhysRefData/ASD/lines_form.html) | HIGH |

---

## II. CHEMISTRY & MOLECULAR

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| QM9 | 134K molecules, 13 quantum properties each | ~30MB | CSV | [quantum-machine.org](https://quantum-machine.org/datasets/) | HIGH |
| QM7b | 7,211 molecules, 14 properties (eigenvalues, polarizability) | ~10MB | CSV | [quantum-machine.org](https://quantum-machine.org/datasets/) | HIGH |
| PubChem (sample) | 100M+ compounds (sample 100K) | ~500MB | JSON/CSV | [pubchem.ncbi.nlm.nih.gov](https://pubchem.ncbi.nlm.nih.gov/docs/downloads) | MEDIUM |
| PubChemQC | 3M molecules DFT ground states, 2M excited states | Very large | Structured | [pubchemqc.riken.jp](https://pubchemqc.riken.jp/) | LOW (sample) |
| QO2Mol | 120K molecules, 20M conformers | Large | GitHub | [arxiv:2410.19316](https://arxiv.org/abs/2410.19316) | MEDIUM |
| DiProDB | Dinucleotide thermodynamic properties | Small | Web | [diprodb.fli-leibniz.de](http://diprodb.fli-leibniz.de/) | HIGH |
| Open Molecular Crystals 2025 | 27M molecular crystal structures | Huge | Structured | [Nature paper](https://www.nature.com/articles/s41597-026-06628-2) | LOW |

---

## III. MATHEMATICS (beyond what Charon already has)

### Already Have (via Charon pipeline)
OEIS (394K), LMFDB (133K), Genus-2 (66K), Maass (35K), Lattices (39K), KnotInfo (13K), Fungrim (3.1K), Number Fields (9.1K), Isogenies (3.2K), FindStat (1993), Metamath (46K), mathlib (8.5K), ANTEDB (244), MMLKG (1.4K), Space Groups (230), Polytopes (1.2K), pi-Base (220), OpenAlex (10K), SmallGroups (2.4K)

### Newly Fetched (2026-04-11)
| Dataset | Objects | Size | Status | Location |
|---------|---------|------|--------|----------|
| Ramanujan Machine Library | Integer relations + discovered formulas | 1.4M | FETCHED | `physics/data/ramanujan_machine/` |

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| DLMF | 100K+ formulas across 36 chapters | ~50MB | LaTeX/MathML | [dlmf.nist.gov](https://dlmf.nist.gov/) | HIGH (scraper needs fixing) |
| ComplexityBase | 551 complexity classes + inclusion relations | Small | Structured | [ohaithe.re/ZooClasses](https://ohaithe.re/ZooClasses/) | HIGH |
| Error Correction Zoo | 1000+ quantum error correction codes | ~10MB | Web | [errorcorrectionzoo.org](https://errorcorrectionzoo.org/) | MEDIUM |
| Calabi-Yau DB | 473M reflexive polytopes | Massive | Numerical | Various | LOW |
| Kreuzer-Skarke | 921K CICYs | Large | Numerical | Web | LOW |
| Atlas of Lie Groups | Structure constants, root systems | Small | Web tools | Web | MEDIUM |
| Lean mathlib 190K declarations | Full theorem dependency graph | Large | Lean 4 source | [github.com/leanprover-community/mathlib4](https://github.com/leanprover-community/mathlib4) | MEDIUM |
| Graded Ring Database | Fano 3/4-folds, K3 surfaces | ~400+ objects | Web | Various | LOW |
| FindStat computed values | Actual statistic values on combinatorial objects | API | JSON | [findstat.org/api](https://www.findstat.org/api/) | MEDIUM |

---

## IV. BIOLOGY & LIFE SCIENCES

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| RCSB PDB (summary stats) | 220K+ protein structures | ~1GB | CSV/JSON API | [rcsb.org](https://www.rcsb.org/) | HIGH |
| 1000 Genomes (variant summary) | 2,504 genomes, variant frequencies | ~500MB summary | VCF/CSV | [internationalgenome.org](https://www.internationalgenome.org/data/) | MEDIUM |
| UniProt (sample) | 250M+ protein sequences | Huge (sample) | FASTA/JSON | [uniprot.org](https://www.uniprot.org/) | LOW |
| Pfam protein families | 20K+ protein families | ~1GB | Various | [pfam.xfam.org](https://pfam.xfam.org/) | MEDIUM |
| Phyllotaxis measurements | ~200 plant morphological measurements | Small | Papers | Scattered | LOW |

---

## V. NETWORKS & GRAPHS

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| Network Repository | 5000+ real-world networks across 30 domains | ~2GB | Edge lists | [networkrepository.com](https://networkrepository.com/) | HIGH |
| SNAP (Stanford) | Social, citation, biological networks | ~5GB | Edge lists | [snap.stanford.edu](https://snap.stanford.edu/data/) | MEDIUM |
| KONECT | 1000+ networks with metadata | ~3GB | Various | [konect.cc](http://konect.cc/) | MEDIUM |

---

## VI. LANGUAGE & CULTURE

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| Leipzig Corpora | 50+ languages, word frequency tables | ~5GB | CSV | [wortschatz.uni-leipzig.de](https://wortschatz.uni-leipzig.de/en/download) | HIGH |
| Google Books Ngrams | Word frequency 1500-2019, 8 languages | ~100GB full | CSV | [storage.googleapis.com](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html) | LOW (sample) |
| Universal Dependencies | 200+ treebanks, 100+ languages | ~2GB | CoNLL-U | [universaldependencies.org](https://universaldependencies.org/) | MEDIUM |

---

## VII. FINANCE & ECONOMICS

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| Yahoo Finance (via yfinance) | 20+ years daily prices, major indices | ~1GB | CSV | Python yfinance | HIGH |
| FRED Economic Data | 800K+ economic time series | API | JSON/CSV | [fred.stlouisfed.org](https://fred.stlouisfed.org/) | MEDIUM |
| Fama-French Factors | Risk factors 1926-present | Small | CSV | [mba.tuck.dartmouth.edu](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) | HIGH |

---

## VIII. CHAOS, DYNAMICAL SYSTEMS & COMPLEXITY

### To Fetch / Compile
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| Classical dynamical systems | ~50 systems with Lyapunov exponents, bifurcation parameters | Small | Compile from literature | Textbooks | MEDIUM |
| Logistic map bifurcation data | Feigenbaum cascade, period-doubling | Compute | Generate | Scripts | HIGH |
| ComplexityBase | 551 classes + inclusion lattice | Small | Structured | [ohaithe.re](https://ohaithe.re/ZooClasses/) | HIGH |

---

## IX. EARTH & CLIMATE

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| USGS Earthquake Catalog | 2M+ events | ~500MB | CSV | [earthquake.usgs.gov](https://earthquake.usgs.gov/earthquakes/search/) | HIGH |
| NOAA Climate Indices | SOI, NAO, PDO, AMO oscillation indices | ~10MB | CSV | [psl.noaa.gov](https://psl.noaa.gov/data/climateindices/list/) | HIGH |

---

## X. AI / NEURAL NETWORKS

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| Model Zoo Dataset | 50,360 neural networks with weight statistics | ~10GB | GitHub | [github.com/ModelZoos](https://github.com/ModelZoos/ModelZooDataset) | MEDIUM |
| Neural Network Zoo taxonomy | Architecture types + lineage graph | Small | Web | [asimovinstitute.org](https://www.asimovinstitute.org/neural-network-zoo/) | LOW |

---

## XI. ALGORITHM STRUCTURE

### Already Have
| Dataset | Status |
|---------|--------|
| FLINT call graph (9,393 C files → 6,474 functions → 73,459 edges) | FETCHED (via Charon) |

### To Fetch
| Dataset | Objects | Size est. | Format | Source | Priority |
|---------|---------|-----------|--------|--------|----------|
| PARI/GP source | Number theory algorithm DAG | Large | C source | [pari.math.u-bordeaux.fr](https://pari.math.u-bordeaux.fr/) | MEDIUM |
| SciPy special functions | ~100 special function implementations | ~10MB | C/Fortran | [github.com/scipy](https://github.com/scipy/scipy) | MEDIUM |

---

## FETCH PRIORITY QUEUE (Top 20)

| # | Dataset | Domain | Why | Est. Time |
|---|---------|--------|-----|-----------|
| 1 | USGS Earthquakes | Geophysics | Power law, 2M events, CSV API | 5 min |
| 2 | GWTC-4.0 | Astrophysics | Black hole mass/spin catalog | 5 min |
| 3 | QM9 molecules | Quantum chem | 134K molecules with eigenvalues | 2 min |
| 4 | Network Repository (top 100) | Graphs | Real-world graphs across 30 domains | 30 min |
| 5 | Leipzig Corpora (10 languages) | Linguistics | Zipf's law parameters | 20 min |
| 6 | DLMF formulas | Mathematics | 100K formulas, 30x Fungrim | needs scraper fix |
| 7 | ComplexityBase | CompSci | Complexity class inclusion lattice | 5 min |
| 8 | RCSB PDB summary | Biology | Protein structure statistics | 10 min |
| 9 | Fama-French factors | Finance | Risk factor time series since 1926 | 2 min |
| 10 | NOAA Climate Indices | Climate | Oscillation time series (SOI, NAO, etc.) | 5 min |
| 11 | DiProDB | DNA physics | Dinucleotide properties | 5 min |
| 12 | QM7b | Quantum chem | 7K molecules, orbital eigenvalues | 2 min |
| 13 | NIST Spectral Lines | Physics | 180K transition lines | 10 min |
| 14 | Error Correction Zoo | Quantum CS | QEC code parameters | 15 min |
| 15 | UCI Superconductor Tc | Materials | 21K materials with Tc (retry) | 2 min |
| 16 | Logistic map data | Chaos | Feigenbaum cascade (generate) | 1 min |
| 17 | Yahoo Finance indices | Finance | S&P 500, etc. daily since 2000 | 5 min |
| 18 | SNAP networks | Graphs | Social/citation/bio networks | 30 min |
| 19 | Universal Dependencies | Linguistics | Syntactic structure across 100 languages | 20 min |
| 20 | 1000 Genomes summary | Genomics | Variant frequency statistics | 30 min |

---

*Compiled: 2026-04-11*
*Total unique sources cataloged: 55+*
*Already fetched: 24 datasets*
*New this session: 5 datasets (NIST ASD, BSE, 3DSC, Ramanujan, PDG extended)*
*Next to fetch: see priority queue above*
