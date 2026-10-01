# W2-41: does a self-carried register context change how the 7ae3 family behaves?

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run:** 02:56:19Z–03:06:24Z, about 7 CPU-min. The worker's own background batches exited normally.
> - **Files:** `r1_carried.py` + `r1_out/*.json.gz` (per-interaction replay of 23 runs), `a2_assay` (T1), `a3_mechanism_A/B` (T2), `a4_inworld` (T3).

## Answer
1. **The 7ae3 family's "register-robust" result holds for every context tested.**
   - F, C3, AC, 5C and C3+AC behave identically under ZERO, BANK, 9 self-carried pools and a birth-conditioned pool: |Δm| ≤ 0.004, and the exact ruler gives identical results.
   - **Dead-register test:** for 2,589 self-carried contexts, 822 birth-conditioned contexts and 3,000 uniform-random contexts:
     - the genome's own LDIR (src, dst, count) is the same as under ZERO;
     - the final halves are the same, with 0 differences in 8,822 × 2 calls per genome and side;
     - the register file converges to the ZERO run's by pc 29 at the latest, before `LD E,A` at 48, `LD H,(HL)` at 49 and the LDIR at 52.
   - **Why:** `LD HL,5C00` at byte 1 overwrites HL. `LD D,L` at 22 and SELF at 23 then rewrite the rest.
2. **The contradiction with W2-26 was a labelling slip.** In 52 of W2-26's 53 context-dependent edges, the genome actually assayed (k@E2) is **foreign**. That includes all 9 control C-edges; 2 of them had a 7ae3 parent at birth, which is where the "7ae3" label came from.
   - The single 7ae3-family case is XTK_35 (53/64 bytes). Its byte 1 changed from 21 to 29, which removes the HL initialiser.
3. **In the world, the family behaves like its static profile; context explains nothing.**
   - Swapping each organism's carried context for ZERO across 5,915 recorded family interactions changes the outcome in 3/2,922 side-0 and 63/2,993 side-1 interactions.
     - Conversion: side 0, 0.374 vs 0.375; side 1, 0.391 vs 0.409 (the carried context slightly *lowers* side-1 conversion).
   - Static p11-credited conversion with actual contexts is 0.350 / 0.365, against world births of 0.348 / 0.365.
   - The exact founder in-world (n = 81): side 0 births 0/21, keep 0.571; side 1 births 0.900, keep 0.917.
   - **The world-vs-static gap is genotype composition, not registers.**
     - Only 1.4% of family interactions involve the exact founder.
     - Non-exact non-converters convert at only 0.52–0.59 on side 1.
     - Side-0 family births come from static side-0 morphs (0.965 births per interaction).
4. **W2-30's sweep prediction and W2-32's X-IMPLANT-MORPH bands are unchanged.** W2-30's caveat "ZERO/BANK contexts only" is discharged.

## T1: profile by donor context (same 1,000 bank partners in every arm, FID ruler)

| genome | ZERO m | SELF m | keep s0 / s1 | conv s0 / s1 |
|---|---|---|---|---|
| F | 1.172 | 1.172 (SELF_S0 / CTL / AGE5+ / BIRTHCOND 1.169–1.172) | 0.521 / 0.903–0.907 | 0.002 / 0.870–0.874 |
| C3 | 1.389 | 1.389 | 0.973 / 0.907 | 0.002 / 0.870 |
| AC | 1.248 | 1.248 | 1.0 / 0.521 | 1.0 / 0.021 |
| 5C | 1.240 | 1.240 | 1.0 / 0.521 | 1.0 / 0.006 |
| C3+AC | 1.469 | 1.468 | 1.0 / 0.961 | 1.0 / 0.010 |

- Class ruler: every arm within 0.003. Exact ruler: identical across all 11 arms.
- The ZERO row reproduces N17e, W2-24 and W2-30.

## T2: which carried registers flip the copy direction
Ablation on the 53 W2-26 context-dependent edges:

| necessary register(s) | edges | sufficient alone? |
|---|---|---|
| L | 30 | yes (30/30) |
| fz | 8 | no |
| A + fz | 8 | no |
| E | 4 | yes |
| E + L | 1 | no |
| C | 1 | yes |
| D | 1 | yes |

- **Mechanism:** when a genome has lost an initialiser, a carried register can reach the copy destination (DE masked to 7 bits). A value of 0x40–0x7F, or a high-bit alias, lands the copy in the partner's half.
- **Traced case, XTK_35:** byte 1 changed 21→29, carried L = 0x40, so LD D,L gives D = 0x40, then A = 0x40, then LD E,A gives E = 0x40. The LDIR copies 0 → 0x4040 into the partner; under ZERO it copies 0 → 0.
- **Byte-1 mutations:** 48 of 60 logged in-world flips have byte 1 mutated. 1,590 of 5,915 family interactions carry a byte-1 mutation, but only 66 flip.
- **Carried L with bit 6 set:** 18.5% of family side-0 contexts, against 44% of bank contexts.

## T3: realized behaviour vs static profile

| group / class / side | n | world births | world keep | static conv: actual / ZERO / BANK context |
|---|---|---|---|---|
| CTL exact F / 0 | 11 | 0.000 | 0.545 | 0 / 0 / 0 |
| CTL exact F / 1 | 37 | 0.892 | 0.892 | 0.892 (all three) |
| RUN exact F / 0 | 10 | 0.000 | 0.600 | 0.10 (all three) |
| RUN exact F / 1 | 23 | 0.913 | 0.957 | 0.957 (all three) |
| RUN side-0 morph / 0 | 642 | 0.967 | 0.989 | 1.0 / 1.0 / 0.983 |
| CTL other family / 1 | 668 | 0.594 | 0.856 | 0.602 / 0.630 / 0.561 |
| RUN other family / 1 | 1,026 | 0.518 | 0.842 | 0.529 / 0.564 / 0.473 |
| RUN other family with C3 / 0 | 87 | 0.000 | 0.816 | 0.046 (all three) |
| all family / 0 | 2,922 | 0.348 | 0.761 | 0.374 / 0.375 / 0.368 |
| all family / 1 | 2,993 | 0.365 | 0.680 | 0.391 / 0.409 / 0.367 |

**Side observation:** C3 at byte 43 occurs in a world runaway (XTK_35: 189 interactions, 47 genomes, epochs 2–31), always together with about 8 other differences. Its side-0 keep is 0.816, against 0.645 for non-C3 family members.

## Adversarial points
1. **Runaway-biased sampling.** SELF_RUN and SELF_CTL agree, and the dead-register null is structural. Bank contexts carry the redirecting L more often, so the bank arm is the harsher test.
2. **Birth-conditioned contexts.** The unconditioned pool gives the same null.
3. **Damaged-half side-1 runs** are the one gap, bounded at ≤ 0.004.
4. **Age 0 (23 rows) and late epochs** are thin. They are covered by 3,000 random contexts.
5. **Rulers.** Promoted static conversion matches world births to within 0.002.
6. **Exact-founder n = 81 is small.**
7. **The family threshold** affects T3 composition only.

## Ledger entry (W2-41)
- **Inference:**
  - Intact 7ae3 code overwrites its whole register file before the copy setup, so "register-robust" holds universally.
  - Context dependence belongs to mutants that have lost an initialiser (mostly foreign genomes, or genomes hit at byte 1).
  - W2-26's premise was a parent-vs-assayed labelling slip.
  - W2-30 and W2-32 are unchanged.
- **Confidence:** high for the null and the relabelling; moderate-high for the ablation mechanism; moderate for composition.
- **Next:**
  - retype W2-26's C-row by k@E2;
  - check the byte-1 hotspot (in-place OPERAND vs partner writes);
  - composition-weighted family m for W2-32's sensitivity analysis;
  - check whether XTK_35's C3 lineage persists past epoch 45.
