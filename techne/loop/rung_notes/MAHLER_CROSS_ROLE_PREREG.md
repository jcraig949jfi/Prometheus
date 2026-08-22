# Pre-registration: is `mahler_measure` correct where four roles depend on it?

Cycle 047. Written and committed **before running any authority comparison**.

## Why this target (the drift, attacked)

Block 042–046's own finding was that "real substrate + actionable intervention" had resolved to
"*my* substrate" — I never once completed the arc on code another role depends on. The scoping
enumeration (no claim, repo-wide, 12,543 files in 40 non-mine roles) says the drift is **not
structural**:

```
79 files across 7 roles import my code
   charon 41, ergon 19, aporia 7, scripts 4, sigma_kernel 4, harmonia 3, theseus 1

by DISTINCT CONSUMER-ROLE count:
   4  techne.lib.mahler_measure.mahler_measure   [charon, harmonia, scripts, sigma_kernel]
   2  prometheus_math.arsenal_meta.ARSENAL_REGISTRY
   2  prometheus_math.discovery_pipeline.DiscoveryPipeline
```

**`mahler_measure` is the highest-consumer callable I own.** Four roles, an external published
authority, and I can intervene. That is the only shape satisfying both halves of the new gate at
once, so it goes first.

## What I already knew (disclosed)

- The function exists at `techne/lib/mahler_measure.py:36`, signature `mahler_measure(coefficients)`.
- Existing tests cover **constants** (`[5] -> 5.0`, `[-7] -> 7.0`, `[c] -> |c|`), **one cyclotomic**
  (`[1,1,1,1,1] -> 1.0`), and a **shift-invariance** composition check. I read those lines.
- **No existing test compares against a published Mahler measure of a non-trivial polynomial.**
  That gap is why an authority check is worth running rather than assumed.
- I have NOT run the function on Lehmer's polynomial or any other authority value.

## Feasibility, verified before sampling

The function imports and is callable; the tests above execute today. Authority values are published
constants requiring no external service, no database, and no optional dependency (#242 is unruled,
so nothing may be installed). **Sample size is therefore fully measurable: n = 8 authority cases
plus 6 domain cases, all constructible from literals.**

## The authority set, fixed in advance

    Lehmer's polynomial  x^10+x^9-x^7-x^6-x^5-x^4-x^3+x+1   M = 1.176280818259917...
    golden ratio         x^2 - x - 1                        M = (1+sqrt 5)/2 = 1.618033988...
    Kronecker/Jensen     x - 2                              M = 2
                         2x - 1                             M = 2 (leading coeff, roots inside)
    cyclotomic Phi_1     x - 1                              M = 1
    cyclotomic Phi_5     x^4+x^3+x^2+x+1                    M = 1
    product rule         (x-2)(x-3)                         M = 6
    Kronecker's theorem  any monic integer poly with M = 1 is a product of cyclotomics and x^k

Sources: Lehmer (1933), Bull. AMS 39:461-479; Mossinghoff's Lehmer's-problem tables; Everest &
Ward, *Heights of Polynomials and Entropy in Algebraic Dynamics* (1999), ch. 1 for the product
rule and Jensen's formula.

## Predictions, committed

1. **All eight authority values agree to `rel=1e-9`.** Confidence: **high.** The function is
   central, four roles use it, and it would be surprising for the core value to be wrong.
2. **At least one DEGENERATE input is mishandled** — empty list, all-zero coefficients, or a
   leading-zero-padded vector. Confidence: **moderate.** This is the locally recurrent
   defect class's natural habitat, and existing coverage stops at constants.
3. **The product rule `M(fg) = M(f)M(g)` holds** on the cases tested. Confidence: high.

Prediction 1 and prediction 2 are deliberately opposed: I expect the mathematics to be right and
the domain edges to be wrong. **If prediction 1 fails, that is far more serious than anything this
loop has found, because four roles consume the value.**

## Decision rule, fixed in advance

- **All authority values correct AND all domain cases handled** → the capability is **VALIDATED on
  real data with four cross-role consumers**. That is a PASS on gate (c), stated as such, and the
  cycle's product is the authority test suite that did not previously exist.
- **An authority value is wrong** → fix it, measure the postcondition by name-diff, and audit
  what the four consuming roles computed with the wrong value.
- **A domain case is mishandled** → fix it in `techne/lib` (mine), and record it as instance N+1 of
  the locally recurrent class, this time in code with cross-role consumers.
- **NULL** → the function is correct everywhere including the edges. Then the cycle produces a
  regression suite and a validated capability, and I report that no defect was found rather than
  hunting for one.

## Constraints

`techne/lib/` and `prometheus_math/` only. No dependency installed. No test marked skip/xfail. An
authority test may not be made to pass by changing the expected value — if the implementation
disagrees with the literature, the implementation is what changes.
