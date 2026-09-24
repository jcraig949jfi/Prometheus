+=====================================================================+
|  CAMPAIGN 6 -- THE ELEVEN DETECTORS, v0.1 (definitions for admission) |
|  Archaeon[m2-49ee5a4d]   2026-09-18   thresholds NOT yet frozen      |
+=====================================================================+

Common contract. Each detector is a pure function of (T0 rows of the
current segment, the run's anchored history it may read, the world
state snapshot, the lineage records) returning
  {outcome: FIRE | QUIET | UNABLE, score: float|null, threshold: float,
   evidence: {...}, subject: {organism_id, lt, eval}}
UNABLE is returned whenever the detector's inputs are not defined for
the subject (no ancestor, no other world, no regime change yet); it is
never silently QUIET. Thresholds are frozen at G6-0 from a calibration
set (C4/C5 lineages: 57 parents, C4-05 walks, C5-02/C5-09 populations)
with Harmonia's chance floor and controls; each detector's frozen
threshold, definition sha256 and code identity are registered in PEW
before the first segment. No detector reads another detector's output
except 10 and 11, which read only the verdict vector.

Distances. fp_dist(a, b) = a fixed weighted L1 over the fingerprint
fields after per-field normalisation by the calibration set's spread
(weights and spreads frozen with the thresholds); struct_dist over the
genotype structural descriptor likewise.

  1  behavioral_novelty      fp_dist(subject, nearest of {ancestors to
                             depth 8, siblings, current population,
                             behaviour library}) -- FIRE when above t1;
                             UNABLE when the library and population are
                             empty (first generation of a run).
  2  lineage_discontinuity   fp_dist(child, parent) relative to the
                             child's struct_dist(child, parent): FIRE when
                             a small structural edit (struct_dist <= s)
                             produces a behavioural jump above t2 (the C4
                             cliff, measured per lineage instead of
                             pooled); UNABLE without a parent.
  3  unexpected_transfer     reward or fingerprint competence on a world
                             the lineage never saw (held-out probe set,
                             one probe per archived generation) rising by
                             >= the band while the home-world reward does
                             not: FIRE; UNABLE if no probe world exists.
  4  structural_reuse        (graph profile) the same connected component
                             (by canonical hash) executed at >= 2 sites,
                             or a SUBGRAPH_COPY whose copy executes: FIRE
                             above t4 executions; (v0 profile) a genome
                             region duplicated and both copies reachable:
                             UNABLE if the profile has no components.
  5  environmental_modification  world-state cells changed by organism
                             actions that persist past the organism's
                             lifetime and are read by another organism
                             later: FIRE when the persisted-and-read count
                             exceeds t5; UNABLE in worlds without
                             persistent state.
  6  niche_divergence        two or more sub-populations whose
                             resources_touched / env_dependencies sets
                             have Jaccard < t6 for >= g6 generations while
                             both persist: FIRE; UNABLE with < 2 resource
                             types or one lineage.
  7  regime_persistence      a lineage whose home-world reward stays
                             within the band across a REGIME_CHANGE event
                             while the population median drops by >= the
                             band: FIRE; UNABLE before the first regime
                             change.
  8  unexplained_gain        reward gain >= the band between parent and
                             child with struct_dist below s8 AND mutation
                             rollback (replay D) reproducing the gain
                             without the recorded edit: FIRE (the gain is
                             not the edit's); UNABLE until replay D has
                             run (this detector is evaluated at
                             escalation, not in-loop).
  9  unexpected_causal_dependence  per-node ablation (E) of a subject
                             finds a dormant-by-lineage node (never
                             executed in ancestors) whose ablation moves
                             the reward by >= the band: FIRE; UNABLE
                             without an ablation set.
  10 detector_disagreement   reads only the verdict vector of 1-9 on one
                             event neighbourhood: FIRE when >= 1 FIRE and
                             >= 2 QUIET among detectors that were ABLE;
                             never UNABLE.
  11 classifier_failure      reads the verdict vector: FIRE when the
                             adjudication classifier (Harmonia lane C)
                             returns none of the named classes, OR when
                             >= 3 detectors return UNABLE on a subject
                             that fired at least one: the observatory
                             could not see; never UNABLE.

Calibration set and controls (G6-0). Positive controls: C4-05 walkers
that exapted (detectors 1, 3), C5-06 recovery children (2), C5-02
rescued lineages (6, 7 across the lateral entry as a regime change),
C4-01 randomize-all children (2 must FIRE, 1 must FIRE), identity
children (all QUIET). Negative controls: C5-09 OLD_v04 populations
(nothing fired in 96 cells by construction of the held-out readings).
Cheat controls: a subject with a fabricated fingerprint of all zeros
must read UNABLE or FIRE on 11, never QUIET everywhere. Chance floors
per detector from shuffled-lineage nulls (Nemesis/Harmonia).

Thresholds: chosen so the negative controls fire at <= 1% per detector
per 1,000 evaluations and each positive control fires; the set is
frozen in DETECTORS_FROZEN.json with sha256 posted at G6-0 and never
moved (the C5 rule).
+=====================================================================+
