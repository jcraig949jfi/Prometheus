# Dataset Candidates — 2026-04-06
## Triaged from MathBases.org (128 databases) + Tavily search results
## Focus: structured, downloadable, numerical invariants, cross-domain bridges

---

## TIER 1: High-value, likely downloadable, direct bridge to existing datasets

### 1. KnotInfo: Table of Knot Invariants
URL: https://knotinfo.org
**What:** Numerical invariants for every knot up to ~13 crossings. Jones polynomial, Alexander polynomial, crossing number, signature, determinant, etc.
**Why:** Jones polynomial coefficients are integers → bridge to OEIS. Knot determinants are integers → bridge to LMFDB conductors. Knot groups connect to number theory.
**Size:** ~3000+ knots with 80+ invariants each
**Download:** CSV download available on site
**Bridge potential:** HIGH (OEIS via polynomial coefficients, LMFDB via determinants)

### 2. Analytic Number Theory Exponent Database (ANTEDB)
URL: https://teorth.github.io/expdb/
**What:** Terry Tao's project. Tracks best known exponents in analytic number theory (prime gaps, Dirichlet L-functions, etc.)
**Why:** Direct connection to LMFDB L-function data. Exponents are numerical → battery-testable.
**Size:** Moderate (hundreds of entries)
**Download:** GitHub, structured data
**Bridge potential:** HIGH (LMFDB L-functions, Charon spectral data)

### 3. Database of Number Fields
URL: http://galoisdb.math.upb.de/ and https://hobbes.la.asu.edu/NFDB/
**What:** Number fields with discriminants, Galois groups, class numbers, regulators.
**Why:** LMFDB already has some, but these are specialized/deeper. Class numbers → OEIS sequences. Galois groups → mathlib theorems.
**Size:** 100K+ fields
**Download:** Bulk download likely (academic project)
**Bridge potential:** HIGH (LMFDB, OEIS, mathlib)

### 4. Database of Local Fields
URL: https://math.la.asu.edu/~jj/localfields/
**What:** Local field extensions with ramification data, Galois groups.
**Why:** Directly relevant to Charon's non-archimedean findings (bad prime behavior → spectral compression).
**Size:** Thousands of entries
**Download:** Web tables, scrapable
**Bridge potential:** HIGH (LMFDB conductor/ramification, Charon spectral data)

### 5. Isogeny Database
URL: https://isogenies.enricflorit.com/
**What:** Isogeny graphs between elliptic curves.
**Why:** We already have isogeny edges in LMFDB graph. This is deeper — more objects, more structure.
**Size:** Unknown but specialized
**Download:** Likely available
**Bridge potential:** HIGH (direct LMFDB supplement)

### 6. A Catalogue of Lattices (Sloane/Nebe)
URL: http://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/
**What:** Lattice invariants — determinant, kissing number, density, theta series coefficients.
**Why:** Theta series are modular forms → bridge to LMFDB. Lattice determinants → OEIS.
**Size:** Thousands of lattices
**Download:** Web tables
**Bridge potential:** HIGH (LMFDB modular forms via theta series, OEIS)

### 7. The Mathematical Functions Grimoire (Fungrim)
URL: http://fungrim.org/
**What:** Machine-readable database of mathematical formulas and identities. Not natural language — symbolic.
**Why:** Formulas connecting different domains are exactly the bridges we're looking for. Special function identities link number theory ↔ analysis ↔ physics.
**Size:** 1000s of formulas
**Download:** GitHub (SymPy format)
**Bridge potential:** HIGH (cross-domain by design)

---

## TIER 2: Good value, moderate effort

### 8. NIST DLMF (deeper ingestion)
URL: https://dlmf.nist.gov/
**What:** We mapped 36 chapters but didn't ingest the actual formulas/identities.
**Why:** 600+ formulas with references to special functions that appear in L-functions.
**Effort:** Moderate (HTML parsing, formula extraction)
**Bridge potential:** MEDIUM (connects to LMFDB via special function theory)

### 9. FindStat (full ingestion)
URL: http://www.findstat.org/
**What:** We have the index (2K statistics, 336 maps). Full data has the actual statistic values.
**Why:** Combinatorial statistics connect permutations → group theory → OEIS sequences.
**Effort:** Low (API working, just need to pull more)
**Bridge potential:** MEDIUM (OEIS, mathlib)

### 10. polyDB
URL: https://polydb.org/
**What:** Polytope database from polymake project. Vertices, faces, f-vectors, symmetry groups.
**Why:** f-vectors are integer sequences → OEIS. Symmetry groups → group theory. Ehrhart polynomials connect to number theory.
**Size:** Thousands of polytopes
**Download:** API available
**Bridge potential:** MEDIUM (OEIS via f-vectors, group theory)

### 11. π-Base (Topology)
URL: https://topology.pi-base.org
**What:** Topological spaces with properties. Structured, searchable.
**Why:** Topological invariants (Betti numbers, Euler characteristic) are integers. Connects to algebraic topology in mathlib.
**Size:** Hundreds of spaces, dozens of properties
**Download:** API or GitHub
**Bridge potential:** MEDIUM (mathlib topology namespace)

### 12. SuiteSparse Matrix Collection
URL: https://sparse.tamu.edu/
**What:** 2800+ sparse matrices from real applications. Eigenvalues, condition numbers, structure.
**Why:** Spectral data (eigenvalues) → parallels with L-function zeros. Matrix structure → graph theory.
**Size:** 2800+ matrices
**Download:** Bulk download (Matrix Market format)
**Bridge potential:** MEDIUM (spectral analysis, linear algebra)

### 13. Encyclopedia of Triangle Centers
URL: http://faculty.evansville.edu/ck6/encyclopedia/ETC.html
**What:** 60,000+ triangle centers with coordinates and properties.
**Why:** Coordinates are algebraic numbers → numerical invariants. Some connect to elliptic curves.
**Size:** 60K+ entries
**Download:** Web scraping needed
**Bridge potential:** LOW-MEDIUM (OEIS via coordinate sequences)

### 14. Error Correction Zoo
URL: http://errorcorrectionzoo.org/
**What:** Taxonomy of error-correcting codes with parameters.
**Why:** Code parameters (n, k, d) are integers. Generator matrices are structured. Connects to lattices and number theory.
**Size:** Hundreds of code families
**Download:** API or GitHub
**Bridge potential:** MEDIUM (lattices, OEIS via code parameters)

---

## TIER 3: Niche but interesting for specific bridges

### 15. Calabi-Yau data (Kreuzer-Skarke)
URL: http://hep.itp.tuwien.ac.at/~kreuzer/CY/
**Size:** 473 million+ reflexive polytopes. Hodge numbers.
**Why:** Hodge numbers are integers. Physics ↔ algebraic geometry bridge.
**Download:** Bulk download available

### 16. SmallCategories
URL: https://smallcats.info/
**Why:** Category theory structures → mathlib CategoryTheory namespace (1046 modules)

### 17. Database of Ring Theory
URL: http://ringtheory.herokuapp.com/
**Why:** Ring properties → algebra, connects to mathlib Algebra/RingTheory

### 18. Classification of Association Schemes
URL: http://math.shinshu-u.ac.jp/~hanaki/as/
**Why:** Association schemes connect combinatorics ↔ group theory ↔ coding theory

### 19. Graded Ring Database
URL: http://www.grdb.co.uk/
**Why:** Algebraic geometry invariants → number theory connections

### 20. Vertex Operator Algebras and Modular Categories
URL: https://www.math.ksu.edu/~gerald/voas/
**Why:** Direct connection to modular forms and representation theory

---

## ALREADY HAVE OR IN PROGRESS
- OEIS ✓ (392K, need cross-references)
- LMFDB ✓ (134K)
- mathlib ✓ (8.4K modules)
- Metamath ✓ (46K theorems)
- Materials Project ✓ (1K, need expansion)
- FindStat ✓ (index only)
- Bilbao ✗ (SSL blocked)
- House of Graphs ✗ (auth blocked)
- ATLAS ✗ (404 on data files — try v3 URL above)

---

## RECOMMENDED DOWNLOAD ORDER
1. **KnotInfo** — CSV download, high bridge potential, ~3K objects
2. **Fungrim** — GitHub, machine-readable formulas, cross-domain bridges
3. **ANTEDB** — GitHub, Tao's project, direct L-function relevance
4. **Number Fields DB** — bulk download, 100K+ objects, LMFDB bridge
5. **Lattice Catalogue** — theta series = modular forms bridge
6. **FindStat full** — API working, just pull more data
7. **polyDB** — API, polytope f-vectors → OEIS
8. **Isogeny DB** — LMFDB supplement
9. **Local Fields DB** — Charon ramification data bridge
10. **π-Base** — topology, mathlib bridge

*Source: MathBases.org (128 databases) + Tavily search*
*Triaged by: Charon + James HITL*
