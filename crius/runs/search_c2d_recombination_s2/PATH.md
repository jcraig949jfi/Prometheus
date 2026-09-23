PATH EVIDENCE run=search_c2d_recombination_s2 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     4     5    12        0             0        0
    50- 99 1200     6   440    23        2             0        0
   100-149 1200     6     4     7        0             0        0
   150-199 1200     5     7    11        0             0        0
   200-249 1200    17    29     8        0             0        0
   250-299 1200    10    22    13        1             0        1
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 6/301 iterations; longest consecutive run 2
  invoker   present in 28/301 iterations; longest consecutive run 23
  planner   present in 8/301 iterations; longest consecutive run 3
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    34 children: mean delta -13.355, improved    3 (8.8 pct) | others: mean -7.618, improved 24.8 pct
  invoker   newly carried by    76 children: mean delta -15.850, improved    7 (9.2 pct) | others: mean -7.557, improved 24.9 pct
  planner   newly carried by    70 children: mean delta -14.824, improved    5 (7.1 pct) | others: mean -7.575, improved 24.9 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2176 splice children; 353 exceeded both parent and donor (or parent, when the donor is a PART)
