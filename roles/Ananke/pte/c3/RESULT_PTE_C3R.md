# PTE-C3R result: FLIP representation factorial

**Provenance**
- Prereg: PREREG_PTE_C3R.md, freeze 5169f7c0c. Stage-2 plan: 87e2909b9.
- Stage 1 (1x, gen 36): launched 2026-10-07T14:44:30Z, deadline +10 h as preregistered. 144 of 192 trajectories ran:
  24 per arm, with the highest idx of every arm censored as the order intends.
- Stage 2 (4x, gen 144; R4, R3 and R0 only, per the C3S selector rule): launched 2026-10-08T00:58:51Z; the last worker
  exited at 15:51Z.
  - 72 trajectories planned (only those with a saved stage-1 state).
  - Primary: 68 rows.
  - Sensitivity: 71 rows.
- **Deviation (c3r_production/DEVIATION_DEADLINE.md).** Stage 2 was launched with a launch + 16 h deadline, not the
  preregistered + 14 h.
  - The watch found this at 15:27Z, before any post-deadline row existed.
  - Three R0 jobs had started after 14:58:51Z. The one unstarted job was blocked. The primary sample excludes the three
    late jobs.
  - **The primary and the all-rows sensitivity reduce to identical labels and an identical kill verdict.**
- Reducer: the frozen reduce_c3r.py, byte-identical at the freeze and stage-2 commits. Integrity flags: none
  (no PLANT_FALSE, no OVERLAP).

## 1. Frozen verdict: NO_REPRESENTATION_EFFECT and MINIMAL_REPRESENTATION_ROUTE_FAILED

Competent searches (the frozen FLIP ruler TRUE on held worlds, at any checkpoint up to the budget):

| arm | representation | 1x (gen 36) | 4x (gen 144) |
|---|---|---|---|
| R0 CURRENT | 16 lines, 2 registers, OP0 | 0/24 | 0/20 |
| R1 CAPACITY | 24 lines, 2 registers, OP0 | 0/24 | not run (selector rule) |
| R2 PERSISTENT | 16 lines, 3 registers, OP0 | 0/24 | not run |
| R5 CAP+PERS | 24 lines, 3 registers, OP0 | 0/24 | not run |
| R3 DUPLICATE | 24 lines, 2 registers, OPD | 0/24 | **0/24** |
| R4 COMPOSED | 24 lines, 3 registers, OPD | 0/24 | **0/24** |

**Kill criterion (order s5): MET.**
- R3 and R4 each have 0 competent of 24 at 4x. The Clopper-Pearson 95% upper bound is .142.
- No arm shows an upward shift in partial function. Per-cell median champion held-B shift against R0 at 4x:
  - R3: +.007 to +.013;
  - R4: +.000 to +.011;
  - the frozen bar is .05 in at least 2 cells.

Contrasts: CAPACITY, PERSISTENT_STATE, DUPLICATION and COMBINATION are all 0 vs 0. None is material.

No competent candidate exists, so the s6 causal assays have no subject.

## 2. What the NULL excludes (and what it does not)

**Excluded at these 4 admitted FLIP cells, from random initialisation, with the M32 selector:**
1. **Capacity.** 8 extra free lines (R1) do not open FLIP at 1x: 0/24.
2. **A persistent register.** A generic non-decaying third register (R2) does not open FLIP at 1x: 0/24.
3. **Capacity plus persistent state (R5)**: 0/24 at 1x.
4. **Block duplication-and-divergence**, with and without the third register (R3, R4): 0/24 each at 4x, 144
   generations. A per-search success rate above about 14% is excluded at 95% for either arm.
5. **A graded climb.** No arm moved the median held B of its champions by even .02 over R0. Every arm sits at chance:
   - median best-checkpoint held B is .50-.52 everywhere;
   - the best single search in any arm reached held B .547.

**Not excluded:**
- **Lower success rates.** A rate under about 14% per search at 4x for R3/R4 is still possible.
- **Larger budgets.** C2C showed that time crosses rarity and not composition: RELAY rose from about 2% to 16/32
  between 1x and 16x, while FLIP stayed at 0.
- **Other duplication operators.** Only one block-duplication family at one rate (P_DUP .25) was tested.
- **Library-seeded composition.** Starting from already-solved one-stage modules is C4's question, not C3R's.
- **R1, R2 and R5 at 4x.** These arms were measured at 1x only, as the C3S selector rule preregistered.

## 3. DESCRIPTIVE (not part of the verdict)

Summary at each arm's final generation (primary rows):

| arm | stage | train max acc (median / max) | duplicated lines in best genome (median) | free NOP lines in best (median) | monitor GB (median) |
|---|---|---|---|---|---|
| R0 | 4x | .530 / .559 | 0 | 1 | .510 |
| R3 | 4x | .544 / .584 | 23 of 24 | 1 | .511 |
| R4 | 4x | .530 / .592 | 23 of 24 | 1 | .501 |
| R1 | 1x | .538 / .578 | 0 | 4.5 | .510 |
| R5 | 1x | .538 / .570 | 0 | 4 | .501 |

**The added capacity was used, but not for FLIP.**
- Under OPD the free region filled within the run: at 4x the best genome is 23 of 24 lines duplicate-marked. A
  DUP-ORIGIN mark survives later point mutations, so this counts copying events, not intact copies.
- Training accuracy stays near chance. Search fills the larger genome with copies of non-functional material, and
  selection cannot tell any of them apart.

**Interpretation.**
- This is the C2/C3S picture again. From random starts there is no graded signal for FLIP to climb, at M32 as at M8.
- More room, a free register or copies of what is already there do not create that signal.
- C3S showed that once partial function exists (a stone), M32 keeps it and sometimes climbs. C3R shows that the
  representation changes tested here do not supply the partial function in the first place.

## 4. What this changes

- **The representation hypothesis in its MINIMAL form is falsified** for these cells: "FLIP is unreachable because the
  16-line, 2-register genome makes a two-stage program combinatorially unreachable, and capacity, persistence or
  duplication will open it".
- The barrier is not "no room" and not "no place to keep the context". The parts of P_FLIP are individually worthless
  under the FLIP ruler, and none of these representations makes them valuable on their own.
- **This routes the 72h order to C4.** The question there is whether already-solved one-stage machinery, represented
  and reused as a unit (library modules with state-register renaming), lets search assemble the two-stage behaviour.
- **REP rule (PREREG_PTE_C4 s3):** R3 has 0 and R4 has 0 at 4x, a tie, so **REP = R4**. Arm A is R5, which shares
  R4's genome spec.

## 5. Files (c3r_production/)

- rows_C3R_s1.jsonl.gz (144 rows) and rows_C3R_s2.jsonl.gz (71 rows; per-generation curves and checkpoint champions);
- pops_C3R.tar: saved populations for both stages, plus the stage-1 GA states used for continuation;
- REDUCE_C3R.json (PRIMARY) and REDUCE_C3R_sensitivity_all_rows.json;
- REDUCE_S1_interim.json;
- DEVIATION_DEADLINE.md;
- logs_s1/ and logs_s2/: worker logs, launch commands, launch and deadline stamps.
