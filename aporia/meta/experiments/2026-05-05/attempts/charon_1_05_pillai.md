# Attempt — Pillai's Conjecture

**Researcher:** Charon 1
**Date:** 2026-05-05
**Time spent:** ~1.25 hours
**Verdict:** PARTIAL_RESULT (reproduced known small-k structure including the Bennett exceptional cases; identified the effective-vs-ineffective bound gap as the load-bearing structural barrier)

## Problem statement

For any fixed positive integer k, the equation

  |x^p − y^q| = k

has only finitely many solutions in positive integers (x, y, p, q) with p, q ≥ 2, x, y ≥ 2, and (p, q) ≠ (2, 2).

The (p, q) = (2, 2) exclusion is essential — `x² − y² = k` always has infinitely many solutions when k can be factored.

The case k = 1 is **Catalan's conjecture** — proved by Mihăilescu in 2002. Only solution: 3² − 2³ = 1.

The general k ≥ 2 case is **Pillai's conjecture** — still open.

## Literature scan: prior attempts

1. **Pillai 1945** — original conjecture; "On the equation 2^x − 3^y = 2^X + 3^Y", *Bull. Calcutta Math. Soc.* 37, 15–20. Established the conjecture as a generalization of Catalan.

2. **Tijdeman 1976** — "On the equation of Catalan." *Acta Arithmetica* 29, 197–209. Used Baker's method (linear forms in logarithms) to prove an effective upper bound for x, y in Catalan's equation. First effective Diophantine result on this kind of equation. **Ineffective constant** — proves finiteness but with a constant that cannot be computed numerically with reasonable effort.

3. **Mihăilescu 2002–2004** — "Primary cyclotomic units and a proof of Catalan's conjecture." *Journal für die reine und angewandte Mathematik* 572, 167–195. Proved Catalan (k = 1) using cyclotomic-field arithmetic + class number theory. **Did NOT use linear forms in logarithms.** This is significant: Mihăilescu's argument is entirely class-field-theoretic and avoids the ineffective Baker constants.

4. **Bugeaud, Hanrot, Mihăilescu (2005)** — "Catalan without logarithmic forms." *Journal de Théorie des Nombres de Bordeaux* 17, 69–85. Streamlined exposition; same class-number-free path.

5. **Bennett 2001** — "Pillai's conjecture revisited." *Journal of Number Theory* 98, 228–235. Major progress: proved that for fixed N ≥ 2, the equation `|(N+1)^x − N^y| = c` has at most ONE solution in positive integers (x, y), for `|c| > 13`, except for finitely many exceptional (N, c) pairs. The exception list: (N, c) ∈ {(2, 1), (2, 5), (2, 7), (2, 13), (2, 23), (3, 13)}. Uses the **hypergeometric method of Thue–Siegel**, avoiding linear forms in logs entirely.

6. **Stroeker & Tijdeman 1982** — proved Pillai's specific conjecture c₀(3, 2) = 13 (i.e., for the bases (3, 2), the largest c with multiple solutions is 13). Used linear forms in logarithms à la Baker.

7. **Recent (2024) work** — arXiv:2403.20037 ("On Pillai's conjecture..."), April 2025 update; arXiv:2201.10964 ("Pillai's conjecture for polynomials") — extends to polynomial analog with stronger results in that setting.

## Attack surfaces tried

### Attack 1 — Direct enumeration of small-k solutions

- **Approach:** for k ∈ [1, 9] and (p, q) ∈ [2, 5]² with (p, q) ≠ (2, 2), enumerate all (x, y) with x, y < 300 satisfying |x^p − y^q| = k. Validate that the empirical count is consistent with the literature, and surface the structure of "exceptional" k where many solutions exist.
- **Tools used:** brute-force Python enumeration.
- **Time spent:** 15 min
- **Result:**

  | k | # solutions | examples |
  |---|---|---|
  | 1 | 2 | 3²−2³ = 1, 2³−3² = −1 (Catalan unique up to sign) |
  | 2 | 2 | 5²−3³ = −2, 3³−5² = 2 |
  | 3 | 0 | none in range |
  | 4 | 6 | 2²−2³ = −4, 11²−5³ = −4, 6²−2⁵ = 4, … |
  | 5 | 2 | 3³−2⁵ = −5, 2⁵−3³ = 5 |
  | 6 | 0 | none in range |
  | 7 | 8 | 32³−181² = 7, 3²−2⁴ = −7, 5²−2⁵ = −7, … |
  | 8 | 4 | 4²−2³ = 8, 2³−4² = −8, 2³−2⁴ = −8, 2⁴−2³ = 8 |
  | 9 | 8 | 6²−3³ = 9, 15²−6³ = 9, 253²−40³ = 9, 5²−2⁴ = 9, … |

  Notable: **k = 7** contains the famously-large solution 32³ − 181² = 7 (32 768 − 32 761 = 7), part of Bennett's exceptional-case analysis. **k = 3 and k = 6** have no solutions in the small range tested — Pillai's conjecture says they should have finitely many; "zero" satisfies that, but a solution at large x or y is not ruled out by my range (x, y < 300).

- **Why it failed:** confirmatory. Reproduces published structure but extends nothing.
- **Obstruction class:** asymptotic_only.
- **Distance to closure:** zero — empirical only.

### Attack 2 — Locate the effective vs ineffective bound gap

- **Approach:** Mihăilescu's Catalan proof is *effective* (constants computable). The general Pillai for k ≥ 2 currently rests on Baker's method which gives only *ineffective* bounds. Question: how big is the gap between Mihăilescu's class-field-theoretic methods (which solved Catalan) and what would be needed for general Pillai?
- **Tools used:** Bugeaud–Hanrot–Mihăilescu 2005 ("Catalan without logarithmic forms") + Bennett 2001 ("Pillai's conjecture revisited") expositions.
- **Time spent:** 30 min
- **Result:** Mihăilescu's proof for Catalan exploits two features specific to k = 1:
  (a) The equation `x^p − y^q = 1` factors as a difference of consecutive perfect powers. The arithmetic of the cyclotomic fields ℚ(ζ_p) and ℚ(ζ_q) constrains this very tightly.
  (b) The "+1" gives access to Wieferich-style and Mirimanoff-style criteria — class-number divisibility conditions that produce contradictions for almost all (p, q) pairs.

  For general k ≥ 2, neither (a) nor (b) applies cleanly:
  - The constraint x^p − y^q = k with k > 1 doesn't factor as "consecutive powers".
  - Class-number-theoretic obstructions for general k correspond to ramification at primes dividing k, which complicates the cyclotomic-arithmetic reduction.

  Bennett 2001 closed many specific (N, c) cases using the *hypergeometric method* (Thue–Siegel), which IS effective and DOES avoid logarithmic forms. But Bennett's method requires the bases (x, y) to be of specific shape (consecutive integers N+1, N), and does not extend to arbitrary bases.

  **The effective-vs-ineffective gap for general Pillai is structural**: Baker's method gives ineffective bounds, Mihăilescu's method works only for k = 1, and Bennett's method works only for specific bases.

- **Why it failed:** the structural toolkit for Catalan (k = 1) does not transfer to general Pillai (k > 1). Each method has a method-specific scope:
  - Baker / linear forms in logs: works for general k but ineffective.
  - Mihăilescu cyclotomic: effective but only k = 1.
  - Bennett hypergeometric: effective but only specific base relationships.
- **Obstruction class:** method_complexity (each method has a structural ceiling; no method covers the full Pillai parameter space).
- **Kill_path classification:** F11 (cross-validation: independent methods all give partial coverage of overlapping but distinct slices).
- **Distance to closure:** new method needed. The "gap" that needs closing is a unified effective Diophantine framework for x^p − y^q = k for all k ≥ 2 and arbitrary x, y. None has been published.

### Attack 3 — Compute Pillai-style finiteness for fixed (p, q) and vary k: a sub-conjecture worth attacking

- **Approach:** instead of attacking Pillai for all k, attack the sub-problem "for fixed (p, q) = (3, 2), the count of (x, y, k) with x³ − y² = k for each k is bounded uniformly in k". This is provably true (Mordell's theorem on x³ − y² = k for any k has finitely many integer solutions), but the count is bounded only by ineffective constants. Question: do recent advances tighten this?
- **Tools used:** literature scan (Mordell *Diophantine Equations* 1969; Stark's tables on Mordell-curve solutions; Bennett's references).
- **Time spent:** 20 min
- **Result:** Mordell's theorem (effective for x² + y³ = k via class-number theory; ineffective in general for higher exponents) gives finiteness for fixed (p, q) = (3, 2). Modern techniques (Cremona's tables of Mordell curves, *p*-adic + lattice-reduction in Magma / PARI) handle specific k case-by-case. **No published unified asymptotic count** for the number of solutions as k → ∞. Each new k still requires individual analysis. The count grows slowly (most k have 0 solutions, some have a handful, exceptional k like k = 17 have 16 known solutions per LMFDB Mordell-curve database).
- **Why it failed:** the sub-problem has the same structural shape as the main problem at smaller scale. Each k is its own elliptic-curve question, and bounding-uniformly-over-k requires class-number / regulator estimates that aren't tight enough.
- **Obstruction class:** non_constructive (count grows but not tightly bounded as k → ∞).
- **Kill_path classification:** F6.
- **Distance to closure:** non-trivial. Improving the asymptotic bound would be substantial number theory.

### Attack 4 — Quick check: is the abc conjecture sufficient for general Pillai?

- **Approach:** Catalan was solved without abc; Brocard finiteness needs abc. What about general Pillai?
- **Tools used:** Wikipedia + Bennett expositions.
- **Time spent:** 15 min
- **Result:** the abc conjecture, if proved, implies Pillai's conjecture. Specifically: from |x^p − y^q| = k with x, y, p, q ≥ 2 and (p, q) ≠ (2, 2), abc provides an effective upper bound on max(x, y) in terms of k, p, q, since abc-input on the triple (x^p, k, y^q) (after sign-fixing and gcd-clearing) yields max(x^p, y^q) ≤ N(x · k · y)^c for some explicit constant c. Combining with 1/p + 1/q ≤ 5/6 (since (p, q) ≠ (2, 2)) gives the finiteness. **Pillai is therefore conditionally proved under abc** — but abc itself is contested. Same abc-status caveat as Brocard.
- **Why it failed:** conditional on abc, which is contested.
- **Obstruction class:** requires_unproven_conjecture.
- **Kill_path classification:** F11 (same abc-conditional pattern as Brocard).
- **Distance to closure:** routes through abc resolution.

## Partial results obtained

The substrate-grade observations from this session:

1. **The structural toolkit fragments**: three distinct effective methods (Mihăilescu, Bennett, hypergeometric / Thue–Siegel) cover *non-overlapping slices* of Pillai's parameter space. Catalan (k = 1) is closed; specific bases are closed; general (k ≥ 2, arbitrary x, y) remains open.

2. **The exceptional-case list is small and known**: Bennett's (N, c) ∈ {(2, 1), (2, 5), (2, 7), (2, 13), (2, 23), (3, 13)} for the consecutive-bases case. Outside this list, the equation has at most one solution. This is a substantive published result narrowing the open territory.

3. **Catalan and Pillai are methodologically separate**: Mihăilescu's Catalan proof did not solve Pillai. The methods that close k = 1 do not close k = 2.

4. **abc conjecture is the only unified path** to general Pillai finiteness, and abc is itself open (with disputed claims).

## Honest "what would unblock this"

1. **A proof of weak abc** — would close Pillai unconditionally via the standard reduction.
2. **A unified effective Diophantine framework for x^p − y^q = k** — combining the Mihăilescu cyclotomic ideas with the Bennett hypergeometric ideas, ideally producing computable bounds that don't depend on linear forms in logarithms. This is an active research direction; recent papers (Bennett, Bugeaud, others) make incremental progress on specific equation families.
3. **Computational extension of the verified k range.** For each fixed small k, verifying "no solutions outside the published ones" is computationally tractable for many specific k. Bennett's (N, c) list could be tightened or extended.
4. **A non-Diophantine reformulation.** No published example, but speculative: if the equation x^p − y^q = k can be reformulated as a class-field-theoretic statement about a specific extension of ℚ, the toolkit might transfer. Speculative; not pursued in this session.

## Calibrated negatives

- **Catalan does not generalize to Pillai by Mihăilescu's method.** This is an explicit observation in Bugeaud–Hanrot–Mihăilescu 2005 and the Bennett expositions. The "+1" is structurally special.
- **Linear forms in logs (Baker, Tijdeman) are ineffective**: they prove finiteness but the constants are too large to compute or use for verification. The state-of-the-art "effective" approaches all use either cyclotomic arithmetic (limited scope) or hypergeometric methods (limited scope).
- **Bennett's exceptional-case list is the cleanest published partial result on Pillai outside Catalan.** It's narrow (only (N+1, N) base pairs) but it does cover an infinite family.
- **The shared abc-dependency of Brocard and Pillai is substrate-grade signal**: any progress on weak abc/Szpiro would unblock both. Suggests cross-problem investment in abc-adjacent approaches.

## Citations

- Pillai, S. S. (1945). "On the equation 2^x − 3^y = 2^X + 3^Y." *Bull. Calcutta Math. Soc.* 37, 15–20. (Original posing of the conjecture.)
- Tijdeman, R. (1976). "On the equation of Catalan." *Acta Arithmetica* 29, 197–209. (Effective bound via Baker's method.)
- Stroeker, R. J. & Tijdeman, R. (1982). [c₀(3, 2) = 13 result; cited per Wikipedia "Catalan's conjecture" → Pillai's conjecture section].
- Mihăilescu, P. (2004). "Primary cyclotomic units and a proof of Catalan's conjecture." *Journal für die reine und angewandte Mathematik* 572, 167–195.
- Bugeaud, Y.; Hanrot, G.; Mihăilescu, P. (2005). "Catalan without logarithmic forms." *Journal de Théorie des Nombres de Bordeaux* 17, 69–85.
- Bennett, M. A. (2001). "Pillai's conjecture revisited." *Journal of Number Theory* 98, 228–235.
- Bennett, M. A. — additional papers, available at personal.math.ubc.ca/~bennett/. Including "On some exponential equations of S. S. Pillai."
- (2025). "On Pillai's conjecture..." arXiv:2403.20037, v2 dated April 2025.
- (2022). "Pillai's conjecture for polynomials." arXiv:2201.10964.
- Mordell, L. J. (1969). *Diophantine Equations*. Academic Press. Chapter on x³ − y² = k and related equations.

— End of attempt
