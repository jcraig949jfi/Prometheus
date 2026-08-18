# Theseus → Ergon Training Anchor Handoff

Generated: 2026-05-19T09:26:50.576102+00:00
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
id: anchor-knots_x_elliptic_curves-00005
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
id: anchor-knots_x_elliptic_curves-00006
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
id: anchor-knots_x_elliptic_curves-00007
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
id: anchor-knots_x_elliptic_curves-00008
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
id: anchor-knots_x_elliptic_curves-00009
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
id: anchor-knots_x_elliptic_curves-00010
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
id: anchor-knots_x_elliptic_curves-00011
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
id: anchor-knots_x_elliptic_curves-00012
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
id: anchor-knots_x_elliptic_curves-00013
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
id: anchor-knots_x_elliptic_curves-00014
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
id: anchor-knots_x_elliptic_curves-00015
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
id: anchor-knots_x_elliptic_curves-00016
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
id: anchor-knots_x_elliptic_curves-00017
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
id: anchor-knots_x_elliptic_curves-00018
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
id: anchor-knots_x_elliptic_curves-00019
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
id: anchor-knots_x_elliptic_curves-00020
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
id: anchor-knots_x_elliptic_curves-00021
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
id: anchor-knots_x_elliptic_curves-00022
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
id: anchor-knots_x_elliptic_curves-00023
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
id: anchor-knots_x_elliptic_curves-00024
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
id: anchor-knots_x_elliptic_curves-00025
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
id: anchor-knots_x_elliptic_curves-00026
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
id: anchor-knots_x_elliptic_curves-00027
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
id: anchor-knots_x_elliptic_curves-00028
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
id: anchor-knots_x_elliptic_curves-00029
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
id: anchor-knots_x_elliptic_curves-00030
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
id: anchor-knots_x_elliptic_curves-00031
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
id: anchor-knots_x_elliptic_curves-00032
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
id: anchor-knots_x_elliptic_curves-00033
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
id: anchor-knots_x_elliptic_curves-00034
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
id: anchor-knots_x_elliptic_curves-00035
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
id: anchor-knots_x_elliptic_curves-00036
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
id: anchor-knots_x_elliptic_curves-00037
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
id: anchor-knots_x_elliptic_curves-00038
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
id: anchor-knots_x_elliptic_curves-00039
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
id: anchor-knots_x_elliptic_curves-00040
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
id: anchor-knots_x_elliptic_curves-00041
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
id: anchor-knots_x_elliptic_curves-00042
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
id: anchor-knots_x_elliptic_curves-00043
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
id: anchor-knots_x_elliptic_curves-00044
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
id: anchor-knots_x_elliptic_curves-00045
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
id: anchor-knots_x_elliptic_curves-00046
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
id: anchor-knots_x_elliptic_curves-00047
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
id: anchor-knots_x_elliptic_curves-00048
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
id: anchor-knots_x_elliptic_curves-00049
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
id: anchor-knots_x_elliptic_curves-00050
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
id: anchor-knots_x_elliptic_curves-00051
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
id: anchor-knots_x_elliptic_curves-00052
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
id: anchor-knots_x_elliptic_curves-00053
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
id: anchor-knots_x_elliptic_curves-00054
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
id: anchor-knots_x_elliptic_curves-00055
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
id: anchor-knots_x_elliptic_curves-00056
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
id: anchor-knots_x_elliptic_curves-00057
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
id: anchor-knots_x_elliptic_curves-00058
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
id: anchor-knots_x_elliptic_curves-00059
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
id: anchor-knots_x_elliptic_curves-00060
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
id: anchor-knots_x_elliptic_curves-00061
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
id: anchor-knots_x_elliptic_curves-00062
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
id: anchor-knots_x_elliptic_curves-00063
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
id: anchor-knots_x_elliptic_curves-00064
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
id: anchor-knots_x_elliptic_curves-00065
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
id: anchor-knots_x_elliptic_curves-00066
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
id: anchor-knots_x_elliptic_curves-00067
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

```yaml
# substrate_block: training_anchor
_schema_version: 1.0.0
id: anchor-knots_x_elliptic_curves-00068
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=e5117795dd3b8216
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
source: Theseus substrate engine record e5117795dd3b8216 emitted 2026-05-18T19:51:12.466245+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4ea1a3ad77da2779
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_9` and `tamagawa_product` of elliptic_curves `5880.bf2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4ea1a3ad77da2779 emitted 2026-05-18T19:51:12.595252+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=d1f57f0d5cb8d2ce
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
source: Theseus substrate engine record d1f57f0d5cb8d2ce emitted 2026-05-18T19:51:12.613254+00:00
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
  record_id=7f2e813c4c19735e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_15` and `tamagawa_product` of elliptic_curves `3755.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7f2e813c4c19735e emitted 2026-05-18T19:51:12.625337+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8a5dc8f959dc1ddd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_124` and `torsion` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8a5dc8f959dc1ddd emitted 2026-05-18T19:51:12.751425+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=aec638839953d0e8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_3` and `torsion` of elliptic_curves `7350.bi1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record aec638839953d0e8 emitted 2026-05-18T19:51:12.788544+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=316cbd060aa1b537
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `rank` of elliptic_curves `8880.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 316cbd060aa1b537 emitted 2026-05-18T19:51:13.013185+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=58574607307dc53c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_2` and `tamagawa_product` of elliptic_curves `5190.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 58574607307dc53c emitted 2026-05-18T19:51:13.087254+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=c395af3aa3d405f0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `4_1` and `rank` of elliptic_curves `5292.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c395af3aa3d405f0 emitted 2026-05-18T19:51:13.117253+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8ad271d1c28c3725
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_2` and `tamagawa_product` of elliptic_curves `231.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ad271d1c28c3725 emitted 2026-05-18T19:51:13.185252+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=7a6fb04d15d2b31c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_1` and `conductor` of elliptic_curves `2100.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7a6fb04d15d2b31c emitted 2026-05-18T19:51:13.320466+00:00
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
  record_id=849fb260efaeec1a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `torsion` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 849fb260efaeec1a emitted 2026-05-18T19:51:13.327465+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=89711976b929b339
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_6` and `tamagawa_product` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 89711976b929b339 emitted 2026-05-18T19:51:14.016448+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=99845f0345c282cc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_11` and `conductor` of elliptic_curves `990.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 99845f0345c282cc emitted 2026-05-18T19:51:14.249172+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=ba24c6cc06a22910
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `tamagawa_product` of elliptic_curves `1056.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ba24c6cc06a22910 emitted 2026-05-18T19:51:14.630644+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8acd28b182852703
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_20` and `tamagawa_product` of elliptic_curves `3510.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8acd28b182852703 emitted 2026-05-18T19:51:14.700981+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=960b018f0a5b12c3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_18` and `tamagawa_product` of elliptic_curves `4770.u1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 960b018f0a5b12c3 emitted 2026-05-18T19:51:14.723076+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=5ae4741063383cf2
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
source: Theseus substrate engine record 5ae4741063383cf2 emitted 2026-05-18T19:51:15.069257+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c82c11b218269b66
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_1` and `conductor` of elliptic_curves `8090.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c82c11b218269b66 emitted 2026-05-18T19:51:15.203350+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e6dee979a7c8dadf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `rank` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e6dee979a7c8dadf emitted 2026-05-18T19:51:15.290458+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=1e815a808e28e690
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_14` and `torsion` of elliptic_curves `2275.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1e815a808e28e690 emitted 2026-05-18T19:51:15.526261+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=edd02bfb6fcea633
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
source: Theseus substrate engine record edd02bfb6fcea633 emitted 2026-05-18T19:51:15.670932+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=e53129084eaa3acf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `torsion` of elliptic_curves `1716.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e53129084eaa3acf emitted 2026-05-18T19:51:15.721152+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4fed0b9532dd0252
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_3` and `torsion` of elliptic_curves `9240.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4fed0b9532dd0252 emitted 2026-05-18T19:51:15.726153+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=4983368950e82922
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_17` and `rank` of elliptic_curves `8505.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4983368950e82922 emitted 2026-05-18T19:51:16.038292+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=764db12c127763d9
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
source: Theseus substrate engine record 764db12c127763d9 emitted 2026-05-18T19:51:16.070291+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f042a59fd296e418
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `torsion` of elliptic_curves `5856.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f042a59fd296e418 emitted 2026-05-18T19:51:16.422362+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=27bd618e28848d82
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `tamagawa_product` of elliptic_curves `5880.bf2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 27bd618e28848d82 emitted 2026-05-18T19:51:16.449360+00:00
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
  record_id=938f9f42fb49f2d1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_13` and `tamagawa_product` of elliptic_curves `9510.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 938f9f42fb49f2d1 emitted 2026-05-18T19:51:16.569359+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=dd0a0206d32c31ff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `torsion` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dd0a0206d32c31ff emitted 2026-05-18T19:51:16.976526+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=e509dece3b6bce83
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `4_1` and `rank` of elliptic_curves `1314.c3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e509dece3b6bce83 emitted 2026-05-18T19:51:17.046898+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=626acc5e7530fa55
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_7` and `torsion` of elliptic_curves `330.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 626acc5e7530fa55 emitted 2026-05-18T19:51:17.054897+00:00
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
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=b9c132c5118626dc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_8` and `rank` of elliptic_curves `2656.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b9c132c5118626dc emitted 2026-05-18T19:51:17.163169+00:00
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
id: anchor-knots_x_elliptic_curves-00101
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=2da29b0b4dd0e1a0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_9` and `conductor` of elliptic_curves `1320.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2da29b0b4dd0e1a0 emitted 2026-05-18T19:51:17.218302+00:00
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
id: anchor-knots_x_elliptic_curves-00102
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=21839737d300065f
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
source: Theseus substrate engine record 21839737d300065f emitted 2026-05-18T19:51:17.249374+00:00
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
id: anchor-knots_x_elliptic_curves-00103
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=d3947d625887c73b
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
source: Theseus substrate engine record d3947d625887c73b emitted 2026-05-18T19:51:17.321373+00:00
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
id: anchor-knots_x_elliptic_curves-00104
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=898881e57e2b3b83
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_5` and `torsion` of elliptic_curves `1325.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 898881e57e2b3b83 emitted 2026-05-18T19:51:17.359373+00:00
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
id: anchor-knots_x_elliptic_curves-00105
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=710e00795c0b88a2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `conductor` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 710e00795c0b88a2 emitted 2026-05-18T19:51:17.393371+00:00
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
id: anchor-knots_x_elliptic_curves-00106
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=dcead24a945b5bb4
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
source: Theseus substrate engine record dcead24a945b5bb4 emitted 2026-05-18T19:51:17.447373+00:00
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
id: anchor-knots_x_elliptic_curves-00107
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=19d98d2d2a4a8a7b
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
source: Theseus substrate engine record 19d98d2d2a4a8a7b emitted 2026-05-18T19:51:17.519370+00:00
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
id: anchor-knots_x_elliptic_curves-00108
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=521a14141f722674
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_5` and `torsion` of elliptic_curves `2064.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 521a14141f722674 emitted 2026-05-18T19:51:17.576372+00:00
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
id: anchor-knots_x_elliptic_curves-00109
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=da6d6047bcb32e64
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_2` and `torsion` of elliptic_curves `4032.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da6d6047bcb32e64 emitted 2026-05-18T19:51:17.939115+00:00
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
id: anchor-knots_x_elliptic_curves-00110
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=d32407affba11d87
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_19` and `conductor` of elliptic_curves `9282.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d32407affba11d87 emitted 2026-05-18T19:51:18.069992+00:00
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
id: anchor-knots_x_elliptic_curves-00111
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=12a8a456a03c1125
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_5` and `tamagawa_product` of elliptic_curves `7744.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 12a8a456a03c1125 emitted 2026-05-18T19:51:18.161200+00:00
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
id: anchor-knots_x_elliptic_curves-00112
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=3b15229267337347
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_18` and `conductor` of elliptic_curves `1876.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3b15229267337347 emitted 2026-05-18T19:51:18.455377+00:00
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
id: anchor-knots_x_elliptic_curves-00113
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=7f9b2b7d97f47cb7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_13` and `rank` of elliptic_curves `3891.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7f9b2b7d97f47cb7 emitted 2026-05-18T19:51:19.083136+00:00
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
id: anchor-knots_x_elliptic_curves-00114
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=3694a4e2a7bf4d78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `10_124` and `torsion` of elliptic_curves `2352.w1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3694a4e2a7bf4d78 emitted 2026-05-18T19:51:19.277226+00:00
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
id: anchor-knots_x_elliptic_curves-00115
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=7f2b4ef8a5f416a6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_1` and `torsion` of elliptic_curves `1716.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7f2b4ef8a5f416a6 emitted 2026-05-18T19:51:19.486107+00:00
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
id: anchor-knots_x_elliptic_curves-00116
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=d953f362093724b9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_6` and `conductor` of elliptic_curves `8789.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d953f362093724b9 emitted 2026-05-18T19:51:19.555221+00:00
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
id: anchor-knots_x_elliptic_curves-00117
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=9ba01505d3d4e2a7
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
source: Theseus substrate engine record 9ba01505d3d4e2a7 emitted 2026-05-18T19:51:19.628259+00:00
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
id: anchor-knots_x_elliptic_curves-00118
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=7fe0f368394fadae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_3` and `torsion` of elliptic_curves `5780.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7fe0f368394fadae emitted 2026-05-18T19:51:19.745302+00:00
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
id: anchor-knots_x_elliptic_curves-00119
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=1f5663fffbcc3edf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_2` and `tamagawa_product` of elliptic_curves `6525.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1f5663fffbcc3edf emitted 2026-05-18T19:51:19.784360+00:00
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
id: anchor-knots_x_elliptic_curves-00120
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=0a42eb49c30e269d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_21` and `conductor` of elliptic_curves `5408.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0a42eb49c30e269d emitted 2026-05-18T19:51:19.836359+00:00
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
id: anchor-knots_x_elliptic_curves-00121
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=a70c945039cd23fa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_19` and `conductor` of elliptic_curves `7810.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a70c945039cd23fa emitted 2026-05-18T19:51:19.894358+00:00
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
id: anchor-knots_x_elliptic_curves-00122
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=3bd68024addcf876
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `conductor` of elliptic_curves `8880.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3bd68024addcf876 emitted 2026-05-18T19:51:19.947528+00:00
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
id: anchor-knots_x_elliptic_curves-00123
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=ca01e91495949c21
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `6_2` and `rank` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ca01e91495949c21 emitted 2026-05-18T19:51:20.123078+00:00
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
id: anchor-knots_x_elliptic_curves-00124
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=5d9caa9a704b743f
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
source: Theseus substrate engine record 5d9caa9a704b743f emitted 2026-05-18T19:51:20.144076+00:00
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
id: anchor-knots_x_elliptic_curves-00125
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=8a44d5d89b7ddfd9
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
source: Theseus substrate engine record 8a44d5d89b7ddfd9 emitted 2026-05-18T19:51:20.157077+00:00
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
id: anchor-knots_x_elliptic_curves-00126
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=563a4aefe5f04ac4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_6` and `tamagawa_product` of elliptic_curves `6175.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 563a4aefe5f04ac4 emitted 2026-05-18T19:51:20.168076+00:00
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
id: anchor-knots_x_elliptic_curves-00127
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=47fc805fe1a7a6fc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_5` and `conductor` of elliptic_curves `7718.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 47fc805fe1a7a6fc emitted 2026-05-18T19:51:20.180076+00:00
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
id: anchor-knots_x_elliptic_curves-00128
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=1a38b4f4d3b38c3e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `conductor` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1a38b4f4d3b38c3e emitted 2026-05-18T19:51:20.335302+00:00
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
id: anchor-knots_x_elliptic_curves-00129
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=b0c9ffe276deb2f6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_139` and `torsion` of elliptic_curves `7743.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b0c9ffe276deb2f6 emitted 2026-05-18T19:51:20.423300+00:00
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
id: anchor-knots_x_elliptic_curves-00130
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=e32aa7a19d3baae2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_2` and `rank` of elliptic_curves `2205.i6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e32aa7a19d3baae2 emitted 2026-05-18T19:51:20.841188+00:00
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
id: anchor-knots_x_elliptic_curves-00131
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f4bfe816c2ff7a39
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_1` and `conductor` of elliptic_curves `1716.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f4bfe816c2ff7a39 emitted 2026-05-18T19:51:20.996185+00:00
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
id: anchor-knots_x_elliptic_curves-00132
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=b361f28dd6409ba3
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
source: Theseus substrate engine record b361f28dd6409ba3 emitted 2026-05-18T19:51:21.084236+00:00
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
id: anchor-knots_x_elliptic_curves-00133
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=07438ac4568968e3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_5` and `tamagawa_product` of elliptic_curves `1760.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 07438ac4568968e3 emitted 2026-05-18T19:51:21.164232+00:00
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
id: anchor-knots_x_elliptic_curves-00134
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5db6561eaa631b26
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `conductor` of elliptic_curves `4845.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5db6561eaa631b26 emitted 2026-05-18T19:51:21.261454+00:00
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
id: anchor-knots_x_elliptic_curves-00135
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=6582993b4ce2c5bb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_3` and `torsion` of elliptic_curves `9114.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6582993b4ce2c5bb emitted 2026-05-18T19:51:21.300600+00:00
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
id: anchor-knots_x_elliptic_curves-00136
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=ef71da526abdf02e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_152` and `conductor` of elliptic_curves `5408.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ef71da526abdf02e emitted 2026-05-18T19:51:21.347937+00:00
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
id: anchor-knots_x_elliptic_curves-00137
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=9133fb3e0c4c0e4a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_8` and `conductor` of elliptic_curves `7982.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9133fb3e0c4c0e4a emitted 2026-05-18T19:51:21.429068+00:00
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
id: anchor-knots_x_elliptic_curves-00138
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=042c6b90838c5962
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_5` and `torsion` of elliptic_curves `7718.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 042c6b90838c5962 emitted 2026-05-18T19:51:21.623133+00:00
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
id: anchor-knots_x_elliptic_curves-00139
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=e6c49d1755c970d8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_1` and `torsion` of elliptic_curves `2170.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e6c49d1755c970d8 emitted 2026-05-18T19:51:22.192969+00:00
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
id: anchor-knots_x_elliptic_curves-00140
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=491b56ba42364e84
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_17` and `conductor` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 491b56ba42364e84 emitted 2026-05-18T19:51:22.318107+00:00
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
id: anchor-knots_x_elliptic_curves-00141
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=cec0dc404b91093b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_2` and `torsion` of elliptic_curves `882.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cec0dc404b91093b emitted 2026-05-18T19:51:22.324107+00:00
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
id: anchor-knots_x_elliptic_curves-00142
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=dae84f33a9e12399
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_1` and `conductor` of elliptic_curves `3192.c4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dae84f33a9e12399 emitted 2026-05-18T19:51:22.666027+00:00
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
id: anchor-knots_x_elliptic_curves-00143
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=b5b95f886a222de9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_1` and `rank` of elliptic_curves `2160.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b5b95f886a222de9 emitted 2026-05-18T19:51:22.713027+00:00
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
id: anchor-knots_x_elliptic_curves-00144
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5eb4a39be8ce9df5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_3` and `conductor` of elliptic_curves `718.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5eb4a39be8ce9df5 emitted 2026-05-18T19:51:22.788025+00:00
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
id: anchor-knots_x_elliptic_curves-00145
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=5a6f3b7bb8770302
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_5` and `rank` of elliptic_curves `612.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5a6f3b7bb8770302 emitted 2026-05-18T19:51:22.796025+00:00
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
id: anchor-knots_x_elliptic_curves-00146
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=2374ccf603faa1e8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_10` and `conductor` of elliptic_curves `9248.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2374ccf603faa1e8 emitted 2026-05-18T19:51:22.816029+00:00
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
id: anchor-knots_x_elliptic_curves-00147
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=d97c646ec12b9330
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_3` and `torsion` of elliptic_curves `4032.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d97c646ec12b9330 emitted 2026-05-18T19:51:22.964060+00:00
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
id: anchor-knots_x_elliptic_curves-00148
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=9e8cc6092cf1322a
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
source: Theseus substrate engine record 9e8cc6092cf1322a emitted 2026-05-18T19:51:23.025158+00:00
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
id: anchor-knots_x_elliptic_curves-00149
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=9d862f094856a359
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
source: Theseus substrate engine record 9d862f094856a359 emitted 2026-05-18T19:51:23.358967+00:00
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
id: anchor-knots_x_elliptic_curves-00150
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=a13fe1d935d66861
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_9` and `tamagawa_product` of elliptic_curves `414.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a13fe1d935d66861 emitted 2026-05-18T19:51:23.531845+00:00
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
id: anchor-knots_x_elliptic_curves-00151
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=6cc1010861bca5ae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `3_1` and `rank` of elliptic_curves `5334.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6cc1010861bca5ae emitted 2026-05-18T19:51:23.545901+00:00
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
id: anchor-knots_x_elliptic_curves-00152
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=dbd98d54b0d31727
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `conductor` of elliptic_curves `7982.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dbd98d54b0d31727 emitted 2026-05-18T19:51:23.618042+00:00
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
id: anchor-knots_x_elliptic_curves-00153
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=67da210f7c7096ec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `tamagawa_product` of elliptic_curves `3520.o2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 67da210f7c7096ec emitted 2026-05-18T19:51:23.643042+00:00
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
id: anchor-knots_x_elliptic_curves-00154
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=dc7789910adddf42
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `5_2` and `conductor` of elliptic_curves `7448.p1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dc7789910adddf42 emitted 2026-05-18T19:51:23.914232+00:00
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
id: anchor-knots_x_elliptic_curves-00155
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=b5f8499ed7465016
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
source: Theseus substrate engine record b5f8499ed7465016 emitted 2026-05-18T19:51:24.193701+00:00
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
id: anchor-knots_x_elliptic_curves-00156
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7827922286421a70
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
source: Theseus substrate engine record 7827922286421a70 emitted 2026-05-18T19:51:24.405829+00:00
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
id: anchor-knots_x_elliptic_curves-00157
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=accf4ba2a3e59d64
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
source: Theseus substrate engine record accf4ba2a3e59d64 emitted 2026-05-18T19:51:24.530173+00:00
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
id: anchor-knots_x_elliptic_curves-00158
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2e3244c585c37634
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `torsion` of elliptic_curves `1056.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2e3244c585c37634 emitted 2026-05-18T19:51:24.771273+00:00
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
id: anchor-knots_x_elliptic_curves-00159
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=910a43b814f5fc03
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_1` and `rank` of elliptic_curves `570.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 910a43b814f5fc03 emitted 2026-05-18T19:51:24.824831+00:00
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
id: anchor-knots_x_elliptic_curves-00160
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=89eec97f17aca58a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_11` and `conductor` of elliptic_curves `2170.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 89eec97f17aca58a emitted 2026-05-18T19:51:24.897005+00:00
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
id: anchor-knots_x_elliptic_curves-00161
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=31b4b7d8cff0ce18
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_6` and `conductor` of elliptic_curves `5056.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 31b4b7d8cff0ce18 emitted 2026-05-18T19:51:24.927102+00:00
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
id: anchor-knots_x_elliptic_curves-00162
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=daab800971246359
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_12` and `tamagawa_product` of elliptic_curves `8211.i1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record daab800971246359 emitted 2026-05-18T19:51:25.042208+00:00
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
id: anchor-knots_x_elliptic_curves-00163
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=4732265941fe20c4
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
source: Theseus substrate engine record 4732265941fe20c4 emitted 2026-05-18T19:51:25.099256+00:00
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
id: anchor-knots_x_elliptic_curves-00164
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8f2fb3d6dcd5ef21
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_3` and `torsion` of elliptic_curves `2028.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8f2fb3d6dcd5ef21 emitted 2026-05-18T19:51:25.148688+00:00
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
id: anchor-knots_x_elliptic_curves-00165
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=810fd6bce1ac192e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `6_2` and `rank` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 810fd6bce1ac192e emitted 2026-05-18T19:51:25.274994+00:00
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
id: anchor-knots_x_elliptic_curves-00166
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=e9b47300ee207b21
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `tamagawa_product` of elliptic_curves `8880.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e9b47300ee207b21 emitted 2026-05-18T19:51:25.301063+00:00
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
id: anchor-knots_x_elliptic_curves-00167
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=5c045c9c8749b764
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_124` and `conductor` of elliptic_curves `9248.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5c045c9c8749b764 emitted 2026-05-18T19:51:25.964065+00:00
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
id: anchor-knots_x_elliptic_curves-00168
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=4af67af92c7fd8d9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_12` and `torsion` of elliptic_curves `3360.q3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4af67af92c7fd8d9 emitted 2026-05-18T19:51:26.422074+00:00
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
id: anchor-knots_x_elliptic_curves-00169
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=13e653f5d96a243f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_2` and `torsion` of elliptic_curves `6050.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 13e653f5d96a243f emitted 2026-05-18T19:51:26.604225+00:00
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
id: anchor-knots_x_elliptic_curves-00170
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=e05007ae6d8a7085
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
source: Theseus substrate engine record e05007ae6d8a7085 emitted 2026-05-18T19:51:26.710458+00:00
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
id: anchor-knots_x_elliptic_curves-00171
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=61a4551c313b6d40
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
source: Theseus substrate engine record 61a4551c313b6d40 emitted 2026-05-18T19:51:26.764702+00:00
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
id: anchor-knots_x_elliptic_curves-00172
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=495117ec17fd7fe2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_2` and `tamagawa_product` of elliptic_curves `2205.i6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 495117ec17fd7fe2 emitted 2026-05-18T19:51:26.889063+00:00
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
id: anchor-knots_x_elliptic_curves-00173
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=a96aa5739939a36e
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
source: Theseus substrate engine record a96aa5739939a36e emitted 2026-05-18T19:51:27.024149+00:00
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
id: anchor-knots_x_elliptic_curves-00174
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=947439a28ce9a415
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `tamagawa_product` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 947439a28ce9a415 emitted 2026-05-18T19:51:27.030148+00:00
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
id: anchor-knots_x_elliptic_curves-00175
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=112926851c9cfdf3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_165` and `conductor` of elliptic_curves `8274.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 112926851c9cfdf3 emitted 2026-05-18T19:51:27.245145+00:00
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
id: anchor-knots_x_elliptic_curves-00176
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=bcf82f77ff0f92e8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_16` and `torsion` of elliptic_curves `4230.bh1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bcf82f77ff0f92e8 emitted 2026-05-18T19:51:27.351246+00:00
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
id: anchor-knots_x_elliptic_curves-00177
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=a869e79e4e0ca7a5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `3_1` and `rank` of elliptic_curves `2205.i6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a869e79e4e0ca7a5 emitted 2026-05-18T19:51:27.448415+00:00
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
id: anchor-knots_x_elliptic_curves-00178
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4efdf8d1b242095f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `5_2` and `torsion` of elliptic_curves `9490.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4efdf8d1b242095f emitted 2026-05-18T19:51:27.547265+00:00
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
id: anchor-knots_x_elliptic_curves-00179
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=448ed5edf3dc1474
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
source: Theseus substrate engine record 448ed5edf3dc1474 emitted 2026-05-18T19:51:27.575865+00:00
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
id: anchor-knots_x_elliptic_curves-00180
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=864a1eb55054b7cf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_1` and `conductor` of elliptic_curves `570.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 864a1eb55054b7cf emitted 2026-05-18T19:51:27.635010+00:00
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
id: anchor-knots_x_elliptic_curves-00181
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=3a7889204545a529
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_3` and `tamagawa_product` of elliptic_curves `7526.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a7889204545a529 emitted 2026-05-18T19:51:27.691010+00:00
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
id: anchor-knots_x_elliptic_curves-00182
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=3031d7a28e69d569
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_3` and `conductor` of elliptic_curves `4235.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3031d7a28e69d569 emitted 2026-05-18T19:51:27.713009+00:00
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
id: anchor-knots_x_elliptic_curves-00183
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=04b559edbfd4e674
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
source: Theseus substrate engine record 04b559edbfd4e674 emitted 2026-05-18T19:51:27.863060+00:00
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
id: anchor-knots_x_elliptic_curves-00184
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=5ec9c712a7be054a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_2` and `torsion` of elliptic_curves `6050.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5ec9c712a7be054a emitted 2026-05-18T19:51:28.110111+00:00
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
id: anchor-knots_x_elliptic_curves-00185
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=13a28b03eb205d73
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `rank` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 13a28b03eb205d73 emitted 2026-05-18T19:51:28.295016+00:00
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
id: anchor-knots_x_elliptic_curves-00186
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=131c9d35cb06cc94
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
source: Theseus substrate engine record 131c9d35cb06cc94 emitted 2026-05-18T19:51:28.341012+00:00
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
id: anchor-knots_x_elliptic_curves-00187
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=0229260fb5887c78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_5` and `rank` of elliptic_curves `8502.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0229260fb5887c78 emitted 2026-05-18T19:51:28.366012+00:00
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
id: anchor-knots_x_elliptic_curves-00188
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=e9109f2ae595e128
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `rank` of elliptic_curves `4571.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e9109f2ae595e128 emitted 2026-05-18T19:51:28.451170+00:00
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
id: anchor-knots_x_elliptic_curves-00189
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=0221f77be34a37b6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_2` and `conductor` of elliptic_curves `5380.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0221f77be34a37b6 emitted 2026-05-18T19:51:28.718959+00:00
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
id: anchor-knots_x_elliptic_curves-00190
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=b22cd6b443e6f7a4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_1` and `rank` of elliptic_curves `2779.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b22cd6b443e6f7a4 emitted 2026-05-18T19:51:29.279250+00:00
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
id: anchor-knots_x_elliptic_curves-00191
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8ed9aeac47064eca
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `3_1` and `rank` of elliptic_curves `372.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8ed9aeac47064eca emitted 2026-05-18T19:51:30.035067+00:00
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
id: anchor-knots_x_elliptic_curves-00192
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=36f359142df7668e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_6` and `torsion` of elliptic_curves `4410.y1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 36f359142df7668e emitted 2026-05-18T19:51:30.204686+00:00
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
id: anchor-knots_x_elliptic_curves-00193
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=42f1867272539de5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_6` and `torsion` of elliptic_curves `6040.j2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 42f1867272539de5 emitted 2026-05-18T19:51:30.365924+00:00
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
id: anchor-knots_x_elliptic_curves-00194
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=ca013030b62b8e4c
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
source: Theseus substrate engine record ca013030b62b8e4c emitted 2026-05-18T19:51:30.437986+00:00
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
id: anchor-knots_x_elliptic_curves-00195
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=32eb287204e7dca6
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
source: Theseus substrate engine record 32eb287204e7dca6 emitted 2026-05-18T19:51:30.754951+00:00
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
id: anchor-knots_x_elliptic_curves-00196
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=b93da3d13d7e0edd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_1` and `torsion` of elliptic_curves `3479.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b93da3d13d7e0edd emitted 2026-05-18T19:51:31.160889+00:00
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
id: anchor-knots_x_elliptic_curves-00197
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=56d8c2874fab0aff
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_1` and `torsion` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 56d8c2874fab0aff emitted 2026-05-18T19:51:31.240885+00:00
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
id: anchor-knots_x_elliptic_curves-00198
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=ca98b95560b46348
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
source: Theseus substrate engine record ca98b95560b46348 emitted 2026-05-18T19:51:31.427992+00:00
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
id: anchor-knots_x_elliptic_curves-00199
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=2738a04430bb5534
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_3` and `tamagawa_product` of elliptic_curves `2205.i6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2738a04430bb5534 emitted 2026-05-18T19:51:31.546110+00:00
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
id: anchor-knots_x_elliptic_curves-00200
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=a39873f55c8cd064
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `torsion` of elliptic_curves `6720.n7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a39873f55c8cd064 emitted 2026-05-18T19:51:31.563110+00:00
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
id: anchor-knots_x_elliptic_curves-00201
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=cf55288cd73c12b7
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
source: Theseus substrate engine record cf55288cd73c12b7 emitted 2026-05-18T19:51:31.593148+00:00
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
id: anchor-knots_x_elliptic_curves-00202
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=82f5c71a63e189bb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_7` and `rank` of elliptic_curves `9490.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 82f5c71a63e189bb emitted 2026-05-18T19:51:31.628171+00:00
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
id: anchor-knots_x_elliptic_curves-00203
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=f87af3b4018f2ee2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `conductor` of elliptic_curves `9825.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f87af3b4018f2ee2 emitted 2026-05-18T19:51:31.921979+00:00
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
id: anchor-knots_x_elliptic_curves-00204
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=42e4cc5aff73ff61
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
source: Theseus substrate engine record 42e4cc5aff73ff61 emitted 2026-05-18T19:51:32.724166+00:00
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
id: anchor-knots_x_elliptic_curves-00205
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=33fcebfe5385f97a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `tamagawa_product` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 33fcebfe5385f97a emitted 2026-05-18T19:51:32.797574+00:00
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
id: anchor-knots_x_elliptic_curves-00206
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=3d79359d121e4b1d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_3` and `torsion` of elliptic_curves `6400.p1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3d79359d121e4b1d emitted 2026-05-18T19:51:33.161011+00:00
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
id: anchor-knots_x_elliptic_curves-00207
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=26a46268120e8980
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_165` and `rank` of elliptic_curves `2680.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 26a46268120e8980 emitted 2026-05-18T19:51:33.782087+00:00
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
id: anchor-knots_x_elliptic_curves-00208
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=6f13de58bc591d39
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_12` and `torsion` of elliptic_curves `4830.bk1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6f13de58bc591d39 emitted 2026-05-18T19:51:34.450870+00:00
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
id: anchor-knots_x_elliptic_curves-00209
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4d98761927d87670
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_8` and `torsion` of elliptic_curves `8043.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4d98761927d87670 emitted 2026-05-18T19:51:35.002027+00:00
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
id: anchor-knots_x_elliptic_curves-00210
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=f3bc33a14d54ab23
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `torsion` of elliptic_curves `2781.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f3bc33a14d54ab23 emitted 2026-05-18T19:51:35.092076+00:00
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
id: anchor-knots_x_elliptic_curves-00211
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8936fbcd29ccad6d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_6` and `tamagawa_product` of elliptic_curves `663.a6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8936fbcd29ccad6d emitted 2026-05-18T19:51:35.210564+00:00
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
id: anchor-knots_x_elliptic_curves-00212
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=b9050252cf66f95a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `3_1` and `rank` of elliptic_curves `3731.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b9050252cf66f95a emitted 2026-05-18T19:51:35.303879+00:00
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
id: anchor-knots_x_elliptic_curves-00213
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=35213b1968b9c83b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_15` and `torsion` of elliptic_curves `5025.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 35213b1968b9c83b emitted 2026-05-18T19:51:35.528678+00:00
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
id: anchor-knots_x_elliptic_curves-00214
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=98a4a0e41aad6b89
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_2` and `tamagawa_product` of elliptic_curves `7448.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 98a4a0e41aad6b89 emitted 2026-05-18T19:51:35.567834+00:00
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
id: anchor-knots_x_elliptic_curves-00215
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=288a8c6b2dd8a08d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `conductor` of elliptic_curves `1056.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 288a8c6b2dd8a08d emitted 2026-05-18T19:51:35.669946+00:00
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
id: anchor-knots_x_elliptic_curves-00216
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=3a4b8263b3907a2e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_165` and `rank` of elliptic_curves `3190.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3a4b8263b3907a2e emitted 2026-05-18T19:51:35.884144+00:00
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
id: anchor-knots_x_elliptic_curves-00217
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5d59da79a65b7170
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `rank` of elliptic_curves `9768.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5d59da79a65b7170 emitted 2026-05-18T19:51:36.080836+00:00
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
id: anchor-knots_x_elliptic_curves-00218
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=6a66288a1823bee8
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
source: Theseus substrate engine record 6a66288a1823bee8 emitted 2026-05-18T19:51:36.264971+00:00
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
id: anchor-knots_x_elliptic_curves-00219
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=c9ee8a9569db8d94
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `4_1` and `rank` of elliptic_curves `2988.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c9ee8a9569db8d94 emitted 2026-05-18T19:51:36.290016+00:00
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
id: anchor-knots_x_elliptic_curves-00220
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=a9e935b4f937bd44
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `conductor` of elliptic_curves `9850.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a9e935b4f937bd44 emitted 2026-05-18T19:51:36.317125+00:00
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
id: anchor-knots_x_elliptic_curves-00221
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=b9afd639fba037d5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_2` and `conductor` of elliptic_curves `8100.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b9afd639fba037d5 emitted 2026-05-18T19:51:36.337125+00:00
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
id: anchor-knots_x_elliptic_curves-00222
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=4a4e83fd9924e4ea
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
source: Theseus substrate engine record 4a4e83fd9924e4ea emitted 2026-05-18T19:51:36.463713+00:00
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
id: anchor-knots_x_elliptic_curves-00223
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=02b91d23e490d9cf
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
source: Theseus substrate engine record 02b91d23e490d9cf emitted 2026-05-18T19:51:37.073842+00:00
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
id: anchor-knots_x_elliptic_curves-00224
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7ec0aa9c94a48943
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
source: Theseus substrate engine record 7ec0aa9c94a48943 emitted 2026-05-18T19:51:37.087842+00:00
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
id: anchor-knots_x_elliptic_curves-00225
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=25c8856251b11a74
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `conductor` of elliptic_curves `9768.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 25c8856251b11a74 emitted 2026-05-18T19:51:37.198886+00:00
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
id: anchor-knots_x_elliptic_curves-00226
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2ac5b2ceae7fa5cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `torsion` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2ac5b2ceae7fa5cb emitted 2026-05-18T19:51:37.993629+00:00
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
id: anchor-knots_x_elliptic_curves-00227
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=38f348fcbd2cac64
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_16` and `conductor` of elliptic_curves `5956.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38f348fcbd2cac64 emitted 2026-05-18T19:51:38.304699+00:00
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
id: anchor-knots_x_elliptic_curves-00228
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=b1d021ddbc32635f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `rank` of elliptic_curves `6525.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b1d021ddbc32635f emitted 2026-05-18T19:51:38.755226+00:00
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
id: anchor-knots_x_elliptic_curves-00229
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=f8c29ccd600d533e
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
source: Theseus substrate engine record f8c29ccd600d533e emitted 2026-05-18T19:51:38.809671+00:00
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
id: anchor-knots_x_elliptic_curves-00230
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=b449789a57db164f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `rank` of elliptic_curves `5856.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b449789a57db164f emitted 2026-05-18T19:51:38.980802+00:00
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
id: anchor-knots_x_elliptic_curves-00231
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=59d41e4ab473edf6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_1` and `tamagawa_product` of elliptic_curves `2779.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 59d41e4ab473edf6 emitted 2026-05-18T19:51:39.870954+00:00
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
id: anchor-knots_x_elliptic_curves-00232
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=94c2bc94b39cd695
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
source: Theseus substrate engine record 94c2bc94b39cd695 emitted 2026-05-18T19:51:40.113004+00:00
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
id: anchor-knots_x_elliptic_curves-00233
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=1ea204385b96c0d7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_21` and `rank` of elliptic_curves `9200.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1ea204385b96c0d7 emitted 2026-05-18T19:51:40.138092+00:00
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
id: anchor-knots_x_elliptic_curves-00234
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f28556c3f81ac2ee
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `rank` of elliptic_curves `8880.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f28556c3f81ac2ee emitted 2026-05-18T19:51:40.638552+00:00
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
id: anchor-knots_x_elliptic_curves-00235
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=9cad06edac220509
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_7` and `torsion` of elliptic_curves `882.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9cad06edac220509 emitted 2026-05-18T19:51:40.679752+00:00
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
id: anchor-knots_x_elliptic_curves-00236
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8c09fa0a6f7cda9e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_21` and `rank` of elliptic_curves `5280.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c09fa0a6f7cda9e emitted 2026-05-18T19:51:40.801754+00:00
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
id: anchor-knots_x_elliptic_curves-00237
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=a1d1b43b2ec14716
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_9` and `tamagawa_product` of elliptic_curves `1001.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a1d1b43b2ec14716 emitted 2026-05-18T19:51:40.985017+00:00
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
id: anchor-knots_x_elliptic_curves-00238
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e610da4bb1c5eec5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `torsion` of elliptic_curves `8800.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e610da4bb1c5eec5 emitted 2026-05-18T19:51:41.245883+00:00
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
id: anchor-knots_x_elliptic_curves-00239
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=fde8b1965f12b18f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `6_1` and `rank` of elliptic_curves `1806.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fde8b1965f12b18f emitted 2026-05-18T19:51:41.513213+00:00
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
id: anchor-knots_x_elliptic_curves-00240
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=c1ee3edc359e2dea
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_6` and `rank` of elliptic_curves `9405.h5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c1ee3edc359e2dea emitted 2026-05-18T19:51:41.538299+00:00
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
id: anchor-knots_x_elliptic_curves-00241
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=8a4f506f47fcca2d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_7` and `torsion` of elliptic_curves `330.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8a4f506f47fcca2d emitted 2026-05-18T19:51:42.943778+00:00
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
id: anchor-knots_x_elliptic_curves-00242
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=3c18b20515c644da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_152` and `conductor` of elliptic_curves `3417.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3c18b20515c644da emitted 2026-05-18T19:51:43.037777+00:00
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
id: anchor-knots_x_elliptic_curves-00243
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=9f4cfce86971e336
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_13` and `conductor` of elliptic_curves `1170.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9f4cfce86971e336 emitted 2026-05-18T19:51:43.620944+00:00
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
id: anchor-knots_x_elliptic_curves-00244
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=0649a91e92a4e6f1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_18` and `conductor` of elliptic_curves `4235.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0649a91e92a4e6f1 emitted 2026-05-18T19:51:43.750942+00:00
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
id: anchor-knots_x_elliptic_curves-00245
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5d6235a6d131f877
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `conductor` of elliptic_curves `1138.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5d6235a6d131f877 emitted 2026-05-18T19:51:43.970937+00:00
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
id: anchor-knots_x_elliptic_curves-00246
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=cf9cba88622a4265
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_3` and `tamagawa_product` of elliptic_curves `2800.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cf9cba88622a4265 emitted 2026-05-18T19:51:44.060037+00:00
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
id: anchor-knots_x_elliptic_curves-00247
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=eafac08fd9b4490d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_1` and `torsion` of elliptic_curves `3479.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record eafac08fd9b4490d emitted 2026-05-18T19:51:44.235712+00:00
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
id: anchor-knots_x_elliptic_curves-00248
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e9fcc63f402cbe52
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_161` and `torsion` of elliptic_curves `1666.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e9fcc63f402cbe52 emitted 2026-05-18T19:51:44.305766+00:00
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
id: anchor-knots_x_elliptic_curves-00249
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=6880e4adc54def37
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `tamagawa_product` of elliptic_curves `7392.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6880e4adc54def37 emitted 2026-05-18T19:51:44.464864+00:00
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
id: anchor-knots_x_elliptic_curves-00250
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=c3e4bcff6e7f078a
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
source: Theseus substrate engine record c3e4bcff6e7f078a emitted 2026-05-18T19:51:44.742715+00:00
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
id: anchor-knots_x_elliptic_curves-00251
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=2de6947b32f92928
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_7` and `tamagawa_product` of elliptic_curves `3520.y2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2de6947b32f92928 emitted 2026-05-18T19:51:45.279518+00:00
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
id: anchor-knots_x_elliptic_curves-00252
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=ac98f70129816c87
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_20` and `conductor` of elliptic_curves `8100.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ac98f70129816c87 emitted 2026-05-18T19:51:45.298599+00:00
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
id: anchor-knots_x_elliptic_curves-00253
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=1b7760043d912d36
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
source: Theseus substrate engine record 1b7760043d912d36 emitted 2026-05-18T19:51:46.010271+00:00
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
id: anchor-knots_x_elliptic_curves-00254
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=bea0cf1d2a04047d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_2` and `rank` of elliptic_curves `240.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bea0cf1d2a04047d emitted 2026-05-18T19:51:46.380896+00:00
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
id: anchor-knots_x_elliptic_curves-00255
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c93b7c4c3a566f9d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_10` and `conductor` of elliptic_curves `4845.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c93b7c4c3a566f9d emitted 2026-05-18T19:51:46.731757+00:00
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
id: anchor-knots_x_elliptic_curves-00256
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=8b3ca52e468051c7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_165` and `conductor` of elliptic_curves `4920.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8b3ca52e468051c7 emitted 2026-05-18T19:51:46.894849+00:00
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
id: anchor-knots_x_elliptic_curves-00257
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=0950014685c5e4f0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `rank` of elliptic_curves `9912.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0950014685c5e4f0 emitted 2026-05-18T19:51:47.144648+00:00
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
id: anchor-knots_x_elliptic_curves-00258
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=97573a385e48f8ae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `torsion` of elliptic_curves `1370.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 97573a385e48f8ae emitted 2026-05-18T19:51:47.223770+00:00
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
id: anchor-knots_x_elliptic_curves-00259
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=8523783d407f7bf6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_10` and `rank` of elliptic_curves `8738.e4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8523783d407f7bf6 emitted 2026-05-18T19:51:47.673812+00:00
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
id: anchor-knots_x_elliptic_curves-00260
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=2834618c9ff66a4a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_3` and `tamagawa_product` of elliptic_curves `4480.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2834618c9ff66a4a emitted 2026-05-18T19:51:48.019653+00:00
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
id: anchor-knots_x_elliptic_curves-00261
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=1d672f1addff4eca
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
source: Theseus substrate engine record 1d672f1addff4eca emitted 2026-05-18T19:51:48.204856+00:00
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
id: anchor-knots_x_elliptic_curves-00262
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=232740e8f648947f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `conductor` of elliptic_curves `8800.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 232740e8f648947f emitted 2026-05-18T19:51:48.276989+00:00
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
id: anchor-knots_x_elliptic_curves-00263
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=85ec35888a1f59ee
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_2` and `rank` of elliptic_curves `3768.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 85ec35888a1f59ee emitted 2026-05-18T19:51:48.346373+00:00
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
id: anchor-knots_x_elliptic_curves-00264
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=1d15106aee139382
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `3_1` and `tamagawa_product` of elliptic_curves `2205.i6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1d15106aee139382 emitted 2026-05-18T19:51:48.538771+00:00
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
id: anchor-knots_x_elliptic_curves-00265
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=72991f8419d77bcb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_8` and `rank` of elliptic_curves `8043.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 72991f8419d77bcb emitted 2026-05-18T19:51:48.564771+00:00
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
id: anchor-knots_x_elliptic_curves-00266
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=723311f968bb3964
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
source: Theseus substrate engine record 723311f968bb3964 emitted 2026-05-18T19:51:48.625832+00:00
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
id: anchor-knots_x_elliptic_curves-00267
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4b2ed10566b06b62
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_4` and `torsion` of elliptic_curves `3933.e3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4b2ed10566b06b62 emitted 2026-05-18T19:51:49.009840+00:00
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
id: anchor-knots_x_elliptic_curves-00268
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=c135309245d97273
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_3` and `rank` of elliptic_curves `2751.d4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c135309245d97273 emitted 2026-05-18T19:51:49.391521+00:00
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
id: anchor-knots_x_elliptic_curves-00269
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=ce6b601ac918b671
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_20` and `tamagawa_product` of elliptic_curves `5880.bf2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ce6b601ac918b671 emitted 2026-05-18T19:51:49.410597+00:00
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
id: anchor-knots_x_elliptic_curves-00270
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=13615584d3aabcb2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `conductor` of elliptic_curves `3192.c4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 13615584d3aabcb2 emitted 2026-05-18T19:51:49.868681+00:00
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
id: anchor-knots_x_elliptic_curves-00271
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=4429e313967b270e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_15` and `conductor` of elliptic_curves `6918.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4429e313967b270e emitted 2026-05-18T19:51:49.925680+00:00
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
id: anchor-knots_x_elliptic_curves-00272
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=0a343cacf94bc6bb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_6` and `rank` of elliptic_curves `525.d5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0a343cacf94bc6bb emitted 2026-05-18T19:51:50.104741+00:00
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
id: anchor-knots_x_elliptic_curves-00273
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=6bf67935ff67302f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_1` and `torsion` of elliptic_curves `3520.ba2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6bf67935ff67302f emitted 2026-05-18T19:51:50.259811+00:00
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
id: anchor-knots_x_elliptic_curves-00274
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e7351c3014315607
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `5_2` and `rank` of elliptic_curves `2304.m2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e7351c3014315607 emitted 2026-05-18T19:51:50.322853+00:00
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
id: anchor-knots_x_elliptic_curves-00275
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=ada3776be0e415b6
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
source: Theseus substrate engine record ada3776be0e415b6 emitted 2026-05-18T19:51:50.416215+00:00
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
id: anchor-knots_x_elliptic_curves-00276
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=5f522715edc07031
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
source: Theseus substrate engine record 5f522715edc07031 emitted 2026-05-18T19:51:51.011805+00:00
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
id: anchor-knots_x_elliptic_curves-00277
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=858df4739adb82f1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_6` and `torsion` of elliptic_curves `5025.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 858df4739adb82f1 emitted 2026-05-18T19:51:51.318688+00:00
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
id: anchor-knots_x_elliptic_curves-00278
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=1d607919a31c0774
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
source: Theseus substrate engine record 1d607919a31c0774 emitted 2026-05-18T19:51:51.520785+00:00
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
id: anchor-knots_x_elliptic_curves-00279
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5aef4d377cdd20c0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_14` and `tamagawa_product` of elliptic_curves `6550.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5aef4d377cdd20c0 emitted 2026-05-18T19:51:51.546122+00:00
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
id: anchor-knots_x_elliptic_curves-00280
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8c598e77bd28271e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_21` and `tamagawa_product` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c598e77bd28271e emitted 2026-05-18T19:51:51.559178+00:00
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
id: anchor-knots_x_elliptic_curves-00281
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=1e7dcffeaccdffe7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_4` and `conductor` of elliptic_curves `7380.a4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1e7dcffeaccdffe7 emitted 2026-05-18T19:51:51.584261+00:00
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
id: anchor-knots_x_elliptic_curves-00282
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c6706e0ed7a410b3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_3` and `rank` of elliptic_curves `2205.i6`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c6706e0ed7a410b3 emitted 2026-05-18T19:51:52.154586+00:00
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
id: anchor-knots_x_elliptic_curves-00283
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=3008cbd662a52788
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `rank` of elliptic_curves `9136.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3008cbd662a52788 emitted 2026-05-18T19:51:52.346664+00:00
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
id: anchor-knots_x_elliptic_curves-00284
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=f98b8098aaf7e7ae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_2` and `torsion` of elliptic_curves `404.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f98b8098aaf7e7ae emitted 2026-05-18T19:51:52.376663+00:00
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
id: anchor-knots_x_elliptic_curves-00285
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=935dce7ceb53abf6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_4` and `torsion` of elliptic_curves `1287.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 935dce7ceb53abf6 emitted 2026-05-18T19:51:52.885773+00:00
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
id: anchor-knots_x_elliptic_curves-00286
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=9e662859ac186c69
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_3` and `torsion` of elliptic_curves `5780.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9e662859ac186c69 emitted 2026-05-18T19:51:52.982565+00:00
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
id: anchor-knots_x_elliptic_curves-00287
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=0015bb3fea3343b5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_17` and `rank` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0015bb3fea3343b5 emitted 2026-05-18T19:51:52.995566+00:00
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
id: anchor-knots_x_elliptic_curves-00288
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2178d13dde65dd43
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_4` and `rank` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2178d13dde65dd43 emitted 2026-05-18T19:51:53.175752+00:00
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
id: anchor-knots_x_elliptic_curves-00289
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=3e24403f66591985
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `conductor` of elliptic_curves `4425.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3e24403f66591985 emitted 2026-05-18T19:51:53.350923+00:00
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
id: anchor-knots_x_elliptic_curves-00290
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=a71ab2e00eb78d24
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_3` and `torsion` of elliptic_curves `5789.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a71ab2e00eb78d24 emitted 2026-05-18T19:51:53.575691+00:00
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
id: anchor-knots_x_elliptic_curves-00291
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=bc6a838017f32dfa
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_21` and `torsion` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bc6a838017f32dfa emitted 2026-05-18T19:51:54.074747+00:00
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
id: anchor-knots_x_elliptic_curves-00292
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=f41648414dade68a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_12` and `tamagawa_product` of elliptic_curves `2496.r2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f41648414dade68a emitted 2026-05-18T19:51:54.225930+00:00
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
id: anchor-knots_x_elliptic_curves-00293
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=4630a17b40510a7b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_7` and `rank` of elliptic_curves `1872.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4630a17b40510a7b emitted 2026-05-18T19:51:54.552602+00:00
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
id: anchor-knots_x_elliptic_curves-00294
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=36599c9e2048075f
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
source: Theseus substrate engine record 36599c9e2048075f emitted 2026-05-18T19:51:54.918784+00:00
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
id: anchor-knots_x_elliptic_curves-00295
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=23208d531db2fe80
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_2` and `torsion` of elliptic_curves `9510.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 23208d531db2fe80 emitted 2026-05-18T19:51:55.148575+00:00
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
id: anchor-knots_x_elliptic_curves-00296
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=97ede6bd34d36eab
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
source: Theseus substrate engine record 97ede6bd34d36eab emitted 2026-05-18T19:51:55.287607+00:00
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
id: anchor-knots_x_elliptic_curves-00297
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=4a5b7e06b1306224
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_20` and `tamagawa_product` of elliptic_curves `7614.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4a5b7e06b1306224 emitted 2026-05-18T19:51:55.414775+00:00
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
id: anchor-knots_x_elliptic_curves-00298
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=e9627e9782c222af
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
source: Theseus substrate engine record e9627e9782c222af emitted 2026-05-18T19:51:55.614671+00:00
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
id: anchor-knots_x_elliptic_curves-00299
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=f79ad08ee7068c87
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
source: Theseus substrate engine record f79ad08ee7068c87 emitted 2026-05-18T19:51:55.798051+00:00
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
id: anchor-knots_x_elliptic_curves-00300
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=a206fa4aba8ed161
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_1` and `conductor` of elliptic_curves `2842.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a206fa4aba8ed161 emitted 2026-05-18T19:51:55.821159+00:00
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
id: anchor-knots_x_elliptic_curves-00301
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=346d246e2be4cde3
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
source: Theseus substrate engine record 346d246e2be4cde3 emitted 2026-05-18T19:51:56.491600+00:00
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
id: anchor-knots_x_elliptic_curves-00302
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=cf5579d459e3be5b
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
source: Theseus substrate engine record cf5579d459e3be5b emitted 2026-05-18T19:51:57.193059+00:00
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
id: anchor-knots_x_elliptic_curves-00303
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=dfb8f6637190c2db
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_1` and `torsion` of elliptic_curves `4195.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record dfb8f6637190c2db emitted 2026-05-18T19:51:57.241332+00:00
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
id: anchor-knots_x_elliptic_curves-00304
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=4d25e149a7d2e454
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
source: Theseus substrate engine record 4d25e149a7d2e454 emitted 2026-05-18T19:51:57.256433+00:00
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
id: anchor-knots_x_elliptic_curves-00305
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=d3736e2808434cd6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_2` and `conductor` of elliptic_curves `9350.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d3736e2808434cd6 emitted 2026-05-18T19:51:57.525294+00:00
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
id: anchor-knots_x_elliptic_curves-00306
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=89c010e515d74624
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `conductor` of elliptic_curves `2830.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 89c010e515d74624 emitted 2026-05-18T19:51:57.551393+00:00
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
id: anchor-knots_x_elliptic_curves-00307
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=ed622fd2e74a337c
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
source: Theseus substrate engine record ed622fd2e74a337c emitted 2026-05-18T19:51:57.756483+00:00
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
id: anchor-knots_x_elliptic_curves-00308
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=3884463a0f3653f1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `torsion` of elliptic_curves `7350.ct7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3884463a0f3653f1 emitted 2026-05-18T19:51:57.784483+00:00
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
id: anchor-knots_x_elliptic_curves-00309
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=cdf71f540fde0a93
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_6` and `rank` of elliptic_curves `7593.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cdf71f540fde0a93 emitted 2026-05-18T19:51:57.835543+00:00
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
id: anchor-knots_x_elliptic_curves-00310
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=d7ef88d48602159a
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
source: Theseus substrate engine record d7ef88d48602159a emitted 2026-05-18T19:51:57.890542+00:00
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
id: anchor-knots_x_elliptic_curves-00311
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=8c3d5d35351c534d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_4` and `torsion` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c3d5d35351c534d emitted 2026-05-18T19:51:58.009579+00:00
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
id: anchor-knots_x_elliptic_curves-00312
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=be1e13da67b66129
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
source: Theseus substrate engine record be1e13da67b66129 emitted 2026-05-18T19:51:58.043633+00:00
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
id: anchor-knots_x_elliptic_curves-00313
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=3b9a4f562dff3676
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_4` and `torsion` of elliptic_curves `3120.n1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3b9a4f562dff3676 emitted 2026-05-18T19:51:58.139730+00:00
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
id: anchor-knots_x_elliptic_curves-00314
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=89cd92c6a386e869
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_161` and `tamagawa_product` of elliptic_curves `7380.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 89cd92c6a386e869 emitted 2026-05-18T19:51:58.572459+00:00
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
id: anchor-knots_x_elliptic_curves-00315
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=da883b4282b79509
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `conductor` of elliptic_curves `4692.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da883b4282b79509 emitted 2026-05-18T19:51:58.659458+00:00
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
id: anchor-knots_x_elliptic_curves-00316
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=f59873574ea98140
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `torsion` of elliptic_curves `2650.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f59873574ea98140 emitted 2026-05-18T19:51:58.834455+00:00
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
id: anchor-knots_x_elliptic_curves-00317
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=52360905a6eb4a1d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_7` and `tamagawa_product` of elliptic_curves `9490.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 52360905a6eb4a1d emitted 2026-05-18T19:51:58.867510+00:00
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
id: anchor-knots_x_elliptic_curves-00318
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=a2240b8b0ae106a8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_3` and `conductor` of elliptic_curves `6400.p1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a2240b8b0ae106a8 emitted 2026-05-18T19:51:58.996357+00:00
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
id: anchor-knots_x_elliptic_curves-00319
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=4f909094cb5d159a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_11` and `tamagawa_product` of elliptic_curves `1330.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4f909094cb5d159a emitted 2026-05-18T19:52:00.308323+00:00
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
id: anchor-knots_x_elliptic_curves-00320
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=16b072d550fe5aa5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `tamagawa_product` of elliptic_curves `4896.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 16b072d550fe5aa5 emitted 2026-05-18T19:52:00.340421+00:00
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
id: anchor-knots_x_elliptic_curves-00321
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e95552243c3f2dac
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_10` and `tamagawa_product` of elliptic_curves `610.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e95552243c3f2dac emitted 2026-05-18T19:52:00.500617+00:00
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
id: anchor-knots_x_elliptic_curves-00322
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=8c26375d74f1cddf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_8` and `tamagawa_product` of elliptic_curves `4576.d3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8c26375d74f1cddf emitted 2026-05-18T19:52:00.501617+00:00
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
id: anchor-knots_x_elliptic_curves-00323
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7d65c0038360e341
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
source: Theseus substrate engine record 7d65c0038360e341 emitted 2026-05-18T19:52:00.581615+00:00
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
id: anchor-knots_x_elliptic_curves-00324
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=968d70b86a7398f6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `torsion` of elliptic_curves `5025.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 968d70b86a7398f6 emitted 2026-05-18T19:52:00.876410+00:00
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
id: anchor-knots_x_elliptic_curves-00325
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=4efe3be26e1f1a86
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_7` and `conductor` of elliptic_curves `2385.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4efe3be26e1f1a86 emitted 2026-05-18T19:52:01.213590+00:00
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
id: anchor-knots_x_elliptic_curves-00326
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=de0d8ab12f4d0c79
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_7` and `rank` of elliptic_curves `6080.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record de0d8ab12f4d0c79 emitted 2026-05-18T19:52:01.318589+00:00
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
id: anchor-knots_x_elliptic_curves-00327
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=0fb75e25c7b2b65d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `tamagawa_product` of elliptic_curves `5280.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0fb75e25c7b2b65d emitted 2026-05-18T19:52:01.424640+00:00
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
id: anchor-knots_x_elliptic_curves-00328
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=ed9cdcfd4bde59cb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `7_7` and `tamagawa_product` of elliptic_curves `404.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ed9cdcfd4bde59cb emitted 2026-05-18T19:52:01.476847+00:00
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
id: anchor-knots_x_elliptic_curves-00329
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=2a150aa3199b6ecf
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
source: Theseus substrate engine record 2a150aa3199b6ecf emitted 2026-05-18T19:52:01.594380+00:00
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
id: anchor-knots_x_elliptic_curves-00330
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=72fa00145be821dc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_10` and `torsion` of elliptic_curves `2650.h1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 72fa00145be821dc emitted 2026-05-18T19:52:01.638927+00:00
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
id: anchor-knots_x_elliptic_curves-00331
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=6e55bb550f372b96
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_165` and `torsion` of elliptic_curves `6370.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 6e55bb550f372b96 emitted 2026-05-18T19:52:01.736404+00:00
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
id: anchor-knots_x_elliptic_curves-00332
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=ddfd1e01f4aded2b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `conductor` of elliptic_curves `3066.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ddfd1e01f4aded2b emitted 2026-05-18T19:52:02.038640+00:00
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
id: anchor-knots_x_elliptic_curves-00333
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=1dcab4bc34acf2da
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_124` and `conductor` of elliptic_curves `1428.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1dcab4bc34acf2da emitted 2026-05-18T19:52:02.206379+00:00
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
id: anchor-knots_x_elliptic_curves-00334
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=347fa8eb75b77516
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_10` and `torsion` of elliptic_curves `6402.o2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 347fa8eb75b77516 emitted 2026-05-18T19:52:02.591399+00:00
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
id: anchor-knots_x_elliptic_curves-00335
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7ef6335f0403e441
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
source: Theseus substrate engine record 7ef6335f0403e441 emitted 2026-05-18T19:52:03.088230+00:00
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
id: anchor-knots_x_elliptic_curves-00336
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=572d9fcb48e7a962
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `rank` of elliptic_curves `2781.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 572d9fcb48e7a962 emitted 2026-05-18T19:52:03.303785+00:00
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
id: anchor-knots_x_elliptic_curves-00337
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=2c062b9719570d1e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `5_2` and `torsion` of elliptic_curves `1216.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2c062b9719570d1e emitted 2026-05-18T19:52:03.703614+00:00
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
id: anchor-knots_x_elliptic_curves-00338
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=dd3c9c0f91d5d2e1
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
source: Theseus substrate engine record dd3c9c0f91d5d2e1 emitted 2026-05-18T19:52:03.924399+00:00
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
id: anchor-knots_x_elliptic_curves-00339
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=93a4051db5f4360c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `conductor` of elliptic_curves `6992.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 93a4051db5f4360c emitted 2026-05-18T19:52:04.071514+00:00
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
id: anchor-knots_x_elliptic_curves-00340
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=02ccc1d36d50397e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_19` and `rank` of elliptic_curves `4688.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 02ccc1d36d50397e emitted 2026-05-18T19:52:04.117565+00:00
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
id: anchor-knots_x_elliptic_curves-00341
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=b3218fd4f68dcaf5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_10` and `torsion` of elliptic_curves `2725.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b3218fd4f68dcaf5 emitted 2026-05-18T19:52:04.467356+00:00
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
id: anchor-knots_x_elliptic_curves-00342
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=0e55d60f1b81fe47
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_20` and `rank` of elliptic_curves `3840.t1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0e55d60f1b81fe47 emitted 2026-05-18T19:52:04.487356+00:00
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
id: anchor-knots_x_elliptic_curves-00343
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c0a09eb06d901e1e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_8` and `rank` of elliptic_curves `2656.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c0a09eb06d901e1e emitted 2026-05-18T19:52:05.028523+00:00
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
id: anchor-knots_x_elliptic_curves-00344
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=fdeeafbc6da56859
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `tamagawa_product` of elliptic_curves `2496.r2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fdeeafbc6da56859 emitted 2026-05-18T19:52:05.114622+00:00
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
id: anchor-knots_x_elliptic_curves-00345
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=77b5eec49fe27eae
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_152` and `conductor` of elliptic_curves `4392.d2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 77b5eec49fe27eae emitted 2026-05-18T19:52:05.437685+00:00
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
id: anchor-knots_x_elliptic_curves-00346
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e816e9a2ed2ab45b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_1` and `rank` of elliptic_curves `9600.bf1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e816e9a2ed2ab45b emitted 2026-05-18T19:52:05.560265+00:00
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
id: anchor-knots_x_elliptic_curves-00347
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=a7a252383ddddb48
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_14` and `torsion` of elliptic_curves `2275.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a7a252383ddddb48 emitted 2026-05-18T19:52:06.324119+00:00
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
id: anchor-knots_x_elliptic_curves-00348
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=9875e29d94224f93
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_4` and `conductor` of elliptic_curves `5280.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9875e29d94224f93 emitted 2026-05-18T19:52:06.554424+00:00
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
id: anchor-knots_x_elliptic_curves-00349
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=509fd15fa9fc1b48
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_3` and `torsion` of elliptic_curves `5175.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 509fd15fa9fc1b48 emitted 2026-05-18T19:52:06.830537+00:00
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
id: anchor-knots_x_elliptic_curves-00350
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=93ab565b800ce350
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_5` and `tamagawa_product` of elliptic_curves `1760.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 93ab565b800ce350 emitted 2026-05-18T19:52:07.038572+00:00
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
id: anchor-knots_x_elliptic_curves-00351
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=82a6325f69e60f78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `3_1` and `conductor` of elliptic_curves `9856.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 82a6325f69e60f78 emitted 2026-05-18T19:52:07.065448+00:00
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
id: anchor-knots_x_elliptic_curves-00352
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=d1b19e3308b701c8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_21` and `torsion` of elliptic_curves `610.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d1b19e3308b701c8 emitted 2026-05-18T19:52:07.221502+00:00
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
id: anchor-knots_x_elliptic_curves-00353
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=58c88b2c80d4ca35
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
source: Theseus substrate engine record 58c88b2c80d4ca35 emitted 2026-05-18T19:52:07.832310+00:00
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
id: anchor-knots_x_elliptic_curves-00354
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=2dc6822b4d62e79f
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
source: Theseus substrate engine record 2dc6822b4d62e79f emitted 2026-05-18T19:52:08.406355+00:00
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
id: anchor-knots_x_elliptic_curves-00355
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=a0d3d70569de5500
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `3_1` and `conductor` of elliptic_curves `2394.n3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a0d3d70569de5500 emitted 2026-05-18T19:52:08.965544+00:00
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
id: anchor-knots_x_elliptic_curves-00356
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=786fea201f01bac0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_5` and `tamagawa_product` of elliptic_curves `2400.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 786fea201f01bac0 emitted 2026-05-18T19:52:09.054543+00:00
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
id: anchor-knots_x_elliptic_curves-00357
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c9189eb00843ce49
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_15` and `torsion` of elliptic_curves `3755.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c9189eb00843ce49 emitted 2026-05-18T19:52:09.889334+00:00
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
id: anchor-knots_x_elliptic_curves-00358
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=fbd77b518cfe342f
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
source: Theseus substrate engine record fbd77b518cfe342f emitted 2026-05-18T19:52:09.947387+00:00
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
id: anchor-knots_x_elliptic_curves-00359
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=e07e1647b32439e4
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
source: Theseus substrate engine record e07e1647b32439e4 emitted 2026-05-18T19:52:10.527373+00:00
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
id: anchor-knots_x_elliptic_curves-00360
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=cd323d1d3df91cb5
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
source: Theseus substrate engine record cd323d1d3df91cb5 emitted 2026-05-18T19:52:11.280219+00:00
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
id: anchor-knots_x_elliptic_curves-00361
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=9b90cb057849bb56
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_1` and `conductor` of elliptic_curves `3520.ba2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9b90cb057849bb56 emitted 2026-05-18T19:52:11.538415+00:00
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
id: anchor-knots_x_elliptic_curves-00362
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=7c696f31d73d2342
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
source: Theseus substrate engine record 7c696f31d73d2342 emitted 2026-05-18T19:52:11.818411+00:00
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
id: anchor-knots_x_elliptic_curves-00363
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=e93d0040a740add2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_19` and `conductor` of elliptic_curves `9856.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e93d0040a740add2 emitted 2026-05-18T19:52:12.157267+00:00
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
id: anchor-knots_x_elliptic_curves-00364
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=dc5f3cfe1d99b2c8
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
source: Theseus substrate engine record dc5f3cfe1d99b2c8 emitted 2026-05-18T19:52:12.339263+00:00
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
id: anchor-knots_x_elliptic_curves-00365
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=bcda7c43f6b734f8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_21` and `rank` of elliptic_curves `2016.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bcda7c43f6b734f8 emitted 2026-05-18T19:52:12.585300+00:00
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
id: anchor-knots_x_elliptic_curves-00366
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=1bb7b84bd7d2d25b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `conductor` of elliptic_curves `8344.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1bb7b84bd7d2d25b emitted 2026-05-18T19:52:12.786383+00:00
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
id: anchor-knots_x_elliptic_curves-00367
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=2c711943e2bde968
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_6` and `tamagawa_product` of elliptic_curves `7920.o3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2c711943e2bde968 emitted 2026-05-18T19:52:12.898382+00:00
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
id: anchor-knots_x_elliptic_curves-00368
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=1eb26b7b968a3e05
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_9` and `tamagawa_product` of elliptic_curves `9450.bu1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1eb26b7b968a3e05 emitted 2026-05-18T19:52:12.922381+00:00
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
id: anchor-knots_x_elliptic_curves-00369
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=954f7527167bd712
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
source: Theseus substrate engine record 954f7527167bd712 emitted 2026-05-18T19:52:13.272166+00:00
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
id: anchor-knots_x_elliptic_curves-00370
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=c90e9c9d765f9c9e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_19` and `torsion` of elliptic_curves `8265.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c90e9c9d765f9c9e emitted 2026-05-18T19:52:13.321209+00:00
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
id: anchor-knots_x_elliptic_curves-00371
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=0da7084f119eafc2
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `torsion` of elliptic_curves `8925.h2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0da7084f119eafc2 emitted 2026-05-18T19:52:14.371483+00:00
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
id: anchor-knots_x_elliptic_curves-00372
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=12ca6264d7d40da9
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
source: Theseus substrate engine record 12ca6264d7d40da9 emitted 2026-05-18T19:52:14.392483+00:00
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
id: anchor-knots_x_elliptic_curves-00373
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=ffbece686703cf6b
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
source: Theseus substrate engine record ffbece686703cf6b emitted 2026-05-18T19:52:14.926162+00:00
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
id: anchor-knots_x_elliptic_curves-00374
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=d55b6492ce53ed8e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_5` and `torsion` of elliptic_curves `1325.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d55b6492ce53ed8e emitted 2026-05-18T19:52:14.986215+00:00
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
id: anchor-knots_x_elliptic_curves-00375
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=25436c20d2ce3ce7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `conductor` of elliptic_curves `2170.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 25436c20d2ce3ce7 emitted 2026-05-18T19:52:15.347979+00:00
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
id: anchor-knots_x_elliptic_curves-00376
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=9df11bfbf0971a6a
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
source: Theseus substrate engine record 9df11bfbf0971a6a emitted 2026-05-18T19:52:15.406196+00:00
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
id: anchor-knots_x_elliptic_curves-00377
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=ff63fb55508e0f15
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_16` and `conductor` of elliptic_curves `2699.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ff63fb55508e0f15 emitted 2026-05-18T19:52:15.690321+00:00
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
id: anchor-knots_x_elliptic_curves-00378
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=aba395c3cb8948f5
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
source: Theseus substrate engine record aba395c3cb8948f5 emitted 2026-05-18T19:52:15.873399+00:00
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
id: anchor-knots_x_elliptic_curves-00379
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=bc990101961d4e98
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_145` and `torsion` of elliptic_curves `1138.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bc990101961d4e98 emitted 2026-05-18T19:52:16.044142+00:00
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
id: anchor-knots_x_elliptic_curves-00380
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=13134a5db65db040
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
source: Theseus substrate engine record 13134a5db65db040 emitted 2026-05-18T19:52:16.260300+00:00
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
id: anchor-knots_x_elliptic_curves-00381
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=8076ce9a87616ed7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_14` and `tamagawa_product` of elliptic_curves `3885.c5`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8076ce9a87616ed7 emitted 2026-05-18T19:52:17.118150+00:00
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
id: anchor-knots_x_elliptic_curves-00382
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=845a8c365480c345
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
source: Theseus substrate engine record 845a8c365480c345 emitted 2026-05-18T19:52:17.515364+00:00
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
id: anchor-knots_x_elliptic_curves-00383
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=e58ef95892589955
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `10_145` and `conductor` of elliptic_curves `6992.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e58ef95892589955 emitted 2026-05-18T19:52:17.926286+00:00
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
id: anchor-knots_x_elliptic_curves-00384
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5441fde90eda0f5b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_17` and `torsion` of elliptic_curves `3834.f1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5441fde90eda0f5b emitted 2026-05-18T19:52:18.359220+00:00
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
id: anchor-knots_x_elliptic_curves-00385
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=293df4e4b826217e
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
source: Theseus substrate engine record 293df4e4b826217e emitted 2026-05-18T19:52:18.729083+00:00
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
id: anchor-knots_x_elliptic_curves-00386
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=fa69194cbd83d57c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_10` and `tamagawa_product` of elliptic_curves `610.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fa69194cbd83d57c emitted 2026-05-18T19:52:19.105555+00:00
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
id: anchor-knots_x_elliptic_curves-00387
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=cce575555e8cec34
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_21` and `rank` of elliptic_curves `9200.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record cce575555e8cec34 emitted 2026-05-18T19:52:19.304251+00:00
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
id: anchor-knots_x_elliptic_curves-00388
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=d217b2a60a769e3b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_1` and `torsion` of elliptic_curves `2781.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d217b2a60a769e3b emitted 2026-05-18T19:52:19.805314+00:00
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
id: anchor-knots_x_elliptic_curves-00389
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=a356e9ecb5bf1adf
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_7` and `conductor` of elliptic_curves `6400.p1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a356e9ecb5bf1adf emitted 2026-05-18T19:52:20.209161+00:00
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
id: anchor-knots_x_elliptic_curves-00390
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=2142a44f523cfceb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_3` and `torsion` of elliptic_curves `2413.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2142a44f523cfceb emitted 2026-05-18T19:52:20.864177+00:00
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
id: anchor-knots_x_elliptic_curves-00391
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=a31f3a819992ca38
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_2` and `torsion` of elliptic_curves `1440.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a31f3a819992ca38 emitted 2026-05-18T19:52:21.239278+00:00
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
id: anchor-knots_x_elliptic_curves-00392
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=3c40ebd61e1c3578
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_2` and `rank` of elliptic_curves `1287.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3c40ebd61e1c3578 emitted 2026-05-18T19:52:21.289277+00:00
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
id: anchor-knots_x_elliptic_curves-00393
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=ae86367f8ff31d9a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_19` and `torsion` of elliptic_curves `8265.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ae86367f8ff31d9a emitted 2026-05-18T19:52:21.491332+00:00
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
id: anchor-knots_x_elliptic_curves-00394
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=d20567b61a1e3bbb
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_10` and `conductor` of elliptic_curves `5193.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d20567b61a1e3bbb emitted 2026-05-18T19:52:21.571586+00:00
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
id: anchor-knots_x_elliptic_curves-00395
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=bd0049b9f4485968
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `6_2` and `torsion` of elliptic_curves `3600.u2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bd0049b9f4485968 emitted 2026-05-18T19:52:21.630175+00:00
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
id: anchor-knots_x_elliptic_curves-00396
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e53d206f6e95bb27
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `conductor` of elliptic_curves `8550.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e53d206f6e95bb27 emitted 2026-05-18T19:52:22.051384+00:00
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
id: anchor-knots_x_elliptic_curves-00397
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=e51c76738cccb596
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_5` and `tamagawa_product` of elliptic_curves `4630.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e51c76738cccb596 emitted 2026-05-18T19:52:22.355632+00:00
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
id: anchor-knots_x_elliptic_curves-00398
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=74e517dce6d1503d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_2` and `conductor` of elliptic_curves `5380.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 74e517dce6d1503d emitted 2026-05-18T19:52:22.872208+00:00
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
id: anchor-knots_x_elliptic_curves-00399
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=d3cd5a0e9032065e
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
source: Theseus substrate engine record d3cd5a0e9032065e emitted 2026-05-18T19:52:23.066803+00:00
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
id: anchor-knots_x_elliptic_curves-00400
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=f7ef3568b1dba594
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
source: Theseus substrate engine record f7ef3568b1dba594 emitted 2026-05-18T19:52:23.347169+00:00
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
id: anchor-knots_x_elliptic_curves-00401
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=b86c8fb923ae5414
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `torsion` of elliptic_curves `9490.b3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record b86c8fb923ae5414 emitted 2026-05-18T19:52:23.442680+00:00
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
id: anchor-knots_x_elliptic_curves-00402
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=e12dd4d373f8698a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_4` and `torsion` of elliptic_curves `1234.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e12dd4d373f8698a emitted 2026-05-18T19:52:25.250267+00:00
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
id: anchor-knots_x_elliptic_curves-00403
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=fc01ead3dc38b96b
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_18` and `torsion` of elliptic_curves `6550.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fc01ead3dc38b96b emitted 2026-05-18T19:52:25.467078+00:00
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
id: anchor-knots_x_elliptic_curves-00404
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=4a63608fe9c67d45
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
source: Theseus substrate engine record 4a63608fe9c67d45 emitted 2026-05-18T19:52:25.865182+00:00
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
id: anchor-knots_x_elliptic_curves-00405
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=4dffa8f61674f189
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_18` and `rank` of elliptic_curves `4161.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4dffa8f61674f189 emitted 2026-05-18T19:52:26.586009+00:00
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
id: anchor-knots_x_elliptic_curves-00406
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=678ec4a4478b74cc
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
source: Theseus substrate engine record 678ec4a4478b74cc emitted 2026-05-18T19:52:26.779100+00:00
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
id: anchor-knots_x_elliptic_curves-00407
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=1d7d97f287c34585
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `6_3` and `tamagawa_product` of elliptic_curves `7200.g1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1d7d97f287c34585 emitted 2026-05-18T19:52:26.916098+00:00
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
id: anchor-knots_x_elliptic_curves-00408
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=3769e637a999eaa7
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
source: Theseus substrate engine record 3769e637a999eaa7 emitted 2026-05-18T19:52:27.297692+00:00
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
id: anchor-knots_x_elliptic_curves-00409
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=1f1d3b702a484cf0
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_2` and `tamagawa_product` of elliptic_curves `5190.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1f1d3b702a484cf0 emitted 2026-05-18T19:52:28.102355+00:00
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
id: anchor-knots_x_elliptic_curves-00410
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=6be92490c0a6f30b
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
source: Theseus substrate engine record 6be92490c0a6f30b emitted 2026-05-18T19:52:28.393232+00:00
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
id: anchor-knots_x_elliptic_curves-00411
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=e7de9d8230ebe667
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_12` and `tamagawa_product` of elliptic_curves `4630.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e7de9d8230ebe667 emitted 2026-05-18T19:52:29.592189+00:00
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
id: anchor-knots_x_elliptic_curves-00412
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=f5b55b94212ce778
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_8` and `torsion` of elliptic_curves `3192.c4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f5b55b94212ce778 emitted 2026-05-18T19:52:29.652240+00:00
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
id: anchor-knots_x_elliptic_curves-00413
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=5e496b745c1182b1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_8` and `rank` of elliptic_curves `9328.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5e496b745c1182b1 emitted 2026-05-18T19:52:29.796541+00:00
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
id: anchor-knots_x_elliptic_curves-00414
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=b8de5848fedf2c64
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
source: Theseus substrate engine record b8de5848fedf2c64 emitted 2026-05-18T19:52:30.611145+00:00
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
id: anchor-knots_x_elliptic_curves-00415
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=e620b4740bcd2af6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `3_1` and `torsion` of elliptic_curves `9856.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e620b4740bcd2af6 emitted 2026-05-18T19:52:30.776100+00:00
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
id: anchor-knots_x_elliptic_curves-00416
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=8a2ef110374978ed
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_18` and `torsion` of elliptic_curves `6550.l1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8a2ef110374978ed emitted 2026-05-18T19:52:32.064235+00:00
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
id: anchor-knots_x_elliptic_curves-00417
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=9c4f87a10d371af8
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_6` and `conductor` of elliptic_curves `7920.o3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9c4f87a10d371af8 emitted 2026-05-18T19:52:32.101419+00:00
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
id: anchor-knots_x_elliptic_curves-00418
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=5bde4c73f4f7fb7c
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
source: Theseus substrate engine record 5bde4c73f4f7fb7c emitted 2026-05-18T19:52:32.200944+00:00
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
id: anchor-knots_x_elliptic_curves-00419
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=da55ce583eeb3cc7
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_1` and `torsion` of elliptic_curves `1716.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record da55ce583eeb3cc7 emitted 2026-05-18T19:52:33.041139+00:00
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
id: anchor-knots_x_elliptic_curves-00420
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=8da09e77cc7c9759
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `4_1` and `rank` of elliptic_curves `2988.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8da09e77cc7c9759 emitted 2026-05-18T19:52:33.070139+00:00
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
id: anchor-knots_x_elliptic_curves-00421
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=3ef40fc08a37571c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_18` and `conductor` of elliptic_curves `5390.x2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3ef40fc08a37571c emitted 2026-05-18T19:52:33.108139+00:00
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
id: anchor-knots_x_elliptic_curves-00422
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2d161721413d9b42
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_145` and `conductor` of elliptic_curves `6992.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2d161721413d9b42 emitted 2026-05-18T19:52:33.604869+00:00
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
id: anchor-knots_x_elliptic_curves-00423
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=58e6248bcc2bed94
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `conductor` of elliptic_curves `6480.m1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 58e6248bcc2bed94 emitted 2026-05-18T19:52:33.683017+00:00
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
id: anchor-knots_x_elliptic_curves-00424
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=2f518e8a13e045e7
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
source: Theseus substrate engine record 2f518e8a13e045e7 emitted 2026-05-18T19:52:33.898065+00:00
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
id: anchor-knots_x_elliptic_curves-00425
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=1d095ea5f278c58a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_19` and `rank` of elliptic_curves `8541.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1d095ea5f278c58a emitted 2026-05-18T19:52:34.028063+00:00
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
id: anchor-knots_x_elliptic_curves-00426
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=9b092b0f8af9dd70
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_7` and `torsion` of elliptic_curves `8789.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9b092b0f8af9dd70 emitted 2026-05-18T19:52:34.193101+00:00
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
id: anchor-knots_x_elliptic_curves-00427
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=8107ecebe9ab1df1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_10` and `torsion` of elliptic_curves `2725.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8107ecebe9ab1df1 emitted 2026-05-18T19:52:35.178997+00:00
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
id: anchor-knots_x_elliptic_curves-00428
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=3c3aa5785ca7a9b3
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_8` and `torsion` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3c3aa5785ca7a9b3 emitted 2026-05-18T19:52:35.457906+00:00
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
id: anchor-knots_x_elliptic_curves-00429
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=66eab70bf1142614
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_8` and `tamagawa_product` of elliptic_curves `3192.c4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 66eab70bf1142614 emitted 2026-05-18T19:52:35.718240+00:00
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
id: anchor-knots_x_elliptic_curves-00430
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=ae35f2d97fdc6f2a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `conductor` of elliptic_curves `7350.ct7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record ae35f2d97fdc6f2a emitted 2026-05-18T19:52:37.388057+00:00
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
id: anchor-knots_x_elliptic_curves-00431
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=3549d7cb58a3ac49
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
source: Theseus substrate engine record 3549d7cb58a3ac49 emitted 2026-05-18T19:52:38.088551+00:00
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
id: anchor-knots_x_elliptic_curves-00432
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=2337ae098b325a50
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_4` and `torsion` of elliptic_curves `1287.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 2337ae098b325a50 emitted 2026-05-18T19:52:38.169886+00:00
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
id: anchor-knots_x_elliptic_curves-00433
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=c32d2fcab2b70fba
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `7_6` and `conductor` of elliptic_curves `7482.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c32d2fcab2b70fba emitted 2026-05-18T19:52:38.238883+00:00
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
id: anchor-knots_x_elliptic_curves-00434
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=1fef58b310a7a0ad
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `tamagawa_product` of elliptic_curves `4896.r1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1fef58b310a7a0ad emitted 2026-05-18T19:52:38.273883+00:00
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
id: anchor-knots_x_elliptic_curves-00435
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=bf3d234b91457b41
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_4` and `conductor` of elliptic_curves `5175.s2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record bf3d234b91457b41 emitted 2026-05-18T19:52:38.929821+00:00
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
id: anchor-knots_x_elliptic_curves-00436
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=8043dbdbc1d5c244
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_7` and `torsion` of elliptic_curves `3520.y2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8043dbdbc1d5c244 emitted 2026-05-18T19:52:39.225047+00:00
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
id: anchor-knots_x_elliptic_curves-00437
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=657dfffb71d60730
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `tamagawa_product` of elliptic_curves `6358.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 657dfffb71d60730 emitted 2026-05-18T19:52:40.090946+00:00
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
id: anchor-knots_x_elliptic_curves-00438
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=f92db43807de80f5
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
source: Theseus substrate engine record f92db43807de80f5 emitted 2026-05-18T19:52:40.187050+00:00
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
id: anchor-knots_x_elliptic_curves-00439
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=a8527c44b8c8e75e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `10_161` and `torsion` of elliptic_curves `637.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a8527c44b8c8e75e emitted 2026-05-18T19:52:41.218948+00:00
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
id: anchor-knots_x_elliptic_curves-00440
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=a3081c1381c5a03b
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
source: Theseus substrate engine record a3081c1381c5a03b emitted 2026-05-18T19:52:41.255947+00:00
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
id: anchor-knots_x_elliptic_curves-00441
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=c4a86c26231281e4
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_4` and `torsion` of elliptic_curves `1176.e1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c4a86c26231281e4 emitted 2026-05-18T19:52:42.070765+00:00
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
id: anchor-knots_x_elliptic_curves-00442
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=47f72537a7906308
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `7_5` and `tamagawa_product` of elliptic_curves `6370.r3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 47f72537a7906308 emitted 2026-05-18T19:52:43.085243+00:00
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
id: anchor-knots_x_elliptic_curves-00443
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=f6e59ff002dfcb8d
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_7` and `tamagawa_product` of elliptic_curves `4920.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f6e59ff002dfcb8d emitted 2026-05-18T19:52:44.340001+00:00
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
id: anchor-knots_x_elliptic_curves-00444
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=afc2a5225bc23c90
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_17` and `rank` of elliptic_curves `7366.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record afc2a5225bc23c90 emitted 2026-05-18T19:52:44.543839+00:00
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
id: anchor-knots_x_elliptic_curves-00445
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=d913314600ce8d4f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `8_3` and `rank` of elliptic_curves `2751.d4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d913314600ce8d4f emitted 2026-05-18T19:52:44.881186+00:00
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
id: anchor-knots_x_elliptic_curves-00446
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=07705ef29a803176
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `10_124` and `rank` of elliptic_curves `2720.b1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 07705ef29a803176 emitted 2026-05-18T19:52:46.189768+00:00
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
id: anchor-knots_x_elliptic_curves-00447
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=64f2588ed5659aef
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_161` and `rank` of elliptic_curves `8880.n4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 64f2588ed5659aef emitted 2026-05-18T19:52:47.067821+00:00
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
id: anchor-knots_x_elliptic_curves-00448
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=fe7dc10976eca1c6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `7_7` and `tamagawa_product` of elliptic_curves `4920.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record fe7dc10976eca1c6 emitted 2026-05-18T19:52:47.580746+00:00
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
id: anchor-knots_x_elliptic_curves-00449
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=70cccced9d6ca651
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_4` and `torsion` of elliptic_curves `490.j1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 70cccced9d6ca651 emitted 2026-05-18T19:52:48.394742+00:00
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
id: anchor-knots_x_elliptic_curves-00450
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=e092ee3fed43faa9
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
source: Theseus substrate engine record e092ee3fed43faa9 emitted 2026-05-18T19:52:48.896802+00:00
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
id: anchor-knots_x_elliptic_curves-00451
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=18f9e2ae7e102f17
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `4_1` and `torsion` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 18f9e2ae7e102f17 emitted 2026-05-18T19:52:49.619737+00:00
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
id: anchor-knots_x_elliptic_curves-00452
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=c529fcf86519c244
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
source: Theseus substrate engine record c529fcf86519c244 emitted 2026-05-18T19:52:49.827896+00:00
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
id: anchor-knots_x_elliptic_curves-00453
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=d2d31b31d93ba511
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_6` and `tamagawa_product` of elliptic_curves `7350.ct7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d2d31b31d93ba511 emitted 2026-05-18T19:52:49.940979+00:00
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
id: anchor-knots_x_elliptic_curves-00454
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=82d4ee46a1ebd19f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_17` and `conductor` of elliptic_curves `9870.h3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 82d4ee46a1ebd19f emitted 2026-05-18T19:52:50.368829+00:00
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
id: anchor-knots_x_elliptic_curves-00455
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=d5399fe7ba2d7226
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `9_4` and `conductor` of elliptic_curves `4624.d1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record d5399fe7ba2d7226 emitted 2026-05-18T19:52:50.529381+00:00
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
id: anchor-knots_x_elliptic_curves-00456
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=9a40b36e50778007
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_7` and `tamagawa_product` of elliptic_curves `1008.l3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9a40b36e50778007 emitted 2026-05-18T19:52:50.793611+00:00
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
id: anchor-knots_x_elliptic_curves-00457
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=46393dfafa51f01d
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
source: Theseus substrate engine record 46393dfafa51f01d emitted 2026-05-18T19:52:51.384596+00:00
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
id: anchor-knots_x_elliptic_curves-00458
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=812f796f8417fe50
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
source: Theseus substrate engine record 812f796f8417fe50 emitted 2026-05-18T19:52:52.026639+00:00
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
id: anchor-knots_x_elliptic_curves-00459
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=4427ca6b7f4b5881
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `tamagawa_product` of elliptic_curves `7982.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4427ca6b7f4b5881 emitted 2026-05-18T19:52:52.330647+00:00
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
id: anchor-knots_x_elliptic_curves-00460
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=5ca57476271ec5cc
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_7` and `conductor` of elliptic_curves `9282.a1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5ca57476271ec5cc emitted 2026-05-18T19:52:53.843795+00:00
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
id: anchor-knots_x_elliptic_curves-00461
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=4007fa23ec1d77fe
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `rank` of elliptic_curves `7350.ct7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4007fa23ec1d77fe emitted 2026-05-18T19:52:54.105580+00:00
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
id: anchor-knots_x_elliptic_curves-00462
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=7bb1e9887688a69f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_6` and `torsion` of elliptic_curves `5862.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7bb1e9887688a69f emitted 2026-05-18T19:52:54.119580+00:00
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
id: anchor-knots_x_elliptic_curves-00463
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=0161f811a7fb6b1e
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `8_13` and `conductor` of elliptic_curves `9350.o1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 0161f811a7fb6b1e emitted 2026-05-18T19:52:54.132621+00:00
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
id: anchor-knots_x_elliptic_curves-00464
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=710d8fd6c0ecc8e5
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_5` and `tamagawa_product` of elliptic_curves `2400.b2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 710d8fd6c0ecc8e5 emitted 2026-05-18T19:52:54.186621+00:00
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
id: anchor-knots_x_elliptic_curves-00465
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=374d559019b74343
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_9` and `tamagawa_product` of elliptic_curves `5440.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 374d559019b74343 emitted 2026-05-18T19:52:54.431949+00:00
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
id: anchor-knots_x_elliptic_curves-00466
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=38a93d658240f467
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `9_8` and `torsion` of elliptic_curves `8605.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 38a93d658240f467 emitted 2026-05-18T19:52:54.527769+00:00
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
id: anchor-knots_x_elliptic_curves-00467
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=e598d310f0bb290e
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
source: Theseus substrate engine record e598d310f0bb290e emitted 2026-05-18T19:52:55.446300+00:00
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
id: anchor-knots_x_elliptic_curves-00468
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=47f7522c640dc7f7
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
source: Theseus substrate engine record 47f7522c640dc7f7 emitted 2026-05-18T19:52:55.732569+00:00
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
id: anchor-knots_x_elliptic_curves-00469
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=7617409062d07524
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `determinant` of knots
  `6_3` and `torsion` of elliptic_curves `6050.f3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7617409062d07524 emitted 2026-05-18T19:52:55.832141+00:00
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
id: anchor-knots_x_elliptic_curves-00470
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=6cef88bfe10d6f25
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
source: Theseus substrate engine record 6cef88bfe10d6f25 emitted 2026-05-18T19:52:56.561770+00:00
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
id: anchor-knots_x_elliptic_curves-00471
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=9c9dd7985e715547
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_20` and `tamagawa_product` of elliptic_curves `7059.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9c9dd7985e715547 emitted 2026-05-18T19:52:56.734544+00:00
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
id: anchor-knots_x_elliptic_curves-00472
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=a01bd20e4faad002
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `6_3` and `torsion` of elliptic_curves `2028.c2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a01bd20e4faad002 emitted 2026-05-18T19:52:57.623492+00:00
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
id: anchor-knots_x_elliptic_curves-00473
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=8aa1a87437fc4e0a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `7_3` and `tamagawa_product` of elliptic_curves `1960.n2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 8aa1a87437fc4e0a emitted 2026-05-18T19:52:57.669492+00:00
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
id: anchor-knots_x_elliptic_curves-00474
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f29b05417332d285
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `8_7` and `torsion` of elliptic_curves `3472.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f29b05417332d285 emitted 2026-05-18T19:52:57.821584+00:00
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
id: anchor-knots_x_elliptic_curves-00475
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c5d7b57e4925c5db
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `9_1` and `rank` of elliptic_curves `2842.e2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c5d7b57e4925c5db emitted 2026-05-18T19:52:58.052627+00:00
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
id: anchor-knots_x_elliptic_curves-00476
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=48b4cd6f4bc1b10a
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
source: Theseus substrate engine record 48b4cd6f4bc1b10a emitted 2026-05-18T19:52:58.354681+00:00
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
id: anchor-knots_x_elliptic_curves-00477
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=1ce2175704d68e6f
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
source: Theseus substrate engine record 1ce2175704d68e6f emitted 2026-05-18T19:52:59.150555+00:00
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
id: anchor-knots_x_elliptic_curves-00478
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=c90f7ecc5353f84c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_1` and `tamagawa_product` of elliptic_curves `3192.c4`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record c90f7ecc5353f84c emitted 2026-05-18T19:52:59.681477+00:00
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
id: anchor-knots_x_elliptic_curves-00479
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=3603a88955919e2f
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
source: Theseus substrate engine record 3603a88955919e2f emitted 2026-05-18T19:53:00.564316+00:00
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
id: anchor-knots_x_elliptic_curves-00480
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f84315d8ced9f51c
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `three_genus` of knots
  `8_11` and `conductor` of elliptic_curves `9196.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f84315d8ced9f51c emitted 2026-05-18T19:53:01.200855+00:00
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
id: anchor-knots_x_elliptic_curves-00481
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=5e3bb1d27c290996
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `4_1` and `rank` of elliptic_curves `870.c3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 5e3bb1d27c290996 emitted 2026-05-18T19:53:01.419264+00:00
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
id: anchor-knots_x_elliptic_curves-00482
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=9c9f48f7271d7753
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_15` and `rank` of elliptic_curves `1600.p3`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9c9f48f7271d7753 emitted 2026-05-18T19:53:01.736637+00:00
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
id: anchor-knots_x_elliptic_curves-00483
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=a6faa308f4b52c78
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_161` and `tamagawa_product` of elliptic_curves `7350.ct7`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a6faa308f4b52c78 emitted 2026-05-18T19:53:02.094669+00:00
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
id: anchor-knots_x_elliptic_curves-00484
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=f3e5aff42998ad9a
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_1` and `rank` of elliptic_curves `9600.bf1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record f3e5aff42998ad9a emitted 2026-05-18T19:53:02.440411+00:00
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
id: anchor-knots_x_elliptic_curves-00485
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=a759c83e31cd7fc6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_1` and `torsion` of elliptic_curves `3850.u1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a759c83e31cd7fc6 emitted 2026-05-18T19:53:02.839565+00:00
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
id: anchor-knots_x_elliptic_curves-00486
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=4c08e281f88f9bc1
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_124` and `rank` of elliptic_curves `4032.bc1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 4c08e281f88f9bc1 emitted 2026-05-18T19:53:02.922564+00:00
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
id: anchor-knots_x_elliptic_curves-00487
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=7099ef32730b15fd
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `10_145` and `conductor` of elliptic_curves `4480.k1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 7099ef32730b15fd emitted 2026-05-18T19:53:03.215608+00:00
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
id: anchor-knots_x_elliptic_curves-00488
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=1a914cd03d02407f
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_8` and `conductor` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 1a914cd03d02407f emitted 2026-05-18T19:53:03.841702+00:00
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
id: anchor-knots_x_elliptic_curves-00489
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=029ae94193e251b5
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
source: Theseus substrate engine record 029ae94193e251b5 emitted 2026-05-18T19:53:04.340537+00:00
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
id: anchor-knots_x_elliptic_curves-00490
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g5; batch=batch-20260518T195105Z-43a075;
  record_id=e1f01bd913b38fd6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g5 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `10_139` and `conductor` of elliptic_curves `862.f2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record e1f01bd913b38fd6 emitted 2026-05-18T19:53:04.640201+00:00
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
id: anchor-knots_x_elliptic_curves-00491
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=3cb1b7326ae329c6
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `6_1` and `rank` of elliptic_curves `2016.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 3cb1b7326ae329c6 emitted 2026-05-18T19:53:05.249375+00:00
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
id: anchor-knots_x_elliptic_curves-00492
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=132e95b05f0c2714
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `9_8` and `rank` of elliptic_curves `7982.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 132e95b05f0c2714 emitted 2026-05-18T19:53:05.276373+00:00
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
id: anchor-knots_x_elliptic_curves-00493
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=a80210fa889f8958
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
source: Theseus substrate engine record a80210fa889f8958 emitted 2026-05-18T19:53:05.636405+00:00
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
id: anchor-knots_x_elliptic_curves-00494
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=2b8dcbadb9cbf321
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
source: Theseus substrate engine record 2b8dcbadb9cbf321 emitted 2026-05-18T19:53:05.711083+00:00
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
id: anchor-knots_x_elliptic_curves-00495
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=g4; batch=batch-20260518T195105Z-43a075;
  record_id=02a759d3f3e8cdb9
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from g4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `signature` of knots
  `5_2` and `torsion` of elliptic_curves `1584.s1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 02a759d3f3e8cdb9 emitted 2026-05-18T19:53:05.904480+00:00
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
id: anchor-knots_x_elliptic_curves-00496
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=228b08c06b207dbd
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
source: Theseus substrate engine record 228b08c06b207dbd emitted 2026-05-18T19:53:06.475443+00:00
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
id: anchor-knots_x_elliptic_curves-00497
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c3; batch=batch-20260518T195105Z-43a075;
  record_id=9a4779eb735d0256
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c3 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `crossing_number` of
  knots `8_4` and `rank` of elliptic_curves `3842.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 9a4779eb735d0256 emitted 2026-05-18T19:53:07.220461+00:00
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
id: anchor-knots_x_elliptic_curves-00498
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c4; batch=batch-20260518T195105Z-43a075;
  record_id=a815350e176c2bec
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c4 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `nf_class_number` of
  knots `10_124` and `rank` of elliptic_curves `8605.c1`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record a815350e176c2bec emitted 2026-05-18T19:53:07.327573+00:00
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
id: anchor-knots_x_elliptic_curves-00499
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=h4; batch=batch-20260518T195105Z-43a075;
  record_id=525407aefef573ed
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
source: Theseus substrate engine record 525407aefef573ed emitted 2026-05-18T19:53:08.608388+00:00
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
id: anchor-knots_x_elliptic_curves-00500
domain: knots_x_elliptic_curves
anchor_type: predicate
dataset_source: Theseus substrate engine (v0.3); generator=c1; batch=batch-20260518T195105Z-43a075;
  record_id=135a6317a289ba03
dataset_license: Project-internal (Prometheus / Theseus engine output)
scale:
  instance_count: 1
  coverage_qualifier: Single substrate-verified instance from c1 emission; relation=equal_mod_2;
    verdict=SHADOW_CATALOG
prompt_template: Does the relation `equal_mod_2` hold between `trace_field_class`
  of knots `9_3` and `torsion` of elliptic_curves `5376.a2`? Return boolean.
expected_answer_shape: "bool \u2014 True iff the relation holds for the given object\
  \ pair"
verification_method: computational_certified
trust_tier: numerically_certified
source: Theseus substrate engine record 135a6317a289ba03 emitted 2026-05-18T19:53:09.944492+00:00
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

