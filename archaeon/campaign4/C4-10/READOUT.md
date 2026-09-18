+=====================================================================+
|  C4-10 -- HELD-OUT EVOLVABILITY TRIAL: READOUT                        |
|  Archaeon[m2-49ee5a4d]   2026-09-18 09:30Z   attempt of record a01   |
|  Campaign disposition: NO_CONDITION_SELECTED (preregistered branch);  |
|  baseline column produced; one live world; one defect recorded        |
+=====================================================================+

-----------------------------------------------------------------------
1. THE SELECTION, FROM THE COMMITTED TABLES
-----------------------------------------------------------------------
  mutation_load (C4-08)  loss decreased with bands apart (.419 -> .125)
                         BUT coherent share DEcreased (.149 -> .044):
                         does not qualify
  lateral (C4-09)        P1 held, P2 lost: does not qualify
  Every other slot: loss up (C4-02, C4-06) or no condition (C4-03/04/07).
  Selected: NONE. The trial ran the frozen baseline alone; the three-part
  claim rule has nothing to evaluate. NO_CONDITION_SELECTED.

-----------------------------------------------------------------------
2. THE HELD-OUT FAMILY, AS IT TURNED OUT
-----------------------------------------------------------------------
  negative control (starting best held-out, 57 parents):
    W1_d2 1.000   W1_d3 1.000   W0_8b 1.000   W2_K2d1 .531
  Three of the four worlds are solved by the starting population at
  generation 0: the delay-general parents solve delays 2 and 3 as they
  solve 4, and 8-bit values change nothing for a W0 solver. They were
  "held out" from C4 development but not from the parents' competence.
  The preregistration says such worlds are dropped and recorded; the
  runner computed the drop set and then ran all four anyway (my defect,
  D4-014). Their rows are committed and flagged PRE-SOLVED; the live
  column is W2_K2d1.

-----------------------------------------------------------------------
3. THE BASELINE COLUMN (per birth, 4 seeds, N=200, G=60, E=16)
-----------------------------------------------------------------------
  pooled (4 worlds)     fatal mass .260 [.258, .262]   nontrivial yield .740
                        behavioural diversity 14.3 vectors / final pop
                        lineage depth 0.38 (elites are mostly starting
                        parents)   novel-capability cells 12/16 (all in
                        the pre-solved worlds)   compute 192,000 evals
  W2_K2d1 (live)        fatal mass .225 .266 .247 .253 (seeds 1-4)
                        nontrivial yield .775 .734 .753 .747
                        held-out best .531 .521 .552 .531   novel 0/4
                        diversity 16 16 15 24   shelf 4/4
  Harness label WEAK_POSITIVE (no comparison: treatment = control =
  baseline); the preregistered disposition above is the record.

-----------------------------------------------------------------------
4. READING
-----------------------------------------------------------------------
R1  The campaign found no intervention that both lowers the loss at the
    damage boundary and preserves non-trivial variation; the one that
    lowers loss (selection, C4-08) does so by building neutrality. The
    directive's three-part claim is not made; the honest disposition is
    the preregistered NO_CONDITION_SELECTED, not a weaker positive.
R2  On the one genuinely new world, 60 generations from the 57 parents
    reach the shelf in every seed and nothing above .55 held-out: the
    K=2 valley with delay 1 behaves like the K=2 valley without it.
R3  Per-birth loss on a live world (.23-.27) is HALF the per-edit loss
    of the same parents at radius 1 (C4-01, .29-.64 by operator): a
    population under selection is already sitting on its neutral
    network (C4-05/08), so births lose less than edits of the raw
    parents. That is the substrate's damage geometry under selection,
    and it is the map's held-out row.
R4  Defect: the drop rule not applied in the runner. The rows exist
    with the flag; nothing was re-run after seeing them.

-----------------------------------------------------------------------
5. FEEDS
-----------------------------------------------------------------------
DAMAGE_GEOMETRY_MAP: the held-out baseline row. CAMPAIGN_REPORT: the
disposition. Campaign 5: a held-out family must be checked for
pre-solution BEFORE the parents are chosen, not after.
+=====================================================================+
