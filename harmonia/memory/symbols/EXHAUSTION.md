---
name: EXHAUSTION
type: shape
version: 1
version_timestamp: 2026-04-20T23:55:00Z
immutable: true
previous_version: null
precision:
  n_kills_threshold: 3
  killed_polarity: negative          # all observed cells in {-1, -2}
  same_axis_class_required: true     # kills must cluster in ONE class
  surviving_classes_threshold: 1     # at least one axis class still untested or +1
  urgency_score_formula: n_kills * mean(|observed_z|) / sqrt(killed_density)
  descriptor_dtypes:
    feature_id: F-id string
    exhausted_class: AXIS_CLASS value
    n_kills: int ≥ 3
    killed_p_ids: list[P-id string]
    surviving_axis_classes: list[AXIS_CLASS value]
    max_kill_z: float64 or null
    urgency_score: float64
proposed_by: Harmonia_M2_sessionA@pending
promoted_commit: pending
references:
  - F011@cb083d869
  - F010@cb083d869
  - Pattern_13@c9335b7c2
  - Pattern_18@c9335b7c2
  - VACUUM@v1
redis_key: symbols:EXHAUSTION:v1:def
implementation: null
---

## Definition

**Negative-side sister to VACUUM@v1.** A feature whose tensor row shows kills (`-1` or `-2`) clustered in one axis class, signalling the resolving axis is *not in that class* and probing must redirect to a different axis class. EXHAUSTION operationalizes Pattern 13 as a queryable diagnostic, the way VACUUM operationalizes Pattern 18.

**Canonical descriptor:**
```
EXHAUSTION@v1[
    feature_id,                  # the F-id with the clustered-kill row
    exhausted_class,             # the AXIS_CLASS value where kills accumulated
    n_kills,                     # number of killed projections in that class (≥ 3)
    killed_p_ids,                # list of P-ids that died
    surviving_axis_classes,      # AXIS_CLASS values not yet exhausted
    max_kill_z,                  # strongest single negative z (informative)
    urgency_score                # composite; higher = stronger redirect signal
]
```

A EXHAUSTION@v1 is **diagnostic** if `n_kills ≥ 3` AND all killed cells share the same `exhausted_class` AND `len(surviving_axis_classes) ≥ 1`. Below `n_kills = 3`: insufficient signal for redirect. If `surviving_classes = 0`: feature is dead, not exhausted (no axis class remains to redirect toward).

**What EXHAUSTION is NOT:**
- Not VACUUM. VACUUM = uniform positive ("we see it everywhere but resolve it nowhere"). EXHAUSTION = clustered kills ("this class doesn't carry it; try elsewhere").
- Not "dead feature." A feature with kills across *all* axis classes is dead. EXHAUSTION requires at least one untested or surviving axis class — it's a *redirect signal*, not a final verdict.
- Not Pattern 13 itself. Pattern 13 is the recognition; EXHAUSTION names the row that exhibits it and exposes its descriptor fields for filtering and ranking by gen_11's demand reader.

## Derivation / show work

**Anchor 1 — F011 family-level kill cluster (2026-04-17 / 2026-04-18):**

F011 GUE first-gap deficit accumulated three independent kills along the family-level / object-property axis class:
- H08 Faltings height — killed (y-intercept 0.164 outside GUE 99% CI)
- H10 ADE reduction type — killed (|Δvar|=0.006 < 0.025 threshold)
- H38 torsion-as-predictor — killed (z1 not predicted by torsion)

Three kills in one axis class (`family_level`) with surviving classes (`preprocessing`, `stratification`, `null_model`, `symmetry_type`). Pattern 13 was promoted on the basis of this cluster; redirection to preprocessing (P051 unfolding) and ultimately to symmetry_type (P028 Katz-Sarnak) followed.

**Anchor 2 — F010 NF-backbone degree-marginal kill (2026-04-17):**

F010 NF backbone via Galois-label trajectory accumulated kills along the *aggregation* axis class:
- Pooled ρ at small n: collapsed at bigsample (Pattern 20)
- Plain-permute null on decontaminated ρ: z=2.38 borderline → block-shuffle z=-0.86 firmly null
- Pattern 21 retroactively classified the original ρ=0.40 as a degree-marginal between-strata coincidence

The exhausted class here was `aggregation` (pooled vs decontaminated vs block-stratified). Surviving classes (object-level scorers like P010 Galois-label, alternative null structures) were the redirect targets, but the feature ultimately died; F010 joined F022 in tier=killed.

**Why this matters for promotion:** the second anchor (F010) is a *partial* EXHAUSTION — it satisfied the diagnostic but the redirect failed. That's still informative for gen_11: EXHAUSTION marks redirect targets, but redirects can fail. EXHAUSTION is a directional signal, not a guarantee.

## References

**Internal:**
- F011@cb083d869 (anchor 1: family-level kill cluster)
- F010@cb083d869 (anchor 2: aggregation kill cluster)
- Pattern_13@c9335b7c2 (the recognition pattern this symbol operationalizes)
- Pattern_18@c9335b7c2 (the positive-side sibling pattern; VACUUM operationalizes it)
- VACUUM@v1 (sister shape — gen_11 demand-reader emits both as DEMAND_SIGNAL variants)

**Adjacent shapes (proposed but not yet symbolized):**
- `OUTLIER` — single-specimen +2 against an axis nothing else resolves; lower-priority demand signal
- `CLIFF` — sharp step-change at a single stratum boundary
- `SUBFAMILY` — tail enrichment/depletion within a parent stratum

## Data / implementation

**Diagnostic rubric (informal, pinned at v1):**

```python
def is_exhaustion_v1(feature_row, axis_class_map, p_id_list):
    """
    Returns the EXHAUSTION descriptor if diagnostic; else a string status code.
    """
    kills = [p for p in p_id_list if feature_row.get(p, 0) < 0]
    if len(kills) < 3:
        return "INSUFFICIENT_KILLS"
    classes = [axis_class_map.get(p, "unknown") for p in kills]
    if len(set(classes)) > 1:
        return "KILLS_NOT_CLUSTERED"
    exhausted = classes[0]
    all_classes = set(axis_class_map.values())
    walked_classes = {axis_class_map.get(p, "unknown")
                      for p in p_id_list
                      if feature_row.get(p, 0) != 0}
    surviving = all_classes - walked_classes
    if len(surviving) < 1:
        return "NO_REDIRECT_TARGET"
    return {
        'feature_id': '<F-id>',
        'exhausted_class': exhausted,
        'n_kills': len(kills),
        'killed_p_ids': kills,
        'surviving_axis_classes': sorted(surviving),
        'urgency_score': len(kills) * mean_abs_z(kills) / sqrt(len(kills) / len(p_id_list))
    }
```

Reading from Redis follows the same pattern as VACUUM@v1: `resolve_row(F)` + an `axis_class_map` populated from projection metadata (or supplied externally until AXIS_CLASS@v1 promotes and a tagging audit lands).

## Usage

**Tight:**
```
F011@cb083d869: EXHAUSTION@v1[
    exhausted_class=family_level, n_kills=3,
    killed_p_ids=[P_H08_faltings, P_H10_ade, P_H38_torsion_predictor],
    surviving_axis_classes=[preprocessing, stratification, symmetry_type, null_model],
    max_kill_z=-2.4, urgency_score=8.7
]
```

**Loose:**
```
F011's family-level axis class is EXHAUSTED@v1 (three kills: Faltings, ADE,
torsion-as-predictor). Pattern 13 redirected probing to preprocessing and
symmetry_type, where P051 and P028 ultimately resolved.
```

**As gen_11 demand-reader output (alongside VACUUM):**
```
demand_signals = [
    *[VACUUM@v1[...] for F in vacuum_features],
    *[EXHAUSTION@v1[...] for F in exhaustion_features],
]
```

Composition with VACUUM: a feature can simultaneously be EXHAUSTION (kills clustered in class A) and VACUUM (uniform +1 across surviving classes). gen_11's demand reader emits both signals; the urgency_score arbitrates which to address first.

## Version history

- **v1** 2026-04-20T23:55:00Z — first canonicalization. Co-promoted with VACUUM@v1 (sister shape) the same evening as gen_11 design. Thresholds pinned: `n_kills ≥ 3`, single-class clustering, `surviving_classes ≥ 1`. Two anchors (F011 family-level, F010 aggregation) — the second is a partial-exhaustion case (redirect failed; feature died). Any threshold change creates v2.
