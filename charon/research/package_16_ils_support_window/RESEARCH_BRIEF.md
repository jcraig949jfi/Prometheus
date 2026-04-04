# Research Package 16: ILS Support Window — Quantitative Zero-Index Mapping
## For: Google AI Deep Research
## Priority: HIGHEST — council members disagree on the number, need definitive answer

---

## Context

The Iwaniec-Luo-Sarnak (ILS) test function support theorem predicts that L-function
families are distinguishable only through zeros within a certain "support window."
Outside this window, all families look the same (universal RMT).

Our finding: BSD invariants predict zero 1 but NOT zeros 2-20 ("the wall"). We claimed
this is consistent with ILS. Four council reviewers gave DIFFERENT predictions for where
the ILS window should close for conductor <= 5000:

- Gemini: "sigma < 1 implies k < 1.35. Only the first zero distinguishes families."
- DeepSeek: "Fourier dual support (-2,2) corresponds to ~2.7 mean spacings — zeros up to index 3-4."
- ChatGPT: "The support interval restricts to the first 3-5 zeros."
- Claude Sonnet: "For conductor <= 5000, the crossover occurs around zero 8-12."

These range from 1.35 to 12. We need the actual, definitive calculation.

## Specific Questions

1. **For a family of elliptic curve L-functions with conductor N <= 5000, what is the
   precise zero index at which the ILS 1-level density loses its power to distinguish
   SO(even) from SO(odd)?** Give the calculation, not just a number. Show how the
   test function Fourier support maps to zero index.

2. **The key formula.** The ILS theorem involves test functions phi whose Fourier
   transform phi-hat has support in (-sigma, sigma). For sigma < 1, SO(even) and
   SO(odd) densities agree. For sigma > 1, they can differ. How does sigma translate
   to zero index n for a specific conductor N? What is the exact formula?

3. **Does the answer depend on sigma=1 vs sigma=2?** ILS proved results for sigma < 2
   (under GRH). Do different sigma values give different windows? What's the current
   best unconditional result vs conditional?

4. **Has anyone computed the 1-level density difference between SO(even) and SO(odd)
   as a function of zero index for a specific conductor range?** Not as a limit, but
   for finite conductor families. Any numerical studies.

5. **The within-symmetry-class question.** ILS predicts family DISCRIMINATION (SO(even)
   vs SO(odd)). Our finding is WITHIN SO(even) (rank 0 vs rank 2). Does ILS make ANY
   prediction about within-symmetry-class discrimination? If not, what does? Is there
   a theorem or conjecture about within-SO(even) rank discrimination from zeros?

6. **The mean spacing calculation.** For conductor N=5000:
   - What is log(N)? (approx 8.517)
   - What is the mean zero spacing near the central point? (approx 2*pi/log(N) ≈ 0.738)
   - If test function support = (-sigma, sigma), which zero indices does it "see"?
   - Work through this explicitly so we can cite exact numbers.

7. **Computational tests.** Has anyone numerically verified ILS predictions for families
   of elliptic curves at conductor <= 5000? Miller (2004, 2006) did some of this —
   what were his specific results regarding the support window and finite-conductor effects?

## Key Papers to Start From

- Iwaniec, Luo, Sarnak — "Low lying zeros of families of L-functions" (2000)
- Miller — "One and two level densities for rational families of elliptic curves" (2004)
- Miller — "Low-lying zeros of a family of elliptic curve L-functions" (2006)
- Young — "Low-lying zeros of families of elliptic curves" (2006)
- Shin, Templier — "Sato-Tate theorem for families" (2016)
- Any paper that explicitly maps ILS support to zero index for finite conductor

## What Outcome Helps Us

- If the window closes at zero index ~1-2 for N=5000: our wall is consistent with ILS,
  but the finding is "expected" not "novel."
- If the window closes at zero index ~4-5: our wall at index 2 is EARLIER than predicted,
  suggesting an artifact or additional mechanism.
- If the window closes at zero index ~8-12: our wall contradicts ILS, which is either
  very interesting or means our methodology is wrong.
- If ILS says nothing about within-SO(even) discrimination: our rank-0 vs rank-2 finding
  is genuinely beyond ILS, regardless of the window calculation.
