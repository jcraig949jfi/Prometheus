# 25 Lesser-Known Open Problems in Mathematics
## Curated for Prometheus — Second-Tier Frontier Problems with Computational Hooks
## Date: 2026-04-17
## Source: Gemini 2.5 Pro, prompted for problems invisible to the public but important to experts

---

## 1. Polynomial Freiman-Ruzsa Conjecture (PFR)

**Subfield:** Additive combinatorics
**Statement:** Let A ⊂ Z^n satisfy |A+A| ≤ K|A|. Then A is contained in a generalized arithmetic progression of dimension O(log K) and size K^O(1)|A|.
**Year/Origin:** ~2005, Green-Ruzsa
**Why it matters:** Central to structure theory of approximate groups; impacts TCS (property testing, expanders).
**Partial results:** Quasi-polynomial bounds (Sanders); polynomial bounds in special settings (finite fields).
**Barrier:** Lack of sharp structural control; entropy vs combinatorial methods mismatch.
**Data coupling:** Finite subsets of Z^n, sumset growth experiments, approximate group databases.

---

## 2. Erdos-Hajnal Conjecture (general graphs)

**Subfield:** Extremal graph theory
**Statement:** For every graph H, there exists δ(H) > 0 such that every H-free graph on n vertices contains a clique or independent set of size n^δ(H).
**Year/Origin:** 1989, Erdos-Hajnal
**Why it matters:** Structure in forbidden subgraph classes; ties to model theory and Ramsey theory.
**Partial results:** Proven for special H (tournaments, small graphs).
**Barrier:** Lack of global structural decomposition.
**Data coupling:** Exhaustive search over H-free graphs, extremal constructions.

---

## 3. Cap Set Bounds in Other Groups

**Subfield:** Additive combinatorics / finite geometry
**Statement:** Generalize exponential decay bounds for cap sets in (Z/3Z)^n to other groups (e.g., (Z/4Z)^n).
**Year/Origin:** Post-2016 (after Ellenberg-Gijswijt breakthrough)
**Why it matters:** Extends polynomial method reach; links to tensor rank.
**Partial results:** Strong bounds for F_3^n; weaker elsewhere.
**Barrier:** Polynomial method rigidity beyond characteristic 3.
**Data coupling:** Finite vector spaces, tensor decompositions.

---

## 4. Sarnak's Mobius Disjointness Conjecture (specific systems)

**Subfield:** Ergodic theory / analytic number theory
**Statement:** For zero-entropy dynamical systems T: (1/N) Σ_{n≤N} μ(n) f(T^n x) → 0.
**Year/Origin:** ~2010, Sarnak
**Why it matters:** Bridges randomness in number theory with dynamics.
**Partial results:** Proven for many systems (rotations, some flows).
**Barrier:** Controlling correlations with multiplicative functions.
**Data coupling:** Mobius values, orbit statistics, OEIS sequences.

---

## 5. Littlewood Conjecture (metric refinement)

**Subfield:** Diophantine approximation / dynamics
**Statement:** inf_{n≥1} n |nα| |nβ| = 0 for all (α,β).
**Status:** Still open in full generality.
**Why it matters:** Rigidity of diagonal flows on homogeneous spaces.
**Partial results:** Almost all (α,β) proven (measure-theoretic).
**Barrier:** Exceptional set structure.
**Data coupling:** Continued fraction expansions, lattice flows, nf_fields.

---

## 6. Zaremba's Conjecture (full version)

**Subfield:** Number theory / dynamics
**Statement:** Every integer q has a coprime numerator a such that the continued fraction of a/q has bounded partial quotients.
**Year:** 1971, Zaremba
**Partial results:** Density-1 subset proven (Bourgain-Kontorovich).
**Barrier:** Thin orbits, expansion gaps.
**Data coupling:** Continued fraction databases, nf_fields (our nf_cf tensor domain!).

---

## 7. McMullen's Conjecture on Arithmetic Chaos

**Subfield:** Arithmetic dynamics
**Statement:** Bounded partial quotient sets generate full Hausdorff dimension.
**Year:** ~2010, McMullen
**Why it matters:** Fractal geometry of number-theoretic sets.
**Barrier:** Nonlinear transfer operators.
**Data coupling:** Symbolic dynamics, continued fractions.

---

## 8. Lang-Trotter Conjecture (effective version)

**Subfield:** Arithmetic statistics
**Statement:** Asymptotics for primes p where a_p(E) = t for fixed elliptic curve E and integer t.
**Year:** 1976, Lang-Trotter
**Partial results:** Conditional (GRH); average results (Katz-Sarnak).
**Barrier:** Deep analytic number theory limitations.
**Data coupling:** ec_curvedata (3.8M curves with Frobenius traces), LMFDB directly.

---

## 9. Moments of L-functions (beyond known ranges)

**Subfield:** Analytic number theory
**Statement:** Determine asymptotics for the 2k-th moment of L-functions on the critical line for k ≥ 3.
**Why it matters:** Random matrix theory correspondence; Keating-Snaith predictions.
**Barrier:** Off-diagonal terms uncontrollable beyond k=2.
**Data coupling:** lfunc_lfunctions (24M with zeros), object_zeros, dirichlet_zeros.

---

## 10. Geometric Bogomolov Conjecture (function fields)

**Subfield:** Arithmetic geometry
**Statement:** Small points on subvarieties of abelian varieties are dense only on special subvarieties.
**Status:** Open in general over function fields.
**Why it matters:** Heights and distribution of rational points.
**Barrier:** Non-archimedean geometry complexity.
**Data coupling:** g2c_curves (Jacobians), height computations.

---

## 11. Green's Conjecture (remaining cases)

**Subfield:** Algebraic geometry
**Statement:** Syzygies of canonical curves are determined by the Clifford index.
**Status:** Mostly solved, edge cases remain.
**Barrier:** Degeneration limits for specific curve types.
**Data coupling:** Curve moduli, syzygy computations (Macaulay2/OSCAR).

---

## 12. Kontsevich Period Conjecture (effective)

**Subfield:** Motives / number theory
**Statement:** All algebraic relations between periods come from geometry (i.e., from the motivic Galois group).
**Barrier:** Lack of motivic Galois control.
**Data coupling:** Period integrals, Feynman integrals, special L-function values in LMFDB.

---

## 13. Matroid Representability over Finite Fields

**Subfield:** Combinatorics / matroid theory
**Statement:** Characterize matroids representable over a given finite field.
**Barrier:** Infinite forbidden minors (Rota's conjecture for GF(5)+).
**Data coupling:** Matroid databases, finite geometry computations.

---

## 14. Hadwiger's Conjecture (intermediate cases)

**Subfield:** Graph theory
**Statement:** K_t-minor-free graphs are (t-1)-colorable.
**Status:** Open for t ≥ 7 (proven for t ≤ 6).
**Barrier:** Minor structure complexity grows super-exponentially.
**Data coupling:** Graph minor enumeration, SAT encodings.

---

## 15. Unique Games Conjecture (fine-grained variants)

**Subfield:** TCS / combinatorics
**Statement:** Approximating certain constraint satisfaction problems is NP-hard beyond specific thresholds.
**Barrier:** Lack of integrality gap constructions for the full conjecture.
**Data coupling:** Constraint satisfaction instances, SDP relaxations.

---

## 16. Kadison-Singer Paving (quantitative bounds)

**Subfield:** Operator theory
**Statement:** Optimal constants in paving conjectures (qualitatively solved by Marcus-Spielman-Srivastava 2013).
**Status:** Existence proven; quantitative optimization open.
**Barrier:** Spectral partitioning limits.
**Data coupling:** Random matrices, expected characteristic polynomials.

---

## 17. Nodal Domain Counts (chaotic manifolds)

**Subfield:** Spectral geometry
**Statement:** Distribution of nodal domains for high eigenvalues on chaotic Riemannian manifolds.
**Barrier:** Quantum chaos unpredictability; Berry's conjecture on random wave models.
**Data coupling:** Numerical eigenfunctions, spectral computations.

---

## 18. Random Simplicial Complexes (homology thresholds)

**Subfield:** Topological combinatorics
**Statement:** Sharp thresholds for vanishing of k-th homology in random d-complexes (Linial-Meshulam model).
**Barrier:** High-dimensional dependence structures.
**Data coupling:** Simulated complexes, persistent homology computations.

---

## 19. Knot Concordance Group Torsion

**Subfield:** Low-dimensional topology
**Statement:** Classify torsion elements in the smooth knot concordance group C.
**Barrier:** Gauge theory limitations (Donaldson/Heegaard Floer provide partial obstructions).
**Data coupling:** KnotInfo (13K knots), concordance invariants, our knots table.

---

## 20. Slice-Ribbon Conjecture (restricted families)

**Subfield:** Knot theory
**Statement:** Every slice knot is ribbon.
**Barrier:** Lack of obstruction invariants distinguishing slice from ribbon.
**Data coupling:** Knot tables, 4-genus data, KnotInfo.

---

## 21. L-space Conjecture (full equivalence)

**Subfield:** Topology / Floer homology
**Statement:** For irreducible rational homology 3-spheres: left-orderable fundamental group ⟺ not an L-space ⟺ admits a co-orientable taut foliation.
**Barrier:** Floer homology computational complexity; foliation constructions.
**Data coupling:** 3-manifold census, SnapPy database.

---

## 22. Cluster Algebra Positivity (general case)

**Subfield:** Algebra / combinatorics
**Statement:** All cluster variables have positive Laurent expansions in terms of any cluster.
**Barrier:** Mutation complexity grows exponentially; known only for finite and affine types.
**Data coupling:** Cluster algebra computations, quiver mutation databases.

---

## 23. Growth Gap Conjecture (refinements)

**Subfield:** Geometric group theory
**Statement:** No intermediate growth rates between polynomial and exponential exist except Grigorchuk-type constructions.
**Barrier:** Exotic group constructions (automata groups) resist classification.
**Data coupling:** Cayley graph growth simulations, word growth computations.

---

## 24. KPZ Universality in Higher Dimensions

**Subfield:** Probability / mathematical physics
**Statement:** Characterize the universality class of KPZ-type stochastic PDEs beyond 1D.
**Barrier:** Renormalization breakdown; Hairer's regularity structures handle subcritical but not the critical 2D case.
**Data coupling:** Numerical simulations, directed polymer models.

---

## 25. Optimal Transport Regularity (rough costs)

**Subfield:** Analysis / PDE
**Statement:** Regularity of optimal transport maps under weak conditions on the cost function (beyond the Ma-Trudinger-Wang condition).
**Barrier:** Lack of convexity structure for general costs.
**Data coupling:** Numerical OT solvers, Monge-Ampere computations.

---

## Prometheus Relevance Assessment

### Directly testable against our data (Bucket A candidates):
- **#8 Lang-Trotter**: ec_curvedata has 3.8M Frobenius traces. Count primes with a_p = t.
- **#9 L-function moments**: lfunc_lfunctions has 24M L-functions with zeros. Compute moments.
- **#6 Zaremba**: nf_fields has 22M number fields; nf_cf tensor domain has CF data.
- **#4 Sarnak Mobius disjointness**: Computable from Mobius values + dynamical systems.
- **#19 Knot concordance**: Our knots table has 13K knots with invariants.
- **#20 Slice-ribbon**: Same knot data, need 4-genus.

### Testable with tensor decomposition:
- **#1 PFR**: Sumset structure detectable in tensor over finite groups.
- **#3 Cap sets**: Tensor rank is literally the mathematical object studied.
- **#22 Cluster positivity**: Cluster mutations are algebraic operations our tensor could track.

### New fingerprint modalities suggested:
- **#5 Littlewood**: CF partial quotient bounds → nf_cf domain.
- **#17 Nodal domains**: Spectral eigenfunction data → new strategy group.
- **#18 Random simplicial homology**: PH thresholds → topological strategy.
- **#12 Kontsevich periods**: Period integrals as L-function special values → lfunc data.

### Cross-domain bridges:
- **#4 Sarnak** bridges ergodic theory ↔ number theory (our Chowla test is a special case)
- **#8 Lang-Trotter** bridges arithmetic statistics ↔ random matrix theory
- **#21 L-space** bridges topology ↔ algebra ↔ Floer homology (our knot silent island)
- **#24 KPZ** bridges probability ↔ mathematical physics (turbulence connection)

---

*These 25 problems are the SECOND TIER — important to experts, invisible to the public. At least 8 are directly testable against Prometheus databases. Several suggest new tensor dimensions.*

*Aporia, 2026-04-17*
