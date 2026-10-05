# D09 -- DEV WINDOW 9 REPORT

C-006, cycle 9, DEV. Evidence tier 2.

## 1. Midpoint synthesis 2
beta01/windows/MIDPOINT_2_SYNTHESIS.md. Limiting rung: **R3, the selection criterion on natural supply.** No positive
R7 yet.

## 2. Diagnostic (DEV-only; it exposes T08's breadth-12 families, which T09 therefore excludes)
G1-vs-PRISTINE mean per-family saving on the breadth-12 validation cells:
- seed 12: 0 positive families of 12. No criterion can help.
- seeds 4, 13, 14: positive families exist only among the extras.
- seed 9: strong positives (up to about 18k charges) mixed with losses. I_0's pooled lower95 rejects it; a subset
  criterion would accept.
- success seeds (3, 8): many positives.

Hence the g10 design.

## 3. Changes
- `gtc.py`: g10 (the subset-benefit criterion, `_select_subset`, TAU = 1000) plus the ORACLE10 / NULL10 variants.
  The g0 path is unchanged.
- `t09_subset.py`: fresh breadth-12 validation (excluding T08's exposed extras), 4 arms, gate and readout.

## 4. Qualification
- A synthetic unit check of `_select_subset`: the eligibility logic is correct (loss > gain rejected; sub-TAU
  rejected).
- Supply: 8/8 fresh extras in 15/15 seeds.

## 5. Compute
The rolling 24 h total is about 47.8 core-h. TEST-9 is held until about 12:45Z, when T53's block rolls off.
