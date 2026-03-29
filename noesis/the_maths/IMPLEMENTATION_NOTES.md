# Noesis Math Collector — Implementation Notes

## Summary

As of 2026-03-28, the `noesis/the_maths/` directory contains **128 files with 1,174 operations** covering the original 60-field prompt, 24 beyond-list fields, and 44 fields from the ChatGPT suggestions and weird_math_2 prompts.

This document covers the analysis and implementation decisions for prompts _3 through _6.

---

## Prompt _3: Non-Western / Cultural Mathematics (noesis_weird_math_3.md)

**20 fields proposed. 19 built, 1 already existed (CRT folded into existing).**

These are high-value because they introduce genuinely different structural primitives — not "the same math with different notation" but cases where the framing produces operations the Western canon doesn't naturally generate.

### Built

| # | File | Key Operations | Bridge Potential |
|---|------|---------------|-----------------|
| 1 | `babylonian_sexagesimal.py` | Base-60 arithmetic, reciprocal tables, regular number detection (2^a * 3^b * 5^c), geometric-mean solving | Connects to: number theory, continued fractions, finite fields |
| 2 | `egyptian_fractions.py` | Greedy decomposition, 2/n table reconstruction, Erdos-Straus verification, optimal decomposition | Connects to: additive combinatorics, approximation theory, partition theory |
| 4 | `kerala_series.py` | Madhava-Leibniz with correction terms, Madhava sine/cosine series, convergence acceleration comparison | Connects to: pade_approximants, divergent_series, hypergeometric_functions |
| 5 | `plimpton322_triples.py` | Regular-number-constrained Pythagorean triple generation, gap analysis | Connects to: number theory, babylonian_sexagesimal |
| 6 | `rod_calculus.py` | Horner scheme evaluation, Jia Xian triangle, Fangcheng (early Gaussian elimination) | Connects to: computational_algebra, orthogonal_polynomials |
| 7 | `vedic_square.py` | Digital root multiplication tables, Z9 Cayley table, nilpotent/idempotent detection | Connects to: digital_root, finite_fields, modular_arithmetic_exotic |
| 8 | `inca_quipu.py` | Tree-structured hierarchical summation, pendant aggregation, cross-cord checksums | Connects to: coding_theory, graph theory |
| 9 | `mayan_vigesimal.py` | Mixed-radix arithmetic (18x20 irregularity), Long Count, Calendar Round LCM | Connects to: modular_arithmetic_exotic, mixed-radix systems |
| 10 | `wasan_sangaku.py` | Descartes circle theorem, Apollonian gasket, inversive distance, Soddy circles | Connects to: convex_geometry, fractal_dimensions, inversive geometry |
| 11 | `pingala_prosody.py` | Binary meter enumeration, Meru Prastara (Pascal's triangle), fast exponentiation, Hemachandra-Fibonacci | Connects to: pascal_variations, fibonacci_variations, combinatorial_species |
| 12 | `jain_combinatorics.py` | Jain permutation/combination formulas, three-tier infinity classification (finite approximation), Lokavibhaga calculations | Connects to: cardinal_arithmetic, combinatorial_species |
| 13 | `catuskoti_logic.py` | Four-valued truth tables (true/false/both/neither), Catuskoti lattice ops, Belnap bilattice | Connects to: paraconsistent_logic, formal_logic_systems — distinct 4-valued structure |
| 14 | `navya_nyaya_logic.py` | Typed absence (prior/posterior/absolute/mutual), qualifier-qualified relations, structured negation | Connects to: formal_logic_systems, domain_theory — no Western equivalent of typed negation |
| 15 | `sona_lusona.py` | Eulerian path construction on dual lattice, monolinearity testing, symmetry classification | Connects to: spectral_graph_theory, graph_homomorphism |
| 16 | `islamic_geometric_patterns.py` | Wallpaper group detection, girih tile substitution rules, quasi-crystalline generation | Connects to: quasicrystal_mathematics, polytope_combinatorics |
| 17 | `yoruba_signed_digit.py` | Signed-digit representation, minimal sum/difference decomposition, NAF comparison | Connects to: elliptic_curves (NAF scalar multiplication), redundant number systems |
| 18 | `warlpiri_kinship.py` | D4 group multiplication, section system composition, marriage rule constraints | Connects to: representation_theory, coxeter_groups, constraint_feasibility |
| 19 | `inka_yupana.py` | Fibonacci-base arithmetic, Zeckendorf decomposition, irregular-base carry propagation | Connects to: fibonacci_variations, non-standard bases |
| 20 | `bambara_divination.py` | GF(2)^4 arithmetic, XOR figure combination, transformation group orbits | Connects to: finite_fields, coding_theory, cellular_automata |

### Skipped

| # | Field | Reason |
|---|-------|--------|
| 3 | Chinese Remainder Theorem (Sunzi) | Already implemented in `modular_arithmetic_exotic.py` (chinese_remainder_solve). Calendar cycle ops folded into `mayan_vigesimal.py` as a general LCM/mixed-radix pattern. |

---

## Prompt _4: Astrophysics / QFT / Fringe Physics (noesis_weird_math_4.md)

**30 fields proposed. 22 built, 8 skipped.**

The computable core of theoretical physics is rich territory. We built everything that has clean, bounded numerical operations. We skipped fields where implementation would require either faking the math or unbounded computation.

### Built

| # | File | Key Operations | Bridge Potential |
|---|------|---------------|-----------------|
| 1 | `kerr_geodesics.py` | ISCO vs spin, photon sphere, frame-dragging, Carter constant, ergosphere | Connects to: elliptic_curves (elliptic integrals), dynamical_systems |
| 2 | `penrose_diagrams.py` | Conformal compactification, causal diamond, null geodesic tracing | Connects to: convex_geometry, catastrophe_theory |
| 3 | `gravitational_lensing.py` | Lens equation, magnification tensor, critical curves, caustics | Connects to: catastrophe_theory, computational_algebra (polynomial roots) |
| 4 | `friedmann_equations.py` | Scale factor evolution, Hubble parameter, lookback time, comoving distance | Connects to: dynamical_systems, optimization_landscapes |
| 6 | `stellar_structure.py` | Lane-Emden integration, Chandrasekhar limit, TOV equation | Connects to: orthogonal_polynomials, dynamical_systems |
| 7 | `cosmic_topology.py` | Fundamental domain construction, Laplacian eigenmodes on flat tori, covering spaces | Connects to: spectral_graph_theory, lattice_theory |
| 8 | `feynman_diagram_algebra.py` | Symanzik polynomials, symmetry factors, degree of divergence, one-loop Passarino-Veltman | Connects to: matroid_theory, spectral_graph_theory, extremal_graph_theory — **HIGH BRIDGE VALUE** |
| 12 | `lattice_gauge_theory.py` | Wilson loop, plaquette action, Polyakov loop, link variable updates | Connects to: percolation_theory, random_matrix_theory, finite_fields |
| 13 | `tqft.py` | Frobenius algebra multiplication/comultiplication, cobordism composition, partition functions on surfaces | Connects to: homological_algebra, representation_theory, category_composition |
| 16 | `pseudo_riemannian.py` | Geodesics in (p,q) signature, wave equation well-posedness, isometry group classification | Connects to: geometric_algebra, clifford_algebra |
| 18 | `tropical_qft.py` | Tropical Feynman rules, tropical partition function, tropical curve counting | Connects to: tropical_geometry, tropical_semirings, tropical_linear_algebra |
| 19 | `p_adic_physics.py` | Freund-Witten amplitude, adelic product formula, Bruhat-Tits tree path integral | Connects to: p_adic_numbers, zeta_functions, l_functions |
| 22 | `causal_set_theory.py` | Poisson sprinkling, causal matrix, Benincasa-Dowker action, dimension estimation | Connects to: lattice_theory, partial orders, percolation_theory |
| 23 | `octonion_qm.py` | Albert algebra multiplication, exceptional Jordan eigenvalues, Freudenthal-Tits magic square | Connects to: quaternion_octonion, representation_theory — magic square derives all exceptional Lie groups |
| 26 | `unparticle_physics.py` | Fractional-dimensional phase space, spectral functions, interference amplitudes | Connects to: fractional_calculus, fractal_dimensions |
| 28 | `spin_foam.py` | 6j-symbol computation, vertex amplitudes, partition function on simplicial complex | Connects to: representation_theory, homological_algebra |
| 29 | `fractional_qm.py` | Fractional Schrodinger equation, Levy path integral, fractional energy levels, barrier tunneling | Connects to: fractional_calculus, random_matrix_theory |
| 5 | `gravitational_choreographies.py` | Figure-eight orbit integration, Floquet stability, phase-offset verification | Connects to: dynamical_systems, optimization_landscapes |
| 9 | `rg_flow_qft.py` | One-loop beta functions, fixed point finding, anomalous dimensions, Callan-Symanzik | Connects to: renormalization_group, dynamical_systems |
| 20 | `noncommutative_geometry.py` | Spectral action (toy), Connes distance, heat kernel coefficients, Dirac spectrum | Connects to: spectral_transforms, clifford_algebra |
| 21 | `twistor_theory.py` | Incidence relation, Penrose transform (simple cases), conformal invariants | Connects to: exterior_calculus, geometric_algebra |
| 30 | `timescape_cosmology.py` | Buchert averaging, backreaction scalar, dressed vs bare Hubble parameter | Connects to: friedmann_equations, ergodic_theory |

### Skipped

| # | Field | Reason |
|---|-------|--------|
| 10 | Anomaly polynomials | Full Chern character and Atiyah-Singer index require algebraic topology machinery beyond bounded numpy. Simplified cases would be misleading — the power is in the general framework. |
| 11 | Instanton mathematics | BPST profile alone is a scalar function; the interesting operations (moduli spaces, multi-instanton solutions) require unbounded algebraic geometry. Would produce a trivially thin module. |
| 14 | Amplituhedron / positive geometry | BCFW recursion for small cases is doable but the positive Grassmannian cell decomposition requires serious algebraic geometry. High fake risk — the operations that make this interesting (sign-flip characterization, momentum twistors) need deep infrastructure. |
| 15 | F-theory compactification | Kodaira fiber classification is a lookup table; actual elliptic fibration construction requires algebraic geometry that can't be honestly reduced to numpy operations. Building a lookup table would be faking it. |
| 17 | Surreal-valued fields | Surreal-valued path integrals are purely formal — no one has computed them. "Surreal regularization" compared to dimensional regularization would be speculative, not mathematical. |
| 24 | Hyper-Kahler quotient | Moment map computation for toy cases is possible but the quotient construction, Kahler potential, and L2 harmonic forms require differential geometry infrastructure. The interesting math is in the general construction, not toy cases. |
| 25 | Wheeler-DeWitt equation | Minisuperspace WKB is a 1D Schrodinger equation — trivially thin. Full superspace is infinite-dimensional. The module would either be a single ODE solver or fake. |
| 27 | Monster moonshine / VOA | Already have `moonshine_theory.py`. VOA partition functions would require vertex operator algebra infrastructure that can't be honestly reduced to numpy. The existing module already captures the j-function coefficients and representation dimension checks. |

---

## Prompt _5: Non-Standard Bases (noesis_weird_math_5.md)

**21 fields proposed. All 21 built.**

Base arithmetic is concrete, fast, and computationally bounded. Every field here produces genuine operations with clear type signatures. The bridge potential is enormous — base representation connects number theory, automata theory, fractal geometry, group cohomology, and combinatorics.

### Built

| # | File | Key Operations | Bridge Potential |
|---|------|---------------|-----------------|
| 1 | `balanced_ternary.py` | Balanced ternary arithmetic, rounding-by-truncation, radix economy | Most efficient integer base; carry structure differs from binary |
| 2 | `negabinary.py` | Negabinary addition (bidirectional carry!), multiplication, sign-free representation | Every integer from unsigned digits — structural inversion |
| 3 | `complex_bases.py` | Base (-1+i) arithmetic, Gaussian integer representation, twindragon fractal | Connects to: fractal_dimensions, elliptic_curves |
| 4 | `fibonacci_base.py` | Zeckendorf encoding, Fibonacci-base addition (substitution carry rules) | Connects to: fibonacci_variations, symbolic_dynamics |
| 5 | `factoradic.py` | Factoradic conversion, Lehmer code to permutation, factorial-base arithmetic | **Natural encoding of permutations** — connects combinatorics to positional notation |
| 6 | `primorial_base.py` | Primorial encoding, digit patterns for primes, CRT connection | Connects to: modular_arithmetic_exotic, number theory |
| 7 | `mixed_radix.py` | General mixed-radix arithmetic, optimal radix selection, combinatorial number system | Connects to: mayan_vigesimal, coding_theory |
| 8 | `redundant_representations.py` | Signed binary, carry-save, constant-time addition (no carry propagation!) | Connects to: yoruba_signed_digit, interval_arithmetic |
| 9 | `bijective_bases.py` | Bijective-base arithmetic, Excel column naming (bijective-26), string-integer bijection | Connects to: formal_language_theory |
| 10 | `non_integer_bases.py` | Base-phi, base-e, base-pi arithmetic, golden string | Connects to: fibonacci_base, continued_fractions |
| 11 | `p_adic_expansions.py` | Infinite-left digit computation, periodic detection, p-adic interpolation | Connects to: p_adic_numbers, p_adic_physics |
| 12 | `symmetric_bases.py` | Symmetric-base rounding (always truncation), signed-digit multiplication | Connects to: balanced_ternary, redundant_representations |
| 13 | `digit_dynamics_arbitrary_base.py` | Digital root/persistence in any base, persistence landscape comparison | Extends: digital_root to arbitrary bases |
| 14 | `automata_base_theory.py` | b-automatic set construction, Cobham's theorem verification, base-dependent regularity | Connects to: automata_theory, automata_infinite_words — **three-way bridge** |
| 15 | `normal_numbers.py` | Digit frequency analysis, normality testing, Champernowne construction | Connects to: algorithmic_randomness, kolmogorov_complexity |
| 16 | `smith_numbers.py` | Smith/Niven/Harshad detection in arbitrary bases, repunit properties | Connects to: mobius_functions, number theory |
| 17 | `carries_as_cocycles.py` | Carry sequence extraction, carry correlation, H2(Z/bZ, Z) cocycle construction | **THE GEM.** Elementary arithmetic → group cohomology. If Noesis finds this bridge independently, it's a real result. Connects to: homological_algebra, representation_theory |
| 18 | `rauzy_fractals.py` | Beta-expansion, Rauzy fractal boundary, Pisot number detection, tiling verification | Connects to: fractal_dimensions, symbolic_dynamics, dynamical_systems — **four-way bridge** |
| 19 | `matrix_bases.py` | 2D base expansion, digit set tiling, Haar wavelet connection | Connects to: multiscale_operators, linear algebra |
| 20 | `residue_number_systems.py` | RNS encoding/decoding, parallel carry-free arithmetic, overflow detection | Connects to: modular_arithmetic_exotic, coding_theory |
| 21 | `base_invariant_properties.py` | Invariance testing, minimal base for property, base-independent canonical forms | Meta-analysis framework for all base-dependent modules |

### Skipped

None. All 21 are concrete and computable.

---

## Prompt _6: Undeciphered Systems (noesis_weird_math_6.md)

**18 systems proposed. Consolidated into 3 modules.**

The individual scripts lack corpus data, and building 18 files named after specific undeciphered writing systems would be dishonest — we're not implementing "Rongorongo mathematics." What we CAN implement honestly are the general analytical tools that would be applied to these systems. These tools are valuable in their own right for analyzing ANY symbolic sequence.

### Built (3 consolidated modules)

| File | Key Operations | What It Captures |
|------|---------------|-----------------|
| `context_dependent_arithmetic.py` | Multi-radix arithmetic where base depends on semantic domain, context-switching rules, cross-system consistency checking | Proto-Elamite concept: the radix is a function of what you're counting. Also captures Mayan mixed-base irregularity. |
| `symbol_analysis_toolkit.py` | Entropy rate at multiple scales, Zipf compliance testing, vocabulary growth (Heaps' law), bigram/trigram transition matrices, writing-vs-decoration discrimination, information capacity estimation, positional frequency analysis, script comparison metrics | General-purpose tools for analyzing ANY symbolic sequence. Applicable to Indus Valley, Phaistos Disc, Vincha symbols, Voynich manuscript, etc. |
| `geometric_reading_transforms.py` | Boustrophedon transform, reverse boustrophedon (Rongorongo), spiral reading order, positional encoding schemes, symmetry-based reading direction detection | Computable geometric transformations applied to sequential symbol reading. |

### Skipped (as individual modules)

| # | System | Reason |
|---|--------|--------|
| 2 | Linear A fractions | Contested fraction values make "correct" arithmetic undefined. The constraint-satisfaction aspect is captured by the symbol analysis toolkit. |
| 3 | Indus Valley | No corpus data in the module. Statistical tools captured in symbol_analysis_toolkit. |
| 5 | Phaistos Disc | Single object, 241 signs. Analysis tools in symbol_analysis_toolkit. |
| 6-11 | Various scripts | Without corpus data, these would be empty shells. The analytical tools are in the consolidated modules. |
| 12-18 | Archaeological objects | Statistical tests captured in symbol_analysis_toolkit. Individual modules would be thin wrappers around the same functions with different docstrings. |

---

## Fields Flagged as Highest Bridge Value

These are the modules most likely to produce novel cross-field connections when composed in the tensor:

1. **`carries_as_cocycles.py`** — Elementary school addition carries are secretly group cohomology cocycles. If Noesis finds this bridge independently, it validates that the system surfaces real mathematical structure.

2. **`feynman_diagram_algebra.py`** — Graph polynomials (Symanzik) connect directly to matroid theory, Tutte polynomial, and spectral graph theory. A bridge hub.

3. **`catuskoti_logic.py`** — Four-valued logic (true/false/both/neither) is structurally distinct from both Boolean logic and existing paraconsistent logic. Directly relevant to epistemic honesty under contradictory evidence.

4. **`rauzy_fractals.py`** — A single object that bridges number theory, dynamical systems, fractal geometry, and algebraic number theory simultaneously.

5. **`factoradic.py`** — Permutations ARE factoradic numbers. The natural encoding of combinatorics as positional notation.

6. **`navya_nyaya_logic.py`** — Typed negation with four absence subtypes has no Western equivalent until very recently. Genuinely different logical operations.

7. **`tropical_qft.py`** — Clean algebraic substitution (sum→min, product→sum) applied to quantum field theory. Composes two existing entries through a well-defined transformation.

8. **`automata_base_theory.py`** — Cobham's theorem connects automata theory to number theory through base representation. Three-way bridge.

9. **`causal_set_theory.py`** — Posets + geometry + discretization. Connects lattice theory, partial orders, and percolation theory to quantum gravity.

10. **`octonion_qm.py`** — The Freudenthal-Tits magic square derives all five exceptional Lie groups from composition algebras. Non-associativity propagating through layers of abstraction.

---

## Implementation Stats After This Round

| Metric | Before | After |
|--------|--------|-------|
| Files | 128 | ~193 |
| Operations | 1,174 | ~1,750+ |
| Fields with zero Western-canon overlap | ~10 | ~30+ |
| Pairwise compositions | 1,377,102 | ~3,000,000+ |

---

## What's Left / Future Directions

If more fields are desired, the richest unexplored veins are:

- **Proof assistants / type theory** — Curry-Howard correspondence makes proofs = programs. The operations are beta-reduction, unification, type inference. Bridges logic to computation.
- **Langlands program** (toy cases) — The modularity theorem (proved for elliptic curves = Wiles) connects number theory to representation theory. Toy cases are computable.
- **Motivic integration** — Kontsevich's theory assigns "volumes" to algebraic varieties over arbitrary fields. Arc space approximations are computable.
- **Derived categories** — The natural home of homological algebra. Shift functors, distinguished triangles, t-structures. Toy cases on small abelian categories are bounded.
- **Condensed mathematics** — Clausen-Scholze's new foundations. Probably too abstract for numpy, but the underlying idea (replace topological spaces with condensed sets) has computable finite approximations.
