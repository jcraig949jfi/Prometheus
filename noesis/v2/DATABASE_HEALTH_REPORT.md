# Noesis v2 Database Health Report

**Generated:** 2026-03-29
**Agent:** Aletheia
**Database:** `noesis_v2.duckdb` (11.3 MB)

---

## 1. Table-by-Table Row Counts

| Table | Rows | Columns |
|-------|-----:|--------:|
| abstract_compositions | 242 | 5 |
| chain_steps | 400 | 6 |
| chains | 100 | 11 |
| composition_instances | 4,694 | 6 |
| cross_domain_edges | 2,634 | 6 |
| cross_domain_links | 185 | 8 |
| damage_operators | 9 | 6 |
| discoveries | 35 | 11 |
| ethnomathematics | 153 | 17 |
| operations | 1,714 | 9 |
| prime_landscape | 6 | 12 |
| transformations | 295 | 10 |
| validation_pairs | 6 | 16 |
| **TOTAL** | **10,468** | |

The database contains 13 tables with 10,468 total rows across 126 distinct columns. The bulk of the data lives in `composition_instances` (4,694), `cross_domain_edges` (2,634), and `operations` (1,714).

---

## 2. Fill Rate (Damage Operator x Hub Matrix)

### Cross-Domain Links Matrix
- **Hubs tracked:** 15
- **Operators in use:** 8
- **Total cells:** 120
- **Filled cells:** 73
- **Fill rate:** 60.83%

### Numpy Tensor (damage_hub_matrix.npy)
- **Shape:** 7 x 20 (operators x hubs)
- **Total cells:** 140
- **Filled cells:** 93
- **Fill rate:** 66.43%

### Tensor Prediction Trajectory (from prediction_stability.jsonl)
The fill rate evolved across 9 tensor rebuilds:

| Timestamp | Hubs | Spokes | Fill Rate | Filled Cells | Consensus | Predictions >0.3 |
|-----------|-----:|-------:|----------:|-------------:|----------:|------------------:|
| 2026-03-29 21:33 | 239 | 345 | 8.04% | 173 | 6 | 1,978 |
| 2026-03-29 23:25 | 239 | 1,800 | 70.94% | 1,526 | 8 | 625 |
| 2026-03-29 23:41 | 239 | 2,216 | 90.28% | 1,942 | 5 | 209 |
| 2026-03-30 00:01 | 239 | 2,496 | 93.86% | 2,019 | 18 | 132 |
| 2026-03-30 00:24 | 242 | 2,512 | 93.43% | 2,035 | 18 | 143 |
| 2026-03-30 00:32 | 242 | 4,563 | 93.76% | 2,042 | 19 | 136 |
| **2026-03-30 00:43** | **242** | **4,671** | **98.30%** | **2,141** | **24** | **37** |

**Current tensor fill: 98.3%** -- only 37 cells remain above prediction threshold. The tensor is near-saturated.

---

## 3. Operator Coverage Distribution

### Coverage in cross_domain_links (how many hubs each operator touches):

| Operator | Hubs Covered |
|----------|-------------:|
| HIERARCHIZE | 13 |
| TRUNCATE | 12 |
| DISTRIBUTE | 11 |
| RANDOMIZE | 10 |
| CONCENTRATE | 10 |
| PARTITION | 9 |
| EXTEND | 4 |
| EXPAND | 4 |

Note: QUANTIZE, INVERT are absent from cross_domain_links entirely. EXPAND is not one of the canonical 9.

### Edge volume by operator (cross_domain_edges):

| Operator | Edges | Unique Sources | Unique Targets |
|----------|------:|---------------:|---------------:|
| TRUNCATE | 462 | 105 | 47 |
| COMPLETE(fails) | 404 | 4 | 101 |
| COMPLETE | 403 | 5 | 121 |
| DISTRIBUTE | 276 | 43 | 33 |
| COMPOSE | 202 | 40 | 47 |
| HIERARCHIZE | 178 | 24 | 25 |
| PARTITION | 157 | 37 | 29 |
| CONCENTRATE | 145 | 22 | 23 |
| RANDOMIZE | 133 | 26 | 24 |
| EXTEND | 90 | 30 | 20 |
| SYMMETRIZE | 73 | 8 | 16 |
| EXTEND+COMPOSE | 56 | 4 | 14 |
| DUALIZE | 20 | 5 | 4 |
| INVERT | 14 | 1 | 14 |
| REDUCE | 9 | 6 | 6 |
| EXPAND | 7 | 4 | 4 |
| QUANTIZE | 3 | 3 | 2 |

TRUNCATE dominates edge volume. INVERT and QUANTIZE are underrepresented.

---

## 4. Hub Completion Distribution

Of the 11 hubs with discoveries recorded:

| Completion | Count | Hubs |
|------------|------:|------|
| 2/9 | 3 | BINARY_DECOMP_RECOMP, PHYS_SYMMETRY_CONSTRUCTION, RECURSIVE_SPATIAL_EXTENSION |
| 1/9 | 8 | RIGIDITY_MOSTOW, CARNOT_LIMIT, ALGEBRAIC_COMPLETION, BROUWER_FIXED_POINT, IMPOSSIBILITY_HOLEVO_BOUND, CROSS_DOMAIN_DUALITY, HEISENBERG_UNCERTAINTY, IMPOSSIBILITY_MAP_PROJECTION |
| 0/9 | 0 | (all tracked hubs have at least 1) |

**Maximum completion: 2/9.** No hub has more than 2 of 9 operators resolved. This is a major growth frontier.

---

## 5. Spoke Source Distribution

### Cross-domain edge provenance:
| Source | Edges |
|--------|------:|
| aletheia_overnight | 1,168 |
| aletheia_overnight_isolated | 1,137 |
| tradition_hub_mapping (aletheia) | ~211 |
| aletheia_manual | 82 |
| gemini_part1 | 30 |
| gemini_part2 | 6 |

**Aletheia fills account for 97.6% of all cross-domain edges.** Gemini batch contributions are minimal (36 edges, 1.4%).

### Chain sources (perfectly balanced):
| Source | Chains |
|--------|-------:|
| claude | 20 |
| chatgpt | 20 |
| council | 20 |
| grok | 20 |
| gemini | 20 |

### Discovery methods:
| Method | Count |
|--------|------:|
| archaeological_prediction | 30 |
| tensor_consensus_prediction | 5 |

---

## 6. Cross-Domain Edge Statistics

| Metric | Value |
|--------|------:|
| **Total edges** | 2,634 |
| **Total links** | 185 |
| **Unique nodes** | 408 |
| **Graph density** | 0.0317 (3.2%) |

### Edge types:
| Type | Count | % |
|------|------:|--:|
| computed_similarity | 1,168 | 44.3% |
| computed_hub_bridge | 1,126 | 42.8% |
| tradition_hub_mapping | 211 | 8.0% |
| structural_kinship | 57 | 2.2% |
| analog | 30 | 1.1% |
| tuning_bridge | 25 | 0.9% |
| hub_bridge | 11 | 0.4% |
| validated_* | 6 | 0.2% |

### Link types:
| Type | Count |
|------|------:|
| existing_hub | 154 |
| new_hub | 31 |

The graph is sparse (3.2% density) with 408 nodes and 2,634 edges. Automated computed edges (similarity + hub_bridge) make up 87.1% of total.

---

## 7. Discovery Log

**Total discoveries: 35**

| Status | Count |
|--------|------:|
| PREDICTED | 30 |
| VERIFIED_EXACT | 4 |
| STRUCTURALLY_IMPOSSIBLE | 1 |

### Verified discoveries (tensor consensus):
1. **DISC_001:** BROUWER_FIXED_POINT + CONCENTRATE = Newton-Raphson method (score: 0.70)
2. **DISC_002:** HOLEVO_BOUND + CONCENTRATE = Pretty Good Measurement (score: 0.69)
3. **DISC_003:** HEISENBERG_UNCERTAINTY + DISTRIBUTE = Weak measurement / AAV (score: 0.64)
4. **DISC_004:** CARNOT_LIMIT + DISTRIBUTE = Stirling/Ericsson regenerative cycles (score: 0.64)

### Structurally impossible:
- **DISC_005:** RIGIDITY_MOSTOW + DISTRIBUTE -- rigidity precludes resolution (score: 0.70)

### Archaeological predictions (top 5 by score):
| ID | Hub | Tradition/System | Score |
|----|-----|-----------------|------:|
| DISC_006 | PHYS_SYMMETRY_CONSTRUCTION | Chinese Remainder Algorithm | 1.000 |
| DISC_007 | BINARY_DECOMP_RECOMP | Jain Combinatorics | 0.999 |
| DISC_008 | BINARY_DECOMP_RECOMP | Computus Calendar Calculation | 0.982 |
| DISC_009 | CROSS_DOMAIN_DUALITY | Sexagesimal Positional System | 0.937 |
| DISC_010 | RECURSIVE_SPATIAL_EXTENSION | Pingala Prosody Combinatorics | 0.865 |

Score range for all 30 archaeological predictions: 0.676 -- 1.000.

---

## 8. Ethnomathematics Coverage

| Metric | Value |
|--------|------:|
| Total systems | 153 |
| Unique traditions | 71 |
| Systems with composition instances | 16 |
| Systems with enriched vectors | 153 (100%) |
| Systems with classification | 151 (98.7%) |
| **Orphaned (no composition link)** | **137 (89.5%)** |

### Top traditions by system count:
| Tradition | Systems |
|-----------|--------:|
| Modern | 14 |
| Islamic | 11 |
| Chinese | 8 |
| African | 5 |
| Ancient Egyptian | 4 |
| Japanese | 4 |
| Polynesian | 4 |
| Greek | 4 |
| European | 4 |

**Warning:** 137 of 153 ethnomathematics systems (89.5%) have no composition instances linking them to the hub-spoke structure. All 153 have enriched primitive vectors, so the data exists for linking -- it just has not been ingested into composition_instances yet.

---

## 9. Chain and Transformation Statistics

| Metric | Value |
|--------|------:|
| Total chains | 100 |
| Verified chains | 100 (100%) |
| Total chain steps | 400 |
| Avg steps per chain | 4.0 |
| Total transformations | 295 |
| Invertible | 0 (0%) |
| Non-invertible | 295 (100%) |

### Primitive type distribution in transformations:
| Primitive | Count | % |
|-----------|------:|--:|
| MAP | 106 | 35.9% |
| REDUCE | 40 | 13.6% |
| DUALIZE | 31 | 10.5% |
| LINEARIZE | 29 | 9.8% |
| SYMMETRIZE | 21 | 7.1% |
| BREAK_SYMMETRY | 19 | 6.4% |
| EXTEND | 18 | 6.1% |
| STOCHASTICIZE | 17 | 5.8% |
| LIMIT | 6 | 2.0% |
| COMPLETE | 5 | 1.7% |
| COMPOSE | 3 | 1.0% |

**Note:** All 295 transformations are marked non-invertible. This may be a data issue (defaults not set) rather than a genuine structural finding -- worth verifying.

---

## 10. Data Quality Checks

### Primary key integrity:
- NULL primary keys: **NONE** -- all clean

### Referential integrity:
| Check | Result |
|-------|--------|
| Duplicate instance_ids | 0 |
| Orphan composition_instances (no matching abstract_composition) | **147** |
| Orphan chain_steps (no matching chain) | 0 |

### Non-canonical operators:

**In discoveries table:**
- COMPOSE, REDUCE, SYMMETRIZE

These are structural primitives, not damage operators. The discoveries table conflates primitive types with damage operator names.

**In cross_domain_edges:**
- COMPLETE, COMPLETE(fails), SYMMETRIZE, EXTEND+COMPOSE, EXPAND, DUALIZE, REDUCE, COMPOSE
- "None. (LIMIT/TRUNCATE vs DISTRIBUTE)."
- "None. (EXTEND vs DISTRIBUTE)."

**10 non-canonical operator labels** appear in cross_domain_edges. These are primitive operation names being used in the `shared_damage_operator` column rather than the canonical 9 damage operators (CONCENTRATE, DISTRIBUTE, EXTEND, HIERARCHIZE, INVERT, PARTITION, QUANTIZE, RANDOMIZE, TRUNCATE).

### Summary of quality issues:

| Issue | Severity | Count |
|-------|----------|------:|
| Orphan composition_instances | MEDIUM | 147 |
| Non-canonical operators in edges | MEDIUM | 10 distinct values |
| Non-canonical operators in discoveries | LOW | 3 distinct values |
| All transforms non-invertible | LOW (likely default) | 295 |
| Ethno systems without compositions | LOW | 137 |

---

## 11. Tensor Prediction History

9 tensor rebuilds tracked in `prediction_stability.jsonl`.

### Trajectory summary:

| Phase | Fill Rate | Spokes | Consensus Predictions |
|-------|----------:|-------:|----------------------:|
| Initial (build 1) | 8.0% | 345 | 6 |
| Densification (build 2-3) | 70.9% -> 90.3% | 1,800 -> 2,216 | 8 -> 5 |
| Saturation (build 4-7) | 93.4% -> 98.3% | 2,496 -> 4,671 | 18 -> 24 |

Key observations:
- Fill rate climbed from 8% to 98.3% across 9 rebuilds
- Spokes grew 13.5x (345 to 4,671)
- Consensus predictions grew from 6 to 24 as the tensor stabilized
- Remaining predictions above 0.3 threshold: **37** (down from 1,978)
- SVD rank stable at 5; Tucker rank stable at [3, 10, 5]

---

## 12. Archaeological Prediction Statistics

The `archaeological_predictions.json` file contains:
- **Top 30 predictions** (stored in discoveries as DISC_006 through DISC_035)
- Predictions organized by damage operator, hub, and tradition

The `novel_predictions.json` file contains:
- **13 assessments** of prediction novelty
- Categories: known, novel, uncertain

### Archaeological predictions by hub (from discoveries):
| Hub | Predictions |
|-----|------------:|
| CROSS_DOMAIN_DUALITY | 9 |
| RECURSIVE_SPATIAL_EXTENSION | 8 |
| BINARY_DECOMP_RECOMP | 4 |
| PHYS_SYMMETRY_CONSTRUCTION | 4 |
| IMPOSSIBILITY_MAP_PROJECTION | 1 |
| ALGEBRAIC_COMPLETION | 1 |

Score distribution: min=0.676, max=1.000, mean~0.77

---

## 13. Operations Coverage

- **Total operations:** 1,714
- **Unique fields:** 173+

Top fields by operation count (all have 10-12 operations each):
invariant_extractors (12), category_composition (12), multiscale_operators (11), navya_nyaya_logic (11), formal_logic_systems (11), geometric_algebra (11), reversible_computing (11), dynamical_systems (11), spectral_transforms (11), ...

The operations table provides dense coverage across 173+ mathematical fields with 10-12 operations per field on average.

### Composition overview:
| Metric | Value |
|--------|------:|
| Abstract compositions | 242 |
| Composition instances | 4,694 |
| Unique systems in instances | 241 |
| Unique traditions in instances | 61 |
| Unique domains in instances | 30 |

---

## Overall Health Assessment

### Strengths
1. **Near-complete tensor fill (98.3%)** -- the core damage-operator x hub tensor is almost saturated
2. **Zero NULL primary keys, zero duplicate instance_ids** -- structural integrity is solid
3. **100% chain verification** -- all 100 chains pass their tests
4. **Balanced chain sourcing** -- 5 models x 20 chains each, no single-source bias
5. **Rich ethnomathematics enrichment** -- all 153 systems have primitive vectors
6. **4 verified exact discoveries** -- tensor predictions confirmed against literature

### Weaknesses
1. **147 orphan composition_instances** -- 3.1% of instances reference non-existent abstract_compositions
2. **10 non-canonical operator labels in edges** -- naming inconsistency between primitives and damage operators
3. **89.5% ethnomathematics orphaned** -- 137 systems lack composition instance linkage
4. **Hub completion maxes at 2/9** -- no hub has been fully mapped across all 9 damage operators
5. **All transformations marked non-invertible** -- likely a default/data issue
6. **INVERT and QUANTIZE underrepresented** -- minimal edge coverage for these operators
7. **97.6% of edges from one agent (Aletheia)** -- low source diversity in cross-domain graph

### Priority Actions
1. Link orphan ethnomathematics systems to composition_instances
2. Normalize non-canonical operator names in cross_domain_edges
3. Investigate the 147 orphan composition_instances
4. Push hub completion beyond 2/9 for top hubs
5. Densify INVERT and QUANTIZE operator coverage
6. Audit invertibility flags on transformations
