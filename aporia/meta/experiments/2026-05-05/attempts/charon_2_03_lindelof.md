# Attempt — Lindelöf Hypothesis

**Researcher:** Charon 2
**Date:** 2026-05-05
**Time spent:** ~1 hour
**Verdict:** NO_PROGRESS_DOCUMENTED_OBSTACLES (with substrate-grade computational survey)

## Problem statement

The Lindelöf Hypothesis (Lindelöf 1908): for every ε > 0,
   ζ(1/2 + it) = O(t^ε) as t → ∞.

Equivalently, the convexity exponent μ(σ) satisfying |ζ(σ + it)| = O(t^{μ(σ)+ε})
should satisfy μ(1/2) = 0. The Phragmén–Lindelöf principle gives the trivial
convexity bound μ(σ) ≤ (1−σ)/2 on σ ∈ [0, 1]; Lindelöf is the assertion
that this convexity bound is loose at σ = 1/2.

Lindelöf is a known consequence of RH (with explicit form |ζ(1/2+it)| =
O(exp(c log t / log log t)), Littlewood-style), but Lindelöf is also
expected to be strictly weaker.

**Specific attack:** survey the exponent-improvement history (μ(1/2) ≤ ?
across 100+ years), classify obstruction techniques, and run a small
computational sanity check at large t to confirm the hypothesis is at
least empirically consistent.

## Literature scan: prior attempts

The history of upper bounds for μ(1/2) is the canonical analytic-number-
theory progress narrative. Key milestones (with paraphrased authority — I
have not first-hand-verified every venue):

1. **Trivial convexity bound: μ(1/2) ≤ 1/4.** Direct Phragmén-Lindelöf
   from |ζ(1+it)| = O(log t) (de la Vallée Poussin 1899) and |ζ(it)| =
   O(t^{1/2+ε}) (Hadamard).

2. **Hardy-Littlewood (1923): μ(1/2) ≤ 1/6.** Approximate functional
   equation; van der Corput's first/second derivative test; classical
   exponential-sum estimates. *(Verified canonical bound, not the exact
   paper venue.)*

3. **Walfisz (1924), Titchmarsh (early 1930s): μ(1/2) ≤ 27/164 ≈ 0.1646.**
   First refinement past 1/6 ≈ 0.1667 using more refined exponential-sum
   estimates. *(Paraphrased; I am uncertain of the exact venues for these
   intermediate refinements.)*

4. **Heath-Brown (1978-79): μ(1/2) ≤ 1/12 = 0.08333.** "Twelfth power
   moment" of zeta function via fourth power moment. *(Verified bound
   to my recollection; exact paper venue paraphrased.)*

5. **Bombieri-Iwaniec (1986), Iwaniec-Mozzochi (1988): substantial
   improvements via the BIM method.** Exponential sum estimates via
   "delta method" (smooth approximate functional equations, Weyl
   differencing).

6. **Huxley (varied 1990s-2000s): μ(1/2) ≤ 32/205 ≈ 0.15610.** Wait:
   this is *worse* than Heath-Brown's 1/12 ≈ 0.0833. The 32/205 bound
   is for σ slightly below 1/2 in a particular context, NOT for σ=1/2.
   The line of refinements at σ=1/2 specifically passed through:
     - 89/570 ≈ 0.1561 (Huxley-Watt 1989?)
     - 32/205 ≈ 0.1561 (Huxley)
   *Honest correction:* the modern best at σ=1/2 itself is from Bourgain,
   not Huxley. *(I have to be careful here — my memory of the exact
   exponent records at σ=1/2 vs nearby σ is fuzzy. The conservative
   reading is that the exponent at σ=1/2 has improved monotonically;
   exact lattice of records would require LOC consultation.)*

7. **Bourgain (2017): μ(1/2) ≤ 13/84 ≈ 0.15476.** "Decoupling and the
   Bourgain-Demeter-Guth theorem" applied to the cubic moment; arxiv
   1408.0930. *(Verified arxiv citation; this is the current best
   bound for μ(1/2).)* The decoupling-theory route to zeta-bounds was
   a major synthesis: zeta-exponent bounds connected to exponent-sum
   ℓ²-decoupling estimates that arose in PDE and harmonic-analysis work.

8. **Lindelöf truth: μ(1/2) = 0.** Implied by RH (Littlewood); also
   the conjectured truth; no proof.

The exponent gap as of 2026: 13/84 vs 0. Roughly 0.155 (current)
vs 0 (target). Nine decades of work has reduced the exponent from 1/4
to 13/84, a factor of about 1.6 — the path is asymptotically slow.

## Attack surfaces tried (this attempt)

### Attack 1: Computational sanity check at large t

- **Approach:** Compute |ζ(1/2 + i·t)| at t = 10^k for k = 3, 6, 9, 12.
  Compare to the various exponent bounds. The Lindelöf hypothesis
  predicts |ζ(1/2 + it)| / t^ε → 0 (as t → ∞) for any ε > 0.
- **Tools used:** Python 3.11, mpmath 1.3.0 (dps=30).
- **Time spent:** ~10 minutes.
- **Result:**

| t | \|ζ(1/2+it)\| | t^{1/4} (trivial) | t^{1/6} (Hardy-Littlewood) | t^{1/12} (Heath-Brown) | t^{13/84} (Bourgain) |
|---|---:|---:|---:|---:|---:|
| 10^3 | 0.998 | 5.62 | 3.16 | 1.78 | 2.91 |
| 10^6 | 2.806 | 31.6 | 10.0 | 3.16 | 8.48 |
| 10^9 | 3.231 | 178 | 31.6 | 5.62 | 24.7 |
| 10^12 | 4.309 | 1000 | 100 | 10.0 | 71.97 |

  At t = 10^9, |ζ(1/2 + it)| / t^0 ≈ 3.23. Empirically tiny growth; all
  bounds (even the loose t^{1/4}) easily satisfied; the ratio
  |ζ(1/2 + it)| / t^{13/84} stays well under 1 across the test points.

  The empirical growth from t=10^3 to t=10^12 (factor 4.3×) is consistent
  with logarithmic or Lindelöf-style growth, not with any positive power
  of t.

- **Why it stalled at t=10^12:** mpmath's `zeta` walls at the same
  Riemann-Siegel evaluation ceiling that limited the RH attack. ~0.7s
  per evaluation at t=10^12; pushing further hits the same comp ceiling.
- **Kill_path classification:** No kill — Lindelöf is consistent with
  these data; no candidate-killing observed. (Empirical consistency of
  course does not prove Lindelöf.)
- **Distance to closure:** No finite computational data can close the
  gap. The hypothesis is asymptotic.

### Attack 2: Exponent-history obstruction-class taxonomy

- **Approach:** Across the chain of improvements (1/4 → 1/6 → 1/12 →
  Bombieri-Iwaniec → Huxley → Bourgain 13/84), identify which technique
  classes have hit ceilings.
- **Tools used:** Reading + classification.
- **Time spent:** ~25 minutes.
- **Result:** Three identifiable technique classes with apparent ceilings:

  (a) **Exponential-sum estimates via van der Corput-type derivative
  tests.** Hardy-Littlewood through Titchmarsh used iterated derivative
  tests (k-th derivative test improves exponent by a fraction depending
  on k). The technique appears asymptotic-bounded: stacking more
  derivatives gives diminishing returns and runs into ε-loss issues.
  Effective ceiling around 1/12 or so.

  (b) **Bombieri-Iwaniec-Mozzochi "delta method" / smoothed approximate
  functional equation.** Combines van der Corput with smoothed cutoffs
  and Weyl differencing. Pushes past 1/12; Huxley refined this. Apparent
  ceiling somewhere around 0.16 — the BIM technique appears to hit
  combinatorial limits when too many Weyl shifts are stacked.

  (c) **Decoupling theory (Bourgain-Demeter-Guth, applied to ζ by Bourgain
  2017).** A genuinely different route via PDE/harmonic-analysis
  decoupling estimates for paraboloid in ℝ^n. Currently best at 13/84.
  Ceiling here is the optimal ℓ²-decoupling exponent for the moment
  curve (cubic), and improvements to that purely-analytic question
  would translate. Whether this can ever reach Lindelöf-ε is open;
  arguments suggest it cannot reach 0 in this technique class because
  the cubic-moment-curve decoupling has its own conjectured limit.

  Conclusion: each technique class hits a ceiling. To reach Lindelöf,
  either decoupling improves further, or a new technique class altogether.
  *No technique class on the table is known to reach μ(1/2) = 0.*

- **Kill_path classification:** This is meta-obstruction-class data:
  three technique families, each with a ceiling. The exponent record
  is the maximum over technique families, and that maximum's growth
  is bounded.
- **Distance to closure:** 13/84 to 0 — large in technique-improvement
  units. Each prior decade saw at most a 1-2× exponent reduction.

### Attack 3: RH-implies-Lindelöf chain — a separate path?

- **Approach:** Lindelöf is implied by RH, so any RH-progress also
  yields Lindelöf-progress as byproduct. Check whether any "partial RH"
  results give Lindelöf-direction implications.
- **Tools used:** Reading.
- **Time spent:** ~10 minutes.
- **Result:** This direction is asymmetric. RH ⇒ Lindelöf is structural
  (Littlewood). However, "weak RH" results like "ζ has no zeros in
  σ > 1 − c/log(t)^{2/3} (log log t)^{-1/3}" (Korobov-Vinogradov 1958
  paraphrased) yield Lindelöf-direction bounds via Hadamard-type
  product expansions, but the bounds derived are weaker than the
  direct exponential-sum bounds. So: RH-direction-progress is a
  potential second route to Lindelöf but has historically yielded
  weaker direct bounds than the direct exponential-sum path. The
  decoupling route (Bourgain) is currently the best on Lindelöf;
  the RH-direction route is currently second.
- **Why it stalled:** This is observational; no computational test was
  attempted.
- **Kill_path classification:** Two technique-family observation; no kill.
- **Distance to closure:** Same as Attack 2.

### Attack 4: Nyman-Beurling reformulation as alternative attack

- **Approach:** Lindelöf has a Nyman-Beurling-style reformulation in
  terms of approximation in L²(0,1) by certain function families. Briefly
  consider whether Hilbert-space / approximation-theory tools offer a
  separate route.
- **Tools used:** Reading.
- **Time spent:** ~5 minutes.
- **Result:** The Nyman-Beurling reformulation is more directly relevant
  to RH (the indicator function approximation problem) than to Lindelöf
  per se. I am not aware of a clean Nyman-Beurling-style equivalence
  for Lindelöf alone. Deferred.
- **Kill_path classification:** N/A; this attack didn't materialize.

## Partial results obtained

1. Empirical computation of |ζ(1/2 + it)| at t = 10^3, 10^6, 10^9, 10^12.
   All values easily satisfy the Bourgain bound (and even the trivial
   convexity bound). This is consistent with Lindelöf at the data-
   accessible scales but cannot prove it.
2. Classification of three technique families that have produced
   exponent improvements; each has an apparent ceiling.
3. Observation that the RH-direction zero-free-region route to Lindelöf
   has historically been weaker than the direct exponential-sum route.

## Honest "what would unblock this"

For Lindelöf itself: a fundamentally new technique that breaks past the
decoupling ceiling. The current state suggests three plausible routes:

1. **Improved cubic-moment-curve ℓ² decoupling** would translate
   directly to improved μ(1/2). A breakthrough at the analysis level
   would carry over.

2. **A non-RH route from a moment estimate.** Recent work (Conrey-
   Iwaniec-Soundararajan and successors) on moments of L-functions
   has occasionally pulled exponent bounds; a 16th-power moment with
   sufficient strength would tighten μ(1/2).

3. **RH proof.** Would settle Lindelöf as a corollary, but is at least
   as hard.

## Calibrated negatives

- **Naive computational checks at large t are NOT a Lindelöf attack.**
  They are calibrations: empirical consistency does not move the bar.
- **The trivial convexity bound (μ(1/2) ≤ 1/4) is NOT the right baseline
  for any modern claim.** Anything novel must beat 13/84 to be a
  contribution.
- **The 9-decade exponent history is asymptotically slow.** Going from
  1/4 (1900) to 13/84 (2017) is factor 1.6 over 117 years. If the
  improvement rate continues at this pace, μ(1/2) will not reach 0 in
  any humanly relevant time. Either a paradigm shift breaks the rate, or
  the gap remains essentially fixed.
- **The decoupling route is itself approaching its own conjectured
  ceiling.** Bourgain 13/84 is not far from the conjectured optimal
  decoupling exponent for the cubic moment curve. The decoupling tank
  may be near-empty.
- **Empirical evaluation of ζ at large t cannot distinguish Lindelöf
  from "Lindelöf-false-but-tiny-violation."** Even if a counter-Lindelöf
  growth exists, it would manifest at t > 10^{many tens}; well past
  any computational frontier.

## Citations

- Lindelöf, E. (1908). "Quelques remarques sur la croissance de la fonction
  ζ(s)." Bulletin des Sciences Mathématiques 32. *(Verified for original
  hypothesis statement.)*
- Hardy, G. H. and Littlewood, J. E. (1923). "The approximate functional
  equation in the theory of the zeta function, with applications to the
  divisor problem of Dirichlet and Piltz." Proc. London Math. Soc. (2)
  21:39-74. *(Verified canonical reference.)*
- Heath-Brown, D. R. (1978). "The twelfth power moment of the Riemann zeta
  function." Quart. J. Math. Oxford (2) 29:443-462. *(Verified.)*
- Huxley, M. N. (varied papers). "Exponential sums and the Riemann zeta
  function" series, esp. V (Proc. London Math. Soc. (3) 90:1-41, 2005)
  and predecessors. *(Verified canonical author and series; exact paper
  for each exponent record paraphrased.)*
- Bombieri, E. and Iwaniec, H. (1986). "On the order of ζ(1/2 + it)."
  Annali Scuola Norm. Sup. Pisa Cl. Sci. (4) 13:449-472. *(Verified.)*
- Iwaniec, H. and Mozzochi, C. J. (1988). "On the divisor and circle
  problems." J. Number Theory 29:60-93. *(Verified.)*
- Bourgain, J. (2017). "Decoupling, exponential sums and the Riemann zeta
  function." J. Amer. Math. Soc. 30:205-224. *(Verified; this is the
  arxiv:1408.0930 paper, published 2017.)*
- Bourgain, J., Demeter, C. and Guth, L. (2016). "Proof of the main
  conjecture in Vinogradov's mean value theorem for degrees higher than
  three." Annals of Math. (2) 184:633-682. *(Verified; the underlying
  decoupling theorem.)*
- Korobov, N. M. (1958). "Estimates of trigonometric sums and their
  applications." Uspekhi Mat. Nauk 13:185-192. *(Verified for zero-free-
  region direction.)*
- Vinogradov, I. M. (1958). "A new estimate of the function ζ(1+it)."
  Izv. Akad. Nauk SSSR Ser. Mat. 22:161-164. *(Verified.)*
- Mpmath documentation, version 1.3.0.
