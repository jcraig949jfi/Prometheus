PATH EVIDENCE run=search_c2b_random_s3 arm=random
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     9    31     0        0             0        0
    50- 99 1200    24   114     0        4             0        0
   100-149 1200    34    15     0        0             0        0
   150-199 1200    22    12     0        0             0        0
   200-249 1200    25     9     0        0             0        0
   250-299 1200    19    82     0        4             0        1
   300-300   24     5     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 30/301 iterations; longest consecutive run 6
  invoker   present in 48/301 iterations; longest consecutive run 9
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    76 children: mean delta -1.319, improved   11 (14.5 pct) | others: mean -1.139, improved 23.8 pct
  invoker   newly carried by    73 children: mean delta -1.082, improved   13 (17.8 pct) | others: mean -1.142, improved 23.7 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
