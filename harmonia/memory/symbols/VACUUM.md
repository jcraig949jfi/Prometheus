---
name: VACUUM
type: shape
version: 1
version_timestamp: 2026-04-20T23:30:00Z
immutable: true
status: active
previous_version: null
precision:
  n_walked_threshold: 4
  uniform_polarity: positive          # all observed cells in {+1, +2}; no kills
  axis_class_diversity_threshold: 2   # ≥ 2 distinct axis classes walked
  urgency_score_formula: n_walked * mean(observed_z) * axis_class_diversity / sqrt(walked_density)
  descriptor_dtypes:
    feature_id: F-id string
    n_walked: int ≥ 4
    walked_p_ids: list[P-id string]
    axis_classes_walked: list[AXIS_CLASS value]
    observed_polarity_set: set ⊂ {+1, +2}
    max_observed_z: float64 or null
    urgency_score: float64
    candidate_axis_classes: list[AXIS_CLASS value]   # classes NOT yet walked
proposed_by: Harmonia_M2_sessionA@pending
promoted_commit: pending
references:
  - F011@cb083d869
  - Pattern_18@c9335b7c2
  - Pattern_13@c9335b7c2
  - LADDER@v1
  - P028@c348113f3
redis_key: symbols:VACUUM:v1:def
implementation: null
---

## Definition

**Invariance row of uniform visibility-without-resolution.** A feature whose tensor row shows `+1` (or `+2`) across every walked projection — never `−1` or `−2` — and whose walked projections span at least two distinct axis classes. The diagnostic claim: *the resolving axis is outside the current catalog.*

**Canonical descriptor:**
```
VACUUM@v1[
    feature_id,                  # the F-id with the uniform-positive row
    n_walked,                    # number of projections tested (≥ 4)
    walked_p_ids,                # list of P-ids in the row
    axis_classes_walked,         # distinct AXIS_CLASS values across those P-ids
    observed_polarity_set,       # ⊂ {+1, +2}; never contains −1 or −2
    max_observed_z,              # optional; the strongest single-projection z
    urgency_score,               # composite; see formula in precision block
    candidate_axis_classes       # AXIS_CLASS values not yet walked — gen_11 input
]
```

A VACUUM@v1 is **diagnostic** if `n_walked ≥ 4` AND `observed_polarity_set ⊆ {+1, +2}` AND `len(set(axis_classes_walked)) ≥ 2`. All three thresholds are pinned at v1. Below any: row is "uniform but undersampled" or "uniform within one axis class," neither of which discriminates *missing-axis* from *single-axis-not-yet-completed*.

**What VACUUM is NOT:**
- Not a finding. A VACUUM is a *demand signal* — it identifies where a coordinate-system invention is needed, not what to conclude. The resolving axis, when invented, may still kill the feature.
- Not the same as Pattern 18. Pattern 18 is the recognition; VACUUM is the queryable diagnostic. Pattern 18 says "uniform visibility means resolving axis is outside the set"; VACUUM names the row that exhibits this and exposes its descriptor fields for filtering and ranking.
- Not the same as `EXHAUSTION` (proposed). EXHAUSTION is the negative-side sister diagnostic — uniform kills clustered in one axis class. Both feed gen_11's demand reader; they are distinct signals.

## Derivation / show work

Emerged from the F011 GUE first-gap investigation trajectory (sessionB/C, 2026-04-17 through 2026-04-18). The canonical VACUUM was F011's invariance row prior to the addition of P028 Katz-Sarnak:

| Projection | Verdict (pre-P028) |
|---|---|
| P050 first-gap | +1 |
| P051 N(T) unfolding | +1 |
| P021 num_bad_primes | +1 |
| P023 rank | +1 |
| P024 torsion | +1 |
| P025 CM | +1 |
| P026 semistable | +1 |

Seven projections, all `+1`, axis classes spanning preprocessing (P050, P051) and stratification (P021, P023, P024, P025, P026) — clean VACUUM by the v1 thresholds. Pattern 18 was promoted on the basis of this row; the resolution came when P028 (Katz-Sarnak family symmetry type) was added to the catalog and immediately discriminated F011 at z=5.38 spread (sessionB tick 9, 2026-04-17), confirming the diagnostic claim.

The current F011 row no longer satisfies VACUUM (it has +2 cells under P028, P020 block-shuffle, and others — resolution has happened). It is preserved here as the historical anchor.

**Why this is not over-fitting to F011.** Pattern 18 has a second confirmation pending: the proposal that EXHAUSTION (negative-side sister) co-promote requires its own anchor. VACUUM as a symbol stands on the F011 case alone because the *diagnostic correctness* was empirically validated — Pattern 18 predicted "the resolving axis is outside the catalog," P028 was added, and it resolved. The shape is general; the canonical instance is F011.

## References

**Internal:**
- F011@cb083d869 (canonical anchor — historical row pre-P028)
- Pattern_18@c9335b7c2 (the recognition pattern this symbol operationalizes)
- Pattern_13@c9335b7c2 (the negative-side sibling pattern; EXHAUSTION will operationalize)
- LADDER@v1 (sister shape; LADDER is found-structure, VACUUM is missing-coordinate)
- P028@c348113f3 (the projection that resolved F011's VACUUM, validating the diagnostic)

**Adjacent shapes (proposed but not yet symbolized):**
- `EXHAUSTION` — negative-side sister: uniform kills clustered in one axis class
- `OUTLIER` — single-specimen +2 against an axis nothing else resolves; lower-priority demand signal
- `CLIFF` — sharp step-change at a single stratum boundary
- `SUBFAMILY` — tail enrichment/depletion within a parent stratum

**External (concept lineage):**
- Pattern 18 first proposed by Harmonia_M2_sessionB (INFO post 1776422033526-0, 2026-04-17), confirmed by sessionA after P028 resolution.
- The symbol's promotion (this MD) was triggered by the gen_11 coordinate-invention design conversation with James, 2026-04-20 evening, where the demand-reader module needed a queryable name for the diagnostic.

## Data / implementation

**Diagnostic rubric (informal, pinned at v1):**

```python
def is_vacuum_v1(feature_row, axis_class_map, p_id_list):
    """
    feature_row: dict[P-id, verdict_int]  # the tensor row for one F-id
    axis_class_map: dict[P-id, AXIS_CLASS_value]
    p_id_list: list[P-id]  # which projections are considered "walked" (verdict ≠ 0)
    """
    walked = [p for p in p_id_list if feature_row.get(p, 0) != 0]
    if len(walked) < 4:
        return "INSUFFICIENT_WALK"
    polarities = {feature_row[p] for p in walked}
    if not polarities.issubset({+1, +2}):
        return "NOT_UNIFORM_POSITIVE"
    classes = {axis_class_map.get(p, "unknown") for p in walked}
    if len(classes) < 2:
        return "SINGLE_CLASS_WALK"
    return "VACUUM_DIAGNOSTIC"
```

**Urgency-score reference formula (v1):**

```
urgency = n_walked * mean(|observed_z| for walked) * len(set(axis_classes_walked)) / sqrt(walked_density)
```
where `walked_density = n_walked / total_projections_in_catalog`. Higher urgency = stronger demand signal. The formula is pinned at v1; tuning creates v2.

**Reading from Redis:**

```python
from agora.tensor import resolve_row, projections, projection_meta
row = resolve_row('F011')                        # {P-id: verdict, ...}
class_map = {p: projection_meta(p).get('axis_class', 'unknown')
             for p in projections()}
verdict = is_vacuum_v1(row, class_map, list(row.keys()))
```

(Note: `axis_class` is not yet a field on projection metadata. The `AXIS_CLASS` symbol candidate at Tier 1 of `CANDIDATES.md` proposes the taxonomy; until promoted, the class_map must be supplied externally.)

## Usage

**Tight (in inter-agent reports):**
```
F011@cb083d869: VACUUM@v1[
    n_walked=7, walked_p_ids=[P050, P051, P021, P023, P024, P025, P026],
    axis_classes_walked=[preprocessing, preprocessing, stratification, ...],
    observed_polarity_set={+1}, max_observed_z=null,
    urgency_score=18.3, candidate_axis_classes=[symmetry_type, finite_N]
]
```

**Loose (in conductor-to-James prose):**
```
F011 was a VACUUM@v1 pre-P028 — uniform +1 across seven projections spanning
two axis classes, signalling the resolving axis was outside the catalog.
P028 Katz-Sarnak resolved it.
```

**As gen_11 demand-reader output:**
```
demand_signals = [
    VACUUM@v1[feature_id=F<id>, urgency_score=<float>, ...]
    for F<id> in features() if is_vacuum_v1(...) == 'VACUUM_DIAGNOSTIC'
]
```

## Version history

- **v1** 2026-04-20T23:30:00Z — first canonicalization. Thresholds pinned: `n_walked ≥ 4`, `observed_polarity ⊆ {+1, +2}`, `len(set(axis_classes_walked)) ≥ 2`. Promotion triggered by gen_11 design conversation; canonical anchor F011 row pre-P028. Any threshold change creates v2.
