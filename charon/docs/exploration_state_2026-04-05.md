# Charon Exploration State: April 5, 2026
## What we actually know vs what we thought we knew

---

## What Survived the Disc Normalization Test

The raw (unnormalized) gap compression is real:
- Raw gap d = -0.029, 13/15 negative (verified April 4)
- r = 0.994 correlation between raw and conductor-normalized
- Within exact-conductor strata: R1 still tighter (t=-3.60, p=3e-4)

What changed: the MAGNITUDE is smaller than we reported. Conductor
normalization amplifies the effect (d = -0.045). Disc normalization
reverses it (d = +0.120). The truth is in the raw gaps (d ~ -0.03).

The effect is real but approximately 40% smaller than conductor-
normalized numbers suggested.

## What Didn't Survive

1. The heuristic explicit formula derivation: wrong sign, 50x wrong magnitude.
   Conductor inflation is NOT the mechanism.

2. The "d = -0.05" headline: inflated by conductor normalization. 
   Raw effect is d ~ -0.03.

3. The claim that zeros "encode" bad-prime arithmetic: random forest 
   can't predict Tamagawa or reduction type from individual zero vectors 
   (AUC = 0.43). The effect is statistical, not per-curve.

## What's Genuinely New and Robust

1. **Oscillator gradient:** Split mult (d=0) -> non-split (d=-0.07) -> 
   additive (d=-0.11). This gradient follows oscillator silence, 
   not conductor inflation. Three levels, monotonic.

2. **Genus-2 dose-response across 4 rank levels:** rho = -1.0.
   d = -0.20, -0.44, -0.69 for ranks 1, 2, 3. Not affected by 
   normalization concerns because all G2 curves are normalized 
   the same way (by log(conductor)).

3. **G2 Sato-Tate two-direction structure:** rank compresses, 
   symmetry type expands. Two independent spectral dimensions.

4. **Kodaira hierarchy within conductor bins:** E-type compresses 
   more than D-type at same conductor. Fiber complexity matters 
   independent of conductor.

5. **Wild ramification scaling at p=2:** f_2 dose-response from 
   d = -0.07 (tame) to -0.20 (f_2=8).

6. **Three-family confirmation:** EC, genus-2, modular forms all 
   show the sign. Five families show nothing. The boundary is 
   algebraic/geometric parameters.

## Open Questions That Need Exploration, Not Papers

### A. The normalization question (CRITICAL)
Which normalization is physically correct for comparing zero 
spacings across curves? The answer determines the effect size.
- Conductor: gives d ~ -0.045 (amplified)
- Discriminant: gives d ~ +0.12 (overcorrected, reverses sign)
- Raw: gives d ~ -0.03 (smallest, most conservative)
- Analytic conductor N/(4pi^2): gives d ~ -0.045 (same as conductor within strata)

The KS convention uses conductor because it enters the functional 
equation. But the disc/cond ratio is rank-dependent (d = -0.26).
Any normalization that uses a rank-correlated quantity will either 
amplify or suppress the gap effect.

EXPLORATION: Find a normalization that is rank-independent. Or prove
that the conductor is the correct normalization from the functional 
equation and the raw-gap comparison is conservative but not "correct."

### B. The oscillator removal mechanism (HIGH PRIORITY)
The gradient (split -> non-split -> additive) is the cleanest 
mechanistic evidence. It bypasses all normalization concerns because
it compares curves within the same rank.

EXPLORATION: 
- Can we isolate the effect of removing a SINGLE prime's oscillation?
  Compare curves identical except one has split and the other has 
  additive reduction at one specific prime.
- Does the effect scale with the SIZE of the removed oscillator?
  A removed good prime (|a_p| ~ 2*sqrt(p)) should matter more 
  than a removed multiplicative prime (|a_p| = 1).

### C. The G2 structure (HIGH PRIORITY, NORMALIZATION-INDEPENDENT)
The G2 dose-response is the strongest result because:
- All G2 curves are degree-4 L-functions, same normalization
- 4 rank levels with perfect monotonic dose-response
- 20,000 objects, high power
- The ST group analysis adds a second dimension

EXPLORATION:
- G2 with full 20+ zeros (need better LMFDB query strategy)
- G2 by bad prime structure (omega, reduction type)
- G2 regulator test (does it replicate the EC finding?)
- G2 disc/cond normalization check

### D. Why does the component group affect only later gaps? (UNKNOWN)
Tamagawa rho is near zero at z5-z6 but -0.07 at z19-z20.
This spectral localization is unexplained. Is there a frequency-
domain explanation? Do different Fourier modes of the explicit 
formula couple to different gap positions?

### E. The ADE classification connection (SPECULATIVE)
Kodaira types follow ADE: I_n ~ A_{n-1}, I*_n ~ D_{n+4}, 
II*/III*/IV* ~ E_8/E_7/E_6. The compression scales with fiber 
complexity. Does it scale specifically with the rank of the 
Dynkin diagram? This would connect to representation theory.

### F. Cross-family bridges (LONG TERM)
The three confirmed families have signature correlation r > 0.91.
Can we find individual objects from different families whose gap 
vectors cluster together? This was Agent 5's secondary mission 
but needs full zero vectors, not just z1-z3.

## What I Should Stop Doing

1. Stop rewriting the paper every time we learn something new
2. Stop treating negative results as failures (the disc test is 
   the most important result today)
3. Stop generating research packages for Gemini when we have 
   testable hypotheses we can run ourselves
4. Stop calling things "confirmed" or "killed" when the truth 
   is nuanced (the normalization question makes most effect 
   sizes uncertain by a factor of ~2)

## What I Should Keep Doing

1. Keep cracking. Every crack has produced a surprise.
2. Document what we learn, not what we plan to publish.
3. Run the normalization-independent tests first (within-rank, 
   within-conductor, G2 dose-response, oscillator gradient).
4. Trust the raw gaps over any normalized version.
5. When a result seems clean, look for the normalization artifact.

---

## Path A/B/C Results (April 5, 8:15 AM)

### PATH A: The rank effect is a SCALE effect, not SHAPE

Mean-spacing normalized gap d = +0.005, 7/14 negative (coin flip).
When each curve's gaps are divided by its own mean gap, the rank 
difference VANISHES. All gaps shrink equally for rank-1. No structured
oscillation pattern in the normalized gap ratios.

Four normalizations compared:
- RAW: d = -0.029, 11/15 neg (real, small)
- Conductor: d = -0.045, 13/15 neg (amplified)
- Geometric mean: d = +0.069, 0/15 neg (overcorrected)
- Discriminant: d = +0.120, 0/15 neg (severely overcorrected)

Within exact conductor: p = 3.5e-4. The effect IS real.
But it's uniform scale compression, not structured shape change.

The disc/cond ratio correlates with rank:
  R0: 2.82, R1: 2.53, R2: 1.67

### PATH B: Oscillator type distinction collapses

At exact conductor match: split vs non-split d = 0.000, p = 0.998.
The global gradient (split -> non-split -> additive) was entirely 
conductor-confounded.

What DOES survive: more additive primes within rank-1 still 
compresses (n_add=2 vs 1: RAW d=-0.027, n_add=3 vs 1: d=-0.070).
Higher total conductor exponent within additive curves compresses 
(Q4 vs Q1: RAW d=-0.072).

### Revised Understanding

The effect is real, small (raw d ~ -0.03), and uniform (scale not
shape). The "structured gap pattern" with dead zones and reversals
was a normalization artifact layered on top of a uniform shift.

What's genuinely interesting:
1. WHY do rank-1 curves have uniformly tighter spacing? Not explained
   by conductor normalization since it persists within exact conductor.
2. WHY does the number of additive primes matter within rank-1?
3. The G2 dose-response (rho=-1.0 across 4 ranks) -- is this also 
   a scale effect or does G2 show genuine shape differences?
4. The cross-family boundary (algebraic yes, analytic no) still holds.
