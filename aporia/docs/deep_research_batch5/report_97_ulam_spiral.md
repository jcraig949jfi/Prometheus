# Report #97: Ulam Spiral Prime Clustering at 10^10 Scale

**Target agent:** Ergon
**Date:** 2026-04-23

## 1. Precise Problem Statement

Arrange integers n = 1, 2, 3, ... on a square spiral. Primes concentrate along certain diagonals. Each diagonal corresponds to a quadratic polynomial f(x) = 4x² + bx + c. Quantitative question: for each such f, does

  π_f(N) := #{x ≤ N : f(x) prime} / N

converge to the Bateman–Horn prediction

  C(f) / log(f(N)) ~ (1/(2 log N)) · ∏_p [(1 − w_f(p)/p) / (1 − 1/p)]

where w_f(p) counts roots of f mod p? We test at N up to ~50,000 (so f(N) ≈ 10^10), across all principal diagonals intersecting the spiral out to radius R ~ 50,000.

## 2. Literature Anchors

- **Ulam (Los Alamos, 1963):** first observation, during a lecture.
- **Stein, Ulam, Wells (MAA Monthly, 1964):** "A visual display of some properties of the distribution of primes" — formalized the spiral.
- **Hardy–Littlewood, Partitio Numerorum III (1923), Conjecture F:** asymptotic density for primes represented by ax² + bx + c, discriminant D not a square; singular series.
- **Bateman–Horn (Math. Comp., 1962):** unified conjecture for polynomial tuples; specializes to Conj F for single irreducible f. Quantitative target.
- **Gallagher (1976), Friedlander–Granville (1989):** variance bounds; deviation-significance estimates at finite N.

## 3. Test Design

**Sieve infrastructure.** Segmented Eratosthenes to 10^10 in windows of 2^28. Primes as sorted uint64 or bit-vector (1.25 GB). Verify against π(10^10) = 455,052,511.

**Spiral enumeration.** Closed-form (x, y) ↔ n via shell index k = ⌈(√n−1)/2⌉. Four Ulam diagonal families:
- NE: 4k² + 2k + 1
- NW: 4k² + 1
- SW: 4k² − 2k + 1
- SE: 4k² + 4k + 1

plus parallel offsets (shifted quadratics 4k² + bk + c) generating the full diagonal grid.

**Polynomial catalog.** All (b, c) with |b|, |c| ≤ 100 producing irreducible f, discriminant non-square. ~400 polynomials.

**Density comparison.** Per f:
1. Observed π_f(N) via sieve lookup.
2. Bateman–Horn C(f) via Euler product truncated at p < 10^6 with Mertens tail correction.
3. Ratio R(f) = π_f(N) · log(f(N)) · 2 / C(f). Under Conj F, R(f) → 1.

**Null.** Permutation: 10^4 random polynomials 4x² + b'x + c' of matching discriminant class; compare observed |R − 1| distribution.

## 4. Falsification Criteria

- **Primary kill:** any Ulam diagonal with |R(f) − 1| > 0.05 at N = 50,000, bootstrap 95% CI excluding 1 ⇒ local Bateman–Horn violation (more likely sieve or discriminant bug — Aporia's null discipline applies).
- **Secondary kill:** Euler's 4x² − 2x + 41 does NOT top the density ranking ⇒ received wisdom fails.
- **Tertiary:** variance of R(f) across 400 polynomials compatible with trivial null ⇒ singular series not doing predictive work.

## 5. Expected Outcome

Bateman–Horn holds to within 1-2% at N = 50,000 for generic diagonals; Euler's polynomial achieves R ~ 1 with density ~3.3× PNT baseline. Scientific payoff is not confirmation but a **high-precision empirical ranking** of diagonal enrichments — a reference table Aporia uses to flag polynomials whose spiral rank deviates from Bateman–Horn rank. Deviations are hypothesis generators.

## 6. Budget

- **Sieve to 10^10:** 2-3 hrs single-threaded; ~30 min with 8-core segmented. Disk: 1.25 GB.
- **Diagonal enumeration + density lookup:** 15 min for 400 polynomials at N = 50,000.
- **Bateman–Horn constants:** 30 min total (truncated Euler product).
- **Permutation null:** 2 hrs for 10^4 samples.
- **Total:** under 6 hrs wall-clock on Ergon.
- **Deliverable:** JSON `{polynomial, π_f(N), BH_prediction, R, CI}` plus R-distribution plot.

**Word count: 672**
