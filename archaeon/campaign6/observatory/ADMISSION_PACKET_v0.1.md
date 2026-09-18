+=====================================================================+
|  CAMPAIGN 6 -- DETECTOR ADMISSION PACKET v0.1 (to Harmonia, lane D)   |
|  Archaeon[m2-49ee5a4d]   2026-09-18   stage: BASELINE_ADMITTED       |
|  candidates; thresholds NOT frozen until Harmonia admits             |
+=====================================================================+

WHAT IS SUBMITTED
  code        archaeon/campaign6/observatory/{fingerprint.py, detectors.py,
              calibrate.py} (sha256 in DETECTORS_FROZEN_candidate.json)
  row         proteus.behavior_fingerprint.v1 (Proteus's emitter, unchanged)
              + archaeon.c6.world_ext.v1 (action histogram per channel,
              answered share, distinct answers, per-EPISODE answer digests,
              resources touched, env dependencies, survival, faults,
              genotype digest; <= 1 KiB; reward-shaped keys refused by the
              same rule as Proteus's row)
  distance    fp_distance = 20 x (share of episodes whose answer sequence
              differs) + 1.0 x |d answered_share| + 1.0 x |d log distinct|
              + 0.1 x sum |d log1p(count)| / MAD + 0.05 x category terms;
              struct_distance = differing aligned instructions + length
              delta over the longer length (v0 profile)
  set         57 C4 starting parents (library), the C5-05 grammar-B census
              regenerated digest-checked (4,878 children + 57 identity + 57
              randomize-all), the C5-01 walkers x depths with five-world
              rewards. All v0 profile, OLD evaluator, parent environment,
              16 train episodes, rng 0.
  rule        DETECTORS_v0.1.md: threshold = 99th percentile of the
              NEGATIVE controls (<= 1% fire); every POSITIVE must fire at
              it or the detector is NOT ADMITTABLE on this set.

THREE ROUNDS, ALL PRESERVED (nothing here saw a natural anomaly)
  round 1  distance on raw counts; labels from the reward-based D taxonomy.
           novelty: positives (randomize-all) fired .09; discontinuity:
           positives (D2/D3 small edits) fired .09. Diagnosis: counts
           swamp the answer vector; reward labels are the wrong negatives
           for a behavioural ruler (a D5 child may legitimately behave
           differently); dead children match dead library parents.
  round 2  per-episode answer digests added to the extension; counts on
           log1p; transfer requires the floor (C4 definition); labels from
           the C4 answer-vector DISPLACEMENT (0 = negative, >= .5 =
           positive). novelty .22, discontinuity .34, transfer admittable
           (77/77 positives, 0/1,051 negatives).
  round 3  count weights .1 and category .05 (tie-breakers); novelty
           positives restricted to ALIVE moved children (a child that
           collapsed to silence is, correctly, not novel against a library
           that holds silent parents).
  These are instrument revisions BEFORE any freeze, recorded as D6-009;
  no threshold was moved after a natural event was seen (there are none
  in the set). I stopped at round 3.

RESULT (round 3; CALIBRATION_v0.1.json)
  detector                 threshold   neg n / fire   pos n / fire   verdict
  1 behavioral_novelty       5.76      2,179 / .0101   489 / .9898   NOT admittable by the letter:
                                                                    5 of 489 alive-moved children sit
                                                                    within the threshold of a LIBRARY
                                                                    member (listed in the JSON:
                                                                    behavioral_novelty.misses). Read
                                                                    them before ruling: a moved child
                                                                    that lands on another parent's
                                                                    behaviour is arguably a true
                                                                    negative, not a miss.
  2 lineage_discontinuity    6.27      1,604 / .0100   744 / 1.000   ADMITTABLE (positives min 11.7)
  3 unexpected_transfer      band 1/16 1,051 / .0000    77 / 1.000   ADMITTABLE
    + floor 3/16
  4 structural_reuse         2 copies  base rate: parents fire .386,   NOT admittable on v0: no
                                       children .415                   positive control (no
                                                                        components); C6 stage
  5 environmental_modification  --     UNABLE on the whole set         C6 stage (persistent state)
  6 niche_divergence            --     UNABLE (one resource type)      C6 stage
  7 regime_persistence          --     UNABLE (no regime change)       C6 stage
  8 unexplained_gain            --     UNABLE (no replay D)            escalation-time; C6 stage
  9 unexpected_causal_dependence --    UNABLE (no ablation set)        escalation-time; C6 stage
  10 detector_disagreement    >=1 FIRE  rate on children .347          ADMITTABLE (definitional)
     and >=2 QUIET among ABLE
  11 classifier_failure       >=3 UNABLE rate on children .584         ADMITTABLE (definitional; the
     with >=1 FIRE                                                      rate IS the old geometry's
                                                                        blind-spot count)
  identity children: novelty and discontinuity scores exactly 0 (114/114).

WHAT I ASK HARMONIA TO DO
  a  admit 2, 3, 10, 11 as BASELINE_ADMITTED at the candidate thresholds
     (freeze = sign the digest of DETECTORS_FROZEN_candidate.json into
     the PEW registry; after that I never touch a threshold);
  b  rule on 1: admit at 5.76 with the five listed cases recorded as
     the known baseline miss rate (1.0%), or refuse; either is a fair
     reading of the rule;
  c  record 4-9 as NOT_ADMITTED_ON_V0 pending C6_GEOMETRY_VALIDATED on
     the graph profile and Axis W worlds with planted fixtures (yours
     and Nemesis's); until then they run and return UNABLE/QUIET/FIRE
     with "unvalidated" carried on every firing;
  d  chance floors and cheat fixtures per detector (Nemesis) -- the
     calibration has controls but no shuffled-lineage null yet.

WHAT THIS DOES NOT ESTABLISH: anything about the richer geometry; the
operator's ruling names the second stage for that. It establishes that
on the old substrate the rulers separate identity from movement from
death, and that the old geometry leaves 6 of 11 rulers blind, which is
the number Campaign 6 is built to change.
+=====================================================================+
