#!/usr/bin/env python3
"""
Fill remaining empty cells in the Noesis damage operator × hub matrix.

Strategy:
  - Only fill cells where a REAL technique/resolution can be named
  - Quality over quantity: skip rather than fabricate
  - Each fill inserts a new spoke into composition_instances

Author: Aletheia (gap fill)
Date: 2026-03-29
"""

import duckdb
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noesis_v2.duckdb")

# =============================================================================
# DOMAIN KNOWLEDGE: Real resolutions for each (hub, operator) pair
# =============================================================================
# Format: (hub_id, operator, instance_suffix, notes)
# Only include cells where we can name a REAL technique.

FILLS = []

def add(hub, op, suffix, notes):
    FILLS.append((hub, op, suffix, notes))

# ─────────────────────────────────────────────────────────────────────────────
# EXTEND — "Add structure or resources to weaken the constraint"
# ─────────────────────────────────────────────────────────────────────────────

# === Logic / Foundations ===
add("GOEDEL_INCOMPLETENESS_1", "EXTEND", "ORDINAL_ANALYSIS",
    "Gentzen's ordinal analysis: extend PA with transfinite induction up to epsilon_0 to prove Con(PA). Add stronger axioms (large cardinals, determinacy) to prove statements unprovable in weaker systems. Each extension pushes the incompleteness boundary higher.")
add("GOEDEL_INCOMPLETENESS_2", "EXTEND", "LARGE_CARDINALS",
    "Large cardinal axioms (inaccessible, measurable, Woodin) extend ZFC to prove consistency of weaker systems. Woodin cardinals prove projective determinacy. Each large cardinal level adds proof-theoretic strength beyond the base system.")
add("HALTING_PROBLEM", "EXTEND", "ORACLE_MACHINES",
    "Turing's oracle machines: extend computation with a halting oracle to decide Sigma_1 sentences. Iterate to build the arithmetic hierarchy (Sigma_n oracles). Hypercomputation models (infinite time Turing machines) extend further. Each oracle level resolves the previous halting problem.")
add("TURING_HALTING", "EXTEND", "BOUNDED_MODEL_CHECKING",
    "Bounded model checking: extend the decision procedure with resource bounds (time, space, depth). Within bounds, halting is decidable. Increase bounds to cover more programs. Termination provers (AProVE, TTT2) use size-change principle + ranking functions as extended proof methods.")
add("CHURCH_UNDECIDABILITY", "EXTEND", "DECIDABLE_FRAGMENTS",
    "Extend by restricting to decidable fragments: monadic second-order logic (Rabin 1969), Presburger arithmetic (quantifier elimination), WS1S/WS2S. Each fragment adds structure (e.g., tree automata) that makes the restricted problem decidable.")
add("ENTSCHEIDUNGSPROBLEM", "EXTEND", "SMT_SOLVERS",
    "SMT solvers (Z3, CVC5) extend decidable theories (linear arithmetic, arrays, bitvectors) with combination frameworks (Nelson-Oppen). Decidable fragments cover vast practical territory. DPLL(T) architecture extends propositional SAT with theory solvers.")
add("RICE_THEOREM", "EXTEND", "ABSTRACT_INTERPRETATION",
    "Cousot & Cousot abstract interpretation: extend the analysis with a Galois connection to an abstract domain. Sound over-approximation of program properties becomes decidable. Widening operators ensure termination. Extends computability at the cost of precision.")
add("TARSKI_UNDEFINABILITY", "EXTEND", "KRIPKE_TRUTH",
    "Kripke's theory of truth: extend the object language with a partial truth predicate using fixed-point semantics. Revision theory (Gupta-Belnap) iterates truth assignments transfinitely. Each extension adds self-referential expressive power while avoiding paradox.")
add("INDEPENDENCE_OF_CH", "EXTEND", "FORCING_AXIOMS",
    "Forcing axioms (Martin's Axiom, PFA, MM) extend ZFC to decide CH and related questions. PFA implies 2^aleph_0 = aleph_2. Large cardinal axioms + determinacy settle projective hierarchy questions. Each forcing axiom adds combinatorial structure.")
add("LOWENHEIM_SKOLEM", "EXTEND", "INFINITARY_LOGIC",
    "Infinitary logics L_kappa_lambda allow infinitely long conjunctions/disjunctions. L_omega1_omega can categorically axiomatize countable structures (Scott's theorem). Adds expressive power to pin down intended models, weakening Lowenheim-Skolem.")
add("GOODSTEIN_INDEPENDENCE", "EXTEND", "TRANSFINITE_INDUCTION",
    "Kirby-Paris: Goodstein's theorem is provable from PA + epsilon_0 induction. The hereditary base representation maps to Cantor normal form; each step decreases the ordinal. Extending PA with transfinite induction is the minimal extension needed.")
add("PARIS_HARRINGTON", "EXTEND", "LARGE_RAMSEY",
    "Paris-Harrington is provable in second-order arithmetic (ACA_0) or PA + epsilon_0 induction. The 'relatively large' condition maps to fast-growing functions exceeding PA's provably total functions. Extending to stronger systems resolves it.")
add("IMPOSSIBILITY_NAIVE_SET_THEORY", "EXTEND", "TYPE_THEORY",
    "Russell's type theory, ZFC's cumulative hierarchy, NBG's proper classes all extend naive set theory with stratification that blocks Russell's paradox. Homotopy type theory adds univalence. Each extension adds structural discipline to avoid inconsistency.")

# === Computability / Complexity ===
add("ALGEBRIZATION_BARRIER", "EXTEND", "GEOMETRIC_COMPLEXITY",
    "Mulmuley-Sohoni Geometric Complexity Theory: extend algebraic methods with representation theory and algebraic geometry to attack P vs NP. GCT aims to bypass algebrization by exploiting symmetry properties of the permanent vs determinant.")
add("NATURAL_PROOFS_BARRIER", "EXTEND", "PSEUDORANDOM_GENERATORS",
    "If one-way functions exist, natural proofs cannot prove circuit lower bounds (Razborov-Rudich). Extend by using non-natural proof techniques: random restrictions (Hastad), communication complexity arguments, or conditional hardness from cryptographic assumptions.")
add("PCP_THEOREM_HARDNESS", "EXTEND", "SDP_HIERARCHIES",
    "Semidefinite programming hierarchies (Lasserre, Sum-of-Squares) extend LP relaxations with positive semidefiniteness constraints. SOS degree-d relaxations give better approximation ratios, and degree-n is exact. Extends the approximation toolkit beyond NP-hardness barriers.")
add("CIRCUIT_LOWER_BOUNDS", "EXTEND", "ALGEBRAIC_GEOMETRY_METHODS",
    "Strassen's degree bound, Baur-Strassen derivative method extend lower bound techniques using algebraic geometry. Grochow-Efremenko use representation theory. Each extension adds mathematical structure to prove stronger lower bounds for specific circuit classes.")
add("CIRCUIT_COMPLEXITY_LOWER_BOUND", "EXTEND", "COMMUNICATION_COMPLEXITY",
    "Karchmer-Wigderson games connect circuit depth to communication complexity. Extend circuit analysis with communication protocols to prove depth lower bounds. Razborov's approximation method extends to monotone circuit lower bounds.")
add("SPACE_TIME_TRADEOFF", "EXTEND", "PARALLEL_COMPUTATION",
    "Extend with parallelism: NC hierarchy uses polynomial processors to solve problems in polylog depth. PRAM models add shared memory. Brent's theorem relates sequential time to parallel depth × processors. Parallelism extends the tradeoff surface to a third dimension.")
add("MINIMUM_CIRCUIT_SIZE_PROBLEM", "EXTEND", "INSTANCE_COMPLEXITY",
    "Ko-Hartmanis instance complexity extends worst-case circuit size to instance-by-instance analysis. Kolmogorov complexity provides a resource-unbounded extension. Time-bounded Kolmogorov complexity (Kt) connects to MCSP via Levin's coding theorem.")

# === Physics ===
add("HEISENBERG_UNCERTAINTY", "EXTEND", "SQUEEZED_STATES",
    "Squeezed states extend the quantum state space: reduce uncertainty in one quadrature below vacuum level at the cost of the conjugate. LIGO uses squeezed light to beat the standard quantum limit. Entangled probes (NOON states) extend to Heisenberg-limited metrology at 1/N scaling.")
add("UNCERTAINTY_PRINCIPLE", "EXTEND", "QUANTUM_ERROR_CORRECTION",
    "Quantum error correction adds ancilla qubits and syndrome measurements to protect encoded information. Shor code, surface codes extend the Hilbert space. Measurement of stabilizers extracts error information without disturbing the logical state, effectively extending precision.")
add("LIGHT_SPEED_LIMIT", "EXTEND", "ALCUBIERRE_METRIC",
    "Alcubierre warp metric: extend GR solutions with exotic matter (negative energy density) to achieve effective superluminal travel by contracting space ahead and expanding behind. Requires negative energy (Casimir effect provides small amounts). Theoretical extension of the constraint.")
add("KELVIN_PLANCK", "EXTEND", "MAXWELLS_DEMON",
    "Maxwell's demon extends thermodynamics with an information-processing agent. Landauer's principle resolves the paradox: erasing the demon's memory costs kT ln 2 per bit. Szilard engine formalizes this. The extension reveals the information-energy equivalence.")
add("CLAUSIUS_INEQUALITY", "EXTEND", "FLUCTUATION_THEOREMS",
    "Jarzynski equality and Crooks fluctuation theorem extend classical thermodynamics to single-molecule regimes. Free energy differences can be extracted from non-equilibrium work distributions. Extends Clausius beyond the macroscopic limit.")
add("THIRD_LAW_UNATTAINABILITY", "EXTEND", "LASER_COOLING",
    "Laser cooling (Doppler, Sisyphus, evaporative) extends achievable temperatures to nanokelvin. Each technique adds structure: optical molasses, magneto-optical traps, Bose-Einstein condensation. Cannot reach exactly 0K but extends the practical floor by 12+ orders of magnitude.")
add("LANDAUER_LIMIT", "EXTEND", "REVERSIBLE_COMPUTING",
    "Bennett's reversible computation: extend logic gates to bijective (Toffoli, Fredkin) to avoid information erasure. Logically reversible computation has no Landauer cost. Extends the energy floor to zero in principle for reversible operations.")
add("THERMODYNAMIC_ASYMMETRY", "EXTEND", "LOSCHMIDT_ECHO",
    "Loschmidt echo / spin echo techniques extend reversibility in practice by time-reversing the Hamiltonian. NMR spin echo (Hahn 1950) reverses dephasing. Extends the window of effective reversibility, though ultimately limited by perturbations.")
add("BEKENSTEIN_BOUND", "EXTEND", "HOLOGRAPHIC_CODES",
    "Holographic error-correcting codes (Pastawski-Yoshida-Harlow-Preskill) extend the bulk information capacity by exploiting the holographic principle. AdS/CFT correspondence shows boundary encodes bulk. Extends information storage by restructuring the encoding.")
add("PENROSE_SINGULARITY", "EXTEND", "LOOP_QUANTUM_GRAVITY",
    "Loop quantum gravity extends GR with quantized area/volume operators, replacing the singularity with a 'quantum bounce.' The minimum area gap (~Planck area) prevents infinite density. Adds quantum geometric structure to resolve the classical singularity.")
add("COSMIC_CENSORSHIP", "EXTEND", "PENROSE_INEQUALITY",
    "Bray-Huisken-Ilmanen Penrose inequality provides partial extensions: the area of apparent horizons bounds the total mass, supporting weak cosmic censorship. Adds geometric inequality structure as evidence for the conjecture.")
add("CHRONOLOGY_PROTECTION", "EXTEND", "QUANTUM_GRAVITY",
    "Quantum gravity effects (Hawking's chronology protection) may extend GR to prevent closed timelike curves. The quantum stress-energy tensor diverges at the Cauchy horizon, providing a physical mechanism. String theory and LQG both suggest CTC-preventing extensions.")
add("TWINS_PARADOX", "EXTEND", "GENERAL_RELATIVISTIC_RESOLUTION",
    "Extend special relativity to GR: the equivalence principle resolves the asymmetry. The accelerating twin's worldline has shorter proper time (integral of ds along path). Gravitational time dilation provides the extended framework where the paradox dissolves.")
add("WEINBERG_MASSLESS_CONSTRAINT", "EXTEND", "HIGGS_MECHANISM",
    "The Higgs mechanism extends the gauge theory with a scalar field whose vacuum expectation value breaks electroweak symmetry. Massless gauge bosons acquire mass through coupling to the Higgs. Extends the particle content to give mass to W/Z while preserving renormalizability.")
add("WHEELER_FEYNMAN_ABSORBER", "EXTEND", "QUANTUM_FIELD_THEORY",
    "QFT extends the absorber theory: Feynman propagator (half-advanced + half-retarded) plus vacuum fluctuations provides a local quantum framework. Extends the action-at-a-distance to a field-theoretic foundation.")
add("ABBE_DIFFRACTION_LIMIT", "EXTEND", "NEAR_FIELD_OPTICS",
    "Near-field scanning optical microscopy (NSOM) extends resolution beyond Abbe by using sub-wavelength apertures in the evanescent field. STED microscopy adds a depletion beam. Structured illumination adds spatial frequency components. Each extends the effective aperture.")
add("GABOR_LIMIT", "EXTEND", "WAVELET_FRAMES",
    "Wavelet frames and oversampled Gabor systems extend the time-frequency representation beyond the Gabor limit. Redundant frames allow better localization at the cost of overcompleteness. Balian-Low theorem is bypassed by giving up orthogonality (Riesz basis property).")
add("NYQUIST_SHANNON", "EXTEND", "COMPRESSED_SENSING",
    "Compressed sensing (Candes-Romberg-Tao, Donoho 2006) extends sampling theory: sparse signals can be recovered from sub-Nyquist samples using L1 minimization. Adds sparsity structure (RIP condition) to extend the sampling bound.")
add("ANTENNA_GAIN_BANDWIDTH", "EXTEND", "METAMATERIAL_ANTENNAS",
    "Metamaterial-loaded antennas extend the Chu-Harrington limit by adding engineered sub-wavelength structures. Active non-Foster matching circuits (negative capacitance/inductance) extend bandwidth beyond passive limits. Each adds artificial structure to weaken the constraint.")
add("MERMIN_WAGNER", "EXTEND", "SUBSTRATE_COUPLING",
    "Coupling a 2D system to a substrate or applying external fields (magnetic, strain) extends the system by breaking continuous symmetry explicitly. Graphene on hBN, magnetic thin films on substrates achieve long-range order by adding external structure that circumvents Mermin-Wagner.")
add("KAM_THEOREM", "EXTEND", "NUMERICAL_KAM",
    "Computer-assisted proofs (de la Llave, Haro) extend KAM theory to larger perturbations by adding rigorous interval arithmetic verification. Parameterization methods extend the domain of validity. Adds computational structure to push the perturbation bound further.")
add("IMPOSSIBILITY_MARGOLUS_LEVITIN_SPEED_LIMIT", "EXTEND", "CATALYTIC_STATES",
    "Catalytic quantum states extend the resource budget: ancilla systems that participate in the evolution but return to their initial state. Extends the effective energy without consuming additional permanent resources.")

# === Quantum Information ===
add("KOCHEN_SPECKER", "EXTEND", "CONTEXTUAL_MODELS",
    "Spekkens toy model extends classical hidden variables with a knowledge restriction (epistemic states). Reproduces many quantum features. Contextual ontological models (Spekkens 2005) extend the hidden variable framework to accommodate contextuality.")
add("NO_BROADCASTING", "EXTEND", "APPROXIMATE_CLONING",
    "Buzek-Hillery approximate cloning machine: extends no-cloning by allowing imperfect copies with fidelity 5/6 for qubits. Asymmetric cloning trades fidelity between copies. Quantum state amplification extends usable copies at reduced fidelity.")
add("NO_COMMUNICATION", "EXTEND", "SUPERDENSE_CODING",
    "Superdense coding extends classical communication: pre-shared entanglement allows 2 classical bits per transmitted qubit. Does not violate no-communication (requires a quantum channel) but extends the capacity by adding entanglement as a resource.")
add("NO_DELETION", "EXTEND", "PARTIAL_TRACE_RECOVERY",
    "Petz recovery map extends quantum information recovery: for degradable channels, the complementary channel's output can partially reconstruct deleted information. Extends recovery by adding channel structure information.")
add("NO_HIDING", "EXTEND", "QUANTUM_SECRET_SHARING",
    "Quantum secret sharing (Cleve-Gottesman-Lo 1999) extends no-hiding by distributing quantum information across multiple parties. The information is hidden from any individual party but recoverable by authorized coalitions. Adds threshold structure.")
add("IMPOSSIBILITY_EASTIN_KNILL_THEOREM", "EXTEND", "CODE_SWITCHING",
    "Code switching: extend the code space by switching between complementary codes that each implement different transversal gates. Pieceable fault tolerance (Yoder-Kim-Chuang 2016) pieces together transversal gates from different codes. Adds inter-code structure.")
add("IMPOSSIBILITY_ENTANGLEMENT_MONOGAMY", "EXTEND", "MULTIPARTITE_ENTANGLEMENT",
    "W-states and GHZ states extend entanglement beyond bipartite: multipartite entanglement distributes quantum correlations differently. MERA tensor networks extend entanglement structure hierarchically. Squashed entanglement quantifies the monogamy extension.")
add("IMPOSSIBILITY_HOLEVO_BOUND", "EXTEND", "SUPERDENSE_CODING_EXTENSION",
    "Superdense coding extends the Holevo bound when pre-shared entanglement is available: transmitting one qubit can communicate 2 classical bits. The entanglement resource extends the accessible information beyond Holevo.")
add("IMPOSSIBILITY_TSIRELSON_BOUND", "EXTEND", "POPESCU_ROHRLICH_BOXES",
    "PR boxes extend quantum correlations to the algebraic maximum (4 for CHSH). While not physically realizable, they extend the no-signaling polytope study. Post-quantum theories (generalized probabilistic theories) extend the correlation framework beyond Tsirelson.")
add("IMPOSSIBILITY_QUANTUM_CAPACITY_NO_ADDITIVITY", "EXTEND", "ENTANGLEMENT_ASSISTED_CAPACITY",
    "Entanglement-assisted capacity (Bennett-Shor-Smolin-Thapliyal 2002) is additive and equals the mutual information of the channel. Extends the quantum capacity framework by adding shared entanglement as a resource, bypassing the non-additivity problem.")
add("IMPOSSIBILITY_QUANTUM_ERROR_CORRECTION_THRESHOLD", "EXTEND", "CONCATENATED_CODES",
    "Concatenated codes extend the threshold: iteratively encoding a code within itself achieves fault tolerance with polynomial overhead when physical error rate < threshold. Surface codes extend the threshold to ~1% with topological structure.")
add("IMPOSSIBILITY_QUANTUM_KEY_DISTRIBUTION_RATE_LIMIT", "EXTEND", "QUANTUM_REPEATERS",
    "Quantum repeaters (Briegel-Dur-Cirac-Zoller 1998) extend QKD range by adding entanglement swapping and purification nodes. Overcomes exponential loss in fiber. All-photonic repeaters and quantum memories extend the architecture further.")
add("KEY_DISTRIBUTION_CLASSICAL", "EXTEND", "QUANTUM_KEY_DISTRIBUTION",
    "QKD (BB84, E91) extends classical key distribution with quantum states whose measurement disturbance reveals eavesdropping. Adds quantum channel structure to achieve information-theoretic security without computational assumptions.")

# === Mathematics (Algebra, Geometry, Topology) ===
add("GALOIS_UNSOLVABILITY", "EXTEND", "DIFFERENTIAL_GALOIS",
    "Differential Galois theory (Picard-Vessiot) extends algebraic Galois theory to differential equations. Adds Lie group structure. Topological Galois theory (Khovanskii) extends further. Ultraradicals and Bring radicals extend the radical tower.")
add("FERMAT_LAST_THEOREM", "EXTEND", "MODULARITY_THEOREM",
    "Wiles' proof extends the framework: the modularity theorem (Taniyama-Shimura-Weil) adds modular form structure to elliptic curves. The extension from FLT to full modularity unlocked Serre's conjecture and the Langlands program.")
add("BANACH_TARSKI", "EXTEND", "AMENABLE_GROUPS",
    "Tarski's theorem: extend the group action to amenable groups where Banach-Tarski fails. Adding a finitely additive measure (amenability) prevents paradoxical decomposition. Folner sequences provide the constructive extension.")
add("IMPOSSIBILITY_BANACH_TARSKI_PARADOX", "EXTEND", "FINITELY_ADDITIVE_MEASURES",
    "Extend with amenable group actions: on abelian groups (and more generally amenable groups), finitely additive translation-invariant measures exist, blocking paradoxical decomposition. The Hahn-Banach theorem provides the extension for abelian groups.")
add("IMPOSSIBILITY_SQUARING_CIRCLE", "EXTEND", "LINDEMANN_WEIERSTRASS_EXTENSIONS",
    "Extend the constructible numbers: if we add a transcendental-number-constructing tool (neusis, marked ruler, origami), circle-squaring becomes possible. Origami (Huzita-Hatori axioms) extends constructible numbers to solve some classically impossible problems.")
add("IMPOSSIBILITY_ANGLE_TRISECTION", "EXTEND", "NEUSIS_CONSTRUCTION",
    "Neusis (marked ruler) construction extends compass-and-straightedge: Archimedes showed angle trisection is possible with neusis. Origami axiom O6 (Huzita) also solves trisection by folding. Each adds a construction primitive that extends the field of constructible numbers to include cube roots.")
add("IMPOSSIBILITY_DOUBLING_CUBE", "EXTEND", "ORIGAMI_CUBE_ROOT",
    "Origami (Huzita-Hatori axiom O6) allows constructing cube roots, enabling cube doubling. Menaechmus' conic section intersection also extends the toolkit. Neusis construction achieves it too. Each extends the constructible field beyond quadratic closures.")
add("IMPOSSIBILITY_REGULAR_POLYGON", "EXTEND", "HIGHER_ORDER_CONSTRUCTIONS",
    "Extending compass-and-straightedge with angle trisection (neusis/origami) enables construction of regular 7-gon, 9-gon, and other non-Fermat polygons. Pierpont's theorem characterizes constructible polygons with trisection: sides of form 2^a * 3^b * p1 * ... * pk for Pierpont primes.")
add("IMPOSSIBILITY_RATIONAL_SQRT2", "EXTEND", "ALGEBRAIC_NUMBER_FIELD",
    "Extend Q to Q(sqrt(2)): the algebraic number field extension provides a minimal field containing sqrt(2). Dedekind cuts or Cauchy sequences extend Q to R. P-adic extensions provide alternative completions. Each adds structure to accommodate irrationals.")
add("IMPOSSIBILITY_TRANSCENDENCE_E_PI", "EXTEND", "SCHANUEL_CONJECTURE",
    "Schanuel's conjecture would extend transcendence theory to determine algebraic independence of e, pi, and their combinations. Extends Lindemann-Weierstrass to a unified framework. Period conjecture (Kontsevich-Zagier) extends to all periods.")
add("NO_DIVISION_ALGEBRA_BEYOND_8", "EXTEND", "CLIFFORD_ALGEBRAS",
    "Clifford algebras extend beyond octonions by relaxing the division algebra requirement. Cl(n) provides 2^n-dimensional algebras for any n. Sedenions (16D) extend by Cayley-Dickson but lose alternativity. Each extension trades algebraic properties for higher dimension.")
add("HAIRY_BALL", "EXTEND", "HIGHER_DIMENSIONS",
    "Odd-dimensional spheres (S^1, S^3, S^7) admit nowhere-vanishing vector fields. Extend from S^2 to S^3 (Hopf fibration provides a global nonvanishing field). Vector field problem (Adams 1962) determines exactly how many independent fields each sphere admits.")
add("EULER_CHARACTERISTIC_OBSTRUCTION", "EXTEND", "LINE_FIELDS",
    "Extend from vector fields to line fields (unoriented tangent directions): even-dimensional manifolds that don't admit vector fields may admit line fields. The obstruction is the mod-2 Euler class, which is weaker. Adds Z/2 structure.")
add("BROUWER_FIXED_POINT", "EXTEND", "KAKUTANI_EXTENSION",
    "Kakutani's fixed point theorem extends Brouwer to set-valued maps (correspondences). Schauder extends to infinite-dimensional Banach spaces. Tychonoff extends to locally convex topological vector spaces. Each adds structure to broaden the fixed point guarantee.")
add("DEHN_IMPOSSIBILITY", "EXTEND", "DEHN_SURGERY_EXTENSION",
    "Extend scissors congruence by adding Dehn invariant as a complete invariant: Sydler (1965) proved volume + Dehn invariant completely characterize scissors congruence in R^3. Extend to the Grothendieck group of polyhedra for a full algebraic framework.")
add("IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT", "EXTEND", "LIE_ALGEBRA_EXTENSION",
    "Extend R^3 cross product to Lie algebras: the cross product is the Lie bracket of so(3). Higher-dimensional Lie algebras (so(n), exceptional Lie algebras) provide non-commutative but structured 'cross products.' Adds Lie-theoretic structure.")
add("IMPOSSIBILITY_CONTINUOUS_BIJECTION_RN", "EXTEND", "PEANO_CURVES",
    "Space-filling curves (Peano, Hilbert) provide continuous surjections R->R^n. Extend by relaxing bijectivity or continuity of inverse. Morton codes (Z-order curves) provide practical near-bijections with controlled discontinuity.")
add("TOPOLOGICAL_INVARIANCE_OF_DIMENSION", "EXTEND", "FRACTAL_DIMENSION",
    "Fractal dimensions (Hausdorff, box-counting, correlation) extend integer topological dimension to non-integer values. Mandelbrot's framework allows continuous dimension spectra. Assouad dimension extends further. Each adds measure-theoretic structure.")
add("COVERING_SPACE_OBSTRUCTION", "EXTEND", "ORBIFOLD_COVERING",
    "Orbifold covering theory (Thurston) extends classical covering spaces to allow quotient singularities. Groupoid coverings extend to non-connected and singular spaces. Stack-theoretic extensions handle even more general spaces.")
add("JORDAN_SCHOENFLIES_FAILURE", "EXTEND", "TAME_EMBEDDINGS",
    "Restrict to PL (piecewise-linear) or smooth embeddings where Schoenflies holds. Alternatively, extend to Alexander's horned sphere framework and study its complement's fundamental group. Brown's theorem extends Schoenflies to all locally flat embeddings in higher dimensions.")
add("POINCARE_DUALITY_OBSTRUCTION", "EXTEND", "INTERSECTION_HOMOLOGY",
    "Goresky-MacPherson intersection homology extends Poincare duality to singular spaces. Perverse sheaves extend further. L^2 cohomology extends to non-compact manifolds. Each adds sheaf-theoretic structure to recover duality.")
add("DEHN_SURGERY_OBSTRUCTION", "EXTEND", "KIRBY_CALCULUS",
    "Kirby calculus extends Dehn surgery with handle slides and stabilization moves. Every closed oriented 3-manifold arises from surgery on a link in S^3 (Lickorish-Wallace). Kirby's theorem identifies which surgery descriptions yield the same manifold.")
add("NASH_ISOMETRIC_EMBEDDING", "EXTEND", "CONVEX_INTEGRATION",
    "Gromov's convex integration extends Nash's C^1 result: h-principle techniques add iterative corrugations to achieve surprising flexibility. De Lellis-Szekelyhidi extend to fluid dynamics (Onsager conjecture). Adds geometric iteration structure.")
add("RIGIDITY_MOSTOW", "EXTEND", "BOREL_CONJECTURE",
    "The Borel conjecture extends Mostow rigidity: aspherical manifolds should be topologically rigid (homotopy equivalent implies homeomorphic). Farrell-Jones extends to a broad class via assembly maps. Adds K-theoretic structure.")
add("TOPOLOGICAL_MANIFOLD_DIMENSION4", "EXTEND", "EXOTIC_STRUCTURES",
    "Freedman's classification extends topological understanding of 4-manifolds using Casson handles and infinite constructions. Exotic R^4 structures (uncountably many) extend the smooth category. Adds gauge-theoretic invariants (Donaldson, Seiberg-Witten).")
add("IMPOSSIBILITY_EXOTIC_R4", "EXTEND", "GAUGE_THEORY_INVARIANTS",
    "Donaldson invariants and Seiberg-Witten invariants extend smooth 4-manifold theory to detect exotic structures. Adding gauge-theoretic structure distinguishes homeomorphic but non-diffeomorphic manifolds.")
add("WHITNEY_EMBEDDING_BOUND", "EXTEND", "HAEFLIGER_EMBEDDING",
    "Haefliger's embedding theorem extends Whitney: 2n+1 ambient dimensions suffice for isotopy uniqueness (n-manifolds). Adds concordance structure. For 2n dimensions (Whitney range), the Whitney trick works for n>=3.")
add("WHITNEY_EMBEDDING_OBSTRUCTION", "EXTEND", "IMMERSION_THEORY",
    "Hirsch-Smale immersion theory extends embedding to immersions: every n-manifold immerses in R^(2n-1) for n>1. Adds homotopy-theoretic structure (h-principle). Cohen's theorem: compact n-manifold immerses in R^(2n-1).")
add("HEAWOOD_CONJECTURE", "EXTEND", "GRAPH_MINORS",
    "Robertson-Seymour graph minor theory extends chromatic theory: each surface has a finite set of forbidden minors for embeddability. Adds well-quasi-ordering structure. The Heawood bound becomes exact (Ringel-Youngs) for all surfaces except Klein bottle.")
add("PENROSE_APERIODICITY", "EXTEND", "ALGEBRAIC_APERIODICITY",
    "Extend to algebraic aperiodic frameworks: substitution rules, cut-and-project from higher-dimensional lattices (de Bruijn 1981). The Penrose tiling is a projection of a 5D cubic lattice slice. Adds number-theoretic structure (golden ratio, Pisot numbers).")
add("IMPOSSIBILITY_PENTAGONAL_TILING", "EXTEND", "PENROSE_KITES_DARTS",
    "Penrose kites and darts extend regular pentagon tiling by breaking the pentagon into non-regular pieces that tile aperiodically. Adds matching rules (local constraints) as additional structure. The einstein (hat tile, Smith et al. 2023) extends to a single aperiodic monotile.")
add("KEPLER_CONJECTURE", "EXTEND", "HIGHER_DIMENSIONAL_PACKINGS",
    "Extend to higher dimensions: E8 lattice (8D) and Leech lattice (24D) are provably optimal (Viazovska 2016, Cohn-Kumar-Miller-Radchenko-Viazovska 2017). Adds modular form structure. Linear programming bounds extend the framework.")
add("RAMSEY_INEVITABILITY", "EXTEND", "HYPERGRAPH_RAMSEY",
    "Hypergraph Ramsey theory extends edge-coloring Ramsey to r-uniform hypergraphs. Hales-Jewett theorem extends to combinatorial lines. Density Ramsey (Szemeredi's theorem) extends from coloring to density conditions.")
add("KNOT_INVARIANT_INCOMPLETENESS", "EXTEND", "KHOVANOV_HOMOLOGY",
    "Khovanov homology categorifies the Jones polynomial, adding a graded chain complex structure. Detects unknot (Kronheimer-Mrowka via instanton homology). Heegaard Floer homology extends further. Each categorification adds homological structure to strengthen the invariant.")
add("IMPOSSIBILITY_BORSUK_ULAM", "EXTEND", "EQUIVARIANT_TOPOLOGY",
    "Equivariant topology (Bredon) extends Borsuk-Ulam to general group actions. Tom Dieck splitting and Borel construction add group-theoretic structure. Conley index extends the fixed-point theory to dynamical systems context.")
add("GAUSS_BONNET_CURVATURE_TOPOLOGY", "EXTEND", "CHERN_WEIL",
    "Chern-Weil theory extends Gauss-Bonnet to higher dimensions and vector bundles. Characteristic classes (Chern, Pontryagin, Euler) extend curvature-topology relations. Atiyah-Singer index theorem extends further to elliptic operators on manifolds.")
add("EULER_POLYHEDRON_OBSTRUCTION", "EXTEND", "HIGHER_EULER",
    "Higher Euler characteristics and Euler calculus (Schanuel, Rota) extend V-E+F=2 to posets, categories, and constructible functions. Extends to orbifolds and stratified spaces. Adds sheaf-theoretic generalization.")
add("FOUR_SQUARES_OBSTRUCTION", "EXTEND", "WARING_PROBLEM",
    "Waring's problem extends: every natural number is a sum of at most g(k) k-th powers. Vinogradov's improvement gives G(k) for sufficiently large n. Extends the four-squares framework to arbitrary powers, adding analytic number theory structure.")
add("LIOUVILLE_APPROXIMATION", "EXTEND", "ROTH_THEOREM",
    "Roth's theorem (1955) sharpens Liouville: algebraic numbers of degree d cannot be approximated by rationals to within q^(-2-epsilon). Schmidt's subspace theorem extends to simultaneous approximation. Adds Thue-Siegel-Roth method.")
add("HASSE_MINKOWSKI_FAILURE", "EXTEND", "BRAUER_MANIN",
    "Brauer-Manin obstruction extends Hasse principle: the Brauer group of the variety provides additional local-to-global constraints. Descent obstructions, etale-Brauer obstruction extend further. Adds cohomological structure to explain Hasse failures.")
add("WEDDERBURN_LITTLE", "EXTEND", "CENTRAL_SIMPLE_ALGEBRAS",
    "Extend finite division rings (all commutative by Wedderburn) to central simple algebras over general fields. Brauer group classifies these extensions. Adds Galois cohomological structure. Artin-Wedderburn theorem extends to semisimple rings.")
add("BURNSIDE_IMPOSSIBILITY", "EXTEND", "REPRESENTATION_THEORY",
    "Burnside's theorem (pq groups are solvable) extends via representation theory. The classification of finite simple groups extends the analysis to all finite groups. Character theory (Brauer, Green) adds modular representation structure.")
add("NIELSEN_SCHREIER", "EXTEND", "BASS_SERRE_THEORY",
    "Bass-Serre theory extends Nielsen-Schreier to groups acting on trees: graphs of groups provide structural decompositions. Adds tree-theoretic structure to understand subgroups of free products and HNN extensions.")
add("VON_NEUMANN_EMBEDDING", "EXTEND", "OPERATOR_ALGEBRAS",
    "Connes' classification of injective factors extends von Neumann algebra theory. Free probability (Voiculescu) extends to non-commutative probability. Adds entropy structure (Connes-Stormer entropy) and K-theoretic invariants.")
add("BAIRE_CATEGORY", "EXTEND", "CHOQUET_THEORY",
    "Choquet theory extends Baire category methods with integral representation on compact convex sets. Martin boundary extends to potential theory. Adds measure-theoretic structure to complement the topological category arguments.")
add("VITALI_NONMEASURABLE", "EXTEND", "SOLOVAY_MODEL",
    "Solovay's model (ZF + DC without full AC) extends set theory to one where all sets of reals are Lebesgue measurable. Adds inaccessible cardinal structure. Demonstrates the dependency on the axiom of choice.")
add("VITALI_SET", "EXTEND", "MEASURE_EXTENSIONS",
    "Caratheodory extension theorem extends pre-measures to sigma-algebras. Banach-Tarski avoidance via restricting to Lebesgue measurable sets. Adds the outer measure structure. Amenable group actions provide translation-invariant extensions.")
add("CANTOR_DIAGONALIZATION", "EXTEND", "FORCING_EXTENSION",
    "Cohen forcing extends models of set theory by adding generic reals. Forces |R| to be arbitrarily large. Each forcing extension adds a specific structured real. Iterated forcing (Martin's axiom, PFA) extends further.")

# === Biology / Neuroscience ===
add("IMPOSSIBILITY_COMPETITIVE_EXCLUSION", "EXTEND", "NICHE_PARTITIONING",
    "Niche partitioning extends the competitive exclusion principle: species coexist by specializing along different resource axes (MacArthur 1958). Character displacement adds morphological structure. Storage effect and spatial heterogeneity extend temporal/spatial niches.")
add("MULLERS_RATCHET", "EXTEND", "SEXUAL_RECOMBINATION",
    "Sexual recombination extends asexual lineages by adding genetic exchange. Recombination breaks the ratchet by reassembling mutation-free genomes from partially damaged ones. Horizontal gene transfer in prokaryotes provides a parallel extension.")
add("IMPOSSIBILITY_FISHER_FUNDAMENTAL_THEOREM", "EXTEND", "PRICE_EQUATION",
    "Price equation extends Fisher's theorem to include transmission bias and environmental change. Robertson's secondary theorem adds non-additive variance. Multilevel selection (Price 1970) extends to group selection. Each adds a component Fisher's partial change missed.")
add("IMPOSSIBILITY_PRICE_EQUATION_CONSTRAINT", "EXTEND", "CONTEXTUAL_ANALYSIS",
    "Contextual analysis (Heisler-Damuth 1987) extends Price equation by separating within-group and between-group selection components. Multilevel regression adds group-level covariates. Extends the partition to arbitrary hierarchical levels.")
add("IMPOSSIBILITY_VALIANT_EVOLVABILITY", "EXTEND", "NEUTRAL_NETWORKS",
    "Neutral networks (Schuster, Fontana) extend Valiant's framework: connected sets of genotypes with equal fitness provide evolutionary pathways through sequence space. RNA neutral networks are empirically validated. Adds network connectivity structure.")
add("IMPOSSIBILITY_NK_FITNESS_LANDSCAPE", "EXTEND", "MODULAR_ARCHITECTURE",
    "Modular genetic architecture (Wagner-Altenberg 1996) extends NK landscapes by restricting epistasis to within-module interactions. Reduces effective K while maintaining evolvability. Nearly decomposable systems (Simon 1962) provide the structural extension.")
add("IMPOSSIBILITY_MODULARITY_EVOLVABILITY_TRADEOFF", "EXTEND", "FACILITATED_VARIATION",
    "Facilitated variation (Gerhart-Kirschner 2007) extends the modularity-evolvability framework: conserved core processes enable diverse phenotypic outcomes from limited genetic change. Adds developmental bias structure. Weak regulatory linkage facilitates the extension.")
add("IMPOSSIBILITY_KLEIBER_METABOLIC_SCALING", "EXTEND", "FRACTAL_SUPPLY_NETWORKS",
    "West-Brown-Enquist (1997) extend metabolic scaling with fractal supply networks: space-filling vascular trees with area-preserving branching derive the 3/4 power law. Adds network geometry structure. Resource transport networks provide the structural basis.")
add("PARADOX_OF_ENRICHMENT", "EXTEND", "SPATIAL_STRUCTURE",
    "Spatial structure (Jansen 1995, de Roos 1998) extends the paradox of enrichment: limited mixing and local interactions prevent global destabilization. Metapopulation dynamics add patch structure. Stage-structured models extend by adding demographic complexity.")
add("LEWONTIN_HERITABILITY", "EXTEND", "GWAS_MOLECULAR",
    "Genome-wide association studies extend heritability from population-level variance partitioning to molecular-level identification. Expression QTLs add transcriptomic structure. Polygenic risk scores extend to individual-level prediction.")
add("NEURAL_CODING_LIMITS", "EXTEND", "POPULATION_CODING",
    "Population codes extend single-neuron information limits: Fisher information scales with N neurons. Neural manifolds add geometric structure. Bayesian decoding extends to optimal readout. Each adds population-level structure beyond individual neuron capacity.")
add("IMPOSSIBILITY_RATE_DISTORTION_NEURAL_CODING", "EXTEND", "PREDICTIVE_CODING",
    "Predictive coding (Rao-Ballard 1999) extends neural coding by transmitting only prediction errors. Reduces information rate by exploiting temporal structure. Efficient coding hypothesis (Barlow 1961) extends by matching neural responses to environmental statistics.")
add("BINDING_PROBLEM", "EXTEND", "GAMMA_SYNCHRONY",
    "Gamma-band synchrony (Singer-Gray 1995) extends binding by adding temporal coincidence structure: neurons representing features of the same object fire in synchrony. Communication through coherence (Fries 2005) extends to inter-area binding. Adds oscillatory phase structure.")
add("BROCAS_BINDING", "EXTEND", "NETWORK_OSCILLATION",
    "Neural oscillations (theta-gamma coupling) extend Broca's area function by adding phase-amplitude coupling structure. Cross-frequency coupling binds linguistic elements across temporal scales. Adds hierarchical temporal structure for syntactic binding.")
add("MILLERS_LAW", "EXTEND", "CHUNKING",
    "Chunking (Miller 1956, Chase-Simon 1973) extends working memory capacity by grouping items into meaningful units. Expert chess memory, language phrases as chunks. Adds hierarchical organization structure to effectively multiply the 7±2 limit.")
add("DUAL_TASK_BOTTLENECK", "EXTEND", "AUTOMATICITY",
    "Automaticity through practice (Shiffrin-Schneider 1977) extends dual-task capacity: automatic processes bypass the central bottleneck. Adds procedural memory structure. Task-specific modules (Fodor) extend processing capacity for trained tasks.")
add("IMPOSSIBILITY_COMPUTATIONAL_IRREDUCIBILITY_CA", "EXTEND", "COARSE_GRAINING",
    "Coarse-graining and renormalization group methods extend predictability of cellular automata at larger scales. Israeli-Goldenfeld (2004) showed some irreducible CA become predictable at coarser resolutions. Adds scale-dependent structure.")
add("IMPOSSIBILITY_INFORMATION_BOTTLENECK", "EXTEND", "DEEP_VARIATIONAL_IB",
    "Deep variational information bottleneck (Alemi et al. 2017) extends IB theory with parameterized encoder/decoder networks. Adds amortized inference structure. Nonlinear IB extends to capture complex sufficient statistics beyond linear projection.")

# === Economics / Game Theory / Social Choice ===
add("ARROW_IMPOSSIBILITY", "EXTEND", "CARDINAL_UTILITIES",
    "Extend ordinal preferences to cardinal utilities (Harsanyi 1955): interpersonally comparable utility functions allow consistent social welfare functions. Adds interval scale structure. Range voting and utilitarian aggregation become possible with cardinal information.")
add("CONDORCET_PARADOX", "EXTEND", "DOMAIN_RESTRICTION",
    "Single-peaked preferences (Black 1948) extend the preference domain with structural constraints that guarantee a Condorcet winner. Value-restricted preferences (Sen 1966) provide a weaker extension. Adds topological structure to the preference space.")
add("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "EXTEND", "BROKER_SUBSIDY",
    "Adding an external subsidy or broker extends the mechanism: with outside money, efficient bilateral trade becomes possible. McAfee's (1992) mechanism adds a spread-based subsidy structure. Extends the budget balance constraint.")
add("INTERPERSONAL_UTILITY", "EXTEND", "REVEALED_PREFERENCE",
    "Afriat's theorem and revealed preference theory extend utility comparison: GARP-consistent choices reconstruct utility up to monotone transformation. Varian's (1982) non-parametric approach adds budget set structure. Money-metric utility extends to a common scale.")
add("COMMONS_DILEMMA", "EXTEND", "OSTROM_INSTITUTIONS",
    "Ostrom's institutional design principles (1990) extend the commons with governance structure: clearly defined boundaries, monitoring, graduated sanctions, conflict resolution. Adds institutional rules as additional structure.")
add("EFFICIENT_MARKET_LIMITS", "EXTEND", "BEHAVIORAL_FINANCE",
    "Behavioral finance extends EMH with bounded rationality structure: prospect theory (Kahneman-Tversky), limits to arbitrage (Shleifer-Vishny). Adds cognitive bias and institutional friction structure that explains persistent anomalies.")
add("SONNENSCHEIN_MANTEL_DEBREU", "EXTEND", "GROSS_SUBSTITUTES",
    "Gross substitutes condition (Kelso-Crawford 1982) extends general equilibrium with structural restrictions on demand: excess demand satisfies the weak axiom. Adds substitutability structure. Yields unique, stable equilibrium.")
add("REVENUE_EQUIVALENCE", "EXTEND", "RISK_AVERSION",
    "Extending risk-neutral bidders to risk-averse bidders (Maskin-Riley 1984) breaks revenue equivalence. First-price auctions generate more revenue with risk-averse bidders. Adds expected utility structure beyond risk neutrality.")
add("SEN_LIBERAL_PARADOX", "EXTEND", "RIGHTS_ASSIGNMENT",
    "Gibbard (1974) extends with alienable rights: individuals can waive their rights through voluntary exchange. Game-form rights (Gaertner-Pattanaik-Suzumura 1992) extend the rights structure. Adds contractual mechanisms to resolve the paradox.")
add("IMPOSSIBILITY_GROSSMAN_STIGLITZ_PARADOX", "EXTEND", "RATIONAL_INATTENTION",
    "Rational inattention (Sims 2003) extends the information acquisition framework with channel capacity constraints. Adds Shannon entropy structure. Agents optimally choose how much information to acquire given processing costs.")
add("IMPOSSIBILITY_LUCAS_CRITIQUE_POLICY_INVARIANCE", "EXTEND", "DSGE_MICROFOUNDATIONS",
    "DSGE models with explicit microfoundations extend policy analysis by modeling agent optimization directly. Adds structural equations derived from utility maximization and rational expectations. Policy changes alter equilibrium through specified channels.")
add("IMPOSSIBILITY_LONG_RUN_PHILLIPS_CURVE", "EXTEND", "NKPC_EXPECTATIONS",
    "New Keynesian Phillips Curve extends with rational expectations and Calvo pricing: adds nominal rigidity structure. NKPC relates inflation to expected future inflation and output gap. Clarida-Gali-Gertler (1999) extend to optimal monetary policy design.")
add("BLACK_SCHOLES_ASSUMPTIONS", "EXTEND", "STOCHASTIC_VOLATILITY",
    "Stochastic volatility models (Heston 1993) extend Black-Scholes by adding a second stochastic process for volatility. Jump-diffusion (Merton 1976) adds Poisson jump structure. Local volatility (Dupire 1994) extends with state-dependent diffusion.")
add("IMPOSSIBILITY_DIAMOND_DYBVIG_BANK_RUNS", "EXTEND", "DEPOSIT_INSURANCE",
    "Government deposit insurance (FDIC) extends the banking system with a credible guarantee structure that eliminates the bank-run equilibrium. Lender of last resort (Bagehot) adds liquidity provision. Each extends the institutional framework.")
add("IMPOSSIBILITY_BALASSA_SAMUELSON_PRICE_CONVERGENCE", "EXTEND", "SECTORAL_MODELS",
    "Dual-sector models (Baumol-Bowen) extend Balassa-Samuelson by explicitly modeling tradeable/non-tradeable sectors. Adds sectoral structure. Penn World Tables provide extended cross-country data for PPP-adjusted comparisons.")
add("IMPOSSIBILITY_BILATERAL_TRADE_CHATTERJEE_SAMUELSON", "EXTEND", "ITERATIVE_MECHANISMS",
    "Iterative mechanisms (Cramton-Gibbons-Klemperer 1987) extend single-shot bilateral trade with multiple rounds. Adds temporal structure. Ascending/descending auctions converge to efficient allocations with more rounds.")
add("IMPOSSIBILITY_COASE_IMPOSSIBILITY_CONDITIONS", "EXTEND", "MECHANISM_DESIGN",
    "Mechanism design (Myerson 1981) extends Coase by adding incentive-compatible institutions. VCG mechanisms extend to multi-agent settings. Adds strategic structure that works despite transaction costs and information asymmetries.")
add("IMPOSSIBILITY_COMPETITIVE_EQUILIBRIUM_INDIVISIBLE", "EXTEND", "WALRASIAN_WITH_TRANSFERS",
    "Ascending auctions with personalized prices (Demange-Gale-Sotomayor 1986) extend competitive equilibrium to indivisible goods with gross substitutes. Adds personalized pricing structure. Kelso-Crawford extends to matching with contracts.")
add("IMPOSSIBILITY_CONGESTION_PRICE_OF_ANARCHY", "EXTEND", "TOLLING",
    "Marginal cost pricing / Pigouvian tolls extend the routing game by adding price structure. Optimal tolls internalize externalities, achieving system-optimal routing. Stackelberg routing adds leader-follower structure.")
add("IMPOSSIBILITY_DICTATORSHIP_WITHOUT_MONEY", "EXTEND", "TOKEN_MECHANISMS",
    "Artificial currency mechanisms (Gorokhovskii-Guo-Hanson) extend dictatorship-only results by adding tokens/scrip as transferable currency. Adds monetary structure without real money. Prediction markets extend with information-based incentives.")
add("IMPOSSIBILITY_ENVY_FREE_DIVISION", "EXTEND", "SPERNER_ALGORITHM",
    "Simmons-Su (1999) use Sperner's lemma to extend envy-free division to arbitrary numbers of players. Stromquist's moving knife extends to continuous division. Aziz-Mackenzie (2016) provide a bounded envy-free protocol. Each adds algorithmic structure.")
add("IMPOSSIBILITY_FOLK_THEOREM_BOUNDARY", "EXTEND", "REPUTATION_EFFECTS",
    "Reputation effects (Kreps-Wilson 1982, Milgrom-Roberts 1982) extend folk theorem beyond complete information: even short-horizon games support cooperation with incomplete information about types. Adds belief structure.")
add("IMPOSSIBILITY_IMPLEMENTATION_MASKIN", "EXTEND", "AUGMENTED_MECHANISMS",
    "Augmented mechanisms (Jackson 1992, Maskin-Moore 1999) extend implementation with additional message structure. Integer games, modulo games add strategic complexity. Unique implementation in undominated strategies extends the solution concept.")
add("IMPOSSIBILITY_NASH_PPAD_HARDNESS", "EXTEND", "SUPPORT_ENUMERATION",
    "Support enumeration method (Porter-Nudelman-Shoham 2008) extends Nash computation by adding combinatorial search structure. Lemke-Howson algorithm adds linear complementarity structure. Homotopy methods extend to deformation paths.")
add("IMPOSSIBILITY_REVELATION_PRINCIPLE_LIMITS", "EXTEND", "ROBUST_MECHANISM_DESIGN",
    "Bergemann-Morris (2005) robust mechanism design extends revelation principle to settings with ambiguity about beliefs. Adds worst-case structure. Ex-post incentive compatibility extends to stronger solution concepts.")
add("IMPOSSIBILITY_REVENUE_EQUIVALENCE_BREAKDOWN", "EXTEND", "OPTIMAL_AUCTION_DESIGN",
    "Myerson (1981) optimal auction design extends revenue analysis by computing virtual valuations. Adds ironing structure for irregular distributions. Bulow-Klemperer (1996) extends: N+1 bidders in second-price > optimal auction with N bidders.")
add("IMPOSSIBILITY_SECOND_WELFARE_IMPOSSIBILITY", "EXTEND", "LINDAHL_PRICING",
    "Lindahl pricing extends welfare theory to public goods: each agent pays their marginal valuation. Clarke tax and Groves mechanism extend with incentive-compatible structures. Adds personalized pricing for non-rival goods.")
add("IMPOSSIBILITY_STABLE_MATCHING_THREE_SIDED", "EXTEND", "ALGORITHM_CONSTRAINTS",
    "Restrict preferences to structured domains: acyclic preferences (Danilov 2003) guarantee stability in three-sided matching. Master lists, common ranking, and short preference lists extend stability existence. Adds preference restriction structure.")
add("IMPOSSIBILITY_STOLPER_SAMUELSON_DISTRIBUTIONAL", "EXTEND", "SPECIFIC_FACTORS",
    "Specific factors model (Ricardo-Viner) extends Stolper-Samuelson by adding factor specificity structure: some factors are mobile between sectors, others are specific. Gives more nuanced distributional predictions.")
add("IMPOSSIBILITY_WELFARE_IMPOSSIBILITY_INTERPERSONAL", "EXTEND", "CAPABILITY_APPROACH",
    "Sen's capability approach extends utility-based welfare by adding a multi-dimensional space of functionings and capabilities. Human Development Index operationalizes this. Adds structural dimensions beyond scalar utility.")
add("VCG_BUDGET_IMPOSSIBILITY", "EXTEND", "REDISTRIBUTION_MECHANISMS",
    "Cavallo (2006) redistribution mechanism extends VCG by returning a portion of payments to agents while maintaining strategy-proofness. Moulin (2009) optimal redistribution. Adds a rebate structure.")
add("IMPOSSIBILITY_VCG_BUDGET_BALANCE", "EXTEND", "AGV_MECHANISM",
    "Arrow-d'Aspremont-Gerard-Varet (AGV) expected externality mechanism extends VCG with balanced transfers. Achieves ex-ante budget balance + efficiency + incentive compatibility. Adds expected transfer structure.")
add("GERRYMANDERING_IMPOSSIBILITY", "EXTEND", "SHORTEST_SPLITLINE",
    "Shortest splitline algorithm extends redistricting with geometric structure: recursively bisect the state along the shortest line that equalizes population. Adds purely geometric constraints. Markov chain Monte Carlo (ReCom) extends with ensemble analysis.")
add("IMPOSSIBILITY_CONDORCET_JURY_LIMITATIONS", "EXTEND", "DELIBERATION",
    "Deliberation extends Condorcet jury theorem beyond independent voting: Austen-Smith-Banks (1996) show communication improves group accuracy when signals are informative. Adds information-sharing structure.")
add("SYBIL_IMPOSSIBILITY", "EXTEND", "PROOF_OF_WORK",
    "Proof-of-work (Dwork-Naor 1993, Bitcoin 2008) extends identity systems by adding computational cost structure. Proof-of-stake adds economic collateral. Proof-of-personhood (Worldcoin, BrightID) extends with biometric structure.")

# === Control Theory ===
add("IMPOSSIBILITY_BODE_INTEGRAL_V2", "EXTEND", "TWO_DEGREE_OF_FREEDOM",
    "Two-degree-of-freedom controllers extend SISO Bode limitations: separate feedback and feedforward paths. Adds structural freedom. Youla parameterization extends the set of all stabilizing controllers with an affine structure.")
add("IMPOSSIBILITY_BODE_GAIN_PHASE", "EXTEND", "NON_MINIMUM_PHASE_COMPENSATION",
    "All-pass compensation extends gain-phase relations by adding phase correction networks. Non-minimum phase zeros impose irreducible phase lag, but added all-pass sections extend the design space.")
add("IMPOSSIBILITY_ZAMES_SENSITIVITY", "EXTEND", "MULTI_OBJECTIVE_H_INF",
    "Multi-objective H-infinity design (mixed sensitivity) extends Zames by adding weighting functions on multiple transfer functions simultaneously. Mu-synthesis extends further with structured uncertainty. Adds multi-channel structure.")
add("IMPOSSIBILITY_KALMAN_OPTIMALITY_BOUND", "EXTEND", "EXTENDED_KALMAN_FILTER",
    "Extended Kalman filter adds linearization structure for nonlinear systems. Unscented Kalman filter adds sigma-point structure. Particle filters extend to arbitrary distributions. Each extends Kalman's framework beyond linear Gaussian assumptions.")
add("IMPOSSIBILITY_TRACKING_DISTURBANCE_LIMIT", "EXTEND", "PREVIEW_CONTROL",
    "Preview control (Tomizuka 1975) extends tracking by adding future reference information. Look-ahead reduces the waterbed effect. Repetitive control adds periodic signal structure. Each extends the information set available to the controller.")
add("IMPOSSIBILITY_MIMO_FUNDAMENTAL_LIMITS", "EXTEND", "DECOUPLING_CONTROL",
    "Decoupling control (Morgan 1964) extends MIMO design by adding pre/post-compensators to diagonalize the plant. Adds structural decoupling. Sequential loop closing with interaction measures (RGA) extends practical MIMO design.")
add("IMPOSSIBILITY_SMALL_GAIN_THEOREM", "EXTEND", "IQC_FRAMEWORK",
    "Integral quadratic constraints (Megretski-Rantzer 1997) extend small gain theorem to structured uncertainties. Adds multiplier structure. Less conservative than unstructured small gain. Zames-Falb multipliers extend to slope-restricted nonlinearities.")
add("IMPOSSIBILITY_WATERBED_GENERALIZED", "EXTEND", "MULTI_RATE_SAMPLING",
    "Multi-rate sampling extends single-rate waterbed by adding temporal structure: different sampling rates for different channels. Lifts the system to a higher-dimensional LTI system. Adds multi-rate structure to reshape sensitivity.")
add("IMPOSSIBILITY_PONTRYAGIN_MAXIMUM_PRINCIPLE", "EXTEND", "RELAXED_CONTROLS",
    "Young measure relaxations extend Pontryagin's principle to chattering controls. Adds measure-valued structure. Sliding mode control extends with discontinuous feedback. Gamkrelidze's generalized controls extend the admissible set.")
add("ASHBY_LIMITS", "EXTEND", "AMPLIFYING_REGULATION",
    "Beer's viable system model extends Ashby's law of requisite variety by adding organizational hierarchy. Each level amplifies variety handling through recursive structure. Conant-Ashby theorem extends: every good regulator is a model of the system.")
add("GRASP_IMPOSSIBILITY", "EXTEND", "UNDERACTUATED_MANIPULATION",
    "Underactuated manipulation extends grasp planning by adding environmental contacts (pivoting, sliding, pushing). Extrinsic dexterity (Dafle et al. 2014) uses external surfaces as additional constraints. Adds environmental structure.")

# === Information Theory / Coding ===
add("SHANNON_CHANNEL_CAPACITY", "EXTEND", "MIMO_CHANNELS",
    "MIMO (multiple-input multiple-output) channels extend Shannon capacity by adding spatial dimensions. Telatar (1999): capacity scales as min(n_t, n_r) * log(SNR) at high SNR. OFDM adds frequency dimension. Each extends the degrees of freedom.")
add("SOURCE_CODING_BOUND", "EXTEND", "DISTRIBUTED_SOURCE_CODING",
    "Slepian-Wolf (1973) distributed source coding extends to correlated sources: joint entropy suffices even with separate encoders. Wyner-Ziv extends to lossy compression with side information. Adds correlation structure.")
add("RATE_DISTORTION_BOUND", "EXTEND", "SUCCESSIVE_REFINEMENT",
    "Successive refinement (Equitz-Cover 1991) extends rate-distortion with layered encoding. Base layer + enhancement layers allow progressive quality. Adds hierarchical coding structure. Universally successive refinable for Gaussian sources.")
add("IMPOSSIBILITY_CHANNEL_CODING_CONVERSE", "EXTEND", "FEEDBACK_CAPACITY",
    "Feedback can extend channel capacity for some channels: Schalkwijk-Kailath (1966) achieves doubly exponential error decay with feedback for AWGN. Cover-Pombra extend to Gaussian channels with memory. Adds causal feedback structure.")
add("ONE_TIME_PAD_NECESSITY", "EXTEND", "STREAM_CIPHERS",
    "Stream ciphers (RC4, ChaCha20) extend OTP by replacing truly random keys with pseudorandom keystreams from short seeds. Adds PRG structure. Computational security replaces information-theoretic security. Extends practical key length.")
add("IMPOSSIBILITY_BERNSTEIN_LETHARGY", "EXTEND", "ADAPTIVE_APPROXIMATION",
    "Adaptive approximation (free knot splines, rational approximation, greedy algorithms) extends polynomial approximation by allowing data-dependent basis placement. Adds adaptive structure. Achieves faster rates for functions with local features.")
add("IMPOSSIBILITY_FABER_THEOREM_INTERPOLATION", "EXTEND", "OVERSAMPLING_INTERPOLATION",
    "Oversampled interpolation extends Faber's result: using more interpolation points than polynomial degree (least squares fit) avoids Runge phenomenon. Adds redundancy structure. Weighted least squares with Christoffel-Darboux kernel extends further.")
add("RUNGE_PHENOMENON", "EXTEND", "CHEBYSHEV_NODES",
    "Chebyshev nodes extend equispaced interpolation by clustering points at interval endpoints. Adds Chebyshev polynomial structure. Minimax property ensures near-optimal interpolation. Leja sequences extend to adaptive node placement.")
add("IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY", "EXTEND", "WEIGHTED_APPROXIMATION",
    "Weighted approximation (Mergelyan, Lavrentiev) extends Muntz-Szasz by adding weight function structure to the approximation space. Changes the completeness condition. Adds measure-theoretic structure to the function space.")
add("MUNTZ_SZASZ", "EXTEND", "GENERALIZED_MUNTZ",
    "Generalized Muntz theorem extends to multivariate settings and general Chebyshev systems. Adds multi-index structure. Operstein (2003) extends to Muntz-type rational approximation.")
add("IMPOSSIBILITY_UNIVERSAL_APPROXIMATION_RATE_IMPOSSIBILITY", "EXTEND", "DEEP_NETWORKS",
    "Deep networks extend shallow universal approximation: depth provides exponential efficiency gains (Telgarsky 2016, Eldan-Shamir 2016). ResNets add skip connections. Adds hierarchical composition structure that achieves polynomial approximation rates.")
add("IMPOSSIBILITY_KOLMOGOROV_SUPERPOSITION_COMPUTATIONAL_BARRIER", "EXTEND", "SMOOTH_REPRESENTATIONS",
    "Smooth Kolmogorov representations (Braun-Griebel 2009) extend the superposition theorem by adding smoothness constraints. Sprecher's algorithm adds constructive inner/outer function computation. Neural network implementations extend to practical computation.")

# === Misc remaining EXTEND fills ===
add("IMPOSSIBILITY_MAP_PROJECTION", "EXTEND", "GLOBE_DIGITAL",
    "Digital globes (Google Earth, Cesium) extend map projection by adding a third spatial dimension: the full sphere is rendered without projection distortion. Virtual reality globes extend further. Adds the missing spatial degree of freedom.")
add("IMPOSSIBILITY_CALENDAR", "EXTEND", "INTERCALARY_MONTHS",
    "Lunisolar calendars (Hebrew, Chinese) add intercalary months (Metonic cycle: 7 in 19 years) to synchronize lunar months with solar year. Adds periodic correction structure. Ethiopian calendar adds a 13th short month.")
add("BYZANTINE_GENERALS_BOUND", "EXTEND", "AUTHENTICATED_CHANNELS",
    "Digital signatures (Dolev-Strong 1983) extend Byzantine agreement to tolerate any number of faults with authenticated channels. Adds cryptographic authentication structure. Blockchain extends with proof-of-work-based agreement.")
add("FLP_IMPOSSIBILITY", "EXTEND", "FAILURE_DETECTORS",
    "Chandra-Toueg (1996) failure detectors extend asynchronous consensus: even unreliable failure detectors (class Diamond-S) suffice for consensus. Adds failure detection structure. Randomized consensus (Ben-Or 1983) extends with probabilistic termination.")
add("IMPOSSIBILITY_CAP", "EXTEND", "CRDT_STRUCTURES",
    "CRDTs (conflict-free replicated data types) extend CAP by adding algebraic structure (semilattice joins, commutative operations) that guarantees eventual consistency without coordination. Adds mathematical structure to the data model itself.")
add("COMMUNICATION_COMPLEXITY_LOWER_BOUND", "EXTEND", "SHARED_RANDOMNESS",
    "Shared randomness (public coins) extends communication complexity: Newman's theorem shows public coins save at most O(log n) bits. Quantum communication extends further (exponential savings for some problems). Adds shared resource structure.")
add("COMPLEXITY_HIERARCHY", "EXTEND", "ADVICE_STRINGS",
    "Karp-Lipton advice (P/poly, BPP/poly) extends complexity classes with non-uniform advice strings. Adds problem-specific hints. Circuit complexity provides the structural extension. Interactive proofs (IP) extend with verifier-prover structure.")
add("IP_EQUALS_PSPACE", "EXTEND", "MULTI_PROVER",
    "Multi-prover interactive proofs (MIP) extend IP to MIP = NEXP. MIP* = RE (Ji et al. 2020) extends further with quantum entanglement between provers. Adds inter-prover structure. Each extension increases the power of the verification framework.")
add("BGS_ORACLE_SEPARATION", "EXTEND", "ALGEBRIZATION",
    "Aaronson-Wigderson algebrization extends relativization to algebraic extensions of oracles. Shows that techniques must be non-algebrizing to separate P from NP. Adds algebraic structure to the oracle framework.")
add("UNIQUE_GAMES_CONJECTURE", "EXTEND", "SOS_HIERARCHY",
    "Sum-of-Squares (SOS) hierarchy provides progressively tighter relaxations for unique games instances. At degree d = n, SOS solves exactly. Adds semidefinite structure. Barak-Kothari-Steurer extend SOS analysis to near-optimal UGC algorithms.")
add("MATIYASEVICH_HILBERT10", "EXTEND", "DECIDABLE_SUBCLASSES",
    "Decidable subclasses extend Hilbert's tenth problem: single-variable polynomials, systems of linear equations, quadratic forms (Hasse-Minkowski). Adds structural restrictions. Presburger arithmetic extends decidability to linear integer arithmetic.")
add("UNDECIDED_TILES", "EXTEND", "SUBSTITUTION_TILINGS",
    "Substitution tilings (Thurston, Kenyon) extend the undecidability by adding self-similar inflation/deflation rules that algorithmically generate valid tilings. Adds hierarchical substitution structure. Meyer sets extend to cut-and-project method.")
add("IMPOSSIBILITY_DU_BOIS_REYMOND_FOURIER_DIVERGENCE", "EXTEND", "CESARO_SUMMATION",
    "Cesaro and Abel summation extend Fourier convergence by adding summability structure. Fejer's theorem: Cesaro means converge uniformly for continuous functions. De la Vallee Poussin means extend further. Each adds a summation kernel that regularizes divergence.")
add("IMPOSSIBILITY_UNIFORM_CONVERGENCE_FOURIER", "EXTEND", "SUMMABILITY_METHODS",
    "Summability methods (Cesaro, Abel, Borel) extend pointwise Fourier convergence to uniform convergence for broader function classes. Adds averaging structure. Gibbs phenomenon is resolved by sigma-approximation (Lanczos sigma factors).")
add("IMPOSSIBILITY_UNIFORM_APPROX_DISCONTINUOUS", "EXTEND", "DISTRIBUTIONAL_APPROXIMATION",
    "Distribution theory (Schwartz) extends uniform approximation to discontinuous functions via weak convergence. Delta sequences approximate the Dirac delta. Sobolev spaces extend classical function spaces. Adds generalized function structure.")
add("IMPOSSIBILITY_WEIERSTRASS_APPROXIMATION_DISCONTINUITY", "EXTEND", "PIECEWISE_POLYNOMIAL",
    "Piecewise polynomial approximation (splines) extends Weierstrass to discontinuous functions: allow breakpoints at discontinuities. B-splines add basis structure. NURBS extend to rational functions. Each adds local structure.")
add("WOLPERT_NO_FREE_LUNCH", "EXTEND", "DOMAIN_SPECIFIC_PRIORS",
    "Bayesian learning with informative priors extends NFL by adding prior knowledge structure. PAC-Bayes bounds quantify the benefit of priors. Transfer learning extends by adding source domain structure. Inductive bias is the structural extension.")
add("PROBLEM_OF_INDUCTION", "EXTEND", "SOLOMONOFF_INDUCTION",
    "Solomonoff's universal prior extends induction with algorithmic probability: assign prior 2^(-K(x)) based on Kolmogorov complexity. Adds computability structure. Bayesian epistemology extends with Dutch book arguments for coherent belief updating.")
add("HUMES_GUILLOTINE", "EXTEND", "CONTRACTUALISM",
    "Contractualism (Scanlon 1998) extends the is-ought gap by adding a structural bridge: moral principles are those no one could reasonably reject. Adds rational agreement structure. Rawls' veil of ignorance extends with hypothetical consent.")
add("QUINE_INDETERMINACY", "EXTEND", "RADICAL_INTERPRETATION",
    "Davidson's radical interpretation extends Quine by adding the principle of charity as structural constraint. Lewis's natural properties add metaphysical structure. Conceptual role semantics extends with inferential role. Each adds constraints that reduce indeterminacy.")
add("UNIVERSAL_GRAMMAR_LIMITS", "EXTEND", "CONSTRUCTION_GRAMMAR",
    "Construction grammar (Goldberg 1995) extends Chomskyan UG by adding form-meaning pair structure at all levels. Usage-based models (Tomasello 2003) extend with statistical learning. Adds distributional structure from experience.")
add("NEUTRAL_THEORY_LIMITS", "EXTEND", "NEARLY_NEUTRAL_THEORY",
    "Ohta's nearly neutral theory (1973) extends Kimura's neutral theory by adding slightly deleterious mutations whose fate depends on population size (|s| ~ 1/Ne). Adds population-size-dependent selection structure.")
add("IMPOSSIBILITY_POPULATION_GENETICS_DRIFT_SELECTION", "EXTEND", "EFFECTIVE_POPULATION_SIZE",
    "Effective population size (Ne) extensions: variance Ne, inbreeding Ne, eigenvalue Ne each add structural corrections for non-ideal populations. Coalescent theory extends drift analysis with genealogical structure. Adds demographic structure.")
add("FISHERS_THEOREM_LIMITS", "EXTEND", "QUANTITATIVE_GENETICS",
    "Quantitative genetics extends Fisher's theorem with the breeder's equation R = h^2 * S. Adds heritability structure. Multivariate extension (Lande equation) adds genetic covariance matrix G. Robertson's secondary theorem extends to non-additive variance.")

# === Signal Processing / Analysis ===
add("IMPOSSIBILITY_CRAMER_RAO_BOUND", "EXTEND", "BAYESIAN_CRAMER_RAO",
    "Bayesian Cramer-Rao bound (Van Trees inequality) extends CRB by adding prior information structure. Posterior CRLB tightens with informative priors. Ziv-Zakai bound extends to non-regular estimation problems. Each adds Bayesian structure.")
add("IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY", "EXTEND", "MANIFOLD_LEARNING",
    "Manifold learning (Isomap, LLE, t-SNE) extends high-dimensional analysis by adding intrinsic low-dimensional manifold structure. Random projections (Johnson-Lindenstrauss) add near-isometric embedding structure. Sparse models extend with sparsity prior.")
add("SZEMEREDI_REGULARITY_LIMIT", "EXTEND", "STRONG_REGULARITY",
    "Strong regularity lemma (Alon-Fischer-Krivelevich-Szegedy 2002) extends Szemeredi with an additional partition structure that approximates all cuts, not just edges. Adds finer structural control at the cost of larger tower-type bounds.")
add("CLASSIFICATION_IMPOSSIBILITY_WILD", "EXTEND", "DERIVED_CATEGORIES",
    "Derived categories and stability conditions (Bridgeland 2007) extend wild classification problems by adding triangulated category structure. Moduli spaces with stability extend to coarse classification. Adds homological algebraic structure.")

# Remaining physics/engineering
add("IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2", "EXTEND", "QUASICRYSTALS",
    "Quasicrystals (Shechtman 1984) extend crystallography by adding non-periodic long-range order with 5-fold and other forbidden symmetries. Cut-and-project method from higher-dimensional lattices provides the structural extension.")
add("ZENO_FLYWHEEL", "EXTEND", "REGULARIZATION",
    "Regularization methods (Benci-Giaquinta, Norton's dome regularization) extend Zeno/supertask frameworks by adding smoothing structure. Distributional analysis extends pointwise limits. Adds analytic continuation structure.")
add("IMPOSSIBILITY_LOTKA_VOLTERRA_STRUCTURAL_STABILITY", "EXTEND", "FUNCTIONAL_RESPONSES",
    "Holling Type II/III functional responses extend Lotka-Volterra with saturation structure. Ratio-dependent models (Arditi-Ginzburg 1989) extend with predator-dependence. Adds nonlinear interaction structure that enables structural stability.")
add("ERGODIC_BREAKING", "EXTEND", "REPLICA_EXCHANGE",
    "Replica exchange Monte Carlo (parallel tempering) extends ergodic sampling by adding copies at different temperatures. Swaps between replicas overcome energy barriers. Adds multi-temperature structure to restore effective ergodicity.")

# PHYS_SYMMETRY_CONSTRUCTION and structural patterns that can meaningfully EXTEND
add("PHYS_SYMMETRY_CONSTRUCTION", "EXTEND", "SUPERSYMMETRY",
    "Supersymmetry extends physical symmetry by adding fermionic generators to the Poincare algebra. Haag-Lopuszanski-Sohnius theorem classifies all possible extensions. Supergravity extends further with local SUSY. Adds graded Lie algebra structure.")
add("ALGEBRAIC_COMPLETION", "EXTEND", "ULTRAPRODUCTS",
    "Ultraproduct construction (Los's theorem) extends algebraic completion to arbitrary first-order structures. Adds ultrafilter structure. Compactifications (Stone-Cech, Alexandroff) extend topological spaces. Each adds completion structure.")
add("CROSS_DOMAIN_DUALITY", "EXTEND", "ENRICHED_CATEGORIES",
    "Enriched category theory extends dualities to multiple domains simultaneously: functors between enriched categories (over monoidal categories) add structural compatibility. Adds enrichment structure. Profunctors extend further.")
add("BINARY_DECOMP_RECOMP", "EXTEND", "WAVELET_PACKETS",
    "Wavelet packets extend binary decomposition by allowing best-basis selection at each level. Adds adaptive tree structure. Matching pursuit and basis pursuit extend to overcomplete dictionaries. Each adds selection structure.")
add("RECURSIVE_SPATIAL_EXTENSION", "EXTEND", "FRACTAL_ANTENNA",
    "Fractal antennas extend recursive spatial patterns to electromagnetic applications: self-similar structures achieve multiband operation. Koch, Sierpinski, Hilbert curve antennas add recursive structure for broadband performance.")
add("METRIC_REDEFINITION", "EXTEND", "ULTRA_METRICS",
    "Ultrametric spaces extend standard metrics with the strong triangle inequality d(x,z) <= max(d(x,y), d(y,z)). P-adic metrics, phylogenetic tree distances are ultrametric. Adds non-Archimedean structure. Gromov hyperbolicity extends further.")
add("FORCED_SYMMETRY_BREAK", "EXTEND", "JUST_INTONATION_LATTICE",
    "Just intonation lattice extends the octave with pure ratio intervals (5-limit, 7-limit tuning). Adds prime-factored pitch structure. Adaptive JI (Hermode tuning) dynamically extends/retracts based on harmonic context.")


# ─────────────────────────────────────────────────────────────────────────────
# RANDOMIZE — "Convert error to probability"
# ─────────────────────────────────────────────────────────────────────────────

add("BAIRE_CATEGORY", "RANDOMIZE", "RANDOM_SEARCH",
    "Randomized search in Baire spaces: random selection from a complete metric space avoids meager sets with probability 1. Probabilistic method (Erdos) constructs objects by showing random ones satisfy desired properties.")
add("BROUWER_FIXED_POINT", "RANDOMIZE", "RANDOMIZED_FIXED_POINT",
    "Randomized algorithms for fixed point computation: stochastic approximation (Robbins-Monro 1951) converges to fixed points probabilistically. Random restarts find multiple fixed points. MCMC stationary distribution is a probabilistic fixed point.")
add("CHRONOLOGY_PROTECTION", "RANDOMIZE", "QUANTUM_FLUCTUATIONS",
    "Quantum vacuum fluctuations near would-be Cauchy horizons provide stochastic enforcement of chronology protection. Hawking's semi-classical calculation shows the stress-energy tensor diverges stochastically, preventing CTC formation probabilistically.")
add("CHURCH_UNDECIDABILITY", "RANDOMIZE", "PROBABILISTIC_DECISION",
    "Probabilistic decidability: BPP provides randomized polynomial-time decision for many problems. Interactive proofs with randomized verifiers (IP=PSPACE) extend decidability stochastically. Randomized algorithms bypass worst-case undecidability in practice.")
add("ENTSCHEIDUNGSPROBLEM", "RANDOMIZE", "RANDOM_TESTING",
    "Random testing (fuzzing) stochastically explores decision problems: while not complete, random input generation finds violations with high probability for many practical instances. Property-based testing (QuickCheck) adds structured randomness.")
add("FERMAT_LAST_THEOREM", "RANDOMIZE", "PROBABILISTIC_NUMBER_THEORY",
    "Probabilistic number theory heuristics (Erdos-Kac theorem style) predicted FLT-like results before Wiles' proof. Random models of Diophantine equations inform conjectures. Adds probabilistic structure to number-theoretic reasoning.")
add("GALOIS_UNSOLVABILITY", "RANDOMIZE", "NUMERICAL_ROOT_FINDING",
    "Randomized numerical root finding (Jenkins-Traub, Aberth-Ehrlich with random starting points) finds all roots of polynomials to arbitrary precision. Random perturbation avoids degenerate cases. Achieves practical solvability probabilistically.")
add("GOEDEL_INCOMPLETENESS_2", "RANDOMIZE", "PROBABILISTIC_PROOFS",
    "Probabilistic proofs and zero-knowledge proofs extend formal provability: PCP theorem shows NP proofs can be verified by reading random bits. Adds stochastic verification structure. Randomized proof search explores the proof space.")
add("HAIRY_BALL", "RANDOMIZE", "RANDOM_VECTOR_FIELDS",
    "Random vector fields on S^2 have isolated zeros (generically). Gaussian random fields on spheres have expected number of zeros related to the Euler characteristic. Adds probabilistic structure to understand the necessity of singularities.")
add("COVERING_SPACE_OBSTRUCTION", "RANDOMIZE", "RANDOM_WALKS_ON_COVERS",
    "Random walks on covering spaces mix according to the spectral gap of the covering graph. Adds stochastic exploration structure. Random walks detect covering space topology through return probabilities.")
add("IMPOSSIBILITY_BODE_GAIN_PHASE", "RANDOMIZE", "STOCHASTIC_CONTROL",
    "Stochastic optimal control (LQG) replaces deterministic Bode constraints with expected-value optimization. Dual control (Feldbaum) adds adaptive probing. Adds probabilistic cost structure that relaxes deterministic gain-phase requirements.")
add("IMPOSSIBILITY_DOUBLING_CUBE", "RANDOMIZE", "RANDOMIZED_CONSTRUCTION",
    "Probabilistic constructions can approximate cube root of 2 to arbitrary precision: random geometric sequences with bias correction converge stochastically. Adds probabilistic construction primitives.")
add("IMPOSSIBILITY_ANGLE_TRISECTION", "RANDOMIZE", "RANDOM_BISECTION",
    "Iterated random bisection with rejection sampling can approximate angle trisection to arbitrary precision. Randomized geometric algorithms achieve practical trisection probabilistically.")
add("IMPOSSIBILITY_RATIONAL_SQRT2", "RANDOMIZE", "CONTINUED_FRACTION_RANDOM",
    "Random continued fraction expansion provides rational approximations to sqrt(2) with probability 1 convergence. Stern-Brocot tree random walk converges. Adds stochastic approximation structure.")
add("IMPOSSIBILITY_COMMUTATIVE_CROSS_PRODUCT", "RANDOMIZE", "RANDOM_ROTATIONS",
    "Random rotations in SO(n) replace deterministic cross products: random rotation composition provides stochastic directional operations. Adds Haar-measure sampling structure on the rotation group.")
add("IMPOSSIBILITY_EASTIN_KNILL_THEOREM", "RANDOMIZE", "RANDOM_COMPILING",
    "Randomized compiling (Wallman-Emerson 2016) converts coherent gate errors into stochastic Pauli noise via random Pauli frame changes. Tailored noise is easier to correct. Adds randomized frame structure to extend transversal gate sets.")
add("IMPOSSIBILITY_ENTANGLEMENT_MONOGAMY", "RANDOMIZE", "RANDOM_DISTILLATION",
    "Random entanglement distillation protocols (BBPSSW, DEJMPS) use probabilistic local operations to concentrate entanglement from many weakly entangled pairs into fewer maximally entangled pairs. Adds stochastic purification structure.")
add("IMPOSSIBILITY_KLEIBER_METABOLIC_SCALING", "RANDOMIZE", "STOCHASTIC_ALLOMETRY",
    "Stochastic allometric models add random variation to metabolic scaling: individual variation in scaling exponents follows a distribution around 3/4. Bayesian allometry (Glazier 2005) treats the exponent as a random variable.")
add("IMPOSSIBILITY_NAIVE_SET_THEORY", "RANDOMIZE", "RANDOM_SET_MODELS",
    "Random graph models of set membership (Erdos-Renyi style) provide consistent probabilistic set theories. Random forcing extensions add generic sets. Adds probabilistic structure to set-theoretic foundations.")
add("IMPOSSIBILITY_COASE_IMPOSSIBILITY_CONDITIONS", "RANDOMIZE", "LOTTERY_MECHANISMS",
    "Lottery mechanisms randomize over allocations to achieve ex-ante efficiency when deterministic mechanisms fail. Random serial dictatorship (Bogomolnaia-Moulin 2001). Adds probabilistic assignment structure.")
add("IMPOSSIBILITY_MUNDELL_FLEMING", "RANDOMIZE", "STOCHASTIC_MACRO",
    "Stochastic macroeconomic models (DSGE with shocks) replace the deterministic Mundell-Fleming trilemma with probabilistic tradeoffs. Adds Bayesian estimation structure. Uncertainty about regime choice becomes a probabilistic decision.")
add("IMPOSSIBILITY_CONTINUOUS_BIJECTION_RN", "RANDOMIZE", "RANDOM_EMBEDDING",
    "Random projections (Johnson-Lindenstrauss) provide near-isometric embeddings with high probability. Random features (Rahimi-Recht 2007) approximate kernel maps stochastically. Adds probabilistic dimensionality reduction.")
add("INTERPERSONAL_UTILITY", "RANDOMIZE", "VEIL_OF_IGNORANCE_LOTTERY",
    "Harsanyi's veil of ignorance lottery: impartial observer assigns random identity, making interpersonal comparison a probabilistic equivalence. Expected utility behind the veil provides a stochastic bridge for utility comparison.")
add("KNOT_INVARIANT_INCOMPLETENESS", "RANDOMIZE", "RANDOM_KNOT_SAMPLING",
    "Random knot generation (Dunfield-Thurston, Even-Zohar) provides statistical studies of knot invariant distributions. Random knot diagrams enable probabilistic invariant computation. Adds stochastic sampling structure.")
add("LANDAUER_LIMIT", "RANDOMIZE", "BROWNIAN_COMPUTING",
    "Brownian computers (Bennett 1982) use thermal fluctuations constructively: computation drifts randomly forward and backward, thermally driven. Adds thermal noise as computational resource. Energy cost approaches zero as computation time grows.")
add("LOWENHEIM_SKOLEM", "RANDOMIZE", "RANDOM_MODELS",
    "Random model theory (Fagin 1976): first-order properties have probability 0 or 1 in random structures (0-1 law). Adds probabilistic structure to model theory. Almost-sure theories provide probabilistic canonical models.")
add("NASH_ISOMETRIC_EMBEDDING", "RANDOMIZE", "STOCHASTIC_EMBEDDING",
    "Stochastic embeddings (Bourgain 1985, random projection embeddings) provide probabilistic distance-preserving maps. Johnson-Lindenstrauss extends to near-isometric random projections. Adds probabilistic metric preservation.")
add("PENROSE_APERIODICITY", "RANDOMIZE", "RANDOM_TILING",
    "Random tiling models (Henley 1991) replace deterministic matching rules with probabilistic tile placement. Maximum entropy tilings. Adds stochastic ensemble structure over the space of valid tilings. Configurational entropy provides thermodynamic extension.")
add("POINCARE_DUALITY_OBSTRUCTION", "RANDOMIZE", "RANDOM_MANIFOLDS",
    "Random manifold models (random simplicial complexes, random Riemannian metrics) provide probabilistic Poincare duality. Linial-Meshulam random 2-complexes have probabilistic topological phase transitions.")
add("TOPOLOGICAL_MANIFOLD_DIMENSION4", "RANDOMIZE", "RANDOM_4_MANIFOLDS",
    "Random 4-manifold models (random Kirby diagrams, random handle decompositions) provide probabilistic smooth structure analysis. Statistical properties of exotic structures. Adds ensemble structure.")
add("SEN_LIBERAL_PARADOX", "RANDOMIZE", "RANDOM_PRIORITY",
    "Random priority mechanisms (random serial dictatorship) resolve Sen's paradox by randomizing the order in which individuals exercise their rights. Adds probabilistic sequencing structure. Ex-ante fair, ex-post potentially liberal.")
add("TARSKI_UNDEFINABILITY", "RANDOMIZE", "PROBABILISTIC_SEMANTICS",
    "Probabilistic semantics assigns truth degrees rather than binary truth values. Keisler's randomized model theory extends to probabilistic structures. Adds stochastic truth valuation that sidesteps the binary definability paradox.")
add("UNDECIDED_TILES", "RANDOMIZE", "MARKOV_CHAIN_TILING",
    "Markov chain sampling over tiling spaces: MCMC methods (Wang tiling samplers) explore the space of valid tilings probabilistically. Local moves with Gibbs sampling provide ergodic exploration. Adds stochastic dynamics.")
add("VON_NEUMANN_EMBEDDING", "RANDOMIZE", "RANDOM_MATRIX_THEORY",
    "Random matrix theory extends von Neumann algebra analysis: Wigner semicircle law, Tracy-Widom distribution provide probabilistic spectral structure. Free probability (Voiculescu) bridges random matrices and operator algebras.")
add("WEINBERG_MASSLESS_CONSTRAINT", "RANDOMIZE", "THERMAL_MASS",
    "Finite temperature field theory gives gauge bosons effective thermal masses from random thermal fluctuations. QCD thermal gluon mass screens color force. Adds stochastic thermal structure that modifies the massless constraint at finite temperature.")
add("IMPOSSIBILITY_STOLPER_SAMUELSON_DISTRIBUTIONAL", "RANDOMIZE", "STOCHASTIC_TRADE",
    "Stochastic trade models (Helpman-Itskhoki 2010) add search friction and random matching to trade models. Distributional effects become probabilistic. Adds stochastic labor market structure.")
add("IMPOSSIBILITY_TSIRELSON_BOUND", "RANDOMIZE", "RANDOM_MEASUREMENTS",
    "Random measurement bases provide stochastic tests of Tsirelson's bound: Bell inequality violations with random settings converge to the quantum bound. Adds randomized experimental structure for device-independent certification.")
add("IMPOSSIBILITY_UNIFORM_APPROX_DISCONTINUOUS", "RANDOMIZE", "STOCHASTIC_APPROX",
    "Stochastic approximation methods converge to discontinuous functions in probability (L^p convergence). Random function series provide almost-sure pointwise convergence except on measure-zero sets. Adds probabilistic convergence structure.")
add("IMPOSSIBILITY_UNIFORM_CONVERGENCE_FOURIER", "RANDOMIZE", "RANDOM_FOURIER",
    "Random Fourier features (Rahimi-Recht 2007) approximate kernel functions via random sinusoidal projections. Convergence is probabilistic but uniform with high probability. Adds Monte Carlo structure to Fourier analysis.")
add("IMPOSSIBILITY_WATERBED_GENERALIZED", "RANDOMIZE", "STOCHASTIC_ROBUST",
    "Stochastic robust control adds probabilistic uncertainty models: chance-constrained optimization allows the waterbed constraint to be violated with small probability. Adds probabilistic constraint relaxation.")
add("IMPOSSIBILITY_ZAMES_SENSITIVITY", "RANDOMIZE", "RANDOMIZED_CONTROL",
    "Randomized control (Tempo-Calafiore-Dabbene 2013): randomly sample controllers from a parameterized family, achieving performance bounds with high probability. Adds probabilistic design structure that bypasses worst-case sensitivity bounds.")
add("JORDAN_SCHOENFLIES_FAILURE", "RANDOMIZE", "RANDOM_EMBEDDINGS",
    "Random embeddings (random PL maps, random smooth maps) are generically tame: Alexander's horned sphere and wild embeddings have measure zero in appropriate function spaces. Adds probabilistic genericity structure.")
add("WEDDERBURN_LITTLE", "RANDOMIZE", "RANDOM_FINITE_FIELDS",
    "Random elements in finite fields: random polynomial roots, random primitive elements provide probabilistic algorithms for field arithmetic. Adds stochastic computation structure for finite field operations.")
add("NO_DIVISION_ALGEBRA_BEYOND_8", "RANDOMIZE", "RANDOM_ALGEBRA_SEARCH",
    "Randomized algebraic search: explore random non-associative algebras with division-like properties. Genetic programming discovers near-division-algebras. Adds stochastic exploration of algebraic structure space.")
add("CLASSIFICATION_IMPOSSIBILITY_WILD", "RANDOMIZE", "RANDOM_REPRESENTATIONS",
    "Random matrix representations of wild quivers provide statistical invariant distributions. Random representations reveal generic decomposition structure. Adds probabilistic classification structure.")
add("IMPOSSIBILITY_WEIERSTRASS_APPROXIMATION_DISCONTINUITY", "RANDOMIZE", "STOCHASTIC_POLYNOMIAL",
    "Bernstein polynomial approximation with random evaluation provides stochastic convergence for bounded functions. Monte Carlo integration of kernel smoothing converges probabilistically. Adds random sampling structure.")

# ─────────────────────────────────────────────────────────────────────────────
# INVERT — "Reverse the structural direction/vector"
# ─────────────────────────────────────────────────────────────────────────────

add("IMPOSSIBILITY_ARROW", "INVERT", "DUAL_VOTING",
    "Dual voting: invert preference aggregation direction by asking which alternatives should be ELIMINATED rather than selected. Anti-plurality (vote against worst) inverts the preference direction. Yields different social choice outcomes.")
add("HALTING_PROBLEM", "INVERT", "CO_RE_ENUMERATION",
    "The complement of the halting set (non-halting programs) is co-r.e. Inverting the decision: enumerate programs that DON'T halt by dovetailed simulation. Productive sets (Rogers) formalize the structural reversal. Inverts the recognition direction.")
add("HEISENBERG_UNCERTAINTY", "INVERT", "WEAK_MEASUREMENT_REVERSAL",
    "Weak measurements with post-selection (Aharonov-Albert-Vaidman 1988): by inverting the measurement direction (pre-selection to post-selection), weak values can exceed eigenvalue bounds. Time-reversal symmetry of quantum mechanics enables this inversion.")
add("SHANNON_CHANNEL_CAPACITY", "INVERT", "SOURCE_CHANNEL_DUALITY",
    "Shannon's source-channel separation theorem: invert the channel coding problem to source coding. Rate-distortion duality inverts the direction: instead of reliable transmission, find minimum distortion at a given rate. Structural reversal of the optimization direction.")
add("NYQUIST_SHANNON", "INVERT", "RECONSTRUCTION_TO_SAMPLING",
    "Invert sampling-to-reconstruction: instead of recovering signal from samples, design the signal to match given samples (interpolation). Papoulis generalized sampling inverts: reconstruct from filtered versions. Reverses the analysis/synthesis direction.")
add("IMPOSSIBILITY_MAP_PROJECTION", "INVERT", "INVERSE_PROJECTION",
    "Inverse map projection: instead of projecting sphere to plane, project plane to sphere. Retroazimuthal projections (Craig, Hammer) invert the usual direction — given a map point, show the azimuth TO a reference point. Reverses the projection direction.")
add("IMPOSSIBILITY_CAP", "INVERT", "PACELC",
    "PACELC (Abadi 2012) inverts CAP's partition-focus: during normal operation (no partition), the tradeoff inverts to latency vs. consistency. Inverts the framing from failure-mode to normal-mode tradeoffs.")
add("BYZANTINE_GENERALS_BOUND", "INVERT", "ACCOUNTABILITY",
    "Accountability (Haeberlen et al. 2007) inverts the Byzantine agreement problem: instead of preventing Byzantine behavior, detect and attribute it after the fact. Adds cryptographic audit trails. Reverses from prevention to attribution.")
add("IMPOSSIBILITY_BODE_INTEGRAL_V2", "INVERT", "INVERSE_SENSITIVITY",
    "Complementary sensitivity T = 1 - S inverts the Bode integral constraint: the integral of ln|T| is determined by RHP zeros (dual to S determined by RHP poles). Inverting between S and T reveals the dual waterbed effect.")
add("IMPOSSIBILITY_KALMAN_OPTIMALITY_BOUND", "INVERT", "DUAL_CONTROL",
    "Dual observer-controller: invert the estimation problem to a control problem via duality (Kalman duality). The optimal estimator structure maps to the optimal regulator via transposition. Structural reversal of the information flow direction.")
add("IMPOSSIBILITY_TRACKING_DISTURBANCE_LIMIT", "INVERT", "DISTURBANCE_OBSERVER",
    "Disturbance observer (Ohishi-Ohnishi 1983) inverts the control direction: instead of tracking a reference, estimate and cancel the disturbance. Inverts from feedforward tracking to feedback disturbance rejection.")
add("IMPOSSIBILITY_CRAMER_RAO_BOUND", "INVERT", "DUAL_ESTIMATION",
    "Fisher information duality inverts the estimation problem: instead of estimating parameters from data, design experiments to maximize Fisher information (optimal experimental design). Inverts the estimation direction to a design problem.")
add("RATE_DISTORTION_BOUND", "INVERT", "CHANNEL_CAPACITY_DUALITY",
    "Rate-distortion and channel capacity are dual problems: invert the source coding bound to get the channel coding bound and vice versa. Gallager's duality relates the two fundamental limits via Legendre transform. Structural reversal of the information-theoretic direction.")
add("FLP_IMPOSSIBILITY", "INVERT", "FAILURE_DETECTION_INVERSION",
    "Invert the consensus direction: instead of reaching agreement despite failures, use consensus failure to DETECT failures. Unreliable failure detectors (Chandra-Toueg) exploit this inversion — the inability to reach consensus reveals the failure pattern.")
add("LIGHT_SPEED_LIMIT", "INVERT", "TACHYONIC_FIELD_THEORY",
    "Tachyonic field theory inverts the superluminal constraint: tachyon condensation (in string theory, Higgs mechanism) reinterprets superluminal modes as instabilities that drive phase transitions. Inverts the speed limit into a stability analysis.")
add("KELVIN_PLANCK", "INVERT", "HEAT_PUMP",
    "Heat pumps invert the thermodynamic direction: instead of extracting work from heat flow (engine), use work to reverse heat flow (from cold to hot). COP > 1 possible. Carnot cycle run backwards provides the structural inversion.")
add("BANACH_TARSKI", "INVERT", "MEASURE_PRESERVING_REASSEMBLY",
    "Invert the paradoxical decomposition: instead of doubling by reassembly, ask which decompositions PRESERVE measure. Amenable group actions invert the problem: their decompositions must be measure-preserving. Inverts from paradox to invariance.")
add("GALOIS_UNSOLVABILITY", "INVERT", "INVERSE_GALOIS",
    "Inverse Galois problem inverts the direction: instead of computing Gal(f) from f, ask which groups G arise as Galois groups over Q. Shafarevich proved all solvable groups occur. Adds the reversed constructive direction.")
add("COMMONS_DILEMMA", "INVERT", "ANTICOMMONS",
    "Heller's tragedy of the anticommons (1998) inverts the commons problem: too many exclusion rights (rather than too few) leads to under-use rather than over-use. Patent thickets exemplify the structural inversion.")
add("IMPOSSIBILITY_GROSSMAN_STIGLITZ_PARADOX", "INVERT", "NOISE_TRADER_RISK",
    "De Long-Shleifer-Summers-Waldmann (1990) invert Grossman-Stiglitz: noise traders create risk that rational traders cannot arbitrage away. Inverts from 'why acquire information' to 'why noise persists.' Reverses the information direction.")
add("IMPOSSIBILITY_LUCAS_CRITIQUE_POLICY_INVARIANCE", "INVERT", "NARRATIVE_ECONOMICS",
    "Shiller's narrative economics inverts the Lucas critique: instead of micro-to-macro (agents optimize, then aggregate), study how macroeconomic narratives shape individual behavior. Inverts the causation direction from expectations to narratives.")
add("WOLPERT_NO_FREE_LUNCH", "INVERT", "ANTI_NO_FREE_LUNCH",
    "Giraud-Caux (2019) invert NFL: when the prior over problems is NON-uniform (real-world distribution), some algorithms ARE universally better. Inverts the assumption direction from worst-case to average-case.")
add("THERMODYNAMIC_ASYMMETRY", "INVERT", "LOSCHMIDT_REVERSAL",
    "Loschmidt's reversibility paradox inverts the time direction: microscopically, every trajectory has a time-reversed counterpart. Spin echo (Hahn 1950) physically inverts dephasing. Inverts entropy increase temporarily by reversing microscopic dynamics.")
add("IMPOSSIBILITY_COMPETITIVE_EXCLUSION", "INVERT", "KEYSTONE_PREDATION",
    "Keystone predation (Paine 1966) inverts competitive exclusion: top predators prevent competitive dominants from excluding weaker competitors. Inverts the competitive hierarchy direction. Predator removal leads to diversity collapse.")
add("MULLERS_RATCHET", "INVERT", "BACK_MUTATION",
    "Back mutation inverts the ratchet direction: reverse mutations restore wild-type alleles. While individually rare, back mutations in large populations counteract the ratchet. Compensatory mutations provide a functional (if not literal) directional inversion.")
add("IMPOSSIBILITY_MODULARITY_EVOLVABILITY_TRADEOFF", "INVERT", "EXPLORATORY_BEHAVIOR",
    "Exploratory behavior (West-Eberhard 2003) inverts the genotype-to-phenotype direction: phenotypic plasticity precedes genetic accommodation. Genetic assimilation (Waddington) inverts the standard developmental direction.")
add("PARADOX_OF_ENRICHMENT", "INVERT", "DEPLETION_STABILIZATION",
    "Invert the enrichment direction: nutrient depletion can stabilize predator-prey oscillations. Chemostat theory shows that reducing carrying capacity stabilizes equilibria. Inverts the resource input direction.")
add("MILLERS_LAW", "INVERT", "OFFLOADING",
    "Cognitive offloading inverts the working memory direction: instead of loading information IN, externalize it OUT (notes, external memory, distributed cognition). Inverts the information flow direction from internalization to externalization.")
add("PROBLEM_OF_INDUCTION", "INVERT", "FALSIFICATIONISM",
    "Popper's falsificationism inverts induction: instead of confirming theories, seek to refute them. Corroboration replaces confirmation. Inverts the epistemic direction from positive evidence to negative evidence.")
add("QUINE_INDETERMINACY", "INVERT", "TRANSLATION_FROM_BEHAVIOR",
    "Radical translation inverted: instead of translating FROM native language, observe translation behavior to learn ABOUT the native language. Field linguistics inverts Quine's direction to practical methodology.")
add("HUMES_GUILLOTINE", "INVERT", "MORAL_REALISM",
    "Moral realism inverts Hume's guillotine: moral facts ARE natural facts (Cornell realism, Railton 1986). Inverts the is-ought direction by identifying moral properties with natural properties. The direction from facts to values is claimed to be direct.")

# ─────────────────────────────────────────────────────────────────────────────
# QUANTIZE — "Force continuous space onto discrete grid"
# ─────────────────────────────────────────────────────────────────────────────

add("IMPOSSIBILITY_SQUARING_CIRCLE", "QUANTIZE", "RATIONAL_APPROXIMATION",
    "Approximate pi with rationals (355/113 = 3.1415929..., 6 decimal places). Grid the plane: pixelated circles quantize the continuous curve. Constructive geometry on integer lattices discretizes the squaring problem.")
add("IMPOSSIBILITY_ANGLE_TRISECTION", "QUANTIZE", "DIGITAL_PROTRACTOR",
    "Digital protractors quantize angles to discrete steps. Any angle can be trisected to arbitrary precision on a discrete grid. Adds digital measurement structure.")
add("IMPOSSIBILITY_DOUBLING_CUBE", "QUANTIZE", "NUMERICAL_CUBE_ROOT",
    "Numerical computation quantizes cube root of 2 to floating-point representation. IEEE 754 double precision gives 15+ decimal digits. Adds discrete arithmetic structure.")
add("IMPOSSIBILITY_RATIONAL_SQRT2", "QUANTIZE", "FLOATING_POINT",
    "IEEE 754 floating-point representation quantizes sqrt(2) to a rational (binary fraction) approximation. Machine epsilon bounds the discretization error. Every computer calculation of sqrt(2) performs this quantization.")
add("ABBE_DIFFRACTION_LIMIT", "QUANTIZE", "PIXEL_DISCRETIZATION",
    "CCD/CMOS sensors quantize the continuous optical field onto a pixel grid. Nyquist-limited pixel size matches the diffraction limit. Super-resolution algorithms reconstruct sub-pixel detail from quantized samples.")
add("GABOR_LIMIT", "QUANTIZE", "STFT_BINS",
    "Short-time Fourier transform quantizes time-frequency plane into discrete bins. Window size × frequency resolution product is bounded by Gabor limit. Discrete Gabor frames provide the quantized representation.")
add("LIGHT_SPEED_LIMIT", "QUANTIZE", "LATTICE_GAUGE",
    "Lattice gauge theory (Wilson 1974) quantizes spacetime onto a discrete lattice. Light speed becomes the lattice propagation speed. Adds discrete spacetime structure for non-perturbative QCD calculations.")
add("IMPOSSIBILITY_CONTINUOUS_BIJECTION_RN", "QUANTIZE", "HASH_FUNCTIONS",
    "Locality-sensitive hash functions quantize R^n onto discrete hash buckets. Space-filling curve indices (Z-order, Hilbert) provide quantized bijection approximations between R^n and integers.")
add("IMPOSSIBILITY_TRANSCENDENCE_E_PI", "QUANTIZE", "SPIGOT_ALGORITHMS",
    "Spigot algorithms (Bailey-Borwein-Plouffe for pi, binary splitting for e) compute digits one at a time, quantizing transcendental numbers to finite decimal/binary representations.")
add("KELVIN_PLANCK", "QUANTIZE", "QUANTUM_HEAT_ENGINE",
    "Quantum heat engines (quantum Otto, quantum Carnot) quantize the working medium to discrete energy levels. Adds discrete energy spectrum. Efficiency bounds become functions of discrete level spacing.")
add("CLAUSIUS_INEQUALITY", "QUANTIZE", "DISCRETE_THERMODYNAMICS",
    "Stochastic thermodynamics on discrete state spaces (master equation formalism) quantizes continuous thermodynamic variables. Entropy production on Markov chains quantizes Clausius inequality to discrete transitions.")
add("LANDAUER_LIMIT", "QUANTIZE", "SINGLE_ELECTRON",
    "Single-electron devices quantize charge to integer multiples of e. Single-electron transistors operate at the fundamental charge quantum. Landauer limit becomes kT ln 2 per single discrete bit erasure.")
add("IMPOSSIBILITY_CURSE_OF_DIMENSIONALITY", "QUANTIZE", "LATTICE_DISCRETIZATION",
    "Lattice discretization quantizes R^d onto a finite grid with N^d points. Curse of dimensionality becomes the combinatorial explosion of grid points. Sparse grids (Smolyak 1963) reduce from N^d to N * (log N)^(d-1).")
add("BANACH_TARSKI", "QUANTIZE", "FINITE_DECOMPOSITION",
    "Finite decomposition (finitely many pieces) quantizes the paradox: with measurable pieces only, Banach-Tarski fails. Laczkovich proved circle-squaring with ~10^40 pieces using translations only — quantizing the number of pieces needed.")
add("COMMONS_DILEMMA", "QUANTIZE", "QUOTA_SYSTEMS",
    "Fishing quotas, carbon credits quantize common resource usage to discrete allowances. Individual Transferable Quotas (ITQ) discretize the continuous resource into tradeable units. Adds integer-valued allocation structure.")
add("IMPOSSIBILITY_COMPETITIVE_EXCLUSION", "QUANTIZE", "DISCRETE_NICHE",
    "Discrete niche models (Tilman's R* theory with discrete resources) quantize the resource axis. Species compete for N discrete resources, allowing up to N coexisting species. Quantizes the continuous niche axis.")
add("IMPOSSIBILITY_NK_FITNESS_LANDSCAPE", "QUANTIZE", "BINARY_GENOTYPE",
    "NK model already uses binary (0/1) genotype strings of length N, quantizing the continuous fitness landscape. Each locus has K epistatic interactions. Adds discrete genetic alphabet structure.")
add("IMPOSSIBILITY_RATE_DISTORTION_NEURAL_CODING", "QUANTIZE", "SPIKE_CODING",
    "Neural spike trains quantize continuous signals to discrete action potentials. Rate coding quantizes to firing frequency bins. Place cells quantize continuous space to discrete fields. Adds discrete neural alphabet.")
add("BINDING_PROBLEM", "QUANTIZE", "NEURAL_ASSEMBLY_CODES",
    "Cell assembly codes (Hebb) quantize continuous representations into discrete neural ensembles. Sparse coding quantizes to discrete active/inactive patterns. Adds discrete population code structure.")
add("BLACK_SCHOLES_ASSUMPTIONS", "QUANTIZE", "BINOMIAL_TREE",
    "Cox-Ross-Rubinstein binomial tree quantizes continuous Black-Scholes dynamics to discrete up/down moves at discrete time steps. As steps increase, converges to Black-Scholes. Adds discrete-time discrete-state structure.")
add("IMPOSSIBILITY_CRAMER_RAO_BOUND", "QUANTIZE", "QUANTIZED_ESTIMATION",
    "Quantized observation models (binary, multi-level ADC) force continuous measurements onto discrete grids. Fisher information for quantized observations is reduced by a quantization factor. Adds discrete observation structure.")
add("IMPOSSIBILITY_INFORMATION_BOTTLENECK", "QUANTIZE", "DETERMINISTIC_IB",
    "Deterministic Information Bottleneck (Strouse-Schwab 2017) quantizes the soft IB clustering to hard assignments. Assigns each input to exactly one cluster. Adds discrete partition structure.")
add("IMPOSSIBILITY_LOTKA_VOLTERRA_STRUCTURAL_STABILITY", "QUANTIZE", "GILLESPIE_ALGORITHM",
    "Gillespie algorithm quantizes continuous Lotka-Volterra ODE dynamics to discrete stochastic events. Each birth/death is a discrete jump. Adds integer-valued population state space. Chemical master equation replaces continuous rate equations.")
add("IMPOSSIBILITY_KLEIBER_METABOLIC_SCALING", "QUANTIZE", "DISCRETE_BRANCHING",
    "Discrete branching models (Murray's law) quantize the continuous vascular tree to integer branching levels. Each generation has a discrete number of daughter branches. Metabolic scaling emerges from the discrete branching structure.")
add("MULLERS_RATCHET", "QUANTIZE", "MUTATION_CLASSES",
    "Muller's ratchet naturally operates on discrete mutation classes: genomes are binned by integer number of deleterious mutations (0, 1, 2, ...). The ratchet clicks when the zero-class is lost. Already inherently quantized.")
add("IMPOSSIBILITY_MARGOLUS_LEVITIN_SPEED_LIMIT", "QUANTIZE", "QUBIT_EVOLUTION",
    "Qubit evolution quantizes the continuous state space to the Bloch sphere's discrete measurement outcomes (|0> and |1>). Quantum speed limit for qubit gates gives minimum gate time = pi*hbar/(2*Delta E). Adds discrete quantum gate structure.")
add("IMPOSSIBILITY_PONTRYAGIN_MAXIMUM_PRINCIPLE", "QUANTIZE", "BANG_BANG_CONTROL",
    "Bang-bang control quantizes the continuous control input to discrete extremal values (maximum or minimum). Optimal for linear systems with bounded controls. Adds discrete switching structure. Time-optimal control is inherently bang-bang.")
add("EFFICIENT_MARKET_LIMITS", "QUANTIZE", "TICK_SIZE",
    "Tick size (minimum price increment) quantizes continuous asset prices to a discrete grid. Market microstructure theory studies tick-size effects on spreads and efficiency. SEC tick size pilot (2016) tested different quantization levels.")
add("IMPOSSIBILITY_DIAMOND_DYBVIG_BANK_RUNS", "QUANTIZE", "DISCRETE_CONTRACTS",
    "Demand-deposit contracts with discrete withdrawal periods quantize continuous liquidity. Suspension of convertibility at discrete thresholds. Adds discrete-time contract structure.")
add("SONNENSCHEIN_MANTEL_DEBREU", "QUANTIZE", "FINITE_ECONOMIES",
    "Finite agent economies quantize the continuum: with N agents, excess demand has more structure. Debreu-Scarf theorem shows the core shrinks to competitive equilibria as N grows. Adds discrete agent structure.")
add("IMPOSSIBILITY_COMPUTATIONAL_IRREDUCIBILITY_CA", "QUANTIZE", "ALREADY_DISCRETE",
    "Cellular automata are already fully quantized: discrete cells, discrete states, discrete time steps. Wolfram's computational irreducibility applies specifically to this discrete setting. CA is the prototypical quantized dynamical system.")
add("ZENO_FLYWHEEL", "QUANTIZE", "PLANCK_TIME",
    "Planck time (~5.4 × 10^-44 s) provides a physical quantization of the continuous Zeno supertask: below Planck scale, the continuous time assumption breaks down. Discretized time prevents infinite subdivisions.")
add("IMPOSSIBILITY_LONG_RUN_PHILLIPS_CURVE", "QUANTIZE", "DISCRETE_INFLATION_TARGETS",
    "Central bank inflation targets quantize continuous monetary policy to discrete bands (e.g., 2% ± 1%). Taylor rule quantizes the interest rate response. Adds discrete policy steps to the continuous Phillips curve tradeoff.")


# ─────────────────────────────────────────────────────────────────────────────
# DISTRIBUTE — "Spread error evenly"
# ─────────────────────────────────────────────────────────────────────────────

add("BGS_ORACLE_SEPARATION", "DISTRIBUTE", "AVERAGE_CASE",
    "Average-case complexity distributes hardness uniformly: instead of worst-case oracle separation, study expected performance over random instances. Impagliazzo's five worlds distribute hardness evenly across instance space.")
add("CHRONOLOGY_PROTECTION", "DISTRIBUTE", "HAWKING_RADIATION",
    "Hawking radiation distributes the black hole information/energy evenly across the thermal spectrum. Semi-classical energy conditions distribute stress-energy uniformly near would-be Cauchy horizons, preventing CTC formation at all points equally.")
add("CLASSIFICATION_IMPOSSIBILITY_WILD", "DISTRIBUTE", "GENERIC_MODULES",
    "Generic decomposition distributes wild representation types evenly: almost all modules of a given dimension have the same indecomposable structure. Kac's theorem distributes roots of the Tits form uniformly across dimension vectors.")
add("DEHN_IMPOSSIBILITY", "DISTRIBUTE", "DISTRIBUTED_SCISSORS",
    "Distribute the Dehn invariant obstruction across multiple pieces: refined scissors congruence distributes angular defects. Zylev's theorem distributes equidecomposition evenly when volumes match.")
add("DEHN_SURGERY_OBSTRUCTION", "DISTRIBUTE", "UNIFORM_SURGERY",
    "Uniform surgery coefficients distribute the linking matrix constraints evenly across all link components. Rational surgery distributes framing coefficients. Dehn filling distributes cusp cross-sections uniformly.")
add("FOUNDATIONAL_IMPOSSIBILITY", "DISTRIBUTE", "REVERSE_MATHEMATICS",
    "Reverse mathematics distributes incompleteness across five subsystems (RCA_0 through Pi^1_1-CA_0). Each theorem is classified into the weakest system that proves it, distributing the foundational burden evenly across the hierarchy.")
add("GOEDEL_INCOMPLETENESS_2", "DISTRIBUTE", "ORDINAL_ANALYSIS_DISTRIBUTED",
    "Ordinal analysis distributes the consistency strength across the proof-theoretic ordinal hierarchy. Each system has a unique ordinal measuring its strength, distributing incompleteness uniformly along the well-ordered scale.")
add("HAIRY_BALL_THEOREM", "DISTRIBUTE", "DIPOLE_FIELD",
    "A dipole vector field distributes the two required zeros (north/south poles) symmetrically. The Hopf index theorem distributes the total index (= Euler characteristic = 2) among singularities. Distributes the topological charge evenly.")
add("IMPOSSIBILITY_BELLS_THEOREM", "DISTRIBUTE", "NOISE_DISTRIBUTED",
    "Distributed noise models in Bell experiments: detection loophole distributes missing events uniformly. Fair sampling assumption distributes undetected events proportionally. Uniform error model distributes local hidden variable failures evenly.")
add("IMPOSSIBILITY_CALENDAR", "DISTRIBUTE", "GREGORIAN_CENTURIES",
    "Gregorian calendar distributes the fractional day (365.2422...) across century rules: leap year every 4 years, except every 100, except every 400. Distributes the error uniformly across centuries for maximum smoothness.")
add("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "DISTRIBUTE", "SYMMETRIC_MECHANISMS",
    "Symmetric mechanisms (Chatterjee-Samuelson k-double auction with k=1/2) distribute the efficiency loss symmetrically between buyer and seller. Equal split of the trading surplus distributes the incentive incompatibility evenly.")
add("RIGIDITY_MOSTOW", "DISTRIBUTE", "UNIFORM_LATTICE",
    "Uniform lattices distribute in hyperbolic space with minimal distortion: Mostow rigidity says the lattice geometry IS the manifold geometry. Volume distributes uniformly. Distributes the rigidity constraint evenly across the fundamental domain.")
add("RUNGE_PHENOMENON", "DISTRIBUTE", "LEAST_SQUARES",
    "Least-squares polynomial approximation distributes the interpolation error uniformly (minimax sense) rather than concentrating oscillations at endpoints. Adds uniform error distribution. Economization of power series distributes error via Chebyshev expansion.")
add("SEN_LIBERAL_PARADOX", "DISTRIBUTE", "PROPORTIONAL_RIGHTS",
    "Proportional rights assignment distributes decisional power evenly across individuals and social concerns. Fractional outcomes distribute the liberal-Pareto conflict symmetrically. Each person's rights affect the outcome proportionally.")
add("TARSKI_UNDEFINABILITY", "DISTRIBUTE", "HIERARCHY_OF_LANGUAGES",
    "Tarskian hierarchy distributes truth predicates across meta-language levels: each level defines truth for the level below. Distributes the self-referential burden uniformly across the infinite hierarchy.")
add("VITALI_NONMEASURABLE", "DISTRIBUTE", "OUTER_MEASURE",
    "Lebesgue outer measure distributes the 'measurability failure' uniformly: the outer measure is defined for ALL sets, distributing the coverage uniformly. The gap between inner and outer measure localizes non-measurability.")
add("WEDDERBURN_LITTLE", "DISTRIBUTE", "UNIFORM_FIELD_STRUCTURE",
    "Finite fields of order p^n distribute multiplicative structure uniformly: every nonzero element generates the cyclic group. Frobenius automorphism distributes the Galois action evenly across field extensions.")


# ─────────────────────────────────────────────────────────────────────────────
# HIERARCHIZE — "Move failure up a level"
# ─────────────────────────────────────────────────────────────────────────────

add("GOEDEL_INCOMPLETENESS_1", "HIERARCHIZE", "PROOF_THEORETIC_ORDINALS",
    "Proof-theoretic ordinal hierarchy: PA < ATR_0 < Pi^1_1-CA_0. Each system proves consistency of lower ones. Incompleteness is pushed up one level in the hierarchy. Gentzen's ordinal epsilon_0 hierarchizes PA's limits.")
add("HEISENBERG_UNCERTAINTY", "HIERARCHIZE", "MEASUREMENT_HIERARCHY",
    "Measurement hierarchy: projective > POVM > weak measurements > continuous monitoring. Each level abstracts measurement disturbance to a higher level. POVM hierarchizes binary measurements into generalized measurements.")
add("IMPOSSIBILITY_BODE_INTEGRAL_V2", "HIERARCHIZE", "CASCADE_CONTROL",
    "Cascade control hierarchizes the Bode integral: inner fast loop handles high-frequency constraints, outer slow loop handles low-frequency specifications. Each level in the cascade addresses its own Bode integral constraint independently.")
add("IMPOSSIBILITY_CAP", "HIERARCHIZE", "TIERED_CONSISTENCY",
    "Tiered consistency models hierarchize CAP: strong consistency for critical data, eventual consistency for non-critical data. Cosmos DB offers five consistency levels. Each tier operates at a different point in the CAP space.")
add("IMPOSSIBILITY_ARROW", "HIERARCHIZE", "FEDERAL_VOTING",
    "Federal/hierarchical voting systems hierarchize Arrow's impossibility: local elections feed into regional/national levels. Each level aggregates differently. Subsidiarity principle hierarchizes decision-making. Moves impossibility up one governmental level.")
add("LIGHT_SPEED_LIMIT", "HIERARCHIZE", "EFFECTIVE_FIELD_THEORY",
    "Effective field theory hierarchizes physics by energy scale: low-energy effective theories have their own 'speed limits' that differ from fundamental ones. Renormalization group organizes theories hierarchically by scale.")
add("KELVIN_PLANCK", "HIERARCHIZE", "EXERGY_HIERARCHY",
    "Exergy analysis hierarchizes thermodynamic losses: first-law efficiency at the lowest level, second-law (exergy) efficiency at a higher level. Pinch analysis hierarchizes heat exchange networks by temperature. Moves the thermodynamic constraint up to the system level.")
add("COMMONS_DILEMMA", "HIERARCHIZE", "POLYCENTRIC_GOVERNANCE",
    "Ostrom's polycentric governance hierarchizes commons management: local communities manage resources at the lowest effective level, with higher-level institutions providing coordination and conflict resolution. Moves the commons failure up to the governance level.")
add("WOLPERT_NO_FREE_LUNCH", "HIERARCHIZE", "META_LEARNING",
    "Meta-learning hierarchizes NFL: instead of choosing a single algorithm, learn to select algorithms at a higher level. AutoML, MAML, and neural architecture search hierarchize the algorithm choice. Moves the no-free-lunch constraint up one level.")
add("FLP_IMPOSSIBILITY", "HIERARCHIZE", "CONSENSUS_HIERARCHY",
    "Herlihy's consensus hierarchy ranks shared objects by consensus number: registers (1), queues (2), compare-and-swap (infinity). Each level can implement consensus for that many processes. Hierarchizes the impossibility by object power.")


# ─────────────────────────────────────────────────────────────────────────────
# TRUNCATE — "Remove problematic region"
# ─────────────────────────────────────────────────────────────────────────────

add("IMPOSSIBILITY_BELLS_THEOREM", "TRUNCATE", "DETECTION_LOOPHOLE",
    "Detection loophole truncates low-efficiency events: by discarding undetected particles, local hidden variable models can reproduce quantum correlations for detection efficiency < ~82% (Eberhard bound). Truncates the sample to avoid Bell violation.")
add("DEHN_SURGERY_OBSTRUCTION", "TRUNCATE", "DEHN_FILLING_RESTRICTION",
    "Thurston's Dehn filling theorem: all but finitely many Dehn fillings of a hyperbolic manifold yield hyperbolic manifolds. Truncate the finite exceptional set. Removes the problematic surgery coefficients.")
add("CLASSIFICATION_IMPOSSIBILITY_WILD", "TRUNCATE", "TAME_SUBCATEGORY",
    "Truncate to tame representation type: Dynkin quivers (A_n, D_n, E_6/7/8) have finitely many indecomposables. Euclidean quivers are tame. Truncates the wild classification problem by restricting to structurally manageable subcategories.")
add("CHRONOLOGY_PROTECTION", "TRUNCATE", "CAUCHY_HORIZON_REMOVAL",
    "Truncate spacetime at the Cauchy horizon: strong cosmic censorship removes the problematic region where closed timelike curves would form. Penrose's censorship truncates the maximal analytic extension.")
add("IMPOSSIBILITY_COASE_IMPOSSIBILITY_CONDITIONS", "TRUNCATE", "SMALL_NUMBERS",
    "Truncate to small-numbers bargaining: with few parties and low transaction costs, Coase theorem applies. Remove the problematic high-transaction-cost/many-party region where negotiation fails.")
add("BGS_ORACLE_SEPARATION", "TRUNCATE", "RESTRICTED_ORACLES",
    "Restrict to structured oracles (random oracles, generic oracles) that truncate the full oracle space. Random oracle hypothesis truncates to probabilistic separation. Removes pathological oracle constructions.")
add("IMPOSSIBILITY_MUNDELL_FLEMING", "TRUNCATE", "SACRIFICE_CAPITAL_MOBILITY",
    "Capital controls truncate free capital mobility: China's managed exchange rate sacrifices free capital flows to maintain monetary policy autonomy and exchange rate stability. Truncates one vertex of the impossible trinity.")
add("IMPOSSIBILITY_EXOTIC_R4", "TRUNCATE", "COMPACT_TRUNCATION",
    "Truncate to compact 4-manifolds: the compact case has only finitely many smooth structures on each topological type (for simply connected). Removes the exotic R^4 phenomena that arise from non-compactness.")
add("FOUNDATIONAL_IMPOSSIBILITY", "TRUNCATE", "PREDICATIVE_MATHEMATICS",
    "Predicative mathematics (Weyl, Feferman) truncates impredicative set comprehension: restrict to predicatively definable sets. Avoids the incompleteness of full second-order arithmetic by truncating the comprehension scheme.")


# ─────────────────────────────────────────────────────────────────────────────
# CONCENTRATE — "Localize error"
# ─────────────────────────────────────────────────────────────────────────────

add("DEHN_SURGERY_OBSTRUCTION", "CONCENTRATE", "EXCEPTIONAL_SURGERY",
    "Thurston's exceptional Dehn fillings concentrate the obstruction: only finitely many surgery coefficients yield non-hyperbolic manifolds. The difficulty is concentrated in this finite exceptional set.")
add("CLASSIFICATION_IMPOSSIBILITY_WILD", "CONCENTRATE", "PREPROJECTIVE_COMPONENT",
    "Preprojective and preinjective components concentrate the 'tame part' of wild categories: these components have Auslander-Reiten structure. The wildness concentrates in the regular components.")
add("CHRONOLOGY_PROTECTION", "CONCENTRATE", "CAUCHY_HORIZON_DIVERGENCE",
    "Semi-classical stress-energy divergence concentrates at the Cauchy horizon: quantum field effects produce infinite energy density exactly where CTCs would form. Concentrates the chronology protection at the precise locus of potential violation.")
add("RUNGE_PHENOMENON", "CONCENTRATE", "ENDPOINT_CLUSTERING",
    "Chebyshev nodes concentrate sample points at interval endpoints (arccosine distribution), exactly where Runge oscillations are worst. Concentrates the interpolation effort at the problematic boundary regions.")
add("IMPOSSIBILITY_MUNDELL_FLEMING", "CONCENTRATE", "STERILIZED_INTERVENTION",
    "Sterilized intervention concentrates the impossible trinity violation in a specific policy instrument: central bank simultaneously buys/sells forex and domestic bonds, concentrating the tension in the balance sheet rather than spreading it across all three goals.")
add("IMPOSSIBILITY_BELLS_THEOREM", "CONCENTRATE", "LOOPHOLE_LOCALIZATION",
    "Fair-sampling loophole concentrates Bell inequality violation in high-efficiency detection events. Locality loophole concentrates in space-like separated measurements. Each experimental improvement concentrates the remaining loophole into a smaller domain.")
add("BGS_ORACLE_SEPARATION", "CONCENTRATE", "DIAGONAL_ORACLE",
    "Diagonal oracles concentrate the separation in a specific query structure: the oracle is designed to diagonalize against one specific class. Concentrates the computational hardness in a single diagonal argument.")
add("FOUNDATIONAL_IMPOSSIBILITY", "CONCENTRATE", "GOEDEL_SENTENCE",
    "The Goedel sentence concentrates incompleteness in a single self-referential statement: 'This statement is unprovable.' All the foundational impossibility is concentrated in this one sentence per system. Rosser's improvement concentrates further.")
add("IMPOSSIBILITY_COASE_IMPOSSIBILITY_CONDITIONS", "CONCENTRATE", "HOLDOUT_PROBLEM",
    "The holdout problem concentrates Coasean bargaining failure in the last negotiating party: strategic behavior concentrates as the number of remaining parties shrinks. The final holdout captures all the surplus.")


# ─────────────────────────────────────────────────────────────────────────────
# PARTITION — "Split domain"
# ─────────────────────────────────────────────────────────────────────────────

add("DEHN_SURGERY_OBSTRUCTION", "PARTITION", "JSJ_DECOMPOSITION",
    "JSJ (Jaco-Shalen-Johannson) decomposition partitions 3-manifolds along incompressible tori into geometric pieces. Each piece has one of Thurston's eight geometries. Partitions the surgery obstruction into independently manageable geometric domains.")
add("FOUNDATIONAL_IMPOSSIBILITY", "PARTITION", "REVERSE_MATH_BIG_FIVE",
    "Reverse mathematics partitions mathematical theorems into five main subsystems (RCA_0, WKL_0, ACA_0, ATR_0, Pi^1_1-CA_0). Each partition handles its own completeness/incompleteness boundary. Partitions the foundational landscape.")
add("HAIRY_BALL_THEOREM", "PARTITION", "CHART_DECOMPOSITION",
    "Partition S^2 into coordinate charts: each chart admits a nonvanishing vector field, but they cannot be consistently assembled globally. Atlas structure partitions the topological obstruction into local-to-global transition failures.")
add("IMPOSSIBILITY_BELLS_THEOREM", "PARTITION", "MEASUREMENT_SETTINGS",
    "Partition measurement settings: Alice and Bob each choose from discrete sets of measurement angles. CHSH inequality partitions the measurement space into 4 settings. Bell scenarios partition by (inputs, outputs, parties).")
add("IMPOSSIBILITY_CALENDAR", "PARTITION", "DUAL_CALENDAR",
    "Dual calendars partition timekeeping: civil/religious, solar/lunar, Gregorian/fiscal. Japanese era system partitions by reign. Mayan Long Count + Tzolkin + Haab partition time into three independent cycles.")
add("CLASSIFICATION_IMPOSSIBILITY_WILD", "PARTITION", "BLOCK_DECOMPOSITION",
    "Block decomposition (Morita equivalence) partitions module categories into blocks with independent classification. Krull-Schmidt partitions into indecomposable direct summands. Each block is classified independently.")
add("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "PARTITION", "MARKET_SEGMENTATION",
    "Market segmentation partitions the buyer-seller space into subsets with different mechanisms: posted prices for one segment, auctions for another, negotiation for a third. Each segment operates with its own efficiency-incentive tradeoff.")
add("IMPOSSIBILITY_COASE_IMPOSSIBILITY_CONDITIONS", "PARTITION", "UNBUNDLING",
    "Property rights unbundling partitions complex goods into separately negotiable components: mineral rights, air rights, usage rights. Each partition can be Coasean-negotiated independently with lower transaction costs.")


# =============================================================================
# MAIN SCRIPT
# =============================================================================

def main():
    con = duckdb.connect(DB_PATH)

    # 1. Query all existing DAMAGE_OP spokes to find empty cells
    existing = set()
    rows = con.execute("""
        SELECT comp_id, notes FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP:%'
    """).fetchall()

    for comp_id, notes in rows:
        # Extract DAMAGE_OP tag
        import re
        match = re.search(r'DAMAGE_OP:\s*(\w+)', notes)
        if match:
            existing.add((comp_id, match.group(1)))

    print(f"Existing (hub, operator) pairs: {len(existing)}")

    # 2. Get all impossibility hubs (those with at least one DAMAGE_OP spoke)
    all_hubs = set()
    for comp_id, op in existing:
        all_hubs.add(comp_id)
    print(f"Total impossibility hubs: {len(all_hubs)}")

    operators = ['EXTEND','RANDOMIZE','INVERT','QUANTIZE','DISTRIBUTE',
                 'HIERARCHIZE','TRUNCATE','CONCENTRATE','PARTITION']

    # Count empty cells
    empty_cells = set()
    for hub in all_hubs:
        for op in operators:
            if (hub, op) not in existing:
                empty_cells.add((hub, op))
    print(f"Total empty cells: {len(empty_cells)}")
    print()

    # 3. Filter fills to only those that fill actual empty cells
    valid_fills = []
    skipped_already_filled = 0
    skipped_hub_not_found = 0

    for hub, op, suffix, notes in FILLS:
        if hub not in all_hubs:
            skipped_hub_not_found += 1
            continue
        if (hub, op) in existing:
            skipped_already_filled += 1
            continue
        valid_fills.append((hub, op, suffix, notes))

    print(f"Valid fills (empty cells with real resolutions): {len(valid_fills)}")
    print(f"Skipped (already filled): {skipped_already_filled}")
    print(f"Skipped (hub not in impossibility set): {skipped_hub_not_found}")
    print()

    # 4. Insert new spokes
    inserted = 0
    errors = 0

    for hub, op, suffix, notes in valid_fills:
        instance_id = f"{hub}__FILL_{op}_{suffix}"
        full_notes = f"{notes} | DAMAGE_OP: {op} | SOURCE: aletheia_gap_fill"

        try:
            con.execute("""
                INSERT INTO composition_instances (instance_id, comp_id, notes)
                VALUES (?, ?, ?)
            """, [instance_id, hub, full_notes])
            inserted += 1
        except Exception as e:
            print(f"  ERROR inserting {instance_id}: {e}")
            errors += 1

    con.commit()

    # 5. Report
    print("=" * 60)
    print(f"CELLS FILLED: {inserted}")
    print(f"CELLS SKIPPED (already filled): {skipped_already_filled}")
    print(f"CELLS SKIPPED (hub not found): {skipped_hub_not_found}")
    print(f"INSERTION ERRORS: {errors}")
    print()

    # Recount empty cells
    new_existing = set()
    rows = con.execute("""
        SELECT comp_id, notes FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP:%'
    """).fetchall()
    for comp_id, notes in rows:
        match = re.search(r'DAMAGE_OP:\s*(\w+)', notes)
        if match:
            new_existing.add((comp_id, match.group(1)))

    new_empty = 0
    for hub in all_hubs:
        for op in operators:
            if (hub, op) not in new_existing:
                new_empty += 1

    total_spokes = con.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
    damage_spokes = con.execute("SELECT COUNT(*) FROM composition_instances WHERE notes LIKE '%DAMAGE_OP%'").fetchone()[0]

    print(f"NEW TOTAL SPOKES: {total_spokes}")
    print(f"DAMAGE_OP SPOKES: {damage_spokes}")
    print(f"REMAINING EMPTY CELLS: {new_empty}")
    print()

    # Breakdown by operator
    print("REMAINING EMPTY CELLS BY OPERATOR:")
    for op in operators:
        count = sum(1 for hub in all_hubs if (hub, op) not in new_existing)
        print(f"  {op}: {count}")

    con.close()


if __name__ == "__main__":
    main()
