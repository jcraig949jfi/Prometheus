# Fakhruddin's Uniform Boundedness Conjecture for Rational Preimage Trees

## Precise Statement

Let f: P^1 -> P^1 be a rational map of degree d >= 2 defined over a number field K with [K:Q] <= D. The **full backward orbit tree** of a point P is the union of all iterated preimages: f^{-1}(P), f^{-2}(P), ... The conjecture, formulated by Fakhruddin in his 2003 paper "Questions on self maps of algebraic varieties" (J. Ramanujan Math. Soc.), asserts: there exists a constant B(d,D) such that for ANY degree-d rational map f over ANY number field K of degree at most D, the number of K-rational preperiodic points of f is at most B(d,D). This extends Morton-Silverman (1994), which conjectured the same bound but only for **periodic** points. Fakhruddin's formulation covers the entire preperiodic tree: periodic points plus their full backward orbit of strictly preperiodic points.

## Connection to Bombieri-Lang

The strategy for proving uniform boundedness, pioneered by Caporaso-Harris-Mazur (1997) for curves of genus g >= 2, transfers to dynamics via **iterated fiber products**. Given f: P^1 -> P^1, define X_n as the n-th iterated fiber product: the variety parametrizing n-tuples (x_1,...,x_n) where f(x_i) = x_{i-1}. For large n, these varieties are of **general type** (high-dimensional analogues of high-genus curves). The Bombieri-Lang conjecture predicts that rational points on varieties of general type are not Zariski dense. By the Caporaso-Harris-Mazur argument, this non-density + a fibration structure forces a uniform bound on rational points across all fibers, yielding B(d,D). The difficulty: proving X_n is of general type requires controlling the singularities of iterated fiber products, which become increasingly complex. This geometric step is the main technical obstacle.

## Known Unconditional Results

For quadratic polynomials f_c(z) = z^2 + c over Q: no rational periodic points of period 4 exist (Morton 1998, Flynn-Poonen-Schaefer 1997), and period 5 is ruled out by Stoll (2008). Period 6 exclusion is conditional on the Birch and Swinnerton-Dyer conjecture. Poonen (1998) conjectured the **complete classification**: assuming no rational period >= 4, there are exactly 12 possible preperiodic portrait graphs, and the maximum number of Q-rational preperiodic points is **9** (achieved by f_c with c = -29/16, giving portrait type (2,1) with 9 points). So the conjectured bound is B(2,1) = 9. This has been computationally verified for c up to height 10^8 but remains unproven.

Fakhruddin proved a key structural result: the dynamical uniform boundedness conjecture for P^1 **implies** uniform boundedness for torsion points on abelian varieties. This was motivated by Poonen's observation that Morton-Silverman for degree-4 maps implies Merel's theorem (uniform boundedness of torsion on elliptic curves). Fakhruddin generalized this to all abelian varieties, showing dynamics is logically **stronger** than classical arithmetic geometry conjectures.

## Doyle-Faber-Krumm: Computational Approach

Doyle, Faber, and Krumm (2014, New York J. Math.) systematically computed preperiodic structures for quadratic polynomials over number fields. They constructed **dynamical modular curves** Y_1(n) parametrizing maps with a point of exact period n, analogous to classical modular curves for elliptic curves. Their key results: they determined which dynamical modular curves have infinitely many quadratic points, yielding a complete classification of possible preperiodic portraits over quadratic fields. More recently (2023-2025), Doyle-Krumm and Doyle-Galarraga extended this to cubic points, showing the dynamical modular curve approach can systematically attack uniform boundedness degree by degree.

## Iterated Fiber Products: Why They Are Hard

Given f: P^1 -> P^1, the n-th fiber product X_n = P^1 x_{f} P^1 x_{f} ... x_{f} P^1 (n copies) parametrizes length-n backward orbits. The K-rational points of X_n correspond exactly to chains x_0, x_1,...,x_{n-1} with f(x_{i+1}) = x_i, all defined over K. The dimension of X_n grows linearly with n, and for large n the canonical bundle becomes ample (general type). However, X_n inherits singularities from the critical points of f, and these accumulate under iteration. Resolving these singularities while maintaining control of the canonical class is the central difficulty. For polynomial maps, the situation is slightly better since infinity is totally invariant, but for general rational maps the geometry of X_n remains largely intractable.

## Computational Search for Extremal Trees

In SageMath, one can search for extremal preimage trees over Q by iterating f_c^{-n}(0) for rational c and tracking which preimages remain rational. The command `f.rational_preimages(P)` in Sage's dynamics library computes one level; iterating gives the backward orbit tree. The known extremal case for quadratic maps: c = -29/16 gives 9 preperiodic points (the conjectured maximum). For degree-3 polynomials, no systematic search has been completed, but Morton-Silverman predicts B(3,1) should be finite. The genetic algorithm approach of Chua-Hutz-Winburn (2025) automates the search for extremal examples across parameter families.
