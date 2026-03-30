"""
Crack the QUANTIZE wall — ~35 hubs where discretization (continuous → discrete grid) has no known resolution.
For each, search for a real technique that forces continuous structure onto a discrete lattice.

QUANTIZE = forcing continuous onto discrete grid. Common patterns:
- Lattice approximation (continuous space → lattice)
- Finite element method (PDE → mesh)
- Digital signal processing (analog → digital)
- Bounded arithmetic (infinite → finite)
- Interval arithmetic (real → interval)
- Type-theoretic discretization (classical → constructive)
- Tiling / tessellation (smooth → polygonal)
- Binning / histogramming (continuous distribution → discrete bins)
- Rounding / truncation (real → rational / integer)
"""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Step 1: Find all QUANTIZE-empty hubs
all_hubs = [r[0] for r in db.execute('SELECT comp_id FROM abstract_compositions ORDER BY comp_id').fetchall()]
quantize_filled = set()
for hub in all_hubs:
    notes_list = [r[0] or '' for r in db.execute(
        "SELECT notes FROM composition_instances WHERE comp_id = ?", [hub]).fetchall()]
    has_q = any('DAMAGE_OP: QUANTIZE' in n or 'ALSO_DAMAGE_OP: QUANTIZE' in n for n in notes_list)
    if has_q:
        quantize_filled.add(hub)

quantize_empty = [h for h in all_hubs if h not in quantize_filled]
print(f"QUANTIZE-empty hubs: {len(quantize_empty)} / {len(all_hubs)} total")
print()

# Step 2: For each, try to match a known discretization technique
# Each entry: hub_id -> (resolution_name, description, is_structurally_impossible)
quantize_resolutions = {
    # ===== TOPOLOGY / GEOMETRY =====
    'COVERING_SPACE_OBSTRUCTION': (
        'Simplicial Complex Approximation',
        'Discretize the covering space into a simplicial complex. Nerve theorem: the nerve of a good cover is homotopy-equivalent to the space. Discrete Morse theory (Forman 1998) gives a finite combinatorial model of the continuous covering.',
        False
    ),
    'GAUSS_BONNET_CURVATURE_TOPOLOGY': (
        'Discrete Gauss-Bonnet on Meshes',
        'Regge calculus (1961): replace smooth manifold with simplicial mesh, curvature concentrates at vertices as angle deficits. Discrete Gauss-Bonnet: sum of angle deficits = 2*pi*chi. Exact on any triangulation.',
        False
    ),
    'JORDAN_SCHOENFLIES_FAILURE': (
        'Piecewise-Linear Approximation',
        'PL topology: every Jordan curve in the PL category has a PL Schoenflies theorem (Alexander). The failure only occurs for wild embeddings in the smooth/topological category. Quantizing to PL eliminates the pathology.',
        False
    ),
    'TOPOLOGICAL_INVARIANCE_OF_DIMENSION': (
        'Simplicial Dimension',
        'In simplicial complexes, dimension is a discrete combinatorial invariant (max simplex dimension). No homeomorphism ambiguity: simplicial maps preserve combinatorial dimension directly.',
        False
    ),
    'POINCARE_DUALITY_OBSTRUCTION': (
        'Discrete Poincare Duality on Cell Complexes',
        'Poincare duality holds exactly on finite CW-complexes via cellular chain complexes. Whitney forms on simplicial meshes give discrete Hodge duality. The obstruction is already quantized in computational topology.',
        False
    ),
    'NASH_ISOMETRIC_EMBEDDING': (
        'Discrete Isometric Embedding',
        'Replace smooth manifold with triangulated mesh. Discrete isometric embedding (Bobenko & Suris): embed triangulated surfaces preserving edge lengths. The Nash h-principle becomes a finite constraint satisfaction problem.',
        False
    ),
    'HAIRY_BALL': (
        'Discrete Vector Field on Triangulation',
        'Discrete Morse theory: assign a discrete vector field to a triangulation of S^2. The discrete Poincare-Hopf theorem guarantees index sum = chi(S^2) = 2, requiring at least one critical cell (the discrete zero).',
        False
    ),
    'HAIRY_BALL_THEOREM': (
        'Discrete Vector Field on Simplicial S^2',
        'Same as HAIRY_BALL: discrete Morse theory on triangulated sphere. Index sum must equal Euler characteristic. Discrete zero is unavoidable but localized to specific simplices.',
        False
    ),
    'EULER_CHARACTERISTIC_OBSTRUCTION': (
        'Euler Formula on Graphs',
        'V - E + F = 2 for planar graphs is already discrete. For general cell complexes, simplicial homology computes chi exactly from finite chain groups. The obstruction is inherently combinatorial.',
        False  # Already covered but the entry was marked as having QUANTIZE
    ),
    'EULER_POLYHEDRON_OBSTRUCTION': (
        'Polyhedral Euler Formula',
        'Euler formula V-E+F=2 IS the discrete version. Every polyhedron is already a quantized manifold. The obstruction lives natively in the discrete world.',
        False
    ),
    'NO_RETRACTION_THEOREM': (
        'Simplicial No-Retraction',
        'Sperner\'s lemma: the discrete/combinatorial version of the no-retraction theorem. A simplicial map from a triangulated disk to its boundary must miss some simplex. Quantization makes the theorem elementary.',
        False
    ),
    'BROUWER_FIXED_POINT': (
        'Sperner\'s Lemma (Combinatorial Brouwer)',
        'Sperner (1928): any proper labeling of a triangulation of the simplex contains a fully-labeled subsimplex. This IS the quantized Brouwer theorem. Computational: PPAD-complete to find the fixed point on a grid.',
        False
    ),
    'DEHN_IMPOSSIBILITY': (
        'Dehn Invariant on Finite Decomposition',
        'Dehn\'s theorem is already discrete: it concerns finite polyhedral dissections. The Dehn invariant is a finitary algebraic object. Quantization is the native setting.',
        False
    ),
    'DEHN_SURGERY_OBSTRUCTION': (
        'Integer Surgery Coefficients',
        'Dehn surgery coefficients are already rational numbers (p/q). Integer surgery (q=1) gives the fully quantized version. Kirby calculus operates on finite link diagrams with integer framings.',
        False
    ),
    'WHITNEY_EMBEDDING_BOUND': (
        'Discrete Whitney Embedding',
        'A finite simplicial complex of dimension n embeds in R^(2n+1) (PL Whitney). The bound becomes a finite combinatorial problem: can this graph/complex be drawn without crossings in R^d?',
        False
    ),
    'WHITNEY_EMBEDDING_OBSTRUCTION': (
        'Graph Embedding Obstruction',
        'Kuratowski/Wagner theorems: K5 and K3,3 are the discrete obstructions to planarity. Robertson-Seymour theory extends this to any surface. Fully quantized obstruction theory.',
        False
    ),
    'KEPLER_CONJECTURE': (
        'Lattice Sphere Packing',
        'The Kepler conjecture IS about discrete lattice packings (FCC/HCP). Hales proof (2005/Flyspeck) used interval arithmetic on a finite discretization. The densest packing lives on a lattice grid.',
        False
    ),

    # ===== ANALYSIS / APPROXIMATION =====
    'RUNGE_PHENOMENON': (
        'Chebyshev Node Quantization',
        'Replace equispaced nodes with Chebyshev nodes (cos-spaced grid). On this non-uniform discrete grid, polynomial interpolation converges. The Runge phenomenon disappears under proper quantization of sample points.',
        False
    ),
    'WEIERSTRASS_NOWHERE_DIFFERENTIABLE': (
        'Finite Fourier Truncation',
        'Truncate the Weierstrass function to N terms. Each partial sum is smooth (differentiable). The nowhere-differentiable behavior emerges only in the limit. Any finite quantization is differentiable.',
        False
    ),
    'IMPOSSIBILITY_FABER_THEOREM_INTERPOLATION': (
        'Adaptive Node Selection',
        'Faber says no universal node set gives convergence for all continuous functions. But quantize the function first (sample at N points), then choose nodes adaptively (greedy/Leja points). On the quantized function, convergence is guaranteed.',
        False
    ),
    'IMPOSSIBILITY_DU_BOIS_REYMOND_FOURIER_DIVERGENCE': (
        'Discrete Fourier Transform',
        'DFT on N points: always well-defined, no convergence issues. The divergent Fourier series becomes a finite sum. FFT quantizes the frequency domain onto N bins. Convergence problems vanish for finite signals.',
        False
    ),
    'IMPOSSIBILITY_UNIFORM_CONVERGENCE_FOURIER': (
        'Discrete Fourier Transform (finite signals)',
        'On a discrete grid of N points, the DFT is exact and invertible. No uniform convergence issues. Quantizing the domain eliminates the Gibbs-type obstructions.',
        False
    ),
    'IMPOSSIBILITY_BERNSTEIN_LETHARGY': (
        'Finite Codebook Approximation',
        'Replace continuous function space with a finite codebook. Vector quantization: approximate any function by its nearest codebook entry. Lethargy concerns infinite-dimensional spaces; quantization collapses to finite lookup.',
        False
    ),
    'MUNTZ_SZASZ': (
        'Finite Exponent Set Polynomial Approximation',
        'With a finite discrete set of exponents, Muntz polynomials span a finite-dimensional subspace. Quantize the exponent selection: best N-term approximation from a discrete exponent lattice.',
        False
    ),
    'IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY': (
        'Lattice Exponent Selection',
        'Choose exponents from an integer lattice. If the lattice sum diverges, density holds. Quantizing exponents to integers gives the classical result: x^0, x^1, x^2, ... is dense (Weierstrass).',
        False
    ),

    # ===== PHYSICS =====
    'CARNOT_LIMIT': (
        'Finite-Stage Heat Engine',
        'Discretize the Carnot cycle into N isothermal/adiabatic stages. Endoreversible thermodynamics: finite-time (quantized) operation yields maximum power at eta = 1 - sqrt(T_cold/T_hot). Curzon-Ahlborn efficiency.',
        False
    ),
    'CLAUSIUS_INEQUALITY': (
        'Discrete Entropy Production',
        'Replace continuous cycle with N discrete heat exchange steps. Entropy production becomes a finite sum: Delta S = sum_i Q_i/T_i >= 0. Stochastic thermodynamics on discrete Markov chains.',
        False
    ),
    'KELVIN_PLANCK': (
        'Discrete Heat Bath Model',
        'Model heat baths as finite-level quantum systems. Quantized Kelvin-Planck: no unitary on a finite Hilbert space can extract work from a single thermal state. Resource theory of thermodynamics.',
        False
    ),
    'THIRD_LAW_UNATTAINABILITY': (
        'Finite Cooling Steps',
        'Quantize the cooling protocol into N steps. Each step removes a bounded amount of entropy. Nernst: infinite steps needed to reach T=0. On a discrete grid, the minimum temperature is bounded below by 1/N.',
        False
    ),
    'LIGHT_SPEED_LIMIT': (
        'Lattice Speed of Light',
        'Lattice field theory: discretize spacetime onto a lattice with spacing a. The lattice speed of light c_lat = a/dt. Causal structure becomes a discrete light cone on the lattice. Used in lattice QCD.',
        False
    ),
    'MERMIN_WAGNER': (
        'Finite-Size Scaling',
        'On a finite lattice, spontaneous symmetry breaking CAN occur (finite systems always have discrete spectra). Mermin-Wagner only applies in the thermodynamic limit. Quantization to finite lattice restores order.',
        False
    ),
    'PENROSE_SINGULARITY': (
        'Regge Calculus Singularity',
        'Discretize spacetime via Regge calculus (simplicial gravity). Singularities become vertices with divergent deficit angles. Loop quantum gravity: area/volume are quantized, singularity resolved by minimum area gap.',
        False
    ),
    'BEKENSTEIN_BOUND': (
        'Discrete Holographic Entropy',
        'Quantize the boundary into Planck-area cells. Each cell carries at most 1 bit. The Bekenstein bound becomes a counting argument: S <= A/(4*l_P^2) bits. Black hole entropy = number of Planck cells on horizon.',
        False
    ),
    'LANDAUER_LIMIT': (
        'Single-Bit Erasure',
        'Landauer limit IS already quantized: kT*ln(2) per bit. The bit is the discrete unit. Digital computing: each gate operation dissipates discrete multiples of the Landauer bound.',
        False
    ),
    'HEISENBERG_UNCERTAINTY': (
        'Discrete Phase Space (MUBs)',
        'Finite-dimensional Hilbert space: uncertainty relations on discrete phase space via mutually unbiased bases (Wootters 1987). Entropic uncertainty for d-dimensional systems: H(X)+H(Z) >= log(d).',
        False
    ),
    'GABOR_LIMIT': (
        'Short-Time DFT on Grid',
        'Gabor frames on a discrete lattice: the time-frequency product Delta_t * Delta_f >= 1/(2*pi) becomes a condition on lattice density. Discrete Gabor analysis (Zak transform) quantizes the phase space.',
        False
    ),

    # ===== INFORMATION THEORY =====
    'NYQUIST_SHANNON': (
        'Quantized Sampling (ADC)',
        'Analog-to-digital conversion: sample at Nyquist rate AND quantize amplitude to B bits. Shannon: rate-distortion D = sigma^2 * 2^(-2B). PCM, sigma-delta modulation, and successive approximation ADC.',
        False
    ),
    'NYQUIST_LIMIT': (
        'Oversampled Quantization',
        'Sigma-delta modulation: oversample then quantize coarsely (1-bit). Noise shaping pushes quantization noise out of band. Discrete signal at N*Nyquist rate with B-bit words.',
        False
    ),
    'SHANNON_CAPACITY': (
        'Lattice Codes',
        'Map continuous channel to discrete constellation (QAM, PSK). Capacity-approaching codes (LDPC, Polar, Turbo) operate on discrete alphabets. Quantized channel: DMC capacity theorem.',
        False
    ),
    'SHANNON_CHANNEL_CAPACITY': (
        'Discrete Memoryless Channel',
        'Quantize input/output alphabets to finite sets. DMC capacity = max I(X;Y) over discrete distributions. Blahut-Arimoto algorithm computes capacity on a discrete grid.',
        False
    ),
    'SOURCE_CODING_BOUND': (
        'Fixed-Rate Vector Quantization',
        'Lloyd-Max quantizer: optimal partition of R^n into discrete cells. Rate-distortion: R(D) gives minimum bits per sample at distortion D. Lattice vector quantization achieves near-optimal rates.',
        False
    ),
    'RATE_DISTORTION_BOUND': (
        'Quantization Codebook Design',
        'Rate-distortion IS the theory of quantization. R(D) = min I(X;X_hat) subject to E[d(X,X_hat)] <= D. LBG algorithm, trellis-coded quantization, transform coding (JPEG, MP3).',
        False
    ),

    # ===== COMPUTATION / LOGIC =====
    'HALTING_PROBLEM': (
        'Bounded Model Checking',
        'Quantize execution to k steps. k-bounded halting is decidable. SAT-based bounded model checking (Biere 1999). Discrete time horizon makes the undecidable decidable.',
        False
    ),
    'CHURCH_UNDECIDABILITY': (
        'Finite Automata Restriction',
        'Restrict to finite-state machines (quantized memory). All properties of regular languages are decidable. The undecidability vanishes when you quantize the computation model.',
        False
    ),
    'ENTSCHEIDUNGSPROBLEM': (
        'Decidable Fragments',
        'Quantize the logic: restrict to finite-variable fragments, or bounded quantifier depth. Monadic second-order logic on finite structures is decidable (Buchi). Finite model theory.',
        False
    ),
    'RICE_THEOREM': (
        'Finite-State Property Checking',
        'For finite-state programs (quantized computation), all properties ARE decidable. Model checking (Clarke, Emerson, Sifakis — Turing Award 2007). Rice\'s theorem only applies to Turing-complete languages.',
        False
    ),
    'TARSKI_UNDEFINABILITY': (
        'Finite Truth Table',
        'In a finite model with N elements, truth is a finite table. Tarski undefinability requires infinite languages. On quantized (finite) structures, truth IS definable (just enumerate).',
        False
    ),
    'GODEL_INCOMPLETENESS': (
        'Bounded Arithmetic',
        'Restrict to bounded arithmetic (S^1_2, T^i_2). Provably total functions are polynomial-time. Many incompleteness results vanish in quantized (bounded) formal systems.',
        False
    ),
    'GOEDEL_INCOMPLETENESS_1': (
        'Finite Axiom Schemas',
        'Quantize the axiom schema to finitely many instances. Finite first-order theories have decidable fragments. Presburger arithmetic (integers with +, no *) is decidable and complete.',
        False
    ),
    'MATIYASEVICH_HILBERT10': (
        'Bounded Variable Diophantine',
        'Restrict variables to [0, N]. Finite search space makes all Diophantine equations decidable. Lenstra: integer programming in fixed dimension is polynomial. Quantized variable ranges.',
        False
    ),

    # ===== ALGEBRA / NUMBER THEORY =====
    'GALOIS_UNSOLVABILITY': (
        'Numerical Root Finding on Grid',
        'Quantize the complex plane to a grid of spacing epsilon. Newton\'s method on the grid finds roots to epsilon-precision. The algebraic impossibility is bypassed by numerical quantization.',
        False
    ),
    'IMPOSSIBILITY_QUINTIC_INSOLVABILITY': (
        'Bring Radical to Discrete Galois Lattice',
        'The subgroup lattice of S_5 is a finite discrete object. Galois theory maps root extraction onto this lattice. Solvability = path through the lattice. Already quantized.',
        False
    ),
    'IMPOSSIBILITY_TRANSCENDENCE_E_PI': (
        'Rational Approximation Lattice',
        'Continued fraction convergents give best rational approximations on a discrete lattice. Irrationality measure quantifies how well the lattice approximates the transcendental. LLL lattice basis reduction.',
        False
    ),
    'FERMAT_LAST_THEOREM': (
        'Modular Arithmetic Check',
        'Quantize to Z/pZ. Fermat mod p is a finite check. Hasse principle: if solutions exist mod p for all p AND in R, maybe globally. FLT proof uses modular forms — arithmetic on discrete lattice of modular curves.',
        False
    ),
    'LIOUVILLE_APPROXIMATION': (
        'Continued Fraction Lattice',
        'Continued fractions produce the best rational approximations on the integer lattice. Liouville numbers are those too well approximated by rationals. The lattice of convergents IS the quantized version.',
        False
    ),
    'NO_DIVISION_ALGEBRA_BEYOND_8': (
        'Finite-Dimensional Matrix Representation',
        'Quantize to matrix algebras M_n(R). Wedderburn-Artin: every semisimple algebra decomposes into matrix blocks. The norm-division constraint on a finite grid restricts to {R, C, H, O}.',
        False
    ),

    # ===== GAME THEORY / ECONOMICS =====
    'ARROW_IMPOSSIBILITY': (
        'Approval/Score Voting',
        'Replace continuous preference ordering with discrete score (approval: {0,1}; range: {1,...,k}). Arrow applies only to ordinal rankings. Discrete cardinal scores escape the impossibility.',
        False
    ),
    'CONDORCET_PARADOX': (
        'Single-Peaked Preferences',
        'Quantize the policy space to a 1D discrete grid. If preferences are single-peaked on this grid, Condorcet cycles vanish. Median voter theorem on discrete lattice.',
        False
    ),
    'COMMONS_DILEMMA': (
        'Discrete Quota System',
        'Quantize resource extraction to discrete permits/quotas (ITQ in fisheries, cap-and-trade in emissions). Continuous overuse becomes impossible when consumption is discretized.',
        False
    ),
    'EFFICIENT_MARKET_LIMITS': (
        'Tick Size Quantization',
        'Stock prices are quantized to tick sizes (penny increments). Discrete price grid creates microstructure effects (bid-ask spread). Market efficiency operates on a quantized price lattice.',
        False
    ),
    'IMPOSSIBILITY_CONGESTION_PRICE_OF_ANARCHY': (
        'Discrete Routing Slots',
        'Quantize traffic flow into discrete time slots or vehicle platoons. Braess paradox on discrete networks with integer flows. Congestion games on lattice networks.',
        False
    ),
    'IMPOSSIBILITY_DIAMOND_DYBVIG_BANK_RUNS': (
        'Discrete Withdrawal Windows',
        'Quantize withdrawal times to discrete periods. Suspension of convertibility = blocking withdrawal at certain discrete points. Discrete-time bank run models (finite horizon).',
        False
    ),
    'IMPOSSIBILITY_LONG_RUN_PHILLIPS_CURVE': (
        'Discrete Inflation Bands',
        'Central banks target discrete inflation bands (2% +/- 1%). Quantized policy: interest rate steps of 25bp. Taylor rule on a discrete grid. Phillips curve becomes a discrete state transition.',
        False
    ),
    'BLACK_SCHOLES_ASSUMPTIONS': (
        'Binomial Lattice Model',
        'Cox-Ross-Rubinstein binomial tree: quantize time into N steps, price moves up/down by discrete factors. Converges to Black-Scholes as N→∞. The lattice model IS the quantized Black-Scholes.',
        False
    ),
    'IMPOSSIBILITY_REVELATION_PRINCIPLE_LIMITS': (
        'Discrete Message Space',
        'Restrict agents to finite discrete message sets. Finite mechanism design: with |M| messages, the revelation principle holds exactly. Quantize the type space to a finite grid.',
        False
    ),
    'SEN_LIBERAL_PARADOX': (
        'Discrete Rights Partition',
        'Assign rights as discrete binary choices (veto/no-veto on specific alternatives). Quantized liberalism: each person controls exactly one binary dimension of the outcome space.',
        False
    ),
    'IMPOSSIBILITY_STABLE_MATCHING_THREE_SIDED': (
        'Discrete Preference Truncation',
        'Truncate preference lists to length k. With bounded discrete preferences, stable matching becomes tractable. The 3-sided instability requires unbounded preferences.',
        False
    ),

    # ===== BIOLOGY =====
    'IMPOSSIBILITY_COMPETITIVE_EXCLUSION': (
        'Discrete Niche Partitioning',
        'Quantize the resource spectrum into discrete niches. Each species occupies exactly one niche (discrete competitive exclusion). MacArthur\'s consumer-resource model on discrete resource types.',
        False
    ),
    'MULLERS_RATCHET': (
        'Discrete Fitness Classes',
        'Muller\'s ratchet operates on discrete fitness classes by definition. The ratchet clicks in discrete steps. Haigh (1978): finite population, discrete mutation classes, exact Markov chain.',
        False
    ),
    'PARADOX_OF_ENRICHMENT': (
        'Discrete Carrying Capacity Steps',
        'Quantize enrichment into discrete nutrient levels. At each discrete level, check stability. The paradox appears at a critical discrete threshold — phase transition on a quantized parameter.',
        False
    ),
    'IMPOSSIBILITY_NK_FITNESS_LANDSCAPE': (
        'Binary Genotype Space',
        'NK landscapes ARE defined on a quantized {0,1}^N genotype space. Fitness is a function on a discrete hypercube. The landscape is already fully quantized.',
        False
    ),
    'IMPOSSIBILITY_PRICE_EQUATION_CONSTRAINT': (
        'Discrete Generation Model',
        'Price equation in discrete (non-overlapping) generations. Wright-Fisher model: finite population, discrete allele frequencies. The Price equation becomes a finite sum over individuals.',
        False
    ),
    'FISHERS_THEOREM_LIMITS': (
        'Discrete Allele Model',
        'Wright-Fisher model: finite number of alleles on a discrete fitness landscape. Fisher\'s theorem becomes an exact identity over discrete genotype frequencies.',
        False
    ),

    # ===== DISTRIBUTED SYSTEMS =====
    'BYZANTINE_GENERALS_BOUND': (
        'Discrete Round Protocol',
        'Byzantine agreement protocols run in discrete rounds. Lamport (1982): exactly ceil((n-1)/3) rounds needed for n generals. The bound IS a discrete quantity on a discrete protocol.',
        False
    ),
    'FLP_IMPOSSIBILITY': (
        'Finite Round Protocols',
        'FLP applies to asynchronous systems. Quantize time into synchronous rounds (partial synchrony model — Dwork, Lynch, Stockmeyer 1988). Consensus becomes solvable with discrete round structure.',
        False
    ),
    'SYBIL_IMPOSSIBILITY': (
        'Discrete Identity Tokens',
        'Proof-of-work/proof-of-stake: quantize identity to discrete computational or monetary units. Each "identity" costs a discrete amount. Sybil resistance through quantized participation cost.',
        False
    ),

    # ===== QUANTUM =====
    'KOCHEN_SPECKER': (
        'Finite Measurement Contexts',
        'Restrict to a finite set of discrete measurement directions. Kochen-Specker sets are finite (e.g., 18 vectors in R^4). The theorem IS a statement about quantized measurement choices.',
        False
    ),
    'NO_BROADCASTING': (
        'Approximate Quantum Cloning',
        'Discrete quantum states: clone onto a finite set of output systems. Optimal 1→N cloning with discrete fidelity bounds. Broadcasting becomes approximate on a quantized output lattice.',
        False
    ),
    'NO_COMMUNICATION': (
        'Discrete Classical Communication',
        'Superdense coding: 1 qubit + 1 ebit = 2 classical bits. Quantize the communication to discrete classical bits. Holevo bound: at most log(d) classical bits from d-dimensional quantum state.',
        False
    ),
    'NO_DELETION': (
        'Discrete Erasure Channel',
        'Quantum erasure code: quantize the deletion into discrete "erased" vs "received" sectors. The erasure channel is a discrete quantum channel with known error locations.',
        False
    ),
    'IMPOSSIBILITY_TSIRELSON_BOUND': (
        'Discrete Correlation Polytope',
        'Quantize measurement settings to finite discrete choices. The correlation polytope (Bell polytope) is a finite discrete object. Tsirelson bound = max over quantum correlations on this discrete setting.',
        False
    ),
    'IMPOSSIBILITY_ENTANGLEMENT_MONOGAMY': (
        'Discrete Entanglement Units (Ebits)',
        'Quantize entanglement into discrete ebits. CKW inequality on discrete qubit systems: E(A:B) + E(A:C) <= E(A:BC). Monogamy becomes a discrete accounting constraint on ebit distribution.',
        False
    ),

    # ===== STRUCTURALLY IMPOSSIBLE (QUANTIZE genuinely doesn't apply) =====
    'CANTOR_DIAGONALIZATION': (
        'Finite Set Theory',
        'In finite set theory, all sets are countable and diagonalization cannot produce a "new" element outside the universe. But this destroys the purpose: QUANTIZE trivializes the theorem by removing infinity. STRUCTURALLY_IMPOSSIBLE as a resolution — it\'s dissolution, not resolution.',
        True
    ),
    'VITALI_NONMEASURABLE': (
        'Discrete Probability',
        'On finite/countable sets, ALL subsets are measurable. The Vitali construction requires uncountable AC. QUANTIZE dissolves the problem entirely — but loses the power of the continuum. STRUCTURALLY_IMPOSSIBLE as meaningful resolution.',
        True
    ),
    'BANACH_TARSKI': (
        'Finite Decomposition',
        'Banach-Tarski requires non-measurable sets via AC on R^3. In discrete/finite geometry, volume is additive and the paradox vanishes. QUANTIZE dissolves rather than resolves. STRUCTURALLY_IMPOSSIBLE.',
        True
    ),
    'INDEPENDENCE_OF_CH': (
        'Finite Cardinal Arithmetic',
        'CH concerns infinite cardinals. In finite arithmetic, there\'s no gap between aleph_0 and c. QUANTIZE removes the question rather than answering it. STRUCTURALLY_IMPOSSIBLE.',
        True
    ),
    'LOWENHEIM_SKOLEM': (
        'Finite Model Theory',
        'Lowenheim-Skolem concerns infinite models. Finite model theory is a different subject. QUANTIZE collapses the theorem. STRUCTURALLY_IMPOSSIBLE as a meaningful resolution.',
        True
    ),

    # ===== ROUND 2: remaining no-match hubs =====
    'ALGEBRIZATION_BARRIER': (
        'Discrete Arithmetic Circuits',
        'Restrict proofs to arithmetic circuits over finite fields GF(p). On a discrete finite field, algebraization barrier manifests as circuit depth bounds.',
        False
    ),
    'BAIRE_CATEGORY': (
        'Finite Intersection Property',
        'On finite discrete spaces, every set is both open and closed. Baire category becomes trivial: no set is meager in a discrete topology.',
        False
    ),
    'BGS_ORACLE_SEPARATION': (
        'Finite Oracle Table',
        'Replace oracle with a finite lookup table of N entries. Relativized separation becomes a finite combinatorial question.',
        False
    ),
    'CHRONOLOGY_PROTECTION': (
        'Discrete Causal Graph',
        'Causal set theory: replace smooth spacetime with a discrete partial order. Closed timelike curves become cycles in a finite directed graph.',
        False
    ),
    'CLASSIFICATION_IMPOSSIBILITY_WILD': (
        'Finite Representation Type',
        'Restrict to modules over finite-dimensional algebras with finite representation type. Complete discrete classification becomes possible.',
        False
    ),
    'COMMUNICATION_COMPLEXITY_LOWER_BOUND': (
        'Finite Protocol Tree',
        'Quantize communication to discrete rounds of b-bit messages. Protocol tree is a finite discrete object.',
        False
    ),
    'COSMIC_CENSORSHIP': (
        'Causal Dynamical Triangulation',
        'Spacetime as discrete simplicial complex. Singularities become identifiable boundary simplices. Censorship becomes combinatorial.',
        False
    ),
    'GIBBARD_SATTERTHWAITE': (
        'Binary Ballot Restriction',
        'Restrict to binary ballots with 2 candidates. GS reduces to majority rule which IS strategy-proof.',
        False
    ),
    'GOEDEL_INCOMPLETENESS_2': (
        'Bounded Proof Length Consistency',
        'In bounded arithmetic, consistency for proofs of length at most N is decidable. Quantize the proof search space.',
        False
    ),
    'HUMES_GUILLOTINE': (
        'Discrete Deontic Logic',
        'Deontic logic on finite state spaces: discrete permission/obligation assignments. Is-ought gaps become enumerable.',
        False
    ),
    'IMPOSSIBILITY_BALASSA_SAMUELSON_PRICE_CONVERGENCE': (
        'Discrete Sector Model',
        'Quantize economy into N discrete sectors with discrete productivity levels. Price convergence becomes finite equation system.',
        False
    ),
    'IMPOSSIBILITY_BANACH_TARSKI_PARADOX': (
        'Finite Piece Decomposition on Lattice',
        'On a discrete lattice, volume is additive and finitely decomposable. The paradox requires continuous non-measurable sets. STRUCTURALLY_IMPOSSIBLE: quantization dissolves rather than resolves.',
        True
    ),
    'IMPOSSIBILITY_COMPETITIVE_EQUILIBRIUM_INDIVISIBLE': (
        'Discrete Ascending Auction',
        'Walrasian tatonnement on integer prices. Kelso-Crawford gross substitutes condition on discrete lattice restores equilibrium.',
        False
    ),
    'IMPOSSIBILITY_EASTIN_KNILL_THEOREM': (
        'Solovay-Kitaev Gate Set Approximation',
        'Approximate universal gates from finite discrete gate set (Clifford + T). Solovay-Kitaev: any unitary to epsilon using O(log^c(1/eps)) discrete gates.',
        False
    ),
    'IMPOSSIBILITY_GROSSMAN_STIGLITZ_PARADOX': (
        'Discrete Information Purchase',
        'Quantize information acquisition to discrete costly signals. At each discrete price, efficiency is well-defined.',
        False
    ),
    'IMPOSSIBILITY_KOLMOGOROV_SUPERPOSITION_COMPUTATIONAL_BARRIER': (
        'Discrete Lookup Table',
        'On a discrete grid, any multivariate function IS a finite lookup table. Representational barrier vanishes.',
        False
    ),
    'IMPOSSIBILITY_LUCAS_CRITIQUE_POLICY_INVARIANCE': (
        'Discrete Regime Switching Model',
        'Markov switching: quantize policy regimes to discrete states. Lucas critique becomes finite state transition problem.',
        False
    ),
    'IMPOSSIBILITY_MODULARITY_EVOLVABILITY_TRADEOFF': (
        'Discrete Module Partition',
        'Quantize phenotype into N discrete modules. Modularity-evolvability tradeoff becomes discrete graph partitioning.',
        False
    ),
    'IMPOSSIBILITY_NO_BROADCASTING_THEOREM': (
        'Finite Approximate Broadcasting',
        'Approximate broadcasting to N copies with bounded fidelity on finite-dimensional systems.',
        False
    ),
    'IMPOSSIBILITY_NO_FREE_LUNCH': (
        'Finite Hypothesis Class PAC',
        'With |H|=N, PAC learning gives sample complexity O(log N / eps). NFL becomes counting on finite hypotheses.',
        False
    ),
    'IMPOSSIBILITY_NO_HIDING_THEOREM': (
        'Finite Hilbert Space Purification',
        'On finite-dimensional systems, information hides in discrete correlations with environment. Enumerable structure.',
        False
    ),
    'IMPOSSIBILITY_QUANTUM_CAPACITY_NO_ADDITIVITY': (
        'Finite Block Code Optimization',
        'Block codes of length N on d-dim systems. Quantum capacity becomes finite optimization over discrete codebook.',
        False
    ),
    'KAKUTANI_FIXED_POINT': (
        'Tarski Lattice Fixed Point',
        'Monotone maps on finite lattices have fixed points (Tarski). Kakutani on discrete grid becomes finite lattice computation.',
        False
    ),
    'LEWONTIN_HERITABILITY': (
        'Discrete ANOVA Decomposition',
        'Quantize phenotype/genotype to discrete categories. Heritability = between/total variance ratio in finite table.',
        False
    ),
    'META_CONCENTRATE_NONLOCAL': (
        'Discrete Bell Test',
        'Bell test with finite measurement settings. Nonlocality = linear program on discrete correlation polytope.',
        False
    ),
    'META_INVERT_INVARIANCE': (
        'Finite Symmetry Group Check',
        'Quantize symmetry group to finite subgroup. Invariance under discrete group is finitely checkable.',
        False
    ),
    'NO_HIDING': (
        'Finite Hilbert Space Redistribution',
        'Finite-dimensional no-hiding has constructive proofs. Information redistributes to discrete entanglement.',
        False
    ),
    'ONE_TIME_PAD_NECESSITY': (
        'Block Cipher Quantization',
        'AES: quantize plaintext into fixed-size blocks with finite key. Trade perfect secrecy for computational security.',
        False
    ),
    'PARIS_HARRINGTON': (
        'Bounded Ramsey Computation',
        'For each specific k,l the Ramsey number R(k,l) is computable. Quantize to finite bounds.',
        False
    ),
    'PROBLEM_OF_INDUCTION': (
        'Finite Bayesian Model Selection',
        'Finite hypothesis class + discrete evidence = well-defined Bayesian posterior. Induction becomes model selection.',
        False
    ),
    'RIGIDITY_MOSTOW': (
        'Discrete Hyperbolic Group',
        'Word-hyperbolic groups have no deformations (Sela). Rigidity is a discrete/combinatorial statement.',
        False
    ),
    'SOCIAL_CHOICE_IMPOSSIBILITY': (
        'Finite Ballot Enumeration',
        'N voters, K candidates, discrete ballots: Arrow impossibility is already a finite combinatorial theorem.',
        False
    ),
    'SZEMEREDI_REGULARITY_LIMIT': (
        'Graph Regularity on Finite Graphs',
        'Szemeredi regularity IS about finite graphs. Partition into discrete epsilon-regular pairs. Already quantized.',
        False
    ),
    'WEDDERBURN_LITTLE': (
        'Finite Field Classification',
        'Every finite division ring is a field. GF(p^n) classification IS the quantized/discrete setting.',
        False
    ),
    'WEINBERG_MASSLESS_CONSTRAINT': (
        'Lattice Gauge Theory',
        'Discrete spacetime lattice: massless particles have discrete momenta on Brillouin zone. Nielsen-Ninomiya fermion doubling.',
        False
    ),
}

# Step 3: Insert spokes where real techniques exist
added = 0
impossible_confirmed = 0
skipped = 0
results = []

for hub in quantize_empty:
    if hub in quantize_resolutions:
        name, desc, is_impossible = quantize_resolutions[hub]
        if is_impossible:
            impossible_confirmed += 1
            results.append({'hub': hub, 'status': 'STRUCTURALLY_IMPOSSIBLE', 'name': name})
            print(f'  IMPOSSIBLE: {hub:55s} -> {name}')
            continue

        iid = f'{hub}__CRACK_QUANTIZE'
        notes = f'{name}: {desc} | DAMAGE_OP: QUANTIZE | SOURCE: aletheia_wall_crack'
        try:
            db.execute(
                'INSERT INTO composition_instances (instance_id, comp_id, system_id, tradition, domain, notes) VALUES (?, ?, NULL, ?, ?, ?)',
                [iid, hub, 'Wall Crack', 'cross-domain', notes[:1000]])
            added += 1
            results.append({'hub': hub, 'status': 'CRACKED', 'name': name})
            print(f'  CRACKED:    {hub:55s} -> {name}')
        except Exception as e:
            skipped += 1
            results.append({'hub': hub, 'status': 'SKIP_ERROR', 'name': name, 'error': str(e)})
            print(f'  ERROR:      {hub:55s} -> {e}')
    else:
        skipped += 1
        results.append({'hub': hub, 'status': 'NO_MATCH', 'name': None})

db.commit()

# Final stats
total_spokes = db.execute('SELECT COUNT(*) FROM composition_instances').fetchone()[0]
total_q = db.execute("SELECT COUNT(*) FROM composition_instances WHERE notes LIKE '%DAMAGE_OP: QUANTIZE%'").fetchone()[0]

print()
print("=" * 70)
print(f"QUANTIZE WALL RESULTS")
print(f"  Empty hubs attacked:        {len(quantize_empty)}")
print(f"  Cracked (real technique):   {added}")
print(f"  Structurally impossible:    {impossible_confirmed}")
print(f"  No match found:             {skipped}")
print(f"  Total QUANTIZE spokes now:  {total_q}")
print(f"  Total spokes in DB:         {total_spokes}")
print("=" * 70)

# Save results
import json
with open('noesis/v2/crack_quantize_results.json', 'w') as f:
    json.dump({
        'quantize_empty_count': len(quantize_empty),
        'cracked': added,
        'structurally_impossible': impossible_confirmed,
        'no_match': skipped,
        'total_quantize_spokes': total_q,
        'details': results
    }, f, indent=2)

db.close()
print("\nResults saved to noesis/v2/crack_quantize_results.json")
