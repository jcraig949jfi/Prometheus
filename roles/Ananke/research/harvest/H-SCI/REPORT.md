<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/H-SCI; sha256(report)=f73661d50a59811c; delimited; see REPORT.provenance.json -->
# H-SCI: independent scientific critique of PTE as a research instrument

Worker H-SCI (Ananke harvest), 2026-09-30. This is an inference task: I read
the engine and task code, the preregistrations, the C1/C1b reports, every
worker report W-A..W-Z, and the syntheses. I recounted a few numbers from the
saved rows. I ran one small new analysis: a normal-run agreement check,
CPU only, 2 threads, about 30 s (files listed at the end).
I treated the syntheses as claims to test. I made no edits outside this
directory and no git writes, and I read nothing under prometheus/cosmos/c3_holdout_D*/.

Evidence keys used below:
- ROWS = roles/Ananke/pte/c1_rows/cells.jsonl.gz (6596 rows).
- C1R = roles/Ananke/pte/c1_report/REPORT.md.
- WX = roles/Ananke/research/workers/W-X/REPORT.md.

## 0. Findings that change the reading of the record

F1. **Nearly all evolved "transport" in PTE is ONE hop.**
- The task dial d is a *geometric* distance, not a hop count (envs.dist_matrix, envs._pick_at).
  - On a ring or torus with d <= radius, the actuator is a direct table neighbour of the sensor.
  - On the global topology every pair is at distance 1, so d does nothing there.
- Recount from ROWS, over evolve cells with held lo99 > .55:
  - RELAY (50 cells): 35 are one-hop ring/torus tasks, 4 are global, and 10 are smallworld (9 of them with d = 1).
  - Only 2 RELAY cells need more than one hop: ring 925caa3a (d5, held .578) and smallworld 882525a9 (d3, held .591).
  - MAJ (19 cells): 18 are one-hop, 1 is global.
- The recorded twin assay agrees:
  - bbef66a1, 31cd2a8a and 62a7fff9 have reach 3.0 and beyond_hop 0.0 (C1R s7).
  - c16d5231 is the exception (beyond_hop .88).
- Wave C's RELAY transfer to d5/delta16 scores 0.500 (C1R s6), because d5 on a radius-3 ring is two hops.
- So the substrate "communicates" almost only by direct broadcast from the sensor to its neighbour.

F2. **The main comm-dependence control cannot fail.**
- zero_comm is exactly 0.500 in 213/213 RELAY rows, 174/174 MAJ rows and 95/95 XOR rows of ROWS.
- This is forced by construction:
  - The actuator is never the sensor.
  - Mirror partners share every physics draw (assays.evaluate: ws = seeds[m - m%2]).
  - With no packets, the actuator's trajectory is therefore identical in both twins, so the pair mean is exactly .5.
- Consequences:
  - COMM_DEPENDENT (PREREG s7) equals SIGNAL for every comm family. P4's "8/352 COMM_DEPENDENT" is just a SIGNAL count.
  - The COMPETENT_WITHOUT_COMM detector can never fire for RELAY, MAJ or XOR.
- max_loss = 1.0 is the same control a second time.
- shuffle_dest sends each copy to a random site among 100-144, so any lattice mechanism collapses under it too.

F3. **Most mechanism claims come from ONE physics point:** ring 144, r3, fanout 8, pw 2, saturate cap 2, sync period 2, lat 1+1*dist+U{0,1}, plastic_route 1, wimm 1.
- 27 of the 50 RELAY SIGNAL cells sit at this point (n_sites ignored).
- Also at this point:
  - all 4 RELAY D-wave cells, the MAJ integration cell 4781b0a1, and the HOLD M2 echo 4ab2ba01 with its fresh champions;
  - the W-I 20-cell panel, the W-L n-back work, and the W-S/W-T RELAY cells (c16d5231 and its descendants).
- All of these descend from ONE A1 census cell, 86fc0105 (held .598, lo99 .576), through wave B/B2 transects and wave C re-evolution. The ROWS parent field shows this.

F4. **The selection bonus is a teacher path that favours one-sided codes.**
- Fitness is acc + 0.10*max(sens_act, 0) + 0.02*sens_any (search.py L94).
- sens_act = mean sign((S0_lead - S0_twin) * y) (assays.py L80-84).
- A rectified code (S0 in {0, +x}) earns the full +0.10 while scoring only 0.75, because ties score .5.
- This is a plausible, untested cause of several recorded patterns:
  - presence and "only the sensor fires" codes dominate (W-J: 29/32; W-C: 7/13);
  - the RECTIFIED joint classes (W-P);
  - one-sided readouts such as 95649e2c (−trials .49; W-H S3);
  - integrators appearing where they do not pay (W-L).
- The only record that raises it is backlog ANANKE-14. Nobody tested it.

F5. **C1's "no integration beyond one sensor" is an artifact of the ruler.** New check: sensor_agreement.json, 128 worlds, normal runs only.
- Method: for each scored trial with S0 != 0, I compared the readout's sign with each sensor's cue sign and with the 5-sensor majority.
- A reader that uses only sensor j can agree with the majority at most P(s_j = maj) = .667 (flip p = .3, analytic).

| cell | acc | best single-sensor agreement | majority agreement |
|---|---|---|---|
| 0a23398f (M3) | .699 | .685 | **.767** |
| f6b623cd (M3) | .693 | .665 | **.771** |
| 613162a3 | .721 | .694 | **.781** |
| 4781b0a1 (M4) | .766 | .773 | **.842** |

- All four champions aggregate several sensors, including the two M3 cells that sit at the ".70 single-sensor ceiling".
- The INTEGRATION label (lo99 > .70) cannot tell noisy multi-sensor aggregation from single-sensor relay.
- This analysis is descriptive and in-sample, not interventional.

---------------------------------------------------------------------

## 1. CHAIN AUDIT

Each boundary answers the brief's questions under these short labels:
- REACH: can the intended phenomenon reach this stage?
- EQUIV: are supposedly different conditions secretly equivalent?
- LEAK: teacher paths, leakage, shortcuts or hidden state.
- RULER: can the ruler tell the intended mechanism from cheap alternatives?
- +CTRL: does the positive control exercise the claim's causal channel?
- NULL: could a NULL come from search rather than physics?
- UNFALS: are there controls that cannot falsify their reading?
- IMPL: assumptions living in implementation rather than declared semantics.

### 1.1 World physics (engine.py, DESIGN.md, envs.py)

- **REACH.**
  - Physics is bit-exact against an independent oracle (185 tests; C1b packet s2), so the engine implements DESIGN.
  - The task layer (envs.py) has NO oracle, and it disagrees with the normative DESIGN.md s7 in two places, with no dated annotation:
    - DESIGN says targets are "EXACTLY balanced within an episode". Code uses i.i.d. coins plus mirror pairs; the envs.py docstring records that the balanced draft was rejected.
    - DESIGN places the MAJ actuator "at distance d from all sensors' centroid". Code places the sensors at distance <= d around the actuator (_pick_at).
- **EQUIV.**
  - d <= radius makes every ring/torus RELAY/MAJ task one hop (F1).
  - d does nothing on global topology.
  - HOLD ignores d and delta (C1 F5, already known).
  - Scaling N at fixed d is the same local problem, so "size-free" is expected by construction.
- **LEAK.**
  - Every world has identical, deterministic readout ticks (evaluate asserts ro_tick equal), a fixed period, and a fixed gap and delta.
  - So a pure timing coincidence can always solve a "memory" or "transport" task:
    - the M2 echo is tuned to the gap, with a parity sawtooth (gap 7 beats gap 8; W-A);
    - M3 works because delay == delta (C1_ERRATA E1).
- **IMPL.**
  - Integer floor decay and shifts are sign-asymmetric (DESIGN s10), so mirror twins are not physical mirrors. This helps rectified codes, and with them F4.
  - For global cells, `levels.dest_mode` can read 'all' while physics_from_levels silently forces 'sample' (e.g. 613162a3). Any analysis that reads dials from `levels` misattributes these cells.
- **UNFALS.** env_permutation (assays.run_controls) scores traces against other pairs' i.i.d. targets. It is near .5 for any policy (range .495-.512 in C1R s7), so it cannot fail. It also runs non-mirrored seeds (World(..., seeds)).

### 1.2 Search reachability (search.py, PREREG s4)

- **REACH.**
  - The GA runs pop 96 x 36 generations with 8 training worlds per generation.
  - Its champions are tails of the seed distribution. The champion's own budget reproduced the S1 and S3 champions in 0/4 seeds (W-H), and REPRODUCED needs only 1 of 2 replicates.
  - Across the whole census, RELAY competence reached .598 at best in A1 (C1R s3). Every RELAY above .8 came from boundary re-searches around one cell (F3).
- **LEAK.** The sens_act shaping bonus (F4) rewards graded and one-sided twin differences, not answers. It is a selection-side teacher path, not organism-side leakage, but it biases which mechanisms are reachable.
- **NULL.**
  - XOR and FLIP (0/165 SIGNAL) have no plant at any physics. relay_flood "cannot solve XOR or FLIP by design" (PREREG s11), and s11 itself says a NULL is informative only where plant viability shows the physics could carry the signal.
  - So the XOR/FLIP NULLs cannot currently be attributed to either physics or search. C1 F1 ("compositions the search never assembled") is a hypothesis, not a finding.
  - XOR looks cheaply expressible (MAX / SUB / GT give |x1 + x2|), but only if both cues arrive in the same wake window. That has never been tested.
  - Multi-hop relay is the same situation: 2 marginal cells, no multi-hop plant study, and relay_flood viable in only 1.9% of RELAY A0 cells.
- **+CTRL.** The reachability plants (W-G C-EFF/C-AVL, W-L P1S/P2S, W-H H1-H4b) are hand-built perfect solvers at the tested physics. They show a mechanism is expressible, not that it is reachable from the GA's starting distribution.

### 1.3 Packet generation (who fires, what is emitted)

- **REACH.** The dominant physical code is WHO FIRES:
  - 7/13 C1 specimens (W-C);
  - 29/32 fresh champions ("only the sensor fires"; W-J);
  - in W-I, 18 specimens show source presence, against 10 payload-value.
- **RULER.**
  - Under superposition, a presence difference is also a content difference.
  - So channel_content and channel_count swaps name the reader's register, not the physical code (W-C F7: P-FIRE / P-FIRE-SUM; W-I: 6 presence codes read as content).
- **LEAK.** The source keeps re-broadcasting the cue:
  - 78% of source copies in 78f3b0ec are re-broadcasts, and 79% in 4781b0a1 (W-T).
  - The readout uses only the first broadcast (c16d5231) or the latest (78f3b0ec).
  - Counts of cue-bearing traffic are therefore not causal weight (W-V).
- **UNFALS.**
  - shuffle_time draws the delay from U[1, LM-1]. At small LM this overlaps the native delays (W-A: U[1,7] against native delays near 4-6).
  - So C1 M1's "depends on WHERE packets go, not when" (shuffle_time .73-.88) is an underpowered negative.

### 1.4 Packet transport

- **REACH.** Only one-hop delivery reliably reaches the actuator in evolved champions (F1). The data contain no evolved multi-hop relay above .6.
- **UNFALS.** In comm families, zero_comm, max_loss and shuffle_dest are all forced to collapse (F2). "CAUSAL_SUPPORT" for RELAY then rests only on packet_ablation, which is also near-definitional for a relay.
- **EQUIV (misread).** The topology->random transplant re-picks the actuator at BFS distance d on the random graph, which is 3 hops for d = 3. That turns a one-hop task into a three-hop task.
  - The collapse to 0.500 (7/7) shows the law does not relay across hops.
  - It does not show that it "encodes lattice geometry" (C1 F2).
- **IMPL / window.** The C1 D-A defect (drop window [t0, ro) with delay == delta) was found and fixed by C1b (E1). The fix is sound.

### 1.5 Receiver semantics

- **REACH.** The receiver operator (sum / saturate / aloha) is behaviourally irrelevant at C1 physics: 29/32 codes put at most one arrival into each decision (W-J E2). It matters only where aggregation pays (lossless E6: one SUM count-code).
- **LEAK / shortcut.**
  - Several readouts overwrite S0 every wake (M2: S0 := IN_c'; 4781b0a1: S0 := IN0_1 - 3).
  - The readout is then a sampler of the last wake window. Nothing is retained at the readout, and any in-flight arrival in that window decides the answer.
- **RULER.**
  - S0 == 0 scores .5, so a one-sided code earns .75 while carrying no information on −trials. Together with F4 this rewards rectification.
  - On sync period-2 physics, the swap tick's clock parity changes the class (W-R), because asleep sites keep accumulating their inbox.

### 1.6 Aggregation

- **REACH.**
  - On the radius-3 ring with d = 3, _pick_at places the 5 MAJ sensors at a±3, a±2 and one of a±1. All five are direct neighbours of the actuator.
  - Aggregation is therefore the physics' own superposition sum followed by a threshold (nomographic; W-J).
- **RULER.** The C1 INTEGRATION label (lo99 > .70) misses noisy aggregation (F5). "No integration beyond one sensor reproduced" rests on that threshold.
  - The fresh replicates of 4781b0a1 (.636, .520) were never tested for aggregation.
- **+CTRL.**
  - W-V's MAJORITY positive control is a lossless, deterministic plant with fixed delays of 7/9/11.
  - The champion runs with loss .1 and fanout-8 sampling over 6 ports, which dilutes pivotality for any noisy summed code.
  - So "DISTRIBUTED-NONMAJ, not a majority" (D_piv .10-.12 against 1.00) cannot be told apart from "a noisy majority by count". The control does not exercise the champion's stochastic delivery channel.

### 1.7 State retention

- **REACH.**
  - The tasks never reward cross-trial retention: targets are i.i.d. and scored per trial. Remembering a past cue can only interfere.
  - So "no retention regime in champions" (W-E, W-G) is the expected outcome of the task design, not a property of PTE.
  - W-G's plants and W-L's n-back work show that retention is expressible (W-G C-EFF, C-AVL) and reachable as integration (W-L).
- **RULER.**
  - The mirror-pair swap cannot tell "carries cue k" from "carries the mirror sign of the whole history". Mirror partners differ in every cue.
  - n-back integrators (answer = sign of the summed history, .63 accuracy) give S-swap z ≈ −1 (W-N: −.95 to −1.08), the same as a clean lag-k store (P1S).
  - The single-cue twins (lens.cue_arrival_profile, lens_swap.twin_profile) can make this distinction, but the swap verdicts do not use them.
- **NULL.** W-L's success criterion (lo99 > .60) passes pure integrators (~.63), so "reached" does not mean "selective". Selective lag-2 storage was 0/4, from one budget, one physics and 4 seeds.

### 1.8 Behaviour

- **LEAK.**
  - HOLD puts the sensor at the actuator, with distractors (64) far below the cue (256), so a local latch is trivial (plants score 1.000).
  - HOLD "SITE 81/85" (W-F) is therefore forced by locality for non-communicating champions. W-F's "FAMILY SELECTS" rests on that one uniform family: within RELAY and MAJ no model beats ~.40.
- **EQUIV.**
  - The fixed trial schedule (1.1) makes a delay line indistinguishable from memory at the trained gap.
  - M2's accuracy is at chance for gap >= 12 (W-A). The delay-line reading is correct; the "memory" wording is not.
- **Unexplained.** 311c465f falls from .76 to .55 when distractors are removed (W-B). That is not a HOLD mechanism in any declared sense.

### 1.9 Assay and ruler (lens, lens_swap, swap_rel)

- **RULER.**
  - The absolute swap rule cannot call FLIP when normal accuracy is below about .62 (W-N, W-O), and the relative rule was built to fix this.
  - FLIP_REL certifies z < −1/2, not a complete transfer. The 42 low-accuracy cases split 24/16/2 by point z (W-Q) or 19/18/5 by the rho-conservative CI (W-U), so completeness is method-dependent.
  - At a fixed offset, the per-trial S/C/N class often just records whether ONE packet has landed yet. W-S: in 3 RELAY cells, the mixed phase is decided by one latency-jitter draw on the source's first broadcast, confirmed at 0x632.
  - Carrier classes of one-hop mechanisms are therefore latency and clock bookkeeping.
  - The truth-table classes (DICT / AND-OR / MUX / HIGHER; W-P) cannot tell a logical conjunction of two registers from a threshold on a sum of graded contributions. W-P's positive controls are binary-register AND/MUX plants; no sum-threshold plant was run.
- **+CTRL.** The known-answer plants are perfect solvers at noise-free readouts or with injected RAND readout noise (W-N). Low accuracy in real specimens comes from the carrier itself (integration, loss, jitter), which the plants do not reproduce.
- **UNFALS / validity.**
  - Pair-bootstrap CIs undercover when strata are small. W-R's async negative control failed its frozen rule at 0x620 (2 offsets) and was clean at 0x621.
  - Seed consistency of REL certificates is 92.7%, below the frozen 95% bar, at |z| .35-.6 (W-Z).
  - c1b.intact() treats NOT_APPLICABLE as intact (W-K).
  - The false-certificate (FC) table is validated only under simulated pair models (worst / realistic / hetero / DEGEN). Heavier-skew nulls are untested (swap_rel docstring).
- **IMPL.**
  - site_all swaps the site arrays of EVERY site, not the readout's.
  - The "S" in W-P's JOINT-2(S, Msum) for 4781b0a1 is therefore the sensors' S1: W-V shows the readout's own S1 is never mirror-different.
  - "Site" and "channel" are global partitions, not places.

### 1.10 Scientific conclusion

- The evidence rests on one physics point (F3), one GA configuration, and seed-namespace holdouts, with a single author.
  - The independent reviewers (Kairos #564, Elenchus #565) never replied (C1b packet s9).
- Counting has been by arm or verdict, not by independent unit. W-Q and W-U moved to specimen x offset groups: 733 verdicts are 249 groups.
- The workers' self-correction culture is real and good. Many errors were caught internally: C1b K1, W-I's identity, W-M's EVERY-mode break, W-Y's refutation of W-V's Kp reading.
- The drift is in the syntheses. They generalise from the ring-144 panel to "PTE" (carriers are trajectories; H6; operator axis) and count forced controls as causal verification.

---------------------------------------------------------------------

## 2. CLAIM AUDIT

| # | Claim | Where | Strongest alternative | Could existing controls falsify it? | Verdict | Smallest discriminating experiment |
|---|---|---|---|---|---|---|
| 1 | Headline: evolved RELAY machinery is comm-dependent, CAUSALLY verified, REPRODUCED and SIZE-FREE (frozen laws .875-.893 from N~100 to 2304 vs exactly .500 without comm) | C1_REPORT s1, s3 M1; C1R s7-8 | One-hop broadcast plus a latch at ONE physics point (F1, F3). Comm-dependence is forced (F2). Size-free follows from locality. The only scaled law, bbef66a1, FAILED fresh-seed reproduction (reps .572 / .506; C1R s7), while the reproduced cells were never scaled; "laws" is one law. | No. zero_comm, max_loss and shuffle_dest are forced. topology->random changes the task to 3 hops. | WEAKENED. Existence of evolved above-chance one-hop relays: SUPPORTED. "Causally verified machinery", "routed", "lattice-geometry-bound", "size-free" as findings: UNSUPPORTED (trivial or forced). | Evolve RELAY at d = 2*radius (forced 2 hops) at the d9cc physics, 8 seeds. Must-fail control: the one-hop champions evaluated with the actuator at d = radius+1. |
| 2 | "Evolution finds transport where the known design dies"; A0 viability is not a map of where communication is possible | C1_REPORT s2 | relay_flood is one multi-hop flood design. Evolved solutions are one-hop and need no flood. | Yes, in principle, but nothing was aimed at it. | SUPPORTED as a caution, but trivially: the two are different tasks in practice. | A one-hop plant (sensor broadcasts, actuator latches) in A0; compare its viability map with the evolved SIGNAL map. |
| 3 | "No integration beyond one sensor reproduced" (M4 not reproduced; M3 = MAJ at .69) | C1_REPORT s1, s3 | The ruler (lo99 > .70) is insensitive. Majority agreement exceeds every single-sensor agreement in M3 x2, 613162a3 and 4781b0a1 (F5). | No. The threshold cannot see noisy aggregation. | WEAKENED | Single-sensor cue-twin census (flip only sensor j's input) on M3 and on 4781b0a1's fresh replicates (.636, .520). Integration iff >= 2 sensors each move the readout. |
| 4 | M3 = transport landing on the readout tick; SETRULE is a one-time bootstrap from the zero-register default | C1b packet s12; CORRECTIONS K3; W-B | Timing coincidence (delay == delta) rather than a mechanism. That is the same reading, just deflated. | Yes, and they were applied: corrected window .501/.500, latency ±1, a one-rule law bit-identical, r never cue-dependent. | SUPPORTED (the "self-modifying, timing-locked" C1 reading is KILLED) | None needed. Optionally, a delay != delta physics to confirm the champion fails. |
| 5 | M2 = in-flight carrier (two-hop echo on payload 1); later "not memory, a tuned echo" | C1b s12; CORRECTIONS K1-K2; SYNTH 09-27 s2; W-A | A delay line enabled by the fixed gap and deterministic readout tick. The "held bit" is a scheduled arrival. | Yes. The pay1-only swap FLIPs, and the flush drops accuracy to chance. | SUPPORTED as an in-flight / echo carrier. The C1b text "signed payload sum is NOT the code" is KILLED (K1). Any "memory" reading is UNSUPPORTED. | A HOLD variant with gap drawn per trial from 6-10. The echo predicts accuracy falling to the kernel overlap; a latch stays ~1. |
| 6 | C1b labels (IN_FLIGHT_PLUS_JOINT_UNRESOLVED; TRANSPORT+RULE_SWITCH_UNRESOLVED) | C1b s4 | — | The A3 eligibility rule works as designed. | SUPPORTED as computed. The absolute "kills" threshold auto-fires near .6 (disclosed). | — |
| 7 | H6: "Search reachability, not physics, bounds what PTE shows" (four independent lines) | SYNTH ARC3 s1; CROSS_THREAD_COMPRESSION | (a) Selection against retention by task design, plus fitness shaping (F4), plus budget. (b) The four lines are not four tests of reachability. W-A/T-DE-1 and W-G show expressibility only, and no search was run at the designed physics. W-H S2 shows search DID reach .963 fixed-rule in 2/4 seeds, which is seed variance. Only W-L tests reachability (0/4, one budget). (c) The biggest NULLs (XOR, FLIP, multi-hop) have no plants, so "not physics" is untested exactly where it matters. | Partly. The "is anything search-reachable we cannot design" test does not threaten H6. The threatening test (a plant fails AND search fails) was never run. | WEAKENED | (i) XOR plant at a co-arrival physics (one hop, jitter 0). If it works and 8 searches fail, that is H6 evidence; if the plant fails, physics binds. (ii) W-L n=2 at 4x budget, plus an anti-integrator task variant. |
| 8 | "Carriers are trajectories, not places" (census SITE RELAY cells carry the bit in the channel first) | SYNTH ARC2 s3, ARC3 s1; W-I | Definitional for any one-hop relay plus latch in a task where sensor != actuator. The bit must be in flight before it lands. W-S shows the per-trial S/C split is whether one packet has landed (jitter). | No mechanism in these tasks could have been "place-only" except HOLD. | SUPPORTED but trivial. "Census SITE was a phase reading" is correct and useful. The general wording is inflation. | Multi-hop tasks: does an intermediate site ever store the bit for many ticks (store-and-forward)? That is the only place/trajectory question with content. |
| 9 | "No nontrivial retention regime in champions"; SI01 CLOSED for current champions; "PTE may be the wrong SI lens" | W-E, W-G, SYNTH ARC3 s3, SYNTH 09-27 s13 | The tasks penalise retention (i.i.d. independent trials), so absence is expected. The sample is 16 specimens from about 4 physics points. | Yes for these specimens: C-POS / C-EFF / C-AVL show the instrument detects retention, and C-CHAOS is rejected. | SUPPORTED for the 16 champions. UNSUPPORTED as a statement about PTE (W-G says so itself). SI01-closed is a scoping decision, fine as scoped. | W-L's integrator-defeating n-back (old cues carry opposite weight) at 4x budget, 8 seeds, with the selectivity criterion. |
| 10 | Relative swap certificate REL4/H2 (promoted swap_rel.py) | W-W, W-X, swap_rel.py | Statistically sound, but the question is whether it measures the carrier. (a) The mirror swap transfers the whole-history sign, so integrators read FLIP_REL COMPLETE. (b) FLIP_REL means z < −1/2 (partial transfers included). (c) FC is validated only under modelled nulls. (d) Seed consistency is 92.7% at intermediate z (W-Z). | Yes as a statistic: 0 false certificates on engine plants, and the must-fails fail. As a carrier ruler: not tested against a history-carrier plant. | SUPPORTED as a certificate on the swap statistic. WEAKENED as a carrier instrument. | Take the W-L integrator champions and P1S. Single-cue-twin swap (only cue k differs): P1S gives z ≈ −1; an integrator should give |z| ≈ its lag-k weight (~.1-.3). If both read FLIP_REL, the mirror certificate is overstated. |
| 11 | "84% of recorded CHANCE verdicts stay CHANCE at 512 worlds" (and the earlier "most are real partial or mixed effects") | W-O; CORRECTIONS 09-29; SYNTH 09-29 s1 | Mostly structural. Of the 615 that stay (my recount of W-O rerun_table.csv): 126 have normal < .62 (FLIP unattainable by rule); 90 are at offset <= 0 (second cue tick after the swap); census UNDEFINED 175 plus IDENTITY-BROKEN 82 (42% uninterpretable); 38% come from 6 specimens; 221 groups. The re-run also changed the design (EVERY to SINGLE; only 29 EVERY checks). | The count reproduces (Harmonia 733/733). | SUPPORTED as a count. UNSUPPORTED as mechanism evidence (already partly corrected by Harmonia). | None needed. Re-express the numbers by group and by cause (rule-unattainable / o0 / identity-broken / phase-pooled / jitter). |
| 12a | W-P: 4781b0a1's N is a clean JOINT-2 AND/OR of site latch S1 and payload-1 in flight | W-P | The cell is a rectified count-threshold presence code. Sensor latches (S1 := 256*(S1 + SENSE > CNT0)) re-emit PAY1 = MAX(IN, SENSE). The readout overwrites S0 := IN0_1 − 3. Redundant copies (latched sources plus packets already emitted) under a one-sided threshold on a sum give AND/OR truth tables by where the threshold falls. The "S1" is the sensors' S1 (W-V). | No. The AND/MUX plants are binary-register plants; no sum-threshold plant was run through tt.py. | Descriptive tables SUPPORTED and replicated (W-M, W-R, W-V numbers agree). "Joint carrier" as a distinct architecture: WEAKENED. | A sum-threshold plant (S0 := Σ rectified arrivals − θ, lossy sampled delivery, sync period 2) through W-P's truth table and W-V's classifier. If it reproduces AND/OR + DISTRIBUTED-NONMAJ + phase effects, the chain reduces to "noisy count threshold". |
| 12b | W-R: classes must be phase-indexed on sync period-2 physics | W-R | Clock parity plus one-packet latency jitter (W-S). | Yes: async control and a plant with a hand-predicted table. | SUPPORTED (the control's first-namespace failure suggests CIs are anti-conservative) | Trial-level resampling for stratum CIs. |
| 12c | W-S: the mixed phase is one jitter draw on the source's first broadcast; W-T: it does not reach MAJ or 78f3b0ec | W-S, W-T | — | Yes: post-hoc P8 confirmed at 0x632, plus a plant known-answer test and a must-fail plant. | SUPPORTED, scoped to 3 RELAY cells. | — |
| 12d | W-V: DISTRIBUTED-NONMAJ, not a majority | W-V | A noisy majority by count. The positive control is lossless and deterministic (1.6). | No. The control does not exercise stochastic delivery. | WEAKENED | Re-run PMAJ at the champion's loss .1 and fanout-8 sampling. If D_piv falls to about .1, "not a majority" dissolves. |
| 12e | W-Y: readout Kp[7] is not a carrier | W-Y | — | Yes (Plant B, MF-X). | SUPPORTED, trivially (Kp[7] = 0 in all 4224 cases). KILLS W-V's "readout Kp carries half the bit" (it was Kp[0], unread). | — |
| 13 | SETRULE compresses, it does not expand (W-H) | W-H, ARC3 s4 | Champion suboptimality is seed variance, not a SETRULE property. | Yes (hand-compiled and searched fixed-rule programs). | SUPPORTED within 5 cells, as W-H scoped it | T-H1 (a task where rules=1 provably cannot solve). |
| 14 | Zero-parameter echo model predicts 46/46 unseen curves | W-A, ARC2 s1 | The model re-implements the engine's own latency, loss and wake arithmetic on the decompiled 3-line law. It certifies that the decompilation is complete, not that a theory was found. | Yes (base-curve null passes 12/44). | SUPPORTED as decompilation-completeness; the "gold standard" framing is inflated | — |

---------------------------------------------------------------------

## 3. STRANGE OBSERVATIONS (normalized away or never followed up)

1. **613162a3 (MAJ, global).**
   - shuffle_dest scores .72, ABOVE normal .688. On global topology, shuffle_dest is almost the same as normal random routing, so this control cannot falsify anything there.
   - The twin assay shows the cue perturbation reaching 98% of sites at readout and 100% at the next trial (div_frac .98/1.00). packet_ablation .545, memory_ablation .543; REPRODUCED False (C1R s7).
   - This is a whole-network chaotic state that still scores ~.69-.72. It aggregates several sensors (F5), and nobody studied it.
2. **The C1 "size-free" law is the non-reproduced one.** bbef66a1 (reps .572/.506) is the only RELAY law in wave E. The "reproduced" RELAY cells were never scaled.
3. **zero_comm is exactly .500 in 100% of RELAY/MAJ/XOR rows** (F2). The C1 package reports it as evidence.
4. **At the M2 physics, HOLD search prefers echoes over latches.**
   - C1b fresh HOLD searches: 3/3 SIGNAL champions were in-flight (packet s7, P5 "lost in intent").
   - Yet W-L's n=0 HOLD control at the same physics and SearchSpec gave a local integrator (.672), and elsewhere HOLD is 81/85 site latches.
   - Same physics, same GA, near-identical task, different mechanism class. Either the outcome is extremely seed-contingent, or W-L's monkeypatched builder is not equivalent to envs HOLD. Neither was checked.
5. **The echo physics is not "HOLD".** 4ab2ba01 is a HOLD champion with zero_comm .5 (comm_delta .38; ROWS): a HOLD solver that cannot hold without the channel, although a 4-instruction latch scores 1.0 there.
6. **One-sided readouts are common.** In 95649e2c, all competence is on + trials (−trials .49, S0 >= 0). 4781b0a1 is RECTIFIED. The sens_act bonus pays such codes (F4); nobody connected the two.
7. **311c465f needs its distractors** (.76 -> .55 without; W-B). It has been unexplained since arc 2.
8. **W-V vs W-Y.** W-V attributed half the readout bit to "readout Kp differs 78-98%". W-Y shows that difference is entirely in Kp[0], which is never read, and Kp[7] is always 0. "Decodable != used" (H3) had already been adopted as a principle.
9. **"Site" means every site.** W-P's JOINT-2 "S1" is not the readout's S1, which is never mirror-different (W-V). The site/channel partition is global.
10. **Early traffic is ignored.** 4781b0a1 at o2-o8: swapping ALL readout-bound traffic leaves raw S0 bit-identical (W-V), although 80-95% of that traffic is mirror-different. The readout ignores everything before its last wake window, so the early N in W-P comes from sensor-to-sensor traffic.
11. **Negative controls and seed consistency failed.**
    - W-R's async negative control failed its frozen rule at 0x620 and was clean at 0x621, but the pair-bootstrap under-coverage it implies was not propagated to other stratified analyses.
    - W-Z's seed consistency of 92.7% missed the frozen 95% bar, and promotion of H2 went ahead the same day.
12. **Completeness is unstable.** Of the 42 "complete transfers" (W-O), 24 are complete by point z (W-Q), 19 by paired CI (W-U), or "only ~half" (SYNTH 09-29).
13. **The normative spec is stale.** DESIGN.md s7 still specifies the rejected within-episode target balancing and the MAJ centroid (1.1), and no oracle covers envs.py.
14. **Recorded dials can differ from the physics.** For global cells, `levels.dest_mode` = 'all' while the physics ran 'sample' (613162a3).
15. **The M3 cells aggregate but sit at the single-sensor ceiling** (F5). Why multi-sensor aggregation gains nothing at loss .3, dup .1, noise 64 and async .8 was never asked.
16. **An r-swap cannot FLIP a per-tick branch.** ARC2's "r is never the bit carrier: 0 FLIPs in 18 swaps" (W-B) comes from an arm that cannot FLIP: SETRULE recomputes r every tick, so swapping r is overwritten on the next tick. W-B noted this; the synthesis presents the count as a finding.

---------------------------------------------------------------------

## 4. WHAT I COULD NOT CHECK

- I re-ran no swap arms, truth tables or census runs, and did not open the raw npz files of W-P, W-R, W-S, W-V or W-Y. Their numbers are taken as reported, cross-checked only where two workers overlap.
- **One-hop classification (F1)** uses the geometry rules in envs.py and topology (d <= radius on ring/torus; d = 1 on smallworld), plus the recorded twin reach. I did not run a per-cell hop census for the smallworld cells, whose rewired edges could make some d = 1 pairs non-adjacent.
- **F5** is a normal-run, in-sample agreement analysis on 128 worlds. It shows that more than one sensor is read, not how. It is not a causal per-sensor intervention.
- **F4 (shaping bias)** is an argument from the code plus circumstantial patterns. No A/B search with and without shaping was run (that would be ANANKE-14).
- I did not verify whether W-L's HOLD builder is equivalent to envs.build HOLD (item 4 above).
- **Not read in detail:** W-C X4, joint_carrier/, designed_echoes/, the spikes logs, BACKLOG_V2, PTE_ENGINE_CARD, the instruments/*.md cards, and the Harmonia evidence audit.
- I did not check the FC simulation code of W-Q, W-U, W-W or W-X beyond reading swap_rel.py.
- I did not check GPU/CPU determinism or the oracle suite.
- Nothing under prometheus/cosmos/c3_holdout_D*/ was read.

## Files (this directory)

- REPORT.md (this file).
- sensor_agreement.py: normal runs of the champions via lens.run, CPU, 2 threads, ns 0x5C1, 128 worlds. It computes readout-sign agreement with each sensor and with the majority.
- sensor_agreement.json: output of the above.
- No background processes were left running, and nothing outside H-SCI/ was edited.
