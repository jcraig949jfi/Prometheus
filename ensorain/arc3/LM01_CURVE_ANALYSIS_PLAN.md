# LM01 curve analysis plan (DESCRIPTIVE; written 2026-09-28 before any campaign row exists)

This does NOT change any frozen verdict. The frozen analysis (ensorain/lm01/analysis.py, freeze 768ea8ce9) gives the
verdicts. This plan names the curves and the shape classifications read BESIDE them (directive Blocks D, E, K). Every
shape rule below is fixed now.

## 1. Reservoir ladder shape (Block D, M)

- Per stratum, the median AC (never-seen / fresh-field / OOD headline set) of random eviction at B/n for the rungs
  c/8 .. 2c, plus the full store (the warm endpoint) and L-R (the declared endpoint).
- Shape classes, using the 90% paired CI of adjacent-rung differences at DELTA .30:
  - MONOTONE_GAIN: no adjacent decrease beyond -DELTA, and full - c/8 > DELTA.
  - SATURATING: B* exists (BOUNDED_SUFFICES as reported by the frozen analysis) and the rungs above B* are EQUIVALENT
    to full.
  - INTERIOR_OPTIMUM: some rung beats BOTH its lower neighbour and the full store by > DELTA.
  - EXCESS_HURTS: full < max(bounded) by > DELTA (the directive-J candidate).
  - FLAT: all rungs EQUIVALENT to full (history quantity irrelevant).
  - UNRESOLVED otherwise.
- Tabulated by family x level x generator. The phase-diagram candidate is shape vs (family, world size, visits/cell).

## 2. Storage vs readout compression (Block E)

Four cells from existing LM01 arms (no new runs):

| cell | storage | readout | LM01 arm |
|------|---------|---------|----------|
| exact + simple | exact store | unlearned kernel | L-K |
| exact + complex | exact store | per-query refit | L-R |
| compressed + simple | bounded learned state | the substrate readout | SELECTIVE ladder point at matched state bytes |
| compressed + complex | bounded factors + B records | warm refit | reservoir at B = c/8 (smallest) |

- Reported per stratum: AC for each cell. Main effects: storage (exact - compressed) and readout (complex - simple).
- Plus bytes and query ops, so the "compression" is located where the effect sits.
- Caveat, fixed now: the simple/complex readouts are not matched in optimizer (SGD vs ALS), and this plan cannot remove
  that confound. T12 / PKG-S1 do.

## 3. Compute trade surface (Block K)

- Per stratum, points (persistent bytes, query ops, fit ops, AC) for every arm and rung, from the measured meters.
- Pareto front in (bytes, query ops) -> AC.
- "Compute substitutes for compression" is read as: along the front, AC at fixed bytes rises with query ops (L-R vs
  S-ladder), and AC at fixed query ops rises with bytes (the reservoir ladder).
- Reported as the front plus the two slopes. No exchange-rate scalar.

## 4. Recoverability vs accuracy (storage information vs used information)

- HR2 (recoverable history) vs AC per reservoir rung and eviction policy.
- The Block-E question "how much retained information is used" is read as the AC gain per unit HR2 along the ladder.
- A steep AC rise at nearly constant HR2 means the readout, not storage, is binding.

## 5. Switching (F3), transfer (F4), nuisance (F5): descriptive slices

- F3: the recency-aware frozen LOSSLESS (L-R-rec) vs the recency-blind endpoint, per generator: the size of the
  "readout cannot find relevant history" effect (directive H).
- F4: fresh-field AC vs the source-field never-seen AC, per arm: how much of the source competence transfers.
- F5 (repaired scale): headline AC with the nuisance coordinate at test uniform, vs the same arm's in-distribution AC
  (the nuisance cost), per arm.

## 6. Known-answer (F1) and calibration

F1 lossless_must_win is reported as calibration only (Block L). A failure there is an INSTRUMENT_FAILURE flag for the
curve analysis, not a science result.

## 7. Output

- ensorain/arc3/LM01_CURVES.md (tables);
- ensorain/arc3/lm01_curves.json (all numbers);
- plots are optional and rendered off M2.
Script: ensorain/arc3/lm01_curves.py, to be written and tested on DEV rows (dev/margins) BEFORE the campaign rows exist.
