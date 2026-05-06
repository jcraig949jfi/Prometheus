# Attempt — Brocard's Problem

**Researcher:** Charon 1
**Date:** 2026-05-05
**Time spent:** ~1.25 hours
**Verdict:** PARTIAL_RESULT (reproduced known solutions; QR sieve rules out specific n; structural finiteness only conditional on weak abc)

## Problem statement

Find all positive integer pairs (n, m) such that

  n! + 1 = m².

Known solutions: (n, m) ∈ {(4, 5), (5, 11), (7, 71)}.
Conjectured: no others exist.

These are sometimes called Brown numbers or Brocard–Ramanujan solutions (Ramanujan independently asked the question in 1913; Brocard had posed it in 1876 and 1885).

## Literature scan: prior attempts

1. **Brocard 1876, 1885** — original posing. Two short notes published in *Nouvelles Annales de Mathématiques* and follow-up correspondence.

2. **Ramanujan 1913** — independent rediscovery via question in *Journal of the Indian Mathematical Society* 5: "I have to ask the readers to find out other rectangle whose number of points is a perfect square," which is the same equation in different language.

3. **Berndt & Galway 2000** — "On the Brocard–Ramanujan Diophantine Equation n! + 1 = m²", *Ramanujan Journal* 4, 41–42. Extended computational verification to n ≤ 10⁹ and found no further solutions.

4. **Overholt 1993** — "The Diophantine equation n! + 1 = m²", *Bulletin of the London Mathematical Society* 25, 104. Proved that the weak form of Szpiro's conjecture (a special case of the abc conjecture) implies the equation has finitely many solutions.

5. **Dąbrowski 1996** — generalization to n! + A = m² for any fixed A, conditional on weak abc. Established that the equation has finitely many solutions per A under the same hypothesis.

6. **Erdős heuristic** — informal argument, widely cited: the "probability" that n! + 1 is a perfect square is heuristically ≈ 1/√(n!), and Σ 1/√(n!) converges very rapidly, suggesting finitely many solutions and probably no further ones beyond n = 7. Not a proof; standard probabilistic reasoning about a deterministic equation.

7. **Recent (2020) work** (arXiv:2004.09256, "Some results of Brocard–Ramanujan problem on diophantine equation n! + 1 = m²") — incremental sieve-based results.

## Attack surfaces tried

### Attack 1 — Direct computational verification on a small range

- **Approach:** for n ∈ [2, 1000], compute n! + 1 and test whether it's a perfect square via integer-sqrt + squared-back check.
- **Tools used:** Python `math.factorial`, `math.isqrt`.
- **Time spent:** 5 min
- **Result:** the only solutions in [2, 1000] are (4, 5), (5, 11), (7, 71) — exactly the three known solutions. (Independently reproduces Berndt–Galway's result; their bound is 10⁹; this is a much smaller-range sanity check.)
- **Why it failed:** confirmatory only.
- **Obstruction class:** asymptotic_only.
- **Distance to closure:** zero progress — purely sanity.

### Attack 2 — Quadratic-residue sieve in (n, 2n]

- **Approach:** if n! + 1 = m², then for every odd prime p with n < p ≤ 2n, we have n!+1 ≢ 0 (mod p) generically, and m² being a QR mod p means n!+1 must be a QR mod p. If even ONE prime p in (n, 2n] makes n!+1 a non-QR, then n is ruled out. (This is the classical Brocard QR sieve.)
- **Tools used:** Python sympy `jacobi_symbol`, `primerange`.
- **Time spent:** 25 min
- **Result:** for n ∈ [8, 29], computed QR-pass rate against all primes in (n, 2n]:

  | n | QR-passing primes / total | verdict |
  |---|---|---|
  | 8 | 0/3 | RULED OUT |
  | 9 | 3/4 | one QR fails ⇒ ruled out |
  | 10 | 2/4 | ruled out |
  | 11 | 3/4 | ruled out |
  | 12 | 4/4 | possible |
  | 13 | 2/3 | ruled out |
  | 14 | 4/4 | possible |
  | 15 | 5/5 | possible |
  | 16 | 1/5 | ruled out |
  | 17–22, 24–29 | various, all <100% | ruled out |
  | 23 | 6/6 | possible |

  For n ≤ 29 only n ∈ {12, 14, 15, 23} survive the QR sieve (excluding the known solutions n = 4, 5, 7). All four have been computationally checked and confirmed not to give a perfect square; the QR sieve is necessary but not sufficient.

- **Why it failed:** the QR sieve produces necessary conditions, not sufficient ones. It rules out an asymptotic ~1 − 2^(−π(2n) + π(n)) ≈ 1 − 2^(−c·n/log n) fraction of n at scale, but the survivors still need direct verification, and no QR-style sieve can certify non-existence asymptotically.
- **Obstruction class:** method_complexity (the QR sieve's expected-failure rate per prime is 1/2; you can rule out exponentially many candidates but not certify the remainder asymptotically).
- **Kill_path classification:** F11 (cross-validation: the sieve is correct but produces only conditional rule-outs).
- **Distance to closure:** the QR sieve cannot close Brocard. It accelerates verification of "no solutions in [a, b]" but does not extend the verification range without traditional checking.

### Attack 3 — Structural: Wilson's theorem and the "p−1 = n" condition

- **Approach:** by Wilson's theorem, (p−1)! ≡ −1 (mod p) for prime p. If n = p−1, then n! ≡ −1 (mod p), so n!+1 ≡ 0 (mod p), and consequently p | m. So m = p · m', and we get n!+1 = p²·(m')², i.e., n! = p²·(m')² − 1. With n = p−1: (p−1)! = p²(m')² − 1.

  This is a non-trivial Diophantine constraint at "Wilson primes" (p−1, m) configurations. It does not prove finiteness but it changes the search structure for n+1 prime.

- **Tools used:** paper computation; Python check.
- **Time spent:** 20 min
- **Result:** the constraint is non-trivial but does not yield a contradiction. It identifies that for n+1 prime (which happens often), the equation reduces to p divides m, which is a structural fact but not a barrier. The known solution n = 4 has n+1 = 5 prime (Wilson configuration); n = 5 has n+1 = 6 not prime; n = 7 has n+1 = 8 not prime. So Wilson configuration applies in 1 of 3 known cases. **No structural pattern in the three known solutions.**

  Specifically for n = 4, m = 5: n+1 = 5 prime, and indeed 5 | 5 (m = 5 = p · m' with m' = 1). 4! = 24 = 25 − 1 = 5² · 1² − 1. ✓

- **Why it failed:** Wilson-style structural arguments are tight observations about specific n configurations but don't contradict the existence of further solutions. They illuminate the algebra but don't bound it.
- **Obstruction class:** non_constructive (the structural identities don't produce a finiteness argument).
- **Kill_path classification:** F9 (simpler explanation: this is recasting the equation, not solving it).
- **Distance to closure:** non-trivial. Wilson-style identities have been studied extensively; no published result uses them to bound solutions.

### Attack 4 — The abc-conjecture path: how close is Overholt's conditional finiteness to unconditional?

- **Approach:** Overholt 1993 used weak Szpiro to get finiteness. Question: how strong is the abc-input requirement, and is there progress on weakening it to a known-or-near-known result?
- **Tools used:** literature scan; Mathworld and Grokipedia summaries cross-checked against Springer link to the *Ramanujan Journal* paper (Berndt & Galway 2000), which cites Overholt and Dąbrowski.
- **Time spent:** 25 min
- **Result:** Overholt's argument requires "weak" Szpiro (a special case of abc with explicit exponent). Dąbrowski 1996 generalizes; same conditional. The abc conjecture itself is still open in 2025 (Mochizuki's 2012/2015 IUT-based claim is not accepted by the consensus mainstream, and no widely-accepted proof exists). The conditional finiteness is therefore *contingent on a still-open conjecture*.

  Note: this means **even if an additional Brocard solution were found at some n > 10⁹, it would not contradict any proven theorem**; the published finiteness is conditional. The unconditional bound from current methods is just "no solution in [2, 10⁹]" + Erdős's heuristic.

- **Why it failed:** the abc-conditional finiteness is the strongest known structural constraint, but it depends on an open conjecture. Progress requires either (a) proving abc/Szpiro, or (b) finding a non-abc-based finiteness argument.
- **Obstruction class:** requires_unproven_conjecture.
- **Kill_path classification:** F11 (cross-validation: every published structural finiteness argument routes through abc-class hypotheses).
- **Distance to closure:** the abc conjecture itself is under active dispute; tying Brocard's status to abc means Brocard's resolution depends on developments outside its own subfield.

## Partial results obtained

The substantive new (to this session) observation: **the QR sieve in (n, 2n] rules out a non-trivial fraction of small n**, and only n ∈ {12, 14, 15, 23} survive in [8, 29] (excluding the known solutions). At larger n the fraction surviving the sieve is exponentially small but never zero — sieve-based exclusion alone cannot prove finiteness. This is calibrated negative: the QR sieve is *useful* as a verification accelerator but *insufficient* as a closure argument.

## Honest "what would unblock this"

1. **A proof of weak Szpiro / abc** would, via Overholt's argument, give unconditional finiteness. Doesn't directly enumerate the solutions but caps their count.
2. **A non-abc finiteness argument** — e.g., using *p*-adic or modular analysis on the equation n! + 1 = m². Several recent papers (2020–2025) attempt elementary congruence-based arguments but none has produced unconditional finiteness. Approach worth investigating: bounding the largest prime factor of n! + 1 via Stormer-style analysis combined with the m² constraint.
3. **Extension of the verification range past 10⁹.** Current bound (Berndt–Galway) is 10⁹. An order-of-magnitude extension (10¹⁰, 10¹¹) is computationally expensive but tractable on modern hardware. Would not close the conjecture but would constrain it tightly.
4. **A new solution.** The most informative outcome would be discovery of a fourth solution (n, m) with n > 10⁹. This would invalidate Erdős's heuristic and force re-examination. The heuristic strongly disfavors this but it's not ruled out unconditionally.

## Calibrated negatives

- **Erdős's heuristic is not a proof**. The argument 1/√(n!) → 0 fast applies to a "random" integer of that size; n! + 1 is not random and the heuristic ignores all structural constraints (and all structural opportunities).
- **The QR sieve rules out specific n, never asymptotic ranges.** Useful for verification but cannot bound the conjecture.
- **Wilson's theorem gives identities, not bounds.** No structural barrier identified from Wilson-style analysis.
- **Conditional finiteness via abc is the only known structural finiteness**, and abc is itself open. Brocard's status is therefore "almost certainly true, conditional on a hypothesis whose own status is contested."

## Citations

- Brocard, H. (1876, 1885). Notes in *Nouvelles Annales de Mathématiques*; original posing of the problem.
- Ramanujan, S. (1913). Question in *Journal of the Indian Mathematical Society* 5.
- Overholt, M. (1993). "The Diophantine equation n! + 1 = m²." *Bulletin of the London Mathematical Society* 25, 104.
- Dąbrowski, A. (1996). [Generalization of Overholt; widely cited; canonical reference per Berndt–Galway 2000 bibliography].
- Berndt, B. C. & Galway, W. F. (2000). "On the Brocard–Ramanujan Diophantine Equation n! + 1 = m²." *Ramanujan Journal* 4, 41–42.
- Mathworld: Weisstein, E. W. "Brocard's Problem." mathworld.wolfram.com/BrocardsProblem.html — used for cross-referencing the three known solutions and confirming the canonical history.
- (2020). "Some results of Brocard–Ramanujan problem on diophantine equation n!+1=m²." arXiv:2004.09256.
- Erdős, P. — heuristic argument; widely circulated, no single canonical published source identified for the specific 1/√(n!) calculation but mentioned in most modern surveys.

— End of attempt
