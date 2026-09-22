# ARES_FIRST_REPORT -- cycle 0 (pressure engineering sandbox)

Currency: 2026-09-19. Ares, M2. Sweep code_commit e19864f52; results
under ares/runs/sweep_c0/; verdict rule preregistered in
ares/DESIGN_C0.md (committed before any result). Eligible count = 3
seeds per world-mode cell. Every number here carries a run id in the
JSON; none is rounded into a nicer one.

This is a first cycle of a sandbox, not a claim about cognition. Read
it as: the apparatus works, it has already falsified three of its own
controls, and one pressure produced a mechanism worth keeping.

## 0. One-paragraph summary

Twelve abstract pressures were run as toy worlds; a dumb GA (P=128,
G=120) evolved generic graph organisms in each under three modes
(pressure present / absent / shuffled). Fitness was world reward only;
memory, planning and modularity were never rewarded or named. ONE
pressure (W4, hidden regime) produced a clean, necessary, localised
memory mechanism that is absent from controls: intact champions score
40/40, and removing within-lifetime activation memory collapses them to
chance (2.6) while removing plasticity does nothing. TWO more pressures
(W5 delayed revelation, W12 dying lineage) produced the target
behaviour but were mis-scored by contaminated controls that the sweep
itself exposed. The rest produced reflexes (W2, W7), failed to induce
adaptation (W3), or did nothing (W11). No mechanism transferred across
worlds; no transplanted subgraph outperformed a random one. Pressure
engineering produced a real fossil on its first cycle -- and, more
useful this early, it produced three calibrated instrument failures.

## 1. Verdict table (preregistered rule, ares/runs/sweep_c0/verdict.txt)

    world  pressure              verdict                         i   ii  iii
    W1     catastrophic tail     MATERIAL                        3/3 3/3 3/3
    W2     rare override         REFLEX (no load-bearing node)   3/3 3/3 1/3
    W3     changing rules        FITNESS WITHOUT THE BEHAVIOUR   3/3 1/3 1/3
    W4     hidden regime         MATERIAL                        3/3 3/3 2/3
    W5     delayed revelation    (mislabelled; see s3.2)         3/3 1/3 2/3
    W7     incompatible regimes  REFLEX                          2/3 2/3 1/3
    W11    irreversible commit   DID NOTHING                     1/3 0/3 3/3
    W12    dying lineage         MERELY HARDER (threshold wrong) 0/3 2/3 2/3

    i   = present champion held-out >= threshold
    ii  = present conditional behaviour present AND absent from shuffled
    iii = >= 1 load-bearing hidden node (ablation delta <= -25% of range)

## 2. The eight charter questions

Q1. WHICH PRESSURES MATERIALLY CHANGED EVOLVED MACHINERY?
- W4 (hidden regime). The strongest result. Two regimes give identical
  observations after step 2 and demand opposite actions; the only
  evidence is a 3-step early cue; there is no reward channel. Present
  champions reach late-life accuracy 1.00 for BOTH regimes (shuffled
  control 0.55, chance). The mechanism is necessary and specific:
  combined-memory ablation (ares/runs/sweep_c0/nomem.json) gives intact
  40.0, no-activation-memory 2.6, no-plasticity 40.0, no-memory 2.6 in
  all three seeds -- the behaviour rides on cross-step ACTIVATION
  memory, not plasticity. Node ablation localises it: in seed 3 two
  nodes (a GATE and a MAX) each drop fitness from 40 to 2.6 when
  removed. Frozen at ares/fossils/W4_activation_memory_s3/ (replays to
  40.0000). Nothing rewarded or named memory.
- W1 (catastrophic tail). MATERIAL but modest. Present champions act
  less often under the danger cue than without it (gap 0.27-0.33 in
  3/3; shuffled gap ~0.00), with a load-bearing node in 3/3 and a small
  activation-memory dependence (no_state 14 vs base 17). Genuine
  conditional catastrophe-avoidance, but low-magnitude.

Q2. WHICH PRESSURES DID NOTHING?
- W11 (irreversible commitment). Champions commit on step 1 (mean
  commit step ~0) at barely-above-chance accuracy (0.56-0.69) while the
  reversible-control world is learnable to 58. The commitment pressure
  produced immediate blind commitment, not evidence accumulation. This
  matches the preregistered prediction P-W11.

Q3. WHICH PRESSURES MERELY INCREASED DIFFICULTY?
- W3 (changing rules). FITNESS WITHOUT THE BEHAVIOUR. Champions reach
  30-54 held-out but by mastering the PRE-flip mapping (acc_pre 1.00)
  and eating the loss after the flip (acc_post 0.00 in 2/3 seeds); only
  seed 3 recovered post-flip (0.99). Within-lifetime adaptation did NOT
  reliably emerge; the GA found that being right for the first ~30
  steps beats adapting. Curiously, W3 fitness rides on PLASTICITY
  (noplast drops seed-1 from 30 to 3; noact leaves it at 30) -- the
  plastic weights lock onto the pre-flip mapping. Predicted (P-W3).
- W7 (incompatible regimes). REFLEX. score_A 1.2 and score_B 0.8 in the
  best seeds (both regimes handled), but the ablation profile is not
  reliably separable (load-bearing in 1/3), so there is no evidence of
  a specialise-plus-arbitrate structure. Predicted (P-W7).

Q4. WERE ANY MECHANISMS REUSABLE ACROSS WORLDS?
- No. Transfer of the W4 champion to other present worlds:
  W4->W4 40.0, W4->W2 23.3, W4->W12 19.8, W4->W1 -10.9, W4->W7 -130.0.
  It is world-specific, sometimes catastrophically so. The W8
  transplant protocol confirms it: evolved-subgraph retention equals
  random-subgraph retention on every source-target pair (both in
  0.00-0.14, differences within noise, random sometimes higher). No
  reusable "organs" emerged. Predicted (P-W8).

Q5. DID ANY PRESSURE CAUSE STATE-DEPENDENT EXPLORATION / RISK?
- Yes: W12 (dying lineage). P(risky | energy) falls from 1.00 in the
  lowest energy bin to ~0.0 in the highest in 2/3 seeds (shuffled and
  absent flat). Risk is taken exactly when the energy store is low and
  death is otherwise certain -- state-dependent risk, with no threshold
  encoded anywhere in the objective. It is scored MERELY HARDER only
  because the fitness threshold was miscalibrated (s3.3); the BEHAVIOUR
  is present and clean. W2 (rare override) also produced conditional
  risk (risky-in-window gap 0.79) but as a reflex (Q6/s3.1).

Q6. DID INCOMPATIBLE REGIMES CREATE SPECIALISATION / ARBITRATION?
- No, not reliably. W7 handles both regimes in the best seeds but shows
  no separable ablation profile in 2/3 seeds. No MoE-ness was scored
  (charter anti-goal); the question was whether ablation localises two
  competences to different nodes, and it did not.

Q7. CAN DEVELOPMENTAL ENCODING FIND MACHINERY FASTER THAN DIRECT?
- No. On W4 the developmental encoding reaches threshold at generation
  10-25 vs direct 15; on W3 at 10-20 vs direct 0-5. It can EXPRESS the
  solution (W4 dev reaches 40) but does not accelerate discovery at
  this budget. Predicted (P-W10).

Q8. DID ANYTHING EMERGE THAT DOES NOT FIT A KNOWN ARCHITECTURE?
- Not this cycle, honestly. The W4 fossil is describable as conditional
  memory (a gate plus a carrier); W2/W7 as reflexes; W12 as a
  state-keyed switch. Nothing yet defies a threshold/gate/carrier
  vocabulary. The charter values this category most; cycle 0 did not
  produce it. The W4 fossil is handed to Nyx/Harmonia for anatomical
  interpretation (ARES-20) precisely so its description is not fixed by
  its builder.

## 3. What the sweep falsified about ITS OWN instruments (the real product)

3.1 The "no_state" ablation did not remove memory. It sets keep off and
    resets activations each step but LEAVES PLASTICITY intact; plastic
    weights persist across steps and are an independent carrier. A
    nostate-arm organism scored ~33 on W4 by using them. Fixed by the
    combined no_memory ablation (ares/supp_nomem.py, EXPLORATORY),
    which is what let W4 be attributed to activation memory
    specifically and W3 to plasticity. LEDGER 2026-09-19.

3.2 The W5 shuffled control is contaminated by a held-out imbalance.
    W5 present champions reach decision accuracy 1.00 in 2/3 seeds --
    genuine information carried across a 26-step delay through
    distractor noise (nomem: intact 50, noact 6, noplast 3, nomem 0 --
    BOTH memory routes needed, neither alone). This CONTRADICTS the
    preregistered prediction P-W5 ("did nothing"): delayed revelation
    DID produce cross-delay memory. The verdict label
    "FITNESS WITHOUT THE BEHAVIOUR" is an artifact: the balanced-seed
    construction balances only the FIRST binary draw (regime), and W5's
    paying side is a SECOND draw, so a fixed guess scores high in the
    shuffled control and trips the "shuffled must not" clause. The
    behaviour is real; the control is wrong. To be re-run at cycle 1
    with a W5-balanced shuffled set.

3.3 The W12 fitness threshold was miscalibrated. It was set from an
    attainable pre-estimate of ~80 (the absent-mode cap), but the
    present world cannot reach 80 because risk is genuinely costly; the
    real present ceiling is ~30. So W12 fails criterion (i) by
    construction while the target behaviour is present (s3, Q5). The
    lesson: attainable-range estimates for a PRESSURE mode must be
    derived from that mode, never borrowed from the mode that removed
    the pressure. LEDGER pending.

3.4 The W2 shuffled control is a reward-feedback leak (recorded before
    the sweep, DESIGN_C0 ADDENDUM 1): windows persist ~2 steps and the
    last-reward channel reveals a paying window one step late, so
    shuffled champions reach 60-80 by a reward reflex rather than 60.
    Handled: the present-vs-shuffled behaviour gap (0.79 vs 0.0-0.27)
    is still valid because it is computed against the TRUE window.

Four preregistered controls, three of them found defective by the data
they were meant to control, all recorded before this report. That is
the cycle's most reliable output.

## 4. Secondary observations (descriptive, NOT claims; 3 seeds only)

- W6 scarcity: scarce champions (2 hidden slots, 1 tick) reach 28-30 on
  the W3 task with 0-2 hidden nodes; abundant champions (12 slots, 4
  ticks) reach 29-44 with 9-12 nodes. Scarcity produced COMPACT
  solutions at modestly lower fitness. No motif unique to scarcity was
  identified; not claimed. (Seed-3 scarce used 0 hidden nodes -- a pure
  input-output reflex.)
- W9 ecological coupling: choice autocorrelation lag1 0.65-0.69 in the
  coupled (present) mode -- a Red Queen cycle, as predicted (P-W9).
  Coupled champions' cycle count (4-7) is not larger than the static-
  opponent control's (2-6): no extra machinery from coupling this
  cycle. The fixed-periodic (shuffled) opponent was exploited to the
  cap (40).
- W4 ancestry: the memory mechanism ACCRETED over ~13 lineage
  generations (add_node x3, add_edge x4, alter_keep x2, perturb_weight
  x7, ...), not one lucky mutation. It was assembled, not stumbled on.

## 5. Decision-rule readout (charter)

The charter's strongest positive result is "a simple pressure
repeatedly causes an inspectable mechanism absent from controls, that
transfers beyond its world, and was not in the objective." W4 meets
three of four clauses (repeatable 3/3, inspectable, absent from
controls, not in the objective) and FAILS transfer -- it is
world-specific. The "still better" result ("we do not know what it does
but ablation proves it matters") is partially met: the W4 GATE+MAX pair
is load-bearing (ablation 40 -> 2.6) and its exact computation is not
yet explained. That is a fossil worth keeping. Pressure engineering is,
on this one cycle, a usable accelerator for mechanism discovery -- with
the sharp caveat that most pressures produced reflexes or nulls, and
the apparatus's main early value was catching its own bad controls.

## 6. The three experiments that should run next

1. FIX AND RE-RUN THE THREE MIS-SCORED INSTRUMENTS, then re-run W4, W5,
   W12 at 10 seeds. Specifically: a W5-balanced shuffled seed set
   (s3.2); a W12 present-derived attainable/threshold (s3.3); the
   combined no_memory ablation promoted to a standard column (s3.1).
   Artifact: sweep_c1 with corrected DESIGN and a 10-seed verdict.
   Only after this are W5 (cross-delay memory) and W12 (state-dependent
   risk) eligible to be called MATERIAL.
2. PRESSURE THE CARRIER HARDER: combine W4 (hidden regime) with W5
   (delay) -- a cue early, a demand late, identical observations
   between -- to see whether the activation-memory motif extends or
   breaks, and hand the W4 fossil to Nyx/Harmonia for interpretation
   (ARES-20) before building on it.
3. TEST WHETHER THE W4 MOTIF IS THE ONLY ROUTE: re-run W4 with keep
   disabled but plasticity ON (does a plasticity-based carrier emerge
   when the activation route is blocked?) and with both disabled (does
   the pressure then produce nothing, confirming memory is the only
   answer to hidden-regime pressure in this substrate?).

## 7. What would make Ares stop (unchanged from DESIGN_C0 s7)

If cycle 1's corrected instruments show W4 was the only pressure to
produce a load-bearing mechanism and every other MATERIAL candidate
collapses to a reflex, the conclusion is that this substrate at this
budget hosts exactly one kind of discoverable machinery (a gated
carrier) and the next question is a SUBSTRATE question, not a pressure
question.
