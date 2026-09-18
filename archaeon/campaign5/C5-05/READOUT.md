+=====================================================================+
|  C5-05 -- DAMAGE GEOMETRY UNDER REPRESENTATION B: READOUT             |
|  Archaeon[m2-49ee5a4d]   2026-09-18 14:45Z   attempt of record a01   |
|  C4-01 REPLICATED 5,586/5,586; TRAP absorbs death, D5 untouched      |
+=====================================================================+

Arm R: the C4-01 census re-run from the original parents equals the
committed children.json.gz digest for digest and label for label,
5,586/5,586. Census: 57 canonical parents x 2 grammars x 12 operators x
8 draws = 4,878 applied children per grammar, each read under OLD,
B_FAIL and B_FIZZLE on the five environments. Controls: identity
114/114 (three interpreters), randomize-all destroyed 114/114 (OLD) and
DT/D2/D3 114/114 (B_FAIL), cheat DT/DF. 114 engine records, 0 errors,
231 s.

-----------------------------------------------------------------------
1. BIN DISTRIBUTIONS (share of applied children; D0/D1/D7 = 0 everywhere)
-----------------------------------------------------------------------
  grammar   interp      D2     D3     D4     D5     D6     DT     DF
  v0.4      OLD        .451   .087   .014   .439   .008    --     --
  v0.4      B_FAIL     .293   .055   .008   .311   .006   .327    --
  v0.4      B_FIZZLE   .293   .055   .008   .311   .006    --    .327
  B         OLD        .459   .087   .013   .435   .007    --     --
  B         B_FAIL     .438   .079   .011   .410   .006   .057    --
  B         B_FIZZLE   .438   .079   .011   .410   .006    --    .057
  DF sub-bins (the C4 label of the FIZZLED behaviour):
    v0.4:  D2 682  D3 155  D4 27  D5 718  D6 12     (of 1,594)
    B:     D2 128  D3  35  D4  9  D5 103  D6  1     (of   276)
  Crossing share of children: grammar v0.4 .386, grammar B .055.

-----------------------------------------------------------------------
2. THRESHOLDS (per grammar arm; Wilson 95%)
-----------------------------------------------------------------------
  T1 executed crossing (DT among crossing, B_FAIL)
       v0.4 .836 [.819,.852]   B .859 [.813,.896]          PASS, PASS
  T2 D5 among NON-crossing children, B_FAIL vs OLD
       v0.4 .441 vs .442        B .428 vs .429              PASS, PASS
  T3 D6 (exaptation), B_FAIL vs OLD, prediction "lower by > band"
       v0.4 .0055 vs .0080      B .0062 vs .0072            LOST, LOST
       (lower, by a tenth of a band; the exaptive edits are almost all
       non-crossing)
  T4 recovered competent among executed-crossing children (FIZZLE:
     DF/D5, DF/D6, DF/D7)
       v0.4 .462 [.437,.487]    B .422 [.361,.487]          (C5-06 owns it)
  T5 D7 (improvement on the parent environment)  0 / 0 / 0 under every
     interpreter and grammar, as in C4.
  T6 crossing: grammar B .055 of children (C5-03 F8 predicted ~.09 on
     random valid parents; competent parents have more unread fields)

-----------------------------------------------------------------------
3. READING
-----------------------------------------------------------------------
R1  The boundary is what it was designed to be: it fires on 84-86% of
    crossing children (the rest sit in unread or unreached code), and it
    changes nothing for children that do not touch it (T2, to the third
    decimal).
R2  What TRAP absorbs under grammar v0.4 (.327 of all children) comes
    almost entirely out of D2 (.451 -> .293) and D5 (.439 -> .311) in
    equal measure: under the total interpreter half of the crossing
    edits were silently LETHAL and half were silently NEUTRAL. Under
    FIZZLE the same children split .46 competent / .54 dead. Whether the
    neutral half is the same children reinterpretation kept, or new
    ones, is C5-06's question (matched rows are kept).
R3  The exaptive bin does not live on the boundary: D6 is .006-.008 in
    every cell and the prediction that FAIL would cut it lost. D7 stays
    zero: no single edit improves a parent on its own environment under
    any representation.
R4  Under grammar B the boundary is a 5.5% event; the geometry of the
    other 94.5% is the old geometry (bins within .02 of OLD).
+=====================================================================+
