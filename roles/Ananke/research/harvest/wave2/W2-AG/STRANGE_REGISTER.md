# PTE STRANGE REGISTER (Wave 1 + Wave 2) -- W2-AG, Ananke, 2026-10-01

Purpose: keep genuinely strange PTE observations DISCOVERABLE. This is not a findings list. Nothing
here is promoted. An entry stays even when its first interpretation died. The observation is what is
preserved.

Status vocabulary:
- REPRODUCED: re-measured on fresh or recorded worlds by a second run.
- NOT REPRODUCED: a fresh run disagrees.
- EXPLAINED-AWAY: a checked mechanism accounts for it. The explanation is given.
- OPEN: not settled.

Other fields:
- "Interp died / obs survived" records whether the first reading died while the observation lived.
- Cross-engine questions are phrased ONLY from documents W2-AG read:
  - roles/Ananke/research/CROSS_ENGINE_THREADS.md, cited as CET with line numbers;
  - roles/Ananke/research/CROSS_THREAD_COMPRESSION.md, cited as CTC.
  - No other seat's report was read.

Paths are relative to roles/Ananke/research/harvest/ unless they start with roles/ or prometheus/.
Sources: INFERENCE_HARVEST_HANDOFF.md s7 (lines 104-113), the wave2/W2-*/REPORT.md files and
wave2/INFERENCE_LEDGER.md.

W2-AG checks (scripts and outputs are in wave2/W2-AG/; CPU, 2 threads, about 0.06 core-h):
- ag_decompile.py writes decompiled.json and decompiled_hopscan.json. It is a static decompile with no
  engine run.
- ag_dict_trace.py and ag_dict_trace2.py write dict_trace_4781.json and dict_trace2_4781.json. They trace
  4781b0a1 under the normal schedule and under DICT.
- ag_dict2.py writes dict2_4781.json. It cues sensor pairs, adjacent vs non-adjacent. Its docstring
  states the prediction and was written before the run.

---------------------------------------------------------------------------------------------------
## 0. Ranked index ("strangest and most deserving of preservation")

| rank | id | one line | status |
|---|---|---|---|
| 1 | SR-01 | Sharp one-hop wall: every transplanted law is EXACTLY .500, with zero variance, at 2 hops on its own ring | REPRODUCED; interpretation shifted |
| 2 | SR-02 | Distractor-strobe HOLD memory, and parity-clock entrainment to the distractor train (bit-pattern-sensitive) | REPRODUCED; mechanism OPEN at register level |
| 3 | SR-03 | 4781b0a1, the only INTEGRATION law: cluster-bound, pivotality below every plant, DICT exactly .500. New: it carries the vote only through a loop between ADJACENT cued sensors | REPRODUCED + mechanism candidate checked (W2-AG) |
| 4 | SR-04 | MAJ champions at the M3 physics sit near the any-program ceiling (.701) and above a sound single-sensor ceiling (.590), yet INTEGRATION can never fire there | REPRODUCED (recorded outputs joined) |
| 5 | SR-05 | 613162a3 and the global-topology paradox: the one cell where the champion beats every plant, on the topology that is worst once normalised | OPEN (its "chaos" and shuffle excess were EXPLAINED-AWAY) |
| 6 | SR-06 | Anti-copy FLIP champions: 964053bb answers -y_prev on 100% of trials at a row where reach is provably <= .552 | REPRODUCED; OPEN why |
| 7 | SR-07 | Rule-mosaic lottery: one live rule plus one dead rule, chosen per world by a seed. Includes held >> train and 437ca0ac's constructive mosaic | REPRODUCED; mechanism EXPLAINED; consequences OPEN |
| 8 | SR-08 | M2: latch-as-needle vs flat echo/integrator basins; M2 is latency-label-bound and needs the channel | REPRODUCED as fact; accessibility interpretation OPEN |
| 9 | SR-09 | FLIP landscape: the plant is an isolated peak; copy-class basins (.60 relay_flood, .688 RELAY_LATCH) go unclimbed; relay_flood's cue-repeat hold | REPRODUCED; first interpretation died |
| 10 | SR-10 | Champions one tick out of tune, concentrated in one cell family (sync-2, delta-8 RELAY) | REPRODUCED (4/16 credible) |
| 11 | SR-11 | LATCHED-PARTIAL: champions answer the first trials, then freeze the readout | REPRODUCED; first interpretation died |
| 12 | SR-12 | The decay floor (positive values below 8 never decay) as an exploited hidden substrate (613162a3, 311c465f) and a plant killer (P-FLIP) | OPEN (cross-cutting, inferred) |
| 13 | SR-13 | Divergence without use: 53e569f4 (div .99, held .719) | OPEN |
| 14 | SR-14 | Stale-information accuracy above the light-cone ceiling (.518 held; .589 A0 plant at ceiling .5) | EXPLAINED-AWAY (small tail residue) |
| 15 | SR-15 | The population climbs sensitivity with zero accuracy variance for whole runs (flat NULL searches) | EXPLAINED-AWAY (w_any bonus) |
| -- | SR-X1..X7 | Archive of Wave-1 strange items explained away (section 3) | EXPLAINED-AWAY / NOT REPRODUCED |

---------------------------------------------------------------------------------------------------
## 1. Entries

### SR-01. The sharp one-hop wall
- **Observation.**
  - Each of the 7 laws C1 transplanted scores .500 at 2 hops on its OWN native ring and physics:
    - RELAY bbef66a1, 31cd2a8a, 62a7fff9 and c16d5231 at d4 and d6;
    - MAJ 4781b0a1, 0a23398f and f6b623cd at d6.
  - At 3 hops on the clustered and Schreier graphs, all 7 also give .500.
  - The same laws keep SIGNAL at matched hop count on a random graph (6/7).
  - The interval is degenerate, not just low. W2-AG read wave2/W2-I/out/hopscan_*.json: lo99 = hi99 =
    .500 in 13 of 14 native 2-hop conditions. The exception is c16d5231 at d4: .498 [.4948, .500].
  - Zero pair variance means the actuator's readout is identical in both mirror twins. So NO
    sensor-derived information from ANY trial arrives at 2 hops, not even the stale cross-trial residue
    that W2-P F4 shows does leak elsewhere (SR-14).
- **Sources.**
  - wave2/W2-I/REPORT.md:32-42 (F1) and :49-57 (F2 table).
  - wave2/INFERENCE_LEDGER.md:320-321.
  - HANDOFF s1 item 2 (INFERENCE_HARVEST_HANDOFF.md:17-18).
- **W2-AG static reading (decompiled.json, decompiled_hopscan.json; semantics from engine.py:310-318,
  where transients are zeroed per tick, and :358, where GT gives 256/0).**
  - In 4 of the 5 single-rule laws, a site that never senses can never emit:
    - 4781b0a1: EMIT = MAX(S1, SENSE), and S1 = GT(S1+SENSE, CNT0) stays 0 without SENSE;
    - bbef66a1: EMIT = MAX(S1, T1 = 0), and S1 = GT(S1, SENSE) stays 0;
    - 31cd2a8a: EMIT = MAX(SENSE, S1), and S1 decays to -44;
    - 62a7fff9: EMIT = XOR(SENSE, 0).
  - The fifth law, c16d5231, is the exception. Its non-sensing sites emit (EMIT = IN0_0 + 8), but with
    zero payloads, so only packet presence (CNT) travels. It is also the only condition with non-zero
    variance beyond one hop.
  - The two 4-rule SETRULE laws were not traced.
  - [V static; Kp/WIMM offsets on ADDI lines not traced.]
- **Status.** REPRODUCED: 7/7 laws, 3 graph families, zero-variance intervals.
- **Interp died / obs survived.** YES.
  - "Topology-bound / lattice-bound" died: W2-G F1, W2-I F2, and port shuffles never remove SIGNAL
    (W2-I F3).
  - "Evolved transport is one hop" survives only as a description. As a comparative law it is
    unsupported (A1 3/32 vs 1/39, p = .32; wave2/W2-AC/REPORT.md:28).
  - The observation itself (a cliff from SIGNAL to exactly nothing) survived and sharpened.
  - Why it is strange: a 12-line flood plant that does carry 2 hops exists at d9cc (H-PLANT plant
    .97-.98; HANDOFF:123-124). The evolved laws are not weak relays. They are structurally mute away
    from the sensors.
- **Cheapest decisive next test.** An emitter census by site class over all 69 RELAY/MAJ SIGNAL
  champions:
  - one eager run each, 8 worlds;
  - count non-zero-payload emissions by never-sensing sites.
  - Prediction: about 0 for every single-rule champion.
  - That turns "one hop" from a measured count into a structural property of what C1 search produced.
  - Cost: well under 0.1 core-h.
- **Cross-engine question (from CET X-1, lines 9-19).**
  - Aether reports that starving the inert relay sites blocks crossing, and T-X-1 proposes applying
    site-class starvation to PTE.
  - SR-01 predicts that starvation of non-sensing sites is an exact no-op for at least 4 of these PTE
    laws.
  - Question: are Aether's relay sites active forwarders in a way that no evolved PTE law is? If so,
    "relay" names different site classes in the two engines.

### SR-02. Distractor-strobe HOLD memory and parity-clock entrainment
- **Observation.**
  - 5 of 86 HOLD champions depend on the distractor schedule. 3 collapse to chance under fair edits:
    2c300c47 1.000 -> .46-.51; 0c18ce5e .958 -> .50; 41fcb232.
  - Silencing only the FIRST awake gap distractor destroys 2c300c47 and 0c18ce5e. Silencing the LAST
    changes nothing.
  - Yet under half-occupancy jitter with the first slot KEPT, they still drop (.62 / .58), so the later
    slot pattern matters too.
  - 311c465f is a write-enable parity clock entrained by the distractor train. Odd distractor amplitudes
    63/65 destroy it (.50/.51). Even amplitudes give a ragged .58-.76 curve that peaks at 60-64.
  - Strobe and robust champions sit at IDENTICAL physics and env. Examples: 2c300c47 vs 85ca202e;
    0c18ce5e vs d49fdac8; 0a3f6b87 vs ae39bee8.
- **Sources.**
  - wave2/W2-E/REPORT.md:29 (S5), :38 (N2), :46-71 (D1).
  - wave2/W2-Q/REPORT.md:29-45 (table and prevalence), :60 (first-slot split), :111-113 (F2 same
    physics).
  - HANDOFF:111 ("311c465f needs its distractors").
  - Ledger :340-343, :486-490.
- **Status.** REPRODUCED: W2-E screen, then W2-Q on 86 cells with paired edits; 0 new cells beyond 5.
  The register-level path is OPEN: decompiled but not traced (W2-E:70; W2-Q Q4).
- **Interp died / obs survived.** YES.
  - Wave-1 "needs its distractors" (an oddity) became a mechanism class.
  - W2-E's "the first distractor is the strobe" was refined by W2-Q: it is necessary, not sufficient.
  - CTC H5 ("HOLD family label predicts mechanism", CTC:47-55) FAILS even within one physics+env cell.
  - The "memory despite distractors" reading died for these 5. It is "memory triggered or clocked by
    distractors".
- **Cheapest decisive next test.** A register trace of 2c300c47 and 311c465f under the first-slot-kept
  jitter edit (W2-Q Q4).
  - It needs about 1 min of CPU per cell, with no search.
  - Its sharp prediction for 311c465f is that the write-enable flips on the parity of a
    decay-floor/mod-2 counter driven by the distractor magnitude (W2-E:29). If so, an amplitude-64 to
    amplitude-66 change should invert accuracy around .5, not merely lower it.
- **Cross-engine question (from CET X-5, lines 46-53).**
  - Herakles EvCA separates "correct at step T" from "correct and stable".
  - The strobe champions are correct only because the environment's input sequence is fixed.
  - Question: does an EvCA rule evolved under a fixed initial-condition ensemble use the ensemble's own
    regularities as a clock in the same way? Would a jittered-schedule control of the kind W2-Q used
    (stochastic gap occupancy) separate those rules?
  - Also relevant: the CTC deeper compression (CTC:57-67) asks why the latch dominates HOLD. The strobe
    is a counterexample in which search chose a schedule-exploiting solution at the same cost.

### SR-03. 4781b0a1: an integration law whose vote travels only through a loop between adjacent cued sensors
- **Observation (aggregated).**
  - 4781b0a1 is C1's only INTEGRATION call (lo99 .742, replicated pooled at 3.4 SE; W2-K:37-41).
  - It is CLUSTER-BOUND (W2-I F3):
    - it fails at one hop on tree-like graphs (Schreier .512/.517);
    - it recovers on a K4-clique graph (.725);
    - its D replicate 8743da7f behaves the same.
  - Its pivotality (D_piv .10-.12) is below every plant tested: count threshold .30, lossy majority
    .38-.44 (HANDOFF:112-113; PTE_CAUSAL_AUDIT_2026-09-30.md:113-116).
  - Under W2-M's DICT ablation (only sensor 0 cued), the champion scores EXACTLY .500 with zero variance
    (W2-M/out/score_signal.json: lo99 = hi99 = .5). The integrating plant scores .651 on the same worlds,
    and 8743da7f scores .566 at the same physics.
- **W2-AG checks [V].**
  - (a) Static (decompiled.json):
    - a sensor latches the sign of its last cue (S1 = GT(S1+SENSE, CNT0));
    - it emits every awake tick while latched;
    - its payload PAY1 = MAX(IN0_1, SENSE). After its 2-tick cue window it therefore forwards only what
      it HEARS from other sensors;
    - the actuator reads S0 = IN0_1 - 3, the last wake window's payload sum.
  - (b) Trace (dict_trace2_4781.json; readouts at t0+16):
    - under DICT the actuator sees one 2-tick burst of 253 about 4 ticks after onset, then nothing;
    - S0 = -3 at every readout, so every mirror pair is exactly .5;
    - under the normal schedule the payload REVERBERATES and grows (sums up to 14817) and is still
      present at readout ticks.
  - (c) Decisive check, prediction written before the run (ag_dict2.py; 16 held pairs):

    | sensors cued | acc [99% CI] |
    |---|---|
    | all 5 | .784 [.714, .846] |
    | one adjacent pair (ring distance <= 3) | .573 [.529, .620] |
    | one non-adjacent pair (both still one hop from the actuator) | .500 [.500, .500], pair sd 0 |
    | sensor 0 alone | .500 [.500, .500] |

  - Reading [I]: the law's information carrier is mutual reverberation between adjacent positive
    sensors. A lone sensor, or two that cannot hear each other, delivers nothing by readout time.
  - This one mechanism plausibly accounts for four anomalies at once:
    - DICT = .500 exactly;
    - cluster-boundness: sensors must be mutual neighbours, as in K4 cliques, which tree-like directed
      graphs lack;
    - low pivotality: one sensor matters only when it makes or breaks an adjacent positive pair;
    - the one-hop wall (SR-01): non-sensors never emit.
  - Wave-1 named "sensor-to-sensor relaying" as one candidate for the residue
    (PTE_CAUSAL_AUDIT_2026-09-30.md:116). This check supports it over W2-E S6's simpler "k=1 threshold"
    reading. A pure one-copy threshold on direct sensor traffic predicts DICT > .5, not exactly .5.
- **Sources.**
  - wave2/W2-I/REPORT.md:98-104.
  - wave2/W2-E/REPORT.md:30 (S6).
  - wave2/W2-M/REPORT.md:119-123.
  - wave2/W2-K/REPORT.md:37-41 and :223 (its NEITHER census class is a coin flip).
  - HANDOFF:112.
- **Status.**
  - REPRODUCED: cluster-bound, DICT .500 (W2-M's number re-derived by W2-AG on 16 pairs), low
    pivotality.
  - The mechanism is a CANDIDATE with one passed must-fail/must-pass pair (n = 16 pairs, one cell).
    Not promoted.
- **Interp died / obs survived.** YES.
  - "Joint carrier" and "not a majority" were weakened in Wave 1 (HANDOFF:21-24).
  - W2-E's "k=1 threshold explains D_piv" is contradicted by DICT = .500.
  - The observations all survived, and now connect.
- **Cheapest decisive next test.**
  - Re-run W-V's pivotality definition on a plant that implements the adjacent-sensor reverberation
    loop. The prediction is D_piv about .1.
  - Or, cheaper: cut only sensor-to-sensor edges, keeping sensor-to-actuator edges, at the native ring
    (a graph-variant patch like W2-I's). The prediction is a collapse to .500.
  - Either costs under 0.05 core-h.
- **Cross-engine question (from CET X-3, lines 32-38, and X-1).**
  - Archaeon FF-20 classifies PTE packets as superposed, non-material state.
  - Here the carrier is not a packet at all but a self-sustaining exchange between two sites, which
    exists only while both hold the same sign.
  - Question: does FF-20's "material" test have a category for state that exists only as a recurrent
    interaction between sites?
  - Does Aether's "who fired" carrier (X-1) also show the pattern "a lone source is inert, a mutually
    coupled pair carries"?

### SR-04. Near-ceiling MAJ integrators that the INTEGRATION ruler can never see
- **Observation.**
  - At the M3-family physics (ring 100, radius 3, async .8, lat 4 = delta 4, loss .3), W2-M derives:
    - any-program ceiling .701 (W2-M/out/attain.json: ceiling_any_program .7008);
    - single-sensor ceiling .590.
  - W2-AG joined score_signal.json with row physics. 11 SIGNAL rows sit at that physics key, and 8 have
    champion lo99 > .590:
    - 0a23398f .695 (lo .648);
    - 18c218f5 .699 (.650);
    - f6b623cd .686 (.642);
    - 1a86071f .680 (.635);
    - 88a1a041 .671 (.626);
    - 88f94654 .652 (.620);
    - 84c8c1d1 .648 (.618);
    - 57650798 .630 (.594).
  - Six of them beat W2-M's single-sensor transport (DICT plant minus champion, CI below 0).
  - So these champions exceed a sound single-sensor ceiling (they integrate) while sitting within
    .002-.05 of the any-program ceiling (they are near-optimal), and INTEGRATION (> .70) is unattainable
    by construction.
- **Sources.**
  - wave2/W2-M/REPORT.md:126-141 (F3) and :102-124 (F2).
  - wave2/W2-P/REPORT.md:52 (18c218f5 margin .038 under W2-P's optimistic model).
  - wave2/W2-L/REPORT.md:336-341 (relay-only MAJ range [.5, .70]).
  - HANDOFF:34 ("no integration beyond one sensor" WEAKENED).
- **Status.** REPRODUCED from recorded outputs (W2-AG join; no new runs). The ceilings are analytic.
  The ceiling rests on W2-M's assumption that S0 is uninformative at an asleep readout (W2-M:141).
- **Interp died / obs survived.** YES.
  - "No integration beyond one sensor" (C1) died for these cells.
  - "No INTEGRATION" there carries no information (W2-M:192).
  - The surviving observation is strange in two ways. C1 search reached about 97% of the physics bound
    at the M3 physics. And these same cells carry the C1b label TRANSPORT+RULE_SWITCH, a label that
    says nothing about integration.
- **Cheapest decisive next test.** The DICT-k curve (cue k = 1..5 sensors) at 0a23398f (W2-M Q7).
  - Integration predicts monotone growth from about .58 at k = 1 to .695 at k = 5.
  - A count threshold predicts a step.
  - Cost: about 0.02 core-h.
- **Cross-engine question (from CET X-5).**
  - Das, Mitchell and Crutchfield's GA particle rules are named as prior art for evolved carriers that
    approach a task optimum.
  - Question: does Herakles score its EvCA rules against a per-physics optimum, so that "near ceiling"
    and "below an absolute bar" can be told apart? PTE's absolute bar hid the near-ceiling cells.

### SR-05. 613162a3 and the global-topology paradox
- **Observation.**
  - 613162a3 (MAJ, global) is the ONE SIGNAL row where the champion beats every plant: .682 vs W2-M
    .590; paired, the champion is above.
  - It is also the one global law that keeps .751 on a random graph with inward placement.
  - Mechanism: every site emits every wake and integrates broadcast payloads, so every site holds a MAJ
    estimate. Cross-trial residue lag-1 is .529.
  - Meanwhile:
    - global has the HIGHEST light-cone ceiling (.912) but the LOWEST ceiling-normalised A0 plant score
      (.038; W2-U F4);
    - A1 RELAY on global is 0/11, though one hop by construction (W2-AC Q3);
    - all 7 global MAJ rows stay UNPLACED (W2-M F7).
- **Sources.**
  - wave2/W2-E/REPORT.md:25-26 and :73-85.
  - wave2/W2-M/REPORT.md:109, :117 and :178-180.
  - wave2/W2-I/REPORT.md:69.
  - wave2/W2-U/REPORT.md:129, :135.
  - wave2/W2-AC/REPORT.md:141.
  - wave2/W2-K/REPORT.md:44-48 (packet clause replicated, 2.96 SE).
  - HANDOFF:105-106.
- **Status.** OPEN. The two Wave-1 strange readings are EXPLAINED-AWAY (SR-X1, SR-X2).
- **Interp died / obs survived.** YES.
  - "Whole-network chaos" and "shuffle beats normal" died.
  - What survived: a broadcast integrator that out-performs designed plants on the topology every
    other measure calls worst.
  - [I] The light cone ignores fanout on global (W2-S F6; W2-J F2), which explains the
    ceiling/normalisation part, but not why the champion beats the plant.
- **Cheapest decisive next test.** W2-E's own test: score the network majority of S0 signs as the
  readout (prediction >= .72), with decay_shift 0 as a must-fail.
  - Add LC2/epidemic re-normalisation of the global A0 cells.
  - Both are analytic or one eager run.
- **Cross-engine question (from CTC H6, lines 80-82).**
  - H6's falsification line asks: "is anything search-reachable that we cannot design? Not yet
    observed." 613162a3 is the standing candidate counterexample at global topology.
  - Question for any engine with hand-designed baselines: is there a substrate regime where evolution
    beats design? In PTE the candidate regime is the one with sampled fanout and no routing control.

### SR-06. Anti-copy FLIP champions
- **Observation.**
  - 964053bb answers -y_{k-1}, the negated last teacher, on 100% of scored trials. Same-cue accuracy is
    .000, changed-cue 1.000, overall .484, B = .500.
  - 22104294 does so on 83-88% of trials.
  - 34f84c6b and f30f89b0 are partial.
  - 964053bb sits at a row where an epidemic bound caps ANY program at .552 (q_max .105;
    W2-S/out/epidemic_bound.json).
  - Evolve champion 545aff2f is the mirror case: TEACHER-COPY, same-cue .816 and changed-cue .132.
  - The anti-copy policy is exactly the "invert on change" half of FLIP inference, without the "hold
    if same" half. It earns no accuracy at all.
- **Sources.**
  - wave2/W2-S/REPORT.md:68-80 (F2), :82-97 (F3) and :152-160 (epidemic table).
  - W2-S/out/t1_table.md:18-22.
- **Status.** REPRODUCED (W2-S, 32 pairs, 44/44 recorded champions bit-exact). The reason is OPEN.
- **Interp died / obs survived.** Partly. W2-L's FLIP_CHANGE certificate died because of these
  champions (W2-S F2). The observation (evolution producing a deterministic, payoff-free anti-teacher
  latch) is unexplained.
  - [I] P-3 (ledger :175-203) shows the w_any bonus drives selection when accuracy is flat. A teacher
    latch makes state twin-sensitive, so it plausibly earns the .02 bonus. Unchecked.
- **Cheapest decisive next test.** Recompute sens_any and sens_act for 964053bb, 22104294 and 545aff2f
  on their training seeds (no search).
  - Prediction: sens_any is at the top of their generation's population.
  - That makes them shaping products, a crisp example of the bonus building inference-shaped parts.
- **Cross-engine question (from CET X-4, lines 39-45).**
  - X-4 lists interventions that cannot fire. The anti-copy champion is the behavioural analogue: a
    component that computes exactly half of the target function and is invisible to the score.
  - Question: do other seats' evolved artefacts contain fully formed sub-functions with zero task
    payoff, and which fitness term built them?

### SR-07. Rule-mosaic lottery (one live rule plus one dead rule)
- **Observation.**
  - With setrule = 0 and rules > 1, each site keeps its random initial rule. In HOLD only the
    ACTUATOR's rule matters (R^2 .69-.96).
  - In 11/15 cells one pinned rule scores exactly .500: it never writes a non-zero S0, so it is dead.
  - Normal accuracy equals the mixture. For 0187372b, (14 x .503 + 18 x .979)/32 = .771 against .768
    measured.
  - The best pin is +.09-.21 above normal.
  - Held >> train (up to +.22) is the 8-final-pair draw over this mixture.
  - Lottery cells are over-represented among census corrections (OR 6.5, p = .019).
  - 437ca0ac (MAJ) is the opposite case: both pins are at chance, normal is .538. It NEEDS the mosaic.
- **Sources.**
  - wave2/W2-E/REPORT.md:37 and :108-116 (N1).
  - wave2/W2-Q/REPORT.md:73-103, :124-127 (W2-E's r0 split corrected) and :134 (437ca0ac).
  - wave2/W2-A1/REPORT.md:142.
  - Ledger :345-346, :491-494.
- **Status.** REPRODUCED (bit-exact); mechanism EXPLAINED (engine.py:155-157 r0 init). Consequences
  OPEN: does a duplicated-rule seed recover the best pin (W2-Q Q1)?
- **Interp died / obs survived.** YES.
  - W2-E's "neighbour rules presumably matter" died: unmirrored-seed bug, W2-Q F6.
  - "Held >> train" as an anomaly died into this mechanism.
  - What survived is strange: a cell's "law" is a per-world coin flip between a working program and a
    dead one. "The cell's mechanism" is not well-defined (W2-Q:151).
- **Cheapest decisive next test.** Re-run W-F swaps for 0187372b, 7ca102eb and b4e404f6 on r-pinned
  worlds (W2-Q Q2).
  - Prediction: census classes become stable at 64 worlds.
  - CPU, minutes.
- **Cross-engine question (from CTC "deeper compression", lines 57-67).**
  - CTC proposes that which solution evolves is set by small contingencies.
  - Here the contingency is per world, not per search. One genome is two mechanisms.
  - Question: in engines whose genomes carry inactive alternatives, is accuracy reported per
    realisation or as the mixture?

### SR-08. M2 (4ab2ba01): latch-as-needle vs flat basins; latency-label-bound; needs the channel
- **Observation.**
  - A 4-line latch scores 1.000 at M2 physics. Yet HOLD search there found in-flight echoes (C1b 3/3)
    and, in W-L's run, a local integrator.
  - 1-mutant robustness:
    - latch: 43% of mutants fall to chance;
    - M2: 13%;
    - integrator: 9%.
  - M2 needs the channel (zero_comm .5 forced: S0 := IN0_0 + IN0_1).
  - M2 is LATENCY-LABEL-BOUND:
    - .510 on the C1 random graph;
    - .865 restored on a Schreier graph that carries the ring's per-port delay labels (2-5 ticks).
  - Its in-flight signed sum differs between twins in 87% of pairs but predicts the previous target only
    at .524 [.464, .582] (W2-B:311).
- **Sources.**
  - wave2/W2-E/REPORT.md:27-28 (S3, S4).
  - wave2/W2-I/REPORT.md:107-110.
  - wave2/W2-K/REPORT.md:18-21 (M2 label kept 62.5%).
  - HANDOFF:107-110.
- **Status.**
  - Facts REPRODUCED.
  - Builder equivalence EXPLAINED (W2-E S3, exact).
  - "Needle vs flat" is OPEN [I] (47 mutants, 8 worlds).
- **Interp died / obs survived.** YES.
  - "Expressibility" died: the latch exists in space.
  - "Same physics, different mechanism class" became seed contingency (p ~ .2).
  - The accessibility puzzle survived.
- **Cheapest decisive next test.** W2-E Q3: a random-prefix census of 2-4-instruction programs at M2
  physics, counting latch-like vs echo-like with acc > .55.
  - Smaller N on CPU is feasible.
- **Cross-engine question (from CTC "deeper compression", lines 64-67).**
  - CTC states that at M2, "latch (4 instr) vs echo (4 instr); the latch dominates, so something beyond
    instruction count ... must also enter".
  - SR-08 says the latch does NOT dominate under search at M2, and the extra term may be mutational
    accessibility.
  - Question for any GA-based seat: is mutational robustness of a solution class measured alongside its
    cost when predicting which class evolves?

### SR-09. FLIP landscape: an isolated peak, unclimbed copy basins, and relay_flood's cue-repeat hold
- **Observation.**
  - At d9cc FLIP (6f82f9c7, one search seed):
    - the 16-line P-FLIP plant is an isolated peak: 6% of mutate() offspring keep function, and every
      line is load-bearing;
    - relay_flood sits in a .602 basin;
    - a 14-line in-space RELAY_LATCH reaches .688 and passes SIGNAL, COMM_DEPENDENT and FLIP_FEEDBACK;
    - the champion reached neither (.479).
  - Across FLIP, the recorded relay_flood is >= the champion in 40/82 rows (W2-L:146-147).
  - relay_flood's FLIP edge: re-emission happens only on cue change, so a repeated cue leaves y_{k-1}
    latched. The analytic form is acc = 1/2 + a*e/4, and the teacher echo HURTS.
  - No copy-class policy exceeds B = .75 (W2-S enumeration).
- **Sources.**
  - wave2/W2-D/REPORT.md:50-67 (F3), :99-109 (F6), :144-147 (F9).
  - wave2/W2-L/REPORT.md:72-139 (F3-F5).
  - wave2/W2-E/REPORT.md:39 and :87-105 (N3).
  - wave2/W2-S/REPORT.md:82-97.
- **Status.**
  - REPRODUCED: W2-L reproduced W2-D bit-for-bit; W2-E 926328ee fresh .633.
  - The a8185ca9 low tail is NOT REPRODUCED (.336 -> .514).
- **Interp died / obs survived.** YES.
  - W2-D's "the echo carries block-mapping information" died (W2-L F3).
  - W2-L's "changed-cue accuracy is exactly 1/2" was corrected to <= 1/2 (W2-S F3a).
  - PREREG s11's "relay_flood cannot solve FLIP" is false at some physics. That is reported, not
    changed.
  - What survived: a landscape in which search climbs to none of three nested, increasingly good,
    in-space programs.
- **Cheapest decisive next test.** Seed RELAY_LATCH (not relay_flood) at 6f82f9c7 and measure k-field
  recovery to P-FLIP (W2-L Q4, W2-D Q1-Q3).
  - This needs search authorisation.
  - The no-search proxy is the exhaustive 1-mutant set of RELAY_LATCH: count mutants with changed-cue
    accuracy above .55.
- **Cross-engine question (from CET fossils line 60-62, verilog-uart2bus "mid-bit sample = anti-D-A").**
  - relay_flood's hold-on-repeat is a sampling-phase strategy.
  - Question: do the Techne fossils (uart2bus, generic-fifo) offer a known minimal circuit for
    "invert on change, hold on repeat" that could serve as a stepping-stone plant?

### SR-10. Champions one tick out of tune, concentrated in one cell family
- **Observation.**
  - 62a7fff9 gains +.055 [.045, .066] at latency+1. Its latency sweep peaks at +1, and delta-1 gives
    .917.
  - Over 30 champions, 4 of 16 comm champions are credibly mis-tuned (+.06-.09 confirmed). All 4 are in
    the ring d3, sync period 2, lat 1/1/1, delta 8 RELAY family.
  - lat+1 and delta-1 agree in sign in 5/6 rows.
  - e9196cae is the mirror case: its gap is too short.
  - HOLD is timing-inert (|gain| <= .0065).
- **Sources.**
  - wave2/W2-E/REPORT.md:40 and :119-125 (N4).
  - wave2/W2-R/REPORT.md:78-121 (F4, F5).
- **Status.** REPRODUCED. "Gap vs parity" is OPEN (delta +/- 1 also flips the env-period parity under
  sync 2).
- **Interp died / obs survived.** YES. The C1 transplant "improvements" were partly an unpaired-normal
  artefact (c16d5231 async .7 is NOT REPRODUCED), but 62a7fff9's gain survived and generalised to a
  family.
- **Cheapest decisive next test.** Split native per-trial accuracy by trial-onset parity for f7e62fe3,
  4316f167 and e9196cae (W2-R Q3).
  - Zero search, seconds of CPU.
  - Loss concentrated on one parity means parity, not gap.
- **Cross-engine question (from CET X-5 and fossil uart2bus, lines 46-49 and 60-61).**
  - The mid-bit sampling fossil is the engineered answer to "sample at the right phase".
  - Question: does Herakles EvCA's "correct at step T" scoring produce rules tuned one step off the
    scoring step, i.e. does a deadline-scored GA leave its own timing slack?

### SR-11. LATCHED-PARTIAL: early-latch champions
- **Observation.**
  - 12 NULL cells (11 RELAY, 1 MAJ): first-half per-trial accuracy is .55-.58, second half about .50.
  - The readout last changes at a median tick of about 1-43 out of 228.
  - The schedule is live, energy is full, emissions continue.
  - The champion answers the first one or two trials, then freezes its readout.
  - 11 of the 12 have an in-space relay_flood plant at .63-.98 (W2-W:141).
  - Contrast cases with the readout frozen but no early competence: 89bd6fdb dies of energy;
    6e0ca725 is transient.
- **Sources.**
  - wave2/W2-T/REPORT.md:169-175 (F4).
  - wave2/W2-O/REPORT.md:104-108 (F3).
  - wave2/W2-W/REPORT.md:139-144.
- **Status.** REPRODUCED (trunc_probe, 12/12).
- **Interp died / obs survived.** YES. "TRUNCATED measurement" (W2-O checklist A4) died. The
  observation was renamed and kept.
- **Cheapest decisive next test.** Trace why the readout freezes in one cell: which register stops
  changing, and whether a sensor latch or the actuator stops being written.
  - One eager run.
  - SR-03's latch structure (a set-reset latch never reset) is a candidate.
- **Cross-engine question (from CET X-5).** "Correct at step T vs correct and stable", inverted: these
  champions are correct early and stable-but-wrong later. Does EvCA see the analogous early-correct,
  then frozen, class?

### SR-12. The decay floor as an exploited hidden substrate (cross-cutting; inferred)
- **Observation.**
  - DESIGN s10: positive values below 2^decay_shift never decay; negatives decay to 0.
  - It appears in three unrelated places:
    - (a) 613162a3's "persist 110" comes from S3+1 becoming a permanent +3 emitter (W2-E:26, :83);
    - (b) 311c465f's clock is described as an "XOR/floor-decay/mod-2 write-enable clock" (W2-E:29);
    - (c) P-FLIP fails at decay > 0 because MULQ bookkeeping truncates and positives floor at 1
      (W2-L:55-58).
  - W2-A1 F8 adds two more undocumented sign asymmetries: saturate and the routing write.
- **Status.** OPEN [I]. No check isolates the floor.
- **Interp died / obs survived.** N/A (new cross-reading).
- **Cheapest decisive next test.** Monkeypatch symmetric decay (in a scratch copy) for 311c465f and
  613162a3.
  - Prediction: 311c465f collapses; 613162a3's persistence vanishes and its accuracy is unchanged.
  - Two eager runs.
- **Cross-engine question (from CET X-4).** Is any other seat's evolved behaviour resting on an integer
  rounding asymmetry of its substrate? X-4's "interventions that cannot fire" has a mirror image here:
  substrate properties nobody intended to provide, which evolution uses.

### SR-13. Divergence without use: 53e569f4
- **Observation.**
  - 53e569f4 (RELAY torus N100, d1, async, loss .6): div_frac .99, held .719, reach 9.1.
  - The HOLD-global cluster shows the same twin divergence (.43-.51) with zero_comm = held exactly
    (divergence unused).
  - For 53e569f4, whether its spread is used is untested.
- **Sources.** wave2/W2-E/REPORT.md:41 and :126-128 (N5), :81.
- **Status.** OPEN.
- **Interp died / obs survived.** N/A.
- **Cheapest decisive next test.** An emitter-masked run (deliver only sensor emissions; W2-E Q6).
- **Cross-engine question (from CET X-2, lines 20-31).** This is the Cosmos C3 split between P1
  (decodable) and P2 (causal utility) in its plainest form. Would the Cosmos P1/P2 certificate call
  53e569f4's network-wide divergence P1-only?

### SR-14. Stale-information accuracy above the light-cone ceiling
- **Observation.**
  - Held accuracy reaches .518 where no current-trial information can reach (4 sync rows).
  - A0 plant accuracy reaches .589 at ceiling .5. 121 of 259 ceiling-.5 cells are above .5.
  - Negating trial k's cue changes S0 at readout k in 0 worlds.
  - Fresh runs: means about .5 (.45/.53 for the top cell).
- **Sources.**
  - wave2/W2-P/REPORT.md:181-187 (F4).
  - wave2/W2-U/REPORT.md:147-154 (F5).
  - wave2/W2-T/REPORT.md:159 (29 NULL cells slightly above bound .5).
- **Status.** EXPLAINED-AWAY: late cues from earlier trials add zero-mean noise.
  - Residue (W2-AG, rows join): over the 259 ceiling-.5 A0 cells, mean .5015 and sd .0217. The top cell
    (74b13c29, .589) is 4.0 SD out, against about 2.9 SD expected for the maximum of 259 Gaussians. The
    next is .5625 (2.8 SD).
  - So one draw is heavy-tailed, plausibly from per-cell heterogeneity in how much stale information
    leaks.
- **Interp died / obs survived.** YES. "The bound is broken" died. The tail and the FP-rate question
  survive (W2-P Q5).
- **Cheapest decisive next test.** Simulate the lo99 > .55 false-positive rate under stale noise alone
  on the 4 sync rows (W2-P Q5).
- **Cross-engine question.** None found in the material read; omitted rather than invented.

### SR-15. Sensitivity climbs while accuracy has zero variance
- **Observation.**
  - In the median NULL run every genome scores exactly .5 until generation 5.
  - In 40 runs accuracy variance is zero for all 36 generations, yet population sens_any rises
    .0002 -> .008-.058.
- **Sources.** wave2/INFERENCE_LEDGER.md:175-203 (P-3).
- **Status.** EXPLAINED-AWAY: f = acc + .10*max(sens_act, 0) + .02*sens_any, so with accuracy tied,
  truncation selects on the bonus.
- **Interp died / obs survived.** YES. "MEMORY_WITHOUT_USE / REACH_BEYOND_HOP on NULLs as substrate
  facts" died into shaping products. Kept because SR-06 may be its behavioural fossil.
- **Cheapest decisive next test.** The w = 0 A/B (search; needs authorisation).
- **Cross-engine question.** None from the material read.

---------------------------------------------------------------------------------------------------
## 2. The case for the top 3

**1. SR-01, the sharp one-hop wall.**
- The strangeness is the exactness, not the shortness.
- 13 of 14 two-hop conditions have a DEGENERATE interval (lo99 = hi99 = .500). The readout is identical
  in both twins.
- So nothing from any trial reaches two hops, not even the stale cross-trial residue that does leak
  elsewhere (SR-14).
- This happens on the laws' own rings, at physics where a 12-line flood carries two hops at .97.
- The static decompile turns it into structure: in 4 of 5 single-rule laws, sites that never sense can
  never emit.
- The one exception (c16d5231, zero-payload emissions) is the one condition with any variance.
- C1 search therefore produced sensor-broadcast laws, not weak relays. Every topology,
  size and transfer statement downstream depends on that.
- It is the observation most likely to be normalised into "transport is short", and the one whose
  exact form is most informative.
- It costs one emitter census to make it structural across all 69 SIGNAL champions.

**2. SR-02, distractor-strobed memory and the parity clock.**
- Evolution recruited the environment's own fixed schedule, and in 311c465f even the bit pattern of
  the distractor amplitude (63 and 65 kill it, 64 works), as a control signal for memory.
- Strobe and robust champions sit at identical physics and env, so the mechanism class is decided by
  the search seed (CTC H5 fails inside one cell).
- Nobody designed these mechanisms. They are the closest PTE has to CTC H6's missing case ("anything
  search-reachable that we cannot design"), even if they are easy to design once seen.
- They are also a live hazard for any HOLD-family claim: 6.5% of HOLD's above-chance accuracy rests on
  the schedule.

**3. SR-03, 4781b0a1's adjacent-sensor reverberation.**
- The single law carrying C1's only INTEGRATION label has four separately reported oddities:
  - cluster-bound;
  - pivotality below every plant;
  - a coin-flip census class;
  - DICT exactly .500.
- Wave 1 listed its residue as "do not normalise away".
- W2-AG's pre-stated check gives one candidate mechanism for all four:
  - an adjacent cued pair carries .573;
  - a non-adjacent pair (both one hop from the actuator) and a lone sensor carry EXACTLY nothing;
  - the trace shows the payload surviving to readout only by reverberating between latched sensors.
- If this holds up, C1's one "integrator" is a recurrent agreement detector between neighbouring
  sensors, and integration in PTE has a carrier that no packet-level instrument was built to see.
- It must stay a candidate: one cell, 16 pairs. Two cheap tests in its entry would falsify it.

Runners-up:
- SR-04: near-optimal integrators that the ruler cannot see, which is the strongest ruler lesson.
- SR-05: the standing candidate for "evolution beats design".
- SR-06: a payoff-free anti-teacher latch.

---------------------------------------------------------------------------------------------------
## 3. Archive: Wave-1 strange items explained away (kept for discoverability)

| id | Wave-1 item | source | status and explanation |
|---|---|---|---|
| SR-X1 | 613162a3 shuffle_dest .72 > normal .688 | HANDOFF:105; W2-E:25; W2-A1:67-76 | NOT REPRODUCED (fresh -.015 [-.045, .016]). On global, shuffle_dest is a routing re-draw: a control equivalent by construction |
| SR-X2 | 613162a3 whole-network "chaos" (div .98-1.00) | HANDOFF:106; W2-E:26, :73-85 | EXPLAINED-AWAY: linear one-hop broadcast integration plus the decay floor. div_frac reads unused divergence. The survivor is SR-05 |
| SR-X3 | M2 echo vs W-L integrator: same physics and GA, different class; builder never checked | HANDOFF:107-109; W2-E:27 | EXPLAINED-AWAY: builders bit-identical; search contingency (p ~ .2). The survivor is SR-08 |
| SR-X4 | 4ab2ba01 needs the channel although a 4-line latch scores 1.0 | HANDOFF:110; W2-E:28 | REPRODUCED as fact (latch 1.000 verified). The puzzle moved from expressibility to accessibility (SR-08) |
| SR-X5 | 311c465f needs its distractors (.76 -> .55) | HANDOFF:111; W2-E:29 | REPRODUCED and mechanised (SR-02) |
| SR-X6 | 4781b0a1 pivotality below every plant | HANDOFF:112 | REPRODUCED. W2-E's k=1 explanation is contradicted by DICT = .500; the candidate mechanism is in SR-03 |
| SR-X7 | The "size-free" law is the one that failed reproduction | HANDOFF:113; W2-E:31; W2-B:238 | EXPLAINED-AWAY: label conflation. The frozen law transfers (.875-.893); what failed is SEARCH reproducibility. Size-freedom is forced for one-hop or local laws |
| -- | c16d5231 async .7 transplant "gain" | W2-E:124 | NOT REPRODUCED (+.015 [-.009, .039]) |
| -- | a8185ca9 FLIP relay low tail .336 | W2-E:39, :100 | NOT REPRODUCED (fresh .514); a 16-pair tail draw |
| -- | W2-E N1 "neighbour rules presumably matter" | W2-Q:124-127 | EXPLAINED-AWAY: the unmirrored-seed r0 recomputation was wrong in 16-38% of worlds |
