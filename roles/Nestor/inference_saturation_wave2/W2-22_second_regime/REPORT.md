# W2-22: is there a kin/density "second regime" under BASE (7ae3, X-TICKET cell)? Also: the ATOMIC horizon check

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Run conditions:** about 66 CPU-min of the 90 allowed, at most 6 processes, `python -B`. No git writes.
> - **Pre-registration:** 2026-10-01T01:42:57Z, written before any run. Last timestamp 02:05:02Z.
> - **Files:** `PREREG.md`, `w22.py`, `v1_equiv.py/.json`, `p1_run.py`, `runs_FIELD.jsonl` / `runs_FREE.jsonl` / `runs_ATOMIC_world.jsonl`, `a1_analyze`, `a2_adversarial`, `a3_atomic`, `s1_mech_smoke`, `log_*.txt`.

## Answer
- **Second regime: NO SECOND REGIME under the pre-registered rule.**
  - Kin pairing plus density (FIELD BANK) does not make large lineages persist more than free branching (FREE BANK).
  - Under the censoring treatment most favourable to FIELD (C−), the conditional ratio is 1.31, Koopman 95% CI [0.60, **2.80**]. The whole interval lies below 3x.
  - Under C+, FIELD is significantly *lower*: 0.27 vs 0.65, p = 0.0014.
  - **Fragile at the edge.** Katz gives an upper bound of 2.87 and a percentile bootstrap gives 3.15, which would make it UNRESOLVED. Koopman was the pre-registered method.
- **New finding: the world persists more than FIELD BANK** (4/4 vs 9/33, p = 0.011). So whatever drives persistence is not kin or density. If it is real, it lies in the realized FULL background: background–background interactions and residue. That is the circular rung 5.
- **ATOMIC: horizon censoring is excluded.**
  - The world at 300 epochs equals the world at 2000 epochs, seed for seed (30/30; 20/30 with depth ≥ 20).
  - W2-14's "0.23 vs 0.67" compared different readouts: `depth_f` (founder tree) against `depth_world` (whole-field causal depth).
  - On identical readouts the model under-predicts slightly, and no difference is significant.

## Eligibility and equivalence
- **Pre-computed eligibility:** 30 conditioned runs expected. Realized: FIELD 33/600 (0.055), FREE 48/1200 (0.040). Both ELIGIBLE.
- **Seeds:** fresh, starting at 1000.
- **Equivalence check:** `run2` equals `ffield.run` on 43/43 runs.

## Results (BASE, horizon 300)

| arm | n | B ≥ 27 | P(B ≥ 163) | P(≥163 \| E27), C+ | P(≥163 \| E27), C− | B_xk, C− |
|---|---|---|---|---|---|---|
| FIELD BANK | 600 | 33 | 0.015 | 9/33 = 0.27 | 0.27 | 5/33 = 0.15 |
| FREE BANK | 1200 | 48 | 0.047 / 0.008 | 31/48 = 0.65 | 10/48 = 0.21 | 10/48 = 0.21 |
| ratio | | | | 0.42 [0.23, 0.72] | **1.31 [0.60, 2.80]** | 0.73 [0.28, 1.82] |

- **C+ and C−:** 21 of the 48 conditioned FREE runs stopped at the 256-member cap with B < 163. C+ counts them as successes and C− as failures.
- **Middle treatment** (a cap counts as success only if B ≥ 100): 15/48, CI [0.43, 1.70].
- **B_xk:** births onto victims that were not already members.

**Rule check:** SUPPORTED needed Fisher p < 0.01 under C+; it got p = 0.9998. NO SECOND REGIME needed the C− CI upper bound below 3; it is 2.80. → **NO SECOND REGIME.**

## Mechanism observations
The mechanism arms were not run: the pre-registration made them conditional on SUPPORTED, and the budget did not allow them.
- **4 of FIELD's 9 successes come only from kin-on-kin births.** Their B_xk is 89–153. Extreme case s1196: B = 15,322, of which 15,169 are kin births.
- **Saturated fields go sterile.** These runs fill all 256 slots and then make 0 certified births in their last 50 epochs: s1536, 1286, 1330, 1471.
- **Smoke test.**
  - M1 lowers maxA from 227 to 99 on s1579, but the runaway still happens.
  - **M2 design flaw:** every kin overwrite falls in the "eroded" class, so fidelity < 0.9 does not separate repair from overwrite. Redefine M2 before any arm.

## ATOMIC: world at 300 epochs vs W2-14 model (seeds 0–29)

| readout | world | model | p | both / world only / model only / neither |
|---|---|---|---|---|
| depth_world ≥ 20 | 20/30 | 14/30 | 0.19 | 9/11/5/5 |
| depth_f ≥ 20 | 5/30 | 7/30 | 0.75 | 0/5/7/18 |
| B ≥ 163 | 14/30 | 10/30 | 0.43 | 5/9/5/11 |
| maxA ≥ 40 | 20/30 | 14/30 | 0.19 | 9/11/5/5 |
| B ≥ 27 | 19/30 | 12/30 | 0.12 | 6/13/6/5 |

- The pre-registered branch reads "mixed". That branch had assumed a single readout.

## Adversarial round
1. **C+ is a cap artefact.** Yes. That is why the verdict uses C−, which favours FIELD.
2. **The verdict depends on the CI method** (2.80 / 2.87 / 3.15). Confidence is medium.
3. **B is inflated by kin births in FIELD.** This is conservative for the NO verdict. On B_xk the ratio is 0.73.
4. **FIELD BANK erases background residue.** The world-vs-FIELD-BANK gap points exactly there, so the question moves to residue.
5. **The "frozen" stop rule.** Its bias is probably small.
6. **Seeds.** W2-14's own seeds point the same way.

## Ledger entry (W2-22)
- **Inference:**
  - Kin plus density does not create a persistence regime. Under C+ the field lowers persistence.
  - Part of FIELD's B ≥ 163 is kin re-conversion inside an already-filled field.
  - The world's extra persistence (4/4 vs 9/33), if real, needs the realized background.
  - F's ATOMIC gap was a readout mismatch, not horizon censoring.
- **Confidence:**
  - medium: NO SECOND REGIME;
  - high: horizon excluded;
  - medium: ATOMIC readout mismatch;
  - low: the world vs FIELD BANK gap (4 events).
- **Next questions:**
  1. Seed-matched FIELD FULL vs FIELD BANK on B_xk (about 3x the cost).
  2. A FREE run with no 256 cap.
  3. ATOMIC with matched readouts at about 100 seeds.
  4. Redefine M2's "eroded".
