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

---

# Round 2 — Lesser-known classical problems (2026-05-08)

**Source:** 32 gaps identified by `aporia/docs/problem_database_coverage_2026-05-08.md`. Round 1 covered specialist-tier problems; Round 2 covers classical-but-less-famous problems whose statements are accessible at undergraduate level but whose computational frontiers map cleanly to substrate operators. The first 18 are also in `aporia/docs/deep_research_batch11_seeds.md`.

---

## 26. Lehmer's Totient Problem

**Subfield:** Number theory (totient function)
**Statement:** Does there exist a composite integer n such that φ(n) divides n - 1?
**Year/Origin:** 1932, D. H. Lehmer
**Why it matters:** Composite n with φ(n) | n-1 would be Carmichael-like at every base. Connections to Carmichael totient and Giuga's conjecture.
**Partial results:** Brute-force verified to ~10^22; Cohen-Hagis 1980 proved any such n must have ≥14 distinct prime factors and be > 10^20.
**Barrier:** No structural obstruction known; existence not ruled out by standard heuristics.
**Data coupling:** Brute-force totient corpus; Carmichael number tables; Giuga number tables.

---

## 27. Pillai's Conjecture

**Subfield:** Number theory (perfect-power gaps)
**Statement:** For every k ≥ 1, the equation x^p - y^q = k has only finitely many integer solutions with min(p,q) ≥ 2. Equivalently, gaps between consecutive perfect powers grow unboundedly.
**Year/Origin:** 1945, S. S. Pillai
**Why it matters:** Catalan's conjecture (gap = 1) proved 2002 by Mihăilescu; Pillai is the natural generalization. Implied by abc.
**Partial results:** Catalan case (k=1) proven 2002; specific k handled.
**Barrier:** abc-implication route blocked by abc itself being open; direct attack stalls.
**Data coupling:** Perfect-power enumeration, exponent-pair tables, abc triples.

---

## 28. Quasiperfect Numbers

**Subfield:** Number theory (perfect-number variants)
**Statement:** Does there exist a positive integer n with σ(n) = 2n + 1?
**Year/Origin:** 19th-century inheritance from perfect-number theory.
**Why it matters:** Sister to odd-perfect-number problem (which IS in the database). If a quasiperfect exists, it must be an odd square > 10^35 with very specific divisor structure.
**Partial results:** None known; brute-force exclusion to large bounds.
**Barrier:** Same arithmetic-density barrier as odd-perfect.
**Data coupling:** σ-function tables, perfect-number computational corpus.

---

## 29. Pollock Tetrahedral Conjecture

**Subfield:** Number theory (Waring-type representation)
**Statement:** Every positive integer is a sum of at most 5 tetrahedral numbers Tn = n(n+1)(n+2)/6.
**Year/Origin:** 1850, F. Pollock.
**Why it matters:** Three-dimensional analog of Lagrange's four-square theorem. Dimension-3 vs dimension-4 representation gap.
**Partial results:** Verified to large bounds. 17 candidate exceptional integers (those needing 5 not 4) catalogued.
**Barrier:** No structural reason 5 is the right bound.
**Data coupling:** Integer-representation tables; Waring-problem corpora.

---

## 30. Euclid-Mullin Sequence

**Subfield:** Number theory (prime sequences)
**Statement:** Define a₁ = 2; a_{n+1} = smallest prime factor of a₁·...·aₙ + 1. Does the sequence contain every prime?
**Year/Origin:** 1963, A. A. Mullin.
**Why it matters:** Tests effectivity of Euclid's-style proofs of prime infinitude. The "5 not yet known to appear" gap is a famous puzzle.
**Partial results:** First several dozen terms computed; smallest missing prime is 5.
**Barrier:** Each new term requires factoring a tower-exponentially-growing integer.
**Data coupling:** Mullin-sequence computation; large-integer factorization records.

---

## 31. Feit-Thompson Divisibility Conjecture

**Subfield:** Number theory / group theory boundary
**Statement:** For distinct primes p, q: (p^q - 1)/(p - 1) is never divisible by (q^p - 1)/(q - 1).
**Year/Origin:** Feit-Thompson 1962 (related to odd-order theorem).
**Why it matters:** A divisibility lemma needed in the original Feit-Thompson proof; theorem now stands without it but the divisibility statement remains independently open.
**Partial results:** Verified for many small (p,q); no structural counterexample.
**Barrier:** No closed-form discriminant for the divisibility.
**Data coupling:** Cyclotomic-polynomial divisibility tables.

---

## 32. Riesel Problem

**Subfield:** Number theory (always-composite arithmetic progressions)
**Statement:** What is the smallest odd k such that k·2ⁿ - 1 is composite for all n ≥ 1?
**Year/Origin:** 1956, H. Riesel.
**Why it matters:** Sister to Sierpiński number problem; together they probe density of "always-composite" residue classes.
**Partial results:** Conjecturally k = 509,203; ~50 candidates remain unresolved.
**Barrier:** Each candidate elimination requires finding ONE prime, but search is sparse.
**Data coupling:** Riesel-sieve project corpus; primality test results at high n.

---

## 33. Sierpiński Number Problem

**Subfield:** Number theory (always-composite arithmetic progressions)
**Statement:** What is the smallest odd k with k·2ⁿ + 1 composite for all n ≥ 1?
**Year/Origin:** 1960, W. Sierpiński.
**Why it matters:** Sister to Riesel. Conjecturally k = 78,557 (Selfridge 1962); pursued by PrimeGrid / Seventeen-or-Bust.
**Partial results:** Down to ~5 candidates remaining.
**Barrier:** Same as Riesel.
**Data coupling:** PrimeGrid / Seventeen-or-Bust corpus.

---

## 34. Hilbert's Tenth Problem over the Rationals

**Subfield:** Logic / number theory boundary
**Statement:** Is there an algorithm that, given a polynomial Diophantine equation, decides whether it has a rational solution?
**Year/Origin:** 1900 (Hilbert); ℚ refinement late 20th c.
**Why it matters:** Over ℤ proved undecidable (DPRM 1970). Over ℚ remains OPEN. A negative answer resolves uniformity questions in arithmetic geometry.
**Partial results:** Mazur uniform-boundedness, if true, implies undecidability over many number fields. Conditional progress under BSD, Mordell.
**Barrier:** Need either explicit Diophantine model of ℤ in ℚ, or a decision procedure.
**Data coupling:** Curves of small genus over ℚ; rational-point datasets; Mazur torsion results.

---

## 35. Congruent Number Problem

**Subfield:** Number theory / elliptic curves
**Statement:** Deterministic algorithm for: is integer n the area of a right triangle with rational sides?
**Year/Origin:** 10th-century Arabic; modern formulation via elliptic curves.
**Why it matters:** Equivalent to determining the rank of Eₙ: y² = x³ - n²x. Tunnell 1983 gives polynomial-time algorithm conditional on BSD.
**Partial results:** Unconditional algorithm for n ≡ 5,6,7 (mod 8). General case relies on BSD.
**Barrier:** BSD itself is open.
**Data coupling:** LMFDB elliptic-curve rank data; Heegner-point algorithms.

---

## 36. Triangulation Conjecture

**Subfield:** Topology
**Statement:** Is every topological manifold homeomorphic to a simplicial complex?
**Year/Origin:** 19th-century inheritance.
**Why it matters:** TRUE in dim ≤3; FALSE in dim ≥5 (Manolescu 2013, Pin(2)-equivariant Seiberg-Witten Floer cohomology obstruction). Boundary at dim 4 remains open and interlaces with smooth-4-Poincaré.
**Partial results:** Manolescu's Pin(2)-cohomology obstruction characterizes high-dim case.
**Barrier:** Dim 4 is the exotic dimension where smooth and topological categories diverge.
**Data coupling:** Triangulated 4-manifold datasets; Kirby diagrams.

---

## 37. Riemannian Zoll Surface Classification

**Subfield:** Differential geometry
**Statement:** Classify all Riemannian metrics on Sⁿ for which every geodesic is closed.
**Year/Origin:** Zoll 1903 (S² with non-round metric).
**Why it matters:** Connects to spectral geometry (Berger conjecture: Zoll implies all Laplacian eigenvalues integers).
**Partial results:** S² Zoll metrics form an infinite-dimensional family (Funk; Guillemin); higher-dim largely unknown.
**Barrier:** No coordinate-free classification; geodesic-flow analysis delicate.
**Data coupling:** Spectral data; geodesic-length spectra; explicit Zoll-metric examples.

---

## 38. Illumination Problem

**Subfield:** Discrete / combinatorial geometry
**Statement:** Is every mirrored polygonal room illuminable from a single point source?
**Year/Origin:** Penrose / Klee, mid-20th c.
**Why it matters:** Tests light-ray dynamics in non-convex billiards; failure regions reveal hyperbolic / chaotic trajectories.
**Partial results:** Tokarsky 1995 constructed a non-illuminable polygonal room (26-sided); some convex cases handled.
**Barrier:** Counterexamples are intricate; positive cases need ergodic-theoretic tools.
**Data coupling:** Polygon-billiards corpus; geodesic-flow datasets.

---

## 39. Erdős-Gyárfás Cycle Conjecture

**Subfield:** Graph theory
**Statement:** Every graph with minimum degree ≥3 contains a cycle of length 2^k for some k ≥ 1.
**Year/Origin:** 1995, Erdős-Gyárfás.
**Why it matters:** Tests how cycle-length structure constrains bounded-min-degree graphs. Connects to Hadwiger's conjecture and graph minor theory.
**Partial results:** Verified for several graph classes (planar, K₄-minor-free).
**Barrier:** Standard cycle-length tools don't isolate powers of 2.
**Data coupling:** Random regular graphs; small-graph enumeration.

---

## 40. Chvátal Toughness Conjecture

**Subfield:** Graph theory (Hamiltonicity)
**Statement:** ∃ constant t₀ such that toughness ≥ t₀ implies Hamiltonian.
**Year/Origin:** 1973, V. Chvátal.
**Why it matters:** Originally conjectured t₀ = 9/4; bounds have moved up. Tests how Hamiltonicity relates to "global connectivity" beyond minimum degree.
**Partial results:** Bauer-Broersma-Veldman 2000 gave non-Hamiltonian graphs with toughness slightly less than 9/4.
**Barrier:** Toughness is NP-hard to compute; structural Hamiltonicity arguments don't naturally use it.
**Data coupling:** Tough-graph corpus; non-Hamiltonian highly-connected graphs.

---

## 41. Painlevé Integrability Classification

**Subfield:** Dynamical systems / ODE theory
**Statement:** Classify ODEs of form y'' = R(x, y, y') (R rational) whose movable singularities are only poles.
**Year/Origin:** Painlevé / Gambier 1900s.
**Why it matters:** Painlevé transcendents appear in random matrix correlation kernels, KdV, gravitational instantons. Classification opens new "function libraries."
**Partial results:** Order-2 done (six canonical PI–PVI); order-3 partial (Cosgrove, Bureau); discrete Painlevé open.
**Barrier:** Painlevé property hard to detect algorithmically; ALAY test necessary not sufficient.
**Data coupling:** Symbolic-computation systems; Painlevé-transcendent corpora.

---

## 42. Mean-Value Polynomial Conjecture (Smale)

**Subfield:** Complex analysis / polynomial theory
**Statement:** For polynomial f of degree d ≥ 2 and z ∈ ℂ, ∃ critical point c with |f(z) - f(c)|/|z - c| ≤ K · |f'(z)| for absolute K.
**Year/Origin:** 1981, Stephen Smale.
**Why it matters:** A "discrete" mean-value theorem. Smale conjectured K = 4 (or K = 1 normalized); current best K bounded by ~d - 1. Matters for Newton's-method convergence.
**Partial results:** Tischler 1989, Crane 2007; small d handled.
**Barrier:** No symmetric tool for all degrees uniformly.
**Data coupling:** Random-polynomial root sets; critical-point distributions.

---

## 43. Erdős-Ko-Rado-Type Generalizations

**Subfield:** Extremal combinatorics
**Statement:** Specific open EKR variants: r-wise intersecting, weighted, vector-space EKR for non-prime-power q, infinite-dim analogs.
**Year/Origin:** Original EKR 1961; generalizations 1990s-present.
**Why it matters:** EKR is the prototype of "concentration on a point" in extremal theory.
**Partial results:** Classical EKR; r-wise (Frankl-Tokushige) partial; vector-space EKR (Hsieh, Frankl-Wilson) for prime-power q.
**Barrier:** Each generalization needs its own structural argument; no universal template.
**Data coupling:** Set-system corpora; vector-space designs over various q.

---

## 44. Kaplansky Direct Finiteness Conjecture

**Subfield:** Algebra (group rings)
**Statement:** For torsion-free group G and field K, the group ring K[G] is directly finite (one-sided invertible ⟹ two-sided invertible).
**Year/Origin:** Kaplansky mid-20th c. (sister to zero-divisor conjecture, which IS in the database).
**Why it matters:** Implied by stronger Kaplansky conjectures. Elek-Szabo 2004 proved direct finiteness for sofic groups (uses Lück approximation). General case open since no known non-sofic group exists.
**Partial results:** Amenable case; sofic case (Elek-Szabo 2004).
**Barrier:** Sofic vs non-sofic dichotomy itself open.
**Data coupling:** Group-ring computational corpora; specific torsion-free groups.

---

## 45. Sensitivity-Adjacent Boolean Function Conjectures

**Subfield:** Theoretical computer science / combinatorics
**Statement:** Sensitivity Conjecture itself was RESOLVED by Hao Huang (2019, ~6-page proof using Cauchy interlacing on signed-edge graphs). Adjacent conjectures remain: tight Boolean-function sensitivity-block-degree relationships; quantum query complexity sharp bounds.
**Year/Origin:** Sensitivity Conjecture 1992 (Nisan-Szegedy); Huang's resolution 2019.
**Why it matters:** A solved problem becomes a calibration anchor — see `aporia/mathematics/solved_problems_genealogy.md` for full backfill. Adjacent open problems remain in tight sensitivity-block bounds.
**Partial results:** Sensitivity Conjecture proved; some adjacent quantum-query bounds open.
**Barrier:** Huang's technique (Cauchy interlacing on signed-edge graphs) is novel but doesn't generalize to all adjacent conjectures.
**Data coupling:** Boolean-function corpus; small-circuit datasets.

---

*Round 2 adds 20 entries (#26-45) to the catalog. Combined catalog now spans 45 problems across two tiers (Round 1: specialist; Round 2: classical-but-less-famous). 12 gaps remain from the 32-gap list — Sierpiński m²-n², Cullen primes, palindromic primes, Fibonacci primes, Kusner L¹, Arnold diffusion, FPU paradox, Ruelle-Takens turbulence, Church-Turing physics thesis, Guralnick-Thompson, Herzog-Schönheim, π·e algebraic independence — queued for Round 3 + batch 12.*

*Aporia, 2026-05-08*
