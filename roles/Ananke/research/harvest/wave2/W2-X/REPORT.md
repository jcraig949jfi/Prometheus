<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-X; sha256(report)=c9bfa50f2ee1a7a4; delimited; see REPORT.provenance.json -->
# W2-X: adversarial review of the principal's Wave-2 products (Ananke)

Worker W2-X, Opus, fresh context. Worktree F:/Prometheus-worktrees/ananke-base-role, read at HEAD 594385d78. The principal committed E-W14..E-W18 and H6 v4 while I was working, so I checked those too where they bear on my findings.

My directory is roles/Ananke/research/harvest/wave2/W2-X/. It contains:
- scripts: check_levels_leak.py, check_p3_flat_labels.py, check_ew13_boundary_bases.py (+ .json), check_multihop_forwarding.py (did not finish, see F8);
- patches: patches/w2x_levels_leak_and_reading3_degenerate.diff and patches/w2x_existing_test_updates.diff;
- tests: tests/test_w2x_regressions.py;
- scratch/pre (code at 14667359b, before the four principal commits), scratch/post (HEAD) and scratch/fix (HEAD with my patches).

## 0. Verdict first
- **Code.** The applied fixes do what their tests say. The "fail before / pass after" counts reproduce exactly: edf1f1f12 3/5; dc46fd00f campaign 6/13 (reading3 5/5).
- **Not neutral.** The dest_mode record fix in dc46fd00f is NOT neutral for any future run. It writes the forced value into the levels dict that `_transect_specs` re-derives physics from.
  - Effect: a topology transect from a global base now runs its torus/ring/random/smallworld cells at dest_mode "sample" instead of the drawn "all", and so gets new cell ids.
  - C1 is unaffected: it had no global base.
  - The neutrality test sidesteps exactly this path by passing `dict(base_lv)`.
- **The new inference.reading3 certifies forced controls.** An array of .5 in every pair (zero_comm / env_permutation) reads TRUE with d_se = inf and keep 1.0, and a test pins that behaviour.
- **Frozen semantics.** No principal commit changed frozen C1/C1b semantics or recorded rows/labels. The C1b driver change matches the disclosed post-hoc correction in c1b/build_summary.py. The P1 track filter is vacuous on C1: all 6 RELAY plant SUPPORTED verdicts are phys track.
- **Science.** The principal's errata are mostly well supported, number by number. The overreach is in the synthesis layers: the handoff, H6 v2-v4 and DEFECT_PATTERNS.
  - Several are contradicted by later workers: W2-P/U/T on "most NULLs are construction", W2-R on "blind selector" and W2-A1 F4, W2-J/W2-S on the recommended rulers, W2-K on 613162a3 fragility, W2-O on 2.5%, W2-I F3 on "topology-bound killed".
  - Two are conceptual errors: the "selection-environment" story for the one-hop wall, and "sharp wall" from 2 hop levels with a mirror-forced .500.

## 1. Findings table
Verdicts: S = SUPPORTED, O = OVERSTATED, C = CONTRADICTED, U = UNSUPPORTED.

| # | Claim | Location | Verdict | Evidence | Proposed corrected wording |
|---|---|---|---|---|---|
| 1 | "Most of C1's structural laws and NULLs are decided by construction ... before search runs" | HANDOFF "Strongest new result" | C | 111/454 = 24% capped at the 50%-power bar; strict (≤ .55) 93/454 = 20.5% (W2-P F2, W2-U F3). Admissible for a search reading: 48-58% (W2-T). XOR alone is 62/83 under LC2 (W2-J). | "About a quarter of C1's evolve NULLs (111/454; 93 strictly) could not reach SIGNAL by construction, and XOR up to 62/83 under LC2. Several structural readings are construction-forced: MAJ placement, hop demand, controls." |
| 2 | "111/454 ... were unwinnable by any program" | E-W14 | O | .614 is the 50%-power SIGNAL-attainable accuracy, not impossibility. W2-U: "strict ≤ .55 count is 93". W2-P ledger says the same. | "...had a joint ceiling below .614, where SIGNAL is reached with < 50% power. 93/454 (20%) have ceiling ≤ .55, so SIGNAL is unattainable." |
| 3 | "Topology-bound laws: KILL candidate (hop count)"; "topology-bound laws are hop-bound" | HANDOFF; DEFECT_PATTERNS P1; E-W1 last sentence | O | W2-I F2/F3: RELAY 15/18 hop-bound, 2 cluster-bound, 1 weak; MAJ 4/6 hop-bound, 2 cluster-bound (4781b0a1 is TOPOLOGY-BOUND refined to CLUSTER-BOUND). Retention at matched hops: median .78, range .36-1.8. The 4 RELAY D-wave numbers are right (lo99 .573-.811, W2-G F1). | "The D-wave collapse is hop count, not lattice offsets. Residual graph dependence remains: clustering or redundant short paths (4 laws) and per-port latency labels (W2-I F3). REFINE, not KILL." |
| 4 | E-W2 "2.5% of random worlds are impossible" | E-W2 | O | W2-A1's 3216 worlds are A0 plant worlds. On C1 evolve worlds: 0 impossible in XOR/FLIP/RELAY, MAJ 0.17% (W2-O). | "...2.5% of A0 random-topology MAJ plant worlds (W2-A1). On C1 evolve worlds, 0.17% (W2-O): immaterial." |
| 5 | E-W2 MAJ geometry: d=1 ≡ d=2 on rings, 3/5 sensors off d, 18% at transport d, 2/3 candidates artefacts, 19/19 SIGNAL one-hop | E-W2 | S | W2-A2 F3, W2-A1 F1, W2-I F4. | Add W2-P: under inward placement 0/35 champions and 0/35 relay_flood become SIGNAL, and 18 rows stay capped. Placement is not the whole MAJ-graph NULL story. |
| 6 | "36/83 = 43% of XOR evolve rows ... capped below .60 for ANY program" | E-W3; HANDOFF "17% → 43%"; H6 v2/v3 "XOR 43%" | O (superseded) | W2-J LC2: 62/83 (75%) capped. W2-U: count 36 but membership differs by 2 in, 2 out (32-pair estimate ± .13). The bound is an expectation (P-1a; W2-P F4: up to .518 from stale cues). | "≥ 36/83 by the deterministic light cone (in expectation); 62/83 by LC2 (W2-J). Membership needs ≥ 512 position pairs (W2-U)." |
| 7 | 150/196 RELAY evolve rows demand one hop; 17 distinct conditions; 21/30 reachable multi-hop rows relay_flood-dead; 40/99 vs 2/9 | E-W4; P-1b | S (numbers) / O (test) | My recount gives 150 one-hop / 46 multi-hop [V]. The unbiased A1 wave is 32 one-hop / 39 multi-hop. "n.s." is computed on rows, but the units are conditions (23 vs 5). | Add: "A1 itself was 55% multi-hop; the 77% comes from targeted waves. The 2/9 vs 40/99 comparison has 5 vs 23 independent conditions." |
| 8 | "Multi-hop is rare is mostly a plant-viability/physics fact" | P-1b result; H6 v2 | C (by P-2) | E-W13: relay_flood death under decay is plant design, not physics. | "...a relay_flood-design fact (E-W13). The 21 'dead' rows are undecided, not physics-dead." |
| 9 | "The search never discovered forwarding. It never needed to, because 77% of RELAY tasks were one-hop (selection-environment limit)" | H6 v3 item 2; v4 "one-hop wall (forwarding never discovered)" | U (category error) | Each GA run selects on ONE cell's task; nothing carries across cells (wave_A docstring; B transects pass no genome). 46 searches faced multi-hop tasks and were fully rewarded for forwarding. The 77% explains pooled counts, not search behaviour. Two multi-hop SIGNAL rows exist: 925caa3a (ring r3 d5, lo99 .556; fails under t, W2-H) and 882525a9 (smallworld d3, lo99 .564). W2-I leaves "whether any law relays" UNRESOLVED. | "No C1 champion is shown to forward. Laws evolved on one-hop tasks (all 7 D laws) do not cross 2 hops. In 30 reachable multi-hop searches (9 relay_flood-viable), 2 marginal SIGNALs occurred, mechanism untested. Whether search can discover forwarding is undecided (n ≈ 9-30)." |
| 10 | "The one-hop wall is sharp ... nothing in between" | H6 v3 item 2 | O | Only two hop levels were tested (1 and 2). Exactly .500 at 2 hops is what mirror pairs force for any program with no current-trial information (W2-B P1; W2-P F4). "Sharp" is a two-point step plus a design-forced value. | "At d9cc-like physics the 7 D laws go from SIGNAL at 1 hop to the mirror-forced .500 at 2 hops; intermediate behaviour is not measured." |
| 11 | "FLIP @ d9cc: S under a blind selector (M = 8)"; "fourth explanation (D)" | H6 v2, v3 statement | C | W2-R F5 [I]: GA genomes share the same 8 worlds, so comparisons are paired. Paired SE is .020-.036, and a .10 gain (relay .60 vs .50) is about 3-5 SE, visible. P-3's own data: genomes score exactly .5 with zero variance (no chance ceiling) until about gen 4. v4 drops the phrase, but the v3 statement still stands in the file. | "FLIP @ d9cc: S (isolated peak, 6% neutral offspring). Selector blindness is disputed (W2-R F5); the M-sweep remains the decisive test." Strike "blind selector" from v3. |
| 12 | "All of R, P, U and V(full) are excluded there" | H6 v2 | O | W2-D F4: U is "excluded over 4 and 2 generations (2/2 runs)". That is 2 seeds, below W2-D's own falsifier F-U (3 seeds) and its 36-generation horizon. | "R, P, V(full) excluded. U not observed over 4+2 generations in 2 seeds (F-U needs 3 seeds and the full horizon)." |
| 13 | "an unclimbed .60 relay basin ... the band where the stepping stones live" | H6 v2 | U | W2-L F5 (as corrected by W2-S): copy-class policies are capped at B ≤ .75 and score exactly 1/2 on changed-cue trials. relay_flood's FLIP edge is a change-gated teacher hold (W2-L F3). No evidence the copy basin lies on a path to inference. | "a .60 copy-policy basin (ceiling .75) whose connection to the inferring plant is untested." |
| 14 | "NULL champions ... MEMORY_WITHOUT_USE (46) and REACH_BEYOND_HOP/persist are, at onset, products of the w_any term" | E-W10; P-3 inference; DEFECT_PATTERNS P7 | O | P-3 shows population sens_any onset only; the labels are measured on final champions. Natural experiment [V, check_p3_flat_labels.py]: in the 40 flat runs (bonus is the ONLY selective signal), MWU 1/40 vs 37/414 non-flat, REACH 11/40 vs 193/414, median beyond_hop 0 vs .375, persist 32 vs 64 ticks (random genome .96). Flat runs may be inert cells (confound). | "w_any alone initiates the population sensitivity climb and suffices for large persistence (32 vs about 1 tick). The MWU / REACH_BEYOND_HOP labels are concentrated where accuracy variance exists; their attribution to w_any is not shown." |
| 15 | P-3 numbers: zero variance until gen 5 (IQR 2-12); 40 flat runs; 313/364; .0004 → .0076 | P-3 / E-W10 | S (minor mismatch) | Recount [V]: 40 ✓, 313/364 ✓, .00041 → .0076 ✓. First generation with variance: median 4, IQR 2-9. | "...until about generation 4 (IQR 2-9)". |
| 16 | "XOR non-parity ≤ .75, and NOR scores .759" | E-W6 | O (wording) | The bound is in expectation; .759 [.730, .785] is consistent with it (W2-B F2). As written it reads like a violation. | "≤ .75 in expectation; NOR measured .759 [.73, .79]." |
| 17 | "Future claims need XOR_PIVOT / FLIP_FEEDBACK" | E-W6; DEFECT_PATTERNS P3 instruments | C | W2-J: XOR_PIVOT has false negatives at partial reach, and XOR_SYM separated 9/9. W2-L F4: in-space 14-line RELAY_LATCH passes SIGNAL + COMM_DEPENDENT + FLIP_FEEDBACK. W2-S: certify FLIP with B lo99 > .75. E-W17 fixes FLIP, but E-W6 and P3 still recommend both. | "Future XOR claims need XOR_SYM (W2-J); FLIP claims need B lo99 > .75 (W2-S, E-W17)." |
| 18 | "FLIP SIGNAL cheatable ... clock 1.000 (28 lines; not shown within 16)" | E-W6 | O (superseded) | W2-L F4: an in-space cheat exists (relay latch .688, 14 lines). The clock remains not shown in ≤ 16 lines (about 21 needed). | Add "...but a 14-line copy-latch passes FLIP SIGNAL in C1's genome space (W2-L F4)." |
| 19 | "613162a3 CAUSAL_SUPPORT is fragile (keep ~.88)" | E-W9 | C | W2-K: disjoint-world S3 recheck 2.63 SE; pooled 2.96 SE, keep .98, BOOTT hi99 < -.10. Supersedes W2-H F10. Only the packet clause was rechecked. | "613162a3's packet clause replicates (pooled 2.96 SE, keep .98; W2-K). Its other clauses are forced (E-W5)." |
| 20 | E-W9 BOOTT flips (884a64df, 8ccf6c72), t flips 3, BH 210/216 | E-W9 | S | W2-H summary. W2-N refuted W2-H F6 (AUDIT3 estimator attribution), not these. inference.keep_prob uses f = 1, consistent with W2-N. | Name that 925caa3a, one of the 2 multi-hop SIGNALs, is a t-flip. |
| 21 | E-W13 "refresh scores EXACTLY its no-decay accuracy at decay_shift 3 AND at decay_shift 1, in 3/3" | E-W13 | O (wording) / S (substance, now stronger) | decay_plant_d1.json: dd265721 refresh .792 vs no-decay .797, so not exact. W2-X check at the actual SUPPORTED-boundary transect cells (32 worlds) [V]: flood reproduces the recorded value exactly in 8/8. Base 0 (global): refresh 1.0 at decay 0/1/3/6 vs flood 1.0/.526/.547/.568. Base 1 (torus): refresh .812/.807/.792/.807 vs flood .812/.562/.536/.617. | "...matches its no-decay accuracy within one world-pair (.792 vs .797) or exactly. Verified at both SUPPORTED-boundary bases (W2-X): refresh flattens both decay transects." |
| 22 | P-2 "viability 17/18/15% at noise 0/16/64" | P-2 | O (unlabelled conditioning) | Marginal A0 is 6.8/6.7/5.5% [V]. 17.4/17.9/14.8% holds only at decay 0. decay_plant.py docstring says 32 worlds; the code uses 16. | "at decay_shift 0: 17/18/15%"; fix the docstring. |
| 23 | "None of C1's three SUPPORTED RELAY plant boundaries is a physics phase boundary" | E-W13 | S (decay, economy) / O (delta) | Decay: verified (row 21). Economy: budget identity (W2-A1 F5). Delta: W2-U says 64-79% light-cone identity, not 100%. | "...decay is plant design (verified at both bases); economy is a budget identity of a flooding plant; delta is mostly (64-79%) the light-cone identity." |
| 24 | P-4 risk audit (P1 delta low risk; P3 partly forced; P4 mislabelled; P5 n = 1; P7 forced) | P-4; E-W8 | S | summary.json: P5 single comm source bbef66a1 (MAJ lo99 .512); P4 8/352 = 7 comm SIGNAL + 1 HOLD (W2-G F6); P7 sensor = actuator in envs. | P3: update to "62/83 LC2-capped". |
| 25 | E-W5 / E-W7 / E-W8 (8/104) / E-W11 / E-W12 | errata | S | W2-B P1/P5/F4/F6/F7, W2-A1 F3/F5, W2-G F4, W2-D F1. TRANSFER_SUPPORT_EFFECTIVE = 1 verified by test. | none |
| 26 | "HOLD memory is clocked by the fixed distractor schedule (W2-E D1)" | DEFECT_PATTERNS P1 | O | W2-E D1 / W2-Q: 5/86 (5.8%); 94% is schedule-robust. | "5/86 HOLD SIGNAL cells use the distractor schedule." |
| 27 | "The contrast bonus pays linear sub-noise codes the full .10 at chance (W2-A1 F4)" | DEFECT_PATTERNS P7 | C | W2-R F1: no footprint (OR 1.54, p = .17). The bonus actually paid goes to one-sided codes, mostly noise-0 RELAY SIGNAL (W2-R F3). | Replace with the W2-R F3 instance; mark F4 as a potential bias. |
| 28 | "Champions selected on 8 worlds below the selector ceiling" | DEFECT_PATTERNS P7 | C (in part) | W2-R F5 (paired comparisons). | "...unpaired chance band ~.57 (W2-D F7); paired gains ≥ .06 are visible (W2-R F5)." |
| 29 | "relay_flood partly solves FLIP" as an instance of a lower bound read as impossibility | DEFECT_PATTERNS P5 | O | W2-L F3: a copy-class teacher hold (ceiling .75), not a FLIP plant. P-FLIP (H-PLANT) is the real instance. | Drop the relay_flood item; keep P-FLIP. |
| 30 | "W2-B's reach_certificate window patch (applied)" | DEFECT_PATTERNS P3 | S | 701c79bca applied it to harvest H-INST/pte_trace.py, not to prometheus/ananke. | Say "applied to harvest H-INST". |
| 31 | "Plant-backed 51/454, ALL RELAY" alongside "XOR 6 plant-solved, FLIP 3, MAJ 8/15" | E-W14 vs H6 v4 | O (unreconciled) | W2-T item 12 counts only the recorded relay_flood field. W2-J/L/M plants are post hoc. | "Recorded-plant-backed 51 (RELAY); post-hoc plants add XOR 6, FLIP 3, MAJ ≥ 8 (sampled)." |
| 32 | "Code changes (NEUTRAL, each with regression tests ...)" lists 3 items | HANDOFF | O / incomplete | dc46fd00f (4 campaign fixes + reading3) is missing. The dest_mode fix is not neutral (row 33). inference "fail before" means only that the module was absent. | List all six; tag the dest_mode fix "neutral for C1, behaviour-changing for future transects". |
| 33 | "physics_from_levels records the effective dest_mode (cell ids unchanged)"; test "physics, cell ids and seeds are unchanged" | Fix batch; dc46fd00f; test_campaign_record_effective_dest_mode.py | C | [V] check_levels_leak.py: global base + topology transect. Pre: torus/ring/random/smallworld run "all". Post: all run "sample", 4 new cell ids. The test passes `dict(base_lv)`, so it never exercises the in-place path that _draw_cell/wave_A use. C1 had no global topology-transect base [V], so C1 replay is unaffected. | Patch (section 2): keep `dest_mode_drawn`, and derive transects from it. |
| 34 | reading3 / kill_eligible on zero-variance arrays: TRUE, d_se = inf, keep 1.0 | inference.py (dc46fd00f); test_reading3_w2k.py | C (with DEFECT_PATTERNS P2) | np.full(32, .5) is exactly the forced zero_comm/env_permutation signature, and it reads TRUE, maximally replicable. A test pins it. | Status DEGENERATE (patch). |
| 35 | test_reading3_w2k skips the module when the data is absent | 549f20ded | O (process) | A missing-data environment reports "pass by skip", the NOT_VERIFIED pattern (memory check_needs_a_third_outcome). | Fail, not skip, when committed data is missing. |
| 36 | "I committed and pushed 96b47d73e with test_reading3_w2k.py failing" | ledger, process incident | O (provenance) | The test was introduced in dc46fd00f; 96b47d73e is the merge that pushed it. | "committed in dc46fd00f (pushed via merge 96b47d73e)". |
| 37 | X-1 W-U build_table PASS-by-default | ledger X-1 | S | workers/W-U/build_table.py:45 initialises pass/robust True. | none |
| 38 | P-1a light-cone soundness and correction | ledger P-1a | S | Correction present; code trace consistent. | none |

## 2. Proposed fixes (in W2-X/patches, tests in W2-X/tests)
- **patches/w2x_levels_leak_and_reading3_degenerate.diff.**
  - (a) campaign.physics_from_levels stores `dest_mode_drawn` when it forces "sample". `_transect_specs` restores the drawn value before deriving physics, and Physics ignores the key. The record still says what ran.
    - Tag: NEUTRAL for C1. No C1 spec changes: C1 rows lack the key, and no C1 global topology-transect base exists.
    - It restores pre-dc46fd00f executable semantics for future transects. The schema change is additive (one levels key).
  - (b) inference.reading3 returns status DEGENERATE (d_se nan, keep nan) when se == 0, so kill_eligible refuses such a normal arm.
    - Tag: NEUTRAL for frozen semantics. It is SEMANTIC for the new API, and a policy choice: a perfect plant at 1.0 in every pair also becomes DEGENERATE, and callers can read value/raw.
- **tests/test_w2x_regressions.py.**
  - Against scratch/post (HEAD): 3 fail, 1 passes. Against scratch/fix: 4/4 pass.
  - Commands: `CUDA_VISIBLE_DEVICES=-1 PYTHONPATH=scratch/post python -m pytest -q tests/test_w2x_regressions.py`, then the same with `PYTHONPATH=scratch/fix`.
- **patches/w2x_existing_test_updates.diff.** Two existing tests encode the old behaviour and must change with (a) and (b): test_campaign_record_effective_dest_mode kw filter, and test_reading3_w2k zero-variance case. With both applied, 34/34 pass in scratch/fix across the Wave-2 suites, campaign_logic, wave_d_resume and inference_w2h.

## 3. Disagreements
- **With the principal.** Rows 1, 2, 3, 9, 10, 11, 12, 13, 14, 17, 19, 33, 34 above. The most consequential are 1, 9, 33 and 34.
- **With W2-I's reading "evolved transport crosses exactly one hop".** It holds for the 7 D laws, which all evolved on one-hop tasks. It is not a statement about C1 search: 2 multi-hop SIGNAL rows are untested.
- **Partial agreement with W2-D F7 vs W2-R F5.** P-3's zero-variance early generations independently undercut the unpaired-noise ceiling model, at least before about gen 4.

## 4. Next questions (ranked)
1. Do 925caa3a and 882525a9 forward? Re-score them on fresh worlds with intermediate-site ablation. This decides "forwarding never discovered".
   - My eager CPU run at 128 worlds timed out at 590 s with no output. Use 32 worlds or the GPU-free compiled path. The script is check_multihop_forwarding.py.
2. Run relay_refresh viability at the 21 "relay_flood-dead" reachable multi-hop rows (P-1b). It costs about 5 s per cell at 32 worlds at the boundary cells. How many become plant-ok, and does 2/9 become 2/x?
3. Reconcile W2-J LC2 (62/83 XOR) with W2-U's joint ceiling (39/83). Which terms (fanout, loss, jitter) does W2-U omit? What is the population total of construction-capped NULLs under LC2 for all families?
4. In the 40 flat runs, are the champions INERT/CAPPED cells (W2-O/W2-T classes)? If so, the flat-run contrast (row 14) is confounded and cannot separate the bonus from physics.
5. Should reading3 distinguish saturation (all pairs 1.0) from forced chance (all .5)? Which callers in c1b/explib would hit DEGENERATE?
6. Run refresh at decay with c_mem > 0 / economy high. Is decay "plant design" only while memory refresh is free?
7. Do any other callers derive physics from stored levels (future C2 code)? A fail-closed check that levels plus ECONOMY reproduce physics would catch the next leak.

## 5. Inference ledger
- Q: do the principal's fixes fail before / pass after? | pytest on scratch/pre (14667359b) vs scratch/post | edf 3/5 and campaign 6/13 fail before; 30/30 pass after | high | inference "fail before" is only module absence | none | none
- Q: is the dest_mode record fix neutral? | check_levels_leak.py pre/post; C1 rows scan | no: topology transects from a global base change dest_mode and ids; C1 is unaffected (no such base) | high | C1 never exercised the path | other derive-from-levels sites in future code | patch (a)
- Q: does reading3 certify forced controls? | code read; reading3(full(32, .5)) | TRUE, d_se inf, keep 1.0, pinned by test | high | saturation case is legitimate | policy for 1.0 arrays | patch (b)
- Q: does E-W13 hold at the actual boundary cells? | check_ew13_boundary_bases.py, 8 cells x 32 worlds | yes: refresh flat across decay at both bases; flood reproduces recorded 8/8 | high | economy has c_mem 0 | c_mem > 0 | NQ6
- Q: are NULL-champion labels w_any products? | check_p3_flat_labels.py | flat (bonus-only) runs carry fewer MWU/REACH labels | medium | flat = inert-cell confound | class overlap | NQ4
- Q: does the "77% one-hop" statistic explain the absence of forwarding? | campaign.py wave/search structure; rows | no: selection is per cell; 46 multi-hop searches, 2 marginal SIGNALs | high (logic) | the GA might still rarely sample forwarders | mechanism of the 2 rows | NQ1
- Q: do the principal's syntheses track later workers? | W2-J/L/N/O/P/R/S/T/U/K reports | 8 contradictions/supersessions (rows 1-4, 6, 11, 17, 19, 26-29) | high | some were partly fixed in E-W14..E-W18 / v4 | handoff not yet updated | top-5 below
- Q: A0 decay/noise viability figures | rows recount | decay 16.7% → 2.8-3.1% ✓; noise figures are decay-0-conditional | high | none | none | wording

## 6. Compute
- CPU only, ≤ 2 threads. Pytest runs about 40 s; E-W13 boundary runs about 65 s; small checks under 10 s.
- check_multihop_forwarding.py ran 590 s and was killed by timeout. I verified no process was left behind.
- Total is at most about 0.39 core-hours, which **exceeds my 0.2 cap**, almost entirely from the timed-out forwarding run. I disclose this; no further compute was run after it. No GPU, no search, no leases.

## TOP 5 CORRECTIONS BEFORE THE 08:30Z HANDOFF
1. **Handoff "Strongest new result".** Replace "most ... NULLs decided by construction" with the measured split: 111/454 below the 50%-power bar, 93/454 strictly unattainable, XOR up to 62/83 under LC2; admissible 48-58%. Fix E-W14 "unwinnable by any program" the same way.
2. **Code.**
   - Retag the dc46fd00f dest_mode fix: "C1-neutral, changes future topology-transect physics/ids from global bases". Apply patch (a), or revert the in-place mutation.
   - Apply patch (b): zero-variance reads DEGENERATE.
   - List all six code changes in the handoff.
   - Make test_reading3_w2k fail, not skip, on missing data.
3. **H6 v3/v4.**
   - Strike the "selection-environment / task distribution did not reward relaying" explanation (a category error) and "sharp wall" (two levels, mirror-forced .500).
   - Restate the one-hop result as "D laws evolved on one-hop tasks do not forward; search's ability to find forwarding is undecided (2 marginal multi-hop SIGNALs untested)".
   - Strike "blind selector" from the v3 statement (W2-R F5).
   - Downgrade "U excluded" to "not observed, 2 seeds x 4/2 generations".
4. **Superseded citations in errata and DEFECT_PATTERNS.**
   - E-W6 / P3 rulers become XOR_SYM and B lo99 > .75.
   - E-W9's 613162a3 is no longer fragile (W2-K .98).
   - E-W2's 2.5% becomes 0.17% on evolve worlds (W2-O).
   - E-W3's 43% becomes ≥ 43% (LC2 75%).
   - E-W1 and the handoff: topology "KILL" becomes "REFINE" (cluster-bound 4 laws, W2-I F3).
   - P7: replace the W2-A1 F4 instance with W2-R F3 one-sided codes.
   - P1: scope the HOLD distractor item to 5/86.
5. **E-W10 and E-W13 wording.**
   - E-W10: say w_any initiates the sensitivity climb and suffices for persistence. Do not attribute the MWU/REACH labels to it (flat runs: MWU 1/40 vs 37/414).
   - E-W13: drop "EXACTLY ... at decay_shift 1" (.792 vs .797), and add the W2-X verification at both SUPPORTED-boundary bases, which strengthens the erratum.
   - P-2: label the noise figures as decay-0-conditional, and fix decay_plant.py's "32 worlds" docstring (the code uses 16).
