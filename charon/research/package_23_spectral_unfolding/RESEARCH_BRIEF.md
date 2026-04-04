# Research Package 23: Spectral Unfolding for L-Function Zeros — Implementation Guide
## For: Google AI Deep Research
## Priority: HIGH — required to resolve whether the BSD wall is real

---

## Context

Package 15 (normalization artifacts) revealed that our Katz-Sarnak normalization
(dividing all zeros by log(N)) is a blunt global scaling that may create the sharp
"BSD wall" between zero 1 and zero 2 as a statistical artifact. The recommended
fix is spectral unfolding — the physics approach used in quantum chaos.

We need to implement spectral unfolding on our 13K EC dataset and rerun the variance
decomposition. This package asks for the exact implementation details.

## Specific Questions

1. **The smooth counting function for EC L-functions.** For an elliptic curve
   L-function of conductor N, what is the exact smooth part N̄(T) of the zero
   counting function? Give the formula including all Gamma factor contributions.
   N(T) = N̄(T) + S(T), where S(T) is the fluctuation we want to preserve.

2. **Unfolding procedure step by step.** Given raw zeros γ₁, γ₂, ..., γ₂₀ for
   a specific EC L-function with conductor N:
   - How do we compute x_n = N̄(γ_n) for each zero?
   - What normalization makes the mean spacing exactly 1?
   - How does this differ from simply dividing by log(N)?

3. **Does unfolding preserve or destroy the BSD signal?** After unfolding, will
   the first zero still show a correlation with Faltings height? Will the wall
   persist, weaken, or vanish?

4. **Has anyone compared Katz-Sarnak normalization vs spectral unfolding for
   statistical analysis of EC L-function zeros?** Any paper that uses both and
   compares results.

5. **Implementation in Python.** What numerical libraries compute the smooth
   part of N(T) for degree-2 L-functions? Is mpmath sufficient? Do we need
   the LMFDB's own counting function code?

6. **The S(T) error term.** After unfolding, the fluctuation S(T) encodes the
   arithmetic information. What is its typical magnitude for conductor 5000?
   Is it large enough that our clustering algorithms can detect it?

## Key Papers
- Bogomolny, Keating — "Gutzwiller's trace formula and spectral statistics"
- Berry, Keating — spectral unfolding in quantum chaos
- Rubinstein — "Computational methods and experiments in analytic number theory"
- Odlyzko — numerical computation of Riemann zeta zeros (unfolding methods)
