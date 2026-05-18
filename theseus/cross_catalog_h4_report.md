# Cross-Catalog H4 Audit Report

Generated: 2026-05-18T18:06:23.273636+00:00

## Reference (knot × EC, from corpus_health Fire #19)

| relation | rate |
|---|---|
| equal | 2.6% |
| equal_mod_2 | 67.2% |
| divides | 50.7% |
| abs_diff_le_3 | 65.0% |

## Audit: knot × genus2 (n=8,000)

### Aggregate rates

| relation | categorical / held | rate |
|---|---|---|
| equal | 10 / 100 | 10.0% |
| equal_mod_2 | 534 / 974 | 54.8% |
| divides | 323 / 575 | 56.2% |
| abs_diff_le_3 | 270 / 527 | 51.2% |

### Stratified by parent_inv_b

| parent_inv_b | relation | rate |
|---|---|---|
| mw_rank | abs_diff_le_3 | 84/150 = 56.0% |
| analytic_rank | abs_diff_le_3 | 72/136 = 52.9% |
| torsion_order | abs_diff_le_3 | 63/131 = 48.1% |
| disc_sign | abs_diff_le_3 | 51/110 = 46.4% |
| disc_sign | divides | 20/20 = 100.0% |
| torsion_order | divides | 53/59 = 89.8% |
| conductor | divides | 73/135 = 54.1% |
| abs_disc | divides | 55/105 = 52.4% |
| mw_rank | divides | 66/136 = 48.5% |
| analytic_rank | divides | 56/120 = 46.7% |
| mw_rank | equal | 5/29 = 17.2% |
| analytic_rank | equal | 3/28 = 10.7% |
| torsion_order | equal | 0/28 = 0.0% |
| conductor | equal_mod_2 | 120/167 = 71.9% |
| abs_disc | equal_mod_2 | 119/182 = 65.4% |
| analytic_rank | equal_mod_2 | 87/160 = 54.4% |
| torsion_order | equal_mod_2 | 90/171 = 52.6% |
| mw_rank | equal_mod_2 | 84/170 = 49.4% |
| disc_sign | equal_mod_2 | 34/124 = 27.4% |

## Replication verdict

- **equal_mod_2**: ref 67.2% vs new 54.8% (drift -12.4pp) → DIFFERS
- **divides**: ref 50.7% vs new 56.2% (drift +5.5pp) → REPLICATES
- **equal**: ref 2.6% vs new 10.0% (drift +7.4pp) → REPLICATES
