# Research Package 14: Tamagawa Numbers and L-Function Zero Statistics
## For: Google AI Deep Research
## Priority: HIGHEST — required by all 4 council reviewers before next experiment

---

## Context

We have demonstrated that the spectral tail of L-function zeros (indices 5-19) for
elliptic curves over Q encodes analytic rank through a channel independent of conductor,
Sha, Faltings height, modular degree, and regulator. Four independent hostile reviewers
(GPT-4.1, Claude Sonnet, Gemini 2.5 Flash, DeepSeek Reasoner) identified a critical
omission: **Tamagawa numbers were not included in our variance decomposition.**

The reviewers disagree on whether Tamagawa numbers matter:
- ChatGPT: "It will explain essentially nothing. Tamagawa numbers affect only the central
  critical value through BSD and have no known effect on high ordinates."
- DeepSeek: "This is a fatal flaw. Tamagawa numbers encode local reduction types which
  influence the functional equation and thus zero distributions globally."
- Gemini: "The Tamagawa product is a glaring omission. Local factors influence the global
  L-function and thus ALL its zeros."

We need the theory settled before running the experiment.

## Specific Questions

1. **Does the explicit formula for L-functions predict Tamagawa-dependent shifts in
   higher zeros?** The explicit formula relates zeros to sums over primes. Tamagawa
   numbers encode local reduction type at bad primes. Is there a known mechanism by
   which local Euler factors at bad primes systematically shift zeros at indices 5-19?

2. **Has anyone measured the correlation between Tamagawa product (or its log) and
   individual L-function zero positions?** Not just the central value L(1), but the
   actual imaginary ordinates of the non-trivial zeros. Any empirical study at all.

3. **What is the theoretical relationship between Tamagawa numbers and the functional
   equation beyond conductor?** The conductor encodes WHICH primes are bad. Tamagawa
   numbers encode HOW bad the reduction is. Does the "how bad" part affect zero
   statistics beyond what conductor already captures?

4. **For conductor N <= 5000, how variable are Tamagawa products?** Are they almost
   always 1-2 (as ChatGPT claims), or do they have meaningful variance? What is the
   distribution of log(Tamagawa product) in LMFDB for this conductor range?

5. **The local-to-global mechanism.** The L-function is a product of local Euler factors.
   Bad-prime local factors (which determine Tamagawa numbers) affect this product. But
   after Katz-Sarnak normalization (dividing by log N), how much of the local factor's
   influence survives in the higher zeros?

6. **Tamagawa numbers in the BSD formula.** In BSD, the leading Taylor coefficient of
   L(E,s) at s=1 equals (Sha * Tam * Omega * Reg) / |E_tor|^2. If Tamagawa product
   varies within a conductor stratum, it changes L(1) — which should affect the first
   zero's position. But does it affect zeros 5-19?

## Key Papers to Start From

- Silverman — "Advanced Topics in the Arithmetic of Elliptic Curves" (Tamagawa numbers chapter)
- Cremona — LMFDB elliptic curve tables (distributions of Tamagawa products)
- Iwaniec, Kowalski — "Analytic Number Theory" (explicit formula, local factors)
- Any empirical study connecting local reduction type to zero statistics
- The murmuration papers (He, Lee, Oliver, Pozdnyakov) — do they control for Tamagawa?

## What Outcome Helps Us

- If theory says Tamagawa cannot affect zeros 5-19 beyond conductor: we can cite this
  when the council objects, and skip the experiment (or run it as confirmation).
- If theory says Tamagawa CAN affect higher zeros: we must include it in the variance
  decomposition before claiming BSD-independence. The experiment becomes mandatory.
