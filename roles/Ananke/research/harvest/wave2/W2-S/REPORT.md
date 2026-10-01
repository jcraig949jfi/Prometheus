<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-S; sha256(report)=6944f8c8d6fbb568; delimited; see REPORT.provenance.json -->
W2-S REPORT: FLIP_CHANGE on the record, and physics removal on the 41 UNDECIDED FLIP rows
Worker: W2-S (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-S/

**Files**
- PLAN.md: written before any scoring. Addenda A1 and A2 were each written before the runs they govern.
- w2s_common.py: hp_common.evaluate semantics, eager, CPU, 1 thread. It adds a per-trial FLIP breakdown: same-cue and changed-cue accuracy, B = (same+changed)/2, and where each answer came from.
- Run scripts: t1_controls.py, t1_record.py, t1_balanced.py, t2_dials.py, run_confirm.sh.
- Analytic scripts: copy_class_enum.py, epidemic_bound.py.
- Tables: tab_t1.py → out/t1_table.md (all 94 rows); tab_t2.py → out/t2_table.md (all 41 rows).
- Logs and data: out/*.json, out/*.log, out/compute_ledger.json.

**Custody**
- I wrote only in my own directory. No git writes.
- CPU only: CUDA_VISIBLE_DEVICES=-1; hp_common asserts cuda is unavailable.
- 1 thread per process. That is within the 2-thread limit and uses about 45% fewer CPU-seconds on this loaded host (measured 8.6 vs 15.4 s).
- graph=True was never used. No search.
- W2-L code (hp_variants, relay_latch_def) was imported read-only.

**Pipeline check [V]**
- All 44 recorded champions scored at 32 pairs reproduce the recorded held accuracy bit-for-bit (44/44).
- The W2-L numbers also reproduce exactly:
  - P-FLIP .943 and RELAY_LATCH .688 at 6f82f9c7;
  - the 5 R-CAND refresh/thin readings at 64 worlds;
  - all 9 single-D runs equal W2-L's refresh baseline bit-for-bit.

## 1. FINDINGS

### F1 [V] No recorded C1 FLIP reading rests on copy-class accuracy, because no reading rests on anything
**Scope:**
- Every C1 FLIP champion: 82 evolve rows plus 12 transfer rows (transfers use extra.genome and seed namespace 0x7F7F).
- C1b and c1_posthoc contain no FLIP cells. C1b holds HOLD, MAJ and RELAY cells; posthoc holds 2 HOLD cells.
- Rows with recorded accuracy > .5 were scored at 32 pairs (44 rows). The rest were scored at 16 pairs (first 32 held worlds).

**Results:**
- Only one row has overall lo99 > .5: 996716ac, .532 [.507].
  - Same-cue .529; changed-cue .537 [.481, .598]; B .533 [.507, .561].
  - Answers come roughly a third each from x_k, y_prev and −y_prev, and about 30% of readouts are 0.
  - So it is weakly above chance and symmetric. It is not copy-class.
- Among the 50 evolve rows with accuracy > .5: mean same-cue .501, mean changed-cue .511. There is no lean toward same-cue trials.
- Distribution of changed-cue accuracy (evolve): min .132, q10 .474, q25 .492, median .500, q75 .509, q90 .528, max 1.000.

**Patterns across the 94 rows:**

| pattern | n | rows |
|---|---|---|
| chance | 81 | — |
| TEACHER-COPY (same ≥ .82, changed ≤ .13, so overall ≈ .5) | 8 | 7 transfers (HOLD champions that latch the teacher) and evolve 545aff2f |
| ANTI-COPY (answers −y_prev) | 4 | see F2 |
| above chance, symmetric | 1 | 996716ac |

**Controls (32 pairs):**

| row | program | overall | changed-cue [lo99] | B [lo99] | FLIP_CHANGE | B > .75 certificate |
|---|---|---|---|---|---|---|
| 6f82 | P-FLIP | .943 | .951 [.903] | .943 [.889] | PASS | PASS |
| 9967 | P-FLIP | 1.000 | 1.000 | 1.000 | PASS | PASS |
| 64d3 | P-FLIP | .854 | .826 [.712] | .842 [.759] | PASS | PASS |
| 6f82 | RELAY_LATCH | .688 | .488 [.421] | .696 [.658] | fail | fail |
| 9967 | RELAY_LATCH | .766 [.719, .807] | .502 [.421] | .751 [.710] | fail | fail |
| 64d3 | RELAY_LATCH | .707 | .469 [.366] | .664 [.597] | fail | fail |
| 6f82 | relay_flood | .602 | .490 [.416] | .618 [.567] | fail | fail |

- Confidence: high.
- Objection: rows at or below .5 were scored at 16 pairs. They cannot carry a reading above .5, so this does not change the answer.
- Commands: t1_record.py 0 2; t1_record.py 1 2; t1_controls.py; t1_balanced.py; tab_t1.py.

### F2 [V] W2-L's FLIP_CHANGE alone is unsound: 4 recorded champions pass it with zero inference
- An anti-teacher policy answers −y_{k−1}. On a changed trial, −y_{k−1} = y_k, so it is always right there and always wrong on same-cue trials.

| champion | changed-cue [lo99] | same-cue | B | answer source |
|---|---|---|---|---|
| 964053bb | 1.000 [1.000] | .000 | .500 | −y_prev on 100% of scored trials |
| 22104294 | .811 [.696] | .110 | .461 | −y_prev on 83–88% |
| 34f84c6b | .666 [.577] | .330 | .498 | −y_prev on ~65% |
| f30f89b0 | .611 (16 pairs, PASS); .591 [.548] (32 pairs, narrow fail) | .423 | .507 | readout 0 on 84%, −y_prev on 16% |

- All four have overall ≈ .5.
- Confidence: high.
- Objection: none of them is a positive reading, so no recorded claim is affected. The problem is the proposed C2 ruler.

### F3 [V, analytic plus exact enumeration] Corrections to W2-L's F5, and a sound certificate
**(a) An error in F5's proof.** On a changed trial, y_{k−1} = m·x_{k−1} = −m·x_k = −y_k. So copying the teacher is always wrong there, not "correct iff m = −1". The copy that is right iff m = −1 is the stale cue x_{k−1}.
- Copy-class changed-cue accuracy is therefore in [0, ½] in expectation, not exactly ½.
- Evidence: the TEACHER-COPY transfers score changed-cue .016–.077, e.g. f728b1d2 answers y_prev on 97–99% of trials.

**(b) The overall ceiling of .75 holds for B (an expectation), not for realised overall accuracy.** RELAY_LATCH at 996716ac scores .766 overall because changed cues were 47% of that row's trials. Its B is .751 [.710, .791].

**(c) The sound certificate is B lo99 > .75.**
- Exact enumeration (copy_class_enum.py) over signed single-source policies (±x_k, ±x_{k−1}, ±y_{k−1}), each choice allowed to depend on whether the cue changed:
  - Every ungated source gives same + changed = 1.
  - Gating gives at most B = .75.
  - B > .75 needs (same: +y_{k−1}, changed: −y_{k−1}). That equals y_{k−1}·x_{k−1}·x_k = m·x_k, which is the inference itself.
- B is linear, so any mixture of non-inferring policies stays ≤ .75. A mixture with weight w on inference gets ≤ .75 + w/4.
- For comparison, "same > .55 AND changed > .55" is cheatable: a 30% anti-copy plus 70% latch mixture gives .70 and .65.
- Exception: FLIP_CHANGE is still valid for a known-code plant whose same-cue branch is the teacher hold. P-FLIP and refresh are such plants, so the anti-copy cheat cannot inflate them.
- Caveat: B > .75 is unattainable wherever reach q < 1 (F6). So at weak-reach physics, no reading can be certified as inference at all.

### F4 [V] 5 of W2-L's 14 R-CANDIDATE readings are copy-range only
Refresh plant (thin at bfa85a55), 32 pairs:

| row | overall [lo99] | changed-cue [lo99] |
|---|---|---|
| 17b093a7 | .630 | .590 [.507] |
| 2aefc9fe | .633 | .549 [.451] |
| a4d9f2e4 | .645 | .328 [.222] |
| f6cfdf82 | .661 | .547 [.463] |
| bfa85a55 | .719 [.661, .773] | .491 [.385] |

- All five fail FLIP_CHANGE, and every overall value is inside the copy range.
- The plant has degraded to teacher-hold behaviour.
- f6cfdf82 and bfa85a55 passed FLIP_FEEDBACK in W2-L. That is more evidence that FLIP_FEEDBACK certifies use of teachers, not inference.
- The other 9 R-CANDs pass FLIP_CHANGE at 16 pairs:
  - 05fe 1.000;
  - d957 .962 [.909];
  - 299a .923 [.840];
  - bda1 .921 [.826];
  - 3947 .927 [.809];
  - c5bc .892 [.780];
  - 0ad0 .844 [.720];
  - 158b .809 [.682];
  - eb07 .734 [.625]. eb07 was not confirmed at 32 pairs; its overall there is .663.
- Commands: t2_dials.py RC_* / RC64_* (NONE spec).

### F5 [V] Physics removal on the 41 rows
- Plant: W2-L refresh with state_dim ≥ 2 and prog_len ≥ 22, labelled as an override.
- Competent means, at 32 pairs: overall lo99 > .55 AND FLIP_CHANGE lo99 > .55 (PLAN A2, fixed before any confirmation run).

**(i) Decay is never a binding dial for the refresh plant.**
- Single-D removal is bit-identical to the baseline at 9/9 rows. The plant renormalises its sign every awake tick.
- So E-W13's decay rescue cannot occur with this plant, and no row became PLANT-DESIGN through decay.
- Other dials that were inert at some rows: C at 5/8 rows, E at 7/16.

**(ii) ALL five brief dials removed: 12/41 pass the screen; 29 fail.**

**(iii) Economy is an off-list binding dial (EXTENDED E).**
- The engine charges c_op × (non-NOP lines) every awake tick. Emission needs E ≥ c_emit × copies, which is 4 × fanout = up to 32.
- Income is 4 per tick and the energy cap is 100. A 22-line plant starves after its first awake tick.
- All 12 rows with c_op = 1 were among the 29 that failed with all five dials removed.
- Removing all five dials plus E/N rescues 10 of the 29: 9 competent (4b84, 56cd, d3f3, d998, f4e5, fc69, 5006, 6037, f476); 06e9 reaches .711 overall but only .427 changed-cue, so it is copy-only.

**(iv) Remaining failures.** 19 rows still fail with every removal, plus 06e99bf2 (copy-only). That leaves the plant inadequate at 20 rows.

### F6 [V analytic; engine-checked] An epidemic bound proves P at 7 global rows, for any program
**Basis (engine._emit):**
- In global topology every copy goes to a uniformly random other site. There is no routing control.
- In expectation, informed sites can grow at most as I(τ) ≤ I(τ−1) + F·w·I(τ−dmin).
- The actuator is exchangeable with every other site, so q ≤ (I(delta)−1)/(N−1).
- Without cue information the best answer is a coin, so accuracy ≤ ½ + q/2.

**Rows where the bound falls below the SIGNAL bar:**

| rows | accuracy bound |
|---|---|
| 964053bb, 9b47d537, cabf1429, f3e99f33 | .552 |
| cdc9405d | .532 |
| ec89b3d5 | .558 |
| ebdbe504 | .5725 |

- All 7 failed even fully lossless. They are P, independent of any plant.

**Other global rows:**
- The bound is .61–.79 at 07bd, cc98, f867, 3f78, 79bc and b283. P is not proven there.
- At five of those (all but b283) the bound is below .75, so B certification is impossible there.

**Consistency check:** no measured plant exceeds its bound across 28 global FLIP rows, including the high R-CAND plants (bound 1.0).

**Root cause:** H-PLANT's light cone assumes "fanout reaching any neighbour", which means one hop to everyone in global topology. It is blind to fanout, so it overstates reach for global-sample rows.

- Confidence: high for the 6 rows at ≤ .558; medium-high for ebdbe504 (.5725).
- Objection: the bound is in expectation and optimistic, which makes it valid as an upper bound.

### F7 [V] Binding dials among the rescued rows (details in T2)
| binding | rows |
|---|---|
| single timing dial | 22104294 (J or U alone); ba09f351 (J) |
| single economy dial E | 4b848d80, 603723a7, d3f36006 |
| joint (L, U, J), confirmed at 32 pairs | 5fbaa2ec L+U; 6e8fb3bb L+U; 7b6b7f69 L+J; 891dbf32 L+J; 9d67b563 L+J; f53a428a L+U+J |
| joint, screen only | 75e32ae0 (J plus L or U; J alone at 32 pairs is copy-like, changed-cue lo99 .480); a467c0f8 (L+U+J; U+J at 32 pairs is copy-only); e0c6650c (C+U+J; J and U+J fail at 32 pairs) |
| E-joint, screen only | 5006, 56cd, d998, f476, f4e5, fc69 (E alone at 32 pairs: fc69 changed-cue lo99 .530, fail) |
| fails at 32 pairs | 12492333 (all-dials-equivalent config scores .587 [.520]) |

## 2. TABLES

### T1. FLIP_CHANGE on the record
The full 94 rows are in out/t1_table.md. Key rows:

| cell | kind | pairs | overall [lo99] | same | changed [lo99, hi99] | FLIP_CHANGE | pattern |
|---|---|---|---|---|---|---|---|
| 996716ac | evo | 32 | .532 [.507] | .529 | .537 [.481, .598] | fail | above chance, symmetric |
| f9413b6b | evo | 32 | .522 [.495] | .515 | .526 | fail | chance |
| cc985854 | evo | 32 | .522 [.484] | .496 | .547 [.494, .598] | fail | chance |
| 964053bb | evo | 32 | .484 | .000 | 1.000 [1.000] | PASS | ANTI-COPY |
| 22104294 | evo | 32 | .510 | .110 | .811 [.696] | PASS | ANTI-COPY |
| 34f84c6b | evo | 32 | .484 | .330 | .666 [.577] | PASS | ANTI-COPY |
| f30f89b0 | evo | 16 / 32 | .493 / .499 | .399 / .423 | .611 PASS / .591 [.548] fail | — | ANTI-COPY (mostly readout 0) |
| 545aff2f | evo | — | .512 | .816 | .132 | fail | TEACHER-COPY |
| f728b1d2 | tra | — | .452 | .994 | .014 | fail | TEACHER-COPY |
| 1ec4e938 | tra | — | .456 | .978 | .024 | fail | TEACHER-COPY |

- Plus 5 more teacher-copy transfers: 97dad3c3, 2ba2c00e, 29a5eb99, ed406581, be5024ce.
- Summary: no recorded FLIP reading rests on copy-class accuracy. Positives pass and negatives fail (F1 controls). FLIP_CHANGE alone is gamed by 4 anti-copy champions; B > .75 separates every case.

### T2. Binding dial for the 41 UNDECIDED rows
- Dial codes: D decay, L loss, C cap, U update, J jitter (the brief's five); E economy and N noise/dup (extended, beyond the brief).
- Screen = 16 pairs; confirmation = 32 pairs. Full values are in out/t2_table.md.

**P (epidemic bound, any program; fail even fully lossless) — 7 rows:**

| row | accuracy bound |
|---|---|
| 964053bb | .552 |
| 9b47d537 | .552 |
| cabf1429 | .552 |
| f3e99f33 | .552 |
| cdc9405d | .532 |
| ec89b3d5 | .558 |
| ebdbe504 | .5725 |

**P-candidate: single timing dial — 2 rows:**
- 22104294: J → 1.000 / 1.000; U → .914 / .876 [.794].
- ba09f351: J → .969 / .996 [.984].

**PLANT-DESIGN: economy (single E confirmed) — 3 rows:**
- 4b848d80: E → .949 / .950.
- 603723a7: E → .919 / .884.
- d3f36006: E → .909 / .814.

**PLANT-DESIGN (tentative): economy jointly with others (all five + E/N, screen only) — 6 rows:**
- 50060cf9 1.000
- 56cdba0a .927
- d99833cb .990
- f476a3ca .930
- f4e59e61 .990
- fc6972d4 1.000

**P-candidate, joint, plant-relative (confirmed at 32 pairs) — 6 rows:**

| row | dials | overall / changed-cue [lo99] |
|---|---|---|
| 5fbaa2ec | L+U | .844 / .747 [.654] |
| 6e8fb3bb | L+U | .920 / .876 |
| 7b6b7f69 | L+J | .777 / .765 |
| 891dbf32 | L+J | .832 / .685 [.560] |
| 9d67b563 | L+J | .992 / .977 |
| f53a428a | L+U+J | .924 / .858 |

**P-candidate, joint, screen only — 3 rows:** 75e32ae0 (J plus L or U), a467c0f8 (L+U+J), e0c6650c (C+U+J).

**UNDECIDED: plant inadequate even fully lossless — 13 rows, plus 12492333 which fails at 32 pairs:**
- 06e99bf2 (copy-only once lossless), 07bde99b, 1dea05b3, 3f78ee89, 79bc73b0, 7da1d985, b283e1ce, c9998fe4, cc985854, d09510b3, d8bcfce0, ecf3945d, f867ff45.
- 12 of these 14 have delta 4 or 8. 8 are global topology.

## 3. REVISED FLIP PLACEMENT (82 C1 evolve NULLs)
| class | count | composition |
|---|---|---|
| P, proven | 31 | 24 W2-L light-cone rows + 7 epidemic-bound rows |
| PLANT-SOLVED | 3 | unchanged; all pass FLIP_CHANGE and B |
| R-CANDIDATE | 9 | was 14; 5 demoted (F4) |
| PLANT-DESIGN | 9 | economy: 3 confirmed + 6 tentative E-joint |
| P-candidate, plant-relative | 11 | timing/loss dials: 2 single + 6 joint confirmed + 3 screen-only |
| UNDECIDED | 19 | 14 plant-inadequate + 5 demoted R-CANDs |

- Total: 82.
- The brief's 4-way split over the 79 non-solved rows depends on how the 11 plant-relative P-candidates are counted:
  - counted as UNDECIDED: P 31 / R-CAND 9 / PLANT-DESIGN 9 / UNDECIDED 30;
  - counted as P: 42 / 9 / 9 / 19.
- "C1 FLIP NULLs are search-limited" is now supported at 3/82, a live possibility at ≤ 9/82, and false at ≥ 31/82.

## 4. PROPOSED FIXES (no executable bug; no diff)
- **(a) NEUTRAL, C2 ruler:** replace W2-L's proposed FLIP_CHANGE with B = mean(same-cue accuracy, changed-cue accuracy), certified when pair-CI lo99 > .75. Keep FLIP_CHANGE only for known-code plants with a teacher-hold same-cue branch.
  - Code: w2s_common.flip_eval computes it.
  - Basis: copy_class_enum.py (asserts the theorem) and t1_balanced.py (controls).
- **(b) NEUTRAL, documentation:** H-PLANT's light cone is blind to fanout for global topology. Pair it with epidemic_bound.py. It is plant-independent and costs under 1 s of CPU.
- **(c) NEUTRAL:** any plant-viability or R-CAND claim on FLIP should require FLIP_CHANGE (or B), not overall lo99 > .55 alone (F4).

## 5. DISAGREEMENTS
- **(a) W2-L F5:** the proof line "copying y_{k−1} correct iff m = −1" is wrong (it is always wrong on a changed trial). The corollary "exactly ½" should read "≤ ½". The .75 bound survives, but as a bound on B or expectation; realised overall reached .766 at 996716ac.
- **(b) W2-L §5a:** FLIP_CHANGE lo99 > .55 is not a sound inference certificate. 964053bb scores 1.000 with no inference.
- **(c) W2-L T1:** 5 R-CANDs (17b0, 2aef, a4d9, f6cf, bfa8) are copy-range readings, not competent plants.
- **(d) W2-L F2 and the brief's E-W13 framing, as applied to the refresh plant:** decay is inert for refresh (9/9 bit-identical). Its failures come from economy, timing/loss and global reach, not decay.
- **(e) H-PLANT lc_census:** bound 1.0 at global-sample rows overstates reach. 7 rows are provably P at ≤ .5725.

## 6. NEXT QUESTIONS (ranked)
1. Confirm at 32 pairs (about 0.05 core-h):
   - all five dials + E/N for the 6 E-joint rows;
   - all five dials for 75e3, a467 and e0c6;
   - eb076f0d's FLIP_CHANGE.
2. Extend the epidemic bound to sample-mode, non-global topologies with plastic_route = 0, where routing is also blind. That could prove P at more of the 13 inadequate ring/random rows.
3. Build an economy-feasible FLIP plant: a short relay rule (≤ 3 non-NOP lines) on relay sites and a long rule only at the actuator, using rules > 1 and setrule. This decides PLANT-DESIGN versus P for the 9 economy rows.
4. Write a jitter- and async-aware light cone. That would turn the U/J P-candidates (22104294, ba09f351 and the joint rows) into P or not P.
5. Compute B for the MAJ/RELAY analogues and for any SI-programme FLIP claims. Is a B-type certificate needed for other families?
6. Why do the 13 inadequate rows (bounds .61–1.0, e.g. c9998fe4 .92 and d09510b3 1.0) fail even fully lossless? Trace whether the cue reaches the actuator under change-gated single-wave flooding.
7. Run the monotonicity spot check I skipped: single removals on rows that fail with every dial removed.

## 7. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- Is the pipeline faithful? | 44/44 bit-matches; W2-L values reproduced | yes | high | — | — | —
- Does any FLIP reading rest on copy-class accuracy? | 94 rows: same vs changed decomposition | no; only 996716ac is above .5, and symmetrically | high | rows ≤ .5 at 16 pairs | — | —
- Is FLIP_CHANGE sound? | 4 anti-copy champions pass it | no | high | — | — | B ruler
- Does F5 hold? | enumeration; teacher-copy transfers at changed-cue .02 | proof error; the bound holds for B | high | class restricted to single-source copies | richer histories | Q5
- Is the B > .75 certificate sound? | theorem + controls separate | yes | high-medium | policies using k−2 history not enumerated | — | Q5
- Are the R-CAND readings inference? | FLIP_CHANGE at 32 pairs | 9 likely yes; 5 copy-range | high | eb07 at 16 pairs only | — | Q1
- Does decay bind the refresh plant? | 9/9 bit-identical | no | high | — | — | —
- Single binding dials? | singles + confirmations | J/U at 2 rows; E at 3 | high | E is plant-length dependent | multi-rule plant | Q3, Q4
- Joint bindings? | leave-one-out + 32-pair confirmations | L+U/L+J at 6; 3 screen-only | medium-high | plant-relative | — | Q1, Q4
- Economy as hidden physics? | engine step 5; 0/12 c_op = 1 rows pass all-five-dial removal; E removal rescues 9 competently, 06e9 copy-only | yes | high | — | — | Q3
- Global reach? | epidemic bound; no measured violations | P at 7 rows | high | optimistic bound | sample-mode, non-global | Q2
- Inadequate rows | fail even fully lossless | 13 undecided | medium | — | why | Q6

## 8. COMPUTE
- Timed process CPU: 1950 s.
- Untimed, estimated: imports about 100 s, profiling about 75 s, tabulation about 5 s.
- Total about 2130 s ≈ 0.59 core-hours against the 0.6 cap (out/compute_ledger.json).
- 1 thread per process; every run under 6 minutes wall; no GPU.
