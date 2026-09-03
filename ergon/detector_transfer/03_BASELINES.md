# 03 - BASELINE TRANSLATION TABLE

The eight baselines frozen in T_, carried forward with preregistered status
preserved. Where translation changed a baseline, ORIGINAL / TRANSLATED /
REASON / CONSEQUENCE are recorded rather than edited silently.

    id  ORIGINAL (Avida T_)          TRANSLATED
    --  ---------------------------  ------------------------------------------
    b1  current task count           count of nonzero components of P(g)
    b2  current merit                s(g)
    b3  current fitness              s(g) after the world's selection transform,
                                     if distinct from b2
    b4  genome length                L
    b5  pd-distance to next change   steps to next realized change  [LOOK-AHEAD]
    b6  cLandscape POS/NEUT/NEG/DEAD scalar neighbourhood summary: fractions of
                                     neighbours better / equal / worse / invalid
    b7  mutation viability           1 - fraction(BOTTOM)
    b8  pd-distance to EQU           steps to the endpoint of interest [LOOK-AHEAD]

    id  Failure mode caught                      If it fires
    --  ---------------------------------------  ---------------------------
    b1  detector tracks current capability       signal is a capability proxy
    b2  detector tracks the very scalar it       FATAL: channel adds nothing
        claims to beat
    b3  as b2, selection-scaled                  as b2
    b4  entropy grows mechanically with          signal is a LENGTH ARTEFACT
        neighbourhood size L*(A-1)
    b5  ceiling: a real detector cannot use it   not competitive with knowing
                                                 the answer
    b6  the historical instrument, reconstructed FATAL: the scalar
                                                 neighbourhood already had it
    b7  signal is just robustness                robustness, not latent structure
    b8  ceiling                                  as b5

TWO TRANSLATION NOTES, recorded rather than absorbed:

b4 IS PROMOTED IN IMPORTANCE. In Avida, length varied only 50->61. In a general
substrate L may vary widely, and since |N1| = L*(A-1), entropy over a larger
neighbourhood is mechanically larger. Any modern report MUST condition on L or
hold it fixed. CONSEQUENCE: an uncontrolled-L design is uninterpretable and
should return DETECTOR_UNIDENTIFIABLE.

b6 IS THE DECISIVE BASELINE. It is the modern reconstruction of the historical
cLandscape instrument. If b6 predicts the events as well as the phenotype
channel, the hypothesis is dead. This is the cheapest available kill and should
be computed FIRST.

Decision rule preserved from T_: if any of b1-b4, b6, b7 predicts realized
events as well as the phenotype-partitioned measures, the signal is KILLED.
