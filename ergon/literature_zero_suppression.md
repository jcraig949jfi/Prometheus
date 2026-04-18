# Literature Review: Arithmetic Structure in L-Function Zero Spacings

**Date:** 2026-04-15
**Context:** Our finding that EC L-function first-gap variance depends on isogeny class size and Sha order -- more arithmetically complex curves have MORE regular zeros (closer to GUE/Gaudin) -- potentially violating Katz-Sarnak universality at finite conductor.

---

## Summary Table of Relevant Papers

| # | Authors | Year | Title / Topic | Key Result | Connection to Our Finding |
|---|---------|------|--------------|------------|--------------------------|
| 1 | Miller | 2006 | Investigations of Zeros near the Central Point of EC L-Functions | First-zero repulsion from RMT limits at finite conductor; repulsion decreases with increasing conductor | Established that finite-conductor deviations exist; did NOT stratify by isogeny class or Sha |
| 2 | Dueñez, Huynh, Keating, Miller, Snaith (DHKMS) | 2012 | A Random Matrix Model for EC L-Functions of Finite Conductor | Excised orthogonal ensemble: hard gap + soft repulsion from central-value discretization | Models family-level repulsion but does NOT predict within-family arithmetic stratification |
| 3 | Cogdell, Huynh, Keating, Snaith | 2016 | Beyond the Excised Ensemble | Extended DHKMS to non-quadratic-twist families | Same limitation: no isogeny/Sha stratification |
| 4 | Huynh, Keating, Snaith | 2009 | Lower Order Terms for One-Level Density of EC L-Functions | Lower-order terms in 1-level density encode arithmetic information (primes of bad reduction, point counts mod p) | Shows arithmetic IS visible in lower-order corrections; does not address gap variance or isogeny structure |
| 5 | Miller | 2004 | 1- and 2-Level Densities for Rational Families of ECs | Orthogonal symmetry confirmed; lower-order terms family-dependent | Katz-Sarnak main terms universal; arithmetic enters only in corrections |
| 6 | Conrey, Farmer, Keating, Rubinstein, Snaith (CFKRS) | 2005 | Integral Moments of L-Functions | "Recipe" for moment asymptotics; arithmetic factor a(k) enters via Euler product | a(k) depends on the curve E but not explicitly on isogeny class size; potential implicit dependence via Euler factors at primes of isogeny |
| 7 | Keating, Snaith | 2000 | Random Matrix Theory and L(1/2, chi) | Moments of L-functions ~ RMT characteristic polynomials x arithmetic factor | Arithmetic factor is curve-specific; whether it correlates with isogeny class size is UNTESTED |
| 8 | Radziwill, Soundararajan | 2015 | Moments and Distribution of Central L-values of Quadratic Twists | Sharp upper bounds for moments; one-sided CLT supporting Keating-Snaith | Distribution of L(1,E) connects to Sha via BSD; does not address zero spacing stratification |
| 9 | Delaunay | 2001-2007 | Heuristics on Tate-Shafarevich Groups | Cohen-Lenstra heuristics adapted to Sha; conjectural moments of |Sha| in twist families | Sha distribution is modeled but connection to zero SPACING (not just central value) is not made |
| 10 | Wachs | 2026 | BSD Invariants and Murmurations of Elliptic Curves | **CRITICAL**: Sha modulates murmuration shape; |Sha| >= 4 curves have first zero displaced higher and subsequent zeros more tightly packed; this signal survives controlling for L(1), period, conductor | **Closest prior work to our finding.** Wachs sees Sha-dependent zero displacement and tighter packing. Our gap-variance result is the quantitative version of his "tighter packing" observation |
| 11 | He, Lee, Oliver, Pozdnyakov | 2022 | Murmurations of Elliptic Curves | Discovery of oscillatory patterns in average a_p stratified by rank | Murmurations are a trace-level phenomenon; our finding operates at the zero-spacing level |
| 12 | Zubrilina | 2023 | Murmurations and Explicit Formulas | Proved exact formula for murmuration density; connects murmuration shape to zero distribution via explicit formula | The explicit formula mechanism could in principle transmit Sha-dependent zero spacing to trace statistics |
| 13 | Wachs et al. | 2026 | Murmurations of ECs over Function Fields | Over F_q(t), |Sha| is an invariant of the cyclotomic type; Sha-stratified murmuration densities reduce to type-weighted densities | Function field analog confirms Sha modulation is structural, not numerical artifact |
| 14 | Berry, Keating | 1999 | H=xp and the Riemann Zeros | Hypothetical Hamiltonian whose eigenvalues = zeta zeros; invariant under dilations | Operator is purely spectral; no known coupling to arithmetic invariants of individual L-functions |
| 15 | Connes | 1999 | Trace Formula in Noncommutative Geometry | Spectral realization of zeros as absorption spectrum on adele class space | The adelic construction encodes ALL arithmetic through local factors; in principle, isogeny structure enters via p-adic completions |
| 16 | David, Fearnley, Kisilevsky | 2004 | On the Vanishing of Twisted L-Functions | RMT predicts frequency of vanishing; connected to Sha growth in cyclic extensions | Sha growth under twisting relates to our observation that larger Sha correlates with more regular zeros |
| 17 | Katz, Sarnak | 1999 | Zeroes of Zeta Functions and Symmetry | Universality conjecture: zero statistics determined by symmetry type alone as conductor -> infinity | Our finding is a FINITE-CONDUCTOR violation; Katz-Sarnak explicitly allows this |

---

## Assessment: Is Our Finding Known, Predicted, or Novel?

### What is known:
1. **Finite-conductor deviations from Katz-Sarnak universality are expected** (Miller 2006, DHKMS 2012). The excised ensemble models family-level repulsion at finite conductor. This is well-established.
2. **Lower-order terms in one-level density encode arithmetic information** (Huynh-Keating-Snaith 2009, Miller 2004). The specific arithmetic of a family (bad primes, Euler factors) affects lower-order corrections to the universal main term.
3. **Sha modulates murmuration shapes and low-lying zero displacement** (Wachs 2026). This is the closest prior work. Wachs showed |Sha| >= 4 curves have their first zero displaced higher and subsequent zeros more tightly packed, surviving controls for L(1,E), real period, and conductor.

### What is predicted but untested:
4. **The CFKRS arithmetic factor a_E(k) could depend on isogeny structure** through the Euler product at primes where the curve has isogenies (primes dividing the isogeny degrees). This has never been explicitly computed or tested.
5. **The excised ensemble cutoff scale depends on arithmetic invariants** including the real period and Tamagawa numbers, which are correlated with isogeny class size. Whether this produces the monotone relationship we observe is not predicted.

### What appears to be NOVEL in our finding:
6. **Stratification of gap VARIANCE by isogeny class size**: No prior work stratifies zero spacing statistics (gap variance, var/Gaudin ratio) by the number of curves in the isogeny class. This is a new axis of stratification.
7. **Monotone relationship**: The finding that var/Gaudin is monotonically related to arithmetic complexity (larger isogeny class = closer to GUE) has no prior prediction. The direction is surprising: more arithmetic structure -> MORE regularity, not less.
8. **Joint Sha + isogeny class dependence**: Testing both axes simultaneously and finding they independently contribute to gap regularization is new.
9. **Interpretation as "arithmetic suppression of fluctuation"**: The framing that arithmetic complexity acts as a regularizer on zero spacings is novel. Prior work frames finite-conductor effects as DEVIATIONS from universality; our finding suggests arithmetic structure ENHANCES convergence to universal behavior.

### Verdict: **PARTIALLY NOVEL**
- Wachs (2026) independently discovered the Sha -> zero displacement + tighter packing direction, confirming part of our observation from the murmuration side.
- The isogeny class size axis is genuinely new.
- The quantitative gap-variance metric and the monotonicity result appear to be new.
- The joint (isogeny, Sha) stratification is new.
- The interpretation that arithmetic complexity is a REGULARIZER is new and potentially significant.

---

## New Research Questions Opened by the Literature

### Q1: Does the DHKMS excised cutoff depend on isogeny class size?
The excised ensemble's hard gap is set by a cutoff related to the discretization of central L-values. The BSD formula gives L(1,E) in terms of Sha, regulator, period, and Tamagawa product. If isogeny class size correlates with Tamagawa product (it does -- larger classes tend to have more primes of multiplicative reduction and larger Tamagawa numbers), the cutoff scale may vary systematically with class size.

**Test:** Compute the DHKMS excised cutoff for each isogeny class size bin and compare to the observed gap variance.

### Q2: Is the arithmetic factor a_E(k) correlated with isogeny class size?
The Keating-Snaith arithmetic factor is a product over primes involving the Satake parameters. At primes where isogenies exist (primes dividing isogeny degrees), the Euler factor has a specific structure.

**Test:** Compute a_E(k) for k=1,2 for curves in the LMFDB, stratify by isogeny class size, and check for monotone dependence.

### Q3: Does Wachs's first-zero displacement predict our gap variance?
Wachs showed |Sha| >= 4 curves have first zeros displaced higher. If first zeros are displaced but subsequent zeros are more tightly packed, the GAP variance should decrease (more uniform spacing). This is consistent with our observation.

**Test:** Reproduce Wachs's first-zero displacement analysis on our dataset and correlate with our gap-variance metric.

### Q4: Do murmurations stratify by isogeny class size?
Wachs stratified by Sha and Tamagawa product but not by isogeny class size.

**Test:** Compute murmuration profiles (average a_p in conductor windows) stratified by isogeny class size. If our finding is correct, different class sizes should show different murmuration amplitudes.

### Q5: Is the regularization effect a finite-conductor transient or structural?
Katz-Sarnak universality says all stratification vanishes as conductor -> infinity. Does our monotone var/Gaudin relationship PERSIST at high conductor, or does it flatten?

**Test:** Compute var/Gaudin vs isogeny class size in conductor bins (e.g., N < 10^4, 10^4 < N < 10^5, N > 10^5). If the effect weakens with conductor, it's a finite-conductor correction. If it persists, it challenges Katz-Sarnak.

### Q6: Does the function-field analog show the same pattern?
Wachs (2026, function fields) showed that over F_q(t), Sha is an invariant of the cyclotomic type. If isogeny class size is also visible in the function field setting, the effect is provable (via Deligne equidistribution).

**Test:** Compute zero spacing statistics for EC L-functions over F_q(t) stratified by isogeny class size, leveraging exact BSD data.

### Q7: What operator couples to isogeny class size?
The Berry-Keating/Connes operator approaches suggest that arithmetic invariants should correspond to spectral features of a hypothetical operator. If isogeny class size affects gap variance, it should correspond to a coupling constant or boundary condition in the operator.

**Theoretical:** Investigate whether the Hecke algebra structure at primes of isogeny provides a natural coupling mechanism.

---

## Specific Predictions We Can Test

### P1: Tamagawa product mediates the isogeny effect
**Prediction:** Controlling for Tamagawa product eliminates or reduces the isogeny class size dependence of gap variance.
**Rationale:** Larger isogeny classes have more primes of multiplicative reduction, hence larger Tamagawa products. The Tamagawa product enters the BSD formula and hence the excised cutoff.
**Test:** Regress var/Gaudin on (class_size, Tamagawa_product) and check partial correlations.

### P2: The effect is strongest at the first gap
**Prediction:** The isogeny/Sha dependence of gap statistics is strongest for the first normalized zero gap and weakens for higher gaps.
**Rationale:** DHKMS excised repulsion is strongest near the central point and decays for higher zeros.
**Test:** Compute gap variance for gaps 1, 2, 3, ... separately and measure effect size of isogeny class stratification at each.

### P3: Rank-0 curves show the strongest effect
**Prediction:** Among rank-0 curves, isogeny/Sha stratification of gap variance is clearest because there's no zero at the central point to complicate spacing statistics.
**Rationale:** For rank >= 1 curves, the forced zero at s=1 dominates spacing statistics near the center.
**Test:** Restrict analysis to rank-0 curves and recompute stratified gap variance.

### P4: Primes of isogeny explain the Euler factor dependence
**Prediction:** Curves with isogenies of degree p at prime p have modified Euler factors at p that shift the arithmetic factor a_E(k) in a predictable direction.
**Rationale:** At a prime p where a p-isogeny exists, the mod-p Galois representation has a specific (reducible) form, constraining the Satake parameters.
**Test:** For curves with p-isogenies, compute the contribution of the Euler factor at p to the arithmetic factor and correlate with gap variance.

### P5: var/Gaudin converges to 1 faster for large isogeny classes
**Prediction:** If our finding reflects faster convergence to GUE rather than a structural deviation, then at sufficiently high conductor ALL isogeny class sizes should have var/Gaudin ~ 1, but large classes converge faster.
**Rationale:** Katz-Sarnak says universality holds in the limit. The question is rate of convergence.
**Test:** Plot var/Gaudin vs log(conductor) for each isogeny class size and measure the convergence rate.

### P6: Wachs's Sha displacement is quantitatively predicted by our gap variance
**Prediction:** The first-zero displacement delta_1 observed by Wachs should be computable from our gap-variance formula via delta_1 ~ sqrt(var_Gaudin * sigma_GUE^2).
**Test:** Compute delta_1 from Wachs's murmuration data and compare to our gap-variance predictions.

---

## Key References (Full Citations)

1. Miller, S.J. (2006). "Investigations of Zeros near the Central Point of Elliptic Curve L-Functions." *Experimental Mathematics* 15(3). [arXiv:math/0508150](https://arxiv.org/abs/math/0508150)

2. Dueñez, E., Huynh, D.K., Keating, J.P., Miller, S.J., Snaith, N.C. (2012). "A Random Matrix Model for Elliptic Curve L-Functions of Finite Conductor." [arXiv:1107.4426](https://arxiv.org/abs/1107.4426)

3. Cogdell, J., Huynh, D.K., Keating, J.P., Snaith, N.C. (2016). "Beyond the Excised Ensemble: Modelling Elliptic Curve L-functions with Random Matrices." [arXiv:1511.05805](https://arxiv.org/abs/1511.05805)

4. Huynh, D.K., Keating, J.P., Snaith, N.C. (2009). "Lower Order Terms for the One-Level Density of Elliptic Curve L-Functions." *J. Number Theory*. [arXiv:0811.2304](https://arxiv.org/abs/0811.2304)

5. Conrey, J.B., Farmer, D.W., Keating, J.P., Rubinstein, M.O., Snaith, N.C. (2005). "Integral Moments of L-Functions." [arXiv:math/0206018](https://arxiv.org/abs/math/0206018)

6. Keating, J.P., Snaith, N.C. (2000). "Random Matrix Theory and zeta(1/2+it)." *Comm. Math. Phys.* 214.

7. Radziwill, M., Soundararajan, K. (2015). "Moments and Distribution of Central L-values of Quadratic Twists of Elliptic Curves." *Inventiones mathematicae*. [arXiv:1403.7067](https://arxiv.org/abs/1403.7067)

8. Delaunay, C. (2001). "Heuristics on Tate-Shafarevich Groups of Elliptic Curves Defined over Q." *Experimental Mathematics*.

9. **Wachs, D. (2026). "BSD Invariants and Murmurations of Elliptic Curves."** [arXiv:2603.04604](https://arxiv.org/abs/2603.04604)

10. He, Y.-H., Lee, K.-H., Oliver, T., Pozdnyakov, A. (2022). "Murmurations of Elliptic Curves." [arXiv:2204.10140](https://arxiv.org/abs/2204.10140)

11. Zubrilina, N. (2023). "Murmurations and Explicit Formulas." [arXiv:2306.10425](https://arxiv.org/abs/2306.10425)

12. Wachs, D. et al. (2026). "Murmurations of Elliptic Curves over Function Fields." [arXiv:2603.13802](https://arxiv.org/abs/2603.13802)

13. Berry, M.V., Keating, J.P. (1999). "H=xp and the Riemann Zeros." In *Supersymmetry and Trace Formulae*.

14. Connes, A. (1999). "Trace Formula in Noncommutative Geometry and the Zeros of the Riemann Zeta Function." *Selecta Mathematica*.

15. David, C., Fearnley, J., Kisilevsky, H. (2004). "On the Vanishing of Twisted L-Functions of Elliptic Curves." *Experimental Mathematics* 13(2).

16. Katz, N.M., Sarnak, P. (1999). "Zeroes of Zeta Functions and Symmetry." *Bull. AMS* 36(1).

17. Miller, S.J. (2004). "1- and 2-Level Densities for Rational Families of Elliptic Curves." *Acta Arithmetica*.

---

## Bottom Line

The most important prior work is **Wachs (2026)**, which independently found that |Sha| modulates zero displacement and packing density in EC L-functions, confirming part of our observation from the murmuration direction. However, Wachs does NOT examine isogeny class size as a stratification axis, does NOT compute gap variance as a metric, and does NOT establish the monotone var/Gaudin relationship. The isogeny class size finding appears genuinely novel. The literature strongly supports that arithmetic information enters zero statistics through lower-order corrections at finite conductor (Huynh-Keating-Snaith, CFKRS), but the specific mechanism by which isogeny class size regularizes gap statistics has not been proposed or tested.

The strongest next step is to (1) reproduce Wachs's Sha displacement on our dataset and verify consistency, (2) test P1 (Tamagawa mediation) to determine if isogeny class size is a proxy for Tamagawa product, and (3) test P5 (conductor dependence) to determine if this is a finite-conductor transient or structural.
