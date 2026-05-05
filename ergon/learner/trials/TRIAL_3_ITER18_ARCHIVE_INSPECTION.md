# Iter 18 archive inspection (seed=42, 5K eps, rate=0.15)

- Total cells filled: **51**
- Cells by winning operator class:
  - structural: 42
  - symbolic: 5
  - anti_prior: 4

## partition_refinement (13 cells)

| dag_h | type | mag | dist | fitness | op | n_evals | hash | predicate |
|---|---|---|---|---|---|---|---|---|
| 2 | other | 2 | 4 | (1,2,1.20,1.00) | structural | 27 | `339dc280` | `{'pos_x': 1, 'n_steps': 5, 'pos_z': 1}` |
| 1 | other | 2 | 4 | (1,2,0.99,1.00) | structural | 32 | `a33fbe8d` | `{'n_steps': 5, 'pos_z': 1}` |
| 0 | other | 2 | 4 | (1,2,0.98,1.00) | structural | 82 | `b4cef3e2` | `{'pos_x': 1}` |
| 1 | other | 1 | 4 | (1,2,0.85,1.00) | structural | 64 | `a612c6fc` | `{'pos_x': 1, 'pos_z': 1}` |
| 2 | other | 1 | 4 | (1,2,0.85,1.00) | structural | 40 | `14fac03e` | `{'pos_z': 1, 'pos_x': 1}` |
| 3 | other | 1 | 4 | (1,2,0.71,1.00) | structural | 14 | `7bd17a3a` | `{'pos_y': 0, 'pos_z': 0, 'n_steps': 7}` |
| 0 | other | 1 | 4 | (1,2,0.52,1.00) | structural | 49 | `bc438555` | `{'n_steps': 7}` |
| 1 | other | 3 | 4 | (1,1,1.29,1.00) | structural | 12 | `f2e247b1` | `{'pos_x': 1, 'n_steps': 5}` |
| 0 | other | 0 | 4 | (1,1,0.40,1.00) | symbolic | 282 | `2d03df7e` | `{'pos_z': 4}` |
| 1 | other | 0 | 4 | (1,1,0.40,1.00) | structural | 235 | `a739d7cf` | `{'pos_z': 4}` |
| 2 | other | 0 | 4 | (1,1,0.40,1.00) | symbolic | 182 | `8c44cace` | `{'pos_z': 4}` |
| 3 | other | 2 | 4 | (0,2,1.13,1.00) | symbolic | 5 | `3f6b62a9` | `{'pos_y': 1, 'pos_z': 1, 'n_steps': 5}` |
| 3 | other | 0 | 4 | (0,1,0.00,1.00) | anti_prior | 39 | `43320e03` | `{'pos_y': 2, 'pos_z': 0, 'n_steps': 7}` |

## ideal_reduction (14 cells)

| dag_h | type | mag | dist | fitness | op | n_evals | hash | predicate |
|---|---|---|---|---|---|---|---|---|
| 1 | other | 2 | 4 | (1,2,1.25,1.00) | structural | 48 | `519a26b6` | `{'pos_x': 1, 'neg_x': 4}` |
| 2 | other | 2 | 4 | (1,2,1.25,1.00) | structural | 63 | `b40e06c0` | `{'pos_x': 1, 'neg_x': 4}` |
| 0 | other | 2 | 4 | (1,2,0.94,1.00) | structural | 44 | `93acc7e3` | `{'neg_x': 4}` |
| 1 | other | 1 | 4 | (1,2,0.85,1.00) | structural | 121 | `c01b047a` | `{'neg_z': 3, 'neg_x': 4}` |
| 2 | other | 1 | 4 | (1,2,0.85,1.00) | structural | 88 | `c7e342fb` | `{'neg_z': 3, 'neg_x': 4}` |
| 3 | other | 1 | 4 | (1,2,0.85,1.00) | structural | 13 | `bf42e260` | `{'neg_z': 3, 'neg_y': 0}` |
| 0 | other | 1 | 4 | (1,2,0.63,1.00) | structural | 80 | `20fce3ad` | `{'neg_z': 3}` |
| 1 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 10 | `64933a4e` | `{'neg_x': 4, 'n_steps': 5}` |
| 2 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 3 | `5b77b2d6` | `{'neg_x': 4, 'n_steps': 5}` |
| 0 | other | 0 | 4 | (1,1,0.42,1.00) | structural | 261 | `6754e3f5` | `{'neg_z': 2}` |
| 1 | other | 0 | 4 | (1,1,0.42,1.00) | structural | 450 | `cfbf112c` | `{'neg_z': 2}` |
| 3 | other | 2 | 4 | (0,2,1.13,1.00) | structural | 7 | `993efd3f` | `{'neg_z': 3, 'pos_z': 0, 'neg_y': 0}` |
| 2 | other | 0 | 4 | (0,1,0.39,1.00) | structural | 692 | `36b053ed` | `{'neg_z': 2, 'neg_y': 1}` |
| 3 | other | 0 | 4 | (0,1,0.00,1.00) | anti_prior | 173 | `8f100d5f` | `{'pos_y': 2, 'neg_z': 1, 'pos_x': 7, 'neg_x': 0}` |

## variety_fingerprint (24 cells)

| dag_h | type | mag | dist | fitness | op | n_evals | hash | predicate |
|---|---|---|---|---|---|---|---|---|
| 1 | boolean_or_class | 2 | 4 | (1,2,1.24,1.00) | structural | 33 | `e86c2529` | `{'n_steps': 7, 'has_diag_pos': True}` |
| 2 | boolean_or_class | 2 | 4 | (1,2,1.24,1.00) | structural | 45 | `583f5cae` | `{'pos_x': 1, 'has_diag_pos': True, 'neg_x': 4}` |
| 2 | other | 2 | 4 | (1,2,1.24,1.00) | structural | 99 | `a469a6b3` | `{'pos_x': 1, 'has_diag_pos': True, 'neg_x': 4}` |
| 1 | other | 2 | 4 | (1,2,1.19,1.00) | structural | 21 | `8c466d93` | `{'has_diag_neg': True, 'neg_x': 4}` |
| 3 | boolean_or_class | 2 | 4 | (1,2,0.88,1.00) | structural | 17 | `309aa20e` | `{'neg_z': 3, 'has_diag_pos': True, 'neg_y': 0}` |
| 3 | other | 2 | 4 | (1,2,0.88,1.00) | symbolic | 13 | `30cbe4c4` | `{'neg_z': 3, 'has_diag_pos': True, 'neg_y': 0}` |
| 1 | boolean_or_class | 1 | 4 | (1,2,0.85,1.00) | structural | 65 | `dfea5977` | `{'neg_z': 3, 'has_diag_neg': True}` |
| 2 | boolean_or_class | 1 | 4 | (1,2,0.85,1.00) | structural | 47 | `045d96ce` | `{'neg_z': 3, 'has_diag_neg': True}` |
| 2 | other | 1 | 4 | (1,2,0.80,1.00) | structural | 98 | `36909c85` | `{'pos_x': 1, 'has_diag_pos': False, 'pos_z': 1}` |
| 0 | boolean_or_class | 1 | 4 | (1,2,0.76,1.00) | structural | 66 | `e9df88f8` | `{'has_diag_pos': True}` |
| 1 | other | 1 | 4 | (1,2,0.76,1.00) | structural | 47 | `9da10a21` | `{'neg_z': 3, 'has_diag_pos': True}` |
| 3 | boolean_or_class | 1 | 4 | (1,2,0.76,1.00) | structural | 11 | `4d967d32` | `{'neg_z': 3, 'has_diag_pos': True}` |
| 3 | other | 1 | 4 | (1,2,0.71,1.00) | structural | 24 | `c1c69493` | `{'neg_z': 3, 'has_diag_pos': False, 'neg_y': 0}` |
| 2 | boolean_or_class | 3 | 4 | (1,1,1.47,1.00) | structural | 11 | `5c89b877` | `{'has_diag_neg': True, 'n_steps': 5, 'neg_x': 4}` |
| 2 | other | 3 | 4 | (1,1,1.47,1.00) | structural | 5 | `94666e98` | `{'has_diag_neg': True, 'n_steps': 5, 'neg_x': 4}` |
| 1 | boolean_or_class | 3 | 4 | (1,1,1.29,1.00) | structural | 8 | `4ac87233` | `{'n_steps': 5, 'has_diag_neg': True}` |
| 1 | other | 3 | 4 | (1,1,1.29,1.00) | structural | 15 | `21aafa93` | `{'has_diag_neg': True, 'n_steps': 5}` |
| 1 | boolean_or_class | 0 | 4 | (1,1,0.42,1.00) | structural | 149 | `7153d34e` | `{'neg_z': 3, 'has_diag_pos': False}` |
| 1 | other | 0 | 4 | (1,1,0.42,1.00) | structural | 152 | `d8603b43` | `{'has_diag_neg': False, 'pos_y': 0}` |
| 2 | boolean_or_class | 0 | 4 | (1,1,0.42,1.00) | anti_prior | 151 | `ba6a217d` | `{'neg_z': 3, 'has_diag_pos': False}` |
| 2 | other | 0 | 4 | (1,1,0.42,1.00) | structural | 555 | `f79dd793` | `{'neg_z': 3, 'has_diag_pos': False}` |
| 3 | boolean_or_class | 0 | 4 | (1,1,0.42,1.00) | symbolic | 42 | `1a57ab9d` | `{'neg_z': 3, 'has_diag_pos': False}` |
| 0 | boolean_or_class | 0 | 4 | (0,1,0.11,1.00) | structural | 60 | `60aac274` | `{'has_diag_neg': False}` |
| 3 | other | 0 | 4 | (0,1,0.00,1.00) | anti_prior | 150 | `55a67b8d` | `{'neg_y': 2, 'neg_z': 1, 'pos_y': 1, 'n_steps': 6, 'has_diag_neg': False}` |
