# Master Data Source Inventory for Prometheus/Charon
## Compiled 2026-04-10
## 32+ sources across physics, quantum, mathematics, and algorithm libraries

---

## Tier 1: Highest Priority (new dimensions, immediately ingestible)

### PHYSICS — The "physically real" axis
| Source | Contents | Size | Format | Priority reason |
|--------|----------|------|--------|----------------|
| **CODATA** | All fundamental physical constants with uncertainties | ~300 constants | Tables | Nouns that the universe measured for us |
| **PDG** | Particle masses, lifetimes, coupling constants, branching ratios | ~1000s entries | Tables/PDF | The Standard Model crystal's output |
| **Planck CMB** | Power spectrum coefficients C_ell for ell=2..2508 | ~2500 numbers | FITS | The universe's own Fourier decomposition |
| **NIST Atomic Spectra** | 90K energy levels, 180K spectral lines | ~270K entries | Web/tables | Eigenvalues of physical Hamiltonians |
| **COD** | 520K+ crystal structures, open access | 520K CIF files | CIF | Physical lattice instantiations |

### MATHEMATICS — New axes for existing instrument
| Source | Contents | Size | Format | Priority reason |
|--------|----------|------|--------|----------------|
| **DLMF** | 100K+ formulas across 36 chapters | ~100K formulas | LaTeX/MathML | 30x Fungrim, machine-readable |
| **Lean mathlib** | 190K theorem declarations | 190K decls | Lean 4 source | Machine-parseable proof structure |
| **Calabi-Yau DB** | 473M reflexive polytopes, CY threefolds | Massive | Numerical | Hodge numbers, intersection forms |
| **Kreuzer-Skarke** | Complete CICY classification | 921K CICYs | Numerical | Genus-3+ territory |
| **Atlas of Lie Groups** | Structure constants, root systems | All Lie types | Web tools | Representation theory crystals |

### ALGORITHM CRYSTALS — Path 1 (frozen verbs)
| Source | Contents | Size | Format | Priority reason |
|--------|----------|------|--------|----------------|
| **FLINT** | 8000 number theory functions, 900K lines | Large | C source | The richest open NT crystal collection |
| **PARI/GP** | Factorization, EC, algebraic NT algorithms | Large | C source | Core number theory verbs |
| **SciPy special** | Airy, Bessel, gamma, hypergeometric impls | ~100 functions | C/Fortran | Special function crystals |
| **Arb** | Rigorous ball arithmetic, error-bounded | Large | C source | Precision geometry of computation |

---

## Tier 2: High Value (more nouns for existing crystals)

### PHYSICS
| Source | Contents | Size | Access |
|--------|----------|------|--------|
| GWOSC | 128 gravitational wave events, waveforms | HDF5 | Free |
| SDSS | 5.8M optical spectra, redshifts | Huge | Free SQL |
| CERN Open Data | LHC collision data, simplified CSV | TB-scale | Free |
| Materials Project | 150K+ structures (we have key) | API | Free w/key |

### MATHEMATICS  
| Source | Contents | Size | Access |
|--------|----------|------|--------|
| LMFDB number fields | 22M fields (we have 9K) | Large | API |
| ArxivFormula | 15M+ formulas from arXiv | Large | GitHub |
| Graded Ring Database | Fano 3/4-folds, K3 surfaces | ~400+ | Web |
| Isabelle AFP | Formal proofs | Large | Open source |
| polyDB | Lattice polytopes, matroids | Large | MongoDB |
| FindStat API values | Actual statistic computations | API | Free |

### QUANTUM
| Source | Contents | Size | Access |
|--------|----------|------|--------|
| Error Correction Zoo | QEC code database | Web | Free |
| IBM Quantum calibration | Gate fidelities, quantum volume | API | Free w/account |

---

## Tier 3: Future Enrichment

| Source | Contents | Notes |
|--------|----------|-------|
| CSD | 1.3M crystal structures | Free viewing, commercial for bulk |
| Google Quantum AI | Supremacy benchmarks | Published results only |
| ECS (INRIA) | Combinatorial structures | Complements OEIS |
| Wolfram Function Repository | Computable functions | Wolfram Language format |
| GMP source | Precision arithmetic algorithms | Algorithm crystal extraction |
| MathBridge | 23M LaTeX formulas + annotations | Research access |
| MATHPILE | 1B tokens mathematical text | Research access |

---

## Acquisition Strategy

### Immediate (this week):
1. CODATA constants — tiny download, immediate enrichment axis
2. Planck CMB C_ell spectrum — ~2500 numbers, IS a sequence (OEIS-comparable)
3. DLMF formulas — 30x Fungrim, same pipeline
4. PDG particle data tables — the universe's eigenvalues

### Near-term (next session):
5. COD crystal structures (bulk CIF download)
6. NIST atomic spectra (scripted query)
7. FLINT source code (algorithm crystal extraction pilot)
8. Lean mathlib declarations (190K theorem operadic skeletons)

### Medium-term:
9. Calabi-Yau polytope database (Hodge number tensors)
10. ArxivFormula corpus (15M formulas)
11. Full LMFDB number fields (22M, massive expansion)
12. PARI/GP + SciPy crystal extraction

---

*All 32 sources are free. 26 support bulk download. The "physically real" axis 
(CODATA + PDG + Planck + NIST spectra) adds a dimension no mathematical database can provide.*
