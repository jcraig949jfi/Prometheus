PATH EVIDENCE run=search_c2c_random_s2 arm=random
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    42   235   120        0             0        0
    50- 99 1200    25    21   119        0             0        0
   100-149 1200    30    22   132        0             0        0
   150-199 1200    17   127    54        4             0        0
   200-249 1200    16    71    91        1             1        0
   250-299 1200    28    21    88        0             0        0
   300-300   24     1     1     3        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 37/301 iterations; longest consecutive run 5
  invoker   present in 93/301 iterations; longest consecutive run 12
  planner   present in 150/301 iterations; longest consecutive run 10
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by   120 children: mean delta -0.011, improved    3 (2.5 pct) | others: mean -0.038, improved 2.6 pct
  invoker   newly carried by   115 children: mean delta -0.060, improved    1 (0.9 pct) | others: mean -0.037, improved 2.6 pct
  planner   newly carried by   278 children: mean delta -0.036, improved    3 (1.1 pct) | others: mean -0.038, improved 2.6 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
