<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/H-IMPL; sha256(report)=adad4c0133c85e20; delimited; see REPORT.provenance.json -->
# H-IMPL: independent implementation audit of PTE (prometheus/ananke)

Worker H-IMPL, 2026-09-30. Worktree F:/Prometheus-worktrees/ananke-base-role at 4a97f97fa.

This was an inference task: I read the code first, then ran bounded CPU reproductions. I applied no patch to any repo file. Everything I wrote is under roles/Ananke/research/harvest/H-IMPL/: patches/, tests/, scratch/.

REPORT.md itself could not be written, because the Write tool refuses report files for subagents. This text is its intended content.

**Compute disclosure.**
- My first action was to run the existing suite (227 tests) with CUDA_VISIBLE_DEVICES set to empty.
- On this host an empty value does NOT hide the GPU: torch.cuda.is_available() stays True. Setting it to "-1" gives False.
- That run (403 s wall, 227 passed) therefore executed the CUDA-eligible tests on the GPU: conformance, graph replay and checkpoint.
- Every later process used CUDA_VISIBLE_DEVICES=-1 and/or device="cpu", with at most 2 threads.
- Total CPU use was about 0.35 core-hours. No background processes are left.

## SCOPE READ

| File | Lines | How read |
|---|---|---|
| engine.py | 572 | all |
| oracle.py | 511 | all |
| physics.py | 148 | all |
| topology.py | 73 | all |
| rng.py | 62 | all |
| envs.py | 238 | all |
| assays.py | 303 | all |
| search.py | 149 | all |
| campaign.py | 882 | all |
| launch.py | 102 | all |
| report.py | 344 | all |
| analysis_a0.py | 205 | all |
| c1b.py | 596 | all |
| c1b_run.py | 358 | all |
| lens.py | 297 | all |
| lens_swap.py | 486 | all |
| swap_rel.py | 201 | all |
| plants.py | 300 | all |
| tests/test_conformance.py | 193 | all |
| other tests | | only the handoff and REPO-path parts |

Specs and plans read:
- DESIGN.md
- PREREG_PTE_C1.md
- PREREG_PTE_C1b.md (s2-s3 and grep hits)
- C1_REPORT.md and C1_ERRATA.md
- c1b/CORRECTIONS_2026-09-27.md
- CORRECTIONS_2026-09-29_SWAP_AUDIT.md
- INSTRUMENT_CARRIER_SWAP.md
- T-SWAP-REL4_PLAN.md (s2-s3)
- W-Q swap_rel2.simulate

Data read (read-only):
- c1_rows/cells.jsonl.gz (6596 rows)
- boundaries_B.json and boundaries_verdicts.json
- ~/ananke_runs/pte-c1 log.txt and watchdog.log
- W-M out/census_*.json

I did not read prometheus/cosmos/c3_holdout_D*.

## FINDINGS

These are the new findings only. Defects already on record are listed under "Previously known defects" in the section on things checked.

| id | file:line | class | severity | failing scenario | evidence / repro | neutral fix? | affected claims |
|---|---|---|---|---|---|---|---|
| H1 | assays.py:248-267 | Multi-sensor twin measured from sensor 0 only | MAJOR | On XOR and MAJ, twin_assay negates EVERY sensor column but measures reach from sensor 0 only. Other sensors' local divergence counts as distal transport. | A program that never emits (S0:=SENSE): MAJ reach 6.0, beyond_hop 1.00; XOR reach 3.0, beyond_hop 1.00; RELAY and HOLD 0. In C1 rows REACH_BEYOND_HOP fires on MAJ 114/162 (59 of them with comm_delta<.02) and XOR 48/83 (46 with comm_delta<.02). | Yes, additive only (patch twin_reach_nearest_sensor). Legacy keys stay bit-identical. | Stored C1 REACH_BEYOND_HOP labels. D-wave MAJ twin lines (0a23398f, f6b623cd, 4781b0a1 all beyond_hop 1.0). Twin fields in W-J e2/e6 MAJ and W-L outputs. No C1_REPORT headline uses them. |
| H2 | assays.py:280; campaign.py:439 | Ruler cannot cross its gate | MINOR | On global topology hop=1 and every env distance is at most 1, so beyond_hop is always 0. | 213 C1 global evolve rows: REACH_BEYOND_HOP is 0 in all of them; max reach 1.0. | Report only (frozen C1 label) | "No distal reach" on global is structural, not a measurement. |
| H3 | engine.py:288, 434-435, 445, 457-458 | Silent overwrite past the schedule | MINOR (latent) | Running a World past Tsch rewrites trace, emit_trace and census row Tsch-1 on every extra tick. | With the cue on the last tick: trace[T-1] is [300,300] after T ticks and [0,0] after T+2 ticks. | Yes (patch engine_trace_past_schedule). No frozen caller runs past Tsch. | None found. It is a hazard for lens and worker scripts. |
| H4 | campaign.py:860, 722-732 | Resume is not deterministic | MINOR (latent) | On a resume inside wave D, D's own replicate evolve rows enter promoted(). That shifts pi, the cell ids and the seeds. | Reproduced; a regression test shows the cell-id sets differ. C1 ran as a single attempt (watchdog.log), so it was not affected. | Yes (patch wave_d_resume_determinism) | None for C1 |
| H5 | campaign.py:860 vs 862 | Two pools for "promoted" | MINOR | Wave D promotes from A, B, B2 and C evolve rows. Wave E uses `r["wave"] in "ABC"`, a substring test that drops B2. | In C1, 3 of the 12 D cells came from B2. E's top 5 includes 0c18ce5e (HOLD), which was never adjudicated. Only ONE RELAY law, bbef66a1, was scaled. | Report only | C1_REPORT s1 says "frozen RELAY laws ... SIZE-FREE", but that rests on one law. PREREG s5 says "top 5 promoted". |
| H6 | campaign.py:631 | Seed reuse across namespaces | MINOR | The B2 search seed H(seed, 0xB2, hash(dial), base, level, rep) has no family or track key. | The 270 B2 rows use only 159 seeds. 69 seeds are shared across families; for example the RELAY, FLIP and HOLD phys decay_shift transects use identical random genomes and world seeds. | Report only | Agreement of B2 reproductions across families (for example the decay boundaries) is not independent. Freshness within a family is fine. |
| H7 | campaign.py:83-90, 494-498; analysis_a0.py:86 | Condition and record aliasing; inert dials | MINOR | (a) Global cells force dest_mode=sample, but `levels` keeps the drawn "all". (b) Some B transects vary a dial that has no effect at their base cell. | (a) 951 of 1589 global rows are recorded as dest_mode=all, and dial_effects and analysis_a0 count them that way. (b) 3 of 78 B transects (27 cells) are pure seed noise: RELAY evo fanout under dest_mode all; MAJ evo collision at cap 0; FLIP phys update_period under async. None of them produced a candidate. | Report only | The dest_mode dial-effect tables in A0 and A1, and the analysis_a0 features. |
| H8 | campaign.py:470 | Wrong dial for the time scale | MINOR | MEMORY_WITHOUT_USE compares against 3*delta for HOLD, but HOLD's time scale is gap and HOLD never reads delta. | In C1 the HOLD flag count is 8 either way. | Report only | None |
| H9 | campaign.py:313 | Mislabelled arm | MINOR | The "size_x2.25" transplant goes 100 -> 144, i.e. x1.44, when n_sites=100. | Affects C1 D cells 0a23398f, f6b623cd and 613162a3 (all MAJ). | Report only | The D transplant table for those 3 cells |
| H10 | report.py:153 | Statistic does not match the claim | MINOR | transplant_transfer uses point accuracy >.55 on 32 worlds. PREREG s9 requires the recipient to reach SIGNAL (lo99 >.55), and transplant_battery keeps no confidence interval. | By inspection | Report only | C1_REPORT M1 "Survives +0.2 loss, +1 latency ..." is a point-accuracy statement, not a SIGNAL statement. |
| H11 | assays.py:217; campaign.py:341, 345 | Mirror-pairing inconsistency | MINOR | The env_permutation null and flip_state_transplant build their World from the raw `seeds`, not the pair-shared seeds[m - m%2] that evaluate() uses. | The null scores traces from a different run than the "normal" it is compared with, and partners in that run are not physics twins. Constant-policy cancellation still holds, because the rotation is by pairs. | Report only | Small effect on C1 ok_perm |
| H12 | assays.py:210; c1b.py:170 | No-op guard blind to physics arms; lat_base aliasing | MINOR (latent) | The digests include the mailbox, whose size depends on LM. A physics arm that changes LM without changing the dynamics can therefore never come out NOT_APPLICABLE. Also, lat_base 0 behaves exactly like lat_base 1 when lat_hop*dist + jitter is 0, because the delay clamps to 1. | ring/all, lat_base 1 -> 0: traces and stats identical, LM 3 -> 2, digests differ. The C1b M3 specimens have lat_base 4, and C1's only physics arm (max_loss) keeps LM. | Report only (C1b is frozen) | None found |
| H13 | lens_swap.py:465-486 | Vacuous gate | MINOR | In the KA7 handoff rule, clause (b) passes vacuously when the final 4 offsets were never scanned, and the final SITE run is not anchored at ro_off-1. | {3: CHANNEL, 5: SITE} with ro_off=10 gives pass=True. All 18 recorded W-M scans covered offsets -1..ro_off-1. | Yes (patch handoff_coverage); identical on all 18 recorded scans | None; recorded results unchanged |
| H14 | lens_swap.py:232-238 | Mixed eligibility denominators | NOTE | phi is computed on world-cells where only that world was normal-correct, and tr_ok comes from the full sample even inside bootstrap resamples. fS, fC and fN use pairs where both worlds were correct. The MIXTURE rule mixes the two. | By inspection | Report only (frozen plan rule) | MIXTURE calls |
| H15 | envs.py:164 | Identity precondition fails by construction | NOTE | HOLD distractors are mirror-NEGATED, so after a mid-gap swap the two chimeras receive different inputs. The instrument doc (F5') says identity is forced "whenever no input arrives", and on HOLD inputs always arrive. | Accumulator plant (S0 += SENSE) on HOLD: sign identity .93, which passes the .90 gate; raw identity_s0 .36. | Report only | Carrier readings on HOLD specimens (M2) |
| H16 | swap_rel.py:78-79, 120-121, 200; W-Q swap_rel2.py:76-86 | Units and model mismatch | NOTE | (a) sd_floor = sqrt(1/4K)/sqrt(P)*.5 is on the standard-error scale, but it floors sd*_b, which is a per-pair standard deviation. The floor is therefore about 1/(2 sqrt P) of the plan's "binomial-scale floor for a pair statistic". (b) swap_verdict_rel4 passes K as scored trials per WORLD. The FC simulator draws a pair statistic as Binomial(K)/K, i.e. K independent trials per PAIR. Real pair means average 2K correlated mirror-world trials. (c) TABLE needs an exact P and K. | By inspection. Consistent with W-X's caveat that H2 coincides with REL3 almost everywhere. | Report only (frozen plan) | The REL4 FC table certifies the simulated model, not the mirror-pair design. |
| H17 | c1b.py:198-211 | Denominator mismatch | NOTE | _perm_p takes the observed value over scored trials but the permuted means over ALL trials. | It is never called on a run that has unscored trials | Report only | None |
| H18 | engine.py:70-75 | Crash and hidden condition | NOTE | Controls.label() raises ValueError when a reset_state_mask is set, and hides distractor_chan=0 (because 0 == False). | Reproduced; regression test written. The function has no callers. | Yes (patch controls_label_mask) | None |
| H19 | engine.py:96; assays.py:49, 197, 234; search.py:385; campaign.py:237, 822; c1b_run.py:278; lens.py:85 | Hidden defaults | NOTE | device="cuda" is the default almost everywhere, but lens.carrier_table and its neighbours default to "cpu". run() defaults to graph=True. The tests pick cuda whenever it is available. CUDA_VISIBLE_DEVICES="" does not hide the GPU on this host. | Measured; see the compute disclosure | Report only | Operational safety, not results |
| H20 | DESIGN s7 vs envs.py:73-221 | Spec drift without annotation | NOTE | Targets are i.i.d. with mirror pairs, not "exactly balanced". The XOR actuator is at distance >= d//2, not >= d, and sensor 2 sits at exactly d. MAJ sensors sit at distance d from the actuator. Env distance is geometric on lattices (d=3 on a radius-3 ring is one hop) but BFS hops on graphs. | By inspection. DESIGN's header requires a dated annotation for any such difference. | Report only | "d" does not mean the same thing across topologies |
| H21 | physics.py:104-106 | Wrong guard comment | NOTE | The int32 mailbox bound ignores accumulation over up to LM-1 emission ticks into one slot. | Not reachable: in-degree is bounded by the neighbour table or spread uniformly by the hash. The oracle uses unbounded ints. | Report only | None |
| H22 | engine.py:497-505, 531-534 | RNG sub-index collision | NOTE | The distractor draw H(ws,CTRL,t,n,100+p) equals the emission CTRL base H(ws,CTRL,t,n,f) whenever fanout > 100. validate() allows fanout up to 4095. | Unreachable in the campaigns (fanout <= 8) | Report only | None |
| H23 | lens_swap.py:131-143 | Unguarded trial boundary | NOTE | A SINGLE arm with offset >= ro_off (or >= the period) swaps after the scored readout, so NO-EFFECT holds by construction. Offsets below -1 reach into trial k-1. | The recorded scans used offsets -1..ro_off-1 | Report only | None |
| H24 | analysis_a0.py:22, 149-159 | Declared null does not match the code | NOTE | The docstring says "family labels permuted within topology". The code permutes the rung label within topology, inside a single family. | By inspection | Report only | Wording of the A0 null |
| H25 | campaign.py:743, 709 | Dead code; stale comment | NOTE | `nn = n if ... else n` has two identical branches. The comment says "at most 3 per family", but the code allows 4, which matches the PREREG. | By inspection | Report only | None |
| H26 | campaign.py:839-845 | Receipt gap | NOTE | Under --allow-dirty, the receipt still records a code_sha that does not describe the running code, and there is no dirty flag. | C1 was launched without the flag (watchdog.cmd) | Report only | None |

## Per-finding detail

**H1.** How the twin is built:
- `sv_tw[t0:t1] = -sv_tw[t0:t1]` negates every column of the schedule: 2 sensors for XOR, 5 for MAJ.
- `src = sidx[:, 0]` and `dsrc = Dm[src]` take distances from sensor 0 only.
- reach is the maximum of those distances over diverged sites.

Why that inflates reach:
- On MAJ, sensors 1-4 sit at distance d from the actuator, so they can be up to 2d from sensor 0. Any program that simply stores SENSE gets reach up to 2d and beyond_hop=1.
- On XOR, sensor 2 sits at distance d from sensor 1, so the same program gets reach d.
- For XOR the twin also leaves the target unchanged, since (-x1)(-x2) = x1 x2. readout_flipped therefore means the opposite of what it means in the other families.

Reproduction (scratch/repro_twin_reach.py, CPU), all with emit_rate 0, accuracy .5 and zero_comm .5:
- RELAY: reach 0, beyond_hop 0.
- MAJ: reach 6, beyond_hop 1.00.
- XOR: reach 3, beyond_hop 1.00.

The patch adds reach_nearest and beyond_hop_nearest. These measure distance to the nearest sensor column that actually had a non-zero cue in the window, so FLIP's silent teacher column is excluded. The regression tests show:
- the silent program gets reach_nearest 0 on MAJ and XOR;
- on RELAY and FLIP, the nearest-sensor values equal the legacy ones.

**H3.** The row index is `tv = t.clamp(max=Tsch-1)`, and index_copy_ writes on every tick. The patch writes the old row back when t >= Tsch, using torch.where on t_dev so the tick stays CUDA-graph safe. Within the schedule the output is bit-identical.

**H4 and H5.**
- H4: at the start of wave D, `prior` holds every stored row. On a resume, D's replicate evolve rows re-enter promoted(), and they can have lo99 above the promoted cells. The patch filters out wave "D" rows inside wave_D. It is neutral for C1, which ran D once with no D rows present.
- H5 is a separate mismatch. `r["wave"] in "ABC"` is a substring test, so "B2" rows are excluded from E but included in D.

**H6.** In the C1 data, seed 2176773745 is used by RELAY, FLIP and HOLD phys/decay_shift census cells. B's seed includes hash(track+dial+fam); B2's does not.

**H7.** physics_from_levels changes the physics kwargs but not the recorded levels. The inert-dial rules I applied:

| Dial | Has no effect when |
|---|---|
| radius | topology is not ring or torus |
| k_random | topology is not random |
| rewire | topology is not smallworld |
| dest_mode | topology is global |
| fanout | dest_mode is all |
| update_p | update mode is sync |
| update_period | update mode is async |
| plastic_route, adapt_shift | dest_mode is all, or topology is global (w is never read) |
| collision | cap is 0 |
| setrule | rules is 1 |
| loss_per_hop | loss is 0, or max_dist is 1 |
| gap | family is not HOLD |
| delta | family is HOLD |
| block | family is not FLIP |
| d | family is HOLD, or topology is global |

A further alias: on random, smallworld and global topologies, (lat_base 1, lat_hop 1) behaves exactly like (lat_base 2, lat_hop 0), including an equal LM.

**H12.** Reproduction (scratch/repro_misc.py, check 3): relay_flood on ring/all with lat_base 1 vs 0.
- Per-world accuracy, traces and stats are all identical.
- LM goes from 3 to 2, so the digests are unequal and the guard can never fire.

**H13.** The patch:
- excludes offsets >= ro_off;
- makes clause (b) require every offset in [ro_off-4, ro_off-1] to be both measured and SITE;
- sets run_start to None unless the last measured offset is ro_off-1.

The existing KA7 tests (E2 passes, E1 fails clause b, the latch fails clause a) all still pass with the patched handoff. A verbatim copy of the legacy rule gives identical results to the patched rule on all 18 recorded W-M scans.

**H15.** scratch/repro_hold_identity.py: HOLD, 32 pairs, trials 2-9, SINGLE site and channel arms at offset 5. Result: eligible 160, identity .931, identity_s0 .356, class SITE. The class is right for this accumulator, but the doc's stated precondition does not hold on HOLD.

**H16.** The code applies the floor to a per-pair standard deviation and then divides by sqrt(P) again:

```
sd_floor(P,K) = sqrt(1/(4K)) / sqrt(P) * 0.5
bsd = max(bsd, sd_floor)
t = d / (bsd / sqrt(P))
```

For P=32 and K=11 the floor is .013. The per-pair SD of a Bernoulli(.5) pair statistic is about .1.

## PATCHES

All in patches/*.diff. `git apply --check` succeeds on 4a97f97fa. None is applied.

1. engine_trace_past_schedule.diff (H3)
2. controls_label_mask.diff (H18)
3. wave_d_resume_determinism.diff (H4)
4. handoff_coverage.diff (H13)
5. twin_reach_nearest_sensor.diff (H1; adds keys only)

**Regression tests** (tests/test_*.py, 15 tests, run with CUDA_VISIBLE_DEVICES=-1):
- On the current code: 11 failed, 4 passed. The 4 that pass are the neutrality checks, which must pass on both.
- On the patched package copy (scratch/patched): 15 passed.

**Existing suite against the patched package, on CPU:**
- test_conformance, test_oracle_selfcheck, test_campaign_logic, test_envs_assays: 132 passed, 13 skipped (the skips are the CUDA-graph tests).
- test_lens_swap, test_lens_instruments, test_swap_rel, test_c1b, test_c1b_switches: all passed.
- test_c1b_run: 13 failures under the patched copy. They come only from REPO being computed from the copied module's location. c1b_run is untouched, and the same file passes 17/17 on the original code.
- The 2 KA7 handoff tests pass with the patched handoff (scratch/run_handoff_patched.py).

## THINGS CHECKED AND FOUND CORRECT

**Hashing and RNG.**
- rng.hash32 in torch int64 matches the host implementation bit for bit. The x*C2 product wraps, but the masked low 32 bits are exact.
- Stream ids match DESIGN.
- The random and smallworld topology draws agree between topology.py and oracle.py.

**Tick order and arithmetic.** Checked by reading and by 80 CPU conformance tests (engine bit-identical to the oracle):
- delivery comes before the environment;
- aloha and saturate use floor division;
- Acc is clamped to 2^20 and SENSE is clamped;
- asleep sites keep Acc, and their registers and O stay unchanged;
- Kp/r_next are applied after the program, and SEL reads the old reg[d];
- the economy tests E before its update and uses S after write-back;
- the routing write happens before sampling (A4);
- dup and delay2 follow DESIGN, and the noise sub-index is f*16+p with P <= 16;
- mutation comes after Kp_next, and decay applies to all sites.

**Mailbox.** Delay lies in [1, LM-1], so the slot just delivered is always empty afterwards.

**Control placement.**
- reset_state_at and flush_inflight_at act after emission and mutation and before decay. This matches the C1b PREREG.
- drop_packets_at acts at delivery.
- Controls draw only from the CTRL stream.

**Hook timing.**
- lens.run applies hooks AFTER tick t, with recorders running first.
- lens_swap.run_arms swaps after tick k*Pd+offset, as the Arm doc says, and selfcheck asserts that the batched run equals lens.run.
- swap and swap_rows copy via advanced indexing, so the right-hand side is copied first and nothing aliases.
- Partners are index ^ 1, and blocks of even size M never cross.
- roll_slots with k=1 loses nothing, because slot t-1 is empty.

**Mirror pairing** is consistent as (2p, 2p+1):
- evaluate, lens, lens_swap and c1b all use ws = seeds[m - m%2];
- envs uses the lead seed and negates the targets for the partner;
- a constant policy scores exactly 0.5 per pair, and S0 == 0 scores 0.5;
- sens_act uses the lead world's targets.

**Search and campaign statistics.**
- The champion is chosen on training accuracy only.
- The held-out, final and training namespaces are distinct.
- comm_delta is paired on the same held-out worlds.
- The A0 living and plant namespaces are distinct.

**C1b.**
- The m2 and m3 label tables are exhaustive and first-match.
- The fixtures exercise the component booleans.
- rule_predicts is scored on a held-out half.
- The release-guard tests pass on the original code.

**swap_rel.**
- FLIP > NO_EFFECT > CHANCE precedence is implemented correctly.
- pair_means is correct.
- The H2 interval is nested inside the BOOTT interval.

**Previously known defects** (confirmed, not re-reported):
- C1 E1: the packet-ablation window excludes the readout tick.
- C1 E2: frozen routing is vacuous under dest_mode all.
- C1 E3: the memory ablation resets S only.
- C1b K1: the census reads payload component 0 only.
- C1 F5: the HOLD env variants change dials HOLD never reads.
- PREREG D1-D3: the boundary-criterion defects.

## OPEN QUESTIONS

1. Should the stored REACH_BEYOND_HOP labels carry an erratum? They are in 678 C1 rows. The MAJ and XOR positives cannot be interpreted (H1), and on global topology the label can never fire (H2).
2. Should C1_REPORT s1 change "frozen RELAY laws ... size-free" to "one RELAY law (bbef66a1)"? (H5)
3. Should the REL4 FC table be re-simulated under mirror-pair statistics (2K correlated trials per pair, with K counted per world) before H2 is used as a carrier ruler? (H16)
4. Should the instrument doc say that swap identity on HOLD is empirical, not forced? (H15)
5. For a future C2 driver, should dial tables read the physics actually run rather than the drawn levels, and skip transects on dials that have no effect at their base? (H7)
