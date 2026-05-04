# Iter 17 archive inspection (seed=42, n_eps=1000)

- Total cells filled: **46**
- Cells by winning operator class:
  - structural: 39
  - symbolic: 3
  - anti_prior: 2
  - uniform: 1
  - structured_null: 1

## partition_refinement (9 cells)

| dag_h | type | mag | dist | fitness | op | n_evals | hash | predicate |
|---|---|---|---|---|---|---|---|---|
| 0 | other | 2 | 4 | (1,2,0.98,1.00) | structural | 17 | `835a48fb` | `{'pos_x': 1}` |
| 1 | other | 2 | 4 | (1,2,0.92,1.00) | structural | 15 | `b435ebee` | `{'n_steps': 5}` |
| 2 | other | 2 | 4 | (1,2,0.88,1.00) | structural | 8 | `39dfebdb` | `{'n_steps': 5, 'pos_y': 2}` |
| 1 | other | 1 | 4 | (1,2,0.71,1.00) | structural | 10 | `f1d566fb` | `{'pos_z': 3, 'n_steps': 5}` |
| 2 | other | 1 | 4 | (1,2,0.71,1.00) | structural | 14 | `9ec7a727` | `{'pos_z': 0, 'n_steps': 7, 'pos_y': 0}` |
| 0 | other | 1 | 4 | (1,2,0.52,1.00) | structural | 4 | `bc438555` | `{'n_steps': 7}` |
| 0 | other | 0 | 4 | (1,1,0.40,1.00) | structural | 62 | `9d653d86` | `{'pos_z': 4}` |
| 1 | other | 0 | 4 | (1,1,0.40,1.00) | structural | 49 | `f9fd95e3` | `{'pos_z': 4}` |
| 2 | other | 0 | 4 | (0,1,0.12,1.00) | structural | 53 | `18295968` | `{'pos_z': 2}` |

## ideal_reduction (13 cells)

| dag_h | type | mag | dist | fitness | op | n_evals | hash | predicate |
|---|---|---|---|---|---|---|---|---|
| 1 | other | 2 | 4 | (1,2,1.25,1.00) | structural | 10 | `ee26582c` | `{'pos_x': 1, 'neg_x': 4}` |
| 2 | other | 2 | 4 | (1,2,1.24,1.00) | structural | 18 | `ca675142` | `{'n_steps': 5, 'neg_y': 0, 'neg_x': 4}` |
| 0 | other | 2 | 4 | (1,2,0.94,1.00) | structural | 7 | `93acc7e3` | `{'neg_x': 4}` |
| 1 | other | 1 | 4 | (1,2,0.82,1.00) | structural | 26 | `663efa16` | `{'n_steps': 5, 'neg_y': 0}` |
| 2 | other | 1 | 4 | (1,2,0.82,1.00) | structured_null | 29 | `2bdd4869` | `{'n_steps': 5, 'neg_y': 0}` |
| 0 | other | 1 | 4 | (1,2,0.63,1.00) | structural | 14 | `c225bc64` | `{'neg_z': 3}` |
| 1 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 2 | `50bb63a2` | `{'n_steps': 5, 'neg_x': 4}` |
| 2 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 8 | `57c7ef3d` | `{'n_steps': 5, 'neg_x': 4}` |
| 0 | other | 0 | 4 | (1,1,0.42,1.00) | structural | 51 | `6754e3f5` | `{'neg_z': 2}` |
| 1 | other | 0 | 4 | (1,1,0.42,1.00) | structural | 79 | `6cb4f40c` | `{'neg_z': 2}` |
| 3 | other | 2 | 4 | (0,2,1.13,1.00) | structural | 4 | `7ed70272` | `{'n_steps': 5, 'neg_y': 4, 'neg_x': 4}` |
| 2 | other | 0 | 4 | (0,1,0.39,1.00) | uniform | 162 | `1814d5ed` | `{'neg_z': 3, 'pos_z': 3}` |
| 3 | other | 0 | 4 | (0,1,0.00,1.00) | anti_prior | 38 | `6d385ded` | `{'neg_x': 1, 'neg_z': 0, 'pos_y': 3, 'pos_x': 7, 'neg_y': 4}` |

## variety_fingerprint (24 cells)

| dag_h | type | mag | dist | fitness | op | n_evals | hash | predicate |
|---|---|---|---|---|---|---|---|---|
| 1 | boolean_or_class | 2 | 4 | (1,2,1.24,1.00) | structural | 4 | `0bb45c16` | `{'has_diag_pos': True, 'n_steps': 7}` |
| 2 | boolean_or_class | 2 | 4 | (1,2,1.24,1.00) | structural | 16 | `59116b93` | `{'pos_x': 1, 'neg_x': 4, 'has_diag_pos': True}` |
| 2 | other | 2 | 4 | (1,2,1.24,1.00) | structural | 14 | `ce944708` | `{'n_steps': 5, 'has_diag_pos': False, 'neg_x': 4}` |
| 3 | boolean_or_class | 2 | 4 | (1,2,1.24,1.00) | structural | 4 | `f06a2bc9` | `{'n_steps': 5, 'neg_y': 0, 'neg_x': 4, 'has_diag_neg': True}` |
| 3 | other | 2 | 3 | (1,2,1.24,1.00) | structural | 3 | `9eb6f9eb` | `{'n_steps': 5, 'has_diag_neg': True, 'has_diag_pos': True, 'pos_x': 1, 'neg_x': 4}` |
| 3 | other | 2 | 4 | (1,2,1.24,1.00) | structural | 25 | `e2fdc86f` | `{'n_steps': 5, 'has_diag_neg': True, 'has_diag_pos': True, 'pos_x': 1}` |
| 1 | other | 2 | 4 | (1,2,0.95,1.00) | structural | 2 | `2b10d4d4` | `{'has_diag_pos': True, 'n_steps': 5}` |
| 2 | boolean_or_class | 1 | 4 | (1,2,0.85,1.00) | structural | 3 | `bfc59f9d` | `{'neg_z': 3, 'has_diag_neg': True}` |
| 0 | boolean_or_class | 1 | 4 | (1,2,0.76,1.00) | symbolic | 13 | `74caf495` | `{'has_diag_pos': True}` |
| 2 | other | 1 | 4 | (1,2,0.76,1.00) | structural | 5 | `1627935b` | `{'has_diag_pos': True, 'neg_z': 3}` |
| 1 | boolean_or_class | 1 | 4 | (1,2,0.59,1.00) | structural | 1 | `4a84e343` | `{'has_diag_pos': True, 'neg_z': 1}` |
| 1 | other | 1 | 4 | (1,2,0.59,1.00) | structural | 8 | `c48bb917` | `{'has_diag_pos': True, 'neg_z': 1}` |
| 2 | boolean_or_class | 3 | 4 | (1,1,1.47,1.00) | structural | 13 | `72d3c640` | `{'n_steps': 5, 'neg_x': 4, 'has_diag_neg': True}` |
| 2 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 4 | `d8c2162b` | `{'n_steps': 5, 'has_diag_neg': True, 'pos_x': 1}` |
| 3 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 2 | `e50a2278` | `{'n_steps': 5, 'has_diag_neg': True, 'pos_x': 1}` |
| 1 | other | 0 | 4 | (1,1,0.42,1.00) | anti_prior | 15 | `924eb907` | `{'has_diag_pos': False, 'neg_z': 3}` |
| 3 | other | 1 | 4 | (0,2,0.86,1.00) | structural | 2 | `ce9a7bf2` | `{'n_steps': 5, 'has_diag_neg': True, 'has_diag_pos': True, 'pos_z': 0}` |
| 1 | boolean_or_class | 0 | 4 | (0,1,0.37,1.00) | structural | 13 | `976e83ed` | `{'neg_z': 2, 'has_diag_neg': False}` |
| 2 | boolean_or_class | 0 | 4 | (0,1,0.34,1.00) | symbolic | 35 | `e8f38dfa` | `{'neg_z': 0, 'has_diag_neg': True}` |
| 0 | boolean_or_class | 0 | 4 | (0,1,0.11,1.00) | structural | 14 | `60aac274` | `{'has_diag_neg': False}` |
| 2 | other | 0 | 4 | (0,1,0.00,1.00) | structural | 55 | `c716ee46` | `{'n_steps': 5, 'has_diag_neg': True, 'pos_x': 6}` |
| 3 | boolean_or_class | 0 | 4 | (0,1,0.00,1.00) | symbolic | 6 | `869fdb1f` | `{'n_steps': 5, 'neg_y': 5, 'neg_x': 4, 'has_diag_neg': False}` |
| 3 | other | 0 | 3 | (0,1,0.00,1.00) | structural | 1 | `2e51de97` | `{'n_steps': 5, 'has_diag_neg': True, 'pos_z': 7, 'pos_x': 1, 'neg_x': 4}` |
| 3 | other | 0 | 4 | (0,1,0.00,1.00) | structural | 62 | `343569c7` | `{'n_steps': 5, 'has_diag_neg': True, 'has_diag_pos': True, 'neg_x': 0}` |
