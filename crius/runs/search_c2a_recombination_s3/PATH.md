PATH EVIDENCE run=search_c2a_recombination_s3 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184     0     0     0        0             0        0
    50- 99 1200     0     0     0        0             0        0
   100-149 1200     0     0     0        0             0        0
   150-199 1200     0     0     0        0             0        0
   200-249 1200     0     0     0        0             0        0
   250-299 1200     0     0     0        0             0        0
   300-300   24     0     0     0        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 0/301 iterations; longest consecutive run 0
  invoker   present in 0/301 iterations; longest consecutive run 0
  planner   present in 0/301 iterations; longest consecutive run 0
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  never newly carried
  invoker   never newly carried
  planner   never newly carried
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2190 splice children; 384 exceeded both parent and donor (or parent, when the donor is a PART)
