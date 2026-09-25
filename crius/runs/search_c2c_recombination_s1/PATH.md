PATH EVIDENCE run=search_c2c_recombination_s1 arm=recombination
PARTS-op frequencies (candidates per window of 50 iterations executing the op at least once on a stream)
  window   n   rec   inv  plan  rec+inv  rec+inv+plan  ownInvoke(solved>seed)
     0- 49 1184   398    12    24        3             0        0
    50- 99 1200  1033    33   960       31            31        0
   100-149 1200   283    10  1109        6             6        0
   150-199 1200    60     4  1101        0             0        0
   200-249 1200    62    14    19        2             0        0
   250-299 1200    37     2    41        0             0        0
   300-300   24     0     0     1        0             0        0
Survival of typed ops in the ELITE (top 8 by fitness per iteration): iterations present / longest consecutive run
  recorder  present in 116/301 iterations; longest consecutive run 84
  invoker   present in 14/301 iterations; longest consecutive run 4
  planner   present in 157/301 iterations; longest consecutive run 146
Selectable foothold: children's fitness minus parent's, by typed op carried (same iteration streams do not
  apply to parents; delta uses each record's own fitness, so this is a coarse, not paired, measure)
  recorder  newly carried by   144 children: mean delta -9.566, improved   28 (19.4 pct) | others: mean -5.733, improved 31.3 pct
  invoker   newly carried by    38 children: mean delta -6.798, improved   13 (34.2 pct) | others: mean -5.804, improved 31.1 pct
  planner   newly carried by    76 children: mean delta -13.944, improved   17 (22.4 pct) | others: mean -5.722, improved 31.2 pct
First candidate with recorder + invoker + own invocation + solved > 22 (proxy for a complete mechanism): None
Recombination: 2143 splice children; 431 exceeded both parent and donor (or parent, when the donor is a PART)
