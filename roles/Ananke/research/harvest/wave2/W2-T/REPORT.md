<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-T; sha256(report)=d843838e38df7911; delimited; see REPORT.provenance.json -->
W2-T REPORT: W2-O's NULL admissibility checklist applied to the whole C1 NULL population
Worker W2-T (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-T/
CPU only, at most 2 threads per process (1 after a restart), eager evaluation. Every process ran under 10 minutes of wall time. No git writes, and nothing outside W2-T was edited.

## How the work was split

**Population.** Every C1 evolve row with held lo99 <= .55. I checked that this is exactly the set of rows with labels.SIGNAL false.
- XOR 83, FLIP 82, RELAY 146, MAJ 143: 454 cells.
- HOLD 58: 512 cells in total. HOLD fitted within the budget, so it was audited too.

**Sample split** (select_t.py, rng 0x57325454, fixed before any run):
- **25% random subsample per family, full guarded replay: 127 cells (113 in the 4 families, 14 HOLD).**
  - Held normal and zero_comm arms in one guarded() context, using W2-O's PATCHED guards (../W2-O/pte_mut; G12 judges only Worlds with ctrl "none").
  - Known-answer check on acc, lo99, hi99, zero_comm, comm_delta, comm_delta_lo99 and held_tel.
  - The FINAL-seed ranking evaluation in a second guarded context, with a known-answer check on champ_train_final.
- **The other 385 cells (341 in the 4 families): guarded NORMAL held arm only.**
  - Known-answer check on acc, lo99, hi99 and held_tel.
  - Guards G1-G5 and G9-G12. G0, G6 and G7 need a matched control and were not evaluated on these cells.
- **All 512 cells:**
  - direct G8 (held seeds against every train and final seed set);
  - engagement (readout-dead worlds, emitting worlds, twin-blind pairs);
  - per-half per-trial accuracy (the TRUNCATED test);
  - reachability;
  - exact wake recomputation compared with the engine's stats["awake"];
  - a NEW combined light-cone + wake bound on the held worlds (lcwake.py);
  - FLAT (curve max_acc);
  - the recorded plant.

So the "cheap" checks were in fact run on every cell, together with a guarded normal-arm replay. Only the control arm and the final-seed evaluation are subsampled.

**Files** (all in W2-T/):
- Scripts: select_t.py, audit_t.py, lcwake.py, summarize_t.py, trunc_probe.py.
- Outputs:
  - out/cells.json;
  - out/audit_b0{0..7}of8.jsonl: per-cell replays;
  - out/lcwake_null_b{0,1}of2.json and out/lcwake_sig_b0of1.json;
  - out/table_t.json: every row plus the summary;
  - out/admissible_cells.tsv;
  - out/trunc_probe.jsonl;
  - out/compute_ledger.json.

**Class rules** (summarize_t.py; first match wins, in W2-O's order):
- **BROKEN:** any of: a gate fails; a break guard fires (G1-G5, G7, G9, G10, G11, held or final); a direct G8 overlap; the wake recomputation differs from the engine.
- **TRUNCATED:** G12 fires on the normal arm AND the first-half per-pair lo99 is above .5.
- **CAPPED:** combined bound < .60. Cells between .60 and .75 are flagged MARGINAL.
- **DEGRADED:** at least 1 held world has no sensor-to-actuator path.
- **INERT:** at least 48/64 worlds are readout-dead.
- **FLAT:** max_acc over all generations <= .5.
- **ADMISSIBLE:** none of the above.

## 1. PER-FAMILY TABLE (exclusive classes)

| family | n | BROKEN | TRUNC | CAPPED | DEGR | INERT | FLAT | ADMISSIBLE (of which MARGINAL) | strict ADM | adm frac strict / lenient |
|---|---|---|---|---|---|---|---|---|---|---|
| XOR   |  83 | 0 |  0 | 35 | 0 | 14 | 4 |  30 (9)  |  21 | .253 / .361 |
| FLIP  |  82 | 0 |  0 | 24 | 0 |  5 | 1 |  52 (1)  |  51 | .622 / .634 |
| RELAY | 146 | 0 | 11 | 17 | 0 | 23 | 2 |  93 (1)  |  92 | .630 / .637 |
| MAJ   | 143 | 0 |  1 | 31 | 1 | 22 | 1 |  87 (32) |  55 | .385 / .608 |
| **4 families** | **454** | **0** | **12** | **107** | **1** | **64** | **8** | **262 (43)** | **219** | **.482 / .577** |
| HOLD  |  58 | 0 |  0 |  0 | 0 |  6 | 0 |  52 (0)  |  52 | .897 / .897 |

- The lenient fraction for the 4 families has a 95% Clopper-Pearson interval of [.530, .623].

**BROKEN rate:**
- Full guarded replay: 0/113 in the 4 families, 95% CI [0, .032]. Including HOLD: 0/127.
- Per family: XOR 0/21 [0, .161]; FLIP 0/20 [0, .168]; RELAY 0/36 [0, .097]; MAJ 0/36 [0, .097]; HOLD 0/14 [0, .232].
- Partial replay on the other 385 cells: 0 failures. That replay checked the gate on acc/lo99/hi99/tel and guards G1-G5 and G9-G12.
- Across all 512 cells:
  - 0 known-answer failures (largest telemetry deviation 1.2e-7, float32 state_nonzero and energy_frac);
  - 0 final-gate failures;
  - 0 wake-recompute mismatches;
  - 0 direct G8 overlaps;
  - 0 cells where the zero_comm arm delivered a packet.

**Flags (non-exclusive, 4 families, n = 454):**
- capped 107; inert 100 (22%); flat 49 (this reproduces W2-O's 49); degraded 5 (all MAJ random); marginal 53.
- 230 cells were selector-invisible (max_acc < .57); 84 of the 262 ADMISSIBLE cells are among them.
- G12 fired on the normal arm in 44 cells.

**Guard alarms:**
- Full subsample, held block: G0 113/127, G6 21, G12 11.
- Normal-arm-only cells: G12 34.
- Final-seed evaluations: G12 9.
- No break guard ever fired.

## 2. ADMISSIBLE CELLS (262 in the 4 families + 52 HOLD)

The full IDs are in out/admissible_cells.tsv. That file also gives held acc, combined bound, MARGINAL, plant acc, max_acc, dead worlds and the replay mode for each cell. Below are 12-character prefixes; * marks MARGINAL (bound .60-.75).

XOR (30): 0e99a4bb1e4f 11252d52dc5e 141c4310f907* 17dd70fa5b2d 1916d8e9d757 1974a9cf7f8e 247e0d4372d0* 2b867f4fdd99 333d6b2b2ac2 4222a5f77275 4ca24b85ab9e 4e7f932f0d32* 51fa3ee07912* 667bb9bd63ff* 74f96e8958d1* 7a16eddd4f87 a0edfda5e3bc ab3e72d3e277 abb5fb8178ef* aee70c906ff1 cc5f54069b85 cd613e2b067c d2b8816cb6e8 d64656f26736* e2fd1e07df85 e3fb8737eac5 e7d6ccb0f59e efc6f7c37ec6 f8f95cc439f5 fafa4580821d*

FLIP (52): 05fea1b55336 06e99bf21c0a 07bde99b2b98 0ad0988d7b7e 124923338e43* 158bdd9a1264 17b093a78864 221042948e32 299a681d2e3c 2aefc9fef958 394743d78562 3f78ee89d5d6 50060cf95d2b 56cdba0a6c46 5fbaa2ecc698 64d33b898116 6e8fb3bb64c1 6f82f9c7d51b 75e32ae0d386 79bc73b022e5 7b6b7f6958c4 7da1d985912e 891dbf32ca70 964053bb4c90 996716ac46f7 9b47d5378f2c 9d67b5635469 a467c0f81468 ba09f3510be6 bda1a1bf2f3a bfa85a55ee67 c5bceddafac4 c9998fe48f93 cabf14291d28 cc9858540c52 cdc9405d347c d09510b3e567 d3f360068a9a d8bcfce07262 d957d95c3a86 d99833cbd7fa e0c6650c66aa eb076f0d822f ebdbe504129f ec89b3d5b8bd f3e99f332406 f476a3cac974 f4e59e6154ea f53a428a92d4 f6cfdf8240aa f867ff454ef2 fc6972d4930e

RELAY (93): 004b051f6154 056d8e0d3a27 07528af06af6 0e7bb02afcc5 12f7f754e3af 14176fce145a 14f5aac89196 15148d69a974 1d64df5ab275 217fc391f1da 253c106e5f21 25a07dbfd388 2af2583be34a 2c6a95479502 3222a6ff4228 3916a19df8b4 3a9073efb66f 3d7b5ccf1238 3d8d3070a1a9 3e627a008485 405e5c5621e7 415b054a7a93 42a75ad4057f 446db43c86b7* 46da8a020f53 4c367b91d6ff 51942344d4e4 52a9a36a446e 59f1df762233 5b394e515e7a 5b7e399542f1 5c21db9edbe9 5ccd25c1161b 5de88012804a 5dfc4ca0e25f 61e15583141a 666bdeaec27c 66b7727e3f8d 66c1d67a17ee 679284c6eee6 6b91d25afff6 6e22f6730608 6ecee4860f23 6f9fb4125e5b 70d9709ee525 726a2b4f9375 7b6c7047d8b8 7b9698f16303 7bf8c5e4a326 7e370212c4e8 7f149dc0df53 828fde314ac2 88a05b4b52f7 89a1f99066fa 89bd6fdb1b66 8cb1e962f96d 94ced72f76bb 9a5c2c46c1f4 9a63f82aefc9 9b34c3c5bde8 9d4027897dce a168243cdfce b0da5696e43e b52c4c30e242 b6a1e13a5f39 b79587f9b01d b8bc699c94d5 b8f9309a74dc bbf2ebab0e14 bf10f055f012 bf34b65cb695 c3d2d69751b1 c570eb98ddb3 c65e4c9ccdb5 c93d420fa500 cb4204e706f1 cb70c3968e96 d4bd91153a91 d660b97aa884 d90dc92f9d98 dee9d363bf73 e4600b4ede46 e63b968f414f e846beb49302 ebb078eb3e54 ee4a2674f0f8 f4f208bb8015 f81c6edd8468 f822f93985e2 fa692af8df50 fc08ea851044 fda98c541782 ff3cbd2c5235

MAJ (87): 02662a50ce19 057941f350d5* 070257d7a8c0 070bdcea3347 074166b9942c 083fde9f3fbb* 08d8f0c51f1c* 093eebedddab 0f1969774985* 11fb94dd01b3 13a086e911f0 1448cd7d2eba* 15e58864edb1* 199b4cc61fc9* 1c12d5607f4f* 1d5988cd8b12 23585a9c08c3 266dd0605e3e 266f35840cc7* 2bf1839353c5 2e80387accc9 2eefc45b9add 308d6488ba12* 32c3fba3d353* 377640d2c293 3a2f01523a2b 3d20243abaf7 3dfdd7145e6e 3f548f988775* 3fd0dbcd7460 423d8365d368* 437ca0ac6ccc 4512732fbf24* 45d695e0b31d* 488b426bb05c 48dbe2a19003* 493a85d25c9c 514b30bd91e6 52215437c9e2* 528879c08ea8 575be1c957db 57c0009092c8* 59834a01e883 5ace0dc811eb 5c35b832e128 612db08fdf75 61fcdc37fa1f 66d9101b9e96 68962f19cd2f 6b602a194314* 6c5608770a7b 6dd65b5afd66 6e0ca7255b6b 772ae210dada 7e2affed17ce* 8051dc5ec4d7 839b39c79ec6 87216808c80c 8a6454f096d7 8b1626389a34 8c5eba065b98* 8ee21e1c33f0 937703a8f426* 99cef8e68ad5 a4a70e029836 a56b60ba6e51* a5c7b8e00575 a8b007fe525f aad7e1b3cf8e ab0a4290d681* acf58f3434a3 bb1ab84c2e00* bf1f3a100b29* c95282846851* cae5c670a976* cd9620ef015c d606cb4e7dac* db507824a3d5 de8665867394* e0202dc0e24c e163e9ea07ec e5dfac9b5c34 f0645585b056 f22be86f17b8* f29ca123a2be f74f80d1f3fb fc9a57cafac8*

HOLD (52): 014118749844 0fa41a3ec06f 194b3be3fae8 28d5cb331bae 388905bb7ed0 3c0ea627ab69 3eb81c1cf7f2 413feb811883 427faaa3db10 4442b1d058a8 46fc241e08c9 4a760c6e88f0 4e35e77672f4 5124b22c3f73 52dafed3808b 5358736c4b50 60eb17381435 618d4e586b37 6597c043ddd0 6bca6faa6bf1 6c48a6492da6 6d2571cda44d 6f36069476c2 71e6b06eece5 7b939a4224fa 85da1114ebc4 90674379a02e 920bbd5a9a1b 95c36dd27a4c 9e0a342f0883 ac9281358f72 ace4b5999e62 b0b440ebff79 b87aa64f1a82 bc0ef6a1ee68 c0244972f975 c09951f4bf41 c2bbc9d84715 c5e3a645e418 c7c60c428afd ce12e730e642 cf137b446c25 d6bfd83ad1df d8e7e83026b1 e544cd3fc32b ebaea8aa631a f355264a0ac4 f4ed42fe34bf f60ed5d12e03 f694455c7f47 f7613ec4bb78 ffbdec400153

TRUNCATED (12): 0dcdb6698519 2c141a10588d 2d0a16a809c1 362815f90811 3e88548b43f5 5bb3fd92c5d9 8282d70e914c adecce567dec cbbfc88c2344 dbd5c558656a e8b67ccee08d (all RELAY) and c959e1a2de65 (MAJ).

DEGRADED (1, exclusive): 14e62ff559e4 (MAJ).

## 3. COMBINED LIGHT-CONE + WAKE BOUND

**What lcwake.py computes:** H-PLANT's light cone with one change. The async wake rule "could wake any tick" is replaced by the engine's exact per-site per-tick WAKE mask. Other semantics:
- SENSE is not latched (engine step 2).
- The inbox does latch while a site sleeps (step 1 accumulates into Acc_sum and Acc_cnt; they are cleared only on an awake tick).
- MAJ uses the Bayes ceiling of majority-of-received-sensors.

**Cells H-PLANT bounds at 1.0 (on its own seeds) that drop below .75: 3 of 210 on held worlds, 5 of 210 on H-PLANT's seeds. None drops below .60.**
- XOR 1/28 (3/28 on H-PLANT's seeds); FLIP 0/57; RELAY 2/125.
- Lowest combined bound: XOR .741, FLIP .811, RELAY .628.

**Any cell whose optimistic cone is ≥ .75 but whose combined bound is < .75:** XOR 3, FLIP 0, RELAY 2, MAJ 30.

**Newly CAPPED** (optimistic cone ≥ .60 but combined < .60): XOR 3, MAJ 2. Every other CAPPED cell is already capped by the timing light cone alone.

**MAJ, which H-PLANT's census never covered:**
- 74/143 MAJ cells reach the full-information ceiling under the optimistic cone. Of those, 23 drop below .75 with exact wake.
- Overall, MAJ combined bound < .75 in 69/143 cells and < .60 in 31/143.

**Size of the wake effect:** on async cells the bound drops by about .01-.04 at update_p .8 and by .11-.37 at update_p .5.

## 4. DENOMINATOR FOR H6-TYPE CLAIMS

Of the 454 C1 NULLs in the 4 families:
- **Strict: 219/454 = 48.2%** are admissible for any search-limitation reading (MARGINAL excluded).
- **Lenient: 262/454 = 57.7%**, 95% CI [.530, .623].

By family (strict / lenient):
- XOR 25% / 36%;
- FLIP 62% / 63%;
- RELAY 63% / 64%;
- MAJ 38% / 61%. MAJ is the family most sensitive to the margin.

**With checklist item 12 applied** (a plant inside the genome space at the cell is needed before an S/U attribution):
- **Only 51/454 = 11.2% qualify, all of them RELAY.**
- Two further RELAY cells have a plant only at prog_len 12 on a genome with prog_len 8, so the plant lies outside the genome space.
- There is 1 FLIP cell where relay_flood scores .6. That is not a FLIP solution.
- XOR, FLIP and MAJ have no task-solving plant recorded: the recorded plant is relay_flood in every case.
- HOLD: 52/58 admissible, but only 30 have a hold_latch plant at the cell's own prog_len.

## 5. FINDINGS
(Each finding has a tag ([V] verified by me with a check, [I] inferred), a confidence, the strongest objection, and what remains unresolved.)

**F1 [V, high]. The C1 NULL population is not broken.**
- Full guarded replay: 0/113 (95% upper bound 3.2%); 0/127 including HOLD.
- 0/512 on the partial checks (gate, guards G1-G5 and G9-G12, G8, wake recomputation, zero_comm leakage).
- Checks: `python audit_t.py <i> 8` for i = 0-7, then `python summarize_t.py`.
- Objection: the guards cover only the corruptions they model (no randomize_source guard; G11 counts at emission). The search generations were not re-run.
- Unresolved: whether a bug present in both the recording run and the re-run would reproduce silently.

**F2 [V, high]. The combined bound is valid and tight.**
- Self-check: in exact-wake mode "opt" it reproduces H-PLANT's lc_census exactly in 60/60 cells (`python lcwake.py selfcheck`). That set includes 20 cells with bound < .9.
- Negative control: no recorded SIGNAL has held acc above its combined bound (0/166; `python lcwake.py signal 0 1`).
- Real champions come close to the bound: HOLD .945 against .978, MAJ .695 against .731.
- 29 NULL cells have held acc a little above their bound. All of them have bound exactly .5 and held lo99 < .5 (largest excess .023), i.e. chance fluctuation around an expectation bound.
- Objection: the bound is optimistic. It ignores energy, caps, loss, the R-port limit and, for FLIP, the teacher. So it is an upper bound, never an achievability claim.

**F3 [V counts / I reading]. Wake loss converts only a handful of uncapped comm cells.**
- Of the 210 XOR/FLIP/RELAY cells H-PLANT bounds at 1.0, 3 drop below .75 and none below .60.
- Nearly all of the physics cap in XOR, FLIP and RELAY comes from H-PLANT's timing cone.
- The real new information is in MAJ, which was never light-coned: 31/143 cells are CAPPED and 32 more are MARGINAL.
- MAJ also has a hard information ceiling of .837 even with perfect information (flip_p .3, n_maj 5 in all 162 MAJ rows).
- Objection: the .60 and .75 thresholds are conventions. I report both.

**F4 [V, high]. "TRUNCATED" cells are early-latch champions, not truncated measurements.**
- trunc_probe.py covered the 11 RELAY cells and 1 MAJ cell.
- First-half per-trial accuracy is .55-.58; second-half accuracy is about .50.
- The readout last changes at a median tick of about 1-43 out of 228.
- The schedule is live in both halves (12/12 cue ticks each). Economy is "off" and energy stays at 1.0 in every RELAY case. Emissions continue.
- So this is not energy death (W2-O's 89bd6fdb mechanism). The champion answers the first one or two trials and then freezes its readout.
- These are search near-misses with real single-shot competence. They are not evidence that search found nothing.
- Objection: c959e1a2 (MAJ, .513 against .500) passes the lo99 > .5 test only narrowly, and it is also INERT.

**F5 [V]. Engagement and FLAT descriptors over the population.**
- INERT flags on 100/454 cells (22%). FLAT flags on 49/454 (10.8%, the same as W2-O).
- 230/454 cells are selector-invisible (max_acc < .57), including 84 of the 262 ADMISSIBLE cells. In those 84, any competence was invisible to selection.

**F6 [V]. Reachability.**
- DEGRADED (some held world has no sensor-to-actuator path) applies to 5 MAJ random cells only.
- My counts agree with W2-O's reach census in every cell (0 mismatches).
- Only 1 of the 5 is DEGRADED as its exclusive class; the others are already CAPPED or INERT.

**F7 [V]. The W2-O sample was representative.**
- My reclassification of W2-O's 16 cells matches theirs, except that MAJ c9d2ff6e is now CAPPED (MAJ cone .524) and MAJ 0327a9ab is MARGINAL.
- W2-O's 8/16 admissible sits inside my CI.

## 6. PROPOSED FIXES
- NEUTRAL, instrument only: lcwake.py is a drop-in, exact-wake extension of H-PLANT lightcone.py, with a self-check against lc_census and a SIGNAL negative control. I propose it as the standard bound for checklist items 7 and 8. No diff is needed, because nothing existing was modified.
- SEMANTIC, but only for the checklist: rename W2-O's class TRUNCATED to LATCHED-PARTIAL. The class is still inadmissible as a "found nothing" NULL. However, it should count as evidence that search reached partial competence, not as an instrument artifact.

## 7. DISAGREEMENTS
- **W2-O F5** ("ceilings stay above the SIGNAL bar, so none CAPPED"): when wake is combined with the cone, 5 more cells drop below .60 (3 XOR, 2 MAJ). The overall effect is still small for XOR, FLIP and RELAY.
- **W2-O checklist A4:** a G12 alarm with an above-chance first half is a latch champion (F4), not a truncated measurement. Of 44 normal-arm G12 alarms, 12 meet the first-half test.
- **H-PLANT lc_census:** it is computed on SCORE_NS worlds, not on held worlds. The two agree within .02 in 290/311 cells; a per-cell bound should use the held seeds. MAJ and HOLD are not covered at all.
- **Item 12 in practice:** the recorded "plant" is relay_flood for XOR, FLIP and MAJ, so it certifies nothing about those tasks. It is also evaluated at prog_len max(L, 12), which puts it outside the genome space for prog_len 8 (2 RELAY cells, 22 HOLD cells).

## 8. NEXT QUESTIONS (ranked)
1. Build task-solving plants for XOR, MAJ and FLIP at each cell's prog_len. Without them, 0% of those families can support an S/U attribution.
2. LATCHED-PARTIAL RELAY (11 cells): does a 10x budget, or an objective that rewards later trials, turn them into SIGNALs?
3. For the 84 ADMISSIBLE but selector-invisible cells, would M = 32 training worlds expose the gradient?
4. Make G12 tell a latch from a freeze: test per-trial accuracy by quarter and require the schedule to be live.
5. Add energy, cap and R-port limits to lcwake for a tighter (still valid) bound. How many MARGINAL MAJ cells fall below .60?
6. Random-genome 10x screen on the 49 FLAT cells: are they search-starved or effectively unreachable?
7. Re-run the full control arm on the remaining 75% only if a new guard (randomize_source or inbox provenance) is added.

## 9. INFERENCE LEDGER
(question | evidence | result | confidence | strongest objection | unresolved | next)
- Are C1 NULLs broken? | full guarded replay on 113, partial on 341 | 0/113 (CI ≤ 3.2%); 0/454 partial | high | guards cover modelled corruptions only | search generations not re-run | Q7
- Is the combined bound valid? | 60/60 lc_census exact; 0/166 SIGNAL violations | valid, tight | high | ignores energy and caps | tighter bound | Q5
- How many lc = 1.0 cells drop below .75? | lcwake on held and SCORE seeds | 3/210 held (5/210 SCORE); 0 below .60 | high | threshold conventions | MAJ dominates | -
- Is TRUNCATED a measurement artifact? | trunc_probe: schedule, energy, emissions, per-half accuracy | no; early-latch champions | high | n = 12 | latch prevalence below the test | Q2, Q4
- What fraction of NULLs is admissible? | checklist on 454 | 48.2% strict / 57.7% lenient | high | MARGINAL boundary | plant gap | Q1
- What fraction is plant-backed? | recorded plants | 11.2% (51 RELAY) | medium | plant evaluated at 32 worlds, mean only | XOR/MAJ/FLIP have none | Q1

## 10. COMPUTE
- About 4,360 CPU-s, about 1.21 core-hours, against the granted 1.5. Breakdown in out/compute_ledger.json.
  - audit: 3,453 s recorded, plus about 150 s for a killed first round and imports;
  - lcwake: 474 s on NULL cells, 191 s on SIGNAL cells, about 20 s self-check;
  - trunc probe: about 45 s;
  - timing probe: 28 s.
- The first round ran at 2 threads on a saturated host. I restarted at 1 thread to stop OMP spin waste; the restart resumed from completed cells.
- CPU only (CUDA_VISIBLE_DEVICES=-1, asserted), eager, every process under 10 minutes of wall time. No leases touched, no git writes, nothing outside W2-T edited.
