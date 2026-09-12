# AC-01 Phase A/B receipt (2026-09-12)

Headline: directed bounded rewriting is an honest ruler for distances, shortest-path membership and search cost,
and its transition generator, distance chart and baselines are verified. It is NOT yet an honest ruler for the
phenomenon AC-01 was chartered to measure. Traps exist, but at the default target set they are dominated by a
target artifact, the calibration universe has no genuine traps at all, and where genuine traps exist their damage
becomes visible within two to five steps. This is a STOP-CONDITION report: no metric was changed, no universe was
adopted after seeing a result, and no compression method exists in this tree. A decision is required (section
"Decision required") before the freeze order can continue past step 4.

## Provenance

- Branch `alien-circuitry/phase-ab-2026-09-12`, worktree `F:/Prometheus-worktrees/alien-circuitry-phase-ab`,
  created from verified `origin/main` = `890c4d452b635c2f90edb50516c1ad4ea9ee07bf` (fetched 2026-09-12).
- Commit 1 `8983387253b953cfe19c217b40559036f28ce83e`: package, tests, controls, docs, evidence.
- Commit 2 (this receipt + results): see `git log`.
- Migrated scratchpad code: `evidence/instrument_failure/PROVENANCE.md` (7 files, sha256 each). The package in
  `universe/` is a re-implementation (vectorised, reverse-BFS distances); its L=8/L=9 counts reproduce the probe
  files exactly (state counts, candidate counts, EASY/MEDIUM/HARD, max D).
- Nothing else was imported. The retired Vivarium branch was not touched.
- Environment: Python 3.12.10, numpy 2.2.6, Windows 11. Tests: `python -m pytest alien_circuitry/tests -q` -> 12 passed.

## Universe

Exact action semantics are in `universe/directed_rewriting.py` (module docstring). Summary:

- State: word over {x, X, y, Y}, 0 <= len <= L. X = inverse(x), Y = inverse(y). Index is a bijection onto range(NS).
- Action = (rule, position). Rule lhs -> rhs is legal at p iff w[p:p+|lhs|] == lhs and |w| - |lhs| + |rhs| <= L.
- cancel: aA -> '' (4 rules), irreversible; NO introduce rule exists.
- relator: each direction of each relation is a separately named rule.
- U-A1 ABELIAN: xy<->yx, xY<->Yx, Xy<->yX, XY<->YX (8 relator rules; all four variants are primitive because
  conjugation is not derivable without introduce). 12 rule types.
- U-A2 BRAID_B3: xyx<->yxy, XYX<->YXY (4 relator rules). 8 rule types.
- U-A3 CANDIDATE (diagnostic only, not adopted) BRAID_B3_ONEWAY: xyx->yxy, XYX->YXY one way. 6 rule types.
- Bounded operational reachability is a strict sub-relation of group equality and is the object under study.
  Two syntactic facts follow: length never increases (so len(t) <= len(s) and same parity are necessary for
  reachability), and relator moves are reversible, so ONLY cancel actions can be traps (measured: relator trap
  count 0 in U-A1 and U-A2 at every L).

Scale (nominal edges = legal actions; distinct = deduplicated successors; times on one core):

```
universe   L   states     nominal edges  distinct edges  enumerate  distances  full run
BRAID_B3   8     87,381        176,584        145,636      0.09 s     0.01 s     2.5 s
BRAID_B3   9    349,525        815,560        669,924      0.48 s     0.05 s     9.6 s
BRAID_B3  10  1,398,101      3,699,144      3,029,220      2.54 s     0.31 s    43.0 s
ABELIAN    8     87,381        436,908        405,960      0.20 s     0.03 s     3.8 s
ABELIAN    9    349,525      2,009,772      1,864,136      1.00 s     0.15 s    13.9 s
ABELIAN   10  1,398,101      9,087,660      8,417,736      5.24 s     0.99 s    67.4 s
```

L=11 (5.6M states) is tractable in the same code; L=12 (22M) would need the M chart chunked to disk.

## Difficulty (candidate problem = start word of length >= 3, target in the 21 words of length <= 2, 0 < D)

```
                     candidates   EASY(3-4)  MEDIUM(5-6)  HARD(>=7)  max D
BRAID_B3  L=9           53,068      43,828       7,148         84      7
BRAID_B3  L=10         309,960     198,356     105,056      4,540     10
ABELIAN   L=9          135,144      66,744      60,192      6,072     10
ABELIAN   L=10         974,808     221,272     591,424    159,976     13
```

Complete distance histograms (BRAID_B3 L=10): D=1 188 | 2 1,820 | 3 17,872 | 4 180,484 | 5 81,344 | 6 23,712 |
7 4,052 | 8 468 | 9 16 | 10 4. (ABELIAN L=10): 1 188 | 2 1,948 | 3 19,580 | 4 201,692 | 5 337,368 | 6 254,056 |
7 108,888 | 8 35,856 | 9 10,656 | 10 3,504 | 11 808 | 12 224 | 13 40. Full histograms for every L are in `results/`.

Branching (distinct successors, all states / states live for some target): BRAID_B3 L=10 2.17 / 2.89, nominal
2.65 / 3.57, fixpoints 57,641; ABELIAN L=10 6.02 / 6.33, nominal 6.50 / 6.90, fixpoints 41. Effective branching
histogram BRAID_B3 L=10: 0:57,641 1:312,228 2:531,432 3:360,208 4:112,768 5:20,800 6:2,752 7:256 8:16.

Braid L=10 answers the section-5 question: 4,540 HARD problems without touching the topology. It is not thin.

## Consequential topology (the part that fails)

Trap = (s, a, t) with D[s,t] >= 0 and D[a(s),t] = UNREACH. Visible = successor has no legal action, or successor
length is below the target length. Latent = neither.

```
                    live (s,a,t)   traps   visible  latent   rate    latent succ. region (median/max)  eccentricity (median/max)
BRAID_B3 L=10        1,123,740   20,128       12   20,116   1.79%          8 / 21                          4 / 7
ABELIAN  L=10        6,795,124   38,752        4   38,748   0.57%         77 / 133                         9 / 16
```

Per-target breakdown at L=10 (both presentations), which is the finding:

- ABELIAN: every trap is on xX, Xx, yY, Yy (9,688 each). Zero traps on the empty word, on x/X/y/Y, and on the
  twelve cancel-free length-2 targets. The mechanism is "cancel the pair the target needs you to keep"
  (example: state xXyY, target xX: cancel[xX] -> yY is a trap; cancel[yY] -> xX solves). The target is not a
  normal form, so success requires refraining from an always-available reduction. That is a target artifact,
  not reasoning structure. **U-A1 contains no genuine traps.** Its large continuation regions (median 77) are
  regions of the same artifact.
- BRAID_B3: 17,776 of 20,128 traps (88%) are the same artifact on xX/Xx/yY/Yy. The remaining 2,352 (588 each on
  xY, Xy, yX, Yx) are genuine: a cancel destroys a relator match the derivation needed. Example: state xXYXyx,
  target xY, D=3; cancel[xX]@0 -> YXyx (dead, no actions); relator XYX->YXY@1 -> xYXYyx -> cancel -> xYXx ->
  cancel -> xY. Genuine-trap continuation regions are 1-9 states, eccentricity 0-4 (median 2). Zero traps on the
  empty word, on length-1 targets, and on xx/xy/XY/yx (same-sign pairs).
- Every latent trap is a cancel, so the admissible length heuristic (len(s)-len(t))/2 DROPS by one on every
  trap: the trap always looks like progress to the length heuristic.
- Local-signature near-clones: 13,028 of 20,116 braid latent traps (65%) have a non-trap sibling action at the
  same state with identical (rule family, successor length, successor out-degree); 17,708 of 38,748 abelian.

Diagnostic D1 (`results/diag_BRAID_B3_L10_reduced3.json`, cancel-free targets up to length 3, 53 targets):
genuine traps rise to 5,264 (0.44% of 1.2M live triples): 0 on length 0-1, 2,352 on length-2 normal forms (0.34%),
2,912 on length-3 normal forms (1.24%), 0 on the four relator-bearing length-3 targets. Regions 2-9 (median 4),
eccentricity 1-4 (median 2). HARD 3,872, max D 8.

Diagnostic D2 (`results/diag_BRAID_B3_ONEWAY_L10_nf2.json`, U-A3 candidate, 17 normal-form targets): the system
is terminating and non-confluent, so traps are commitments to the wrong normal form. 19,490 traps (2.6% of
748,764 live triples), 96% latent; **1,340 on the empty word** (1.39% of its live triples), 1,654 on length-1,
16,496 on length-2 normal forms. 17,330 of the traps are RELATOR choices (32% of live relator applications for
these targets are traps); for those the length heuristic does not move at all. Regions 2-18 (median 4),
eccentricity 1-5 (median 2). HARD 1,768, max D 8. Example (target empty word): state xxXXYXYxyx, D=6;
rel1[XYX->YXY]@3 -> xxXYXYYxyx (out-degree 3, region 9, eccentricity 3, target lost);
rel0[xyx->yxy]@7 -> xxXXYXYyxy (out-degree 3, D=5). Two relator applications, same family, same successor
length and out-degree, opposite long-horizon consequence.

What "delayed observability" means here, in numbers: in every variant measured, a searcher that exhausts the
forward region of a successor detects the damage after at most 21 expansions (U-A2 artifact class), 9 (U-A2
genuine class), 18 (U-A3), and the BFS depth of that region is at most 4-5 for genuine traps. The phenomenon is
real, irreversible and locally invisible by the length heuristic, but it is shallow.

The structural reason, named: in a terminating rewriting system with normal-form targets, traps exist iff the
system is non-confluent, and delayed observability is bounded by the divergence depth of its critical pairs.
Cancel-only reduction is confluent (hence no traps on the empty word in U-A1/U-A2); adding reversible relators
cannot create traps; the one-way relator creates critical pairs (cancel vs relator, relator vs relator) whose
divergence is short because the relator is short. Deeper delayed damage needs longer or more numerous critical
pairs, which is a universe design decision, not a tuning knob.

## Baselines (500 problems per stratum, seed 20260912; distances of forward BFS, bidirectional BFS, D and the
oracle agree on every sampled problem, mismatches = 0 at every L)

```
BRAID_B3 L=10  (n=2000, mean D 4.53)     states expanded   transitions examined
  forward BFS                                   14.16              29.46
  bidirectional BFS                             11.44              37.84
  oracle (perfect D, min-burden descent)         4.53               8.60
ABELIAN L=10   (n=2000, mean D 4.68)
  forward BFS                                  122.83             691.56
  bidirectional BFS                             58.25             435.08
  oracle                                         4.68              16.94
```

Per stratum, BRAID_B3 L=10, transitions examined (forward / bidirectional / oracle): EASY 22.2 / 28.4 / 7.3,
MEDIUM 36.3 / 46.8 / 10.0, HARD 55.6 / 67.9 / 14.3. ABELIAN L=10: EASY 330.9 / 186.8 / 14.8, MEDIUM 881.7 /
456.3 / 20.5, HARD 1540.5 / 1085.0 / 27.4.

Ordering inflation (oracle SA vs forward BFS minus oracle SA vs bidirectional BFS): in states +7.6 points
(braid L=10), +4.2 (abelian L=10); in transitions -6.5 (braid), +1.4 (abelian). Bidirectional BFS is NOT the
cheaper baseline in transitions for the braid universe, because the reverse graph (predecessors = all words
that cancel or rewrite to the state) has high in-degree. Consequence for preregistration: the uninformed
baseline must be defined per cost unit; the draft proposes the per-problem minimum of the two.

Provisional oracle headroom (SA_oracle, ratio of sums), at the current 21-target configuration:

```
                      vs forward BFS         vs bidirectional BFS
                      states  transitions    states  transitions
BRAID_B3 L=10          0.680     0.708        0.604     0.773
ABELIAN  L=10          0.962     0.976        0.920     0.961
BRAID_B3_ONEWAY L=10   0.598     0.609        0.504     0.723   (diagnostic, 17 targets)
```

These are measurements of a configuration that is not frozen. They are not thresholds.

Base rate that matters for M2: among retained (non-trap) live actions, the fraction that lies on a shortest
path is 0.930 (braid L=10) and 0.685 (abelian L=10). In the braid universe "take any non-trap action" is
right 93% of the time; the decision-relevant content is concentrated in the 7% plus the 1.8% traps.

## Representation substrate

D chart, int16, UNREACH = -1, dimensions states x 21 targets:

```
                 live entries  density   dense raw   dense lzma   sparse COO raw  sparse COO lzma   sha256(D)
BRAID_B3 L=10       309,985    1.06%    58.72 MB     170 KB        1.86 MB          166 KB          8178d6c9...
ABELIAN  L=10       974,841    3.29%    58.72 MB     281 KB        5.85 MB          374 KB          035dc3a3...
```

Sparse COO = (state int32, target uint8, value uint8) per live entry. M1 denominators must be the lzma size of
the sparse COO; lzma alone gives 345x on the dense array because 99% of it is UNREACH.

M chart (schema in `metrics.M_SCHEMA`): edge table, one row per nominal action (src, dst, rule, pos, dst out-degree,
dst forward region, dst eccentricity; 18 bytes/row), and an edge x target table with dD (int8, +127 = lost,
-128 = inert) and a flag byte (live, retained, on shortest path, trap, latent trap).

```
                  edges       edge x target   live entries  retained    on SP     traps   edge-target raw  zlib9
BRAID_B3 L=10   3,699,144     77,682,024      1,123,740   1,103,612  1,026,192  20,128     155.4 MB      1.27 MB
ABELIAN  L=10   9,087,660    190,840,860      6,795,124   6,756,372  4,627,188  38,752     381.7 MB      5.27 MB
```

Target set (21 words of length <= 2): per-target reachable states, distance histograms and baseline burden are in
`results/*.json` under `target_stats` and `baselines.per_target`. Verified: D = 0 only at the target itself
(no trivial state identification); length parity and the length lower bound are syntactically visible
reachability filters and are declared as such. The target set is NOT appropriate as it stands: the four
cancellable targets manufacture the dominant trap class. Reduced options are in "Decision required".

## Experimental isolation

Masks (`metrics.mask_proposal`, deterministic sha256 buckets; proposal only, nothing frozen):

```
BRAID_B3 L=10   state rows  train 838,932 states / 185,996 live entries; val 279,719 / 61,761; test 279,450 / 62,228
                entries     train 186,117; val 61,984; test 61,884
                target cols held out: Y, yY, YX, XY  (60,889 live entries; 249,096 kept)
ABELIAN  L=10   state rows  train 838,611 / 585,921; val 279,552 / 194,174; test 279,938 / 194,746
                entries     train 585,666; val 194,909; test 194,266
                target cols held out: Y, yY, YX, XY  (179,021 live entries; 795,820 kept)
```

Target-column holdout is universe-independent by construction (hash key omits the universe) so OOD-A/B hold out the
same targets in every presentation. The search engine traverses the legal graph freely at evaluation; only
consequential supervision (D, M) is masked during fitting.

OOD-A (method-family transfer): choose family, DSL, objectives, architecture and hyperparameters on U-A1 train/val
only; freeze; fit that family on U-A2 train entries only; evaluate on U-A2 test entries and test problems.
OOD-B (zero-refit): fit on U-A1; apply to U-A2 with no U-A2 consequence fitting; report separately; failure does
not kill the primary hypothesis.
Caveat from this receipt: U-A1 has no genuine traps, so OOD-A can transfer a D/shortest-path representation but
cannot select for trap-awareness. If traps are the phenomenon, the calibration universe must contain them
(U-A3 in both an abelian-like and a braid-like form, or a different PC1).

Controls (`controls/construct.py`, construction only, tests pass): PC1 = U-A1 with exponent vector withheld;
PC2 = cloned relator rules (verified: identical distinct graph and D, more nominal edges); PC3 = Kronecker tensor
A[i1,i2]B[i3,i4] with naive flattening rank n^2 and structured flattening rank 1 (verified n=5); NC1-A =
degree-preserving edge swap (verified degrees, no loops, no multi-edges); NC1-B = per-column permutation of live D
values (verified exact marginals); NC2 = catalogue of latent traps with a locally indistinguishable non-trap
sibling (13,028 in braid L=10; examples in `results/BRAID_B3_L10.json` under `traps.examples`).

## Cost accounting prepared

Offline: enumeration and distance times above; peak memory not yet instrumented (add `tracemalloc`/RSS before
freeze). Online: the uncompressed lookup endpoint is D[s, t] at O(1) with 166 KB (lzma) / 1.86 MB (COO) for
braid L=10; per-decision cost of any method will be reported as wall-clock and, where honest, as operation counts.

## Proposed preregistration

See `PREREGISTRATION_DRAFT.md`: metrics M1-M6 with the base rates above, kill thresholds for H1/H2/H3 with
justification, H4 flagged as untestable as written in Universe A, instrument kills for NC1-B/PC1/PC3, and the
rule that every threshold ships with its attainable range and SE. Nothing is frozen; B2 is not yet measured.

## Decision required (stop condition)

The universe contains branching, irreversibility and delayed observability, but not in the calibration
universe, and in the test universe mostly through a target artifact. Options, none executed:

1. Keep U-A2 at L=10, restrict targets to cancel-free words of length <= 3 (D1). Genuine traps: 5,264 (0.44%),
   shallow (eccentricity <= 4). U-A1 then has zero traps and calibrates only D and shortest-path channels.
2. Adopt U-A3 (one-way relator, non-confluent) at L=10 with normal-form targets (D2). Traps on the canonical
   target, relator-choice traps invisible to the length heuristic, 2.6% prevalence, eccentricity <= 5. Needs an
   abelian-like non-confluent calibration partner (e.g. one-way commutation) to keep PC1 meaningful; not built.
3. Accept that delayed observability of 2-5 steps is the phenomenon at this scale and proceed with 1 or 2.
4. Design a universe with longer critical-pair divergence (longer relators or several interacting one-way
   relators), separately named, measured with this same instrument before adoption.

My stand: option 2 with a one-way abelian partner as PC1, because it is the only variant where the empty-word
target carries traps and where trap actions are not length-visible; then decide 3 vs 4 from that universe's
measured eccentricity distribution. I have not built the partner or changed any default.

## Remaining structural objections

- Only cancel can trap in U-A1/U-A2 (relators are reversible). Any "consequence structure" found there is a
  statement about which cancellation to defer, plus distance geometry.
- The 93% on-shortest-path base rate in U-A2 means most decisions are free; navigation gains will be decided on a
  small minority of states. Sample sizes per stratum must be set from that minority, not from the corpus size.
- Oracle transitions examined assumes the oracle scores every legal action; a method that can stop scanning early
  would beat the oracle on that count. The count definition must be fixed per method class before freezing.
- Peak memory and per-decision cost are not yet instrumented.
- H4 (operator rank) is vacuous with 6-12 rule types; needs re-scoping or removal.
