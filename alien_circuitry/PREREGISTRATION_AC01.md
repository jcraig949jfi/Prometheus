# AC-01D-v1 preregistration (FROZEN 2026-09-12 by operator ruling after a6e3e80)

Status: FROZEN. Representation fitting is authorised in the committed family order below. The corpus, masks, input
policy, baselines and denominators are unchanged from a6e3e80 (hashes in `results/ac01d/CORPUS_MANIFEST.json` and
`results/ac01d/FREEZE.json`). This revision changes only the success criteria, the split weighting, the storage
condition, the path-quality metric, the family scoring eligibility, and the scope statement, exactly as ruled.

## 0. Scope statement

AC-01D-v1 applies to the full transformation monoid T_7 with the 63 restricted-growth rank-2 targets and corpus
states of rank >= 3. A positive result is a statement about THIS universe and THIS target-rank regime. It does not
license the sentence "distance geometry of transformation monoids is compressible". Target-rank transfer (rank 3,
rank 4 targets) and n = 8 are the obvious replications if v1 passes; they are separate experiments with their own
preregistration.

## 1. Question

After exact reachability is supplied by the known kernel invariant, can a compact representation recover enough
shortest-path structure to reduce navigation cost toward the oracle, on unseen targets and states, with convincing
uncertainty bounds and a meaningful compression/navigation trade-off?

Two lanes: AC-01R (sensitivity control: recover the withheld kernel relation from raw digits) and AC-01D (primary:
distance geometry on the 11,138,190 reachable pairs).

## 2. Frozen corpus objects (unchanged; `data/AC01_T7_corpus.npz`, regenerable by `python -m alien_circuitry.ac01d.corpus`)

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
```

Evaluation sets (AC-01D reachable rows / AC-01R rows): FIT 4,289,843 / 19,703,569; HELD_PAIRS 1,072,543 /
4,928,831; VAL 1,780,521 / 8,184,700; HELD_STATES 1,793,853 / 8,227,400; HELD_TARGETS 1,321,710 / 6,404,424;
HELD_BOTH 441,595 / 2,139,124. FIT is the only set a representation may be fitted on; VAL is the only set that may
steer hyperparameters; the HELD sets are touched once per family.

## 3. Input feature policy (unchanged)

Allowed: raw state digits F[s], raw target digits, action id, rank, count vector, block-size multiset, no-op flag,
target equality. Discovery of the partition from raw digits is allowed. Prohibited as input, engineered or hashed:
pairwise image-equality indicators, kernel blocks/ids, canonical forms or hashes of the partition, any lookup into
D. `kernel_audit` is read only by the kernel-aware baselines and by post-hoc AC-01R comparison. Every family's data
loader is audited against this list before fitting.

## 4. Baselines (unchanged, `ac01d/baselines.py`; HELD_STATES shown, other sets in `results/ac01d/baselines.json`)

```
                        transitions   states   path   excess   HC_D(transitions) [95% CI]
oracle (D descent)          38.6       17.2    17.2    0.0      1
KA-DFS (rank order)         87.5       40.5    39.5   22.3      0            <- C_K for cost units
KA-GBFS (best-first)       132.7       60.8    20.8    3.7     -0.92 [-1.30, -0.64]   <- path-quality reference
KA+FM (DFS)                308.4      151.7   117.2  100.0     -4.51 [-5.37, -3.86]
KA+FM-GBFS              14,558.7    6,636.9   27.0    9.8    -295.8 [-343.5, -257.7]
KA+LA3                   1,518.3      657.1   37.3   20.1     -29.2 [-31.0, -27.9]
```

All solve 1.000 with zero failures. Residual headroom per problem: 87.5 - 38.6 = 48.9 transitions on HELD_STATES
(92.8 - 38.8 = 54.0 on HELD_TARGETS; 88.7 - 38.3 = 50.4 on HELD_BOTH).

## 5. Metrics (revised)

HC_D = 1 - (C_M - C_O) / (C_K - C_O), C_K = KA-DFS, ratio of sums over an evaluation set, 1,000-resample bootstrap
95% interval over problems; transitions examined primary, states expanded secondary. Decision-time work of the
representation is included in C_M (counted as transitions-equivalent where honestly countable, wall-clock beside).

Failure rule (unchanged, sacrosanct): solve rate 1.000 on every scored held set; failures counted separately; a
method with any failure has no HC_D on that set.

Path quality is CO-PRIMARY. Every method is placed on the two-dimensional frontier (transitions examined, excess
path length) per set, and dominance is judged against the two kernel-aware references:
  DOMINATES KA-DFS      fewer transitions than KA-DFS AND excess path lower than KA-DFS by >= 5 steps
  APPROACHES KA-GBFS    excess path within +2 of KA-GBFS while transitions <= KA-DFS
  COST ONLY             HC_D > 0 with excess path not better than KA-DFS
  PATH ONLY             excess path better than KA-DFS with HC_D <= 0
A representation is compelling if it dominates KA-DFS or approaches KA-GBFS without paying KA-GBFS's cost. No
scalar collapses the two axes.

Storage: CR = 1,060,696 / serialized representation bytes (the lzma sparse exact distance chart; action-table
denominator 485,612 reported beside). Report the best HC_D attainable at the landmarks CR >= 1.5, 2, 4, 8 and the
full (CR, HC_D) frontier. A representation must use MATERIALLY LESS storage than the frozen exact representation
(CR >= 1.5) for any compression claim; CR >= 4 is not a gate.

Distance channel (secondary, informational): exact match, within-1, MAE, Spearman on each scored set, against the
permitted feature model (0.24 / 0.61 on HELD_STATES, 0.17 / 0.49 on HELD_TARGETS).

AC-01R: the representation-induced reachability score, PR-AUC on the AC-01R rows of HELD_BOTH (prevalence 0.2154),
with the permitted-feature reference computed on that same population at first use; post hoc adjusted mutual
information between the representation's state classes and kernel classes.

## 6. Success bands (revised; the critical sets are HELD_TARGETS and HELD_BOTH)

```
HC_D <= 0.20                                   no useful compression
0.20 < HC_D < 0.40                             weak but real structure
HC_D >= 0.40 on HELD_TARGETS and HELD_BOTH     meaningful structural compression   (lower bootstrap bound > 0.20)
HC_D >= 0.60                                   strong result
HC_D >= 0.40 and CR >= 4                       strong compact-circuit result
strong HELD_STATES, weak HELD_TARGETS          target-specific map compression, not general geometry
AC-01R passes, AC-01D fails                    instrument rediscovers the known invariant; no useful distance structure
quotient / signature family wins               useful compression exists; no need for exotic circuitry
only tensor / learned / evolved wins           genuinely interesting representation result
```

Verdict matrix by split: passes only HELD_STATES -> within-target compression; passes HELD_TARGETS -> cross-target
structural compression; passes HELD_BOTH -> strongest evidence. Family kill: HC_D <= 0.20 on HELD_TARGETS and
HELD_BOTH after the family's budget, or bootstrap interval containing 0 on both. Global negative result if every
eligible family is killed: "the T_7 rank-2 distance geometry admits no compact navigational representation under
these six families", preserved as a result.

## 7. Families, scoring eligibility, order, budgets (order unchanged)

A family is scorable on a held set only if it can be applied to that set's states and targets without touching their
D entries. Quotient, signature and plain matrix factorisation have no input encoding for unseen states or targets:
they are scored as compression of the exact table (CR at HC_D = 1 on FIT, generalisation on HELD_PAIRS via row
sharing where defined) and cannot earn the cross-target verdicts. Only digit-encoded families can.

```
order  family                          input                                   scorable sets                  budget
1      C3 exact behavioural quotient   FIT D rows (train targets)              FIT compression, HELD_PAIRS     1 CPU-h
2      C4 consequence signatures       successor-D / shortest-path signatures  FIT compression, HELD_PAIRS     1 CPU-h
3      C1 matrix low-rank completion   masked state x target chart             HELD_PAIRS                      2 CPU-h
4      C2 tensor (CP / Tucker / TT)    7 digit modes x target digits, masked   ALL four held sets              4 CPU-h
5      C5 learned embedding            raw digits (state, target, action)      ALL four held sets              6 CPU-h
6      C6 evolved DSL                  operators over raw digits and counts    ALL four held sets              6 CPU-h
```

Every family must expose: serialized bytes; a predictor of D for any (state, target) it is eligible for; a
navigation policy = KA pruning + best-first by predicted D AND DFS ordering by predicted D (both evaluated); a
reachability score for AC-01R where applicable. Evaluation harness: `ac01d/evaluate.py` (frozen with this file).
Tensor Train is one of three C2 decompositions with no privileged status. A family stops early if its VAL HC_D is
< 0 after half its budget. Total 20 CPU-h plus evaluation; hard memory ceiling 1.2 GB RSS per process; one process
at a time on this host. Freeze sample size: 300 problems per held set (bootstrap 1,000), distance metrics on
300,000 rows per set.

## 8. Stopping rules (unchanged)

Stop and report if: any claimed solution fails mechanical verification; any solve rate on reachable problems drops
below 1.000; any corpus hash changes; a family's loader reads prohibited features or the D chart; a representation's
bytes exceed the lzma denominator while claiming compactness; the AC-01R control fails for every eligible family
(instrument insensitive: no AC-01D claim may then be made); or all families are killed (negative result, preserved).

## 9. Hashes

Corpus arrays: section 2. COO distance chart c9c30211…; COO action table efa9afef…. `results/ac01d/FREEZE.json`
records sha256 of this file, of `ac01d/corpus.py`, `ac01d/baselines.py`, `ac01d/evaluate.py`,
`gate2/observation_monoid.py`, `universe/monoid.py`, `universe/uc1_seed.py` at the freeze commit.
