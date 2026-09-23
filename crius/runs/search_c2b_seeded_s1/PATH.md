PATH EVIDENCE run=search_c2b_seeded_s1 arm=seeded
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    20    19     0        0             0        0
    50- 99 1200     2    11     0        0             0        0
   100-149 1200    16    14     0        0             0        0
   150-199 1200   619     5     0        2             0        0
   200-249 1200  1001    19     0       16             0        7
   250-299 1200   531     7     0        6             0        0
   300-300   24     1     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 113/301 iterations; longest consecutive run 103
  invoker   present in 16/301 iterations; longest consecutive run 2
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by   146 children: mean delta -18.100, improved    7 (4.8 pct) | others: mean -7.518, improved 26.1 pct
  invoker   newly carried by    59 children: mean delta -12.468, improved    6 (10.2 pct) | others: mean -7.693, improved 25.8 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
