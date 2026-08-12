# Theseus → Ergon Training Anchor Handoff

Generated: 2026-06-07T07:05:07.595995+00:00
Selection: top 500 records with training_weight ≥ 0.5 and verdict ∈ ['SHADOW_CATALOG', 'PROMOTED', 'REJECTED']

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
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3eb95fe22b2c64cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_3`
  and `torsion` of elliptic_curves `6650.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3eb95fe22b2c64cb emitted 2026-05-30T06:27:29.718003+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00002
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=85fe2c2758156199
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_17`
  and `tamagawa_product` of elliptic_curves `9350.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 85fe2c2758156199 emitted 2026-05-30T06:27:30.222994+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00003
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=da124e1347504f45
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_5` and
  `rank` of elliptic_curves `8400.co3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da124e1347504f45 emitted 2026-05-30T06:27:29.733002+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00004
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=07993788f681fbe8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_4`
  and `tamagawa_product` of elliptic_curves `5958.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 07993788f681fbe8 emitted 2026-05-30T06:27:30.228993+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00005
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=22216ce06ade237d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `10_3` and
  `rank` of elliptic_curves `3479.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 22216ce06ade237d emitted 2026-05-30T06:27:30.685985+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00006
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a7602e9dc03ab1de
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `torsion` of elliptic_curves `8838.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a7602e9dc03ab1de emitted 2026-05-30T06:27:29.737003+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00007
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=59c1d3603fa70259
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `tamagawa_product` of elliptic_curves `723.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 59c1d3603fa70259 emitted 2026-05-30T06:27:32.177891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00008
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=def5e48edec1be3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_6` and
  `torsion` of elliptic_curves `9920.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record def5e48edec1be3e emitted 2026-05-30T06:27:30.273992+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00009
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9573f95fe056619c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_2`
  and `rank` of elliptic_curves `2448.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9573f95fe056619c emitted 2026-05-30T06:27:30.236993+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00010
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=eef1fe5e951dbcda
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_161`
  and `torsion` of elliptic_curves `5187.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eef1fe5e951dbcda emitted 2026-05-30T06:27:31.105898+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00011
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=24d15fbc81396144
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_3`
  and `rank` of elliptic_curves `8766.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 24d15fbc81396144 emitted 2026-05-30T06:27:30.688984+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00012
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a3be2b748a05fe87
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_7`
  and `rank` of elliptic_curves `7685.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a3be2b748a05fe87 emitted 2026-05-30T06:27:30.114996+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00013
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=623f0b26e1f9b6c9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `6_3`
  and `torsion` of elliptic_curves `1936.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 623f0b26e1f9b6c9 emitted 2026-05-30T06:27:29.784001+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00014
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4ce243f3adb83abc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_161`
  and `torsion` of elliptic_curves `3192.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4ce243f3adb83abc emitted 2026-05-30T06:27:32.208891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00015
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a7544f58d9125d58
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_17`
  and `rank` of elliptic_curves `2170.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a7544f58d9125d58 emitted 2026-05-30T06:27:32.203891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00016
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1414457323317c78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `8_19`
  and `rank` of elliptic_curves `45.a8`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1414457323317c78 emitted 2026-05-30T06:27:30.281992+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00017
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e5277b9c9b001081
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_5` and
  `tamagawa_product` of elliptic_curves `2934.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e5277b9c9b001081 emitted 2026-05-30T06:27:30.523986+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00018
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=654f3b8b420b4e85
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_5`
  and `torsion` of elliptic_curves `7920.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 654f3b8b420b4e85 emitted 2026-05-30T06:27:30.269992+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00019
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6642ea1661f5b8af
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_5` and
  `rank` of elliptic_curves `9256.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6642ea1661f5b8af emitted 2026-05-30T06:27:30.614986+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00020
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1dba83f8c8a27870
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_21`
  and `rank` of elliptic_curves `4800.cq4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1dba83f8c8a27870 emitted 2026-05-30T06:27:31.128898+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00021
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=580ec1e0afe315fc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_12`
  and `tamagawa_product` of elliptic_curves `8211.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 580ec1e0afe315fc emitted 2026-05-30T06:27:31.280892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00022
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6654d5ccb2e24e25
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_16`
  and `torsion` of elliptic_curves `8827.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6654d5ccb2e24e25 emitted 2026-05-30T06:27:30.701985+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00023
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=78b2fba1aadd6ebd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `10_3` and
  `torsion` of elliptic_curves `8670.v8`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78b2fba1aadd6ebd emitted 2026-05-30T06:27:30.757982+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00024
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=adc239b71aecbe8c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `4_1` and
  `rank` of elliptic_curves `5440.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record adc239b71aecbe8c emitted 2026-05-30T06:27:30.138995+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00025
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f55636e210a0788d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `torsion` of elliptic_curves `9126.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f55636e210a0788d emitted 2026-05-30T06:27:32.051890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00026
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4cfec43bc2f67633
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `10_1` and
  `tamagawa_product` of elliptic_curves `7770.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4cfec43bc2f67633 emitted 2026-05-30T06:27:29.787002+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00027
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=987bb1b0d6f640e7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_3`
  and `torsion` of elliptic_curves `6050.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 987bb1b0d6f640e7 emitted 2026-05-30T06:27:29.813000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00028
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7d658b06b6360689
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `4_1` and
  `torsion` of elliptic_curves `7366.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d658b06b6360689 emitted 2026-05-30T06:27:32.209891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00029
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1e56c215c20750eb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_17` and
  `torsion` of elliptic_curves `1472.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1e56c215c20750eb emitted 2026-05-30T06:27:32.718863+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00030
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=38cd1ca13883f6d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `3_1`
  and `tamagawa_product` of elliptic_curves `5235.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38cd1ca13883f6d1 emitted 2026-05-30T06:27:32.220891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00031
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0e5c65132f74d1da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_1`
  and `rank` of elliptic_curves `3479.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0e5c65132f74d1da emitted 2026-05-30T06:27:33.063366+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00032
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=86fec7e9a95c3b44
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `10_165`
  and `tamagawa_product` of elliptic_curves `6160.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 86fec7e9a95c3b44 emitted 2026-05-30T06:27:30.361990+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00033
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8aea45633b648e07
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_2`
  and `torsion` of elliptic_curves `2751.d4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8aea45633b648e07 emitted 2026-05-30T06:27:30.311992+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00034
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f732f5dd73c7a969
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_9` and
  `torsion` of elliptic_curves `5304.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f732f5dd73c7a969 emitted 2026-05-30T06:27:30.535988+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00035
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fa07097a41855e0d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_5` and
  `torsion` of elliptic_curves `4582.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fa07097a41855e0d emitted 2026-05-30T06:27:30.529988+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00036
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=abd52cb915c8d939
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_13`
  and `tamagawa_product` of elliptic_curves `7623.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record abd52cb915c8d939 emitted 2026-05-30T06:27:30.399990+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00037
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f9c8b648aa079042
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_3` and
  `tamagawa_product` of elliptic_curves `1659.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f9c8b648aa079042 emitted 2026-05-30T06:27:30.270993+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00038
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e9c093d4d0f87594
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_14`
  and `tamagawa_product` of elliptic_curves `3248.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e9c093d4d0f87594 emitted 2026-05-30T06:27:30.645986+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00039
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=194780f9207c16fd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_161`
  and `rank` of elliptic_curves `2656.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 194780f9207c16fd emitted 2026-05-30T06:27:30.636984+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00040
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=be6539218a41358d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_161`
  and `rank` of elliptic_curves `8322.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be6539218a41358d emitted 2026-05-30T06:27:31.171895+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00041
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e0b56520ae021fd6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_165`
  and `tamagawa_product` of elliptic_curves `7725.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e0b56520ae021fd6 emitted 2026-05-30T06:27:31.134901+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00042
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=91480e74a25140fa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_3`
  and `torsion` of elliptic_curves `4576.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 91480e74a25140fa emitted 2026-05-30T06:27:31.286891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00043
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f927477e10cb9ebd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_3` and
  `tamagawa_product` of elliptic_curves `9864.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f927477e10cb9ebd emitted 2026-05-30T06:27:31.281892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00044
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8c235acc368bcee1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_3`
  and `tamagawa_product` of elliptic_curves `3648.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c235acc368bcee1 emitted 2026-05-30T06:27:30.850981+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00045
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fbaa02f4c924a63c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `10_124`
  and `torsion` of elliptic_curves `3126.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fbaa02f4c924a63c emitted 2026-05-30T06:27:30.713984+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00046
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=aa9a5b08b9798657
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `10_165`
  and `tamagawa_product` of elliptic_curves `5950.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record aa9a5b08b9798657 emitted 2026-05-30T06:27:30.940980+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00047
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ab5a2b1a376778ad
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_139`
  and `torsion` of elliptic_curves `1869.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ab5a2b1a376778ad emitted 2026-05-30T06:27:30.758982+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00048
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7c67e134b266372f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `5_2`
  and `rank` of elliptic_curves `6678.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7c67e134b266372f emitted 2026-05-30T06:27:31.931386+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00049
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c8cc5f05499a6016
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_145`
  and `rank` of elliptic_curves `4560.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c8cc5f05499a6016 emitted 2026-05-30T06:27:30.141994+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00050
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7685c2e3639fe063
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_5`
  and `tamagawa_product` of elliptic_curves `9450.cl2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7685c2e3639fe063 emitted 2026-05-30T06:27:32.064894+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00051
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4ed7edb071f44339
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_5` and
  `rank` of elliptic_curves `6600.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4ed7edb071f44339 emitted 2026-05-30T06:27:32.061894+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00052
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=62e270651ab8e496
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `3_1` and
  `tamagawa_product` of elliptic_curves `9865.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 62e270651ab8e496 emitted 2026-05-30T06:27:29.872000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00053
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b854d5e639ca1f46
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_161`
  and `rank` of elliptic_curves `1800.m4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b854d5e639ca1f46 emitted 2026-05-30T06:27:29.837001+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00054
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a18f59af93ceb066
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `3_1` and
  `tamagawa_product` of elliptic_curves `1216.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a18f59af93ceb066 emitted 2026-05-30T06:27:29.969998+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00055
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b022d27cfc992337
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_165`
  and `tamagawa_product` of elliptic_curves `8526.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b022d27cfc992337 emitted 2026-05-30T06:27:29.817001+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00056
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c4b6562fb54243f3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_161`
  and `rank` of elliptic_curves `5880.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c4b6562fb54243f3 emitted 2026-05-30T06:27:32.237890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00057
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ad014498e25dd7f3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_6` and
  `rank` of elliptic_curves `7410.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad014498e25dd7f3 emitted 2026-05-30T06:27:33.030857+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00058
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4d5e92ed0b8daa51
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_18`
  and `rank` of elliptic_curves `4564.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4d5e92ed0b8daa51 emitted 2026-05-30T06:27:32.721863+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00059
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c2a6c1acd73e4da4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `3_1`
  and `torsion` of elliptic_curves `7350.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c2a6c1acd73e4da4 emitted 2026-05-30T06:27:32.720864+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00060
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e30f4d0db88bd7d9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_1`
  and `tamagawa_product` of elliptic_curves `2443.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e30f4d0db88bd7d9 emitted 2026-05-30T06:27:32.223890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00061
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6371b40bd2f545e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_16` and
  `rank` of elliptic_curves `7308.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6371b40bd2f545e3 emitted 2026-05-30T06:27:32.314890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00062
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1841be19efc43193
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_14` and
  `rank` of elliptic_curves `3510.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1841be19efc43193 emitted 2026-05-30T06:27:33.073366+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00063
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=42202337f00edcc7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_2` and
  `rank` of elliptic_curves `6358.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 42202337f00edcc7 emitted 2026-05-30T06:27:33.094365+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00064
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fd5d5fb4023628df
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `10_124`
  and `torsion` of elliptic_curves `336.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fd5d5fb4023628df emitted 2026-05-30T06:27:30.370990+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00065
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0d477b010afcc765
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_7` and
  `torsion` of elliptic_curves `5150.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0d477b010afcc765 emitted 2026-05-30T06:27:30.367995+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00066
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=49c74bff9a5b6b95
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_152`
  and `rank` of elliptic_curves `2070.b5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 49c74bff9a5b6b95 emitted 2026-05-30T06:27:34.317644+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00067
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1bb68c9fa4c1b834
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `5_2`
  and `torsion` of elliptic_curves `9864.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1bb68c9fa4c1b834 emitted 2026-05-30T06:27:31.828388+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00068
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ab05e2a2f54e4886
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_3` and
  `torsion` of elliptic_curves `7605.h4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ab05e2a2f54e4886 emitted 2026-05-30T06:27:30.540988+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00069
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=606842df917deca5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_9` and
  `tamagawa_product` of elliptic_curves `4688.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 606842df917deca5 emitted 2026-05-30T06:27:30.558988+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00070
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5fe68955b862e27a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `3_1`
  and `tamagawa_product` of elliptic_curves `5334.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5fe68955b862e27a emitted 2026-05-30T06:27:30.676984+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00071
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=da1353e1d23adaf7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_10`
  and `torsion` of elliptic_curves `3200.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da1353e1d23adaf7 emitted 2026-05-30T06:27:31.445396+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00072
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9f988e0eecf2e1ac
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_161`
  and `torsion` of elliptic_curves `6867.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9f988e0eecf2e1ac emitted 2026-05-30T06:27:30.420990+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00073
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=580039310eb68725
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_15`
  and `tamagawa_product` of elliptic_curves `6400.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 580039310eb68725 emitted 2026-05-30T06:27:30.412990+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00074
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6b11a0789fc76427
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_8` and
  `tamagawa_product` of elliptic_curves `570.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6b11a0789fc76427 emitted 2026-05-30T06:27:30.276994+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00075
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a1f1aae314dc41eb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_16` and
  `rank` of elliptic_curves `1865.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a1f1aae314dc41eb emitted 2026-05-30T06:27:30.323991+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00076
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=baaecfd7751479c3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `10_139`
  and `tamagawa_product` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record baaecfd7751479c3 emitted 2026-05-30T06:27:30.661985+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00077
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f501d0204dbcc2a6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_4` and
  `tamagawa_product` of elliptic_curves `7685.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f501d0204dbcc2a6 emitted 2026-05-30T06:27:30.665986+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00078
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=99c7b38d75ef22ba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_5`
  and `tamagawa_product` of elliptic_curves `1176.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 99c7b38d75ef22ba emitted 2026-05-30T06:27:33.565356+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00079
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=227352e90d6fc548
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `6_3` and
  `tamagawa_product` of elliptic_curves `7776.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 227352e90d6fc548 emitted 2026-05-30T06:27:33.611355+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00080
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=05022f2d6941e63b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_6`
  and `tamagawa_product` of elliptic_curves `528.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 05022f2d6941e63b emitted 2026-05-30T06:27:31.205893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00081
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=98ac0429b05d23ca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_10` and
  `rank` of elliptic_curves `3768.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 98ac0429b05d23ca emitted 2026-05-30T06:27:31.175893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00082
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9d3d741396e9c117
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_9` and
  `torsion` of elliptic_curves `6566.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9d3d741396e9c117 emitted 2026-05-30T06:27:35.126816+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00083
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5368baa23843dfd6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_15`
  and `rank` of elliptic_curves `2420.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5368baa23843dfd6 emitted 2026-05-30T06:27:31.919386+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00084
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=afd509d7b26ccce9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_1` and
  `rank` of elliptic_curves `6585.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record afd509d7b26ccce9 emitted 2026-05-30T06:27:31.290892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00085
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e6fe95d6c8f0ff96
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_4`
  and `torsion` of elliptic_curves `4571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e6fe95d6c8f0ff96 emitted 2026-05-30T06:27:31.295891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00086
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3bcfb18a4453b430
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `5_2`
  and `tamagawa_product` of elliptic_curves `864.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3bcfb18a4453b430 emitted 2026-05-30T06:27:31.406397+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00087
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2053b8d64060c591
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_161`
  and `torsion` of elliptic_curves `8141.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2053b8d64060c591 emitted 2026-05-30T06:27:31.517395+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00088
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5f4f27e86d7487d5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_18`
  and `torsion` of elliptic_curves `6550.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5f4f27e86d7487d5 emitted 2026-05-30T06:27:30.889980+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00089
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7b321d55f1321713
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_7` and
  `tamagawa_product` of elliptic_curves `466.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b321d55f1321713 emitted 2026-05-30T06:27:31.074899+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00090
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4431b02c35f9ba56
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_4`
  and `rank` of elliptic_curves `9152.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4431b02c35f9ba56 emitted 2026-05-30T06:27:30.750983+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00091
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=80c60698cb3bd3ba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_1`
  and `rank` of elliptic_curves `9865.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 80c60698cb3bd3ba emitted 2026-05-30T06:27:30.719984+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00092
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ff1b8a71e8b55bb6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `rank` of elliptic_curves `4896.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff1b8a71e8b55bb6 emitted 2026-05-30T06:27:31.001900+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00093
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=97b4b560e48cd1e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_5`
  and `torsion` of elliptic_curves `1760.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 97b4b560e48cd1e3 emitted 2026-05-30T06:27:31.361890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00094
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0e9f2903e31098a0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_7`
  and `tamagawa_product` of elliptic_curves `6090.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0e9f2903e31098a0 emitted 2026-05-30T06:27:30.789982+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00095
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=30348af606358534
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_13` and
  `tamagawa_product` of elliptic_curves `3822.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 30348af606358534 emitted 2026-05-30T06:27:30.776983+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00096
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a0e2202a613b2fd1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_9` and
  `rank` of elliptic_curves `4928.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a0e2202a613b2fd1 emitted 2026-05-30T06:27:31.945386+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00097
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c4a298a512d8ec40
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_7`
  and `rank` of elliptic_curves `5236.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c4a298a512d8ec40 emitted 2026-05-30T06:27:31.943386+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00098
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=dacac6fb0cf52174
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_152`
  and `torsion` of elliptic_curves `6270.l2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dacac6fb0cf52174 emitted 2026-05-30T06:27:34.173647+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00099
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c641a24bfc633ac9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `7_4` and
  `tamagawa_product` of elliptic_curves `6566.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c641a24bfc633ac9 emitted 2026-05-30T06:27:33.371360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00100
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=762eb04bf4d226c5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_8` and
  `tamagawa_product` of elliptic_curves `6768.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 762eb04bf4d226c5 emitted 2026-05-30T06:27:32.080894+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00101
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e243e6675dbb4a5d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_5`
  and `tamagawa_product` of elliptic_curves `2830.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e243e6675dbb4a5d emitted 2026-05-30T06:27:32.088893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00102
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=81f16b706441c84a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_5`
  and `torsion` of elliptic_curves `5040.bl1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 81f16b706441c84a emitted 2026-05-30T06:27:32.159892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00103
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8eea70c21c69ad20
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_3` and
  `rank` of elliptic_curves `1267.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8eea70c21c69ad20 emitted 2026-05-30T06:27:33.176364+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00104
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c5b27380390da87e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_19`
  and `tamagawa_product` of elliptic_curves `864.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c5b27380390da87e emitted 2026-05-30T06:27:29.888000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00105
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5cdcc6476d477969
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_7` and
  `torsion` of elliptic_curves `1968.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5cdcc6476d477969 emitted 2026-05-30T06:27:30.045996+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00106
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=22ad09128a81511c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_7`
  and `torsion` of elliptic_curves `7200.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 22ad09128a81511c emitted 2026-05-30T06:27:29.844001+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00107
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e25a3b5fb541e169
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_5`
  and `rank` of elliptic_curves `8308.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e25a3b5fb541e169 emitted 2026-05-30T06:27:29.867000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00108
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=36aa022fdeae702d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_10`
  and `rank` of elliptic_curves `7092.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 36aa022fdeae702d emitted 2026-05-30T06:27:29.991998+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00109
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=240459df890d1df8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `8_2` and
  `tamagawa_product` of elliptic_curves `414.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 240459df890d1df8 emitted 2026-05-30T06:27:32.157892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00110
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a8e4e95e63171d1b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_9`
  and `torsion` of elliptic_curves `7514.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8e4e95e63171d1b emitted 2026-05-30T06:27:29.830001+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00111
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e328dc49453e90ec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_9`
  and `tamagawa_product` of elliptic_curves `7872.s2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e328dc49453e90ec emitted 2026-05-30T06:27:29.826001+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00112
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=81ac19670038f15a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_5` and
  `rank` of elliptic_curves `8835.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 81ac19670038f15a emitted 2026-05-30T06:27:32.271890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00113
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1e2b4f0bfe5565ca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_6`
  and `rank` of elliptic_curves `960.c6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1e2b4f0bfe5565ca emitted 2026-05-30T06:27:32.247891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00114
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=77828c28186cb079
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_3`
  and `tamagawa_product` of elliptic_curves `5400.bv1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 77828c28186cb079 emitted 2026-05-30T06:27:33.416360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00115
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b719b0c790623d28
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_5`
  and `rank` of elliptic_curves `6327.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b719b0c790623d28 emitted 2026-05-30T06:27:33.404359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00116
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1ad5288422bd69c6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_1`
  and `rank` of elliptic_curves `9240.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1ad5288422bd69c6 emitted 2026-05-30T06:27:32.726864+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00117
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1407fd11c51a8ecb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_3`
  and `tamagawa_product` of elliptic_curves `1668.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1407fd11c51a8ecb emitted 2026-05-30T06:27:32.749862+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00118
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6f9397f3dd15b1d9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `torsion` of elliptic_curves `6370.r3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6f9397f3dd15b1d9 emitted 2026-05-30T06:27:32.859861+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00119
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3cffde4a48cae191
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_8` and
  `torsion` of elliptic_curves `5082.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3cffde4a48cae191 emitted 2026-05-30T06:27:32.917859+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00120
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e842ed74c74d18d8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_1`
  and `torsion` of elliptic_curves `1138.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e842ed74c74d18d8 emitted 2026-05-30T06:27:32.817862+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00121
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=04aab05614eb73f3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_2`
  and `torsion` of elliptic_curves `8874.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 04aab05614eb73f3 emitted 2026-05-30T06:27:32.301889+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00122
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d3ea423bf9ab9398
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_2` and
  `torsion` of elliptic_curves `2130.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d3ea423bf9ab9398 emitted 2026-05-30T06:27:33.221363+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00123
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=847bce1752464c85
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_139`
  and `torsion` of elliptic_curves `2027.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 847bce1752464c85 emitted 2026-05-30T06:27:32.316889+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00124
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=40e1d56a2d70f896
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_5`
  and `torsion` of elliptic_curves `5616.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 40e1d56a2d70f896 emitted 2026-05-30T06:27:33.079366+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00125
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7d35a6e9149d4557
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_161`
  and `tamagawa_product` of elliptic_curves `4195.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d35a6e9149d4557 emitted 2026-05-30T06:27:33.171364+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00126
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9166cd7688469585
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `6_1`
  and `tamagawa_product` of elliptic_curves `1850.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9166cd7688469585 emitted 2026-05-30T06:27:33.117365+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00127
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9ad13bb499040225
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_10`
  and `torsion` of elliptic_curves `1680.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9ad13bb499040225 emitted 2026-05-30T06:27:36.072798+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00128
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9d52ce8d91e86be7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_13`
  and `rank` of elliptic_curves `4161.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9d52ce8d91e86be7 emitted 2026-05-30T06:27:34.439642+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00129
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=abfee01daf31bd74
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_5` and
  `torsion` of elliptic_curves `6336.bi1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record abfee01daf31bd74 emitted 2026-05-30T06:27:30.470989+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00130
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9684f4cbab5bef12
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_2` and
  `torsion` of elliptic_curves `3248.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9684f4cbab5bef12 emitted 2026-05-30T06:27:30.372990+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00131
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7aa53579c94b60ab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_18`
  and `torsion` of elliptic_curves `3800.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7aa53579c94b60ab emitted 2026-05-30T06:27:31.779389+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00132
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=344d19300ab027db
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_8` and
  `torsion` of elliptic_curves `8640.bu2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 344d19300ab027db emitted 2026-05-30T06:27:34.464642+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00133
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e4adbbbdda916ed8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_16` and
  `tamagawa_product` of elliptic_curves `1254.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e4adbbbdda916ed8 emitted 2026-05-30T06:27:34.332644+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00134
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b2d627974bfef341
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_5` and
  `rank` of elliptic_curves `9864.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b2d627974bfef341 emitted 2026-05-30T06:27:34.303645+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00135
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ffee26d3f3cd9d06
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_7`
  and `torsion` of elliptic_curves `8979.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ffee26d3f3cd9d06 emitted 2026-05-30T06:27:34.414642+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00136
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=38dd7d384bd354b5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_4`
  and `tamagawa_product` of elliptic_curves `8672.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38dd7d384bd354b5 emitted 2026-05-30T06:27:31.560394+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00137
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5aae050543df04a0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_139`
  and `torsion` of elliptic_curves `4630.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5aae050543df04a0 emitted 2026-05-30T06:27:31.726390+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00138
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e7ac63864b95dc19
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_3`
  and `tamagawa_product` of elliptic_curves `3504.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e7ac63864b95dc19 emitted 2026-05-30T06:27:30.568986+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00139
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=12f14c451d22043e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `4_1`
  and `torsion` of elliptic_curves `3190.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 12f14c451d22043e emitted 2026-05-30T06:27:31.549394+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00140
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cfa45166b7c4651a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_17`
  and `torsion` of elliptic_curves `5970.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cfa45166b7c4651a emitted 2026-05-30T06:27:31.409397+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00141
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c14fc227ddcec6e4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_161`
  and `tamagawa_product` of elliptic_curves `1960.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c14fc227ddcec6e4 emitted 2026-05-30T06:27:34.384642+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00142
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6c073b95e77d27d7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `6_3` and
  `rank` of elliptic_curves `2420.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6c073b95e77d27d7 emitted 2026-05-30T06:27:31.491396+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00143
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=58afd910cb41d141
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_11`
  and `torsion` of elliptic_curves `3726.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 58afd910cb41d141 emitted 2026-05-30T06:27:31.892387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00144
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7f38ea5f4bab2557
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `8_19`
  and `tamagawa_product` of elliptic_curves `5025.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7f38ea5f4bab2557 emitted 2026-05-30T06:27:35.787804+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00145
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=350261af1153f612
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_161`
  and `torsion` of elliptic_curves `3630.a3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 350261af1153f612 emitted 2026-05-30T06:27:30.579987+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00146
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=71e02f7313e2ef41
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_165`
  and `rank` of elliptic_curves `5610.bc4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 71e02f7313e2ef41 emitted 2026-05-30T06:27:30.454989+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00147
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1164065885310d6a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_5`
  and `torsion` of elliptic_curves `7920.be2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1164065885310d6a emitted 2026-05-30T06:27:33.771652+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00148
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fc4a8f01b4d83220
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_124`
  and `rank` of elliptic_curves `528.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fc4a8f01b4d83220 emitted 2026-05-30T06:27:35.575807+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00149
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=766af2569b8c1597
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `rank` of elliptic_curves `2724.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 766af2569b8c1597 emitted 2026-05-30T06:27:35.633807+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00150
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=59fc145e3409ce16
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_10`
  and `torsion` of elliptic_curves `5040.i5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 59fc145e3409ce16 emitted 2026-05-30T06:27:30.333991+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00151
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8f52087b93354076
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_19`
  and `tamagawa_product` of elliptic_curves `9422.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8f52087b93354076 emitted 2026-05-30T06:27:33.910650+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00152
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0838ff5719c72dd1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_3`
  and `tamagawa_product` of elliptic_curves `9633.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0838ff5719c72dd1 emitted 2026-05-30T06:27:33.737652+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00153
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e11b515d42ff362c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_4` and
  `rank` of elliptic_curves `1918.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e11b515d42ff362c emitted 2026-05-30T06:27:33.761653+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00154
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=968dd4910c922681
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_10`
  and `rank` of elliptic_curves `8925.k2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 968dd4910c922681 emitted 2026-05-30T06:27:30.669985+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00155
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c5d8a0ee8ae3ad55
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_1`
  and `torsion` of elliptic_curves `7543.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c5d8a0ee8ae3ad55 emitted 2026-05-30T06:27:33.632357+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00156
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9cc1f0d9702fad86
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_18`
  and `tamagawa_product` of elliptic_curves `8217.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9cc1f0d9702fad86 emitted 2026-05-30T06:27:33.588355+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00157
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9a7f281a1299dd6f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_10`
  and `rank` of elliptic_curves `2394.n3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9a7f281a1299dd6f emitted 2026-05-30T06:27:35.703805+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00158
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6f3bf88d33439b6b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_16`
  and `tamagawa_product` of elliptic_curves `4560.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6f3bf88d33439b6b emitted 2026-05-30T06:27:33.617355+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00159
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=aeea606af86be143
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `6_2`
  and `torsion` of elliptic_curves `9070.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record aeea606af86be143 emitted 2026-05-30T06:27:33.930649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00160
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=615687758fae5cdd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_2` and
  `rank` of elliptic_curves `9114.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 615687758fae5cdd emitted 2026-05-30T06:27:35.232815+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00161
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e27b230a14a5d8c0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_5` and
  `rank` of elliptic_curves `1296.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e27b230a14a5d8c0 emitted 2026-05-30T06:27:31.278892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00162
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=dda36f7ecfcb78d6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_20` and
  `torsion` of elliptic_curves `9768.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dda36f7ecfcb78d6 emitted 2026-05-30T06:27:31.226892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00163
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=74fc8a6479ddb715
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_10`
  and `tamagawa_product` of elliptic_curves `6306.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 74fc8a6479ddb715 emitted 2026-05-30T06:27:31.905387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00164
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b9e6a75848643457
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_5` and
  `rank` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b9e6a75848643457 emitted 2026-05-30T06:27:35.236814+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00165
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a2c7f321bd9b8303
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_15`
  and `tamagawa_product` of elliptic_curves `404.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a2c7f321bd9b8303 emitted 2026-05-30T06:27:35.145815+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00166
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d017cbb8b1b1cd6f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_4`
  and `rank` of elliptic_curves `4941.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d017cbb8b1b1cd6f emitted 2026-05-30T06:27:35.124816+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00167
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cedf3efa93e0c363
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `5_2`
  and `rank` of elliptic_curves `4774.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cedf3efa93e0c363 emitted 2026-05-30T06:27:35.209814+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00168
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9d35c0e6d12cb20d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_6` and
  `rank` of elliptic_curves `6477.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9d35c0e6d12cb20d emitted 2026-05-30T06:27:31.683391+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00169
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=dda7662a0c217233
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_17`
  and `torsion` of elliptic_curves `3174.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dda7662a0c217233 emitted 2026-05-30T06:27:31.898387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00170
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=403f977f6da23590
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_2` and
  `rank` of elliptic_curves `9633.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 403f977f6da23590 emitted 2026-05-30T06:27:31.310891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00171
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5987e7d33d070854
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_6` and
  `torsion` of elliptic_curves `5082.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5987e7d33d070854 emitted 2026-05-30T06:27:31.668393+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00172
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=37a2e7efd46b118e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_152`
  and `tamagawa_product` of elliptic_curves `6768.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 37a2e7efd46b118e emitted 2026-05-30T06:27:31.440396+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00173
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=97035829f708a448
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_8` and
  `torsion` of elliptic_curves `1440.c3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 97035829f708a448 emitted 2026-05-30T06:27:35.201815+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00174
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b24f0e16337bfd74
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_2`
  and `rank` of elliptic_curves `5460.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b24f0e16337bfd74 emitted 2026-05-30T06:27:31.530395+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00175
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8cfa9bd9105b2e3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_10` and
  `torsion` of elliptic_curves `1339.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8cfa9bd9105b2e3e emitted 2026-05-30T06:27:33.545359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00176
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b0171253e96107a9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_2`
  and `torsion` of elliptic_curves `7565.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b0171253e96107a9 emitted 2026-05-30T06:27:30.903980+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00177
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b4aad85500b0c5ff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_2`
  and `tamagawa_product` of elliptic_curves `6571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b4aad85500b0c5ff emitted 2026-05-30T06:27:31.065899+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00178
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6471510f66b89cf9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_12` and
  `tamagawa_product` of elliptic_curves `528.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6471510f66b89cf9 emitted 2026-05-30T06:27:31.077899+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00179
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0e883021c41adbf2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_161`
  and `rank` of elliptic_curves `4215.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0e883021c41adbf2 emitted 2026-05-30T06:27:31.233893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00180
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=bc9f9168f49c5d32
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_4`
  and `rank` of elliptic_curves `5719.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bc9f9168f49c5d32 emitted 2026-05-30T06:27:30.814981+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00181
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e06f76bd3a8a4813
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_3`
  and `rank` of elliptic_curves `5760.bn2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e06f76bd3a8a4813 emitted 2026-05-30T06:27:30.831981+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00182
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=301be435d1a3945b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_8` and
  `torsion` of elliptic_curves `942.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 301be435d1a3945b emitted 2026-05-30T06:27:30.790982+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00183
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c41d50a1444e5258
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_20`
  and `torsion` of elliptic_curves `4481.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c41d50a1444e5258 emitted 2026-05-30T06:27:30.853981+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00184
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6a78fa5b9a94889b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_2`
  and `rank` of elliptic_curves `6308.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6a78fa5b9a94889b emitted 2026-05-30T06:27:31.003900+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00185
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e5385fd66138211b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_21` and
  `rank` of elliptic_curves `9108.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e5385fd66138211b emitted 2026-05-30T06:27:31.356890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00186
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e5d4511a8c3a1be2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_20`
  and `torsion` of elliptic_curves `4050.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e5d4511a8c3a1be2 emitted 2026-05-30T06:27:31.390398+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00187
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a29ccf4b45d2caed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_6`
  and `torsion` of elliptic_curves `3933.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a29ccf4b45d2caed emitted 2026-05-30T06:27:34.058649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00188
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=59439f5edcbce831
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_2`
  and `rank` of elliptic_curves `5024.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 59439f5edcbce831 emitted 2026-05-30T06:27:30.927979+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00189
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8d7aa64a62671fd6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_16`
  and `tamagawa_product` of elliptic_curves `840.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8d7aa64a62671fd6 emitted 2026-05-30T06:27:30.929980+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00190
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1b123218caa52e72
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_4` and
  `rank` of elliptic_curves `8835.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1b123218caa52e72 emitted 2026-05-30T06:27:30.926980+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00191
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=612a6cb7c4e71580
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_7` and
  `torsion` of elliptic_curves `3648.bg2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 612a6cb7c4e71580 emitted 2026-05-30T06:27:30.946979+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00192
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=62f49cbdbbf21ac6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_7`
  and `tamagawa_product` of elliptic_curves `8265.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 62f49cbdbbf21ac6 emitted 2026-05-30T06:27:34.699634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00193
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4220f930a42e0a66
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_15` and
  `torsion` of elliptic_curves `978.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4220f930a42e0a66 emitted 2026-05-30T06:27:31.989385+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00194
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=837c01057638e6d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_3`
  and `tamagawa_product` of elliptic_curves `6946.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 837c01057638e6d1 emitted 2026-05-30T06:27:31.951386+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00195
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4e864a5532157b44
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_14`
  and `torsion` of elliptic_curves `2420.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4e864a5532157b44 emitted 2026-05-30T06:27:33.353360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00196
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=97a028b396b13780
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_18` and
  `tamagawa_product` of elliptic_curves `3128.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 97a028b396b13780 emitted 2026-05-30T06:27:34.710633+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00197
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=69c872584d958dad
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `rank` of elliptic_curves `2874.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 69c872584d958dad emitted 2026-05-30T06:27:34.187647+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00198
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e9017b9963816a2b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_6` and
  `tamagawa_product` of elliptic_curves `9510.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e9017b9963816a2b emitted 2026-05-30T06:27:34.155648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00199
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=033fb11e60aa2aa5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_12`
  and `tamagawa_product` of elliptic_curves `2808.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 033fb11e60aa2aa5 emitted 2026-05-30T06:27:34.683634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00200
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e47d79aa9065c879
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_16`
  and `torsion` of elliptic_curves `1950.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e47d79aa9065c879 emitted 2026-05-30T06:27:33.251362+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00201
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=92bb3880c55d35ed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_7` and
  `rank` of elliptic_curves `6240.x3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 92bb3880c55d35ed emitted 2026-05-30T06:27:33.319361+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00202
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=eb709a6e2f3bd568
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `10_139`
  and `tamagawa_product` of elliptic_curves `8463.d4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eb709a6e2f3bd568 emitted 2026-05-30T06:27:32.098893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00203
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=be23a1db7f82fcb9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_11` and
  `rank` of elliptic_curves `1254.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be23a1db7f82fcb9 emitted 2026-05-30T06:27:33.235363+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00204
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5451f2420ea2583b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_3`
  and `torsion` of elliptic_curves `1760.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5451f2420ea2583b emitted 2026-05-30T06:27:33.155364+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00205
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=90c1b96447eb04f5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_2`
  and `tamagawa_product` of elliptic_curves `640.g2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 90c1b96447eb04f5 emitted 2026-05-30T06:27:34.264644+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00206
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=251b0280e9f32efe
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_10` and
  `rank` of elliptic_curves `990.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 251b0280e9f32efe emitted 2026-05-30T06:27:33.206363+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00207
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=be83c7b815995e0b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `3_1` and
  `torsion` of elliptic_curves `6050.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be83c7b815995e0b emitted 2026-05-30T06:27:33.381359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00208
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=747dff006fe0dff4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_3`
  and `torsion` of elliptic_curves `3328.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 747dff006fe0dff4 emitted 2026-05-30T06:27:29.895000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00209
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=24fa3ca987bac98a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_7` and
  `torsion` of elliptic_curves `4114.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 24fa3ca987bac98a emitted 2026-05-30T06:27:30.026997+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00210
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2f2fadf49beceb13
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_10`
  and `tamagawa_product` of elliptic_curves `5408.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2f2fadf49beceb13 emitted 2026-05-30T06:27:30.095996+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00211
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3f21e618669ea4c7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_6` and
  `rank` of elliptic_curves `5958.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f21e618669ea4c7 emitted 2026-05-30T06:27:31.958385+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00212
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ebd1cec02085cf5f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_11` and
  `torsion` of elliptic_curves `5408.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ebd1cec02085cf5f emitted 2026-05-30T06:27:30.024997+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00213
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a91a99fcecb77dc9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `4_1`
  and `tamagawa_product` of elliptic_curves `6124.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a91a99fcecb77dc9 emitted 2026-05-30T06:27:29.852000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00214
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4c899ce0fd55e8ba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_2`
  and `torsion` of elliptic_curves `5862.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4c899ce0fd55e8ba emitted 2026-05-30T06:27:30.221993+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00215
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=71a2ac278537a4ab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_161`
  and `torsion` of elliptic_curves `1008.l5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 71a2ac278537a4ab emitted 2026-05-30T06:27:29.884000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00216
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ec5a02ebf376b04c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_8`
  and `rank` of elliptic_curves `9835.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ec5a02ebf376b04c emitted 2026-05-30T06:27:29.996999+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00217
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7c18dc6728384515
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `torsion` of elliptic_curves `1370.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7c18dc6728384515 emitted 2026-05-30T06:27:32.142892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00218
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c1bd6c03868663fd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_7`
  and `tamagawa_product` of elliptic_curves `8505.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c1bd6c03868663fd emitted 2026-05-30T06:27:32.158892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00219
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5b86c025b9861f99
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_8` and
  `torsion` of elliptic_curves `8050.u1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5b86c025b9861f99 emitted 2026-05-30T06:27:33.458358+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00220
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3f9b016efc91974a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_16`
  and `torsion` of elliptic_curves `5538.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f9b016efc91974a emitted 2026-05-30T06:27:29.904000+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00221
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=aaef7a6247a4ddd5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_6`
  and `tamagawa_product` of elliptic_curves `2850.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record aaef7a6247a4ddd5 emitted 2026-05-30T06:27:29.946999+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00222
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8ca1bec590e34469
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_20`
  and `rank` of elliptic_curves `4485.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ca1bec590e34469 emitted 2026-05-30T06:27:29.895999+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00223
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=468358e30ad8b6b3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_4`
  and `torsion` of elliptic_curves `4112.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 468358e30ad8b6b3 emitted 2026-05-30T06:27:29.982998+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00224
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4dede2469e168201
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_6` and
  `rank` of elliptic_curves `8100.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4dede2469e168201 emitted 2026-05-30T06:27:33.840651+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00225
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cdda7803f681f32d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_124`
  and `tamagawa_product` of elliptic_curves `3768.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cdda7803f681f32d emitted 2026-05-30T06:27:32.691866+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00226
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3d1724edd9def97f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_10`
  and `tamagawa_product` of elliptic_curves `5780.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3d1724edd9def97f emitted 2026-05-30T06:27:32.281890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00227
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=62a57c409319f494
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_17`
  and `torsion` of elliptic_curves `1379.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 62a57c409319f494 emitted 2026-05-30T06:27:33.007858+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00228
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8dabf34d2fd10e4e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_6` and
  `torsion` of elliptic_curves `718.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8dabf34d2fd10e4e emitted 2026-05-30T06:27:33.880650+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00229
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cbf918a41d70d185
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `10_124`
  and `tamagawa_product` of elliptic_curves `8883.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cbf918a41d70d185 emitted 2026-05-30T06:27:33.423358+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00230
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a70b2ae405ae431e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_18`
  and `rank` of elliptic_curves `4890.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a70b2ae405ae431e emitted 2026-05-30T06:27:33.421359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00231
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=72e7b6c9238c9616
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_4` and
  `tamagawa_product` of elliptic_curves `4481.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 72e7b6c9238c9616 emitted 2026-05-30T06:27:33.833652+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00232
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8172078907321b8a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_14`
  and `torsion` of elliptic_curves `5748.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8172078907321b8a emitted 2026-05-30T06:27:32.952859+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00233
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2a16347e7b2beeec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_1` and
  `rank` of elliptic_curves `2779.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a16347e7b2beeec emitted 2026-05-30T06:27:32.974858+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00234
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e7203b831de950d3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_16` and
  `torsion` of elliptic_curves `5088.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e7203b831de950d3 emitted 2026-05-30T06:27:32.755862+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00235
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2a3d0f6b094e7456
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_3`
  and `rank` of elliptic_curves `2413.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a3d0f6b094e7456 emitted 2026-05-30T06:27:32.924860+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00236
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b1073e8e17c1fc98
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_19`
  and `rank` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b1073e8e17c1fc98 emitted 2026-05-30T06:27:32.893860+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00237
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=704a74ad248d0f91
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_3` and
  `rank` of elliptic_curves `7944.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 704a74ad248d0f91 emitted 2026-05-30T06:27:33.827651+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00238
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6b6387e36452fdc8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `torsion` of elliptic_curves `6946.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6b6387e36452fdc8 emitted 2026-05-30T06:27:32.921859+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00239
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a96d6f33405105cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_2` and
  `tamagawa_product` of elliptic_curves `2135.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a96d6f33405105cb emitted 2026-05-30T06:27:33.041860+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00240
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=54742b30d3d22a42
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_161`
  and `torsion` of elliptic_curves `9702.cc2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 54742b30d3d22a42 emitted 2026-05-30T06:27:32.843860+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00241
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7371c34387263976
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `rank` of elliptic_curves `6650.bh2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7371c34387263976 emitted 2026-05-30T06:27:32.823861+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00242
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=10de6209cb34be67
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `8_3` and
  `tamagawa_product` of elliptic_curves `414.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 10de6209cb34be67 emitted 2026-05-30T06:27:32.312889+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00243
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5259f8e3ce3353fa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_2`
  and `torsion` of elliptic_curves `3675.l2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5259f8e3ce3353fa emitted 2026-05-30T06:27:32.819861+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00244
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c4ea7da86983e6fc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_10`
  and `torsion` of elliptic_curves `5789.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c4ea7da86983e6fc emitted 2026-05-30T06:27:33.395360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00245
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=353a49267a741870
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_2`
  and `rank` of elliptic_curves `6026.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 353a49267a741870 emitted 2026-05-30T06:27:33.309360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00246
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3bd8b956c108d203
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_6`
  and `torsion` of elliptic_curves `4107.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3bd8b956c108d203 emitted 2026-05-30T06:27:32.777862+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00247
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1550c8432004afd8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_13` and
  `torsion` of elliptic_curves `610.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1550c8432004afd8 emitted 2026-05-30T06:27:32.770863+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00248
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=430fd02c1f833d1a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_6`
  and `tamagawa_product` of elliptic_curves `2493.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 430fd02c1f833d1a emitted 2026-05-30T06:27:33.286361+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00249
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d392324a4a34bf6c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_4` and
  `rank` of elliptic_curves `2646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d392324a4a34bf6c emitted 2026-05-30T06:27:33.284361+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00250
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7720e645755e1751
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_13` and
  `rank` of elliptic_curves `9822.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7720e645755e1751 emitted 2026-05-30T06:27:36.046799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00251
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d951aedaecb25c40
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_8`
  and `tamagawa_product` of elliptic_curves `6327.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d951aedaecb25c40 emitted 2026-05-30T06:27:36.298796+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00252
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=415d51825d686aa7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_17` and
  `rank` of elliptic_curves `7630.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 415d51825d686aa7 emitted 2026-05-30T06:27:36.212796+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00253
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6143514f96dfe7fb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_3`
  and `torsion` of elliptic_curves `5450.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6143514f96dfe7fb emitted 2026-05-30T06:27:36.050798+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00254
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1ef43f3114d2d9d2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `10_1` and
  `torsion` of elliptic_curves `840.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1ef43f3114d2d9d2 emitted 2026-05-30T06:27:36.341795+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00255
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5c74c2b800eadae1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_10` and
  `tamagawa_product` of elliptic_curves `3600.x2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5c74c2b800eadae1 emitted 2026-05-30T06:27:36.073798+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00256
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3000c4f1927848ab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `4_1` and
  `rank` of elliptic_curves `3417.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3000c4f1927848ab emitted 2026-05-30T06:27:34.477641+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00257
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=942ac64a7c45b945
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_9`
  and `tamagawa_product` of elliptic_curves `7380.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 942ac64a7c45b945 emitted 2026-05-30T06:27:34.653635+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00258
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f9036155347eae6f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_3`
  and `tamagawa_product` of elliptic_curves `1869.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f9036155347eae6f emitted 2026-05-30T06:27:30.497988+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00259
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7b1aba411f7cac08
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_17`
  and `rank` of elliptic_curves `8697.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7b1aba411f7cac08 emitted 2026-05-30T06:27:34.475641+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00260
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4a7c84038ee187d5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_21`
  and `torsion` of elliptic_curves `6270.l2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4a7c84038ee187d5 emitted 2026-05-30T06:27:34.679634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00261
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ccfeef30659ad43d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `5_2`
  and `rank` of elliptic_curves `5304.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ccfeef30659ad43d emitted 2026-05-30T06:27:34.656634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00262
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f9ffe872337c7b75
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_17`
  and `tamagawa_product` of elliptic_curves `404.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f9ffe872337c7b75 emitted 2026-05-30T06:27:31.826388+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00263
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=eb2aeb63bbadea01
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_5` and
  `rank` of elliptic_curves `9450.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eb2aeb63bbadea01 emitted 2026-05-30T06:27:34.662636+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00264
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e61069f281e3c9c6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_4` and
  `rank` of elliptic_curves `6630.y1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e61069f281e3c9c6 emitted 2026-05-30T06:27:34.651634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00265
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2252de0c02de710c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_2` and
  `torsion` of elliptic_curves `9291.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2252de0c02de710c emitted 2026-05-30T06:27:35.051627+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00266
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9af0870a3f1d0aa5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_4` and
  `torsion` of elliptic_curves `1267.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9af0870a3f1d0aa5 emitted 2026-05-30T06:27:34.396641+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00267
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2c8380754e7ef56d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_18` and
  `torsion` of elliptic_curves `2346.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2c8380754e7ef56d emitted 2026-05-30T06:27:34.512641+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00268
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=acf4700550737d9c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_8` and
  `torsion` of elliptic_curves `645.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record acf4700550737d9c emitted 2026-05-30T06:27:34.320645+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00269
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ac112cfef3a5e8bf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_7` and
  `torsion` of elliptic_curves `7448.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac112cfef3a5e8bf emitted 2026-05-30T06:27:35.104816+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00270
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9cc03ba4796a54c1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_10`
  and `torsion` of elliptic_curves `7952.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9cc03ba4796a54c1 emitted 2026-05-30T06:27:34.424642+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00271
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=38d57faca5025f3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_145`
  and `tamagawa_product` of elliptic_curves `5856.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38d57faca5025f3e emitted 2026-05-30T06:27:35.116817+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00272
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5625815af4e6d25b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_3`
  and `rank` of elliptic_curves `5187.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5625815af4e6d25b emitted 2026-05-30T06:27:34.576640+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00273
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=aafce865ed55aabe
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `3_1` and
  `rank` of elliptic_curves `4107.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record aafce865ed55aabe emitted 2026-05-30T06:27:34.544640+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00274
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5ce8f0c128388348
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_9` and
  `torsion` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5ce8f0c128388348 emitted 2026-05-30T06:27:31.728390+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00275
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0075c79ab39ea2f7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_5`
  and `tamagawa_product` of elliptic_curves `5990.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0075c79ab39ea2f7 emitted 2026-05-30T06:27:34.551637+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00276
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=85051a44f66f7373
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_16`
  and `torsion` of elliptic_curves `1520.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 85051a44f66f7373 emitted 2026-05-30T06:27:31.579394+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00277
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1a75d177f66750cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_17` and
  `torsion` of elliptic_curves `3192.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1a75d177f66750cb emitted 2026-05-30T06:27:31.558394+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00278
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=63ac8f01ba25c4ab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `5_2`
  and `tamagawa_product` of elliptic_curves `7776.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 63ac8f01ba25c4ab emitted 2026-05-30T06:27:31.850389+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00279
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=81436571ec6bc3fa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_4` and
  `rank` of elliptic_curves `4800.d5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 81436571ec6bc3fa emitted 2026-05-30T06:27:31.782391+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00280
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7dcf92853785e17f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_8`
  and `torsion` of elliptic_curves `2724.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7dcf92853785e17f emitted 2026-05-30T06:27:34.361643+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00281
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cda705997389c7cf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_2` and
  `torsion` of elliptic_curves `4928.bf2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cda705997389c7cf emitted 2026-05-30T06:27:34.547640+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00282
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f247f445cb7aa522
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_5` and
  `tamagawa_product` of elliptic_curves `7975.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f247f445cb7aa522 emitted 2026-05-30T06:27:34.524641+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00283
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=920c34c49b9a3e11
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_4` and
  `rank` of elliptic_curves `2595.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 920c34c49b9a3e11 emitted 2026-05-30T06:27:34.624635+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00284
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c9a3d71b741978b4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_14`
  and `torsion` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c9a3d71b741978b4 emitted 2026-05-30T06:27:34.367643+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00285
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=af92cae213676ffa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `5_2`
  and `rank` of elliptic_curves `5418.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record af92cae213676ffa emitted 2026-05-30T06:27:34.341641+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00286
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c530687495d33fa2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `4_1`
  and `rank` of elliptic_curves `2205.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c530687495d33fa2 emitted 2026-05-30T06:27:34.535640+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00287
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7a44b5e0995edf90
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_3`
  and `tamagawa_product` of elliptic_curves `9070.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7a44b5e0995edf90 emitted 2026-05-30T06:27:34.525640+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00288
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d22d61064787f315
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_7`
  and `torsion` of elliptic_curves `882.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d22d61064787f315 emitted 2026-05-30T06:27:35.810803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00289
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=809d23b377f65e00
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `4_1`
  and `tamagawa_product` of elliptic_curves `4928.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 809d23b377f65e00 emitted 2026-05-30T06:27:35.975800+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00290
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=64e89619cc95e710
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `10_161`
  and `tamagawa_product` of elliptic_curves `3931.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 64e89619cc95e710 emitted 2026-05-30T06:27:30.584988+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00291
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0439a389c6e579dd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_4`
  and `tamagawa_product` of elliptic_curves `8090.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0439a389c6e579dd emitted 2026-05-30T06:27:35.803803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00292
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8bd5014114650db9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `3_1` and
  `torsion` of elliptic_curves `891.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8bd5014114650db9 emitted 2026-05-30T06:27:36.029799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00293
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=37d10b252a59b24c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_2` and
  `rank` of elliptic_curves `2373.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 37d10b252a59b24c emitted 2026-05-30T06:27:36.007800+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00294
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5ebaba52797342c0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `4_1` and
  `torsion` of elliptic_curves `8528.h4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5ebaba52797342c0 emitted 2026-05-30T06:27:33.785653+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00295
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5bfe09f36c324788
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_124`
  and `torsion` of elliptic_curves `5808.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5bfe09f36c324788 emitted 2026-05-30T06:27:36.010799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00296
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=786fad9bda513bab
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_161`
  and `torsion` of elliptic_curves `9400.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 786fad9bda513bab emitted 2026-05-30T06:27:35.961801+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00297
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8c8f3fcf6b602937
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_3`
  and `tamagawa_product` of elliptic_curves `2170.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c8f3fcf6b602937 emitted 2026-05-30T06:27:35.794803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00298
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c0d0674845393b5c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `4_1`
  and `tamagawa_product` of elliptic_curves `6954.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c0d0674845393b5c emitted 2026-05-30T06:27:35.719804+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00299
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=535e6af8c0d1cdd5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_14` and
  `rank` of elliptic_curves `2988.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 535e6af8c0d1cdd5 emitted 2026-05-30T06:27:35.813803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00300
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b10e9561941b6413
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_3`
  and `rank` of elliptic_curves `366.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b10e9561941b6413 emitted 2026-05-30T06:27:35.596807+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00301
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6429559d24f53115
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_1`
  and `torsion` of elliptic_curves `9408.bb1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6429559d24f53115 emitted 2026-05-30T06:27:35.546808+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00302
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fa9e5918b4772fa1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_7` and
  `rank` of elliptic_curves `1806.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fa9e5918b4772fa1 emitted 2026-05-30T06:27:35.762804+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00303
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=80d59353b6ffa55b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_1`
  and `torsion` of elliptic_curves `2640.r4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 80d59353b6ffa55b emitted 2026-05-30T06:27:35.734804+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00304
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a78206ec96fc0234
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `8_19`
  and `torsion` of elliptic_curves `9350.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a78206ec96fc0234 emitted 2026-05-30T06:27:35.945800+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00305
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d9861dc8426fc8cc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_165`
  and `rank` of elliptic_curves `4150.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d9861dc8426fc8cc emitted 2026-05-30T06:27:35.856803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00306
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=52aa6653e2cef80e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `5_2` and
  `torsion` of elliptic_curves `6840.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 52aa6653e2cef80e emitted 2026-05-30T06:27:33.769653+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00307
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ca22de44a60e5138
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_10`
  and `tamagawa_product` of elliptic_curves `7685.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ca22de44a60e5138 emitted 2026-05-30T06:27:35.881802+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00308
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=401260d3cc592c60
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_6` and
  `rank` of elliptic_curves `1206.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 401260d3cc592c60 emitted 2026-05-30T06:27:33.753652+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00309
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cc40c0175da6066e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_7` and
  `rank` of elliptic_curves `8838.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cc40c0175da6066e emitted 2026-05-30T06:27:33.735652+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00310
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4edc9e0f82fb1184
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `4_1`
  and `torsion` of elliptic_curves `7059.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4edc9e0f82fb1184 emitted 2026-05-30T06:27:33.924650+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00311
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e43f4dcc2f4dbc3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_7`
  and `torsion` of elliptic_curves `4800.cb1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e43f4dcc2f4dbc3e emitted 2026-05-30T06:27:33.778653+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00312
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d5615db0b75b735b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_4`
  and `tamagawa_product` of elliptic_curves `1428.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d5615db0b75b735b emitted 2026-05-30T06:27:35.683806+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00313
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e0f88e88926186ba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_5`
  and `rank` of elliptic_curves `6525.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e0f88e88926186ba emitted 2026-05-30T06:27:35.876802+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00314
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f3d0fc9dc04f535a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_4` and
  `torsion` of elliptic_curves `8883.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f3d0fc9dc04f535a emitted 2026-05-30T06:27:35.817802+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00315
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=38c49246d02af4a5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_14` and
  `torsion` of elliptic_curves `5950.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38c49246d02af4a5 emitted 2026-05-30T06:27:35.956800+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00316
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=33ec356df1702af8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_1`
  and `rank` of elliptic_curves `6050.bl1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 33ec356df1702af8 emitted 2026-05-30T06:27:35.697805+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00317
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=141ab3f8bd090cc8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_4`
  and `torsion` of elliptic_curves `9240.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 141ab3f8bd090cc8 emitted 2026-05-30T06:27:35.675806+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00318
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7ee32769029fe5d8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_4` and
  `torsion` of elliptic_curves `4650.br1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7ee32769029fe5d8 emitted 2026-05-30T06:27:35.848803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00319
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fc07c2073c1260e7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_6` and
  `torsion` of elliptic_curves `7434.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fc07c2073c1260e7 emitted 2026-05-30T06:27:35.828803+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00320
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8251da8e07df5e60
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_7`
  and `torsion` of elliptic_curves `258.g2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8251da8e07df5e60 emitted 2026-05-30T06:27:35.269813+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00321
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cdb7c873d2c6a2d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_18`
  and `tamagawa_product` of elliptic_curves `782.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cdb7c873d2c6a2d1 emitted 2026-05-30T06:27:35.400810+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00322
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=11a8f10915b4cd3c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `4_1` and
  `torsion` of elliptic_curves `2725.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 11a8f10915b4cd3c emitted 2026-05-30T06:27:31.279892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00323
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=01909a5d7cd8b893
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_7`
  and `torsion` of elliptic_curves `3870.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 01909a5d7cd8b893 emitted 2026-05-30T06:27:35.245813+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00324
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d0ede635be9294e5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_3` and
  `rank` of elliptic_curves `6650.bh2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d0ede635be9294e5 emitted 2026-05-30T06:27:35.434811+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00325
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=be4a4b162ba6d429
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_2` and
  `torsion` of elliptic_curves `7920.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be4a4b162ba6d429 emitted 2026-05-30T06:27:35.402811+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00326
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c00dc84137798376
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_4`
  and `torsion` of elliptic_curves `6850.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c00dc84137798376 emitted 2026-05-30T06:27:31.911387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00327
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ad5059c716755895
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_1`
  and `rank` of elliptic_curves `7565.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad5059c716755895 emitted 2026-05-30T06:27:35.416811+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00328
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f85c5f5f8a8acab4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_10` and
  `torsion` of elliptic_curves `7366.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f85c5f5f8a8acab4 emitted 2026-05-30T06:27:35.367811+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00329
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=208878aefe8e1bbc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_3`
  and `tamagawa_product` of elliptic_curves `6992.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 208878aefe8e1bbc emitted 2026-05-30T06:27:35.513809+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00330
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d5aea7489396dec9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_5`
  and `rank` of elliptic_curves `1674.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d5aea7489396dec9 emitted 2026-05-30T06:27:35.208814+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00331
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1794bdbb8c46d0bb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_139`
  and `rank` of elliptic_curves `3768.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1794bdbb8c46d0bb emitted 2026-05-30T06:27:35.278813+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00332
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ad16ff17f8751e0e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `6_2` and
  `rank` of elliptic_curves `5684.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad16ff17f8751e0e emitted 2026-05-30T06:27:35.144815+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00333
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=827b54505f957b01
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_1`
  and `tamagawa_product` of elliptic_curves `586.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 827b54505f957b01 emitted 2026-05-30T06:27:35.514810+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00334
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=59ba496a95947bc5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_15`
  and `tamagawa_product` of elliptic_curves `7744.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 59ba496a95947bc5 emitted 2026-05-30T06:27:35.223814+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00335
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=00543ff051e5c62d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_7` and
  `torsion` of elliptic_curves `6026.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 00543ff051e5c62d emitted 2026-05-30T06:27:35.535808+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00336
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ce90a2fe5282b098
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `6_2`
  and `torsion` of elliptic_curves `2730.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ce90a2fe5282b098 emitted 2026-05-30T06:27:35.359811+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00337
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6963c0bc7acead54
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_3` and
  `tamagawa_product` of elliptic_curves `3731.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6963c0bc7acead54 emitted 2026-05-30T06:27:35.320812+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00338
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8b2abdea4899ce43
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_3` and
  `torsion` of elliptic_curves `6909.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8b2abdea4899ce43 emitted 2026-05-30T06:27:31.902387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00339
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b3266299b0bde19c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_14`
  and `rank` of elliptic_curves `6585.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b3266299b0bde19c emitted 2026-05-30T06:27:35.341812+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00340
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=46e377a483024abb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_2`
  and `tamagawa_product` of elliptic_curves `5414.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 46e377a483024abb emitted 2026-05-30T06:27:31.697390+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00341
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=32c2df59c7c30b93
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `6_3` and
  `tamagawa_product` of elliptic_curves `4845.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 32c2df59c7c30b93 emitted 2026-05-30T06:27:31.677391+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00342
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6c58603f82b4a06d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_4`
  and `torsion` of elliptic_curves `4560.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6c58603f82b4a06d emitted 2026-05-30T06:27:33.497357+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00343
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=98e1aa4a5faad984
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_5`
  and `torsion` of elliptic_curves `3931.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 98e1aa4a5faad984 emitted 2026-05-30T06:27:31.907387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00344
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cb623400032f65f5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `4_1`
  and `torsion` of elliptic_curves `5684.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cb623400032f65f5 emitted 2026-05-30T06:27:35.153815+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00345
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=55072f01a89d730c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_14` and
  `rank` of elliptic_curves `913.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 55072f01a89d730c emitted 2026-05-30T06:27:35.327812+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00346
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c26b9c6adfada61c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_7`
  and `torsion` of elliptic_curves `1001.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c26b9c6adfada61c emitted 2026-05-30T06:27:35.282813+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00347
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=097c81a6255f7447
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `torsion` of elliptic_curves `9350.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 097c81a6255f7447 emitted 2026-05-30T06:27:35.361811+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00348
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=30b73de36f465be7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_145`
  and `torsion` of elliptic_curves `1960.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 30b73de36f465be7 emitted 2026-05-30T06:27:35.166819+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00349
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=04721cea22f54158
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_139`
  and `torsion` of elliptic_curves `7448.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 04721cea22f54158 emitted 2026-05-30T06:27:35.147815+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00350
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=df5b631db7575eed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `4_1`
  and `rank` of elliptic_curves `7315.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record df5b631db7575eed emitted 2026-05-30T06:27:35.289813+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00351
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a5c205e0ccb754e5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_2`
  and `tamagawa_product` of elliptic_curves `4770.z2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a5c205e0ccb754e5 emitted 2026-05-30T06:27:35.286813+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00352
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e2dfd330378793a5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_139`
  and `tamagawa_product` of elliptic_curves `637.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e2dfd330378793a5 emitted 2026-05-30T06:27:31.264892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00353
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d0499f292779f35e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `9_1` and
  `tamagawa_product` of elliptic_curves `5950.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d0499f292779f35e emitted 2026-05-30T06:27:31.070899+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00354
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8eecd3b856cea26a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_19`
  and `tamagawa_product` of elliptic_curves `7770.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8eecd3b856cea26a emitted 2026-05-30T06:27:31.315894+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00355
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1721d60ad98b6ff1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `7_2` and
  `tamagawa_product` of elliptic_curves `5800.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1721d60ad98b6ff1 emitted 2026-05-30T06:27:31.314891+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00356
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=836455e81031c8c5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_165`
  and `torsion` of elliptic_curves `4230.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 836455e81031c8c5 emitted 2026-05-30T06:27:31.266892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00357
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cc0a64ed474d7756
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_4`
  and `torsion` of elliptic_curves `6050.bl1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cc0a64ed474d7756 emitted 2026-05-30T06:27:31.249893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00358
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ce92be99105d08f8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_19`
  and `rank` of elliptic_curves `7920.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ce92be99105d08f8 emitted 2026-05-30T06:27:34.105648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00359
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ba667d2bf432ddf9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_8`
  and `tamagawa_product` of elliptic_curves `5115.c4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ba667d2bf432ddf9 emitted 2026-05-30T06:27:34.092648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00360
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=02278faca362d15f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_1`
  and `rank` of elliptic_curves `3330.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 02278faca362d15f emitted 2026-05-30T06:27:31.054899+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00361
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=dfc750df8d78527f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `6_1`
  and `torsion` of elliptic_curves `840.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dfc750df8d78527f emitted 2026-05-30T06:27:31.124897+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00362
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3db89aef7357816b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `10_124`
  and `tamagawa_product` of elliptic_curves `546.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3db89aef7357816b emitted 2026-05-30T06:27:31.094898+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00363
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=dd758970a5dc207a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_8` and
  `torsion` of elliptic_curves `486.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dd758970a5dc207a emitted 2026-05-30T06:27:31.028899+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00364
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b353ed6c08a5db41
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_15` and
  `rank` of elliptic_curves `9114.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b353ed6c08a5db41 emitted 2026-05-30T06:27:31.148893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00365
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=57fe98394417377f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_8` and
  `rank` of elliptic_curves `7371.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 57fe98394417377f emitted 2026-05-30T06:27:30.834982+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00366
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=bab2f5e0cfc2d7b6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_16`
  and `tamagawa_product` of elliptic_curves `4571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bab2f5e0cfc2d7b6 emitted 2026-05-30T06:27:34.267644+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00367
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=29ed618e795cf951
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_2`
  and `rank` of elliptic_curves `240.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 29ed618e795cf951 emitted 2026-05-30T06:27:31.139894+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00368
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=37909ac7c681e40a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_16`
  and `tamagawa_product` of elliptic_curves `2346.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 37909ac7c681e40a emitted 2026-05-30T06:27:34.063649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00369
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=db1454da48d5954e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_1`
  and `rank` of elliptic_curves `782.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record db1454da48d5954e emitted 2026-05-30T06:27:31.360890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00370
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9c32b440cc1b0a98
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_3`
  and `tamagawa_product` of elliptic_curves `1379.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9c32b440cc1b0a98 emitted 2026-05-30T06:27:34.091649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00371
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8ccc930957baa6a3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `6_1` and
  `torsion` of elliptic_curves `5190.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ccc930957baa6a3 emitted 2026-05-30T06:27:34.078649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00372
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=20b7a5b22d14efd0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_5` and
  `rank` of elliptic_curves `4565.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 20b7a5b22d14efd0 emitted 2026-05-30T06:27:34.071646+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00373
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8c566c493a8b812b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_6`
  and `tamagawa_product` of elliptic_curves `5400.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c566c493a8b812b emitted 2026-05-30T06:27:34.059649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00374
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=70e130adcb863ef9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `9_1`
  and `torsion` of elliptic_curves `3339.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 70e130adcb863ef9 emitted 2026-05-30T06:27:34.289645+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00375
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5d8da8064f76fc5d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_6`
  and `torsion` of elliptic_curves `5208.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5d8da8064f76fc5d emitted 2026-05-30T06:27:34.095649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00376
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6e9ef975751e4f32
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_3`
  and `torsion` of elliptic_curves `6570.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6e9ef975751e4f32 emitted 2026-05-30T06:27:31.345890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00377
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b9d689247072f769
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_3` and
  `tamagawa_product` of elliptic_curves `6256.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b9d689247072f769 emitted 2026-05-30T06:27:33.940649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00378
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3cc8539977d57126
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_3` and
  `rank` of elliptic_curves `9870.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3cc8539977d57126 emitted 2026-05-30T06:27:33.940649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00379
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e6009d2bf0c7ffff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_2` and
  `rank` of elliptic_curves `2730.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e6009d2bf0c7ffff emitted 2026-05-30T06:27:31.327890+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00380
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8c075aa43d12d072
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_4`
  and `tamagawa_product` of elliptic_curves `9990.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c075aa43d12d072 emitted 2026-05-30T06:27:34.007650+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00381
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=be1664bc3b44a0ef
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_2`
  and `torsion` of elliptic_curves `558.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be1664bc3b44a0ef emitted 2026-05-30T06:27:30.938979+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00382
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4de14ea7a999a1be
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_21`
  and `rank` of elliptic_curves `8280.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4de14ea7a999a1be emitted 2026-05-30T06:27:34.295645+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00383
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=be8f189a21b19194
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_1` and
  `tamagawa_product` of elliptic_curves `528.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be8f189a21b19194 emitted 2026-05-30T06:27:33.957651+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00384
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ad46fc1604a0a385
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_13` and
  `torsion` of elliptic_curves `7998.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad46fc1604a0a385 emitted 2026-05-30T06:27:34.730633+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00385
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=10c8d7b3d95aeb5c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_18`
  and `tamagawa_product` of elliptic_curves `4112.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 10c8d7b3d95aeb5c emitted 2026-05-30T06:27:34.886631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00386
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3089540b24ebdad2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_5` and
  `torsion` of elliptic_curves `1734.j4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3089540b24ebdad2 emitted 2026-05-30T06:27:32.044389+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00387
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c64da89e42c18b89
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `8_19`
  and `tamagawa_product` of elliptic_curves `2656.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c64da89e42c18b89 emitted 2026-05-30T06:27:34.724634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00388
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5dbb4bceedd0713d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_6`
  and `torsion` of elliptic_curves `3570.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5dbb4bceedd0713d emitted 2026-05-30T06:27:34.940629+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00389
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3f64e753af82fc12
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_21`
  and `torsion` of elliptic_curves `4768.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f64e753af82fc12 emitted 2026-05-30T06:27:34.888630+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00390
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ef6dc559780dfa38
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_2`
  and `torsion` of elliptic_curves `2568.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ef6dc559780dfa38 emitted 2026-05-30T06:27:33.363359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00391
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d6880c8e83dc9548
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_7` and
  `torsion` of elliptic_curves `222.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d6880c8e83dc9548 emitted 2026-05-30T06:27:34.890630+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00392
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b99a73cfd1837cb9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_19`
  and `rank` of elliptic_curves `4774.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b99a73cfd1837cb9 emitted 2026-05-30T06:27:34.868631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00393
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1265968647587f4c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_10`
  and `tamagawa_product` of elliptic_curves `4576.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1265968647587f4c emitted 2026-05-30T06:27:34.944629+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00394
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=91962c5d3cbe8c2b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_7` and
  `torsion` of elliptic_curves `8838.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 91962c5d3cbe8c2b emitted 2026-05-30T06:27:34.682635+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00395
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=70a2c176225ca9d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_20`
  and `tamagawa_product` of elliptic_curves `7308.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 70a2c176225ca9d1 emitted 2026-05-30T06:27:34.751633+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00396
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5f8a6f23689106ef
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_8`
  and `rank` of elliptic_curves `2830.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5f8a6f23689106ef emitted 2026-05-30T06:27:34.182647+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00397
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0658144aa983d65c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_161`
  and `torsion` of elliptic_curves `1495.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0658144aa983d65c emitted 2026-05-30T06:27:34.948629+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00398
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d51d9732fe1392dd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_17`
  and `tamagawa_product` of elliptic_curves `7448.p1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d51d9732fe1392dd emitted 2026-05-30T06:27:34.687634+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00399
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a209e82591c2b9ac
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_7`
  and `torsion` of elliptic_curves `9600.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a209e82591c2b9ac emitted 2026-05-30T06:27:34.962628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00400
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ce123c0e285d0e19
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_4`
  and `tamagawa_product` of elliptic_curves `2724.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ce123c0e285d0e19 emitted 2026-05-30T06:27:34.840631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00401
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=439b041c9ba09113
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `6_1`
  and `torsion` of elliptic_curves `5304.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 439b041c9ba09113 emitted 2026-05-30T06:27:34.814631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00402
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0dfeda467342b5a2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_11`
  and `rank` of elliptic_curves `7488.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0dfeda467342b5a2 emitted 2026-05-30T06:27:33.351360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00403
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2fe93eb7d33d2de5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `3_1` and
  `rank` of elliptic_curves `8040.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2fe93eb7d33d2de5 emitted 2026-05-30T06:27:34.834631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00404
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e8b28f067bc89e84
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_11`
  and `tamagawa_product` of elliptic_curves `9009.k2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e8b28f067bc89e84 emitted 2026-05-30T06:27:33.282362+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00405
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7233b70018807947
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_5` and
  `torsion` of elliptic_curves `2808.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7233b70018807947 emitted 2026-05-30T06:27:33.242363+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00406
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=16b6a9a552f8027a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_139`
  and `torsion` of elliptic_curves `2079.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 16b6a9a552f8027a emitted 2026-05-30T06:27:33.373359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00407
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=817f3b7de9f0c012
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_11`
  and `tamagawa_product` of elliptic_curves `5236.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 817f3b7de9f0c012 emitted 2026-05-30T06:27:33.362359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00408
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3f9edf9c92bd2af5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_8` and
  `rank` of elliptic_curves `5954.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f9edf9c92bd2af5 emitted 2026-05-30T06:27:34.208647+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00409
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c32243af92ffc34e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_14` and
  `torsion` of elliptic_curves `9480.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c32243af92ffc34e emitted 2026-05-30T06:27:34.826631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00410
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d8b5ba4c4930523d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_21`
  and `tamagawa_product` of elliptic_curves `3325.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d8b5ba4c4930523d emitted 2026-05-30T06:27:34.757633+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00411
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=37f83b9c01888591
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `6_1` and
  `torsion` of elliptic_curves `7488.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 37f83b9c01888591 emitted 2026-05-30T06:27:34.843631+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00412
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=bf62ea6ad0c40990
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_18`
  and `torsion` of elliptic_curves `7460.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bf62ea6ad0c40990 emitted 2026-05-30T06:27:34.222646+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00413
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8879276ffc6340ff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_10` and
  `rank` of elliptic_curves `4518.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8879276ffc6340ff emitted 2026-05-30T06:27:34.197647+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00414
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1b2182a9275a0a9c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_2` and
  `rank` of elliptic_curves `6240.x3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1b2182a9275a0a9c emitted 2026-05-30T06:27:34.765633+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00415
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=652099f3b5115edf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `5_2` and
  `torsion` of elliptic_curves `2646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 652099f3b5115edf emitted 2026-05-30T06:27:34.763632+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00416
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=088146a1a0d3dc15
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_3`
  and `torsion` of elliptic_curves `2274.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 088146a1a0d3dc15 emitted 2026-05-30T06:27:31.964385+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00417
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2274b52e553e3c03
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_19`
  and `rank` of elliptic_curves `7410.t2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2274b52e553e3c03 emitted 2026-05-30T06:27:30.032997+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00418
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8ba90ddc6660e40f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_21` and
  `rank` of elliptic_curves `1113.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ba90ddc6660e40f emitted 2026-05-30T06:27:32.112893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00419
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=894f03a5bda58679
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_5` and
  `rank` of elliptic_curves `9864.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 894f03a5bda58679 emitted 2026-05-30T06:27:32.101893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00420
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e8c750a4e3783cee
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_10`
  and `rank` of elliptic_curves `7725.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e8c750a4e3783cee emitted 2026-05-30T06:27:31.971385+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00421
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=b96c4f4b5a196a36
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_4` and
  `tamagawa_product` of elliptic_curves `1494.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b96c4f4b5a196a36 emitted 2026-05-30T06:27:31.961387+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00422
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=bfed1aefbbfeb2d9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_7`
  and `torsion` of elliptic_curves `4950.w2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bfed1aefbbfeb2d9 emitted 2026-05-30T06:27:33.642355+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00423
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e27f54b26662fc8c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_10`
  and `tamagawa_product` of elliptic_curves `1379.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e27f54b26662fc8c emitted 2026-05-30T06:27:33.571356+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00424
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d5c9eaec948e051b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_6`
  and `tamagawa_product` of elliptic_curves `8028.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d5c9eaec948e051b emitted 2026-05-30T06:27:36.412790+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00425
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f88ee97c618a39de
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_9` and
  `tamagawa_product` of elliptic_curves `5800.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f88ee97c618a39de emitted 2026-05-30T06:27:30.119996+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00426
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8a58484184a11563
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `3_1` and
  `rank` of elliptic_curves `1056.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8a58484184a11563 emitted 2026-05-30T06:27:30.100996+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00427
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=bfe0c4335172a4d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_11` and
  `torsion` of elliptic_curves `2352.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bfe0c4335172a4d1 emitted 2026-05-30T06:27:30.017997+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00428
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f2218aa38c1cf509
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_2`
  and `rank` of elliptic_curves `2358.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f2218aa38c1cf509 emitted 2026-05-30T06:27:36.449951+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00429
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=db5422af6226a820
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_5`
  and `torsion` of elliptic_curves `3600.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record db5422af6226a820 emitted 2026-05-30T06:27:36.398791+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00430
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ad32dfc46a150644
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_3` and
  `torsion` of elliptic_curves `5808.b4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ad32dfc46a150644 emitted 2026-05-30T06:27:33.645354+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00431
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6c92660cd8d025e7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_3`
  and `tamagawa_product` of elliptic_curves `8766.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6c92660cd8d025e7 emitted 2026-05-30T06:27:30.206994+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00432
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a8ad5e45cd759a49
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `5_2` and
  `rank` of elliptic_curves `7840.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8ad5e45cd759a49 emitted 2026-05-30T06:27:33.475357+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00433
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=06616680a5b1135f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_8` and
  `rank` of elliptic_curves `9600.br2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 06616680a5b1135f emitted 2026-05-30T06:27:32.150893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00434
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=37fa1edeb3f26dce
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_3`
  and `rank` of elliptic_curves `3312.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 37fa1edeb3f26dce emitted 2026-05-30T06:27:33.543356+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00435
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=572690fc9be4288b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_13`
  and `torsion` of elliptic_curves `7872.s2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 572690fc9be4288b emitted 2026-05-30T06:27:33.489357+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00436
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f093ac688d1e4ee8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_11` and
  `torsion` of elliptic_curves `2934.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f093ac688d1e4ee8 emitted 2026-05-30T06:27:33.484411+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00437
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d7504b5683457c21
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_6` and
  `rank` of elliptic_curves `3114.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d7504b5683457c21 emitted 2026-05-30T06:27:33.473357+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00438
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d1f30f458f04d66c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `10_3`
  and `tamagawa_product` of elliptic_curves `4774.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d1f30f458f04d66c emitted 2026-05-30T06:27:33.666354+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00439
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d637356c0ff920a6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_2` and
  `rank` of elliptic_curves `6198.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d637356c0ff920a6 emitted 2026-05-30T06:27:33.585355+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00440
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=94557cc8fd53c473
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_1` and
  `rank` of elliptic_curves `7315.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 94557cc8fd53c473 emitted 2026-05-30T06:27:32.125893+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00441
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=18e9bbf6b6874405
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_3`
  and `rank` of elliptic_curves `5712.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 18e9bbf6b6874405 emitted 2026-05-30T06:27:33.436358+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00442
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=19ee13a2ca178753
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_1`
  and `torsion` of elliptic_curves `966.i2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 19ee13a2ca178753 emitted 2026-05-30T06:27:33.431358+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00443
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2400a1e49328552f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_20` and
  `torsion` of elliptic_curves `7469.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2400a1e49328552f emitted 2026-05-30T06:27:32.118892+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00444
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4b7f8f59bdce6d00
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `6_2`
  and `rank` of elliptic_curves `9796.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4b7f8f59bdce6d00 emitted 2026-05-30T06:27:33.456358+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00445
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=189a619b3097136e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_5`
  and `rank` of elliptic_curves `4480.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 189a619b3097136e emitted 2026-05-30T06:27:29.953998+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00446
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c03568d86c6ee4a0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `7_2` and
  `tamagawa_product` of elliptic_curves `9062.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c03568d86c6ee4a0 emitted 2026-05-30T06:27:33.675354+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00447
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c8a2a61637a2253b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_12`
  and `torsion` of elliptic_curves `9108.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c8a2a61637a2253b emitted 2026-05-30T06:27:33.447359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00448
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cc8af97000875f91
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_139`
  and `tamagawa_product` of elliptic_curves `7482.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cc8af97000875f91 emitted 2026-05-30T06:27:34.106649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00449
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e344c43f0fa0c5e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_12` and
  `torsion` of elliptic_curves `6175.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e344c43f0fa0c5e3 emitted 2026-05-30T06:27:35.010628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00450
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=9978dd6285ca8cf2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_6` and
  `torsion` of elliptic_curves `5376.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9978dd6285ca8cf2 emitted 2026-05-30T06:27:32.702863+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00451
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=92de0e27fce4c0a4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_3`
  and `tamagawa_product` of elliptic_curves `9864.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 92de0e27fce4c0a4 emitted 2026-05-30T06:27:33.900651+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00452
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=48b0461953b093c8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_3`
  and `tamagawa_product` of elliptic_curves `6570.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 48b0461953b093c8 emitted 2026-05-30T06:27:35.036628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00453
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=593d7c990d9b3ca4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `4_1` and
  `torsion` of elliptic_curves `8800.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 593d7c990d9b3ca4 emitted 2026-05-30T06:27:35.016628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00454
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3bf965ea926eb753
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `nf_class_number` of knots `4_1`
  and `tamagawa_product` of elliptic_curves `9062.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3bf965ea926eb753 emitted 2026-05-30T06:27:33.024857+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00455
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5a2011d8c8b85b33
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `rank` of elliptic_curves `8925.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5a2011d8c8b85b33 emitted 2026-05-30T06:27:35.028627+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00456
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3f8cda308f0f269d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_13`
  and `torsion` of elliptic_curves `8175.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f8cda308f0f269d emitted 2026-05-30T06:27:34.985628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00457
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=cd2f31109a56746c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `4_1` and
  `rank` of elliptic_curves `3857.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cd2f31109a56746c emitted 2026-05-30T06:27:35.047627+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00458
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=e7d564e0e9a2bbec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_3`
  and `torsion` of elliptic_curves `336.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e7d564e0e9a2bbec emitted 2026-05-30T06:27:33.831651+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00459
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fcf2ba28d32a1c0f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `9_10`
  and `tamagawa_product` of elliptic_curves `9196.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fcf2ba28d32a1c0f emitted 2026-05-30T06:27:34.111649+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00460
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5f05aaa97e425f75
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `determinant` of knots `3_1` and
  `rank` of elliptic_curves `9850.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5f05aaa97e425f75 emitted 2026-05-30T06:27:36.386792+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00461
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=1ad78917d846b2ae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_7` and
  `rank` of elliptic_curves `345.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1ad78917d846b2ae emitted 2026-05-30T06:27:36.035799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00462
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8e73554a5b302d11
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_3` and
  `torsion` of elliptic_curves `2304.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8e73554a5b302d11 emitted 2026-05-30T06:27:33.839651+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00463
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=34d747ca0cf69acf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_3` and
  `torsion` of elliptic_curves `9240.x4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 34d747ca0cf69acf emitted 2026-05-30T06:27:36.041799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00464
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=81b1f94ee1feec44
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_4`
  and `rank` of elliptic_curves `9600.br2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 81b1f94ee1feec44 emitted 2026-05-30T06:27:34.970628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00465
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c91b0ad189d6b192
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_8`
  and `torsion` of elliptic_curves `1434.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c91b0ad189d6b192 emitted 2026-05-30T06:27:34.129648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00466
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=030f492e2c676b39
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_9` and
  `torsion` of elliptic_curves `6290.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 030f492e2c676b39 emitted 2026-05-30T06:27:32.989858+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00467
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=d5443cf11ee42acf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_1` and
  `torsion` of elliptic_curves `3392.k2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d5443cf11ee42acf emitted 2026-05-30T06:27:34.138648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00468
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=88346d743576ff22
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_3` and
  `tamagawa_product` of elliptic_curves `5235.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 88346d743576ff22 emitted 2026-05-30T06:27:32.963858+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00469
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=39a6a45f6443178a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_21`
  and `rank` of elliptic_curves `8640.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 39a6a45f6443178a emitted 2026-05-30T06:27:32.929859+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00470
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2f2adeb3eef3d325
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `6_1`
  and `rank` of elliptic_curves `8106.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2f2adeb3eef3d325 emitted 2026-05-30T06:27:33.036857+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00471
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7a577ef0caf9b13a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_16`
  and `rank` of elliptic_curves `4774.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7a577ef0caf9b13a emitted 2026-05-30T06:27:33.022858+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00472
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ef41a177baa8571a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `3_1`
  and `torsion` of elliptic_curves `3186.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ef41a177baa8571a emitted 2026-05-30T06:27:33.427359+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00473
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6b53fd6d4183a064
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_13` and
  `tamagawa_product` of elliptic_curves `5748.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6b53fd6d4183a064 emitted 2026-05-30T06:27:34.135647+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00474
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8843b60cfb0eff36
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_13`
  and `tamagawa_product` of elliptic_curves `2646.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8843b60cfb0eff36 emitted 2026-05-30T06:27:34.116648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00475
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=f6679b6bdbd0f1ec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `6_3` and
  `torsion` of elliptic_curves `2352.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f6679b6bdbd0f1ec emitted 2026-05-30T06:27:34.973628+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00476
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3f1c834b3df663b6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `8_12`
  and `tamagawa_product` of elliptic_curves `8800.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f1c834b3df663b6 emitted 2026-05-30T06:27:33.821652+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00477
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c39b9ecb61c3a132
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_12`
  and `torsion` of elliptic_curves `8827.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c39b9ecb61c3a132 emitted 2026-05-30T06:27:33.425358+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00478
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=fcb808572e76b771
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_9` and
  `rank` of elliptic_curves `3885.c5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fcb808572e76b771 emitted 2026-05-30T06:27:34.128648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00479
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=78891f2eb8b21afd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `10_145`
  and `torsion` of elliptic_curves `158.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 78891f2eb8b21afd emitted 2026-05-30T06:27:34.127648+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00480
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=8def852cd73963bb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_17` and
  `tamagawa_product` of elliptic_curves `3822.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8def852cd73963bb emitted 2026-05-30T06:27:36.150799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00481
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7e0b85b5cb11307d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `4_1`
  and `rank` of elliptic_curves `3262.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7e0b85b5cb11307d emitted 2026-05-30T06:27:36.134798+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00482
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=13645fe20c3465a5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_2` and
  `rank` of elliptic_curves `6965.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 13645fe20c3465a5 emitted 2026-05-30T06:27:33.134364+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00483
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a543d0a16d27c3b3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_6`
  and `tamagawa_product` of elliptic_curves `6402.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a543d0a16d27c3b3 emitted 2026-05-30T06:27:36.164797+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00484
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4999d88d31be3ac9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_2`
  and `torsion` of elliptic_curves `1216.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4999d88d31be3ac9 emitted 2026-05-30T06:27:33.044860+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00485
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=4deff41a003b9961
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_2`
  and `torsion` of elliptic_curves `3300.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4deff41a003b9961 emitted 2026-05-30T06:27:32.781862+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00486
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=24370402d539535d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_5` and
  `torsion` of elliptic_curves `7520.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 24370402d539535d emitted 2026-05-30T06:27:36.364791+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00487
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3a329a27a8049c8b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_2` and
  `rank` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a329a27a8049c8b emitted 2026-05-30T06:27:32.849861+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00488
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=330cdec3f7ada0af
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `9_6` and
  `tamagawa_product` of elliptic_curves `9210.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 330cdec3f7ada0af emitted 2026-05-30T06:27:36.190798+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00489
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=7ee5e7ff70a9e5b7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `7_5`
  and `torsion` of elliptic_curves `862.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7ee5e7ff70a9e5b7 emitted 2026-05-30T06:27:36.146799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00490
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=2078611aabce30b7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_11`
  and `rank` of elliptic_curves `7130.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2078611aabce30b7 emitted 2026-05-30T06:27:36.112800+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00491
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=bf07966a340f73bb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `9_5`
  and `rank` of elliptic_curves `4770.u1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bf07966a340f73bb emitted 2026-05-30T06:27:36.198798+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00492
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a5e59cbc1815f57f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `7_4` and
  `torsion` of elliptic_curves `3186.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a5e59cbc1815f57f emitted 2026-05-30T06:27:36.105799+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00493
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=a8c7b451b5110552
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `9_7` and
  `rank` of elliptic_curves `5202.l2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8c7b451b5110552 emitted 2026-05-30T06:27:33.218363+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00494
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=3859b9035264aa35
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `signature` of knots `8_16` and
  `tamagawa_product` of elliptic_curves `3440.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3859b9035264aa35 emitted 2026-05-30T06:27:33.287361+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00495
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=c8b415ef807e3561
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_20`
  and `torsion` of elliptic_curves `7526.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c8b415ef807e3561 emitted 2026-05-30T06:27:33.395360+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00496
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=10e9729b9ae7492e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_4` and
  `torsion` of elliptic_curves `6984.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 10e9729b9ae7492e emitted 2026-05-30T06:27:36.250797+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00497
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=5e1d1867b5e40742
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `10_165`
  and `torsion` of elliptic_curves `3042.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5e1d1867b5e40742 emitted 2026-05-30T06:27:36.234797+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00498
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=0f5b4c77fab0a2ca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `crossing_number` of knots `7_5`
  and `tamagawa_product` of elliptic_curves `1865.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0f5b4c77fab0a2ca emitted 2026-05-30T06:27:36.231797+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00499
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=ff4fd2ecc1d09a2f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `three_genus` of knots `8_12`
  and `torsion` of elliptic_curves `6630.y1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff4fd2ecc1d09a2f emitted 2026-05-30T06:27:36.252797+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00500
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=d2; batch=batch-20260530T060336Z-4396ba;
  record_id=6ea4819fb40ff144
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d2 emission; relation=?;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `?` hold between `trace_field_class` of knots `8_15`
  and `torsion` of elliptic_curves `5390.x2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6ea4819fb40ff144 emitted 2026-05-30T06:27:36.225797+00:00
source_date: '2026-05-30'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `?`. Training weight:
  0.500. Per Fire #22, divides-on-zero was a known bug fixed; this anchor was emitted
  on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

