<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-B; sha256(report)=daf47178cb05c8d3; delimited; see REPORT.provenance.json -->
W2-B REPORT: RULER REACHABILITY PROOFS (Opus worker W2-B for Ananke, Wave-2 inference saturation)

**Directory:** `roles/Ananke/research/harvest/wave2/W2-B/`

**Files:**
- Code: `rows_audit.py`, `analytic.py`, `adversaries.py`, `rulers_extra.py`, `rulers_c1.py`, `attain.py`, `certify_c1.py`, `reverdict.py`
- Checks: `check_flip.py`, `check_xor.py`, `check_reachcert.py`, `check_carryover.py`, `check_beyond_hop.py`, `check_census_identity.py`
- Tests: `tests/test_attain.py`, `tests/test_reachcert_patch.py`
- Patch: `patch/reach_certificate_window_decision.diff` (with `patch/orig` and `patch/patched` copies)
- Outputs: `out/*.json`

**Ground rules I kept:**
- CPU only: `CUDA_VISIBLE_DEVICES=-1`, `device="cpu"`, 2 threads. `w2b_common` asserts that `torch.cuda.is_available()` is False.
- No git writes. I read no C4 reviews, nothing under `c3_holdout_D*`, and no other Wave-2 worker's files.
- Line numbers are at worktree HEAD `edf1f1f12`. Only `report.py` moved during the session.

## 0. HEADLINE

| ruler | verdict | the counterexample, in one line |
|---|---|---|
| SIGNAL | sound | sound as a task-competence gate in RELAY, MAJ and HOLD |
| SIGNAL / INTEGRATION on XOR | CHEATABLE as evidence of parity | every non-parity 2-input readout scores ≤ .75 and crosses SIGNAL |
| SIGNAL on FLIP | CHEATABLE as evidence of feedback tracking | the block schedule is deterministic. FLIP_CLOCK learns m0 from the first teacher, ignores every later one, and scores 1.000 [1,1]. P-FLIP falls to .500 when the later teachers are removed. |
| zero_comm (RELAY/XOR/MAJ) | DEGENERATE | forced to exactly .5 in every pair |
| COMM_DEPENDENT (same families) | alias of SIGNAL | no independent content |
| LOCAL_ONLY (same families) | UNREACHABLE | can never be true |
| env-permutation clause | DEGENERATE | passes for every program |
| CAUSAL_SUPPORT (comm families) | reduces to one live clause | equals the packet-ablation clause (verified on 8/8 D-wave comm rows) |
| REACH_BEYOND_HOP (XOR/MAJ) | CHEATABLE | a one-hop emitter always fires it; a silent program fires it when sensor spacing > hop |
| REACH_BEYOND_HOP (global topology) | UNREACHABLE | every distance is ≤ 1 |
| relay_flood plant-viability gate (≥ .75) | never crossed in XOR, MAJ, FLIP | 0/1000 A0 cells each |
| 2-level transects | UNREACHABLE | 8 of 104 C1 transects can never produce a boundary candidate |
| size-free law test | forced pass | for lattice-local laws (all 15 wave-E rows) |
| absolute swap FLIP | unreachable below normal ≈ .62–.66 | needs that normal even with a perfect follow |
| swap_rel | attainable iff the identification guard holds | no-op arms force NO_EFFECT_REL: 24 of 98 W-Z NO_EFFECT_REL arms have swap scores identical to normal |
| C1b predictors (M, CARRYOVER, C) | exactly .5 whenever the predictor is twin-symmetric | |
| AUDIT3's 95% bar | miscalibrated | a perfect instrument fails it with P ≥ .14 |
| reach_certificate (H-INST draft) | CHEATABLE as a null-admissibility certificate | an earlier-trial hook makes a trial ABSORBED; a 1/16-world magnitude nudge reads REACHED_OUTPUT. Patch provided. |
| proposed lag profile | bounded by accuracy | uninformative at decision level for competent specimens |
| proposed per-sensor census | SOUND for XOR (proved) | |

**The certifier** (`attain.py`) generalises `lens.verify_reach`. Given a ruler and a family of worlds × programs with roles (null / adversary / plant / probe), it reports:
- the attainable range;
- null and adversary scores, and the cheapest crossing;
- the eligibility count;
- forced, pair-exact and aliased outcomes;
- a verdict (SOUND / CHEATABLE / DEGENERATE / UNREACHABLE / NO_PLANT).

It also has an analytic half for CI-bound gates. 9/9 known-answer tests pass. The certifier on the C1 rulers is in `out/certify_c1.json` and `out/certify_c1_final.json`.

## 1. RULER TABLE (deliverable 1)

**Notation:**
- P = mirror pairs, K = scored trials per world.
- "min true for 50%" = the true accuracy at which the gate is crossed half the time (normal approximation, twin-equivariant program, `analytic.py`).
- [V] = verified here by a check or a proof (P1–P13 in section 2). [I] = inferred.

| ruler | definition (file:line) | attainable range | forced by construction | cheapest adversary and score | verdict |
|---|---|---|---|---|---|
| SIGNAL lo99 > .55 | campaign.py:430; search.py:131-134 | lo99 in [0,1]. Min true for 50%: .614 at P32 K12; .574 at P256 K11 [V] | Constant policies give .5 per pair exactly. No-transport readouts give exactly .5 per pair in RELAY/XOR/MAJ [V P1]. | RELAY/HOLD: none. MAJ: a single-sensor relay (ceiling .70) crosses, but SIGNAL claims no integration there. XOR: non-parity readout .75 [V]. FLIP: FLIP_CLOCK 1.000 [V]. | SOUND for task competence. CHEATABLE as evidence of XOR parity or FLIP feedback tracking. |
| COMM_DEPENDENT | campaign.py:431-433 | RELAY/XOR/MAJ: equals SIGNAL | comm_delta_lo99 = lo99 − .5 exactly where zero_comm is forced (213/213 RELAY, 95/95 XOR, 174/174 MAJ rows, |diff| < 1e-9) [V] | n/a | DEGENERATE (alias of SIGNAL). In FLIP it is SIGNAL plus noise (zero_comm E = .5, exactly .5 in 62/94 rows). Sound in HOLD. |
| LOCAL_ONLY | campaign.py:434 | always False in RELAY/XOR/MAJ | SIGNAL ⟹ comm_delta_lo99 > .05 > .03 | n/a | UNREACHABLE (0/482 rows in those families) [V] |
| zero_comm control | search.py:129; assays.py:181; campaign.py:457 | exactly {.5} per pair, for every program | yes: shared physics draws, actuator never a sensor, negated targets [V P1] | null program scores .5 | DEGENERATE. Certifier: pair-exact across 19 rows. |
| CAUSAL_SUPPORT (comm) | campaign.py:443-458 | equals the packet_ablation clause | the zero_comm clause and the env_perm clause are both forced true | n/a | DEGENERATE in 2 of 3 clauses. CAUSAL equals the pa clause in 8/8 D comm rows [V]. |
| env_permutation in [.40,.60] | assays.py:214-228; campaign.py:447 | E = .5 for any program. Certifier range .474–.500; C1 range .495–.512. | yes [V P5] | the null passes | DEGENERATE (cannot fail) |
| packet_ablation ≤ normal − .10 | assays.py:174-185 | drops arrivals in [t0, ro) only | an arrival at the readout tick survives | lag-0 transport: M3 specimens .697/.686 under the C1 window | UNREACHABLE for lag-0 transport, giving false NOT_SUPPORTED (known C1_ERRATA E1; restated) |
| memory_ablation (HOLD) | assays.py:186; campaign.py:451-454 | resets S only | non-S carriers (inbox, w, Kp, in-flight) are untouched | the M2 delay line | UNREACHABLE for non-S memory (known D-B/E3) |
| REACH_BEYOND_HOP, legacy | campaign.py:439; assays.py:249, 258, 276-298 | {0,1}. Always 0 on global. | reach is measured from sensor 0, but every perturbed sensor diverges | One-hop emitter (no relay): 1.0 on XOR d2/d3 and MAJ at X0 r3. Silent: 1.0 on MAJ X0 d2 and ring24 MAJ; 0 on XOR d ≤ hop [V check_beyond_hop] | CHEATABLE (XOR/MAJ). UNREACHABLE (global, P4). Sound for single-sensor families (RELAY/FLIP/HOLD). |
| REACH_BEYOND_HOP_NEAREST | assays.py:265-269, 300 | {0,1} | none found | silent and one-hop emitter both 0 [V] | SOUND in the tested family |
| INTEGRATION MAJ lo99 > .70 | campaign.py:437 | k ≤ 2 sensors cap at .70 exactly; 3 → .784; 5 → .837 [V P6] | none | Reader at the .70 ceiling: false positive .005 (P32 K12). One live sensor through maj_sum: .62, fails. maj_sum with 5 sensors: lo99 .771, passes [V]. | SOUND. False negatives when transport-limited, e.g. lossy integrators below .70 (H-SCI F5). |
| INTEGRATION XOR (= any XOR SIGNAL) | report.py:127-128; PREREG s7 | any readout that contradicts parity on ≥ 1 input combo scores ≤ .75 [V P2] | single input: x2-only exactly .5 per pair; x1-only E = .5 | not_P (NOR of the flags): .759 [.730, .785] at X0, M128. Crosses SIGNAL with power ≈ 1 at P32 [V] | CHEATABLE as parity. SOUND as "both inputs' information arrived". |
| relay_flood plant viability ≥ .75 | campaign.py:285-298, 113, 385 | RELAY/HOLD reachable; XOR max .574; MAJ max .693; FLIP max .734 [V rows] | relay_flood's XOR readout has no parity component (P2 corollary) [I] | n/a | UNREACHABLE for XOR/MAJ/FLIP in the census (0/1000 each). A one-hop majority plant (maj_sum) scores lo99 .771 at X0, so MAJ itself is not physics-capped. |
| transect boundary (s8) | campaign.py:588-616 (601) | 2-level dials are skipped | code needs ≥ 3 LEVELS; PREREG s8 asks for ≥ 3 REPLICATES per level | n/a | UNREACHABLE on 8/104 transects (XOR setrule ×2, XOR dup ×2, FLIP update_period ×2, HOLD update_mode ×2) [V] |
| SUPPORTED boundary | campaign.py:637-655 | needs B2 fresh seeds + the other base | B2 seeds shared across families (H-IMPL H6) | n/a | weakened independence (known) |
| size-free law (wave E) | campaign.py wave E; C1_REPORT s1 | pass is forced for N-invariant local mechanisms | d fixed; ring r3 d3 is one hop; HOLD actuator = sensor | the tested laws themselves (15/15 rows are these two kinds) [V rows] | DEGENERATE for the tested laws. Informative only for N-dependent physics (global/random routing). |
| TRANSFER_SUPPORT, cross-family | PREREG s7; campaign.py wave C | RELAY → MAJ is embedded (MAJ is a 5-sensor RELAY) | none | a plain relay reaches about .70 on MAJ (one sensor) [I]; no C1 row fired | CHEATABLE as evidence of cross-family generalisation [I]. HOLD variants forced (known F5). |
| lens.verify_reach | lens.py:252-297 | "applied" = whole-batch digest over any tick | REACHED = the plant fired at another physics | edit to an inert store reads "applied" (H-INST) | CHEATABLE (applied ≠ reached; known). plant_fired's FLIP path is unreachable below normal ≈ .66. |
| absolute swap rule | lens.py:125-133 | FLIP needs normal ≥ .662 (P32 K12) / .624 (P256 K11) for 50% power, even with a perfect follow [V] | NO-EFFECT forced for arm-identical swaps and at chance-level normal | n/a | UNREACHABLE (FLIP) below ≈ .62–.66. DEGENERATE (NO-EFFECT) for no-op arms. |
| swap_rel FLIP_REL / NO_EFFECT_REL / CHANCE_REL | swap_rel.py:437-468 | all three attainable iff ident (lo99 normal > .5) [V P7] | a no-op arm gives NO_EFFECT_REL whenever eligible | 24/98 W-Z NO_EFFECT_REL arms have swap scores bit-identical to normal [V] | Attainability SOUND. DEGENERATE for no-op arms; needs an arm-identity guard. |
| H2 sd_floor (H16) | swap_rel.py:378-379, 421 | the floor binds only when ≥ P−2 pairs are identical (P32 floor .0133 vs 1/2/3 pairs off by one step: .0080/.0112/.0135) [V] | n/a | n/a | units error confirmed, inert in practice (consistent with H2 = BOOTT on 439/439) |
| census S/C/N + classify | lens_swap.py:197-245, 339 | at offsets ≥ cue_len−1, site_acc + chan_acc = 1 exactly | identity holds in 1.000 of cases at o ≥ 1; broken at o < cue_len−1 (identity .55 at o=−1, .81 at o=0) [V] | change-only relay_flood: IDENTITY-BROKEN → MIXTURE → SITE across offsets [V] | the two arms are one measurement; class is a phase reading; SITE is reachable by any bit already delivered to the inbox (a SITE array) [I] |
| C1b kills / drops / intact | c1b.py:27-33, 178-195 | drops needs normal ≥ .60 + CI; NOT_APPLICABLE ⟹ intact | yes, guarded by the A1–A3 fixtures | n/a | SOUND as guarded |
| C1b T (C1 window intact lo99 ≥ .62) | c1b.py:31, PREREG s4 | normal ≥ .681 (P32 K12) for 50% power [V] | n/a | M3 normal .693/.686 sit at the edge (lo99 .655/.643) | attainable only near the edge; already marked not_eligible |
| C1b M / C / CARRYOVER | c1b.py:214-249, 471-486 | exactly .5 per pair when the predictor is twin-symmetric [V P10] | M3's r is constant (map {0:0}). M3's in-flight count AND signed sum are twin-identical at 100% of onsets [V] | n/a | UNREACHABLE for non-sign codes. M false and CARRYOVER false are forced for M3, where the twin identity is the stronger finding. |
| AUDIT3 consistency ≥ 95% | plans/T-SWAP-AUDIT3_PLAN.md | expected disagreements 11.8 (principal's plug-in) | n/a | a perfect instrument fails with P ≥ .14 (Poisson). Observed 22: P = .005. [V arithmetic] | miscalibrated (noisy). The excess over noise is real. |
| reach_certificate (draft) | H-INST/pte_trace.py:414-467 | REACHED_OUTPUT if 1 of M worlds changes the readout VALUE; ABSORBED if the readout site is touched at any tick from the earliest hook | n/a | (a) +1 nudge in one world: REACHED_OUTPUT, decision change 0/16. (b) trial-0 hook: trial 5 reads ABSORBED (touch lag −68); the trial-5 hook alone reads NOT_REACHED [V] | CHEATABLE as a null certificate. Patch in section 7. |
| lag profile (proposed) | lens.py:197-238; harvest INSTRUMENT_GAPS rank 7 | decision-level D(0) ≥ 2a−1; D(j≥1) ≤ 2(1−a) [V P8] | yes, by accuracy | any competent specimen (a → 1 forces D(j≥1) → 0) | DEGENERATE at decision level for competent specimens |
| per-sensor census (proposed) | rulers_extra.py | p_j in [0,1]. XOR: min_j p_j > .5 ⟺ positive-weight parity component [V P2] | non-read sensors give p_j = 0 unless they interfere | one-flag readouts (.56/.50) fail; P-XOR (1, 1) passes [V] | SOUND for XOR. MAJ caveat: interference [I]. |
| FLIP_FEEDBACK (proposed) | rulers_c1.py m_flip_feedback | lo99(normal − teachers removed after trial 0) > .10 | n/a | FLIP_CLOCK: diff 0, fails. P-FLIP: diff .5, passes [V] | SOUND in the tested family |

**The H-PLANT loophole generalised:** best accuracy of a readout that ignores the property the family claims to test.

| family (property) | best property-free readout | cheapest attainable form |
|---|---|---|
| RELAY (transport) | exactly .5 per pair (P1) | — |
| MAJ (integration) | any 1 or 2 sensors: .70 exactly | — |
| XOR (parity) | any parity-contradicting 2-input rule: ≤ .75 (P2) | NOR of the flags, .759 |
| FLIP (feedback tracking) | teacher-free: exactly .5 per world (P3) | teacher once + block clock: 1.0 (P3) |
| HOLD (memory) | memoryless: E = .5 (distractors are independent of y; the readout tick has no sense input) | — |

## 2. PROOFS

**P1 — forced zero_comm.**
- `evaluate` gives mirror twins the same world seed (assays.py:56; lens.py:89; c1b.py:55). So every hash stream (WAKE, RANDOP, ROUTE, LOSS, LAT, NOISE, DUP, MUT, CTRL) is identical.
- `envs.build` gives twins identical positions (lead seed). `sense_val` differs only by sign: column 0 only in XOR (envs.py:201); all columns otherwise. Targets are negated.
- Under zero_comm, `_emit` returns before any mailbox write (engine.py:534-536). So a site's state is a function of its own sense input and shared hash streams.
- In RELAY/XOR/MAJ the actuator is never a sensor: `_pick_at` returns Mrow > 0, XOR uses `setdiff`, and d ≥ 1 in C1.
- So the actuator's S0 trace is identical in the twins. For each trial, corr_b + corr_b' = 1 (one match if s0 ≠ 0; .5 + .5 if s0 = 0). The pair mean is .5 exactly for every program.
- `pair_ci` uses seed-0 indices, so the CI of (a − .5) equals the CI of a minus .5. Hence COMM_DEPENDENT ⟺ (lo99 > .55 ∧ lo99 − .5 > .03) ⟺ SIGNAL, and LOCAL_ONLY ≡ False. ∎
- FLIP: the teacher reaches the actuator, so zero_comm is not exact. But teacher k arrives after readout k (envs.py:188) and x_k is independent of everything seen before, so E = .5. ∎

**P2 — XOR parity bound.**
- Fix the history h, which is identical in the twins and independent of the current inputs. The readout is f_h(x1, x2) in {−1, 0, +1} over 4 equiprobable combos. Per-combo score is in {0, .5, 1}.
- Score > .75 needs ≥ 3 combos equal to parity and no combo contradicting it. So any f_h that contradicts parity on ≥ 1 combo scores ≤ .75.
- Of the 16 Boolean f, those scoring .75 are exactly the 4 AND/OR-type functions, with pivotality (.5, .5). Parity has (1, 1). Single-variable functions have (1, 0) and score .5. Odd f (f(−x) = −f(x)) score exactly .5 [V, `analytic.py` E].
- For every non-parity Boolean f, p1 + p2 ≤ 1. So for any mixture over h, min_j E[p_j] ≤ .5.
- Therefore min_j p_j > .5 implies a parity component with positive weight. The twins differ only in sensor j's cue inside trial k, so h is common to both and the bound is exact. ∎

**P3 — FLIP determinism.**
- envs.py:179-182: m_k = m0·(−1)^⌊k/block⌋; the first trial of each block is unscored; the number of blocks is even (envs.py:178).
- The teacher τ0 = m0·x0 reaches the actuator (envs.py:177, 188-189).
- (i) Transport of x_k, (ii) one bit of memory from τ0, and (iii) a clock of period block·Pd together give 1.0 on every scored trial with no use of τ_k for k ≥ 1.
- A readout that never uses a teacher and has fixed sign is correct on exactly half of the scored trials in every world (equal scored counts at m = ±1). A clock-only readout scores 0 or 1 per pair, E = .5. ∎

**P4 — legacy REACH_BEYOND_HOP.**
- The twin negates every column in [t0, t1) (assays.py:249); reach is measured from column 0 (258, 278).
- No-relay programs: silent divergence = the perturbed sensor sites, so reach = max_j dist(s0, s_j).
- A one-hop emitter also diverges recipients' mail (276), so reach = max_j dist(s0, s_j) + radius > radius = hop whenever two distinct sensors exist (always in XOR and MAJ).
- Global topology: `dist_matrix` is 1 off the diagonal (envs.py:90-91), so reach ≤ 1 = hop. ∎

**P5 — env_permutation cannot fail.**
- World b's trace is a function of seeds[b]. y_{b+2k} comes from an independent ENV stream (different lead seed). So E[agreement] = .5 for every program.
- The SD is about .5/√(M·K) per rotation (.018 at M64 K12), averaged over M/2 − 1 rotations. Crossing ±.10 is beyond 5 SD per rotation and far beyond for the mean. ∎

**P6 — MAJ ceilings.**
- With 5 independent sensors flipped with p = .3 and readout value ties scoring .5, the Bayes accuracy of the best rule using k sensors is .70, .70, .784, .784, .837 for k = 1..5.
- At P32 K12, lo99 > .70 has power .005 at p = .70, .92 at .784, and 1.0 at .837. ∎

**P7 — swap_rel ideal outcomes.**
- s = a gives DN = (a − .5)/2; s = 1 − a gives DF = −(a − .5)/2; s = .5 gives DF = (a − .5)/2 and DN = −DF.
- The bootstrap-t interval is equivariant under affine maps; only the H2 absolute floor breaks this, and only in the near-degenerate regime.
- So each ideal outcome yields its certificate ⟺ lo(a) > .5 (= ident). A no-op arm is NO_EFFECT_REL whenever eligible [V: synthetic, all 10 draws, plus test]. ∎

**P8 — lag profile.**
- In single-cue twins, trial k's target flips with the cue. If both twins are correct, the decisions differ, so D(0) ≥ P(both correct) ≥ 2a − 1.
- For j ≥ 1 the targets are identical. If both twins are correct, the decisions are equal, so D(j) ≤ 2(1 − a_{k+j}). ∎

**P9 — absolute swap.**
- FLIP ⟺ hi99(s) < .40. With the ideal s = 1 − a, this needs a > .60 + z·se, i.e. a ≥ .662 at P32 K12. ∎

**P10 — C1b predictors.**
- `rule_predicts` fits map(v) = sign(Σ y) over the first half of worlds, which are whole pairs (half = (M//2)//2·2 is even). A twin-symmetric r contributes y_b + y_b' = 0, so map(v) = 0, pred = 0, and the score is .5.
- `census_predicts` / `carryover`: a predictor identical in the twins gives corr_b + corr_b' = 1, i.e. .5 per pair. ∎

**P11 — transects.**
- `detect_boundaries` skips any transect with fewer than 3 level indices (campaign.py:601). ∎

**P12 — size test [I].**
- d and delta are fixed. Ring and torus neighbourhoods of the sensor and actuator are isomorphic across N ≥ the source N, and physics is local.
- So a mechanism without global traffic has the same accuracy distribution at every N, up to wrap-around effects.

**P13 — AUDIT3.**
- Disagreements between two independent draws, under a perfect instrument, are approximately Poisson(11.8): P(X ≥ 16) = .141 and P(X ≥ 22) = .005. ∎

## 3. THE ATTAINABILITY CERTIFIER (deliverable 3)

**Design (`attain.py`):**
- `Cell` (physics, env, label, optional world edit). `Program` (name, role, make, `lacks`, `only`: roles can depend on the world). `Ruler` (name, claim, `measure → {value, passed, pairs?}`).
- `certify()` returns all rows, the attainable [min, max], eligibility per role, null and adversary scores, the cheapest crossing, and `forced` (pair-exact when per-pair vectors are returned; needs ≥ 2 programs).
- Verdict precedence: forced-and-never-crossing = UNREACHABLE; forced or always-pass-including-nulls = DEGENERATE; null/adversary crosses = CHEATABLE; nothing crosses = UNREACHABLE (plants offered) or NO_PLANT; a plant crosses with no cheat = SOUND.
- `alias(a, b)` detects identical pass vectors.
- Analytic half: `ci_gate_power`, `min_true_to_cross`, `pair_sd` (twin correlation 0 or 1).
- It generalises verify_reach: verify_reach is the special case "one intervention ruler, one specimen (applied?), one plant (fired?)". The certifier adds nulls and adversaries, forced/alias detection and an eligibility count, and is aimed at the claim rather than the hook.

**Rulers shipped (`rulers_c1.py`):** SIGNAL, zero_comm, COMM_DEPENDENT, INTEGRATION(MAJ), REACH_BEYOND_HOP, REACH_BEYOND_HOP_NEAREST, env_permutation clause, XOR_PIVOT (proposed), FLIP_FEEDBACK (proposed).

**Adversary and plant library (`adversaries.py`):**
- P-XOR and P-FLIP, copied verbatim from H-PLANT.
- `xor_oneflag` (4 non-parity readouts).
- `flip_clock` (28 lines; sync period 1).
- `maj_sum` (one-hop 5-sensor majority).
- Plus `plants.null`, `sense_copy`, `relay_flood`, `hold_latch`, `echo_hold`.

**Run on C1 rulers** (`python certify_c1.py 32`, then `python reverdict.py`; 491 CPU-s):

| ruler | verdict | key numbers |
|---|---|---|
| zero_comm | DEGENERATE | pair-exact .5, 19/19 rows |
| SIGNAL (comm families) | SOUND | 2/4 plants cross, 0 cheats |
| COMM_DEPENDENT | SOUND, and alias of SIGNAL | identical pass vector on 19/19 rows |
| SIGNAL as XOR ruler | CHEATABLE | not_P .708 lo99 at 16 pairs |
| XOR_PIVOT | SOUND | |
| INTEGRATION(MAJ) | SOUND | maj_sum .771 lo99; one-live-sensor .62 fails |
| REACH_BEYOND_HOP | CHEATABLE | sense_copy 1.0 on MAJ |
| REACH_BEYOND_HOP_NEAREST | SOUND | |
| REACH_BEYOND_HOP on global | UNREACHABLE | forced 0 |
| SIGNAL as FLIP ruler | CHEATABLE | FLIP_CLOCK 1.0 |
| FLIP_FEEDBACK | SOUND | |
| env_permutation | DEGENERATE | range .474–.500, passes for all programs |

**Tests** (`tests/test_attain.py`, 9 known-answer tests, each with a must-fail input):
- forced zero_comm in RELAY but not in HOLD;
- COMM_DEPENDENT ≡ SIGNAL alias;
- legacy beyond-hop CHEATABLE vs nearest SOUND;
- global UNREACHABLE vs ring reachable;
- XOR SIGNAL CHEATABLE vs pivot SOUND;
- FLIP SIGNAL CHEATABLE vs feedback SOUND;
- analytic gate eligibility;
- swap_rel no-op forced;
- single program never "forced".

Result: 8 passed in the full run (108 s). The one failing test (my plant assumption for nearest-reach on MAJ ring24) was fixed by adding the RELAY world; the fixed test passed on rerun. Command: `CUDA_VISIBLE_DEVICES=-1 python -m pytest tests/test_attain.py -q -p no:cacheprovider`.

**Limits:**
- Verdicts are relative to the declared family. SOUND is not a proof; CHEATABLE, DEGENERATE and UNREACHABLE rows are constructive.
- Forced detection is exact equality, so stochastic near-forcing (the env_perm style) is caught by always-pass-including-nulls instead.
- The FLIP_CLOCK adversary uses prog_len 28. Inside C1's genome space (≤ 16 lines), attainability of the clock cheat is NOT shown.

## 4. RECORDED C1/C1b VERDICTS IF DEGENERATE RULERS ARE DISCOUNTED (deliverable 4)

- **COMM_DEPENDENT.** All-wave held rows: RELAY 55 and MAJ 19 are identical to SIGNAL.
  - A1 "8/352 COMM_DEPENDENT" is 7 comm-family SIGNALs (RELAY 4, MAJ 3) plus 1 genuine HOLD.
  - P4 (≤ 5% of A1 COMM_DEPENDENT) still holds as a SIGNAL-rate statement.
  - The headline "communication-dependent machinery" must rest on packet ablation and C1b's corrected window, not zero_comm.
  - LOCAL_ONLY = 0 in RELAY/XOR/MAJ is structural, not measured.
- **CAUSAL_SUPPORT.** RELAY 4/4 and MAJ 9e72f9b6, 544f3d24 stand, but each rests on ONE live clause (packet_ablation). The C1b corrected window confirmed RELAY at .50 4/4. MAJ 023539c4 and feadc823 (NOT_SUPPORTED) are the lag-0 window defect (E1).
- **REACH_BEYOND_HOP.**
  - MAJ (114/162) and XOR (48/83): void. This includes the d ≤ hop rows (XOR 17/30, MAJ 75/82), which the silent-program reading in E-H1 does not explain; one-hop emission does (P4).
  - Global (0/213): structural.
  - RELAY, FLIP and HOLD stand.
- **INTEGRATION.** MAJ M4 (lo99 .742): the ruler is sound; the cell is unreproduced (known). XOR: 0 rows, so no change. Any future XOR claim needs XOR_PIVOT.
- **Plant viability.**
  - XOR, MAJ and FLIP NULLs never had plant eligibility (0/1000 A0 cells each), so "living" for those families was sensitivity-only.
  - C1_REPORT's "seeding half of A1 in living A0 cells gave no advantage (MAJ 2 vs 1)" compares a sensitivity-only criterion in MAJ.
  - s7's "nothing could have fired" qualifier could not be supplied for those families.
- **Phase boundaries.** No candidate could exist on XOR setrule/dup, FLIP update_period or HOLD update_mode (8 transects). "No boundary" there is structural.
- **Size-free (wave E).** All 15 rows are a HOLD latch (actuator = sensor) or bbef66a1 (ring r3, d3 = one hop). The pass is forced, so the wording should be "local laws are N-invariant". bbef66a1 is also unreproduced (E-H5).
- **TRANSFER_SUPPORT.** P5 (0 cross-family) holds. The RELAY→MAJ direction would have been a cheap pass.
- **env_permutation.** Discounting it changes no verdict.
- **C1b.**
  - Labels unchanged.
  - M3 "M false" and "CARRYOVER false" are forced by twin symmetry. The stronger reading is that M3's in-flight count and signed sum are twin-identical at every onset (100%), i.e. no aggregate cue carryover despite about 1516 packets in flight.
  - M3's T clause sits at the eligibility edge (already not_eligible).
  - M2's Z is already _UNRESOLVED.
- **Swap readings.**
  - 24 of 98 W-Z NO_EFFECT_REL arms (mostly channel_all on HOLD latches and some RELAY cells) are score-identical to normal. They should read TRIVIAL_NO_EFFECT, not evidence.
  - Absolute-rule FLIP was unattainable for every specimen with normal below about .62–.66, so W-O's "84% stay CHANCE" was partly forced (already corrected by W-Z: 48/314 FLIP_REL).

## 5. FINDINGS

**F1 [V]. FLIP SIGNAL is passed with no use of feedback after trial 0.** Confidence high.
- Check: `python check_flip.py 64` (ring24 r1, dest all, lossless, prog_len 28; FLIP d3 delta8, block 4 and block 2; M64).
- Results:

| arm | FLIP_CLOCK | P-FLIP |
|---|---|---|
| normal | 1.000 [1,1] | 1.000 [1,1] |
| teachers after trial 0 removed | 1.000 [1,1] | .500 [.5,.5] |
| all teachers removed | .500 | .500 |

  Block 2 gives the same pattern.
- Objection: prog_len 28 and update_period 1 are outside C1's genome space and d9cc. Unresolved: a ≤ 16-line clock cheat.
- No C1 FLIP SIGNAL exists, so no recorded verdict changes. Any future FLIP claim needs FLIP_FEEDBACK or randomised switch times.

**F2 [V]. The XOR "one-flag" result is the general non-parity ceiling of .75, and per-sensor pivotality separates the two.** Confidence high.
- Proof P2. Check: `python check_xor.py 128` (X0, M128).

| readout | acc [99% CI] | pivotality (p1, p2) |
|---|---|---|
| P-XOR | 1.000 | (1.0, 1.0) |
| not_P (NOR of flags) | .759 [.730, .785] | (.56, .50) |
| P | .241 | — |
| not_Q, P_and_notQ_neg | .259 each | — |

- Objection: pivotality was measured on 32 worlds × 3 trials. Unresolved: pivotality at the C1-sampled XOR points.

**F3 [V]. zero_comm is forced; COMM_DEPENDENT is an alias of SIGNAL; LOCAL_ONLY is unreachable in RELAY/XOR/MAJ.** Confidence high.
- Check: `python rows_audit.py` and `out/certify_c1.json`.
- This extends Wave-1 E-H2b with the exact CI identity and LOCAL_ONLY.

**F4 [V]. CAUSAL_SUPPORT in comm families equals the packet_ablation clause alone (8/8 D comm rows).** Confidence high.
- Objection: n = 8. But the proofs (P1 forced zero_comm, P5 forced env_perm) cover all rows.

**F5 [V]. env_permutation clause: certifier DEGENERATE (passes for all 16 rows incl. nulls).** Confidence high.
- H-SCI already called it UNFALS. Here it is certified, with the proof P5.

**F6 [V]. Legacy REACH_BEYOND_HOP is fired by one-hop emitters on XOR/MAJ even when d ≤ hop; silent programs fire it only when sensor spacing > hop.** Confidence high.
- Check: `python check_beyond_hop.py`. one_hop_emitter on X0 r3: XOR d3 1.0, XOR d2 1.0, MAJ d2 1.0, RELAY d3 0. Silent: XOR d3/d2 0, MAJ 1.0.

**F7 [V]. 8/104 C1 transects have 2 levels and can never yield a boundary candidate; code requires ≥ 3 levels, PREREG s8 asks ≥ 3 replicates per level.** Confidence high.
- Objection: maybe the 3-level rule is a deliberate smooth-amplifier requirement. If so, it is unstated in PREREG.

**F8 [V]. The relay_flood plant never crosses .75 in XOR, MAJ or FLIP (0/1000 A0 each).** Confidence high.
- relay_flood partly uses the FLIP teacher: .581 [.513, .643] on the lossless ring, falling to .500 with teachers removed.
- maj_sum shows MAJ itself is attainable at X0 (lo99 .771).

**F9 [V]. Absolute swap FLIP needs normal ≥ .662 (P32) / .624 (P256) under a perfect follow.** Confidence high.
- swap_rel's three certificates are attainable iff ident; no-op arms force NO_EFFECT_REL; 24/98 W-Z NO_EFFECT_REL arms are score-identical.
- Check: `python analytic.py`. Objection: score identity is not state identity, but the certificate is forced either way.

**F10 [V]. H16: the floor binds only when ≥ P−2 pairs are identical.** Confidence high. Inert, consistent with H2 = BOOTT on 439/439.

**F11 [V]. reach_certificate draft: window aliasing and any/value aggregation.** Confidence high.
- Check: `python check_reachcert.py`.
- Trial-0 hook: ABSORBED (lag −68). Trial-5 hook alone: NOT_REACHED. One-world +1 nudge: REACHED_OUTPUT with output 1/16 and decision 0.
- Patch and regression tests in section 7.

**F12 [V]. C1b M / CARRYOVER are exactly .5 for twin-symmetric predictors; M3's in-flight count and sum are twin-identical at 100% of onsets.** Confidence high.
- Check: `python check_carryover.py`.
- For M2 4ab2ba01, count is identical but sum differs in 87% of pairs (sign predicts the previous target at .524 [.464, .582]).

**F13 [V, proof]. The decision-level lag profile is bounded by accuracy (P8).** Confidence high.
- Objection: a value- or margin-level profile escapes the bound but measures difference, not use.

**F14 [V]. Census identity is broken by construction at offsets below cue_len−1; a change-only relay reads IDENTITY-BROKEN → MIXTURE → SITE across offsets.** Confidence medium-high.
- Check: `python check_census_identity.py`. Identity .55 at o=−1, .81 at o=0, 1.0 at o ≥ 1; MIXTURE at o = 1–4 (fS .44 / fC .56); SITE at o = 7.
- Reading: MIXTURE is reached by the previous trial's state reuse. It is a correct per-trial mixture, not a pathology.

**F15 [V arithmetic]. AUDIT3's 95% bar fails a perfect instrument with P ≥ .14.** Confidence medium. It rests on the principal's plug-in of 11.8, which understates disagreement.

**F16 [I]. The size-free test is forced for the tested laws; cross-family TRANSFER is cheap in the RELAY→MAJ direction.** Confidence medium. Neither was run.

## 6. (merged into section 1)

## 7. PROPOSED FIXES

**(a) NEUTRAL: reach_certificate (harvest draft; not frozen).**
- Diff: `patch/reach_certificate_window_decision.diff`.
- Changes:
  - touches are counted only inside the trial's own window [cue onset, readout];
  - new keys: `decision` (scored sign change), `absorbed` (fraction of admissible-null worlds), `per_world` verdicts.
- Regression tests: `tests/test_reachcert_patch.py`. Against the current module (`W2B_PTE=orig`): 2 failed. Against the patched module: 2 passed.
- The H-INST suite (23 tests) passes against the patched module, imported first.

**(b) NEUTRAL (new instruments, no frozen semantics):** `attain.py` plus the XOR_PIVOT and FLIP_FEEDBACK rulers, with `tests/test_attain.py`. These are proposed for plan-first promotion.

**(c) SEMANTIC (future preregs only; do not touch C1/C1b):**
- (i) Retire zero_comm and env_permutation as evidence in comm families. Replace them with the corrected-window packet ablation and an actuator-isolation control.
- (ii) Use REACH_BEYOND_HOP_NEAREST.
- (iii) XOR claims require min_j pivotality > .6.
- (iv) FLIP needs randomised switch times or the FLIP_FEEDBACK must-drop control.
- (v) The boundary gate should state its level/replicate rule; allow 2-level dials with an explicit test.
- (vi) An arm-identity guard for swap_rel (score-identical arms read TRIVIAL).
- (vii) Run the certifier on every gate before freeze, with eligibility counts.
- (viii) The AUDIT3-style consistency bar should come from the expected-agreement distribution.

## 8. DISAGREEMENTS

**D1. H-PLANT and its principal review.** The "one-flag" readout is NOT single-sensor: it is NOR over both sensors' + flags.
- .763 is the general .75 ceiling of every parity-contradicting rule (P2), and "+ iff P" is .25 in expectation.
- XOR SIGNAL remains sound evidence that both inputs arrived. Only the parity reading is cheatable.

**D2. C1_ERRATA E-H1 / H-IMPL H1.** "A program that never emits scores beyond_hop 1.00 ... XOR reach 3" does not hold when d ≤ hop: silent XOR at X0 d3 r3 scores 0.
- The general and stronger cause is one-hop emission from the second sensor, which also explains the d ≤ hop rows.

**D3. PREREG s11 / H-SCI ("relay_flood cannot solve FLIP by design"; "XOR/FLIP have no plant").**
- relay_flood reaches .58 (ring) and up to .734 (A0) on FLIP through teacher memory.
- MAJ also never passes the plant gate (0/1000), although a MAJ plant exists (maj_sum).

**D4. PTE_INSTRUMENT_GAPS rank 7.** The lag profile as a decision-level rate cannot separate integrator from store for competent specimens (P8).

**D5. INSTRUMENT_GAPS rank 2 / H-INST ("only ABSORBED is an admissible null").** As implemented, ABSORBED is reachable from earlier trials and from a single world (F11). It needs the window plus a per-world admissible fraction.

**D6. PREREG_PTE_C1 s2 ("XOR single-input = 0.500 exactly").** This holds per pair only for x2-only readouts. x1-only readouts are .5 in expectation, not per pair.

**D7. Principal AUDIT3 note.** Agree it is a plan defect. Quantified: P(fail | perfect instrument) ≥ .14.

## 9. NEXT QUESTIONS (ranked)

1. Score P-XOR vs not_P with XOR_PIVOT at the C1-sampled XOR points aa2b8d68 and 4eeca9f1. Does pivotality separate them at real loss and latency? (Minutes of CPU.)
2. Does H-PLANT's P-FLIP at d9cc pass FLIP_FEEDBACK (it should drop to .5)? Can a ≤ 16-line clock cheat exist at d9cc (update_period 2)? If yes, C1-space FLIP SIGNAL is cheatable outright.
3. Run the certifier over a stratified sample of C1 census physics for each C2 gate, to get per-gate eligibility counts before any C2 freeze.
4. Fix the batch aggregation rule for the patched reach_certificate (minimum admissible fraction), with known-answer plants.
5. Per-sensor census on MAJ with a rectified single-sensor reader under cap/aloha: can collisions make non-read sensors pivotal (a CHEATABLE integration reading)?
6. A use-weighted lag statistic (margin change at readout, conditioned on an unchanged decision), with integrator vs lag-k store plants as known answers.
7. Re-label the 24 score-identical W-Z NO_EFFECT_REL arms as TRIVIAL in the swap record. Do any carrier claims rest on them?
8. Do any C1 RELAY CAUSAL_SUPPORT cells depend on lag-0 arrivals elsewhere (corrected-window recheck beyond D-wave)?

## 10. INFERENCE LEDGER

Format: question | evidence | result | confidence | strongest objection | unresolved | next

- zero_comm forced? | P1; rows_audit (213/95/174 exact; CI identity < 1e-9); certifier pair-exact | DEGENERATE; COMM_DEP ≡ SIGNAL; LOCAL_ONLY unreachable | high | none (proof) | FLIP only E = .5 | retire as evidence
- CAUSAL_SUPPORT live clauses? | D rows 8/8; P1, P5 | equals packet_ablation | high | n = 8 | — | corrected-window recheck beyond D
- env_perm can fail? | P5; certifier 16/16 pass; C1 range | no | high | — | — | retire
- REACH_BEYOND_HOP? | P4; check_beyond_hop; rows by d vs hop | CHEATABLE XOR/MAJ (one-hop emitter); UNREACHABLE global | high | nearest variant untested on lossy physics | — | adopt nearest
- XOR one-flag generalised? | P2; check_xor; analytic E | ≤ .75 ceiling; pivotality separates | high | small pivot sample | C1-sampled points | Q1
- FLIP cheat? | P3; check_flip; certifier | clock 1.0 ignoring teachers | high | prog_len 28 | ≤ 16-line attainability | Q2
- MAJ INTEGRATION? | P6; certifier (maj_sum .771, 1-sensor .62) | SOUND, FP .005 | high | transport-limited false negatives | interference | Q5
- plant gate reachability? | rows (0/1000 XOR/MAJ/FLIP); check_flip relay_flood | UNREACHABLE in census; relay_flood uses the FLIP teacher | high | plant max over 16 pairs is noisy | — | per-family plants
- transect 2-level? | P11; rows (8/104) | UNREACHABLE | high | intent unknown | — | prereg wording
- size-free test? | P12; wave-E rows | forced for tested laws | medium | wrap-around at N 400 | — | none
- absolute swap / swap_rel attainability? | P7, P9; analytic C; W-Z arrays (24/98) | FLIP needs normal ≥ .62–.66; swap_rel = ident; no-op forced | high | score identity ≠ state identity | carrier claims on the 24 | Q7
- H16 floor? | lattice SDs vs floor | binds only at ≥ P−2 identical pairs | high | — | — | none
- C1b predictors / carryover? | P10; check_carryover | forced .5 for twin-symmetric; M3 aggregates twin-identical | high | aggregates hide site-level differences | site-level carryover | none urgent
- census identity / classes? | check_census_identity | identity forced only at o ≥ cue_len−1; MIXTURE from change-only relays | medium-high | one plant, one physics | — | phase keys (B3)
- AUDIT3 bar? | P13 | miscalibrated (P fail ≥ .14) | medium | plug-in estimate | — | expected-agreement bar
- reach_certificate? | check_reachcert; patch tests 2F/2P; H-INST 23/23 | window + aggregation gaps fixed | high | thresholds for batch nulls | aggregation rule | Q4
- lag profile? | P8 | decision-level bounded by accuracy | high | margin-level escapes | use-weighted version | Q6

## 11. COMPUTE

CPU only, 2 threads per process. About 1,520 CPU-s in total (≈ 0.42 core-h, under the 0.5 cap). No GPU touch: every engine process had `CUDA_VISIBLE_DEVICES=-1`, `device="cpu"` and the `torch.cuda.is_available()` assertion.

| run | CPU-s |
|---|---|
| check_flip | 78 |
| check_xor | 107 |
| certify_c1, first run (crashed at the last job, about 400 s, rerun) | ~400 |
| certify_c1, second run | 491 |
| test_attain | ~150 |
| H-INST suite ×2 (orig and patched) | ~140 |
| check_carryover | 22 |
| check_beyond_hop | 24 |
| check_census_identity | 10 |
| check_reachcert | 4 |
| test_reachcert_patch ×2 | ~16 |
| analytic, rows audits, reverdict | ~40 |

No leases were acquired or released; the principal holds skullport:cpu8.
