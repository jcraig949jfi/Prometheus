PATH EVIDENCE run=search_c2c_random_s3 arm=random
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184    50    16   110        0             0        0
    50- 99 1200    13    30    54        0             0        0
   100-149 1200    55    77    37        2             0        0
   150-199 1200    15     7    56        0             0        0
   200-249 1200    34    12    78        0             0        0
   250-299 1200   555    14   200        8             7        2
   300-300   24    24     0    24        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 59/301 iterations; longest consecutive run 28
  invoker   present in 45/301 iterations; longest consecutive run 9
  planner   present in 84/301 iterations; longest consecutive run 11
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    99 children: mean delta -0.345, improved   12 (12.1 pct) | others: mean -0.666, improved 15.7 pct
  invoker   newly carried by    76 children: mean delta -0.405, improved   14 (18.4 pct) | others: mean -0.664, improved 15.6 pct
  planner   newly carried by   197 children: mean delta -0.632, improved   17 (8.6 pct) | others: mean -0.662, improved 15.8 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
