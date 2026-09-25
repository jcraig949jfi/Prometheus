PATH EVIDENCE run=search_c2c_recombination_s2 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     8     6     9        0             0        0
    50- 99 1200    34    33    17        1             0        0
   100-149 1200    10     7    11        0             0        0
   150-199 1200     8     6    39        0             0        0
   200-249 1200     2     3    12        0             0        0
   250-299 1200     7     5    10        0             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 10/301 iterations; longest consecutive run 2
  invoker   present in 14/301 iterations; longest consecutive run 5
  planner   present in 16/301 iterations; longest consecutive run 4
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    47 children: mean delta -14.893, improved    7 (14.9 pct) | others: mean -5.388, improved 31.8 pct
  invoker   newly carried by    41 children: mean delta -7.624, improved    9 (22.0 pct) | others: mean -5.437, improved 31.7 pct
  planner   newly carried by    62 children: mean delta -11.011, improved   11 (17.7 pct) | others: mean -5.402, improved 31.8 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 1862 splice children; 403 exceeded both parent and donor (or parent, when the donor is a PART)
