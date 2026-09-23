PATH EVIDENCE run=search_c2c_seeded_s1 arm=seeded
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     8     9   283        0             0        0
    50- 99 1200     8    48    98        0             0        0
   100-149 1200    33    52   146        0             0        0
   150-199 1200    41    85   234        1             1        0
   200-249 1200     4    10   226        0             0        0
   250-299 1200    32     9   110        0             0        0
   300-300   24     1     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 14/301 iterations; longest consecutive run 6
  invoker   present in 29/301 iterations; longest consecutive run 6
  planner   present in 82/301 iterations; longest consecutive run 17
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by   104 children: mean delta -16.911, improved    6 (5.8 pct) | others: mean -9.724, improved 21.2 pct
  invoker   newly carried by   190 children: mean delta -14.586, improved   24 (12.6 pct) | others: mean -9.699, improved 21.2 pct
  planner   newly carried by   821 children: mean delta -17.056, improved   58 (7.1 pct) | others: mean -8.899, improved 22.8 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
