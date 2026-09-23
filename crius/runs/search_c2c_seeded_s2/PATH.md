PATH EVIDENCE run=search_c2c_seeded_s2 arm=seeded
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     6     7    11        0             0        0
    50- 99 1200     8    46   591        1             1        0
   100-149 1200     5     7    65        0             0        0
   150-199 1200    19     6   180        0             0        0
   200-249 1200     8     7    24        0             0        0
   250-299 1200     9    24    36        0             0        0
   300-300   24     0     1     1        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 10/301 iterations; longest consecutive run 5
  invoker   present in 12/301 iterations; longest consecutive run 5
  planner   present in 58/301 iterations; longest consecutive run 30
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    39 children: mean delta -14.039, improved    3 (7.7 pct) | others: mean -8.360, improved 24.1 pct
  invoker   newly carried by    54 children: mean delta -14.086, improved    6 (11.1 pct) | others: mean -8.347, improved 24.1 pct
  planner   newly carried by   247 children: mean delta -18.564, improved   16 (6.5 pct) | others: mean -8.029, improved 24.6 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 0 splice children; 0 exceeded both parent and donor (or parent, when the donor is a PART)
