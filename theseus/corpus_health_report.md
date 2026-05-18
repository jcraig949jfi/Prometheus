# Theseus Corpus Health Report

Generated: 2026-05-18T16:29:22.419078+00:00
Corpus files scanned: 9

## Volume

- Total emissions across all corpus files: **483,277**
- Unique record_ids (cross-batch deduplicated): **394,623**
- Cross-batch duplicates: 88,654
- Cross-batch dedup rate: **81.7%** unique

## Verdict distribution (across all unique records)

- **REJECTED**: 255,375 (64.7%)
- **SHADOW_CATALOG**: 125,222 (31.7%)
- **INCONCLUSIVE**: 14,026 (3.6%)

## H4 cross-catalog bridge extensibility (per-relation)

- **equal_mod_2**: 2,818/4,192 = **67.2%** categorical
- **abs_diff_le_***: 2,710/4,045 = **67.0%** categorical
- **divides**: 1,082/2,136 = **50.7%** categorical
- **equal**: 10/411 = **2.4%** categorical

Reference: Fires #13-14 seed-confirmed rates were parity ~63%, divides ~40%, equal ~2%.

## Per-generator record counts

- **a1**: 71,984
- **f4**: 50,861
- **c1**: 40,858
- **c3**: 33,049
- **f3**: 32,698
- **a3**: 32,694
- **a2**: 30,004
- **c2**: 15,934
- **d3**: 14,896
- **a4**: 14,759
- **h2**: 14,616
- **d2**: 11,241
- **h4**: 10,784
- **c5**: 9,014
- **b2**: 3,636
- **a5**: 2,308
- **d1**: 2,112
- **b1**: 1,340
- **e3**: 1,060
- **c4**: 396
- **h1**: 379

## Top high-weight records (Ergon training candidates)

- `0.6500` | c1 | SHADOW_CATALOG
   MUT[a]:trace_field_class(knot:8_3) equal_mod_2 tamagawa_product(ec:8528.h4) | 6 vs 4 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[b:torsion→rank] crossing_number(knot:8_21) equal_mod_2 rank(ec:4845.b1) | 8 vs 0 | holds=True
- `0.6500` | a1 | SHADOW_CATALOG
   determinant(knot:7_7) equal_mod_2 torsion(ec:9702.bn2) | 21 vs 1 | holds=True
- `0.6500` | c1 | SHADOW_CATALOG
   MUT[a]:trace_field_class(knot:8_9) equal_mod_2 tamagawa_product(ec:5334.a1) | 6 vs 8 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[b:conductor→torsion] trace_field_class(knot:10_152) equal_mod_2 torsion(ec:990.e3) | 6 vs 6 | holds=True
- `0.6500` | c1 | SHADOW_CATALOG
   MUT[b]:trace_field_class(knot:8_11) equal_mod_2 tamagawa_product(ec:8528.h4) | 6 vs 4 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[b:torsion→conductor] trace_field_class(knot:8_11) equal_mod_2 conductor(ec:5334.a1) | 6 vs 5334 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[a:trace_field_class→three_genus] three_genus(knot:10_152) equal_mod_2 conductor(ec:990.e3) | 4 vs 990 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[b:torsion→tamagawa_product] trace_field_class(knot:8_11) equal_mod_2 tamagawa_product(ec:5334.a1) | 6 vs 8 | holds=True
- `0.6500` | a1 | SHADOW_CATALOG
   trace_field_class(knot:9_2) equal_mod_2 conductor(ec:2160.f1) | 6 vs 2160 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[b:conductor→tamagawa_product] trace_field_class(knot:10_152) equal_mod_2 tamagawa_product(ec:990.e3) | 6 vs 48 | holds=True
- `0.6500` | a1 | SHADOW_CATALOG
   crossing_number(knot:8_13) equal_mod_2 rank(ec:288.c4) | 8 vs 0 | holds=True
- `0.6500` | a1 | SHADOW_CATALOG
   crossing_number(knot:7_5) equal_mod_2 rank(ec:3136.t1) | 7 vs 1 | holds=True
- `0.6500` | c3 | SHADOW_CATALOG
   C3_SLIDE[b:conductor→torsion] trace_field_class(knot:8_11) equal_mod_2 torsion(ec:5334.a1) | 6 vs 2 | holds=True
- `0.6500` | c1 | SHADOW_CATALOG
   MUT[a]:trace_field_class(knot:7_7) equal_mod_2 conductor(ec:7776.c1) | 6 vs 7776 | holds=True

## Verdict evolution across batches (chronological)

- **batch-20260518T144818Z-b71b10** (n=49,258): REJ 70% / SHADOW 9% / INC 20%
- **batch-20260518T144918Z-b330d0** (n=117,446): REJ 60% / SHADOW 39% / INC 1%
- **batch-20260518T145649Z-b59e66** (n=106,522): REJ 75% / SHADOW 25% / INC 0%
- **batch-20260518T150429Z-e7276a** (n=81,672): REJ 57% / SHADOW 43% / INC 0%
- **batch-20260518T151213Z-627be2** (n=22,828): REJ 52% / SHADOW 38% / INC 10%
- **batch-20260518T151353Z-aab13b** (n=212): REJ 49% / SHADOW 41% / INC 11%
- **batch-20260518T151528Z-400b29** (n=15,864): REJ 72% / SHADOW 28% / INC 0%
- **batch-20260518T151926Z-8ea29a** (n=821): REJ 72% / SHADOW 28% / INC 0%
