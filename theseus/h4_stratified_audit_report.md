# H4 Stratified Audit Report

Generated: 2026-05-18T17:02:08.762636+00:00
Corpus files: 9
H4 records analyzed: 19,667

## Verdict on parity > divides > equal hierarchy

**Test**: do the categorical-rate findings hold uniformly across
ec_invariants, or are they driven by specific small-range invariants
(suspected: tamagawa_product)?

## Aggregate relation rates (for reference)

- **equal_mod_2**: 5,602/8,336 = 67.2%
- **abs_diff_le_***: 3,595/6,257 = 57.5%
- **divides**: 2,154/4,255 = 50.6%
- **equal**: 20/819 = 2.4%

## Per-(ec_invariant, relation) stratified rates

Sorted by relation then by rate descending.

| ec_invariant | relation | shadow/total | rate |
|---|---|---|---|
| rank | abs_diff_le_* | 2399/3336 | 71.9% |
| tamagawa_product | abs_diff_le_* | 679/1245 | 54.5% |
| torsion | abs_diff_le_* | 517/1676 | 30.8% |
| rank | divides | 174/192 | 90.6% |
| torsion | divides | 653/743 | 87.9% |
| tamagawa_product | divides | 686/1364 | 50.3% |
| conductor | divides | 641/1956 | 32.8% |
| torsion | equal | 8/250 | 3.2% |
| tamagawa_product | equal | 6/194 | 3.1% |
| rank | equal | 6/375 | 1.6% |
| torsion | equal_mod_2 | 1350/1894 | 71.3% |
| tamagawa_product | equal_mod_2 | 1506/2119 | 71.1% |
| conductor | equal_mod_2 | 1509/2330 | 64.8% |
| rank | equal_mod_2 | 1237/1993 | 62.1% |

## Within-relation variance across ec_invariants

If a relation's rate varies wildly across ec_invariants,
the aggregate is artifact-laden. If rates cluster tightly,
the relation has uniform structural meaning.

### equal_mod_2
- n_invariants analyzed: 4
- mean rate: 67.3%
- min: 62.1% | max: 71.3%
- range: 9.2 percentage points
- stdev: 4.0pp

### divides
- n_invariants analyzed: 4
- mean rate: 65.4%
- min: 32.8% | max: 90.6%
- range: 57.9 percentage points
- stdev: 24.7pp

### abs_diff_le_*
- n_invariants analyzed: 3
- mean rate: 52.4%
- min: 30.8% | max: 71.9%
- range: 41.1 percentage points
- stdev: 16.8pp

### equal
- n_invariants analyzed: 3
- mean rate: 2.6%
- min: 1.6% | max: 3.2%
- range: 1.6 percentage points
- stdev: 0.7pp

