<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-A1; sha256(report)=4ccdf6bc157bda01; delimited; see REPORT.provenance.json -->
# W2-A1: what the PTE world code actually does (worker W2-A1, Ananke Wave 2, 2026-10-01)

Worktree: F:/Prometheus-worktrees/ananke-base-role at fd631acb2. I wrote only under roles/Ananke/research/harvest/wave2/W2-A1/ and changed no repo file. Every script and test ran CPU-only (CUDA_VISIBLE_DEVICES=-1, at most 2 threads); `scratch/common.py` asserts that no GPU is visible. Run every command from the worktree root.

**Code read in full:**
- engine.py, physics.py, topology.py, rng.py, envs.py, plants.py.
- From assays.py: evaluate, controls, twin assay, transplant.
- From campaign.py: physics_from_levels, waves, transplant battery.
- search.py.
- The oracle's docstring (ambiguities A1-A19).

**Documents read:** DESIGN.md, PREREG_PTE_C1.md, PREREG_PTE_C1b.md, C1_REPORT.md, C1_ERRATA.md, PTE_CAUSAL_AUDIT, and H-IMPL/REPORT.md.

## Deliverables (files)

| File | What it is |
|---|---|
| CAUSAL_GRAPH.txt | Causal graph derived from the code. For every write of a state array or transient it gives the parents and engine.py line numbers, plus a state-level adjacency list and structural notes. |
| causal_graph.dot | The same graph as Graphviz DOT; edge labels are line numbers. |
| tests/test_w2a1_engine_invariants.py | 78 invariant tests. All pass on current code. |
| tests/test_campaign_record_effective_dest_mode.py | Regression test for the dest_mode record fix. |
| tests/test_campaign_flip_state_transplant.py | Regression test for the FLIP state-transplant fix. |
| tests/test_SEMANTIC_envs_maj_forward_placement.py | Test for the MAJ sensor-placement fix. |
| patches/campaign_record_effective_dest_mode.diff | NEUTRAL fix. |
| patches/campaign_flip_transplant_noop.diff | NEUTRAL fix. |
| patches/campaign_combined.diff | The two NEUTRAL fixes together. |
| patches/SEMANTIC_envs_maj_forward_placement.diff | SEMANTIC fix, for C2 only. |
| scratch/*.py | Every check cited below. Patched package copies are in scratch/patched and scratch/patched_envs. |

**Short version of the causal graph (full version in the files):**
- **Sites interact only through the mailbox.** Msum and Mcnt are indexed by the receiving site; there is no other edge between sites and no edge between worlds.
- **SENSE enters only through an awake site's register file** (engine.py:316). It is never latched; packets, by contrast, wait in Acc.
- **The environment is open loop.** The schedule is fixed before tick 0, and the FLIP teacher is the target value, not an error signal that depends on what the system did.
- **Every random draw is a pure function of (ws, stream, t, n, j).** Mirror twins share ws (assays.py:56), so twins share every draw: wake, route, loss, latency, noise, RAND, mutation and CTRL.

## 1. Findings

Tags: [V] = verified by a check (script given); [I] = inferred from code reading.

**F1 [V] MAJ sensors are placed in the wrong direction on directed graphs. This produces 2 of the 3 MAJ topology boundary candidates, and the third is confounded.**
- **What the code does:** envs.py:212 calls `_pick_at(g, M[a], d)`. M[a] is the BFS hop count from the actuator over the directed out-edge table, but packets travel sensor to actuator, which is M[s, a]. The two are equal only on symmetric graphs (ring, torus, global).
- **Random topology, A0 MAJ plant worlds:**
  - Only 2959 of 16080 sensors (18%) sit at transport distance d.
  - In 81 of 3216 worlds (2.5%) the actuator has no in-edge, and in 101 worlds no sensor can reach it at all. Those worlds can only score 0.5.
- **The transect (MAJ topology, phys track, base 1).** Recorded level means: torus .625, ring .611, random .503, smallworld .618, global .493.
  - With forward placement and the same random draws, the random level becomes .602 / .648 / .622 (B) and .579 / .638 / .667 (B2), i.e. about .62.
  - So candidates [1,2] (-.108) and [2,3] (+.115) are artefacts of the placement.
  - Candidate [3,4] (smallworld to global, -.125) is confounded by F2: base 1 has dest_mode=all, so the global level also switches the copy count from 4 to 2.
- **Effect on recorded labels:** none. All three stay CANDIDATE; the "fresh-seed reproduced" flag reproduces because the artefact is deterministic.
- **MAJ D-wave topology->random transplants:** they collapse with either placement (0.50 / 0.50 / 0.50 with forward placement), so those readings stand.
- **XOR has the same reachability hole:** envs.py:195 does not require that the actuator be reachable from sensor 2. XOR is NULL anyway.
- **Checks:** `python roles/Ananke/research/harvest/wave2/W2-A1/scratch/maj_direction.py`, `maj_direction2.py`, `maj_transplant_dir.py`.
- **Confidence:** high.
- **Strongest objection:** the forward rerun could differ in something besides direction. Answer: `_pick_at` consumes exactly one draw per sensor either way, the seeds are identical, and only the distance vector changes. Base 0 (plant-dead at every level) does not change, as expected.
- **Unresolved:** how much of the MAJ NULL on random and smallworld cells, and of the MAJ dial_effects tables, is this artefact.

**F2 [V] dest_mode, re-attacked from code: the alias exists and the record is wrong, but it changed nothing downstream except one confound and the evidence-package text.**
- physics_from_levels (campaign.py:88-89) forces sample on global but stores the drawn levels. Exactly 951 of 1589 global rows record "all"; the row's `physics` dict, which is what the engine runs, says sample.
- **No effect on what wave B chose to transect.** I recomputed campaign.dial_effects with the actual dest_mode for all 8 family-by-track selections, and the selected dial lists are identical. My reimplementation reproduces the transects wave B actually ran exactly. The dest_mode effect score moves (RELAY plant 3.46 to 5.58 SE) but never enters a top 3. A0_FINDINGS and a0_interactions do not use dest_mode.
- **Consequential piece 1:** a topology transect at a dest_mode=all base silently changes the copy count from R to F at its global level. This affects 6 transect groups and one candidate (MAJ topology phys base 1 [3,4]).
- **Consequential piece 2:** the committed c1_report/summary.json describes 5 of the 12 D-wave adjudicated cells (four HOLD latches and the MAJ cell 613162a3) and 3 "A1 best" entries as "global, dest_mode all". They ran sample, four of them with fanout 1, i.e. one random recipient per emission.
- **Checks:** `scratch/rows_alias.py`, `scratch/dial_select.py`, plus the summary.json walk recorded in this report's ledger.
- **Confidence:** high.
- **Unresolved:** none for C1. Fix offered for C2 (P1).

**F3 [V] max_loss is the same run as zero_comm, and shuffle_dest on global topology is a re-draw of the routing noise, not a control.**
- **max_loss:** with loss 1.0, surv16 = 0, so nothing is ever delivered and the stats match zero_comm exactly. The pair vectors are identical in 12 of 12 D rows.
- **shuffle_dest on global:** every copy already goes to a uniformly random other site, so shuffle_dest only re-draws recipients from the same distribution (plus self-delivery with probability 1/N).
  - On 613162a3 over 3 seed sets, shuffle_dest moved accuracy by +.042 / -.010 / +.014.
  - Re-drawing the ROUTE stream (monkeypatching rng.ROUTE; no file changed) moved it by +.033..+.054 / -.019..-.005 / -.007..+.030.
  - So the recorded "shuffle_dest .72 > normal .688" is variance from the routing realisation.
- **Checks:** a short python one-off over the D rows (not saved; recorded in the ledger), and `scratch/global_shuffle.py`.
- **Confidence:** high.
- **Objection:** self-delivery could matter for programs that read their own packets. That is the only possible difference, and it was not detectable here.
- **Effect on labels:** none. CAUSAL_SUPPORT does not use either control. It does affect wording: C1_REPORT M1 counts "zero-comm, max-loss and shuffled destinations" as three controls, and max_loss is not an independent one.

**F4 [V] The twin-contrast selection bonus cannot see noise on linear paths.**
- Twins share the NOISE draw (engine.py:515-518), so for a linear readout S0_lead - S0_twin cancels additive noise exactly. assays.sens_act (assays.py:83, used in search.py:94) then pays the full +0.10 at chance accuracy:
  - linear relay, amplitude 1, noise 64: accuracy .507, sens_act +1.000;
  - thresholded readout, same physics: sens_act +.023 (it tracks roughly 2*acc-1).
- **Consequences:**
  - Under noise, selection favours linear, sub-noise codes over thresholded ones of equal accuracy, by up to 0.10. This adds to the "pays one-sided codes" point in the Wave-1 audit (item 0.3).
  - The L2 rung (frac_contrast_pos) measures influence with the noise removed.
- **Checks:** `scratch/common_mode.py`, `scratch/common_mode2.py`; tests I7 pin the mechanism.
- **Confidence:** high for the mechanism; its effect on C1 champions is unmeasured.
- **Effect on labels:** none; champions and labels use accuracy only.

**F5 [V] The SUPPORTED "economy low to high" boundary in RELAY plant viability follows from arithmetic.**
- Energy never gates operations, only emission (engine.py:386-393). relay_flood has 12 non-NOP instructions; with c_op 1 and income 4 it loses at least 8 per tick, reaches E = 0 within about 12 ticks, and can never afford an emission again.
  - Measured last emission tick: 11 (sync period 1) and 38 (period 2); plant accuracy .615 / .646.
  - A0 RELAY at economy high: 0 of 364 cells reach .75; maximum .602.
- **Prediction confirmed:** every comm-family SIGNAL under "high" (4 cells) is a sync-period-2 MAJ program with 4-6 active instructions per rule and emit rate about .003. RELAY is 0 of 24.
- **Also:** the ENERGY register is a readable constant (1000 when the economy is off, otherwise e_max). So the economy dial changes which constants a program can read as well as what things cost.
- **Check:** `scratch/economy_gate.py`.
- **Confidence:** high.
- **Effect on labels:** none. It sharpens C1_REPORT's "gated by energy cost" into a budget identity you could predict without running anything.

**F6 [V] The FLIP adapted-state transplant (PREREG s9) can never return data.**
- campaign.flip_state_transplant builds the donor and the recipient from identical seeds, genome and schedule, so transplant_state always raises "NOT_APPLICABLE: transplant changed nothing". That exception escapes run_cell, so any FLIP adjudication cell would fail and count toward PARK.
- Two further mismatches with its own docstring:
  - it promises "fresh cues, same mapping", but the code uses the same cues;
  - it scores trials k0+1 and k0+2, which already run under the flipped mapping of block 2.
- No FLIP cell reached wave D in C1 (0 FLIP SIGNAL), so no row is affected.
- **Check:** `scratch/flip_transplant.py`.
- **Confidence:** high.
- **Fix:** P2 (NEUTRAL; it turns the crash into an honest NOT_APPLICABLE). The real design fix is SEMANTIC and belongs in C2.

**F7 [V] SENSE is not latched for asleep sites, which sets ceilings nobody stated.**
- A cue lasting cue_len ticks is missed with probability (1-p)^cue_len.
- Single-sensor ceiling = 1 - 0.5(1-p)^2: .875 at p=.5 and .98 at p=.8.
- MAJ under async .5: single-sensor ceiling .650 (the PREREG states .70); five-sensor Bayes ceiling .788 (.837 under sync).
- The data never exceed these ceilings. Best held accuracy: HOLD async .5 .839 vs .875; RELAY async .8 .786; MAJ async .5 best lo99 .509.
- **Checks:** `scratch/async_ceiling.py`, `scratch/maj_ceiling.py`; test I10.
- **Confidence:** high.
- **Effect on labels:** none. The INTEGRATION bar is conservative there.

**F8 [V] Two sign asymmetries that DESIGN s10 does not mention.**
- **Saturate collision:** floor((-x)·cap/tot) is not -floor(x·cap/tot), so small positive sums vanish while small negative sums survive.
- **Routing write:** rval >> shift adds 0 for rval in [1, 2^k-1] but -1 for rval in [-2^k, -1], so small noisy rval values steadily depress w.
- **Checks:** `scratch/small_semantics.py` (a); test I7 shows both break twin antisymmetry, as noise and decay do.
- **Confidence:** high.
- **Effect on labels:** none known. The M2 specimen uses saturate, but its payloads are about ±256.

**F9 [V] Dials that are read but have no effect, beyond H-IMPL H7.**
- **cap with collision=none:** cap is never enforced, contrary to DESIGN s1's "max packets per site per tick". This holds in 1761 of 4963 cap>0 rows. H7 lists only the converse case.
- **k_random and radius on smallworld:** inert, contrary to DESIGN s1 (oracle ambiguity A15).
- **EnvSpec.variant:** always 0, a dead dial.
- **Soundness of my inert-dial table:** I encoded it as an effective-physics canonicaliser (`scratch/canon.py`). Across 73 dial changes with genomes that always transmit, there were 0 cases where it said "inert" and the run differed (`scratch/check_canon2.py`).
- **Applied to all 104 B/B2 transect groups:** exactly 3 are fully inert (the same 3 as H7), with no partial aliases and no boundary sitting on identical physics (`scratch/transect_alias.py`).
- **Confidence:** high.

**F10 [V] "XOR single-input = 0.500 exactly" (PREREG s2) holds only for sensor 2.**
- Twins negate x1 only, so x2 is identical in both twins. A program that reads only x2 is exactly .500 per pair; one that reads only x1 is .500 only in expectation, with pair values from .208 to .667.
- **Check:** `scratch/xor_single.py`.
- **Effect on labels:** none (XOR has 0 SIGNAL).

**F11 [V] Smaller semantic notes.**
- **The `delivered` statistic is counted at emission.** It includes packets later destroyed by aloha collisions, drops or flushes, and packets still in flight. In a test with nothing ever reaching an inbox, it read 160 delivered, 144 collided, Acc 0 (`small_semantics.py` b).
- **shuffle_time widens the delay range rather than permuting it.** Normal delays are 2..5; shuffled delays are 1..7 on M1 physics.
- **shuffle_dest keeps the original edge's distance** for loss and latency, and can deliver to the sender itself.
- **With rules > 1 and setrule = 0, sites form a fixed random mosaic of rule variants** (r0 = H(ws, INIT, ...)), not a homogeneous program. [I]
- **The no-op guard compares full state digests.** A control that changes only state nothing reads (w under dest_mode all) passes it; this is the mechanism behind erratum E2 and H12. [I]

**Invariants (tests/test_w2a1_engine_invariants.py, 78 tests, all pass on current code):**

| # | Invariant | Holds? |
|---|---|---|
| I1 | Messages are conserved with no loss, no duplicates and no cap: count and payload in equal count and payload out | yes |
| I2 | attempted = delivered + lost, including under zero_comm | yes |
| I3 | Locality under zero_comm: perturbing one site's input changes no other site, ever (the root cause of zero_comm reading exactly .500) | yes |
| I4 | Light cone: divergence at hop distance h appears no earlier than t_p + h·dmin | yes |
| I5 | A world's trajectory does not depend on which other worlds share its batch | yes |
| I6 | All state stays within its bounds | yes |
| I7 | Twins of a sign-symmetric program are exact negatives | yes, except under noise, saturate or decay; the test pins these breaks |
| I8 | Inert-dial changes leave traces bit-identical (pins the dial-semantics table) | yes |
| I9 | CTRL-stream controls leave emission and loss draws unchanged | yes |
| I10 | Async cue loss: hold_latch scores about .875 at p = .5 | yes |

To show the tests can fail: under a wrong premise (duplicates on, zero_comm off, hop counts doubled, a non-inert dial), each of I1, I3, I4 and I8 fails, as it should (`scratch/mutation_check.py`).

**Mismatch table.** None of these changes a recorded C1 or C1b label.

| # | Document says | Code does (file:line) | Changes a verdict? |
|---|---|---|---|
| 1 | DESIGN s1: cap is the maximum packets per site per tick | cap enforced only under aloha or saturate (engine 282-293) | no |
| 2 | DESIGN s1: k_random applies to smallworld | ignored (topology.py:28-36) | no |
| 3 | DESIGN s7: targets exactly balanced | iid targets + mirror pairs (envs 120, 152); PREREG matches code | no |
| 4 | DESIGN s7: XOR sensors and actuator at distance >= d | s2 exactly at d; a at >= d//2; a may be unreachable from s2 (envs 191-197) | no |
| 5 | DESIGN s7: MAJ actuator at distance d from the sensors' centroid | reversed-direction placement (envs 208-214), F1 | 2 CANDIDATEs are artefacts; labels unchanged |
| 6 | DESIGN s7: FLIP teacher is a separate site, amplitude A | teacher is the actuator, amplitude 128 (envs 177, 189); PREREG matches code | no; explains why FLIP zero_comm is not forced (62 of 94 rows exactly .500) |
| 7 | PREREG s2: XOR single input exactly .500 | true for x2 only, F10 | no |
| 8 | Not stated anywhere | SENSE not latched while asleep, F7 | no |
| 9 | DESIGN s10 lists decay, SHR and MULQ as sign-asymmetric | saturate and the routing write are also asymmetric, F8 | no |
| 10 | Controls docstring for shuffle_dest and shuffle_time | F3, F11 | no; changes wording only |
| 11 | max_loss treated as its own control | identical run to zero_comm, F3 | no; changes wording only |
| 12 | campaign.py flip_state_transplant docstring | F6 | latent crash; C1 untouched |
| 13 | Recorded levels | dest_mode alias on global and n_sites in wave E rows, F2 | no |
| 14 | Stats vocabulary | `delivered` counted at emission, F11 | telemetry only |
| 15 | DESIGN C2: independent streams | true; but twins share every stream, so twin-difference statistics cancel noise, F4 | selection only |
| 16 | Economy as a cost dial | ENERGY is a readable constant; the "high" level is a budget identity, F5 | no; changes interpretation only |

## 2. Proposed fixes

- **P1 NEUTRAL: patches/campaign_record_effective_dest_mode.diff.** physics_from_levels writes the dest_mode that actually runs back into `levels`.
  - cell_id does not hash levels, so ids and seeds are unchanged.
  - Verified that C1's wave-B dial selection is identical with corrected levels.
  - Test: tests/test_campaign_record_effective_dest_mode.py fails on current code (1 failed, 3 passed) and passes on the patch (4 passed). The existing tests test_campaign_logic and test_wave_d_resume_determinism also pass on the patched copy.
- **P2 NEUTRAL: patches/campaign_flip_transplant_noop.diff.** The FLIP state transplant returns {"status": "NOT_APPLICABLE"} instead of crashing the cell, and reports no accuracy for a no-op.
  - Test: tests/test_campaign_flip_state_transplant.py fails on current code (2 failed) and passes on the patch (2 passed).
  - Combined P1 + P2 diff: patches/campaign_combined.diff (`git apply --check` passes). test_envs_assays, test_campaign_logic, test_c1b_switches and test_wave_d_resume_determinism pass on the patched copy (36 tests).
- **P3 SEMANTIC, for C2 only: patches/SEMANTIC_envs_maj_forward_placement.diff.** Places MAJ sensors by transport distance (column M[:, a]), re-draws actuators that have no in-edge, and requires the XOR actuator to be reachable from both sensors.
  - Episodes on ring, torus and global are bit-identical to the frozen code (golden digest 6d106abafb245c54, checked on both copies), so every C1 SIGNAL physics point is unaffected.
  - Test: tests/test_SEMANTIC_envs_maj_forward_placement.py fails on current code (2 failed, 1 passed) and passes on the patch (3 passed). test_envs_assays and test_campaign_logic pass on the patched copy.
- **Not code, for the principal to annotate (DESIGN annotations):** cap under collision=none; k_random on smallworld; FLIP teacher site and amplitude; SENSE not latched; saturate and routing-write sign asymmetry; meaning of `delivered`; max_loss being the same run as zero_comm; shuffle_dest on global.

**Running the tests:**
```
CUDA_VISIBLE_DEVICES=-1 python -m pytest -q roles/Ananke/research/harvest/wave2/W2-A1/tests
W2A1_PKG_ROOT=roles/Ananke/research/harvest/wave2/W2-A1/scratch/patched CUDA_VISIBLE_DEVICES=-1 python -m pytest -q roles/Ananke/research/harvest/wave2/W2-A1/tests/test_campaign_record_effective_dest_mode.py roles/Ananke/research/harvest/wave2/W2-A1/tests/test_campaign_flip_state_transplant.py
W2A1_PKG_ROOT=roles/Ananke/research/harvest/wave2/W2-A1/scratch/patched_envs CUDA_VISIBLE_DEVICES=-1 python -m pytest -q roles/Ananke/research/harvest/wave2/W2-A1/tests/test_SEMANTIC_envs_maj_forward_placement.py
```
On current code the first command reports the 5 expected failures listed above (P1: 1, P2: 2, P3: 2); the invariant suite and the neutrality tests pass.

## 3. Disagreements with Wave 1 and the principal

1. **PTE_CAUSAL_AUDIT s0.1, "max_loss and shuffle_dest are the same forced control":** half right.
   - max_loss is literally the same run as zero_comm (identical pair vectors).
   - shuffle_dest is not forced on lattices: its D values are .521 / .523 / .514 / .525 / .520, i.e. near chance mechanically but not exact.
   - On global topology shuffle_dest has a different defect: it is a re-draw of the routing noise (F3).
2. **H-IMPL H7, "dial_effects and analysis_a0 count them that way":** true but it had no consequence. B dial selection is unchanged and the A0 findings do not use dest_mode. The consequences are the topology-transect confound and the summary.json descriptions (F2).
3. **H-IMPL H20 treats the MAJ geometry drift as a NOTE:** on directed graphs it is material. It manufactures 2 of the 3 MAJ topology candidates, and about 2.5% of random-topology MAJ worlds are impossible by construction (F1).
4. **C1_REPORT and PREREG annotation D1 read the MAJ topology candidates as categorical level contrasts:** they are an artefact (two) and a confound (one). D1's caution was right, but its explanation was not.
5. **H-IMPL H7's inert-dial table** misses "cap is inert when collision = none" (1761 rows) and the smallworld cases.
6. **C1_REPORT reads the economy boundary as "energy cost gates the design":** it is a budget identity (instruction count against income) that holds for any program (F5).

## 4. Next questions (ranked)

1. In C1 cells with noise > 0, are champions disproportionately linear (unthresholded) or low-amplitude readouts, as F4 predicts? Count champion readout types against noise, then run a bonus-free search on 2-3 noisy cells. CPU, small.
2. Re-measure A0 MAJ plant viability on random and smallworld cells with forward placement (patched copy, CPU, about 1000 cells × 32 worlds; needs a bounded budget). How much of "MAJ NULL on directed graphs" eligibility was placement artefact?
3. Do evolved champions read the ENERGY register? If so, separate the cost effect from the constant effect in the economy contrasts.
4. Under sync period 2, the wake parity makes the usable window alternate between delta and delta-2 across trials. Compute the per-cell timing ceilings for the RELAY/MAJ NULL cells: are any NULLs ceiling-bound?
5. Replace the no-op guard's state digest with one over read state only (exclude unread w and the size of the LM mailbox), so that vacuous controls such as frozen_routing under dest_mode all come out NOT_APPLICABLE automatically. Check this against the C1b A2.1 table.
6. Design a working FLIP state transplant before any FLIP adjudication in C2: a recipient with fresh cues under the same mapping, scored within the donor's block.
7. Should XOR worlds whose actuator is unreachable from sensor 2 on random graphs be counted, and how many are there in C1?

## 5. Inference ledger
question | evidence | result | confidence | strongest objection | unresolved | next
- dest_mode alias consequences | rows_alias.py, dial_select.py, summary.json walk | 951/1589 exact; B dial selection unchanged; 6 transect groups confounded; 5/12 D descriptions wrong | high | another consumer of levels I missed | none for C1 | apply P1 for C2
- inert dials | canon.py, check_canon2.py, transect_alias.py | 0 cases where "inert" was wrong in 73 changes; 3 inert transects (= H7); cap-under-none and smallworld cases are new | high | the test genomes are not exhaustive | dial_effects dilution | pin with test I8
- MAJ placement direction | maj_direction*.py, maj_transplant_dir.py | 18% of sensors at transport distance d; 2.5% of worlds impossible; random dip disappears (.50 to .62) | high | the forward rerun changes something else | size of the MAJ NULL artefact | Q2, P3
- forced and aliased controls | D-row comparison (one-off), global_shuffle.py | max_loss = zero_comm in 12/12 rows; shuffle_dest on global = route re-draw | high | self-delivery effect | none | annotate
- common-mode noise and the bonus | common_mode*.py | linear sens_act +1.0 at acc .507; thresholded +.02 | high (mechanism) | effect on real champions unknown | selection bias size | Q1
- economy boundary | economy_gate.py | plant mute by tick 11; A0 high 0/364; high-economy SIGNALs all small period-2 MAJ programs | high | emission cost also contributes | ENERGY-constant confound | Q3
- FLIP state transplant | flip_transplant.py | always raises; would fail the cell | high | none | real design | P2, Q6
- async cue loss | async_ceiling.py, maj_ceiling.py, test I10 | ceilings hold in all rows; MAJ single-sensor ceiling .65 at p=.5 | high | none | none | none
- sign asymmetries | small_semantics.py, test I7 | saturate and routing-write floors are asymmetric | high | low practical size | effect on M2 | annotate
- XOR single input | xor_single.py | exact for x2 only | high | none | none | annotate
- engine invariants | test_w2a1_engine_invariants.py, mutation_check.py | I1-I10 hold; tests can fail | high | the property set is incomplete | GPU graph equivalence not tested here | adopt as regression tests

## 6. Compute used
- About 12 minutes of process wall time in total. Every process was CPU-only, with at most 2 threads and well under 10 minutes each.
- Estimate: about 0.2 core-hours; upper bound 0.4 if both threads were busy throughout.
- No GPU, no lease action, no background processes left running, no repo file modified. The read-only git commands used were status and log.
