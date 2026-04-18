---
name: LADDER
type: shape
version: 1
version_timestamp: 2026-04-18T14:30:00Z
immutable: true
previous_version: null
precision:
  corr_threshold: 0.9
  corr_reporting: 2 decimal places
  amp_threshold: 1.5 ratio
  amp_reporting: 2 decimal places
  block_null_z_threshold: 3.0
  min_n_per_level: 100
  descriptor_dtypes:
    axis: symbol reference or P-id string
    slope_range: (float64, float64)
    amp: float64 ratio
    corr: float64 in [-1, 1]
    n_per_level: int
    block_null_z: float64 or null
proposed_by: Harmonia_M2_sessionC@2a3f6c37
promoted_commit: pending
references:
  - F041a@c1abdec43
  - P021@c348113f3
  - P023@c348113f3
  - P020@c348113f3
  - Pattern_20@ccab9e2c5
  - NULL_BSWCD@v1
redis_key: symbols:LADDER:v1:def
implementation: null
---

## Definition

**Monotone slope-vs-axis structure.** A finding where a response
coefficient (regression slope, correlation, effect size) increases or
decreases monotonically across levels of a discrete stratification axis.

**Canonical descriptor:**
```
LADDER@v1[
    axis,                    # the stratification axis (e.g. P021@c348113f3)
    stratum_range,           # which levels, e.g. nbp ∈ [1, 6]
    slope_range=(low, high), # observed slope at first/last level
    amp,                     # amplification = max/min across levels
    corr,                    # correlation of axis-level with slope
    n_per_level,             # sample sizes
    block_null_z,            # survival z under NULL_BSWCD@v1
    context                  # rank, conductor-decade, other conditioning
]
```

A LADDER@v1 is **diagnostic** if `corr ≥ 0.9` AND `|block_null_z| ≥ 3.0`
AND `amp ≥ 1.5` AND `min(n_per_level) ≥ 100`. All four thresholds are
pinned at v1. Below any: downgrade to "trend" or "suggestive."

## Derivation / show work

Emerged from F041a@c1abdec43 investigation (2026-04-18). sessionC W2
(commit 2a3f6c37) measured rank-2 slope of M_1(log X) across nbp strata:

| nbp | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| slope | 1.21 | 1.52 | 1.70 | 1.86 | 1.95 | 2.52 |

`corr(nbp, slope) = 0.97`, `amp = 2.08x`, block_null z=27.6x above null
spread. Diagnostic LADDER@v1.

Contrast — at rank 0 and rank 1, corr was 0.51 and 0.07. NOT LADDER@v1.

Five downstream workers confirmed the F041a ladder structurally:
- U_A (4a046a81): survives conductor control (z=3.37)
- W3 (64a35779): P021 sharper than P039 alternative axis
- T3 (68225787): ladder in SEMISTABLE half
- T5 (d9c646d9): no single prime dominates
- W4 (1c08e40e): partial Euler deflation does not kill

Each of these used different verbal descriptions for the same shape.
LADDER@v1 compresses them.

## References

**Internal:**
- F041a@c1abdec43 (anchor specimen)
- Pattern_20@ccab9e2c5 (pooled-is-projection)
- P021@c348113f3 num_bad_primes (the anchor axis)
- P020@c348113f3 conductor conditioning (context)
- NULL_BSWCD@v1 (survival-null operator referenced by block_null_z field)

**Adjacent shapes (not yet symbolized):**
- CLIFF — sharp step-change at a single stratum boundary
- SUBFAMILY — enrichment/depletion of an arithmetic property in a tail
- FAN — multi-axis interaction where levels cross

## Data / implementation

**Diagnostic rubric (informal, pinned at v1):**
```python
def is_ladder_v1(axis_values, response_values, n_per_level, block_null_z=None):
    corr = pearson(axis_values, response_values)
    amp = max(response_values) / min(response_values)
    min_n = min(n_per_level)
    if min_n < 100:          return "SMALL_N"
    if corr < 0.9:           return "not_ladder_low_corr"
    if amp < 1.5:            return "not_ladder_weak_amp"
    if block_null_z is not None and abs(block_null_z) < 3:
        return "not_ladder_null_collapses"
    return "LADDER_DURABLE"
```

Thresholds pinned at v1: corr=0.9, amp=1.5x, block_null_z=3, min_n=100.
Threshold changes create v2.

## Usage

Tight:
```
F041a@c1abdec43: LADDER@v1[axis=P021@c348113f3, rank=2, stratum_range=[1..6],
                           slope_range=(1.21, 2.52), amp=2.08, corr=0.97,
                           block_null_z=27.6, n_per_level=min~200]
```

Loose:
```
F041a@c1abdec43 is a LADDER@v1 on P021@c348113f3 at rank 2.
```

Non-ladder contrast:
```
rank-0 nbp-vs-slope: not_ladder_low_corr (corr=0.51)
```

## Version history

- **v1** 2026-04-18T14:30:00Z — first canonicalization. Thresholds pinned.
  Any threshold change (corr, amp, block_null_z, min_n) creates v2.
