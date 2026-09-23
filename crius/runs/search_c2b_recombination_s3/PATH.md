PATH EVIDENCE run=search_c2b_recombination_s3 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     5     5     0        0             0        0
    50- 99 1200    12     7     0        0             0        0
   100-149 1200    27     9     0        0             0        0
   150-199 1200    12     8     0        0             0        0
   200-249 1200     7     4     0        0             0        0
   250-299 1200     8     3     0        0             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 11/301 iterations; longest consecutive run 6
  invoker   present in 12/301 iterations; longest consecutive run 4
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by    41 children: mean delta -15.808, improved    4 (9.8 pct) | others: mean -7.304, improved 27.6 pct
  invoker   newly carried by    31 children: mean delta -6.811, improved    9 (29.0 pct) | others: mean -7.355, improved 27.5 pct
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2214 splice children; 386 exceeded both parent and donor (or parent, when the donor is a PART)
