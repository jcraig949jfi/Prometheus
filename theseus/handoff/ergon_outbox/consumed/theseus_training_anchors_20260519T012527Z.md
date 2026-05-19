# Theseus → Ergon Training Anchor Handoff

Generated: 2026-05-19T01:25:27.925166+00:00
Selection: top 100 records with training_weight ≥ 0.5 and verdict ∈ ['SHADOW_CATALOG', 'PROMOTED']

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

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00006
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d35697176438d54e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_124` and `conductor` of elliptic_curves `7344.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d35697176438d54e emitted 2026-05-18T17:35:48.789878+00:00
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
id: anchor-knots_x_elliptic_curves-00007
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3a90397ee4269e08
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `conductor` of elliptic_curves `9152.y1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a90397ee4269e08 emitted 2026-05-18T17:35:48.791878+00:00
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
id: anchor-knots_x_elliptic_curves-00008
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2ad888aaaa95aaf6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_16` and `torsion` of elliptic_curves `7257.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2ad888aaaa95aaf6 emitted 2026-05-18T17:35:48.794878+00:00
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
id: anchor-knots_x_elliptic_curves-00009
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b976a75d0b387b85
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_6` and `torsion` of elliptic_curves `8514.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b976a75d0b387b85 emitted 2026-05-18T17:35:48.795880+00:00
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
id: anchor-knots_x_elliptic_curves-00010
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0af9761f5ecfffa3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_7` and `rank` of elliptic_curves `5040.bl1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0af9761f5ecfffa3 emitted 2026-05-18T17:35:48.799879+00:00
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
id: anchor-knots_x_elliptic_curves-00011
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=583a66692092d75d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_7` and `tamagawa_product` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 583a66692092d75d emitted 2026-05-18T17:35:48.801879+00:00
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
id: anchor-knots_x_elliptic_curves-00012
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7271d3439a71f08e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `5_2` and `conductor` of elliptic_curves `329.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7271d3439a71f08e emitted 2026-05-18T17:35:48.804879+00:00
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
id: anchor-knots_x_elliptic_curves-00013
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7b5c8ec67755161b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `5_2` and `rank` of elliptic_curves `9600.bm2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b5c8ec67755161b emitted 2026-05-18T17:35:48.807879+00:00
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
id: anchor-knots_x_elliptic_curves-00014
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ce6a649563d31877
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_3` and `torsion` of elliptic_curves `3136.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ce6a649563d31877 emitted 2026-05-18T17:35:48.810879+00:00
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
id: anchor-knots_x_elliptic_curves-00015
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=644fe2dd748ef43e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_9` and `rank` of elliptic_curves `5520.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 644fe2dd748ef43e emitted 2026-05-18T17:35:48.811879+00:00
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
id: anchor-knots_x_elliptic_curves-00016
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=17f5e2455bd6b6a9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_5` and `conductor` of elliptic_curves `1876.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 17f5e2455bd6b6a9 emitted 2026-05-18T17:35:48.811879+00:00
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
id: anchor-knots_x_elliptic_curves-00017
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7a6ab5d7c0da8ff8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_9` and `torsion` of elliptic_curves `45.a8`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7a6ab5d7c0da8ff8 emitted 2026-05-18T17:35:48.813879+00:00
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
id: anchor-knots_x_elliptic_curves-00018
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=902071df86386ef5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_1` and `tamagawa_product` of elliptic_curves `8827.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 902071df86386ef5 emitted 2026-05-18T17:35:48.813879+00:00
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
id: anchor-knots_x_elliptic_curves-00019
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=81cfeb0e55fb1381
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_4` and `conductor` of elliptic_curves `1446.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 81cfeb0e55fb1381 emitted 2026-05-18T17:35:48.815879+00:00
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
id: anchor-knots_x_elliptic_curves-00020
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=40c922fb37aa04e0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_18` and `tamagawa_product` of elliptic_curves `4170.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 40c922fb37aa04e0 emitted 2026-05-18T17:35:48.815879+00:00
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
id: anchor-knots_x_elliptic_curves-00021
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=89e41bcd066260f9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_3` and `conductor` of elliptic_curves `6175.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 89e41bcd066260f9 emitted 2026-05-18T17:35:48.821880+00:00
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
id: anchor-knots_x_elliptic_curves-00022
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=42c59cda665db4cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `tamagawa_product` of elliptic_curves `830.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 42c59cda665db4cb emitted 2026-05-18T17:35:48.822879+00:00
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
id: anchor-knots_x_elliptic_curves-00023
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=20bb549f4842d0f6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_6` and `tamagawa_product` of elliptic_curves `2730.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 20bb549f4842d0f6 emitted 2026-05-18T17:35:48.822879+00:00
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
id: anchor-knots_x_elliptic_curves-00024
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6573c12b8f85270f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `torsion` of elliptic_curves `1815.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6573c12b8f85270f emitted 2026-05-18T17:35:48.825878+00:00
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
id: anchor-knots_x_elliptic_curves-00025
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9dcec1edfce45a99
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `tamagawa_product` of elliptic_curves `9292.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9dcec1edfce45a99 emitted 2026-05-18T17:35:48.827878+00:00
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
id: anchor-knots_x_elliptic_curves-00026
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b09e0bbc43206237
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_16` and `conductor` of elliptic_curves `4624.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b09e0bbc43206237 emitted 2026-05-18T17:35:48.827878+00:00
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
id: anchor-knots_x_elliptic_curves-00027
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=754e60220174d94b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_6` and `rank` of elliptic_curves `5187.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 754e60220174d94b emitted 2026-05-18T17:35:48.829879+00:00
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
id: anchor-knots_x_elliptic_curves-00028
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7e38d656ca8b1901
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_4` and `conductor` of elliptic_curves `1440.c3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7e38d656ca8b1901 emitted 2026-05-18T17:35:48.839878+00:00
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
id: anchor-knots_x_elliptic_curves-00029
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=555d14eebedad407
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `tamagawa_product` of elliptic_curves `5187.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 555d14eebedad407 emitted 2026-05-18T17:35:48.840878+00:00
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
id: anchor-knots_x_elliptic_curves-00030
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=00848633e562d0ce
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_13` and `rank` of elliptic_curves `2800.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 00848633e562d0ce emitted 2026-05-18T17:35:48.841878+00:00
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
id: anchor-knots_x_elliptic_curves-00031
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6bccbf7c9a5ba210
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_7` and `tamagawa_product` of elliptic_curves `6066.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6bccbf7c9a5ba210 emitted 2026-05-18T17:35:48.842878+00:00
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
id: anchor-knots_x_elliptic_curves-00032
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d273e13610f1e131
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_8` and `tamagawa_product` of elliptic_curves `2720.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d273e13610f1e131 emitted 2026-05-18T17:35:48.842878+00:00
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
id: anchor-knots_x_elliptic_curves-00033
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7ca94bbdee1cc4f7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `tamagawa_product` of elliptic_curves `5558.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7ca94bbdee1cc4f7 emitted 2026-05-18T17:35:48.842878+00:00
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
id: anchor-knots_x_elliptic_curves-00034
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ef627484e97bbd84
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_165` and `rank` of elliptic_curves `4624.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ef627484e97bbd84 emitted 2026-05-18T17:35:48.843878+00:00
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
id: anchor-knots_x_elliptic_curves-00035
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=69da4426dff515c9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `conductor` of elliptic_curves `2752.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 69da4426dff515c9 emitted 2026-05-18T17:35:48.847878+00:00
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
id: anchor-knots_x_elliptic_curves-00036
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b3821c8ab05daf9e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_5` and `tamagawa_product` of elliptic_curves `3325.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b3821c8ab05daf9e emitted 2026-05-18T17:35:48.848878+00:00
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
id: anchor-knots_x_elliptic_curves-00037
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=98cb59329058bfcd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_152` and `rank` of elliptic_curves `646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 98cb59329058bfcd emitted 2026-05-18T17:35:48.861881+00:00
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
id: anchor-knots_x_elliptic_curves-00038
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=47ea087435ec941a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_17` and `rank` of elliptic_curves `1113.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 47ea087435ec941a emitted 2026-05-18T17:35:48.864882+00:00
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
id: anchor-knots_x_elliptic_curves-00039
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6396c77c397c8013
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_152` and `conductor` of elliptic_curves `7344.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6396c77c397c8013 emitted 2026-05-18T17:35:48.867881+00:00
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
id: anchor-knots_x_elliptic_curves-00040
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a1cc56061aeed841
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_2` and `torsion` of elliptic_curves `486.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a1cc56061aeed841 emitted 2026-05-18T17:35:48.868881+00:00
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
id: anchor-knots_x_elliptic_curves-00041
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=26c97387aa291f77
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_152` and `torsion` of elliptic_curves `9422.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 26c97387aa291f77 emitted 2026-05-18T17:35:48.869945+00:00
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
id: anchor-knots_x_elliptic_curves-00042
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=12065ee9c4b29d0c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_21` and `rank` of elliptic_curves `3646.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 12065ee9c4b29d0c emitted 2026-05-18T17:35:48.871448+00:00
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
id: anchor-knots_x_elliptic_curves-00043
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=55b626b0d7c0c00d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_9` and `tamagawa_product` of elliptic_curves `5958.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 55b626b0d7c0c00d emitted 2026-05-18T17:35:48.872453+00:00
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
id: anchor-knots_x_elliptic_curves-00044
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8530b063b629dcd9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_3` and `conductor` of elliptic_curves `431.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8530b063b629dcd9 emitted 2026-05-18T17:35:48.873453+00:00
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
id: anchor-knots_x_elliptic_curves-00045
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2f2ad793f30914eb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_7` and `torsion` of elliptic_curves `5808.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2f2ad793f30914eb emitted 2026-05-18T17:35:48.875452+00:00
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
id: anchor-knots_x_elliptic_curves-00046
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=206dcf3a18626e1f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `tamagawa_product` of elliptic_curves `4450.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 206dcf3a18626e1f emitted 2026-05-18T17:35:48.878452+00:00
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
id: anchor-knots_x_elliptic_curves-00047
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5dac2b63470bf1d7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `rank` of elliptic_curves `2493.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5dac2b63470bf1d7 emitted 2026-05-18T17:35:48.881453+00:00
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
id: anchor-knots_x_elliptic_curves-00048
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=de19ec4fe641ba7d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_21` and `conductor` of elliptic_curves `2574.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record de19ec4fe641ba7d emitted 2026-05-18T17:35:48.883453+00:00
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
id: anchor-knots_x_elliptic_curves-00049
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5c0088aa3e7d2ff7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_152` and `rank` of elliptic_curves `7934.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5c0088aa3e7d2ff7 emitted 2026-05-18T17:35:48.884452+00:00
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
id: anchor-knots_x_elliptic_curves-00050
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=14b0871dcc66ee9a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `tamagawa_product` of elliptic_curves `1936.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 14b0871dcc66ee9a emitted 2026-05-18T17:35:48.887452+00:00
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
id: anchor-knots_x_elliptic_curves-00051
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f62df475be2d3a54
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_17` and `torsion` of elliptic_curves `3328.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f62df475be2d3a54 emitted 2026-05-18T17:35:48.888452+00:00
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
id: anchor-knots_x_elliptic_curves-00052
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7b0fe77768f06318
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_124` and `torsion` of elliptic_curves `6358.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b0fe77768f06318 emitted 2026-05-18T17:35:48.888452+00:00
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
id: anchor-knots_x_elliptic_curves-00053
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a8429ff4307d3055
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `torsion` of elliptic_curves `4032.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8429ff4307d3055 emitted 2026-05-18T17:35:48.890514+00:00
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
id: anchor-knots_x_elliptic_curves-00054
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f669c3d648e3055c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_12` and `rank` of elliptic_curves `2730.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f669c3d648e3055c emitted 2026-05-18T17:35:48.892514+00:00
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
id: anchor-knots_x_elliptic_curves-00055
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=12e1a7dea3c250b6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_5` and `torsion` of elliptic_curves `9768.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 12e1a7dea3c250b6 emitted 2026-05-18T17:35:48.896514+00:00
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
id: anchor-knots_x_elliptic_curves-00056
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d2353564d64058e6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `4_1` and `torsion` of elliptic_curves `5558.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d2353564d64058e6 emitted 2026-05-18T17:35:48.897514+00:00
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
id: anchor-knots_x_elliptic_curves-00057
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3b4902f65682cd69
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_139` and `conductor` of elliptic_curves `7920.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3b4902f65682cd69 emitted 2026-05-18T17:35:48.897514+00:00
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
id: anchor-knots_x_elliptic_curves-00058
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6b4f4aabe54c30e9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_4` and `conductor` of elliptic_curves `9210.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6b4f4aabe54c30e9 emitted 2026-05-18T17:35:48.900587+00:00
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
id: anchor-knots_x_elliptic_curves-00059
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=09c4d0e88414ac4a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `rank` of elliptic_curves `2730.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 09c4d0e88414ac4a emitted 2026-05-18T17:35:48.900587+00:00
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
id: anchor-knots_x_elliptic_curves-00060
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cd3a4ddc54943240
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `tamagawa_product` of elliptic_curves `1815.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cd3a4ddc54943240 emitted 2026-05-18T17:35:48.905571+00:00
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
id: anchor-knots_x_elliptic_curves-00061
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=75a7698377866e7e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_3` and `torsion` of elliptic_curves `4950.w2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 75a7698377866e7e emitted 2026-05-18T17:35:48.906570+00:00
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
id: anchor-knots_x_elliptic_curves-00062
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=942f9234e90bb894
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `conductor` of elliptic_curves `1960.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 942f9234e90bb894 emitted 2026-05-18T17:35:48.906570+00:00
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
id: anchor-knots_x_elliptic_curves-00063
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=da0858b628d84418
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_21` and `torsion` of elliptic_curves `822.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da0858b628d84418 emitted 2026-05-18T17:35:48.908570+00:00
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
id: anchor-knots_x_elliptic_curves-00064
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7b359b80ef62f02f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_165` and `rank` of elliptic_curves `384.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b359b80ef62f02f emitted 2026-05-18T17:35:48.911615+00:00
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
id: anchor-knots_x_elliptic_curves-00065
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=eed969564c19d9c0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `torsion` of elliptic_curves `9835.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eed969564c19d9c0 emitted 2026-05-18T17:35:48.912615+00:00
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
id: anchor-knots_x_elliptic_curves-00066
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c43bb85f721b3dc3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_4` and `tamagawa_product` of elliptic_curves `544.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c43bb85f721b3dc3 emitted 2026-05-18T17:35:48.914614+00:00
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
id: anchor-knots_x_elliptic_curves-00067
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e34255f7af8665da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `4_1` and `torsion` of elliptic_curves `9126.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e34255f7af8665da emitted 2026-05-18T17:35:48.921664+00:00
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
id: anchor-knots_x_elliptic_curves-00068
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=09b1d13cc8bff14e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_14` and `conductor` of elliptic_curves `2420.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 09b1d13cc8bff14e emitted 2026-05-18T17:35:48.922665+00:00
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
id: anchor-knots_x_elliptic_curves-00069
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=08068fc9ca967c10
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `tamagawa_product` of elliptic_curves `4752.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 08068fc9ca967c10 emitted 2026-05-18T17:35:48.933719+00:00
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
id: anchor-knots_x_elliptic_curves-00070
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fe9881898e57bf3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_10` and `torsion` of elliptic_curves `1494.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fe9881898e57bf3e emitted 2026-05-18T17:35:48.937721+00:00
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
id: anchor-knots_x_elliptic_curves-00071
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=51dc057a7c7ff567
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `conductor` of elliptic_curves `2568.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 51dc057a7c7ff567 emitted 2026-05-18T17:35:48.944719+00:00
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
id: anchor-knots_x_elliptic_curves-00072
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=676029555198e8f5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_6` and `conductor` of elliptic_curves `2646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 676029555198e8f5 emitted 2026-05-18T17:35:48.945719+00:00
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
id: anchor-knots_x_elliptic_curves-00073
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=05e2f2964951ac93
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_7` and `rank` of elliptic_curves `6946.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 05e2f2964951ac93 emitted 2026-05-18T17:35:48.946720+00:00
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
id: anchor-knots_x_elliptic_curves-00074
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b6c8d6f011f7300a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_2` and `conductor` of elliptic_curves `8496.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b6c8d6f011f7300a emitted 2026-05-18T17:35:48.950720+00:00
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
id: anchor-knots_x_elliptic_curves-00075
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2a66b476d439c192
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_2` and `torsion` of elliptic_curves `39.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a66b476d439c192 emitted 2026-05-18T17:35:48.951719+00:00
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
id: anchor-knots_x_elliptic_curves-00076
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cb8d8949c53d8907
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_139` and `rank` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cb8d8949c53d8907 emitted 2026-05-18T17:35:48.954720+00:00
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
id: anchor-knots_x_elliptic_curves-00077
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a23361d04e8874a5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_5` and `torsion` of elliptic_curves `4667.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a23361d04e8874a5 emitted 2026-05-18T17:35:48.961719+00:00
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
id: anchor-knots_x_elliptic_curves-00078
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8fadc6e4b2cef2b7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_124` and `conductor` of elliptic_curves `6700.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8fadc6e4b2cef2b7 emitted 2026-05-18T17:35:48.963719+00:00
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
id: anchor-knots_x_elliptic_curves-00079
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8bbea1d2baf97dd4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `3_1` and `rank` of elliptic_curves `4560.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8bbea1d2baf97dd4 emitted 2026-05-18T17:35:48.963719+00:00
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
id: anchor-knots_x_elliptic_curves-00080
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b72478b66384f1e1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_17` and `rank` of elliptic_curves `7030.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b72478b66384f1e1 emitted 2026-05-18T17:35:48.965719+00:00
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
id: anchor-knots_x_elliptic_curves-00081
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f6d4a6241ccce5b2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_4` and `rank` of elliptic_curves `558.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f6d4a6241ccce5b2 emitted 2026-05-18T17:35:48.965719+00:00
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
id: anchor-knots_x_elliptic_curves-00082
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5a1f25e079cc5c71
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `tamagawa_product` of elliptic_curves `2400.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5a1f25e079cc5c71 emitted 2026-05-18T17:35:48.966719+00:00
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
id: anchor-knots_x_elliptic_curves-00083
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b243de12e4ea8d12
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_1` and `conductor` of elliptic_curves `6008.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b243de12e4ea8d12 emitted 2026-05-18T17:35:48.968719+00:00
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
id: anchor-knots_x_elliptic_curves-00084
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ee9d40b71ff7cbaa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_165` and `tamagawa_product` of elliptic_curves `5040.o2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ee9d40b71ff7cbaa emitted 2026-05-18T17:35:48.972720+00:00
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
id: anchor-knots_x_elliptic_curves-00085
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=381deaf36b4802b7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `tamagawa_product` of elliptic_curves `9600.br2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 381deaf36b4802b7 emitted 2026-05-18T17:35:48.973719+00:00
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
id: anchor-knots_x_elliptic_curves-00086
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8e0beb796e409cdb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `tamagawa_product` of elliptic_curves `637.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8e0beb796e409cdb emitted 2026-05-18T17:35:48.976719+00:00
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
id: anchor-knots_x_elliptic_curves-00087
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=794d1f9e21768c8d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_20` and `rank` of elliptic_curves `9314.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 794d1f9e21768c8d emitted 2026-05-18T17:35:48.977720+00:00
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
id: anchor-knots_x_elliptic_curves-00088
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c33c3e066596e69a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_19` and `conductor` of elliptic_curves `960.c6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c33c3e066596e69a emitted 2026-05-18T17:35:48.979719+00:00
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
id: anchor-knots_x_elliptic_curves-00089
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0c4526a5ee4d4ade
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `5_2` and `torsion` of elliptic_curves `7826.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0c4526a5ee4d4ade emitted 2026-05-18T17:35:48.988720+00:00
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
id: anchor-knots_x_elliptic_curves-00090
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6eac729b2bd32cca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `rank` of elliptic_curves `546.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6eac729b2bd32cca emitted 2026-05-18T17:35:48.991723+00:00
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
id: anchor-knots_x_elliptic_curves-00091
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=34006502339a515b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `conductor` of elliptic_curves `7728.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 34006502339a515b emitted 2026-05-18T17:35:48.993719+00:00
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
id: anchor-knots_x_elliptic_curves-00092
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=83a223637fed8e1a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_10` and `tamagawa_product` of elliptic_curves `9196.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 83a223637fed8e1a emitted 2026-05-18T17:35:48.996719+00:00
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
id: anchor-knots_x_elliptic_curves-00093
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2ed0d68ee6186d2f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `tamagawa_product` of elliptic_curves `5269.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2ed0d68ee6186d2f emitted 2026-05-18T17:35:48.996719+00:00
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
id: anchor-knots_x_elliptic_curves-00094
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=539e055192373824
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_1` and `rank` of elliptic_curves `6066.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 539e055192373824 emitted 2026-05-18T17:35:48.997720+00:00
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
id: anchor-knots_x_elliptic_curves-00095
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2dbd420b9ff99b1c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_15` and `conductor` of elliptic_curves `7514.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2dbd420b9ff99b1c emitted 2026-05-18T17:35:48.998720+00:00
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
id: anchor-knots_x_elliptic_curves-00096
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=203e477965583847
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `torsion` of elliptic_curves `7934.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 203e477965583847 emitted 2026-05-18T17:35:48.998720+00:00
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
id: anchor-knots_x_elliptic_curves-00097
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2e585babad091645
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `tamagawa_product` of elliptic_curves `2088.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2e585babad091645 emitted 2026-05-18T17:35:49.001781+00:00
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
id: anchor-knots_x_elliptic_curves-00098
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=56599012e757a9a5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_3` and `torsion` of elliptic_curves `4590.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 56599012e757a9a5 emitted 2026-05-18T17:35:49.003780+00:00
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
id: anchor-knots_x_elliptic_curves-00099
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=23798685c9478565
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_3` and `torsion` of elliptic_curves `966.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 23798685c9478565 emitted 2026-05-18T17:35:49.004781+00:00
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
id: anchor-knots_x_elliptic_curves-00100
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8ac4bc3dbd8bc64a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `torsion` of elliptic_curves `3891.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ac4bc3dbd8bc64a emitted 2026-05-18T17:35:49.008782+00:00
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

