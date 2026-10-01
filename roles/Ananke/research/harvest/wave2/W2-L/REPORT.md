<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-L; sha256(report)=ea64a8ed82bdc28d; delimited; see REPORT.provenance.json -->
W2-L REPORT: placing the FLIP NULLs, and the FLIP/MAJ relay-only control
Worker W2-L (Opus) for Ananke, Wave 2. Directory: roles/Ananke/research/harvest/wave2/W2-L/

**Files**
- w2l_common.py: CPU, 2 threads; wraps H-PLANT hp_common.evaluate (eager); uses row held seeds.
- PLAN.md: classification rule frozen before scoring. Addenda A1 and A2 were written before the runs they govern.
- hp_variants.py: P-FLIP unchanged, plus V1 "refresh" and V2 "thin".
- Run scripts: gate.py, t1_flip.py, t2_relay.py, t2_mech.py, t3_feedback.py, t4_final.py, t5_relay_echo.py, relay_latch_def.py.
- tabulate.py; out/*.json and out/*.log; out/t1_table.md (the full FLIP table); out/compute_ledger.json.

**Custody**
- Nothing outside my directory was edited. No git writes.
- CPU only: CUDA_VISIBLE_DEVICES=-1; hp_common asserts torch.cuda.is_available() is False; 2 threads.
- No graph=True. No evolutionary search.
- W2-B code was imported read-only (rulers_c1.m_flip_feedback).

**Protocol for every scored number**
- The row's own physics and env.
- The row's own held seeds: H_int(search_seed, HELD_NS), M=64 = 32 mirror pairs. This lets readings be compared world-for-world with the recorded held values.
- 99% pair-bootstrap CI (assays.pair_ci).
- Variant screens used the first 32 or 16 of the held worlds, as stated per row.

## 0. KNOWN-ANSWER GATE: PASS [V]
Run: python gate.py → out/gate.json.

| program at 6f82f9c7 (d9cc), 32 held pairs | acc [99% CI] | other | matches |
|---|---|---|---|
| P-FLIP | .943 [.888, .984] | — | W2-D t_v_ruler held value, bit-for-bit |
| relay_flood | .6016 [.5495, .6497] | comm_delta lo99 .0378 | W2-D F6, bit-for-bit |

The brief expected "~.97" on 32 pairs. That figure is H-PLANT's 128-pair score (.978 on other worlds). On this cell's own 32 held pairs, P-FLIP scores .943.

## 1. FINDINGS

### F1 [V] Task-1 totals: placing the 58 light-cone-uncapped FLIP NULLs (82 evolve rows; 24 are capped)

| class | n | rows |
|---|---|---|
| PLANT-SOLVED (exact genome space and physics; not R, not P → S or U) | 3 | 6f82f9c7 (.943 [.888,.984]); 996716ac (1.000 [1,1]); 64d33b89 (.854 [.785,.916]) |
| R-CANDIDATE (only plants found need 22 or 28 lines; every C1 prog_len is ≤ 16) | 14 | see table T1 |
| UNDECIDED (P-FLIP and both variants fail, even with overrides) | 41 | see table T1 |

- Commands: run_t1_base.sh, run_t1_var.sh refresh, t1_flip.py thin, t4_final.py; table from tabulate.py.
- Confidence: high for the counts.
- **Strongest objection to R-CANDIDATE:** it only means my plants needed more than 16 lines. A 16-line decay-robust FLIP plant is not excluded, so these rows are not R.
- **Strongest objection to UNDECIDED:** I did not run any physics-removal (P) tests on these rows, for compute reasons.
- U is tested only at 6f82f9c7 (by W2-D). At the other two PLANT-SOLVED rows the remaining link is "S or U".

### F2 [V] P-FLIP's dominant failure mode is decay_shift; it is the plant's fragility, not FLIP's
**Base P-FLIP results:**
- 0 of 49 rows with decay > 0 succeed.
- 3 of 9 rows with decay 0 succeed.
- The 6 decay-0 failures are all async, global or loss ≥ .3 (f476, 5006, a467, e0c6, 6e8f, 07bd).

**Mechanism (from engine.py, step 9 `S -= S >> decay_shift`; and the plant's code):**
- P-FLIP carries the mapping multiplicatively: T1 = S0·S1>>8, then S0 = T1·S1>>8.
- Under decay the operands shrink, so the MULQ products truncate to 0.
- Negative values decay all the way to 0; positive values floor at 1.
- So both the mapping m and the readout sign are lost within a few ticks.

**V1 "refresh" fix:** sign-normalise S0 and S1 to ±256 at the start of every awake tick (+6 lines, 22 total).
- It rescues 13 rows to SIGNAL. All 13 have decay > 0.
- It reproduces .943 at 6f82f9c7, so it does not damage the plant.

**V2 "thin" (refresh + RAND-thinned relay re-emission; sensors always emit; 28 lines):**
- Rescues 1 more row: bfa85a55, .719 [.661,.773], under cap 1 saturate.
- 7b6b7f69 was .695 on the 16-world screen and .622 [.543,.695] at M=64, so it fails.

Confidence: high for the decay mechanism. Medium for "caps/collisions"; only one row was rescued by thinning.

### F3 [V] The relay's FLIP edge is a change-gated hold of the teacher, not mapping information
**What the relay does (relay_flood + envs.py FLIP schedule):**
- The teacher y = m·x arrives at the actuator as SENSE ±128 at t0+delta+1.
- relay_flood latches its sign (T0 = SENSE + IN0_0).
- The sensor re-emits only when its cue differs from its own latched sign (XOR T1^S0). So a repeated cue sends no wave, and the actuator keeps y_{k−1}.
- Within a block y_{k−1} = m·x_{k−1} = m·x_k = y_k, so the hold is correct.

**Per-trial decomposition at 6f82f9c7 (t2_mech.py), accuracy by (m, cue same/changed vs trial k−1):**

| program | m+ same | m+ change | m− same | m− change | overall |
|---|---|---|---|---|---|
| relay_flood | .828 | .818 | .643 | .106 | .602 |
| RELAY_LATCH (F4) | .927 | .896 | .867 | .043 | .688 |
| P-FLIP | .938 | .938 | .918 | .979 | .943 |

Changed-trial accuracy: relay_flood .462, RELAY_LATCH .474, P-FLIP .958.

**Analytic model (derivation):**
- Let a = P(a changed cue is delivered by readout).
- Let e = P(the teacher's flood echo has not overwritten the sensor's latch before the next cue).
- In m+ blocks: acc = ½ + ½a.
- In m− blocks with the latch intact: acc = ½.
- In m− blocks with the latch overwritten: acc = ½(1−a).
- Hence **acc_relay = ½ + a·e/4**.
- The echo hurts. At d9cc the echo reaches the sensor in roughly a third of the m− same-cue trials (.643 instead of about .9). That is why relay_flood stops at .60.

Confidence: high (the decomposition matches the model's cell pattern).

### F4 [V] A 14-line relay with no mapping inference passes SIGNAL, COMM_DEPENDENT and FLIP_FEEDBACK at d9cc
**RELAY_LATCH (relay_latch_def.py; state_dim 1; 14 lines; fits the exact genome space of 6f82f9c7):**
- Lines 0–7: P-FLIP's transport (the ±128 teacher is excluded from v; re-emit on change).
- Lines 8–13: S0 := v where v ≠ 0, then S0 := SENSE (teacher latch). The teacher is never emitted, so e = 1.
- The readout is always a copy of the last cue wave or the last teacher. It never inverts a sign.

**Result (t5_relay_echo.py → out/t5_relay_latch_d9cc.json):**

| measure | value |
|---|---|
| held accuracy | .688 [.633, .742] |
| zero-comm | .505 |
| comm_delta lo99 | .130 |
| teachers removed after trial 0 | .531 |
| FLIP_FEEDBACK paired diff lo99 | .112 |
| labels | SIGNAL, COMM_DEPENDENT and FLIP_FEEDBACK all pass |

**Prediction:** ½ + a/4 with a ≈ .9 gives ≈ .72. Observed .688; the residual comes from teacher and latch losses (m+ same .927).

**So none of SIGNAL, COMM_DEPENDENT and FLIP_FEEDBACK, singly or together, certifies mapping inference below .75.**

Confidence: high.
Objection: this is one cell. Attainability elsewhere is untested. A relay with a = 1 and e = 1 needs cue delivery within delta and no lossy teacher latch.

### F5 [V analytic proof + per-trial check] The relay-plus-teacher-echo ceiling for FLIP is exactly .75
**Policy class:**
- The readout on trial k is a copy of x_k or of y_{k−1}.
- The choice may depend on cues and timing, but not on m (equivalently, not on the joint sign of (x_{k−1}, y_{k−1})).

**Proof:**
- Every scored trial has trial k−1 in the same block, because k mod block ≠ 0 (envs.py).
- Same cue (probability ½): y_{k−1} = y_k, so copying y_{k−1} is always correct.
- Changed cue: copying x_k is correct iff m = +1; copying y_{k−1} = −m·x_k is correct iff m = −1.
- m is a fair coin per world (m0), independent of the cues, so the changed-cue case gives exactly ½.
- Total: ½·1 + ½·½ = ¾. Mirror pairs negate every input and leave this unchanged.
- The bound is attained by "hold the teacher unless the cue changed" (RELAY_LATCH with a = 1).

**Exceeding .75 requires answering −y_{k−1} on a change, i.e. computing m = x_{k−1}·y_{k−1}. That is inference.**

Corollary: on changed-cue trials every copy-class policy has expected accuracy exactly ½. Measured: .462 and .474 for the two relays, against .958 for P-FLIP.

### F6 [V] Task 2 totals: relay_flood against the recorded readings

**FLIP:**
- No C1 FLIP row, evolve or transfer, has held lo99 > .52. The maximum is 996716ac at .532 / lo99 .507.
- So no recorded FLIP SIGNAL or near-SIGNAL reading exists for a relay to explain. The relay control is vacuous on C1's FLIP data.
- Recorded C1 plant_viability relay_flood (32 worlds, seeds 0x9147; no CI) is ≥ the evolved champion's held accuracy at 40 of 82 FLIP rows (max .637 at 6e8fb3bb; ≥ .55 at 6 rows).
- In half the rows, then, search did not reach even the relay level.

**MAJ (45 rows: held lo99 > .52 or SIGNAL; 20 of them SIGNAL):**
- relay_flood scores .469–.573.
- 0 of 45 cross SIGNAL (max relay lo99 .521).
- It matches (within the recorded half-width) 7 non-SIGNAL rows and exceeds 1 (fc9a57ca: .560 vs .551).
- It matches or exceeds 0 SIGNAL rows.
- Where relay acc ≥ .55, its zero-comm is .500 and comm_delta lo99 ≤ .021, so it never passes COMM_DEPENDENT.
- For the only INTEGRATION row (4781b0a1, .789), relay scores .480.

### F7 [V for the numbers; I for the general band] FLIP_FEEDBACK has a false-negative band for genuine feedback users
- P-FLIP-refresh mechanisms, which do use every teacher by construction, fail FLIP_FEEDBACK at:
  - .630 (17b093a7, diff lo99 .018);
  - .633 (2aefc9fe, .039);
  - .645 (a4d9f2e4, .049);
  - .663 (eb076f0d, .017).
- They pass at .661 (f6cfdf82, .104) and .719 (bfa85a55, .112).
- At 32 pairs, the fixed .10 drop is attainable only from roughly .66–.70.
- Combined with F4, FLIP_FEEDBACK is both cheatable (by a copy policy) and blind to weak true inference.

### Addendum answers (principal, re W2-B)
**(1) Does P-FLIP at 6f82f9c7 pass FLIP_FEEDBACK? Yes [V].**
- Normal .943; teachers removed after trial 0 .516 [.497, .542]; paired diff lo99 .359.
- The other two PLANT-SOLVED rows also pass: 996716ac (removed → .500), 64d33b89 (removed → .504).
- Command: t3_feedback.py.

**(2) Can a clock cheat fit inside C1's genome space at d9cc? NOT SHOWN.** About 15 minutes of design effort.
- Line budget at d9cc: state_dim 2, update_period 2, wimm 1, plastic_route 1.
- Persistent storage beyond S0 and S1 exists only through WIMM/Kp. Each stored scalar costs about 3 lines (index CONST, WIMM, ADDI read-back).
- Sketched minimum:

| component | lines |
|---|---|
| transport with teacher exclusion | ~6–8 |
| first-teacher latch | ~3 |
| counter | ~4 |
| phase (MOD and compare) | ~3 |
| boundary flip | ~3 |
| readout m·x | ~2 |
| total | ~21 > 16 |

- W2-B's clock is 28 lines and needs period 1, state_dim ≥ 4 and plastic_route 0. d9cc has none of these.
- Note: RELAY_LATCH (F4) is a different, 14-line in-space cheat against the inference reading of FLIP SIGNAL.

**(3) FLIP_FEEDBACK wherever my plants or relay_flood cross SIGNAL:**
- Per row, in table T1.
- No relay_flood crosses SIGNAL on any scored FLIP or MAJ row. At d9cc it gets lo99 .5495 and FLIP_FEEDBACK fails: teachers removed .518, diff lo99 .030.
- RELAY_LATCH passes (F4).
- For the strong refresh rows the check is conservative and unpaired: diff ≥ screen lo99 − teachers-removed hi99, on 16 pairs. Every such row clears .10 by ≥ .25.

## 2. TABLES

### T1. The 58 uncapped FLIP evolve rows
- "C1 held" = recorded champion held accuracy.
- "relay pv32" = recorded C1 plant_viability relay_flood.
- Base is P-FLIP at M64. "OVR Lx→16" means the genome-space override needed by the 16-line plant.
- Refresh is screened at M32, thin at M16. Both are always overrides (22 and 28 lines).
- Every row has light-cone bound 1.00 except where shown.

**PLANT-SOLVED and R-CANDIDATE rows (17):**

| cell | topology/update | env | C1 held | base | refresh | tags | class: reading | FLIP_FEEDBACK |
|---|---|---|---|---|---|---|---|---|
| 996716ac46f73a43 | torus sync | d1 dl8 b4 | .532 | exact 1.000 [1,1] | 1.000 | cap4 aloha, econ | PLANT-SOLVED: base | PASS (≥ .50) |
| 6f82f9c7d51bcef1 | ring sync | d3 dl16 b4 | .479 | exact .943 [.888,.984] | .943 | cap2 sat | PLANT-SOLVED: base | PASS (paired .359) |
| 64d33b89811637f7 | torus async .8 | d1 dl8 b2 | .513 | exact .854 [.785,.916] | .852 | cap2 aloha, econ | PLANT-SOLVED: base | PASS (≥ .25) |
| bfa85a55ee67f7fb | smallworld sync | d1 dl4 b4 | .503 | OVR L12 .521 | .615 | decay3, cap1 sat | R-CAND: thin .719 [.661,.773] M64 | PASS (paired .112) |
| 05fea1b55336dedf | smallworld sync | d5 dl16 b2 | .488 | exact .498 | 1.000 | decay3, econ | R-CAND: refresh 1.000 [1,1] M32 | PASS (≥ .50) |
| d957d95c3a86fe53 | global async .8 | d5 dl16 b4 | .502 | OVR L8 .505 | .961 | decay3 | R-CAND: refresh .961 [.906,1] M32 | PASS (≥ .39) |
| 394743d78562ab5f | global sync | d1 dl16 b2 | .502 | OVR L12 .509 | .953 | decay3, cap4 aloha | R-CAND: refresh .953 [.891,1] M32 | PASS (≥ .37) |
| bda1a1bf2f3a927a | global async .8 | d5 dl16 b4 | .480 | OVR L8 .499 | .948 | decay3, cap1 sat | R-CAND: refresh .948 [.885,.990] M32 | PASS (≥ .37) |
| 299a681d2e3cbee1 | random async .8 | d2 dl16 b2 | .492 | exact .488 | .934 | decay6, econ | R-CAND: refresh .934 [.855,.988] M32 | PASS (≥ .31) |
| c5bceddafac4dc7b | global async .8 | d5 dl16 b4 | .494 | OVR L8 .508 | .922 | decay3 | R-CAND: refresh .922 [.854,.974] M32 | PASS (≥ .35) |
| 0ad0988d7b7e0076 | global async .8 | d5 dl16 b4 | .504 | OVR L8, D1→2 .458 | .878 | decay6, econ | R-CAND: refresh .878 [.784,.958] M32 | PASS (≥ .26) |
| 158bdd9a126414e5 | global async .8 | d5 dl16 b4 | .501 | OVR L8 .512 | .875 | decay3 | R-CAND: refresh .875 [.802,.938] M32 | PASS (≥ .30) |
| eb076f0d822f52c1 | torus sync | d3 dl16 b4 | .503 | exact .500 | .680 | decay1, cap1 aloha | R-CAND: refresh .663 [.574,.751] M64 | FAIL (.017) |
| f6cfdf8240aa339a | ring async .5 | d3 dl16 b4 | .511 | exact .501 | .643 | decay3, econ | R-CAND: refresh .661 [.599,.723] M64 | PASS (.104) |
| a4d9f2e4c636234e | smallworld sync | d1 dl16 b2 | .492 | exact .514 | .633 | decay3, cap4 aloha, loss .6 | R-CAND: refresh .645 [.586,.701] M64 | FAIL (.049) |
| 2aefc9fef958812a | random async .8 | d3 dl16 b2 | .496 | exact .505 | .643 | decay1, cap4 aloha | R-CAND: refresh .633 [.564,.706] M64 | FAIL (.039) |
| 17b093a7886431d8 | torus sync | d1 dl8 b4 | .499 | exact .508 | .664 | decay1 | R-CAND: refresh .630 [.561,.711] M64 | FAIL (.018) |

**UNDECIDED rows (41).** Columns: cell | topology/update | env | base P-FLIP | refresh M32 | thin M16 | tags.
- f476a3ca | global async | d1 dl4 b2 | exact .563 [.509,.624] | .521 | .539 | loss .3
- ec89b3d5 | global async | d3 dl4 b2 | exact .550 [.486,.618] | .543 | .508 | decay6, loss .3
- 50060cf9 | random async | d2 dl8 b2 | exact .529 | .566 | .566 | —
- 07bde99b | global sync | d2 dl8 b4 | OVR .522 | .518 | .521 | loss .3
- 5fbaa2ec | global sync | d1 dl16 b2 | OVR .520 | .586 | .531 | decay6, cap1 sat, loss .3
- a467c0f8 | ring async | d3 dl8 b2 | exact .515 | .521 | .500 | —
- 9d67b563 | random sync | d5 dl16 b4 | OVR .513 | .516 | .500 | decay6, loss .6
- f3e99f33 | global sync | d2 dl8 b4 | exact .513 | .495 | .510 | decay6
- e0c6650c | ring async | d2 dl4 b2 | exact .511 | .482 | .613 | cap1 aloha
- ecf3945d | ring sync | d3 dl8 b4 | exact .508 | .516 | .547 | decay3, cap4 sat, loss .6
- 79bc73b0 | global sync | d5 dl8 b4 | OVR .503 | .409 | .552 | decay3, cap4 sat
- 7da1d985 | random async | d5 dl4 b2 | exact .502 | .469 | .508 | decay3, cap4 aloha
- ba09f351 | smallworld sync | d3 dl8 b4 | OVR D .501 | .491 | .430 | decay1
- 06e99bf2 | ring sync | d2 dl4 b4 | OVR .501 | .474 | .448 | decay6, loss .6
- 56cdba0a | global async | d1 dl16 b4 | OVR .501 | .482 | .479 | decay6, cap1 sat, loss .3
- 4b848d80 | smallworld async | d3 dl16 b4 | OVR .500 | .477 | .521 | decay1, cap1 sat
- 603723a7 | smallworld async | d2 dl16 b4 | OVR .500 | .526 | .500 | decay3
- 964053bb | global sync | d2 dl8 b4 | exact .500 | .503 | .505 | decay3, cap4 sat
- 9b47d537 | global sync | d2 dl8 b4 | exact .500 | .492 | .500 | decay3, cap4 aloha
- b283e1ce | global async | d3 dl16 b2 | OVR .500 | .523 | .523 | decay3, cap2 aloha, loss .3
- cabf1429 | global sync | d2 dl8 b4 | exact .500 | .490 | .510 | decay3
- d09510b3 | global sync | d5 dl16 b4 | OVR .500 | .505 | .505 | decay3, loss .6
- d8bcfce0 | ring sync | d1 dl4 b4 | OVR .500 | .503 | .539 | decay1, cap4 sat
- ebdbe504 | global async | d3 dl8 b4 | OVR .500 | .500 | .500 | decay3, cap4 aloha, loss .6
- f4e59e61 | random async | d3 dl16 b4 | OVR .500 | .487 | .495 | decay3, cap1 sat, loss .6
- f53a428a | global async | d1 dl4 b4 | OVR .500 | .561 | .531 | decay6, loss .3
- 3f78ee89 | global sync | d2 dl4 b4 | OVR .499 | .493 | .482 | decay1, cap1 aloha, loss .3
- 75e32ae0 | random async | d3 dl16 b4 | exact .498 | .523 | .464 | decay1, loss .3
- 1dea05b3 | random async | d2 dl16 b4 | exact .496 | .469 | .534 | decay1, cap4 aloha
- 891dbf32 | ring sync | d3 dl8 b2 | OVR D .496 | .598 | .547 | decay1, cap2 sat, loss .3
- cc985854 | global sync | d5 dl4 b4 | exact .494 | .503 | .495 | decay3, cap2 aloha, loss .3
- fc6972d4 | torus async | d3 dl16 b2 | OVR .494 | .523 | .484 | decay6, cap2 sat
- d99833cb | ring async | d1 dl16 b4 | OVR .492 | .464 | .500 | decay6, cap1 aloha
- d3f36006 | ring sync | d3 dl16 b4 | OVR .491 | .495 | .490 | decay6, cap2 sat, loss .3
- f867ff45 | global async | d5 dl8 b4 | exact .490 | .471 | .505 | decay6
- 12492333 | ring sync | d1 dl4 b4 | OVR .488 | .487 | .521 | decay6, loss .3
- cdc9405d | global sync | d3 dl4 b4 | exact .484 | .490 | .458 | decay6, cap2 sat, loss .3
- c9998fe4 | global sync | d1 dl8 b4 | OVR .469 | .523 | .495 | decay6
- 7b6b7f69 | ring sync | d2 dl8 b2 | exact .468 | .580 | .695 (M64: .622 [.543,.695]) | decay6, cap2 sat, loss .3
- 6e8fb3bb | global async | d1 dl16 b2 | exact .467 | .457 | .477 | cap2 aloha, loss .6
- 22104294 | ring sync | d3 dl16 b2 | OVR .453 | .656 [.516,.789] | .555 | decay6

Tag counts across the 41 UNDECIDED rows:

| tag | rows |
|---|---|
| decay > 0 | 35 |
| global topology | 20 |
| loss ≥ .3 | 22 |
| async | 19 |
| cap with collision | 23 |

### T2. MAJ rows: relay_flood at row physics, 32 held pairs
Format per row: cell | recorded held acc [lo99] | recorded SIGNAL | relay acc [99% CI] | verdict.

**SIGNAL rows (20):**
- 4781b0a1 | .789 [.742] | Y | .480 [.418,.540]
- 18c218f5 | .699 [.650] | Y | .548 [.500,.596]
- 0a23398f | .695 [.648] | Y | .555 [.491,.615]
- f6b623cd | .686 [.642] | Y | .562 [.504,.620]
- 613162a3 | .682 [.630] | Y | .500 [.426,.574]
- 1a86071f | .680 [.635] | Y | .573 [.521,.625]
- 88a1a041 | .671 [.626] | Y | .514
- 88f94654 | .652 [.620] | Y | .529
- 84c8c1d1 | .648 [.618] | Y | .555
- 8743da7f | .636 [.615] | Y | .469
- 57650798 | .630 [.594] | Y | .569 [.510,.630]
- 8e1caf6b | .606 [.574] | Y | .531
- 626aa72f | .589 [.568] | Y | .518
- e341694d | .585 [.564] | Y | .529
- fded1681 | .584 [.565] | Y | .528
- 4ecdfb3f | .582 [.559] | Y | .518
- 26f9428b | .582 [.564] | Y | .525
- 8ccf6c72 | .578 [.554] | Y | .542
- 3c3d996a | .578 [.559] | Y | .526

**Non-SIGNAL rows with held lo99 > .52:**
- 488b426b .574 → .520; 5ace0dc8 .572 → .528; 528879c0 .570 → .499; f22be86f .570 → .521
- 437ca0ac .568 → .565 (match)
- e0202dc0 .567 → .523; 57c00090 .566 → .542; 266dd060 .566 → .514; 48dbe2a1 .564 → .507; 3d20243a .561 → .529
- 1448cd7d .559 → .544 (match)
- 199b4cc6 .559 → .520; 02662a50 .559 → .519; 070257d7 .559 → .501; bb1ab84c .557 → .501
- 083fde9f .556 → .533 (match)
- fc9a57ca .551 → .560 (match, EXCEEDS)
- 839b39c7 .551 → .525; 308d6488 .550 → .491; f74f80d1 .550 → .521
- 8a6454f0 .549 → .548 (match)
- 1c12d560 .549 → .547 (match)
- 057941f3 .546 → .514; 87216808 .546 → .524
- 0f196977 .544 → .543 (match)
- acf58f34 .536 → .518

Full fields are in out/t2_relay_maj.json.

## 3. RULER-ATTAINABILITY FACTS: the relay-only attainable range

**FLIP:**
- Copy-class policies (relay plus teacher echo or latch, no sign inversion) attain [.5, .75] exactly (F5 proof).
- relay_flood realises ½ + a·e/4.
- Measured maxima:
  - relay_flood: .602 at d9cc (32 pairs); .637 at 32 worlds (C1 pv32, 6e8fb3bb, no CI).
  - RELAY_LATCH: .688 at d9cc, in-space, 14 lines.
- So a FLIP reading in (.55, .75] is not evidence of mapping inference, even with COMM_DEPENDENT and FLIP_FEEDBACK.
- A reading certifies inference only when:
  - lo99 > .75; or
  - (proposed) changed-trial accuracy lo99 > .55, since every copy policy has an expectation of exactly ½ there (F5 corollary).

**MAJ:**
- Copying any single sensor attains at most 1 − flip_p = .70. C1's INTEGRATION bar (> .70) already sits on this ceiling.
- relay_flood's "any dissenting wave wins" dynamics:
  - ideal ½[(1−.3q)^5 + 1 − (1−.7q)^5], where q is the per-wave delivery probability [I];
  - .583 at q = 1, peaking at ≈ .667 at q ≈ .42.
- Measured relay_flood at the 45 rows: ≤ .573; none crosses SIGNAL. C1 pv32 over all 162 MAJ evolve rows: max .599.
- So relay-only range for MAJ = [.5, .70]. Every MAJ SIGNAL reading except 4781b0a1 lies inside it by value, but relay_flood at those exact physics reproduces none of them.

## 4. REVISED FLIP H6 STATEMENT
H6-FLIP (C1, 82 evolve NULLs, one search seed each):
- **24 rows: P.** The light-cone bound is < .60. "Search-limited" is false there.
- **3 rows: R and P excluded.** At 6f82f9c7, 996716ac and 64d33b89 a 16-line plant in the exact genome space solves FLIP (lo99 .785–1.0). It passes FLIP_FEEDBACK, and FLIP_CHANGE was checked at 6f82f9c7 (.958). The link is S or U; U is excluded only at 6f82f9c7 (W2-D).
- **14 rows: R-CANDIDATE.** Every one has decay_shift > 0. The only competent plants found need 22–28 lines (sign refresh against decay; 1 also needs thinning against a saturating cap). R is not established, because a ≤ 16-line decay-robust plant is not excluded.
- **41 rows: UNDECIDED,** not "S by default". They are dominated by decay 3–6, global/async transport and loss ≥ .3.
- So "C1 FLIP NULLs are search-limited" is supported at 3/82, open at 55/82 and false at 24/82.
- Scope note for any future FLIP success: a non-inferring 14-line relay with a teacher latch reaches .688 at d9cc. FLIP claims of mapping inference need lo99 > .75 or a changed-trial certificate, in addition to SIGNAL, COMM_DEPENDENT and FLIP_FEEDBACK.

## 5. PROPOSED FIXES
**NEUTRAL (C2 design; no frozen semantics changed; no diff, because no executable bug was found):**
- (a) **FLIP_CHANGE:** accuracy restricted to scored trials with x_k ≠ x_{k−1}, required to have lo99 > .55.
  - Proof of ½ for the whole copy class: F5.
  - Discriminates at d9cc: relays .462 and .474, P-FLIP .958.
  - It can be computed for every recorded C1/C1b FLIP champion from its stored genome, with no new search.
- (b) Report FLIP readings against the relay-only ceiling .75.
- (c) Replace FLIP_FEEDBACK's fixed .10 drop, or pair it with FLIP_CHANGE (F4, F7).

**Documentation for the principal:** H-PLANT's "P-FLIP solves FLIP in C1's own genome space" holds only at decay 0. P-FLIP is decay-fragile: 0 of 49 decay > 0 rows.

## 6. DISAGREEMENTS
- **(a) W2-B ruler table: "FLIP_FEEDBACK … SOUND in the tested family".** A 14-line non-inferring RELAY_LATCH passes it at d9cc (diff lo99 .112). The ruler certifies use of later teachers, not mapping tracking. It also fails true P-FLIP-refresh mechanisms at .63–.66 (F7).
- **(b) W2-D F6 mechanism (the echo "carries some block-mapping information").** The relay carries no mapping information (F5). Its edge is the change-gated hold, and the echo reduces it: removing the echo raises .60 to .69.
- **(c) W2-D section 5 "58 uncapped FLIP NULLs UNPLACED".** Now 3 are placed (not R, not P), 14 are R-candidates and 41 stay undecided.
- **(d) H-PLANT P-FLIP generality:** see the documentation note above.
- **(e) The brief's gate value:** "~.97 on 32 pairs" is .943 on 6f82f9c7's own held pairs. .978 was on 128 other pairs. Not a failure.

## 7. NEXT QUESTIONS (ranked)
1. Compute FLIP_CHANGE for every recorded FLIP champion in C1/C1b and for the SI-programme FLIP claims. Does any FLIP reading rest on copy-class accuracy? It is cheap: stored genomes, 32 pairs.
2. Build a ≤ 16-line decay-robust FLIP plant, for example by using MULQ clamping at large magnitudes as an implicit sign refresh. That would turn the 14 R-candidates into PLANT-SOLVED, or sharpen them toward R.
3. Physics-removal diagnosis on the 41 UNDECIDED rows: the refresh plant with decay → 0, loss → 0 and cap → 0 one at a time (about 0.5 core-hours). This separates P from plant inadequacy.
4. Seed RELAY_LATCH (.688, 14 lines, in-space) at 6f82f9c7 in place of relay_flood (W2-D Q1). Is "invert on change" a short mutational step from the latch?
5. Score RELAY_LATCH at the 3 PLANT-SOLVED and 14 R-candidate rows. That gives a per-row relay-only control for any future search success.
6. MAJ: test the OR-vote model's q-dependence. Does a thinned relay (q ≈ .4) reach about .67 at C1 MAJ physics, i.e. a relay-only false SIGNAL on MAJ?
7. Power curve for FLIP_FEEDBACK versus FLIP_CHANGE at P32 and P256 across true accuracies .55–.80.

## 8. INFERENCE LEDGER
question | evidence | result | confidence | strongest objection | unresolved | next
- Is my pipeline faithful? | P-FLIP .943 and relay .6016 / cd lo99 .0378 at 6f82, bit-equal to W2-D | yes | high | one cell | — | —
- Where does P-FLIP solve the uncapped FLIP rows? | base on 58 rows at M64 | 3/58 in-space | high | one plant | other 16-line plants | Q2
- Why does P-FLIP fail? | decay>0: 0/49; refresh rescues 13 (all decay>0) | decay breaks the MULQ bookkeeping | high | async/global/loss also implicated | 41 rows | Q3
- Caps and collisions? | thin rescues 1 of 42 (bfa85a55) | minor factor | medium | M16 screen is noisy | — | Q3
- Per-row placement | rule frozen in PLAN.md | 3 PLANT-SOLVED / 14 R-CAND / 41 UNDECIDED | high (counts) | R-CAND ≠ R | P tests | Q2, Q3
- Why does a relay beat chance on FLIP? | per-trial decomposition (m × same/change) | change-gated teacher hold; echo hurts; acc = ½ + ae/4 | high | model idealised | multi-cell check | Q5
- Relay+echo ceiling? | proof; changed-trial acc .46/.47 | .75 exactly; > .75 needs inference | high | class excludes associative tables | — | Q1
- Is the ceiling approachable in-space? | RELAY_LATCH .688 at d9cc, all 3 labels | yes, at one cell | high | one cell | other cells | Q5
- Does relay explain the MAJ SIGNAL rows? | relay_flood at 45 rows: ≤ .573, 0 SIGNAL | no | high | other relay forms (thinned) | q-dependence | Q6
- Does relay explain any FLIP reading? | no FLIP row has lo99 > .52 | vacuous | high | — | — | —
- P-FLIP FLIP_FEEDBACK at d9cc? | diff lo99 .359 | passes | high | — | — | —
- Clock cheat in ≤ 16 lines at d9cc? | line-budget sketch ~21 | not shown | low-medium | WIMM tricks unexplored | — | —
- Is FLIP_FEEDBACK sound? | relay_latch passes; refresh plants at .63–.66 fail | cheatable plus false negatives | high | 32 pairs | power curve | Q7

## 9. COMPUTE
- Measured process time: 2120 CPU-s = 0.589 core-hours (out/compute_ledger.json).
- Plus about 20–60 s of untimed row-reading one-liners: total ≈ 0.59–0.61 core-hours against the 0.6 cap. It may be marginally over, by under a minute.
- Breakdown:

| item | CPU-s |
|---|---|
| gate | 50 |
| base P-FLIP, 58 × M64 | 581 |
| refresh screen | 469 |
| thin screen | 256 |
| M64 rescoring and FLIP_FEEDBACK | 336 |
| MAJ relay | 219 |
| FLIP_FEEDBACK at d9cc | 106 |
| RELAY_LATCH | 51 |
| per-trial decompositions | 51 |

- Every process ran under 3 minutes wall. GPU: none.
