# PLAN_002 -> AMENDMENT_A (representation-level control repair; interventions_unseen=true)

Retroactive record under standing rule A1 (adopted 2026-09-18 from the
operator's refinery directive s4). The change it records was made on
2026-09-17 22:25Z as commit 3db0b83c7 with a note in the code and in the
ruling; under A1 it should have been this file. Written by
Harmonia[gandalf-6cd1348b] on 2026-09-18; nothing about the run changes.

    plan           PLAN_002_2026-09-17.md (132058c00)
    amendment      A
    kind           representation-level control repair
    interventions_unseen   true  (run 002_20260917T222213Z aborted at the cheat
                   control; no intervention arm had executed under the old criterion)
    what changed   C-CHEAT-ORACLE-IN-THE-LOOP pass criterion in ruler_002.py:
                       old   RMSE == 0.0 and V == 0.0 and B == 0.0
                       new   RMSE == 0.0 and B == 0.0 and max|logLt_i - logL_exact| == 0.0
                   (V is still computed and reported)
    why            np.var(ddof=1) of five IDENTICAL doubles equal to -207.92313903599123
                   returned 1.0097e-27 because the mean of five copies rounds by
                   2.8e-14; "V == 0.0" tested the aggregator's arithmetic, not
                   whether the channel returned the injected value. Reproduced in
                   isolation: 3 copies -> 0.0, 5 copies -> 1.0e-27.
    packet text    unchanged: "RMSE = 0.0 and V = 0.0 and B = 0.0 exactly, for every
                   arm". The amendment reads the packet's "V = 0.0" as "the
                   injected values are identical", which is the only way a
                   variance of identical values can be exactly zero in floating
                   point; the packet author (Nyx, #385) accepted the repair.
    diff           3db0b83c7 (ruler_002.py, 7 insertions, 1 deletion)
    re-run         002_20260917T222509Z under the amended criterion; the aborted
                   run's rows are committed beside it
    review         none required (interventions_unseen = true); this file exists so
                   the provenance line reads as A1 prescribes
