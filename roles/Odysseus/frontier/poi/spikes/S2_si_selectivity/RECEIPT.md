# S2 RECEIPT -- SI selectivity readings (a)-(c) under margin, balance and permutation null

Worker: disposable spike worker for Odysseus POI frontier. Date 2026-09-27. Stdlib Python only. Wall 2m48s, 1 core.

## Question

The delegate (roles/Odysseus/frontier/poi/raw/I3_laws_rsi_worlds.md, T2/T4, s5 D1) reported, INFERRED:
 (a) winner class carries more information about task FAMILY (0.236 bits) than about GENERATOR (0.183 of H=1.221);
 (b) selective arms win pairwise worlds 139/164;
 (c) declared relevance-driven eviction (keep_worst, residual_reservoir) LOSES to random eviction.
Do these survive (1) counting a win only beyond the program's 0.30 AC margin, (2) balanced arm counts / matched worlds,
(3) a permutation null (>= 1000 permutations, fixed RNG seed)?

## The margin (quoted)

ensorain/PREREG_WTP_LM01.md s6.0 (frozen v0.3.1, 768ea8ce9):
  "6.0 GOVERNING TOLERANCE (operator ruling item 2): DELTA = 0.30 AC (a 2x MSE ratio).
   - Noise enters only through the CI: a 90% two-sided t-interval over worlds of the PAIRED per-world difference ...
   - EQUIVALENT: the CI lies inside (-0.30, +0.30).
   - WIN: the CI lies entirely beyond +0.30 in the stated direction.
   - Anything else is UNRESOLVED."
Also ensorain/LM01_PREREG_REVIEW_2026-09-26.md s2: "AC = -log10(MSE / field variance). 0.30 AC = a 2x MSE ratio."
This spike applies it two ways: (i) per-world point rule (a world is "won" only if the best arm of the winning class
beats the best arm of every other class by > 0.30; else TIE), and (ii) the program's own per-stratum paired 90% t-CI
rule (WIN+/WIN-/EQUIV/UNRESOLVED). Sensitivity at 0.15 and 0.60 is also in the JSON.

## Dev / sealed separation (established from the record)

- PREREG_WTP_LM01.md s9: "Dev ranges used: 9_1xx_xxx .. 9_6xx_xxx ... make_world refuses any other seed below 10^9";
  CAMPAIGN seeds are 10^9 + hash, REPLICATION 2 x 10^9 + hash. roles/Ensorain/STATUS.md: "dev seeds 9.1M-9.9M;
  campaign seeds disjoint".
- Seeds actually read (asserted < 10^9 in probe.py): selection_v2 9_410_000-015; margins v1 9_500_000-015; fixture
  9_330_000-003. No campaign, launch, sealed or C3 file was opened. python -m ensorain.lm01.launch was not run.

## Files used (path, git SHA from `git log -1 --format=%h -- <path>`)

  roles/Odysseus/frontier/poi/raw/I3_laws_rsi_worlds.md      e82bf2311  (delegate notes: T2, T4, s5 D1)
  ensorain/lm01/dev/selection_v2.json                         6f677751a  (1,200 rows, 1,032 OK, 26 arms/world;
                                                                          sha256 0091e59959cdc7ff = FROZEN source)
  ensorain/lm01/FROZEN_SELECTION.json                         6f677751a  (1 frozen arm per class per stratum)
  ensorain/lm01/dev/margins/*.jsonl                           8d4ca5017  (margins v1: 1,056 OK worlds; frozen S/L/H
                                                                          arms AC_a; reservoir ladder random|B and
                                                                          declared-policy|B at the same B, same world)
  ensorain/lm01/dev/fixture_reservoir.json                    6a48ff937  (eviction positive-control medians)
  ensorain/PREREG_WTP_LM01.md                                 768ea8ce9  (margin s6.0, seeds s9)
  ensorain/LM01_PREREG_REVIEW_2026-09-26.md                   222ed8082  (margin s2)
  roles/Ensorain/STATUS.md                                    222ed8082  (dev/campaign seed disjointness)
  programs/selective_irreversibility/EXPERIMENTS.md           61b970537  (03:48Z eviction claim)
  ensorain/lm01/select_arms.py 860fc7cf6, ensorain/lm01/margins.py 3fc37e0c7 (read only, to confirm row semantics)

## Command

  cd roles/Odysseus/frontier/poi/spikes/S2_si_selectivity && python3 probe.py
  -> probe_out.json. NPERM = 2000, NBOOT = 1000, random.Random(20260927). Deterministic.

Nulls: (N1) winner labels shuffled across worlds -> chance MI given finite n; (N2) family shuffled within generator
blocks -> null for I(W;F|G); (N3) generator shuffled within family blocks -> null for I(W;G|F); (N4) per-world
permutation of AC across arm labels -> chance S-win count; (N5) per-world sign flip of (declared - random) -> chance
mean and loss count. Plus a world bootstrap 90% CI of I(W;F) - I(W;G).

## Results

### (a) family vs generator information (bits)

 set                                    n     H(W)   I(W;F)  I(W;G)  diff   boot90 diff      null mean I(F)/I(G)
 sel_v2 26 arms, raw (reproduction)   1032  1.221  .236    .183    +.053  [+.009, +.093]    .009 / .014
 sel_v2 26 arms, delta .30 (TIE kept) 1032  1.524  .421    .250    +.171  [+.115, +.224]    .006 / .008
 sel_v2 26 arms, delta .30 decisive    557  0.980  .469    .238    +.231  [+.152, +.303]    .005 / .008
 sel_v2 balanced 1/class, raw         1032  1.354  .171    .184    -.012  [-.050, +.021]    .009 / .013
 sel_v2 balanced 1/class, delta .30   1032  1.570  .363    .281    +.082  [+.032, +.127]    .012 / .018
 margins v1 held-out 1/class, raw     1020  1.314  .199    .159    +.040  [+.001, +.073]    .009 / .014
 margins v1 held-out 1/class, d .30   1020  1.588  .358    .245    +.113  [+.066, +.160]    .012 / .018
 All observed I values exceed every one of 2000 N1 permutations (p < .0005); N1 p95 of the diff is ~.004.
 Conditional (raw, 26 arms): I(W;F|G) = .535 (N2 null mean .027), I(W;G|F) = .482 (N3 null mean .029); both p < .0005.
 Same pattern in every set (e.g. margins v1 d.30: .555 vs .442). I(W;level) <= .027 everywhere.
 Delegate numbers reproduced exactly (H 1.221, .236, .183, .010; generator x class table identical).

### (b) selective wins on pairwise-generator worlds

 set                              raw    >.15   >.30   >.60   N4 null @.30 mean/p99   per-stratum rule @.30 (11 strata)
 sel_v2 26 arms (8 S of 26)       139/164 92    71     38     18.0 / 26             WIN+ 2, EQUIV 2, UNRESOLVED 7
 sel_v2 balanced 1/class          133/164 89    69     32     18.2 / 27             WIN+ 1, EQUIV 4, UNRESOLVED 6
 margins v1 held-out 1/class      124/162 95    74     39     21.9 / 32             WIN+ 3, EQUIV 1, UNRESOLVED 7
 Held-out WIN+ strata: F2-L2, F2-L3, F3-L3. F4-L1 is EQUIV. F5-L2/L3 flip sign held-out (mean -0.37, -0.26;
 UNRESOLVED) versus +0.57/+0.47 in selection_v2.

### (c) declared eviction vs random eviction, same world, same B (margins v1)

 rung  n     mean(decl-rand)  decl loses >.30  decl wins >.30  within   N5 loss-count p99  per-stratum (policy) verdicts
 c/8   1020  +0.156           37               253             730      165                EQUIV 39, WIN+ 13, UNRES 17
 c/4   1020  +0.134           47               273             700      181                EQUIV 37, WIN+ 14, UNRES 16, WIN- 2
 c/2   1020  +0.145           12               228             780      137                EQUIV 43, WIN+ 6, UNRES 20
 c      828  +0.078           19                97             712       70                EQUIV 43, WIN+ 1, UNRES 13
 2c     816  +0.014           19                12             785       22                EQUIV 51
 Sign-flip null for the mean: p <= .001 at every rung (in the direction declared > random). Both policies positive
 at c/8..c (keep_worst +0.06..+0.19, residual_reservoir +0.09..+0.16).
 Positive-control world (fixture, 4 seeds, medians only; the basis of the recorded claim): keep_worst - random =
 -0.139, residual_reservoir - random = -0.122. Both inside the 0.30 margin; no per-world rows exist, so no CI or
 permutation is possible.

## What changed vs the delegate's reading

(a) SURVIVES in direction, but not as stated. The raw +.053 gap is small (bootstrap 90% [.009, .093]) and VANISHES
    under arm balance on the same rows (-.012, [-.050, +.021]); on held-out seeds with balance it is +.040, barely
    above 0. With the 0.30 margin, family > generator is clear and larger (+.08 to +.23, all CIs above 0), largely
    because family decides WHETHER there is a decisive winner (TIE rate). Both quantities are far above chance. But
    the conditional terms are each ~0.45-0.55 bits: neither family nor generator "decides" the winner alone; the
    winner is set by their interaction (joint I(W;F,G) ~ .72 of 1.22 raw). So the recorded "generator decides" claim
    is not supported, and neither is "family decides"; the correct reading is family x generator.
(b) SURVIVES as "selective is the most frequent winner on pairwise worlds", far above chance, but the headline
    shrinks: 139/164 -> 71/164 beyond 0.30 (74/162 held-out, balanced). Under the program's own paired-CI rule only
    1-3 of 11 pairwise strata are WIN+ for S; most are UNRESOLVED; F4 strata are EQUIV and F5 flips sign held-out.
(c) REVERSED as a general statement. On matched worlds at matched B, declared eviction BEATS random on average
    (+0.08 to +0.16 AC at B <= cells; 228-273 world wins vs 12-47 losses beyond 0.30; 0-2 strata WIN- of ~69).
    The recorded loss is confined to the corrupted-half positive-control fixture, and there the deficit (-0.12,
    -0.14) is inside the 0.30 margin on 4 seeds: not a loss by the program's rule. T4 ("why does random beat smart
    eviction") asks about an effect that the dev record does not show outside that one fixture.

## Limits

- Dev rows only; the frozen campaign would supersede everything here.
- Balanced selection_v2 uses arms frozen on those same rows (in-sample); margins v1 is the out-of-sample check.
- The per-world 0.30 point rule is my operationalization; the program's rule is the per-stratum CI, reported beside it.
- N1/N4 are chance nulls (no structure). They show the effects are not noise, not that the effects mean what the
  labels say. Arm-label permutation (N4) is a weak null against any real quality difference between arms.
- Family and generator are not fully crossed (F1 only has generator "random"); H(gen) 2.74 > H(fam) 2.16 bits.
- margins v1 F5 rows predate the F5 real_cells scale repair (PREREG s2; dev/margins_f5real not used), so F5 held-out
  numbers carry that defect.
- selection_v2 (01:01) predates the one-ALS-convergence rule (D7, recorded 03:48Z); margins v1 (04:37) postdates it.
- In margins v1 the declared policy is the per-stratum frozen choice (1 of 2), picked on selection_v2 seeds, so a
  mild selection advantage over random is possible; it cannot explain 228-273 wins vs 12-47 losses.
- (c) on the positive-control world rests on 4 fixture medians; no per-world rows, so no CI/null there.
- Housekeeping: probe.py and a first-run probe_out.json were committed by the parent session (d53c189eb) while this
  spike was running; the current probe_out.json (with the bootstrap) differs from that commit. This worker made no
  git operations.
