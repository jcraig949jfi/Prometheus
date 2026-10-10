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

## AMENDMENT E3R-A1 (pre-data; red team reviews/REDTEAM_E3R_PREFREEZE.md, 5717ba313: 2 BLOCKER / 7 MAJOR)

**ADOPTED IN FULL:**
- red-team s3 amendments A1-A12 (required A1-A4; recommended A5-A12);
- the rulings in s4 on decisions 1-9;
- the s5 claim limits.

They supersede this draft wherever they conflict. In particular:
1. **Censoring (A1).**
   - OE scratch is capped at 3,600 CPU-s.
   - CENSORED is a third state. Each cell gets LO / HI bounds; a cell whose bounds disagree is COUNTS_CONDITIONAL.
   - OE scratch runs lazily, only when an OE chain reaches 12.
   - One extension to 14,400 CPU-s is allowed for searches that decide the label.
   - OE scratch envelope: 16 core-h.
   - The frozen non-OE scratch is a secondary control only.
2. **X-ABS text = the implemented rule (A2):**
   - the dual reducer is allowed (an antitone context swaps max / min), disclosed as added after seeing W6eb945cc;
   - probes = lists of length 0..max dev length plus all singletons over the dev element range;
   - only top-level `(map L xs)` nodes;
   - the highest valid ancestor wins.
3. **Seeds 0, 1, 2 for both OE cells and off_xabs are REQUIRED (A3).**
   - The trivialisation check reuses the seed-0 OE scratch; this is a declared deviation.
   - The label is STABLE / MAJORITY / SEED_UNSTABLE.
   - The PRIMARY output is the per-family attribution table: OE-only / X-ABS-only / both / either / neither.
4. **Interpretation map rewritten (A4).**
   - E3-R discriminates repair class WITHIN TFS-1. It does NOT discriminate CHANGE vs MIGRATE.
   - UNDERDETERMINED_STONE is split into UD-R1 (dev gap; WORLD) and UD-EXTRACT (with a global-equivalence check).
   - NONE + horizon-dominated: "no repair class identified at 1e6; horizon binding". This is NOT a CHANGE_SEARCH finding.
   - The MIXED reading lists the residual links.
5. **Fixed reading cell for NONE:** on_xabs (A5).
6. **off_xabs = 9 / 15 is KNOWN** (reviewer s3.2; red-team check), so DEVELOPMENTAL and EITHER are unattainable at seed 0. off_xabs runs first as a reproduction check. Its "8-10" prediction is withdrawn.
7. **X-ABS is a post-hoc single-motif patch.**
   - BOTH_REQUIRED reads "OE + post-hoc patch".
   - SEARCH must report whether X-ABS changed any stone in the OE cells (masking).
8. **Every label is conditional on the readout fallback.** on_xabs with fallback OFF is priority 2; if it disagrees, A1-C applies.
9. **Compute (A9).**
   - Envelope about 14 core-h, debited with concurrent load; <= 2 workers.
   - The run order is A9 order.
   - Start not before 2026-10-11 11:30Z.
   - At the hard stop, report what is complete. Otherwise REPAIR_CLASS = INCOMPLETE with bounds.
10. **Custody:** UTC start / end in every result file; FREEZE_E3R.json with git-blob hashes; an assert that the reused off_frozen cell = 7 / 15.
