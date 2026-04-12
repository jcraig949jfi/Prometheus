# Round 3 Challenges — Compiled from Session Reviews
## Sources: James (5), ChatGPT (5), DeepSeek (5)
## Status: Queued for 2026-04-10

---

## From James — 5 Challenges (Layer 3 depth probes)

### J1. Galois Image Portrait — density of traces classification
*"Can the instrument distinguish Large image (SL_2(F_ell)) from Small image (dihedral/Borel) purely from a_p distribution?"*
- Data: 17K weight-2 forms in DuckDB
- Builds on: C02 (starvation hierarchy), CT4 (CM rediscovery)
- Status: **READY** — all data and tools exist

### J2. Picard-Fuchs Operadic Skeleton — differential geometry bridge
*"Map skeletons of Calabi-Yau differential operators against L-function skeletons."*
- Data: Would need Picard-Fuchs operator database (AESZ database or similar)
- Builds on: C12 (operadic dynamics), CL5 (Gamma wormhole)
- Status: **NEEDS DATA** — Picard-Fuchs operators not in pipeline

### J3. Ghost Cluster Analysis — Layer 3 on the 641 near-misses
*"Run symmetry scan on the 641 failures. Are they non-congruence subgroups or Maass forms killed by phase shift?"*
- Data: CT5 failure records + CT4 symmetry detection
- Builds on: CT5, CT4
- Status: **READY** — highest ROI per James and DeepSeek

### J4. Mock Shadow Mapping — find shadows without being told the definition
*"Give the tool Mock Theta functions and ask it to find their shadows in the 17K modular forms."*
- Data: OEIS mock theta sequences + DuckDB modular forms
- Builds on: C09 (moonshine), CT4 (Layer 3)
- Status: **READY** — data exists

### J5. Brauer-Manin Obstruction Probe — scaling law at its limit
*"Can mod-p fingerprinting detect structural thinning for equations with only local solutions?"*
- Data: Would need curated set of Brauer-Manin obstructed equations
- Builds on: CL1 (universal scaling law)
- Status: **NEEDS DATA** — need obstructed equation database

---

## From ChatGPT — Round 2 strategic assessment + next moves

### Key insights captured:
1. **Three-layer confirmation**: Scalar (dead) → Structural (working) → Transformational (now open)
2. **"Each prime gives an independent projection; higher primes = higher resolution"** — the unified view connecting CT1 (cross-ell independence), CL1 (scaling law), CL2 (mod-2 collapse)
3. **Adelic viewpoint discovered computationally**: Objects ≈ intersection of independent prime-wise structures
4. **641 near-misses = where new math lives**: most die to F13/F14, suggesting asymptotic/phase-aware transformations are the missing capability

### CT-R3 priorities (from ChatGPT):
1. **Exploit 641 near-misses** with Layer 3 transforms (= James J3)
2. **Push scaling law as classification invariant** — does slope depend on dimension, degree, symmetry group?
3. **Build deformation detection** — combine CT1 clusters + CT4 transforms → detect paths through structure space
4. **Break the mod-2 barrier** — extract structure WITHIN the cliques
5. **Expand the knot bridge** (DS3 torus family → OEIS match)

---

## From DeepSeek — 5 targeted extensions

### DS-R3-1. Scaling law as active detector for hidden algebraic families
*"Take 10K OEIS sequences without known algebraic interpretations. Rank by enrichment slope. Verify top 5% with BM + LMFDB."*
- Builds on: CL1 (universal scaling)
- Status: **READY** — all data exists
- Note: Overlaps with James's strategic vision of the scaling law as a discovery tool

### DS-R3-2. Deconstructing mod-2 GSp_4 cliques — Richelot isogenies or new phenomenon?
*"For each clique, compute Richelot isogeny degree, (2,2)-isogeny, maximal isotropic subgroups of 2-torsion."*
- Builds on: CL2 (mod-2 cliques)
- Status: **PARTIAL** — curve labels available, Richelot computation needs SageMath
- Note: Could partially test with LMFDB isogeny data for genus-2

### DS-R3-3. Near-miss resurrection with parameter sweeps
*"Re-run failed tests on 641 near-misses with parameter grids (F14 lags 1-10, F13 window sizes). Apply Layer 3 to resurrected cases."*
- Builds on: CT5 (failure mining), CT4 (Layer 3)
- Status: **READY** — all infrastructure exists
- Note: Converges with James J3 and ChatGPT priority #1

### DS-R3-4. Genus-3 Sato-Tate classifier (82K curves → 410 groups)
*"Install SageMath, compute Frobenius for 82K genus-3 curves, train Mahalanobis classifier on 410-group fingerprints."*
- Builds on: DS2 (98.3% genus-2 classifier)
- Status: **BLOCKED on SageMath** — highest-value unblock
- Note: Would be first empirical map of genus-3 ST groups over Q

### DS-R3-5. Generating function isomorphism — different recurrences, same closed form
*"Compute rational generating functions G(x)=P(x)/Q(x) for all 2,740 characteristic polynomials. Cluster by reduced G(x)."*
- Builds on: C08 (recurrence clustering), C17 (Collatz family)
- Status: **READY** — sympy can reduce rational functions
- Note: Could find "Collatz cousins" with different recurrences but same closed form

---

## Deduplication & Priority

| Theme | Sources | Priority | Status |
|-------|---------|----------|--------|
| **Near-miss resurrection + Layer 3** | James J3, ChatGPT #1, DeepSeek DS-R3-3 | **1 (unanimous)** | READY |
| **Scaling law as active detector** | DeepSeek DS-R3-1, ChatGPT #2 | **2** | READY |
| **Galois image portrait** | James J1 | **3** | READY |
| **Mod-2 clique deconstruction** | DeepSeek DS-R3-2, ChatGPT #4 | **4** | PARTIAL (needs SageMath for full) |
| **Mock shadow mapping** | James J4 | **5** | READY |
| **Generating function isomorphism** | DeepSeek DS-R3-5 | **6** | READY |
| **Genus-3 ST classifier** | DeepSeek DS-R3-4 | **7** | BLOCKED (SageMath) |
| **Picard-Fuchs operadic** | James J2 | **8** | NEEDS DATA |
| **Brauer-Manin obstruction** | James J5 | **9** | NEEDS DATA |
| **Deformation paths** | ChatGPT #3 | **10** | Ready but complex build |
| **Knot bridge expansion** | ChatGPT #5 | **11** | READY |

**Top 5 for immediate firing (all READY):**
1. Near-miss resurrection (J3/DS-R3-3) — unanimous highest priority
2. Scaling law as detector (DS-R3-1) — invert the finding into a tool
3. Galois image portrait (J1) — Layer 3 depth probe
4. Mock shadow mapping (J4) — moonshine depth
5. Generating function isomorphism (DS-R3-5) — recurrence to closed form

---

*Compiled: 2026-04-10*
*Post: 25/25 challenges complete, Layer 3 open, universal scaling law confirmed*
