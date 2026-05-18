# Cross-Catalog H4 Audit Report

Generated: 2026-05-18T21:06:35.033037+00:00

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
| equal | 11 / 118 | 9.3% |
| equal_mod_2 | 616 / 984 | 62.6% |
| divides | 413 / 663 | 62.3% |
| abs_diff_le_3 | 188 / 487 | 38.6% |

### Stratified by parent_inv_b

| parent_inv_b | relation | rate |
|---|---|---|
| analytic_rank | abs_diff_le_3 | 65/150 = 43.3% |
| torsion_order | abs_diff_le_3 | 65/172 = 37.8% |
| mw_rank | abs_diff_le_3 | 58/165 = 35.2% |
| torsion_order | divides | 60/73 = 82.2% |
| abs_disc | divides | 84/123 = 68.3% |
| conductor | divides | 78/127 = 61.4% |
| analytic_rank | divides | 97/169 = 57.4% |
| mw_rank | divides | 94/171 = 55.0% |
| torsion_order | equal | 5/41 = 12.2% |
| analytic_rank | equal | 3/32 = 9.4% |
| mw_rank | equal | 3/45 = 6.7% |
| abs_disc | equal_mod_2 | 131/186 = 70.4% |
| conductor | equal_mod_2 | 146/208 = 70.2% |
| mw_rank | equal_mod_2 | 128/206 = 62.1% |
| analytic_rank | equal_mod_2 | 117/201 = 58.2% |
| torsion_order | equal_mod_2 | 94/183 = 51.4% |

## Audit: knot × modular_forms (n=8,000)

### Aggregate rates

| relation | categorical / held | rate |
|---|---|---|
| equal | 0 / 99 | 0.0% |
| equal_mod_2 | 556 / 957 | 58.1% |
| divides | 397 / 784 | 50.6% |
| abs_diff_le_3 | 289 / 547 | 52.8% |

### Stratified by parent_inv_b

| parent_inv_b | relation | rate |
|---|---|---|
| a_p_5 | abs_diff_le_3 | 52/73 = 71.2% |
| a_p_3 | abs_diff_le_3 | 67/106 = 63.2% |
| a_p_2 | abs_diff_le_3 | 56/99 = 56.6% |
| char_order | abs_diff_le_3 | 59/131 = 45.0% |
| weight | abs_diff_le_3 | 55/135 = 40.7% |
| char_order | divides | 34/35 = 97.1% |
| weight | divides | 67/104 = 64.4% |
| level | divides | 90/161 = 55.9% |
| a_p_5 | divides | 76/146 = 52.1% |
| a_p_2 | divides | 72/187 = 38.5% |
| a_p_3 | divides | 58/151 = 38.4% |
| a_p_2 | equal | 0/20 = 0.0% |
| weight | equal | 0/31 = 0.0% |
| char_order | equal | 0/27 = 0.0% |
| level | equal_mod_2 | 110/162 = 67.9% |
| a_p_2 | equal_mod_2 | 105/161 = 65.2% |
| a_p_3 | equal_mod_2 | 104/161 = 64.6% |
| a_p_5 | equal_mod_2 | 89/149 = 59.7% |
| weight | equal_mod_2 | 106/189 = 56.1% |
| char_order | equal_mod_2 | 42/135 = 31.1% |

## Audit: knot × oeis_sleeping (n=8,000)

### Aggregate rates

| relation | categorical / held | rate |
|---|---|---|
| equal | 0 / 57 | 0.0% |
| equal_mod_2 | 457 / 1030 | 44.4% |
| divides | 281 / 601 | 46.8% |
| abs_diff_le_3 | 0 / 400 | 0.0% |

### Stratified by parent_inv_b

| parent_inv_b | relation | rate |
|---|---|---|
| first_value | abs_diff_le_3 | 0/202 = 0.0% |
| second_value | abs_diff_le_3 | 0/181 = 0.0% |
| first_value | divides | 43/61 = 70.5% |
| second_value | divides | 75/123 = 61.0% |
| a_number_int | divides | 67/131 = 51.1% |
| seq_len | divides | 96/286 = 33.6% |
| second_value | equal | 0/27 = 0.0% |
| first_value | equal | 0/30 = 0.0% |
| a_number_int | equal_mod_2 | 161/281 = 57.3% |
| second_value | equal_mod_2 | 102/222 = 45.9% |
| seq_len | equal_mod_2 | 123/307 = 40.1% |
| first_value | equal_mod_2 | 71/220 = 32.3% |

## Replication verdict

- **equal_mod_2**: ref 67.2% vs new 62.6% (drift -4.6pp) → REPLICATES
- **divides**: ref 50.7% vs new 62.3% (drift +11.6pp) → DIFFERS
- **equal**: ref 2.6% vs new 9.3% (drift +6.7pp) → REPLICATES
