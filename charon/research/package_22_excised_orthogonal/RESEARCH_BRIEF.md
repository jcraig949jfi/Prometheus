# Research Package 22: The Excised Orthogonal Ensemble — Predictions for Zeros 5-19
## For: Google AI Deep Research
## Priority: HIGHEST — directly models our empirical regime

---

## Context

Three of our seven research reports (packages 15, 16, 21) converge on the same model:
the **Excised Orthogonal Ensemble** developed by Dueñez, Huynh, Keating, Miller, and
Snaith. This model modifies standard SO(2N) by conditioning on the characteristic
polynomial exceeding a cutoff at the central point, modeling the hard gap from
Waldspurger's formula at finite conductor.

Our RMT simulation used pure GUE with pinned zeros and got ARI = 0.44. Our empirical
data gives 0.49. The 0.05 gap is attributed to finite-conductor effects. The excised
model is specifically designed for this regime. If we simulate from the excised ensemble
instead of pure GUE, it might close the gap entirely.

## Specific Questions

1. **What are the exact predictions of the Excised Orthogonal Ensemble for the
   distribution of zeros 5-19?** Not just the first zero or the 1-level density,
   but the specific spacing statistics at indices 5-19 for conductor N ~ 5000.

2. **Has anyone simulated k-means clustering on excised ensemble eigenvalues?**
   Or any classification/clustering task on excised vs standard SO(2N)?

3. **What is the cutoff parameter X for conductor 5000?** The excision condition
   is |Λ_A(1)| ≥ exp(X). How does X depend on conductor? What is the correct
   value for our regime?

4. **Does the excised model predict different clustering ARI than pure SO(2N)?**
   Specifically: if we simulate rank-0 from excised SO(even) and rank-2 from
   excised SO(even) with 2 pinned zeros, will the tail clustering be tighter
   (higher ARI) than the non-excised version?

5. **Implementation details.** How do you sample from the excised ensemble?
   Rejection sampling on SO(2N)? MCMC? Is there a direct construction?
   What matrix sizes reproduce conductor-5000 statistics?

## Key Papers
- Dueñez, Huynh, Keating, Miller, Snaith — the excised model papers (2011+)
- Miller — "Investigations of zeros near the central point" (2006)
- Conrey, Farmer, Keating, Rubinstein, Snaith — L-functions Ratios Conjecture
