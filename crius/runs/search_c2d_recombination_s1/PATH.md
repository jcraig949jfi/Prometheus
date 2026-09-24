PATH EVIDENCE run=search_c2d_recombination_s1 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     8    20   105        1             0        0
    50- 99 1200     6   585    25        3             1        0
   100-149 1200     5   288    48        0             0        0
   150-199 1200     3     7    18        0             0        0
   200-249 1200     7     9     6        0             0        0
   250-299 1200     1     3     5        0             0        0
   300-300   24     3     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 4/301 iterations; longest consecutive run 1
  invoker   present in 51/301 iterations; longest consecutive run 46
  planner   present in 20/301 iterations; longest consecutive run 12
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    30 children: mean delta -11.152, improved    8 (26.7 pct) | others: mean -6.291, improved 30.2 pct
  invoker   newly carried by    40 children: mean delta -12.467, improved    5 (12.5 pct) | others: mean -6.277, improved 30.3 pct
  planner   newly carried by   109 children: mean delta -11.578, improved   20 (18.3 pct) | others: mean -6.230, improved 30.3 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2159 splice children; 465 exceeded both parent and donor (or parent, when the donor is a PART)
