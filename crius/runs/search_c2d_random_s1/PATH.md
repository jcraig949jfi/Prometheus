PATH EVIDENCE run=search_c2d_random_s1 arm=random
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    10    10    67        0             0        0
    50- 99 1200   106    13    45        2             1        0
   100-149 1200    42    24    60        0             0        0
   150-199 1200    20   148   154        2             0        0
   200-249 1200    15    37   407        0             0        0
   250-299 1200    19    25   126        0             0        0
   300-300   24     1     0     2        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 51/301 iterations; longest consecutive run 5
  invoker   present in 47/301 iterations; longest consecutive run 7
  planner   present in 150/301 iterations; longest consecutive run 28
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    98 children: mean delta -0.115, improved    2 (2.0 pct) | others: mean -0.069, improved 4.8 pct
  invoker   newly carried by   100 children: mean delta -0.061, improved    1 (1.0 pct) | others: mean -0.070, improved 4.8 pct
  planner   newly carried by   226 children: mean delta -0.063, improved    5 (2.2 pct) | others: mean -0.070, improved 4.8 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
