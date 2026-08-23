# Pre-registered prediction — iteration 26, before running arms

## Weakness addressed
The compressibility predictor is LINEAR interpolation of the P3d-P3c gap on oracle
ceiling, fitted to two anchors. Nothing has tested linearity. The three interior
residuals so far are all negative — F_MT -0.001, F_M -0.015, F_M2 -0.021 — which is
3/3 same sign (sign test p = 0.25, suggestive of slight concavity, not significant).
A fourth and fifth interior point are needed, and ideally at a HIGH ceiling where
the band excludes zero.

## Stronger design than another permutation variant
Both new points vary the ACTION COUNT (5 and 6) rather than the permutation knob.
Every family so far differed only in how many actions permute. If the predictor is
really a function of ceiling, it must work when the ceiling is moved a different
way. If it only works along the permutation axis, it is a fit to one knob.

## Structure measured first, arms not run
  F_MT 5 actions: ceiling 0.810 -> predicted +0.212
  F_MT 6 actions: ceiling 0.870 -> predicted +0.234

## Falsifiers
  F1. Either measured 20-seed gap falls outside its band (+/-0.082).
  F2. Both residuals negative AND larger in magnitude than 0.04, which with the
      three existing negative residuals would make 5/5 same sign (sign test
      p = 0.031) and indicate real curvature — the linear predictor would then be
      systematically biased and must be replaced.

---

## VERDICT â€” BOTH FALSIFIERS FIRE

```
family            ceiling  predicted  measured  residual   band
F_MT 5 actions      0.810    +0.212    +0.075    -0.137    OUT
F_MT 6 actions      0.870    +0.234    +0.023    -0.212    OUT
```
Residuals across all five interior points: -0.001, -0.015, -0.021, -0.137, -0.212.
5/5 negative, sign test p = 0.062. F2 fires on magnitude.

The predictor was NOT a function of oracle ceiling. It was a fit to the
PERMUTATION axis. Move the ceiling a different way â€” by adding actions â€” and a
family with ceiling 0.870, nearly as compressible as abelian F_T (1.000), shows a
gap of +0.023 against F_T's +0.284.

This retro-invalidates the two earlier "discriminating out-of-sample successes":
all five original families shared n_actions = 4, so the predictor was interpolating
WITHIN one knob, never generalising across knobs.
