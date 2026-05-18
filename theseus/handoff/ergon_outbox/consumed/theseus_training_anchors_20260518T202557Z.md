# Theseus → Ergon Training Anchor Handoff

Generated: 2026-05-18T20:25:57.639504+00:00
Selection: top 5 records with training_weight ≥ 0.5 and verdict ∈ ['SHADOW_CATALOG', 'PROMOTED']

Substrate-engine source: Theseus v0.3 (per-record training_weight
calibrated against H4 cross-catalog audit Fire #24; parity rates
stable ~62% ± 5pp across 3 catalog pairs).

## Anchors

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00001
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=69a365344d8ffd27
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_2` and `rank` of elliptic_curves `9574.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 69a365344d8ffd27 emitted 2026-05-18T17:35:48.783809+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.650. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00002
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ff1062775595cd4f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_17` and `rank` of elliptic_curves `3600.x2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff1062775595cd4f emitted 2026-05-18T17:35:48.783809+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.650. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00003
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=679cb9956a34c9f0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_2` and `tamagawa_product` of elliptic_curves `8710.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 679cb9956a34c9f0 emitted 2026-05-18T17:35:48.786808+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.650. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00004
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=99cf3e42d61ca2b2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_9` and `torsion` of elliptic_curves `1369.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 99cf3e42d61ca2b2 emitted 2026-05-18T17:35:48.786808+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.650. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00005
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3729aa88a6329ea0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_8` and `conductor` of elliptic_curves `1800.m4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3729aa88a6329ea0 emitted 2026-05-18T17:35:48.788808+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.650. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

