# Thompson Group F: The Amenability Problem

## For Charon — Deep Research Brief

### 1. Definition and Importance

Thompson's group F consists of all piecewise-linear homeomorphisms of [0,1] with:
- Breakpoints at dyadic rationals (k/2^n)
- Slopes that are powers of 2

F is finitely presented with generators x_0, x_1. It embeds in the larger Thompson groups T (circle homeomorphisms) and V (Cantor set homeomorphisms). F is important because it sits precisely at the boundary between amenable and non-amenable groups: it contains no free subgroup (ruling out the easiest non-amenability proof), yet no one has found a Folner sequence (ruling out the easiest amenability proof). It is the most natural candidate for a counterexample to the von Neumann conjecture's "spirit" — a finitely presented group that is non-amenable without containing F_2.

### 2. Amenability: Two Equivalent Definitions

**Invariant mean:** G is amenable if there exists a finitely additive, left-invariant probability measure on all subsets of G. Abelian groups, solvable groups, and groups of subexponential growth are all amenable.

**Folner condition:** G is amenable iff for every finite subset S of G and every epsilon > 0, there exists a finite set A in G with |SA \ A| / |A| < epsilon. These "almost-invariant" finite sets form a Folner sequence.

**Kesten's criterion (1959):** G is amenable iff the spectral radius of the random walk operator on G (with respect to a symmetric generating set) equals 1. Equivalently, the norm ||sum of generators|| in C*_r(G) achieves its maximum.

### 3. Evidence for Non-Amenability

**Cogrowth estimates (Haagerup-Haagerup-Ramirez Solano, 2015):** Extensive numerical computation of the cogrowth series for F with standard generators. Results: ||I + A + B|| ~ 2.95 (amenability requires 3.0) and ||A + A^{-1} + B + B^{-1}|| ~ 3.87 (amenability requires 4.0). The gap is small but persistent, suggesting F is "almost amenable" but not amenable.

**Folner function growth (Moore, 2013):** If F is amenable, its Folner function must grow at least as fast as a tower of exponentials — far faster than any previously known amenable group. This makes constructing explicit Folner sets computationally infeasible.

**Burillo-Cleary-Wiest experiments:** Random walk simulations on Cayley graphs of F show drift behavior consistent with non-amenability.

**Elder-Rechnitzer-van Rensburg:** Cogrowth sequence analysis suggests the universality class is inconsistent with amenability. A rigorous determination of this universality class would likely settle the question.

### 4. Why Standard Techniques Fail

- **No free subgroups:** F is "too abelian" — every pair of elements nearly commutes at infinity. So the Tits alternative and ping-pong arguments don't apply.
- **Not elementary amenable:** F sits outside the closure of abelian groups under extensions and directed unions, so standard amenability constructions fail.
- **Cost = 1:** The L^2-Betti number / cost approach (Gaboriau) cannot distinguish F from amenable groups; F has cost 1, same as Z.
- **The group is "too infinite":** F has exponential growth but is not hyperbolic, not linear, not residually finite. Most machinery requires at least one of these.

### 5. Equivalent Formulations

The amenability of F is equivalent to:

1. **Kesten's criterion:** The spectral radius of the simple random walk on the Cayley graph equals 1.
2. **Ore condition (Bartholdi-Kielak):** For the group ring K[F], any a,b have nonzero solutions to au = bv. This reduces further to the monoid ring K[M] where M is the positive monoid of F. Degree-1 case is solved; general case open.
3. **Folner sets exist** for the Cayley graph of F.
4. **C*_r(T) structure:** F is non-amenable iff the reduced C*-algebra of T is simple (Breuillard-Kalantar-Kennedy-Ozawa).
5. **Vanishing of certain L^2-cohomology obstructions** (though cost alone is insufficient).

### 6. Connection to Operator Algebras

- **C*_r(F):** If F is non-amenable, then C*_r(F) != C*(F), providing a natural example of a finitely presented group where the full and reduced C*-algebras differ.
- **C*_r(T):** Has a unique maximal ideal. F is non-amenable iff C*_r(T) is simple. If F is amenable, C*_r(T) has infinitely many ideals.
- **Von Neumann algebra L(F):** Known to be inner asymptotically abelian. The factor L(F) is a II_1 factor; its properties are sensitive to amenability but current invariants cannot distinguish.
- **C*_r(F) is not residually finite-dimensional**, regardless of amenability — another way F evades standard tests.

### 7. Computational Feasibility (GAP/MAGMA)

**Short answer: No direct Folner computation is feasible.**

- F is infinite and finitely presented, so GAP/MAGMA can work with it as an fp-group, but cannot enumerate Folner sets — Moore's result implies any Folner set (if it exists) is unimaginably large.
- **What IS computable:** Random walk return probabilities (Kesten criterion approximation), cogrowth coefficients via transfer matrices on tree diagrams, and norm estimates in truncated group rings. Haagerup et al. used custom C++ code, not GAP/MAGMA, for their spectral computations.
- **The Ore condition** is testable degree-by-degree in the positive monoid ring, and degree-1 solutions have been found. Higher degrees are computationally intensive but theoretically tractable in GAP with custom routines for the monoid presentation.
- **Best computational path:** Cogrowth universality class determination or systematic Ore-condition testing at increasing degrees in K[M].

---

**Bottom line for Charon:** This is the cleanest "boundary object" in group theory. F is non-amenable by every numerical test, but the gaps are small enough that no computation can be rigorous proof. The Ore condition reformulation (Bartholdi-Kielak) and the C*_r(T) simplicity equivalence are the two most promising theoretical attack vectors. The problem's difficulty stems from F being simultaneously too regular (no free subgroups, cost 1) and too wild (exponential growth, non-elementary) for any existing framework to grip.

## Sources

- [Amenability problem for Thompson's group F: state of the art (Guba, 2023)](https://arxiv.org/abs/2305.07113)
- [A computational approach to the Thompson group F (Haagerup et al., 2015)](https://arxiv.org/abs/1409.1486)
- [Computational explorations of the Thompson group T (Haagerup et al., 2021)](https://arxiv.org/abs/1705.00198)
- [Fast growth in Folner sets for Thompson's group F (Moore)](https://arxiv.org/abs/0905.1118)
- [Maximal ideals of reduced group C*-algebras and Thompson's groups (2024)](https://arxiv.org/abs/2403.13645)
- [On the Ore condition for the group ring of Thompson's group F (2021)](https://arxiv.org/abs/2101.01848)
- [Thompson groups — Wikipedia](https://en.wikipedia.org/wiki/Thompson_groups)
- [Thompson's Group at 40 Years — AIM Problem List](https://aimath.org/WWN/thompsonsgroup/thompsonsgroup.pdf)
- [Amenability of Thompson's group F? — Danny Calegari (Geometry and the Imagination)](https://lamington.wordpress.com/2009/07/06/amenability-of-thompsons-group-f/)
