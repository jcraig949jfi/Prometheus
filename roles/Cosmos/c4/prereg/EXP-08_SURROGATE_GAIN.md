# EXP-08 -- INSTRUMENT: does the one-step fit underestimate the gain? (prereg 2026-10-11, before data)

Origin: EXP-07 left a residual underprediction (~ -.04 median signed excess error at a >= .85) after the start-state
repair. H-GAIN: the surrogate's learned one-step map contracts faster than the system (fitted gain < a), and the
shortfall compounds over the k + 2 steps of an episode.

Measurement (planted systems only; the same 38 systems and seeds as EXP-07, so the fitted surrogates are identical):
- rho_fit = median over 256 stationary points Z of the spectral radius of the finite-difference Jacobian
  d step(Z, o) / dZ (deterministic part, distractor symbol o = V, eps 1e-3), in whitened coordinates (a similarity
  transform of the true linear map, so the truth is a; the onehot(cur) block has no dynamics from Z).
- shortfall s = (rho_fit / a)^(k + 2) - 1 per (system, k) cell.

Decisions fixed now:
- H-GAIN SUPPORTED iff median(rho_fit - a) over the a .95 systems <= -.01 AND Spearman(s, EXP-07 O1 signed excess
  error) over the a >= .85 cells >= .50.
- Otherwise H-GAIN REJECTED. Either way the surrogate stays unqualified; no instrument change is adopted here.

DISCLOSURE (added before this file was committed, decision rules above unchanged): a one-system smoke test of the
driver was run before the commit and printed an outcome value: G1 Res a .95 s .1 w1, rho_fit 1.021 (gap +.071,
i.e. AGAINST H-GAIN) for all three k. This was a process slip (the prereg should be committed before any run). The
rules were written before it and are not changed; the system is included in the analysis as planned.
