# RESULTS WTP-05 sub-assay E2: two-axis revival of WTP-04 dead families (C-014-E2)

Seat: Ensorain[ubu006-4b001784]. Date: 2026-10-10.
- Prereg: ensorain/wtp5/PREREG_E2_REVIVAL.md, committed before any row (232dbe90f), plus its runner-robustness
  amendment.
- Rows: ensorain/runs/wtp05/revival/e2.jsonl (270 units). Score: ensorain/runs/wtp05/revival/e2_score.json.
- Wall time: ~3 h. The first 81 rows ran on 3 workers. The resumed 189 rows ran on 2 workers next to SCREEN and
  took 8,132 s. The log shows LAPACK DLASCL warnings, which suggest the crashing units fed NaN input to the SVD.

## Verdict per family (preregistered rule: a cell pays only if both seeds pay)
| family | verdict | paying cells | cell labels (45 cells) |
|---|---|---|---|
| F01 | NOT_REVIVED | 0 | 40 DEAD, 4 SPLIT, 1 ILLEGAL |
| F06 | NOT_REVIVED | 0 | 45 DEAD |
| F11 | NOT_REVIVED | 0 | 39 DEAD, 6 ILLEGAL |

## Predictions
- **R1 (F01 and F06 NOT_REVIVED): HIT.**
- **R2 (F11 SINGLE_AXIS_REVIVAL via memory): NOT CONFIRMED and UNRESOLVED (see the crash mask below).** It is not
  scored as a refutation.
- **R3 (no COUPLED_REVIVAL): HIT.**
- **R4 (any coupled revival is memory x price): MOOT.** There is no coupled revival.

## Failure shapes (unit level; recorded, not promoted to cell verdicts)
1. **F11, band .5: a crash mask.**
   - Seed 41005001 is CHEAP_PAYS in 6 cells, with the constant carrier the winner:
     - change static and change p800;
     - price x.01, x.1 and x1;
     - noise native.
     - In each, best cheap .056-.061 beats trivial .039-.045 and clears the margin .011.
     - This is WTP-04's band=.5 CHEAP_PAYS cell, reproduced on a fresh seed.
   - Seed 41005002 crashed with numpy LinAlgError ("SVD did not converge") in exactly those 6 cells. Each crash
     became ILLEGAL, so none of the 6 cells can pay.
   - In the 3 band-.5 cells where seed 2 ran (change p200, noise sd=0, noise sd=.1), both seeds are DEAD.
   - So the F11 band-.5 island is neither confirmed nor refuted by E2.
   - The crash sits in the frozen WTP-04 harness. It was not patched, because WTP-04 code stays frozen.
2. **F01, cheaper information: a one-seed structured pay.**
   - Seed 41005002 is STRUCT_PAYS at price x.01 and x.1, at memory band native and band .1:
     - winner tt; best structured .61 against best cheap .56 and trivial .57;
     - oracle .93; H .12.
   - Seed 41005001 is DEAD in the same cells, so the cells are SPLIT.
   - This is the only structured-carrier pay in any dead family across WTP-04 and E2.
   - It is a single axis (price), not a coupled one, and it does not replicate across seeds.
3. **F06: DEAD in all 90 units.** No grid point moves it.

## What this does and does not establish
- No WTP-04 dead family is revived by any memory x change, memory x price or memory x noise point under the
  preregistered two-seed rule. No revived world is added to WTP-05 as a test environment.
- The F11 band-.5 question remains open because of an instrument defect (7 crash units in 270, 6 of them in
  one place).
- Resolving it needs either a numerically guarded harness, which would be a new versioned harness and not
  WTP-04, or a third seed. Neither is run here. Either is a preregistered follow-up for the operator to call.
- The F01 price result is a lead, not a revival.
