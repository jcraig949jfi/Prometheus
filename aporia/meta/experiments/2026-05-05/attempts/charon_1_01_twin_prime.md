# Attempt — Twin Prime Conjecture

**Researcher:** Charon 1
**Date:** 2026-05-05
**Time spent:** ~1.5 hours
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES

## Problem statement

There exist infinitely many primes p such that p+2 is also prime.

Equivalently: the prime-gap function `g(p_n) = p_{n+1} − p_n` takes value 2 for infinitely many n.

## Literature scan: prior attempts

1. **Brun 1919** — pure sieve approach. Showed the sum of reciprocals of twin primes converges (Brun's constant ~ 1.902). Implies the twin-prime counting function is at most O(x / (log x)²) — gives upper bound, no lower bound.

2. **Hardy–Littlewood 1923** ("Some problems of partitio numerorum III: On the expression of a number as a sum of primes") — circle method + heuristic. Conjectures π₂(x) ~ 2C₂ x / (log x)² where C₂ ≈ 0.6601618 (twin prime constant). Heuristic only; no proof of any lower bound.

3. **Goldston–Pintz–Yıldırım 2009** ("Primes in tuples I", Annals of Mathematics 170) — proved liminf (p_{n+1} − p_n) / log p_n = 0. Did not produce a finite gap bound.

4. **Zhang 2013** ("Bounded gaps between primes", Annals 179, 2014) — proved liminf (p_{n+1} − p_n) ≤ 70 000 000. First finite bound.

5. **Maynard 2015** ("Small gaps between primes", Annals 181) — independent method using multidimensional Selberg sieve; reduced bound to 600 unconditionally.

6. **Polymath 8a → 8b 2014** ("Variants of the Selberg sieve, and bounded intervals containing many primes", Tao + many authors) — combined Maynard's framework with optimization to bound 246 unconditionally; conditional on Elliott–Halberstam (EH), bound drops to 12; under generalized EH (GEH), to 6.

7. **Friedlander–Iwaniec 1998** — "Asymptotic sieve for primes" + "Primes of the form a² + b⁴" (Annals 148, 1998) — among the only successful instances of breaking the parity barrier in sieve theory.

## Attack surfaces tried

### Attack 1 — Hardy–Littlewood verification, finite-N convergence

- **Approach:** verify the twin-prime constant heuristic π₂(x) ~ 2C₂ x/(log x)² and measure how slowly it converges. If the constant were observed to be drifting, that would suggest an unmodeled correction term and a possible attack vector.
- **Tools used:** Python sympy `isprime`/`nextprime`, manual loop.
- **Time spent:** 15 min
- **Result:**

  | N | actual π₂(N) | HL prediction | ratio |
  |---|---|---|---|
  | 10⁴ | 205 | 155.6 | 1.317 |
  | 10⁵ | 1 224 | 996.1 | 1.229 |
  | 10⁶ | 8 169 | 6 917.5 | 1.181 |

  Convergence is slow but monotonic toward 1. Consistent with literature (the HL estimate has well-known logarithmic corrections at finite N — Wolf, Riesel-Vaughan-style asymptotic-with-error papers describe this).
- **Why it failed:** purely confirmatory of existing heuristic. Does not produce any new structural information; the slow convergence is itself a known phenomenon, not a novel signal.
- **Obstruction class:** asymptotic_only (the HL constant is meaningful only as x → ∞; finite-N data cannot establish it).
- **Kill_path classification:** F9 (simpler explanation: this is just numerical confirmation of a heuristic, not evidence for a new mechanism).
- **Distance to closure:** infinite — verifying HL doesn't get you to a proof.

### Attack 2 — Read the Maynard sieve apparatus and locate the parity-problem load-bearing barrier

- **Approach:** identify the precise step in the Maynard / GPY / Selberg sieve framework where the path from 246 → 2 fails. The brief asks for surface area; pinning down WHERE the bound stops shrinking is substrate-grade negative data.
- **Tools used:** literature scan (Tao's blog post on the parity problem; the Polymath 8 retrospective arXiv 1409.8361; Murty–Vatwani "Twin primes and the parity problem", J. Number Theory 180:2017).
- **Time spent:** 35 min
- **Result:** the parity barrier is structural in any pure-sieve approach. Selberg-type sieves cannot distinguish numbers with an odd number of prime factors from those with an even number; for twin primes the relevant set has **odd** factor count (namely 1), so the sieve over-estimates by a factor of 2. Concretely: any Brun- or Selberg-type bound on the count of n with both n and n+2 prime is at least (2 + o(1)) × (true count). To prove infinitely many twin primes, you must show the lower bound is positive — but the sieve loses a factor of 2, and 2 × 0 = 0. Friedlander–Iwaniec broke this barrier for primes of the form a² + b⁴ by exploiting bilinear structure that twin-primes (which are linear in n) lack. Maynard's bound is unconditional; the path to 2 specifically requires either a new sieve framework or input from a completely different direction (e.g., Heath-Brown–style use of Siegel-zero hypotheticals, or autocorrelation estimates from L-functions).
- **Why it failed:** the parity barrier is a theorem of sieve theory, not a calculation that can be tightened. Until someone exhibits a non-sieve mechanism that detects 1-almost-primes (i.e., primes themselves) in pairs, the sieve route stops at any finite bound k ≥ 2.
- **Obstruction class:** method_complexity (the method's structural ceiling is proven, not contingent).
- **Kill_path classification:** F11 (cross-validation: every pure-sieve attempt converges on the same 2× obstruction; this isn't a single-paper artifact, it's the framework's signature).
- **Distance to closure:** load-bearing, multi-decade. Maynard 2014 quoted (HKLF Forum): *"to lower the bound to 2 for the Twin Prime Conjecture, new methods have to be invented."*

### Attack 3 — Conditional-result chase: what does Elliott–Halberstam buy you, and why doesn't generalized EH close it?

- **Approach:** under EH (level of distribution θ → 1/2), Polymath bound → 12. Under GEH, → 6. Question: what would a θ > 1/2 result give? If even GEH leaves a gap of 6, then EH-style improvements alone cannot close the conjecture.
- **Tools used:** Polymath 8a/8b retrospective.
- **Time spent:** 15 min
- **Result:** the limit of the Maynard sieve framework, even with hypothetical θ → 1, is a gap bound that depends on the dimension of the underlying GPY weight. Polymath 8b explicitly notes the GEH-bound of 6 is the framework's structural floor: the Maynard sieve detects k-tuples (k = 6 for GEH), not pairs. Going from 6 → 2 inside this framework is not possible regardless of the level of distribution; you need a different sieve.
- **Why it failed:** the GEH lower bound of 6 is itself an artifact of the framework; even oracle-grade input on prime distribution doesn't reduce it to 2. This is a substrate-grade negative on the EH-pursuit strategy: improving distribution-of-primes hypotheses is necessary but not sufficient.
- **Obstruction class:** requires_unproven_conjecture (combined with method_complexity — even granting the conjecture, the method ceiling is 6).
- **Kill_path classification:** F6 (base rate: even maximal-strength input to the current framework leaves k=6 floor).
- **Distance to closure:** requires new framework, not improved input.

### Attack 4 — Quick check: any leverage from the recent (2025–2026) Larsen / Maynard / Tao "long gaps" line of work?

- **Approach:** search for whether the parallel "gaps between primes" line (Erdős prize problem on long gaps; Ford–Green–Konyagin–Maynard–Tao 2014, then improvements by others) has produced reciprocity / cross-fertilization with the small-gaps line.
- **Tools used:** literature scan with date filter.
- **Time spent:** 15 min
- **Result:** no evidence of cross-fertilization; small-gap and long-gap directions remain methodologically separate. Long-gap progress uses Maier-matrix / GCD-of-shifted-primes constructions that don't transfer to lower-bounding small-gap density. No canonical source identified for a 2025–2026 paper that bridges them.
- **Why it failed:** different methodologies; the "long gap" methods produce existence statements, not density. Twin prime is a density question.
- **Obstruction class:** method_complexity (different machinery).
- **Distance to closure:** no decrease.

## Partial results obtained

None. All four attacks confirm the structural barriers without moving them. The strongest *new* observation is calibrated negative: **even unconditional GEH-strength input to the Maynard framework yields k=6**, which means future work on Elliott–Halberstam alone — without a new sieve framework — cannot close the conjecture. This is consistent with Maynard's own published assessment.

## Honest "what would unblock this"

1. **A new sieve framework that breaks parity for linear configurations.** Friedlander–Iwaniec showed parity could be broken in some non-linear contexts (a² + b⁴). Twin primes is the simplest linear pair. No analogous breakthrough is known.

2. **A bilinear-form input from L-function theory** — autocorrelation estimates for π(x) shifted by 2 — that bypasses the sieve entirely. Heath-Brown's 1983 conditional argument from Siegel zeros is the closest published analog, but it conditions on a hypothesis (existence of Siegel zeros) that nobody believes is true.

3. **A non-classical method.** GPT/AI-assisted theorem proving has not produced traction here, as far as published literature shows. Twin primes is a frequent informal target for "AI for math" work but no substantive arXiv submission has come from that direction in 2025–2026 that I can confirm without inventing citations.

## Calibrated negatives

- The Hardy–Littlewood prediction is *finite-N undercounted* (ratio 1.18 at 10⁶) and convergence to 1 is logarithmic. Numerical extrapolation alone provides no path to a proof; the constant 2C₂ is well-believed but the assertion is asymptotic-only.
- The Polymath 8b GEH bound of 6 is a **structural floor of the Maynard framework**, not a tightenable bound. Pursuing improved distribution conjectures alone (EH → GEH → "super-EH") cannot close the conjecture inside this framework. This is the strongest substrate-grade negative I can extract from one session of attack.
- The parity barrier (Selberg 1949) is now ~75 years old. The single major break (Friedlander–Iwaniec 1998) used non-linear structure that twin primes lack. The barrier is currently load-bearing and there is no published roadmap I can verify for breaking it for linear configurations.

## Citations

- Hardy, G. H. & Littlewood, J. E. (1923). *Acta Mathematica* 44, 1–70. ("Some problems of partitio numerorum III: On the expression of a number as a sum of primes.")
- Brun, V. (1919). *Bulletin des Sciences Mathématiques* (initial announcement of Brun's sieve and convergence of twin-prime reciprocals).
- Goldston, D. A.; Pintz, J.; Yıldırım, C. Y. (2009). "Primes in tuples I." *Annals of Mathematics* 170, 819–862.
- Zhang, Y. (2014). "Bounded gaps between primes." *Annals of Mathematics* 179, 1121–1174. (Posted 2013.)
- Maynard, J. (2015). "Small gaps between primes." *Annals of Mathematics* 181, 383–413.
- Polymath, D. H. J. (2014). "Variants of the Selberg sieve, and bounded intervals containing many primes." *Research in the Mathematical Sciences* 1:12.
- Polymath, D. H. J. (2014). "The 'bounded gaps between primes' Polymath project: a retrospective." arXiv:1409.8361.
- Friedlander, J. & Iwaniec, H. (1998). "Asymptotic sieve for primes." *Annals of Mathematics* 148, 1041–1065.
- Friedlander, J. & Iwaniec, H. (1998). "The polynomial X² + Y⁴ captures its primes." *Annals of Mathematics* 148, 945–1040.
- Selberg, A. (1949). On parity in elementary sieve methods (multiple papers; original parity-obstruction observation; canonical reference: Selberg, *Collected Papers* vol. II).
- Tao, T. (2007). "Open question: the parity problem in sieve theory." Personal blog post (terrytao.wordpress.com), tagged in his "parity problem" series.
- Murty, M. R. & Vatwani, A. (2017). "Twin primes and the parity problem." *Journal of Number Theory* 180, 643–659.
- Maynard, J. as quoted in Hong Kong Laureate Forum coverage: *"To lower the bound to 2 for the Twin Prime Conjecture, new methods have to be invented."*

— End of attempt
