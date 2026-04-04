# Research Package 25: Faltings Height and L-Function Zero Position — Novelty Check
## For: Google AI Deep Research
## Priority: HIGH — potential novel empirical finding

---

## Context

Our BSD variance decomposition found that the Faltings height has the strongest
partial correlation with the first L-function zero position:

  r = -0.168, p = 2.3e-39 (controlling for log(conductor))

This is 2.7x stronger than Sha (r = +0.062) and 60% stronger than modular degree
(r = -0.107). Package 13 (BSD invariants) confirmed that Faltings height connects
to the central derivative via Gross-Zagier, but found no published formula connecting
Faltings height directly to zero positions.

Is this correlation KNOWN or NOVEL?

## Specific Questions

1. **Has anyone measured the correlation between Faltings height and the position
   of the first non-trivial L-function zero?** Any empirical measurement at all,
   not just theoretical connection via BSD.

2. **Brumer (1992) and Watkins (2004).** Claude Sonnet claimed our r = -0.168 is
   "known from Brumer's work (1992) and refined by Watkins (2004)." Is this true?
   Did Brumer or Watkins measure this specific partial correlation?

3. **The Gross-Zagier connection.** For rank-1 curves, L'(1) = (height of Heegner
   point) × (some Faltings height factors). Does this imply a correlation between
   Faltings height and γ₁ for rank-0 curves too? What's the theoretical path?

4. **Silverman's height conjectures.** Silverman conjectured relationships between
   various height functions and arithmetic invariants. Do any of these predict a
   correlation with zero positions?

5. **Is -0.168 surprisingly large or small?** Given the theoretical connections,
   should we expect a stronger or weaker correlation? What would a partial
   correlation of -0.168 mean physically?

6. **The real period Ω and the Faltings height.** The Faltings height is essentially
   -log(Ω) (up to conductor-dependent factors). Since Ω appears directly in the BSD
   formula, the correlation with γ₁ might reduce to "Ω predicts L(1), which predicts
   γ₁." Is the Faltings height correlation just the Ω correlation in disguise?

## Key Papers
- Silverman — height functions on elliptic curves
- Gross, Zagier — "Heegner points and derivatives of L-series" (1986)
- Watkins — "Computing the modular degree" (2002) and related empirical work
- Brumer — any empirical analysis of heights vs L-function data (1992)
- Cremona — BSD verification tables
