# Paper References — Charon literature pinning

Compiled across today's session. For F011 paper methods + discussion sections.

## Primary theoretical references (citations to lock)

### Katz-Sarnak universality theorem (Axis 1 + Axis 3b)
- **Katz, N. M. & Sarnak, P.** (1999). "Random Matrices, Frobenius Eigenvalues, and Monodromy." AMS Colloquium Publications, Vol. 45.
  - Chapters 1-3: universality of classical group families.
  - Section 3.3: 2-point density corrections per symmetry class (source for nbp-sign bridge).
  - Section 5: local spacing distributions.

### 1-level density for EC / modular form families (Axis 1)
- **Iwaniec, H., Luo, W. & Sarnak, P.** (2000). "Low lying zeros of families of L-functions." Publ. Math. Inst. Hautes Études Sci. 91, 55-131.
  - Sections 4-5: 1-level density formulas for even/odd weight-2 modular form families.
  - Source for <x_1>_O+ ≈ 0.503 and <x_1>_O- ≈ 0.862 under Katz-Sarnak scaling.
- **Young, M. P.** (2005/2006). "Low-lying zeros of families of elliptic curves." J. Amer. Math. Soc. 19, 205-250.
  - Refines ILS to strict-rank EC family with explicit conductor normalization.

### USp(4) / genus-2 families (Axis 1, 2)
- **Miller, S. J.** (2004). "One- and Two-Level Densities for Rational Families of Elliptic Curves: Evidence for the Underlying Group Symmetries." Compositio Math. 140, 952-992.
- **Dueñez, E. & Miller, S. J.** (2009). "The effect of convolving families of L-functions on the underlying group symmetries." Proc. London Math. Soc. 99, 787-820.
  - Family symmetry assignment for G2C and products.

### Related universality work
- **Rudnick, Z. & Sarnak, P.** (1996). "Zeros of principal L-functions and random matrix theory." Duke Math. J. 81, 269-322.
  - Foundational: universality of bulk 2-point correlation across all L-function families.
- **Odlyzko, A. M.** (1987). "On the distribution of spacings between zeros of the zeta function." Math. Comp. 48, 273-308.
  - Original empirical GUE confirmation on ζ(s) zeros.

## Specific-value references (numerical predictions)

- <x_1>_{O+(2N)} ≈ 0.503 (ILS 2000 Table 1; numerical integration of 1 - sin(2πx)/(2πx) + δ(x)/2 × x)
- <x_1>_{O-(2N+1)} ≈ 0.862 (same, with forced central zero)
- **Ratio O-/O+ ≈ 1.71** — observed 1.72 (MATCH to 0.2%)
- <x_1>_{USp(2N)} ≈ 0.72 (asymptotic)
- <x_1>_{USp(4)} ≈ 0.81 (finite-N)
- **USp(4)/O+ ratio ≈ 1.61** — observed 2.29 (DEVIATES by 45%; may be degree-4 finite-N correction or beyond-theory)

## nbp-sign bridge (Axis 3b theoretical anchor)

Katz-Sarnak 1999 Sec 3.3 gives 2-point correlation corrections at finite N:
  R_2^{O+}(x)  = R_2(x) + (1/2)(sin πx/πx)(1 - δ(x))    [POSITIVE sin term]
  R_2^{O-}(x)  = R_2(x) + (1/2)(sin πx/πx)(1 + δ(x))    [POSITIVE sin term]
  R_2^{USp}(x) = R_2(x) - (1/2)(sin πx/πx)              [NEGATIVE sin term]

Orthogonal families (O+/O-) → POSITIVE correction → nbp ρ > 0 (observed +1.0)
Symplectic family (USp) → NEGATIVE correction → nbp ρ < 0 (observed -0.9)

Per-curve interpretation (our contribution):
  Bad prime count (nbp) encodes Euler-factor simplification.
  At high nbp, the universal R_2 correction becomes per-curve observable.
  Sign of the correction = sign of the family-averaged KS correction.

## Lehmer spectrum (F014:P040 section)

- **Lehmer, D. H.** (1933). "Factorization of certain cyclotomic functions." Ann. Math. 34, 461-479.
  - Original polynomial with M ≈ 1.17628.
- **Smyth, C. J.** (1971). "On the product of the conjugates outside the unit circle of an algebraic integer." Bull. London Math. Soc. 3, 169-175.
  - Non-reciprocal bound 1.3247 (Pisot number).
- **Mossinghoff, M. J.** (1998+). "Polynomials with small Mahler measure." Math. Comp. 67, 1697-1705 (and subsequent updates).
  - Exhaustive tables of small-Mahler-measure polynomials up to degree 44.
- **Boyd, D. W.** (1998). "Mahler's measure and special values of L-functions." Experiment. Math. 7, 37-82.
  - Deninger-Boyd bridge to L(E,2) for elliptic curves.
- **McMullen, C. T.** (2002). "Dynamics on K3 surfaces: Salem numbers and Siegel disks." J. Reine Angew. Math. 545, 201-233.
  - K3 surface automorphisms have Salem polynomial characteristic polynomials.

## CM EC classification (V-GAMMA section)

- **Olga Balkanova, Dmitri Frolenkov** — recent work on CM EC L-function statistics.
- **Heegner numbers**: classical list {-3, -4, -7, -8, -11, -19, -43, -67, -163}, class number 1 imaginary quadratic.
- **Non-maximal orders**: {-12, -16, -27, -28} are orders of conductor > 1 in Heegner-field rings of integers.
- The 13 rational CM discriminants have h(O) = 1 by construction.

## Methodology references (for Methods section)

- **scipy.stats.ortho_group**: Haar-random orthogonal matrices. Used for O+ matched null simulation.
- Matched-null local-4-gap normalization: Ergon's methodology, novel to this session.
- PARI ellrank for rank / 2-Selmer via cypari bindings (used in BSD consistency audit).

## Possibly relevant forward work

- **Conrey, J. B. & Farmer, D. W.** "Explicit formulas and random matrix theory." Various.
- **Keating, J. P. & Snaith, N. C.** (2000). "Random matrix theory and ζ(1/2+it)." Comm. Math. Phys. 214.
  - Moments of L-values; connects to our mechanism (c) Euler product analysis.

---

Verified by Charon literature pass, 2026-04-22.
All references should be double-checked against library access before submission;
memory-sourced pages and section numbers may be approximate.
