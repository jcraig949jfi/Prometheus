C2 ACCESSIBILITY FRONTIER SUMMARY (DESIGN_C2 s8)
create/invk/invOwn/keep/typed = candidates (of 7208) that created a store object / invoked a block / invoked with own-created blocks / kept bytes or invoked / executed a typed op; qual columns = final-population top1 on sealed streams; take/blk = takeover-check outcomes; repro = qualified candidates with reuse_gain > 0 and competence kept on 3/3 streams; pos/rows = rows with reuse_gain > 0.

RUNG C2A
  gate: PASS (A=P B=P C=P D=P E=P F=P G=P H=P)  positive control: (see GATE.md header)
  PARTS: part             len dist     fit   solv    dFit    sign dSolv   tpFit  tpDFit
         P_BASE            19    0  21.924   21.5       -       -     -  21.924       -
         P_CAL             35   18  21.924   21.5  -0.000    0/10   0.0  21.924  -0.000
  run                       cands create invk invOwn keep typed | fitA   fitF  sucA sucF  reuse  blk invk chains | take blk | repro pos/rows
  search_c2a_random_s1       7208   3427 2800   2800 4531     0 |   7.23   6.20  7.0  6.0 4192.4 32.0 848.7      1 |  981 651 | 0 17/30
      lineage: reads 4541 -> 343, writes 7369 -> 9241, invokes 4299.8 -> 4128.0, blocks 0.0 -> 57.7, wsBytes 188 -> 1967, successes 2.2 -> 8.0
      candidates that invoked a block: 2800; of those in their iteration's top 8: 1026
  search_c2a_random_s2       7208   1736   28     28 2705     0 |   9.24   8.57  9.0  8.3  560.2 54.0  0.0      3 |  813 524 | 0 11/30
      lineage: reads 12 -> 3176, writes 5354 -> 3421, invokes 2142.2 -> 716.5, blocks 0.9 -> 43.6, wsBytes 41 -> 1037, successes 0.7 -> 6.0
      candidates that invoked a block: 28; of those in their iteration's top 8: 4
  search_c2a_random_s3       7208   3435   22     22 4178     0 |   3.52   3.52  3.3  3.3    0.0  0.0  0.0      2 |  995 712 | 0 0/30
      lineage: reads 5318 -> 23481, writes 15156 -> 54864, invokes 1545.3 -> 704.6, blocks 1.4 -> 0.0, wsBytes 1764 -> 5670, successes 2.6 -> 4.8
      candidates that invoked a block: 22; of those in their iteration's top 8: 1
  search_c2a_recombination_  7208    706    0      0 6028     0 |  21.77  21.77 21.3 21.3    0.0  0.0  0.0      6 | 1012 419 | 0 1/30
      lineage: reads 0 -> 66, writes 94 -> 381, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 139 -> 255, successes 21.4 -> 21.7
      candidates that invoked a block: 0; of those in their iteration's top 8: 0
  search_c2a_recombination_  7208   1657   14     14  187     0 |  20.08  20.08 19.7 19.7    0.0  0.0  0.0      4 | 1066 298 | 0 0/30
      lineage: reads 0 -> 0, writes 60 -> 0, invokes 29.1 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 20.9 -> 21.4
      candidates that invoked a block: 14; of those in their iteration's top 8: 0
  search_c2a_recombination_  7208    951    0      0  516     0 |  20.09  20.09 19.7 19.7    0.0  0.0  0.0      6 |  980 201 | 0 0/30
      lineage: reads 0 -> 3, writes 25 -> 0, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 21.2 -> 21.3
      candidates that invoked a block: 0; of those in their iteration's top 8: 0
  search_c2a_seeded_s1       7208    453    0      0  495     0 |  22.76  22.76 22.3 22.3    0.0  0.0  0.0      8 |  932 359 | 0 1/30
      lineage: reads 0 -> 681, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 0 -> 0, successes 21.5 -> 21.5
      candidates that invoked a block: 0; of those in their iteration's top 8: 0
  search_c2a_seeded_s2       7208    449    8      8 1035     0 |  22.09  22.09 21.7 21.7    0.0  0.0  0.0      8 |  845 429 | 1 3/30
      lineage: reads 68 -> 91, writes 162 -> 0, invokes 0.0 -> 35.9, blocks 0.0 -> 0.0, wsBytes 57 -> 0, successes 21.5 -> 22.0
      candidates that invoked a block: 8; of those in their iteration's top 8: 1
  search_c2a_seeded_s3       7208    555    4      4 1710     0 |  21.78  21.78 21.3 21.3    0.0  0.0  0.0      4 |  857 392 | 0 0/30
      lineage: reads 188 -> 79, writes 27 -> 100, invokes 0.0 -> 0.0, blocks 0.0 -> 0.0, wsBytes 5 -> 34, successes 21.3 -> 22.4
      candidates that invoked a block: 4; of those in their iteration's top 8: 0

RUNG C2B
  gate: PASS (A=P B=P C=P D=P E=P F=P G=P H=P)  positive control: PROCEDURE_REUSE_C1
  PARTS: part             len dist     fit   solv    dFit    sign dSolv   tpFit  tpDFit
         P_BASE            19    0  21.924   21.5       -       -     -  21.924       -
         P_REC             25    7  21.923   21.5  -0.001    0/10   0.0  21.923  -0.001
         P_INV             37   20  21.922   21.5  -0.002    0/10   0.0  21.922  -0.002
         P_REC_INV         43   26  23.060   22.6   1.138    7/10   1.1  22.846   0.924
  run                       cands create invk invOwn keep typed | fitA   fitF  sucA sucF  reuse  blk invk chains | take blk | repro pos/rows
  search_c2b_random_s1       7208   1736  148     41 7024  1532 |   6.57   3.85  6.3  3.7 6745.1 39.3  0.0      0 |  952 654 | 0 16/30
      lineage: reads 7481 -> 5037, writes 3487 -> 15847, invokes 0.0 -> 378.2, blocks 3.5 -> 15.3, wsBytes 0 -> 4647, successes 3.1 -> 4.4
      candidates that invoked a block: 148; of those in their iteration's top 8: 33
  search_c2b_random_s2       7208   2832  518    106 6210   356 |   2.84   2.84  2.7  2.7    6.3  3.0  0.0      3 | 1028 624 | 0 24/27
      lineage: reads 12 -> 3691, writes 0 -> 5402, invokes 0.0 -> 13.1, blocks 1.5 -> 15.3, wsBytes 0 -> 136, successes 1.7 -> 2.5
      candidates that invoked a block: 518; of those in their iteration's top 8: 179
  search_c2b_random_s3       7208   1186  196     52 6217   393 |   2.51   2.51  2.3  2.3    5.8  1.0  0.0      1 |  912 714 | 0 27/30
      lineage: reads 4992 -> 16797, writes 12175 -> 19831, invokes 4.3 -> 0.0, blocks 2.0 -> 12.8, wsBytes 4363 -> 8116, successes 2.9 -> 5.5
      candidates that invoked a block: 196; of those in their iteration's top 8: 65
  search_c2b_recombination_  7208    336   38      2 7142  2287 |  19.05  19.05 18.7 18.7    7.1  1.0  0.0      7 |  971 326 | 6 27/30
      lineage: reads 20 -> 22, writes 164 -> 178, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 328 -> 338, successes 20.9 -> 21.3
      candidates that invoked a block: 38; of those in their iteration's top 8: 9
  search_c2b_recombination_  7208   2069  222    126 7111   150 |  20.75  20.75 20.3 20.3    6.8 32.0  0.0      6 |  918 316 | 0 30/30
      lineage: reads 0 -> 56, writes 0 -> 186, invokes 0.0 -> 0.0, blocks 2.0 -> 17.7, wsBytes 0 -> 38, successes 21.4 -> 20.7
      candidates that invoked a block: 222; of those in their iteration's top 8: 31
  search_c2b_recombination_  7208    268   29      2 6982   107 |  22.78  22.78 22.3 22.3    7.1  1.0  0.0      7 |  877 333 | 0 30/30
      lineage: reads 11 -> 11, writes 17 -> 24, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.3 -> 22.3
      candidates that invoked a block: 29; of those in their iteration's top 8: 3
  search_c2b_seeded_s1       7208   2323   48     16 7011  2241 |  19.41  19.41 19.0 19.0    7.2  1.0  0.0      4 |  938 394 | 0 30/30
      lineage: reads 0 -> 16, writes 0 -> 58, invokes 0.0 -> 0.0, blocks 2.0 -> 7.9, wsBytes 0 -> 17, successes 21.4 -> 21.2
      candidates that invoked a block: 48; of those in their iteration's top 8: 13
  search_c2b_seeded_s2       7208    704   45      4 6648   154 |  21.76  21.76 21.3 21.3    7.2  1.0  0.0      6 |  711 299 | 0 30/30
      lineage: reads 71 -> 44, writes 4 -> 0, invokes 0.0 -> 0.0, blocks 4.3 -> 2.0, wsBytes 0 -> 0, successes 21.7 -> 22.0
      candidates that invoked a block: 45; of those in their iteration's top 8: 6
  search_c2b_seeded_s3       7208    373   44      2 6953   168 |  22.76  22.75 22.3 22.3    7.1  1.0  0.0      7 |  431 232 | 0 30/30
      lineage: reads 0 -> 0, writes 0 -> 0, invokes 0.0 -> 0.0, blocks 2.0 -> 2.0, wsBytes 0 -> 0, successes 21.1 -> 21.9
      candidates that invoked a block: 44; of those in their iteration's top 8: 11

RUNG C2C
  gate: FAIL (A=P B=P C=P D=P E=F F=P G=P H=F)  positive control: (see GATE.md header)
  PARTS: part             len dist     fit   solv    dFit    sign dSolv   tpFit  tpDFit
         P_BASE            19    0  21.924   21.5       -       -     -  21.924       -
         P_REC             25    7  21.923   21.5  -0.001    0/10   0.0  21.923  -0.001
         P_INV             37   20  21.922   21.5  -0.002    0/10   0.0  23.162   1.238
         P_REC_INV         43   26  23.060   22.6   1.138    7/10   1.1  23.068  -0.094
         P_PLAN            58   41  21.867   21.5  -0.057    0/10   0.0  38.665  16.741
         P_REC_INV_PLAN    64   47  37.841   37.4  15.974   10/10  15.9  38.664  -0.000
  run                       cands create invk invOwn keep typed | fitA   fitF  sucA sucF  reuse  blk invk chains | take blk | repro pos/rows

RUNG C2D
  run                       cands create invk invOwn keep typed | fitA   fitF  sucA sucF  reuse  blk invk chains | take blk | repro pos/rows
