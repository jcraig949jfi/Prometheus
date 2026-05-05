# Cluster characterization: trial_3_iter31_a149_u05_15k_ledger.jsonl

- Corpus: `a149_real` (1457 records)
- Ledger: `ergon\learner\trials\ledgers\trial_3_iter31_a149_u05_15k_ledger.jsonl`
- High-confidence clusters found: **12**

## Cluster #1: lift=29.00, match=7, kr=1.000

**Simplest predicate** (5-conjunct):

```
{
  "neg_x": 3,
  "neg_y": 3,
  "has_diag_pos": false,
  "pos_x": 2,
  "pos_y": 2
}
```

_12 predicate variants in ledger represent this cluster._

**Match records** (7):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149086 | False | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 2 |
| A149110 | False | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149146 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 1 |
| A149162 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 2 |
| A149166 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149167 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149170 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 3 | True | 3 |

**First found**: seed=1234, ep=1220

## Cluster #2: lift=27.92, match=5, kr=1.000

**Simplest predicate** (1-conjunct):

```
{
  "neg_x": 4
}
```

_216 predicate variants in ledger represent this cluster._

**Match records** (5):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149074 | True | False | 2 | 5 | 4 | 1 | 1 | 1 | 1 | 1 | True | 4 |
| A149081 | True | False | 1 | 5 | 4 | 3 | 1 | 1 | 1 | 1 | True | 4 |
| A149082 | True | False | 1 | 5 | 4 | 1 | 1 | 1 | 2 | 2 | True | 4 |
| A149089 | True | False | 0 | 5 | 4 | 3 | 1 | 1 | 1 | 2 | True | 4 |
| A149090 | True | False | 0 | 5 | 4 | 2 | 1 | 1 | 2 | 3 | True | 4 |

**First found**: seed=42, ep=82

## Cluster #3: lift=27.92, match=5, kr=1.000

**Simplest predicate** (3-conjunct):

```
{
  "neg_x": 3,
  "pos_y": 3,
  "neg_y": 2
}
```

_81 predicate variants in ledger represent this cluster._

**Match records** (5):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149164 | False | False | 0 | 5 | 3 | 2 | 1 | 2 | 3 | 1 | True | 1 |
| A149169 | False | False | 0 | 5 | 3 | 2 | 1 | 2 | 3 | 2 | True | 1 |
| A149220 | False | False | 0 | 5 | 3 | 2 | 1 | 2 | 3 | 1 | True | 1 |
| A149229 | False | False | 0 | 5 | 3 | 2 | 1 | 2 | 3 | 2 | True | 1 |
| A149231 | False | False | 0 | 5 | 3 | 2 | 1 | 2 | 3 | 3 | True | 2 |

**First found**: seed=42, ep=1484

## Cluster #4: lift=27.92, match=5, kr=1.000

**Simplest predicate** (3-conjunct):

```
{
  "neg_y": 1,
  "neg_z": 3,
  "pos_z": 2
}
```

_101 predicate variants in ledger represent this cluster._

**Match records** (5):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149076 | False | False | 2 | 5 | 1 | 1 | 3 | 1 | 1 | 2 | True | 1 |
| A149104 | False | False | 1 | 5 | 1 | 1 | 3 | 1 | 2 | 2 | True | 1 |
| A149107 | False | False | 1 | 5 | 1 | 1 | 3 | 2 | 2 | 2 | True | 1 |
| A149159 | False | False | 1 | 5 | 1 | 1 | 3 | 2 | 2 | 2 | True | 1 |
| A149160 | False | False | 0 | 5 | 1 | 1 | 3 | 2 | 3 | 2 | True | 1 |

**First found**: seed=100, ep=510

## Cluster #5: lift=27.92, match=5, kr=1.000

**Simplest predicate** (7-conjunct):

```
{
  "neg_x": 3,
  "neg_y": 3,
  "has_diag_pos": false,
  "pos_x": 2,
  "n_steps": 5,
  "pos_y": 2,
  "has_diag_neg": true
}
```

**Match-set-equivalent shorter forms**:

- 5-conjunct: `{'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'pos_y': 2, 'has_diag_neg': True}`
- 6-conjunct: `{'neg_x': 3, 'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'pos_y': 2, 'has_diag_neg': True}`
- 6-conjunct: `{'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'n_steps': 5, 'pos_y': 2, 'has_diag_neg': True}`

**Match records** (5):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149146 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 1 |
| A149162 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 2 |
| A149166 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149167 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149170 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 3 | True | 3 |

**First found**: seed=1234, ep=5427

## Cluster #6: lift=27.42, match=4, kr=1.000

**Simplest predicate** (4-conjunct):

```
{
  "pos_z": 2,
  "pos_y": 2,
  "neg_y": 3,
  "neg_x": 3
}
```

_9 predicate variants in ledger represent this cluster._

**Match records** (4):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149110 | False | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149166 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149167 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149499 | True | True | 0 | 5 | 3 | 3 | 3 | 2 | 2 | 2 | True | 4 |

**First found**: seed=100, ep=12374

## Cluster #7: lift=26.93, match=3, kr=1.000

**Simplest predicate** (2-conjunct):

```
{
  "neg_x": 4,
  "pos_y": 1
}
```

_20 predicate variants in ledger represent this cluster._

**Match records** (3):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149074 | True | False | 2 | 5 | 4 | 1 | 1 | 1 | 1 | 1 | True | 4 |
| A149081 | True | False | 1 | 5 | 4 | 3 | 1 | 1 | 1 | 1 | True | 4 |
| A149089 | True | False | 0 | 5 | 4 | 3 | 1 | 1 | 1 | 2 | True | 4 |

**First found**: seed=42, ep=9163

## Cluster #8: lift=26.93, match=3, kr=1.000

**Simplest predicate** (4-conjunct):

```
{
  "pos_z": 2,
  "pos_y": 2,
  "neg_y": 3,
  "has_diag_neg": true
}
```

_42 predicate variants in ledger represent this cluster._

**Match records** (3):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149166 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149167 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149499 | True | True | 0 | 5 | 3 | 3 | 3 | 2 | 2 | 2 | True | 4 |

**First found**: seed=100, ep=10639

## Cluster #9: lift=26.93, match=3, kr=1.000

**Simplest predicate** (4-conjunct):

```
{
  "pos_y": 2,
  "neg_z": 3,
  "pos_z": 2,
  "has_diag_neg": false
}
```

_21 predicate variants in ledger represent this cluster._

**Match records** (3):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149104 | False | False | 1 | 5 | 1 | 1 | 3 | 1 | 2 | 2 | True | 1 |
| A149107 | False | False | 1 | 5 | 1 | 1 | 3 | 2 | 2 | 2 | True | 1 |
| A149159 | False | False | 1 | 5 | 1 | 1 | 3 | 2 | 2 | 2 | True | 1 |

**First found**: seed=42, ep=13076

## Cluster #10: lift=26.93, match=3, kr=1.000

**Simplest predicate** (4-conjunct):

```
{
  "neg_y": 1,
  "pos_x": 2,
  "neg_z": 3,
  "pos_z": 2
}
```

_8 predicate variants in ledger represent this cluster._

**Match records** (3):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149107 | False | False | 1 | 5 | 1 | 1 | 3 | 2 | 2 | 2 | True | 1 |
| A149159 | False | False | 1 | 5 | 1 | 1 | 3 | 2 | 2 | 2 | True | 1 |
| A149160 | False | False | 0 | 5 | 1 | 1 | 3 | 2 | 3 | 2 | True | 1 |

**First found**: seed=100, ep=2541

## Cluster #11: lift=26.93, match=3, kr=1.000

**Simplest predicate** (7-conjunct):

```
{
  "neg_x": 3,
  "neg_y": 3,
  "has_diag_pos": false,
  "pos_x": 2,
  "n_steps": 5,
  "pos_y": 2,
  "pos_z": 1
}
```

**Match-set-equivalent shorter forms**:

- 5-conjunct: `{'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'pos_y': 2, 'pos_z': 1}`
- 6-conjunct: `{'neg_x': 3, 'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'pos_y': 2, 'pos_z': 1}`
- 6-conjunct: `{'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'n_steps': 5, 'pos_y': 2, 'pos_z': 1}`

_2 predicate variants in ledger represent this cluster._

**Match records** (3):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149086 | False | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 2 |
| A149146 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 1 |
| A149162 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 1 | True | 2 |

**First found**: seed=1234, ep=1134

## Cluster #12: lift=26.93, match=3, kr=1.000

**Simplest predicate** (7-conjunct):

```
{
  "neg_x": 3,
  "neg_y": 3,
  "has_diag_pos": false,
  "pos_x": 2,
  "n_steps": 5,
  "pos_y": 2,
  "pos_z": 2
}
```

**Match-set-equivalent shorter forms**:

- 5-conjunct: `{'neg_x': 3, 'neg_y': 3, 'has_diag_pos': False, 'pos_y': 2, 'pos_z': 2}`
- 6-conjunct: `{'neg_x': 3, 'neg_y': 3, 'has_diag_pos': False, 'pos_x': 2, 'pos_y': 2, 'pos_z': 2}`
- 6-conjunct: `{'neg_x': 3, 'neg_y': 3, 'has_diag_pos': False, 'n_steps': 5, 'pos_y': 2, 'pos_z': 2}`

_2 predicate variants in ledger represent this cluster._

**Match records** (3):

| seq_id | has_diag_neg | has_diag_pos | n_axis_aligned | n_steps | neg_x | neg_y | neg_z | pos_x | pos_y | pos_z | kill_verdict | n_kill_tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A149110 | False | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149166 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |
| A149167 | True | False | 0 | 5 | 3 | 3 | 1 | 2 | 2 | 2 | True | 3 |

**First found**: seed=1234, ep=7483

