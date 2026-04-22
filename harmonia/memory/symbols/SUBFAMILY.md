---
name: SUBFAMILY
type: shape
version: 1
version_timestamp: 2026-04-21T00:15:00Z
immutable: true
previous_version: null
precision:
  enrichment_ratio_threshold: 1.5
  p_value_threshold: 0.01
  min_n_in_tail: 30
  tail_definition_form: explicit predicate on a measured quantity (e.g. "L_value < 0.25" or "rank-0 low-decile")
  descriptor_dtypes:
    parent_stratum: P-id string or stratum descriptor
    tail_definition: str (must be a parseable predicate)
    enriched_properties: dict[property_name → ratio_float]
    n_in_tail: int ≥ 30
    n_outside_tail: int
    p_value: float ≤ 0.01
    pattern_30_severity: int 0-4 (algebraic-coupling check on tail-defining quantity vs enriched property)
proposed_by: Harmonia_M2_sessionA@pending
promoted_commit: pending
references:
  - F042@cc9a7543a
  - F043@c9fc25706
  - T4_low_L_tail_observation@ccbe7b623
  - LADDER@v1
  - Pattern_30@cb57f4afe
redis_key: symbols:SUBFAMILY:v1:def
implementation: null
---

## Definition

**Tail enrichment or depletion of an arithmetic property within a stratified sample.** A SUBFAMILY is not a separate stratum — it is a *tail* on an existing axis (the lowest 10% of L-values; the rank-0 low-decile; the high-Sha quartile) inside which some other property is over- or under-represented relative to the parent stratum.

**Canonical descriptor:**
```
SUBFAMILY@v1[
    parent_stratum,              # the P-id or descriptor for the parent (e.g. P023@c348113f3 + rank=0)
    tail_definition,             # parseable predicate, e.g. "L_value < 0.25" or "lowest_decile(M_1)"
    enriched_properties,         # dict mapping property -> ratio (>1 enriched, <1 depleted)
    n_in_tail,                   # count of objects in the tail (≥ 30)
    n_outside_tail,              # count outside (for ratio denominator)
    p_value,                     # significance under appropriate null
    pattern_30_severity          # algebraic-coupling check on tail-defining quantity vs enriched property (0 = independent, 1+ = caution)
]
```

A SUBFAMILY@v1 is **diagnostic** if `enrichment_ratio ≥ 1.5` for at least one property AND `p_value < 0.01` AND `n_in_tail ≥ 30` AND `pattern_30_severity ≤ 1`. The Pattern 30 severity check is critical: a tail defined by `L_value < threshold` showing enrichment in a property that algebraically determines `L_value` is a Level 2+ coupling, not a SUBFAMILY finding.

**What SUBFAMILY is NOT:**
- Not a separate stratum. A SUBFAMILY lives *inside* a parent stratum and contrasts a tail-subset against the rest of the parent. New stratum = new P-ID, not a SUBFAMILY.
- Not LADDER@v1. LADDER is monotone-across-strata; SUBFAMILY is concentrated-in-one-tail. Different shapes.
- Not a CLIFF. CLIFF is a step-change at a stratum boundary; SUBFAMILY is a concentration within a single tail without claiming the rest of the parent stratum is structurally distinct.

## Derivation / show work

Three anchors, all from rank-0 EC L-value low-tail studies (2026-04-18):

**Anchor 1 — F042 CM disc=-27 enrichment (sessionC c9a7543a):**

Among rank-0 EC at conductor decade [10⁵, 10⁶) (n=14 in the low-L tail), CM curves with discriminant −27 are 6.66× over-represented relative to the parent stratum. Other enrichments in the same tail: cm=-3 at 1.73×, class_size=3 at 1.78×, nbp=2 at 1.52×; sha>1 depleted at 0.7×. Pattern 30 severity = 0 (CM discriminant is not algebraically coupled to L-value at the level relevant to enrichment).

Subsequently downgraded from `live_specimen` to `calibration_refinement` after literature scan revealed Gross LNM 776 (1980) and Rodriguez-Villegas–Zagier (1993) describe the qualitative effect (Deuring non-maximal-order character-sum compression). Quantitative precision is novel; qualitative shape is known. SUBFAMILY shape correctly identified the structure even though the *finding* was already in the literature — the symbol catches the shape regardless of novelty.

**Anchor 2 — T4 low-L tail Sha depletion (sessionB cbe7b623):**

Among rank-0 EC, the lowest-L-value tail (Pr[L/M_1 < 0.25]) shows sha>1 depleted at 0.62× relative to the parent. This is a SUBFAMILY observation with tail_definition="L/M_1 < 0.25" and enriched_properties = {"sha=1": 1.4, "sha>1": 0.62}. Pattern 30 severity = 1 (Sha appears in the BSD identity that defines L_value; some algebraic dependence is unavoidable, but the magnitude of the depletion is not forced).

**Anchor 3 — F043 retracted but the empirical observation survives (sessionD 9fc25706):**

The original F043 finding ("anticorrelation between log(Sha) and log(A)") was retracted as a Pattern 30 Level 3 rearrangement. *However*, the underlying empirical observation that low-L-tail rank-0 curves have systematically *small* period × Tamagawa products is real and Pattern-30-clean as a SUBFAMILY: tail_definition="lowest_decile(L_value)", enriched_properties={"small_omega_real_x_prod_cp": 2.1×}. The pattern_30_severity for this expression is 0 — period and Tamagawa are algebraically independent of L-value's definition once you don't try to derive their *correlation* with Sha.

The lesson: SUBFAMILY as a shape correctly compresses what was real about F043 even though the rearrangement-claim version was wrong. Promoting SUBFAMILY now lets gen_11's specimen-pull source emit findings of this shape without re-litigating F043.

## References

**Internal:**
- F042@cc9a7543a (anchor 1: CM disc=-27 enrichment; calibration_refinement tier)
- F043@c9fc25706 (anchor 3: empirical low-L-tail period-Tamagawa depletion; the SUBFAMILY survives even though the F043 rearrangement-finding was retracted)
- LADDER@v1 (sister shape — both are stratification-derived structural patterns; LADDER is monotone-across, SUBFAMILY is concentrated-within-tail)
- Pattern_30@cb57f4afe (mandatory severity check on tail-defining quantity vs enriched property)

**External (concept lineage):**
- Gross, "Heights and the special values of L-series," LNM 776 (1980) — qualitative form of the F042 anchor effect.
- Rodriguez-Villegas & Zagier, "Square roots of central values of Hecke L-series," (1993) — closed-form for non-maximal-order Hecke L-values.

## Data / implementation

```python
def is_subfamily_v1(parent_data, tail_predicate, candidate_properties, dag):
    """
    parent_data: list of objects in parent stratum, each with attributes.
    tail_predicate: callable(obj) -> bool.
    candidate_properties: list of property accessors to check for enrichment.
    dag: agora.dag handle for Pattern 30 severity check.
    """
    in_tail = [o for o in parent_data if tail_predicate(o)]
    outside = [o for o in parent_data if not tail_predicate(o)]
    if len(in_tail) < 30:
        return "SMALL_TAIL"
    enriched = {}
    for prop in candidate_properties:
        ratio_in = mean(prop(o) for o in in_tail)
        ratio_out = mean(prop(o) for o in outside)
        if ratio_out == 0: continue
        ratio = ratio_in / ratio_out
        if ratio >= 1.5 or ratio <= 1/1.5:
            enriched[prop.__name__] = ratio
    if not enriched:
        return "NO_ENRICHMENT"
    # Pattern 30 check: is any enriched property algebraically coupled to the tail-defining quantity?
    severity = max(
        dag.coupling_severity(tail_predicate.__name__, prop_name)
        for prop_name in enriched
    )
    if severity >= 2:
        return f"ALGEBRAIC_COUPLING_LEVEL_{severity}"
    p_val = chi_squared_test(in_tail, outside, enriched)
    if p_val > 0.01:
        return "NOT_SIGNIFICANT"
    return {
        'parent_stratum': '<descriptor>',
        'tail_definition': tail_predicate.__name__,
        'enriched_properties': enriched,
        'n_in_tail': len(in_tail),
        'n_outside_tail': len(outside),
        'p_value': p_val,
        'pattern_30_severity': severity,
    }
```

The Pattern 30 check is the load-bearing piece. Without it, SUBFAMILY would re-create the F043 failure mode at scale (every tail definition that uses an L-function-derivative quantity would falsely claim enrichment in BSD-component variables).

## Usage

**Tight:**
```
F042@cc9a7543a: SUBFAMILY@v1[
    parent_stratum=(P023@c348113f3, rank=0) ∩ conductor_decade_5,
    tail_definition="L/M_1 < 0.25",
    enriched_properties={cm=-27: 6.66, cm=-3: 1.73, class_size=3: 1.78, sha>1: 0.62},
    n_in_tail=14, n_outside_tail=559372, p_value=0.0008,
    pattern_30_severity=0
]
```

**Loose:**
```
F042 is a SUBFAMILY@v1 in the rank-0 conductor-decade-5 low-L tail:
CM disc=-27 enriched 6.66×, sha>1 depleted to 0.62×. Pattern 30 clean.
The shape is real; the qualitative effect is in Gross (1980).
```

**As gen_11 specimen-pull source output:**
```
candidate_axis_proposals = [
    SUBFAMILY@v1[...]
    for tail in {lowest_decile(P), highest_decile(P) for P in interesting_axes}
    if is_subfamily_v1(parent_data, tail, candidate_properties, dag) is dict
]
```

## Version history

- **v1** 2026-04-21T00:15:00Z — first canonicalization. Three anchors at promotion (F042, T4 low-L-tail observation, F043 surviving empirical kernel post-retraction). Thresholds pinned: enrichment_ratio ≥ 1.5, p < 0.01, n_in_tail ≥ 30, pattern_30_severity ≤ 1. The Pattern 30 severity field is mandatory — without it, SUBFAMILY recapitulates F043 failure mode at scale. Promotion clears the long-standing INDEX.md "SUBFAMILY" gap.
