# Pre-registration: the hyperbolic-volume conflation, and what it costs to fix

Cycle 046. Written and committed **before measuring C_site and before any edit**.

## The defect

`load_knot_trace_field_corpus()` returns 48 hyperbolic knots, **every one carrying
`hyperbolic_volume = 0.0`**, with `_LAST_LOAD_SOURCE = "curated-only"`. KnotInfo is unavailable and
the curated fallback supplies `0.0`.

**A hyperbolic knot with volume 0 is mathematically impossible** — hyperbolic ⟹ volume > 0
(Mostow rigidity makes the volume a topological invariant, and the smallest is the figure-eight's
2.029883…, Cao–Meyerhoff 2001). So the corpus ships an impossible value as if measured. This is the
answering-outside-your-domain class — *"volume is 0"* and *"volume is unknown because the source is
absent"* shipped as one number — in real mathematical data, in code I own.

## What I already knew, and one thing I got wrong

- Cycle 045 reported **"44 non-test references"** and deferred on that number.
- **That figure is suspect and I am flagging it before it is used again.** `prometheus_math/
  topology.py` imports a *function* called `hyperbolic_volume` from `techne.lib.hyperbolic_volume`,
  which is a different thing from the *field* `entry.hyperbolic_volume`. A grep for the bare name
  counts both. The real blast radius is probably smaller than 44, and possibly much smaller.
- `_knot_trace_field_corpus.py:1183` already filters `e.hyperbolic_volume > 0.0` on one path, so
  part of the codebase treats 0.0 as "not hyperbolic" — which is exactly the conflation, encoded.
- `knot_trace_field_env.py:448` does `vol = float(e.hyperbolic_volume)` and uses it as a feature.

## Measurement 1 — C_site, as the four-part tuple

Declared before measuring, and reported whatever it comes to:

    callee edit              lines changed in the corpus module itself
    direct callers           non-test sites reading the FIELD (not the function)
    tests                    tests touching the field
    transitive type fallout  sites broken if the field's type changes float -> Optional[float]

The field/function split is resolved by hand before counting. **Cycle 045's "44" is superseded by
whatever this produces, and if it is materially smaller I will say so plainly rather than let the
larger number stand as justification for having deferred.**

## Decision rule, fixed in advance and keyed to the measured cost

- **If direct field-readers ≤ 10** → make the fallback stop asserting a false measurement, and fix
  every reader. Preferred shape: the corpus does not emit an impossible value at all.
- **If direct field-readers > 10** → do the minimum honest change that removes the impossible
  value from the *hyperbolic* corpus, leave the type alone, and report the remaining exposure with
  its cost.
- **If the fallback turns out already to be correct** and the 0.0 comes from somewhere else, the
  diagnosis is wrong and I report that; cycle 045's finding would then be misattributed.

## Predictions, committed

1. **Direct field-readers ≤ 10.** Confidence: **moderate-to-high.** Most of the 44 will be the
   same-named function, docstrings, or the corpus module's own internals.
2. **The fix will not require changing `float` → `Optional[float]`.** Confidence: **moderate.** An
   impossible value can be removed by not classifying volumeless entries as hyperbolic, without
   touching the type.
3. **At least one consumer currently treats 0.0 as a real feature value** (`knot_trace_field_env`
   line 448 is the candidate). Confidence: **high** — I have already read that line.

## Postcondition, and how it will be measured

`test_knot_trace_field_env::test_authority_figure_8_volume_is_2_0299` and
`::test_property_all_hyperbolic_knots_have_nonzero_volume` are the two currently-red tests.

**The postcondition is measured by diffing the full `prometheus_math` failure list BY NAME**, before
and after — not by a predicted count. Cycle 045 predicted 28 and got 29; that will not repeat.

**A red test may become green only by the corpus ceasing to ship impossible values.** If the
authority test cannot pass because the real volume data is genuinely absent, then it **stays red**
and I report it as red. Making an authority test pass without the authority's data would be
fabricating a measurement, which is worse than a red test.

## NULL outcome

If no honest change can remove the impossible value without either fabricating volumes or emptying
the hyperbolic corpus, that is the result: **the defect is real, unfixable without the data source,
and the corpus should be documented as unusable for volume-dependent work.** Reported as such.

## Constraints

`prometheus_math/` only. No test marked skip or xfail to move a count. No dependency installed —
HITL #242 is unruled, so it stays blocked.
