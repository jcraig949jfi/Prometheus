"""
Aporia — Expand the mathematics catalog with additional sources.

Adds questions from: Hilbert's problems (open ones), Smale's problems,
Simon problems, Erdős conjectures, comprehensive conjecture list,
Langlands program, and all missing Wikipedia problems.

Deduplicates against existing questions.jsonl by title similarity.
"""

import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATH_JSONL = ROOT / "mathematics" / "questions.jsonl"

# ── Load existing ────────────────────────────────────────────────────────

def load_existing():
    existing = []
    if MATH_JSONL.exists():
        with open(MATH_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.append(json.loads(line))
    return existing


def normalize_title(t):
    """Normalize for dedup: lowercase, strip punctuation, collapse whitespace."""
    t = t.lower().strip()
    t = re.sub(r"[''`\u2013\u2014\-]", "", t)
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def get_existing_titles(existing):
    return {normalize_title(q["title"]) for q in existing}


def next_id(existing):
    max_num = 0
    for q in existing:
        m = re.match(r"MATH-(\d+)", q["id"])
        if m:
            max_num = max(max_num, int(m.group(1)))
    return max_num


def q(counter, subdomain, title, statement, **kw):
    counter[0] += 1
    return {
        "id": f"MATH-{counter[0]:04d}",
        "title": title,
        "domain": "mathematics",
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

# ── New questions ────────────────────────────────────────────────────────

def new_questions(counter):
    qs = []
    def m(sub, title, stmt, **kw):
        qs.append(q(counter, sub, title, stmt, **kw))

    WIKI = "https://en.wikipedia.org/wiki/List_of_unsolved_problems_in_mathematics"
    CONJ = "https://en.wikipedia.org/wiki/List_of_conjectures"
    HILB = "https://en.wikipedia.org/wiki/Hilbert%27s_problems"
    SMALE = "https://en.wikipedia.org/wiki/Smale%27s_problems"
    SIMON = "https://en.wikipedia.org/wiki/Simon_problems"
    ERDOS = "https://en.wikipedia.org/wiki/Erd%C5%91s_conjecture"
    LANG = "https://en.wikipedia.org/wiki/Langlands_program"

    # ── Hilbert's open problems ──────────────────────────────────────
    m("set_theory", "Hilbert 1: Continuum hypothesis", "Is there a set whose cardinality is strictly between integers and reals?", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"])
    m("number_theory", "Hilbert 8: Riemann hypothesis", "All non-trivial zeros of the Riemann zeta function have real part 1/2.", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert", "millennium"], notes="Also Millennium Prize and Smale #1")
    m("number_theory", "Hilbert 9: General reciprocity law", "Find the most general reciprocity theorem in algebraic number fields.", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"])
    m("number_theory", "Hilbert 12: Kronecker's Jugendtraum", "Extend Kronecker's theorem on abelian extensions to any number field.", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"])
    m("algebraic_geometry", "Hilbert 15: Schubert calculus", "Provide rigorous foundation for Schubert's enumeration methods.", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"], status="partially_solved")
    m("real_algebraic_geometry", "Hilbert 16: Topology of algebraic curves", "Describe relative positions of ovals from real algebraic curves and count limit cycles.", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"])
    m("pde", "Hilbert 20: Boundary value problems", "Do all variational problems with boundary conditions have solutions?", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"])
    m("automorphic_forms", "Hilbert 22: Uniformization", "Can analytic relations be uniformized via automorphic functions?", year_posed=1900, posed_by="David Hilbert", sources=[HILB], tags=["hilbert"])

    # ── Smale's open problems ────────────────────────────────────────
    m("number_theory", "Smale 4: Shub-Smale tau conjecture", "Bounds on integer zeros of single-variable polynomials.", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("number_theory", "Smale 5: Diophantine in exponential time", "Can one decide if a Diophantine equation has integer solutions in exponential time?", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("celestial_mechanics", "Smale 6: N-body central configurations", "Is the number of relative equilibria finite in the n-body problem for any mass choice?", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("discrete_geometry", "Smale 7: Distribution of points on 2-sphere", "Find algorithm minimizing logarithmic potential energy for N points on a sphere.", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("optimization", "Smale 9: Strongly polynomial linear programming", "Find a strongly-polynomial time algorithm for linear programming feasibility.", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("dynamical_systems", "Smale 10: Pugh's closing lemma", "Extend the closing lemma to higher smoothness in dynamical systems.", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("dynamical_systems", "Smale 12: Diffeomorphism centralizers", "Are diffeomorphisms with trivial centralizers dense in C^r?", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("dynamical_systems", "Smale 13: Hilbert's 16th problem (Smale)", "Bound the number of limit cycles of polynomial vector fields.", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])
    m("intelligence", "Smale 18: Limits of intelligence", "Fundamental limits of human and machine intelligence.", year_posed=1998, posed_by="Steve Smale", sources=[SMALE], tags=["smale"])

    # ── Simon problems (open ones) ───────────────────────────────────
    m("mathematical_physics", "Simon 1: Anderson model extended states", "Prove the Anderson model has purely absolutely continuous spectrum for v >= 3.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 2: Anderson model 2D localization", "Prove the spectrum of the 2D Anderson model is dense pure point.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 3: Quantum diffusion", "Demonstrate particle displacement grows linearly with time in higher dimensions.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 6: Almost Mathieu critical coupling", "Establish absolutely continuous spectrum at critical coupling for all irrational alpha.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 8: Decaying potential AC spectrum", "Prove spectral properties for Laplacian plus decaying potential in higher dimensions.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 9: Ionization boundedness", "Prove N_0(Z) - Z is bounded as Z -> infinity.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 10: Ionization energy asymptotics", "Determine asymptotic behavior of ionization energy as nuclear charge increases.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 11: Nuclear shell model", "Make mathematical sense of the nuclear shell model.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 12: Molecular configuration", "Justify first-principles molecular configuration determination.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 13: Quantum crystals", "Prove ground states approach periodic configurations as nuclear count -> infinity.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 14: Density of states continuity", "Prove the integrated density of states k(E) is continuous in E.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])
    m("mathematical_physics", "Simon 15: Lieb-Thirring conjecture", "Establish optimal constants in the Lieb-Thirring inequality.", year_posed=2000, posed_by="Barry Simon", sources=[SIMON], tags=["simon"])

    # ── Erdős conjectures ────────────────────────────────────────────
    m("graph_theory", "Erdős-Gyárfás conjecture", "Every graph with minimum degree 3 has a cycle whose length is a power of 2.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("combinatorics", "Erdős-Hajnal conjecture", "Graphs excluding a fixed induced subgraph contain a polynomially large clique or independent set.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("number_theory", "Erdős-Mollin-Walsh conjecture", "There are no three consecutive powerful numbers.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("number_theory", "Erdős-Selfridge conjecture", "Every covering system with distinct moduli has at least one even modulus.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("diophantine_equations", "Erdős-Straus conjecture", "The equation 4/n = 1/x + 1/y + 1/z has positive integer solutions for all n > 1.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("additive_combinatorics", "Erdős conjecture on arithmetic progressions", "Every set with divergent sum of reciprocals contains arbitrarily long arithmetic progressions.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("discrete_geometry", "Erdős-Szekeres conjecture", "2^(n-2)+1 points in general position guarantee a convex n-gon.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("additive_combinatorics", "Erdős-Turán conjecture on additive bases", "If A is an additive basis of order 2, then the representation function is unbounded.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("number_theory", "Erdős ternary expansion conjecture", "Powers of 2 contain digit 2 in base 3 for all n > 8.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("diophantine_equations", "Erdős-Moser conjecture", "1^k + 2^k + ... + (m-1)^k = m^k has no solutions except 1+2=3.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])
    m("combinatorics", "Erdős minimum overlap problem", "Determine the limiting behavior of overlapping sets in partitions.", posed_by="Paul Erdős", sources=[ERDOS], tags=["erdos"])

    # ── Langlands program ────────────────────────────────────────────
    m("automorphic_forms", "Langlands reciprocity conjecture", "Every Artin L-function equals one arising from an automorphic cuspidal representation.", sources=[LANG], tags=["langlands"])
    m("automorphic_forms", "Langlands functoriality conjecture", "Homomorphisms of L-groups produce correspondences between automorphic forms.", sources=[LANG], tags=["langlands"])
    m("representation_theory", "Local Langlands correspondence", "Parameterize L-packets of admissible irreducible representations of reductive groups over local fields.", sources=[LANG], tags=["langlands"])
    m("automorphic_forms", "Global Langlands for GL(2,Q)", "Complete correspondence for GL(2) over the rationals.", sources=[LANG], tags=["langlands"])
    m("algebraic_geometry", "Geometric Langlands conjecture", "Establish deeper categorical relationship between sheaves on BunG and coherent sheaves on parameter stack.", sources=[LANG], tags=["langlands"])
    m("automorphic_forms", "Generalized functoriality for reductive groups", "Relate automorphic representations compatibly with L-functions for all reductive groups.", sources=[LANG], tags=["langlands"])

    # ── From comprehensive conjecture list (not already in catalog) ──
    m("number_theory", "abc conjecture", "For coprime a+b=c, the radical rad(abc) is usually not much smaller than c.", sources=[CONJ], tags=["number_theory"], notes="Mochizuki claims proof via IUT; disputed")
    m("number_theory", "Agoh-Giuga conjecture", "p is prime iff sum of (k^(p-1)) for k=1..p-1 is -1 mod p.", sources=[CONJ])
    m("number_theory", "Andrica's conjecture", "The difference of consecutive prime square roots is always less than 1.", sources=[CONJ])
    m("operator_k_theory", "Baum-Connes conjecture", "The assembly map in K-theory of reduced group C*-algebras is an isomorphism.", sources=[CONJ])
    m("number_theory", "Beal's conjecture", "If A^x + B^y = C^z with A,B,C,x,y,z positive integers and x,y,z>2, then A,B,C share a common factor.", sources=[CONJ])
    m("number_theory", "Beilinson conjecture", "Relates special values of L-functions to regulators of algebraic K-theory.", sources=[CONJ])
    m("harmonic_analysis", "Bochner-Riesz conjecture", "Bochner-Riesz means converge in L^p for certain ranges of p.", sources=[CONJ])
    m("diophantine_geometry", "Bombieri-Lang conjecture", "Varieties of general type over number fields have non-dense rational points.", sources=[CONJ])
    m("number_theory", "Brocard's conjecture", "There are at least four primes between p_n^2 and p_{n+1}^2 for n >= 2.", sources=[CONJ])
    m("number_theory", "Brumer-Stark conjecture", "Relates Artin L-functions to annihilators of class groups.", sources=[CONJ])
    m("number_theory", "Bunyakovsky conjecture", "Irreducible polynomials with positive leading coefficient and gcd(f(1),f(2),...)=1 take infinitely many prime values.", sources=[CONJ])
    m("number_theory", "Carmichael totient conjecture", "For every n, the equation phi(x)=n has either 0 or >= 2 solutions.", sources=[CONJ])
    m("number_theory", "Catalan-Dickson conjecture", "All aliquot sequences either terminate or become periodic.", sources=[CONJ])
    m("number_theory", "Catalan's Mersenne conjecture", "The sequence M2, M_{M2}, M_{M_{M2}}, ... is all prime.", sources=[CONJ])
    m("group_theory", "Cherlin-Zilber conjecture", "Every simple group of finite Morley rank is an algebraic group over an algebraically closed field.", sources=[CONJ])
    m("number_theory", "Chowla conjecture", "Correlations of the Möbius function with itself at shifted arguments vanish.", sources=[CONJ])
    m("graph_theory", "Conway's thrackle conjecture", "A thrackle has at most as many edges as vertices.", sources=[CONJ])
    m("number_theory", "Elliott-Halberstam conjecture", "Primes in arithmetic progressions have level of distribution 1.", sources=[CONJ])
    m("graph_theory", "Erdős-Faber-Lovász conjecture", "The chromatic number of the union of n edge-disjoint complete graphs sharing at most one vertex is n.", sources=[CONJ])
    m("number_theory", "Firoozbakht's conjecture", "p_n^{1/n} is strictly decreasing for all n >= 1.", sources=[CONJ])
    m("number_theory", "Fortune's conjecture", "For every primorial p_n#, the smallest prime greater than p_n#+1 gives a fortunate number that is prime.", sources=[CONJ])
    m("number_theory", "Four exponentials conjecture", "At least one of certain four exponentials is transcendental.", sources=[CONJ])
    m("number_theory", "Gauss circle problem", "Determine the exact error term in counting lattice points inside a circle.", sources=[CONJ])
    m("number_theory", "Gilbreath conjecture", "Iterated absolute differences of prime sequence always begin with 1.", sources=[CONJ])
    m("graph_theory", "Goldberg-Seymour conjecture", "The chromatic index of a multigraph is at most max(Delta+1, Gamma).", sources=[CONJ])
    m("number_theory", "Goormaghtigh conjecture", "The Diophantine equation (x^m-1)/(x-1) = (y^n-1)/(y-1) has only two known solutions.", sources=[CONJ])
    m("number_theory", "Grimm's conjecture", "If n+1,...,n+k are all composite, they have distinct prime factors in order.", sources=[CONJ])
    m("geometric_topology", "Hilbert-Smith conjecture", "Every locally compact group acting effectively on a manifold is a Lie group.", sources=[CONJ])
    m("probability_theory", "Ibragimov-Iosifescu conjecture", "CLT holds for phi-mixing sequences under certain variance conditions.", sources=[CONJ])
    m("number_theory", "Keating-Snaith conjecture", "Moments of the Riemann zeta on the critical line follow random matrix predictions.", sources=[CONJ])
    m("number_theory", "Lemoine's conjecture", "Every odd number >= 7 is the sum of an odd prime and twice a prime.", sources=[CONJ])
    m("number_theory", "Lenstra-Pomerance-Wagstaff conjecture", "Predicts the distribution of Mersenne primes.", sources=[CONJ])
    m("number_theory", "Leopoldt's conjecture", "The p-adic regulator of a number field is non-zero.", sources=[CONJ])
    m("graph_theory", "List coloring conjecture", "The list chromatic number of every graph equals its chromatic index.", sources=[CONJ])
    m("diophantine_approximation", "Littlewood conjecture", "For all real alpha, beta: liminf n*||n*alpha||*||n*beta|| = 0.", sources=[CONJ])
    m("graph_theory", "Lovász conjecture", "Every connected vertex-transitive graph has a Hamiltonian path.", sources=[CONJ])
    m("diophantine_geometry", "Manin conjecture", "Describes the distribution of rational points of bounded height on Fano varieties.", sources=[CONJ])
    m("number_theory", "Marshall Hall's conjecture", "|x^3 - y^2| >> x^{1/2} for integers x,y with y^2 != x^3.", sources=[CONJ])
    m("diophantine_geometry", "Mazur's conjectures", "Topology of rational points on varieties: connected components and density.", sources=[CONJ])
    m("analytic_number_theory", "Montgomery's pair correlation conjecture", "Pair correlation of zeta zeros follows the GUE distribution.", sources=[CONJ])
    m("number_theory", "n conjecture", "Generalization of abc to n terms with appropriate height bounds.", sources=[CONJ])
    m("number_theory", "New Mersenne conjecture", "Characterizes which Mersenne numbers are prime based on p.", sources=[CONJ])
    m("number_theory", "Oppermann's conjecture", "There is always a prime between n^2-n and n^2, and between n^2 and n^2+n.", sources=[CONJ])
    m("graph_theory", "Petersen coloring conjecture", "Every bridgeless cubic graph has a Petersen minor.", sources=[CONJ])
    m("computational_complexity", "Quantum PCP conjecture", "Quantum analogue of the PCP theorem holds.", sources=[CONJ])
    m("graph_theory", "Reconstruction conjecture", "Every graph on 3+ vertices is determined by its deck of vertex-deleted subgraphs.", sources=[CONJ])
    m("graph_theory", "Ringel-Kotzig conjecture", "Every tree with m edges has a graceful labeling.", sources=[CONJ])
    m("additive_combinatorics", "Rudin's conjecture on squares in APs", "The number of perfect squares in an arithmetic progression of length N is O(N^{2/3+epsilon}).", sources=[CONJ])
    m("dynamical_systems", "Sarnak conjecture", "The Möbius function is orthogonal to all zero-entropy sequences.", sources=[CONJ])
    m("number_theory", "Schanuel's conjecture", "If z_1,...,z_n are Q-linearly independent complex numbers, then the transcendence degree of {z_i, e^{z_i}} is >= n.", sources=[CONJ])
    m("number_theory", "Schinzel's hypothesis H", "Polynomials satisfying necessary conditions simultaneously take prime values infinitely often.", sources=[CONJ])
    m("number_theory", "Scholz conjecture", "The shortest addition chain for 2^n-1 is at most n-1 + the chain length for n.", sources=[CONJ])
    m("number_theory", "Second Hardy-Littlewood conjecture", "pi(x+y) <= pi(x) + pi(y) for all x,y >= 2.", sources=[CONJ])
    m("number_theory", "Selfridge's conjecture", "No Wieferich prime is also a Wilson prime.", sources=[CONJ])
    m("number_theory", "Singmaster's conjecture", "There is a finite upper bound on how many times a number (other than 1) can appear in Pascal's triangle.", sources=[CONJ])
    m("graph_theory", "Tuza's conjecture", "The minimum triangle edge cover is at most twice the maximum triangle packing.", sources=[CONJ])
    m("number_theory", "Unicity conjecture for Markov numbers", "Markov numbers determine their Markov triples uniquely.", sources=[CONJ])
    m("diophantine_geometry", "Uniformity conjecture", "The number of rational points on a genus g >= 2 curve over Q is bounded by a function of g alone.", sources=[CONJ])
    m("number_theory", "Vandiver's conjecture", "The class number of the maximal real subfield of cyclotomic fields is not divisible by p.", sources=[CONJ])
    m("number_theory", "Vojta's conjecture", "Deep analogue of Nevanlinna theory for number fields predicting Diophantine approximation bounds.", sources=[CONJ])
    m("algebraic_geometry", "Weight monodromy conjecture", "The monodromy filtration equals the weight filtration up to shift on l-adic cohomology.", sources=[CONJ])
    m("algebraic_k_theory", "Bloch-Beilinson conjectures", "Relates Chow groups and K-theory to L-functions via regulators.", sources=[CONJ])
    m("algebraic_k_theory", "Bloch-Kato conjecture", "Milnor K-theory modulo a prime equals étale cohomology (partially proved by Voevodsky).", sources=[CONJ], status="partially_solved")
    m("number_theory", "Bateman-Horn conjecture", "Predicts the density of simultaneously prime values of polynomials.", sources=[CONJ])
    m("number_theory", "Waring's conjecture (refined)", "Determine g(k) and G(k) exactly for all k in Waring's problem.", sources=[CONJ])

    # ── Missing Wikipedia math problems (from second crawl) ──────────
    m("complex_analysis", "Goodman's conjecture", "Coefficients of multivalued functions satisfy specific inequalities.", sources=[WIKI])
    m("numerical_analysis", "Kung-Traub conjecture", "Optimal order for multipoint iteration without memory is 2^{d-1}.", sources=[WIKI])
    m("complex_analysis", "Mean value problem", "Every polynomial of degree n has a critical point within distance 1 of a given root.", sources=[WIKI])
    m("analysis", "Pompeiu problem", "If a body has vanishing integral over all rigid motions, must it be a ball?", sources=[WIKI])
    m("complex_analysis", "Vitushkin's conjecture", "Compact sets of finite 1-dim Hausdorff measure have zero analytic capacity iff they are purely unrectifiable.", sources=[WIKI])
    m("complex_analysis", "Landau's constants", "Determine the exact values of the Bloch and Landau constants.", sources=[WIKI])
    m("pde", "Vlasov-Maxwell regularity", "Do smooth solutions exist globally for the Vlasov-Maxwell system?", sources=[WIKI])
    m("combinatorics", "Dittert conjecture", "The permanent function maximum on doubly stochastic matrices under a constraint.", sources=[WIKI])
    m("combinatorics", "Latin squares problems", "Various open questions about existence and properties of Latin squares.", sources=[WIKI])
    m("combinatorics", "Map folding", "How many ways can a strip of stamps be folded?", sources=[WIKI])
    m("combinatorics", "Dedekind numbers", "Compute M(n) for n >= 10 — counting antichains of the Boolean lattice.", sources=[WIKI])
    m("combinatorics", "Van der Waerden numbers", "Determine exact values of Van der Waerden numbers W(r,k).", sources=[WIKI])
    m("combinatorics", "Self-avoiding walks", "Determine the connective constant and scaling limit of self-avoiding walks.", sources=[WIKI])
    m("dynamical_systems", "Arnold-Givental conjecture", "Lower bound on fixed points of certain Hamiltonian diffeomorphisms from Morse theory.", sources=[WIKI])
    m("dynamical_systems", "Arnold conjecture", "Every Hamiltonian symplectomorphism has at least as many fixed points as a function on M has critical points.", sources=[WIKI])
    m("quantum_mechanics", "Berry-Tabor conjecture", "Quantum energy levels of classically integrable systems have Poisson statistics.", sources=[WIKI])
    m("ergodic_theory", "Banach's problem", "Does there exist an ergodic system with simple Lebesgue spectrum?", sources=[WIKI])
    m("chaos_theory", "Eden's conjecture", "The supremum of local Lyapunov dimensions is achieved on critical orbits.", sources=[WIKI])
    m("dynamical_systems", "Fatou conjecture", "Hyperbolic maps are dense in the quadratic family.", sources=[WIKI])
    m("chaos_theory", "Kaplan-Yorke conjecture", "Attractor dimension equals the Kaplan-Yorke dimension from Lyapunov exponents.", sources=[WIKI])
    m("ergodic_theory", "Margulis conjecture", "Classify measures invariant under higher-rank diagonalizable actions.", sources=[WIKI])
    m("dynamical_systems", "Hilbert-Arnold problem", "Uniform bound on limit cycles for polynomial vector fields in finite-parameter families.", sources=[WIKI])
    m("quantum_chaos", "Quantum unique ergodicity", "Eigenfunctions of the Laplacian on negatively curved manifolds equidistribute.", sources=[WIKI])
    m("ergodic_theory", "Rokhlin's multiple mixing problem", "Does strong mixing imply mixing of all orders?", sources=[WIKI])
    m("symplectic_geometry", "Weinstein conjecture", "Every compact contact-type hypersurface carries a periodic Reeb orbit.", sources=[WIKI])
    m("dynamical_systems", "Juggler sequence conjecture", "Every positive integer eventually reaches 1 under the juggler map.", sources=[WIKI])

    # Covering/Packing not yet in catalog
    m("discrete_geometry", "Covering problem of Rado", "Maximum area of a disjoint subset of unit-area axis-parallel squares.", sources=[WIKI])
    m("discrete_geometry", "Erdős-Oler conjecture", "Circle packing in equilateral triangles for triangular numbers.", sources=[WIKI])
    m("discrete_geometry", "Disk covering problem", "Smallest radius r(n) so n disks cover the unit disk.", sources=[WIKI])
    m("discrete_geometry", "Reinhardt's conjecture", "The smoothed octagon has the lowest packing density among centrally symmetric convex shapes.", sources=[WIKI])
    m("discrete_geometry", "Square packing in square", "What is the asymptotic growth of wasted space when packing squares?", sources=[WIKI])
    m("discrete_geometry", "Ulam's packing conjecture", "The round ball is the worst-packing convex solid.", sources=[WIKI])
    m("discrete_geometry", "Tammes problem", "Optimal point arrangements on the sphere for n > 14 (except 24).", sources=[WIKI])

    # Differential geometry not yet in catalog
    m("differential_geometry", "Spherical Bernstein problem", "Are entire minimal graphs on spheres equatorial?", sources=[WIKI])
    m("differential_geometry", "Cartan-Hadamard conjecture", "The isoperimetric inequality extends to Cartan-Hadamard manifolds.", sources=[WIKI])
    m("differential_geometry", "Chern's conjecture (affine)", "Compact affine manifolds have zero Euler characteristic.", sources=[WIKI])
    m("differential_geometry", "Filling area conjecture", "The hemisphere minimizes area among shortcut-free surfaces bounding a circle.", sources=[WIKI])
    m("spectral_geometry", "Yau's conjecture on first eigenvalue", "First eigenvalue of minimal hypersurface in S^{n+1} equals n.", sources=[WIKI])
    m("differential_geometry", "Osserman conjecture", "Osserman manifolds are flat or locally rank-one symmetric.", sources=[WIKI])

    # Discrete geometry
    m("discrete_geometry", "Big-line-big-clique conjecture", "Large enough point sets contain many collinear or many mutually visible points.", sources=[WIKI])
    m("discrete_geometry", "Hadwiger covering conjecture", "Every n-dim convex body can be covered by 2^n smaller homothetic copies.", sources=[WIKI])
    m("discrete_geometry", "Happy ending problem", "Determine f(n): points in general position guaranteeing a convex n-gon.", sources=[WIKI])
    m("discrete_geometry", "Heilbronn triangle problem", "Bounds on the minimum area triangle from n points in the unit square.", sources=[WIKI])
    m("discrete_geometry", "Kalai's 3^d conjecture", "Every centrally symmetric d-polytope has at least 3^d faces.", sources=[WIKI])
    m("discrete_geometry", "Kobon triangle problem", "Maximum triangles formed by n lines with no three concurrent.", sources=[WIKI])
    m("discrete_geometry", "McMullen problem", "Can any n+3 points in general position in R^d be projected to convex position?", sources=[WIKI])

    # Euclidean geometry
    m("geometry", "Bellman's lost-in-a-forest problem", "Shortest curve that reaches the boundary from any unknown interior point.", sources=[WIKI])
    m("geometry", "Lebesgue's universal covering problem", "Minimum-area convex set covering all planar sets of diameter 1.", sources=[WIKI])
    m("geometry", "Mahler's conjecture", "The volume product of a centrally symmetric convex body is minimized by the cube.", sources=[WIKI])
    m("geometry", "Moser's worm problem", "Smallest-area convex set covering all unit-length curves.", sources=[WIKI])
    m("polyhedral_geometry", "Dürer's conjecture", "Every convex polyhedron has a non-overlapping edge unfolding.", sources=[WIKI])
    m("polyhedral_geometry", "Rupert's property generalization", "Every convex polyhedron has Rupert's property (a larger copy fits through a hole in it).", sources=[WIKI])
    m("fractal_geometry", "Falconer's conjecture", "Sets of Hausdorff dimension > d/2 in R^d have positive-measure distance sets.", sources=[WIKI])
    m("geometry", "Kelvin problem", "Is the Weaire-Phelan structure the optimal equal-volume foam?", sources=[WIKI])

    # Graph theory expansions
    m("graph_theory", "Vizing's conjecture", "The domination number of the Cartesian product >= the product of domination numbers.", sources=[WIKI])
    m("graph_theory", "Hadwiger conjecture (graph theory)", "Every graph with no K_t minor is (t-1)-colorable.", sources=[WIKI])
    m("graph_theory", "Cycle double cover conjecture", "Every bridgeless graph has a cycle double cover.", sources=[CONJ])
    m("graph_theory", "Seymour's second neighborhood conjecture", "Every orientation has a vertex whose second neighborhood is at least as large as its first.", sources=[CONJ])

    # Number theory expansions
    m("number_theory", "Landau's fourth problem", "Are there infinitely many primes of the form n^2 + 1?", sources=[WIKI], tags=["landau"], year_posed=1912, posed_by="Edmund Landau")
    m("number_theory", "Artin's conjecture on L-functions", "Artin L-functions for non-trivial irreducible representations are entire.", sources=[CONJ])

    # Probability theory
    m("probability_theory", "Schramm's conformally invariant scaling limits", "Rigorous scaling limits of critical lattice models in 2D.", sources=[WIKI])

    return qs


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    existing = load_existing()
    existing_titles = get_existing_titles(existing)
    start_num = next_id(existing)
    counter = [start_num]

    new = new_questions(counter)

    # Deduplicate
    added = []
    skipped = 0
    for nq in new:
        nt = normalize_title(nq["title"])
        if nt in existing_titles:
            skipped += 1
            continue
        existing_titles.add(nt)
        added.append(nq)

    all_questions = existing + added

    # Write
    with open(MATH_JSONL, "w", encoding="utf-8") as f:
        for entry in all_questions:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"  Existing: {len(existing)}")
    print(f"  New candidates: {len(new)}")
    print(f"  Skipped (duplicate): {skipped}")
    print(f"  Added: {len(added)}")
    print(f"  Total: {len(all_questions)}")


if __name__ == "__main__":
    main()
