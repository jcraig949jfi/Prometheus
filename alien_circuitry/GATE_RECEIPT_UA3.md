# AC-01 U-A3 lookahead gate receipt (2026-09-12)

Verdict: **NO-GO — TOO SHALLOW.**

One-sentence answer: after giving an ordinary symbolic searcher five steps of exact local lookahead there is no
consequential uncertainty left in U-A3 for a compressed representation to exploit: depth 4 proves every one of the
12,191 traps at about six states per call, the residual set is empty, and the shortest distance itself is a closed
form in four symbol counts, so every successful path is a shortest path and a random depth-first walk is within
11% of the oracle.

No compression method was implemented, run, or inspected. U-A1, U-A2, their results, hashes, controls and the
Phase A/B receipt are unchanged (U-A3 and two PC1 candidates were added to `presentations.py` as new entries).

## Provenance

- Branch `alien-circuitry/phase-ab-2026-09-12`, base `origin/main` = `890c4d452`.
- Commits: `8983387` package; `9abb1ef` Phase A/B receipt; `0f97ddf` gate machinery + PC1-candidate controls;
  this receipt's commit carries the U-A3 results and one navigation fix (see "Corrections").
- Tests: `python -m pytest alien_circuitry/tests -q` -> 20 passed (12 universe/controls + 8 gate).
- Frozen files hashed into the result JSON: `gate/observation.py` sha256 b52695eb…, `gate/navigation.py` c5399cd6…;
  trap table `results/gate/U_A3_ONEWAY_BRAID_L10_traps.csv.gz` (uncompressed sha256 f76647e1…);
  graph: nominal edges f1a13a47…, D f831ce34….
- Environment: Python 3.12.10, numpy 2.2.6, scipy 1.17.1, Windows 11. The full U-A3 gate run takes 7.4 s.

## U-A3 — ONE-WAY BRAID

Exact semantics (`universe/directed_rewriting.py`, `presentations.py` entry `U_A3_ONEWAY_BRAID`): words over
{x, X, y, Y} with len <= L = 10; actions are (rule, position) with rules

```
cancel[xX] 'xX'->''   cancel[Xx] 'Xx'->''   cancel[yY] 'yY'->''   cancel[Yy] 'Yy'->''   rel0 'xyx'->'yxy'
```

legal at p iff the word has the lhs at p (no length increase is possible, so the cap never blocks an action). No
`yxy -> xyx`, no `XYX -> YXY`. Nominal action = (rule, position); distinct successors deduplicated for search.

Termination (`gate/termination.py`), argument and executable evidence:

- Measure mu(w) = (len(w), #x(w)), lexicographic. cancel drops len by 2; the relator keeps len and drops #x by one
  (xyx has two x, yxy has one). Every action strictly decreases mu; mu is bounded below. This does not use L:
  termination is intrinsic to the orientation. The cap only makes the state set finite.
- Verified on every nominal edge: measure violations 0 of 3,196,701.
- Self-loops 0. Strongly connected components 1,398,101 = one per state; largest SCC 1. Cycles: none.
- Longest directed path (height, iterative relaxation to a fixed point): max 8. Height histogram
  0: 96,648 | 1: 296,347 | 2: 409,823 | 3: 337,983 | 4: 187,491 | 5: 56,792 | 6: 11,255 | 7: 1,658 | 8: 104.
- Terminal (irreducible) states: 96,648 of 1,398,101. Edges: 3,196,701 nominal, 2,526,777 distinct.
- Cross-check: the same SCC test on two-way BRAID_B3 at L=5 reports cycles (test `test_two_way_universe_is_not_a_dag`).

## Corpus

Mechanical target rule, fixed before any trap rate was inspected: every terminal state of length <= 2, in index
order. That yields 17 targets: '' (1), x X y Y (4), and the 12 cancel-free length-2 words. No reducible word is a
target, so the Phase A/B artifact (targets like xX) cannot occur. Length-3 terminal words were not added.

```
candidate problems (start len >= 3, 0 < D)      194,247
EASY (3-4) / MEDIUM (5-6) / HARD (>= 7)         152,615 / 39,204 / 854      max D 8
distance histogram  1:148  2:1,426  3:13,869  4:138,746  5:33,929  6:5,275  7:802  8:52
effective branching, live states                 2.74 (nominal 3.47)
```

Per target (reachable states / problems): '' 24,341 / 24,336; x 6,085 / 6,084; X 5,769 / 5,768; y 6,429 / 6,428;
Y 5,741 / 5,740; xx 11,853 / 11,852; xy 14,911 / 14,910; xY 11,424 / 11,423; XX 11,058 / 11,057; Xy 11,883 / 11,882;
XY 11,027 / 11,026; yx 14,911 / 14,910; yX 11,883 / 11,882; yy 13,506 / 13,505; Yx 11,424 / 11,423; YX 11,027 /
11,026; YY 10,996 / 10,995. Distance histograms per target are in the result JSON (`target_stats`). No target
creates a second artifact: every target carries traps (65 to 1,847) and D = 0 only at the target itself.

## Trap topology

Trap = (s, a, t) with D[s,t] >= 0 and D[a(s),t] = UNREACH. All 12,191 recorded with source, family, rule, position,
successor, source distance, successor local features, region and eccentricity/height (`results/gate/*_traps.csv.gz`).

```
genuine traps                 12,191   of 674,846 live (s,a,t) triples   rate 1.81%
  relator-induced             11,123   (91.2%)    cancel-induced 1,068 (8.8%)
visible (successor terminal)     482   latent 11,709
post-trap region size   1:482  2:2,902  3:1,318  4:3,364  5:474  6:1,612  7:224  8:951  9:224  10:296  11-16: 344
post-trap eccentricity  0:482  1:3,164  2:5,037  3:3,484  4:24         max 4
post-trap height        identical to eccentricity for every trap successor (tree and graph horizons coincide)
source distance         1:2  2:39  3:629  4:9,021  5:2,272  6:216  7:12
```

Matched siblings (`gate/analysis.sibling_match`, features frozen in `observation.py`): every trap has at least one
non-trap sibling action from the same source (12,191 of 12,191). Exact match on all six features (rule family,
successor length, successor out-degree, successor equals target, successor cancel count, successor relator count):
162 traps (1.3%); loose match on the first three: 262. The 162 exactly matched pairs are frozen as the diagnostic
set (rows with `exact_match = 1` in the trap table). Three of them:

- source xyxyxyYYXY, target xy, D = 5: relator at 0 -> yxyyxyYYXY (out-degree 1, region 2, target lost);
  relator at 2 -> xyyxyyYYXY (out-degree 1, D = 4). Same rule, same features, opposite consequence, H_pair = 1.
- source xXXxyXxxYX, target Xy, D = 5: cancel Xx at 2 -> region 4, eccentricity 2, target lost;
  cancel xX at 0 -> D = 4. H_pair = 2.
- source XxxyxxXYYX, target Xy, D = 6: cancel Xx at 0 -> region 6, eccentricity 3, target lost;
  cancel xX at 5 -> D = 5. H_pair = 3.

## Frozen observation language and lookahead

Depth-0 features of a state: length, terminal flag, out-degree, action count, cancel count, relator-match count,
the four symbol counts, immediate target equality; derived: length lower bound (len(s') - len(t))/2 and the
provably-unreachable tests (length, parity, and the abelianisation exponent e = cx - cX + cy - cY, which every
action preserves). Nothing global: no D, no Reach, no trap labels, no cross-problem cache.

Exact bounded lookahead of depth h from a candidate successor: graph BFS within h moves with a visited set;
SAFE(d) when the target appears at depth d <= h, TRAP when the forward region is exhausted (no frontier node has an
unseen successor), UNKNOWN otherwise. Sound in both directions (test `test_lookahead_is_sound`). Costs counted
"uncached" per call and "cached" against a per-problem memo shared with the search.

## Q1 — trap classification over all 674,846 live triples (exact, sound controller)

Mapping A treats UNKNOWN as SAFE (the operational choice of a searcher without proof); mapping B treats UNKNOWN as
TRAP. Prevalence 1.81%. Base rates: always-SAFE recall 0, balanced accuracy 0.5; always-TRAP precision 0.018.

```
h   traps proven   non-traps proven safe   resolved   A: recall  precision  FPR    bal.acc   B: precision  FPR
0        482              180               0.1%       0.040      1.000    0      0.520        0.018      0.9997
1      3,646            3,078               1.0%       0.299      1.000    0      0.650        0.018      0.995
2      8,683           41,877               7.5%       0.712      1.000    0      0.856        0.019      0.937
3     12,167          531,166              80.5%       0.998      1.000    0      0.999        0.085      0.198
4     12,191          647,373              97.7%       1.000      1.000    0      1.000        0.444      0.023
5     12,191          661,053              99.8%       1.000      1.000    0      1.000        0.884      0.002
```

PR-AUC is not reported: the controller is three-valued and sound, so precision is 1 at every recall it attains.

Cost per lookahead call (3,000 random live successors, uncached; states expanded / transitions examined / fraction
resolved): h0 1.0 / 2.2 / 0.00; h1 2.0 / 3.7 / 0.02; h2 4.1 / 6.8 / 0.11; h3 5.5 / 8.5 / 0.75; h4 5.8 / 8.8 / 0.97;
h5 5.8 / 8.8 / 1.00. The ball saturates at about six states because the forward cone of a typical successor in
U-A3 has six states in total. Depth-3 lookahead removes 99.8% of trap uncertainty for 5.5 states per call.

## Observability horizon

H_trap = smallest depth at which the trap is proven (= eccentricity of the trap successor; the tree horizon via
height is identical). H_pair = min(H_trap, D of the best good sibling).

```
                          0      1      2      3      4     5    >5      n
all genuine traps       482  3,164  5,037  3,484    24     0     0   12,191
cancel traps             80    382    552     50     4     0     0    1,068
relator traps           402  2,782  4,485  3,434    20     0     0   11,123
matched subset (H_trap)   0     10    126     26     0     0     0      162
matched subset (H_pair)   0     10    126     26     0     0     0      162
```

Residual set R_5 (matched pairs unresolved at depth 5): **empty** under both graph and tree semantics. There is no
long-horizon structure to characterise. The deepest trap in the universe is resolved at depth 4, and only 24 traps
need it.

## Q2 — navigation (900 problems: 300 EASY, 300 MEDIUM, 300 HARD; mean D 5.37; seed 20260912)

Uninformed exact baselines and oracle (per-problem means; distances agree across all four on every problem):

```
                          states expanded   transitions examined
forward BFS                   13.05               20.23
bidirectional BFS             10.94               27.88
per-problem min (B8)          10.94               20.23
oracle (perfect D)             5.37                7.96
oracle SA vs B8               0.510               0.607
```

Policies (greedy walk = commit, no backtracking; DFS = policy-ordered depth-first with backtracking; costs are the
cached per-problem totals including lookahead; every DFS run solved 100% with zero excess path length):

```
policy   greedy solve  catastrophic   DFS transitions  DFS states   uncached transitions   residual SA (oracle vs policy)
                                        (cached)        (cached)     (greedy)               transitions   states
B0 random     0.942       0.058            9.0            5.5           8.8                   0.111        0.027
B1 length     0.981       0.019            8.4            5.4           8.3                   0.054        0.007
B2 local      0.994       0.006            8.9            5.4           8.8                   0.102        0.004
LA1           0.996       0.004           15.9            9.4          29.8                   0.498        0.428
LA2           0.998       0.002           18.2           10.8          42.5                   0.562        0.502
LA3           0.998       0.002           19.4           11.5          50.4                   0.589        0.533
LA4           1.000       0.000           19.9           11.9          53.3                   0.601        0.547
LA5           1.000       0.000           20.2           12.0          55.0                   0.605        0.553
```

Excess path length is 0.00 for every solved problem under every policy (see "Degeneracy"). Per-stratum rows are in
the JSON; HARD catastrophic rates for greedy: B0 4.3%, B1 2.3%, B2 1.0%, LA1 1.0%, LA2/LA3 0.7%, LA4/LA5 0.

Reading: lookahead buys nothing a searcher needs. B2 with zero lookahead already solves 99.4% greedily; the
backtracking DFS of any policy solves everything at 8.4 to 9.0 transitions, and adding lookahead only adds its own
cost (LA5 costs 2.4x B2 for the same solutions). The residual headroom that a compressed representation could
still claim, against the strongest cheap policy by cost (B1-DFS), is 5.4% in transitions and 0.7% in states. The
larger "residual SA" numbers against LA1-LA5 measure the lookahead's own overhead, not uncertainty.

## Degeneracy found while attacking the claim

Every path from s to t in U-A3 has the same length, and that length is a local closed form. Let cx, cX, cy, cY be
the symbol counts. A cancel of x-type lowers cX by one, a cancel of y-type lowers cY by one, and only the relator
changes cx beyond that (by minus one, raising cy by one). Along any path, the x-cancels a, y-cancels b and relator
applications r are forced by the endpoints: a = cX(s) - cX(t), b = cY(s) - cY(t), r = cx(s) - cx(t) - a, so the
path length a + b + r = (cx(s) - cx(t)) + (cY(s) - cY(t)). Verified: the formula equals D on all 194,268 live
(state, target) entries with 0 mismatches, and every retained edge lies on a shortest path (662,655 of 662,655).
Consequently the distance channel of the consequence chart carries zero information beyond symbol counts, the
"on shortest path" channel is identical to "retained", and the only consequential content in U-A3 is the
reachability bit, which depth-4 lookahead resolves exactly. This is a structural property of a one-way relator
that changes the count vector in a fixed direction; it would have to be excluded by design in any successor
universe.

## Positive control

**NO MATCHED PC1 FOUND.**

- ONEWAY_ABELIAN_ALL4 (all four commutation variants one way, plus cancel): terminating (DAG confirmed), 0 traps
  on 13 mechanical targets at L=9. It is confluent (every critical pair joins), so it has no normal-form
  divergence and cannot calibrate trap-awareness. Retained only as a confluent no-trap control: any method that
  "finds" traps there is broken.
- ONEWAY_ABELIAN_XY (xy -> yx only, plus cancel): non-confluent, 15,261 traps on 16 targets at L=9, 90% relator-
  induced, H_obs <= 5 for all (0:310 1:2,490 2:6,580 3:5,073 4:730 5:78), 168 exactly matched pairs, R_5 empty.
  It has divergence but no consequence structure I can state in closed form, so it cannot serve as a known-answer
  control, and it is as shallow as U-A3.
- The old two-way ABELIAN (U-A1) remains a distance/coordinate control (exponent vector), not a trap control.

## Corrections made during the gate

- The greedy walker's "every option proven dead" stop rule read the first key element as a tier; B0/B1 keys did not
  carry a tier, so B1 greedy stopped whenever all successors had length 2. Fixed by giving every policy a tier
  prefix; regression test `test_greedy_never_stops_early_for_tierless_policies` added; gate rerun. Only the B1
  greedy row changed (from an invalid 7.8% solve rate to 98.1%).
- The first height DP assumed the (len, #x) measure; replaced by DAG-safe iterative relaxation so the PC1
  candidates (where that measure does not apply) get correct heights.
- A crash on universes with zero traps (ALL4) in the summary code was fixed; no numbers were affected.

## Recommendation for a separately named longer-horizon universe (not built)

Properties it must have, each measurable with the existing gate before adoption:

1. Non-confluent and terminating with critical-pair divergence deeper than the lookahead budget: H_obs > 5 for a
   substantial matched-sibling subset, R_5 non-empty and not explained by a target artifact. Natural source: a
   rewriting system whose Knuth-Bendix completion needs many long added rules, so competing normal forms separate
   only after several overlapping applications.
2. Path length must not be a symbol-count invariant: at least two rules with linearly independent count signatures
   whose application counts are not fixed by the endpoints (test: variance of path length between fixed endpoints
   > 0, and "retained" != "on shortest path").
3. Random-walk solve rate well below 1 and uninformed search cost large relative to D, so navigation has headroom
   that a cheap policy does not already take (test: B0 and B2 greedy solve rates and B8 versus oracle).
4. Mechanical normal-form targets, no reducible targets, all targets carrying traps.
5. Exhaustively enumerable at a cap where the above hold.

Until a universe passes those tests, AC-01 has nothing to compress that a five-step symbolic search does not
already observe.
