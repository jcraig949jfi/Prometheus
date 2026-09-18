# CW01 priority loop - cycle report ARCH4_2026-09-18

Ten frozen perturbations executed under their own preregistrations (PREREG.json hashed before each run).

| rank | id | parent | type | disposition / reading | s |
|---|---|---|---|---|---|
| 1 | P-C15 | T-ARCH4/D1 | serendipity | material=True | 71.2 |
| 2 | P-C16 | T-ARCH4/M1 | serendipity | material=True | 11.2 |
| 3 | P-C13 | T-ARCH4/R1 | exploratory | material=False | 4.6 |
| 4 | P-C14 | T-ARCH4/W1 | exploratory | material=True | 1.5 |
| 5 | P-C03 | T-ARCH4/R1 | one-axis-walk | material=True | 9.3 |
| 6 | P-C04 | T-ARCH4/M1 | one-axis-census | material=True | 22.0 |

## Evidence appended this cycle (46 events, 30 material)

- **T-X09** <- P-B04 (not material): T2-impossible-without-T1: NULL (foundation-first 1/4, K1>sham 4/4)
- **T-E02** <- P-B04 (not material): changed economics re-pose: NULL
- **T-E02** <- P-B05 (not material): e02 under weather: foundation-first {'STATIC': 0, 'WEATHER': 0, 'SHAMWEATHER': 0}; gap contrast 0.0
- **T-X01** <- P-B05 (not material): neutral drift under STATIC/WEATHER/SHAM in e02: {'STATIC': 0.20557902224462576, 'WEATHER': 0.18670348730938835, 'SHAMWEATHER': 0.20557902224462576}
- **T-X07** <- P-A11 (not material): chain organism on e07 task: single-op ceiling 0.266, best arith chain 0.266, best scrambled 0.165, stateless optimum 0.354, floor 0.161
- **T-E09** <- P-A11 (not material): composition probe on a generalising task: chains do not materially exceed the single-op ceiling on held-out lifetimes
- **T-E07** <- P-B03 (MATERIAL): e07's damage family posed in e01's world: NEGATIVE (weather lineages retain less); STATIC r 0.181, WEATHER r 0.359, c -0.264 [-0.124, 0.124]
- **T-E01** <- P-B03 (MATERIAL): e01 organisms under blind state deletion: retention r 0.181 at f=0.2 (STATIC lineages)
- **T-X08** <- P-B09 (not material): TTL-distribution evolution: FIXED rel7 0.829 vs DIST rel7 0.828 (effect -0.001, band [-0.009, 0.009])
- **T-E04** <- P-B09 (not material): schedule-distribution perturbation run; see T-X08
- **T-X01** <- P-A10 (MATERIAL): fixation vs structure: {'tournament3': 31.0, 'tournament2': 55.5, 'tournament1': 76.5, 'islands4': 21.5} (neutral ~96)
- **T-X04** <- P-A08 (MATERIAL): target-geometry interpolation: no phi gives mutual invasibility; the asymmetry flips between [(0.0, 0.25), (0.25, 0.5), (0.75, 1.0)]
- **T-E06** <- P-A08 (not material): geometry interpolation result: no phi gives mutual invasibility; the asymmetry flips between [(0.0, 0.25), (0.25, 0.5), (0.75, 1.0)]
- **T-E08** <- P-A01 (MATERIAL): held-out selection pilot: competent-lineage rate 0.50 (lower bound 0.25, min_count 4 < 6): unreachable under this rule, no production spent
- **T-X02** <- P-A04 (not material): training breadth 8/32/128: competent reps 4.00/2.00/5.33, held64 159.9/164.2/178.8; 128-8 competent effect 1.33 [-3.33, 6.00]
- **T-E08** <- P-A04 (not material): breadth screen bears on e08's eligibility surface: {8: {'competent_reps': 4.0, 'held64': 159.86572265625}, 32: {'competent_reps': 2.0, 'held64': 164.2021484375}, 128: {'competent_reps': 5.333333333333333, 'held64': 178.79817708333334}}
- **T-X04** <- P-A08 (MATERIAL): RECONCILER NOTE: at phi 0.50 and 0.75 NEITHER substrate invades the other (both invaders go extinct): contingent, founder-controlled dominance - one of the five regimes e06 required reachable. The axis runs TAPE-dominance (phi 0) -> TREE-dominance (0.25) -> bistability (0.5, 0.75) -> TREE-dominance (1.0). Not mutual invasibility, but a third regime the driver's rule did not name.
- **T-E06** <- P-A08 (MATERIAL): RECONCILER NOTE: contingent dominance located at intermediate target geometry (see T-X04); e06's reachability requirement gains one regime (history-dependent dominance) even though coexistence is still unreached.
- **T-X08** <- P-B09 (MATERIAL): RECONCILER NOTE: the inversion is NOT schedule specialisation: lineages evolved under a TTL distribution show the same rel(7) 0.83 and rel(30) 1.07 as fixed-TTL lineages, and their absolute scores at every TTL are within the band. The phenotype is intrinsic to the channel economics (a faster-forgetting channel hurts any policy), so the 'tuned to one schedule' reading is falsified.
- **T-E07** <- P-B03 (MATERIAL): RECONCILER NOTE (CW01-D071): raw retention DOUBLED under weather (0.181 -> 0.359) at a 7% intact cost; the frozen ability-adjusted ratio reads NEGATIVE because the normalising margin is ~0.003. Both readings are on record; neither is promoted. Material: the damage question is posable in e01's world (damage fires on evolved organisms, sham bit-inert).
- **T-E09** <- P-A11 (MATERIAL): RECONCILER NOTE: on e07's task all four arithmetic chains converge to exactly the single-op ceiling (0.266) and scrambled chains to the floor (0.161); the stateless linear optimum is 0.354. A 3-op digit chain cannot even reach a linear readout: the boundary is the chain representation, not w13.
- **T-E08** <- P-A01 (MATERIAL): RECONCILER NOTE: under held-out selection the pilot is BIMODAL - 2 lineages 8/8 competent (held64 175-184), 2 lineages 0/8 (156-160). Lineages either generalise fully or not at all; the eligibility surface is a lineage-level coin, not a representative-selection artefact.
- **T-X02** <- P-A04 (not material): RECONCILER NOTE: 128 train seeds raise held64 to 178.8 (vs 159.9 at 8 seeds) and competent reps to 5.3/8 (vs 4.0), inside the tiny-n relabelling band (3 vs 4 lineages); 32 seeds gave 2.0/8 - the breadth response is noisy at this lineage count. Directionally supportive, not established.
- **T-X01** <- P-A10 (MATERIAL): RECONCILER NOTE: the hitchhiking floor is SELECTION STRENGTH - tournament 1 (pure drift) fixes at median 76.5 ~ N=96, tournament 2 at 55.5, tournament 3 (as run) at 31, and 4 demes of 24 at 21.5 (small-deme drift). Every ecological noise floor in e06 was measured under 3x-accelerated fixation.
- **T-X09** <- P-B04 (MATERIAL): RECONCILER NOTE: with T2 impossible without T1 the K1 knockout is load-bearing in 4/4 (loss 0.08-0.11 vs sham 0.00) - the first executed knockout in this lineage - yet p_factor still fixes first or simultaneously (foundation-first 1/4): both genes rise together because p_factor is neutral until p_norm rises. Order is not the right ruler for a co-required pair; the knockout is.
- **T-E06** <- P-A07 (MATERIAL): variation regime swap: TREE invades under some variation regime; rows [(0.0, False, True), (0.5, False, True), (1.0, True, True)]
- **T-ARCH4** <- C4-REH-1 (not material): 2026-09-17: launch-gate item G2 (integration rehearsal C4-REH-1) set aside SKIPPED_SAFEGUARD_TERMINOLOGY after roughly seven attempts were interrupted by an automated safeguard acting on the lead's own output (messages of very different length, one of eight words with no commands; tails of command sequences lost; not predictable from content). Diagnosed by the operator as vocabulary inherited from the evolutionary-computation framing. Item intact and resumable; NOT a scientific state (archaeon/campaign4/DISPOSITION_C4-REH-1.md, HANDOFF_2026-09-17.md).
- **T-ARCH4** <- operator-directive-2026-09-18 (not material): The operator's reactivation directive states the trajectory 'twice encountered' safeguard interruptions. The committed artifacts document ONE episode (C4-REH-1, multiple attempts, 2026-09-17) and the handoff it forced; no second episode is recorded in archaeon/campaign4 or roles/Archaeon/journal. Recorded as reported; treated as infrastructure, never as evidence about the hypothesis.
- **T-ARCH4/R1** <- C5-05 (MATERIAL): representation B (narrow in-table, FAIL/FIZZLE) built and qualified by Archaeon; C4-01 census replicated exactly; boundary fires on 84-86% of crossing children; FIZZLE recovers competence in .42-.46 of them; D7 still 0
- **T-ARCH4/S1** <- C5-01 (MATERIAL): deep walk to 64: exaptation .050 -> .082, marginal yield per step falls 4x, yield per evaluation below a random single edit's; PRESERVE_NEUTRAL NO
- **T-ARCH4/D1** <- C5-02 (MATERIAL): fair lateral ecology at equal total compute on screened unsolved worlds: 0/24 cells improved; takeover without improvement replicated
- **T-ARCH4/P1** <- C5-09 (MATERIAL): reach at equal compute under OLD and B, four arms: NO_GAIN in 96 cells
- **T-ARCH4** <- C5 (MATERIAL): Campaign 5 closed BOUNDARY_CREATED_NO_DISCOVERY_GAIN: the neutral cliff was described one level deeper (a fizzled child is its parent with a hole, displacement .015), not escaped
- **T-ARCH4/W1** <- P-C14 (MATERIAL): silent drift curve (displacement mean): {'W0': 0.001, 'W0_noise': 0.018, 'W1_d1': 0.118, 'W1_d2': 0.109, 'W1_d3': 0.127, 'W1_d4': 0.108}; digests verified 60/60
- **T-ARCH4/R1** <- P-C13 (not material): swamp under decode rules: {'modulo': {'answering_share': 0.04529201430274136, 'D7': 0, 'D6': 0, 'max_reward_any_env_children': 0.125, 'walker_max_reward_any_env': 0.125}, 'nop': {'answering_share': 0.03575685339690107, 'D7': 0, 'D6': 0, 'max_reward_any_env_children': 0.125, 'walker_max_reward_any_env': 0.0}, 'halt': {'answering_share': 0.03933253873659118, 'D7': 0, 'D6': 0, 'max_reward_any_env_children': 0.125, 'walker_max_reward_any_env': 0.0}}
- **T-ARCH4/D1** <- P-C15 (MATERIAL): blind vs contiguous deletion loss: {'parent|f0.1|blind': 0.564, 'parent|f0.1|contiguous': 0.463, 'parent|f0.2|blind': 0.761, 'parent|f0.2|contiguous': 0.652, 'parent|f0.3|blind': 0.878, 'parent|f0.3|contiguous': 0.795}
- **T-E07** <- P-C15 (MATERIAL): e07's blind deletion family applied to Campaign 4 programs: see T-ARCH4/D1
- **T-ARCH4/M1** <- P-C04 (MATERIAL): locality at radius 4: loss distributed 0.630 / block 0.569 / sequential 0.048; displacement 0.620 / 0.545 / 0.054
- **T-ARCH4/R1** <- P-C03 (MATERIAL): walk under trap-to-NOP vs modulo: acceptance 0.673 vs 0.602, len delta 1.80 vs 0.30, exaptation 0.032 vs 0.043, insulation events/walker 0.0
- **T-ARCH4/M1** <- P-C16 (MATERIAL): compound walk: len delta modulo 0.30 / r2 1.80 / r2+balanced 2.35; exaptation 0.043 / 0.032 / 0.043
- **T-ARCH4/R1** <- P-C13 (not material): RECONCILER: the degenerate swamp has no gradient under ANY decode rule (modulo / trap-NOP / trap-HALT): D7 = D6 = 0 over 839 children per rule, max reward on any environment .125 < floor .1875, walkers stay silent; the swamp is a property of the programs, not the decode.
- **T-ARCH4/M1** <- P-C04 (MATERIAL): RECONCILER: at radius 4, BLOCK edits (one window of 4 instructions) lose less than DISTRIBUTED edits (loss .569 vs .630; displacement .545 vs .620); sequential-viable filtering leaves loss .048 by construction. Locality is an axis of the damage geometry that C4-02's radius curve did not measure.
- **T-ARCH4/D1** <- P-C15 (MATERIAL): RECONCILER: BLIND scattered deletion of k instructions is more destructive than CONTIGUOUS deletion of the same k at every fraction (parents: .564/.761/.878 vs .463/.652/.795 at f .1/.2/.3; walkers slightly more robust than parents at every cell). Damage spread over more sites hurts more than a contiguous hole of equal size - consistent with P-C04 and with C4-04's near-zero reference effect for contiguous deletion.
- **T-ARCH4/R1** <- P-C03 (MATERIAL): RECONCILER: under trap-to-NOP the walk accepts MORE (.673 vs .602), grows SIX times more length (+1.80 vs +.30 instructions at depth 16), exapts LESS (.032 vs .043) and is slightly less structurally diverse (1.24 vs 1.35): insulation makes the neutral band wider and emptier. D072: the insulation count was lost.
- **T-ARCH4/M1** <- P-C16 (MATERIAL): RECONCILER: length-balanced proposal weights do NOT stop growth under trap-to-NOP (+2.35 vs +1.80 instructions); they restore exaptation to the modulo level (.043). Growth is driven by the ACCEPTANCE filter (NOP-trapped insertions are neutral and accepted, deletions of live code are rejected), not by the proposal mix - 'neutrality + length' is one phenomenon here.
- **T-ARCH4/W1** <- P-C14 (MATERIAL): RECONCILER: silent W0 drift becomes loud at ANY delay (.118/.109/.127/.108 at d1..d4, flat) and only faintly under noise (.018): the walkers' drift lives in timing-sensitive behaviour that W0's immediate asks never exercise; delay is a switch, not a dose.

## State after the cycle (28 trajectories, 3 in TEMPORAL_STASIS)

- T-ARCH4: ACTIVE - reactivated into the Nestor pool by operator directive; scoped nodes carry any future stasis
- T-ARCH4/D1: ACTIVE - a locality law is emerging across two perturbations; next: dose-response in number of sites at fixed k
- T-ARCH4/M1: ACTIVE - a mechanism for length growth is now stated and testable: next, a walk that rejects length-increasing neutral steps
- T-ARCH4/P1: ACTIVE - reactivated into the Nestor pool by operator directive; scoped nodes carry any future stasis
- T-ARCH4/R1: TEMPORAL_STASIS[starting_population=degenerate-gen0 x representation=trap-decode] - three decode rules strike the same surface; the next informative perturbation needs a different starting population (e.g. injected in-table generators as in C5-04)
- T-ARCH4/S1: TEMPORAL_STASIS[search_depth=walk-depth] - depth alone saturates; further depth is not informative; other search-dynamics axes (band rule, proposal weights) remain open
- T-ARCH4/W1: ACTIVE - a named phenotype now: timing-sensitive silent drift; next: which instructions carry it (ablation of accepted steps by ref_broken)
- T-ARCH5: ACTIVE - sibling descendant recorded from origin/main
- T-E01: ACTIVE - initial record
- T-E02: ACTIVE - initial record
- T-E03: ACTIVE - initial record
- T-E04: ACTIVE - initial record
- T-E05: ACTIVE - initial record
- T-E06: ACTIVE - search regime matters; next: locate the rate/geometry pair
- T-E07: ACTIVE - the question is posable in this world; next: severity dose and I2-style scramble
- T-E08: ACTIVE - eligibility surface confirmed to be about generalisation, not selection rule; next: P-A04's breadth result
- T-E09: TEMPORAL_STASIS - chain form still cannot compose on a second task; the boundary is the representation, not w13
- T-X01: ACTIVE - the floor is now a measured function of structure; next: apply the slowest structure inside an ecology run
- T-X02: ACTIVE - screening axis measured; next: rotating seed schedules
- T-X03: ACTIVE - initial record
- T-X04: ACTIVE - a bistable regime exists on the geometry axis; next: seeded-frequency sweep at phi 0.5 to map the separatrix
- T-X05: ACTIVE - initial record
- T-X06: TEMPORAL_STASIS - an instrument fact, fully mapped by the probe curve; the next informative step is its use inside a reposed T-E07, not further probing
- T-X07: ACTIVE - initial record
- T-X08: TEMPORAL_STASIS - the specialisation explanation is falsified and the remaining explanation (intrinsic channel economics) has no further perturbation available at this scale
- T-X09: ACTIVE - initial record
- T-X10: ACTIVE - initial record
- T-X11: ACTIVE - initial record

Rank is temporary. Every trajectory outside the ten waits with its record intact. The next cycle begins with global re-evaluation of the whole pool.