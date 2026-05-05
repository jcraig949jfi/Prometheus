# Trial 3 Surprise-Predicate Investigation

**Predicate:** `{'neg_z': 3, 'pos_x': 4, 'neg_y': 1}`
**Verdict:** **LIKELY_ARTIFACT_PLANTED_OVERLAP**

## Corpus structure
- Total entries: 150
- Total kills: 13 (baseline rate 0.0867)
- OBSTRUCTION_SIGNATURE matches: 8 (all killed: 8)
- SECONDARY_SIGNATURE matches: 4 (all killed: 4)
- Other (noise) kills: 1

## Surprise-predicate full lift evaluation
- Match-group size:    1
- Matched kill rate:   1.0000
- Baseline kill rate:  0.0805
- Lift:                12.4167

## Matched records
- Record 0: kill=True [ALSO_SECONDARY]
  features: {'n_steps': 7, 'neg_x': 2, 'pos_x': 4, 'neg_y': 1, 'pos_y': 0, 'neg_z': 3, 'pos_z': 3, 'has_diag_neg': False, 'has_diag_pos': True}

## Non-overlap analysis
(removing records that ALSO match planted signatures, recompute lift)
- Non-overlap match-group size: 0
- Non-overlap kills:            0
- Non-overlap kill rate:        0.0000
- Baseline kill rate:           0.0000
- Non-overlap lift:             0.0000

## Verdict interpretation
The predicate has a small match-group overlapping a planted signature. The high lift comes from the planted matches being kills by construction, NOT from independent signal. **Substrate-grade interpretation: this is the engine partially-rediscovering the planted signal via a coarser conjunctive predicate. Useful for validating selection pressure works; not a separate discovery.**