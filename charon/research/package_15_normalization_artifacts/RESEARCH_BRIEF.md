# Research Package 15: Normalization Artifacts in L-Function Zero Statistics
## For: Google AI Deep Research
## Priority: HIGH — determines whether the "BSD/Tail Wall" is real or artifact

---

## Context

We discovered a sharp "wall" in how BSD invariants predict L-function zero positions:
- BSD invariants explain 6.1% of zero-1 variance beyond conductor
- BSD invariants explain 0.01% of variance in zeros 2-20 beyond conductor
- The transition is sharp: zero 1 = +0.061 increment, zero 2 = +0.001, zeros 3+ = +0.000

Three of four council reviewers flagged that Katz-Sarnak normalization (dividing each
zero gamma_n by log(conductor N)) might CREATE this wall by construction. The argument:
normalization is designed to push higher zeros toward universal RMT statistics, so of
course arithmetic information "disappears" — it's been normalized away.

We plan to repeat the analysis on raw (unnormalized) zeros. But first we need to know:
has this specific artifact been documented before?

## Specific Questions

1. **Has anyone published a finding about L-function zeros that was later shown to be
   a normalization artifact?** Any case where a statistical pattern in normalized zeros
   vanished (or appeared) when using unnormalized zeros. Precedent matters.

2. **What information does Katz-Sarnak normalization provably preserve vs destroy?**
   The normalization gamma_n / log(N) is designed to make the mean spacing approach 1
   as N -> infinity. In the process, what arithmetic information is lost? Is the loss
   total for higher zeros, or only partial?

3. **Alternative normalizations.** Are there normalizations other than gamma_n / log(N)
   that preserve more arithmetic information? For example:
   - gamma_n / (analytic conductor)^(1/degree)
   - gamma_n * (mean spacing)^(-1) computed locally
   - Unfolding via the smooth part of N(T)
   Which is standard practice, and does the choice matter for statistical analysis?

4. **The wall at zero 2 vs ILS predictions.** The ILS support theorem predicts that
   family discrimination should persist through zeros up to index ~3-4 for conductor
   ~5000. Our wall is at zero 2 — EARLIER than ILS predicts. Is this discrepancy
   consistent with normalization compression, or does it suggest something else?

5. **Normalization and variance decomposition.** When computing R^2 of zero position
   regressed on arithmetic invariants, does normalizing the dependent variable
   (the zero position) by a function of the predictor (conductor) create statistical
   artifacts? This is a known issue in regression (normalizing Y by a function of X
   that's also a predictor creates spurious patterns).

6. **What do physicists do?** In quantum chaos and random matrix theory, when comparing
   empirical spectra to RMT predictions, what normalization is standard? Do they use
   "unfolded" spectra (mapping to unit mean spacing via the smooth density), and is
   this different from the number-theoretic gamma_n / log(N)?

## Key Papers to Start From

- Katz, Sarnak — original normalization conventions
- Rudnick, Sarnak — "Zeros of principal L-functions" (1996) — normalization details
- Bogomolny, Keating — "Gutzwiller's trace formula and spectral statistics" (spectral unfolding)
- Any paper comparing results under different L-function zero normalizations
- Conrey, Snaith — "Applications of the L-functions Ratios Conjecture" (2008)

## What Outcome Helps Us

- If the wall is a known normalization artifact: we retract the "two channels" claim
  and reframe as "normalization separates central from bulk information, as expected."
- If the wall persists under raw zeros: the finding is real, not an artifact, and the
  independence claim strengthens significantly.
- If alternative normalizations give different wall positions: the wall's location is
  normalization-dependent, but the existence of SOME separation may be robust.
