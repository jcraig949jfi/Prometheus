# Universal Database Inventory — Every Domain We Can Reach
## 2026-04-13

65+ databases across mathematics, physics, chemistry, biology, astronomy, earth science.
From subatomic to cosmological scale. For the universal tensor.

## IMMEDIATE PULLS (small, fast, high feature density)

| # | Database | Domain | Objects | Features | Format | Download |
|---|----------|--------|---------|----------|--------|----------|
| 1 | QM9 | Quantum chem | 134K | 13 QM properties | XYZ/CSV | figshare |
| 2 | NASA Exoplanets | Astronomy | 6.1K | 20+ orbital | CSV API | REST |
| 3 | NNDC/NuDat | Nuclear | 3.3K nuclides | 15+ nuclear | CSV API | web query |
| 4 | ATNF Pulsars | Astronomy | 3.4K | 69-105 params | CSV | web export |
| 5 | GWTC | Gravitational waves | 218 events | 15 params | JSON | GWOSC API |
| 6 | SnapPy 3-manifolds | Topology | 11K | volume, CS, homology | SQLite | pip install |
| 7 | Open Supernova | Astronomy | 60K | mag, z, type | JSON | GitHub |

## MEDIUM PULLS (need bulk download, hours)

| # | Database | Domain | Objects | Format | Size est |
|---|----------|--------|---------|--------|----------|
| 8 | COD crystals | Crystallography | 520K | CIF bulk | ~20 GB |
| 9 | OQMD | Materials (DFT) | 1.4M | SQL/API | ~10 GB |
| 10 | AFLOW | Materials (DFT) | 3.5M | JSON API | ~50 GB |
| 11 | ChEMBL | Bioactivity | 2.5M | SQLite | ~35 GB |
| 12 | PubChem (subset) | Chemistry | 119M (sample 1M) | CSV | ~5 GB |
| 13 | Kreuzer-Skarke | Algebraic geom | 474M polytopes | PALP | ~100 GB |
| 14 | House of Graphs | Graph theory | thousands | graph6 | ~1 GB |
| 15 | ATLAS finite groups | Representation | 716 groups | GAP | ~100 MB |
| 16 | Error Correction Zoo | Coding theory | hundreds | YAML/git | ~50 MB |
| 17 | Open Reaction DB | Chemistry | millions | protobuf | ~50 GB |

## LARGE PULLS (need infrastructure, days)

| # | Database | Domain | Objects | Size est |
|---|----------|--------|---------|----------|
| 18 | Gaia DR3 | Stellar (sample) | 1.8B (sample 1M) | ~10 GB |
| 19 | SDSS DR17 | Astronomical | 5.8M spectra | ~100 GB |
| 20 | PDB | Structural biology | 227K structures | ~1 TB |
| 21 | AlphaFold | Predicted structures | 200M | ~23 TB |
| 22 | UniProt | Proteins | 574K reviewed | ~100 GB |
| 23 | PubChem full | Chemistry | 119M | ~500 GB |
| 24 | USGS earthquakes | Geophysics | millions | ~10 GB |
| 25 | World Ocean DB | Oceanography | 20.6M profiles | ~100 GB |

## ALREADY PULLING (LMFDB mirror dump)

| Table | Rows | Status |
|-------|------|--------|
| g2c_curves | 66K | DONE (41 MB) |
| artin_reps | 793K | DONE (445 MB) |
| mf_newforms | 1.1M | IN PROGRESS (~8 GB) |
| ec_curvedata | 3.8M | QUEUED |
| lfunc_lfunctions | 24.2M | QUEUED (~43 GB est) |

## ALREADY LOADED (in tensor v7)

EC (31K), OEIS (20K), knots (13K), genus-2 (66K), NF (9K), Fungrim (3K),
MF (50K), groups (50K), Maass (15K), lattices (39K), Dirichlet zeros (185K),
object zeros (50K), HMF (50K), Belyi (1.1K), superconductors (4K),
materials (10K), atomic spectra (99), particles (225), metabolism (4.2K).
Total: 601K objects x 182 dimensions.

## SCALE COVERAGE

| Scale | Domain | Database | Objects |
|-------|--------|----------|---------|
| Subatomic | Nuclear | NNDC/NuDat | 3.3K |
| Subatomic | Particle | PDG | 225 |
| Subatomic | Gravitational | GWTC | 218 |
| Atomic | Spectra | NIST ASD | 43K levels |
| Molecular | QM | QM9 | 134K |
| Molecular | Chemistry | PubChem | 119M |
| Molecular | Bioactivity | ChEMBL | 2.5M |
| Crystal | Structure | COD + MP + AFLOW | 4M+ |
| Crystal | Superconductor | 3DSC | 41K |
| Protein | Structure | PDB + AlphaFold | 200M+ |
| Protein | Function | UniProt | 574K |
| Cell | Expression | HCA | 70M cells |
| Brain | Connectivity | Allen + HCP | 1.2K subjects |
| Organism | Metabolism | BiGG/Recon3D | 10K reactions |
| Planet | Exoplanets | NASA Archive | 6.1K |
| Stellar | Properties | Gaia DR3 | 1.8B |
| Stellar | Pulsars | ATNF | 3.4K |
| Stellar | Supernovae | OSC | 60K |
| Galactic | Spectra | SDSS | 5.8M |
| Cosmological | CMB | Planck | 2K multipoles |
| Cosmological | GW events | GWTC | 218 |
| Mathematical | Number theory | LMFDB | 24M+ L-functions |
| Mathematical | Sequences | OEIS | 394K |
| Mathematical | Topology | KnotInfo + SnapPy | 24K |
| Mathematical | Groups | GAP + ATLAS | 545K+ |
| Mathematical | Alg. geometry | Kreuzer-Skarke | 474M |
| Mathematical | Combinatorics | FindStat + Graphs | thousands |
| Mathematical | Formal proofs | Metamath + Lean | 100K+ |

From quarks to quasars. One tensor.
