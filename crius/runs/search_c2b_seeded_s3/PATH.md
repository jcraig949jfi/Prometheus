PATH EVIDENCE run=search_c2b_seeded_s3 arm=seeded
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    14    24     0        0             0        0
    50- 99 1200     8     4     0        0             0        0
   100-149 1200    12    21     0        0             0        0
   150-199 1200     8    21     0        0             0        0
   200-249 1200     6    17     0        0             0        0
   250-299 1200    18    16     0        1             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 14/301 iterations; longest consecutive run 2
  invoker   present in 31/301 iterations; longest consecutive run 5
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    59 children: mean delta -15.074, improved    6 (10.2 pct) | others: mean -11.283, improved 14.5 pct
  invoker   newly carried by    67 children: mean delta -11.957, improved    9 (13.4 pct) | others: mean -11.308, improved 14.5 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
