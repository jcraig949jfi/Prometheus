# W2-27: re-deriving W2-8 D10 and the C-A3 / X-MAT counts

> Saved by Nestor from the worker's returned text, condensed with every number kept. The harness blocks subagents from writing report files.
> - **Files:** `rederive.py`, `rederive.json` (run 2026-10-01 02:26Z, under 1 CPU-s).
> - **Data read:** all 144 C-A3 result files (1,296 checkpoints) and all 26 X-MAT result files.

## Answer
1. **The D10 premise was overstated, but it is not false where it was used.**
   - At the endpoint checkpoint of the 26 eligible runs, L_share ∈ {0, 0.6641, 1}. This reproduces.
     - "Eligible" means every D0 genome is not state-free, and at least one state-free genome appears.
   - The red-team's 84 distinct values span all 1,296 checkpoints of all 144 runs, so that is a different set.
   - Both of the red-team's counterexamples are ineligible:
     - 27000053 never has a state-free genome;
     - 7ae3_27000033 has state-free D0 genomes.
   - **The 8 / 4 / 3 counts reproduce exactly and never depended on the premise.**
   - The two event clauses are redundant at the endpoint in 26/26 runs.
2. **"Last checkpoint with" is the frozen design, not a coding bug.**
   - The code: `c_a3_internalize/run_ci.py:51` picks `last = next(c for c in reversed(checkpoints) if c["free"] > 0)`; `:53` then applies `free_in_L >= 0.8*free and L_share >= 0.5`. This matches the frozen docstring at `:20`.
   - `x_mat_internalize/run_xmi.py:191-197` reads the same checkpoint.
   - D10 is therefore a **validity weakness** of the design: one genome at one checkpoint counts as an event (ffa6 27000012, 27000024).
3. **C-A3 → CONFIRMED-FRAGILE stands. Four of W2-15's numbers are corrected:**
   - The p values are **two-sided 0.063 as coded and 0.62 at the final checkpoint**. W2-15 quoted the one-sided 0.031 and 0.31.
   - **The cell split is an eligibility effect.** 22 ffa6 runs are eligible against 4 for 7ae3 (p = 1.4e-4). Among eligible runs the split is 7/22 vs 1/4 (p = 1.0), so the D4 confound acts on eligibility.
   - "84-194 state-free genomes" should read **84, 13, 41 and 194 genomes** (101, 19, 84 and 194 organisms).
   - **Which runs persist depends on the reading.** Only 3 runs pass every strict reading: 7ae3 27000023, ffa6 27000046 and ffa6 27000048.
4. **X-MAT does not depend on which checkpoint is read.**
   - All 55 checkpoints in the 8 event runs that have state-free organisms in L give X ≤ 0.14 and attributed share ≥ 0.405, so every one is ENDOGENOUS_MATERIAL.
   - The replays are identical to the C-A3 records.
   - **W2-15's "4 persistent + 4 transient" qualifier for X-MAT should change.** Transience is about C-A3's recurrence, not a weakness of X-MAT.
   - "ARTIFACT-RISK, no positive control" stands; it is independent of D10.
   - W2-8's "X close to determined by L_share" should be **withdrawn**: X is read from organism bytes.

## Table 1: C-A3 event counts by reading (144 runs, 72 per cell; 26 eligible: ffa6 22, 7ae3 4)

| reading | events | ffa6:7ae3 | two-sided /72 | one-sided /72 | two-sided, eligible | runs |
|---|---|---|---|---|---|---|
| (a) as coded | 8 | 7:1 | 0.063 | 0.031 | 1.0 | 23*, 12, 20, 24, 46, 48, 51, 52 |
| (b) holds at the final checkpoint | 4 | 3:1 | 0.62 | 0.31 | 0.51 | 23*, 20, 46, 48 |
| (c) majority of checkpoints from first crossing | 4 | 3:1 | 0.62 | 0.31 | 0.51 | 23*, 46, 48, 52 |
| (c′) W2-8 "majority" (SF ≥ ½ of competent at the final checkpoint) | 3 | 2:1 | 1.0 | 0.50 | 0.41 | 23*, 46, 48 |
| (d1) at any checkpoint | 8 | 7:1 | 0.063 | | | as (a) |
| (d2) two consecutive checkpoints | 5 | 4:1 | 0.37 | | | 23*, 46, 48, 51, 52 |
| (d3) (a) plus L ≥ 0.5 from first crossing to end | 7 | 6:1 | 0.12 | | | (a) without 12 |
| (d4) (a) plus final L ≥ 0.5 plus SF in the last 3 checkpoints | 5 | 4:1 | 0.37 | | | 23*, 20, 24, 46, 48 |

\* 23 is the 7ae3 run (7ae3 27000023); all other numbers are ffa6 27000xxx runs.

## Table 2: the 8 coded events

| run | first SF → last | checkpoints with SF | at the final checkpoint | what happens |
|---|---|---|---|---|
| 7ae3 23 | 1600 → 2000 | 5/5 | L 1.0, 84 SF | persistent |
| ffa6 12 | 1600 only | 1/5 | L 0.03, 0 | one genome; L collapses |
| ffa6 20 | 400 → 2000 | 6/17 | L 1.0, 13 | passes (b), fails (c) |
| ffa6 24 | 1900 only | 1/2 | L 1.0, 0 | one genome |
| ffa6 46 | 700 → 2000 | 14/14 | L 1.0, 41 | persistent |
| ffa6 48 | 200 → 2000 | 19/19 | L 1.0, 194 | persistent |
| ffa6 51 | 1100 → 1200 | 2/10 | L 1.0, 0 | brief |
| ffa6 52 | 800 → 1600 | 8/13 (peak 112) | L 1.0, **0 competent** | competence dies out under L |

## Table 3: X-MAT at every tagged checkpoint

| run | checkpoints | max X | min attributed share | ENDOGENOUS throughout |
|---|---|---|---|---|
| 7ae3 23 | 5 | 0.000 | 0.955 | yes |
| ffa6 12 | 1 | 0.107 | 0.438 | yes |
| ffa6 20 | 5 | 0.041 | 0.472 | yes |
| ffa6 24 | 1 | 0.000 | 0.922 | yes |
| ffa6 46 | 14 | 0.090 | 0.473 | yes |
| ffa6 48 | 19 | 0.092 | 0.559 | yes |
| ffa6 51 | 2 | 0.140 | 0.781 | yes |
| ffa6 52 | 8 | 0.138 | 0.405 | yes |

The pre-registered X-MAT rule needs exactly 8 events, so it cannot be re-applied to 4. The qualitative reading carries over; the formal verdict does not.

## Decision on W2-15

| W2-15 item | decision |
|---|---|
| C-A3 → CONFIRMED-FRAGILE | **Stands.** Add: two-sided p values; 3 robust runs; the split is an eligibility effect; 13-194 genomes. |
| X-MAT "4 persistent + 4 transient" | **Change.** The verdict holds at every checkpoint. ARTIFACT-RISK (no positive control) stands. |
| W2-8 "L_share only {0, 0.664, 1}" | Narrow to "at the endpoint of the 26 eligible runs". |
| W2-8 "X close to determined by L_share" | Withdraw. |
| Red-team F11 | Partly right. The prose was too broad; the recount reproduces. |
| X-A3-SFLINEAGE | Same endpoint; not checked. |

## Adversarial points
- **Readings (b) and (c) both give 4 but pick different runs.** FRAGILE is the honest label.
- **Conditioning on eligibility is post-treatment.** It shows only that the ffa6 excess sits upstream.
- **No direction was pre-registered** (`run_ci.py:28`: per-cell counts are "secondary, never decisive"), so p values are two-sided.
- **Checkpoints within a run are not independent.** The claim is only that the result does not depend on which checkpoint is read.
- **Run 52's L = 1.0 with 0 competent genomes** may be the N13 ruler problem.
- **D10 is not a code defect, but it is a validity weakness.**

## Ledger entry (W2-27)
- **Inference.**
  - D10 is a design weakness, not a bug.
  - The counts reproduce.
  - Strict readings give 3-4 events, with 3 robust runs.
  - The cell split is not significant two-sided under any strict reading (p ≥ 0.37) and is explained by eligibility.
  - The X-MAT verdict does not depend on the endpoint.
- **Confidence.** High for direct reads. Moderate for which readings count as "sensible".
- **Strongest objection.** Persistence may be a zero-register-screen artifact (run 52, N13). The true count could be higher.
- **Next questions.**
  - Re-screen run 52 after epoch 1600 with the victim-register screen.
  - Apply reading (b) to X-A3-SFLINEAGE.
  - Any re-confirmation should freeze a persistence endpoint and include a null arm.
