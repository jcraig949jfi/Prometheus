# WTP-04 Habitable Islands -- map stage -- results

Seat: Ensorain[ubu006-4b001784]. Date: 2026-10-07.

- Prereg and engine: ensorain/PREREG_WTP04.md + ensorain/wtp4/, precommit 63b8e4b8f, pushed to main before any
  eval row.
- Rows: ensorain/runs/wtp04/eval.jsonl (1,296 units).
- Score: eval_score.json (`python -m ensorain.wtp4.score4 eval`).
- Run: ubu006, 3 workers, nice 10, 37,148 s (10.3 h; the prereg estimate of ~3 h was wrong by 3.4x).
- Seeds 41004001, 41004002.

## VERDICT (score4, mechanical): ISLANDS_MAPPED

- Instrument: all 11 axes are LIVE. Every axis is >= 84% live after excluding no-op levels; forgetting is 81/96,
  every other axis 100%.
- Families with a PAYS cell: 9 of 12.
- Families with a replicated PAYS<->DEAD boundary on an ordered axis: 8 of 12 (needed >= 6).
- SPLIT (the two seeds disagree): 11.3% of non-native cells (NOISE_LIMITED needs >= 30%).

Non-native cells (636):

    STRUCT_PAYS 145   CHEAP_PAYS 75   DEAD 279   SPLIT 72   INFO_VALUELESS 33   TRAPPED 32

## 1. The headline: habitability is a FAMILY property, not an axis property

Per family, over its 53 perturbed cells:

    family  key                              native        pays/53  dominant
    F00     cp few_big fiber                 SPLIT         20       STRUCT 20
    F01     cp many_small cell               DEAD           0       DEAD 44
    F02     cp many_small fiber              DEAD           0       DEAD 51
    F03     lowrank many_small cell          STRUCT_PAYS   33       STRUCT 32
    F04     pairwise binary masked           STRUCT_PAYS   32       STRUCT 31
    F05     pairwise few_big masked          CHEAP_PAYS    32       CHEAP 31
    F06     pairwise many_small cell         DEAD           0       DEAD 47
    F07     pairwise many_small marginal     CHEAP_PAYS    38       CHEAP 38
    F08     sum few_big masked               STRUCT_PAYS   32       STRUCT 32
    F09     tt few_big cell                  STRUCT_PAYS   29       STRUCT 29
    F10     tt few_big fiber                 SPLIT          3       SPLIT 27
    F11     tt many_small cell               DEAD           1       DEAD 48

The pattern:
- The families divide into two groups.
  - Dead at native: F01, F02, F06, F11. They stay dead almost everywhere (0-1 of 53). No single-axis move
    outward revives them.
  - Paying at native: F03, F04, F05, F07, F08, F09. They pay in 55-72% of their perturbed cells.
- At one-axis resolution the islands are not reached by perturbation. They are inherited from the founder.
- The winning carrier class is a family constant as well. Families where structured carriers win stay
  structured; cheap families stay cheap.
  - A carrier-class change along an axis, replicated in both seeds, happened in only 2 of 132 family-axis
    pairs:
    - F04 change_timescale: struct -> cheap as change gets faster;
    - F05 forgetting: cheap -> struct at rate .3.
  - So the operator's THEN question ("where does the preferred carrier change?") has almost no single-axis
    support in these worlds.

## 2. Per-axis map (pooled over the 12 families; P = pays, S = of which STRUCT, D dead, T trapped, I info-valueless, X split)

    memory_ratio        .5 P7/S3 | .25 P6/S4 | .1 P5/S4 | .03 P3/S1 | .01 P1/S0 | .003 P0
    change_timescale    static P6/S4 | p800 P6/S4 | p200 P2/S1 | p50 P2/S1 | p12 P0
    information_cost    x.1 P7/S5 | x1 P6/S4 | x10 P3/S2 (I2) | x100 P0 (I7)
    observation_noise   0 P7/S5 | .1 P7/S5 | .3 P6/S4 | 1 P0 (X4) | 3 P0
    irreversibility     door 0 P5 | .1 P5 (T2) | .3 P5 (T4) | .6 P5 (T5)
    credit_delay        0 P6 | 4 P7 | 16 P6 | 64 P6
    topology            lattice P7/S6 | ring P1 (T3) | small_world P1 (T3) | erdos P3 | tree P1 (T9) | scale_free P2
    compute_cost        x.1 P7/S5 | x1 P6/S4 | x10 P3/S1 | x100 P1 | x1000 P0 (I4)
    forgetting          0 P7 | .02 P7 | .1 P7 | .3 P6
    active_sensing      random P4 | greedy P4 | novelty P7 | probe_greedy P0 (I10) | rollout P0
    recurrence_lifetime x4 P4 (T2,X3) | x2 P5 (X3) | x1 P6 | x.5 P7 | x.25 P5

Where learning dies. Each of these levels leaves 0 paying cells in all 12 families:
- observation noise sd >= 1;
- drift every 12 steps;
- information cost x100;
- compute cost x1000;
- memory band .003;
- probe_greedy / rollout policies.

Sharp, replicated edges:
- Change timescale: the edge falls between a drift period of 800 and 200 steps in F00, F03 and F09. F08
  survives to p50.
- Observation noise: the edge falls between sd .3 and 1.0 in F00, F03, F08 and F09.
- Memory: each family dies at a different band:
  - F05: .25 -> .1;
  - F04: .1 -> .03;
  - F03 and F08: .03 -> .01.
  - The edge is family-specific, consistent with a memory / description-length threshold. That is untested
    here.
- Price edges:
  - Information: x1 -> x10 in F08 and F09; x10 -> x100 in F04 and F07.
  - Compute: x1 -> x10 in F03 and F09; x10 -> x100 in F08; x100 -> x1000 in F07.
  - At high information prices the OUTCOME is INFO_VALUELESS: even the oracle cannot buy information
    profitably.
  - Information stops being worth having before learning stops working.

Where learning is robust:
- credit delay up to 64;
- forgetting up to .3;
- door closure. Paying stays 5 of 12 at every door level; what the doors change is DEAD -> TRAPPED.

## 3. Predictions (prereg s8), scored

- P1 (PAYS non-decreasing in lifetime): REFUTED.
  - PAYS by lifetime: x.25 5, x.5 7, x1 6, x2 5, x4 4.
  - The long-life loss is SPLITs (F00, F04, F05, F10) and traps (F06, F09 at x4). It is not clean deaths.
  - Longer lives give more chances to hit a confining or degenerate state, and the WTP-03 degeneracy stop
    ends the life.
  - Undiscriminated. The WTP-03 claim that learning-time / lifetime controls inhabitability is NOT supported
    as a monotone law in this population.
- P2 (info cost x100 kills paying in >= half of the x1 payers): HIT. All 6 die; 7 of 12 cells are
  INFO_VALUELESS.
- P3 (no STRUCT_PAYS at band .003): HIT. There are 0 PAYS cells of any kind.
- P4 (p12 drift hurts STRUCT more than CHEAP): HIT ON THE LETTER (STRUCT 4 -> 0, CHEAP 2 -> 0); its MECHANISM IS
  REFUTED.
  - Cheap and recency carriers die too. Fast change kills learning, not structure in particular.
- P5 (structured carriers win < 40% of paying cells): REFUTED. They win 145 of 220 (66%).
  - Caveat: the structured wins sit almost entirely in 5 families (F00, F03, F04, F08, F09; F05 adds 1). These are completion-friendly
    generators (cp / lowrank / pairwise-binary / sum / tt).
  - The cheap wins sit in 3 (F05, F07, F10).
  - Pooled shares mostly count families.
- P6 (no PAYS at noise sd 3): HIT.
- P7 (verdict odds): ISLANDS_MAPPED, the .35 outcome.

## 4. What this does and does not establish

Established, at two seeds per cell and the WTP-03 economy held fixed:
- Habitability is rare and inherited (6 of 12 families at native). It is robust to delay and forgetting, and
  killed by noise, fast change, information and compute prices, and memory starvation.
- For each family the kill edges are bracketed to one level step.
- Cheap competitors were run first everywhere. They explain all of the habitability in F05 and F07 (and F10's
  little), and none of it in F03, F04, F08 and F09.

NOT established:
- That any STRUCT_PAYS cell is beyond known physics. No N6 (tuned same-class batch fit) was run. These
  families are the WTP-03 completion positive control.
- Interactions. Axes were moved one at a time; a dead family might be revivable by two moves together.
- The memory edge as a description-length law. That is suggested, not tested.

Limitations specific to this run:
- active_sensing: the random twin always uses the random policy. Under probe_greedy / rollout every other life
  pays probe or rollout prices, and the random twin outearns even the oracle (e.g. F08 seed 41004001: random
  1.30, oracle .94), so those cells read INFO_VALUELESS. The axis therefore measures "paid sensing versus a
  free random walk", not learning versus no learning. Read it that way.
- topology: off-lattice geometries trap F08/F09, even without one-way edges, because of the family's
  directed-edge fraction (prereg s7a).
- Two seeds per cell: 11% SPLIT. Splits are reported, never rounded.
- Bitwise ubu006-bound. Not comparable bit-for-bit with WTP-03 M2 rows.

## 5. Recommendation (nothing launched)

1. THEN (substrate collision) should be narrow:
   - only the 4 structured-carrier islands (F03, F04, F08, F09);
   - with N6 in the ladder;
   - at the replicated edges (memory, change, noise, price), where the margin over cheap carriers is
     smallest.
   - The question is whether a structured carrier ever beats N6 near an edge.
   - WTP-04 gives little reason to expect a carrier change along single axes.
2. Two-axis probe for the dead families. A small preregistered 2D grid on F01, F06 and F11 (memory x change,
   memory x price) would test whether habitability can be created by moves in combination, or only inherited.
3. RESERVE becomes more urgent. Every WTP-03 family is tensor-native, and the structured winners are
   completion families. Non-tensor-native grammars are the only route to a different answer to "what substrate
   survives".
4. Instrument debt:
   - make the active_sensing baseline policy-matched;
   - discriminate the long-life SPLIT / TRAP effect (P1);
   - budget the next run at the measured ~29 s per unit-core, not the prereg's guess.
