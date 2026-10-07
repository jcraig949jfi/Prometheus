# REPORT E1: CHIASMA four-organism Ontological Shock

Seat: Hades. Claim level: AUTHOR_TESTED (no outside challenge yet).
Verdict tuple:
- EXECUTION: RAN (840/840 runs, rc=0, 2026-10-07T09:39:32Z to 09:48:02Z).
- AUTHORITY: UNQUALIFIED (author-tested only).
- OUTCOME: primary FAIL; attribution NOT_ATTRIBUTED.

Conditions repeated wherever this verdict is quoted:
- world family PW-H (m=16, one redundant literal as the false foundation,
  noise-free);
- ratios R21/R11/R12;
- caps 600/1000/3000 bytes;
- evaluation seeds 2187867196-205;
- code 591ad0591, prereg sha256 8268343c..., freeze 02b5f57a1.

## 1. Primary (preregistered, chiasma/verdict_e1.py)

"O4 beats X" = lower err_CDE on at least 8 of 10 paired seeds.

| cell (ratio, cap) | O4 vs O1 | O4 vs O2 | O4 vs O4R | beats both |
|---|---|---|---|---|
| R21, 600 / 1000 / 3000 | 10/10 | 10/10 | 9/10 | yes (3 cells) |
| R11, 600 / 1000 / 3000 | 8/10 | 6/10 | 7, 7, 6 /10 | no |
| R12, 600 / 1000 / 3000 | 3/10 | 2, 1, 1 /10 | 1/10 | no |

- Cells where O4 beats O1 and O2: 3/9. Since 2*3 < 9, the verdict is **FAIL**.
  Charter s7 mapping: KILL or radically REVISE O4 as designed.
- Attribution: O4 beats its random-seam counterfeit O4R only where it also wins
  (R21). NOT_ATTRIBUTED.
- O4's collateral exceeds O2's in every cell (O2's is strictly lower on 10/10
  seeds everywhere). Median O4 collateral_CDE is 209 (R21), 368 (R11) and 475 (R12),
  against 0 for O1-O3.

Plain reading: O4's eager seams restore the pruned literal in every cell that used
the broken justification. That is right for the Y-dependents and wrong for the
decoys. The seams pay off only when the false abstraction carries more true
dependents than incidental ones (R21). They are a bet, not a diagnosis of which
structure is load-bearing.

## 2. Secondary (preregistered as non-deciding)

| contrast (wins/10 per cell) | R21 | R11 | R12 |
|---|---|---|---|
| O4L vs O1 | 10, 10, 10 | 10, 10, 10 | 10, 10, 10 |
| O4L vs O2 | 10, 10, 10 | 10, 10, 10 | 9, 10, 10 |
| O4L vs O3 | 10, 10, 10 | 10, 10, 10 | 10, 10, 10 |
| O4L vs O0 | 0, 0, 0 | 5, 5, 5 | 9, 9, 9 |
| O4 vs O0 | 0, 0, 0 | 1, 1, 1 | 3, 2, 2 |
| O3 vs O2 | 2, 1, 1 | 2, 1, 1 | 2, 1, 1 |
| O3 vs O3R | 5, 6, 10 | 5, 6, 10 | 5, 3, 10 |

(cells in cap order 600, 1000, 3000; source chiasma/runs/e1-eval/VERDICT.json)

- O4L is provenance repair: a failing cell restores the literal it pruned, from the
  record of why it was pruned, instead of being retracted and relearned. It beats
  O1, O2 and O3 in all 9 cells with collateral 0. This is the only gain in E1 that
  looks like a mechanism. O4L was added after dev run 1, so this is an exploratory
  finding that needs its own preregistered test, not a result.
- O0, the cheapest counter-organism (never compresses, keeps the full anchor), beats
  every arm in R21 and ties O4L in R11. O4L beats it only in R12. No organism
  dominates across ratios. The pre-shock bet (keep f or drop it), which the A/B
  data cannot settle, decides most of err_CDE.
- Failure compression did not pay off here. O3 never beats O2 on err_CDE (at most
  2/10). The cap 600 / 800 effect seen in dev did not hold on the evaluation seeds.
- Shadow content matters only with room to spare. O3 beats random shadow O3R at
  cap 3000 (10/10 in every ratio), not at 600 or 1000.
- Medians and all endpoints per arm and cell: chiasma/runs/e1-eval/TABLES.md.
  Ops: O3, O4 and O4L use about 1.8-2.6x O2's learning ops (shadow upkeep);
  compute was not matched.

## 3. Instrument tripwires (stated in the prereg before evaluation)

- "O1 wins anything": FIRED. O1 beats O4 in R12 (O4 vs O1 3/10). Diagnosis: O4's
  decoy collateral, not a broken O1. The weld-without-negatives rule behaves as
  designed (O1 loses to O2 on unrel targets).
- "CEIL loses to any capped arm": FIRED. In R12, CEIL's median err_CDE is 433,
  against O3 292 and O4L 257. Diagnosis: a design fault. CEIL changes two things
  at once (unbounded memory AND no consolidation), so it inherits O0's keep-f bet.
  It is not a ceiling for err_CDE. Fix: the ceiling must be "O3 with no cap",
  differing in one variable only.
- "EMB beats a geometric arm": did not fire. EMB is worst everywhere (median
  err_CDE 21k-28k, never recovers).

## 4. Predictions written before evaluation, scored

| prediction | outcome |
|---|---|
| primary MIXED | WRONG: FAIL. R11 also failed (O4 vs O2 6/10) |
| NOT ATTRIBUTED | RIGHT |
| O4L beats O1, O2, O3 in all 9 cells | RIGHT |
| O3 beats O2 at cap 600 in at least 2 ratios | WRONG (2/10 in each) |
| O0 beats O4 and O4L in R21, loses in R12 | R21 right; R12 right for O4L (O4L beats O0 9/10), wrong for O4 (O4 beats O0 at most 3/10) |

## 5. What this does and does not show

Shows, under the stated conditions:
- Eager revision seams on a single compressed literal do not beat positive-only or
  raw-failure organisms in general. Whether they win depends on how many true
  dependents the false abstraction carries relative to incidental ones.
- Keeping the provenance of compression (O4L) is the one mechanism that beat the
  charter's O1-O3 everywhere. That finding is post hoc.
- In this world, the cheapest counter-organism (no compression) is as good as or
  better than every CHIASMA arm whenever true dependents are common.

Does not show:
- Anything about 8-16-D coordinates, factoring, other species, evolution, WT-4 at
  scale, or WT-5 fault lines.
- Anything outside one world family with a single redundant literal.
- Anything an outside reviewer has tried to break.

## 6. Recommendation to the operator (HADES-10; the decision is the operator's)

REVISE, do not evolve. The charter's s7 condition for evolution is not met. Proposed
next steps, each its own preregistration on fresh seeds:
1. E1b: O4L as the primary subject against O1, O2, O3 and O0, with a counterfeit
   lazy provenance (repair restores a random pruned-set literal), and the ceiling
   fixed to O3-uncapped.
2. A world with several false abstractions of different loads, so that "identify
   the load-bearing abstraction" is something an organism can do from evidence,
   not a bet the ratio decides.
3. A world where failures are the main information channel (disjunctive and
   incompatibility-heavy), before claiming anything about shadow compression.
4. An outside first-sight challenge of E1 (G3) before E1b is frozen.

## 7. Artifacts

- chiasma/runs/e1-eval/rows.jsonl: 840 rows.
- VERDICT.json and TABLES.md.
- receipts.tar.gz: 840 full receipts with checkpoints. RECEIPTS_SHA256.jsonl lists
  each receipt's sha256 before archiving.
- STARTED_UTC.txt, FINISHED_UTC.txt and sweep_stdout.txt.
- Freeze: chiasma/FREEZE_E1.json. Prereg: chiasma/PREREG_E1.md. Design:
  chiasma/DESIGN_E1.md. WT-0: chiasma/runs/wt0/.
