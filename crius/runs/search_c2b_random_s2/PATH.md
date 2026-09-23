PATH EVIDENCE run=search_c2b_random_s2 arm=random
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184   169    42     0        5             0        1
    50- 99 1200    44    42     0        0             0        0
   100-149 1200     8     6     0        0             0        0
   150-199 1200     1     4     0        0             0        0
   200-249 1200     8     3     0        0             0        0
   250-299 1200    18    16     0        0             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 37/301 iterations; longest consecutive run 10
  invoker   present in 22/301 iterations; longest consecutive run 4
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    82 children: mean delta -0.478, improved   10 (12.2 pct) | others: mean -0.600, improved 30.2 pct
  invoker   newly carried by    47 children: mean delta -0.752, improved   10 (21.3 pct) | others: mean -0.597, improved 30.0 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
