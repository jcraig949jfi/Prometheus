# Research Package 26: Transfer Learning Across Arithmetic Families
## For: Google AI Deep Research
## Priority: MEDIUM — informs cross-family architecture design

---

## Context

Our architecture builds a unified k-NN search space where elliptic curves, modular
forms, and (eventually) higher-degree L-functions coexist. This is implicitly a
transfer learning problem: representations learned from one arithmetic family must
generalize to others.

arXiv:2502.10360 (Costa et al., Feb 2025) explicitly tested transfer learning —
training on one sub-dataset and evaluating on another. We need their specific results
to calibrate what's achievable.

## Specific Questions

1. **What were Costa et al.'s transfer learning results?** Specifically:
   - Train on classical modular forms, test on Hilbert modular forms: accuracy?
   - Train on ECs over Q, test on ECs over number fields: accuracy?
   - Train on degree-2 L-functions, test on degree-4: accuracy?
   - Which transfers worked and which degraded?

2. **What representation enables cross-family transfer?** Did they use raw
   Dirichlet coefficients, normalized coefficients, or something else?
   Does the choice of representation affect transfer success?

3. **The "universal vanishing order" hypothesis.** Their paper suggests that
   the vanishing order leaves a universal footprint in early Dirichlet
   coefficients regardless of the geometric source. How universal is this?
   Does it extend to degree-4 (genus 2) L-functions?

4. **Zero-based transfer vs coefficient-based transfer.** Our approach uses
   zeros, Costa uses coefficients. Has anyone compared which representation
   transfers better across families? Zeros are more "universal" (all governed
   by RMT), but coefficients are more "arithmetic" (encode the specific object).

5. **Charton's int2int transformer.** The integer-to-integer sequence model
   treats Dirichlet coefficients as tokens. Has this been tested for cross-
   family prediction? What were the results?

6. **The Selberg class as a unifying framework.** If all L-functions in the
   Selberg class share the same axiomatic structure, shouldn't transfer learning
   work "for free" once the degree and conductor are normalized? What breaks?

## Key Papers
- arXiv:2502.10360 — "Machine learning the vanishing order of rational L-functions"
- Charton — int2int package and sequence-to-sequence for integer sequences
- He, Lee, Oliver — transfer learning references in murmuration papers
- Kazalicki, Vlah — CNN rank prediction (2022)
