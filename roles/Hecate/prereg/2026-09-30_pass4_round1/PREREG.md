# PREREG -- Hecate Pass 4 (first falsification), round 1 (HECATE-09)

Frozen: 2026-09-30Z, before any Pass 4 code exists. Author:
Hecate[m1-dd0c3882]. Applies to the three round-1 SIGNAL worlds
(hecate/programs/PROBE_ROUND1_REPORT.json, commit 0097e7822).

## What the author already knows (declared, because it shapes the attacks)

Round-1 rows already show: (71b6) a fixed-L1 listener ties the adaptive
listener on accuracy at lower depth; (321a) the resistance step sits
exactly at the textbook decoding radius; (5b0b) failure is determined
by endpoint location, which correlates with "lucky". So two of the three
attacks below are expected to kill the ORIGINAL-world claim. Each world
therefore also gets one ALTERNATIVE-IMPLEMENTATION attack (charter Pass 4
list) that asks whether the mechanism survives where the trivial
explanation is removed by construction. Survival is decided by that
attack plus replication, never by the original world alone.

## Common rules

- Fresh implementer instance per world; it may read the round-1 world
  directory for its world only. Faithfulness guard, rows per (arm, seed),
  positive + cheat controls, evaluator-in-code: as in
  ../2026-09-29_probe_round1/PREREG.md.
- NEW (from round-1 lessons): the evaluator first reports ONLY the
  positive and cheat controls; treatment statistics are computed only
  after both are detected. If a control fails, one repair is allowed
  before any treatment statistic has been printed.
- Replication (R) uses fresh seeds disjoint from round 1, n as stated.
- <= 10 CPU core-minutes per world.

## Predicate per world: SURVIVES iff R reproduces the round-1 SIGNAL
## AND the ALT attack passes AND controls are detected in every arm set.
## The ORIGINAL-world attack is recorded; if it fires, the original-world
## claim is FOSSIL (with rows) whatever ALT does.

### HT-71b65251aa W3 (adaptive pragmatic depth)

  R    seeds 100-109; round-1 success rule reproduces at theta 0.6.
  ORIG kill if fixed-L1 accuracy >= adaptive accuracy - 0.005 AND fixed-L1
       mean depth <= adaptive mean depth (adaptivity is dominated).
  ALT  a speaker variant under which depth matters, fixed BEFORE any
       listener runs: fixed-L2 accuracy - fixed-L1 accuracy >= 0.02
       (checked first; if not met, ALT is NOT_ELIGIBLE and recorded, the
       implementer may choose one other speaker variant, once). Pass iff
       adaptive accuracy >= fixed-L2 accuracy - 0.01 AND adaptive mean
       depth <= 0.8 x fixed-L2 depth AND Spearman(depth, listener
       uncertainty) >= 0.5, over 10 seeds.

### HT-321a8fd8e0 W1 (code-decoded outcome rule)

  R    seeds 100-119; step at k = 4 reproduces for BCH(31,16).
  ORIG kill if, for at least two further codes of different minimum
       distance d (e.g. d = 3 and d = 5), the manipulation fraction is 0
       for k <= floor((d-1)/2) and > 0 at k = floor((d-1)/2) + 1 -- i.e.
       the rule is minimum-distance decoding and nothing more. If it
       fires, prior art is labelled KNOWN_ANALOGUE_FOUND.
  ALT  matched-redundancy majority vote (repetition of each outcome bit
       over the same number of agents). Pass iff the code rule's largest
       fully-resistant coalition size exceeds the majority rule's at equal
       agent count. (A pass shows the code beats plain redundancy; it
       does not make the mechanism new.)

### HT-5b0b3ebb8d W4 (unwitnessed-but-verified beliefs are fragile)

  R    60 fresh seeds; MH OR >= 1.5, p < 0.01 reproduces.
  ORIG re-analysis stratified by (endpoint-in-disabled-region, visit
       decile). Kill if no stratum has outcome variance (failure fully
       determined by endpoint) OR the stratified MH OR < 1.5 OR p >= 0.01.
  ALT  a shift that removes TRANSITIONS on paths (not states at
       endpoints), so failure is not decided by endpoint location: a
       belief fails iff a transition on its supporting path is removed.
       Pass iff MH OR (lucky vs grounded) >= 1.5, p < 0.01, stratified by
       visit decile AND path length, over 60 seeds, with a null twin that
       removes transitions uniformly at random from the same count.

## Consequences

  SURVIVES     program -> PROMISING (allocation state; predicate PASS on
               committed rows; still NOT a supported conclusion -- that
               needs Pass 10 independent review). Next: Pass 5 lenses
               from the anomalies, Pass 6 transfer.
  ORIG fires,  original-world claim FOSSIL with rows; program stays
  ALT passes   PROBING; the mechanism continues in the ALT world only.
  ALT fails    program -> PARK (two worlds, no surviving signal); the
               rows and anomalies stay navigable.
  ALT NOT_ELIGIBLE twice / controls fail   -> PARK with reason recorded.
