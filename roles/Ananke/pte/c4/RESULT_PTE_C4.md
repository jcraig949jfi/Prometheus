# PTE-C4 result: composition and reuse ladder

**Provenance**
- Prereg: PREREG_PTE_C4.md.
- Freezes:
  - library stage L: aba974cf1;
  - target stage T: 6e1ea0b98;
  - s8 diagnostic D: 216f50b24, frozen before the T reduction.
- REP = R4, by the C3R tie rule. Selector M32.
- **Library stage:** 2026-10-08 16:04-18:10Z. 47 of 64 searches ran before the 2 h wall; the highest-idx rounds were
  censored.
- **Target stage:** 2026-10-08 18:20Z to 2026-10-09 06:19Z. 168 of 168 searches.
  - **Infrastructure incident.** At 01:34-01:35Z the GPU driver reset five times (nvlddmkm 153), and all three
    workers died.
  - The cause was a second GPU tenant: the operator's ComfyUI (Aporia, #1944).
  - The workers were relaunched ONCE at 02:05Z, with the same commands and the same frozen deadline. The 3 interrupted
    jobs were re-run from scratch.
  - Record: c4T_production/logs/INCIDENT_GPU_TDR.md.
- Reducer: the frozen reduce_c4.py. Integrity flags: none.

## 1. Library stage

Every (cell, one-stage task) had at least 2 competent searches:

| cell | RELAY1H (d = 1) | HOLD (gap 8) |
|---|---|---|
| FLIP-0000 | 3/6 | 4/6 |
| FLIP-0004 | 2/6 | 3/6 |
| FLIP-0099 | 4/6 | 5/6 |
| FLIP-0167 | 2/6 | 4/5 |

The frozen library LIBRARY_C4.json holds 8 modules: the live lines of the lowest-idx competent champion per
(cell, task), 1-9 lines each.

Known answer: no module placed alone is TRUE on GATE or FLIP at any admitted cell (56 checks).

**One-stage machinery is therefore available, solved by search, and frozen.**

## 2. Frozen verdict: NO_COMPOSITION for GATE and for FLIP

| task | A: R5, OP0 | B: R4, OPD | C: R4, OPDL (library + renaming) | labels |
|---|---|---|---|---|
| GATE (4 cells) | 0/32 | 0/32 | 0/32 | NO_COMPOSITION |
| FLIP (3 cells) | 0/24 | 0/24 | 0/24 | NO_COMPOSITION |

- DUPLICATION_HELPS: absent (0 vs 0). REUSE_IMPROVES_COMPOSITION: absent (0 vs 0).
- Clopper-Pearson 95% upper bound per arm: .109 for GATE (0/32) and .142 for FLIP (0/24). Pooled over the three arms of
  a task: .038 for GATE (0/96) and .050 for FLIP (0/72).

**Reuse diagnostics (arm C):**

| | GATE | FLIP |
|---|---|---|
| MODULE_PRESENT | 32/32 | 24/24 |
| MODULE_LIVE | 32/32 | 23/24 |
| MODULE_CAUSAL | 0/0 (no competent champion) | 0/0 |

No competent champion exists, so the s6 causal assays (swaps, register-zero, library ablation) and the transplant have
no subject.

## 3. DESCRIPTIVE

| task, arm | train max acc (median / max) | held mean acc (median / max) | library-tagged lines in champion (median) | of which live | duplicated lines (median) | module slots still unmodified |
|---|---|---|---|---|---|---|
| GATE A | .531 / .563 | .504 / .542 | 0 | 0 | 0 | — |
| GATE B | .533 / .563 | .506 / .536 | 0 | 0 | 14 | — |
| GATE C | .538 / .562 | .512 / .542 | 18 of 24 | 6 | 12 | 99/561 (18%) |
| FLIP A | .545 / .582 | .502 / .529 | 0 | 0 | 0 | — |
| FLIP B | .535 / .570 | .503 / .522 | 0 | 0 | 14 | — |
| FLIP C | .531 / .566 | .500 / .539 | 19 of 24 | 4 | 11 | 72/410 (18%) |

**Library modules were taken up and stayed live, but they did not compose.**
- In arm C the library came to dominate the genome: about 18-19 of 24 lines descend from inserted modules.
- 4-6 of those lines are live in the champion.
- Only about 18% of tagged slots still hold an unmodified module instruction.
- Search kept module material and then mutated it, without assembling a two-stage program. Training accuracy stayed
  within about .04 of chance in every arm.

## 4. What the NULL excludes

At these cells, with the M32 selector and a 36-generation budget:
1. **Block duplication** (B vs A) does not make GATE or FLIP reachable.
2. **Insertion of solved one-stage RELAY/HOLD modules** with uniform state-register renaming (C) does not make them
   reachable, even though the modules were present and live in every champion.
3. Pooled over arms, a per-search success rate above about 4% (GATE) or 5% (FLIP) is excluded at 95% for this
   architecture at this budget.

**Not excluded:**
- larger budgets (C5T tests 4x);
- other library constructions, e.g. modules evolved for the target's own context channel;
- non-uniform renaming;
- other search architectures.

**What the null does not decide.** Whether composition is representable but not searchable, or not reachable even from
correct parts, is decided by the s8 diagnostic (section 5).

## 5. s8 diagnostic (PREREG_PTE_C4 s7; FREEZE_C4_D 216f50b24)

**Route:** neither REUSE_IMPROVES_COMPOSITION nor COMPOSITION_REACHED holds for either task, so the s8 diagnostic runs.
- Arm D: GATE at the 4 cells, idx 0..7, R4 + OPDL. The library is the cell's own two DESIGNED halves of the GATE plant
  (CONTEXT latch, CUE relay + product).
- It shares the gen-0 populations with arms A/B/C.
- Launched 2026-10-09T06:23:50Z, deadline 09:23:49Z.

Verdict: PENDING (to be added from reduce_c4d.py).

## 6. Files

- **Library stage:** c4L_production/ (rows, pops, logs); LIBRARY_C4.json; PLAN_C4_L.json; FREEZE_C4_L.json.
- **Target stage:** c4T_production/ (rows_C4T.jsonl.gz, 168 rows; pops_C4T.tar; logs, incident record and un-claimed
  jobs); REDUCE_C4.json; PLAN_C4_T.json; FREEZE_C4_T.json.
- **s8 diagnostic:** DLIB_C4.json (with its known-answer checks), PLAN_C4_D.json, FREEZE_C4_D.json; production to
  follow.
- **Flights:** c4_flight/.
