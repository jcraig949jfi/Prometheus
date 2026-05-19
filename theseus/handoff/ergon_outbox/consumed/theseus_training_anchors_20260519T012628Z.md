# Theseus → Ergon Training Anchor Handoff

Generated: 2026-05-19T01:26:28.159655+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=712439aa49c32375
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `conductor` of elliptic_curves `1716.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 712439aa49c32375 emitted 2026-05-18T19:51:07.097109+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=c94799a9a08e2ac6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_4` and `tamagawa_product` of elliptic_curves `4571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c94799a9a08e2ac6 emitted 2026-05-18T19:51:07.126212+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=c1d71d9f1cc8206e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_11` and `torsion` of elliptic_curves `3520.o2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c1d71d9f1cc8206e emitted 2026-05-18T19:51:07.167348+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=805104d35a7dbbbe
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_13` and `torsion` of elliptic_curves `4032.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 805104d35a7dbbbe emitted 2026-05-18T19:51:07.182347+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=725bd273da4a5165
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_4` and `tamagawa_product` of elliptic_curves `3510.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 725bd273da4a5165 emitted 2026-05-18T19:51:07.291408+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7046775c43afa2a1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7046775c43afa2a1 emitted 2026-05-18T19:51:07.300408+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=476df49112b98f8b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_4` and `tamagawa_product` of elliptic_curves `4050.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 476df49112b98f8b emitted 2026-05-18T19:51:07.305408+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c3c0f9b406178e2a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `torsion` of elliptic_curves `1716.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c3c0f9b406178e2a emitted 2026-05-18T19:51:07.348452+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=22c7e06053b846c1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_14` and `rank` of elliptic_curves `6066.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 22c7e06053b846c1 emitted 2026-05-18T19:51:07.368451+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5cc3ee729711fcff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `torsion` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5cc3ee729711fcff emitted 2026-05-18T19:51:07.397451+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=f529fd61feb6fd10
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `tamagawa_product` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f529fd61feb6fd10 emitted 2026-05-18T19:51:07.419514+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=7d89eac5489ac3ad
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_5` and `torsion` of elliptic_curves `2275.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d89eac5489ac3ad emitted 2026-05-18T19:51:07.426514+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=15015952a56a1afb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_3` and `tamagawa_product` of elliptic_curves `840.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 15015952a56a1afb emitted 2026-05-18T19:51:07.470558+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=1931dc939bd2acff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `conductor` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1931dc939bd2acff emitted 2026-05-18T19:51:07.545675+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=efbe27d1870fdc4c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_2` and `tamagawa_product` of elliptic_curves `8265.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record efbe27d1870fdc4c emitted 2026-05-18T19:51:07.560765+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=ede7cc9c66aab551
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `conductor` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ede7cc9c66aab551 emitted 2026-05-18T19:51:07.581865+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=2d0a3393878f18b0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `rank` of elliptic_curves `5856.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2d0a3393878f18b0 emitted 2026-05-18T19:51:07.662221+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=692629e98efd264c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_8` and `rank` of elliptic_curves `4571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 692629e98efd264c emitted 2026-05-18T19:51:07.683303+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=28a972347e31284e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_6` and `torsion` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 28a972347e31284e emitted 2026-05-18T19:51:07.684304+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=bd034097162f8eea
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_10` and `rank` of elliptic_curves `5990.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bd034097162f8eea emitted 2026-05-18T19:51:07.690306+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=ff3a6699d454993b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_11` and `tamagawa_product` of elliptic_curves `3520.o2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff3a6699d454993b emitted 2026-05-18T19:51:07.713303+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=ff064b7a52d37a1f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff064b7a52d37a1f emitted 2026-05-18T19:51:07.810421+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=052178f0650554b6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `rank` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 052178f0650554b6 emitted 2026-05-18T19:51:07.815423+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=4705700a72086686
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_10` and `rank` of elliptic_curves `5856.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4705700a72086686 emitted 2026-05-18T19:51:07.920522+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=496848f4ae5ce347
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `6_1` and `torsion` of elliptic_curves `2112.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 496848f4ae5ce347 emitted 2026-05-18T19:51:07.926522+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=31e4e5ad7880ad35
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 31e4e5ad7880ad35 emitted 2026-05-18T19:51:07.957630+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=805115e352d3f933
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_8` and `rank` of elliptic_curves `7982.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 805115e352d3f933 emitted 2026-05-18T19:51:07.999813+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c619d68aef0439ca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `conductor` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c619d68aef0439ca emitted 2026-05-18T19:51:08.008879+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=ebb0e0096c96d4e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `tamagawa_product` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ebb0e0096c96d4e3 emitted 2026-05-18T19:51:08.112284+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=daa5da526da1bbfd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_10` and `rank` of elliptic_curves `9574.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record daa5da526da1bbfd emitted 2026-05-18T19:51:08.126285+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=c4c73cfc4ee5dce2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_11` and `conductor` of elliptic_curves `7378.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c4c73cfc4ee5dce2 emitted 2026-05-18T19:51:08.219423+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=7a690b560a906ff6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_8` and `rank` of elliptic_curves `3630.a3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7a690b560a906ff6 emitted 2026-05-18T19:51:08.233423+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7fce6ed97220a72a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7fce6ed97220a72a emitted 2026-05-18T19:51:08.235423+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=a138330d86976ce5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `rank` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a138330d86976ce5 emitted 2026-05-18T19:51:08.299439+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=885efe8971fb909e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 885efe8971fb909e emitted 2026-05-18T19:51:08.392551+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=68f3fd9c6bd1b3e4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `torsion` of elliptic_curves `4655.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 68f3fd9c6bd1b3e4 emitted 2026-05-18T19:51:08.404551+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=fd53b989866db2d9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_1` and `conductor` of elliptic_curves `2100.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fd53b989866db2d9 emitted 2026-05-18T19:51:08.603011+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=efa4b7257c80fae3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_10` and `torsion` of elliptic_curves `4655.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record efa4b7257c80fae3 emitted 2026-05-18T19:51:08.611057+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2d559ba8feca079c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_13` and `torsion` of elliptic_curves `4032.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2d559ba8feca079c emitted 2026-05-18T19:51:08.679252+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=265c851bb93876cf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_161` and `conductor` of elliptic_curves `6480.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 265c851bb93876cf emitted 2026-05-18T19:51:08.701251+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=8a000a907fcdd4f8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8a000a907fcdd4f8 emitted 2026-05-18T19:51:08.703252+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=0a844133c43d8b35
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_13` and `torsion` of elliptic_curves `8946.h4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0a844133c43d8b35 emitted 2026-05-18T19:51:08.752305+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=369f9f0eb8eb74e6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_19` and `rank` of elliptic_curves `7810.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 369f9f0eb8eb74e6 emitted 2026-05-18T19:51:08.815359+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4c746f7b332da76e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_9` and `rank` of elliptic_curves `3648.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4c746f7b332da76e emitted 2026-05-18T19:51:08.820360+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=65fabb755c3ec154
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_13` and `tamagawa_product` of elliptic_curves `7776.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 65fabb755c3ec154 emitted 2026-05-18T19:51:08.955358+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=db670e3f3b24289b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_11` and `rank` of elliptic_curves `3417.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record db670e3f3b24289b emitted 2026-05-18T19:51:08.956358+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e454bb347993f68e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_3` and `torsion` of elliptic_curves `1176.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e454bb347993f68e emitted 2026-05-18T19:51:08.998414+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=3f0704b9abbe8a4f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_20` and `conductor` of elliptic_curves `5187.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3f0704b9abbe8a4f emitted 2026-05-18T19:51:08.999414+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=95a41753accb8593
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_9` and `conductor` of elliptic_curves `3216.l2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 95a41753accb8593 emitted 2026-05-18T19:51:09.070458+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=35eb3681252ceddf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `torsion` of elliptic_curves `9768.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 35eb3681252ceddf emitted 2026-05-18T19:51:09.084458+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4d1771a4debaf6d7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `3_1` and `rank` of elliptic_curves `5808.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4d1771a4debaf6d7 emitted 2026-05-18T19:51:09.100503+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7e45ba0f0cc0c0f8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7e45ba0f0cc0c0f8 emitted 2026-05-18T19:51:09.236029+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=f3c476a9ee12a9e0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `rank` of elliptic_curves `6006.t3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f3c476a9ee12a9e0 emitted 2026-05-18T19:51:09.366343+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=a3fd19aae7764883
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `torsion` of elliptic_curves `8904.i3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a3fd19aae7764883 emitted 2026-05-18T19:51:09.380343+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=01308158a28e1cbd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 01308158a28e1cbd emitted 2026-05-18T19:51:09.383343+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=d1; batch=batch-20260518T195105Z-43a075;
  record_id=7833a0bdd1b11708
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `{knot}` and `rank` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7833a0bdd1b11708 emitted 2026-05-18T19:51:09.411400+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=480e6c92c86371ef
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_12` and `torsion` of elliptic_curves `4560.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 480e6c92c86371ef emitted 2026-05-18T19:51:09.476482+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=21ce81a5494d8b28
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 21ce81a5494d8b28 emitted 2026-05-18T19:51:09.479480+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=fb9adcd617b03057
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `5_2` and `rank` of elliptic_curves `8090.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fb9adcd617b03057 emitted 2026-05-18T19:51:09.548482+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=90bb5c1e366d9716
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_1` and `rank` of elliptic_curves `2160.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 90bb5c1e366d9716 emitted 2026-05-18T19:51:09.602526+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=83f667938961ec79
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 83f667938961ec79 emitted 2026-05-18T19:51:09.604526+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=5f1a26c561f09535
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `tamagawa_product` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5f1a26c561f09535 emitted 2026-05-18T19:51:09.610526+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f3d15318835f107b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `conductor` of elliptic_curves `6480.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f3d15318835f107b emitted 2026-05-18T19:51:09.639627+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=d628be50fab3076a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_4` and `rank` of elliptic_curves `3417.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d628be50fab3076a emitted 2026-05-18T19:51:09.652675+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=48cd355e6e414239
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_5` and `rank` of elliptic_curves `9070.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 48cd355e6e414239 emitted 2026-05-18T19:51:09.717012+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=3b7929164eaf4ad4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3b7929164eaf4ad4 emitted 2026-05-18T19:51:09.747173+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=d463fd8da3735753
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_12` and `rank` of elliptic_curves `3360.q3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d463fd8da3735753 emitted 2026-05-18T19:51:09.831328+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=22b1ab45bf141d3a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `conductor` of elliptic_curves `5208.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 22b1ab45bf141d3a emitted 2026-05-18T19:51:09.868327+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=a7b629ad19e04759
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_14` and `torsion` of elliptic_curves `2275.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a7b629ad19e04759 emitted 2026-05-18T19:51:10.103365+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=be8e1eebbc975775
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_4` and `conductor` of elliptic_curves `6104.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be8e1eebbc975775 emitted 2026-05-18T19:51:10.112365+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=5efa8e42544f782a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_2` and `torsion` of elliptic_curves `6195.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5efa8e42544f782a emitted 2026-05-18T19:51:10.266485+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=3452005d47c5e16c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_15` and `conductor` of elliptic_curves `1960.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3452005d47c5e16c emitted 2026-05-18T19:51:10.450178+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=4dfea617e07a35e5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_15` and `tamagawa_product` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4dfea617e07a35e5 emitted 2026-05-18T19:51:10.463392+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=a58919446c7d3ef1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `3_1` and `rank` of elliptic_curves `7810.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a58919446c7d3ef1 emitted 2026-05-18T19:51:10.607446+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=cefebfce77776f4c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_7` and `tamagawa_product` of elliptic_curves `3520.y2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cefebfce77776f4c emitted 2026-05-18T19:51:10.642443+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=8b57ea29196cfd0f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8b57ea29196cfd0f emitted 2026-05-18T19:51:10.672443+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=7d58de8dfad939c5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_7` and `rank` of elliptic_curves `7312.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7d58de8dfad939c5 emitted 2026-05-18T19:51:10.713442+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=6af7d3a1d64294a3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6af7d3a1d64294a3 emitted 2026-05-18T19:51:10.715442+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=a8b05cb3abbc1af1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_11` and `torsion` of elliptic_curves `9070.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8b05cb3abbc1af1 emitted 2026-05-18T19:51:10.761441+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=31056e74fc071a10
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_1` and `torsion` of elliptic_curves `3200.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 31056e74fc071a10 emitted 2026-05-18T19:51:10.901679+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=446a241f49f21db8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_18` and `conductor` of elliptic_curves `1876.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 446a241f49f21db8 emitted 2026-05-18T19:51:10.983044+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=754c3878760ef667
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 754c3878760ef667 emitted 2026-05-18T19:51:11.040243+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=4d8abda96d86bff6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_1` and `conductor` of elliptic_curves `8090.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4d8abda96d86bff6 emitted 2026-05-18T19:51:11.052243+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=2b597481bf5ec00f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_3` and `torsion` of elliptic_curves `3933.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2b597481bf5ec00f emitted 2026-05-18T19:51:11.152291+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2d683ca99a95891f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_13` and `rank` of elliptic_curves `7776.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2d683ca99a95891f emitted 2026-05-18T19:51:11.207009+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=e867bb6ecb92f33e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_2` and `rank` of elliptic_curves `3504.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e867bb6ecb92f33e emitted 2026-05-18T19:51:11.255205+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=96c5c3d74bc4d0da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_2` and `rank` of elliptic_curves `7920.g3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 96c5c3d74bc4d0da emitted 2026-05-18T19:51:11.269456+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=0a054019b233c9b6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_18` and `tamagawa_product` of elliptic_curves `4235.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0a054019b233c9b6 emitted 2026-05-18T19:51:11.418659+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=2a54b773ed75314a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `tamagawa_product` of elliptic_curves `7744.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2a54b773ed75314a emitted 2026-05-18T19:51:11.476971+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=045ea90b0e2b1be6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_5` and `torsion` of elliptic_curves `7092.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 045ea90b0e2b1be6 emitted 2026-05-18T19:51:11.544224+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=cdaa786087e9467b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_1` and `rank` of elliptic_curves `2779.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cdaa786087e9467b emitted 2026-05-18T19:51:11.708319+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=96f65606852a3a7e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_7` and `torsion` of elliptic_curves `3472.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 96f65606852a3a7e emitted 2026-05-18T19:51:11.845410+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=ee22ec854720750c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_4` and `tamagawa_product` of elliptic_curves `3510.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ee22ec854720750c emitted 2026-05-18T19:51:11.853410+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=922b6b5b4c191846
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 922b6b5b4c191846 emitted 2026-05-18T19:51:12.105406+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=657c4dcb460bb10e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_6` and `torsion` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 657c4dcb460bb10e emitted 2026-05-18T19:51:12.111405+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=34fac00fc5a5cc8e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_7` and `conductor` of elliptic_curves `8789.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 34fac00fc5a5cc8e emitted 2026-05-18T19:51:12.118406+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=c8c428a9814d9d0e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from h4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `knot_invariant` of
  knots `{knot}` and `ec_invariant` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c8c428a9814d9d0e emitted 2026-05-18T19:51:12.120406+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=d1; batch=batch-20260518T195105Z-43a075;
  record_id=4a0f655e436e4215
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from d1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `{knot}` and `conductor` of elliptic_curves `{ec_object}`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4a0f655e436e4215 emitted 2026-05-18T19:51:12.214405+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=da3661296f25aeb9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `rank` of elliptic_curves `8904.i3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da3661296f25aeb9 emitted 2026-05-18T19:51:12.301532+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=be3c0d08c1ea1c0f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_11` and `rank` of elliptic_curves `9196.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record be3c0d08c1ea1c0f emitted 2026-05-18T19:51:12.464246+00:00
source_date: '2026-05-18'
caveats: 'Substrate-engine-generated training anchor. Verification is computational
  (relation evaluator over integer invariants), not analytical proof. Per Fire #24
  cross-catalog audit, parity (equal_mod_2) relations are ~62% structurally extensible
  across catalog pairs; divides/abs_diff_le_K rates are catalog-specific; equality
  is mostly small-range artifact. Relation type for this anchor: `equal_mod_2`. Training
  weight: 0.975. Per Fire #22, divides-on-zero was a known bug fixed; this anchor
  was emitted on the fixed code path.'
consumed_by: ergon/learner/scripts/ingest_training_anchors.py
source_report: theseus/journals/BATCH_LOG.md
```

