REPORT -- which cue-holding architecture evolution builds when the cue time varies

1. WHAT I SET OUT TO TEST
In the variable-delay hidden-regime world, a +-1 cue appears for 3 steps. The window starts at a random step in [0,20], and reward comes only in the last 10 of 40 steps. Ares evolved 10 lineages on this world (seeds 201-210). I wanted to find out what memory those champions actually built. An earlier reading of the fixed-timing world left two candidate designs open:
(i) a cue-magnitude threshold that ignites from the organism's resting state at any time, with a wide safety margin;
(ii) a resting state parked within about 0.1 (in cue units) of the ignition boundary, so any small cue tips it.
A third possibility was that the lineages route around both, through plastic weights, decaying traces or float artefacts. Per champion I ran the proposed discriminators:
- ignition from the zero state and from a settled rest state at cue starts 0/5/10/15/20;
- the ignition threshold in cue units (the "margin");
- re-scoring with plasticity frozen (R=0);
- for seed 208, perturbing its decayed trace by tiny amounts.
I added one test the proposed rule needed: locating where the bit is stored after ignition.

2. WHAT I DID
Data: ares/runs/sweep_c2/W16_present_s201..s210.json @1dde117f7. The genome analysed is the training-selected one, snapshots[-1].genome, i.e. the last generation's training champion, not final.genome. Its replay reproduces the logged champ_heldout exactly for all 10 seeds. It differs from final.genome in 6/10 seeds.
Code: git archive of ares/ @1dde117f7, exported to work/R-17/src. Its substrate execution is identical to the one the runs recorded (@ab137f52b); the only difference is a keep-mutation step-size parameter. The world is ares/worlds.py W16VariableDelay. The apparatus is adapted from nyx/readings/ares_w4_reading.py @bf5073a91 (drive / scc_report / latch_test ideas).
Scripts, all in /home/jcraig/artemis-selftest/work/R-17/:
  w16lib.py         - loader, batched rollout, clean synthetic drive, forced-start world, runtime hook for flush-to-zero and per-tick noise
  part1_scores.py   -> out/part1_scores.json
      Scores on 256 fresh episode seeds (700000+, not any holdout) under: intact; shuffled world; R=0; keep=0; no activation memory; recurrent edges cut; flush |v|<1e-6 and <1e-3 to zero; per-tick activation noise sd 1e-6 and 1e-2.
  part2_drive.py    -> out/part2_drive.txt/.json
      Forced-start profile (starts 0..20, 32 seeds each, intact and R=0). Clean drive: noise channel 0, 3-step cue of +-c for c in 0.05..2.0 at starts 0,5,10,15,20. Run from zero, and from a settled rest state (one full cue-free episode first, activations and plastic weights carried). Also cue-free default action, and a set-then-opposite-cue test.
  part3_s208_ties.py -> out/part3.txt/.json
      Seed 208 trace and perturbations of +1e-30, -1e-30 and +1e-40, plus zeroing. Its comparator threshold scan. An exact-tie census of the output argmax for all champions (64 fresh real episodes).
  part4_storage.py  -> out/part4.txt/.json
      Where the bit is stored: at t=25 after an ignition cue, either reset plastic weights to the genome, or replace activations by the cue-free run's activations. Settled-rest split (carry activations only / weights only). Real-world reward per regime, intact vs R=0.
Everything was run with env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 <script>.

3. RESULT
Common to all 9 solvers: the detector is one-sided. With no cue, each champion settles to a fixed default action, which is the action for one regime. Only the other cue sign has to ignite; the default-sign cue needs nothing. Default is action 2 for seeds 201, 204, 207, 210 and action 1 for 202, 205, 206, 208, 209.
The ignition threshold c* is the smallest 3-step cue that gives 10/10 correct final actions (clean drive, from the zero state, at starts 0/5/10/15/20). For reference, the real cue is 1.0 +- 0.2 and the background noise has sd 0.3.
   201: 0.1 0.2 0.3 0.5 0.8   settled rest 0.7-0.9
   202: 1.2 at all starts     (above the cue mean -> partial solver)
   204: 0.8-0.9;  205: 0.8-1.2;  206: 0.6-0.9;  207: 0.3-0.8;  208: 0.95 (comparator: cue > ~0.945)
   209: 0.5 -> 1.0 rising with start;  210: 0.7 flat
Only seed 201 at start 0 (c*=0.1, the transient just after the episode reset) matches the near-boundary design. Every other threshold is 0.5-1.2, a wide margin of 2-4 background sd.

Per-champion scores on fresh seeds (intact / shuffled / R=0 / recurrent edges cut / flush-to-zero 1e-6):
   201  9.31 / -0.20 / 9.12 / 0.72 / 9.31
   202  7.34 / -0.36 / -0.46 / -0.34 / 7.34
   203  0.47 (non-solver: constant action)
   204  9.04 / 0.11 / 0.47 / 1.77 / 9.04
   205  8.17 / -0.42 / 8.17 / -0.48 / 8.17
   206  9.15 / -0.44 / 2.95 / -0.47 / 9.02   (noise sd 1e-6: 8.22; sd 1e-2: 5.38)
   207  9.28 / -0.16 / -0.55 / 8.30 / 9.28  (no activation memory: 8.90)
   208  9.07 / -0.25 / 9.07 / 9.07 / -0.35  (flush 1e-3: -0.53; noise sd 1e-6: 0.33)
   209  8.56 / 0.08 / 6.08 / -0.14 / 8.56
   210  9.91 / -0.45 / 0.47 / 0.49 / 9.91

Storage location. At t=25 I either reset the plastic weights or replaced the activations with their rest values:
- activation-held: 201, 204, 205, 206, 208, 209 (the activation reset kills the bit; the weight reset does not);
- plastic-weight-held: 202, 210 (weight reset kills 202 and drops 210 to 0.6);
- both, redundantly: 207 (either reset alone survives; no-activation-memory scores 8.90).

Seed 208 is a numeric artefact. After ignition its trace decays to 1e-10..2e-22 by t=39 and is never exactly 0. The competing outputs are -0.040 and exactly 0.0. The cue-absent case is an exact tie, which argmax breaks to the first index.
- Adding +1e-30 (or the denormal +1e-40) to the zero trace at t=29 flips all 10 scored actions.
- Adding -1e-30 to a live trace changes nothing.
- Zeroing the live trace flips the action.
- In real episodes, 62.5% of its scored steps are exact output ties and 36% more have gaps below 1e-6.
Detection itself is a genuine threshold from rest; the memory is an underflow-scale number read through an exact-zero tie. No other champion has exact ties. Seed 206 has 15% of its scored steps with output gaps below 1e-6, and it loses 0.9 under 1e-6 noise and 3.8 under 1e-2 noise.

Per-champion call, with the deciding measurement:
   201  threshold-from-rest. Activation loop (cut recurrence -> 0.72); R=0 irrelevant; ignites from settled rest at all starts, c* 0.7-0.9. Near-boundary only in the first few steps after reset. The opposite cue re-sets it.
   205  threshold-from-rest. Thresholding output with a self-loop, as the hand reading proposed; R=0 irrelevant; c* 0.8-1.2 including from settled rest. Margin sits near the cue mean, hence 8.2.
   204  other. Threshold ignition with an activation hold, but ignition needs plasticity (R=0: never ignites, score 0.47).
   206  other. Activation hold. Plasticity raises the threshold: at R=0 c* falls 0.9 -> 0.5 and background noise falsely ignites it (regime-0 reward -3.6). Partly numerically fragile.
   209  other. Activation hold; c* rises with start. It cannot ignite from activations carried from a cue-free episode, so it relies on the transient after the episode reset (time-coupled, not a stationary rest).
   202  plastic storage. Weight reset kills the bit; R=0 -> no ignition.
   207  plastic (+ redundant activation) storage. R=0 flips the default. Weights carried from a cue-free episode disable ignition.
   210  plastic storage. Weight reset -> 0.6; R=0 -> no ignition; carried weights disable ignition.
   208  numeric artefact (see above).
   203  non-solver.
Tally over 9 solvers: clean threshold-from-rest 2 (201, 205); threshold detection with a plastic-assisted or time-coupled detector and activation hold 3 (204, 206, 209); plastic storage 3 (202, 207, 210); numeric artefact 1 (208); near-boundary rest 0.

Plain conclusion: the near-boundary rest design was not built. Every solver is a one-sided cue-magnitude threshold over a cue-free default, with a wide margin (0.5-1.2 cue units). That is the threshold-from-rest design, minus the symmetry. But only 2/9 hold the result in a clean activation latch that is independent of plasticity and timing. 3/9 store it in plastic weights, 3/9 need plasticity or the episode-reset transient for detection, and 1/9 "stores" it as a float32 underflow residue read through an argmax tie.

4. DID IT RESOLVE THE QUESTION
Partly. It resolves the question as posed: near-boundary rest is refuted (0/9), and cue-magnitude ignition from rest describes the detection stage in all 9. It shows the question's framing was too narrow in two ways:
(a) the designs are one-sided, with a default state;
(b) detection and storage are dissociable, so "which latch" has different answers per lineage.
The proposed rule "collapse at R=0 means plastic storage" is wrong for 204 and 206. There, plasticity shapes the detector, and the bit is held in activations. The storage-localisation test was needed to separate the two cases.
Not done:
- I did not identify the exact plastic sub-circuit in 202/204/207/210 (which edge's weight carries or gates the bit).
- I did not analyse the final (reporting-set-selected) genomes, so whether they differ mechanistically is open.
- n = 9 solvers from one cycle-2 config.

5. CONSEQUENCES
- Instrument/substrate defect (for Ares; also the defect catalogue). The substrate lets a float32 value of ~1e-22 carry a bit, because the action is a deterministic first-index argmax and an unfed keep node decays geometrically without reaching 0. Seed 208 is a full-score champion built on this: it collapses under flush-to-zero at 1e-6 or under 1e-6 activation noise. Its "cut_keep -> 0" and "zero recurrent edges" readings are genuine, but the carrier is not a usable memory. Seed 206 is partly exposed.
  Suggested fix: add a small activation noise floor or flush-to-zero, and/or random or abstain tie-breaking, and rerun the variable-delay arm. The carrier census (KEEP class) should be treated as contaminated until then.
- For Nyx: the fixed-timing reading's threshold-from-rest prediction holds for the detection stage (9/9, wide margin); the near-boundary alternative gets 0/9. Both designs as written assumed symmetric detection; the evolved designs are one-sided (default + one ignition sign). Nyx's "settled rest" notion is ill-defined for plastic organisms: carried plastic weights drift during a cue-free episode and disable ignition in 202/207/210.
- For Ares: plasticity's role under this pressure is split. It is the store in 3/9 and a detector component or threshold tuner in 2/9. Carrier-class counts from R=0 ablation alone conflate these; a storage-localisation test (reset weights vs reset activations after the cue) is cheap and should be added to dissect.
- This is a new positive result (the one-sided threshold-from-rest detection design) plus a reproduction of the known 5/9 plasticity load. Seed 205's hand reading is confirmed by replay; seed 208's hand reading is confirmed exactly.

6. COST
About 1.5 h of my time. About 20 CPU-minutes total (part 1 7 min; parts 2-4 about 12 min), with at most 2 processes at once. No GPU, no holdouts touched; only fresh episode seeds were generated. Not done: the plastic sub-circuit tracing, a comparison against final genomes, and larger seed counts for the forced-start profile (32 per start).
