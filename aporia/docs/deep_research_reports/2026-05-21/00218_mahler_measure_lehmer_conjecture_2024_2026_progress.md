# Mahler measure + Lehmer conjecture 2024-2026 progress

**Pythia queue id:** 218
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd5VTBQYXVqcEpmLTNfdU1QLW9QOGlBOBIXeVUwUGF1anBKZi0zX3VNUC1vUDhpQTg
**Elapsed:** 250s
**Completed at:** 2026-05-21T18:28:20.640654+00:00

---

# Progress on the Mahler Measure and Lehmer's Conjecture (2024–2026)

**Key Points:**
*   **Classical Bounds and Extremal Polynomials:** Research suggests significant progress in finding normalized bounds for Littlewood polynomials, with Turyn polynomials demonstrating normalized Mahler measure ratios reaching 0.9511. Simultaneously, computational claims from late 2025 suggest potential discoveries of Complex Salem Numbers possessing Mahler measures smaller than Lehmer's classical constant, though these require further independent verification. 
*   **Multivariate Limits and Dynamics:** The evidence leans toward a robust framework for understanding limits of multivariate Mahler measures. Recent generalizations of Boyd and Lawton's theorems to multiple variables demonstrate that sequences of Laurent polynomials formed by monomial substitutions converge to the Mahler measure of the base polynomial, with explicitly defined error bounds. 
*   **Motivic Cohomology and L-Functions:** It seems likely that the deep connections between Mahler measures, regulators, and special values of L-functions are solidifying. Recent work extending Deninger's framework relates two-variable cyclotomic polynomials to Dirichlet L-values via the Beilinson regulator map.
*   **Elliptic and General Conjectures:** Experimental databases constructed in 2025 provide the most extensive empirical data to date for the Elliptic Lehmer and Lang conjectures over quadratic fields. Progress has also been recorded in analogous number-theoretic problems bearing Lehmer's name, including the Totient Conjecture and the Ramanujan Tau Trace conjecture.

**Overview of the Lehmer Problem:** 
Lehmer's conjecture, introduced by Derrick Henry Lehmer in 1933, is a profound unsolved problem in number theory. It posits that the Mahler measure of any non-cyclotomic irreducible polynomial with integer coefficients is bounded below by a universal constant strictly greater than 1. This simple yet elusive question has sparked decades of research spanning Diophantine geometry, transcendence theory, and dynamical systems. 

**Recent Advancements (2024-2026):**
The period between 2024 and 2026 has witnessed highly active research around Mahler measures. Methodological breakthroughs have bridged analytic number theory and topology, linking the Mahler measure to Fuglede-Kadison determinants, hyperbolic 3-manifolds, and topological entropy. Concurrently, high-performance computing and algorithmic refinements have enabled the exploration of generalized Lehmer conjectures across elliptic curves, non-commutative quaternionic domains, and specialized sequences like numerical semigroups. 

---

## Introduction and Core Definitions

The **Mahler measure** is a foundational analytic invariant in transcendental number theory, algebraic geometry, and arithmetic dynamics [cite: 1]. It quantifies the average logarithmic size of a polynomial's values evaluated on the unit torus [cite: 1]. Originally emerging from questions regarding the distribution of roots of polynomials, it has since evolved into a versatile tool for probing deep algebraic and topological structures.

For a univariate non-zero polynomial \( P(x) = a_0(x - \alpha_1)(x - \alpha_2)\cdots(x - \alpha_D) \) with integer coefficients (\( P(x) \in \mathbb{Z}[x] \)), the Mahler measure \( M(P) \) is defined elegantly via its roots in the complex plane \( \mathbb{C} \) [cite: 2]. The classical Mahler measure is given by the formula:
\[ M(P(x)) = |a_0| \prod_{i=1}^D \max(1, |\alpha_i|) \]
Equivalently, the logarithmic Mahler measure \( m(P) \) is defined as \( m(P) = \log M(P) \) [cite: 3, 4]. Due to a classical application of Jensen's Formula [cite: 5, 6], for any \( \alpha \in \mathbb{C} \), \( m(x - \alpha) = \log \max(|\alpha|, 1) \) [cite: 5]. Therefore, the Mahler measure can also be expressed as an integral over the unit circle [cite: 1]:
\[ m(P) = \frac{1}{2\pi} \int_0^{2\pi} \log|P(e^{i\theta})| \, d\theta \]
Because the coefficients of \( P \) are integers, it is a known property that \( m(P) \geq 0 \) [cite: 5, 7]. A classical theorem due to Kronecker establishes that for an irreducible polynomial \( P \in \mathbb{Z}[x] \setminus \{0\} \), the Mahler measure \( m(P) = 0 \) if and only if \( P(x) = x \) or \( P \) is a product of cyclotomic polynomials [cite: 2, 5]. Consequently, a product of cyclotomic polynomials yields a Mahler measure of exactly 1 [cite: 6].

### Lehmer's Conjecture
In 1933, while searching for large primes using a primality test generalized from the Lucas-Lehmer test, D.H. Lehmer investigated the sequences \( \Delta_N(P) \) associated with polynomials \( P \in \mathbb{Z}[x] \) [cite: 5]. He observed that to apply these tests effectively, the sequence \( |\Delta_N(P)| \) must not grow too rapidly [cite: 5]. Lehmer related the growth rate of these sequences to the Mahler measure, demonstrating that \( \lim_{N \to \infty} |\Delta_{N+1}(P) / \Delta_N(P)| = \exp(m(P)) \) provided \( P \) does not vanish on the unit circle [cite: 5, 8]. 

Seeking to optimize his search for prime numbers, Lehmer wanted to find polynomials with a small, positive logarithmic Mahler measure [cite: 3, 5]. This led him to formulate what is now known as **Lehmer's Mahler measure problem** or **Lehmer's Conjecture** [cite: 2, 9]. The conjecture asserts the existence of an absolute constant \( \mu > 1 \) such that for every polynomial \( P(x) \in \mathbb{Z}[x] \) that is not a product of cyclotomic polynomials (and not the monomial \( x \)), its Mahler measure satisfies \( M(P) \geq \mu \) [cite: 2]. 

Lehmer himself identified a degree-10 reciprocal polynomial:
\[ L(x) = x^{10} + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1 \]
This polynomial has a Mahler measure of approximately \( M(L) \approx 1.176280818 \dots \) [cite: 10, 11]. To this day, no polynomial with integer coefficients has been found with a Mahler measure strictly between 1 and 1.17628 [cite: 9, 10]. The conjecture broadly predicts that the value \( 1.17628\dots \) is indeed the absolute minimum [cite: 10, 12].

## Theoretical Bounds and the Schinzel-Zassenhaus Connection

While a complete resolution to Lehmer's conjecture remains elusive, substantial partial results and lower bounds have been formulated over the years, setting the stage for recent 2024–2026 developments.

### The Dobrowolski Bound and Reciprocal Polynomials
For decades, the best general lower bound for the Mahler measure of a polynomial with integer coefficients was established by Dobrowolski (1979) and later refined by Voutier [cite: 5, 13]. For an irreducible polynomial \( P \in \mathbb{Z}[x] \) of degree \( d \geq 2 \), the Dobrowolski bound states that the Mahler measure falls short of proving Lehmer's conjecture by a factor that decays logarithmically with the degree [cite: 5]. Dobrowolski utilized estimates from the Prime Number Theorem to analyze sums over primes and lower bound character sums [cite: 14].

Furthermore, C.J. Smyth demonstrated in 1971 that Lehmer's conjecture holds unconditionally for non-reciprocal polynomials [cite: 12, 13]. A polynomial is reciprocal if its coefficients read the same forwards and backwards, meaning that if \( \alpha \) is a root, so is \( 1/\alpha \) [cite: 12]. Smyth proved that non-reciprocal units have a minimal Mahler measure bounded by \( \theta_0 \), the smallest Pisot-Vijayaraghavan number, which is the positive root of \( x^3 - x - 1 \) [cite: 13]. Thus, the search for counterexamples to Lehmer's conjecture was fundamentally narrowed to reciprocal polynomials [cite: 12]. 

Researchers in 2024 have also sought to constrain the search space by examining Galois groups [cite: 12]. According to Amoroso and David (2006), Lehmer's conjecture is true if the Galois group of the polynomial is sufficiently small (e.g., bounded by a polynomial in \( n \)) [cite: 12]. Computational projects, such as those launched in Spring 2024 at MXM, have aimed at computing the Mahler measures and Galois groups of reciprocal polynomials using computer algebra systems like Sage and Magma to refine these structural conjectures [cite: 12].

### Dimitrov's Resolution of the Schinzel-Zassenhaus Conjecture
A critical breakthrough closely allied to Lehmer's problem—and heavily discussed in the 2024–2026 period—is Vesselin Dimitrov's proof of the Schinzel-Zassenhaus conjecture [cite: 13, 15]. Often considered a "satellite" to Lehmer's problem, the Schinzel-Zassenhaus conjecture addresses the "house" of a non-zero algebraic integer \( \alpha \) (the maximum modulus of its conjugates) [cite: 15, 16]. 

Dimitrov proved that for any non-zero algebraic integer \( \alpha \) of degree \( d \) that is not a root of unity, there exists a conjugate \( \alpha' \) such that:
\[ |\alpha'| \geq 2^{1/(4d)} \]
[cite: 5, 16]. This establishes that the maximum root of such an irreducible monic polynomial is bounded below by \( 2^{1/4d} \) (or more broadly, \( M(P) \) cannot be arbitrarily close to 1 since \( \max |\alpha_i| \geq 2^{1/4d} \)) [cite: 16, 17]. Dimitrov's proof elegantly translates the arithmetic problem into an analytic one utilizing the Pólya rationality theorem for power series with integer coefficients and estimates of the logarithmic capacity (transfinite diameter) of sets [cite: 16, 18]. 

In 2024, researchers continued to leverage Dimitrov's methodology. For example, his techniques have been applied to determine lower bounds for the maximum modulus of roots of monic integer polynomials with roots symmetrically distributed with respect to the unit circle [cite: 18]. Furthermore, Dimitrov's analytic frameworks have provided new inspiration to attack the full Lehmer conjecture [cite: 13, 16].

## Extremal Polynomials and Computational Breakthroughs (2024–2026)

Driven by advances in computational complexity and optimization algorithms, the 2024–2026 period yielded remarkable numerical findings regarding extremal polynomials.

### Littlewood and Turyn Polynomials
The Mahler measure is centrally important in extremal problems involving **Littlewood polynomials**—polynomials of degree \( n \) whose coefficients are strictly \( \pm 1 \) [cite: 1]. A major open question has been determining the supremum of the normalized Mahler measure \( M(f) / \|f\|_2 \) for \( f \in \mathcal{L}_n \) [cite: 1]. 

In a significant 2024 advancement, Mossinghoff established that Turyn polynomials featuring a quarter-degree shift yield a normalized Mahler measure ratio of \( M(f) / \|f\|_2 \to 0.9511 \) as the degree increases [cite: 1]. This set a new record, surpassing previous extremal examples like the Rudin-Shapiro polynomials, which only attained a lower bound of roughly \( 0.8578 \) [cite: 1]. Mossinghoff's 2024 breakthrough bounded any universal global gap \( 1 - \epsilon \) in the supremal normalized Mahler measure by \( \epsilon \leq 0.049 \) [cite: 1].

### Complex Salem Numbers and the IFO Preprints (Late 2025)
A potentially revolutionary (though currently empirical/preprint-stage) claim emerged in December 2025 by researcher Sinan Ibaguner [cite: 19]. Through a framework named the "Trinity Principle"—combining Human Intuition, Artificial Intelligence, and the "Ibaguner Fractal Operator (IFO)"—Ibaguner claimed the discovery of Complex Salem Numbers with Mahler measures strictly smaller than Lehmer's traditional constant [cite: 19]. 

The preprint states that a minimal Mahler measure of \( M_{\text{min}} = 1.14283629 \) was discovered [cite: 19]. If verified mathematically, this would surpass the real-domain boundary of \( 1.176280818 \), inherently shifting Lehmer's problem into the complex domain and extending theorems like the Pisot-Vijayaraghavan theorem to complex Pisot numbers [cite: 19]. While these 2025 claims are presented as a unification paradigm, standard academic consensus dictates they await rigorous peer review and theoretical substantiation before fully overturning Lehmer's original bounds for \( \mathbb{Z}[x] \) [cite: 19].

## Multivariate Mahler Measures and Limit Formulas

While Lehmer's original question was univariate, contemporary research actively investigates multivariate generalizations. The logarithmic Mahler measure for a Laurent polynomial \( P \in \mathbb{C}[z_1^{\pm 1}, \dots, z_n^{\pm 1}] \setminus \{0\} \) in \( n \) variables is defined as the mean of \( \log|P| \) restricted to the standard \( n \)-torus [cite: 1, 20]:
\[ m(P) = \frac{1}{(2\pi)^n} \int_0^{2\pi} \cdots \int_0^{2\pi} \log|P(e^{i\theta_1}, \dots, e^{i\theta_n})| \, d\theta_1 \cdots d\theta_n \]
[cite: 3]. The Mahler measure of a multivariable polynomial is intimately connected to topological entropy, arithmetic dynamics, and L-functions [cite: 6, 20]. 

### Convergence of Monomial Substitutions
A major triumph in multivariate Mahler measures published in 2024 (following 2022 preprints) is the collaborative work of F. Brunault, A. Guilloux, M. Mehrabdollahei, and R. Pengo [cite: 3, 21]. They investigated the limits of Mahler measures under monomial substitutions, answering a deep structural question [cite: 22, 23]. 

Classical work by Boyd and Lawton proved that one can approximate the Mahler measure of a multivariate polynomial using univariate substitutions. Brunault et al. successfully generalized these theorems to multivariate monomial substitutions [cite: 22, 24]. Specifically, they proved that sequences of Laurent polynomials derived from a fixed multivariate Laurent polynomial \( P \) via monomial substitutions yield sequences of Mahler measures that strictly converge to the Mahler measure of the original polynomial \( P \) [cite: 4, 22]. 

Furthermore, the team provided a rigorous, explicit upper bound for the error term in this convergence [cite: 22, 23]. This error bound generalization directly extended prior results by Dimitrov and Habegger [cite: 21, 24]. In their exploration, they also furnished a complete asymptotic expansion for a specific family of 2-variable polynomials [cite: 21]. For a family of polynomials \( P_d \), they computed the asymptotic error term as \( d \to \infty \) relative to a matrix \( A_d \), heavily featuring the spectral radius \( \rho(A_d) \) [cite: 23]. This multivariate convergence framework provides a powerful mechanism to study sets of Mahler measures, demonstrating that such sets are closed—a critical topological property originally hypothesized when evaluating Lehmer's conjecture globally [cite: 4, 24].

## Connections to L-Functions, Motives, and Regulators

One of the most profound developments surrounding Mahler measure in recent years is its "mysterious link" to special values of L-functions, Dedekind zeta functions, and polylogarithms [cite: 7, 25]. This association transforms the Mahler measure from a simple height function into an entity capturing deep arithmetic geometry.

### Deninger's Cohomological Framework
The theoretical architecture bridging Mahler measures to L-values was established by C. Deninger [cite: 26, 27]. Deninger demonstrated that if a polynomial \( P \) does not vanish on the \( n \)-torus \( \mathbb{T}^n \), its Mahler measure can be interpreted geometrically as a Deligne period of the motive associated with the algebraic variety defined by \( P = 0 \) [cite: 26]. By invoking Beilinson's conjecture, which links regulator maps to special L-values, Deninger hypothesized that \( m(P) \) equates to the regulator of a relevant motivic cohomology class, up to a non-zero rational factor [cite: 27]. 

Historically, this was exemplified by Boyd and Smyth, who found exact relations such as:
\[ m(1 + x + y) = L'(\chi_{-3}, -1) \]
where \( \chi_{-3} \) is the odd Dirichlet character of conductor 3 [cite: 26, 28]. Similarly, elliptic curve relations were found, such as \( m(1 + x + 1/x + y + 1/y) = r_E L'(E, 0) \), where \( E \) is a specific elliptic curve [cite: 26].

### 2025–2026 Advances by He and Lee
In late 2025 and January 2026, researchers Wei He and Jungwon Lee released groundbreaking work systematically expanding this framework [cite: 27]. Inspired by Deninger, they presented an exact formula relating the Mahler measure of a two-variable variant of cyclotomic polynomials directly to regulators of classes in motivic cohomology associated with cyclotomic fields [cite: 27]. 

He and Lee achieved this by deeply analyzing the Beilinson regulator map applied to systematically constructed elements within the motivic cohomology group [cite: 27, 29]. Their results yielded a formula expressing the Mahler measure as a linear combination of special values of the derivatives of Dirichlet L-functions [cite: 27, 29]. 

Under specific linear independence hypotheses concerning the derivatives of partial Dirichlet L-values at \( s = 0 \) and \( s = -1 \), He and Lee studied the Galois module structure of the relative cohomology [cite: 27, 29]. This allowed them to refine their identity to isolate a single L-value [cite: 27, 29]. Their methodology generalized Chinburg's conjecture from real primitive odd Dirichlet characters to all primitive odd characters [cite: 27, 30]. This solidifies the theoretical backing that for certain families of polynomials (like those of conductors \( f = 3, 4, 8, 15, 20 \), and \( 24 \)), the Mahler measure inherently acts as a volume descriptor for hyperbolic objects and encapsulates motivic L-data [cite: 30, 31].

### Higher-Dimensional Polylogarithms
Other parallel research in this timeframe expanded Mahler measures to up to five variables. Formulations were uncovered expressing the Mahler measure in terms of multiple polylogarithms [cite: 31]. In these instances, the formulas are homogeneous, and their weight corresponds exactly to the number of variables in the polynomial [cite: 31]. This aligns perfectly with the cohomological expectations outlined by Maillot and Rodriguez-Villegas, indicating that multivariable Mahler measure corresponds universally to higher-weight motivic integration [cite: 31, 32].

## Elliptic and Abelian Generalizations

Lehmer's conjecture fundamentally queries the behavior of heights of non-torsion algebraic numbers. This concept naturally generalizes to elliptic curves and abelian varieties, leading to the **Elliptic Lehmer Conjecture** and **Lang's Conjecture** [cite: 33]. 

### The Elliptic Lehmer Conjecture
Let \( E \) be an elliptic curve over a number field \( K \), and let \( \hat{h}(P) \) denote the canonical height of a point \( P \in E(\overline{K}) \) [cite: 33]. The canonical height \( \hat{h}(P) = 0 \) if and only if \( P \) is a torsion point [cite: 33, 34]. The Elliptic Lehmer Conjecture predicts how the smallest positive height of a non-torsion point varies with the degree of its minimal field of definition. 

Specifically, Conjecture 1.1 (Elliptic Lehmer) states that there exists a strictly positive constant \( C_E > 0 \) such that for all non-torsion points \( P \in E(\overline{K}) \setminus E(\overline{K})_{\text{tors}} \):
\[ \hat{h}(P) \cdot [K(P) : K] \geq C_E \]
[cite: 33, 34]. 

Lang's Conjecture (Conjecture 1.2) further asserts that the height relates uniformly to the minimal discriminant and j-invariant of the curve [cite: 33]. By defining \( M_E = \max\{\hat{h}(j_E), \log |N_{K/\mathbb{Q}} \Delta_E|, 1\} \), Lang conjectured a universal constant \( C_{K,d} > 0 \) bounding the ratio \( \hat{h}(P) / M_{E'} \) [cite: 33, 34].

### Experimental Data (2025)
Despite theoretical progress via abelian varieties, empirical data on the actual values of \( C_E \) and \( C_{K,d} \) was historically sparse [cite: 33]. In 2025, Orvis et al. published a comprehensive computational investigation into these elliptic analogs [cite: 33, 34]. Utilizing over 800 hours of CPU time, they constructed a massive database of quadratic points of small height on 17,834 elliptic curves over the rationals (\( K = \mathbb{Q} \)) [cite: 33, 34]. 

In 728 specific instances, their algorithm provably isolated the point of the absolute smallest canonical height on the given elliptic curve across *any* quadratic field [cite: 33, 34]. For 542 curves, it was rigorously verified that no non-torsion points exist of height smaller than five in any quadratic field [cite: 33]. This 2025 database provides the most robust empirical evidence to date anchoring the constants \( C_E \) and \( C_{K,d} \), confirming that as the discriminant and conductor grow, the minimum heights adhere strictly to the non-zero boundaries predicted by the Elliptic Lehmer and Lang formulations [cite: 33].

## Topology, Entropy, and Dynamical Systems

The interdisciplinary reach of the Mahler measure has deepened significantly, particularly its relation to topology and dynamics.

### Ergodic Automorphisms and Topological Entropy
The Mahler measure of a polynomial in \( k \) variables is inextricably linked to the topological entropy of a \( \mathbb{Z}^k \)-dynamical system canonically associated with that polynomial [cite: 5, 6]. Work by Lind established that the infinite-dimensional torus possesses ergodic automorphisms of finite positive entropy—or exclusively automorphisms of infinite entropy—depending entirely on the solution to Lehmer's problem [cite: 2]. 

Because ergodic compact group automorphisms are measurably isomorphic to Bernoulli shifts (classified by Ornstein's theorem via entropy), Lind showed that the moduli space of all ergodic compact group automorphisms is either countable or uncountable directly contingent upon the truth of Lehmer's conjecture [cite: 2]. Thus, proving Lehmer's conjecture would instantly resolve profound classification problems in ergodic theory.

### The Fuglede-Kadison Determinant and L2-Torsion
Another major bridge built between Lehmer's conjecture and topology involves the **Fuglede-Kadison determinant** [cite: 10]. For Laurent polynomials \( P \in \mathbb{Z}[t, t^{-1}] \), the polynomial ring can be interpreted as the group ring of the infinite cyclic group [cite: 10]. The Mahler measure of \( P \) aligns precisely with the Fuglede-Kadison determinant of the associated multiplication operator on \( \ell^2(\mathbb{Z}) \) [cite: 10].

Lück proposed a geometric approach to evaluate these determinants, linking them to the \( L^2 \)-torsion of manifolds [cite: 10]. The \( L^2 \)-torsion of hyperbolic 3-manifolds can be computed in terms of their hyperbolic volume [cite: 10]. Research surrounding the SPP 2026 "Geometry at Infinity" initiative demonstrated that the fundamental groups of small-volume hyperbolic 3-manifolds permit matrices over integral group rings with exceptionally small Fuglede-Kadison determinants [cite: 10]. 

For instance, the **Weeks manifold**—known to be the closed orientable hyperbolic 3-manifold of minimal volume—yields an integral group ring element with a Fuglede-Kadison determinant taking a value of approximately \( 1.051\dots \) [cite: 10]. This value is remarkably smaller than the expected bound of \( 1.17628 \) in the classical univariate Lehmer conjecture [cite: 10]. While this does not violate Lehmer's classical univariate polynomial bound, it showcases how generalized Lehmer problems in group rings of hyperbolic manifolds behave radically differently due to underlying topological geometries [cite: 10].

### Hyperbolic Dehn Fillings and Trace Fields
The connections to 3-manifold topology extend to Dehn surgery. For a 1-cusped hyperbolic 3-manifold \( M \), Thurston demonstrated that the manifolds \( M_{p/q} \) obtained via \( p/q \)-Dehn filling remain hyperbolic for all but finitely many coprime pairs \( (p,q) \) [cite: 11]. Researchers have utilized Lehmer's conjecture (and Dimitrov's Schinzel-Zassenhaus theorem) to bound the degrees of the trace fields \( K(M_{p/q}) \) [cite: 11].

The A-polynomial of a knot relates the Mahler measure to the geometry of the complement. By analyzing the roots of the A-polynomial near 1, mathematicians have established explicit piecewise-linear lower bounds for the degree of the trace field as a function of the Dehn filling parameters [cite: 11]. Assuming Lehmer's conjecture unconditionally bounds the Mahler measure, the degree of the trace field must grow predictably, ensuring that Dehn surgeries produce manifolds with vast, distinct trace fields [cite: 11].

### Numerical Semigroups and Quaternionic Domains
Novel algebraic structures are also being tested against the Mahler measure. In a May 2026 talk at the Max Planck Institute for Mathematics, M. Mehrabdollahi proved a conjecture by P. Moree and A. Herrera-Poyatos (assuming the truth of Lehmer's conjecture) detailing the Mahler measure of polynomials arising specifically from numerical semigroups [cite: 35, 36]. 

Simultaneously, a March 2024 paper by Weijia Wang et al. introduced the **quaternionic Mahler measure** for non-commutative polynomials [cite: 37]. By establishing the existence of this measure for slice regular polynomials in one and two variables, they extended the classic Lehmer problem into the non-commutative quaternionic realm, proving various formulas that map traditional Mahler properties onto non-commutative algebraic structures [cite: 37].

## Clarification: Other "Lehmer Conjectures" Addressed in 2025

It is vital in an exhaustive academic overview to disambiguate "Lehmer's Mahler measure problem" from other conjectures bearing Lehmer's name, as significant progress occurred across multiple such problems in the 2024–2026 window. 

### Lehmer's Totient Conjecture
Lehmer's Totient Conjecture (1932) asks whether any composite integer \( n \) satisfies \( \phi(n) \mid (n - 1) \), where \( \phi \) is Euler's totient function [cite: 2, 38]. If true, no such composite exists, and the condition strictly identifies prime numbers [cite: 39].

In a November 2025 preprint, an immense computational and theoretical stride was made regarding this conjecture [cite: 38]. The research eliminated all 14-prime composites using 2-adic valuation analysis, backed by explicit computation [cite: 38, 39]. Furthermore, the authors introduced the "bounded-catch framework"—a \( q \)-adic inequality describing overflow thresholds for high-prime clusters [cite: 38]. Across thousands of configurations of 15 to 20 primes, all random tuples overflowed by \( q \leq 13 \) [cite: 38]. The paper concluded that under the Generalized Riemann Hypothesis (GRH), the proportion of surviving composite configurations drops to analytic density zero, fundamentally capturing the asymptotic truth of Lehmer's Totient Conjecture for almost all composites [cite: 38, 39].

### The Generalized Lehmer Conjecture (Ramanujan Tau Function)
Another completely separate problem is Lehmer's conjecture concerning the non-vanishing of Ramanujan's tau function, \( \tau(n) \neq 0 \) [cite: 2, 40]. The tau function represents the Hecke eigenvalues for the modular discriminant in the space of cusp forms of weight 12 and full level, \( S_{12}(SL_2(\mathbb{Z})) \) [cite: 40]. 

In November 2025, L. Chiriac and E. Williams made significant strides on a generalized version of this conjecture posed by Rouse (2006) [cite: 40]. Rouse conjectured that the trace of Hecke operators \( T_n \), denoted \( \text{Tr}_{2k}(\Gamma_0(N), n) \), does not vanish under certain weight and level conditions [cite: 40]. Chiriac and Williams refined Rouse's algorithmic approach to unconditionally settle the conjecture for the trace of \( T_3 \) in full generality, thereby proving that specific coefficients of the characteristic polynomial of \( T_3 \) can never be zero [cite: 40]. 

## Conclusion

The 2024–2026 period has proven to be an era of immense synthesis for the Mahler measure and Lehmer's conjecture. While the absolute minimum bound of \( 1.17628\dots \) for univariate integer polynomials remains unbreached in verified classical mathematics, the surrounding theoretical architecture has expanded exponentially. 

Dimitrov's resolution of the Schinzel-Zassenhaus conjecture provided the analytic tools necessary to construct robust lower bounds [cite: 16, 18]. Mossinghoff's bounds on Littlewood polynomials have driven the extremal ratios to near-unity [cite: 1]. Brunault, Guilloux, Mehrabdollahei, and Pengo rigorously sealed the behavior of multivariate Mahler limits, granting geometric stability to the measure under monomial transformations [cite: 22, 23]. Furthermore, Deninger's vision of Mahler measure as a motivic regulator has been powerfully validated by He and Lee, solidifying the bridge between multivariate cyclotomic polynomials and Dirichlet L-values [cite: 27, 29].

As topological explorations yield startlingly small Fuglede-Kadison determinants in hyperbolic manifolds [cite: 10], and empirical databases exhaustively chart the Elliptic Lehmer landscape [cite: 33], the Mahler measure has transcended its origins as a mere root-bounding function. Whether or not Lehmer's original degree-10 polynomial is eventually proven to hold the absolute minimum measure, the mathematical tools developed to answer the question have irreversibly unified arithmetic geometry, dynamical systems, and topology.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFWtPCyYVJij3bI7NROAdJXRmUXi9Vl2ooF-oTofvBkbUqAhKnWK6_lEoqJ-AFBr4cdypt2QiUd1WYaByBLUbPffdtUU_KdKa5i2imZoUmSFV71Ily_K0g1RvPFsIM_DFTnP38znnL5A==)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3S-tpiyUWtoo7cGDDWu1KDAs7bfCp4sLencO3Sc69Yu17_ce28GPUrzIVq-7toUm3MN6ZTOyGJjlnr05PY04oB123l7_96lCMa_W3VZhb5p5GzsABNeIt9NMxsjIabOa_JdhFA16yc5g=)
3. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHvQ0uSeNu_RtP3g8BM-eK6FphxpiaNnjCeauITqkRcNOzSg6vBXvWHHJK3C8Ah1TVe7y6MMAq_os18h_XxTRPmvtzhB_4iVFAXoYMqGErY5VTgMChZXHeWZftxvI2d-ImwckCbqLHyCilAmQHwOU=)
4. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEepuXSIniCX6U0UNEU1NeF3EXjdIf1NmAtGGZtYx0OgfA_8sBGszvg6bBW7uDPqYB0jKYNQwf2r_FXJlhyDFfGSdCd86RLGl8RoYhzjACYRuUldg1euaW8L7HFnGQpmIHtvoCzPjI=)
5. [uni-goettingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE03LXunL_CJdZioV9kMGBdzcPDJY6FJix7bnSXFpOIOJJXJSvbqQBDmYNfvKyJdIp4pzEY3LpsoAnjisSMnRirXCGhOEVqXCXG-Ma6kROKJcF5pCMdb3JMbYkOThS8Bz7_cSUv9J7J4uQjVI7J6AyRH_jku_vOUVbEDb1dozW6n5U8k6V785QquBO_0C_ztR3DYO3vfGmMolR5Y6VomzaLrhroQIt1)
6. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDjr_8xuVH6KXw-NZNANLl9xQpgBem09EYabaHcl91wAsi4k9tcUiK9U9NGEu1V0yPHJqoqoJNGI1Mh-2w-6ss6dNcd8x96GO_nty-k93prBTR967x8_2wcSWTg7wD0L02xtNhU8c=)
7. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLxtrWYyjsDMdliK2eU4Sn7Px1tPQh6oP1kYAncLPdcn58cbKub-6fHi9RH_lHwU8IfrY9VyEr07Ao_RVsDsgPrpSwJt6B970XQoglAMb6iEyofphp7Pel6ZqMhgHS7ebMmnnL6N0qf_7d33ycEyVZwmocJbGFoZ0=)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0vqkSn-MyRqM0GepUk4sFrBLINcWlydOxBJ5ekhzEhcudgAo3u_Ts34lWhiXzsH5BUMt4GfprponYwV9CNAVOx7QjSTcXyxXwpOrW9O8AC0DBJNWUz36lwcMAO_g-FWiKbHBWbuIpYysBWZA5Ke3u-yXa4OitVVFQuZ7n-iwFA-tPCnEWJMQltw-lOgVWeUW1IJm7j7BXpc5_CI2VUg==)
9. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTjJJRtF3NvVsX7IchdAXb8zIPbwELuhKcRgsEAPUrUF0_vVBLRHhPVdBFjjLN26ESQO-Gy8Z3ByfOtm6SVskuVg-E_yxCP7roDUwbPBNQqMWg7oIQC_w56JginGuamJ09n5xEpucEH9f5lIFF0yEXQ1FuIg==)
10. [spp2026.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_4P4dkZBWMbBM2YvIVYNXnwCZmWkKY9Qduvw1lQBnGKbLGGL7JqwEJoIwbAsoLMeEG3ClJnLBaRsnm0-6s9cMt3k5XgMIawJjz4NnCZE5d5ioaXAMhwRnfQ9ToQEceCsg3ZLdxXAHf0XOpemBh2R4y8zo1uMYUNwuylO2p2VPqfoZDgqe)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAS1L2ihLh2MRy1mnLAZ8hdDRNzOXFtUiExQQFTuiYTp0APL6Q790ginV_xjzvouH9x40mViEPf7Q2FccAUvJ5frLh7wxRuB15QU5yZ8ASNV7MgvvF4w==)
12. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5w4wxNfy_FUlCwI6VZl3DD8VkFoD20JsRcAJ0Kl3sKJrFx8tD9qPasREbDkjHGhvr9oq19h-ocVKd1-nW7BSZwEn1dP1SM-n5BaAxwqDcJIZM33DB0g3wqcpz8lc2PihAEFtyZLj_kHqrLQ==)
13. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHWz1CKuKFXUfXShVxE-Vobbg1tuCZmXBCb1ce9fPrfiVJVC2mhq_hh_sXFTMdM8GDpgzpTQikrPn8HB4lt8pxGQ2rg8ly1gGZAxp7TP7bPEkSzEAkfToFl_Plrhi28AElT3bZ6-9d7ErliE235OInFRJW)
14. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcNyQ-38Bgf34AF7sjd4Q4HuJM5XIU7aDTCbrLZXponotaXMVcVXjYlHvnLtvYmzFU6ShVxYtSsoBU9ODqRP81PlaCePaM4yJ8qSAIdHS22yIA6JnrFrBnzALM0P4JWhqDsmAGsjPcPQX40--P-Jwnm-hUO3lEu9XZsEzvAw1CyP_jBvc=)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtQjTamoZcT8smvHJpQaeR9uXHNZm8K-iWMh2ZHjg5y_RMClVEAZizJsIlR2rA5lqxxj-J8lYm8nhBJL47M5jJJaNLLM8d4vdlhqww_srqAXIScqmlQtgFvzuDdmvWTZtw7WeI7FIat4fk2PocHbPVkb2WoPo-NEVw-jQ21hIHWDvOLIoC-T2yk4qhtTjyyvtgwVEyriHrJQwgt6ZbpddPRIF1RI8=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3uZId6VbxZRnExIwu_D5pKebdv849DfEpD-BGxtVNhZsgj2O4i-3gpKYGlFUcoJjB4ChxpcFY1EJvm8ESN1pcoQ4RS2kABCebfWhLMDhOWslN0nBNbw==)
17. [cuni.cz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE67Wt_0mPYT4mi8nlQdEpZFmXW4ZEVlTpVrGMQ8x1OXSdb0_LA9lxMzGl_x4oeekVQORxHYDFiLXyYhncOhMFsherHg9HUToUAY2b5xsuN_4fYsISVCbvtp7O0ZYFxS99XehCbR706dlTD_YloVzgbBi0b4vXYsUp8d7k_aEjo4b-6251m4Q==)
18. [okstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElXOrp79QFZgPc5nOpHq2VjxMBDjNIlKcGPHE9yAY_qNUhcoGSUQiFkddYog0A6j4JEz0YhoTpfsMgvkIXz9JuaMTCcppicGgcEaTdBudGBWxfXHCXoBOzy_i7oSAEPc_JBK6X3W70oQhaC7Gw3A-gRfafUydxn9CY6_3EAQgTugyKwYTL4Vh76uVF3tCMK1jemtfxUhU_ol6QqFI1nNAUiNofi72T2uwGrQ==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqP5Y2QgOqC5zrwC1uA8sFa7emSn0gVjennSdPH-NqakUaX4to2EdlNHNkszccjl66Wqaamt12w_Qddtg5a5IgwqC9k-jVQcbRws8Irktw44rDB7CjaLhPZF_5iuq6CPC2iifgNzeW6H9BKDY_ZZl_yozgWFlCUXMRo7ptz02ce1Tk5_Ocz-7rwK8rp33zA7p8P1VQFoD_3IMdl6jCxR3rUkRDJ24LHkl-pUfR7Icx30cPsAK_ThHXv3vgcgekO5-NRU6Y42ziQqJyUQeKPvkPUoW99f-UiS20NwXmpVK8QqdDKjpFzj04lA==)
20. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLLcvDsK28HCD1lN5Q1tSzeYG6LaJ1kNcHW-_NrvDnditwFFuPUuxtZsEXFO9wZiOku7IF7zQ8Co27dQJ6hiJpBbrbgrSyuh3LKygFje1z_3gsUD1ykuVHqag7n80YeVLOUJO81YTKEnhOavIwwtbxiWh04QaEOg==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUmmJQJlRBMUb_ILChq23_R4ztYGHv_V_z0s3KEMG7WuT_yD73C4ta5sonB9nzQRA_iu-e23WI2CazCwGxb5wBCTNDgBTISXDfGgZ5n2xMUq1TdbuqpQ==)
22. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6C_uwssA7-8kZXecopPtsmYlrA2lR2fNia0JaoeYZWpg0D26RSb8-vNMZx3oxQyzjgL4ZK3WIW8xTFAt1MD3BkMdJMSN4rMDfCfyW0EjT05Mrv1TdHJoc8vyoNXzltkdUfB__Kaxd)
23. [ens-lyon.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFduMY9Nknd1KEU0okvbftBmkWVM8GYlgIV40xeJX8JGRrekjn8AAnYoD8wI9UuKyG5p4qWXgLNPUG5-mePKVXxEtiSNxp7xCZHwwNZBuyBS0IYjI99D_Nz1w7jpZhWzKn_WOFQ27isaBjt8rhvp2-WNLqZDnrbFkDi-NF6)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1t8tQPY96vEYwLAkfvh0y7cR86u8mcOkx7Gys3bFaf7qktt8eeExJmMQZQPcSz9PHtQABFQYn6jbXj91rKaHNMmMTnpbOMy5ZEDGU-e_9r-P11wIUQIatDc8cYhMip0ND5f0LCpKMczDSazyyzCy9hoSSWJhhcUpxwVoIuIB3lqNXP1GjOkOVkU5rOdCBY1SATsTqmDYUOg==)
25. [scholaris.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3Ds_gEOFqiUGK1GZDwPAod0FA_ya3GPS4g0DdN4ZsDSAYuiYsLwkjsIrVtaOCLCIkmLxsYNRRhljF3XM8RosPbM1pfGdSH3k74dt6L3pXH1pdMiAQ4fdj4yhhxFKLz-oiG83zgsvnw6lXkBLmr4yhpOhi2DyDxZQe3NOmW32s2FzQ-y3wHYTnzuKw2FOZPSn0N42wlTHaM2V74NU=)
26. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnzCZoM-QLtpAn0hfU-FBRNVbTSwCaoTeMuOMRuJviRHg96Hrk9ySBzJoEXuIZHzF6j7D9j-bnlzmOc4WfE2bWaU3XV6HiLrvMvGWiQG4d4pVdzSvyTej9x3pe885vCTKgLhV2gBdP15A=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSP57HdpAZIQpCR8MYDNPI8ZaiUPyybLqL3Tzjy8GmyLv75UObtA4SkL3ILAr_ae5CrV26sKQyjFV7y0v3PbfXybzEnn0TRUcXVmgBJ4UTG5JMfNwmcA==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ-3tM1pej1oND3WIHNSiWWhFVZQcdjQbfr9KXyqZemMH13EXN2GbxXWqNLMS_aAJ2GHr97QgHZLbQ36CQIcNI5HsWWwZxshUn6SYDCY3-2lf9zBtb5arwQJDJrEAV0rDVBJrX_EOW9kkz6DCgcpQAxzJRgLlqGjcJDF9dih_E_FZTHxE5YJjEA2hG3o_wDxquZEcPacn-ZNh4CAKkGjJbnaKlNfGLhQeLOPTxFab6jwh3SqUvOwB5pZujqQGt)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_r7xDrtU5KE_P_QIiAlZ3ubB2K-qlestg0xb8dO07s97PiMkZOlEF4oKT_ZarFW8uoUXFpRmYrpXmhsuPwFMEhtzRev7vZ86Qu8Uar01TOH4oYoZDjQ==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXzEoBFjFynwxlsHIH1XJhFhGG5k6hVc7G5WjZ711JgKF1n_uOc-Pm2H1sGeXkSVDOac9wR3hEVZvNeuyhvYnckavDwt4nLJn2s_i-AFXBPg7BWK5PG65htdCHZqbr4FLuDSWowZjXNQV3yAHlJu07-9adsOdAjvwRD2G5zxeE_FLMzoPa3vpsvNNvhAzqng==)
31. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTSFUPj2sfssYSTzfyHez5Sg5RGSNlQmMw-UZvmy80so3oYMd8tsjPbT2Pz4ttbMqDre_A7wGx2kyrKoZOWYMOV60ifPNjb7u9ZuhGDNZaOSv33oR_iWPVxog8XD2oym8QBQ3Q6D5IAc9xBXUe2g4EdPMAdzDuyirzVmXJgVeQYZi1IlU=)
32. [umontreal.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7zfEMF1O5xTDR5t68ZzzMIqQPcNz8YOsxAcow96IdamWip4KRlKPFNT4xkiKBFIptv6pkQpH2kdXnIKJKtmNPBIJ6julNFi7sU2QKqD2DBEVy19gGVJortUkVa0eq2RARhxdiwQU=)
33. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFFOHgwHtUEQ1m970B16yDeHuRifIN34zaddq8TK435dR9Pl9dANff365yayAu92aFAxrr52MwcREntT2BzZrtDXmKUpDTFD3xPFNlPeGd-k7DMLU5G1fy2Qy62mJQUOoZErRrhg==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWB791wEJulvZvS4cScYFiUaRd51P_HtvmIR90OYuBuUKHg23BImwjofMIixIfFjE9ibNBaX-qEqygDHoWlxhtSRHawa4ygoPhnyNs2K7z4u_LnkWIaA==)
35. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjIo_QcZnjQ7ugE5TOJ0s8SjAhwbLUr-SK2I2pDW8Gaa0zE3WqbmY_H8OJjCySGFkjEQ-lrUPaDmVYcxhbCz5_cjr8tix_fxR61zhxeEMsQBMLErSl4JPj8m9suGQ=)
36. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkPITDLbMa1SJqoqbvANbJNNdh9TIH96ZXWeRa104_AlBhdBrsHDYWbpGcXW2e_Y6cpOKkFHcwjze_xWhPy2Sd_1IG6xvO8E-ECkc-VNkQ36_WOttqS3M1IYcFgNaspWs-)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4Cr4khKWTWhYwqx5laG3x9i8yeR91Nb1Iu5_iko2NzR3EkVh0WR0gZxgtHVaR7ABTNz4iszZPAuTEXf_G0gdppqoBaCwq1Ga6rx90OULPKkmV9J3Img==)
38. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPS0cTF--Z3g24qbdYsIPSXgmN6-8rwCB6ESMGQapn7UHAH3yxb0ZS-dw7vROLrP9JnZJQ7qEc8-tdW_2vF83GC4FxTp09F3Ygkrb-ydDFp_pksCwgc4p1kdjdeVd3gsGcTmxvNO8=)
39. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT0jUQSbp4mr_JlnBZO_Pah7dqDW5OyQoQ_CoLZ9u5IErCVMOZ_RTbT0ufiex-zkvwDh32NESTKXaBJdfd9IET46gT87vtbi1we03iXDJMz_kv5uh344Vj-ovphra3MbkSyRUwYluw8BfsLIL5ha9gi0k=)
40. [pdx.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG10ENv8Y652vaOb1uPukDHBW_BHBN23Xu9wpxvEKhGUGxGafnvBRMZZkA-GZpGqEQU2A2Wr5og0MsOXxEJRw8OoUa2qZDjuDFBVmqy-1QISWxwug_Li9otBICLa7aC3VpfCvpruDyqOH5sW7aUmaAmSbCQ4jOwk37J7UVff2dZ2mJRq4ggvt8ymw==)

