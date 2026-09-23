# CW01 priority loop - cycle report CYCLE2_2026-09-18

Ten frozen perturbations executed under their own preregistrations (PREREG.json hashed before each run).

| rank | id | parent | type | disposition / reading | s |
|---|---|---|---|---|---|
| 1 | P-D01 | T-ARCH4/M1 | parameterized-dose-surface | material=True | 208.4 |
| 2 | P-D02 | T-ARCH4/W1 | parameterized-switch-probe | material=False | 6.1 |
| 3 | P-D03 | T-ARCH4/M1 | parameterized-mechanism-break | material=True | 120.0 |
| 4 | P-D13 | T-E06 | serendipity | material=True | 21.8 |
| 5 | P-B07 | T-E03 | serendipity | material=False | 103.6 |
| 6 | P-D12 | T-X05 | exploratory-dose | material=False | 350.9 |
| 7 | P-B10 | T-X11 | exploratory | search limit | 226.9 |
| 8 | P-D11 | T-X01 | cross-material | material=False | 31.4 |
| 9 | P-D05 | T-E06 | replication-confirmatory | NOT_REPLICATED | 142.5 |
| 10 | P-D07 | T-E07 | reposed-confirmatory | RAN (see RESULT.json) | 137.9 |

## Evidence appended this cycle (70 events, 45 material)

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
- **T-ARCH4/W1** <- P-D02 (not material): delay switch grid (w0 walkers, displacement): {'det0': 0.001, 'det1': 0.118, 'det2': 0.109, 'det4': 0.108, 'stoch01': 0.001, 'rare0001': 0.002, 'hetero1234': 0.0, 'interleaved_d0': 0.001, 'interleaved_d1': 0.07, 'random_order': 0.001, 'noise_d0': 0.009, 'noise_d1': 0.119}; loud step depth median 7.0, ops {'splice': 1, 'operand_perturbation': 2, 'randomization': 1, 'insertion': 2, 'duplication': 1, 'region_swap': 2, 'reference_redirection': 1}, regions {'opaque_io': 1, 'indirection': 2, 'logical': 4, 'comparison': 2, 'arithmetic': 1}, ref_broken 0.0
- **T-E06** <- P-D05 (not material): recombination-1.0 mutual invasibility replication: NOT_REPLICATED; mutual cells rate 1.0 1/12 vs 0.5 0/12; TREE invades {0.5: 4, 1.0: 8}; by geometry {'graph': {0.5: 0, 1.0: 1}, 'legacy': {0.5: 0, 1.0: 0}}
- **T-X11** <- P-B10 (MATERIAL): plateau sweep: search limit; router-minus-evolved precision gap at G60 {0.1: 0.449, 0.2: 0.441, 0.35: 0.465, 0.5: 0.366}, G240 {0.1: 0.392, 0.2: 0.411, 0.35: 0.445, 0.5: 0.357}
- **T-E03** <- P-B07 (not material): representational tax on e03: {'0': (0.985, 0.247, 1.143, 4), 'H/4': (0.986, 0.245, 1.157, 4), 'H/2': (0.986, 0.221, 1.119, 4), 'H': (0.985, 0.254, 1.12, 4)}
- **T-ARCH4/M1** <- P-D03 (MATERIAL): acceptance-filter grid: length by rule under trap-NOP {'orig': 1.07, 'no_growth': -4.0, 'lennorm': 0.99, 'lencost': -1.74, 'symdel': -0.89}; by trap {'modulo': -0.38, 'nop': 1.07, 'halt': -1.77}; by proposal {'frozen': 1.8, 'balanced': 2.35, 'delheavy': -0.93}; growth breaks in 10/15 nop cells
- **T-E07** <- P-D07 (MATERIAL): absolute-retention dose: {'0.1': ('POSITIVE', 0.00316, 0.0011), '0.2': ('NULL', 0.00136, 0.00041), '0.3': ('NEGATIVE', 0.00045, 9e-05), '0.45': ('NEGATIVE', 0.00044, 0.0001)}; intact cost -0.00416 [-0.00216, 0.00216]; damage fires True
- **T-X05** <- P-D12 (not material): amputation-only dose: held64 {'None': 156.2, '2': 139.5, '5': 144.3, '10': 161.7, '20': 155.2}; scalar {'None': 1.868, '2': 0.813, '5': 0.875, '10': 1.167, '20': 1.524}
- **T-E08** <- P-D12 (not material): structural pressure alone on w13: {'None': 156.2, '2': 139.5, '5': 144.3, '10': 161.7, '20': 155.2}
- **T-X01** <- P-D11 (not material): tournament x recombination cross: coexistence counts {'t3_r0.5': 2, 't2_r0.5': 1, 't3_r1.0': 2, 't2_r1.0': 3}; final TREE {'t3_r0.5': 0.779, 't2_r0.5': 0.539, 't3_r1.0': 0.826, 't2_r1.0': 0.729}
- **T-E06** <- P-D11 (not material): coexistence attempt under (t2, r1.0): 3/4 coexisting
- **T-E06** <- P-D13 (MATERIAL): blind damage in the ecology: {'STATIC': (0, 0.75, 0.0288), 'DAMAGE': (2, 0.432, -0.0064), 'SHAM': (1, 0.885, 0.0438)}; sham identical to static False
- **T-ARCH4/M1** <- P-D01 (MATERIAL): locality dose surface: loss coefficients log2_s +0.024, log2_k +0.145, decode=nop -0.030, place=random -0.002; sites at k=8 {1: 0.662, 2: 0.762, 4: 0.779, 8: 0.774}; kinds {'delete': 0.717, 'opcode': 0.742, 'operand': 0.355, 'move': 0.75}
- **T-ARCH4/W1** <- P-D02 (MATERIAL): RECONCILER (D073): stochastic/interleaved/random-order cells were vacuous (identical episodes at K=1). Live cells: det1/2/4 .118/.109/.108 vs det0 .001; interleaved_d1 .07; NOISE words in-tick .009 vs an inserted NOISE tick .118: the switch is an extra TICK. Delay-evolved walkers .017; C4-08 descendants .332. 10/60 walkers show a distinct loud step (mixed operators, no broken jumps). Promoted to T-X12.
- **T-ARCH4/M1** <- P-D03 (MATERIAL): RECONCILER: growth under trap-NOP (+1.80 baseline) REVERSES under no_growth (-3.1 frozen, -6.0 deletion-heavy), lencost (-1.4/-3.1), symdel+delheavy (-3.5), and under trap-HALT (-0.76); length-balanced proposals still grow (+2.35). When growth reverses, exaptation RISES (.064-.074 vs .032) and structural diversity rises (1.56-1.64 vs 1.19): length accumulation was suppressing exaptation. Acceptance rule and proposal opposition each suffice; the mechanism is confirmed and controllable.
- **T-E07** <- P-D07 (MATERIAL): RECONCILER: absolute retained score is LOWER under weather at every dose (.0011 vs .0032 at f=.1 ... .0001 vs .0004 at .45; raw differences outside the band); intact margin under weather is a third of static (.0019 vs .0061, outside band); the sham arm equals static exactly. The ability-adjusted contrast flips sign across doses (POSITIVE at .1, NEGATIVE at .3/.45) - covariate extrapolation again (D071). Reading: weather selects for state AVOIDANCE in this organism. Promoted to T-X13.
- **T-E06** <- P-D05 (MATERIAL): RECONCILER: NOT_REPLICATED as mutual invasibility (1/12 cells at rate 1.0) but a REVERSAL: TREE invades TAPE in 8/12 cells at 1.0 vs 4/12 at 0.5 while TAPE's invasion collapses; the recombination rate sets the DIRECTION of dominance and mutual invasibility is a crossing point. Promoted to T-X14. P-A07's evidence is corrected: one cell at the crossing.
- **T-X11** <- P-B10 (MATERIAL): RECONCILER: the plateau is a SEARCH LIMIT: Bayes-optimal router precision 1.0/1.0/.96/.80 at overlap .1/.2/.35/.5 vs evolved .55/.56/.50/.43; the gap (.37-.46 at G60) shrinks only slightly by G240 (.36-.45). The linear activation policy under this GA does not approach the ceiling; continuation: population 256 / 1000 generations / a nonlinear policy.
- **T-E03** <- P-B07 (not material): RECONCILER: the representational tax was INERT: non-zero-weight share stays .985 at every lambda because clipped Gaussian mutation never drives a weight below the .05 threshold; MI excess, sparsity and score unchanged. Instrument fact (the burden coordinate must be attainable by the mutation operator - the e08 lesson again), not a null about burden pressure.
- **T-X05** <- P-D12 (not material): RECONCILER: amputation alone at intervals 2/5/10/20 lowers burden (scalar .81-1.52 vs 1.87) without raising held64 (139-162 vs 156, all inside the band); the TAX+AMP held64 association in e08 is not carried by structural pressure alone.
- **T-E06** <- P-D11 (MATERIAL): RECONCILER: 80-generation mixed runs seeded 50/50 COEXIST in 2/4 (t3 r.5, TREE .53/.58), 1/4 (t2 r.5), 2/4 (t3 r1.0), 3/4 (t2 r1.0). e06 never ran mixed 80-generation runs after adding resource sharing (its gate refused on rare invasion), so 'coexistence unreachable' was a statement about invasion from 10%, not about coexistence from parity. Coexistence without mutual invasibility - a protected or slow-fixing regime - is now on record; continuation: 240 generations, seeded-frequency sweep.
- **T-X01** <- P-D11 (MATERIAL): RECONCILER: tournament 2 x recombination 1.0 gives the most coexisting runs (3/4) and TREE .73; tournament 2 alone lowers TREE (.54) and coexistence (1/4). The two axes do not simply add.
- **T-E06** <- P-D13 (MATERIAL): RECONCILER (D076: sham not draw-matched to STATIC; read DAMAGE vs SHAM): blind deletion of 10% of body units per generation tilts the ecology toward TAPE (final TREE .43 vs .885 under sham; growth -.006 vs +.044) and raises coexistence (2/4 vs 1/4); TREE bodies shrink (8.5 vs 13-16 units). Subtree contraction hurts trees more than instruction loss hurts tapes: representation-blind damage is not substrate-neutral in effect.
- **T-E07** <- P-D13 (MATERIAL): cross: e07's damage family in e06's ecology changes which representation wins (see T-E06)
- **T-ARCH4/M1** <- P-D01 (MATERIAL): RECONCILER: locality DOSE SURFACE (57536 rows, 360 cells, 126 programs, held-out W2_K2d1): loss per doubling of units lost k +0.145 vs per doubling of sites s +0.024 - the law is mostly a dose in units, with a small locality term (k=8 spread over 1 site .66 vs 8 sites .77, +.05 outside the paired band; k 2->8 at one site .43->.66, +.40). Kind: operand damage .36 vs delete/opcode/move .72-.75 (operands are the soft coordinate). Decode trap (-0.030) and placement (-0.002) inert. Genotype set: parents and 16-step walkers lose ~.20 more than C4-08 selected tops (selection built robustness to structural loss). Continuation manifold: instruction-role map of the operand softness; pairwise site epistasis at fixed k; other held-out families; C4-08 tops vs their own ancestors.

## State after the cycle (31 trajectories, 7 in TEMPORAL_STASIS)

- T-ARCH4: ACTIVE - reactivated into the Nestor pool by operator directive; scoped nodes carry any future stasis
- T-ARCH4/D1: ACTIVE - a locality law is emerging across two perturbations; next: dose-response in number of sites at fixed k
- T-ARCH4/M1: ACTIVE - a surface exists; continuation: instruction role, pairwise epistasis, other held-out families
- T-ARCH4/P1: ACTIVE - reactivated into the Nestor pool by operator directive; scoped nodes carry any future stasis
- T-ARCH4/R1: TEMPORAL_STASIS[starting_population=degenerate-gen0 x representation=trap-decode] - three decode rules strike the same surface; the next informative perturbation needs a different starting population (e.g. injected in-table generators as in C5-04)
- T-ARCH4/S1: TEMPORAL_STASIS[search_depth=walk-depth] - depth alone saturates; further depth is not informative; other search-dynamics axes (band rule, proposal weights) remain open
- T-ARCH4/W1: ACTIVE - mechanism narrowed to cross-tick state; continuation: content of the inserted tick, K=2 worlds, persist off
- T-ARCH5: ACTIVE - sibling descendant recorded from origin/main
- T-E01: ACTIVE - initial record
- T-E02: ACTIVE - initial record
- T-E03: TEMPORAL_STASIS[burden=L0-threshold on continuous weights x mutation=clipped-gaussian] - this coordinate cannot move under this operator; a descendant needs a mutation that can zero weights or a magnitude-based burden
- T-E04: ACTIVE - initial record
- T-E05: ACTIVE - initial record
- T-E06: ACTIVE - damage is a new axis for the ecology; continuation: dose f, damage one substrate, draw-matched sham
- T-E07: TEMPORAL_STASIS[world=e01-retention x organism=5-gene] - two rulers and two dose designs strike the same surface: a one-parameter retention policy can only avoid or accept damage; the next informative perturbation needs an organism that can represent protection (a redundancy channel)
- T-E08: ACTIVE - eligibility surface confirmed to be about generalisation, not selection rule; next: P-A04's breadth result
- T-E09: TEMPORAL_STASIS - chain form still cannot compose on a second task; the boundary is the representation, not w13
- T-X01: ACTIVE - the floor is now a measured function of structure; next: apply the slowest structure inside an ecology run
- T-X02: ACTIVE - screening axis measured; next: rotating seed schedules
- T-X03: ACTIVE - initial record
- T-X04: ACTIVE - a bistable regime exists on the geometry axis; next: seeded-frequency sweep at phi 0.5 to map the separatrix
- T-X05: ACTIVE - one factor excluded; next: tax alone at matched burden, then tax x amputation at matched burden
- T-X06: TEMPORAL_STASIS - an instrument fact, fully mapped by the probe curve; the next informative step is its use inside a reposed T-E07, not further probing
- T-X07: ACTIVE - initial record
- T-X08: TEMPORAL_STASIS - the specialisation explanation is falsified and the remaining explanation (intrinsic channel economics) has no further perturbation available at this scale
- T-X09: ACTIVE - initial record
- T-X10: ACTIVE - initial record
- T-X11: ACTIVE - a search-limit finding with obvious continuations
- T-X12: ACTIVE - anomaly promoted to its own node in cycle 2
- T-X13: ACTIVE - anomaly promoted to its own node in cycle 2
- T-X14: ACTIVE - anomaly promoted to its own node in cycle 2

Rank is temporary. Every trajectory outside the ten waits with its record intact. The next cycle begins with global re-evaluation of the whole pool.