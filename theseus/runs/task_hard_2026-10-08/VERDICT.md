# THESEUS-31b verdict (prereg roles/Theseus/prereg/2026-10-08_task_hard/, 075d58921;
# amendment 1 checkpointing only, 94d856b5e)

Run: python -m theseus.synth.task_hard --tag task_hard_2026-10-08 --workers 4 (rerun after the
first attempt was killed at the 2 h limit with nothing written). Wall 3489 s, CPU 13360 s.
Task: c3 cue recall V = 8, k = 8 (chance .125), J_hard = mean over task seeds 0, 1.

GATE: noop .119 (<= .175); relay .972, memcomp 1.000 (>= .30). PASSES.
Part 1 (mean J_hard / median / share >= .5):
  A .907 / 1.000 / .92   E .846 / 1.000 / .85   D .821 / 1.000 / .82   R .660 / .969 / .62
  C .502 / .302 / .45    B .487 / .171 / .45    P .406 / .128 / .35    G0 .382 / .119 / .33
H-TASK-HARD: D > one-shot (P+B+C) Mann-Whitney one-sided p 1.9e-14; D > R p .0018.
VERDICT Part 1: SUPPORTED -- 31a replicates at the harder setting, now off the ceiling for
one-shot arms (pooled one-shot median .21 vs D 1.0).

Part 2 (single-rule knockouts on capable genomes, J drop >= .2 = essential):
  carrier size 0 / 1 / >= 2 :  D 24/14/2   E 28/8/4   R 16/21/3   A 12/25/3
                               B 10/13/17  C 9/16/15  P 4/13/18   G0 6/10/9
  essential ops: one-shot arms' commonest multi-part carrier is remember+recall (B 10, C 10,
  P 12 genomes); D's single essentials are mostly react (9) and lensmap (3).
H-CARRIER (D multi-part share > R, Fisher): 2/40 vs 3/40, p .82 -> NOT SUPPORTED.

EXPLORATORY (post hoc, not preregistered -- the next item preregisters it): capable deep
descendants are mostly REDUNDANT carriers -- no single rule is essential (D 24/40, E 28/40)
-- vs one-shot 23/115 (Fisher D > one-shot p 4.8e-6) and R 16/40 (p .059). One-shot
collisions that succeed tend to depend on a fragile two-rule memory pair (remember+recall,
both essential); deep descendants keep the cue along several overlapping paths. Candidate
mechanism for the depth advantage: DEGENERACY (redundant carriers), not composition.
Successor THESEUS-33: double knockouts to test degeneracy directly.

Predictions: H1h gate RIGHT; H2h H-TASK-HARD supported RIGHT; H3h most capable D are
one-part WRONG (most are redundant, size 0); H4h H-CARRIER not supported RIGHT.
