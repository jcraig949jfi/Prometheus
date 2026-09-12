# AC-01 preregistration package (AC-01R + AC-01D), 2026-09-12

Status: **for freeze review. Nothing has been fitted.** Corpus, masks, feature policy, baselines and denominators are
built, measured and hashed (`results/ac01d/CORPUS_MANIFEST.json`, `results/ac01d/baselines.json`,
`results/ac01d/ac01r_leakage_report.json`; code in `ac01d/`). The numerical thresholds below are proposals with their
attainable ranges and the measured baseline values beside them. No representation family has been run.

## 1. Universe and lanes

Universe: full T_7 = maps [7] -> [7] under left action of {cycle, swap01, collapse01} (`universe/monoid.py`,
generators `uc1_seed.pch_generators`). 823,543 states; 2,470,629 legal actions (358,061 no-ops); targets = the 63
restricted-growth maps of rank 2; corpus states = rank >= 3 (820,890). Exact D by reverse BFS; reachability equals
kernel refinement (theorem, verified on every pair).

- AC-01R (sensitivity control): predict reachability R[f, t] on all 51,716,070 corpus pairs (positive fraction
  0.2154) without being handed the kernel relation. Known answer withheld: ker f refines ker t.
- AC-01D (primary): on the 11,138,190 reachable pairs, learn a compact representation of D(f, t) and use it to
  navigate with reachability supplied. The reachability question is closed by ruling and is not scored here.

## 2. Frozen corpus objects (data/AC01_T7_corpus.npz, regenerable by `python -m alien_circuitry.ac01d.corpus`)

```
array          shape / dtype          sha256 (prefix)   content
F              823,543 x 7 int8       871e6164          raw state digits (the map)
D              823,543 x 63 int16     b8ad6f59          exact distance, -1 = unreachable
succ           823,543 x 3 int32      1e0063dc          successor of each generator (self for no-ops)
targets        63 int64               d59fc2ce          target state ids
state_role     823,543 int8           0fead724          0 train / 1 val / 2 test  (494,229 / 164,243 / 165,071)
target_role    63 int8                f458c313          1 = held-out target (13 of 63)
pair_role      823,543 x 63 int8      c3d1cf03          1 = held pair (20%) within train x train
kernel_audit   823,543 int32          b513f5dd          21 pairwise-collision bits; AUDIT AND KA BASELINE ONLY
rank, C        per state              (derived)         rank and count vector (permitted features)
```

Derived per (state, target, action): successor D = D[succ[s, a], t]; shortest-path membership = successor D + 1 == D[s, t];
every reachable row has at least one shortest-path action (fraction 1.000; mean 1.23 per row).
Distance histogram of the reachable pairs: D 3..24, mode 17 (manifest). Held-out targets (universe-independent hash
order): 0001000 0001110 0100100 0001101 0000110 0101110 0100110 0111010 0001111 0101111 0011010 0000011 0101001.

Masks (deterministic): state role = sha256("AC01|T7|state|<digits>"); target role = sha256("AC01|target|<digits>")
order; pair role = splitmix64(state*64 + target) >= 80%. Evaluation sets (AC-01D rows / AC-01R rows):

```
FIT           train states x train targets, pair role fit     4,289,843 / 19,703,569
HELD_PAIRS    train x train, pair role held                    1,072,543 /  4,928,831
VAL           val states x train targets                       1,780,521 /  8,184,700
HELD_STATES   test states x train targets                      1,793,853 /  8,227,400
HELD_TARGETS  train states x held-out targets                  1,321,710 /  6,404,424
HELD_BOTH     test states x held-out targets                     441,595 /  2,139,124
```

FIT is the only set a representation may be fitted on; VAL is the only set that may steer hyperparameters; the four
HELD sets are frozen and touched once per family.

## 3. Input feature policy (frozen)

Allowed as representation input: the raw state digits F[s] (7 categorical symbols), the raw target digits, the
action id, and the permitted engineered features (rank, count vector, block-size multiset, no-op flag, target
equality). A representation may DISCOVER pairwise structure from the raw digits; that is the point of AC-01R.
Prohibited as input, engineered or hashed: pairwise image-equality indicators, kernel blocks, kernel ids, any
canonical form or hash of the partition, any lookup into D. `kernel_audit` is read only by the KA baselines and by
the post-hoc AC-01R comparison. Every family's data loader is audited against this list before fitting.

## 4. Baselines (implemented in `ac01d/baselines.py`; all prune kernel-incompatible successors; 100 problems per
held set with D >= 5; DFS/GBFS budget 40,000 expansions; all solved 100%, zero failures)

```
                        transitions   states   path   excess   HC_D(transitions) [95% CI]        (HELD_STATES; other sets in JSON)
oracle (D descent)          38.6       17.2    17.2    0.0      1
KA  (DFS, rank order)       87.5       40.5    39.5   22.3      0                                denominator for cost units
KA-GBFS (best-first)       132.7       60.8    20.8    3.7     -0.92 [-1.30, -0.64]              denominator for path units
KA+FM (DFS by feature-model D)   308.4   151.7  117.2  100.0   -4.51 [-5.37, -3.86]
KA+FM-GBFS                14,558.7   6,636.9   27.0    9.8   -295.8 [-343.5, -257.7]
KA+LA3 (exact lookahead 3)  1,518.3    657.1   37.3   20.1    -29.2 [-31.0, -27.9]
```

Feature model (table regressor on FIT pairs, 8,830 cells; permitted features only): R^2 0.62 / exact 0.24 /
within-1 0.61 on HELD_PAIRS and HELD_STATES; R^2 0.45 / exact 0.17 / within-1 0.49 on HELD_TARGETS and HELD_BOTH.
It does not transfer across targets and it is harmful as a search guide. Bounded lookahead cannot prove traps and
only adds cost. The uninformed exact searches from the survivor gate remain on record (bidirectional BFS 1,111
transitions, forward BFS 18,328) but are no longer a success denominator.

## 5. Cost units, HC_D, failure rule

Primary unit: transitions examined (legal inferences evaluated), C_K = KA-DFS. Secondary: states expanded (same
denominator); path length and excess path length with C_K = KA-GBFS; wall-clock reported, never combined.

HC_D = 1 - (C_M - C_O) / (C_K - C_O), ratio of sums over the problems of an evaluation set, with a 1,000-resample
bootstrap 95% interval over problems. HC_D = 0 is the kernel-aware baseline, 1 the oracle, negative is worse than
knowing only the invariant. Per-method cost includes every operation of the representation at decision time
(counted as transitions-equivalent where honestly countable, else reported as wall-clock beside).

Failure rule: on reachable problems a method must reach the exact target (verified mechanically by the engine),
with solve rate 1.000 on every held set, matching KA. Failures are reported as counts and are never averaged into
cost. A method with any failure has no HC_D.

## 6. Storage denominator (M1)

```
AC-01D distance chart, sparse COO (state int32, target uint8, D uint8):   raw 66,829,140 B   zlib 3,307,576   lzma 1,060,696
AC-01D action table (successor D x3 int8 + shortest-path bits):           raw 44,552,760 B   zlib 2,018,624   lzma   485,612
```

CR = 1,060,696 / serialized representation bytes (primary); the action-table denominator is reported beside for
representations that encode ΔD directly. A representation larger than 1,060,696 bytes is not compact whatever its
HC_D; a representation is reported on the (CR, HC_D) frontier, never as one number.

## 7. Proposed thresholds (attainable range and measured references stated)

AC-01D primary success, per held set (HELD_STATES, HELD_TARGETS, HELD_BOTH; HELD_PAIRS as the easiest):
  HC_D(transitions) >= 0.50 with bootstrap lower bound > 0.30, zero failures, and excess path <= 3.7 (KA-GBFS) or the
  method reported on the path unit separately. Attainable range (-inf, 1]; references: KA 0, KA-GBFS -0.92, FM -4.5.
  Compression claim requires CR >= 4 at that HC_D (representation <= 265 KB); the frontier is reported regardless.
AC-01D kill for a family: HC_D(transitions) <= 0.20 on every held set, or bootstrap interval containing 0 on
  HELD_STATES, after the family's compute budget.
AC-01D distance-channel secondary: exact-match >= 0.50 and within-1 >= 0.85 on HELD_STATES (FM 0.24 / 0.61);
  exact-match >= 0.40 on HELD_TARGETS (FM 0.17). Not a success criterion by itself: navigation is.
AC-01D global negative result: every family killed -> "T_7 distance geometry admits no compact navigational
  representation at CR >= 4 under these families", preserved as a result.

AC-01R sensitivity pass: reachability predictor induced by the representation reaches PR-AUC >= 0.95 on the AC-01R
  rows of HELD_BOTH (prevalence 0.2154; permitted-feature reference to be computed on this population at freeze;
  the collapse-action reference is PR-AUC 0.685 [0.684, 0.686], normalised improvement 0.48, balanced accuracy
  0.74, nMI 0.31, 69% of trap entropy remaining). Post hoc: adjusted mutual information between the
  representation's state classes and kernel classes >= 0.90 means the kernel coordinate was recovered.
  AC-01R fail with AC-01D pass, or the reverse, are both informative and both preserved.

Sample sizes at freeze: 300 problems per held set (bootstrap 1,000), which puts the HC_D interval half-width near
0.15 (measured 0.3 at 100 problems); distance-channel metrics on 300,000 rows per set (SE < 0.002).

## 8. Representation families and ordering (none run)

```
order  family                          input                                       output                       budget
1      C3 exact behavioural quotient   D rows over train targets (FIT states)      state classes + class D table  1 CPU-h
2      C4 consequence signatures       successor-D / shortest-path signatures      class table                   1 CPU-h
3      C1 matrix low-rank completion   masked state x target chart                 factors (rank sweep)          2 CPU-h
4      C2 tensor (CP / Tucker / TT)    7 digit modes x target mode, masked         cores (rank sweep)            4 CPU-h
5      C5 learned embedding            raw digits (state, target, action)          <= 265 KB parameters          6 CPU-h
6      C6 evolved DSL                  operators over raw digits and counts        program + tables              6 CPU-h
```

Every family must expose: (a) serialized bytes, (b) a predictor of D for any (state, target), (c) a navigation policy
= KA pruning + best-first and DFS ordering by predicted D, evaluated by `ac01d/baselines.py`'s harness. Tensor Train
has no privileged status; it is one of three C2 decompositions. Families run in the order above; a family is stopped
early if its VAL HC_D is < 0 after half its budget. Total budget 20 CPU-h plus evaluation; hard memory ceiling
1.2 GB RSS per process (this host runs other seats; the survivor gate was killed three times above ~650 MB plus
transients). n = 8 out-of-distribution (16.7M states, 2.1 GB distance chart) is NOT feasible on this host as
configured and is not required for the first verdict.

## 9. Stopping rules

Stop and report if: any claimed solution fails mechanical verification; any method's solve rate on reachable problems
drops below 1.000; any corpus hash changes; a family's data loader is found to read prohibited features or the D
chart; a representation's bytes exceed the lzma denominator while claiming compactness; the AC-01R control fails
for every family (instrument insensitive: no AC-01D claim may then be made); or all families are killed (negative
result, preserved).

## 10. Hashes

Corpus arrays: section 2. COO distance chart c9c30211…; COO action table efa9afef…. Frozen code: `ac01d/corpus.py`,
`ac01d/baselines.py`, `gate2/observation_monoid.py`, `universe/monoid.py`, `universe/uc1_seed.py` as committed in
this package's commit (see `git log`); the survivor gate and design-search results are untouched.
