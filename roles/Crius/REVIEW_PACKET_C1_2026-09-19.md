CRIUS -- CAMPAIGN 1 REVIEW PACKET -- RELAY (PROCEDURE WORLD)
2026-09-19  instance m2-8d43bbf9  branch crius/base-role-adopt-2026-09-18
Ruling: roles/Crius/prompts/2026-09-19_c1_ruling/ (ba02a9e7c). Prereg:
crius/DESIGN_C1.md (a9928654b, before code). Freeze 97af44f88:
config_hash 32dfb243be9fdec9, world 7c53db874324b532, generator
624728b00fdd3f2f. Gate A-H: crius/runs/gate_c1/GATE.md, ALL PASS.
================================================================================

0. VERDICT

The gate holds: RELAY contains an independently useful artifact channel.
The hand-written procedure control transplants competence through
executable blocks alone (ARTIFACT_TRANSPLANT 18/18 vs CODE_ONLY 3-5/18
solved on the stage-D remainder; ablation returns it to CODE_ONLY), and
on the sealed qualification streams it passes every criterion of the
charter s13 checklist 3/3, including "executable components reused",
which no Player had passed before. Selection under competence-first
fitness, with rotating streams and three variation regimes (mutation,
seeded mutation, seeded mutation + segment splice), found NO persistent
machinery: nine runs, 64,872 candidates, zero acquired-state effect in
any qualified candidate (ACCUMULATED == FRESH to the last digit). What
it found instead is a third solver shape: stride-counter pseudo-random
action generators that out-walk systematic enumeration on chain tasks
(27-32/50 vs the seed's 25/50 on sealed streams) by luck that the
budgets make available. Predictions: Q1, Q2, Q3 (state clause), Q4 held;
Q3 (count clause) and Q5 lost. Two degrees of freedom are named below;
one is cheap to fix (budgets), the other is the same wall as C0 (the
operator cannot reach store-observe-lookup-replay). Recommendation at
the end.

1. WHAT CHANGED SINCE C0 (all under crius/, commit 97af44f88)

  world_c1.py / tasks_c1.py  RELAY: Z_8^4 objects; 12 primitives
      INC/DEC/SWAP(pos) behind a per-stream permutation of ids; a hidden
      per-stream library of 3 templates (2-3 (kind, offset) steps applied
      relative to an ARGUMENT); tasks are chains of 1-4 templates with
      fresh arguments; sealed namespaces search / qual / gate.
  evaluate.py   C1_FITNESS = solved + 0.5 * (1 - charged/max): one solved
      task dominates any cost term; unsolved tasks charged full budget.
  vm.py / env.py  FAIL sentinel for every store failure (poisons
      arithmetic, never stored, never acted on); ACT accepts only
      0..12; INPUT status; per-invocation log (entry registers, emitted
      actions); TaskResult.success_in_block; per-task store-op trace.
  search.py     one rotating stream per iteration (parents re-evaluated
      on it: common random numbers within the comparison); arm
      "recombination" = segment splice from a second parent on 30 percent
      of children (Apollo's dispatch_merge record checked; generic
      analogue, no store knowledge).
  baselines_c1.py  RANDOM, ENUMERATE, ENUMERATE_VM (search seed), QUIT,
      TABLE_MEMO, PROCEDURE_REUSE (blocks only: calibration block +
      argument-taking template blocks; plans in the head; executes by
      BLK_INVOKE), PROCEDURE_NOCAL (permutation ignored).
  gate_c1.py    witnesses A-H; fixtures/ (three C0 fossils);
      tests/test_c1_integrity.py (7 tests; suite 18 passed).

2. GATE (crius/runs/gate_c1/GATE.md; gate streams 301-303; PASS x8)

  A  QUIT 20.3/17.3/20.3 < ENUMERATE 31.4/26.3/28.4 (fitness)
  B  every unsolved ENUMERATE task charged its budget (19/24/22 tasks)
  C  33 x BLK_NEW then ACT: no action, status 1 then 2; FAIL poisons
     arithmetic; out-of-range values are invalid actions (tests)
  D  TABLE_MEMO replays 0 / 0 / 0; PROCEDURE solved 30/30/30 chains
     inside invoked blocks, NOCAL 0/0/0
  E  PROCEDURE ACC 50/49/50 vs FRESH 31/25/28; reuse_gain C-E 23081 /
     23912 / 22999 (98 percent of FRESH charged cost)
  F  ARTIFACT_TRANSPLANT 18/18/18 solved, mean cost 20.8/28.5/~30 vs
     CODE_ONLY 3/5/5, 957/924/884 (code identical)
  G  ARTIFACT_ABLATION_ALL == CODE_ONLY (957.2 / 923.7 / 884.4)
  H  transplanted blocks unchanged; 2/3/3 template blocks invoked with
     >= 3 distinct arguments giving >= 3 distinct action sequences;
     TABLE_MEMO FULL == CODE_ONLY (3/6/5)
  Control fixes made while the gate failed on the CONTROL (dated,
  DESIGN_C1 s10): live calibration map; two-witness rule for recording
  a template; depth-1 probe before planning. World, generator, metric,
  operators untouched.

3. QUALIFICATION REFERENCE (sealed qual streams 201-203, means; fit =
   C1_FITNESS; A=ACCUMULATED F=FRESH)

  player              fitA   fitF   sucA  sucF  interA  interF  reuse_gain
  PROCEDURE_REUSE_C1  47.12  26.96  46.7  26.7    8916   38056    29005.3
  TABLE_MEMO_C1       26.96  26.96  26.7  26.7   37456   37456      -17.9
  ENUMERATE_VM_C1     25.29  25.29  25.0  25.0   37856   37856        0.0
  RANDOM_C1           10.16  10.16  10.0  10.0   62546   62546        0.0
  s13 checklist (0-7, seeds passing of 3): PROCEDURE_REUSE_C1
  3 3 3 3 3 3 3 3; every other control 3 0 0 0 0 0 0 0.
  Families (ACCUMULATED, solved/n over 3 streams): PROCEDURE chain2
  36/36, chain3 27/30, chain_repeat3 11/12, chain4 6/12, singles 60/60.
  ENUMERATE_VM chain2 ~14/36, chain3 ~4/30, chain4 0/12.

4. SEARCH (9 runs x 7208 candidates; crius/runs/CAMPAIGN_SUMMARY.md)

  run           useSt keepS sol40 | qual top1 (final-population rank)
                                  | fitA   fitF   sucA  interA reuse blk invk
  random_s1      5207  1051     0 |  0.11   0.11   0.0       0   0.0  0    0
  random_s2      5719  1293     0 |  8.49   8.49   8.3   62843   0.0  0    0
  random_s3      4719   649     0 |  0.11   0.11   0.0       0   0.0  0    0
  seeded_s1      5566  1088   216 | 30.99  30.99  30.7   32168   0.0  0    0
  seeded_s2      4486   482   151 | 27.63  27.63  27.3   35978   0.0  0    0
  seeded_s3      6481  3590    99 | 30.98  30.98  30.7   33442   0.0  0    0
  recomb_s1      4756   906   190 | 27.98  27.98  27.7   32712   0.0  0    0
  recomb_s2      5511  2786   247 | 31.99  31.99  31.7   30875   0.0  0    0
  recomb_s3      6444   549   196 | 30.33  30.33  30.0   30776   0.0  0    0
  useSt/keepS: candidates that executed a store op / kept bytes or
  invoked a block on their stream; sol40: candidates solving >= 40/50 on
  their (rotating) stream. "best ever" fitnesses of 45-49 are STREAM LUCK
  (short, cancelling templates make chains brute-forceable on some
  streams); the fair rank is the final population, re-evaluated on one
  common stream, and its top candidates are what the qual columns show.
  Ancestors and contemporaries (3 + 3 per run) and the best-ever
  candidates were qualified too: all fitA == fitF, blk 0, invk 0.
  s13 checklist for every searched candidate: 3 0 0 0 0 0 0 0.

5. WHAT SEARCH BUILT (OBSERVATION)

  S1  STRIDE-COUNTER WALKERS (seeded and recombination arms, 6/6 runs).
      Example seeded_s1 top1 d467f76689979ce2 (56 instructions, ancestry
      depth 186): a counter R0 starting at -8 with stride 17 (CONST R5,
      17; ADD R0, R0, R5), actions ACT (R0 mod 12), ACT (R0/12 mod 12),
      ACT R2 where R2 = num_ops (RESET), looping. A pseudo-random action
      stream with periodic resets. On sealed streams: singles 55/60,
      chain2 16/36, chain3 14/30, chain_repeat3 5/12, chain4 2/12 --
      more chains than systematic enumeration (which never leaves depth
      3) because a walk with 800-1200 interactions reaches 4-6-move
      targets by luck. No INPUT of the target in the loop, no store
      read that affects control flow, ACC == FRESH exactly.
  S2  RANDOM ARM: nothing (0-8/50); one run produced a random-walk
      script below RANDOM_C1 (8.3 vs 10.0).
  S3  RECOMBINATION did not differ from mutation-only in outcome (27.7-
      31.7 vs 27.3-30.7 solved); splice segments appear in the winning
      ancestries but carry action-generation code, never store code.
  S4  STORE USE IS COMMON AND NEVER LOAD-BEARING: 62-90 percent of
      candidates executed store instructions (usesSt), 7-50 percent kept
      bytes or invoked a block, and among the 90 qualified candidates
      (10 per run) none had any ACC/FRESH difference. The store is used
      as a source of integers and side effects, as in C0.

6. PREDICTIONS (DESIGN_C1 s8)

  Q1 HELD: the gate passed on the first world instance (after control
     fixes, not world fixes).
  Q2 HELD: random arm never reached 20/50 (max 8.3 on sealed streams).
  Q3 HALF: seeded arm shows no acquired-state effect (HELD) but solves
     27-31/50, not 20-24 (LOST): walkers, not enumerators.
  Q4 HELD (the one this campaign wanted to lose): recombination arm, no
     acquired-state effect within 300 iterations.
  Q5 LOST: searched candidates solve 5-16 chain tasks per sealed stream
     (chain2 16/36, chain3 14/30 for seeded_s1), not <= 2: luck is
     abundant under the frozen budgets.
  Ledger rows added to roles/Crius/calibration/LEDGER.md.

7. INTERPRETATION

  - The artifact axis is now testable and the positive control uses it:
    F/G/H are the first receipts in this lane where competence lives in
    executable blocks with an argument port and nowhere else.
  - The fitness did its job: no quitter appeared in nine runs (QUIT-shaped
    candidates score 17-20 and lose to walkers at 27-32).
  - The rotating streams did theirs: no candidate is worse on sealed
    streams than on its search streams beyond stream luck; F2/F3 shapes
    from C0 did not recur.
  - The search operator is the wall, as in C0 and as Q4 predicted. The
    reuse route is worth +20 tasks (47 vs 27) and is never approached:
    reaching it requires calibrate + record-as-procedure + plan + invoke,
    each useless without the others. Segment splice does not bridge it
    because no population member carries any of the parts.
  - A second, cheaper wall was exposed by Q5: with chain budgets of
    800-1600 a random walk solves a third of the chains, so selection
    climbs the walk gradient (real, smooth) instead of the reuse gradient
    (absent until complete).

8. DEGREES OF FREEDOM NAMED

  D1 BUDGET CALIBRATION (cheap). Set chain budgets so that RANDOM_C1's
     chain solve rate is < 5 percent while PROCEDURE_REUSE_C1's route
     (mean 33-167 interactions per chain) stays inside them: e.g. chain2
     250, chain3 400, chain4 600. Then walkers lose their gradient.
  D2 OPERATOR / SUBSTRATE (the real wall). Either the substrate makes
     "keep this and apply it later with an argument" a 1-2 edit change
     (a typed-block substrate; CRIUS-25, XL) or the population is seeded
     with the PARTS of the reuse mechanism as separate lineages (a
     calibrator that only probes, a recorder that only records, an
     invoker that only invokes) so recombination has something to
     combine -- that is the Apollo dispatch_merge shape, and it needs a
     decision because it puts hand-written mechanism into the population.
  D3 (observed, not acted on) block ids are values: a legitimate clock.
     CRIUS-28 (XL) records the opaque-handle option.

9. RECOMMENDATION

  Do not run more of C1 as frozen. Run C1b = C1 with D1 only (budgets
  recalibrated, everything else frozen; a config-hash change, gate
  re-run, three arms x three seeds, ~1 hour of M2): it answers whether
  the walker gradient was masking anything. If C1b is still flat, the
  operator/substrate decision (D2) is the next campaign, and it is the
  operator's call, not mine.

10. WHAT WOULD FALSIFY / STOP

  - A C1b candidate with reuse_gain > 5 percent of FRESH charged cost and
    competence kept, on sealed streams, falsifies D2 as "the" wall.
  - If C1b's random arm still finds walkers at chain budgets where
    RANDOM_C1 solves < 5 percent, the budget calibration is wrong, not
    the thesis.
  - Stop the lane if the operator judges D2 already answered by Apollo.

11. CONFLICTS OF INTEREST AND PROVENANCE

  - I wrote world, generator, metric, controls and operators; the
    positive control encodes the world's primitive semantics (planning
    in the head) and is a control only.
  - Control fixes (3) and the qualification selection fix (rank within
    the final population under rotation) were made after seeing results;
    both are dated (DESIGN_C1 s10; qualify.py).
  - The C0 packet's F1 mechanism is CORRECTED here: growing block ids
    exceeding a loop bound, not a failure value aliasing RESET
    (tests/test_c1_integrity.py). The integrity change stands on ruling
    5 and retired the C0 action-script fossil (wrap-around immediates).
  - Grades: MEASURED s2-s6; INFERRED s7-s9.

12. RECEIPTS

  crius/runs/gate_c1/            GATE.json, GATE.md, control batteries
  crius/runs/baselines_c1/       7 controls x gate streams 301-303
  crius/runs/search_c1_<arm>_s<k>/  RUN_META, candidates.jsonl.gz (7208
      CandidateReceipts with stream seeds, store traces, ancestry),
      iterations.jsonl, best.json, qualify_qual/ (SUMMARY.json + battery
      receipts incl. invocation logs), REPORT.md
  crius/runs/CAMPAIGN_SUMMARY.md
  crius/fixtures/c0_failure_families.json
================================================================================
