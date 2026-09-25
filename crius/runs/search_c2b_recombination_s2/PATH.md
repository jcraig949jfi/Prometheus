PATH EVIDENCE run=search_c2b_recombination_s2 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     5     4     0        0             0        0
    50- 99 1200     6     7     0        0             0        0
   100-149 1200     5    29     0        1             0        1
   150-199 1200    10     9     0        0             0        0
   200-249 1200     3     4     0        0             0        0
   250-299 1200     8    59     0        1             0        0
   300-300   24     2     2     0        1             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 3/301 iterations; longest consecutive run 1
  invoker   present in 19/301 iterations; longest consecutive run 4
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    39 children: mean delta -12.874, improved    7 (17.9 pct) | others: mean -6.502, improved 27.9 pct
  invoker   newly carried by    65 children: mean delta -9.917, improved   14 (21.5 pct) | others: mean -6.506, improved 27.9 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2092 splice children; 376 exceeded both parent and donor (or parent, when the donor is a PART)
