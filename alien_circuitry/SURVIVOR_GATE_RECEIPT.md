# AC-01 survivor falsification gate receipt (2026-09-12)

Verdict: **NO-GO — RESIDUAL TOO SMALL.**

Two preregistered kills fired. K3 fired without any threshold sensitivity: in U-C1 with the frozen rank-5 map, the
kernel-refinement criterion is exactly sufficient, so the residual reachability layer R1 is zero on all 51,716,070
corpus pairs and every one of its 6,097,140 traps is explained by the known invariant. K2 also fired by the letter of
its PR-AUC clause on PC-H (0.685 against a preregistered 0.5), while its mutual-information clause did not (0.31
against 0.5); the diagnostic in "Gate B" shows the leak is rank-conditional trap prevalence, not kernel
identification, and that the 0.5 PR-AUC line was calibrated to a 9.2% base rate when the collapse-only base rate is
39%. I did not change K2 after seeing the value; the operator rules on it. K1, K4 and K5 did not fire.

Answer to the remaining AC-01 question: after subtracting shallow lookahead and the known kernel invariant there is
still substantial exact search burden, but it lives in the distance layer, not in reachability. The kernel-aware,
residual-blind searcher still costs 2.4x (PC-H) and 2.0x (U-C1) the oracle in transitions (H2 = 0.58 and 0.51),
takes paths 13 to 18 steps longer than optimal, and permitted count features explain only 51-58% of the variance of
D with 23-24% exact-match. Whether that distance geometry admits a compact representation is the live question;
with this seed there is no reachability question left for a compressor to answer.

## Provenance

- Branch `alien-circuitry/phase-ab-2026-09-12`, base `origin/main` = `890c4d452`. Prior universes untouched
  (Datalog record, U-A1, U-A2, U-A3 gate at fb6f4c9, design search at f7ba883).
- Commits: `9997a33` seed + preregistration (before any n=7 measurement); `fd214d4` gate2 machinery; this receipt's
  commit carries results, the runner's phase/memory patches and the leakage diagnostic.
- Tests: `python -m pytest alien_circuitry/tests -q` -> 28 passed (12 universe/controls, 8 U-A3 gate, 8 survivor).
- Record correction accepted: the canonical U-A3 numbers are the committed ones (71.2 / 99.8 / 100% at h = 2/3/4,
  none beyond 4, R_5 empty, longest path 8). No historical receipt was rewritten.
- Memory: this machine had 3.8 GB free (another seat's process holds 7.8 GB); three runs were killed by the harness
  at ~650 MB RSS plus transients. The runner was split into analysis and navigation phases with per-stage dumps, and
  the leakage/distance attacks were capped at 3M / 250k rows by seeded per-target subsampling. Nothing in the
  measurements changed except those sample sizes, which are recorded in the JSON.

## Frozen objects

- U-C1 seed: string `AC01|U-C1|rank5map|n=7|frozen-2026-09-12`, seed 5773439276592744044, map
  [3, 4, 0, 3, 3, 5, 6] (rank 5, merges values 0, 3, 4), sha256 a3ef1c7b…; committed at 9997a33 before
  enumeration. Not redrawn.
- Targets: the 63 restricted-growth maps of rank 2. Corpus: 820,890 states of rank >= 3. Strata by exact D:
  EASY 3-8, MEDIUM 9-14, HARD >= 15.
- Observation language: `SURVIVOR_GATE_PREREG.md`; implemented in `gate2/observation_monoid.py`; test
  `test_observer_features_are_pairwise_free` checks two states with different kernels and equal count vectors get
  identical features.

## PC-H — full T_7

Graph: 823,543 states; 2,470,629 legal actions of which 358,061 are no-ops (collapse on a state without value 0);
1,910,756 distinct edges; out-degree 1/2/3 for 78,126 / 403,621 / 341,796 states. 877 strongly connected
components = Bell(7), one per kernel; the largest is the 5,040 permutations. The generated monoid from the
identity is all of T_7 (word length up to 34). Reachable (state, target) pairs 11,138,190; R0 40,577,880; R1 0.
D from 3 to 24; strata EASY 58,310 / MEDIUM 2,344,748 / HARD 8,735,132.

Traps: 3,069,066 of 33,422,508 live triples (9.18%), all collapses; 126 are rank-visible. Post-trap region
7 / 2,401 / 2,401 / 16,807 / 117,649 (quartiles); eccentricity 5 / 21 / 23 / 27 / 30.

Gate A (exact lookahead, graph semantics; tree semantics is undefined because the universe has cycles):

```
h            0        1        2        3        4        5
traps proven 0        0        0        0        0        126      (recall 0.00004; precision 1; FPR 0)
safe proven  126      378      1,547    4,711    9,870    22,134
resolved     0.00%    0.00%    0.00%    0.01%    0.03%    0.07%
ball cost    1.0/2.3  2.0/4.7  4.3/10   8.2/19   15.6/36  29.2/68   states / transitions per call
H_obs        <=5: 126   6-12: 14,448   13-20: 608,412   21-30: 2,446,080   >30: 0
```

PR-AUC of the sound controller equals its recall (precision 1 at every attained recall): 0.00004. K1 requires
LA5 > 10%: not fired by five orders of magnitude. The emulated verdicts agreed with the literal BFS ball on 100% of
2,595 sampled calls at every depth.

Gate B (leakage; 3,000,000 of 8,167,866 live collapse triples, split 60/40 by hashed state; base rate 0.390):

```
feature set                          cells   PR-AUC   bal.acc   recall@P>=0.5   nMI
tuple A (preregistered)               180    0.685    0.701       1.00          0.314
tuple B (A + full count vectors)    5,084    0.685    0.728       1.00          0.314
diagnostic: A minus c0, c1             72    0.680    0.702       1.00          0.307
diagnostic: ranks only                 11    0.555    0.634       1.00          0.267
diagnostic: c0, c1, target blocks      63    0.638    0.729       1.00          0.290
diagnostic: merged size vs max block   21    0.592    0.626       0.85          0.181
```

Calibration is exact (table classifier; every bin's mean prediction equals its observed rate within 0.02). The
kernel class is not reconstructed: 69% of the trap entropy survives every permitted feature set, and most of the
recovered 31% is carried by rank alone (how many collapses remain determines how likely a blind collapse is to be
wrong). K2's PR-AUC clause fires (0.685 >= 0.5); the MI clause does not (0.314 < 0.5).

Distance attack (249,984 reachable pairs, 7,214 cells, 0.7% unseen): table regressor R^2 0.580, exact 0.238,
within-1 0.611, MAE 1.43, Spearman 0.75; linear on numeric features R^2 0.457; rank-only R^2 0.447. K4 not fired.

Navigation (120 problems, 40 per stratum, mean D 12.4; DFS budget 40,000 expansions; lookahead charged per call at
the sampled ball mean, an approximation stated in the preregistration):

```
                       greedy solve  catastrophic   DFS solve   DFS transitions   excess   traps taken
B0 random                  0.100        0.825         0.975         6,298          67.4       1.79
B1 rank                    0.033        0.167         1.000         4,782          17.8       1.43
B2 local                   0.033        0.167         1.000         4,776          17.8       1.43
LA1 .. LA5                 0.03-0.22    0.16-0.17     1.000      27,013 .. 325,740  15-12     1.3-1.4
KA kernel-aware (ref)      0.033        0.000         1.000            65          17.8       0.00
forward BFS  8,273 states / 18,328 transitions   bidirectional BFS 460 / 1,111   oracle 12.4 / 27.4
```

H0 = 0.975 (transitions; oracle vs per-problem min of the two exact searches). H1 = 0.994 (B2). H2 = 0.577
(oracle 27.4 vs KA 65). Lookahead never helps: it cannot prove traps here and its cost dominates.

## U-C1 — frozen restricted submonoid

Graph: same 823,543 states; 2,470,629 actions, 80,312 no-ops; 2,390,316 distinct edges; out-degree 3 for
745,417 states. 877 SCCs again (permutations act within each kernel class). The generated monoid from the identity
has 364,903 elements (rank histogram 7 / 2,646 / 63,210 / 205,800 / 88,200 / 0 / 5,040 for ranks 1..7: rank 6 is
never produced), max word length 28. Reachable pairs 11,138,190 — identical to PC-H. R0 40,577,880. **R1 = 0.**
D from 5 to 20; strata EASY 1,037,792 / MEDIUM 7,406,998 / HARD 2,693,400.

Why R1 is zero (theorem, after the fact): the frozen map merges the classes of three values. Conjugating by the
permutations, any two or three classes of a state can be placed on those values; applying the map with only two of
them present merges exactly those two. Every pairwise coarsening is therefore realisable, and the rank-2 targets
need nothing else. The n=6 residuals (2-5%) came from maps whose merge patterns could not realise every pairwise
merge; this seed's pattern can. The seed was frozen before this was known and is not redrawn.

Traps: 6,097,140 (18.2% of live triples), all by the rank-5 map, 5,796 rank-visible; region 7 / 343 / 2,401 /
2,401 / 16,807; eccentricity 6 / 13 / 15 / 17 / 19. Gate A: 0 traps proven at every depth 0..5 (min eccentricity
6); safe proofs 126 .. 58,758; resolved 0.18% at h = 5; ball cost at h = 5 60 states / 160 transitions.
Leakage (base 0.570): PR-AUC 0.861 / 0.862, balanced accuracy 0.73, nMI 0.33. Distance attack: table R^2 0.510,
exact 0.232, within-1 0.608, Spearman 0.67; linear 0.268; rank-only 0.267.

Navigation (120 problems, mean D 11.6): bidirectional BFS 761 states / 3,076 transitions; forward BFS 18,166 /
51,646; oracle 11.6 / 30.0; H0 = 0.990. Cheap policies: B0 DFS solves 95.8% at 18,860 transitions, B1/B2 95.0%
at 18,100 (HARD 85%), lookahead policies same solve rates at 117k .. 2.9M; H1 = 0.998 (B0, the only cheap policy
above 95%). KA: 100% solved, 61 transitions, zero traps, excess 12.7; H2 = 0.507.

## Kill summary

```
K1 SHALLOW      PC-H LA5 recall 0.00004  (limit 0.10)         not fired
K2 LEAKAGE      PC-H PR-AUC 0.685 (limit 0.5) FIRED by letter; nMI 0.314 (limit 0.5) not fired; see diagnostic
K3 RESIDUAL     U-C1 R1 = 0 pairs, 0% of kernel-compatible, 0 R1-traps (limits 10,000 / 1% / 5%)   FIRED
K4 DISTANCE     exact 0.24 / 0.23, R^2 0.58 / 0.51 (limits 0.9 / 0.95)    not fired
K5 ORACLE       D produced in 3.3 s per universe                          not fired
```

## What remains true and what to rule on

1. T_7 is the first universe in this programme where five steps of exact lookahead resolve essentially nothing
   (0.004%), and where bad states keep thousands of viable states for 13 to 30 steps. Gate A is passed in a way
   no previous universe approached.
2. The known invariant explains reachability completely in both universes as frozen. The primary discovery layer
   that U-C1 was built to provide does not exist with this seed.
3. The distance layer is real and unexplained: kernel-aware search is still 2.0-2.4x the oracle, count features
   leave 42-49% of D's variance, and the 63 targets give a multi-column distance chart. If AC-01 continues, it
   continues as a distance-geometry question on T_7, with PC-H's reachability layer as the sensitivity control.
4. K2's PR-AUC line must be re-set before any rerun, with the collapse-only base rate (0.39) and the SE of PR-AUC
   on ~1.2M held-out rows stated beside it, and with a decision on whether rank-conditional prevalence counts as
   leakage at all (it is a prior every searcher can estimate from its own failures).
5. A U-C1 with R1 > 0 needs a rank-dropping generator whose merge pattern cannot realise every pairwise
   coarsening, selected by a committed procedure (for instance the first seed in a fixed sequence whose map has no
   two-value merge reachable under conjugation), never by inspecting consequence structure.

Nothing was fitted, decomposed or embedded. No corpus objects were frozen, because the gate did not pass.
