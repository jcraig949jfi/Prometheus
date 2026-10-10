# E3-R: REPAIR-CLASS DISCRIMINATION FOR STONE ACQUISITION (NEW PRE-REGISTRATION; DRAFT, NOT FROZEN)

C-015, W04. Written after independent review v1 (reviews/INDEPENDENT_REVIEW_RESULTS_v1.md; response
reviews/COORDINATOR_RESPONSE_REVIEW_v1.md). A new preregistration under the directive. It does NOT re-test or relabel
any frozen Beta-04 label (TFS1_INSTRUMENT_QUALIFIED = NO stands). It cannot produce COMPOSITIONAL_DISCOVERY: stones
still come from R1 tasks indexed by the sealed decomposition. Its output informs ONLY the recommendation (which repair
class the evidence supports).

## Question
The first demonstrated failure is stepping-stone ACQUISITION. Which repair class removes it?
- **SEARCH:** observational-equivalence (OE) pruning, exactly as built and frozen in FREEZE_E3KP (`oe=True`); it
  enlarges the effective size-class coverage at 1e6.
- **DEVELOPMENTAL:** a refactoring-invariant stone extraction (X-ABS, below).

Both are crossed in a 2x2 at matched budget.

## Known before this prereg (stated so the reader can discount)
1. **Reviewer exploratory (s3.2, 133 CPU-s, not committed):** with readout-of-map stones for the 3 mis-cut units, the
   seed-0 chain qualifies 2 of 5 affected families; the about 9 / 15 projection is the reviewer's.
2. **E3-KP pilot OE row:** 7 / 7 chain-qualified (exposed pilot_v2; scratch incomplete).
3. **E3-KP production seed rows:** 9 / 15, 8 / 15.

## Extraction X-ABS (to be implemented and frozen before any production run; target-blind, dev-only)
For an R1 program P of kind f / p / s with a closed lambda L of the kind's type as the function argument of a
`map` / `filter` / `foldl` / `scanl` / `zipw` node N:
1. **Candidate set.** L itself, plus every ABSORBED candidate L' = (lam x C[(L x)]), where P = C_out[R(N)] and C is
   an enclosing Int context on the path from N's reducer R up to the root. Only for kind f, and only where R is one of
   max / min / head / last (element-selecting reducers).
2. **Validity check (target-blind).** Rewrite P to P' = R(map L' xs). Keep L' only if P' and P agree on ALL dev
   inputs AND on a fixed, target-blind probe set of 200 random lists (seeded; elements drawn from the union of the R1
   dev input range). The check uses P's outputs, not the sealed mechanism.
3. **Choice.** The MAXIMALLY absorbed valid candidate (largest C) is the stone. Ties go to the smaller term.
4. **Scope.** For kinds p and s, X-ABS = the frozen rule (no absorption defined). The readout fallback is applied as
   in the frozen rule when no lambda exists.

## Design
- **Cells:** {OE off, OE on} x {X-FROZEN, X-ABS}.
- **Fixed:** seed 0; B = 1e6; max size 12; the 15 production families; E3-KP rules for R1 attempts, chain search,
  judging (test + tribunal), first-failing-link labels; fallback ON.
- **Reuse:** the cell OE-off x X-FROZEN = the E3-KP primary (7 / 15), reused from runs/kp_production, not re-run.
- **Secondary:** cell (OE on, X-ABS) at seeds 1 and 2, only if compute allows (priority 3).

## Outcomes (frozen at freeze)
Per cell: pooled chain-qualified / 15, with scratch fails taken from E3-KP (15 / 15 at seed 0; scratch under OE is
re-run in OE cells, per A3.5).

| Label | Rule |
|---|---|
| **REPAIR_CLASS = SEARCH** | OE on x X-FROZEN >= 12 / 15 AND OE off x X-ABS < 12 |
| **REPAIR_CLASS = DEVELOPMENTAL** | X-ABS x OE off >= 12 AND OE on x X-FROZEN < 12 |
| **REPAIR_CLASS = BOTH_REQUIRED** | only OE on x X-ABS >= 12 |
| **REPAIR_CLASS = EITHER** | both single-factor cells >= 12 |
| **REPAIR_CLASS = NONE** | no cell >= 12. The first failing link of the best cell is reported. |

- Scratch-fail >= 12 / 15 is required in any cell counted as >= 12; otherwise that cell is marked TRIVIALISED.
- Each cell's first-failing-link counts are reported.

**Interpretation for the recommendation (fixed now):**
- SEARCH / DEVELOPMENTAL / BOTH_REQUIRED / EITHER support CHANGE_SEARCH_OR_DEVELOPMENTAL_MACHINERY, naming the class.
- NONE with horizon-dominated links: still CHANGE_SEARCH (larger search change needed).
- NONE with UD-dominated links after X-ABS: points toward the WORLD (foundry identifiability) or MIGRATE. This is
  stated together with the AR-1 result.

## Predictions (before data)
- OE on x X-FROZEN: 9-11 / 15 (OE cures horizons but not mis-cuts).
- X-ABS x OE off: 8-10 / 15.
- OE on x X-ABS: 11-14 / 15.

Most likely REPAIR_CLASS = BOTH_REQUIRED or NONE.

## Compute
- The OE R1 searches are shared across the two OE cells. Chain searches differ per cell.
- Projection: 3.3-7 core-h for the OE cells (E3-KP A3 projection) + about 0.5 core-h for X-ABS x OE off.
- Run ONLY when the rolling 24 h window has room: not before about 2026-10-11 11:30Z.
- <= 2 workers.
