# Cycle 051 — PRE-REGISTRATION: squarefree decomposition for `mahler_measure`

**Committed BEFORE writing the fix or running any comparison.**
Closes the reopened **HITL #266**. Track 1 build, TDD via the `math-tdd` skill.

**Confidence field RESTORED on every prediction** — cycle 050 measured my calibration curve as
flat (`p_held = 9/13 = 0.692`; `high` and `moderate` both 0.67) and found that preregs 049 and
050 had silently dropped the field the six before them carried. Restoring it is the H1a
build-debt, and these five rows are the first new data for the curve.

## The defect (measured, cycle 050)

`M(p) = |a_n| * prod max(1, |alpha_i|)` computed from `np.roots`. For an **m-fold** root,
`np.roots` displaces each copy by `eps^(1/m)`, not `eps`.

```
f    = [1,1,-1,-1] = (x+1)^2 (x-1)      all roots on |z|=1  ->  M = 1 EXACTLY
f*f  = (x+1)^4 (x-1)^2                                      ->  M = 1 EXACTLY
measured M(f*f) = 1.000146167647        error 1.5e-4;  eps^(1/4) = 1.22e-4
```

Consumer consequence: `lookup_by_M(M, tol=1e-6)` returns `[]` — **an absence read as "not in
the catalog"** — for any polynomial carrying a repeated root.

## The fix

Mahler measure is multiplicative. Squarefree-decompose over the exact integers first
(`f = c * prod_i g_i^i`, `g_i` squarefree and pairwise coprime), then
`M(f) = |c| * prod_i M(g_i)^i`. Each `g_i` has **simple roots**, so every root-finding call is
back in the well-conditioned regime. **Wrap, don't rewrite** (Standing Order #1): `sympy.sqf_list`
owns the decomposition, which is exact over `Z[x]`.

## The domain limit, stated in advance so it is not discovered as a surprise

This fixes **exactly-repeated** roots. It does **not** fix *near*-multiple roots — two genuinely
distinct roots at distance 1e-8 are ill-conditioned in the same way and carry no exact common
factor to split out. And squarefree decomposition needs **exact** coefficients, so float or
complex input must fall back to the current path. **Any claim that this "fixes the precision
problem" would be the wrong-population error a sixth time.** It fixes one named mechanism.

## Predictions, committed with confidence

1. **The known counterexample resolves exactly** — `M((x+1)^4 (x-1)^2)` returns 1.0 to within
   1e-12. Confidence: **high.** The decomposition is exact and each factor is linear.
2. **`test_property_MULTIPLICATIVITY` goes green** across Hypothesis's search at the existing
   `rel=1e-5`. Confidence: **moderate.** Hypothesis may find a *near*-multiple-root case, which
   §"domain limit" says this fix does not address.
3. **No existing authority value moves by more than 1e-12.** Confidence: **low-to-moderate.**
   Catalog entries are Salem/Lehmer-type and should already be squarefree, making the new path a
   no-op for them — but "should already be" is exactly the kind of assumption this loop keeps
   getting wrong, and I have not checked it.
4. **The squarefree path is slower** on typical (already-squarefree) input. Confidence:
   **moderate-to-high.** sympy's exact arithmetic is not free; the question is whether it is
   affordable, not whether it costs.
5. **At least one of the 8,625 catalog entries is NOT squarefree.** Confidence: **low.** Stated
   so that prediction 3's "no-op" reasoning is itself falsifiable rather than assumed.

## Kill test

**If prediction 3 fails — any existing authority value moves — the fix does not ship this
cycle.** A change that silently moves published numbers needs its own blast-radius pass and
pre-registration, not a paragraph inside a cycle about something else (cycle 045's rule,
applied to me; cycle 050 already deferred this build once on the same grounds).

## Self-guard

The postcondition is a **name-diff** via `techne/scripts/arsenal_red.py` against the cycle-050
baseline (38 failed / 4131 passed), never a count comparison, and never against a partially
written output file (cycle 048's near-miss).

*— Techne, cycle 051, before building.*
