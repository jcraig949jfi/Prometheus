# Result packet: C2BX (RELAY budget extension) and PTE-C2C (FLIP operator x path geometry)

Date: 2026-10-06. Prepared by Ananke, instance m1-46797183, on M1 with the RTX 5060 Ti.

**Provenance**
- Authority: operator order of 2026-10-06, roles/Ananke/prompts/2026-10-06_c2b_close_c2bx_c2c/ (64dad7553).
- Freeze: 2d2c1bed3, code 3c1988f46. C2B input 1ac44021c. C2A and C2B are unmodified.
- Run: 152/152 jobs, 06:56:36Z to about 14:25Z (7.5 h; the C2B-calibrated projection was 7.7 h). No censoring.
- Integrity: 0 flags. No PLANT_FALSE, no START_COMPETENT, no OVERLAP. All 32 C2BX prefix gates passed: the gen-144
  population and the 36-144 statuses are identical to C2B.
- Frozen verdicts are from reduce_c2c.py (REDUCE_C2C.json). Sections 1.3 and 2.3 are DESCRIPTIVE and are labelled
  so.

## Part 1: C2BX, the RELAY-mh budget-scaling extension (a measurement campaign)

### 1.1 Cumulative success (a competent checkpoint champion at or before the budget; checkpoints every 36 generations)

| scope | n | 4x (gen 144) | 8x (gen 288) | 16x (gen 576) | NEW in (144, 288] | NEW in (288, 576] | tail (frozen) |
|---|---|---|---|---|---|---|---|
| pooled | 32 | 7 (CP95 .09-.40) | 10 (.16-.50) | **16** (.32-.68) | 3 | 6 | **TAIL_CONTINUES** |
| leave-RELAY-0019-out | 24 | 2 | 4 | **9** | 2 | 5 | **TAIL_CONTINUES** |

| cell | 4x | 8x | 16x | first competent generations |
|---|---|---|---|---|
| RELAY-0010 | 1/8 | 1/8 | 2/8 | 144, 396 |
| RELAY-0019 | 5/8 | 6/8 | 7/8 | 36, 72, 108, 144, 144, 180, 396 |
| RELAY-0027 | 0/8 | 2/8 | 5/8 | 180, 216, 360, 396, 468 |
| RELAY-0032 | 1/8 | 1/8 | 2/8 | 108, 468 |

Each cell alone is labelled TAIL_SPARSE, because the rule needs at least 2 cells for TAIL_CONTINUES.

### 1.2 Reading

The late-arrival tail continues at a steady rate. The (288, 576] window, which is 8 blocks of 36 generations,
produced 6 new lineages, against 3 in the 4 blocks of (144, 288]. That is about 0.75 new lineages per block in both
windows: the arrival rate has neither fallen nor risen.
- **It is not a RELAY-0019 artefact.** Leaving that cell out, 9/24 searches reach competence by 16x, up from 2/24
  at 4x.
- **RELAY-0027 matters most.** It was 0/48 in C2A BASE and 0/8 in C2B B4X, and it reaches 5/8 by 16x, all after
  gen 144.
- **Persistence is complete.** All 16 competent searches stayed competent at every later checkpoint.

C2B found scaffold-enabled reconstructive reachability (BRK1). Separately, ordinary unscaffolded search (these are
the B4X searches continued) reaches the competence class slowly: 16/32 within 16x, with arrivals still occurring at
16x.
The C1 budget censored it heavily (1/96 at 1x in C2A). Per the order, the budget is not escalated further.

### 1.3 DESCRIPTIVE

- The 16 cumulative successes are 7 found by gen 144 (C2B's B4X) plus 9 new.
- Arrival generations are spread from 144 to 468 with no clustering.
- RELAY-0010 and RELAY-0032 stay low (2/8 each) through 16x. The rate differs by cell (0019 > 0027 > 0010 ≈ 0032).

## Part 2: PTE-C2C, FLIP operator x path geometry (2x2)

### 2.1 Frozen classification: **NEITHER_IMPROVES_WITH_SPARSE_EXCEPTIONS**

| arm | operator | start | successes / n | per cell (0000, 0004, 0099, 0167) |
|---|---|---|---|---|
| a: OP0_BASE | frozen | random | 0/32 (CP95 0-.11) | 0/8, 0/8, 0/8, 0/8 |
| b: OPB_BASE | block | random | 0/32 (0-.11) | 0/8, 0/8, 0/8, 0/8 |
| c: OP0_STEP | frozen | graded stone | 0/28 (0-.12), background 0 | 0/4, 0/8, 0/8, 0/8 |
| d: OPB_STEP | block | graded stone | 1/28 (.001-.18), background 0 | 0/4, 0/8, **1/8**, 0/8 |

**Contrasts.** None of the four is material:
- Mb, b vs a: 0 vs 0.
- Mc, c vs a: 0 vs 0.
- Md|b, d vs b: 1 vs 0, one-sided p .50.
- Md|a, d vs a: 1 vs 0, one-sided p .50.

Applying the predeclared interpretation: **operator/path explanations are weakened.** Neither the mechanism-blind
block operator, nor a graded partially functional stepping stone, nor the two together materially improve FLIP
accessibility within the C1 budget. Per the order, a true representation experiment becomes the next campaign.

The single success (FLIP-0099 OPB_STEP idx 0) is a SPARSE_EXCEPTION.
- It is lineage-attributed (share .94), with B .900.
- It is 3 lines from the plant.
- Its stone was B .628, built as changed-cue .876 against same-cue .381.
- It does not replicate across cells.

### 2.2 What this adds to C2B

C2B already ruled out a 4x budget, a copy/latch stone and two-edit proximity for FLIP. C2C now also rules out the
following, at the C1 budget:
- a line-block operator (block copy, move and replace);
- a graded partial stone, with or without that operator.

### 2.3 DESCRIPTIVE: graded stones are not retained as partial function

- **The stone's descendants win selection but lose its function.** In 22/28 (OP0) and 14/28 (OPB) STEP searches
  the final champion descends from the stone (share ≥ .5). Yet those champions sit at chance: median accuracy
  .505 and median B .51, against the stones' own median accuracy .612 and B .615 on the same held worlds.
- **The partial function erodes.** The plant (B ≈ .9) was retained 32/32 in C2A PSEED, and the C2B copy plateau
  (accuracy ≈ .675) persisted. A graded stone's partial mapping use near the selector's noise floor is neither
  climbed nor kept.
- **Candidate explanation (post-hoc, untested).** Selection on 8 training worlds (4 pairs) with shaping may not
  resolve B ≈ .6 partial function from noise-fit genomes. C2A M32 found that more selector worlds did not rescue
  BASE, but it was never tested from a graded start.
- **Block operator descriptives.** OPB did not shift BASE champions off chance: median B .502 under OPB against
  .500 under OP0. Under OPB the stone lineage went extinct more often (11/28 against 6/28).

### 2.4 Threats (from the prereg, plus observed)

- **FLIP-0004's plant is near the ruler margin.** That cell is 0 in every arm.
- **The stones are plant degradations.** A null for STEP means "graded near-plant starts do not help". It does
  not mean "no stepping stone exists".
- **OPB is one block family at one rate.**
- **Every result is at the C1 budget of 36 generations.** C2B showed that 4x did not help FLIP BASE; C2C did
  not combine B4X with OPB or STEP.
- **Same author.** The C2B external review is still pending; C2C has no external review.

## Part 3: Program status

- **RELAY-mh: reachable by ordinary search at long horizons.** 16/32 at 16x, and 9/24 without RELAY-0019. The C1
  and C2A "search limit" for RELAY-mh is mostly a budget artefact.
- **FLIP: inaccessible under every perturbation tested.**
  - Within 4x the budget: C2B.
  - At 1x, under a block operator, a graded stone, or both: C2C.
  - Across C2B and C2C, the only FLIP successes outside PSEED are 2 C2B BRK1 rebuilds and 1 unreplicated C2C
    OPB_STEP success (1/120 C2C searches).
- **Next campaign (needs the operator):** the FLIP representation experiment. Its candidate questions are recorded
  in PREREG_C2BX_C2C.md, and it is not designed yet:
  - a persistent mapping bit as first-class state;
  - an alternative instruction for the teacher-to-mapping update;
  - a larger program space;
  - a representation in which the mapping inversion is a single field.

  A cheap side question surfaced by section 2.3: are graded stones retained at M32, or at W0? That is optional
  and is not designed here.

## Files

- `REDUCE_C2C.json`
- `production/rows_C2C.jsonl.gz`: 152 rows.
- `production/pops_C2C.tar`: final populations, plus tags and parent logs for C2C.
- `PREREG_C2BX_C2C.md`, `FREEZE_C2C.json`, `PLAN_C2C.json`.
- `stones/`, `flight1/` and `flight2/`.
