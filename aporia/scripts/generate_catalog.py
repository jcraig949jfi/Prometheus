"""
Aporia — Generate the open-questions catalog from crawled data.

Writes one questions.jsonl per domain under aporia/<domain>/questions.jsonl.
Each line is a JSON object following the Aporia schema.
"""

import json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── helpers ──────────────────────────────────────────────────────────────
_counters = {}

def _id(domain_code):
    _counters.setdefault(domain_code, 0)
    _counters[domain_code] += 1
    return f"{domain_code}-{_counters[domain_code]:04d}"

def q(domain, domain_code, subdomain, title, statement, **kw):
    return {
        "id": _id(domain_code),
        "title": title,
        "domain": domain,
        "subdomain": subdomain,
        "statement": statement,
        "status": kw.get("status", "open"),
        "importance": kw.get("importance", ""),
        "year_posed": kw.get("year_posed", None),
        "posed_by": kw.get("posed_by", ""),
        "sources": kw.get("sources", []),
        "tags": kw.get("tags", []),
        "related_ids": [],
        "papers": [],
        "notes": kw.get("notes", ""),
    }

WIKI = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_"

# ── MATHEMATICS ──────────────────────────────────────────────────────────
def math_questions():
    W = WIKI + "mathematics"
    D, C = "mathematics", "MATH"
    qs = []
    def m(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    # Algebra
    m("algebra", "Birch-Tate conjecture", "Relates the order of the center of the Steinberg group to a number field's Dedekind zeta function.")
    m("algebra", "Casas-Alvero conjecture", "A polynomial sharing factors with all its derivatives must be a power of a linear polynomial.")
    m("operator_algebra", "Connes embedding problem", "Concerns splitting properties in von Neumann algebra theory.")
    m("matrix_theory", "Crouzeix's conjecture", "Matrix norm of a function applied to a matrix is at most twice its supremum over field of values.")
    m("linear_algebra", "Determinantal conjecture", "The determinant of summed normal matrices satisfies specific inequalities.")
    m("homological_algebra", "Eilenberg-Ganea conjecture", "Groups with cohomological dimension 2 possess 2-dimensional Eilenberg-MacLane spaces.")
    m("k_theory", "Farrell-Jones conjecture", "Assembly maps are isomorphisms for certain algebraic K-groups.")
    m("universal_algebra", "Finite lattice representation problem", "Every finite lattice is isomorphic to congruence lattice of some finite algebra.")
    m("algebraic_geometry", "Goncharov conjecture", "Concerns cohomology of certain motivic complexes.")
    m("algebraic_geometry", "Green's conjecture", "Clifford index of non-hyperelliptic curves determined by linear syzygy properties.")
    m("differential_algebra", "Grothendieck-Katz p-curvature conjecture", "A local-global principle for linear differential equations.")
    m("combinatorial_matrix_theory", "Hadamard conjecture", "Hadamard matrices exist for every positive integer multiple of 4.")
    m("matrix_theory", "Hadamard's maximal determinant problem", "Maximum determinant of matrices with +/-1 entries.")
    m("algebraic_geometry", "Hilbert's fifteenth problem", "Establish rigorous foundations for Schubert calculus.")
    m("real_algebraic_geometry", "Hilbert's sixteenth problem", "Characterize possible configurations of M-curve components.")
    m("commutative_algebra", "Homological conjectures in commutative algebra", "Multiple related open problems about homological properties of local rings.")
    m("ring_theory", "Jacobson's conjecture", "Intersection of all Jacobson radical powers in Noetherian rings equals zero.")
    m("ring_theory", "Kaplansky's conjectures", "Several open problems in group algebras and ring theory.")
    m("ring_theory", "Kothe conjecture", "Rings with no nil two-sided ideals have no nil one-sided ideals.")
    m("commutative_algebra", "Monomial conjecture", "Concerns tight closure in Noetherian local rings.")
    m("geometric_algebra", "Perfect cuboid conjectures", "Does a perfect cuboid with all integer edges, face diagonals, and space diagonal exist?")
    m("real_algebra", "Pierce-Birkhoff conjecture", "Piecewise-polynomial functions equal maxima of minima of polynomials.")
    m("matroid_theory", "Rota's basis conjecture", "n disjoint matroid bases can form matrix rows and columns that are also bases.")
    m("galois_cohomology", "Serre's conjecture II", "Galois cohomology vanishes for semisimple groups over certain fields.")
    m("commutative_algebra", "Serre's positivity conjecture", "Intersection multiplicities are positive under dimension conditions.")
    m("diophantine_geometry", "Uniform boundedness conjecture for rational points", "Bounded count of rational points on genus >= 2 curves over number fields.")
    m("representation_theory", "Wild problems", "Classification of matrix pairs under simultaneous conjugation.")
    m("algebraic_geometry", "Zariski-Lipman conjecture", "Free derivation modules imply smooth varieties.")
    m("quantum_information", "Zauner's conjecture", "SIC-POVMs exist in all finite dimensions.")

    # Group Theory
    m("combinatorial_group_theory", "Andrews-Curtis conjecture", "Balanced trivial presentations reach trivial form via Nielsen transformations.")
    m("group_theory", "Bounded Burnside problem", "Determine which free Burnside groups B(m,n) are finite.")
    m("galois_theory", "Inverse Galois problem", "Every finite group appears as Galois group of an extension of the rationals.")
    m("group_theory", "Isomorphism problem of Coxeter groups", "Determining when Coxeter groups are isomorphic.")
    m("group_theory", "Sofic groups", "Is every discrete countable group sofic?")
    m("group_theory", "Surjunctive groups", "Every group satisfies the surjunctivity property for cellular automata.")

    # Representation Theory
    m("automorphic_forms", "Arthur's conjectures", "Relating automorphic representations and Langlands parameters.")
    m("modular_representation_theory", "Dade's conjecture", "Character block counts relate to local subgroup block counts.")
    m("character_theory", "McKay conjecture", "p-part character counts match between group and p-Sylow normalizer.")

    # Analysis
    m("complex_analysis", "Brennan conjecture", "Integral powers of conformal derivative moduli satisfy bounds.")
    m("harmonic_analysis", "Fuglede's conjecture", "Nonconvex sets are spectral iff they tile by translation.")
    m("functional_analysis", "Invariant subspace problem", "Every bounded operator on complex Banach space has an invariant subspace.")
    m("algebraic_number_theory", "Lehmer's conjecture", "Non-cyclotomic polynomials have Mahler measure bounded away from 1.")
    m("complex_analysis", "Sendov's conjecture", "Roots in unit disk have critical points within distance 1.")
    m("fluid_dynamics", "Euler equations regularity", "Do smooth solutions exist for all time for incompressible Euler equations?")
    m("analysis", "Flint Hills series convergence", "Does the sum of 1/(n^3 sin^2 n) converge?")

    # Combinatorics
    m("order_theory", "1/3-2/3 conjecture", "Every finite partially ordered set that is not totally ordered has a pair with comparison probability between 1/3 and 2/3.")
    m("discrete_geometry", "Lonely runner conjecture", "Runners at distinct speeds on circular track achieve mutual distance >= 1/(k+1).")
    m("combinatorial_geometry", "No-three-in-line problem", "Maximum collinear-avoiding points in n x n grid.")
    m("set_theory", "Sunflower conjecture", "k-uniform sunflowers require bounded collection sizes.")
    m("combinatorial_set_theory", "Union-closed sets conjecture", "Union-closed families contain an element in at least half the sets.")
    m("ramsey_theory", "Ramsey numbers", "Determining specific Ramsey numbers like R(5,5).")

    # Dynamical Systems
    m("dynamical_systems", "Birkhoff conjecture", "Integrable convex billiards have elliptical boundaries.")
    m("dynamical_systems", "Collatz conjecture", "The 3n+1 sequence reaches 1 from any positive integer.")
    m("complex_dynamics", "MLC conjecture", "The Mandelbrot set is locally connected.")
    m("dynamical_systems", "Triangular billiards", "Every triangle contains a periodic billiard path.")
    m("ergodic_theory", "Furstenberg conjecture", "x2, x3 action invariant measures on the circle are Lebesgue or atomic.")

    # Number Theory
    m("number_theory", "Goldbach's conjecture", "Every even integer greater than 2 is the sum of two primes.", importance="landau")
    m("number_theory", "Twin prime conjecture", "There are infinitely many pairs of primes differing by 2.", importance="landau")
    m("number_theory", "Legendre's conjecture", "There is a prime between n^2 and (n+1)^2 for every positive integer n.", importance="landau")
    m("analytic_number_theory", "Riemann hypothesis", "All non-trivial zeros of the Riemann zeta function have real part 1/2.", importance="millennium", year_posed=1859, posed_by="Bernhard Riemann")
    m("analytic_number_theory", "Lindelof hypothesis", "Growth bounds on the Riemann zeta function on the critical line.")
    m("analytic_number_theory", "Pair correlation conjecture", "Spacings of zeta zeros follow GUE random matrix distribution.")
    m("arithmetic_geometry", "Birch and Swinnerton-Dyer conjecture", "Rank of an elliptic curve equals the order of vanishing of its L-function at s=1.", importance="millennium")
    m("algebraic_geometry", "Hodge conjecture", "Every Hodge class on a projective complex manifold is a rational combination of algebraic cycle classes.", importance="millennium")
    m("number_theory", "Cramér conjecture", "Prime gaps are O((log p)^2).")
    m("number_theory", "Polignac's conjecture", "For every even number 2k, there are infinitely many prime gaps of size 2k.")
    m("algebraic_number_theory", "Artin's conjecture on primitive roots", "Every non-square integer is a primitive root modulo infinitely many primes.")

    # Algebraic Geometry
    m("algebraic_geometry", "Abundance conjecture", "Nef canonical bundles on log terminal varieties are semiample.")
    m("algebraic_geometry", "Jacobian conjecture", "Polynomial maps with constant nonzero Jacobian have polynomial inverses.")
    m("algebraic_geometry", "Standard conjectures on algebraic cycles", "Relations between algebraic cycles and Hodge cohomology.")
    m("algebraic_geometry", "Tate conjecture", "Algebraic cycles and Galois representations relate via étale cohomology.")
    m("algebraic_geometry", "Section conjecture", "Fundamental group splitting for curves over finitely-generated fields.")
    m("algebraic_geometry", "Nagata's conjecture on curves", "Minimal degree for plane curves through prescribed points.")

    # Topology
    m("topology", "Smooth 4D Poincaré conjecture", "Is every homotopy 4-sphere diffeomorphic to the standard 4-sphere?")
    m("algebraic_topology", "Novikov conjecture", "Higher signatures are homotopy invariants.")
    m("algebraic_topology", "Whitehead conjecture", "Every subcomplex of an aspherical 2-complex is aspherical.")

    # Geometry
    m("discrete_geometry", "Borsuk's problem", "Can every bounded set in R^n be partitioned into n+1 subsets of smaller diameter?")
    m("discrete_geometry", "Kissing number problem", "Exact kissing numbers in dimensions other than 1,2,3,4,8,24.")
    m("discrete_geometry", "Sphere packing", "Densest packing density in dimensions other than 1,2,3,8,24.")
    m("geometry", "Moving sofa problem", "What is the largest shape that can navigate an L-shaped corridor?")
    m("harmonic_analysis", "Kakeya conjecture", "Besicovitch sets in R^n have Hausdorff dimension n.")
    m("topology", "Inscribed square problem", "Does every Jordan curve contain four points forming a square?")
    m("differential_geometry", "Carathéodory conjecture", "Every convex surface has at least 2 umbilical points.")
    m("differential_geometry", "Hopf conjectures", "Positive sectional curvature and Euler characteristic of even-dimensional manifolds.")

    # Games
    m("game_theory", "Chess outcome", "What is the result of perfect play in chess?")

    # Set Theory
    m("set_theory", "Continuum hypothesis", "Is there a cardinality strictly between the integers and the reals?", year_posed=1878, posed_by="Georg Cantor")

    # Navier-Stokes (also physics but stated as math millennium problem)
    m("partial_differential_equations", "Navier-Stokes existence and smoothness", "Do smooth solutions always exist for the 3D Navier-Stokes equations?", importance="millennium")

    # Yang-Mills (math millennium)
    m("quantum_field_theory", "Yang-Mills existence and mass gap", "Does non-trivial quantum Yang-Mills theory with finite mass gap exist in 4D?", importance="millennium")

    # P vs NP (math millennium)
    m("computational_complexity", "P vs NP", "Does every problem whose solution can be verified in polynomial time also have a polynomial-time solution?", importance="millennium")

    return qs


# ── PHYSICS ──────────────────────────────────────────────────────────────
def physics_questions():
    W = WIKI + "physics"
    D, C = "physics", "PHYS"
    qs = []
    def p(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    p("theoretical_physics", "Theory of Everything", "Can all physical aspects of the universe be explained by a single coherent theoretical framework?")
    p("theoretical_physics", "Dimensionless physical constants", "What is the minimum number of dimensionless constants from which all others derive?")
    p("quantum_gravity", "Quantum gravity", "How can quantum mechanics and general relativity be reconciled into a consistent theory?")
    p("quantum_gravity", "Black hole information paradox", "Does black hole radiation contain information about the black hole's interior?")
    p("quantum_gravity", "Cosmic censorship hypothesis", "Can naked singularities arise from realistic initial conditions?")
    p("quantum_gravity", "Holographic principle", "Does quantum gravity admit a lower-dimensional description without gravity?")
    p("quantum_gravity", "Problem of time", "How is time reconciled between quantum mechanics and general relativity?")
    p("cosmology", "Cosmic inflation", "Is cosmic inflation correct and what is the inflaton field?")
    p("cosmology", "Horizon problem", "Why is the universe so homogeneous when the Big Bang predicts larger anisotropies?")
    p("cosmology", "Origin and future of the universe", "How did conditions for existence arise and how will the universe end?")
    p("cosmology", "Matter-antimatter asymmetry", "What mechanism produced the baryon asymmetry after the Big Bang?")
    p("cosmology", "Cosmological constant problem", "Why doesn't vacuum zero-point energy produce a large cosmological constant?")
    p("cosmology", "Dark matter identity", "What is dark matter composed of?")
    p("cosmology", "Dark energy", "What causes the accelerating expansion of the universe?")
    p("cosmology", "Shape of the universe", "What is the 3-manifold topology and curvature of comoving space?")
    p("particle_physics", "Hierarchy problem", "Why is gravity approximately 10^38 times weaker than the strong force?")
    p("particle_physics", "Magnetic monopoles", "Do particles carrying magnetic charge exist?")
    p("particle_physics", "Proton decay", "Is the proton stable or does it eventually decay?")
    p("particle_physics", "Grand unification", "Do the electromagnetic and nuclear forces unify at high energies?")
    p("particle_physics", "Supersymmetry", "Does spacetime supersymmetry occur at the TeV scale?")
    p("particle_physics", "Color confinement", "Can an analytic proof show that quarks are permanently confined in hadrons?")
    p("particle_physics", "Generations of matter", "Why do three generations of quarks and leptons exist?")
    p("particle_physics", "Neutrino mass", "What is the absolute neutrino mass scale and the mass hierarchy?")
    p("particle_physics", "Strong CP problem", "Why does the strong interaction conserve CP symmetry?")
    p("particle_physics", "Muon g-2 anomaly", "Why does the measured muon anomalous magnetic moment differ from prediction?")
    p("solar_physics", "Solar cycle", "How does the Sun generate its periodically reversing magnetic field?")
    p("solar_physics", "Coronal heating problem", "Why is the Sun's corona much hotter than its surface?")
    p("astrophysics", "Astrophysical jets", "Why do certain accretion discs emit relativistic jets along polar axes?")
    p("astrophysics", "Supermassive black holes", "What explains the M-sigma relation and early growth of distant quasar black holes?")
    p("astrophysics", "Supernovae mechanism", "What mechanism converts a stellar implosion into an explosion?")
    p("astrophysics", "Ultra-high-energy cosmic rays", "How do cosmic rays exceed the GZK energy limit?")
    p("astrophysics", "Fast radio bursts", "What causes transient radio pulses from distant galaxies?")
    p("fluid_dynamics", "Navier-Stokes existence and smoothness", "Do smooth solutions always exist for the Navier-Stokes equations?", importance="millennium")
    p("fluid_dynamics", "Turbulence", "Can a theoretical model describe turbulent flow internal structures?")
    p("condensed_matter", "High-temperature superconductivity", "What mechanism enables superconductivity at elevated temperatures?")
    p("condensed_matter", "Glass transition", "What physical processes underlie the glass transition?")
    p("condensed_matter", "Sonoluminescence", "What causes light emission from imploding sound-excited bubbles?")
    p("condensed_matter", "Fractional quantum Hall effect at 5/2", "What mechanism explains the nu = 5/2 fractional quantum Hall state?")
    p("quantum_computing", "Fault-tolerant quantum computing", "Can scalable fault-tolerant quantum computing be achieved?")
    p("quantum_computing", "BQP vs NP", "What is the relationship between quantum and classical complexity classes?")
    p("plasma_physics", "Fusion confinement", "Can plasma be confined long enough at sufficient temperature for net fusion power?")
    p("plasma_physics", "Ball lightning", "What is the exact physical nature of ball lightning?")
    p("quantum_foundations", "Interpretation of quantum mechanics", "How does quantum superposition and wavefunction collapse yield observed reality?")
    p("thermodynamics", "Arrow of time", "Why does entropy increase define a direction of time?")
    p("biophysics", "Abiogenesis", "Can life emerge from purely physical processes?")
    p("biophysics", "Homochirality origin", "Why do biological systems use only left-handed amino acids and right-handed sugars?")
    p("quantum_biology", "Quantum biology", "Do quantum coherence effects play functional roles in biological systems?")

    return qs


# ── COMPUTER SCIENCE ─────────────────────────────────────────────────────
def cs_questions():
    W = WIKI + "computer_science"
    D, C = "computer_science", "CS"
    qs = []
    def c(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    c("computational_complexity", "P versus NP", "Can every problem whose solution is quickly verifiable also be quickly solved?", importance="millennium")
    c("computational_complexity", "BQP vs NP", "What is the relationship between quantum and classical complexity classes?")
    c("computational_complexity", "NC = P", "Do problems solvable in parallel polylogarithmic time equal those in polynomial time?")
    c("computational_complexity", "NP = co-NP", "Does the complement of NP equal NP?")
    c("computational_complexity", "P = BPP", "Does deterministic polynomial time equal probabilistic polynomial time?")
    c("computational_complexity", "P = PSPACE", "Does polynomial time equal polynomial space?")
    c("computational_complexity", "L = NL", "Does logarithmic space equal nondeterministic logarithmic space?")
    c("computational_complexity", "L = RL", "Does logarithmic space equal randomized logarithmic space?")
    c("computational_complexity", "Unique Games Conjecture", "Are the optimal approximation bounds for certain CSPs achieved by known algorithms?")
    c("computational_complexity", "Exponential Time Hypothesis", "Does 3-SAT require exponential time in the worst case?")
    c("cryptography", "One-way functions existence", "Do functions exist that are easy to compute but hard to invert?")
    c("cryptography", "Integer factorization in P", "Can integer factorization be done in polynomial time on a classical computer?")
    c("cryptography", "Discrete logarithm in P", "Can the discrete logarithm be computed in polynomial time classically?")
    c("lattice_cryptography", "Shortest vector problem", "Can the shortest lattice vector be found in polynomial time?")
    c("graph_algorithms", "Graph isomorphism", "Is graph isomorphism in P or is it NP-intermediate?")
    c("game_theory", "Parity games", "Can parity games be solved in polynomial time?")
    c("data_structures", "Dynamic optimality conjecture", "Do splay trees have bounded competitive ratio?")
    c("signal_processing", "FFT lower bound", "Can the FFT be computed in o(n log n) time?")
    c("arithmetic_algorithms", "Fastest multiplication", "What is the fastest algorithm for multiplying two n-digit numbers?")
    c("linear_algebra_algorithms", "Matrix multiplication exponent", "What is the true exponent omega of matrix multiplication?")
    c("optimization", "Strongly polynomial linear programming", "Does linear programming admit a strongly polynomial time algorithm?")
    c("graph_algorithms", "All-pairs shortest paths", "Can APSP be solved in strongly sub-cubic time?")
    c("string_algorithms", "Edit distance", "Can edit distance be computed in strongly sub-quadratic time?")
    c("computational_geometry", "3SUM conjecture", "Can 3SUM be solved in O(n^{2-epsilon}) time?")
    c("type_theory", "Barendregt-Geuvers-Klop conjecture", "Is every weakly normalizing pure type system also strongly normalizing?")
    c("automata_theory", "Cerny conjecture", "Does every synchronizable n-state DFA have a synchronizing word of length at most (n-1)^2?")
    c("algorithmic_number_theory", "Skolem problem", "Is it decidable whether a linear recurrence sequence has a zero?")
    c("algorithmic_number_theory", "Hilbert's tenth problem over Q", "Is the solvability of Diophantine equations over the rationals decidable?")
    c("fair_division", "Envy-free cake-cutting complexity", "How many queries are needed for envy-free cake-cutting?")

    return qs


# ── BIOLOGY ──────────────────────────────────────────────────────────────
def biology_questions():
    W = WIKI + "biology"
    D, C = "biology", "BIO"
    qs = []
    def b(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    b("origins_of_life", "Origin of life", "How, where, and when did life on Earth originate?")
    b("evolution", "Origin of sexual reproduction", "What selective forces drove the emergence of sexual reproduction?")
    b("virology", "Origins of viruses", "How and when did different viral groups originate?")
    b("evolution", "Origin of eukaryotes", "Did eukaryotic cells form through random endosymbiotic events or deterministic principles?")
    b("evolution", "Last universal common ancestor", "What were the characteristics of LUCA shared by Archaea and Bacteria?")
    b("biochemistry", "Biological homochirality", "Why are biological amino acids left-handed and sugars right-handed?")
    b("cell_biology", "Unknown protein functions", "What are the roles of the ~20% of proteins with unknown function?")
    b("cell_biology", "Cell size determinants", "How do cells determine appropriate growth size before division?")
    b("cell_biology", "Golgi apparatus transport", "What is the exact mechanism by which proteins move through the Golgi?")
    b("biochemistry", "Protein folding", "Can protein 3D structure be predicted from amino acid sequence alone?")
    b("biochemistry", "Enzyme kinetics anomalies", "Why do some enzymes exhibit faster-than-diffusion kinetics?")
    b("biochemistry", "RNA folding", "Can RNA 3D structure be predicted from sequence?")
    b("biochemistry", "De novo enzyme design", "Can highly active enzymes be designed from scratch for any reaction?")
    b("aging", "Biological aging", "Is senescence programmed by gene expression or caused by accumulative damage?")
    b("developmental_biology", "Organ growth and size", "How do organs reliably form to correct shapes and sizes?")
    b("human_biology", "Handedness", "How does handedness develop and why does left-handedness persist?")
    b("human_biology", "Laughter", "What are the exact neural processes producing laughter?")
    b("human_biology", "Yawning function", "What is the biological or social purpose of yawning?")
    b("neuroscience", "Sleep function", "What are the biological functions of sleep?")
    b("neuroscience", "Consciousness", "What is the neural basis of subjective experience?")
    b("neuroscience", "Free will", "Do organisms possess free will?")
    b("neuroscience", "Memory storage", "Where and how are memories stored and retrieved?")
    b("paleontology", "Cambrian explosion", "What caused the rapid diversification of animal life at the start of the Cambrian?")
    b("botany", "Darwin's abominable mystery", "What is the evolutionary origin of flowering plants?")
    b("ecology", "Paradox of the plankton", "Why does phytoplankton diversity violate the competitive exclusion principle?")
    b("ecology", "Ecosystem organization", "Do ecosystems function as superorganisms or collections of individuals?")
    b("ethology", "Butterfly migration navigation", "How do monarch butterfly descendants return to specific overwintering locations?")
    b("ethology", "Homing mechanisms", "What neurobiological mechanism explains animal homing abilities?")

    return qs


# ── NEUROSCIENCE ─────────────────────────────────────────────────────────
def neuro_questions():
    W = WIKI + "neuroscience"
    D, C = "neuroscience", "NEURO"
    qs = []
    def n(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    n("consciousness", "Hard problem of consciousness", "Why do physical processes give rise to subjective experience?")
    n("consciousness", "Binding problem", "How are objects and features combined into unified conscious experience?")
    n("consciousness", "Neural basis of self", "What constitutes the neural basis of self?")
    n("consciousness", "Function of consciousness", "What function does consciousness serve, if any?")
    n("consciousness", "Animal consciousness", "Which animals or lifeforms have conscious experience?")
    n("consciousness", "Quantum mind hypothesis", "Do quantum effects play a role in brain function?")
    n("perception", "Sensory integration", "How does the brain convert sensory input into coherent private experience?")
    n("perception", "Sense integration", "How are the different senses integrated?")
    n("memory", "Memory storage and retrieval", "Where are memories stored and how are they retrieved?")
    n("memory", "Synaptic tagging molecule", "What molecule is responsible for synaptic tagging?")
    n("memory", "Brain plasticity", "How plastic is the mature brain?")
    n("language", "Neural implementation of language", "How is language implemented neurally in the brain?")
    n("language", "Semantic meaning basis", "What is the neural basis of semantic meaning?")
    n("language", "Language acquisition", "How are infants able to acquire language?")
    n("language", "Linguistic relativity", "How do grammatical patterns affect cognitive habits?")
    n("computational_neuroscience", "Neural code", "What is the neural code?")
    n("computational_neuroscience", "Canonical cortical computation", "Is there a canonical computation performed by cortical columns?")
    n("computational_neuroscience", "Action potential timing", "How important is precise spike timing for neocortical processing?")
    n("sleep", "Biological function of sleep", "What is the biological function of sleep?")
    n("sleep", "Purpose of dreams", "Why do humans dream?")
    n("free_will", "Free will neuroscience", "What is the neural basis of free will?")
    n("anesthesia", "General anesthetic mechanisms", "How do general anesthetics produce unconsciousness?")
    n("intelligence", "Emergence of intelligence", "What laws govern the emergence and evolution of intelligence?")

    return qs


# ── CHEMISTRY ────────────────────────────────────────────────────────────
def chem_questions():
    W = WIKI + "chemistry"
    D, C = "chemistry", "CHEM"
    qs = []
    def ch(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    ch("physical_chemistry", "Room-temperature superconductivity", "Can high-temperature superconductors reach room-temperature transition?")
    ch("physical_chemistry", "Trans-actinide chemistry", "How do relativistic and spin-orbit effects modify trans-actinide chemical behavior?")
    ch("physical_chemistry", "Lithium-air battery", "Is a practically useful lithium-air battery achievable?")
    ch("organic_chemistry", "Biomolecular homochirality origin", "What is the origin of homochirality in biomolecules?")
    ch("organic_chemistry", "Water-organic interface kinetics", "Why do certain organic reactions accelerate at water-organic interfaces?")
    ch("organic_chemistry", "Quaternary carbon stereochemistry", "Can quaternary carbons with arbitrary substituents and stereochemistry be constructed?")
    ch("inorganic_chemistry", "Phi bond existence", "Are there molecules that certainly contain a phi bond?")
    ch("inorganic_chemistry", "Nitrogen metastable allotropes", "Does nitrogen admit metastable allotropes under standard conditions?")
    ch("inorganic_chemistry", "Artificial photosynthesis", "Can artificial photosynthesis produce common fuels?")
    ch("inorganic_chemistry", "Direct carbon capture economics", "Can new techniques make direct carbon capture economical?")
    ch("biochemistry", "Faster-than-diffusion enzyme kinetics", "Why do some enzymes exhibit faster-than-diffusion kinetics?")
    ch("biochemistry", "Protein folding prediction", "Can protein structure be predicted from sequence and environment alone?")
    ch("biochemistry", "De novo enzyme design", "Is it possible to design highly active enzymes de novo for any reaction?")
    ch("biochemistry", "RNA folding prediction", "Can RNA tertiary structure be accurately predicted from sequence?")

    return qs


# ── ASTRONOMY ────────────────────────────────────────────────────────────
def astro_questions():
    W = WIKI + "astronomy"
    D, C = "astronomy", "ASTRO"
    qs = []
    def a(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    a("solar_system", "Planets beyond Neptune", "Are there any non-dwarf planets beyond Neptune?")
    a("solar_system", "Extreme TNO orbits", "Why do extreme trans-Neptunian objects have elongated orbits?")
    a("solar_system", "Saturn's rotation rate", "What is the rotation rate of Saturn's deep interior?")
    a("exoplanets", "Solar System-like systems", "How common are planetary systems resembling our Solar System?")
    a("solar_physics", "Solar magnetic field generation", "How does the Sun generate its periodically reversing magnetic field?")
    a("solar_physics", "Maunder minimum", "What caused the Maunder Minimum and other grand minima?")
    a("solar_physics", "Coronal heating", "Why is the Sun's corona so much hotter than its surface?")
    a("stellar_formation", "Initial mass function", "Why is the stellar mass distribution apparently universal?")
    a("stellar_explosions", "Supernova mechanism", "How does a stellar implosion become an explosion?")
    a("nucleosynthesis", "P-nuclei nucleogenesis", "What astrophysical process creates these rare isotopes?")
    a("transients", "Fast radio bursts", "What causes transient radio pulses from distant galaxies?")
    a("cosmic_rays", "Ultra-high-energy cosmic rays", "How do cosmic rays exceed the GZK energy limit?")
    a("galactic_dynamics", "Galaxy rotation problem", "Does dark matter alone explain galactic rotation curves?")
    a("high_energy_astrophysics", "Ultraluminous X-ray sources", "What powers X-ray sources exceeding the Eddington limit?")
    a("black_holes", "Black hole information paradox", "What happens to information in evaporating black holes?")
    a("black_holes", "M-sigma relation", "What causes the correlation between black hole mass and stellar velocity dispersion?")
    a("black_holes", "Final parsec problem", "Why can't supermassive black holes merge within a Hubble time?")
    a("cosmology", "Hubble tension", "Why do different methods for measuring H0 give discrepant results?")
    a("cosmology", "Dark matter identity", "What is the composition of dark matter?")
    a("cosmology", "Dark energy cause", "What causes the accelerating expansion of the universe?")
    a("cosmology", "Baryon asymmetry", "Why is there far more matter than antimatter?")
    a("cosmology", "Universe shape", "What is the topology and curvature of comoving space?")
    a("cosmology", "Cosmic inflation", "Is cosmic inflation correct?")
    a("cosmology", "Ultimate fate of universe", "Will the universe end in Big Freeze, Rip, Crunch, or Bounce?")
    a("astrobiology", "Fermi paradox", "Why haven't we detected extraterrestrial intelligence?")
    a("astrobiology", "Extraterrestrial life", "Is there other life in the universe?")

    return qs


# ── ECONOMICS ────────────────────────────────────────────────────────────
def econ_questions():
    W = WIKI + "economics"
    D, C = "economics", "ECON"
    qs = []
    def e(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    e("capital_theory", "Cambridge capital controversy", "Is the natural growth rate exogenous or endogenous to demand?")
    e("marxist_economics", "Transformation problem", "Can commodity labor values be generally converted to competitive prices?")
    e("behavioral_economics", "Revealed preference validity", "Does revealed preference theory accurately reflect consumer choice?")
    e("behavioral_economics", "Unified model of cognitive biases", "Can a unified model incorporating all known cognitive biases make useful predictions?")
    e("financial_economics", "Equity premium puzzle", "Why do stock returns substantially exceed bond returns over long periods?")
    e("financial_economics", "Dividend puzzle", "Why do dividend-paying companies receive higher valuations?")
    e("international_economics", "Home bias in trade", "Why does intra-country trade substantially exceed inter-country trade?")
    e("international_economics", "Equity home bias puzzle", "Why do investors hold so little foreign equity despite diversification benefits?")
    e("international_economics", "Feldstein-Horioka puzzle", "Why do national savings correlate highly with domestic investment despite open markets?")
    e("international_economics", "PPP puzzle", "Why are real exchange rates more volatile and persistent than models predict?")
    e("international_economics", "Exchange rate disconnect", "Why are exchange rate-macroeconomic variable links so weak in the short term?")

    return qs


# ── GEOSCIENCE ───────────────────────────────────────────────────────────
def geo_questions():
    W = WIKI + "geoscience"
    D, C = "geoscience", "GEO"
    qs = []
    def g(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    g("planetary_formation", "Giant impact hypothesis", "Did a collision with Theia give birth to the Moon?")
    g("geothermics", "Earth's long-term heat balance", "How has Earth's internal temperature decayed since formation?")
    g("geomorphology", "Landscape evolution from topography", "Can topographic data reveal past tectonic and climatic conditions?")
    g("erosion", "Mountain range longevity", "What controls how long ancient mountain ranges retain topographic relief?")
    g("fluvial_geomorphology", "Erosion and transport laws", "What physical laws govern sediment transport and landscape evolution?")
    g("oceanography", "Ocean chemical resilience", "How resilient is the ocean to chemical perturbations?")
    g("meteorology", "Storm track dynamics", "What controls the dynamics of storm tracks?")
    g("meteorology", "Tropical cyclone frequency", "Why do we observe the specific number of tropical cyclones that we do?")
    g("climatology", "ENSO and QBO nature", "Are ENSO and QBO stochastic, chaotic, or deterministically forced?")
    g("atmospheric_phenomena", "Skyquakes", "What causes skyquakes?")
    g("igneous_petrology", "Granite magma emplacement", "How are granite magma chambers emplaced in the crust?")
    g("volcanology", "Supervolcano structure", "What are the structures and magmatic properties of supervolcano systems?")
    g("seismology", "Mantle non-uniformities", "What are the rheological details of the mantle and 660 km discontinuity?")
    g("geochemistry", "Gutenberg discontinuity chemistry", "What is the precise chemical heterogeneity at the core-mantle boundary?")
    g("core_dynamics", "Core heterogeneities", "What are the heterogeneities of Earth's core and their dynamical significance?")
    g("planetary_dynamics", "Chandler wobble driver", "What mechanism drives Earth's Chandler wobble?")

    return qs


# ── PHILOSOPHY ───────────────────────────────────────────────────────────
def phil_questions():
    W = WIKI + "philosophy"
    D, C = "philosophy", "PHIL"
    qs = []
    def ph(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    ph("epistemology", "Gettier problem", "Is justified true belief sufficient for knowledge?")
    ph("epistemology", "Problem of induction", "Can inductive reasoning be rationally justified?")
    ph("epistemology", "Münchhausen trilemma", "Can any truth be proven without circular, regressive, or dogmatic arguments?")
    ph("epistemology", "Problem of the criterion", "How can justification be determined without infinite regress?")
    ph("metaphysics", "Why there is something rather than nothing", "What explains the existence of anything at all?")
    ph("metaphysics", "Problem of universals", "Do properties exist in reality or only in thought and language?")
    ph("metaphysics", "Sorites paradox", "At what point does removing elements change what something is?")
    ph("metaphysics", "Theseus paradox", "When all parts are replaced, is it still the same object?")
    ph("philosophy_of_mind", "Mind-body problem", "How do the physical body and non-physical mind interact?")
    ph("philosophy_of_mind", "Qualia", "Are subjective experiences mind-dependent or objective properties?")
    ph("philosophy_of_mind", "Hard problem of consciousness", "Why do we have subjective experience?")
    ph("philosophy_of_mind", "Cognition and AI", "Can artificial systems possess genuine understanding and consciousness?")
    ph("philosophy_of_mind", "Personal identity", "What makes a person at one time identical to a person at another?")
    ph("philosophy_of_mathematics", "Nature of mathematical objects", "Are numbers and sets real entities or formal constructions?")
    ph("philosophy_of_science", "Demarcation problem", "What distinguishes science from non-science?")
    ph("philosophy_of_science", "Scientific realism", "Does a mind-independent world exist and remain empirically accessible?")
    ph("philosophy_of_religion", "Existence of God", "Can philosophical arguments demonstrate that God exists?")
    ph("ethics", "Moral luck", "How does moral responsibility change based on uncontrolled circumstances?")
    ph("ethics", "Moral knowledge", "Are moral facts possible and how do we know them?")

    return qs


# ── STATISTICS ───────────────────────────────────────────────────────────
def stats_questions():
    W = WIKI + "statistics"
    D, C = "statistics", "STAT"
    qs = []
    def s(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    s("error_analysis", "Systematic error detection", "How to detect and correct systematic errors when random errors are large?")
    s("estimation_theory", "Graybill-Deal estimator admissibility", "Is the Graybill-Deal estimator admissible for common means of normal populations with unequal variances?")
    s("meta_analysis", "Dependent p-values in meta-analysis", "How to handle dependent p-values in meta-analysis?")
    s("hypothesis_testing", "Behrens-Fisher problem", "Is there a uniformly most powerful test for the difference of two means with unknown unequal variances?")
    s("multiple_testing", "Multiple comparisons", "How to simultaneously control error rates and preserve power in multiple testing?")
    s("design_of_experiments", "Latin square problems", "How to resolve open problems in Latin squares for experimental design?")
    s("philosophical_probability", "Doomsday argument", "Is the probabilistic argument predicting human race lifetime valid?")

    return qs


# ── INFORMATION THEORY ───────────────────────────────────────────────────
def infoth_questions():
    W = WIKI + "information_theory"
    D, C = "information_theory", "INFO"
    qs = []
    def i(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    i("channel_coding", "Capacity of a general wireless network", "The capacity of a general wireless network is not known.")
    i("channel_coding", "Broadcast channel capacity", "The capacity of the broadcast channel is unknown in general.")
    i("channel_coding", "Interference channel capacity", "The capacity when two transmitter-receiver pairs interfere is unsolved.")
    i("channel_coding", "Two-way channel capacity", "The capacity of a bidirectional simultaneous channel is unknown.")
    i("channel_coding", "ALOHA capacity", "The capacity of the ALOHA random access scheme is still unknown.")
    i("channel_coding", "Quantum channel capacity", "The capacity of a quantum channel is in general not known.")
    i("source_coding", "Lossy distributed source coding", "The best compression of correlated sources with non-communicating encoders is not known.")

    return qs


# ── FAIR DIVISION ────────────────────────────────────────────────────────
def fairdiv_questions():
    W = WIKI + "fair_division"
    D, C = "fair_division", "FAIR"
    qs = []
    def f(sub, title, stmt, **kw):
        qs.append(q(D, C, sub, title, stmt, sources=[W], **kw))

    f("cake_cutting", "Envy-free cake-cutting query complexity", "How many queries are needed for envy-free cake divisions?")
    f("cake_cutting", "Truthful cake-cutting mechanism", "Does a deterministic truthful fair mechanism exist for multiple agents?")
    f("item_allocation", "Maximin-share fairness complexity", "What is the computational complexity of maximin-share allocation?")
    f("item_allocation", "EFX allocation existence", "For 3+ agents with additive valuations, does an EFX allocation always exist?")
    f("item_allocation", "Pareto-optimal EF1 allocation", "What is the complexity of finding both Pareto-optimal and EF1 allocations?")
    f("item_allocation", "Price of fairness for EF1", "What is the welfare loss ratio from imposing EF1 fairness?")

    return qs


# ── WRITE ALL ────────────────────────────────────────────────────────────
DOMAIN_GENERATORS = {
    "mathematics": math_questions,
    "physics": physics_questions,
    "computer_science": cs_questions,
    "biology": biology_questions,
    "neuroscience": neuro_questions,
    "chemistry": chem_questions,
    "astronomy": astro_questions,
    "economics": econ_questions,
    "geoscience": geo_questions,
    "philosophy": phil_questions,
    "statistics": stats_questions,
    "information_theory": infoth_questions,
    "fair_division": fairdiv_questions,
}

def main():
    total = 0
    for domain, gen in DOMAIN_GENERATORS.items():
        out_dir = ROOT / domain
        out_dir.mkdir(parents=True, exist_ok=True)
        qs = gen()
        out_path = out_dir / "questions.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for entry in qs:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"  {domain:25s} -> {len(qs):4d} questions -> {out_path}")
        total += len(qs)
    print(f"\n  TOTAL: {total} questions across {len(DOMAIN_GENERATORS)} domains")

if __name__ == "__main__":
    main()
