PATH EVIDENCE run=search_c2c_recombination_s3 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    69     3    17        1             0        1
    50- 99 1200    38    38    11        2             0        0
   100-149 1200     2    32     8        0             0        0
   150-199 1200    11     8    23        0             0        0
   200-249 1200     8     4     6        0             0        0
   250-299 1200     4     4     5        0             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 8/301 iterations; longest consecutive run 2
  invoker   present in 7/301 iterations; longest consecutive run 1
  planner   present in 10/301 iterations; longest consecutive run 2
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by   125 children: mean delta -15.170, improved    8 (6.4 pct) | others: mean -7.394, improved 26.9 pct
  invoker   newly carried by    88 children: mean delta -15.264, improved    6 (6.8 pct) | others: mean -7.433, improved 26.8 pct
  planner   newly carried by    68 children: mean delta -12.414, improved   10 (14.7 pct) | others: mean -7.482, improved 26.6 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2182 splice children; 377 exceeded both parent and donor (or parent, when the donor is a PART)
