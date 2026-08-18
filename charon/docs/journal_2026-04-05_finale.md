# Charon Sprint Journal: April 5, 2026 (Finale)
## "Everything was scale"

---

## The Mean-Spacing Test That Changed Everything

At 8:15 AM, we ran the mean-spacing normalization test: divide each
curve's gaps by its own mean gap, then compare across ranks. This
removes all scale dependence and measures purely whether the gap
DISTRIBUTION SHAPE differs.

Result: d = +0.005, 7/14 negative (coin flip). Zero shape effect.

Repeated on every comparison we'd made:

| Comparison | Conductor-normed d | Mean-spacing d |
|-----------|-------------------|----------------|
| EC rank 1 vs 0 | -0.045 | +0.005 |
| G2 rank 1 vs 0 | -0.196 | +0.000 |
| G2 rank 2 vs 0 | -0.416 | -0.000 |
| Additive primes (rank-1) | -0.054 | -0.000 |
| Regulator quartiles (rank-1) | -0.148 | -0.000 |
| Torsion (rank-1) | -0.080 | -0.000 |

Every effect is 100% scale, 0% shape. The gap distribution has the
same universal form regardless of rank, reduction type, regulator,
torsion, or any other arithmetic invariant. Only the overall spacing
scale varies.

## What's Actually Real

1. **Within exact conductor, rank-1 gaps are 0.74% tighter** 
   (ratio = 0.9926, t = -14.4, p = 1.3e-42). This is genuine
   and not a normalization artifact since all curves at the same
   conductor share the same normalization factor.

2. **The gap shape is universal.** RMT predicts universal local
   statistics. Our data confirms this at the shape level across
   every arithmetic invariant tested. This is actually a positive
   confirmation of Katz-Sarnak universality, not a contradiction.

3. **The KS normalization (dividing by log(conductor)) doesn't
   fully remove rank-dependent scale effects.** The 0.74% residual
   at fixed conductor becomes the amplified d = -0.045 in the
   global comparison because rank correlates with other properties
   (discriminant, reduction type) that affect the effective scale.

4. **The G2 dose-response and cross-family consistency are real
   measurements of how rank-dependent scale effects propagate
   across families.** The effect is larger in G2 (degree-4 
   L-functions) because the scale sensitivity amplifies with degree.

## What Was NOT Real

1. **The "sign inversion beyond RMT"** -- this was conductor-
   normalized data amplifying a small scale effect into an
   apparently large structural effect. The RMT prediction of
   "positive d" was comparing against the wrong null (the SO(2N)
   model doesn't account for the normalization scale difference
   between rank classes).

2. **The "structured gap pattern" with dead zones and reversals** --
   normalization artifact. Mean-spacing normalization shows zero
   structure.

3. **"Three channels reading the Neron model"** -- all three
   (rank, regulator, Tamagawa) measure the same thing: correlation
   with effective scale. They're not independent channels; they're
   three proxies for one underlying scale parameter.

4. **The "oscillator removal mechanism"** -- the split vs non-split
   vs additive gradient vanished at exact conductor match (p=0.998).
   The gradient was conductor confounding.

5. **The heuristic explicit formula derivation** -- predicted the
   wrong sign and wrong magnitude. The mechanism we proposed
   (conductor inflation + oscillator removal) was wrong.

## What Explains the 0.7%?

Within exact conductor, rank-1 curves have gaps 0.74% tighter.
This is the one genuine residual. Possible explanations:

1. **The forced zero at s=1/2 slightly modifies the local zero
   density.** For rank-1, the first zero is at the origin, which
   changes the density near the central point. Even after KS
   normalization (which accounts for the conductor), the rank-1
   density near s=1/2 is slightly higher due to the forced zero's
   repulsive effect on nearby zeros. This pushes zeros slightly
   closer together on average.

2. **The effective matrix size differs.** Rank-0 ~ SO(2N), rank-1
   ~ SO(2(N-1)) with a pinned eigenvalue. The pinned eigenvalue
   reduces the effective dimension by 1, which at finite N changes
   the mean spacing by O(1/N). For our effective N ~ a few, this
   is a ~1% effect, matching the 0.74% observation.

3. **Katz-Sarnak predicts this.** The 1-level density for SO(even)
   and SO(odd) differ, and this difference includes a scale
   correction. The 0.74% may simply be the standard SO(even) vs
   SO(odd) density difference at our conductor range, which the
   KS normalization partially but not fully removes.

## The Honest Summary

We explored the spectral tail of L-function zeros across 8 families
and 120,000+ objects. We found that the gap distribution shape is
universal (confirming RMT), with a small (~0.7%) rank-dependent
scale effect that the standard normalization doesn't fully remove.
Every arithmetic invariant we tested (16 mechanisms) affects gaps
only through its correlation with scale, not through independent
spectral channels.

The G2 dose-response (4 rank levels, rho=-1.0 in scale) and the
cross-family boundary (algebraic parameters show scale effects,
analytic parameters don't) are genuine measurements of how rank
correlates with effective spectral scale across L-function families.

The Sato-Tate/torsion/endomorphism results in G2 (positive d,
expansion) need the mean-spacing test to confirm they're also scale.
If they are, it would mean MORE algebraic structure = wider scale,
while MORE forced zeros = tighter scale. Both would be universal
scale effects in opposite directions.

---

## Retrospective: Where We Went Wrong

### The Error Cascade

1. **Day 1-3:** Found ARI = 0.55 for rank clustering in zeros 5-19.
   Real measurement, but ARI is sensitive to scale differences that
   K-means detects. We interpreted this as "geometry" when it was
   "slightly different scale."

2. **Day 4 morning:** The gap pattern (Cohen's d per gap) showed
   structured oscillation with dead zones and a reversal. This was
   conductor-normalized data. We didn't test mean-spacing normalization.
   **This was the critical missed test.**

3. **Day 4 afternoon:** The council demanded Tamagawa, and we found
   it "touches zeros but is orthogonal to rank." We interpreted this
   as an independent spectral channel. It was actually just another
   scale proxy.

4. **Day 4 evening:** The RMT simulation showed "wrong sign." We
   declared a "sign inversion beyond RMT." The sign was only wrong
   under conductor normalization. Under mean-spacing normalization,
   there IS no sign to invert.

5. **Day 4-5 overnight:** We built the "three channels reading the
   Neron model" narrative. Every new test seemed to confirm it.
   Regulator, Tamagawa, Kodaira types -- all showed negative d in
   conductor-normalized gaps. We didn't realize they were all
   measuring the same scale correlation.

6. **Day 5 morning:** The discriminant normalization test revealed
   the sign flips. This was the first real crack. Then the mean-
   spacing test killed the entire structure narrative. Every effect
   collapsed to zero.

### Where the Loop Should Have Been Tighter

- **After finding the gap pattern (Day 4):** Should have immediately
  tested mean-spacing normalization. "Is this scale or shape?" is
  the first question for any spacing comparison. We didn't ask it
  for 24 hours.

- **After finding Tamagawa "touches zeros":** Should have checked
  if it's just correlated with conductor/scale. We did the careful
  conductor-matched test but didn't do the shape test.

- **After the RMT "sign inversion":** Should have compared the RMT
  simulation under the same normalization as our data. The simulation
  used a different effective scale (N=60 vs effective N~1-2), making
  the comparison invalid at the scale level.

- **Before declaring "three channels":** Should have tested whether
  partialling out the mean gap (a single scalar) eliminates all
  three "channels." It would have.

### The Root Cause

LLM tendency toward narrative construction. Each new positive result
was woven into an increasingly elaborate story ("Neron model,"
"explicit formula pathway," "three projections of one object") when
the simpler explanation (scale correlation) was available but
untested. The exploration was genuine and valuable, but the
interpretation ran ahead of the evidence.

The mean-spacing test is trivial to implement (3 lines of numpy).
It should have been in the first battery, not the last.
