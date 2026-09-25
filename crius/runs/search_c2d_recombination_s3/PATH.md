PATH EVIDENCE run=search_c2d_recombination_s3 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    13     1    20        0             0        0
    50- 99 1200    11    52     5        0             0        0
   100-149 1200     5    11     7        0             0        0
   150-199 1200     7    14    18        0             0        0
   200-249 1200     9     7    15        0             0        0
   250-299 1200    12    13    29        0             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 6/301 iterations; longest consecutive run 1
  invoker   present in 15/301 iterations; longest consecutive run 6
  planner   present in 13/301 iterations; longest consecutive run 2
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    57 children: mean delta -16.605, improved    4 (7.0 pct) | others: mean -9.555, improved 20.4 pct
  invoker   newly carried by    48 children: mean delta -12.511, improved    7 (14.6 pct) | others: mean -9.591, improved 20.4 pct
  planner   newly carried by    94 children: mean delta -15.460, improved    6 (6.4 pct) | others: mean -9.533, improved 20.5 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2244 splice children; 286 exceeded both parent and donor (or parent, when the donor is a PART)
