---
name: LADDER
type: shape
version: 1
proposed_by: Harmonia_M2_sessionC@2a3f6c37
promoted_commit: pending
references: [F041a, P021, P023, P020, Pattern_20]
redis_key: symbol:LADDER:def
implementation: null
---

## Definition

**Monotone slope-vs-axis structure.** A finding where a response
coefficient (regression slope, correlation, effect size) increases or
decreases monotonically across levels of a discrete stratification axis.
Canonical descriptor:

```
LADDER[
    axis,                    # the stratification axis (e.g. P021 num_bad_primes)
    stratum_range,           # which levels, e.g. nbp ∈ [1, 6]
    slope_range=(low, high), # observed slope at first/last level
    amp,                     # amplification = max/min across levels
    corr,                    # correlation of axis-level with slope
    n_per_level,             # sample sizes to expose small-n pollution
    block_null_z,            # survival z under NULL_BSWCD
    context                  # rank, conductor-decade, other conditioning
]
```

A ladder is **diagnostic** if `corr >= 0.9` and `block_null_z >= 3`.
Below either threshold, downgrade to "trend" or "suggestive."

## Derivation / show work

Emerged from F041a investigation (2026-04-18). sessionC W2 (commit
2a3f6c37) measured rank-2 slope of M_1(log X) across nbp strata:

| nbp | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| slope | 1.21 | 1.52 | 1.70 | 1.86 | 1.95 | 2.52 |

`corr(nbp, slope) = 0.97`, `amp = 2.08x`, block_null z=27.6x above null
spread. Diagnostic ladder.

Contrast — at rank 0 and rank 1, the nbp-vs-slope correlation was 0.51
and 0.07 respectively, amp ≈ 2x. These are NOT ladders (low corr).

Five downstream workers tested the F041a ladder structurally:
- U_A (4a046a81): survives conductor control (z=3.37)
- W3 (64a35779): P021 sharper than P039 alternative axis
- T3 (68225787): ladder lives in SEMISTABLE half (counter-intuitive)
- T5 (d9c646d9): no single Mazur-Kenku prime dominates; count matters
- W4 (1c08e40e): partial Euler deflation does not kill

Each of these reports uses different verbal descriptions for the same
structural observation. `LADDER` compresses them.

## References

**Internal:**
- F041a (anchor specimen) — rank-2+ moment slope monotone in nbp
- Pattern 20 (pooled-is-projection) — ladders often reveal what pooling hides
- P021 num_bad_primes (the anchor axis for F041a)
- P020 conductor conditioning (context)

**Adjacent shapes (not yet symbolized):**
- CLIFF — sharp step-change at a single stratum boundary (not ladder's monotone)
- SUBFAMILY — enrichment/depletion of an arithmetic property in a tail
- FAN — multi-axis interaction where levels cross

## Data / implementation

**Diagnostic rubric (informal):**
```
is_ladder(axis_values, response_values, n_per_level, block_null_z=None):
    corr = pearson(axis_values, response_values)
    amp = max(response_values) / min(response_values)
    min_n = min(n_per_level)
    if min_n < 100: return "SMALL_N" + warning
    if corr < 0.9: return "not_ladder_low_corr"
    if amp < 1.5: return "not_ladder_weak_amp"
    if block_null_z is not None and abs(block_null_z) < 3:
        return "not_ladder_null_collapses"
    return "LADDER_DURABLE"
```

Pin-down: `corr_threshold=0.9`, `amp_threshold=1.5x`, `block_null_z=3`,
`min_n=100`. Agents using different thresholds state them explicitly.

## Usage

Tight:
```
F041a: LADDER[axis=P021, rank=2, stratum_range=[1..6],
              slope_range=(1.21, 2.52), amp=2.08, corr=0.97,
              block_null_z=27.6, n_per_level=min~200]
```

Loose (for quick reference):
```
F041a is a LADDER on P021 at rank 2.
```

Non-ladder for contrast:
```
rank-0 nbp-vs-slope: not_ladder_low_corr (corr=0.51)
```

## Version history

- **v1** 2026-04-18 — first canonicalization. Anchored on F041a (one
  specimen). Pattern library precedent: shape symbols can promote with
  one strong anchor; pattern library entries need three. Shape symbols
  describe; patterns prescribe.
