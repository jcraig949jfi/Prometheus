# Nursery crucibles C and B: results (2026-09-14)

Governing definitions: `nursery/CRUCIBLES.md` @ 86a429e. Preregistration: `PREREG_C_B.md` @ d3b9533; B control
addendum `PREREG_B_ADDENDUM.md` @ 8851f05. C result committed at 8157e9e before B was run.

## CRUCIBLE-C: C-PASS (NUR-004; second ecology for NUR-001)

Question: is the Diomedes h1 pooled ceiling partly a pooling artefact, and does quotienting by invariant pair change a
consequential decision beyond a null?

- Source: frozen Diomedes h1 population, rebuilt by the frozen builders from the identity-proved harvest cache (digest
  1b4abb1a reproduced). 22 qualifying invariant pairs; about 15,100 held states per seed; 5 seeds; 60/40 split by state
  within pair. Label: candidate breaks the relation (exact oracle).
- Decision operationalised as exact cost-to-first-break: test the up-to-100 candidates in predicted order, count until
  the first breaking candidate.

```
cost to first break (mean over 5 seeds)
oracle 1.00 | canonical pair 2.22 | break-rate only 2.55 | pooled 2.69 | matched-N pooled 2.76 | random 3.16
pair x relation (SECONDARY, not in verdict) 1.75
reduction canonical vs pooled 0.47 (per seed 0.34-0.62, bootstrap SE ~0.04)
random-class permutation null: 200 per seed, observed above every permutation on every seed (p = 0.005 each)
HC = 0.28 (per seed 0.22-0.34); matched-N HC = -0.04; AUC pooled 0.571 vs canonical 0.660
```

- Boring explanations checked: sample size (matched-N pooled is worse than pooled, so no); pair-ID memorisation (the class
  selects which logistic scores a candidate; features are the frozen relational coordinates, no identifier column);
  capacity mismatch (same model family and settings in both arms); multiple testing (one class definition; the stronger
  pair x relation result is reported and excluded); decision-time irrelevance (the class key is part of the state before
  any label, and the metric is the search decision itself).
- Failure geometry: the pooled logistic is worse than the one-feature break-rate baseline (2.69 vs 2.55), so pooling over
  sign-disagreeing classes does active harm; the quotient recovers only 28% of the pooled-to-oracle gap.
- Instrument history preserved: run 1 crashed on a seed overflow; runs 2-4 were killed by host memory (the frozen state
  builder peaks near 8.6 GB); repair = compact float32 states after the builder, one seed per process, checkpoints. No
  scientific change.

## CRUCIBLE-B: B-KILL (NUR-002)

Question: do macros mined from repeated oracle shortest-path subsequences reduce kernel-aware search more than equally
privileged arbitrary macros, under unchanged accounting?

- Mining (FIT only, 2,000 oracle paths, mean length 16.7): six length-2 macros (1,0) (0,2) (0,1) (0,0) (2,1) (2,0) with
  counts 9044 / 5869 / 5310 / 4996 / 4453 / 1822 (cycle=0, swap01=1, collapse01=2).
- Run 1 instrument failure (preserved, 9b0a963): the preregistered "6 random length-matched macros excluding the mined
  set" is infeasible (only 3 non-mined length-2 sequences exist); the rejection sampler hung for 11 hours. No held result
  was written or seen.
- Control repaired before any held result (8851f05): the exact distribution over all C(9,6) = 84 six-sets of length-2
  macros; the mined set is one of them.

```
HC_D on transitions vs frozen KA-DFS         mined     mean of other 83   CI half-width   mined rank of 84   verdict
DFS   HELD_TARGETS                           -19.46    -16.10             1.34            84 (worst)
DFS   HELD_BOTH                              -18.50    -15.37             1.29            84 (worst)          B-KILL
GBFS  HELD_TARGETS                           -12.25    -12.81             1.10            39
GBFS  HELD_BOTH                              -11.67    -12.63             1.04            39                  B-KILL
all 84 sets, any held set, either searcher: 0 with positive HC_D; best GBFS set -2.96..-3.13; best DFS set -11.57..-12.55
mined, HELD_BOTH: 1,028 transitions (DFS, excess path 63.2) and 681 (GBFS, excess 18.0); zero failures everywhere
```

### Harness defect found by the no-macros sanity check (does not change the verdict)

`MacroWorld` with no macros should reproduce the frozen kernel-aware references; it does not (HELD_BOTH DFS 196.3 vs
88.6 transitions, GBFS 189.1 vs 122.2; similar on the other sets, `crucible_b2_no_macros_sanity.json`). Root cause,
confirmed exactly (`crucible_b2_harness_rootcause.json`): the runner counts duplicate successors when two generators
reach the same state (196 -> 170) and breaks rank ties by generator index instead of by position in the sorted
successor list (170 -> 88.6); with both corrected, costs match the frozen references identically on every problem. The
preregistration itself said "rank distance then action order", so the runner followed the frozen text; the frozen text
disagreed with how the denominator was built.

Consequences:

1. The absolute HC_D values above mix a harness difference (about -2 with no macros) with the macro effect; they are not
   reported as the size of a macro effect.
2. The verdict stands. Its decisive KILL clause compares the mined set with the other 83 inside one harness, where the
   mined set is worst of 84 (DFS) and mid-pack (GBFS). Inside the same harness every one of the 84 sets costs more than
   no macros (HELD_BOTH: no macros 196 DFS / 189 GBFS; mined 1,028 / 681; best GBFS set about 247).
3. No rerun under a different ordering was performed: that would change the policy after seeing held results.
4. New caveat with wider reach: kernel-aware search cost roughly doubles under an arbitrary change of tie-break order.
   HC_D denominators throughout AC-01D carry this sensitivity. Oracle-level representations (the orbit table, HC_D
   ~0.998) are insensitive because their cost matches the oracle whatever the denominator; mid-range figures (C5 0.91,
   CP 0.55, C6 0.54) carry an unmeasured denominator sensitivity.

## Portfolio consequence

- NUR-001 (quotient) gained evidence: a second positive ecology with a different failure geometry (noisy statistical
  selection, HC 0.28) beside T_7 (exact combinatorial, HC 0.998), with the tensor-QD inert case still standing.
- NUR-002 (compiled trajectory, as move-set augmentation) lost evidence: in T_7, adding the most frequent oracle
  subsequences as extra actions is no better than adding any other six length-2 sequences, and every such augmentation
  increases search.
- Not orthogonal in a useful way yet: the move-set lever has no positive instance to compose with, so CRUCIBLE-E is not
  warranted.
