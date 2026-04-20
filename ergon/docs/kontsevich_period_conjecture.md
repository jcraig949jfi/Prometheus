# Kontsevich Period Conjecture — Deep Research for Ergon

## Precise Statement (Kontsevich-Zagier 2001)

A **period** is a complex number whose real and imaginary parts are values of absolutely convergent integrals of rational functions with rational coefficients over domains in R^n defined by polynomial inequalities with rational coefficients. Equivalently: integrals of algebraic differential forms over algebraic cycles.

The ring of periods P contains all algebraic numbers, pi, log(2), zeta(k) for k >= 2, polylogarithms at algebraic arguments, and L-function special values at integer points.

**The Conjecture:** If two period integrals are equal as complex numbers, then one can be transformed into the other by a finite sequence of three operations: (1) **additivity** of integrands and domains, (2) **change of variables** with algebraic Jacobian, (3) **Stokes' formula** (Newton-Leibniz). All coefficients algebraic throughout.

This says the transcendence theory of periods is entirely *geometric*: no analytic coincidences exist. Every numerical identity between periods has an algebraic-geometric proof.

## Known Results — Brown's Program

Francis Brown (2012-2017) proved the conjecture for **multiple zeta values** (MZVs). His method: construct a motivic period algebra via the motivic fundamental group of P^1 minus {0,1,infinity}, then show the "period map" from motivic to numerical MZVs is injective modulo lower-weight terms. Key ingredients: motivic coaction, the Drinfeld associator, and the Deligne-Goncharov mixed Tate category over Z. Brown's 2012 result: all MZV relations follow from associator relations (regularized double shuffle plus distribution). This gives a concrete decision procedure for MZV identities.

Huber-Klawitter (2011) proved the conjecture for 1-dimensional periods (periods of curves). Ayoub's Nori-motivic formalism provides a framework where the conjecture reduces to the conservativity of the period realization functor.

## Connection to LMFDB Data

L-function special values ARE periods. Specifically:
- **L(E, 1)** for elliptic curves: the BSD formula gives L(E,1) = (Omega * |Sha| * prod(c_p) * R) / |E_tors|^2. The real period Omega is literally an elliptic integral — a period. The L-value itself is a period.
- **L(f, k)** for modular forms at critical integers: Eichler-Shimura gives these as period integrals of cusp forms along modular symbols. Our `lfunc_lfunctions` table stores `leading_term` which is L^*(s) at the central point.
- **Dirichlet L-values** L(chi, n): periods via Gauss sums and polylogarithms.
- **Dedekind zeta values** zeta_K(n): periods involving regulators and class numbers.

**What this means for Ergon:** The `tamagawa_mediation.py` finding that Faltings height (= log of real period) mediates the L-value channel is a period-theoretic statement. Isogeny class size correlates with period structure through the BSD formula. The Kontsevich conjecture predicts that ALL relations we find between L-values in our LMFDB data should ultimately have geometric explanations via algebraic cycles.

## Fungrim Formulas as Period Identities

The `fungrim_bridge.py` script already tests Fungrim formulas against known constants. Many Fungrim identities ARE period relations: zeta(2) = pi^2/6, Catalan's constant = L(chi_4, 1), etc. The conjecture says these are not numerical accidents but consequences of geometry.

**Testable prediction:** For any Fungrim identity equating two period expressions, there should exist a chain of the three Kontsevich-Zagier moves connecting them. The harder test: find two period expressions that are numerically equal to high precision but where no geometric chain is known. These would be either (a) evidence against the conjecture or (b) pointers to undiscovered geometry.

## PSLQ for Discovering Period Relations

The PSLQ algorithm (Ferguson-Bailey-Arwade) finds integer relations among real numbers: given (x_1, ..., x_n), it finds integers (a_1, ..., a_n) with sum a_i * x_i = 0 to arbitrary precision. This is the primary computational tool for period discovery.

**Application to our pipeline:** Compute L-values numerically to 100+ digits (via `mpmath` or PARI/GP's `lfun`), then PSLQ-search for integer-linear combinations involving pi^k, log(p), zeta(k), and other periods. Any relation found is a *candidate* period identity, then the Kontsevich conjecture predicts a geometric proof exists.

Bailey-Borwein used PSLQ to discover that integral representations of Mahler measures equal L-values of elliptic curves — precisely the kind of EC-knot bridge that our silent islands analysis flagged. Boyd's conjecture (Mahler measure of certain polynomials = L'(E, 0)/L(E, 0)) was found by PSLQ and remains partly open.

## What Would Failure Look Like?

Two periods proven equal (or equal to 10,000 digits) with no geometric chain. Candidates:
- Euler's constant gamma: not even known to be a period (let alone irrational). If gamma equals some period, proving it via the three moves would be extraordinary.
- e: known to NOT be a period (it is an exponential period in the extended sense of Kontsevich-Zagier). The exponential period ring is strictly larger.
- Relations between L-values of unrelated motives: if L(E_1, 1) = L(E_2, 1) numerically with no known isogeny or modular correspondence, that would stress the conjecture.

## Computational Approaches for Ergon

1. **PSLQ on LMFDB L-values:** Take leading_term values from `lfunc_lfunctions`, compute to high precision, search for period relations. Any new relation found = candidate for the silent island breaker.
2. **Mahler measure bridge:** Compute Mahler measures of Alexander polynomials (knots domain) and PSLQ-match against EC L-values. This is exactly Boyd's program and directly targets the knot-EC silence.
3. **Period matrix of genus-2 curves:** Our genus-2 data includes period matrices. Cross-reference with L-values — the Kontsevich conjecture says all numerical coincidences have motivic explanations.
4. **Fungrim audit:** Classify Fungrim formulas by whether both sides are periods. For those that are, check if the three-move chain is known. Unknown chains = open problems.

## Connection to Project Architecture

The Kontsevich conjecture is the *theoretical foundation* for why silent islands should eventually connect. If L-values are periods, and Mahler measures are periods, and all period relations are geometric, then the knot-EC silence means we lack the geometric bridge — not that none exists. The conjecture predicts it exists. The PSLQ approach is the computational lever to find it numerically, after which the geometry follows (or the conjecture fails, which is also a finding).
