# HT-974471f045 / W5 design notes (Pass 3 v2)

Generator prompt hecate/programs/_prompts/pass3_v2.md (sha256 2adcfc8d...d461),
bound by roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md.

## What the world tests

M2 (bracketed inheritance) through lens L2 (bracketing ledger) and L7
(permuted-fitness twin). The reservoir is heritable and frozen in life; the
readout is refitted from scratch every life with a fixed sample budget. The
claim is an interaction: a small lifetime budget (n=8) pushes task
information into the heritable reservoir, a large one (n=200) does not. The
observable is the L2 reservoir-attributed gain, G = NRMSE on a fresh gen-0
reservoir minus NRMSE on the individual's own reservoir, same inputs, same
training indices, at instrument budget n=8.

It can fail cleanly in three separate ways: evolution may not move the
reservoir at all (S1, F1), both budgets may deposit the same content (S2,
F2), or the gain may be generic few-shot conditioning rather than task
content (S3).

## Why it avoids the earlier failures

- W1 (SPEC_UNATTAINABLE): its positive control could not reach its own
  threshold because a rank-one deposit at eps=0.05 could not make a
  20-sample readout succeed, and the whole instrument sat near chance
  (NRMSE ~0.97). Here the positive control was run before freezing: the
  constructed reservoir scores NRMSE 0.17 at n=8 against 1.00 for a random
  one (G = 0.83 vs threshold 0.30). The instrument's dynamic range is
  measured, not assumed. The first control run failed (see Revisions) and
  was repaired before any threshold was frozen.
- W3 (NULL, masking selected at both budgets): the contrast was between two
  conditions that both carried selection pressure (the hand mask helped
  even more at k=50). Here the pressure difference was measured before
  freezing: the constructed task-carrying reservoir beats a gen-0 reservoir
  by 0.825 NRMSE at n=8 and by 0.008 at n=200. The budget contrast is
  therefore a real pressure contrast for this content.
- W3's twin was only a masked-fraction drift baseline; here the twin (L7)
  enters a success clause directly (S4), and a content clause (S3,
  off-task channel u2 with identical statistics) separates task deposits
  from generic learnability improvements.
- The spec is self-contained and every threshold is on a statistic the
  controls compute with the same function (`clause_values` in controls.py)
  that the treatment must use.

## Ambiguities resolved

1. "Task information in reservoir (ablation)": L2 ablation (b) - (a). The
   replacement is a fresh reservoir from the gen-0 law, not a "matched
   spectrum" copy, because the constructed positive control has spectral
   radius near 0 and a spectrum-matched random matrix would be degenerate.
2. Instrument budget: the observable is measured at n=8 in BOTH arms, so
   S2 compares the same quantity; the HIGH arm is only selected at n=200.
3. Positive control for the HIGH arm: the hypothesis says high budget leaves
   the reservoir near-random, so its effect-present construction is a
   gen-0-law reservoir.
4. Null twin without treatment code: a permuted-fitness twin ignores
   fitness, so it equals neutral drift under the same genealogy law. The
   controls implement it as drift with a random ranking each generation;
   no fitness is computed. The twin's own S4 value is 0 by definition.
5. Elites for the controls: the constructed/gen-0 individuals (positive
   control) and 5 random final-generation individuals (twin); for the
   treatment, the top 5 by the arm's own fitness at generation 60.
6. CHEAT: in the LOW arm the own-reservoir task prediction is replaced by
   the target (NRMSE_own = 0), everything else measured normally on gen-0
   reservoirs. All four clauses pass under it (detected).
7. Ridge lambda 1e-2 and no leak are fixed instrument choices recorded in
   the spec; lambda was changed once before freezing (revision 1).

## Revisions before freezing

1. After r1: positive control failed (G_task -0.68). Chain gain 2.0 saturated
   tanh; lambda 1e-6 made n=8 an exact interpolation. Gain -> 1.0, lambda ->
   1e-2. Rows kept in control_rows_r1_superseded.jsonl.
2. After r2 (already attainable): generations 30 -> 60, mutation 0.02 ->
   0.05 relative, so the treatment has a fair chance to reach a structured
   reservoir. Twin changed identically. Rows in
   control_rows_r2_superseded.jsonl. Frozen on r3 (control_rows.jsonl).

Control CPU total 16 s (budget 5 core-minutes).
