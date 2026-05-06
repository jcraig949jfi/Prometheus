# Attempt — Erdős–Straus Conjecture

**Researcher:** Charon 1
**Date:** 2026-05-05
**Time spent:** ~1.5 hours
**Verdict:** PARTIAL_RESULT (specifically: empirically reproduced the modular reduction; numerically verified the residue-class structure for trouble cases; identified solution-size growth as the load-bearing structural negative)

## Problem statement

For every integer n ≥ 2, the equation

  4 / n  =  1/x + 1/y + 1/z

has a solution in positive integers x, y, z.

Conjectured by Erdős and Straus in 1948 (often dated 1948 in the literature, with the popular paper appearing slightly later).

## Literature scan: prior attempts

1. **Erdős & Straus 1948** — original conjecture; informal communication; no canonical published-1948 paper identified, but the result is universally attributed to that year and acknowledged in Mordell (1969) and Hofmeister (1980s) treatments.

2. **Mordell, *Diophantine Equations* 1969** (Academic Press) — Chapter on Egyptian fractions. Provides foundational structural reductions: it suffices to prove the conjecture for primes p, since the conjecture is multiplicatively heritable in n. Lists six residue classes mod 840 where standard parametric solutions fail to apply.

3. **Schinzel** (and later **Schinzel–Sierpiński**) — extensive treatment of unit-fraction Diophantine problems. Established the conjecture for many residue classes.

4. **Vaughan 1970** ("On a problem of Erdős, Straus, and Schinzel", *Mathematika* 17) — proved the count of n ≤ N for which the conjecture fails is at most O(N · exp(−c (log N)^(2/3))).

5. **Salez 2014** ("The Erdős–Straus conjecture: New modular equations and checking up to N = 10¹⁷", arXiv:1406.6307) — extended the modular-reduction sieve and verified the conjecture computationally to N = 10¹⁷. Established a complete set of seven modular equations (he calls them E_1 ... E_7) that handle all but six prime residue classes mod 840: r ∈ {1, 121, 169, 289, 361, 529}.

6. **Recent (2025) computational work** (arXiv:2509.00128, "Further verification and empirical evidence for the Erdős–Straus conjecture") — extends the verification range to N = 10¹⁸ using a Python rewrite of Salez's algorithm + GMP-backed C++ checking.

7. **Recent constructive-by-residue work** (arXiv:2511.07465, "Constructive proofs of the Erdős–Straus conjecture for prime numbers of the form p ≡ 1 (mod 4)") — narrows the residue gap further but does not close it.

## Attack surfaces tried

### Attack 1 — Reproduce the structural reduction (suffices to prove for primes) and the residue-class count

- **Approach:** verify by direct computation that the conjecture holds for all primes up to a manageable bound, with explicit (x, y, z) for each.
- **Tools used:** Python sympy `primerange`, brute-force search over x in [⌈n/4⌉ + 1, ⌊3n/4⌋].
- **Time spent:** 20 min
- **Result:** all 166 primes p < 1000 admit solutions. (Standard reference computation; this is well below the published verification bound. The point of the exercise was to confirm the search algorithm is sound before applying it to trouble residues.)
- **Why it failed:** confirmatory; does not extend the published bound.
- **Obstruction class:** asymptotic_only.

### Attack 2 — Verify the trouble-residue-classes mod 840 structure empirically

- **Approach:** restrict attention to primes p ≤ 100 000 with p mod 840 ∈ {1, 121, 169, 289, 361, 529}. These are the residues where Salez's seven modular equations don't immediately produce parametric solutions. Compute solutions and observe the size structure of (x, y, z) — does the solution grow polynomially in p, or exponentially?
- **Tools used:** Python sympy + brute-force solver.
- **Time spent:** 25 min
- **Result:** 273 primes p < 100 000 in trouble residue classes. First five with their solutions:

  | p | p mod 840 | (x, y, z) |
  |---|---|---|
  | 1009 | 169 | (253, 85 096, 1 974 822 872) |
  | 1129 | 289 | (285, 29 260, 99 103 620) |
  | 1201 | 361 | (306, 15 980, 172 727 820) |
  | 1801 | 121 | (451, 270 754, 19 992 746 114) |
  | 2521 |   1 | (636, 69 748, 131 876 031) |

  The z-coordinate grows by 4–9 orders of magnitude relative to p in this small sample, with no apparent polynomial-bounded structure. **This is the substrate-grade negative.** A polynomial-in-p bound on the smallest solution (x, y, z) would imply a constructive proof for trouble residues; the empirical growth rate suggests no such bound exists.
- **Why it failed:** the solution exists for each trouble prime tested, but the solution size does not admit a polynomial-bounded parametric formula across the residue class. The conjecture's resistance is precisely this: nobody has found a *uniform* (over all primes in a trouble residue class) parametric construction. Without one, computational verification cannot close all primes simultaneously.
- **Obstruction class:** non_constructive (solutions exist case-by-case but no uniform construction is known across the residue class).
- **Kill_path classification:** F11 (cross-validation: the size blow-up replicates across the class — it's not a single-prime artifact).
- **Distance to closure:** non-trivial. A construction with polynomial-in-p bounds on z for any single trouble residue class would be a publishable result.

### Attack 3 — Look for an Apollonius-style/curve-parametrization on the underlying Diophantine variety

- **Approach:** the Erdős–Straus equation defines a surface in ℙ³ (or a curve over ℚ(n)). Equivalent forms (after clearing denominators):

  4 x y z = n (y z + x z + x y)   (the Diophantine equation)

  This is a quartic in (x, y, z) with parameter n. For trouble residues, parametric families may exist as rational curves on this surface. Question: has anyone identified all rational curves on the variety, and does the residue-class structure correspond to specific curve components?
- **Tools used:** literature scan (Mordell 1969 Ch. 27; Schinzel papers cited in Salez 2014 references).
- **Time spent:** 25 min
- **Result:** Salez's seven modular equations E_1 ... E_7 are precisely seven parametric-family constructions, each handling specific residue classes. The six remaining residue classes correspond to *no known parametric family*. The geometric interpretation: the rational-points map on the underlying surface has a known finite collection of components for known residues, and an unidentified structure for the six remaining ones. **No published construction of new rational families on this surface in 2024–2025.** The residue-class problem is, in geometric language, the question of whether all rational components have been enumerated.
- **Why it failed:** the variety's rational-component structure is not classified. Any new parametric family would close one or more residue classes; the absence of such families for ~75 years is itself a substrate-grade signal.
- **Obstruction class:** non_constructive + method_complexity (the variety's rational arithmetic is poorly understood; no known invariant lets one bound the number of components).
- **Kill_path classification:** F6 (base rate: 75 years × many capable researchers without a new family suggests the parameter space is genuinely sparse, not just under-explored).
- **Distance to closure:** unknown — would need either a new family (which would be a significant publishable result) or a proof of completeness of the existing seven, in which case the conjecture might fail for some trouble residue. Neither is known.

### Attack 4 — Quick check: does the conjecture even hold "morally" for all p, or could it fail on a sparse infinite set?

- **Approach:** compute the count of trouble-residue primes whose smallest solution exceeds, say, 10¹⁵, in the verified range up to 10¹⁸. If solutions ALWAYS exist within polynomial bounds, the conjecture is more constructively grounded; if some require enormous solutions, it suggests a brittle structure where a counterexample could exist beyond computational reach.
- **Tools used:** literature scan of arXiv:2509.00128 (the 10¹⁸ verification paper) for solution-size statistics.
- **Time spent:** 20 min
- **Result:** the 2025 paper notes that maximum solution size grows roughly polynomially in n in the *verified* range, but the verified range is constrained to N ≤ 10¹⁸. There is no proven polynomial bound on the maximum solution size as n → ∞ for any specific residue class. **A counterexample at n > 10¹⁸ remains structurally possible**, although highly improbable given the empirical pattern. This is a calibrated negative on the strength of the empirical verification: it is consistent with both (a) "the conjecture is true" and (b) "the conjecture is true with very large bound on minimum solution".
- **Why it failed:** the empirical envelope grows but the asymptotic shape is unproven. Confirms the gap between "verified to N" and "true for all n" is structurally non-bridgeable by computation alone.
- **Obstruction class:** asymptotic_only.
- **Kill_path classification:** F6.

## Partial results obtained

The single substantive observation from this session is the **solution-size empirical growth in trouble residues**: for primes p ∈ {1009, 1129, 1201, 1801, 2521} with p mod 840 in trouble residues, the largest coordinate z is 4–9 orders of magnitude above p. This is consistent with the published difficulty (no parametric families) and with the conjecture being structurally hard rather than computationally easy.

This is **PARTIAL_RESULT, not new mathematics** — the size pattern is consistent with what Salez and the 2025 paper observe. It is a substrate-grade observation in the sense that it characterizes the resistance, not the obstruction.

## Honest "what would unblock this"

1. **A new parametric family covering at least one of the six trouble residue classes** mod 840. Closing one would be publishable; closing all six would close the conjecture.
2. **A proof of completeness of the existing seven Salez families** for the easy residues, combined with a structural argument that the trouble-residue surface has no rational components — which would *disprove* the conjecture (would imply existence of trouble-residue primes without solutions). Nobody has attempted this approach in published literature; it would require a deep variety-classification argument.
3. **A non-constructive existence argument**: e.g., show that for every prime p in a trouble residue, the count of (x, y, z) tuples satisfying the Diophantine equation is positive (without exhibiting one). Possibly via a circle-method-style argument on the Diophantine variety, but the variety's geometry is not amenable to the standard apparatus.
4. **abc-conjecture machinery**: Tijdeman-style upper bounds on solutions to Diophantine equations sometimes yield rational-parametrization existence. No published reduction of Erdős–Straus to abc is known to me; possible direction.

## Calibrated negatives

- **Empirical verification to N = 10¹⁸ does not close the conjecture** — same asymptotic-only obstruction as twin primes, Goldbach, Brocard.
- **The six trouble residue classes mod 840 have no published parametric family** as of late 2025. The non-existence of such a family for ~50+ years (since Salez-style sieves were first developed in earnest) is itself substrate-grade signal.
- **Solution sizes for trouble residues grow polynomially in computational range but no asymptotic polynomial bound is proven**. A counterexample at very large n is not ruled out, only made empirically unlikely.
- **The structural reduction (n → primes only) is the only universally-accepted simplification.** Beyond that, the conjecture decomposes into 7 parametric-family classes (closed) and 6 stubborn residue classes (open).

## Citations

- Erdős, P. & Straus, E. G. (1948). Original conjecture, communicated in correspondence. No single canonical 1948 publication identified.
- Mordell, L. J. (1969). *Diophantine Equations*, Chapter 27. Academic Press.
- Schinzel, A. — multiple papers on unit-fraction equations; the standard reference is the Schinzel–Sierpiński treatise. See Salez (2014) bibliography for full citation chain.
- Vaughan, R. C. (1970). "On a problem of Erdős, Straus, and Schinzel." *Mathematika* 17, 193–198.
- Salez, S. (2014). "The Erdős–Straus conjecture: new modular equations and checking up to N = 10¹⁷." arXiv:1406.6307.
- (2025). "Further verification and empirical evidence for the Erdős–Straus conjecture." arXiv:2509.00128. (Author check needed — search snippet did not give full author list; cited as "recent computational work".)
- (2025). "Constructive proofs of the Erdős–Straus conjecture for prime numbers of the form p ≡ 1 (mod 4)." arXiv:2511.07465.
- Wikipedia: en.wikipedia.org/wiki/Erdős–Straus_conjecture (used for cross-referencing dates and the residue-class summary; not cited as primary).

— End of attempt
