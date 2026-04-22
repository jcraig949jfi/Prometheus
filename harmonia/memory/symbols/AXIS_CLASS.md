---
name: AXIS_CLASS
type: constant
version: 1
version_timestamp: 2026-04-21T00:05:00Z
immutable: true
status: active
previous_version: null
precision:
  taxonomy_form: enumerated controlled vocabulary
  n_values: 10
  values:
    - family_level
    - magnitude
    - ordinal
    - categorical
    - stratification
    - preprocessing
    - null_model
    - scorer
    - joint
    - transformation
  values_immutable_at_v1: true       # adding a value is a v2 bump
  example_p_ids_per_value:
    family_level: H08_faltings, H10_ade, H38_torsion_predictor
    magnitude: P003_megethos
    ordinal: P023_rank, P038_sha
    categorical: P010_galois_label, P011_lhash, P024_torsion
    stratification: P020_conductor, P021_nbp, P028_katz_sarnak
    preprocessing: P050_first_gap, P051_unfolding, P052_prime_decon
    null_model: P040_perm_null, P041_variance_decomp, P042_feature_perm, P043_bootstrap
    scorer: P001_cosine, P002_kurtosis, P034_alignment
    joint: P020_x_P023, P021_x_P024 (compositions)
    transformation: log_conductor, conductor_mod_p, prime_signature
  units: dimensionless categorical
  tagging_audit_status: PENDING (worker task seeded; complete tagging of all 37 promoted P-IDs is the v1 acceptance criterion)
proposed_by: Harmonia_M2_sessionA@pending
promoted_commit: pending
references:
  - VACUUM@v1
  - EXHAUSTION@v1
  - Pattern_13@c9335b7c2
  - Pattern_18@c9335b7c2
  - coordinate_system_catalog@c8b37d995
redis_key: symbols:AXIS_CLASS:v1:def
implementation: null
---

## Definition

**Controlled vocabulary classifying what kind of coordinate a projection is.** Without this taxonomy, VACUUM@v1 and EXHAUSTION@v1 cannot specify "axis class" precisely, and gen_11's demand reader cannot distinguish "uniform across one class" from "uniform across many classes." AXIS_CLASS@v1 pins the taxonomy at ten values, with examples per value, so every projection in the catalog can be tagged with exactly one primary class (and optionally secondary classes).

**The ten values:**

| Value | What it captures | Example P-IDs |
|---|---|---|
| `family_level` | Object-property predictors (object's intrinsic algebraic invariants used as input) | H08 Faltings, H10 ADE, H38 torsion-as-predictor |
| `magnitude` | Scale-confounded axes; should be regressed-out before other analysis | P003 Megethos |
| `ordinal` | Ranked discrete (rank, Sha order, conductor decile-as-rank) | P023 rank, P038 Sha |
| `categorical` | Unordered discrete labels (Galois group, isogeny hash) | P010 Galois-label, P011 Lhash, P024 torsion |
| `stratification` | Discrete partitions of the sample for per-stratum analysis | P020 conductor, P021 nbp, P028 Katz-Sarnak, P022 aut_grp |
| `preprocessing` | Transformations applied before measurement (unfolding, decontamination, first-gap restriction) | P050 first-gap, P051 N(T) unfolding, P052 prime decontamination |
| `null_model` | Counterfactual generators (permutation, bootstrap, model-based) | P040 perm null, P041 variance decomp, P042 feature perm, P043 bootstrap |
| `scorer` | Coupling / distance / similarity functions | P001 cosine, P002 kurtosis, P034 AlignmentCoupling |
| `joint` | Compositions of two or more axes (rank × torsion, conductor-decile × CM) | not yet in catalog as standalone; emerges in stratified analyses |
| `transformation` | Reparameterizations of a single axis (log, mod p, signature) | candidate axes from gen_11 source B (algebraic transformations) |

**Tagging convention:** each P-ID in `coordinate_system_catalog.md` carries an `axis_class:` field with its primary class. P-IDs that span multiple classes (rare but real — P028 Katz-Sarnak is both `stratification` and `family_level` because it depends on rank parity) carry an additional `secondary_classes:` list.

## Derivation / show work

The taxonomy emerged from the gen_11 coordinate-invention design conversation (2026-04-20 evening). Pattern 13 ("kills along an axis class indicate the class doesn't carry the feature") and Pattern 18 ("uniform visibility means the resolving axis is outside the catalog") both invoke "axis class" as a primitive concept, but no controlled vocabulary existed. The ten values were chosen to (a) cover all 37 currently-promoted P-IDs without ambiguity for ≥ 90% of them, (b) match the structure already implicit in `coordinate_system_catalog.md`'s informal section headers, and (c) leave room for new classes (`joint`, `transformation`) that gen_11's generators will emit.

**The 90% coverage check (informal):** scanning `coordinate_system_catalog.md` and `build_landscape_tensor.py` PROJECTIONS, the existing P-IDs map roughly:
- 4 in `family_level` (the H-prefixed killed projections that informed Pattern 13)
- 1 in `magnitude` (P003)
- 2–3 in `ordinal`
- 3–4 in `categorical`
- 12+ in `stratification`
- 4 in `preprocessing`
- 4 in `null_model`
- 3 in `scorer`
- 0 currently-promoted `joint` or `transformation` (these are gen_11 outputs)

The full tagging audit is a worker task seeded alongside this promotion (see `worker_journal_sessionA_20260420.md`); v1's acceptance criterion includes the audit completing. Until then, the class_map for VACUUM/EXHAUSTION queries is supplied externally.

## References

**Internal:**
- VACUUM@v1 (consumer — references AXIS_CLASS values in `axis_classes_walked` field)
- EXHAUSTION@v1 (consumer — references AXIS_CLASS values in `exhausted_class` and `surviving_axis_classes` fields)
- Pattern_13@c9335b7c2 (motivates the need for a controlled axis-class vocabulary on the kill side)
- Pattern_18@c9335b7c2 (motivates it on the visibility side)
- `coordinate_system_catalog.md` (where per-P-ID `axis_class` tags live)

**Adjacent constants (proposed):**
- `GATE_VERDICT@v1` — three-valued filter output, sister controlled-vocabulary symbol promoted same evening

## Data / implementation

```python
AXIS_CLASS_VALUES = {
    'family_level', 'magnitude', 'ordinal', 'categorical',
    'stratification', 'preprocessing', 'null_model', 'scorer',
    'joint', 'transformation',
}

def validate_axis_class(value):
    if value not in AXIS_CLASS_VALUES:
        raise ValueError(f"unknown axis_class {value!r}; valid: {sorted(AXIS_CLASS_VALUES)}")
    return value
```

**Per-P-ID storage convention** (catalog frontmatter or `agora.tensor.projection_meta`):
```yaml
axis_class: stratification
secondary_classes: [family_level]   # optional; used only when ambiguity is real
```

**Resolution from Redis:** `agora.tensor.projection_meta(P-id).get('axis_class')` after the tagging audit lands. Until then: external lookup via the table in this MD's Definition section.

## Usage

**In VACUUM/EXHAUSTION descriptors:**
```
VACUUM@v1[axis_classes_walked=[preprocessing, stratification, stratification, ...]]
EXHAUSTION@v1[exhausted_class=family_level, surviving_axis_classes=[stratification, preprocessing]]
```

**In coordinate_system_catalog.md per-P-ID frontmatter** (after audit lands):
```yaml
- id: P028
  label: Katz-Sarnak family symmetry type
  axis_class: stratification
  secondary_classes: [family_level]
```

**As gen_11 demand-reader filter:**
```python
"only emit demand signals where surviving classes include at least one in
 {transformation, joint} — i.e., where gen_11's own generator sources have
 fresh territory to propose into"
```

## Version history

- **v1** 2026-04-21T00:05:00Z — first canonicalization. Ten values pinned. Adding a value (e.g., a future `topological` or `proof_theoretic` class) requires a v2 bump per VERSIONING.md Rule 4 (the values list is part of the precision block). Tagging audit of all 37 promoted P-IDs seeded as worker task; v1 status carries `tagging_audit_status: PENDING` until that worker completes. Promoted alongside VACUUM@v1 and EXHAUSTION@v1 to make those symbols actually queryable.
