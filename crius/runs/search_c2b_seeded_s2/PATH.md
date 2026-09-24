PATH EVIDENCE run=search_c2b_seeded_s2 arm=seeded
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     8     6     0        0             0        0
    50- 99 1200    75    11     0        0             0        0
   100-149 1200     5     8     0        0             0        0
   150-199 1200     4     0     0        0             0        0
   200-249 1200     9     5     0        0             0        0
   250-299 1200     8    14     0        0             0        0
   300-300   24     1     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 19/301 iterations; longest consecutive run 10
  invoker   present in 11/301 iterations; longest consecutive run 2
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    54 children: mean delta -13.721, improved    6 (11.1 pct) | others: mean -9.724, improved 20.0 pct
  invoker   newly carried by    36 children: mean delta -10.616, improved    3 (8.3 pct) | others: mean -9.750, improved 20.0 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
