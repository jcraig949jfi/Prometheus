CRIUS -- CAMPAIGN 0 REVIEW PACKET -- ADAPTIVE WORKSPACE SANDBOX
2026-09-19  instance m2-8d43bbf9  branch crius/base-role-adopt-2026-09-18
Charter: roles/Crius/prompts/2026-09-19_charter/CHARTER_CAMPAIGN_0.md
(sha256 5c58c97d...). Design + preregistration: crius/DESIGN_C0.md
(committed before code, de2ea2fb2). Freeze: 68cc85ff9, config_hash
65fd4678cbcdd9c5, world 57065ca240cee53d, partitions ece4bd004beb4710.
================================================================================

0. VERDICT IN ONE PARAGRAPH

The sandbox works: its positive control acquires reusable state and every
control dissociates the way it should. The search did not discover
learning-to-learn. Under the preregistered fitness function selection
climbed toward NOT LEARNING: a ratio of competence gained to budget spent
rewards abstention, and after 300 iterations the best program solves 5.5
of 50 tasks. Under a post-hoc variant that charges abstention, selection
found better brute-force ENUMERATION ORDERS and hard-coded ACTION SCRIPTS
that memorise the search partition in code; none acquired state, and all
were worse than the seed on held-out tasks. Three degrees of freedom are
named (metric, search operator, world), each with the receipt that shows
it. Recommendation: do not run more of Campaign 0; run Campaign 1 with the
metric and world changes below, or stop the lane if a search-operator
result from Apollo already answers the middle one.

1. WHAT WAS BUILT (architecture, all under crius/ at the repository root)

  world.py      6 hidden ops on Z_16^4: 3 translations, 2 context-
                conditional translations (parity of x[0]), 1 rotation
  tasks.py      TaskSpec, frozen 3-way composition partitions (search
                C/D, search E, qualification), lifetimes of 50 tasks in
                stages A10 B10 C12 D10 E8; suites search / heldout_v1
  workspace.py  cells, streams, records, links, alloc; costed; 4096-byte
                capacity; snapshot/restore/scramble
  artifacts.py  ExecutableBlock (instructions + 8 state slots) in a
                32-block store; create/append/patch/copy/compose/delete/
                invoke; events, invocation counts, dependency edges
  vm.py         8-register bytecode VM, 48 opcodes (arith, vector, branch,
                INPUT, ACT/ACTI, WS_*, BLK_*, BLK_REC_BEGIN/END);
                assembler; ENUMERATE seed program
  env.py        TaskRun: interactions vs compute vs store units, budgets,
                success + 200-step grace, replay trajectory
  evaluate.py   frozen metric; conditions A-D over a lifetime; E-J from a
                stage-D snapshot; full_battery
  baselines.py  RANDOM HEURISTIC ENUMERATE ENUMERATE_VM CACHE_REUSE ADAPTIVE
  search.py     (8+24) mutation-and-selection, 7 mutation operators,
                CandidateReceipt ancestry, arms random / seeded
  qualify.py    heldout_v1 battery for top-3, 3 contemporaries, 3
                ancestors, 6 baselines x 3 qualification seeds
  report.py     ASCII tables + mechanical s13 checklist per run
  campaign_summary.py  one row per run + store-usage census
  tests/test_sandbox.py  11 tests (charter s17 list + cheat control +
                bounds); 11 passed on the final tree
  Commands: python -m crius.baselines --config crius/configs/c0.json
            python -m crius.search --config ... --iterations 300 --seed 1
                                   --arm seeded
            python -m crius.qualify --run RUN_ID --suite heldout_v1
            python -m crius.report --run RUN_ID
  Not built: any integration, gating, orchestration, LLM-in-loop, JIT.

2. FROZEN METRIC (drives search; every component in every receipt)

  gain_t = max(0, perf(best object) - perf(start)), perf = 1 - hamming/4
  C0_EFFICIENCY = sum gain_t / (1 + sum inter_t/budget_t
                  + sum (steps_t + store_t)/20000 + mean state_t/4096)
  adaptation_cost_t = interactions_t + 0.01 * (steps_t + store_t)
  reuse_gain_t = cost_t(FRESH) - cost_t(ACCUMULATED), same task, exact
  c0x (EXPLORATORY, post hoc): unsolved task charged 1.0 experience.

3. ASSAY VALIDATION (search suite, seeds 101/102; crius/runs/baselines_c0)

  player        effA   effF   succA interA interF reuse_gain blocks
  RANDOM        0.193  0.193    4   13311  13311       0.0     0
  HEURISTIC     2.844  2.844   47    1482   1482       0.0     0
  ENUMERATE     1.926  1.926   50    4139   4139       0.0     0
  ENUMERATE_VM  1.773  1.773   50    4424   4424       0.0     0
  CACHE_REUSE   5.784  1.859   50     114   4139    3987.9     0
  ADAPTIVE      5.078  1.839   50     114   4139    3906.2    27
  (seed 101; seed 102: CACHE_REUSE 5.507/1.561, reuse_gain 3673.8)
  Controls on CACHE_REUSE seed 101: SCRAMBLED eff 2.080; RESET 4.700,
  and the task right after each reset costs 41.6 / 259.8 / 45.7 against
  ENUMERATE's 40.2 / 256.0 / 44.3 on the same tasks, cheap again one task
  later (3.0 vs 52.3). Stage-D remainder: FULL_TRANSPLANT 5.50 =
  ACCUMULATED 5.50; ARTIFACT_TRANSPLANT 19.40 = CODE_ONLY 19.40 =
  COMPUTE_MATCHED = STORAGE_MATCHED 19.40. s17 "positive control
  benefits": met, on the DATA axis.
  ARTIFACT axis: no positive control exists in this world. ADAPTIVE's
  blocks are a net cost at depth <= 3 (ablating all of them lowers the
  remainder 10.01 -> 7.81, seed 101) and on held-out RESET beats
  ACCUMULATED for it (2.64 vs 1.97). Checklist calibration on held-out:
  CACHE_REUSE passes 0,1,2,4,7 on 3/3 seeds, 3 and 5 on 2/3, 6 on 0/3
  (no blocks); ENUMERATE_VM, HEURISTIC, RANDOM pass nothing but 0.

4. SEARCH RESULTS (12 runs x 7208 candidates; crius/runs/CAMPAIGN_SUMMARY.md)

  run              useSt keepS sol40   best succ intr | qEffA qEffF qSuc qReuse
  (X = EXPLORATORY c0x; columns defined below)
  c0_rnd_s1         2727   448     0 2.5399 17.0  211 | 2.839 2.839 16.3    0.0
  c0_rnd_s2         3208   519     0 2.2598  7.5   96 | 2.021 2.021  6.7    0.0
  c0_rnd_s3         3664   580     0 2.0424  3.0   50 | 2.025 2.025  4.0    0.0
  c0_seed_s1        6721   389    19 4.3403  5.5  148 | 3.881 2.019  2.0  186.5
  c0_seed_s2        1776   274    38 2.5194 20.0  246 | 3.021 3.021 20.0    0.0
  c0_seed_s3        1886   274    14 2.5312 21.0  306 | 2.949 2.949 21.7    0.0
  c0x_rnd_s1 X      7206  7081     0 0.9568 38.0  850 | 0.591 0.584 25.0   20.6
  c0x_rnd_s2 X      7200  5671     0 0.7686 34.0  504 | 0.506 0.504 22.7  -11.9
  c0x_rnd_s3 X      7203  3955     0 0.9601 37.5  738 | 0.558 0.615 23.3  -57.1
  c0x_seed_s1 X     3710   508  3447 2.0758 50.0 2290 | 1.347 1.347 45.0    0.0
  c0x_seed_s2 X     4619  2285  3420 1.9463 50.0 2746 | 1.389 1.389 45.0    0.0
  c0x_seed_s3 X     2359   180  3600 1.9581 50.0 2470 | 1.499 1.499 48.0    0.0
  usesSt = candidates that executed any store op; keepSt = kept bytes or
  invoked a block; solv40 = candidates solving >= 40/50 on search seeds;
  succ/inter = best's mean successes/interactions on search seeds; q_* =
  best on heldout_v1 (3 seeds). Reference on heldout_v1: ENUMERATE_VM
  effA 1.601 (c0) / 1.506 (c0x), 48/50; CACHE_REUSE 2.965 / 1.575 FRESH,
  50/50, reuse_gain 5315.7.
  s13 checklist (0-7), searched bests: c0 random s1-s3, c0 seeded s2-s3,
  c0x seeded s1-s3: pass only guard 0 (nothing else). c0 seeded s1: 0/8.
  c0x random s1-s3: 0-1 seeds on any criterion. No searched candidate
  satisfies criteria 1-7 on any seed.

5. THREE FAILURE SHAPES (OBSERVATION; each from named receipts)

  F1  ABSTENTION UNDER THE RATIO METRIC (c0, all 6 runs). Within 3
      iterations of the seed a crippled enumerator that solves only
      depth-1 tasks scored 2.50 > 1.62. By iteration 300 the best (seeded
      s1, cdc90b7185eeeeed) solves 5.5/50 with 148 interactions, 4.34.
      On held-out it solves 2/50 ACCUMULATED but 16/50 FRESH, eff 3.88
      vs 2.02: its only "acquired state" is a block store it fills with
      32 empty blocks (BLK_NEW / BLK_COMPOSE of empty blocks, 34 creates,
      0 invocations, 0 workspace bytes); once full, BLK_NEW returns -1,
      which as an action is RESET, and the program stops probing. The
      store is used as a clock that says "stop trying". reuse_gain +186.5
      with competence collapsing. This passed checklist criterion 1 until
      guard 0 (competence kept) was added the same day; criteria 3-7
      failed it on their own (FULL transplant remainder 8.67 vs CODE_ONLY
      0.69). Receipts: crius/runs/search_c0_seeded_s1/REPORT.md, best.json.
  F2  BETTER ENUMERATION ORDERS, NO STATE (c0x seeded, 3/3 runs). Bests
      solve 50/50 on search seeds with 2290-2746 interactions against
      the seed's 4424/4335, using 0 store ops. Listing (s1,
      1bec543c80abe8aa): the depth-2 loop drops the MOD and acts on c/k
      directly; the depth-3 loop increments by 2 (stride-2 enumeration).
      On heldout_v1 they are WORSE than the seed: 45-48/50, effA
      1.347-1.499 vs 1.506; the skipped sequences were ones the search
      partition never needed. reuse_gain 0.0 exactly; RESET = SCRAMBLED
      = ACCUMULATED. Receipts: crius/runs/search_c0x_seeded_s*/REPORT.md.
  F3  HARD-CODED ACTION SCRIPTS (c0x random, 3/3 runs). Bests are 50-58
      instruction sequences of ACT/ACTI with one loop, no INPUT
      instruction at all, and a stream that is written (WS_APPEND, 50
      bytes) and read back only as a length (WS_SLEN). 34-38/50 on search
      seeds (C 67-75 percent, D 50 percent)
      drops to 22.7-25.0/50 on held-out: primitives 60/60, reversed pairs
      9/18, held-out pairs 0/18, held-out triples 2/15. reuse_gain +20.6,
      -11.9, -57.1 (noise around 0). The program memorised the search
      partition's compositions in its code. Receipts:
      crius/runs/search_c0x_random_s*/REPORT.md.
  Census: in c0, 0.2-0.5 percent of seeded-arm candidates (14-38 of
  7208) and 0 of 21624 random-arm candidates solved >= 40/50; in c0x
  seeded, 47-50 percent did (3420-3600). Store use is common (25-100
  percent of candidates) and load-bearing nowhere among the 84 qualified
  candidates (7 per run): none both kept state and lowered later cost
  while keeping competence. The census cannot test the unqualified rest
  (no FRESH run for them); CRIUS-15 would.

6. PREDICTIONS SCORED (DESIGN_C0.md s9; ledger rows in calibration/)

  P1 LOST in part: ENUMERATE solved 3/6 held-out depth-4 tasks (budget
     1500 covers depth 1-3 plus ~180 depth-4 sequences; targets have
     shorter equivalents); late/early is 0.48-1.97 on n=10, noise.
  P2 LOST in form, HELD in substance: within-depth late/early is flat
     (acquisition completes in A/B); reuse_gain C-E +3900; RESET clause
     held exactly (numbers in s3).
  P3 HALF: ADAPTIVE 6/6 depth-4, ENUMERATE 3/6 not 0.
  P4 HELD: no random-arm Player with late/early < 0.8 at depth 3; the
     random arm produced no solver at all under c0.
  P5 HELD, and stronger than written: seeded descendants exceed the seed
     by halting earlier; reuse_gain 0 (s2, s3); the one state effect
     (s1) is abstention keyed on store fullness, not competence.

7. INTERPRETATION (each sentence names what it rests on)

  - The ratio metric is not a fitness function for learning-to-learn: its
    optimum in this world is minimal effort with partial credit (F1
    numbers; CAMPAIGN_SUMMARY row c0_seeded_s1). Charging abstention (c0x)
    removes the quitter optimum but leaves search where C1 predicted:
    improving the solver's code, not acquiring state (F2, F3).
  - Point mutation from ENUMERATE_VM reaches stride and order changes
    (1-3 edits) and never reaches store-observe-lookup-branch-replay
    (at least ~10 coordinated edits with no reward until complete).
    Evidence: 0 of 21624 c0x-seeded candidates with usesSt > 0 improved
    on the seed by keeping state (census + checklist).
  - In this world nothing procedural is worth keeping: once op effects
    are data, tasks are solved by table lookup, and executable blocks are
    a net cost even for the hand-written ADAPTIVE (s3). The artifact axis
    of the assay is untested by any positive control. That is a property
    of the world, not of the search.
  - The held-out partition did its job three times (F1 competence
    collapse only visible ACC vs FRESH; F2 and F3 both worse on held-out).

8. THE MISSING DEGREES OF FREEDOM (charter s18 step 10)

  D1 METRIC. Unsolved tasks must cost their budget, and gained competence
     must be non-decreasing under accumulation, or abstention wins. c0x
     shows the first half; guard 0 in report.py is the second half as an
     instrument, not yet as fitness.
  D2 SEARCH OPERATOR. The reuse mechanism is a multi-edit structure with
     no partial reward. Either the substrate makes "store now, look up
     later" a one- or two-edit change (typed blocks, or a WS_FIND-keyed
     replay primitive), or the operator is recombination over a
     population that already contains observers and replayers (Apollo's
     2026-06-16 crossover result predicts this). Both are testable
     without changing the world.
  D3 WORLD. The expensive thing to acquire must be a PROCEDURE, not a
     datum: e.g. each task hides a per-task parameter that a fixed
     multi-step probing protocol reveals; the protocol (not its result)
     is what a block can carry, and only then can ARTIFACT_TRANSPLANT
     beat CODE_ONLY for any Player.

9. PROPOSED CAMPAIGN 1 (preregister in crius/DESIGN_C1.md before code)

  World: same ops plus a per-task hidden scale s in {1,2,3} applied to
    every translation; s is discoverable by a 2-probe protocol (apply op0
    twice, read the delta). A block that performs the protocol and writes
    s is the reusable procedure; a table alone cannot generalise across s.
  Metric: cost-based, not ratio: sum over tasks of (interactions_t if
    solved else budget_t) + 0.01 * compute, minimised; competence guard
    as a hard constraint on qualification, never as fitness.
  Search: two arms held constant (random, seeded) plus one recombination
    arm; population 8+24, 300 iterations, 3 seeds, as now; the
    single-mutation landscape from the seed enumerated once (CRIUS-16).
  Predictions to write: (a) under the cost metric the seed is not beaten
    by quitters; (b) the recombination arm produces at least one
    candidate with reuse_gain > 5 percent of FRESH cost on held-out and
    competence kept, the point-mutation arms none; (c) ARTIFACT_TRANSPLANT
    < CODE_ONLY for the hand-written protocol control by > 20 percent.
  Cost: one day of build, under two hours of M2 compute.

10. WHAT WOULD FALSIFY THIS PACKET / WHAT TO STOP

  - If a re-run of any c0x seeded run with a recombination operator
    yields a candidate with reuse_gain > 5 percent and competence kept on
    heldout_v1, D2 is the whole story and D3 is unnecessary.
  - If the hand-written protocol control in Campaign 1 shows no
    ARTIFACT_TRANSPLANT advantage, the artifact axis remains untestable
    in this family of worlds and the lane should stop building worlds.
  - Stop now if the program already holds a measured answer to D2 from
    Apollo's crossover work; then only D1 + D3 are worth a campaign.
  - Not worth continuing: more iterations of Campaign 0 under either
    config (12 runs, all three shapes stable across seeds).

11. CONFLICTS OF INTEREST AND PROVENANCE GRADES

  - I wrote the world, the metric, the baselines and the search; the
    positive controls encode domain knowledge (context bit, delta
    keying) and are controls only, never in the searched set.
  - c0x, ADAPTIVE macro planning and checklist guard 0 were written
    after seeing results; each is dated in DESIGN_C0.md s10 / report.py.
  - All numbers are from committed receipts, deterministic in (spec,
    seed, suite, condition); replay hashes are in every receipt. Grade:
    MEASURED for everything in s3-s6; INFERRED for s7-s9.
  - Python baselines' store units are not budget-charged (VM Players'
    are); their compute is approximate, declared in DESIGN_C0.md s6.

12. RECEIPT LOCATIONS (all under the repository)

  crius/runs/baselines_c0/          6 players x 2 seeds, full battery
  crius/runs/baselines_c0x/         same under the exploratory config
  crius/runs/search_<cfg>_<arm>_s<k>/  RUN_META.json, candidates.jsonl.gz
      (7208 CandidateReceipts with ancestry), iterations.jsonl, best.json
      (program, listing, receipt), qualify_heldout_v1/ (SUMMARY.json +
      one battery receipt .json.gz per player x seed), REPORT.md
  crius/runs/CAMPAIGN_SUMMARY.md    the table in s4
  crius/DESIGN_C0.md                design, freeze, predictions, addenda
  roles/Crius/calibration/LEDGER.md lost predictions
================================================================================
