# Research Package 1: The Spectral Tail Finding
## For: Google AI Research Mode
## Priority: HIGHEST — this is the core finding

---

## What We Found

We built a search system over 17,314 elliptic curve isogeny classes using
low-lying zeros of their L-functions as coordinates (Katz-Sarnak normalized,
first 20 zeros). When clustering within conductor strata, the zero vectors
encode analytic rank at ARI = 0.55.

We then ran an ablation: remove the first zero (which encodes rank directly
via order of vanishing at s=1/2, per BSD). Expected result: ARI collapses
because rank IS the first zero.

**Actual result: ARI IMPROVES.**

| Zeros Used | ARI |
|-----------|-----|
| All 20 | 0.5456 |
| Drop first (1-19) | 0.5486 |
| Drop first two (2-19) | 0.5512 |
| Zeros 5-19 only | **0.5548** |
| First zero only | 0.2974 |

The rank signal is NOT in the central vanishing. It's in zeros 5-19 — the
global spectral shape. Removing central zeros monotonically improves clustering.

## What We Need From This Research

1. **Has anyone previously demonstrated that removing the first L-function zero
   improves rank-correlated clustering?** We believe this specific observation
   is not in the literature. Confirm or refute.

2. **What does Katz-Sarnak theory predict about rank information in the higher
   zeros (positions 5-20)?** The symmetry type (SO(even) vs SO(odd)) affects
   the n-level density. Does the 1-level density of zeros 5-20 carry rank
   information through the symmetry type mechanism?

3. **Are there papers on "zero repulsion" or "zero spacing statistics" that
   predict different spacing patterns for rank 0 vs rank 1 elliptic curves
   in the TAIL of the zero distribution (not near the central point)?**

4. **The Iwaniec-Luo-Sarnak (2000) one-level density paper** — does their
   framework predict that higher zeros (beyond the central region) carry
   family-distinguishing information? How does their test function support
   constraint interact with our finding?

5. **Random matrix theory comparison:** For GOE/GUE/GSE ensembles, does
   removing the smallest eigenvalue improve clustering by ensemble type?
   Is there an analogous phenomenon in random matrix theory?

## Key Papers to Start From

- Iwaniec, Luo, Sarnak — "Low lying zeros of families of L-functions" (2000)
- Katz, Sarnak — "Zeroes of zeta functions and symmetry" (1999)
- Miller — "One and two level densities for families of elliptic curves" (2004)
- Sawin, Sutherland — murmuration density formula (arXiv:2504.12295, 2025)
- Young — "Low-lying zeros of families of elliptic curves" (2006)

## Attach These Files

- `charon/reports/first_zero_ablation_2026-04-02.md` (our results)
- `charon/reports/council_review_synthesis.md` (the hostile review that prompted the ablation)
