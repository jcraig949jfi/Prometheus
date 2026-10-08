# PTE-C4 preregistration: composition and reuse ladder

Status: library stage FROZEN by FREEZE_C4_L.json (aba974cf1); target stage FROZEN by FREEZE_C4_T.json (the commit adding it). Each freeze
comes before its stage's production rows. The rules below are fixed at the library-stage freeze. The target-stage
freeze adds only the frozen library and its hashes.

**Authority:** the 72h order (roles/Ananke/prompts/2026-10-07_72h_c3_c4_c5/, 8c48ebfdf), s6 and s7.

## 1. Question

Can search build a two-stage behaviour when already-solved one-stage machinery can be represented and reused as a
unit?

## 2. Ladder (the four admitted FLIP cells' physics; c4_admission.py at the C4 representation)

| rung | task | stages | ruler | plant (positive control only) | adversaries |
|---|---|---|---|---|---|
| 1 | RELAY1H: RELAY at d = 1 | one | SIGNAL + late-half | relay_flood | null |
| 2 | HOLD: gap 8, 12 trials | one | SIGNAL + late-half | hold_latch | null |
| 3 | GATE: gated relay | two | SIGNAL + late-half | gate_plant | null; relay_flood (cue without context) |
| 4 | FLIP | two | the frozen B ruler | P_FLIP | null; RELAY_LATCH |
| 5 | XOR | — | — | — | — |

- **GATE** (envs family GATE, registered outside envs.FAMILIES so C1 is unchanged). A context sign, i.i.d. per
  block, is sensed at the actuator at the block's first trial. The cue arrives d away every trial, and the target is
  context × cue. Mirror twins negate the cue only.
- **XOR is NOT VIABLE** at these cells and representation. P-XOR needs state_dim ≥ 4 and payload_width ≥ 2, and
  none of the C2 XOR candidates was admitted (W2-AD: 0/81). This is recorded, not run.
- **Admission at R4:** 15/16 (cell, task). FLIP at FLIP-0099 is NOT admitted: the copy adversary reads INDETERMINATE
  on fresh worlds (the known near-boundary copy behaviour at that cell). It stays unavailable.

## 3. Representation

REP = whichever of R3 and R4 has more competent FLIP searches at 4x in C3R; a tie goes to R4.

- Arm A uses R5 (capacity and persistent register, no duplication). It shares REP's genome spec when REP is R4.
- **Outcome (C3R, f2c8351af):** R3 0/24 and R4 0/24 at 4x, a tie, so **REP = R4**. Arms A (R5) and B/C (R4) share
  one genome spec, so all three arms of a task share the gen-0 population and training worlds.
- Selector: the C3S decision (M32 iff SELECTOR_RESOLUTION_EFFECT).

## 4. Library stage (L)

- **Searches:** RELAY1H and HOLD at the 4 cells, idx 0..7, REP + OPD, 36 generations: 64 searches.
- **Frozen library (build_library.py).** For each (cell, one-stage task):
  - take the lowest-idx competent champion (deterministic);
  - find its LIVE lines by line ablation on 32 fresh worlds;
  - those lines, in program order, form one module.
- Up to 8 modules. None can contain GATE, FLIP or XOR content: only RELAY1H and HOLD were searched.

## 5. Target stage (T)

- **Tasks:** GATE and FLIP at every admitted (cell, task). idx 0..7, 36 generations.
- **Seeds:** search_seed = H(C4_NS = 0xC4001007, task id, cell_key, idx). All arms of a task share the gen-0
  population and training worlds when their genome spec is equal.

| arm | representation | operator |
|---|---|---|
| A | R5 | OP0 (no duplication, no library) |
| B | REP | OPD (duplication-and-divergence, P_DUP .25) |
| C | REP | OPDL = OPD plus library insertion: with P_LIB .15 per offspring, a uniformly chosen frozen module is copied into free (all-NOP) capacity, otherwise at a uniform position, and is INSTANTIATED with a uniformly random permutation of the state registers; its lines are library-tagged |

- **Why renaming (added 2026-10-07, before any C4 data).** With flat global registers, independently evolved RELAY and
  HOLD modules both drive the readout register S0, so copied modules overwrite each other. Renaming their state
  registers at instantiation (c4_common.rename_state) is the smallest generic "reusable module" mechanism:
  - every reference to S_i is mapped to S_perm(i), the permutation uniform;
  - temps, I/O and shift fields are untouched;
  - tests: identity, involution, shift fields, and function restored by renaming back.

  This is the s6 "smallest compositional representation" step taken in case C3R is null. It is content-blind and
  task-blind.
- **Per champion, on held worlds:**
  - competence;
  - live lines;
  - library-tagged lines (count, live count, unmodified vs modified);
  - ablation of all library lines (competence after ablation);
  - dup lines.

## 6. Frozen interpretation (reduce_c4.py)

**Material(x vs y):** x ≥ 4, in ≥ 2 cells, and x − y ≥ 4, on paired (cell, idx).

**Labels per task:**

| label | rule |
|---|---|
| DUPLICATION_HELPS | Material(B vs A) |
| REUSE_IMPROVES_COMPOSITION | Material(C vs B) |
| COMPOSITION_REACHED | some arm ≥ 4 competent across ≥ 2 cells |
| SPARSE_EXCEPTION | otherwise any competent search |
| NO_COMPOSITION | none |

**Reuse diagnostics (arm C):**
- MODULE_PRESENT and MODULE_LIVE (fractions);
- MODULE_CAUSAL: competent champions whose competence is lost when their library lines are ablated, k/n;
- MODULE_INTEGRITY;
- median live-line count of competent champions per arm (the description length).

**Carrier swaps (swap_v2)** for every competent GATE/FLIP champion: S0, S1, S2 and payload, at mid-trial offsets.
GATE mirror twins share the context by construction, so swaps locate only the CUE carrier. The CONTEXT carrier is
located by ablation: each state register is held at 0 every tick (known answer: the GATE plant's context lives in
S2, and S2 zeroed gives FALSE).

**Transplant:** for every competent arm-C champion with causal library lines, its live library lines are inserted
into 8 fresh random REP genomes (free region), the GA runs 12 generations, and the transplant recipients are compared
with 8 un-seeded controls. This is reported descriptively.

## 7. Kill and route rules (order s8 and s10)

- If REUSE_IMPROVES_COMPOSITION is absent and COMPOSITION_REACHED is absent for both tasks, the s8 diagnostic runs
  once: REPRESENTABLE_BUT_UNSEARCHABLE vs REPRESENTATION_STILL_INADEQUATE.
  - It uses the GATE plant decomposed into its relay and latch halves, inserted as a two-module library.
  - Can search then combine the TWO designed halves? If yes, the representation can express the composition and the
    one-stage modules evolved by search are the gap (REPRESENTABLE_BUT_UNSEARCHABLE with an evolved-module gap). If
    no, composition is not reachable even from correct parts (REPRESENTATION_STILL_INADEQUATE for search).
- **s8 diagnostic, made concrete (fixed at the L freeze, before any C4 data):**
  - **Library.** D-LIB has two modules:
    - the CONTEXT half of gate_plant: the lines that latch the actuator-sensed context into a persistent register;
    - the CUE half: the lines that relay the cue and form the product.
    - They are cut from c4_common.gate_plant by line ablation on 32 fresh worlds, each half kept in program order.
  - **Known answers, checked before any D search:**
    - the two halves re-assembled (in plant order, identity renaming) reproduce the plant's competence;
    - each half alone is not competent.
  - **Arm D:** R4 with OPDL, using D-LIB in place of the evolved library. GATE at the 4 cells, idx 0..7, 36 generations,
    C4 seeds (the same gen-0 populations as arms A/B/C).
  - **Verdict:**

    | competent D searches | verdict |
    |---|---|
    | >= 4, across >= 2 cells | REPRESENTABLE_BUT_UNSEARCHABLE (search can combine correct parts; the evolved one-stage modules are the gap) |
    | <= 1 | REPRESENTATION_STILL_INADEQUATE for search (composition is not reached even from the correct parts) |
    | otherwise | INCONCLUSIVE_SPARSE |

  - Its code (the D-LIB builder) is frozen in FREEZE_C4_D.json before its production.
- If C3R and C4 are both clean NULLs, the C5 slot runs the terminal composition assay (order s10). Its kill rule is
  preregistered before that run.

## 7a. Library stage outcome (recorded at the T freeze)

- 47 of 64 library searches ran before the 2 h deadline (the highest idx rounds were censored).
- Every (cell, one-stage task) had >= 2 competent searches, so the frozen library has all 8 modules (LIBRARY_C4.json), with 1-9 live lines each.
- Known answer: no module placed alone in a NOP genome is TRUE on GATE or FLIP at any admitted cell (56 checks, c4_flight/module_alone_check.txt).

## 7b. Production

- Workers: 3 on the M1 GPU under the Fabric lease. Each stage has a deadline written into FREEZE_C4_<stage>.json as
  launch + H hours, and the launcher takes the deadline from that file (C3R lesson: the stage-2 launch used + 16 h
  where the prereg said + 14 h).
- Order puts the highest idx last, so a wall censors whole rounds of every arm equally.

## 8. Threats

- Modules are frozen champions of one physics; inserting them at other cells tests transfer, but there is only one
  library per run.
- GATE is a designed rung. Its plant is a positive control and never enters the library.
- Same author; review is requested.
