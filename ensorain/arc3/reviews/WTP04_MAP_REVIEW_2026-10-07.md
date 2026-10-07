+==============================================================================+
| REVIEW PACKET -- ENSORAIN WTP-04 HABITABLE ISLANDS (MAP STAGE)               |
| Author: Ensorain seat (Claude Opus 5.5), host ubu006 (Linux, 4 cores, 15 GB) |
| Date: 2026-10-07                                                             |
| For: operator (HITL) + external reviewers                                    |
| Status: CLOSED -- mechanical verdict ISLANDS_MAPPED; nothing further launched|
| Self-contained: no repo access needed; every load-bearing number is inline.  |
+==============================================================================+

------------------------------------------------------------------------------
0. SUMMARY
------------------------------------------------------------------------------
Mandate. Operator direction 2026-09-30: "map the boundaries of computationally
habitable worlds": take each independent WTP-03 founding family and push its
physics outward, before choosing any favoured substrate. Standing rule:
cheap competitors first, always. Operator chat 2026-10-06: "Go".

Question asked. Two parts:
  - In which worlds does learning pay at all? (A learner earns more than
    no-memory and frozen-memory twins.)
  - Where it pays, does a cheap carrier suffice, or does a structured one win?
    Cheap carriers: constant, table, additive.
    Structured carriers: low-rank, CP, TT, DCT.

Verdict (rule fixed in advance): ISLANDS_MAPPED.
  - 9 of 12 families have a paying cell.
  - 8 of 12 have a replicated paying<->dead boundary on an ordered axis.
  - Seed disagreement (SPLIT) is 11.3% of cells.

Main finding. At one-axis resolution, habitability is INHERITED from the
founding family; it is not created by moving physics.
  - 4 families are dead at native and stay dead in 52-53 of 53 perturbed cells.
  - 6 families pay at native and pay in 55-72% of perturbed cells.
  - The winning carrier class (cheap vs structured) is also a family constant.
    It changed, replicated, in only 2 of 132 family x axis pairs.

------------------------------------------------------------------------------
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
------------------------------------------------------------------------------
- Engine: ensorain/wtp4/ (new). It imports the frozen WTP-03 world executor
  unchanged.
  - families.py: the 13 WTP-03 founder lineages -> 12 families. Fixed rule:
    lineages are the same family iff they share generator class, dims style and
    observation kind. Representative = the member with the highest WTP-03
    information demand.
  - axes.py: 11 axes, each moving ONE gene (topology: one coupled pair).
    54 grid points per family including native.
  - habit.py: one unit = one (perturbed world, seed).
    * Runs "immortal" lives (metabolism 0), so death cannot confound earning.
    * Lives: random twin, frozen twin, oracle twin, 3 cheap carriers, and 4
      structured carriers (those that fit the memory cap).
    * Rate = net earnings per step.
  - score4.py: labels, cell consensus, boundaries, liveness check, verdict.
  - 6 unit tests.
- The prereg, engine, tests and all dev rows were committed and pushed to main
  at 63b8e4b8f BEFORE the first eval row.
- Eval seeds 41004001 and 41004002 were never used before that commit.

Labels.
  Unit:
    - tmax = best trivial-twin rate; gap = oracle - tmax.
    - TRAPPED: the oracle life itself is confined (graph reachability < 5%).
    - INFO_VALUELESS: gap <= .02 or gap <= .2|tmax| (information not worth
      having).
    - margin m = max(.01, .1 x gap).
    - DEAD: no carrier beats tmax by m.
    - STRUCT_PAYS: the best structured carrier also beats the best cheap one
      by m.
    - CHEAP_PAYS: otherwise.
  Cell = 2 seeds, conservative:
    - pays only if both seeds pay;
    - STRUCT only if both are STRUCT;
    - SPLIT if the seeds disagree on paying.

------------------------------------------------------------------------------
2. WHY IT MATTERS
------------------------------------------------------------------------------
- WTP-03 searched 38,000 random worlds. It found that learning-capable worlds are
  rare (0.48% admitted, 13 founder lineages), and every promoted specimen was
  known completion physics.
- The operator's reframing asks what a universe must have before learning is
  physically useful, and what substrate survives there.
- This stage draws the map. Substrate collision inside the islands is the
  next stage, and this map decides where (and whether) it is worth running.

------------------------------------------------------------------------------
3. DESIGN AS EXECUTED
------------------------------------------------------------------------------
Axes and levels (benign -> harsh):
  memory_ratio        cap/cells    .5 .25 .1 .03 .01 .003
  change_timescale    static, drift .3 every 800/200/50/12 steps
  information_cost    read/write/probe/rollout prices x .1 1 10 100
  observation_noise   sd 0 .1 .3 1 3
  irreversibility     door-close prob 0 .1 .3 .6
  credit_delay        0 4 16 64 steps
  topology (cat.)     lattice ring small_world erdos tree scale_free (one-way
                      edges zeroed)
  compute_cost        compute price x .1 1 10 100 1000
  forgetting          rate 0 .02 .1 .3
  active_sensing      random greedy novelty probe_greedy rollout policies
  recurrence_lifetime lifetime x 4 2 1 .5 .25

Grid and run:
  - 12 families x 54 points x 2 seeds = 1,296 units.
  - ubu006, 3 workers, nice 10.
  - 37,148 s (10.3 h). The prereg estimated ~3 h, wrong by 3.4x.
  - 0 crashes.

------------------------------------------------------------------------------
4. DEV STAGE AND THE INSTRUMENT DEFECTS IT CAUGHT (all fixed pre-commit)
------------------------------------------------------------------------------
Dev seeds:
  - 9900001: natives, all families.
  - 9900002: F08/F09, all axes.
  - 9900003: 4 families x 3 axes.

Defects found:
  D1 The liveness check compared event digests only. Cost axes change earnings
     but not events, so they read as falsely "inert" (0/8, 0/10 live).
     Fix: compare (digest, U); exclude no-op levels.
  D2 Every off-lattice topology (and door-close > 0 in F08) ended every life,
     oracle included, in a confinement stop, and the scorer called it ILLEGAL.
     Fixes:
       - confinement is a real way to die, labelled TRAPPED;
       - the topology axis now zeroes one-way edges, which belong to
         irreversibility.
     F08/F09 remain TRAPPED off-lattice because of their directed-edge
     fraction. This is disclosed, not hacked.
  D3 "constant" has a different name in the in-life registry (mapping fix).

Disclosure: two families' full dev maps (F08, F09) were seen before the
prereg's predictions were committed. P2 and P6 had been written before those
rows; P1, P3, P4, P5 and P7 could have been influenced and were not changed.

------------------------------------------------------------------------------
5. RESULTS (exact)
------------------------------------------------------------------------------
Liveness:
  - Every axis is live in 100% of non-no-op units, except forgetting (81/96).
  - No axis is INERT.

Non-native cells (636):
  STRUCT_PAYS 145 | CHEAP_PAYS 75 | DEAD 279 | SPLIT 72 | INFO_VALUELESS 33 |
  TRAPPED 32

Per family (native label; paying cells out of 53 perturbed):
  F00 cp/few_big/fiber           SPLIT        20  (all STRUCT)
  F01 cp/many_small/cell         DEAD          0
  F02 cp/many_small/fiber        DEAD          0
  F03 lowrank/many_small/cell    STRUCT_PAYS  33
  F04 pairwise/binary/masked     STRUCT_PAYS  32
  F05 pairwise/few_big/masked    CHEAP_PAYS   32  (31 CHEAP)
  F06 pairwise/many_small/cell   DEAD          0
  F07 pairwise/many_small/marg.  CHEAP_PAYS   38  (all CHEAP)
  F08 sum/few_big/masked         STRUCT_PAYS  32
  F09 tt/few_big/cell            STRUCT_PAYS  29
  F10 tt/few_big/fiber           SPLIT         3  (27 SPLIT)
  F11 tt/many_small/cell         DEAD          1

Pooled per axis: paying cells out of 12 (S = of which STRUCT).
  memory      .5:7(S3) .25:6(4) .1:5(4) .03:3(1) .01:1(0) .003:0
  change      static:6(4) p800:6(4) p200:2(1) p50:2(1) p12:0
  info price  x.1:7(5) x1:6(4) x10:3(2) x100:0 [7 INFO_VALUELESS]
  noise       0:7(5) .1:7(5) .3:6(4) 1:0 [4 SPLIT] 3:0
  doors       0:5 .1:5 .3:5 .6:5 [TRAPPED rises 0->2->4->5]
  credit      0:6 4:7 16:6 64:6
  topology    lattice:7(6) ring:1 small_world:1 erdos:3 tree:1 [9 TRAPPED]
              scale_free:2
  compute     x.1:7(5) x1:6(4) x10:3(1) x100:1 x1000:0
  forgetting  0:7 .02:7 .1:7 .3:6
  sensing     random:4 greedy:4 novelty:7 probe_greedy:0 [10 INFO_VAL.]
              rollout:0
  lifetime    x4:4 x2:5 x1:6 x.5:7 x.25:5

Replicated boundaries: 27. Examples:
  - change: dies between p800 and p200 in F00, F03 and F09; F08 survives to p50.
  - noise: dies between sd .3 and 1.0 in F00, F03, F08 and F09.
  - memory, family-specific: F05 .25->.1, F04 .1->.03, F03 and F08 .03->.01.
  - info price: x1->x10 in F08 and F09; x10->x100 in F04 and F07.
  - compute: x1->x10 in F03 and F09; x10->x100 in F08; x100->x1000 in F07.

Carrier-class changes (replicated) along an axis: 2 of 132.
  - F04 change: struct -> cheap.
  - F05 forgetting: cheap -> struct at .3.

Predictions (prereg s8):
  P1 PAYS non-decreasing in lifetime ........ REFUTED (5,7,6,5,4 for x.25..x4)
  P2 info x100 kills >= half the x1 payers .. HIT (6 of 6)
  P3 no STRUCT at memory .003 ............... HIT (no PAYS at all)
  P4 fast drift hurts STRUCT more ........... HIT on the letter (4->0 vs 2->0),
                                              MECHANISM REFUTED: cheap dies too
  P5 STRUCT wins < 40% of paying cells ...... REFUTED (145/220 = 66%,
                                              concentrated in 5 families)
  P6 no PAYS at noise sd 3 .................. HIT
  P7 verdict odds ........................... ISLANDS_MAPPED was the .35 outcome

------------------------------------------------------------------------------
6. INCIDENTS
------------------------------------------------------------------------------
- Host move M2 -> ubu006 the day before. Results are bitwise platform-bound,
  and nothing here is compared bit-for-bit with WTP-03's M2 rows.
- The run took 3.4x the estimate. The envelope held: 3 workers, RAM never near
  the 3 GB floor.

------------------------------------------------------------------------------
7. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------
DOES (2 seeds per cell; WTP-03 calibrated economy held fixed):
  - Habitable worlds in this grammar are inherited islands. Single-axis moves
    shrink them but do not create them.
  - Learning dies, in every family, under any one of:
      noise sd >= 1; drift every 12 steps; info price x100;
      compute price x1000; memory .003 of cells.
    It survives credit delay up to 64 and forgetting up to .3.
  - At high prices, information becomes worthless (the oracle cannot profit)
    before learning becomes impossible.
  - Cheap carriers explain all of the habitability of F05 and F07, and none of
    it in F03, F04, F08 and F09.

DOES NOT:
  - Show anything beyond known physics. No N6 (tuned same-class batch fit) was
    run. The structured-winner families are WTP-03's completion positive
    control.
  - Test interactions. A dead family might revive under two simultaneous
    moves.
  - Establish the family-specific memory edge as a description-length law.
    That is suggested only.

Known weaknesses (please attack):
  W1 The active_sensing baseline is not policy-matched. The random twin always
     walks for free, while probe_greedy and rollout pay to sense. Those cells
     therefore read INFO_VALUELESS (e.g. F08: random 1.30 vs oracle .94).
     The axis measures paid sensing vs a free walk.
  W2 Off-lattice topology is confounded with each family's directed-edge
     fraction (F08/F09 TRAPPED).
  W3 The independence rule is genome-level. Two "families" may share a
     mechanism, which inflates the pooled shares (P5's 66% mostly counts
     families).
  W4 Lifetime is non-monotone because of SPLITs and TRAPs at long lives.
     Undiscriminated; the life-ending degeneracy stop may be the cause.
  W5 Two seeds give 11% SPLIT. Edges are bracketed to one level step, not
     located.

------------------------------------------------------------------------------
8. DECISION / RECOMMENDATION (operator's call; seat's lean)
------------------------------------------------------------------------------
Options:
  (a) Two-axis revival probe on dead families F01, F06 and F11 (e.g. memory x
      change, memory x price). Small, preregistered. It asks whether
      habitability can be CREATED, or only inherited. Cheap: ~150-300 units.
  (b) Narrow substrate collision:
      - only in the structured islands F03, F04, F08 and F09;
      - with N6 in the ladder;
      - at the replicated edges, where the structured margin is thinnest.
      This asks whether a structured carrier ever beats known batch physics
      near an edge.
  (c) Move to RESERVE: non-tensor-native grammars. Every family here is
      tensor-native and the structured winners are completion families, so
      the carrier answer cannot differ until the matter differs.
  (d) Stop the WTP line.

Seat's lean: (a) then (c). (a) is cheap, and it decides whether "islands are
inherited" is a law or an artefact of one-axis moves. WTP-04 gives little
reason to expect (b) to find a carrier change, so (b) should wait until (a) or
(c) gives it a reason.

------------------------------------------------------------------------------
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------------------------
Q1 Is "habitability is inherited" just a restatement of the WTP-03 admission
   filter (worlds were selected near a calibrated economy), rather than a fact
   about physics?
Q2 Do immortal twins measure the right thing? A world where learning "pays"
   but every organism would starve is called habitable here.
Q3 With 2 seeds and the conservative AND rule, are the 27 boundaries real
   edges, or the places where seed noise first crosses the margin?
Q4 Is holding the WTP-03 calibrated economy fixed a bias? Each native world
   was tuned to be barely feasible, so many outward moves are harsh by
   construction.
Q5 Should the 4 dead-at-native families have been in the map at all, given
   that their representatives were admitted by WTP-03 as learnable worlds?

------------------------------------------------------------------------------
10. ARTIFACTS (origin/main)
------------------------------------------------------------------------------
  ensorain/PREREG_WTP04.md            prereg (precommit 63b8e4b8f9c1)
  ensorain/wtp4/                      engine + tests (63b8e4b8f)
  ensorain/runs/wtp04/eval.jsonl      1,296 rows (87965d589)
  ensorain/runs/wtp04/eval_score.json full score: cells, maps, boundaries
  ensorain/runs/wtp04/dev_axes*.jsonl dev rows (never pooled with eval)
  ensorain/RESULTS_WTP04_MAP.md       seat report
  ensorain/requirements.txt           pinned runtime (Python 3.14.4, numpy
                                      2.3.5, scipy 1.16.3)
  Reproduce: python -m ensorain.wtp4.campaign4 eval --seeds 41004001,41004002
             python -m ensorain.wtp4.score4 eval

+==============================================================================+
| END. "Not worth continuing" is a first-class answer: if the reviewer judges  |
| that WTP-04 only re-describes the WTP-03 admission filter, say so, and the   |
| WTP line should stop or go straight to new grammars (option c/d).            |
+==============================================================================+
