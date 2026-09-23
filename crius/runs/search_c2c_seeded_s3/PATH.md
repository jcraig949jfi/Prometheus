PATH EVIDENCE run=search_c2c_seeded_s3 arm=seeded
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    14    11    72        0             0        0
    50- 99 1200    11     5    11        0             0        0
   100-149 1200    11    26    22        0             0        0
   150-199 1200    16    41    29        5             0        0
   200-249 1200    13    36    30        0             0        0
   250-299 1200    20     9  1084        0             0        0
   300-300   24     0     1    24        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 13/301 iterations; longest consecutive run 2
  invoker   present in 29/301 iterations; longest consecutive run 4
  planner   present in 83/301 iterations; longest consecutive run 55
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    72 children: mean delta -13.018, improved   12 (16.7 pct) | others: mean -7.754, improved 23.4 pct
  invoker   newly carried by    93 children: mean delta -10.614, improved   15 (16.1 pct) | others: mean -7.770, improved 23.5 pct
  planner   newly carried by    70 children: mean delta -11.079, improved   17 (24.3 pct) | others: mean -7.775, improved 23.4 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
