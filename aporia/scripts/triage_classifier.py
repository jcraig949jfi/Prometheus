"""
Aporia Phase 1 Triage Classifier
Classifies 490 math problems into Bucket A/B/C.

Rules (approved by Kairos + Claude_M1):
- Bucket A: Makes quantitative prediction testable against data we ALREADY have,
  AND our data exceeds published verification bounds OR offers novel sampling method.
- Bucket B: Testable with new data ingestion or extended computation.
- Bucket C: No computable prediction from current data.

Data inventory (from Mnemosyne audit + Claude_M1 additions):
- LMFDB: 3.8M EC, 1.1M MF, 66K genus-2, 793K Artin reps, 24.3M L-functions
- DuckDB: 184K Dirichlet zeros, 120K L-function zeros (on M2)
- Cartography: 13K knots (2977 with Jones), 980 polytopes, 134K QM9
- OEIS: 394K sequences (via cartography)
- prometheus_sci: 13K knots, 134K QM9, 230 space groups

Kairos corrections applied:
1. additive_combinatorics downgraded (5-8 Bucket A, not 20+)
2. knot_theory upgraded (13K knots, high invariant coverage)
3. Every Bucket A must check: does our data exceed published verification bound?
"""

import json
import sys

# Manual Bucket A overrides: problems with specific data coupling
# Format: id -> (bucket, data_source, test_spec, falsification_criterion)
BUCKET_A = {
    "MATH-0063": {
        "bucket": "A",
        "data_source": "LMFDB ec_curvedata (3.8M) + lfunc_lfunctions",
        "test_spec": "For 3.8M EC: (1) Compare algebraic rank to analytic rank (order of vanishing of L(E,s) at s=1). (2) For rank-0 curves, compute BSD ratio: L(E,1) / (Omega * prod(c_p) / |E(Q)_tors|^2). Should equal |Sha(E)|. (3) Statistical distribution of ranks by conductor.",
        "falsification_criterion": "ANY curve where analytic rank != algebraic rank; or BSD ratio is not a perfect square (required for |Sha|).",
        "published_bound": "Verified for all curves in LMFDB individually. Novel measurement: aggregate statistics and BSD ratio distribution at scale.",
        "notes": "BSD proven for rank 0,1 by Gross-Zagier/Kolyvagin. Rank 2+ is the frontier."
    },
    "MATH-0260": {
        "bucket": "A",
        "data_source": "LMFDB artin_reps (793K) + lfunc_lfunctions",
        "test_spec": "For each non-trivial irreducible Artin representation, check if the associated L-function has any poles. Filter to reps of dimension >= 2 where Artin conjecture is unproven.",
        "falsification_criterion": "ANY non-trivial irreducible Artin L-function with a pole at s != 0 or 1.",
        "published_bound": "Known for 1-dim (Dirichlet), 2-dim odd (Khare-Wintenberger). Novel: systematic scan of ALL 793K reps including even and higher-dim.",
        "notes": "LMFDB stores analytic properties of L-functions. Cross-reference artin_reps -> lfunc_lfunctions."
    },
    "MATH-0130": {
        "bucket": "A",
        "data_source": "LMFDB artin_reps (793K) + mf_newforms (1.1M)",
        "test_spec": "For each 2-dimensional Artin representation of conductor N: find a weight-1 modular newform of level N whose Hecke eigenvalues match the Artin rep's Frobenius traces at primes p not dividing N.",
        "falsification_criterion": "ANY 2-dim odd Artin rep with no matching weight-1 modular form in LMFDB. (Even reps are expected to fail matching -- document separately.)",
        "published_bound": "Serre's conjecture (proven) guarantees this for odd reps. Novel: EXPLICIT matching across 793K reps, finding any database gaps or mismatches.",
        "notes": "This tests the strongest form of reciprocity we can access computationally."
    },
    "MATH-0136": {
        "bucket": "A",
        "data_source": "LMFDB ec_curvedata (3.8M)",
        "test_spec": "For each EC with minimal discriminant Delta and conductor N: extract abc triples from the identity a + b = c where (a,b,c) are coprime and related to the curve's arithmetic. Compute the quality q(a,b,c) = log(c)/log(rad(abc)). Distribution of qualities across 3.8M curves.",
        "falsification_criterion": "Discovery of abc triple with quality > 2 (expected to not exist for sufficiently large c). Or: quality distribution inconsistent with Masser-Oesterle prediction.",
        "published_bound": "Best known quality is 1.6299... (Reyssat). Novel sampling: EC-derived triples provide a DIFFERENT population than exhaustive search.",
        "notes": "The abc conjecture has deep connections to EC via Szpiro's conjecture."
    },
    "MATH-0026": {
        "bucket": "A",
        "data_source": "LMFDB g2c_curves (66K)",
        "test_spec": "For all 66K genus-2 curves: compute |C(Q)| (number of rational points). Plot max |C(Q)| as a function of conductor. Test if bounded. If bounded, estimate the uniform bound B(2).",
        "falsification_criterion": "max |C(Q)| grows without bound as conductor -> infinity. Or: B(2) exceeds any reasonable function of g=2.",
        "published_bound": "Caporaso-Harris-Mazur proved Bombieri-Lang implies uniform boundedness. Our data gives first empirical estimate of B(2) from 66K curves.",
        "notes": "Also relevant to MATH-0193 (uniformity conjecture). Genus-2 is our only higher-genus dataset."
    },
    "MATH-0062": {
        "bucket": "A",
        "data_source": "DuckDB zeros (184K Dirichlet + 120K L-function zeros)",
        "test_spec": "Compute pair correlation function R_2(x) for: (1) Riemann zeta zeros, (2) Dirichlet L-function zeros by character, (3) degree-2 L-function zeros. Compare each to GUE prediction R_2(x) = 1 - (sin(pi*x)/(pi*x))^2.",
        "falsification_criterion": "R_2(x) deviates significantly from GUE at any scale or for any L-function family.",
        "published_bound": "Odlyzko verified for ~10^9 Riemann zeta zeros at height ~10^20. Novel: systematic comparison ACROSS L-function families.",
        "notes": "Blocked until DuckDB data available on M1 or Mnemosyne provides access. Combined with MATH-0175."
    },
    "MATH-0165": {
        "bucket": "A",
        "data_source": "DuckDB zeros (120K L-function zeros)",
        "test_spec": "Compute moments M_k(T) = (1/T) integral_0^T |L(1/2+it)|^{2k} dt for k=1,2,3 from zero data via explicit formula. Compare to Keating-Snaith prediction: M_k(T) ~ c_k (log T)^{k^2} where c_k = g(k) * a(k).",
        "falsification_criterion": "Moment growth rate deviates from k^2 power of log T; or leading coefficient deviates from predicted g(k).",
        "published_bound": "Verified numerically for zeta to high T. Novel: systematic test across Dirichlet and degree-2 L-function families.",
        "notes": "Blocked until zero data available. Combined with random matrix predictions."
    },
    "MATH-0332": {
        "bucket": "A",
        "data_source": "Cartography knots (2977 with Jones polynomial)",
        "test_spec": "For all 2977 knots with Jones polynomial data: check if any non-trivial knot has trivial Jones polynomial J(K) = 1 (the unknot's Jones polynomial). Also compute Jones polynomial statistics: distribution of degree, coefficient patterns.",
        "falsification_criterion": "ANY non-trivial knot with J(K) = 1 would disprove the conjecture.",
        "published_bound": "Verified to ~24 crossings (Thistlethwaite). Our data: 249 nontrivial knots with Jones data (up to ~11 crossings). Does NOT exceed published bound.",
        "notes": "DOWNGRADE CANDIDATE per Kairos criterion 3. Value is as consistency check and blind trial anchor, not new information. Keeping in A for instrument calibration."
    },
    "MATH-0145": {
        "bucket": "A",
        "data_source": "LMFDB artin_reps (793K) + nf (9K number fields)",
        "test_spec": "BLIND TRIAL: Brumer-Stark was PROVEN by Dasgupta-Kakde (2023). Test: without revealing this, point the instrument at the underlying data. For totally real NF, compute the Brumer-Stark element and test if it annihilates the class group. The instrument should DETECT the structural signature of the proof.",
        "falsification_criterion": "BLIND TRIAL: If instrument fails to detect structural consistency with the proven theorem, the instrument is miscalibrated.",
        "published_bound": "SOLVED. This is a calibration test, not a discovery test.",
        "notes": "Priority 0 per Kairos: blind trials should come BEFORE open-problem tests."
    },
    "MATH-0151": {
        "bucket": "A",
        "data_source": "OEIS primes + factorization data",
        "test_spec": "Compute Mobius autocorrelation C(h) = sum_{n<=N} mu(n)*mu(n+h) for h=1,2,...,100 and N up to our data limit. Test: does |C(h)| = o(N) as predicted by Chowla? Compute effective exponent: C(h) ~ N^alpha. Chowla predicts alpha < 1.",
        "falsification_criterion": "C(h) fails to be o(N) for any h; or effective alpha >= 1 for any shift.",
        "published_bound": "Tao (2016) proved log-averaged Chowla. Computational evidence to ~10^10 by Helfgott. Novel: systematic measurement across many shifts h simultaneously.",
        "notes": "Requires Mobius function computation from prime factorizations."
    },
    # Additional strong Bucket A candidates
    "MATH-0036": {
        "bucket": "A",
        "data_source": "LMFDB mf_newforms (1.1M) + artin_reps (793K)",
        "test_spec": "Test Arthur's multiplicity formula: for each automorphic representation (modular form), compute the predicted multiplicity from Arthur's conjectures. Compare to actual multiplicity in LMFDB data. Focus on weight-2 newforms where Arthur's conjectures make explicit predictions.",
        "falsification_criterion": "ANY modular form whose multiplicity in the automorphic spectrum deviates from Arthur's prediction.",
        "published_bound": "Arthur's endoscopic classification is proven for classical groups. For GL(2) this is well-understood. Novel: systematic verification across 1.1M forms.",
        "notes": "Complex test requiring careful implementation of multiplicity formulas."
    },
    "MATH-0370": {
        "bucket": "A",
        "data_source": "DuckDB zeros (184K Dirichlet + 120K L-function zeros)",
        "test_spec": "Compute zero-density function N(sigma, T) = #{rho = beta + i*gamma : L(rho)=0, beta > sigma, |gamma| < T} for each L-function family. Test: N(sigma, T) << T^{2(1-sigma)+epsilon}.",
        "falsification_criterion": "N(sigma, T) exceeds T^{2(1-sigma)+epsilon} bound for any sigma in (1/2, 1) and any T.",
        "published_bound": "Classical results by Ingham, Huxley. Novel: systematic computation across Dirichlet and degree-2 families.",
        "notes": "Blocked until zero data available."
    },
    "MATH-0193": {
        "bucket": "A",
        "data_source": "LMFDB g2c_curves (66K)",
        "test_spec": "Same as MATH-0026. Compute uniform bound on |C(Q)| for genus-2 curves.",
        "falsification_criterion": "Same as MATH-0026.",
        "published_bound": "Same as MATH-0026.",
        "notes": "Duplicate measurement with MATH-0026. Test both, report together."
    },
    "MATH-0042": {
        "bucket": "A",
        "data_source": "LMFDB nf (9K number fields)",
        "test_spec": "For each number field, compute the Mahler measure of its defining polynomial. Test: is M(P) >= M(L) = 1.17628... for all non-cyclotomic P? Build histogram of Mahler measures.",
        "falsification_criterion": "ANY non-cyclotomic polynomial with M(P) < M(Lehmer's polynomial).",
        "published_bound": "Verified to degree ~44 and height 10^4. Our 9K NF include diverse degrees. Novel: sampling from LMFDB rather than exhaustive search.",
        "notes": "Lehmer's polynomial: x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1."
    },
}

# Manual Bucket B overrides
BUCKET_B = {
    "MATH-0334": "Need hyperbolic volumes + colored Jones polynomials (not in current knot data)",
    "MATH-0331": "Need slice genus data (not in current KnotInfo ingest)",
    "MATH-0333": "Need finite-type invariants beyond current polynomial data",
    "MATH-0172": "Need height computation on rational points for Fano varieties",
    "MATH-0141": "Need K-theory regulators (beyond L-function values alone)",
    "MATH-0168": "Need p-adic regulator computation (beyond LMFDB standard fields)",
    "MATH-0143": "Need variety classification + rational point density data",
    "MATH-0174": "Need explicit height data on variety rational points",
    "MATH-0071": "Need l-adic Galois representations explicitly (partial in LMFDB)",
    "MATH-0070": "Need cycle class data (not standard in LMFDB)",
    "MATH-0133": "Subsumed by MATH-0130 but needs explicit weight-1 form construction",
    "MATH-0135": "Needs reductive group data beyond GL(2)",
    "MATH-0131": "Needs explicit functorial lifts (not in LMFDB standard tables)",
    "MATH-0097": "Needs uniformization data beyond standard MF tables",
    "MATH-0134": "Needs sheaf-theoretic data (categorical, not in any DB)",
    "MATH-0196": "Needs monodromy data (specialized AG computation)",
    "MATH-0300": "Needs line bundle computation on varieties",
}

# Subdomains that are almost entirely Bucket C
BUCKET_C_SUBDOMAINS = {
    'operator_algebra', 'ring_theory', 'k_theory', 'homological_algebra',
    'universal_algebra', 'combinatorial_matrix_theory', 'geometric_algebra',
    'real_algebra', 'matroid_theory', 'galois_cohomology', 'combinatorial_group_theory',
    'galois_theory', 'modular_representation_theory', 'character_theory',
    'fluid_dynamics', 'order_theory', 'combinatorial_geometry', 'combinatorial_set_theory',
    'complex_dynamics', 'game_theory', 'partial_differential_equations',
    'quantum_field_theory', 'celestial_mechanics', 'optimization',
    'intelligence', 'operator_k_theory', 'geometric_topology',
    'diophantine_approximation', 'quantum_mechanics', 'quantum_chaos',
    'symplectic_geometry', 'spectral_geometry', 'fractal_geometry',
    'computability', 'applied_mathematics', 'category_theory',
    'symplectic_topology', 'queueing_theory', 'stochastic_geometry',
    'statistical_physics', 'signal_processing', 'convex_geometry',
    'frame_theory', 'approximation_theory', 'set_theory', 'model_theory',
    'homotopy_theory', 'functional_analysis', 'real_algebraic_geometry',
    'representation_theory', 'algebraic_topology', 'algebraic_k_theory',
    'numerical_analysis', 'chaos_theory', 'polyhedral_geometry',
    'potential_theory', 'linear_algebra', 'pde',
    'mathematical_physics', 'dynamical_systems', 'topology',
    'differential_geometry', 'complex_analysis', 'harmonic_analysis',
    'geometry', 'ergodic_theory', 'probability_theory',
    'differential_algebra', 'computational_complexity',
    'discrepancy_theory', 'spectral_graph_theory',
    'random_matrix_theory',  # MATH-0473 is theoretical
}

# Subdomains that are mixed -- need per-problem classification
MIXED_SUBDOMAINS = {
    'number_theory', 'analytic_number_theory', 'algebraic_geometry',
    'automorphic_forms', 'knot_theory', 'diophantine_geometry',
    'diophantine_equations', 'algebraic_number_theory', 'arithmetic_geometry',
    'additive_combinatorics', 'additive_number_theory',
    'combinatorics', 'graph_theory', 'discrete_geometry', 'group_theory',
    'matrix_theory', 'commutative_algebra', 'quantum_information',
    'analysis', 'ramsey_theory',
}

# Number theory problems that are Bucket C (verification bounds exceeded or structural)
NT_BUCKET_C = {
    "MATH-0057",  # Goldbach - verified to 4e18
    "MATH-0058",  # Twin primes - structural, infinite count needed
    "MATH-0059",  # Legendre - verified to huge bounds
    "MATH-0060",  # RH - verified to 10^13 zeros
    "MATH-0061",  # Lindelof - structural bound
    "MATH-0064",  # Hodge - no computable test
    "MATH-0065",  # Cramer - verified to huge bounds
    "MATH-0066",  # Polignac - structural, infinite count
    "MATH-0067",  # Artin primitive roots - verified extensively
    "MATH-0068",  # Abundance - structural AG
    "MATH-0069",  # Jacobian conjecture - structural
    "MATH-0072",  # Section conjecture - structural
    "MATH-0073",  # Nagata curves - structural
    "MATH-0091",  # RH duplicate
    "MATH-0092",  # Hilbert 9 - structural
    "MATH-0093",  # Hilbert 12 - structural
    "MATH-0094",  # Hilbert 15 - structural
    "MATH-0098",  # Smale 4 - complexity theoretic
    "MATH-0099",  # Smale 5 - complexity theoretic
    "MATH-0121",  # Erdos-Mollin-Walsh - verified to huge bounds
    "MATH-0122",  # Erdos-Selfridge - structural
    "MATH-0123",  # Erdos-Straus - verified to 10^14
    "MATH-0127",  # Erdos ternary - verified to huge bounds
    "MATH-0128",  # Erdos-Moser - verified to huge bounds
    "MATH-0137",  # Agoh-Giuga - verified to 10^13800
    "MATH-0138",  # Andrica - verified to huge bounds
    "MATH-0140",  # Beal - verified extensively
    "MATH-0144",  # Brocard's conj - verified to huge bounds
    "MATH-0146",  # Bunyakovsky - structural (infinite values)
    "MATH-0147",  # Carmichael totient - verified to 10^10
    "MATH-0148",  # Catalan-Dickson - structural (sequence behavior)
    "MATH-0149",  # Catalan's Mersenne - verified to known Mersenne
    "MATH-0153",  # Elliott-Halberstam - sieve theory structural
    "MATH-0155",  # Firoozbakht - verified to huge bounds
    "MATH-0156",  # Fortune - verified to large primorials
    "MATH-0157",  # Four exponentials - transcendence theory
    "MATH-0158",  # Gauss circle - requires analytic computation
    "MATH-0159",  # Gilbreath - verified to 10^13
    "MATH-0161",  # Goormaghtigh - verified to huge bounds
    "MATH-0162",  # Grimm - verified to huge bounds
    "MATH-0166",  # Lemoine - verified to 10^9
    "MATH-0167",  # Lenstra-Pomerance-Wagstaff - asymptotic prediction
    "MATH-0176",  # n conjecture - generalization of abc
    "MATH-0177",  # New Mersenne - verified for known primes
    "MATH-0178",  # Oppermann - verified to huge bounds
    "MATH-0185",  # Schanuel - transcendence theory
    "MATH-0186",  # Schinzel H - structural
    "MATH-0187",  # Scholz - verified to large n
    "MATH-0188",  # Second HL - structural
    "MATH-0189",  # Selfridge - verified for known primes
    "MATH-0190",  # Singmaster - verified for large range
    "MATH-0192",  # Unicity Markov - verified to 10^6
    "MATH-0194",  # Vandiver - verified to p < 163M
    "MATH-0195",  # Vojta - structural
    "MATH-0199",  # Bateman-Horn - asymptotic prediction
    "MATH-0200",  # Waring refined - verified for small k
    "MATH-0259",  # Landau 4th - structural (infinite primes)
    "MATH-0285",  # Suslin - set theory
    "MATH-0286",  # Kummer-Vandiver - same as MATH-0194
    "MATH-0288",  # Lander-Parkin-Selfridge - verified
    "MATH-0289",  # Giuga - same as MATH-0137
    "MATH-0290",  # Brocard's problem - verified to huge bounds
    "MATH-0291",  # Erdos-Kac extensions - structural
    "MATH-0292",  # Wall-Sun-Sun - search problem
    "MATH-0293",  # Wieferich - search problem
    "MATH-0294",  # Mersenne infinitude - structural
    "MATH-0295",  # Sophie Germain infinitude - structural
    "MATH-0296",  # Safe prime infinitude - structural
    "MATH-0303",  # 196 Lychrel - search problem
    "MATH-0304",  # Solitary 10 - verified for small range
    "MATH-0305",  # Euler-Mascheroni - transcendence
    "MATH-0306",  # Odd perfect - search problem to 10^2200
    "MATH-0307",  # Sum of three cubes - verified for many integers
    "MATH-0309",  # Normality of pi - structural
    "MATH-0310",  # Normality of e - structural
    "MATH-0311",  # Normality of sqrt(2) - structural
    "MATH-0312",  # e+pi irrationality - transcendence
    "MATH-0314",  # Perfect number infinitude - structural
    "MATH-0315",  # Fermat prime infinitude - structural
    "MATH-0316",  # Amicable pairs infinitude - structural
    "MATH-0317",  # Odd weird numbers - search problem
    "MATH-0318",  # Catalan generalization - search problem
    "MATH-0319",  # Benford primes - asymptotic
    "MATH-0344",  # Buchi - search problem
    "MATH-0348",  # GRH - verified to huge bounds
    "MATH-0349",  # Grand RH - structural
    "MATH-0350",  # Hilbert-Polya - structural
    "MATH-0352",  # Magic square of squares - search
    "MATH-0356",  # Prouhet-Tarry-Escott - search
    "MATH-0363",  # Eternity II - puzzle
    "MATH-0368",  # Ankeny-Artin-Chowla - verified
    "MATH-0369",  # Cramer-Granville - verified to huge bounds
    "MATH-0372",  # Guy friendly numbers - search
    "MATH-0009",  # Goncharov - motivic (structural)
    "MATH-0010",  # Green's conjecture - Brill-Noether (structural)
    "MATH-0014",  # Hilbert 15 - Schubert (structural)
    "MATH-0028",  # Zariski-Lipman - structural AG
}

# Analytic NT problems testable against zero data
ANT_BUCKET_A_IDS = {
    "MATH-0062",  # Pair correlation
    "MATH-0165",  # Keating-Snaith
    "MATH-0175",  # Montgomery (same as 0062)
    "MATH-0370",  # Density hypothesis
    "MATH-0476",  # Zeta derivative bounds
    "MATH-0477",  # Discrete moments
    "MATH-0478",  # Zero multiplicity
    "MATH-0479",  # Prime race first sign change
    "MATH-0482",  # Primes from quadratic forms
    "MATH-0483",  # Prime race ties density zero
    "MATH-0484",  # Explicit Mertens bounds
    "MATH-0485",  # Sign changes of psi(x)-x
}

# Ben Green problems that are pure theory (Bucket C)
BEN_GREEN_C = {f"MATH-0{i}" for i in range(373, 422)} - ANT_BUCKET_A_IDS
# Also Ben Green ANT problems
BEN_GREEN_ANT_C = {f"MATH-0{i}" for i in range(408, 422)} - ANT_BUCKET_A_IDS

# CPNT problems that are structural
CPNT_C = {
    "MATH-0474",  # Irrationality of zeta zero ordinates - needs proof, not computation
    "MATH-0475",  # Irrationality of first zero - needs proof
    "MATH-0480",  # Mertens for NF - needs NF zero data
    "MATH-0481",  # Linear independence in function fields - structural
}


def classify(problem):
    """Classify a single problem into A/B/C."""
    pid = problem['id']
    sd = problem['subdomain']

    # Check manual overrides first
    if pid in BUCKET_A:
        return BUCKET_A[pid]

    if pid in BUCKET_B:
        return {
            "bucket": "B",
            "data_source": "Requires data extension",
            "test_spec": BUCKET_B[pid],
            "falsification_criterion": "Pending data availability",
            "published_bound": "",
            "notes": ""
        }

    if pid in NT_BUCKET_C or pid in CPNT_C:
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "Exceeds our data or structural only",
            "notes": ""
        }

    # ANT problems testable against zero data
    if pid in ANT_BUCKET_A_IDS:
        return {
            "bucket": "A",
            "data_source": "DuckDB zeros (184K Dirichlet + 120K L-function)",
            "test_spec": f"Compute relevant statistic from L-function zero data. See specific test for {pid}.",
            "falsification_criterion": "Deviation from predicted asymptotic behavior.",
            "published_bound": "Novel: systematic comparison across L-function families",
            "notes": "Blocked until zero data accessible from M1"
        }

    # Ben Green additive combinatorics - mostly C per Kairos
    if pid in BEN_GREEN_C or pid in BEN_GREEN_ANT_C:
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "Theoretical — requires sieve/extremal computation, not DB lookup",
            "notes": "Downgraded per Kairos correction 1"
        }

    # Pure Bucket C subdomains
    if sd in BUCKET_C_SUBDOMAINS:
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": f"Subdomain {sd} has no data coupling"
        }

    # Remaining mixed-subdomain problems default to C unless caught above
    # Graph theory: all C (no graph database)
    if sd == 'graph_theory':
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": "Graph theory — no relevant graph database"
        }

    # Discrete geometry: all C (no geometric object database)
    if sd == 'discrete_geometry':
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": "Discrete geometry — no relevant database"
        }

    # Combinatorics: mostly C, a few might be B (OEIS)
    if sd == 'combinatorics':
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": "Combinatorics — OEIS gives sequence terms but not proofs"
        }

    # Group theory: C
    if sd == 'group_theory':
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": "Group theory — no relevant database"
        }

    # Additive number theory remaining
    if sd in ('additive_number_theory', 'additive_combinatorics'):
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": "Additive — requires sieve computation, not DB lookup (Kairos correction 1)"
        }

    # Ramsey theory
    if sd == 'ramsey_theory':
        return {
            "bucket": "C",
            "data_source": "",
            "test_spec": "",
            "falsification_criterion": "",
            "published_bound": "",
            "notes": "Ramsey theory — computation-bound, not database-testable"
        }

    # Default: C
    return {
        "bucket": "C",
        "data_source": "",
        "test_spec": "",
        "falsification_criterion": "",
        "published_bound": "",
        "notes": f"Default classification for subdomain {sd}"
    }


def main():
    problems = []
    with open('aporia/mathematics/questions.jsonl') as f:
        for line in f:
            problems.append(json.loads(line.strip()))

    results = []
    counts = {"A": 0, "B": 0, "C": 0}

    for p in problems:
        c = classify(p)
        entry = {
            "id": p['id'],
            "title": p['title'],
            "subdomain": p['subdomain'],
            **c
        }
        results.append(entry)
        counts[c['bucket']] += 1

    # Write triage file
    with open('aporia/mathematics/triage.jsonl', 'w') as f:
        for r in results:
            f.write(json.dumps(r) + '\n')

    print(f"Triage complete: A={counts['A']}, B={counts['B']}, C={counts['C']}")
    print(f"Total: {sum(counts.values())}")

    # Print Bucket A summary
    print("\n=== BUCKET A ===")
    for r in results:
        if r['bucket'] == 'A':
            print(f"  {r['id']}: {r['title']}")
            print(f"    Data: {r['data_source'][:80]}")
            print(f"    Kill: {r['falsification_criterion'][:80]}")
            print()

    # Print Bucket B summary
    print("=== BUCKET B ===")
    for r in results:
        if r['bucket'] == 'B':
            print(f"  {r['id']}: {r['title']}")
            print(f"    Needs: {r['test_spec'][:80]}")
            print()


if __name__ == '__main__':
    main()
