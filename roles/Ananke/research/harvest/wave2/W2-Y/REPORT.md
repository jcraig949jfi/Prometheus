<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-Y; sha256(report)=2f1d7fdd007fdb81; delimited; see REPORT.provenance.json -->
# W2-Y: are the C1 B/B2 boundary verdicts predictable from the joint ceiling? (worker W2-Y, Ananke Wave 2)

**Setup.**
- Worktree: F:/Prometheus-worktrees/ananke-base-role. All files are in roles/Ananke/research/harvest/wave2/W2-Y/.
- CPU only: CUDA_VISIBLE_DEVICES=-1, `torch.cuda.is_available()==False` asserted, 2 threads per process.
- I made no git writes and no repo edits.
- I imported W2-P `task2_timing`/`w2p_common` and W2-U `w2u_ceil` read-only. I took the P-1 `relay_refresh` function source from decay_plant.py and ran it with exec. I did not import that module, so its experiment did not run.

**Files** (all under W2-Y/, outputs in out/):
- `task1_ceilings.py`: the W2-P/W2-U joint ("light cone", LC) ceiling for all 1056 B/B2 rows, on each row's own physics and env and its own seeds:
  - plant seeds `world_seeds(H_int(search_seed,0x9147),32)`, campaign.py:299;
  - held seeds for evolve rows.
- `analyze1.py`: the per-verdict decomposition with the LC ceiling, for all 37 verdicts.
- `flood_ceil.py` + `task2_flood.py`: a tighter "flood ceiling" (section 1, F2), with known-answer checks.
- `analyze2.py`: the same decomposition with the flood ceiling.
- `task3_decay.py`: re-scores the decay transects with P-1's relay_refresh plant.
- `task4_a0_topology.py`: a check of W2-U's topology claim.
- `make_table.py` -> out/verdict_table.txt: the merged table.

**Method.**
- Identity model per transect: metric_l = .5 + g·(ceil_l − .5).
- g is fitted by least squares through (.5,.5) on the transect's **non-boundary** levels. A pooled g and g=1 are also stored.
- Predicted step = g·Δceil over the boundary pair. Residual = observed jump − predicted step. Share = predicted / observed.
- Classes:
  - **IDENTITY:** share ≥ .67 and the residual fails the PREREG s8 jump test (|res| < max(.10, 3·se)).
  - **GENUINE:** the residual passes that test and share < .33.
  - **PARTIAL:** everything else.
- sens/emit verdicts are program-space metrics, not accuracies, so they get NA.

## 1. Findings

**F1 [V] The per-verdict table (all 37).** Confidence: high for the numbers. Known-answer check: the level means I recompute from the rows equal the recorded verdict means in 21/21 accuracy verdicts.

Columns:
- LC and FLOOD give the ceiling per level, then predicted step / residual / class.
- B2 is the residual on the fresh-seed transect, using the B-fitted g.

| # | Verdict | Label | Means | LC ceiling | LC class | Flood ceiling | Flood pred / resid / class | B2 resid | Final |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RELAY delta b1 evo **acc** [0,1] | CAND | .592 .772 .681 | .75 1 1 | PARTIAL (+.09/+.09) | .613 .995 1 | +.139/+.042 IDENTITY | +.06 | IDENTITY |
| 2 | HOLD decay b1 evo acc [1,2] | CAND | .643 .609 .847 .785 | 1 flat | GENUINE | – | – | B2 jump −.164 (sign reversed) | NOT REPRODUCED; noise |
| 3 | RELAY decay b0 phys plant [0,1] | **SUPP** | 1 .547 .543 .568 | 1 flat | GENUINE | 1 flat | 0/−.453 GENUINE | −.46 | PLANT-DESIGN: relay_refresh 1.0 1.0 1.0 1.0 |
| 4 | RELAY delta b0 phys plant [0,1] | **SUPP** | .585 .983 .991 | **1 1 1** | GENUINE (LC blind) | **.685** .999 1 | +.308/+.089 IDENTITY | +.051 | IDENTITY (+ small plant term) |
| 5 | RELAY economy b0 phys plant [1,2] | **SUPP** | 1 1 .547 | 1 flat | GENUINE | 1 flat | GENUINE | −.46 | NOT IDENTITY; energy, unresolved |
| 6 | RELAY decay b1 phys plant [0,1] | **SUPP** | .80 .536 .535 .575 | 1 flat | GENUINE | 1 flat | GENUINE | −.262 | PLANT-DESIGN: refresh .80 .823 .783 .814 |
| 7 | RELAY delta b1 phys plant [0,1] | **SUPP** | .486 .641 .755 | .5 1 1 | PARTIAL (+.255/−.101) | .5 .955 1 | +.232/−.078 IDENTITY | −.088 | IDENTITY (step smaller than the identity predicts) |
| 8 | RELAY economy b1 phys plant [1,2] | **SUPP** | .812 .783 .568 | 1 flat | GENUINE | 1 flat | GENUINE | −.187 | NOT IDENTITY; energy, unresolved |
| 9 | RELAY delta b1 evo plant [0,1] | CAND | .559 .826 .95 | .75 1 1 | IDENTITY (+.225/+.043) | .611 .995 1 | +.345/−.078 IDENTITY | −.118 | IDENTITY |
| 10 | MAJ topology b1 phys plant [1,2] | CAND | .625 .611 .503 .618 .493 | .81 .742 .541 .798 .837 | PARTIAL | .726 .665 .514 .716 .511 | −.082/−.026 IDENTITY | +.03 | IDENTITY |
| 11 | MAJ topology b1 phys plant [2,3] | CAND | same | same | PARTIAL | same | +.120/−.005 IDENTITY | −.015 | IDENTITY |
| 12 | MAJ topology b1 phys plant [3,4] | CAND | same | same | GENUINE (LC: global .837) | same (global .511) | −.122/−.003 IDENTITY | −.005 | IDENTITY |
| 13 | MAJ economy b1 phys plant [1,2] | CAND | .625 .64 .531 | .81 flat | GENUINE | .726 flat | GENUINE | −.072 | NOT IDENTITY; energy, unresolved |
| 14 | FLIP decay b0 phys plant [0,1] | CAND | .659 .49 .521 .508 | .975 flat (copy .721) | GENUINE | – | – | −.112 | PLANT-DESIGN: refresh .659 .630 .651 .635 |
| 15–18 | HOLD decay b0/b1 phys plant [0,1], [1,2] | **SUPP** ×4 | 1 .75 1 1 | 1 flat (no transport) | GENUINE | – | – | ±.24/.25 | PLANT-DESIGN [I], write-once latch |
| 19 | HOLD gap b1 phys plant [0,1] | CAND | 1 .75 .75 | 1 flat | GENUINE | – | – | −.25 | PLANT-DESIGN [I], same erosion |
| 20–21 | HOLD decay b1 evo plant [0,1], [1,2] | CAND ×2 | 1 .75 1 1 | 1 flat | GENUINE | – | – | ±.25 | PLANT-DESIGN [I] |
| 22–37 | sens ×8, emit ×8 (rules, prog_len, state_dim, channels, topology, delta) | 3 SUPP (MAJ and FLIP emit vs rules), 13 CAND | – | ceiling flat in 15/16; Δ = −.021 in XOR state_dim emit | NA | – | – | – | PROGRAM-SPACE |

Counts:
- **Accuracy verdicts (21):**
  - IDENTITY 8: the 4 RELAY delta verdicts, the 3 MAJ topology verdicts and the evolved RELAY acc.
  - PLANT-DESIGN 10: 3 decay verdicts confirmed by re-scoring with the refresh plant; 7 HOLD verdicts inferred.
  - Energy, unresolved: 3 economy verdicts.
  - Not reproduced: 1.
- **Under the LC ceiling alone:** only 1 IDENTITY, 4 PARTIAL and 16 GENUINE. The light cone misses the identity wherever routing is random (F2).
- Strongest objection: the flood ceiling is a Monte-Carlo expectation of an upper bound, not the bound on the exact engine draws (32 reps per world and trial). The MC error on ceiling means is well under .01.
- Unresolved: the g_local fits rest on 1–3 levels. For the 3-level transects, g comes from a single level.

**F2 [V] The W2-P/W2-U light-cone ceiling is wrong on global topology and dest_mode "sample".** Confidence: high.
- engine.py `_emit` (482–530):
  - **global:** each of the F=fanout copies goes to a uniformly random other site (rng.ROUTE). A program cannot choose the actuator.
  - **sample:** each copy goes to a neighbour drawn by the routing weights w, which start uniform (engine.py:158). Only plastic_route can bias them.
- `T2.earliest` treats every site as addressable at 1 hop on global. It also ignores loss, jitter and dup.
- My `flood_ceil.py` is a maximal-flood any-program bound:
  - every informed site emits all its copies at every awake tick;
  - it includes random destinations, loss, jitter, dup and wake;
  - it optimistically ignores cap, collision, economy, decay and noise.
- Known-answer checks:
  - KA1: with loss, jitter and dup off and deterministic destinations it equals T2 lc exactly, 9/9 rows (RELAY and MAJ; torus and ring; values .669–1.0).
  - KA2: a global single-hop-round closed form, 1−(1−.9/63)^8 = .1087, against MC .1090.
- Effect at RELAY delta b0 (global, sync period 2, lat 2, fanout 8): LC ceiling 1, 1, 1 against flood .685, .999, 1.0. Under LC the delta-4 plant collapse looks "GENUINE"; under the flood ceiling it is 78% identity.
- MAJ topology b1: the global level drops from LC .837 to flood .511 and random from .541 to .514. All three topology "boundaries" become identity with residuals ≤ .026.
- Command: `python task2_flood.py ka && python task2_flood.py rows && python analyze2.py`.

**F3 [V] The RELAY delta boundary, P1's lead boundary, is the transport-time identity.** Confidence: high.
- **b0 (.585 → .983):**
  - The flood ceiling steps .685 → .999. Predicted step +.308 (g = .98, fitted on delta 16); observed +.398; residual +.089 (3.7 SE, but below the .10 jump threshold). B2 residual +.051.
  - The residual says relay_flood attains only 46% of its headroom at delta 4 against 97% at delta 8. That is a small plant-design term on top of the identity.
- **b1 (.486 → .641):**
  - The ceiling steps .5 → .955. The identity over-predicts (+.232 against +.155; residual −.078, B2 −.088). The boundary exists only because the ceiling leaves .5.
  - Its size is plant-limited: jitter 3 and dup on torus dest-all; plant attainment .31 at delta 8 and .51 at delta 16.
- **The evolved-competence CANDIDATE** (RELAY acc delta 4 → 8, +.18): flood-predicted +.139, residual +.042 (B2 +.060).
  - Champion attainment of the ceiling falls with delta (.81, .55, .36). The champions are not better at delta 8; only the ceiling rose.
- Strongest objection: g_local is fitted on one level (delta 16). Under g=1 the residual is +.084 (b0) and −.30 (b1). Under every g I tried, the step is the ceiling stepping and the plant never beats it.
- Unresolved: whether the b0 +.09 under-attainment at delta 4 is relay_flood's write-on-change echo at period 7 (next question 3).

**F4 [V] The decay boundary vanishes under a decay-robust plant (E-W13 confirmed on the actual C1 transect rows).** Confidence: high.
- `task3_decay.py` re-scores every B row of the RELAY decay transects (b0, b1) and the FLIP decay transect (b0). It uses each row's own physics and plant seeds, with prog_len max(L,16).
- KA: relay_flood at prog_len max(L,12) reproduces the recorded plant accuracy exactly in 12/12 rep-0 rows.

| Transect | relay_flood (recorded) | relay_refresh |
|---|---|---|
| RELAY b0 | 1.0, .547, .543, .568 | 1.0, 1.0, 1.0, 1.0 |
| RELAY b1 | .800, .536, .535, .575 | .800, .823, .783, .814 |
| FLIP b0 | .659, .490, .521, .508 | .659, .630, .651, .635 (no step; FLIP stays copy-limited) |

- Every decay level's ceiling is identical by construction, because decay changes no transport dial.
- So the RELAY and FLIP decay boundaries are **plant-design**: relay_flood writes on change only and never refreshes S0. They are not physics.
- Strongest objection: relay_refresh is a single alternative design. It does show a decay-robust design exists at every level of both bases, which is all the falsification needs.
- Unresolved: B2 rows were not re-scored with the refresh plant. B2 shares physics with B, so I expect the same result.

**F5 [I] The HOLD decay and gap boundaries are plant-design too: a write-once latch eroded by integer decay.** Confidence: medium-high.
- The HOLD ceiling is flat at 1.0: sensor = actuator (envs.build HOLD branch), and sync period ≤ cue_len.
- Decay is S −= S >> shift (engine.py:445). At shift 1 negative memories reach 0 in about 9 ticks, while positive ones stall at 1. The latch therefore loses half the trials when gap ≥ 8.
- The transect rows fit this:
  - the dip appears only at decay 1, with gap 8 or 16;
  - in the gap transect at decay 1: gap 4 → 1.0, gap 8 and 16 → .75;
  - at decay 3, gap 16 still gives .992.
- A latch that re-normalises S0 every awake tick would survive, because decay applies once per tick after the program. I did not run this.
- Strongest objection: the sign asymmetry is a genuine substrate property, as DESIGN s10 says. It only bites non-refreshing memories.
- Unresolved: an executed refresh-latch check (next question 2).

**F6 [I] The economy boundary is the only accuracy boundary that is neither identity nor shown to be plant-design.** Confidence: medium.
- No transport ceiling moves across economy levels.
- Arithmetic at "high" (e_income 4, e_max 100, c_emit 4 × copies, c_op 1 per non-NOP op per awake tick, c_mem 1):
  - relay_flood has 12 non-NOP ops, so it spends about 13 per awake tick against income 4.
  - b1 (torus r3 dest-all, sync period 1): emit cost 96. E hits 0 after about 11 ticks and never recovers, so only about the first trial transports. Predicted plant ≈ .54; observed .568.
  - b0 (global, period 2): E runs out after about 40 ticks, about 2 trials; predicted ≈ .58, observed .547.
- But even a minimal relay (3–4 ops plus c_mem) has spend ≥ income at b1. Emission costs 96, close to e_max, so a frugal program could emit about once in many trials. At b0 an energy-limited random flood is weak.
- So economy-high plausibly caps every program: energy physics, unresolved.

**F7 [V] W2-U's "global is the worst topology once normalised" depends on the light-cone ceiling.** Confidence: medium (small sample).
- Sample: 30 A0 RELAY cells per topology (rng 11), exact plant seeds.

| Topology | LC ceiling (mean) | Flood ceiling (mean) | Normalised plant, LC | Normalised plant, flood |
|---|---|---|---|---|
| global | .925 | .701 | .061 | .125 (highest) |
| random | .801 | .752 | .075 | .098 |
| ring | .756 | .715 | .09 | .118 |
| smallworld | .76 | .727 | .106 | .094 |
| torus | .821 | .734 | .042 | .084 |

- The light cone overstates global's ceiling more than any other topology's (−.22). The ranking flips in this sample. Each normalised mean rests on n ≈ 16–21, so the ranking is noisy.
- Command: `python task4_a0_topology.py`.

**F8 [I] The emit "boundary" along delta (RELAY b0 evo emit, delta 8 → 16) is probably an exposure-time identity.**
- frac_emitting = mean(emit_rate > 0), and episode length T = 12·(delta+3) is 132 against 228 ticks.
- A program that emits rarely is more likely to register any emission over the longer episode. Untested.

## 2. Proposed fixes
- No executable bug in campaign.py, so no diff.
- **NEUTRAL (C2 tooling):** use `flood_ceil.ceilings`, not the light cone, for admission and normalisation wherever topology = global or dest_mode = sample (and where loss, jitter or dup are > 0).
- **NEUTRAL:** C2's boundary detector should also report each boundary after subtracting the ceiling-predicted step, as computed here.
- **Annotation proposal for C1_ERRATA (the principal decides):**
  - §4 "SUPPORTED, physics, known design": delta = transport-time identity (F3); decay = relay_flood design artefact, with the transect re-score (F4, extends E-W13); economy = the only remaining physics candidate, unresolved (F6).
  - HOLD ×4 SUPPORTED = non-refreshing-latch artefact [I].

## 3. Disagreements
- **W2-U F4 / its consequence** ("RELAY's delta boundary is predictable from the ceiling alone"):
  - The conclusion is right, but not with W2-U's ceiling. At b0 the LC ceiling is flat at 1.0 across delta 4/8/16, so the LC model calls the SUPPORTED delta step GENUINE.
  - The identity appears only with the flood ceiling, i.e. random routing on global.
- **W2-U F4 / F6 topology** ("survives and strengthens; global worst once normalised"): not robust. Global's LC ceiling is overstated by about .22 (F7).
- **W2-P task2_timing assumption** "any neighbour reachable": false for global and sample (engine.py `_emit`).
  - Consequence: W2-P/W2-U construction-capped counts are undercounts on global and sample rows.
  - Example: MAJ topology b1 random/global, flood about .51, so capped; LC .54/.84.
- **C1_REPORT §4 and the §2 ladder** ("L2' gated by decay, delay, energy cost (SUPPORTED)"): decay is design, delay is identity, energy is open.
  - The report's own reading ("SUPPORTED boundaries belong to a known hand-written design") is directionally right but understated. For delta the boundary does not belong to the design at all: any design faces the same transport ceiling.

## 4. Consequences
- **P1 (HELD):** the label is mechanically correct (≥ 1 RELAY plant SUPPORTED) and must stay; it is frozen.
  - Its scientific content: the delta boundary is the trivial "signal must arrive before readout" bound (F3); the decay boundary is a relay_flood artefact that disappears with a refreshing plant (F4).
  - Only economy might be substrate physics, and that is unproven (F6).
  - P1 should be read as "HELD; content identity + plant-design; economy open". It supports no physics claim beyond the transport bound.
- **C1_REPORT boundary claims:**
  - Of the 13 SUPPORTED: 2 are identity (delta), 2 plant-design (RELAY decay), 4 plant-design [I] (HOLD), 3 program-space prior (emit vs rules), and 2 energy, open.
  - **No SUPPORTED boundary is established physics beyond the light-cone/flood bound.**
  - The single evolved-competence CANDIDATE is identity.
  - "There is no reproducible phase boundary in EVOLVED competence" is strengthened: even the candidate is the ceiling.

## 5. Next questions (ranked)
1. **Energy-aware any-program ceiling for economy "high".** Compute the minimum spend of any relay program against income, with copies × c_emit vs e_max; or run a minimal 3–4-op relay plant on RELAY economy b0/b1. That decides whether economy is physics. (cheap: about 30 engine evaluations)
2. **Refresh-latch on the HOLD decay and gap transects** (S0 := sign(S0)·256 every awake tick, threshold 128). Does the .75 dip vanish, turning F5 from [I] into [V]?
3. **The b0 delta-4 under-attainment** (plant reaches 46% of the flood headroom, against 97% at delta 8). Is it relay_flood's echo across the period-7 trial boundary? Test relay_refresh or a TTL relay at delta 4.
4. **Re-run W2-P/W2-U construction-capped counts with the flood ceiling** for global and sample rows (RELAY, MAJ, XOR, FLIP). How many more NULLs are construction-capped?
5. **Re-run W2-U's A0 normalisation on all 1000 cells with the flood ceiling** (about 300 s at R=8). This settles whether topology survives normalisation.
6. **The emit-vs-delta exposure identity (F8).** Normalise frac_emitting per tick of episode length and recheck the RELAY b0 evo emit verdict.
7. **C2 boundary criterion:** require that a boundary survive subtraction of the ceiling-predicted step. Preregister it before C2 data.

## 6. Inference ledger
question | evidence | result | confidence | strongest objection | unresolved | next
- Do C1 accuracy boundaries follow the LC ceiling? | task1_ceilings + analyze1, KA means 21/21 | LC: 1 IDENTITY, 4 PARTIAL, 16 GENUINE | high (numbers) | LC is wrong on global/sample | — | F2
- Is the LC ceiling correct on global/sample? | engine.py _emit 482–530; flood_ceil KA1 9/9, KA2 .1090 vs .1087 | no; random destinations | high | flood is an MC expectation | exact-draw bound | Q4
- RELAY delta boundary | analyze2: b0 pred +.308 vs +.398, b1 +.232 vs +.155, acc +.139 vs +.18; B2 agrees | IDENTITY | high | g_local fitted on 1 level | b0 +.09 plant term | Q3
- MAJ topology boundaries | flood: global .511, random .514 | IDENTITY ×3 (resid ≤ .026) | medium-high | MAJ flood assumes independent per-sensor floods | — | Q4
- Decay boundary under a robust plant | task3_decay, KA 12/12; refresh flat | PLANT-DESIGN (RELAY b0, b1; FLIP b0) | high | single alternative design | B2 not re-scored | —
- HOLD dip | decay arithmetic engine.py:445; gap/decay transect pattern | PLANT-DESIGN [I] | medium-high | asymmetry is substrate physics | refresh-latch not run | Q2
- Economy | energy arithmetic; flat ceilings | NOT IDENTITY; physics vs plant open | medium | minimal programs may also starve | energy ceiling | Q1
- W2-U topology normalisation | task4: global LC .925 vs flood .701; normalised .061 → .125 | not robust | medium | n ≈ 20 per topology | full 1000 cells | Q5
- Emit vs delta | T = 12·(delta+3) | exposure identity [I] | low-medium | untested | — | Q6

## 7. Compute used
About 1140 CPU-seconds, or 0.32 core-hours, against a 0.4 cap. CPU only, 2 threads, every run under 10 minutes wall.

| Run | CPU-s |
|---|---|
| task1 LC ceilings | 79 |
| first flood-ceiling run: unvectorised, killed at 600 s timeout, no output | ≈ 600 |
| flood KA checks | 5 |
| flood rows | 27 + 80 |
| decay re-score (36 refresh + 12 KA engine evaluations) | 298 |
| A0 topology check | 42 |
| analyses | ≈ 10 |

**Process note:** task1_ceilings.py first saved its output through w2p_common.save, which writes into W2-P/out/. The new untracked file W2-P/out/task1_ceilings.json existed there for about 5 minutes. I moved it to W2-Y/out and patched the script to save locally. Nothing in W2-P was overwritten (git status of W2-P is clean).
