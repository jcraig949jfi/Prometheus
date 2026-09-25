# S1-C -- the 1,031 PAIR_EXECUTION replicators re-adjudicated through P-11

Currency 2026-09-24. Machine records: `P11_REASSAY.json` (aggregate),
`P11_REASSAY.jsonl` (one row per run, including the first P-11-causal donor genome),
`S1C_BREAKDOWN.json` (event causes by axis). Per-event files are kept locally under
`replays/p11/` and are gitignored.

P-11 was specified, tested and committed (`f28e5fd72`, pushed) **before** any of the
1,031 was inspected. It is a **new forensic assay**. It does not rewrite the frozen
result:

- **predecessor criterion: 1,031 admissible** (frozen, unchanged);
- **P-11 stricter causal reassay: 57 surviving** (48 under the literal
  last-write-at-all reading of authorship, reported alongside).

Every one of the 1,031 replays reproduced its frozen summary field for field
(REPLAY_MATCH 1,031 / 1,031). As an external check, the replayed predecessor-criterion
depth distribution, 911 / 111 / 9 at depth 1 / 2 / 3, equals FINDINGS A-1 exactly.

## Disposition

| | runs | events |
|---|---|---|
| predecessor criterion | 1,031 | 7,919 |
| P-11 causal | **57** | **69** |
| literal-authorship reading | 48 | 54 |

Per-event criterion failures, by majority of 3 draws: C2 (rebuild a randomized victim)
7,829; C4 (donor authorship) 6,595; C5 (donor-disabled control) **11**. Events failing
only one criterion: C2 1,253, C4 11, C5 2. As P11_SPEC section 4 predicted, C5 almost
never decides. Non-surviving runs containing at least one event that fails C2: 974;
C4: 959; C5: 4.

## Causal replication depth

| max depth | predecessor criterion | P-11 |
|---|---|---|
| 0 | - | 974 |
| 1 | 911 | **55** |
| 2 | 111 | **2** |
| 3 | 9 | **0** |

**Depth-1 dominance remains, and strengthens:** 88.4% of runs under the predecessor
criterion, 96.5% of P-11 survivors. No P-11 lineage reaches depth 3.

## Survivors: where they are

| field | distribution among the 57 |
|---|---|
| structure | NICHES_HIGH_MIG 28, WELL_MIXED 18, ENV_MIG 5, RESERVOIR 3, NICHES_ISOLATED 1, NICHES_PERIODIC_MIG 1, COMPETENCE_MIG 1 |
| representation | Z8_64 27, Z8_32 18, Z8_SLOTTED 8, Z8_SHARED 2, Z8_SEPARATED 2 |
| pressure | QUALITY_DIVERSITY 32, METABOLIC 14, EXEC_TIME_COST 5, COMPETITION 2, NONE_IMPLICIT 2, PREDATION 1, NOVELTY 1 |
| atlas_axis | RECOMBINATION 35 (of 910 reassayed, 3.8%), RESIDUE_TRANSPORT 13 (of 94, 13.8%), other axes 9 (of 27, 33%) |

## Why the other 974 fail

Event categories (`s1c_breakdown.py`):

| axis | events | P-11 causal | genuine partial copy | not donor-authored | under 10% directed changes on the observed event |
|---|---|---|---|---|---|
| RECOMBINATION | 6,547 | 44 | 128 | 6,363 | **6,287** |
| RESIDUE_TRANSPORT | 1,279 | 13 | 109 | 1,148 | 32 |
| all other axes | 93 | 12 | 23 | 58 | 2 |
| **all** | **7,919** | **69** | **260** | **7,569** | 6,321 |

**Z80A-D05 -- the world's recombination operator was credited as the donor replicating.**
The predecessor measures pair-tape fidelity **after** `_mutate`. Under `atlas_axis =
RECOMBINATION`, `_mutate` splices the victim with a randomly chosen living organism,
which is often the donor or a near-copy of it. In 6,287 of 6,547 RECOMBINATION-axis events
the interaction itself moved fewer than 10% of the victim's bytes toward the donor. The
victim became donor-like in the splice, and the write-count clause was satisfied by
unrelated writes. That is why 910 of the 1,031 sit on one atlas axis. The first case
examined (`ec37c8167691fb2c-s7979-tM-a0`) is typical: the victim half was 3.1% donor-like
after the interaction and 95.3% after the splice.

Off that axis, failures are mostly mixed authorship: substantial donor-directed change,
but under 90% of it written by the donor. There are also 260 genuine partial copies that
cannot rebuild a random victim.

## Consequence for the predecessor's headline

A-1 narrows a third time. The honest statement becomes: *57 of 1,031 random-start
pair-tape runs contain at least one interaction in which one organism can rebuild a
randomized partner to >= 0.90 fidelity by its own writes; none of those lineages
reaches depth 3.*
