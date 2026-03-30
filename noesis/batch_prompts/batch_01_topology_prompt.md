# BATCH SPOKE GENERATION — Fill the Grid

## Your Task

For each hub listed below, evaluate ALL 9 damage operators and classify each cell as FILLED, EMPTY_PLAUSIBLE, or IMPOSSIBLE.

### The 9 Damage Operators
| # | Operator | What it does | Example |
|---|----------|-------------|---------|
| 1 | DISTRIBUTE | Spread damage uniformly | Equal temperament |
| 2 | CONCENTRATE | Localize damage | Wolf interval |
| 3 | TRUNCATE | Remove problematic region | Bandlimiting |
| 4 | EXPAND | Add resources/structure | Error correction |
| 5 | RANDOMIZE | Convert to probability | Monte Carlo |
| 6 | HIERARCHIZE | Push to meta-level | Combined cycle engines |
| 7 | PARTITION | Split domain | Gain scheduling |
| 8 | QUANTIZE | Force onto discrete grid | 12-TET tuning |
| 9 | INVERT | Reverse direction | Heat pumps |

## Output Format

Return a JSON array. For each hub, provide hub_id and a 9-element operator_grid:

```json
[
  {
    "hub_id": "BROUWER_FIXED_POINT",
    "operator_grid": [
      {"operator": "DISTRIBUTE", "status": "FILLED", "resolution_name": "Approximate fixed points", "description": "Distribute error across epsilon-approximate fixed points.", "primitive_sequence": ["MAP","SYMMETRIZE"], "cross_domain_analog": "equal_temperament"},
      {"operator": "CONCENTRATE", "status": "IMPOSSIBLE", "description": "Fixed points are global; cannot localize."},
      {"operator": "TRUNCATE", "status": "EMPTY_PLAUSIBLE", "description": "Restrict to subdomain where fixed point is known."}
    ]
  }
]
```

Rules:
- FILLED = known technique from published literature. Name it.
- IMPOSSIBLE = structural reason why this operator CANNOT apply.
- EMPTY_PLAUSIBLE = could exist but you can't name a specific technique.

---

## HUBS TO EVALUATE: Topology & Geometry (27 hubs)

### Hub 1: BANACH_TARSKI
- **Name:** Banach Tarski *(look up the formal impossibility statement)*

### Hub 2: BROUWER_FIXED_POINT
- **Impossibility:** Any continuous self-map of a compact convex set must have a fixed point; it is impossible to continuously retract a disk onto its boundary | SOURCE: L.E.J. Brouwer, 1911. Uber Abbildung von Mannigfaltigkeiten. Mathematische Annalen 71(1):97-115
- **Source:** MAP(continuous) -> COMPLETE(retraction) FAILS -> BREAK_SYMMETRY(boundary) | WHY: The identity map on the boundary has nontrivial degree; extending it to a retraction would collapse homology, contradic

### Hub 3: BURNSIDE_IMPOSSIBILITY
- **Name:** Burnside Impossibility *(look up the formal impossibility statement)*

### Hub 4: COVERING_SPACE_OBSTRUCTION
- **Impossibility:** A continuous map lifts to a covering space if and only if its induced fundamental group homomorphism lands in the covering subgroup; otherwise lifting is impossible | SOURCE: Lifting criterion theorem, formalized by Seifert and Threlfall 1934; modern treatment in Hatcher Ch.1
- **Source:** MAP(continuous) -> EXTEND(lift) FAILS -> BREAK_SYMMETRY(fundamental_group) | WHY: The long exact sequence of homotopy groups for the fibration forces pi_1 compatibility; loops in the base that are not

### Hub 5: DEHN_IMPOSSIBILITY
- **Name:** Dehn Impossibility *(look up the formal impossibility statement)*

### Hub 6: DEHN_SURGERY_OBSTRUCTION
- **Impossibility:** Every closed orientable 3-manifold arises from surgery on a link in S^3, but the surgery coefficients are constrained by linking matrix signature; not all coefficient choices yield distinct manifolds | SOURCE: Lickorish 1962 A representation of orientable combinatorial 3-manifolds; Wallace 1960; Kir
- **Source:** COMPOSE(surgeries) -> COMPLETE(classification) FAILS -> BREAK_SYMMETRY(Kirby_moves) | WHY: Kirby moves generate equivalences between surgery presentations; the resulting quotient is the set of 3-manif

### Hub 7: EULER_CHARACTERISTIC_OBSTRUCTION
- **Impossibility:** A compact manifold admits a nowhere-vanishing vector field if and only if its Euler characteristic is zero; nonzero chi forces singularities | SOURCE: Poincare 1885, Hopf 1926. Vektorfelder in n-dimensionalen Mannigfaltigkeiten. Mathematische Annalen 96:225-249
- **Source:** MAP(tangent_field) -> COMPLETE(global_nonvanishing) FAILS -> BREAK_SYMMETRY(index_sum) | WHY: Poincare-Hopf theorem forces the sum of indices of zeroes to equal chi(M); when chi != 0, at least one sin

### Hub 8: EULER_POLYHEDRON_OBSTRUCTION
- **Name:** Euler Polyhedron Obstruction *(look up the formal impossibility statement)*

### Hub 9: GAUSS_BONNET_CURVATURE_TOPOLOGY
- **Impossibility:** The integral of Gaussian curvature over a closed surface is locked to 2*pi*chi; it is impossible to change total curvature without changing topology | SOURCE: Gauss 1827 Disquisitiones Generales; Bonnet 1848; Chern 1944 (higher dimensions). Allendoerfer-Weil 1943 for general case
- **Source:** REDUCE(integrate_curvature) -> MAP(to_topology) FORCED -> BREAK_SYMMETRY(metric_freedom_lost) | WHY: Gauss-Bonnet is a topological invariant computed from geometry; the integral is insensitive to loca

### Hub 10: HAIRY_BALL
- **Name:** Hairy Ball *(look up the formal impossibility statement)*

### Hub 11: IMPOSSIBILITY_BANACH_TARSKI_PARADOX
- **Impossibility:** No finitely additive, isometry-invariant measure can be defined on all subsets of R^3 that assigns positive measure to the unit ball. Equivalently: a solid ball can be decomposed into finitely many pieces and reassembled into two copies of the original ball using rigid motions alone.
- **Source:** COMPOSE(rigid_motions) → COMPLETE(measure_on_all_subsets) FAILS → BREAK_SYMMETRY(restrict_to_Lebesgue_measurable_sets) | The free group F_2 embeds in SO(3) via rotations. The Hausdorff paradox on S^2 

### Hub 12: IMPOSSIBILITY_COMPETITIVE_EQUILIBRIUM_INDIVISIBLE
- **Impossibility:** Competitive equilibrium (Walrasian equilibrium with integer allocations) may fail to exist when goods are indivisible and agents have general preferences; when it exists, it may not be Pareto efficient or envy-free simultaneously || CLOSURE FAILURE: Convexity of preferences and production sets is es
- **Source:** Convexity of preferences and production sets is essential for existence via Kakutani's fixed-point theorem. With indivisible goods, the aggregate excess demand correspondence is not convex-valued: sma

### Hub 13: IMPOSSIBILITY_CRAMER_RAO_BOUND
- **Impossibility:** For any unbiased estimator θ̂ of a parameter θ, the variance satisfies Var(θ̂) ≥ 1/I(θ), where I(θ) is the Fisher information. No unbiased estimator can have variance below this bound.
- **Source:** COMPOSE(unbiased_estimator) → COMPLETE(zero_variance_estimation) FAILS → BREAK_SYMMETRY(allow_bias_to_reduce_MSE) | The Cauchy-Schwarz inequality applied to the score function and the estimator yields

### Hub 14: IMPOSSIBILITY_KLEIBER_METABOLIC_SCALING
- **Impossibility:** West, Brown & Enquist (1997) derived from first principles that metabolic rate B scales as B ~ M^(3/4) for organisms with fractal-like distribution networks that minimize transport costs while serving all cells. An organism cannot simultaneously: have a space-filling distribution network, minimize t
- **Source:** COMPOSE(space-filling + cost-minimization + 3D embedding) -> COMPLETE(linear scaling) FAILS -> BREAK_SYMMETRY(accept sublinear scaling or non-fractal network)

### Hub 15: IMPOSSIBILITY_KOLMOGOROV_SUPERPOSITION_COMPUTATIONAL_BARRIER
- **Impossibility:** Kolmogorov's Superposition Theorem (1957) represents any continuous multivariate function as compositions and sums of univariate functions, BUT the inner functions are highly non-smooth (typically nowhere-differentiable), making the representation computationally intractable for smooth approximation
- **Source:** COMPOSE(univariate_superposition) → COMPLETE(smooth_multivariate_representation) FAILS → BREAK_SYMMETRY(sacrifice_exactness_for_smoothness) | The inner functions φ_q are universal (independent of f) b

### Hub 16: IMPOSSIBILITY_MARGOLUS_LEVITIN_SPEED_LIMIT
- **Impossibility:** A quantum system with average energy E above the ground state cannot transition to an orthogonal state faster than time t_min = pi*hbar/(2E); computation speed is fundamentally bounded by energy || CLOSURE FAILURE: The overlap |<psi(0)|psi(t)>| between initial and evolved states is bounded below by 
- **Source:** The overlap |<psi(0)|psi(t)>| between initial and evolved states is bounded below by cos^2(Et/hbar) for short times, from the Mandelstam-Tamm inequality extended by Margolus-Levitin. Orthogonality req

### Hub 17: IMPOSSIBILITY_NASH_PPAD_HARDNESS
- **Impossibility:** No polynomial-time algorithm can compute a Nash equilibrium in general normal-form games unless PPAD = P || CLOSURE FAILURE: Brouwer fixed-point theorem guarantees existence but the corresponding computational problem (finding the fixed point) is PPAD-complete. The proof reduces END-OF-LINE to Nash,
- **Source:** Brouwer fixed-point theorem guarantees existence but the corresponding computational problem (finding the fixed point) is PPAD-complete. The proof reduces END-OF-LINE to Nash, showing that the combina

### Hub 18: IMPOSSIBILITY_WEIERSTRASS_APPROXIMATION_DISCONTINUITY
- **Impossibility:** No sequence of polynomials can converge uniformly to a discontinuous function on a compact interval. Polynomial approximation in the sup-norm is impossible outside C[a,b].
- **Source:** COMPOSE(polynomial_sequence) → COMPLETE(all_bounded_functions) FAILS → BREAK_SYMMETRY(weaken_norm_to_Lp) | Polynomials are continuous, and uniform limits of continuous functions are continuous (a topo

### Hub 19: KAKUTANI_FIXED_POINT
- **Impossibility:** Any upper semicontinuous set-valued map from a compact convex set to itself with convex values must have a fixed point; no escape is possible under these conditions | SOURCE: Shizuo Kakutani, 1941. A generalization of Brouwer's fixed point theorem. Duke Mathematical Journal 8(3):457-459
- **Source:** EXTEND(point-to-set) -> MAP(usc) -> COMPLETE(fixed_point) FORCED | WHY: Approximate selections via Michael selection theorem reduce to Brouwer; convexity of values prevents escape through averaging

### Hub 20: KNOT_INVARIANT_INCOMPLETENESS
- **Impossibility:** No single computable knot invariant can distinguish all non-equivalent knots; every known invariant has blind spots where distinct knots receive identical values | SOURCE: Multiple results: Jones polynomial fails to distinguish mutant knots (Morton 1986); unknot detection via Jones polynomial is ope
- **Source:** MAP(knot_to_invariant) -> COMPLETE(discrimination) FAILS -> COMPOSE(multiple_invariants) | WHY: Each invariant captures only partial topological information; mutation operations preserve many polynomi

### Hub 21: NASH_ISOMETRIC_EMBEDDING
- **Impossibility:** C^1 isometric embeddings are flexible (Nash-Kuiper: can embed flat torus in R^3) but C^2 embeddings are rigid (must respect curvature). Smoothness and geometry cannot be simultaneously free | SOURCE: Nash 1954 C^1 isometric embeddings; Nash 1956 smooth case. Kuiper 1955. Borisov 2004 fractional regu
- **Source:** MAP(embed_isometrically) -> COMPLETE(smooth+isometric) FAILS at C^1/C^2 boundary -> BREAK_SYMMETRY(regularity) | WHY: Below C^2 the convex integration method allows wild solutions (h-principle); at C^

### Hub 22: POINCARE_DUALITY_OBSTRUCTION
- **Impossibility:** Not every space satisfying Poincare duality is a manifold; surgery theory obstructions (Wall groups) prevent realization of Poincare duality spaces as manifolds | SOURCE: C.T.C. Wall, 1970. Surgery on Compact Manifolds. London Mathematical Society Monographs
- **Source:** DUALIZE(homology<->cohomology) -> COMPLETE(manifold_structure) FAILS -> BREAK_SYMMETRY(surgery_obstruction) | WHY: The surgery exact sequence contains L-group obstructions; the signature and Arf invar

### Hub 23: RIGIDITY_MOSTOW
- **Impossibility:** Finite-volume hyperbolic manifolds of dimension >= 3 have no continuous deformations; the geometry is completely determined by the fundamental group. Moduli space is a single point | SOURCE: G. Daniel Mostow, 1968. Quasi-conformal mappings in n-space and the rigidity of hyperbolic space forms. Publi
- **Source:** MAP(deform_metric) -> EXTEND(moduli_space) FAILS -> SYMMETRIZE(unique_geometry) | WHY: In dim >= 3, quasi-conformal maps between hyperbolic manifolds must be conformal (isometric). The boundary extens

### Hub 24: TOPOLOGICAL_INVARIANCE_OF_DIMENSION
- **Name:** Topological Invariance Of Dimension *(look up the formal impossibility statement)*

### Hub 25: TOPOLOGICAL_MANIFOLD_DIMENSION4
- **Impossibility:** R^4 is the unique Euclidean space admitting uncountably many exotic smooth structures; classification of smooth 4-manifolds is algorithmically undecidable. Smooth = topological fails uniquely in dimension 4 | SOURCE: Donaldson 1983 (gauge theory obstructions); Freedman 1982 (topological classificati
- **Source:** MAP(topological->smooth) -> COMPLETE(unique_smoothing) FAILS -> BREAK_SYMMETRY(gauge_theory_invariants) | WHY: Donaldson's theorem shows the intersection form constrains smooth structures via Yang-Mil

### Hub 26: WHITNEY_EMBEDDING_BOUND
- **Name:** Whitney Embedding Bound *(look up the formal impossibility statement)*

### Hub 27: WHITNEY_EMBEDDING_OBSTRUCTION
- **Impossibility:** An n-dimensional manifold cannot always be embedded in R^(2n-1); dimension 2n is necessary in general. Characteristic class obstructions prevent lower-dimensional embeddings | SOURCE: Hassler Whitney, 1936. Differentiable manifolds. Annals of Mathematics 37(3):645-680; Whitney 1944 self-intersection
- **Source:** MAP(embed) -> REDUCE(ambient_dim) FAILS -> BREAK_SYMMETRY(self_intersection) | WHY: Stiefel-Whitney classes provide mod-2 obstructions; the normal bundle must admit sections, and characteristic class 

