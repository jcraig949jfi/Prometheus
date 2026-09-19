C2 PARTS DIAGNOSTIC rung=c2b (gate streams [301, 302, 303, 304, 305, 306, 307, 308, 309, 310]; controls only)
ENUMERATE_VM (search seed): fit 21.720 solved 21.3 cost 9843
part            ancestor      len dist |     fit  solv    cost |    dFit  sign  dSolv  dCost |   tpFit tpSol  tpDFit  procs
P_BASE          -              19    0 |  21.924  21.5    9378 |       -     -      -      - |  21.924  21.5       -    1.0
P_REC           P_BASE         25    7 |  21.923  21.5    9485 |  -0.001  0/10    0.0    108 |  21.923  21.5  -0.001   22.5
P_INV           P_BASE         37   20 |  21.922  21.5    9592 |  -0.002  0/10    0.0    214 |  21.922  21.5  -0.002    1.0
P_REC_INV       P_INV          43   26 |  23.060  22.6    4976 |   1.138  7/10    1.1  -4616 |  22.846  22.4   0.924    5.1
dist = instruction edit distance from P_BASE; dFit = part - ancestor (paired, same streams); sign = streams with dFit > 0;
tp* = store pre-loaded from PROCEDURE_REUSE_C1's end-of-lifetime artifacts on the same stream; procs = objects created per lifetime
