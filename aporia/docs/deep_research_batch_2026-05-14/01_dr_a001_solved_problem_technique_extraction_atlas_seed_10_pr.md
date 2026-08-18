# Prompt 01: DR-A001 — Solved-problem technique extraction (Atlas seed, 10 problems) [ATLAS-PILOT]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZbjhGYXRQTEZQdUktc0FQaks3MTJRbxIXWW44RmF0UExGUHVJLXNBUGpLNzEyUW8
**Elapsed:** 636s

---

# PROBLEM-ATLAS PILOT: Solved-Problem Technique Extraction (Layer 5.5 Substrate Architecture)

**Substrate Routing:** Prometheus Layer 5.5 (Meta-Research / Problem Atlas)
**Execution Mode:** Substrate Input / Catalog Registration
**Target:** Extraction of mathematical technique-to-hardness mappings for 10 definitive mathematical breakthroughs (2010–2025).

This report executes the Problem-Atlas Pilot protocol. The objective is to rigorously deconstruct 10 solved mathematical problems, stripping away conventional narrative framing (the "gravity wells" of human mathematical literature) to extract pure, actionable substrate inputs. These inputs take the form of primitive registrations, catalog edits, anti-anchor pins, and work-queue entries. We enforce strict adherence to the HARD-5 distinct coordinates doctrine, ensuring that mathematically distinct invariants are never collapsed into generalized natural language tokens. Every finding is anchored to primary source coordinates, distinguishing explicit temporal milestones between preprint dissemination and peer-reviewed finality.

The analysis is structured to feed directly into the Prometheus substrate, treating mathematical literature not as a collection of human achievements, but as an optimization landscape of barrier-crossings. 

---

## 1. Sensitivity Conjecture 

### Mathematical Coordinates
*   **Sensitivity $s(f)$**: The maximum over all $x \in \{0,1\}^n$ of the number of indices $i$ such that flipping the $i$-th bit changes the value of $f(x)$.
*   **Block Sensitivity $bs(f)$**: The maximum number of disjoint subsets of indices such that flipping the bits in any subset changes the value of $f$.
*   **Boolean Degree $\deg(f)$**: The degree of the unique multilinear real polynomial representing $f$.
*   **Subgraph Max Degree $\Delta(H)$**: The maximum vertex degree of an induced subgraph $H \subset Q_n$.
*   **Largest Eigenvalue $\lambda_1(H)$**: The spectral radius of the adjacency matrix of $H$.
*   *(HARD-5 Enforcement)*: $s(f)$, $bs(f)$, $\deg(f)$, $\Delta(H)$, and $\lambda_1(H)$ are FIVE distinct coordinates. The Gotsman-Linial equivalence maps boolean function sensitivity to hypercube subgraph max degree $\Gamma(H) = \max(\Delta(H), \Delta(Q_n - H))$. They must not be collapsed into "complexity measures."

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Spectral graph theory via sign-flipped adjacency matrices / Clifford algebra representations.** 
The proof relies on constructing a $2^n \times 2^n$ symmetric signed adjacency matrix $A_n$ for the hypercube $Q_n$ such that $A_n^2 = nI$. By applying Cauchy's eigenvalue interlacing theorem to this carefully constructed matrix, it strictly bounds the largest eigenvalue (and thus the maximum degree) of any induced subgraph $H$ of size $2^{n-1}+1$ to be at least $\sqrt{n}$ [cite: 1, 2]. 

**Anti-Gravitational-Well:** The mathematical literature heavily exhibits a gravity well around Hao Huang's "magic matrix" construction. We explicitly surface and weight HIGHER the alternative formulation by Daniel Mathews [cite: 3], which demonstrates that this matrix construction is a natural manifestation of **Clifford algebras of positive definite signature**. Roman Karasev [cite: 3] also related these matrices to exterior algebras (Clifford algebras with a zero quadratic form). Furthermore, the $q$-analogue generalization by Tao and Karasev (replacing hypercubes with powers of $l$-cycles) demonstrates that the substrate should register this not as an isolated matrix trick, but as a systematic application of Clifford algebra representations to subgraph eigenvalue bounding [cite: 2, 4].

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**REPRESENTATION_GAP (Primary) / CONCEPTUAL_ABSENCE (Secondary)**. 
The problem stalled because researchers attempted to bound boolean complexity measures directly using Fourier analysis or decision tree logic. The Gotsman-Linial equivalence (1992) translated the problem into graph theory, but bounding $\Delta(H)$ lacked the necessary algebraic geometry. The representation gap was crossed when the problem was mapped into the spectral domain using a non-standard signed adjacency matrix where $A_n^2 = nI$.

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Repurposed:** Cauchy interlacing theorem. 
**Substantially Repurposed / Newly Applied:** The use of a specifically constructed signed adjacency matrix (or its formal equivalent, positive-definite Clifford algebras [cite: 3]) to artificially force the eigenvalues of the hypercube into $\sqrt{n}$ and $-\sqrt{n}$, each with multiplicity $2^{n-1}$. This exact spectral distribution is what allows the interlacing theorem to output the tight lower bound for $2^{n-1}+1$ vertex subgraphs [cite: 2].

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Hao Huang. "Induced subgraphs of hypercubes and a proof of the Sensitivity Conjecture". *Annals of Mathematics* 190(3), pp. 949-955. Published: **October 28, 2019** [cite: 5, 6].
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** Hao Huang. arXiv:1907.00847v1 [math.CO]. **July 1, 2019** [cite: 7].

### (e) PRECURSOR DEPENDENCIES
1.  **Gotsman-Linial equivalence (1992):** Established the direct equivalence between $s(f)$ bounds and the maximum degree of induced subgraphs of $Q_n$ [cite: 8].
2.  **Chung-Füredi-Graham-Seymour lower bound (1988):** Proved $\Delta(H) \ge (\frac{1}{2} - o(1))\log_2 n$ and constructed the exact tight subgraph configuration proving $\lceil \sqrt{n} \rceil$ was the theoretical ceiling [cite: 1, 8].
3.  **Cauchy Eigenvalue Interlacing Theorem:** The foundational spectral tool required to execute the final bounding step [cite: 9].

### (f) BEHAVIOR DELTA
**Primitive Registration:** Register `positive_definite_clifford_algebra_mapping` as a primary algebraic transformation primitive for bounding subgraph eigenvalues. 
**Anti-Anchor Pin:** Pin the substrate against attempting brute-force combinatorial search on boolean function decision trees when exploring block sensitivity; force automatic translation through the Gotsman-Linial spectral pipeline.

---

## 2. Bounded Gaps Between Primes 

### Mathematical Coordinates
*   **Unconditional Gap Limit $\Delta_1$**: $\liminf_{n \to \infty} (p_{n+1}-p_n) \le C_U$ unconditionally.
*   **Conditional Gap Limit $\Delta_{EH}$**: $\liminf_{n \to \infty} (p_{n+1}-p_n) \le C_C$ conditional on Elliott-Halberstam (EH) or Generalized Elliott-Halberstam (GEH).
*   **Bounded Gap Sequence Set $H$**: The specific $k$-tuple admissible set used in the sieve.
*   **Distribution parameter $\theta$**: The level of distribution of primes in arithmetic progressions.
*   *(HARD-5 Enforcement)*: The generalized gap $\liminf_{n \to \infty} (p_{n+m}-p_n) \le C_m$ is distinct from $\Delta_1$. The unconditional bound ($C_U = 246$ via Polymath8) and the conditional bound ($C_C = 6$ via GEH) must be rigidly separated in the substrate [cite: 10, 11].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Multi-dimensional Selberg sieve with smoothed weights coupled with optimized Bombieri-Vinogradov theorem variants.**
Zhang closed the gap by proving a weakened variant of the Elliott-Halberstam conjecture, extending the level of distribution of primes in arithmetic progressions beyond the $1/2$ barrier (specifically to $1/2 + \varpi$) for smooth moduli [cite: 11]. Maynard independently closed the gap by replacing the 1-dimensional Goldston-Pintz-Yıldırım (GPY) sieve weights with symmetric multi-dimensional sieve weights, drastically reducing the required level of distribution $\theta$ to below $1/2$ (thus requiring no new results on primes in arithmetic progressions) [cite: 11, 12].

**Anti-Gravitational-Well:** The literature frequently collapses this into "The Maynard-Tao method" or simply "Zhang's breakthrough". We must separate these. Furthermore, the gravity well frames this strictly as a victory of analytic number theory. We weight equally the **calculus of variations formulation** used by Polymath8 [cite: 13]. Polymath8b reduced the problem of optimizing the sieve weights to a purely numerical optimization of a multi-dimensional integral (a variational calculus problem), combined with Tao's $\epsilon$-trick for enlarging the sieve support beyond the standard simplex [cite: 11, 13].

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**METHOD_GAP (Primary) / COUPLED_DIFFICULTY (Secondary)**.
The parity barrier in sieve theory represented a hard METHOD_GAP; classical sieves could not distinguish integers with an even number of prime factors from those with an odd number. The GPY method almost worked but required an unproven distribution level $\theta > 1/2$. The COUPLED_DIFFICULTY was the fusion of optimizing sieve weights and bounding error terms in prime distributions. Zhang attacked the error terms; Maynard attacked the sieve weights [cite: 11].

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** Multi-dimensional sieve weights (Maynard) replacing the rigid 1D GPY weights [cite: 11, 12]. Flexible error terms in Elliott-Halberstam type estimates allowing smooth moduli (Zhang).
**Repurposed:** The Goldston-Pintz-Yıldırım (GPY) sieve framework; the Bombieri-Vinogradov theorem.

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED (Zhang):** Yitang Zhang. "Bounded gaps between primes". *Annals of Mathematics* 179(3), pp. 1121-1174. Published: **May 2014** (Accepted early May 2013) [cite: 10].
*   **PEER-REVIEWED (Maynard):** James Maynard. "Small gaps between primes". *Annals of Mathematics* 181(1), pp. 383-413. Published: **2015** (Announced November 19, 2013) [cite: 12, 14].

### (e) PRECURSOR DEPENDENCIES
1.  **Goldston-Pintz-Yıldırım (GPY) sieve (2005):** Established that bounded gaps follow from the Elliott-Halberstam conjecture [cite: 11].
2.  **Bombieri-Vinogradov theorem:** The foundational theorem for the distribution of primes in arithmetic progressions, giving a distribution level of $\theta = 1/2$.
3.  **Bombieri, Fouvry, Friedlander, and Iwaniec works:** Variants of Elliott-Halberstam bounding error terms for primes in arithmetic progressions [cite: 13].

### (f) BEHAVIOR DELTA
**Catalog Edit:** Split the substrate representation of "Selberg Sieve" into `1D_GPY_Weights` and `Multi_Dimensional_Maynard_Tao_Weights` as distinct functional optimization spaces.
**Work-Queue Entry:** Route all existing parity-barrier constrained sieve problems through the Polymath8b variational calculus optimizer to check if multidimensional weight relaxation crosses the exactness threshold.

---

## 3. Erdős Discrepancy Problem 

### Mathematical Coordinates
*   **Discrepancy $D(N)$**: $\sup_{n, d \in \mathbb{N}} |\sum_{j=1}^n f(jd)|$ for a sequence $f: \mathbb{N} \to \{-1, +1\}$.
*   **Logarithmic Averaged Correlation**: $\lim_{x \to \infty} \frac{1}{\log x} \sum_{n \le x} \frac{f(n)f(n+h)}{n}$.
*   **Hilbert Space Norm Discrepancy**: $\| \sum_{j=1}^n f(jd) \|_H$ for sequences taking values in the unit sphere of a real or complex Hilbert space.
*   *(HARD-5 Enforcement)*: The classical scalar discrepancy $D(N)$ must remain strictly separate from the vector-valued Hilbert space discrepancy corollary. Partial sums $\sum_{j=1}^n f(jd)$ must not be collapsed mathematically with the logarithmically averaged correlation limits [cite: 15, 16, 17].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Logarithmically averaged nonasymptotic Elliott conjecture applied to completely multiplicative functions, combined with a Fourier-analytic reduction.**
Tao reduced the general sequence problem to completely multiplicative functions (where $f(ab) = f(a)f(b)$) via a Fourier-analytic argument from the Polymath5 project. He then applied his newly established logarithmically averaged nonasymptotic Elliott conjecture to prove that any multiplicative counterexample would have to pretend to be a Dirichlet character. Finally, he demonstrated that functions resembling Dirichlet characters must exhibit at least logarithmic growth on average in their partial sums, breaking the bounded discrepancy assumption [cite: 15, 16, 17].

**Anti-Gravitational-Well:** The narrative focuses purely on Tao's analytic masterclass. The substrate must equally weight the **SAT solver abstraction** by Boris Konev and Alexei Lisitsa (2014) [cite: 15]. Konev and Lisitsa translated the problem for $C=2$ into a Boolean satisfiability problem, proving that any sequence of length 1161 must have discrepancy $>2$. 

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**GLOBAL_OBSTRUCTION (Primary) / EXACTNESS_BARRIER (Secondary)**.
The sequence $f(n)$ could be locally constructed to avoid high discrepancy (e.g., alternating steps), but the global restriction of checking all homogeneous arithmetic progressions $\{d, 2d, 3d, \dots, nd\}$ forces a global obstruction. Bounding the correlations of successive values of multiplicative functions faced an exactness barrier until the Matomäki-Radziwiłł breakthrough [cite: 16, 17].

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** The logarithmically averaged nonasymptotic Elliott conjecture, effectively showing that the Chowla conjecture is a special case of the Elliott conjecture under logarithmic averaging [cite: 16, 18].
**Repurposed:** Polymath5 Fourier-analytic reduction (reducing general sequences to stochastic completely multiplicative functions) [cite: 15, 17]. The Matomäki-Radziwiłł theorems on correlations of multiplicative functions in short intervals.

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Terence Tao. "The Erdős discrepancy problem". *Discrete Analysis* 2016:1, 27 pp. Published: **February 28, 2016** [cite: 16, 17].
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** Terence Tao. arXiv:1509.05363v1. **September 17, 2015** [cite: 17, 19].

### (e) PRECURSOR DEPENDENCIES
1.  **Matomäki-Radziwiłł theorem (2015):** Established bounds on correlations of successive values of multiplicative functions [cite: 16].
2.  **Polymath5 Project (2010):** Provided the crucial Fourier-analytic reduction step to isolate completely multiplicative functions [cite: 15, 17].
3.  **Borwein-Choi-Coons analysis:** Earlier heuristic/analytic framework used to rule out specific "pretentious" multiplicative behaviors [cite: 18].

### (f) BEHAVIOR DELTA
**Primitive Registration:** Register `logarithmic_averaging` as a primary symmetry-breaking operator for nonasymptotic multiplicative functions.
**Anti-Anchor Pin:** Anchor the substrate against attempting to calculate discrepancy bounds exclusively via strict asymptotic limits; route sequence bound problems through logarithmic averaging pipelines to extract pretend-character behaviors.

---

## 4. Cap Set Problem 

### Mathematical Coordinates
*   **Three-term Progression-Free Bound $r_3(\mathbb{Z}_3^n)$**: The maximal size of a subset of $\mathbb{F}_3^n$ with no three-term arithmetic progressions.
*   **Four-term Group Bound $r_3(\mathbb{Z}_4^n)$**: The analogous bound for the group $\mathbb{Z}_4^n$ (where Croot-Lev-Pach established $|A| \le 4^{\gamma n}$ with $\gamma \approx 0.926$).
*   **Monomial Dimension $m_d$**: The number of monomials in $x_1, \dots, x_n$ with total degree $\le d$ and individual variable degree $\le q-1$.
*   **Evaluation Matrix Rank $\text{rk}(P)$**: The algebraic rank of the $F_q$-matrix $B_{x,y} = P(x-y)$.
*   *(HARD-5 Enforcement)*: The cyclic group problem $r_3(\mathbb{Z}/N\mathbb{Z})$ is fundamentally distinct from the vector space problem $r_3(\mathbb{F}_p^n)$. The substrate must distinctly index Croot-Lev-Pach bounds ($\mathbb{Z}_4^n$) [cite: 20] separately from Ellenberg-Gijswijt bounds ($\mathbb{F}_p^n$) [cite: 21].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Polynomial method via dimension bounding of bounded-degree polynomial spaces and evaluation-matrix rank tracking.**
Croot, Lev, and Pach (CLP) developed a lemma bounding the size of a progression-free subset $A$ by expressing the condition as the vanishing of a polynomial $P(x,y,z)$ on $A \times A \times A$. By evaluating the rank of the matrix $B_{x,y} = P(x-y)$, they showed the rank is strictly bounded by the number of monomials of degree $\le d$. Ellenberg and Gijswijt applied this directly to $\mathbb{F}_q^n$, proving that the size of $A$ is bounded by $c^n$ for some $c < q$ (specifically $c \approx 2.756$ for $q=3$) [cite: 21, 22].

**Anti-Gravitational-Well:** The traditional polynomial method literature treats this as an ad-hoc trick. The substrate must weight equally Terry Tao's **symmetric formulation**, which recasts the CLP lemma symmetrically. Furthermore, we mandate surfacing the **Lean formalization abstraction** (Eberl, Dahmen, Hölzl, Lewis 2019) [cite: 23, 24]. The formalized proof translates the matrix rank argument into pure type-theoretic vector space constraints, which is mathematically distinct from the polynomial evaluation formulation and much more native to an AI research substrate.

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**REPRESENTATION_GAP (Primary)**.
For over a decade, additive combinatorics attempted to solve the affine cap problem using Fourier analysis (the Roth-Meshulam theorem and the Bateman-Katz bounds), which failed to break the $O(3^n/n^{1+\epsilon})$ barrier [cite: 21]. The representation gap was viewing the set as a frequency domain problem rather than viewing the set as the zero-locus of polynomials with bounded variables/degrees.

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** The Croot-Lev-Pach (CLP) polynomial lemma bounding the size of progression-free sets via the rank of evaluation matrices over finite fields [cite: 20, 21].
**Repurposed:** The polynomial method (historically used by Dvir for the finite field Kakeya problem), drastically simplified and repurposed without relying on Schwartz-Zippel derivations.

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED (Ellenberg-Gijswijt):** Jordan S. Ellenberg, Dion Gijswijt. "On large subsets of $\mathbb{F}_q^n$ with no three-term arithmetic progression". *Annals of Mathematics* 185(1), pp. 339-343. Published: **December 2, 2016** (Received May 31, 2016) [cite: 21, 22].
*   **PEER-REVIEWED (Croot-Lev-Pach):** Ernie Croot, Vsevolod F. Lev, Péter Pál Pach. "Progression-free sets in $\mathbb{Z}_4^n$ are exponentially small". *Annals of Mathematics* 185(1), pp. 331-337. Published: **December 2, 2016** [cite: 20, 25].

### (e) PRECURSOR DEPENDENCIES
1.  **Meshulam's bound (1995):** Improved Brown-Buhler's $o(3^n)$ to $O(3^n/n)$ via Fourier analysis [cite: 21].
2.  **Bateman-Katz bound (2012):** The absolute limit of Fourier techniques, yielding $O(3^n/n^{1+\epsilon})$ [cite: 21].
3.  **Dvir's Finite Field Kakeya Proof (2008):** The foundational inspiration for applying the polynomial method to combinatorial geometry over finite fields.

### (f) BEHAVIOR DELTA
**Work-Queue Entry:** Execute a system-wide scan of all unresolved additive combinatorics boundaries (e.g., $r_k(\mathbb{Z}/N\mathbb{Z})$) to test for representation-gap vulnerability via finite-field evaluation-matrix rank substitution. 
**Catalog Edit:** Register `CLP_Evaluation_Matrix_Rank` as a fundamental invariant for bounding subset sizes over abelian groups.

---

## 5. Kadison-Singer Problem 

### Mathematical Coordinates
*   **Operator Norm $\| \sum v_i v_i^* \|$**: The norm of the sum of rank-1 positive semidefinite Hermitian matrices.
*   **Expected Characteristic Polynomial Roots $\mu_i$**: The largest roots of the expected polynomials of a random matrix distribution.
*   **Paving Bounds**: The explicit bounds generated for Anderson's paving conjecture matrix diagonals.
*   *(HARD-5 Enforcement)*: The matrix operator norm $\|M\|_2$ must not be mathematically conflated with the maximum root of the expected characteristic polynomial. The substrate must strictly separate probabilistic bounds (Matrix Chernoff high-probability bounds with logarithmic loss) from the exact combinatorial deterministic bounds derived via interlacing families [cite: 9, 26].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Method of interlacing polynomials and multivariate real stable polynomials bounded by a barrier function argument.**
Marcus, Spielman, and Srivastava proved that the expected characteristic polynomials of sums of independent rank-1 positive semidefinite Hermitian matrices are real-rooted. They did this by generating multivariate real stable polynomials and applying stability-preserving operators. By showing these characteristic polynomials form an "interlacing family," they proved there exists at least one polynomial in the family whose largest root is bounded strictly by the largest root of the expected characteristic polynomial. The maximum root is explicitly bounded using a multivariate generalization of a barrier function argument [cite: 9, 26, 27].

**Anti-Gravitational-Well:** The literature gravitates towards treating this as a pure graph-theoretic/Ramanujan graph victory. The substrate must surface the **Free Probability Theory perspective**. While free probability yields the correct asymptotic intuition for the sum of random matrices, it fails to provide the exact bounds for finite matrices. The substrate must weight the distinction: Free Probability provides the *guess*, Interlacing Families provide the *exact rigorous bound*.

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**EXACTNESS_BARRIER (Primary) / REPRESENTATION_GAP (Secondary)**.
Standard random matrix tools (like Matrix Chernoff bounds) yield bounds with high probability but incur a logarithmic loss factor [cite: 26]. The Kadison-Singer problem (via Anderson's Paving Conjecture) required an *exact* worst-case bound without the log factor. The representation gap was translating an operator algebra problem $\left(\mathcal{B}(\mathcal{H})\right)$ into a problem about bounding the largest roots of expected univariate polynomials.

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** Mixed characteristic polynomials; the method of interlacing families of polynomials.
**Repurposed:** Borcea and Brändén's multivariate real stable polynomials [cite: 9]; barrier function arguments (originally developed by Batson, Spielman, and Srivastava for spectral sparsification) [cite: 9].

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Adam W. Marcus, Daniel A. Spielman, Nikhil Srivastava. "Interlacing families II: Mixed characteristic polynomials and the Kadison-Singer problem". *Annals of Mathematics* 182(1), pp. 327-350. Published: **July 30, 2014** (Issue dated 2015) [cite: 9, 28].
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** arXiv preprint (v1) announced around **June 2013** [cite: 29].

### (e) PRECURSOR DEPENDENCIES
1.  **Anderson's Paving Conjecture / Weaver's $KS_2$ Conjecture (1990s):** The discrete finite-dimensional equivalences of the infinite-dimensional Kadison-Singer operator algebra problem [cite: 9, 27].
2.  **Borcea and Brändén's theorems (2008):** Characterized operators that preserve the real stability of multivariate polynomials [cite: 9].
3.  **Batson-Spielman-Srivastava Barrier Functions (2009):** The bounding mechanism controlling the shift of roots under the differential operator $1 - \partial_x$ [cite: 9].

### (f) BEHAVIOR DELTA
**Training-Corpus Filter:** Apply a heuristic filter ensuring that expected characteristic polynomials of random matrices are mapped directly to `exact_maximum_root_bounding` protocols (Interlacing) rather than strictly routing to probabilistic concentration inequalities (Chernoff/Hoeffding).

---

## 6. Willmore Conjecture 

### Mathematical Coordinates
*   **Willmore Energy $W(M)$**: $\int_M H^2 dA$, the integral of the square of the mean curvature $H$ over a surface $M$ immersed in $\mathbb{R}^3$.
*   **Gauss Curvature $K$**: A separate topological invariant dictated by Gauss-Bonnet.
*   **Min-Max Width $L(\Pi)$**: The area of the min-max minimal surface associated with a homotopy class $\Pi$.
*   **$p$-widths**: The volume spectrum derived from min-max theory.
*   *(HARD-5 Enforcement)*: The classic Willmore energy $W(M)$ must be isolated from the multi-parameter min-max width $L(\Pi)$ and the $p$-widths of the surface. Furthermore, the embedded Willmore energy ($\ge 2\pi^2$) is mathematically strictly distinct from the immersed-but-not-embedded energy ($\ge 8\pi$). Do not collapse these [cite: 30, 31, 32].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Almgren-Pitts min-max theory of minimal surfaces applied to multi-parameter families.**
Marques and Neves proved the conjecture by transforming it into a problem of bounding the area of a minimal surface in the unit sphere $S^3$. Using the conformal invariance of the Willmore energy, they applied an advanced, multi-parameter version of the Almgren-Pitts min-max theory. They constructed a specific 5-parameter family of surfaces associated with the homotopy class of the torus, proving that the min-max width $L(\Pi)$ of this family corresponds precisely to the Clifford torus, which has a Willmore energy of $2\pi^2$ [cite: 30, 32, 33].

**Anti-Gravitational-Well:** The literature treats Marques-Neves strictly as an endpoint to Willmore. We must highlight the **Li-Yau conformal volume** formulation (1982) [cite: 32] as an equally critical alternative abstraction. The substrate must register that the min-max theory utilized here birthed the broader study of **$p$-widths** (Chodosh-Mantoulidis), which solves Yau's conjecture on minimal surfaces. The $p$-width abstraction is the true generalizable payload [cite: 31].

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**GLOBAL_OBSTRUCTION (Primary) / NON_HEREDITARY_STRUCTURE (Secondary)**.
The Willmore energy is a global conformal invariant. Local minimization flows (like Willmore flow) get stuck in local minima and fail to prove the global $2\pi^2$ bound for all possible topologies. Simplifications to symmetric surfaces (like tori of revolution, solved by Langer & Singer [cite: 32]) destroy the non-hereditary global geometric pathologies present in arbitrary embeddings.

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Repurposed:** Almgren-Pitts min-max theory of minimal surfaces. Originally developed for 1-parameter families (to prove the existence of at least one minimal surface), Marques and Neves repurposed and scaled the machinery to handle highly complex multi-parameter (5-dimensional) continuous families of surfaces.

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Fernando C. Marques, André Neves. "Min-Max theory and the Willmore conjecture". *Annals of Mathematics* 179(2), pp. 683-782. Published: **March 1, 2014** (Accepted December 2012) [cite: 32, 33, 34].
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** arXiv:1202.6036v1. **February 27, 2012** [cite: 32, 34].

### (e) PRECURSOR DEPENDENCIES
1.  **Almgren-Pitts Min-Max Theory (1980s):** The geometric measure theory framework for proving the existence of minimal surfaces via min-max procedures.
2.  **Li-Yau Conformal Volume (1982):** Established the link between conformal invariants and the first eigenvalue of compact surfaces [cite: 32].
3.  **Langer & Singer (1984) / Willmore tube cases:** Solved the bounded localized geometries, framing the exact Clifford Torus boundary [cite: 32].

### (f) BEHAVIOR DELTA
**Catalog Edit:** Add `p_widths` to the substrate registry as a distinct spectrum of geometric invariants alongside Willmore energy and Conformal volume. Route global geometric optimization problems through high-parameter Almgren-Pitts min-max flows.

---

## 7. Virtual Haken Conjecture 

### Mathematical Coordinates
*   **Fundamental Group $\pi_1(M)$**: The infinite fundamental group of the 3-manifold.
*   **CAT(0) Cube Complex**: The non-positively curved geometric space the group acts upon.
*   **Quasi-convex Subgroup Index**: The index of the separable subgroups within $\pi_1(M)$.
*   *(HARD-5 Enforcement)*: A "cubulated hyperbolic group" is a strict mathematical coordinate and must not be collapsed into a general "word-hyperbolic group" or a generic "Haken manifold." The distinction between *Haken* (contains a 2-sided incompressible surface) and *virtually Haken* (possesses a finite-sheeted cover that is Haken) must remain absolute [cite: 35, 36, 37].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Group actions on CAT(0) cube complexes via Virtual Gluing and the Malnormal Special Quotient Theorem.**
Agol proved that every cubulated hyperbolic group is virtually special. He achieved this by establishing a "Virtual Gluing Theorem," which allows locally convex acylindrical subcomplexes of a virtually special cube complex (which may only match up to finite index) to be glued together exactly via an isometry after passing to a finite cover. This leveraged Wise's Malnormal Special Quotient Theorem to show that hyperbolic 3-manifolds, once cubulated, possess finite-sheeted covers that satisfy the Haken condition [cite: 36, 37].

**Anti-Gravitational-Well:** The gravity well attributes the entire topological victory to Agol. The anti-gravitational requirement is to surface and weight equally **Daniel Wise's hierarchy of virtually special cube complexes** and the **Kahn-Markovic surface subgroup theorem** [cite: 36]. Without Kahn-Markovic proving that every closed hyperbolic 3-manifold contains an immersed nearly-geodesic surface (allowing cubulation), Agol's algebraic geometric group theory has no input. 

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**REPRESENTATION_GAP (Primary)**.
For decades, geometric topology attempted to solve the Virtual Haken conjecture using pure 3-manifold topology (Dehn surgery, foliation theory). The breakthrough required bridging a massive representation gap: translating the topological problem into geometric group theory. By forcing the fundamental group to act on CAT(0) cube complexes, the topological barriers were bypassed using algebraic subgroup separability [cite: 36, 37].

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** The Virtual Gluing Theorem for locally convex acylindrical subcomplexes within CAT(0) cube complexes [cite: 37].
**Repurposed:** Wise's Malnormal Special Quotient Theorem; Kahn-Markovic surface subgroup immersions.

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Ian Agol (with an appendix by Ian Agol, Daniel Groves, and Jason Manning). "The virtual Haken conjecture". *Documenta Mathematica* 18, pp. 1045-1087. Published: **July 14, 2013** [cite: 35, 36, 37].
*   **ANNOUNCED-NOT-PUBLISHED:** Agol announced the proof in a seminar at the Institut Henri Poincaré on **March 12, 2012** [cite: 36].

### (e) PRECURSOR DEPENDENCIES
1.  **Kahn-Markovic Surface Subgroup Theorem (2012):** Proved that closed hyperbolic 3-manifolds contain many immersed quasi-Fuchsian surfaces, allowing the manifold to be cubulated [cite: 36].
2.  **Wise's Malnormal Special Quotient Theorem:** Provided the algebraic mechanism to control the hyperplanes of the cube complexes [cite: 36].
3.  **Haglund-Wise Special Cube Complexes (2008):** Defined the required hyperplane embedding conditions (no self-osculating or inter-osculating hyperplanes) [cite: 36, 37].

### (f) BEHAVIOR DELTA
**Primitive Registration:** Register `virtual_gluing_over_CAT(0)_cube_complexes` as a primary topological-to-algebraic translation mechanism. 
**Substrate Input:** Any topological problem requiring the proof of finite-sheeted covers possessing a specific property must automatically pipeline through a Kahn-Markovic style cubulation check.

---

## 8. Schinzel-Zassenhaus Conjecture 

### Mathematical Coordinates
*   **Algebraic Integer Modulus $\max |\alpha_i|$**: The absolute value of the largest conjugate of an algebraic integer $\alpha$.
*   **Mahler Measure $M(\alpha)$**: $\prod_{i=1}^n \max(1, |\alpha_i|)$.
*   **Transfinite Diameter / Logarithmic Capacity**: The capacity of the compact sets defined on the Riemann surface of the inverse analytic function.
*   *(HARD-5 Enforcement)*: The strict maximum conjugate bound $\max |\alpha_i| \ge 2^{-1/(4n)}$ is a mathematically distinct coordinate from the Mahler Measure bounds $\ge \exp(C/n^3)$ (Matveev) or $\ge \exp(c/n)$ (Dobrowolski). The substrate must not conflate the Schinzel-Zassenhaus root modulus maximum with the Lehmer conjecture's product of all roots outside the unit circle [cite: 38, 39, 40].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Power series expansion of logarithmic capacity bounded via resultants.**
Dimitrov proved the optimal lower bound $\max |\alpha_i| \ge 2^{1/(4n)}$ (often written bounded away by $(\log 2)/(4n)$ for roots outside the unit circle). He achieved this by bridging complex analysis with algebraic number theory. Specifically, he utilized the resultant of the polynomial $P(z)$ and its reciprocal $P(1/z)$. By applying a Pólya-Carlson type theorem related to transfinite diameters and constructing a highly non-trivial asymptotic expansion of the zeros using principal values of the logarithm function, Dimitrov quantified the exact "repulsive force" between roots [cite: 38, 39, 40, 41].

**Anti-Gravitational-Well:** The literature often attempts to tackle Schinzel-Zassenhaus strictly through the lens of Boyd's conjecture and Smyth's inequalities on the Mahler measure. Dimitrov sidestepped the Mahler measure gravity well by utilizing **Cassels' resultant estimate** combined with **transfinite diameters** [cite: 40, 41]. The substrate must weight transfinite diameter formulations equal to Mahler Measure for algebraic unit bounding problems.

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**EXACTNESS_BARRIER (Primary)**.
Previous bounds (e.g., Dubickas, Matveev, Rhin, Wu) successfully established that a repulsive bound existed, yielding bounds proportional to $1/n^2$ or $1/n^3$. The exactness barrier was establishing the optimal asymptotic tightness inversely proportional to $n$ exactly (specifically $c/n$). 

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** A novel unification of Cassels' resultant bounding methodology with complex analytic transfinite diameters to explicitly measure the spatial repulsion of polynomial roots [cite: 39, 40, 41].
**Repurposed:** Pólya-Carlson rational function expansions; Cassels' theorem on resultants.

### (d) PRIMARY SOURCE CITATION
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** Vesselin Dimitrov. "A proof of the Schinzel-Zassenhaus conjecture on polynomials". arXiv:1912.12545v1 [math.NT]. **December 28, 2019** [cite: 38, 42]. *(Note: Dimitrov published related breakthrough work in Annals of Mathematics in 2021 regarding Mordell-Lang [cite: 42], but the Schinzel-Zassenhaus standalone proof remains primarily anchored by this definitive 2019 arXiv preprint which is universally recognized as the closed proof [cite: 39, 43]).*

### (e) PRECURSOR DEPENDENCIES
1.  **Cassels' Resultant Estimates:** A classical idea bounding the resultant of $P(z)$ and $P(1/z)$ [cite: 41].
2.  **Pólya-Carlson Theorem:** Analytic theorem linking power series with integer coefficients to rational functions.
3.  **Dubickas' Asymptotic Bounds (1990s):** Provided the best-known prior asymptotic approximations to the $1/n$ order [cite: 40].

### (f) BEHAVIOR DELTA
**Anti-Anchor Pin:** Decouple Schinzel-Zassenhaus structural reasoning strictly from Lehmer/Mahler measure gradient descents in the substrate.
**Catalog Edit:** Link the `resultant_of_reciprocal_polynomials` node directly to `transfinite_diameter_bounding` as a proven solution pathway for root repulsion exactness barriers.

---

## 9. Duffin-Schaeffer Conjecture 

### Mathematical Coordinates
*   **Approximation Error $\psi(q)/q$**: The bounding target for Diophantine approximation $| \alpha - a/q | \le \psi(q)/q$.
*   **Lebesgue Measure**: The full metric measure of the set of valid real numbers $\alpha$.
*   **GCD Overlap Connectivity $\max_{q_1, q_2} \gcd(q_1, q_2)$**: The network constraint on the overlapping denominators.
*   *(HARD-5 Enforcement)*: The classical 1-dimensional Duffin-Schaeffer scalar fraction bound must not be collapsed with the $k$-dimensional analogue (resolved in 1990 by Vaughan and Pollington) or the Hausdorff measure analogue (resolved in 2006 by Beresnevich and Velani) [cite: 44, 45].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Graph-theoretic compression algorithms over prime-factor GCD graphs.**
The crux of the Duffin-Schaeffer conjecture relies on the converse of the Borel-Cantelli lemma: determining if the sum of the probabilities $\sum \psi(q)\phi(q)/q = \infty$ guarantees full Lebesgue measure despite the events (the approximations) not being strictly independent. Koukoulopoulos and Maynard mapped the Diophantine approximation overlap conditions (governed by $\gcd(q_1, q_2)$) onto the connectivity constraints of a massive graph network. By using a density increment/compression argument over this graph, they proved that any severe overlap in the arithmetic progressions forces a highly restrictive structural limitation on the network, which violates the divergence assumption [cite: 44, 45].

**Anti-Gravitational-Well:** Metric number theory typically approaches this using pure harmonic analysis and analytic number theory (e.g., Montgomery's approaches). We heavily weight the **Graph Theory Network Routing** abstraction. The substrate must recognize that Koukoulopoulos and Maynard literally bypassed analytic bounding failures by treating prime factorizations as topological graph connectivity metrics [cite: 45].

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**COUPLED_DIFFICULTY (Primary) / REPRESENTATION_GAP (Secondary)**.
The problem fused metric measure theory with the highly erratic distribution of prime factors (the structural dependency of the denominators $q$). Classical Borel-Cantelli variants failed because they could not decouple the arithmetic dependencies of the fractions from their spatial overlaps. The representation gap was solved by viewing the $\gcd$ overlaps as edges in a graph [cite: 44, 45].

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Invented:** A purely graph-theoretic model designed to bound the measure of overlapping arithmetic progressions based on their GCDs using network compression arguments [cite: 45].
**Repurposed:** Classical density increment arguments (historically used in additive combinatorics like Szemerédi's theorem) applied to Diophantine metrics.

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Dimitris Koukoulopoulos, James Maynard. "On the Duffin-Schaeffer conjecture". *Annals of Mathematics* 192(1), pp. 251-307. Published: **July 17, 2020** (Accepted May 1, 2020) [cite: 14, 44, 45].
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** arXiv:1907.04593. **July 17, 2019** [cite: 44, 45].

### (e) PRECURSOR DEPENDENCIES
1.  **Beresnevich and Velani (2006):** Proved that a Hausdorff measure analogue of the Duffin-Schaeffer conjecture is equivalent to the original, a priori weaker, Duffin-Schaeffer conjecture [cite: 44].
2.  **Borel-Cantelli Lemma variants:** The standard probability theory bounds for dependent events.
3.  **Vaughan-Pollington dimensional bounds (1990):** Provided structural insight into how overlaps behave in higher dimensions, pointing to the unique pathologies of 1D [cite: 44].

### (f) BEHAVIOR DELTA
**Work-Queue Entry:** Execute a system-wide translation of unresolved metric number theory overlap conditions (e.g., Littlewood conjecture variants) into graph connectivity bound problems. 
**Primitive Registration:** Register `GCD_Network_Graph_Compression` as a valid tool for breaking Borel-Cantelli dependence barriers.

---

## 10. Erdős Sum-Product Conjecture (Current Progress Limit)

### Mathematical Coordinates
*   **Sum-Product Bound $\max(|A+A|, |AA|)$**: Unconditionally bounded from below by $|A|^{4/3 + 2/1167 - o(1)}$.
*   **Multiplicative Energy $E_\times(A)$**: The number of solutions to $ab = cd$ in the set $A$.
*   **Convex Set Difference $|A-A|^5|f(A)-f(A)|^5$**: Bounded asymptotically by $\gtrsim |A|^{13}$.
*   **Second-order Sum-Product $|AA + AA|$**: Bounded from below by $|A|^{127/80 - o(1)}$.
*   *(HARD-5 Enforcement)*: The primary scalar sum-product exponent limit ($4/3 + c$) is mathematically distinct from the second-order multi-set exponents ($|AA+AA|$) and the convex difference limits. Do not conflate the pure Erdős-Szemerédi conjecture target ($\approx 2$) with these fractional increments [cite: 46, 47, 48].

### (a) THE TECHNIQUE THAT CLOSED THE METHOD GAP
**Streamlined incidence geometry via point-line configurations and optimized dyadic pigeonholing.**
Rudnev and Stevens pushed the best known sum-product estimate over the reals to $|A|^{4/3 + 2/1167 - o(1)}$ (breaking the standard $4/3$ barrier set by Solymosi). They achieved this by streamlining the arguments of Solymosi, Konyagin, and Shkredov, avoiding the spectral method bounds that created upper-bound bottlenecks. Instead, they relied strictly on bounding the equation $d = x - y$ using lower and upper bounds derived from point-line incidences and heavily optimized dyadic pigeonholing of the multiplicative energy parameters $E_\times(A)$ [cite: 46, 47].

**Anti-Gravitational-Well:** The gravity well in additive combinatorics treats the $4/3$ Szemerédi-Trotter incidence bound as a hard geometric wall. We must explicitly surface alternative pathways: **Query complexity on the polynomial Freiman-Ruzsa conjecture** (Pálvölgyi-Zhelezov) [cite: 49] and **Mudgal's unbounded expansion of polynomials** [cite: 49]. The substrate must weight structural group-theoretic expansion (Freiman-Ruzsa) as an equal-or-higher likelihood pathway to breaking the exponent $\to 2$ compared to fractional point-line incidence optimizations.

### (b) HARDNESS TYPE PRIMARILY ADDRESSED
**EXACTNESS_BARRIER (Primary) / REPRESENTATION_GAP (Secondary)**.
The sum-product phenomenon was stuck near $\approx 1.3333$ due to an exactness barrier dictated by the limits of crossing numbers in geometric graph theory. Advancing the exponent to $\approx 1.335$ required extracting fractional polynomial gains from the exact distribution of realisations $r_{A+B}(x)$ without losing bounds in spectral error terms [cite: 47]. 

### (c) NEW MACHINERY INVENTED OR REPURPOSED
**Repurposed:** Szemerédi-Trotter point-line incidence bounds; Solymosi's dyadic pigeonholing of line slopes; Konyagin-Shkredov synthetic additive formulations [cite: 46, 47].
**Invented (Incremental):** Elimination of the spectral method in favor of direct combinatorial bounding of the difference equation $d = x - y$ under strict popularity assumptions, allowing a worst-case scenario analysis when $|A+A| = |AA|$ [cite: 47].

### (d) PRIMARY SOURCE CITATION
*   **PEER-REVIEWED:** Misha Rudnev, Sophie Stevens. "An update on the sum-product problem". *Mathematical Proceedings of the Cambridge Philosophical Society* 173(2), pp. 411-430. Published: **October 11, 2021** (Received June 1, 2020) [cite: 46, 47, 50].
*   **ANNOUNCED-NOT-PUBLISHED (Preprint):** arXiv:2005.11145v1. **May 22, 2020** [cite: 50].

### (e) PRECURSOR DEPENDENCIES
1.  **Solymosi's geometric bound (2008):** Established the $\delta = 1/3 - o(1)$ baseline using point-line configurations on a grid [cite: 46].
2.  **Konyagin and Shkredov's synthetic approach (2015):** Enabled passing slightly beyond the $4/3$ limit using structural additive theory [cite: 46].
3.  **Shakan's record bound (2019):** Previously held the limit at $1/3 + 5/5277 - o(1)$ prior to Rudnev and Stevens [cite: 46].

### (f) BEHAVIOR DELTA
**Substrate Input:** Monitor `Polynomial_Freiman_Ruzsa_query_complexity` boundary parameters. Set an anti-anchor pin against further optimizing Szemerédi-Trotter point-line crossing numbers for the pure Erdős-Szemerédi conjecture; prioritize structural subset expansion protocols.

---

```yaml
# SUBSTRATE_BLOCK: atlas_seed_entry
# TARGET: Layer 5.5 Problem Atlas
# SCHEMA: Unregistered (Pilot Adjudication Pending)
schema_version: "5.5-pilot"
entries:
  - problem_id: "sensitivity_conjecture"
    resolved_by: "Huang_2019"
    hardness_type: ["REPRESENTATION_GAP", "CONCEPTUAL_ABSENCE"]
    technique_registration: "positive_definite_clifford_algebra_mapping"
    anti_gravity_routing: "Clifford algebras over 'magic matrix' heuristics"
  - problem_id: "bounded_gaps_primes"
    resolved_by: "Zhang_2013_Maynard_2015"
    hardness_type: ["METHOD_GAP", "COUPLED_DIFFICULTY"]
    technique_registration: "multidimensional_sieve_weights_variational_calculus"
    anti_gravity_routing: "Polymath8b variational calculus over pure analytic bounds"
  - problem_id: "erdos_discrepancy"
    resolved_by: "Tao_2015"
    hardness_type: ["GLOBAL_OBSTRUCTION", "EXACTNESS_BARRIER"]
    technique_registration: "logarithmically_averaged_elliott_conjecture"
    anti_gravity_routing: "SAT solver abstraction (Konev-Lisitsa) as co-primary"
  - problem_id: "cap_set"
    resolved_by: "CLP_Ellenberg_Gijswijt_2016"
    hardness_type: ["REPRESENTATION_GAP"]
    technique_registration: "CLP_Evaluation_Matrix_Rank"
    anti_gravity_routing: "Lean type-theoretic vector constraints over basic evaluation bounds"
  - problem_id: "kadison_singer"
    resolved_by: "Marcus_Spielman_Srivastava_2013"
    hardness_type: ["EXACTNESS_BARRIER", "REPRESENTATION_GAP"]
    technique_registration: "interlacing_families_real_stable_polynomials"
    anti_gravity_routing: "Distinguish exact interlacing from free-probability approximations"
  - problem_id: "willmore_conjecture"
    resolved_by: "Marques_Neves_2012"
    hardness_type: ["GLOBAL_OBSTRUCTION", "NON_HEREDITARY_STRUCTURE"]
    technique_registration: "multiparameter_almgren_pitts_min_max"
    anti_gravity_routing: "p-widths spectrum and Li-Yau conformal volume as primary invariants"
  - problem_id: "virtual_haken"
    resolved_by: "Agol_2012"
    hardness_type: ["REPRESENTATION_GAP"]
    technique_registration: "virtual_gluing_over_CAT(0)_cube_complexes"
    anti_gravity_routing: "Wise hierarchy & Kahn-Markovic surface subgroups equal to Agol gluing"
  - problem_id: "schinzel_zassenhaus"
    resolved_by: "Dimitrov_2019"
    hardness_type: ["EXACTNESS_BARRIER"]
    technique_registration: "transfinite_diameter_resultant_bounding"
    anti_gravity_routing: "Transfinite diameter mapping over Mahler measure gradient descent"
  - problem_id: "duffin_schaeffer"
    resolved_by: "Koukoulopoulos_Maynard_2019"
    hardness_type: ["COUPLED_DIFFICULTY", "REPRESENTATION_GAP"]
    technique_registration: "GCD_Network_Graph_Compression"
    anti_gravity_routing: "Graph connectivity compression over classical metric harmonic analysis"
  - problem_id: "erdos_sum_product_limit"
    resolved_by: "Rudnev_Stevens_2020"
    hardness_type: ["EXACTNESS_BARRIER", "REPRESENTATION_GAP"]
    technique_registration: "dyadic_pigeonholed_incidence_geometry"
    anti_gravity_routing: "Freiman-Ruzsa query complexity over fractional incidence bounds"
```

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyC2eybvvHLR3N7BrqBugI6w2Sd68GO9Yz87SloGfLTuH9qnVWfpZw6G3Mmk_Rk830ZPXxH-2Y-Vua-rVgcEd31G5HiO__5zwY53O-098RPz_bmykk)
2. [iith.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9xlJ5j1SyPqokv9o3JrIbejviz2My9m_m2SyrViCKxj0vwkZUlOwXH3TUPUyqRs9OTyZHVOOzIXrP5jWMh0pEw9xz1jHgM49qFDtEY6mOQSVHGeBiCCClBubtgIBfxqjd8oGdm8OUtmQjwJRV0g==)
3. [danielmathews.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL0tlxqmzN6mt_M255PhritzCBpH8UPrs-yrHK-iYtIj66AV2jKhdIN0vE4qpYLGWnOzmnPhBfCclfBZl-d6YsRrDlh6W75SzDKTx9iBnfzSs_qCY9JJlx9x-nJ-u-HEdkAVswej5riEQ_NHtewyLFTxWx6n9tdYwX3-L2yizyV1Iu6oRETDagvI744lBrFq2IYJcUjkzwsBeoMUPNILHNLr9sHtLbAE_qozjzZA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlNs8FRqdSNQrYrqjnVsMHivdlmYpEcBqbBmbFdXvHMMXrsTN0ybeRk8bRwdq9YShBvv9UczDLhvn-pZxNHHeBKpF8D0mnlqqogHtTpgDzYCkKtp2g)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGVnvujbaw_3nzkDCul-BOHVhuNAcShmUKQYS5Mh7TYXFjEInL14jrgGlIcm93qRCW_cvEQLXbu_yk1e_hrQHCUHuwZh-1eqnWKasev0Ol3QMmAQHeSiPXsi182uAVRzy1G8uaHLc=)
6. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtX4oGbJYnRb2pMvYlmz8SZj72U5m1Tr5vh0seaRpLk_VyR8EPEqveYvAF3eNSrU7bbMhnyRJVlPMpIac03sXkISlJFbvms1Tq2xq6Fnvi8whsOH9iT6qxRI7tmDfTnKtafMdk7A==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFH8FzIy10QcDPmx2Cl3sJ_i2n1qxEp3OR2LU2LpcMMZFJJ4ituKMLUG0K1UopCdt7qM4UtpQibB1AmWGLu3odQwLsPe2VMAJ2aQl6cEFp48CyNIe-G)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzNBSu6I1D2esmz_ZJZ33PG6GizS9NRYF7N9K4DNnQAsJklMpLi018NoF8fR22KlU0ULQrqlMyx5tl80IPABPG2-7swD0LshZU28iKBnS1-l389N0w)
9. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgaV9x-xVD2u70QR0vgV90JTw8MXg3Z8jg9q9BbawppOHMLVhhX_MBWrYdvsHAz4W74wA5W7fThjkK6DJG_AXwwWH6d1n0T16h3hzvEdg2G-YIHycMjlQZVkz8TD7VPvxKMeS22__AWMcMDnv4jrI96BMS5-RCZEM3soGy3ZKllhYu)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH08llBW5H6jF-YiwArYixN9ARMVaCdpaDK6hpuWEqfD0g6LmO9PYzza6a6Gdm2imMCP9ccv4O2kPh7mcMQYaNP0VOWjaeqmudpBhJYJK7cFEtLlT_VFgilw4OndXwFUg==)
11. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTo0ce9VOGuNC5Q28TMcBMk5AzcFbgKnAgB5LYcUCIgieSBC1Qs0gSGNV6Mx5_6kbIhrvocfL2u9QxT1ULAcusC-JL-LhRfoLWqkGC8aHyuIgd8nDDrbadkQOEIrUzbD2RqZZGH4Q=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmUYYIGnvBoO07urs2gQHf2K96ndqcEXf_z8keWQMX-w4o701TuM4f16Ix7-_inM6uBUHGzQUUJew7YSX7x4aNQvQFGV185ueGsFTcX4wB0BUTivkC)
13. [polymathprojects.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkie0sbsQ2ffhXe836XaCnVrwLoVs62I_RwN0gt1GdykKiy6qR4r1CzJ2QNkf4moI5wbohLDZQkcNrehDGfUMCDfw1_S7_UFd5F9kAcNvI14yyYe1M2JyTeHF33dNGmgbGKxYUG8xJJM-1WFb0Dux_7CpoIkZh1gYBqTgumSD0iGFjjZ2G080uKILe)
14. [google.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8YBi3yQUYOdY1xkoRKQJqiwm7uYLxOsbz_eoI4zI8Pu-gfYJzpECXgFrpzjkAGPkqapC1jEu8C0z22VCVYkjDsuMrTGwpHjJm7cFRCtsXuPWh8EDPFnMOeve91MV3xX7OUug61i5VZYLjxa1oIY-1)
15. [aperiodical.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2bj984LP7Vt7CqWDAQNmOYq1spNpDO4bBBulfEKnKYGv2poQC06kui40ScxMvi5i_-PIcm2aRXxx6sG7q61R_wqIahiRSehZ5-2zkVcRn_qPzAMUaT-ltW_88uPHGzt_drmIW7X7d1nS5WfpIUubjpQ9N7fOFltzucM4hxgS15eD5_Z11oSbZ_AU=)
16. [discreteanalysisjournal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErewz9yDIaC9bpB2_0SLGCweHCGYbzCeX4hoi5w-3hL1t8ln76qRIsAMUHMdYz2cqpT9GfvpP--7ATz4fVBWNtM_tWRMMbKCoO74LfKYtmj6rG6GhT8xy13QcssBwX5qjRoiLl7lVJDK36BTy0PY1hTFaKjAM_CVx5fnzV1QLHnQ6B)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsm6cRMXzNfeThbY16Pm92-0MNpQE4tfmNT_7VxNMN-yzW8bLwSEUqgAINo-YJ1MfK3xA1N7n-DmT8l_OD2eQ3Jbw6lJxj3sPaEbijgtY86ScCvegr)
18. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZVTYwQuaIqVpzibu7oVYgJfp5tXbCtyj-JEHaQpdGwzof_UGLi3xwmeo-4N2WNaumkt1KGQFLpPgPZ4H6lq-Bo6P_Z6MIUzpVGkxs_umrohEP16jvUUSJbC032PPeIpdFSNNNBlAuvV2ogD_YM_cMwsbiy9QVSpVoKqtq8IATJmf4CUnOGnkUucHSLSU2KhvitcO8T-pCBw==)
19. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYwejHm9ARKKCqyO6QPcKK57-5HvgzpKjKI-yNPzy0tdbULfqqYKepAu6iZ_1nMN2DU2YAPOFxDbEPE12TC35uJoVJxWCwnLBEdQrqEGXI-Y9CWq_iMcwc0UL1zgAeBBkotHNdDoZvczDpVboz1MO-idfn29qnVahGFDQXFg==)
20. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHEXKmrCvtAGEPUeDC6kek6p9v_gKYMpDEyQqvfVbA_fD98J8mEyR3BQ14uVSX7hKElpwmtwHAhZMrGxWgPEn4O3BhsmXKBSL7H7p7-AnJp_jig3FcU66lAdjtSs7gqvtmJvL15kGRCKer37gQj3NJNKmeL3TQK-HXRBOW6YU7dqii)
21. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD1-HCvXYCykwAyfkBEC_mHC3lDyXD3R3ujrPZ1ylmFmsyncUaKRqW0dAv6oVKdn4trmKNoaGnutsgENyjMlrXxR-L1bgd7yn3rHDTKkTPm8LdFamgA4YD0VyUgYqi9nKmEBht6K2Xm7Mbogwgd3eN5B38HVYS8l5RIWs1yvfOXFY1)
22. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoI-8S8MTSuiEZVdFwd6spczHVkmaB8kcXB2S9d905eScaWHbgaB3DgAwtMrnwWoSYdp0GcEH9DnrjF5xvIHdBsg4MXfDNMWkHDeRlRC02DMbgexhka_JR-Tj8sa2yyBmNDQToPg==)
23. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKXAQohN9gWBiNXWpBhPPPqMUhh2w3tD9hJ2gtQ05SAoj-wnvucisN6p9eGKNUZk3O7WeXUzokP9GrFI8-G-1LrjzW0cRPK8wAco52SZYlYVmTnLyrzbQKl9lUGT8j4SZzh94BQ-QuFEE1fINM9o7Ss8zGzAaUbGAlH5c=)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJOAsx60KVpt-x5q-WmYau5_LlFkVRzxRsmJXCqoDk1OieK18tv7g4rGYdWICesAUhKkT1jU6f92qbyEjr1CBjvNtawhQ6mtYKZJJRDXML9zY0tG8PJgVIUIR67BVZDQ==)
25. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErNX3H_MRgaTkhB7T_jBzrt0T0OKYwCFD6JXQhtBSSOxpru_2e9A6i8kW-dFuur6QX6nJocFZoEIEVxeFASrEuJmT058qos-iCpwPYjqrhhpvxD4fjcibYr89tb-kTB5CWjFX8Tw==)
26. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnF7vpwLdzOy4uAvzq7SViM05sKYENbIW0Axi9axazK9AnlNsFvLuOf0_3-AWVF2Axt7qswg3Eogu3X6MdoUSrH2xwxI3rMRpx0w4cFkPryqKdIJOkoVzZd669YI2ZsOkMlqFJWgl63n_RBA==)
27. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhlhSifb2TwEMN4ptqUlO7zU7Eh_3ztp5bklyiUw4VsAIYziSMZNLeaPzHMk3hART_2h7OYko3JHUokMTRsa-c-8YEmNBDTjHLScx8EfkBUhm12xbZPMoESRyNGJpihXQ=)
28. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwn1NU1bSzMBc_Mnt2mZ2nnjlVHyAwpgUGBiR-CU7P5sr9F3Zc2Thvy-_yZT_BHVTy5Mr1uNw8LbMKMsqU-XHORrfRkrvGXSyqzv8rDeqdYBKHPs9ZIITj3FEb-ZZ2vgFkHDtqWg==)
29. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLUeSe56fXPR7JEKF-QyEcg6BFsPx1CwXGWWCs87302r_MafDsKPlGqMQhZrRa6_n9_mTt8e4VG6MZvUbKZ3Mc7YZdGHtS-pnr4rLwfCYKfR_TWrLQIvTQd2tZm4SWDAnmUwCLlPolc8vojYLCjL4fnLAXZHMiFj2UhiNKYxGgKs_Z6qhGHDgvqdDxvvuw-V3G6A_WoWdi44TpteNzhctsDmOobFnWwfDgMQfzVmKkjaQAwnDMCSeuNwYqX8piJpPZ_8pvQ0A62Zg=)
30. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMRkYExyeeDFQWsksimwR990wzOaQNmlp2_3HKx1ifHuVHwA7FO2SFc50rHGPbqy00lRLr9Ap1XZKpwJ4dca6500lM5ha_JIeVl-pSqtNAlyLvRM_dcQQbgSQ9xITT4nBt9lnPcAWGkobhH4xjtSB6CsU2aCB7URFaPo69WLijpx6N)
31. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFM2atVfsO0oxVR6aS3_TVc8fFvZWCcScB4hTzEsa42WFl7NrsQjtJW2vS3oMTg7Vb-UDISD3wBIrGmY-30QFIPWR3Eo0eo_vMda3sfY9hDagiNuFY2Y1uVlUkqsWHKmijstu5C9lX3cauzTMjueOewL4=)
32. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuK7G-ByWvYy4CNXva2orgG8T46pwep-bhWpos8nv0KPWDi7GPTx5FveokQEmYhauQHF-hDMMuh5GMcpPJH5sr-vRh8rc9z2XTC6kOXrKNNSyHaYmtOuBPzn9pgkAUqgIaykbGIC4=)
33. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnhXblSMNk6oTd-G-N2gkGOGUQS3I7upMRqd0vbMIgqo1K04yKZnBMlihJ_JByy39eZYc0juS8g4vUSYJrbJn2srrDPtMOhVJYxZV86V3cYg7jwMFXPKpauFJQEU3YQqkN86YaGw==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhUCrIdHe8FWJwYedHC_0GK2VxaaPazMMVr1CPkHRAN4wOuzHJi4yLTSLIyJmPqeUqlWFqGt3tiUfcF8RPZRVpR69xO3qatIp617UBTdGtNex1j1w=)
35. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpex5_AH2b-fUzEzDVcebS6xS8FR1a08dsMERoNwBBNEozf6erWuCkjzzbDi6SLOwC84qT5Eq0qq8RXoKNcJfhKkCyoUHr4AKmtirLYYdVfnGoJQssAKcY-kmsk6mscqePMD3NtQ20922eoV2jTKHL3Q==)
36. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL9-W0rF4ZLe6WlejiMloH42-TxkaNO6ppelzHfB8yzjQFbC5mEmeHB7EDRS364CPpD-0sNlA4kuUoSJvIQ8gjfwE5o61Oyj_2-eja8sKhgrXv0w_LslalQntPbmyinIm4WacjFcGskdSkuGab)
37. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG380_v3qxtGD5eB8q2CkxbX-rsuXaeRUFj2jFiwVQQJ8pa7fMVq_XW95x2c4expZOZ46wad5Qfj3uhsrT5rLpRZD-WFK8jaOYKavJzN6-0SqDeB2hBCXW4-bp8NtoCysym2SGSqDYbKc0=)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESv2HVTNOyAxvV6rG1HM2rSszoHk10KPKxJDJHi3Kvth8XLX9tfRIbF5Ypn93jL5vFq_SiDLb7NsEEL9cinMUIz0BjXu0qXKJ6TzhHrY4qo4xW81b-)
39. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXR1sRyt_3LOZRm6tdul_LHmhf1hPP4eu3rwn7tX-DvBOUZXyNPAOeaGrt8GC1GJLLxOuL7JGEJSLVxJWLxeiuB7XzrwMIlmFHtQhyAxC8sfbEfRx3DsunFS1LJe2nMjmXTRpasYmmWay_Q-tyii4h2tJchkWFfcXZaNCx5Vxe_bKuEq8JkFY50dhwT9cHu62C0ej7RCU=)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLEVAaUXlZZa7QsUI0rIgM_6Uxp3VVfrPPhGkMPaI4KW3T660WKhPgFMeef26AkNSEIY16qfA-NkSlpLGUqszfidOvCVb6VEgoc_8KOki2s__7ZFjA)
41. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMqEvkEdtRACY8A4chl95bFhkc0ox-QPzVVHAg-TSHc7T3kdH_gZ1U7hXzgd6V8P4YiaSO0KevvXBRlVNCK-Wf6X95-CG6NBFDOLQEYNLxFl8z0DOGRRVFBDl8CM-TEZbVO6lo1mtMmJwreL96QWHhSxmQXKbFyKBZa0nlMyomT0RzDYclmhfh-Toesmu7mlsPQb3J_5swN5SINmeBhPXgjNQcuA==)
42. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsUMEUyvgpYRrYjom4pMk5_X8BFyZjB1zK8uyd2_zBw5sAeT_mzDrS7PBk-RX5fiRDBXztx3TpnQJGRzsAlvtdAARLaQYlvzAshGGU8AofTgxNrPaTPLIVDjAjpSAJAJ2k3AwV)
43. [163.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhb-ZjoHVMl4GTx8UXW2jHEEtrKt9nSbsixczAeB6urH3OdBoJwtVAlztahm3H7cfKLnUoYU-ORIn6jaPeu81FIAy05KpZW1aDcSV7A6_g4anTIWG3I6urjxgY4pzUCDv4f_8d4wvTaUc=)
44. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3talPTwV1v7VilprMb4kHm3lijgja4HM56CGiBZEnt--S28E3Cn0M_Ti9Yrno8OJkUTkNRnLu_uB15Qg8ZaGWdz6Fxi5-ObsevENaJRCc3cPHatl8Fchn4dbFxhZ8azV2Rz6QgBfFctBi4QFEe_JnCXtr)
45. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVgVb21AxzLVwG-qeq87WHj20Exsk1l9gB2biz_lJcxQv85Y9u97EEjKQdWi7iG6casSMXWG8EA4cMJ4LPKIfxFj-6OXDEOn7t1b4068rmEkHrTkKIWeNrPHBLQvr6BKesj3GJUw==)
46. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQwNJ_M3qTVnmZfOH9lU27gi1rdqQixmO5FRn_Jk-3l-zsjNymtHXp_SVoW84VklBpU-pkP6ZJFbWx578T2MrtnElYvOKtn1Fs3gXzv1ZVrBx3mAGiKPMa_D8zUb12iN5te4YJyjpBUVM6U1239XnLLlLaggNwvSN3elIhtJqS05UBF3WclE6DDEYGHFbceFFrOZQ-N_nUs3LtjYuW8ea_65HT28ZT3EewweaUwe3jOM9yMUZTiLhPF-nKbHDKU6SuSD_e8YMQff9enk2UoXBYiWv_zBxIySk6eTVvl-D4J56JwuTH1w9Sguo=)
47. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3KY9tRaa5m9MOxSTeGhk1C9QZqK0dKJk13e86EZioRFhH8yuVl3Y0bTTjOPjImDLIbIGrWBVx0tk_901_WgpeuuwS77zfEu6SwVp6G_DKagqtqPT-YgHhiLGv-JbdLyaqn4Gxq7ZP0oRG5-MOtZQBE4Ri2b7aWrvbmHFCSaApm6FcYICfK8O4pMzg3AI5TFj76F_xk9h-Tfizgzu2FNwQOfez0w2mgJO9mOv3xM3B5SG0UnMLeKHPFeTy023FuPO2zgfwp5V321guEtIKaBoBZ-RHZWkC0xcQLLMkzUU=)
48. [combinatorics.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1zT1kwfueZlJ165qy_5x8UlcBbx4B6cBMDyQSd3j9vKsdxRbbwwZLp1jlVNInemVRbBBbe0f2v09JWz9AWCmJLMZi9WM5Kw0p4Y4SNBP5T8P_-dKSiRhHn5LlIgR6-CBDJdmTT9tTWUjGYYadL4svJoYcmTfSN9DhyICJQqcNIkC-QVU=)
49. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj073CUpgSVs8c-GV_tmWAQobXa9zmBliVPUvR-D4GnsmMPpHxe3jEgFZ6iR19z8B13ndZUmQ_sWMyPDdDwpD1LW06oqgX3H8XzqHOEl8X9QhCjm2_gs8u1Ww=)
50. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8B_8N3DtonUBaP-TzdHa9AK-8cmnpNnJODbs4exKkAkdlsIaFER-sdNMg0HQGj39eJTXNObPbOh2nxgvOX9ka4ADAdr6iRSInm9O8xIdUCi1PQaCg)

