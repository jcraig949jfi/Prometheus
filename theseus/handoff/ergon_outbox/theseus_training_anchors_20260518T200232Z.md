# Theseus → Ergon Training Anchor Handoff

Generated: 2026-05-18T20:02:32.168315+00:00
Selection: top 500 records with training_weight ≥ 0.5 and verdict ∈ ['SHADOW_CATALOG', 'PROMOTED']

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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00101
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7b76478073b1f199
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_6` and `tamagawa_product` of elliptic_curves `240.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b76478073b1f199 emitted 2026-05-18T17:35:49.010781+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00102
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2073a8c99cd0923d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_3` and `torsion` of elliptic_curves `1240.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2073a8c99cd0923d emitted 2026-05-18T17:35:49.011781+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00103
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=89023dbe383026e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `tamagawa_product` of elliptic_curves `7035.l3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 89023dbe383026e3 emitted 2026-05-18T17:35:49.012781+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00104
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=03d9683b2b1cf0c9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_3` and `rank` of elliptic_curves `6240.x3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 03d9683b2b1cf0c9 emitted 2026-05-18T17:35:49.013780+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00105
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bc9eba1cc867632e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_13` and `rank` of elliptic_curves `2027.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bc9eba1cc867632e emitted 2026-05-18T17:35:49.018781+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00106
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a5bc2a74b654074a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_16` and `tamagawa_product` of elliptic_curves `4565.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a5bc2a74b654074a emitted 2026-05-18T17:35:49.021780+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00107
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a66155fd3ed1a14c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_161` and `conductor` of elliptic_curves `637.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a66155fd3ed1a14c emitted 2026-05-18T17:35:49.023780+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00108
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7340d37718c61758
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `conductor` of elliptic_curves `3822.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7340d37718c61758 emitted 2026-05-18T17:35:49.029854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00109
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5b8cde024e58dc13
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `tamagawa_product` of elliptic_curves `8925.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5b8cde024e58dc13 emitted 2026-05-18T17:35:49.030858+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00110
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=01b0bf94cc3465f9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_2` and `torsion` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 01b0bf94cc3465f9 emitted 2026-05-18T17:35:49.034854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00111
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5fd87631b655d1cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_12` and `tamagawa_product` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5fd87631b655d1cb emitted 2026-05-18T17:35:49.034854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00112
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ea0a631bb184e87f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_12` and `conductor` of elliptic_curves `9126.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ea0a631bb184e87f emitted 2026-05-18T17:35:49.034854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00113
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=73673828a72c6413
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `torsion` of elliptic_curves `9660.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 73673828a72c6413 emitted 2026-05-18T17:35:49.035855+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00114
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2b8d80c7dc1926d3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_11` and `torsion` of elliptic_curves `8904.i3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2b8d80c7dc1926d3 emitted 2026-05-18T17:35:49.035855+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00115
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f3191a19aa312dd7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_11` and `rank` of elliptic_curves `4768.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f3191a19aa312dd7 emitted 2026-05-18T17:35:49.038854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00116
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d39f4acfbb513c5f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `5_2` and `conductor` of elliptic_curves `6020.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d39f4acfbb513c5f emitted 2026-05-18T17:35:49.040853+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00117
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a7d37de5677124f2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_6` and `conductor` of elliptic_curves `6566.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a7d37de5677124f2 emitted 2026-05-18T17:35:49.041853+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00118
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=97f5174474886328
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_7` and `tamagawa_product` of elliptic_curves `782.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 97f5174474886328 emitted 2026-05-18T17:35:49.041853+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00119
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2e8251219ca81f41
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `4_1` and `torsion` of elliptic_curves `56.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2e8251219ca81f41 emitted 2026-05-18T17:35:49.042853+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00120
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=4574807fc308f06f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_8` and `torsion` of elliptic_curves `9225.u1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4574807fc308f06f emitted 2026-05-18T17:35:49.046854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00121
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ff82e2d892531e93
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_21` and `rank` of elliptic_curves `4806.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff82e2d892531e93 emitted 2026-05-18T17:35:49.047854+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00122
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0a6571b23ec56eba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_11` and `tamagawa_product` of elliptic_curves `7488.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0a6571b23ec56eba emitted 2026-05-18T17:35:49.054931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00123
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=276f252750382f34
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_4` and `tamagawa_product` of elliptic_curves `4464.x1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 276f252750382f34 emitted 2026-05-18T17:35:49.054931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00124
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=99a76255991c0559
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_3` and `tamagawa_product` of elliptic_curves `56.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 99a76255991c0559 emitted 2026-05-18T17:35:49.055931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00125
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=aa5f5619e476a61a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_6` and `conductor` of elliptic_curves `4582.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record aa5f5619e476a61a emitted 2026-05-18T17:35:49.059931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00126
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=38f7c449d15e9665
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `rank` of elliptic_curves `8103.b6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38f7c449d15e9665 emitted 2026-05-18T17:35:49.060931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00127
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e4eb33f6984ba892
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `tamagawa_product` of elliptic_curves `3534.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e4eb33f6984ba892 emitted 2026-05-18T17:35:49.063931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00128
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3940ce17c38e6193
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_5` and `rank` of elliptic_curves `4752.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3940ce17c38e6193 emitted 2026-05-18T17:35:49.066931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00129
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=433630f2c12446d4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_3` and `torsion` of elliptic_curves `2002.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 433630f2c12446d4 emitted 2026-05-18T17:35:49.068931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00130
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0c9421476b34b1cc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_1` and `conductor` of elliptic_curves `2800.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0c9421476b34b1cc emitted 2026-05-18T17:35:49.069931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00131
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ac52c0508d8ac258
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_3` and `torsion` of elliptic_curves `7920.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac52c0508d8ac258 emitted 2026-05-18T17:35:49.070931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00132
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2bdc98e58734bae1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_152` and `torsion` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2bdc98e58734bae1 emitted 2026-05-18T17:35:49.071931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00133
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b555ae5abc9661a4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_124` and `tamagawa_product` of elliptic_curves `5610.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b555ae5abc9661a4 emitted 2026-05-18T17:35:49.077931+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00134
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=280eabe0a6b8e6ce
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_5` and `conductor` of elliptic_curves `528.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 280eabe0a6b8e6ce emitted 2026-05-18T17:35:49.084979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00135
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=270d2c20b121e5f8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_8` and `tamagawa_product` of elliptic_curves `4050.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 270d2c20b121e5f8 emitted 2026-05-18T17:35:49.086979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00136
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c3e625f51c1da1be
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_145` and `rank` of elliptic_curves `2016.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c3e625f51c1da1be emitted 2026-05-18T17:35:49.087979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00137
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7fd81704a818be98
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_16` and `conductor` of elliptic_curves `7593.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7fd81704a818be98 emitted 2026-05-18T17:35:49.087979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00138
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1dce1c619bfcf505
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_14` and `conductor` of elliptic_curves `3392.k2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1dce1c619bfcf505 emitted 2026-05-18T17:35:49.088979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00139
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0e20308fa4f98a56
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_6` and `torsion` of elliptic_curves `414.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0e20308fa4f98a56 emitted 2026-05-18T17:35:49.090979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00140
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=55445d99e4b6702b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `tamagawa_product` of elliptic_curves `5269.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 55445d99e4b6702b emitted 2026-05-18T17:35:49.091983+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00141
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3a7388ffb3ee7650
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `4_1` and `torsion` of elliptic_curves `5472.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a7388ffb3ee7650 emitted 2026-05-18T17:35:49.093979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00142
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f4f059bea6a009d8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_9` and `conductor` of elliptic_curves `2576.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f4f059bea6a009d8 emitted 2026-05-18T17:35:49.096980+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00143
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=73f68f9ba479ff2f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_152` and `conductor` of elliptic_curves `8730.i4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 73f68f9ba479ff2f emitted 2026-05-18T17:35:49.097979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00144
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d3d8f4dc0d7d3dca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `4_1` and `tamagawa_product` of elliptic_curves `9450.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d3d8f4dc0d7d3dca emitted 2026-05-18T17:35:49.097979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00145
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ac15dad1acfee0a9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_20` and `conductor` of elliptic_curves `9312.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac15dad1acfee0a9 emitted 2026-05-18T17:35:49.098979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00146
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a81b3defbb102571
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_152` and `torsion` of elliptic_curves `3696.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a81b3defbb102571 emitted 2026-05-18T17:35:49.100979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00147
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=27149e478d2005b5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_124` and `conductor` of elliptic_curves `3038.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 27149e478d2005b5 emitted 2026-05-18T17:35:49.101979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00148
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c6a6b7af0c74dbac
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_15` and `rank` of elliptic_curves `8568.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c6a6b7af0c74dbac emitted 2026-05-18T17:35:49.104979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00149
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=404c1a242335cb68
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_1` and `conductor` of elliptic_curves `4160.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 404c1a242335cb68 emitted 2026-05-18T17:35:49.107979+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00150
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=4d436b5b7b55bb65
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_14` and `rank` of elliptic_curves `1680.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4d436b5b7b55bb65 emitted 2026-05-18T17:35:49.112029+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00151
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0c9220e689f710f6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_8` and `tamagawa_product` of elliptic_curves `8040.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0c9220e689f710f6 emitted 2026-05-18T17:35:49.114028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00152
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2a6c0421fbfae207
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `torsion` of elliptic_curves `8400.co3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a6c0421fbfae207 emitted 2026-05-18T17:35:49.115029+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00153
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b19f6ebff0430ecb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_3` and `torsion` of elliptic_curves `9768.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b19f6ebff0430ecb emitted 2026-05-18T17:35:49.120028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00154
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f1633a98eda57d0b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_14` and `conductor` of elliptic_curves `9570.q1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f1633a98eda57d0b emitted 2026-05-18T17:35:49.121028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00155
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8f3b553ebdb02a09
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_4` and `conductor` of elliptic_curves `2781.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8f3b553ebdb02a09 emitted 2026-05-18T17:35:49.122029+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00156
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0e3ee8da36070f5e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_124` and `torsion` of elliptic_curves `3330.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0e3ee8da36070f5e emitted 2026-05-18T17:35:49.126028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00157
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=26bf82633ac8914f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `torsion` of elliptic_curves `1764.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 26bf82633ac8914f emitted 2026-05-18T17:35:49.127028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00158
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ac47ad8111b9fe36
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_152` and `torsion` of elliptic_curves `822.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac47ad8111b9fe36 emitted 2026-05-18T17:35:49.139028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00159
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=646b8856d7357f2b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `rank` of elliptic_curves `1960.n2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 646b8856d7357f2b emitted 2026-05-18T17:35:49.146028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00160
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f82d6642f89877f0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `conductor` of elliptic_curves `404.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f82d6642f89877f0 emitted 2026-05-18T17:35:49.146028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00161
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fadad5061834414e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_11` and `conductor` of elliptic_curves `7540.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fadad5061834414e emitted 2026-05-18T17:35:49.148028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00162
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1766a3dccac78051
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_2` and `conductor` of elliptic_curves `913.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1766a3dccac78051 emitted 2026-05-18T17:35:49.149028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00163
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9c63ccb1f3ee57fa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_13` and `torsion` of elliptic_curves `4774.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9c63ccb1f3ee57fa emitted 2026-05-18T17:35:49.151028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00164
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8138b067b9d3c7d2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `10_124` and `conductor` of elliptic_curves `45.a8`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8138b067b9d3c7d2 emitted 2026-05-18T17:35:49.153028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00165
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ae26cb2a32df71d4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_18` and `torsion` of elliptic_curves `4392.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ae26cb2a32df71d4 emitted 2026-05-18T17:35:49.156037+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00166
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=66c9d431a7e88a7f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_139` and `conductor` of elliptic_curves `2352.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 66c9d431a7e88a7f emitted 2026-05-18T17:35:49.158028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00167
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=664bb040ffb4713a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_18` and `torsion` of elliptic_curves `8322.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 664bb040ffb4713a emitted 2026-05-18T17:35:49.159028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00168
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=55b15bade827b1dc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_8` and `tamagawa_product` of elliptic_curves `944.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 55b15bade827b1dc emitted 2026-05-18T17:35:49.161028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00169
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=18456d3af534cdec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_4` and `tamagawa_product` of elliptic_curves `9350.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 18456d3af534cdec emitted 2026-05-18T17:35:49.162028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00170
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6fe46b317c09943e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_17` and `conductor` of elliptic_curves `8827.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6fe46b317c09943e emitted 2026-05-18T17:35:49.163028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00171
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2ffb4e24952a0224
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_5` and `tamagawa_product` of elliptic_curves `7975.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2ffb4e24952a0224 emitted 2026-05-18T17:35:49.166028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00172
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8e1438e3c44de1a7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_4` and `rank` of elliptic_curves `7245.n3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8e1438e3c44de1a7 emitted 2026-05-18T17:35:49.168028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00173
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=41ca75416e2604e8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_9` and `torsion` of elliptic_curves `2800.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 41ca75416e2604e8 emitted 2026-05-18T17:35:49.170028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00174
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3fc8b1a7b4f1bf3c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_3` and `rank` of elliptic_curves `6840.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3fc8b1a7b4f1bf3c emitted 2026-05-18T17:35:49.174027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00175
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d4e3e107cb7937ad
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_152` and `rank` of elliptic_curves `3066.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d4e3e107cb7937ad emitted 2026-05-18T17:35:49.175027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00176
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b932efd807e4f4db
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_6` and `conductor` of elliptic_curves `3190.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b932efd807e4f4db emitted 2026-05-18T17:35:49.176028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00177
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0527f81da85ed024
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_10` and `rank` of elliptic_curves `9768.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0527f81da85ed024 emitted 2026-05-18T17:35:49.176028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00178
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=76a9b9f1f952ff6e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `rank` of elliptic_curves `7914.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 76a9b9f1f952ff6e emitted 2026-05-18T17:35:49.177027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00179
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5f43f014f8e23a2c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_6` and `torsion` of elliptic_curves `4464.x1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5f43f014f8e23a2c emitted 2026-05-18T17:35:49.180027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00180
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ec5581ecb2ad296c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_2` and `tamagawa_product` of elliptic_curves `5544.q1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ec5581ecb2ad296c emitted 2026-05-18T17:35:49.180027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00181
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cb2fc6fd30a9b4e9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_5` and `rank` of elliptic_curves `528.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cb2fc6fd30a9b4e9 emitted 2026-05-18T17:35:49.181027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00182
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=09ed9fcde18f33f1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `tamagawa_product` of elliptic_curves `4719.k4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 09ed9fcde18f33f1 emitted 2026-05-18T17:35:49.181027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00183
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0c2444fb6a6db3a3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_3` and `torsion` of elliptic_curves `5187.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0c2444fb6a6db3a3 emitted 2026-05-18T17:35:49.183027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00184
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6ec247c87d79c86d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `tamagawa_product` of elliptic_curves `8528.h4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6ec247c87d79c86d emitted 2026-05-18T17:35:49.184027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00185
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5e61108e28cb71e6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `tamagawa_product` of elliptic_curves `8211.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5e61108e28cb71e6 emitted 2026-05-18T17:35:49.186028+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00186
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8210f27cc3ccf011
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_15` and `conductor` of elliptic_curves `9768.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8210f27cc3ccf011 emitted 2026-05-18T17:35:49.189027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00187
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0509c67cb8945115
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_16` and `tamagawa_product` of elliptic_curves `4170.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0509c67cb8945115 emitted 2026-05-18T17:35:49.192027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00188
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ba272b350d93994b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_15` and `torsion` of elliptic_curves `3042.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ba272b350d93994b emitted 2026-05-18T17:35:49.193027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00189
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7d632b006444b802
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_2` and `conductor` of elliptic_curves `3126.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d632b006444b802 emitted 2026-05-18T17:35:49.198027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00190
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8284fc2a55495d29
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_3` and `tamagawa_product` of elliptic_curves `9702.cc2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8284fc2a55495d29 emitted 2026-05-18T17:35:49.201027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00191
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e8afe96c0d0a031d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_14` and `tamagawa_product` of elliptic_curves `9162.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e8afe96c0d0a031d emitted 2026-05-18T17:35:49.205027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00192
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=31c5652f099ae02b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_5` and `torsion` of elliptic_curves `7350.ct7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 31c5652f099ae02b emitted 2026-05-18T17:35:49.207027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00193
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=602c8f20cc84e59b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_5` and `rank` of elliptic_curves `9350.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 602c8f20cc84e59b emitted 2026-05-18T17:35:49.210027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00194
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a89e55e0bd436df6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_1` and `conductor` of elliptic_curves `9990.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a89e55e0bd436df6 emitted 2026-05-18T17:35:49.212027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00195
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d4b3880315b287dd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_11` and `tamagawa_product` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d4b3880315b287dd emitted 2026-05-18T17:35:49.213027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00196
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=566915bef36a606b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_6` and `tamagawa_product` of elliptic_curves `7696.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 566915bef36a606b emitted 2026-05-18T17:35:49.213027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00197
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9b5f994c77ce33f6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_12` and `tamagawa_product` of elliptic_curves `9570.q1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9b5f994c77ce33f6 emitted 2026-05-18T17:35:49.214027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00198
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9fc3d71859ae675a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_124` and `conductor` of elliptic_curves `782.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9fc3d71859ae675a emitted 2026-05-18T17:35:49.215027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00199
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=874be6452859b0c3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_8` and `tamagawa_product` of elliptic_curves `6720.bg1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 874be6452859b0c3 emitted 2026-05-18T17:35:49.217027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00200
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3f1a07eaf3e6815a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_11` and `tamagawa_product` of elliptic_curves `2800.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f1a07eaf3e6815a emitted 2026-05-18T17:35:49.217027+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00201
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=157cdd657b27e17d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `conductor` of elliptic_curves `1984.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 157cdd657b27e17d emitted 2026-05-18T17:35:49.220084+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00202
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=27a196fe364918a7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_165` and `conductor` of elliptic_curves `7378.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 27a196fe364918a7 emitted 2026-05-18T17:35:49.222084+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00203
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=60969b0ea388228f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `3_1` and `rank` of elliptic_curves `7410.u3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 60969b0ea388228f emitted 2026-05-18T17:35:49.223084+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00204
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=389c836bdc723bed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_20` and `torsion` of elliptic_curves `1800.v2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 389c836bdc723bed emitted 2026-05-18T17:35:49.225084+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00205
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=59a4e6c034b14e83
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_2` and `torsion` of elliptic_curves `7696.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 59a4e6c034b14e83 emitted 2026-05-18T17:35:49.228085+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00206
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6f89fc739e052a1f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_3` and `rank` of elliptic_curves `9162.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6f89fc739e052a1f emitted 2026-05-18T17:35:49.229139+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00207
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e1b32717f948bbde
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_152` and `tamagawa_product` of elliptic_curves `9856.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e1b32717f948bbde emitted 2026-05-18T17:35:49.230139+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00208
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ef43dcc2785a46a6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_21` and `rank` of elliptic_curves `4430.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ef43dcc2785a46a6 emitted 2026-05-18T17:35:49.231139+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00209
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7d75ce40e2b6d308
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `rank` of elliptic_curves `8400.co3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d75ce40e2b6d308 emitted 2026-05-18T17:35:49.231139+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00210
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e6cfff980266ef51
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `tamagawa_product` of elliptic_curves `8838.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e6cfff980266ef51 emitted 2026-05-18T17:35:49.236139+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00211
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1ece5eba0280b598
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_7` and `conductor` of elliptic_curves `7344.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1ece5eba0280b598 emitted 2026-05-18T17:35:49.240193+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00212
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b12b3571566e8bed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `tamagawa_product` of elliptic_curves `2184.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b12b3571566e8bed emitted 2026-05-18T17:35:49.249234+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00213
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=eb4cf7e0a7d2276d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_124` and `torsion` of elliptic_curves `2680.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eb4cf7e0a7d2276d emitted 2026-05-18T17:35:49.251233+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00214
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c11e944609005797
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `tamagawa_product` of elliptic_curves `637.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c11e944609005797 emitted 2026-05-18T17:35:49.251233+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00215
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=818de71aa50857d0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `torsion` of elliptic_curves `8043.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 818de71aa50857d0 emitted 2026-05-18T17:35:49.254233+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00216
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7a9a5475f3a79f1a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `conductor` of elliptic_curves `3216.l2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7a9a5475f3a79f1a emitted 2026-05-18T17:35:49.257233+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00217
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5555ee0a7806aa85
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_4` and `rank` of elliptic_curves `2130.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5555ee0a7806aa85 emitted 2026-05-18T17:35:49.261276+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00218
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d0b57870d839c706
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_5` and `conductor` of elliptic_curves `3330.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d0b57870d839c706 emitted 2026-05-18T17:35:49.261276+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00219
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fdcbb8b95d7dcef6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `rank` of elliptic_curves `7520.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fdcbb8b95d7dcef6 emitted 2026-05-18T17:35:49.265276+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00220
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=51e33b27a6958d2b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `4_1` and `tamagawa_product` of elliptic_curves `7840.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 51e33b27a6958d2b emitted 2026-05-18T17:35:49.266280+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00221
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b646514ec9f71eb2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_3` and `conductor` of elliptic_curves `4800.cp2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b646514ec9f71eb2 emitted 2026-05-18T17:35:49.268280+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00222
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9b528c11d96d4942
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_6` and `rank` of elliptic_curves `2443.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9b528c11d96d4942 emitted 2026-05-18T17:35:49.270360+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00223
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=710f73a6eca9068b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `tamagawa_product` of elliptic_curves `1290.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 710f73a6eca9068b emitted 2026-05-18T17:35:49.274357+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00224
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2a7a14aed50e7483
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_9` and `torsion` of elliptic_curves `5880.bf2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a7a14aed50e7483 emitted 2026-05-18T17:35:49.276358+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00225
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=dda88ba72427dbeb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_10` and `tamagawa_product` of elliptic_curves `6650.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dda88ba72427dbeb emitted 2026-05-18T17:35:49.276358+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00226
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=392bc500b39229a4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_9` and `rank` of elliptic_curves `2988.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 392bc500b39229a4 emitted 2026-05-18T17:35:49.277357+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00227
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d9f6b409c8222346
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_8` and `rank` of elliptic_curves `5544.q1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d9f6b409c8222346 emitted 2026-05-18T17:35:49.278357+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00228
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a152e2380a706e78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `rank` of elliptic_curves `6306.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a152e2380a706e78 emitted 2026-05-18T17:35:49.279410+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00229
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e750813231ba65a1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_1` and `rank` of elliptic_curves `6336.bi1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e750813231ba65a1 emitted 2026-05-18T17:35:49.280409+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00230
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8ea329241e6ce0ab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_9` and `torsion` of elliptic_curves `862.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ea329241e6ce0ab emitted 2026-05-18T17:35:49.280409+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00231
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f83c136e7b954a3d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `conductor` of elliptic_curves `3248.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f83c136e7b954a3d emitted 2026-05-18T17:35:49.281410+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00232
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3beaa63b0c3ec9fe
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_2` and `torsion` of elliptic_curves `4935.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3beaa63b0c3ec9fe emitted 2026-05-18T17:35:49.281410+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00233
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cd66157eb8aa6de4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_14` and `torsion` of elliptic_curves `7952.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cd66157eb8aa6de4 emitted 2026-05-18T17:35:49.283409+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00234
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=69a9c422ec5e2838
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_14` and `conductor` of elliptic_curves `2192.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 69a9c422ec5e2838 emitted 2026-05-18T17:35:49.283409+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00235
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a51b109b890d4c14
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `5_2` and `rank` of elliptic_curves `8775.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a51b109b890d4c14 emitted 2026-05-18T17:35:49.285409+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00236
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=639b853f2584ec98
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_4` and `conductor` of elliptic_curves `5269.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 639b853f2584ec98 emitted 2026-05-18T17:35:49.285409+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00237
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a6892bee10cee02f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `tamagawa_product` of elliptic_curves `7366.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a6892bee10cee02f emitted 2026-05-18T17:35:49.286411+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00238
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7c3ac029d6ab7b2c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_152` and `rank` of elliptic_curves `9447.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7c3ac029d6ab7b2c emitted 2026-05-18T17:35:49.290452+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00239
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8ba2544f5cd24c60
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_9` and `rank` of elliptic_curves `5408.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ba2544f5cd24c60 emitted 2026-05-18T17:35:49.293452+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00240
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=78066fdc228da9ae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_124` and `conductor` of elliptic_curves `9633.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78066fdc228da9ae emitted 2026-05-18T17:35:49.293452+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00241
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b3f9bade44c4b302
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `rank` of elliptic_curves `3768.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b3f9bade44c4b302 emitted 2026-05-18T17:35:49.294451+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00242
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e46d806d26ae4055
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_2` and `conductor` of elliptic_curves `4800.bu2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e46d806d26ae4055 emitted 2026-05-18T17:35:49.294451+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00243
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=4a520a93c463d963
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `5_2` and `torsion` of elliptic_curves `9408.bb1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4a520a93c463d963 emitted 2026-05-18T17:35:49.298452+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00244
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=84af5e9c6f277119
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `conductor` of elliptic_curves `9702.bn2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 84af5e9c6f277119 emitted 2026-05-18T17:35:49.302493+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00245
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b1ea660552a7c04c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_4` and `conductor` of elliptic_curves `5040.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b1ea660552a7c04c emitted 2026-05-18T17:35:49.303493+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00246
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=815deecac67c4834
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `tamagawa_product` of elliptic_curves `8308.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 815deecac67c4834 emitted 2026-05-18T17:35:49.306493+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00247
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=71c334ce54b92760
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `conductor` of elliptic_curves `2352.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 71c334ce54b92760 emitted 2026-05-18T17:35:49.308492+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00248
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7bed293ecdd9a8f5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_1` and `tamagawa_product` of elliptic_curves `4107.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7bed293ecdd9a8f5 emitted 2026-05-18T17:35:49.312532+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00249
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fe5273d2f2be38f5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_2` and `conductor` of elliptic_curves `7881.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fe5273d2f2be38f5 emitted 2026-05-18T17:35:49.315532+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00250
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ace71de67dee99e7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_1` and `rank` of elliptic_curves `466.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ace71de67dee99e7 emitted 2026-05-18T17:35:49.319600+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00251
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=028fc2d0cea77171
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_1` and `conductor` of elliptic_curves `2213.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 028fc2d0cea77171 emitted 2026-05-18T17:35:49.322600+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00252
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=147dc89dcea5da87
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_1` and `torsion` of elliptic_curves `1968.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 147dc89dcea5da87 emitted 2026-05-18T17:35:49.326599+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00253
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6c178ddac5dfa5ae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_6` and `conductor` of elliptic_curves `8330.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6c178ddac5dfa5ae emitted 2026-05-18T17:35:49.331648+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00254
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1628d1e4b34163f1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_11` and `tamagawa_product` of elliptic_curves `6992.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1628d1e4b34163f1 emitted 2026-05-18T17:35:49.332648+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00255
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e9a2a4347a362eb5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_3` and `rank` of elliptic_curves `8710.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e9a2a4347a362eb5 emitted 2026-05-18T17:35:49.333648+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00256
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c1cb36e11c043130
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `conductor` of elliptic_curves `6402.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c1cb36e11c043130 emitted 2026-05-18T17:35:49.334648+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00257
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=260d258c889df109
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `torsion` of elliptic_curves `5304.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 260d258c889df109 emitted 2026-05-18T17:35:49.336648+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00258
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c60073e18bfd9574
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_3` and `rank` of elliptic_curves `4950.w2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c60073e18bfd9574 emitted 2026-05-18T17:35:49.336648+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00259
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=34b054d71a514359
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_1` and `conductor` of elliptic_curves `90.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 34b054d71a514359 emitted 2026-05-18T17:35:49.338649+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00260
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2c69081613bba952
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_12` and `torsion` of elliptic_curves `5088.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2c69081613bba952 emitted 2026-05-18T17:35:49.340888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00261
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=193517cf3c673673
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_8` and `conductor` of elliptic_curves `5190.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 193517cf3c673673 emitted 2026-05-18T17:35:49.343888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00262
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=930632ef2010a9a9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `5_2` and `rank` of elliptic_curves `7718.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 930632ef2010a9a9 emitted 2026-05-18T17:35:49.344888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00263
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f5e0030401cd1af7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `tamagawa_product` of elliptic_curves `6867.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f5e0030401cd1af7 emitted 2026-05-18T17:35:49.346888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00264
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8a4e340cf6079ec0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_6` and `conductor` of elliptic_curves `7380.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8a4e340cf6079ec0 emitted 2026-05-18T17:35:49.346888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00265
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=287ed48970fadcd0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_1` and `tamagawa_product` of elliptic_curves `1288.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 287ed48970fadcd0 emitted 2026-05-18T17:35:49.347887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00266
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1691066247e01097
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `conductor` of elliptic_curves `2420.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1691066247e01097 emitted 2026-05-18T17:35:49.349888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00267
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e3567f7c368bb0a7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_4` and `tamagawa_product` of elliptic_curves `6370.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e3567f7c368bb0a7 emitted 2026-05-18T17:35:49.351888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00268
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2a6a933d93adb5a3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_4` and `torsion` of elliptic_curves `9768.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a6a933d93adb5a3 emitted 2026-05-18T17:35:49.352887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00269
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=21339b11f0cf8103
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_12` and `rank` of elliptic_curves `8510.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 21339b11f0cf8103 emitted 2026-05-18T17:35:49.354887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00270
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ad94709fe358b4fc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `tamagawa_product` of elliptic_curves `45.a8`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad94709fe358b4fc emitted 2026-05-18T17:35:49.354887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00271
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=04cf799741c5f844
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_3` and `tamagawa_product` of elliptic_curves `9225.u1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 04cf799741c5f844 emitted 2026-05-18T17:35:49.356888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00272
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=06eb80410ab5f4d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `torsion` of elliptic_curves `7350.f4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 06eb80410ab5f4d1 emitted 2026-05-18T17:35:49.357887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00273
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=440972f415b865fa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `3_1` and `conductor` of elliptic_curves `8043.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 440972f415b865fa emitted 2026-05-18T17:35:49.361888+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00274
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a2ee5d58ce7df9d2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_6` and `torsion` of elliptic_curves `7030.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a2ee5d58ce7df9d2 emitted 2026-05-18T17:35:49.362887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00275
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b37446fcdf1fda9c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `rank` of elliptic_curves `2988.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b37446fcdf1fda9c emitted 2026-05-18T17:35:49.363887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00276
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3dfd44e0df5902f1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `rank` of elliptic_curves `5400.bv1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3dfd44e0df5902f1 emitted 2026-05-18T17:35:49.368887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00277
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=da4612b64ae7b405
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_1` and `rank` of elliptic_curves `7770.g2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da4612b64ae7b405 emitted 2026-05-18T17:35:49.371889+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00278
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8888587e741b5e24
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_2` and `rank` of elliptic_curves `5418.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8888587e741b5e24 emitted 2026-05-18T17:35:49.371889+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00279
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=051769407dc538ef
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_2` and `torsion` of elliptic_curves `1216.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 051769407dc538ef emitted 2026-05-18T17:35:49.373887+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00280
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a63bcea3148c0385
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_1` and `torsion` of elliptic_curves `8672.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a63bcea3148c0385 emitted 2026-05-18T17:35:49.379393+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00281
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bb15630d9269f25e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_6` and `torsion` of elliptic_curves `1320.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bb15630d9269f25e emitted 2026-05-18T17:35:49.384393+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00282
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5dea9b7460faf326
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_1` and `torsion` of elliptic_curves `4098.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5dea9b7460faf326 emitted 2026-05-18T17:35:49.384393+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00283
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=eaa0b121d7ac308c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `torsion` of elliptic_curves `4830.bk1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eaa0b121d7ac308c emitted 2026-05-18T17:35:49.384393+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00284
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a96cb683087a4db4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_9` and `tamagawa_product` of elliptic_curves `5450.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a96cb683087a4db4 emitted 2026-05-18T17:35:49.387393+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00285
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2265a7be4dfb3c7d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_10` and `rank` of elliptic_curves `2850.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2265a7be4dfb3c7d emitted 2026-05-18T17:35:49.387393+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00286
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=473e7f25b1f23505
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_1` and `rank` of elliptic_curves `7920.be2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 473e7f25b1f23505 emitted 2026-05-18T17:35:49.390457+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00287
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b8f0bdf0910732a4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_6` and `rank` of elliptic_curves `2100.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b8f0bdf0910732a4 emitted 2026-05-18T17:35:49.391457+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00288
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ca7f25b9e846a2f2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_2` and `rank` of elliptic_curves `9350.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ca7f25b9e846a2f2 emitted 2026-05-18T17:35:49.391457+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00289
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b0944fda54e45669
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_14` and `tamagawa_product` of elliptic_curves `1113.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b0944fda54e45669 emitted 2026-05-18T17:35:49.393456+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00290
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2c760f18fa1dd3ee
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `conductor` of elliptic_curves `2724.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2c760f18fa1dd3ee emitted 2026-05-18T17:35:49.396456+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00291
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=29fd6fb774b98175
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `rank` of elliptic_curves `2574.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 29fd6fb774b98175 emitted 2026-05-18T17:35:49.400502+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00292
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=caf165d20066f7f6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_1` and `tamagawa_product` of elliptic_curves `336.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record caf165d20066f7f6 emitted 2026-05-18T17:35:49.403501+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00293
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1f61309b7e31e7e7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_1` and `torsion` of elliptic_curves `8550.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1f61309b7e31e7e7 emitted 2026-05-18T17:35:49.407502+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00294
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=578eedd18616ec18
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_6` and `torsion` of elliptic_curves `4006.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 578eedd18616ec18 emitted 2026-05-18T17:35:49.410551+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00295
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5dc101d3d1022b6b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `rank` of elliptic_curves `2808.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5dc101d3d1022b6b emitted 2026-05-18T17:35:49.413547+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00296
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5935d40d992d0d08
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_8` and `torsion` of elliptic_curves `9225.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5935d40d992d0d08 emitted 2026-05-18T17:35:49.414547+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00297
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=92c41ad293119707
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_18` and `tamagawa_product` of elliptic_curves `2730.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 92c41ad293119707 emitted 2026-05-18T17:35:49.416547+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00298
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9b33614371e7965f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_16` and `tamagawa_product` of elliptic_curves `6984.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9b33614371e7965f emitted 2026-05-18T17:35:49.418547+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00299
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=308fcda303baf165
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_13` and `rank` of elliptic_curves `1600.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 308fcda303baf165 emitted 2026-05-18T17:35:49.419606+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00300
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=11e01bdd69638460
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_3` and `tamagawa_product` of elliptic_curves `3648.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 11e01bdd69638460 emitted 2026-05-18T17:35:49.421607+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00301
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=eb8ddd2032ff118d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_8` and `conductor` of elliptic_curves `372.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eb8ddd2032ff118d emitted 2026-05-18T17:35:49.425607+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00302
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c8b29e3c7043237b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_6` and `tamagawa_product` of elliptic_curves `9240.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c8b29e3c7043237b emitted 2026-05-18T17:35:49.427606+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00303
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=36f266d07c2063b5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `conductor` of elliptic_curves `2730.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 36f266d07c2063b5 emitted 2026-05-18T17:35:49.429664+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00304
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=53f9788581fbb717
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_4` and `conductor` of elliptic_curves `8106.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 53f9788581fbb717 emitted 2026-05-18T17:35:49.431666+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00305
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8169ed17ce1f836f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_1` and `torsion` of elliptic_curves `7920.be2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8169ed17ce1f836f emitted 2026-05-18T17:35:49.432665+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00306
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0f83554da30fdf53
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_3` and `rank` of elliptic_curves `7832.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0f83554da30fdf53 emitted 2026-05-18T17:35:49.432665+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00307
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f79d5e49f7c0e037
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `torsion` of elliptic_curves `4800.bu2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f79d5e49f7c0e037 emitted 2026-05-18T17:35:49.438666+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00308
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d493afa569c75af1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_3` and `rank` of elliptic_curves `9865.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d493afa569c75af1 emitted 2026-05-18T17:35:49.439717+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00309
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ffacb7e5b81b90e5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_124` and `rank` of elliptic_curves `9510.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ffacb7e5b81b90e5 emitted 2026-05-18T17:35:49.442716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00310
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c9005e482bf95413
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `rank` of elliptic_curves `890.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c9005e482bf95413 emitted 2026-05-18T17:35:49.448716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00311
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7c75711456bebef4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `rank` of elliptic_curves `6008.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7c75711456bebef4 emitted 2026-05-18T17:35:49.451717+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00312
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=660a15ae86ecae78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `tamagawa_product` of elliptic_curves `9350.bi1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 660a15ae86ecae78 emitted 2026-05-18T17:35:49.452716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00313
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b8b8b28918f8fe26
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `conductor` of elliptic_curves `7540.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b8b8b28918f8fe26 emitted 2026-05-18T17:35:49.454716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00314
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6de2bc2dc5968d33
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_6` and `conductor` of elliptic_curves `4768.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6de2bc2dc5968d33 emitted 2026-05-18T17:35:49.460716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00315
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d281851f8668791a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_7` and `rank` of elliptic_curves `2352.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d281851f8668791a emitted 2026-05-18T17:35:49.461716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00316
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=27ccd9fdec3ae921
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_20` and `tamagawa_product` of elliptic_curves `830.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 27ccd9fdec3ae921 emitted 2026-05-18T17:35:49.462716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00317
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=17d8cda676656b55
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `torsion` of elliptic_curves `2130.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 17d8cda676656b55 emitted 2026-05-18T17:35:49.465716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00318
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8aa1781b65217494
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `3_1` and `torsion` of elliptic_curves `345.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8aa1781b65217494 emitted 2026-05-18T17:35:49.466716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00319
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=968175381b009e4c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_15` and `tamagawa_product` of elliptic_curves `2070.b5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 968175381b009e4c emitted 2026-05-18T17:35:49.467716+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00320
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3607a5e2f3ecf4d2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_152` and `tamagawa_product` of elliptic_curves `1288.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3607a5e2f3ecf4d2 emitted 2026-05-18T17:35:49.470765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00321
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b0a44bd617b19db1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_3` and `torsion` of elliptic_curves `5922.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b0a44bd617b19db1 emitted 2026-05-18T17:35:49.476765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00322
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6da9790f4a59bc47
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `rank` of elliptic_curves `8946.h4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6da9790f4a59bc47 emitted 2026-05-18T17:35:49.479765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00323
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a1a3ef33c9cb35b3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_7` and `tamagawa_product` of elliptic_curves `9912.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a1a3ef33c9cb35b3 emitted 2026-05-18T17:35:49.483765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00324
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fb0d0ae89e5a53c8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_2` and `conductor` of elliptic_curves `646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fb0d0ae89e5a53c8 emitted 2026-05-18T17:35:49.485765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00325
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ad99d44bc0ca1f6c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_3` and `conductor` of elliptic_curves `2840.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad99d44bc0ca1f6c emitted 2026-05-18T17:35:49.485765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00326
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=49bcfc5e031e7fb4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_1` and `conductor` of elliptic_curves `2394.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 49bcfc5e031e7fb4 emitted 2026-05-18T17:35:49.487765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00327
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=81a34dfecc7034da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_6` and `torsion` of elliptic_curves `507.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 81a34dfecc7034da emitted 2026-05-18T17:35:49.490765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00328
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=762046ac7cf4d857
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_12` and `conductor` of elliptic_curves `2970.y1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 762046ac7cf4d857 emitted 2026-05-18T17:35:49.491765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00329
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=80bb8dc33cec1e29
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `tamagawa_product` of elliptic_curves `3840.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 80bb8dc33cec1e29 emitted 2026-05-18T17:35:49.491765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00330
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=846393299f325e8c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `rank` of elliptic_curves `693.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 846393299f325e8c emitted 2026-05-18T17:35:49.494765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00331
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7cf94b327afd8bfc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_3` and `tamagawa_product` of elliptic_curves `7245.n3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7cf94b327afd8bfc emitted 2026-05-18T17:35:49.496765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00332
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3a041c3a1ff7433f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_21` and `tamagawa_product` of elliptic_curves `9152.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a041c3a1ff7433f emitted 2026-05-18T17:35:49.497765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00333
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=482306a2885ab6df
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_18` and `rank` of elliptic_curves `2758.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 482306a2885ab6df emitted 2026-05-18T17:35:49.498765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00334
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9f9b6a91602ba294
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_1` and `rank` of elliptic_curves `4806.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9f9b6a91602ba294 emitted 2026-05-18T17:35:49.500765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00335
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d3b2de3c4a94d1e9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_6` and `tamagawa_product` of elliptic_curves `5880.bf2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d3b2de3c4a94d1e9 emitted 2026-05-18T17:35:49.501765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00336
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6bee14b3a354d9f3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `8_19` and `torsion` of elliptic_curves `6026.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6bee14b3a354d9f3 emitted 2026-05-18T17:35:49.503765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00337
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8d5b8a0bf12d0b0b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_145` and `torsion` of elliptic_curves `8541.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8d5b8a0bf12d0b0b emitted 2026-05-18T17:35:49.504765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00338
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=574fd9cce67cb260
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_3` and `conductor` of elliptic_curves `3330.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 574fd9cce67cb260 emitted 2026-05-18T17:35:49.505765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00339
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ac5edc99c016974e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_124` and `torsion` of elliptic_curves `1970.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac5edc99c016974e emitted 2026-05-18T17:35:49.511765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00340
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=00c09ac2e07a5a6f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_3` and `tamagawa_product` of elliptic_curves `4264.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 00c09ac2e07a5a6f emitted 2026-05-18T17:35:49.516765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00341
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=91a2c59823709234
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_15` and `rank` of elliptic_curves `6768.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 91a2c59823709234 emitted 2026-05-18T17:35:49.522765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00342
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=120492017bfa697d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `4_1` and `conductor` of elliptic_curves `4800.cq4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 120492017bfa697d emitted 2026-05-18T17:35:49.522765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00343
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c5cf78936f738a32
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_6` and `conductor` of elliptic_curves `5985.j5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c5cf78936f738a32 emitted 2026-05-18T17:35:49.523765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00344
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2d8b26407b78b5ea
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_4` and `rank` of elliptic_curves `1339.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2d8b26407b78b5ea emitted 2026-05-18T17:35:49.524765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00345
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=71c4f716b3db1d7b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_165` and `conductor` of elliptic_curves `7035.l3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 71c4f716b3db1d7b emitted 2026-05-18T17:35:49.525765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00346
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=685ed5a3a1fdcc2f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_145` and `rank` of elliptic_curves `4161.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 685ed5a3a1fdcc2f emitted 2026-05-18T17:35:49.527765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00347
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1a4f87e9e570229b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `4_1` and `tamagawa_product` of elliptic_curves `3891.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1a4f87e9e570229b emitted 2026-05-18T17:35:49.530764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00348
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d91aec963774623a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_19` and `tamagawa_product` of elliptic_curves `7460.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d91aec963774623a emitted 2026-05-18T17:35:49.530764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00349
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=56134840d8e2bd54
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_11` and `rank` of elliptic_curves `102.c3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 56134840d8e2bd54 emitted 2026-05-18T17:35:49.532764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00350
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c2e1872a319ea2ea
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_17` and `conductor` of elliptic_curves `944.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c2e1872a319ea2ea emitted 2026-05-18T17:35:49.533765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00351
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fbf001cc495f4d3b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_1` and `conductor` of elliptic_curves `9070.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fbf001cc495f4d3b emitted 2026-05-18T17:35:49.538764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00352
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fc9d751584e08012
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `torsion` of elliptic_curves `3360.q3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fc9d751584e08012 emitted 2026-05-18T17:35:49.539765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00353
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=4fa193c47234f02b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_9` and `conductor` of elliptic_curves `7230.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4fa193c47234f02b emitted 2026-05-18T17:35:49.542764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00354
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d96a0736d5d94e71
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_152` and `conductor` of elliptic_curves `2376.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d96a0736d5d94e71 emitted 2026-05-18T17:35:49.544764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00355
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=03c6d30c768b5110
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_12` and `conductor` of elliptic_curves `5808.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 03c6d30c768b5110 emitted 2026-05-18T17:35:49.545765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00356
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9571ca0f22a974b4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_9` and `tamagawa_product` of elliptic_curves `2800.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9571ca0f22a974b4 emitted 2026-05-18T17:35:49.549765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00357
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=729ecc62867d5d18
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_7` and `rank` of elliptic_curves `1680.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 729ecc62867d5d18 emitted 2026-05-18T17:35:49.550764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00358
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d1f4b1064d4956c3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `rank` of elliptic_curves `8400.co3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d1f4b1064d4956c3 emitted 2026-05-18T17:35:49.552764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00359
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=129d5b63c1a05c13
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `conductor` of elliptic_curves `1216.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 129d5b63c1a05c13 emitted 2026-05-18T17:35:49.552764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00360
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=dc7556f9b26e4c66
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `conductor` of elliptic_curves `890.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dc7556f9b26e4c66 emitted 2026-05-18T17:35:49.555764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00361
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3468abef7ffa816e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_10` and `rank` of elliptic_curves `2970.y1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3468abef7ffa816e emitted 2026-05-18T17:35:49.557764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00362
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ca793c7958318256
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `torsion` of elliptic_curves `1098.k4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ca793c7958318256 emitted 2026-05-18T17:35:49.557764+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00363
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=34fd4424b64ba844
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_18` and `torsion` of elliptic_curves `3328.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 34fd4424b64ba844 emitted 2026-05-18T17:35:49.558765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00364
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=121c3f2555f76b98
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_20` and `conductor` of elliptic_curves `2790.ba3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 121c3f2555f76b98 emitted 2026-05-18T17:35:49.559817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00365
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=637c9064f51887ca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_3` and `conductor` of elliptic_curves `6400.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 637c9064f51887ca emitted 2026-05-18T17:35:49.559817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00366
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=494eb49aeaa80839
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_7` and `rank` of elliptic_curves `3933.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 494eb49aeaa80839 emitted 2026-05-18T17:35:49.559817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00367
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=711f25756e880b4f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `rank` of elliptic_curves `8490.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 711f25756e880b4f emitted 2026-05-18T17:35:49.560816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00368
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=94123de010da6f78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_21` and `conductor` of elliptic_curves `2358.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 94123de010da6f78 emitted 2026-05-18T17:35:49.563817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00369
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=dfc06c8b2371d78a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `torsion` of elliptic_curves `8190.i4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dfc06c8b2371d78a emitted 2026-05-18T17:35:49.564817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00370
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3e7d2e30f77b0f80
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_6` and `torsion` of elliptic_curves `5304.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3e7d2e30f77b0f80 emitted 2026-05-18T17:35:49.566816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00371
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1780b08b1c01fcd4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_9` and `conductor` of elliptic_curves `6571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1780b08b1c01fcd4 emitted 2026-05-18T17:35:49.566816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00372
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5f0c194c9b52d2ca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_11` and `tamagawa_product` of elliptic_curves `2420.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5f0c194c9b52d2ca emitted 2026-05-18T17:35:49.567816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00373
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3ced4e9ca5c47d1b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_152` and `torsion` of elliptic_curves `4410.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3ced4e9ca5c47d1b emitted 2026-05-18T17:35:49.567816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00374
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=21db30afbc0da363
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_5` and `tamagawa_product` of elliptic_curves `4935.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 21db30afbc0da363 emitted 2026-05-18T17:35:49.573817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00375
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c44c15bc160cb304
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_10` and `torsion` of elliptic_curves `6525.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c44c15bc160cb304 emitted 2026-05-18T17:35:49.575816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00376
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ac402b01fca6d9df
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_3` and `torsion` of elliptic_curves `5304.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac402b01fca6d9df emitted 2026-05-18T17:35:49.579817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00377
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=932e2d94beb79612
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_3` and `torsion` of elliptic_curves `5800.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 932e2d94beb79612 emitted 2026-05-18T17:35:49.580817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00378
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=710d61d4123f98aa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_7` and `tamagawa_product` of elliptic_curves `4195.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 710d61d4123f98aa emitted 2026-05-18T17:35:49.582817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00379
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=09cb46022789d486
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_1` and `tamagawa_product` of elliptic_curves `4800.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 09cb46022789d486 emitted 2026-05-18T17:35:49.584816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00380
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d6742b52ba6253c4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_7` and `conductor` of elliptic_curves `9225.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d6742b52ba6253c4 emitted 2026-05-18T17:35:49.585816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00381
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=edc071bc6027ef88
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_1` and `torsion` of elliptic_curves `4485.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record edc071bc6027ef88 emitted 2026-05-18T17:35:49.589817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00382
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6e30112f9186af3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `3_1` and `tamagawa_product` of elliptic_curves `5808.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6e30112f9186af3e emitted 2026-05-18T17:35:49.591816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00383
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=de81416133901fa4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_16` and `torsion` of elliptic_curves `2646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record de81416133901fa4 emitted 2026-05-18T17:35:49.595816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00384
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d754db0f0f9e0082
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `conductor` of elliptic_curves `1254.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d754db0f0f9e0082 emitted 2026-05-18T17:35:49.595816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00385
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e77b86491e7f7625
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_124` and `rank` of elliptic_curves `693.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e77b86491e7f7625 emitted 2026-05-18T17:35:49.596816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00386
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7b3a5a148baa05bf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_13` and `rank` of elliptic_curves `2448.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b3a5a148baa05bf emitted 2026-05-18T17:35:49.596816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00387
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=43d97a7e478723d5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `4_1` and `rank` of elliptic_curves `1590.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 43d97a7e478723d5 emitted 2026-05-18T17:35:49.597816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00388
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5a9696081fb7752d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_124` and `conductor` of elliptic_curves `6550.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5a9696081fb7752d emitted 2026-05-18T17:35:49.601816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00389
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8835f03e9af94781
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_1` and `tamagawa_product` of elliptic_curves `1446.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8835f03e9af94781 emitted 2026-05-18T17:35:49.603816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00390
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=719031fe1d320512
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_10` and `torsion` of elliptic_curves `4160.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 719031fe1d320512 emitted 2026-05-18T17:35:49.603816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00391
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d0ec2955b7488623
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_4` and `tamagawa_product` of elliptic_curves `5538.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d0ec2955b7488623 emitted 2026-05-18T17:35:49.603816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00392
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2a0a6d7c0cf5d67b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_9` and `conductor` of elliptic_curves `3042.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a0a6d7c0cf5d67b emitted 2026-05-18T17:35:49.604816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00393
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=30332bacdccdfce2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_15` and `conductor` of elliptic_curves `1216.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 30332bacdccdfce2 emitted 2026-05-18T17:35:49.604816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00394
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bb301b23a1ba3283
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_165` and `conductor` of elliptic_curves `4598.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bb301b23a1ba3283 emitted 2026-05-18T17:35:49.606816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00395
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a8df8e2471d8802b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `torsion` of elliptic_curves `1815.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8df8e2471d8802b emitted 2026-05-18T17:35:49.607816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00396
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c9d02e9ee85e32a8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_10` and `rank` of elliptic_curves `3200.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c9d02e9ee85e32a8 emitted 2026-05-18T17:35:49.608816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00397
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=10953974658bfc3a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_19` and `torsion` of elliptic_curves `2310.v4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 10953974658bfc3a emitted 2026-05-18T17:35:49.616817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00398
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=8111bb85d2a93aab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_7` and `rank` of elliptic_curves `1800.m4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8111bb85d2a93aab emitted 2026-05-18T17:35:49.616817+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00399
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=666b0ca7ad66384f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_8` and `tamagawa_product` of elliptic_curves `8730.k2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 666b0ca7ad66384f emitted 2026-05-18T17:35:49.620816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00400
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7122f4cc9c724ba7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_14` and `torsion` of elliptic_curves `9600.bf1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7122f4cc9c724ba7 emitted 2026-05-18T17:35:49.621815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00401
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5315f40d35e8f725
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_6` and `tamagawa_product` of elliptic_curves `4752.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5315f40d35e8f725 emitted 2026-05-18T17:35:49.623816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00402
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=226408a0300ea157
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_3` and `tamagawa_product` of elliptic_curves `8496.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 226408a0300ea157 emitted 2026-05-18T17:35:49.624815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00403
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3a2c909661824f7c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_2` and `tamagawa_product` of elliptic_curves `882.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a2c909661824f7c emitted 2026-05-18T17:35:49.626815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00404
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d1dd785b361b73ff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_3` and `conductor` of elliptic_curves `4560.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d1dd785b361b73ff emitted 2026-05-18T17:35:49.627815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00405
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cf75c19bf8759536
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_17` and `tamagawa_product` of elliptic_curves `5950.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cf75c19bf8759536 emitted 2026-05-18T17:35:49.628815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00406
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=522caea081921577
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_139` and `tamagawa_product` of elliptic_curves `3330.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 522caea081921577 emitted 2026-05-18T17:35:49.629816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00407
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ae59223863e3688e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `conductor` of elliptic_curves `2898.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ae59223863e3688e emitted 2026-05-18T17:35:49.633815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00408
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7ab634107b57f111
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_2` and `rank` of elliptic_curves `4480.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7ab634107b57f111 emitted 2026-05-18T17:35:49.635815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00409
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9513059785f9afd5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `conductor` of elliptic_curves `7770.g2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9513059785f9afd5 emitted 2026-05-18T17:35:49.635815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00410
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=0ff9f51b337f8289
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `5_2` and `rank` of elliptic_curves `1446.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0ff9f51b337f8289 emitted 2026-05-18T17:35:49.636821+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00411
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c76a06612c953659
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_6` and `torsion` of elliptic_curves `2680.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c76a06612c953659 emitted 2026-05-18T17:35:49.637816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00412
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1174b5393a2416ce
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_2` and `tamagawa_product` of elliptic_curves `7308.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1174b5393a2416ce emitted 2026-05-18T17:35:49.640815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00413
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=9903851f95d125b9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_19` and `tamagawa_product` of elliptic_curves `1785.a3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9903851f95d125b9 emitted 2026-05-18T17:35:49.640815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00414
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a631d7a16f0456da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_165` and `tamagawa_product` of elliptic_curves `7565.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a631d7a16f0456da emitted 2026-05-18T17:35:49.645815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00415
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=78e98ccf2701055a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `torsion` of elliptic_curves `7245.n3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78e98ccf2701055a emitted 2026-05-18T17:35:49.645815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00416
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=af416cdf24470a51
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_20` and `tamagawa_product` of elliptic_curves `3126.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record af416cdf24470a51 emitted 2026-05-18T17:35:49.650815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00417
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=2e48640ed9d2fd93
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_6` and `rank` of elliptic_curves `9633.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2e48640ed9d2fd93 emitted 2026-05-18T17:35:49.655816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00418
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=deace9fd30c8aee4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_2` and `torsion` of elliptic_curves `7840.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record deace9fd30c8aee4 emitted 2026-05-18T17:35:49.656816+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00419
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ecc76004018a1e6b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_165` and `rank` of elliptic_curves `9450.dy1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ecc76004018a1e6b emitted 2026-05-18T17:35:49.657815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00420
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b23eb05be21c9fac
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `conductor` of elliptic_curves `4800.d5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b23eb05be21c9fac emitted 2026-05-18T17:35:49.658815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00421
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cd99492ee23deaea
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `conductor` of elliptic_curves `1806.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cd99492ee23deaea emitted 2026-05-18T17:35:49.661815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00422
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=90b4cc4c759c0254
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_8` and `tamagawa_product` of elliptic_curves `6064.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 90b4cc4c759c0254 emitted 2026-05-18T17:35:49.661815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00423
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cb9cd8dd5aad5826
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_9` and `rank` of elliptic_curves `7623.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cb9cd8dd5aad5826 emitted 2026-05-18T17:35:49.662815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00424
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=78b1b05150c98c4d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_1` and `tamagawa_product` of elliptic_curves `2808.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78b1b05150c98c4d emitted 2026-05-18T17:35:49.666815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00425
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bde8e14102e620f9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_124` and `conductor` of elliptic_curves `8605.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bde8e14102e620f9 emitted 2026-05-18T17:35:49.667815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00426
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c6c4e0dff1070bbf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_3` and `conductor` of elliptic_curves `6585.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c6c4e0dff1070bbf emitted 2026-05-18T17:35:49.671814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00427
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=547d983ff7e854f3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_3` and `torsion` of elliptic_curves `5304.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 547d983ff7e854f3 emitted 2026-05-18T17:35:49.672815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00428
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6cf0b350791b2cce
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `conductor` of elliptic_curves `2420.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6cf0b350791b2cce emitted 2026-05-18T17:35:49.672815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00429
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=78c41b2b23d0f886
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_3` and `rank` of elliptic_curves `1325.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78c41b2b23d0f886 emitted 2026-05-18T17:35:49.672815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00430
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=08ae83b2f4c1ce9d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_5` and `conductor` of elliptic_curves `2112.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 08ae83b2f4c1ce9d emitted 2026-05-18T17:35:49.677815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00431
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c9e473cb7289e61d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_7` and `tamagawa_product` of elliptic_curves `5187.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c9e473cb7289e61d emitted 2026-05-18T17:35:49.679815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00432
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=23e2553c8ec48f77
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_152` and `tamagawa_product` of elliptic_curves `6894.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 23e2553c8ec48f77 emitted 2026-05-18T17:35:49.680815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00433
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=39470c994eadb916
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_152` and `torsion` of elliptic_curves `3472.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 39470c994eadb916 emitted 2026-05-18T17:35:49.685815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00434
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=85086fb7493e2625
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `torsion` of elliptic_curves `1734.j4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 85086fb7493e2625 emitted 2026-05-18T17:35:49.692814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00435
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=52296bd8d0370009
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `conductor` of elliptic_curves `1296.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 52296bd8d0370009 emitted 2026-05-18T17:35:49.694814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00436
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=41f5f04010dcea5b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_5` and `torsion` of elliptic_curves `2378.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 41f5f04010dcea5b emitted 2026-05-18T17:35:49.697815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00437
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=6d187d3ac320df49
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_9` and `torsion` of elliptic_curves `1324.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6d187d3ac320df49 emitted 2026-05-18T17:35:49.702814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00438
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bbf4db28871e14ed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `tamagawa_product` of elliptic_curves `3891.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bbf4db28871e14ed emitted 2026-05-18T17:35:49.704814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00439
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=744e97b2338266c1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_4` and `tamagawa_product` of elliptic_curves `1960.n2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 744e97b2338266c1 emitted 2026-05-18T17:35:49.710814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00440
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=217db88db62d49bc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `4_1` and `tamagawa_product` of elliptic_curves `158.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 217db88db62d49bc emitted 2026-05-18T17:35:49.711815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00441
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=15e61a7ef2c05fbf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_6` and `conductor` of elliptic_curves `8490.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 15e61a7ef2c05fbf emitted 2026-05-18T17:35:49.711815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00442
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a8648dd2fa8320a3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `rank` of elliptic_curves `7320.q4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8648dd2fa8320a3 emitted 2026-05-18T17:35:49.712814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00443
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a77b2b097b2f4482
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_11` and `tamagawa_product` of elliptic_curves `960.c6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a77b2b097b2f4482 emitted 2026-05-18T17:35:49.713815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00444
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e7cc74f08d9b170f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_7` and `rank` of elliptic_curves `4032.w5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e7cc74f08d9b170f emitted 2026-05-18T17:35:49.714814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00445
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=002fd74b7a8d9818
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_3` and `rank` of elliptic_curves `2160.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 002fd74b7a8d9818 emitted 2026-05-18T17:35:49.716814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00446
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=915edbea55abfe7f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_7` and `tamagawa_product` of elliptic_curves `459.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 915edbea55abfe7f emitted 2026-05-18T17:35:49.716814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00447
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7587c4bf66f0d623
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `3_1` and `tamagawa_product` of elliptic_curves `2730.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7587c4bf66f0d623 emitted 2026-05-18T17:35:49.722815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00448
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=872081839aa73489
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_14` and `tamagawa_product` of elliptic_curves `9570.q1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 872081839aa73489 emitted 2026-05-18T17:35:49.724814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00449
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7b8fac3e57f6de62
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_4` and `conductor` of elliptic_curves `6105.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b8fac3e57f6de62 emitted 2026-05-18T17:35:49.724814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00450
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=919e1b59e460d631
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_17` and `conductor` of elliptic_curves `4170.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 919e1b59e460d631 emitted 2026-05-18T17:35:49.725814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00451
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=d3f6e6add4a24e97
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_2` and `tamagawa_product` of elliptic_curves `4160.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d3f6e6add4a24e97 emitted 2026-05-18T17:35:49.727814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00452
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=882d0e3eb0e5a935
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `4_1` and `rank` of elliptic_curves `7770.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 882d0e3eb0e5a935 emitted 2026-05-18T17:35:49.729815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00453
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=11f4de20e0fa9830
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `conductor` of elliptic_curves `5040.o2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 11f4de20e0fa9830 emitted 2026-05-18T17:35:49.732814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00454
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7890bf4466387bc0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `torsion` of elliptic_curves `2730.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7890bf4466387bc0 emitted 2026-05-18T17:35:49.733815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00455
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=afa5bf3e1b91a3ad
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_8` and `torsion` of elliptic_curves `3768.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record afa5bf3e1b91a3ad emitted 2026-05-18T17:35:49.738814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00456
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=3b00aed615ea6a02
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `3_1` and `rank` of elliptic_curves `6026.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3b00aed615ea6a02 emitted 2026-05-18T17:35:49.738814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00457
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ffb1352639a36505
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `rank` of elliptic_curves `6402.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ffb1352639a36505 emitted 2026-05-18T17:35:49.739814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00458
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ccb035032b8e4c3d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_15` and `conductor` of elliptic_curves `9210.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ccb035032b8e4c3d emitted 2026-05-18T17:35:49.739814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00459
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=854641940f33ccc1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_3` and `rank` of elliptic_curves `8262.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 854641940f33ccc1 emitted 2026-05-18T17:35:49.741814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00460
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bfe1b7f557953daa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_1` and `conductor` of elliptic_curves `2160.p2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bfe1b7f557953daa emitted 2026-05-18T17:35:49.741814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00461
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c57f952fa002cda8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_165` and `rank` of elliptic_curves `9282.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c57f952fa002cda8 emitted 2026-05-18T17:35:49.743815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00462
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c5b3487aa0a868ef
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_139` and `torsion` of elliptic_curves `9763.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c5b3487aa0a868ef emitted 2026-05-18T17:35:49.743815+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00463
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f0d8f1d4df6dbb06
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_20` and `conductor` of elliptic_curves `7950.p2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f0d8f1d4df6dbb06 emitted 2026-05-18T17:35:49.746814+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00464
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=949e3b68f82d6bf4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_3` and `torsion` of elliptic_curves `3479.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 949e3b68f82d6bf4 emitted 2026-05-18T17:35:49.750868+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00465
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c3010a3e60a31901
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_5` and `tamagawa_product` of elliptic_curves `6006.r2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c3010a3e60a31901 emitted 2026-05-18T17:35:49.751868+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00466
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=262b831a10408582
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `rank` of elliptic_curves `1074.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 262b831a10408582 emitted 2026-05-18T17:35:49.763868+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00467
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=e408cde3bad4ff6d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_5` and `torsion` of elliptic_curves `2493.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e408cde3bad4ff6d emitted 2026-05-18T17:35:49.775868+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00468
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=df386444ac489c2a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `conductor` of elliptic_curves `7392.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record df386444ac489c2a emitted 2026-05-18T17:35:49.777867+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00469
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=19f0de6d5f07e38a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_1` and `torsion` of elliptic_curves `7840.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 19f0de6d5f07e38a emitted 2026-05-18T17:35:49.778867+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00470
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f7ea392fe3dad594
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_14` and `rank` of elliptic_curves `2160.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f7ea392fe3dad594 emitted 2026-05-18T17:35:49.782910+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00471
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1ab6289f3916c3c4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_18` and `conductor` of elliptic_curves `913.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1ab6289f3916c3c4 emitted 2026-05-18T17:35:49.782910+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00472
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=ea7a41a6019feae5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_139` and `torsion` of elliptic_curves `7308.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ea7a41a6019feae5 emitted 2026-05-18T17:35:49.783911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00473
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=02030934693ab4d2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `conductor` of elliptic_curves `6090.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 02030934693ab4d2 emitted 2026-05-18T17:35:49.785910+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00474
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=cb571a7a1bfb92d7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_1` and `rank` of elliptic_curves `2548.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cb571a7a1bfb92d7 emitted 2026-05-18T17:35:49.786912+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00475
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=28abbca405d1c986
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_3` and `tamagawa_product` of elliptic_curves `9570.q1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 28abbca405d1c986 emitted 2026-05-18T17:35:49.787920+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00476
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fb60a20d23ce436b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_7` and `torsion` of elliptic_curves `3477.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fb60a20d23ce436b emitted 2026-05-18T17:35:49.790912+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00477
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=19c3fa0e96156275
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_11` and `tamagawa_product` of elliptic_curves `6570.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 19c3fa0e96156275 emitted 2026-05-18T17:35:49.793910+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00478
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=50f93b105456fd0b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `4_1` and `tamagawa_product` of elliptic_curves `1320.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 50f93b105456fd0b emitted 2026-05-18T17:35:49.799910+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00479
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fccf06c7115bca75
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `tamagawa_product` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fccf06c7115bca75 emitted 2026-05-18T17:35:49.803911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00480
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=a89ed7e5bea04cf4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_9` and `rank` of elliptic_curves `4160.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a89ed7e5bea04cf4 emitted 2026-05-18T17:35:49.806911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00481
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7d9d047cd0fb9e61
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_7` and `conductor` of elliptic_curves `3520.y2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d9d047cd0fb9e61 emitted 2026-05-18T17:35:49.806911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00482
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c706414cd3ec4437
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_3` and `conductor` of elliptic_curves `4920.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c706414cd3ec4437 emitted 2026-05-18T17:35:49.807911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00483
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=12abc11d328f6e94
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_13` and `rank` of elliptic_curves `8090.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 12abc11d328f6e94 emitted 2026-05-18T17:35:49.807911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00484
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=5b207a46a8a12031
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_15` and `conductor` of elliptic_curves `5150.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5b207a46a8a12031 emitted 2026-05-18T17:35:49.808911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00485
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c55f7d648e587c7f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `conductor` of elliptic_curves `2358.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c55f7d648e587c7f emitted 2026-05-18T17:35:49.811911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00486
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=934e7836d5ec99d6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `conductor` of elliptic_curves `8820.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 934e7836d5ec99d6 emitted 2026-05-18T17:35:49.812911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00487
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=46b5e439dc25639f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `rank` of elliptic_curves `459.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 46b5e439dc25639f emitted 2026-05-18T17:35:49.813911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00488
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=93de24cabb66f006
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `rank` of elliptic_curves `7975.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 93de24cabb66f006 emitted 2026-05-18T17:35:49.814911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00489
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=78e18b85be73123b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_20` and `conductor` of elliptic_curves `637.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78e18b85be73123b emitted 2026-05-18T17:35:49.815911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00490
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c0499cd59485c7ee
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_4` and `rank` of elliptic_curves `9990.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c0499cd59485c7ee emitted 2026-05-18T17:35:49.815911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00491
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=b0e64d6f613260e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_161` and `rank` of elliptic_curves `7650.bm2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b0e64d6f613260e3 emitted 2026-05-18T17:35:49.815911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00492
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=1c39083fe9bb4681
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `rank` of elliptic_curves `5400.bv1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1c39083fe9bb4681 emitted 2026-05-18T17:35:49.821911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00493
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=15aedf708881cb8a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_10` and `tamagawa_product` of elliptic_curves `862.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 15aedf708881cb8a emitted 2026-05-18T17:35:49.822911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00494
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=c826fa454030d8e8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_5` and `torsion` of elliptic_curves `8850.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c826fa454030d8e8 emitted 2026-05-18T17:35:49.822911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00495
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bba21fa598807fba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_165` and `tamagawa_product` of elliptic_curves `5958.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bba21fa598807fba emitted 2026-05-18T17:35:49.823911+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00496
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=767490ea0d9b1b46
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_3` and `rank` of elliptic_curves `7469.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 767490ea0d9b1b46 emitted 2026-05-18T17:35:49.825910+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00497
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=f1b1169a8f994b25
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_7` and `torsion` of elliptic_curves `9450.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f1b1169a8f994b25 emitted 2026-05-18T17:35:49.839959+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00498
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=fb35f74c10581e9e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_2` and `torsion` of elliptic_curves `4200.z4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fb35f74c10581e9e emitted 2026-05-18T17:35:49.840959+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00499
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=7f9d0634c17ef35e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `rank` of elliptic_curves `7810.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7f9d0634c17ef35e emitted 2026-05-18T17:35:49.841959+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00500
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=a1; batch=batch-20260518T173548Z-b9034c;
  record_id=bbb66962ab356c04
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from a1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_5` and `conductor` of elliptic_curves `6840.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bbb66962ab356c04 emitted 2026-05-18T17:35:49.841959+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.000. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

