PATH EVIDENCE run=search_c2b_recombination_s1 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     5    16     0        0             0        0
    50- 99 1200     7     8     0        0             0        0
   100-149 1200     2     3     0        0             0        0
   150-199 1200     7     7     0        0             0        0
   200-249 1200     5  1034     0        1             0        0
   250-299 1200     8  1171     0        8             0        0
   300-300   24     0    23     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 4/301 iterations; longest consecutive run 1
  invoker   present in 103/301 iterations; longest consecutive run 97
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    34 children: mean delta -12.922, improved    3 (8.8 pct) | others: mean -6.183, improved 31.1 pct
  invoker   newly carried by    27 children: mean delta -6.005, improved   11 (40.7 pct) | others: mean -6.216, improved 31.0 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2189 splice children; 429 exceeded both parent and donor (or parent, when the donor is a PART)
