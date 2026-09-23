# CW01 priority loop - cycle report 2026-09-18

Ten frozen perturbations executed under their own preregistrations (PREREG.json hashed before each run).

| rank | id | parent | type | disposition / reading | s |
|---|---|---|---|---|---|
| 1 | P-A11 | T-X07 | serendipity | chains do not materially exceed the single-op ceiling on held-out lifetimes | 4.5 |
| 2 | P-B05 | T-E02 | serendipity | order unchanged (p_factor first remains the rule) | 112.1 |
| 3 | P-A04 | T-X02 | search-boundary | material=False | 923.4 |
| 4 | P-B09 | T-X08 | exploratory | no relabelling-clearing change in rel(7); inversion persists or is noise | 45.9 |
| 5 | P-B03 | T-E07 | transplant-break-inconclusive | NEGATIVE (weather lineages retain less) | 94.2 |
| 6 | P-A08 | T-X04 | exploratory | no phi gives mutual invasibility; the asymmetry flips between [(0.0, 0.25), (0.25, 0.5), (0.75, 1.0)] | 29.4 |
| 7 | P-A10 | T-X01 | exploratory | material=True | 26.8 |
| 8 | P-A07 | T-E06 | search-boundary | TREE invades under some variation regime | 17.7 |
| 9 | P-B04 | T-X09 | break-null-changed-economics | NULL | 34.3 |
| 10 | P-A01 | T-E08 | break-inconclusive | UNREACHABLE_UNDER_RULE | 69.9 |

## Evidence appended this cycle (26 events, 14 material)

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

## State after the cycle (20 trajectories, 3 in TEMPORAL_STASIS)

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