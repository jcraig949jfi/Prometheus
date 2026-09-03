# Failure Landscape Implications

Candidate observables for Daedalus. No experiment is proposed here; these are things that
would be visible if the motif is operating.

## The prediction

If a system carries a correlational memory in its generator, its failures should be
**structured by that memory**, not uniformly distributed. Specifically, DERIVED from the motif
(none of this is measured in S1-S3):

| observable | what it would look like | why the motif predicts it |
|---|---|---|
| inaccessible phenotype families | a region of phenotype space that mutation never reaches, despite being expressible | orthogonal directions must fight W |
| spurious attractors | outputs that were never selected for and are not mixtures the designer intended | unnormalised Hebbian superposition |
| over-represented historical combinations | the output distribution has modes at past targets even under new selection | deeper basins for frequently stored patterns |
| correlated failure modes | failures cluster along the stored correlation structure rather than independently | failures inherit the geometry of W |
| deformation BEFORE macroscopic change | the failure frontier moves while mean fitness is flat | W changes continuously; phenotype expression is saturating and lags |

## The one that matters most

**Does the failure frontier deform before macroscopic adaptation is visible?**

This is the observable with the highest information value for Prometheus, because it is the
signature of the generator changing while the output has not yet moved. If measurable, it is a
direct read on "history modified the machine" as distinct from "history moved the population".

Candidate measurement, offered without commitment: hold selection constant, track the
DISTRIBUTION of offspring phenotypes around a fixed parent over generations, and ask whether
its shape changes while its mean does not.

## Honest limits

- None of the above is demonstrated in the recovered sources.
- The motif is continuous; whether these signatures survive in a discrete substrate is K5 and
  is unresolved.
- "Spurious attractor" is imported from Hopfield theory, and the equivalence map already marks
  the associative-memory reading as ANALOGICAL_ONLY. The prediction is therefore weaker than it
  sounds and should be treated as a thing to look for, not a thing to expect.
