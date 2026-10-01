<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-AI; sha256(report)=709757a84f71849c; delimited; see REPORT.provenance.json -->
W2-AI — Do the two C1 multi-hop RELAY SIGNAL champions FORWARD? (Ananke wave 2)

Files (all in roles/Ananke/research/harvest/wave2/W2-AI/):
- fwd.py: known-answer gate, hop table, emission-ablation conditions, twin-divergence ticks. The hook is an AblWorld subclass whose _emit does want := want & ~mask[B,N]. A silenced site still computes and receives, but cannot put packets in flight. The economy is off in both cells, so silencing costs nothing.
- twin_by_trial.py: the recorded twin_assay reproduced, then repeated for all 12 trials.
- per_trial.py: accuracy by trial index, and a test of a one-shot latch model.
- Outputs: out_925caa3a_gate.json, out_882525a9_gate.json, out_925caa3a_ablate.json, out_882525a9_ablate.json, out_twin_by_trial.json, out_per_trial.json, gate_*.log.
- Run commands:
  - `python fwd.py <prefix> gate`
  - `W2AI_M=64 python fwd.py <prefix> ablate`
  - `python twin_by_trial.py`
  - `python per_trial.py`
  - All CPU eager with 2 threads.
- Full cell ids: 925caa3a48964717 (ring r3, d5) and 882525a9d4a3d073 (smallworld rewire 50, d3, directed table).

VERDICTS
- 925caa3a48964717: FORWARDS, one-shot. Information crosses 2 hops (and 3 or more when the shortest paths are silenced), once per episode. It is an irreversible flood latch, not a relay that works trial by trial.
- 882525a9d4a3d073: FORWARDS, one-shot. Information crosses 3 directed hops, once per episode, by the same latch mechanism.
- Neither cell is SHORTCUT-ONLY: 64/64 held worlds are true multi-hop in both cells. Neither is UNRESOLVED.

FINDINGS

F1 [V] Known-answer gate passes exactly for both cells. Confidence: high.
- Recomputing on all 64 held worlds (world_seeds(H(search_seed, HELD_NS=0x4E1D), 64), mirror pairs, CPU eager) reproduces acc, lo99 and hi99 bit-exactly:
  - 925caa3a: .578125 / .55598 / .609375
  - 882525a9: .591146 / .56380 / .622402
- Command: `python fwd.py 925caa3a gate` and `python fwd.py 882525a9 gate`; gate_exact=true.
- The recorded twin assay (trial 2, hseeds[:16]) also reproduces exactly on CPU for both cells (twin_by_trial.py, trial2_repro_exact=true).
- Each 64-world eval takes about 7.5 s wall, so I ran every analysis on all 64 worlds and did not drop to 32.
- Objection: none. Unresolved: none.

F2 [V] Hop demand: no 1-hop worlds exist in either cell. Confidence: high.
- Per-world BFS over the engine's own neighbour table (topology.graph_distances), from sensor to actuator:
  - ring: hop = 2 in 64/64 worlds;
  - smallworld: hop = 3 in 64/64 worlds;
  - accuracy on 1-hop worlds is therefore undefined (n = 0); accuracy on 2+-hop worlds is the full held value.
- Why this holds by construction:
  - On graphs, envs.dist_matrix IS directed BFS hop distance, the same table and direction the engine emits along, and _pick_at finds an exact-d site in every world.
  - On the ring, an env distance of 5 at radius 3 always needs ceil(5/3) = 2 hops.
- In the smallworld, rewiring creates some odd placements, e.g. s=68, a=69: adjacent on the torus, but the directed edge 68->69 was rewired away, so it is 3 hops. These are still true 3-hop demands. Smallworld rewiring did not create shortcuts here.
- The "1-hop worlds" concern does not apply to these two cells.

F3 [V] Forwarding is logically certified and the path is located. Confidence: high.
- Cut test: ablate emission at the sensor's out-neighbours (6 sites on the ring, about 4 on the smallworld). The actuator is not among them in any world. Result in both cells: acc = .500 exactly, 0/32 pairs off .5, and the actuator's state NEVER diverges between twins.
- All-but-sensor-and-actuator silenced: the same result.
- Controls change nothing; results stay bit-identical to baseline:
  - random off-path sites of the same size;
  - random off-path sites matched in size to the shortest-path set;
  - the nearest off-path sites on the sensor side.
  - Baseline in both cells: 31/32 or 32/32 pairs off .5, and the actuator diverges in 32/32 pairs.
- Shortest-path intermediates only (sites v with d(s,v)+d(v,a)=h):
  - ring, {s+2, s+3}: acc .578 -> .582, no loss; the first divergence at the actuator moves from tick 2 to tick 4, so the wave reroutes through 3-hop paths (e.g. s -> s+1 -> s+4 -> a);
  - smallworld, about 2.75 sites: acc .591 -> .557, lo99 .529, a partial loss; the actuator's first divergence moves from tick 8 to tick 15.
- Above-chance pairs: 31 vs 0 (sign p = 9e-10) and 32 vs 0 (p = 5e-10).
- Logic: with every world at 2+ hops, the actuator can only differ between mirror twins if some site that is neither sensor nor actuator emits something that depends on the cue. The ablations show where this happens: the sensor's out-neighbours, with multi-path redundancy.
- Objection: the cut result of exactly .5 is partly tautological (with a vertex cut silenced, the mirror design forces .5). The non-tautological content is that equal-sized off-path ablations have zero effect, and that shortest-path silencing reroutes the wave instead of killing it.

F4 [V] The mechanism is a one-shot irreversible flood latch, not a relay that works per trial. Confidence: high. This is the main new result.
- Accuracy by trial index (64 held worlds, per_trial.py):
  - 925caa3a: 1.00, .70, .59, .58, .55, .52, then .50 exactly for trials 6-11;
  - 882525a9: .98, .77, .66, .59, .56, .52, .52, then .50 for trials 7-11.
- Latch model: a world is quiescent (readout S0 < 0) until its FIRST positive cue. That cue triggers a self-sustaining flood, and from then on readout S0 > 0 for good.
- Model fit:
  - It predicts 99.6% (925caa3a) and 99.0% (882525a9) of individual readouts.
  - Predicted accuracy .5794 vs observed .5781 (925caa3a); .5924 vs .5911 (882525a9).
  - Fitted sign means: quiescent -1.00, fired +.99 in both cells.
- The twin assay over all trials agrees:
  - readout_flipped by trial = 1, .5, .19, .06, ... (geometric, as a latch predicts);
  - ring reach = 72 at trial 0, i.e. half of a 144-site ring, so the wave covers the whole world.
- Accuracy ceiling: at 12 trials a one-shot latch tops out at about .58-.59 (one twin is right on trial 0, the other until its first positive cue at expected trial 2, then both are at 50%). Both champions sit at that ceiling.
- Decompiled champions show the gate (via hp_common.decompile):
  - 925caa3a: `EMIT = MAX(SENSE, IN0_1)`; it emits on a positive cue or on a received payload, and S0 = IN0_0 - 66.
  - 882525a9: `EMIT = MOD(-109, max(CNT0, SENSE)+1)`, which is > 0 iff a packet arrived or the cue is positive; S0 = CNT0 - 1.
  - In both, emission is triggered by receipt, so re-emission is forwarding.
  - Nothing stops the cascade or resets it to quiescence, so it latches.
- Objection: the latch model was fitted with 2 free signs. But it predicts the whole trial-by-trial profile, and readouts are never ambiguous (0-1% zeros).
- Unresolved: whether any C1 champion forwards repeatedly, trial after trial.

F5 [V] REACH_BEYOND_HOP=False on both rows is a false negative for forwarding. Confidence: high.
- campaign.py:461 labels REACH_BEYOND_HOP = (twin beyond_hop >= .5). The twin assay negates the cue of trial 2 only (assays.twin_assay, trial=2).
- For a latch, trial 2 has the wave already fired in about 75% of worlds, so beyond_hop is about .19-.25 even though forwarding is certified (F3).
- Beyond_hop is 1.0 at trial 0 in both cells (twin_by_trial.py).
- So the label measures "does trial 2's cue still travel far", not "can the champion forward".
- [I] Any row-level claim that "no RELAY champion reaches beyond one hop", if it is drawn from REACH_BEYOND_HOP, is biased against latches.

F6 [I] Why W2-X's run timed out. Confidence: medium.
- hp_common sets torch.set_num_threads(HP_THREADS, default 8) after W2-X's set_num_threads(2). So W2-X ran 8 torch threads under OMP_NUM_THREADS=2, which plausibly caused thread contention.
- The same evals take about 7 s per 64 worlds in my scripts, which avoid hp_common.evaluate.
- I did not reproduce the hang.

PROPOSED FIXES (no code patches filed; both would be NEUTRAL instrument additions)
- N1: add a per-trial accuracy profile and a "latch" flag (accuracy at .5 over the late half of trials, accuracy at trial 0 near 1) to the row diagnostics.
- N2: report beyond_hop at trial 0, or the maximum over trials, next to the trial-2 value. REACH_BEYOND_HOP should not be read as "cannot forward".
- I wrote neither as a diff, because the frozen labels must not change. They are reporting proposals for the principal.

DISAGREEMENTS
- With H6 v3/v4 "forwarding never discovered": wrong at the existence level.
  - C1 search found forwarding in 2 of the multi-hop searches (2 of about 30 reachable; 46 faced multi-hop tasks per W2-X).
  - The forwarding found is a one-shot trigger wave. It is NOT a reusable relay channel.
  - Correct statement: "Search discovered once-per-episode forwarding (receipt-triggered flood latches, at the ~.58-.59 one-shot ceiling) in 2 multi-hop cells. No sustained per-trial multi-hop relay is shown."
- With W2-X row 9's proposed wording "No C1 champion is shown to forward": now superseded. Two are shown to forward (F3); their mechanism is one-shot (F4).
- With W2-H's t-interval flip on 925caa3a: the flip is about the .55 margin, not about being above chance. Forwarding is certified regardless (31 vs 0 pairs).
- Implication for C1_ERRATA:
  - E-W19 says "multi-hop rarer, not shown absent". It should now read: multi-hop SIGNAL is present but latch-type.
  - E-W21: at 12 trials a one-shot latch clears the SIGNAL margin (lo99 > .55). A RELAY SIGNAL near .58-.60 therefore does not certify per-trial relay competence. That is a scoring-design property, not a physics boundary.
- Bottom line on whether C1 search can discover forwarding:
  - It can discover forwarding as an excitable-medium cascade.
  - Whether it can discover per-trial (resettable) forwarding stays UNDECIDED.
  - The selection signal for per-trial forwarding above the latch ceiling (about +.08 to +.09) is the margin a search would have to climb, and none of the 2 cells did.

NEXT QUESTIONS (ranked)
1. How many of the 50 RELAY SIGNAL rows are one-shot latches? 16 rows sit at held acc <= .598, which is the latch ceiling. Run per_trial.py on all 50 (about 8 s each). If most low-acc SIGNALs are latches, the A1 RELAY rate (4/71) shrinks for per-trial relay competence.
2. Does a resettable relay exist in program space at these two physics? A one-shot latch plus a reset (e.g. a decay_shift > 0 level, or a plant with refresh) would turn the cascade into per-trial forwarding. Check plant viability at 925caa3a and 882525a9 physics with relay_refresh.
3. Recompute REACH_BEYOND_HOP as the maximum over trials (or at trial 0) for all rows. How many labels flip, and does any C1/H6 claim rest on that label?
4. Does the latch ceiling depend on the number of trials? At 12 trials the ceiling is about .58. A prereg with more trials, or one that scores only trials 4+, would separate latches from relays. Proposal for C1b/C2 design (SEMANTIC, future prereg only).
5. Smallworld path ablation lost .034 while ring path ablation lost nothing. Is smallworld forwarding route-limited (sample dest_mode, cap 2 saturate)? This bears on whether directed small-world graphs push search toward fragile single paths.
6. Do the 7 D laws (one-hop) also show latch profiles? If so, "one-hop wall" and "latch" may be one phenomenon: a latch cannot fire twice, regardless of hops.

INFERENCE LEDGER
- Q: Do the recorded held values reproduce? | fwd.py gate, 64 worlds | exact match, both cells | high | none | none | done
- Q: Are any worlds 1-hop (placement or shortcut)? | BFS on the engine table, per world | 0/64 in each cell; ring all 2 hops, smallworld all 3 | high | the direction of BFS vs emission (checked: both use nbr[u] outbound) | none | none
- Q: Does information cross intermediate sites? | out-neighbour cut, all-silent, shortest-path set, 3 equal-size controls, 64 worlds | cut gives .500 exactly and no actuator divergence; controls stay bit-identical to baseline; shortest-path silencing reroutes (ring) or partly cuts (smallworld) | high | the cut result is forced by the mirror design | none | NQ5
- Q: What is the mechanism? | per_trial.py, twin_by_trial.py, decompile | one-shot receipt-triggered flood latch; model fits 99-99.6% of readouts; trials 6+ at .5 | high | 2 fitted signs | per-trial relays elsewhere? | NQ1, NQ2
- Q: Is REACH_BEYOND_HOP valid for forwarding? | twin assay over trials | trial 2 = .19/.25 but trial 0 = 1.0 | high | the label was never defined as "can forward" | other rows | NQ3
- Q: Can C1 search discover forwarding? | F3 + F4 | yes, as one-shot cascades (2 cells); per-trial relaying undecided | medium-high | n = 2 | latch prevalence | NQ1, NQ4
- Q: Why did W2-X time out? | hp_common thread setting | probably 8 torch threads under OMP=2 | medium | not reproduced | — | none

COMPUTE
- CPU only (CUDA_VISIBLE_DEVICES=-1, asserted no CUDA), 2 threads, eager (graph=False), no search, no leases.
- About 465 CPU-s in total:
  - gate: 29 s;
  - ablate: 200 s;
  - twin by trial: 200 s;
  - per-trial: about 30 s;
  - decompile: under 5 s.
- Total about 0.13 core-hours, under the 0.4 cap. Every run was under 60 s wall.
