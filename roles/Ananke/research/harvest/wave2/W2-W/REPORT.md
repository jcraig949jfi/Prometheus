<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-W; sha256(report)=b9b4fe0b8c6a71a2; delimited; see REPORT.provenance.json -->
W2-W REPORT: one placement table for the 454 C1 NULL evolve cells (plus 58 HOLD), merging every Wave-2 classification
Worker W2-W (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-W/
CPU only (CUDA_VISIBLE_DEVICES=-1, cuda asserted unavailable), 2 threads. No git writes. Nothing was edited outside W2-W.

## 0. Files

**Scripts** (they run in this order):
- collect.py → out/labels.json. Every source label for each cell, read from saved out/ files only.
- classify.py → null_placement.csv, out/placement.json, out/summary.json.
- contradictions.py → contradictions.csv.
- refresh_check.py → out/refresh_check.json. This was the only engine run; it resolves contradiction C7.

**Deliverables:**
- null_placement.csv: 512 rows (454 NULL plus 58 HOLD) and 52 columns.
  - One label column per source: hplant_lc, w2d_tags, w2j_*, w2l_class, w2s_*, w2m_*, w2p_*, w2u_*, w2t_*, w2o_class, w2i_verdict, w2q, p1b, p2_decay_artefact, rec_plant*, w2w_refresh.
  - The merge: plant_tier, best_bound and its source, final_class, final_basis, admissible, eligible_strict, eligible_lenient, evidence_path.
- contradictions.csv: 271 rows (one per cell and contradiction id), covering 186 distinct cells.

**Population.** The population is W2-T's: every evolve row with held lo99 ≤ .55. This is the same set as labels.SIGNAL false. XOR 83, FLIP 82, RELAY 146, MAJ 143, HOLD 58.

## 1. Final classes and rules (classify.py; first match wins)

Two terms used throughout:
- **Certificate:** a sound upper bound on any program's accuracy whose sampling error is controlled. The accepted certificates are:
  - W2-T combined light cone plus exact wake, on the held set;
  - W2-U joint ceiling, on 1024 worlds and on the held set;
  - W2-J LC2, using its 99% CI upper end;
  - W2-S epidemic bound (analytic);
  - W2-M k-sensor light cone, on the held set.
  
  H-PLANT and W2-P are not used as certificates, because W2-U reproduces them exactly and supersedes them (165/165 and 25/25 cells).
- **Plant tiers** (thresholds as in each source): IN_SPACE fits the row's own sampled genome; OVERRIDE fits C1's genome space (16 lines or fewer) once the row's genome fields are raised; BEYOND_C1 needs more than 16 lines.

The rules, in order:
1. **CONSTRUCTION_PLACEMENT:** a W2-P placement-only MAJ row. The inward ceiling must clear .614 even after subtracting the gap between W2-P's model and the tightest certificate.
2. **P_PROVEN:** the minimum certificate is below .60.
3. **LATCHED_PARTIAL / INERT / FLAT:** the W2-T exclusive class (W2-T TRUNCATED was renamed LATCHED-PARTIAL).
4. **PLANT_SOLVED_IN_SPACE:** a task plant that fits the row's own sampled genome.
   - FLIP: W2-L PLANT-SOLVED.
   - MAJ: W2-M PLANT-SOLVED, strict or weak.
   - RELAY/HOLD: recorded relay_flood or hold_latch with acc ≥ .60 at the row's own prog_len.
   - RELAY: the W2-W relay_refresh check with acc ≥ .60 and lo99 > .55.
5. **PLANT_SOLVED_OVERRIDE:** a plant inside C1's genome space (16 lines or fewer), but only after raising the row's genome fields. Cases:
   - W2-J's 16-line plants with lo99 > .55;
   - RELAY/HOLD plants that need prog_len 12 or 16 where the row has 8 or 12;
   - MAJ c7ec8097 (INT_2 at 14 lines, lo99 .636).
6. **R_CANDIDATE:** the only plants found need more than 16 lines (W2-S's 9 FLIP rows; XOR 84cf905d, but that cell is INERT).
7. **PLANT_DESIGN:** W2-S economy rows.
8. **P_CANDIDATE:** any of these:
   - W2-S plant-relative timing/loss rows;
   - a bound in [.60, .614), the 50%-power SIGNAL bar;
   - a W2-J LC2 point estimate below .60 whose CI straddles .60.
9. **UNDECIDED:** everything else.

H6 denominator definitions:
- eligible = admissible (W2-T ADMISSIBLE or DEGRADED) AND PLANT_SOLVED_IN_SPACE. "Strict" also excludes W2-T MARGINAL cells.
- physics-capped = P_PROVEN + CONSTRUCTION_PLACEMENT.
- open = the rest.

## 2. PER-FAMILY COUNTS (final_class)

| class | XOR | FLIP | RELAY | MAJ | 4 families | HOLD |
|---|---|---|---|---|---|---|
| P_PROVEN | 59 | 31 | 17 | 27 | **134** | 0 |
| CONSTRUCTION_PLACEMENT | 0 | 0 | 0 | 5 | 5 | 0 |
| P_CANDIDATE | 3 | 12 | 0 | 2 | 17 | 0 |
| LATCHED_PARTIAL | 0 | 0 | 11 | 1 | 12 | 0 |
| INERT | 7 | 5 | 23 | 21 | 56 | 6 |
| FLAT | 2 | 1 | 2 | 1 | 6 | 0 |
| PLANT_SOLVED_IN_SPACE | 0 | 3 | 54 | 8 | **65** | 30 |
| PLANT_SOLVED_OVERRIDE | 4 | 0 | 3 | 0 | 7 | 22 |
| R_CANDIDATE | 0 | 9 | 0 | 0 | 9 | 0 |
| PLANT_DESIGN | 0 | 7 | 0 | 0 | 7 | 0 |
| UNDECIDED | 8 | 14 | 36 | 78 | 136 | 0 |
| n | 83 | 82 | 146 | 143 | 454 | 58 |

## 3. THE DENOMINATOR TABLE A FUTURE H6 CLAIM MUST USE

| | XOR | FLIP | RELAY | MAJ | **4 families** | HOLD |
|---|---|---|---|---|---|---|
| n NULL | 83 | 82 | 146 | 143 | **454** | 58 |
| search-limitation ELIGIBLE, strict (admissible, not MARGINAL, in-space plant) | 0 | 3 | 54 | 5 | **62 (13.7%)** | 30 |
| eligible, lenient (MARGINAL allowed) | 0 | 3 | 54 | 8 | **65 (14.3%)** | 30 |
| PHYSICS-CAPPED (P_PROVEN + CONSTRUCTION_PLACEMENT) | 59 | 31 | 17 | 32 (5 placement) | **139 (30.6%)** | 0 |
| OPEN | 24 | 48 | 75 | 103 | **250 (55.1%)** | 28 |
| of which P_CANDIDATE (probably capped, not proven) | 3 | 12 | 0 | 2 | 17 | 0 |
| of which inadmissible (INERT / FLAT / LATCHED_PARTIAL) | 9 | 6 | 36 | 23 | 74 | 6 |
| of which a plant exists, but not in the row genome (OVERRIDE / R) | 4 | 9 | 3 | 0 | 16 | 22 |
| of which PLANT_DESIGN / UNDECIDED | 8 | 21 | 36 | 78 | 143 | 0 |

- The eligible cells are:
  - FLIP: 6f82f9c7, 996716ac, 64d33b89;
  - MAJ: 070257d7, 13a086e9, 3d20243a, 437ca0ac, 8051dc5e (strict); 1448cd7d, 15e58864, 48dbe2a1 (MARGINAL);
  - RELAY: 54 cells, listed in the CSV.
- 4 of the 8 MAJ cells are W2-M "weak" (post-hoc INT_LEAK, or integration not shown).
- 12 further cells have an in-space plant but are inadmissible: 11 LATCHED_PARTIAL RELAY plus 2682069a (INERT).
- Eligibility is a denominator only. It is not evidence for S. W2-D's F-U, F-V and F-S tests still have to be met per cell.

## 4. CONTRADICTION LIST
Every row is in contradictions.csv. Here they are by id, with resolutions.

**C1. Cap counts: W2-P/W2-U 111 vs W2-T 107 vs W2-J XOR 62 vs final 139.** [V] (36 cells)
All four numbers are correct for their own definitions:

| source | rule | XOR | FLIP | RELAY | MAJ | total |
|---|---|---|---|---|---|---|
| W2-P / W2-U | light cone + async cue loss + actuator wake, joint < .614/.628, 1024 worlds | 36 | 24 | 17 | 34 | 111 |
| W2-T | light cone + EXACT wake mask + intermediate-relay wake, < .60, held set | 35 | 24 | 17 | 31 | 107 |
| W2-J | LC1 (H-PLANT) + LC2 (fanout, per-copy loss, sensor wake, dup, jitter), < .60 | 62 | – | – | – | – |

Reconciliation:
- **W2-U 111 → final 139:**
  - 3 come out: MAJ 937703a8, 45d695e0 and 8c802392 have a ceiling of exactly .600, which is below .614 but not below .60. They become P_CANDIDATE, P_CANDIDATE and INERT.
  - 31 go in:
    - 23 XOR via W2-J LC2;
    - 7 FLIP via the W2-S epidemic bound;
    - MAJ f1bd05cd: W2-T .550 against W2-U .627. W2-T is tighter because it requires intermediate relays to be awake (a real engine constraint), and W2-P assumes they fire on arrival.
- **W2-T 107 → 139:** +24 XOR (21 LC2-only, plus d64656f2, c83ce615 and fafa4580 via W2-U at 1024 worlds), +7 FLIP epidemic, +1 MAJ 0327a9ab (construction placement at .605).
- **W2-J 62 → 59 P_PROVEN:** W2-J's 3 CAPPED-LC2(point) rows have 99% upper ends of .602, .603 and .638. Final classes: ab3e72d3 and d2b8816c P_CANDIDATE; 74a24d53 INERT.
- **"36 XOR capped" vs "62":** the difference is definitional. W2-P and W2-U omit fanout, per-copy loss and jitter. Global rows with fanout 1–2 drop from a light-cone bound of 1.0 to about .50 under LC2.
- **Sensitivity:**
  - with only the light-cone family of certificates (W2-T/W2-U/W2-M): XOR 38, FLIP 24, RELAY 17, MAJ 31;
  - P_PROVEN at a best bound ≤ .55 (strict impossibility): XOR 50, FLIP 25, RELAY 16, MAJ 25.
- **Basis split (7 cells; certificates agree on capped, but the held and 1024-world bounds fall on different sides of .60):** c83ce615, cd1b61b5, d43ef071, d64656f2, fafa4580 (all XOR), 0677e0ae and f1bd05cd (MAJ). I kept the any-sound-certificate rule. Each cell's basis is in best_bound_src.

**C2. H-PLANT lc_census against the final cap, 31 cells (23 XOR, 7 FLIP, 1 RELAY).**
- XOR membership against W2-P (which used H-PLANT): 797c8957 and d43ef071 drop out of W2-U, and e1fc5118 and 73d733c5 come in.
- Final: all 4 are P_PROVEN.
  - 797c8957: LC2 upper .587.
  - d43ef071: held-set bound .594 (W2-T and W2-U agree).
- 312b5cf6, which W2-J F7 flagged as "not robustly capped" at 64 fresh worlds, is capped by W2-T (.570) and by W2-U at 1024 worlds (.589).
- RELAY de5ad87b is outside H-PLANT (.609) but inside every other source (W2-T below .60).

**C3. W2-P "placement-only" (6 MAJ cells).**
- Five stay CONSTRUCTION_PLACEMENT: e41b7b13, 5edb4474, 09c6dc85, 699c8b2a (inward .73–.82) and 0327a9ab (.670).
- 0677e0ae becomes P_PROVEN. Its inward margin over .614 is .005, smaller than the .032 gap between W2-P's model and W2-T's exact-wake bound (.605 vs .573).

**C4. A plant exists but W2-T calls the cell inadmissible (18 cells).**
- XOR 48256f59 (16-line override plant lo99 .751) and 84cf905d (37-line plant) are W2-T INERT.
- 11 LATCHED_PARTIAL RELAY cells have in-space relay_flood at .63–.98.
- MAJ c7ec8097 is INERT.
- 4 more RELAY INERT cells have plants: 2682069a in space; 21b64fd1, 8d5ba838 and 9a7a6f57 by override.
- Kept inadmissible per the W2-O checklist. They are reported as a separate tier in s3.

**C5. W2-L vs W2-S on FLIP (46 cells).** W2-S supersedes W2-L. The changes:
- 5 R-CANDs demoted to copy-range;
- 7 UNDECIDED rows become P by the epidemic bound;
- the rest of W2-L's UNDECIDED rows are split into P-candidate, PLANT-DESIGN and UNDECIDED.

**C6. W2-S PLANT-DESIGN vs W2-T.** 603723a7 is FLAT and 4b848d80 is INERT. W2-S never applied the admissibility checklist. Admissibility takes precedence.

**C7. P-1b vs P-2 on RELAY decay rows (41 cells), resolved with one minimal engine check (s5 F1).**

**C8. W2-T item 12 ("plant-backed 51, all RELAY; XOR/FLIP/MAJ have no plant") vs plants found by W2-J, W2-L and W2-M (17 cells).** W2-T read only the recorded relay_flood. The task plants supersede it for those cells.

**C9. W2-O vs W2-T (3 cells).**
- abb5fb81: W2-O and W2-T call it admissible (marginal); final P_PROVEN by LC2 (.504).
- c9d2ff6e: W2-O INERT+flat; W2-T CAPPED; final P_PROVEN.
- 0327a9ab: W2-O and W2-T call it INERT; final CONSTRUCTION_PLACEMENT.

**C10. W2-D tags vs final (63 cells).**
- 58 cells tagged unplaced, flat or winners_curse are P_PROVEN, and 5 are CONSTRUCTION_PLACEMENT. W2-D used only H-PLANT, which omits MAJ, LC2 and epidemic reach.
- W2-D's "notRP" uses relay_flood ≥ .75 with no genome check.

**C11. W2-J's "PLANT-SOLVED" (6 XOR cells)** means "physics allows", at lo99 > .60 and any length. None of the 6 fits the row's own genome.
- Final: 4 PLANT_SOLVED_OVERRIDE (1974a9cf, 333d6b2b, 4222a5f7, e2fd1e07). e2fd1e07's 16-line plant has lo99 .568, which passes .55 but not W2-J's .60.
- The other 2 are INERT.

**C12. W2-M's "R-candidate"** (c7ec8097, 5c35b832) is a row-genome override that stays inside C1's space.
- c7ec8097 has lo99 .636, so its plant tier is OVERRIDE. Its final class is INERT.
- 5c35b832 has lo99 .535, so it is not solved.

**C13. W2-U's own text has two figures swapped.** It says "fafa4580 .597 at 128 worlds and .648 at 1024". Its JSON says the reverse: .648 at 128 worlds (task1_xor_flip.json) and .597 at 1024 (task1b_big.json). The JSON is used.

## 5. FINDINGS

**F1 [V, high]. P-2's "decay is a relay_flood artefact" does NOT transfer to C1's RELAY NULL cells. P-1b's multi-hop reading survives, but not for the reason P-1b gave.**
- Check: `python refresh_check.py`.
  - Scope: every RELAY NULL with recorded relay_flood ≤ .60, decay_shift > 0, and not P_PROVEN (41 cells).
  - Plants: relay_refresh (P-2's plant) and relay_flood with decay_shift set to 0.
  - Worlds: the recorded plant's 32 worlds.
- Known-answer: relay_flood reproduces the recorded plant acc exactly in 41/41 cells.
- Results:
  - refresh scores at SIGNAL level (acc ≥ .60, lo99 > .55) in only 6/41 cells: 679284c6, 6e22f673 and 9b34c3c5 in space; 217fc391, 8d5ba838 and 9a7a6f57 by override.
  - refresh equals decay-0 relay_flood within .01 in 35/41 cells, so decay is not the binding dial in 35.
  - Of P-1b's 16 multi-hop plant-dead rows with decay > 0, refresh revives 1.
- So "multi-hop is rare" remains mostly plant viability, but other dials bind (async, cap/aloha, loss), not decay.
- The E-W13 wording should be scoped to the A0 matched counterfactual (decay as the only change).
- Objection: one alternative plant only, 32 worlds. Unresolved: which dial binds in the 35.

**F2 [V, high]. All the "different" cap counts are one ordering of bounds.** Every certificate is a sound upper bound, and they differ only in which engine losses they model. W2-T's exact-wake model additionally requires intermediate relays to be awake (W2-P lets them fire on arrival). That one gap explains f1bd05cd and 0677e0ae.

**F3 [V, high]. 30.6% of C1 NULLs are physics-capped as built (139/454), 3.7% more are probable caps (17), and only 13.7–14.3% are eligible for a search-limitation reading.** Eligibility is concentrated in RELAY (54/62). XOR has 0. FLIP has 3. MAJ has 5–8, and 69 MAJ NULLs were never plant-scored (W2-M sampled 30 of 143).

**F4 [I, medium]. Glossary drift caused most of the headline disagreements; only a few were factual.** The factual ones:
- f1bd05cd (model gap);
- the .600 MAJ trio (threshold);
- 3 XOR world-sampling cases;
- the C7 overgeneralisation;
- the W2-U text swap.

## 6. GLOSSARY (same word, different class; different words, same class)

**CAPPED and related words:**
- W2-T: combined bound < .60 on the held set, as an exclusive class.
- W2-P/W2-U "construction-capped": joint ceiling < .614 (K=12) or .628 (K=8, FLIP block 2). This is a 50%-power bar, not impossibility.
- W2-J: CAPPED-LC1 = H-PLANT < .60 on 64 SCORE worlds; CAPPED-LC2 = LC2 99% upper < .60; "(point)" = point estimate < .60 with a straddling CI.
- W2-O: bound .50 (every trial infeasible).
- W2-M "LC-P": k-sensor light cone < .60.
- W2-D "P:lightcone<.60" = H-PLANT.
- W2-S "P" = light cone or epidemic bound.
- H-PLANT's census counted all kinds, not only evolve rows (P-1a correction).
- All map to P_PROVEN, CONSTRUCTION_PLACEMENT or P_CANDIDATE.

**PLANT-SOLVED and related words:**
- W2-L: exact genome space, lo99 > .55.
- W2-M: a member that fits the row genome, lo99 > .55, plus a paired integration certificate ("weak" = without it, or post-hoc INT_LEAK).
- W2-J: lo99 > .60 on fresh worlds at ANY length. This means "physics allows" (H-PLANT's phrase), not in-space.
- W2-T "plant-backed" (item 12): recorded relay_flood/hold_latch with mean ≥ .60 at prog_len max(L, 12).
- W2-D "notRP": recorded family plant ≥ .75.
- P-1b/P-2 "viable": mean > .6.
- These map to the three plant tiers (IN_SPACE, OVERRIDE, BEYOND_C1).

**R-CANDIDATE:**
- W2-L/W2-S: only plants of more than 16 lines → R_CANDIDATE.
- W2-M: an override inside C1's space → PLANT_SOLVED_OVERRIDE.
- W2-J "search-OR-representation" → OVERRIDE (or R for 84cf905d).

**P-candidate:**
- W2-S: plant-relative (removing a dial rescues the plant).
- Final: also bounds in [.60, .614) and the LC2 point cases.

**PLANT-DESIGN:**
- W2-S: removing economy rescues a 22-line plant.
- P-2 "plant artefact" (decay): no separate class. Per C7 the cell becomes plant-solved where refresh succeeds and UNDECIDED otherwise.

**FLAT:**
- W2-T/W2-O: max_acc ≤ .5 in every generation.
- W2-D "flat:no_selectable_gradient": mean acc rose < .01 and last max_acc ≤ .51. This is closer to W2-T's selector_invisible (< .57). It is a different class.

**INERT:**
- W2-T: ≥ 48/64 held worlds readout-dead.
- W2-O: ≥ 50/64.
- W2-D "inert:population_state_insensitive": population sens_any < 1e-3, a different concept.

**TRUNCATED (W2-O) = LATCHED-PARTIAL (W2-T) = LATCHED_PARTIAL.**

**UNDECIDED:**
- W2-J: physics permits but plants fail, or economy-throttled.
- W2-L: plants fail, with no physics test.
- W2-S: plant inadequate even when lossless.
- W2-M: plant inadequate, or the cell was never sampled.
- W2-D: "unplaced".
- I-labels: "INDETERMINATE (no native signal)".

**one-hop / multi-hop:**
- P-1b: ceil(d/radius), d on graphs, 1 on global.
- W2-M / W2-A2: realised sensor distances (one_hop, multi_all, multi_some).
- Same words, different counts.

**Thresholds in use:** .55 (SIGNAL lo99; strict impossibility); .60 (proof convention); .614/.628 (50%-power attainability); .75 (MARGINAL upper edge; FLIP copy and B certificate).

## 7. PROPOSED FIXES
- No executable bug was found, and no diff is proposed.
- NEUTRAL, documentation:
  - (a) scope E-W13 per F1;
  - (b) correct W2-U's fafa4580 sentence (C13);
  - (c) C2 admission and H6 accounting should use the minimum certificate across W2-T, W2-U, W2-J LC2 and W2-S epidemic, and state the threshold explicitly.

## 8. DISAGREEMENTS
- **W2-T s4** ("only 11.2% plant-backed, all RELAY"): the merged figure is 13.7–14.3%, including FLIP 3 and MAJ 5–8.
- **P-1b's objection, and P-2's extrapolation to the 21 multi-hop rows:** refresh revives 1 of 16 (F1).
- **W2-P's 0677e0ae "placement-only":** not robust (C3).
- **W2-J's "H6 FALSE at ≥ 62 rows":** 59 are proven at 99%, and 3 are candidates.
- **W2-M's "R-candidate" wording for c7ec8097:** it is a C1-space override.

## 9. NEXT QUESTIONS (ranked)
1. Score the W2-M plant family on the 69 unexamined MAJ NULLs. This is the largest open block, and their status decides MAJ eligibility.
2. For the 35 RELAY cells where neither relay_flood nor refresh works and decay does not bind: single-dial removal (async, cap, loss). Is the binding dial physics or plant design?
3. Extend LC2 (fanout, loss, jitter) to FLIP, RELAY and MAJ. It added 23 XOR caps; how many FLIP, RELAY and MAJ "UNDECIDED" cells does it cap?
4. Re-run W2-P's inward placement under W2-T's relay-wake model. Do the 5 CONSTRUCTION_PLACEMENT cells stay uncapped once placement is corrected?
5. The 17 P_CANDIDATEs: a jitter- and async-aware light cone (W2-S Q4) plus LC2 at R=16 and 256 worlds for the 3 LC2-point XOR rows.
6. Eligibility at strict plant certification: on the 54 RELAY eligible cells, how many survive relay_flood scored on fresh worlds with lo99 > .55 rather than a 32-world mean ≥ .60?
7. Should the 12 plant-backed LATCHED_PARTIAL cells and the 6 plant-backed INERT cells form a separate "search reached partial competence" tier for H6?

## 10. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- Why 111 vs 107 vs 62 caps? | collect/classify; per-cell certificates | threshold (.60 vs .614), model terms (relay wake, fanout/loss/jitter), world sampling; final 139 + 17 candidates | high | the any-certificate rule mixes held and population bounds (7 split cells) | split cells | Q3, Q5
- Does P-2 transfer to C1 RELAY NULLs? | refresh_check.py, 41 cells, KA 41/41 | 6/41 rescued; decay not binding in 35/41 | high | one alternative plant, 32 worlds | binding dial | Q2
- Is f1bd05cd capped? | W2-T .550 vs W2-U/W2-P .627; lcwake.py vs task2_timing assumptions | yes; W2-T's intermediate-relay wake requirement is a real engine constraint | medium-high | not engine-traced per world | — | Q4
- Placement-only MAJ rows | W2-P inward vs model gap | 5 robust, 0677e0ae not | medium | inward not recomputed under W2-T's model | — | Q4
- H6 denominator | placement.json | eligible 62/65, capped 139, open 250 | high (counts) / medium (plant tiers: 32-world means; W2-M weak members) | 69 MAJ unexamined | — | Q1, Q6
- Glossary | source definitions read in code (mine_c1.py, summarize_t.py, PLANs) | 9 term clashes mapped | high | — | — | —

## 11. COMPUTE
- refresh_check.py: 570 CPU-s of process time at 2 threads, about 0.16 core-hours, eager CPU. The rest was file reading, about 15 CPU-s.
- Total about 0.16 core-hours against the 0.2 cap. No GPU, no search, no leases, no git writes.
