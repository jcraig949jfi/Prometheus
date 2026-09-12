# Chop Shop calibration across three specimens (Lean simp, hypothesis shrinker, diomedes K0 census)

Date 2026-09-12. Requested by the N2 ruling ("updated calibration across all
three specimens"). Numbers from the three cuts.json files via cutledger.
Nothing here is a score; it is what the ledgers say side by side.

## The three questions and their answers

    Lean       Can Nyx catch a bad decomposition?      YES, but only by execution: CUT-2
               (paper) changed 7 kinds and falsified nothing; CUT-3 (one compile)
               falsified a control and found two boundaries the paper never would.
    Shrinker   Does the corrected knife transfer?     PARTLY, and the negative answers are
               the useful ones: K3 K2 K8 changed numbers as promised; K5 K6 ran and came
               back negative (null config really null; foreign callee not load-bearing).
    Census     Can Nyx refrain from inventing anatomy? YES on this specimen: 0 organs,
               0 pressures, two candidates tempted and refused on a PREREGISTERED
               duplicate control, five fishing impulses logged and none acted on.
               The null won because the control existed before inspection.

## Side by side

    quantity                              lean_simp     shrinker      census
    candidates at CUT-1                   23            18            12
    ORGAN at last cut                     4             6             0
    PRESSURE written                      4 (+1 held)   1 (+1 held)   0 (1 tempted, refused)
    inherited rate at CUT-1               0.87          0.56          1.00
    inherited-and-supported               0             2             6
    inherited-and-falsified               0             0             0
    boundaries drawn across defs          3             8             0
    executable contact before paper?      no            yes           yes (only cut)
    kind changes by argument / by run     7 / 1         0 / 1         0 / 0 (dispositions set once)
    independent-of-ancestor tests run     0             3             6 (all textbook recurrences)
    cheat controls fired / did not        1 / 1         3 / 1         3 / 0
    hidden machinery found                2 (eq_self;   1 (label      1 (LCG power-of-two
                                          unifier)      alignment)    bootstrap degeneracy)
    prediction of the knife's harshness   too harsh(P5) too harsh(P7) matched (P1)
    preregistered composite               FAILS         PASSES        n/a (no revision cut)
    consumer state                        #175 REJECTED_BLOCKED (182); #176 open
                                                        #190 #191 open   report to owner only

## The repeated calibration signal, tracked as ruled

    Lean      P5  "< half of 8 organs survive CUT-2"      5/8 survived      too harsh
    Shrinker  P7  "<= 2 of 7 survive"                    6 survived        too harsh
    Census    P1  "0 organs, 0 pressures"                0 / 0             matched
Two of three predictions about her own knife were too harsh; the third was
a null prediction and matched. The signal is NOT corrected for by
becoming more permissive (ruling): the two tempted census candidates were
refused on the preregistered control, not on a feeling that the count
should be low. The next positive specimen's harshness prediction should
be stated as a number with the same-kind survival metric, and the two
misses should be quoted beside it when it is written.

## Inherited boundaries: the rate is not the story

    Lean 0.87 with 0 supported; shrinker 0.56 with 2 inherited-and-supported;
    census 1.00 with 6 inherited-and-supported (every function that was run
    recomputed to a textbook quantity on foreign inputs; entropy read only). Three specimens, three different
    meanings of the same rate: on Lean it measured a habit; on the shrinker
    it measured where the programmer had already found the mechanism; on
    the census it measured a file made of textbook pieces. The four-category
    report the ruling asked for is what makes the three distinguishable.

## What execution did each time

    Lean      one 9 s compile: a negative control failed to fire -> two boundaries
    Shrinker  16 blocks, 1.4 s worst case: a consumer failure reproduced, one pass at 0 calls
    Census    self-test + 10 blocks: a bootstrap with zero width on power-of-two counts
On all three specimens the cut-changing or owner-relevant finding came from
running something, never from reading. Reading found the candidates;
running found what was wrong with them.

## Schema pressure noticed (not acted on; charter XV)

The census is an INSTRUMENT. The Chop Shop vocabulary has ORGAN, PRESSURE,
DATA, POLICY, SCAFFOLDING, COUPLED_CLUSTER, RECURRENCE. An instrument's
computations landed in RECURRENCE and its rules in POLICY, correctly, but
the thing as a whole -- "a check that refuses a claim before it is made" --
has no slot. Two readings: (a) the schema is right and instruments are
doctrine + statistics, which is what the cut found; (b) the schema forces
instruments into recurrence and a Chopper who only has this schema will
never see one as anatomy. Recorded as AMBIGUITY.md cut C; the format
changes only when a consumer's failure says so.

## Consumer state at this writing (00:10Z sync: 0 new)

    #176 Archaeon (Lean organs)                        DELIVERED, no return
    #189 Proteus+Vivarium (rewriting substrate claim)  question, no answer
    #190 Vivarium+Proteus (shrinker pressure)          DELIVERED, no return
    #191 Archaeon (shrinker organs)                    DELIVERED, no return
    #175 Vivarium (Lean pressures)                     REJECTED_BLOCKED via #182
    ORGANs CONSUMED: 0. Pressures OPERATIONALIZED: 0. Open architectural risk, unchanged.
