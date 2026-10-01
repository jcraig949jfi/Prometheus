# W2-40: C3 and C3+AC bands under the class and exact keep rulers

> Saved by Nestor from the worker's returned text, condensed with every number kept. The harness blocks report-file writes by subagents.
> - **Run:** 2026-10-01 02:48:47Z–02:55:40Z. 46.5 CPU-s, static.
> - **Files:** `c3_bands.py`, `c3_bands.json`, `run.log`, `extra_power.txt`.

## Answer

1. **Under the class ruler, the C3 and C3+AC bands stay disjoint at n = 64.**
   - C3's keep-leveraged band (M3) moves from 0.865–0.990 down to **0.721–0.976**.
   - C3+AC's M3 band stays at 1.000.
   - The per-call bands (M2) are C3 0.018–0.127 and C3+AC 0.027–0.172.
   - The draft's ≥ 41/64 cut-off is slightly off: M3 at its class low end reaches ≥ 41 with probability only 0.94.

2. **Under the exact ruler, the C3 arm cannot tell the two mappings apart.**
   - C3: M2 0.014–0.086 and M3 0.022–0.167. The bands nest.
   - C3+AC: the bands overlap at counts 19–26, with worst-case power 0.47–0.53.

3. **The world counts births by FID and never tests keep. So class is the right ruler and exact is wrong.**
   - A birth requires `predecessor_accepts`: fid_other ≥ 0.90, fid_self < 0.90, and donor wrote ≥ 0.25n. `_fidelity` (world.py:1373) is the positional share of identical bytes.
   - BASE write-back is unconditional. An organism keeps its oid/anc unless it is itself converted.
   - So members that drift stay in the lineage, and their later births count toward B. Their FID m is about the parent's (W2-30).
   - Exact keep counts them as losses. For C3 at side 0, exact keep is 0.519 against class keep 0.955.

4. **Recommendation: freeze the class bands.**

   | arm | M2 cut-off | M3 cut-off |
   |---|---|---|
   | C3 (n = 64) | ≤ 14 | ≥ 32 (≥ 39 raw) |
   | C3+AC (n = 64) | ≤ 17 | ≥ 41 |
   | AC (n = 384) | M2 is killed at ≥ 28 (was ≥ 27) | — |

## Static inputs (averaged over sides)

| ruler | F | AC | C3 | C3+AC |
|---|---|---|---|---|
| FID keep / conv / m / geometric ratio | .714 / .438 / 1.172 / 1 | .760 / .511 / 1.248 / 1.39 | .940 / .436 / 1.389 / 4.75 | .981 / .505 / 1.469 / 16.94 |
| class keep / m / geometric ratio | .703 / 1.154 / 1 | .755 / 1.239 / 1.43 | .924 / 1.368 / 3.91 | .975 / 1.462 / 13.77 |
| exact keep / m / geometric ratio | .494 / .847 / 1 | .701 / 1.175 / 2.51 | .595 / .943 / 1.24 | .773 / 1.253 / 3.34 |

Cross-checks:
- FID agrees with W2-32 to within 0.0013.
- Class and exact agree exactly with W2-30.
- FID reproduces `calc_bands.json` M1/M2/M3 exactly.

## Bands: P(B ≥ 163) mapped to a count band

| arm (n) | ruler | M2 | M3 | M1 | M2 vs M3 disjoint? |
|---|---|---|---|---|---|
| C3 (64) | FID | .020–.122 → 0–13 | .865–.990 → 50–64 | .957–.982 | yes |
| C3 (64) | **class** | .018–.127 → 0–14 | .721–.976 → 39–64 | .896–.960 | **yes** (gap 15–38) |
| C3 (64) | exact | .014–.086 → 0–10 | .022–.167 → 0–17 | .088–.150 | **no** |
| C3+AC (64) | **class** | .027–.172 → 0–17 | 1.000 → 64 | 1.000 | **yes** |
| C3+AC (64) | exact | .050–.294 → 0–26 | .419–.946 → 19–64 | .784–.905 | no |
| AC (384) | class | .010–.048 → 1–27 | .037–.238 → 8–108 | 6–58 | no |
| AC (384) | exact | .033–.213 → 6–98 | .197–.826 → 61–331 | | no; power 0.98 |

**Power at n = 64 under the class ruler:**
- M3 at 0.72: ≥ 41 with probability 0.938; ≥ 39 with 0.981; ≥ 32 with 1.000.
- M3 at 0.625 (the allowance floor): ≥ 32 with 0.985.
- M2 at 0.127: ≤ 14 with 0.987.
- M2 at 0.172: ≤ 17 with 0.980.

## Adversarial points
1. **The class ruler was not chosen to fit these results.** It was fixed in W2-30, before this scoring, and here it moves the band *against* the draft.
2. **Class over-counts** halves that are broken at sites outside the class set. The effect is small and in the same direction as FID.
3. **Class under-counts** C3 reverting to F. That pushes M3 down, so the true band is a little higher.
4. **Exact predicts the wrong world.** Under exact, AC's geometric ratio beats C3's (2.51 vs 1.24), against every functional ruler.
5. **Kin partners after expansion** are not modelled. This is inherited from W2-32.
6. **M2's B counts keeps, while the world's B counts P-11 conversions.** Calibration fixes only the scale. Inherited from W2-32.
7. **The allowance floor is bracketed.** Both ≥ 32 and ≥ 39 stay disjoint with power ≥ 0.98.

## Ledger entry (W2-40)
- **Inference.**
  - Class is the right ruler.
  - D1 stays decisive at n = 64 with C3 at ≤ 14 / ≥ 32 and AC's M2 kill at ≥ 28.
  - Exact would make C3 uninformative, but exact misdescribes the world.
- **Confidence.**
  - High for the arithmetic and the code reading.
  - Moderate that class is the best proxy.
- **Strongest objection.** The B-definition mismatch inherited from W2-32 (adversarial point 6).
- **Next.**
  1. A class-plus-still-copier ruler.
  2. Kin and self-carried contexts (W2-41).
  3. Update the draft's §5 before freeze, with Nestor's sign-off.
