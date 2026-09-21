# DESIGN_C1 -- Ares cycle 1: VALIDATE, COMPRESS, EXIT (preregistered)

Currency: 2026-09-21. Ares. Operator directive verbatim at
roles/Ares/prompts/2026-09-21_cycle1_directive/ (MANIFEST beside it).
Committed BEFORE any cycle-1 run. Changes after a result is seen go in
a dated ADDENDUM only. This cycle does not broaden the catalogue and
does not begin another exploratory sweep. It ends in a hard
disposition and the seat is then parked; cycle 2 is not self-
authorised.

## 1. The three repairs (each verified before this file was committed)

R1 no_state retired. The three-way memory ablation in search.dissect
   now names every cross-step channel: no_activation_mem (keep off +
   activations reset each step; plasticity intact), no_plasticity
   (plastic weights frozen at the genome), no_memory (both). Within-
   step ticks and the world's own feedback channels are not memory.
   A GA arm on the no_memory substrate (arm_nomem_W4) is the positive
   control of the semantics: with no cross-step channel, W4 present
   must sit at its floor.
R2 W5 control semantics. Held-out seeds are now balanced per world on
   EVERY hidden binary via world.balance_key() (search.balanced_seeds_
   for): W5 shuffled is 8/8/8/8 on (token, pay), so a fixed guess
   scores exactly 0 there. Verified 2026-09-21.
R3 W12 threshold from its own mode. ares/calibrate_w12.py evaluates the
   "risky iff energy < k" family in PRESENT mode: best 30.28 (k=3.5);
   best fixed 19.00. Threshold = 19.00 + 0.2 * (30.28 - 19.00) = 21.26.
   The absent-mode ceiling (80) is never used again.

## 2. Apparatus

As cycle 0 (substrate default Config; GA P=128, G=120, eps=4, elites
16) with: per-world balanced 32-episode held-out sets (start 20000);
per-generation champion snapshots for ancestry; SEEDS 1..10.
Worlds: W4, W5, W12 (repaired reruns) and W13 (carrier stress: W4 cue
steps 0-2, distractor sd 1.0 on the cue channel steps 3-59, reward only
steps 60-79, no reward channel). Modes present/absent/shuffled.
Plus arm_nomem_W4 (present, 10 seeds).
Total 130 GA runs. Eligible count per world-mode cell = 10.

## 3. Floors and thresholds (present mode; attainable from the mode itself)

    world  floor  attainable  threshold  source
    W4      0.00     40.0        8.00    cap (40 paying steps)
    W5      0.00     50.0       10.00    cap (one +50 decision)
    W12    19.00     30.28      21.26    calibrate_w12 (present family)
    W13     0.00     20.0        4.00    cap (20 paying steps)

## 4. Per-seed criteria

  (i)   held-out >= threshold
  (ii)  behaviour, present AND absent from shuffled (as C0 s4):
        W4/W13 acc in paying steps >= 0.65 with both regimes >= 0.55;
               shuffled < 0.65
        W5     dec_acc >= 0.7 with both sides >= 0.55; shuffled < 0.7
        W12    P(risky|lowest bin) - P(risky|highest bin) >= 0.3;
               shuffled < 0.15
  (iii) >= 1 load-bearing hidden node (ablation delta <= -25% of
        (base - floor))
  (iv)  MEMORY-DEPENDENCE (W4, W5, W13 only): no_memory ablation
        retains <= 25% of (base - floor). W12 keys on OBSERVED energy;
        (iv) is recorded, not required.
A criterion HOLDS for a world when it holds in >= 7/10 seeds.

Per champion, two labels are recorded (never optimised):
  memory class from the three-way ablation, using "collapses" = retains
  <= 25% of gain: ACT (no_activation_mem collapses, no_plasticity does
  not), PLAST (reverse), BOTH (each alone collapses), REDUNDANT
  (neither alone, no_memory does), NONE (no_memory does not collapse).
  signature = sorted multiset of ops of its load-bearing nodes
  (e.g. GATE+MAX). Exact match counts as "same".

## 5. Disposition rule (applied mechanically by ares/validate.py)

For W4 (the cycle-0 fossil), and reported the same way for W5 and W12:
  NO_REPLICATION    (i) or (ii) holds in < 7/10.
  CONTROL_ARTIFACT  (i) and (ii) hold, but (iv) holds in < 7/10 (the
                    behaviour replicates but is not memory-carried: the
                    cycle-0 ablation reading was the artifact), OR the
                    repaired shuffled control shows the behaviour in
                    >= 4/10 (the gap was the control's).
  VALIDATED_FOSSIL  (i)(ii)(iv) hold, (iii) holds, AND one exact
                    signature recurs in >= 5/10 champions.
  MECHANISM_DIVERSE (i)(ii)(iv) hold but no signature reaches 5/10
                    (functionally equivalent memory, structurally
                    varied). If GATE+MAX appears in <= 1/10 it is
                    recorded as an idiosyncrasy of lineage s3.
For W12, (iv) is dropped from the rule; CONTROL_ARTIFACT there means
the repaired shuffled control shows the behaviour in >= 4/10.

W13 carrier stress, classified by the majority memory class among
above-threshold champions (>= 5/10 above threshold required, else FAIL):
  PRESERVE   ACT majority (the W4 substrate survives the stress)
  RECRUIT    BOTH or PLAST majority (the second channel is recruited)
  DIFFERENT  REDUNDANT majority (memory, but neither channel alone
             matters) -- reported as such, not named
  NEW_CARRIER >= 5/10 above threshold with class NONE: a cross-step
             route outside both named channels. Per doctrine this is
             an INSTRUMENT question first (a leak or an unenumerated
             channel) and is chased as one before any claim; it is the
             only outcome that could earn another round, and only
             after the channel is identified.

## 6. Ancestry and causal transplant (every qualifying champion)

Ancestry: per-generation champion snapshots are evaluated intact and
no_memory every 5 generations; emergence_gen = first generation where
(intact - no_memory) >= 50% of the final gap; onset_gen = first
generation held-out > floor + 10% of range. accretion = emergence_gen -
onset_gen. Reported as a distribution; "one-shot" if accretion <= 5 in
>= 7/10, "accreted" if >= 10 in >= 7/10, else mixed.
Causal transplant: the champion's load-bearing hidden nodes (with
internal edges, input edges and output edges preserved; other
external connections randomly re-attached) are spliced into 64 random
gen-0 organisms; a random subgraph of equal size/edge count into 64
others. PORTABLE if mean(recipient fitness | evolved) - mean(| random)
>= 25% of (champion - floor). Failures are preserved in the same file.

## 7. Predictions (each can lose)

  P1  W4 replicates: (i) 10/10, (ii) >= 9/10, (iv) >= 8/10.
  P2  W4 signature: GATE+MAX recurs in 2-4 of 10; no signature reaches
      5/10 -> MECHANISM_DIVERSE. (I do not expect one implementation.)
  P3  arm_nomem_W4 sits at the floor (<= 4.0) in 10/10.
  P4  W5 with the repaired control: (i) >= 6/10 (search-limited),
      (ii) holds where (i) holds; class BOTH or ACT; disposition
      NO_REPLICATION or MECHANISM_DIVERSE depending on 7/10.
  P5  W12 with the own-mode threshold: (i) >= 8/10, (ii) >= 7/10,
      shuffled flat; disposition VALIDATED_FOSSIL or MECHANISM_DIVERSE
      (behaviour is a state-keyed switch; signature likely diverse).
  P6  W13: above threshold in 4-7/10 (harder); class ACT majority ->
      PRESERVE; NEW_CARRIER does not occur.
  P7  W4 ancestry: accreted (>= 10 gens) in >= 6/10; transplant
      PORTABLE in <= 4/10 (the motif depends on its wiring context).

## 8. Exit

After the disposition: report (ARES_CYCLE1_REPORT.md), review packet,
artifacts to Nyx/Harmonia without waiting for their reading, STATUS ->
PARKED, backlog annotated, no cycle 2. If NEW_CARRIER fires it is
reported as an instrument question with the channel-hunt as the single
proposed follow-up, and the seat still parks pending the operator.

## ADDENDA (dated, appended only)
