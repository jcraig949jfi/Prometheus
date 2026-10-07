# PREREG E1: CHIASMA four-organism Ontological Shock (frozen before evaluation seeds exist)

Seat: Hades. Charter: roles/Hades/prompts/2026-10-07_charter/ s7. Design:
chiasma/DESIGN_E1.md. Freeze record: chiasma/FREEZE_E1.json (sha256 of this file
over LF-normalized bytes, the code blob ids, the commit). Nothing in this file
changes after the freeze commit. Any later deviation is written in REPORT_E1.md as
a deviation, never edited in here.

## Exposure record

Before freezing, the author saw development seeds 900001-900005 only:
- dev-sizing-1: 420 runs; caps 1000, 3000, 10000; all arms.
- dev-sizing-2: 126 runs; caps 600, 800; seeds 900001-900003.
Decisions taken after seeing dev data, all recorded in DESIGN_E1.md s6:
- the endpoint definitions (bet_B separated; collateral = newly broken; recovery
  from the first exception);
- the O4L ablation;
- the ratio factor;
- the cap set.
Evaluation seeds did not exist when this file was frozen. They are derived from
this file's own hash.

## Code under test

chiasma/world.py, organisms.py, runner.py, sweep.py, verdict_e1.py, at the blob ids
listed in FREEZE_E1.json. The evaluation runs only from a checkout whose blobs match.
After the freeze, no change to these files affects E1. A fix discovered later is a
deviation with its own rerun, reported beside the frozen run.

## Design

- World family PW-H, WorldSpec defaults except n_ydep/n_decoy by ratio:
  R21 = (16, 8), R11 = (12, 12), R12 = (8, 16).
- Evaluation seeds: s_i = int(H[:8], 16) + i for i = 0..9, where H is this file's
  sha256 (LF-normalized) from FREEZE_E1.json. The same 10 seeds are used for every
  ratio.
- Caps (total bytes P + N + U): 600, 1000, 3000. CEIL runs uncapped, once per
  (ratio, seed).
- Arms: O1, O2, O3, O4, O4L, O0, O3R, O4R, CEIL, EMB, with org_seed 0.
- Command: python -B -m chiasma.sweep chiasma/runs/e1-eval <s_0..s_9> --caps
  600,1000,3000 --full --procs 8
- Verdict: python -B -m chiasma.verdict_e1 chiasma/runs/e1-eval/rows.jsonl
- Budget: dev runs cost 1.26 CPU core-hours per 420 runs. E1 is 3 x 10 x 28 = 840
  runs, about 2.6 core-hours, well inside MWO-0004 R2.

## Primary claim and verdict (charter s7 kill rule)

Cell = (ratio, cap), 9 cells. In a cell, "O4 beats X" means O4's err_CDE is
strictly lower than X's on at least 8 of the 10 paired seeds; ties count as not
beating. Bytes are matched by the cap. Ops are reported beside every contrast,
not matched.
- PASS: O4 beats O1 AND O2 in all 9 cells.
- FAIL: O4 beats both in fewer than half the cells (n_both * 2 < 9).
- MIXED: otherwise.
- NOT_VERIFIED: any cell lacks 10 paired seeds.
Charter mapping:
- PASS: O4 survives E1. Next is the G3 outside challenge, then the operator decides
  on evolution.
- MIXED: REVISE, naming the failing cells.
- FAIL: KILL or radically REVISE O4 as designed.

Attribution rule (counterfeit control): a PASS is reported as MECHANISM_ATTRIBUTED
only if O4 also beats O4R (random seams) in all 9 cells. Otherwise it is NOT
ATTRIBUTED: the phenotype is real, but correct seams are not shown to cause it.

Eligibility: every cell has exactly 10 paired seeds, so 8 wins is attainable. A
cell where 3 or more seeds tie cannot be beaten and is reported as such. err_CDE
ties were not seen in dev between O4 and O1/O2.

## Secondary (reported, never decide the primary verdict)

Per cell, the same 8/10 rule:
- O4L vs O1, O2, O3, O0;
- O4 vs O0;
- O3 vs O2 (does compression beat raw at equal bytes?);
- O3 vs O3R (does shadow content matter?);
- O2 collateral_CDE vs O4.
Every endpoint per arm and cell is reported as a median, with NOT_RECOVERED counts.

## Author's predictions (written before evaluation; scored in REPORT_E1.md)

From dev, the author predicts:
- primary MIXED: O4 beats O1 and O2 in R21; fails against O2 in R12; R11
  uncertain.
- NOT ATTRIBUTED: O4R about equals O4.
- O4L beats O1, O2 and O3 in all 9 cells.
- O3 beats O2 at cap 600 in at least two of three ratios, but not at 3000.
- O0 beats O4 and O4L in R21 and loses in R12.
A prediction that comes true is not evidence that the design is fair. It is
recorded so that a surprise is visible.

## What would make the author wrong about the instrument (stated now)

- O1 wins anything: the weld-without-negatives rule may be broken, not
  positive-only geometry.
- EMB beats any geometric arm: the probes reward memorized examples.
- CEIL loses to any capped arm on err_CDE: consolidation would be helping
  accuracy, contrary to the design reading.
Each of these is reported as an instrument finding, not as a result about CHIASMA.
