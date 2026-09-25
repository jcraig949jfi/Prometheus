# D-series Round 2 report (confirmation) + exploratory boundary check

Currency: 2026-09-24. Rows d1_round2.jsonl (3,192 lives, all OK), score
d1_round2_score.json / _stdout.txt (ensorain/d1/round2.py, 163d50a54).

INSTRUMENT CONTROLS FAIL in the RANDOM background: N1 world x org (true by
construction) p .029 > .0083 (pattern r .86); N5 sweeps x kappa
(accounting) replicated. By PREREG_D2 the RANDOM background is
under-powered: no null in it is evidence. Cause: about half the
random-background lives sit at the clipped R^2 = -1 floor, which
compresses every coupling, true ones included.

    nom  pair                     RANDOM p   r      COMPETENT p   r
    N1   world x org    (R^2)     2.9e-2    .86     ~0 (F 26.5)  .78
    N2   lam x org      (R^2)     8.8e-4    .93 REP 2.7e-2       .00
    N3   forget x org   (R^2)     .94       .95     .83          .17
    N4   scratch x surprise (R^2) 9.7e-3    .57     1.6e-2       .94
    N5   sweeps x kappa (EFF)     1.4e-6    .92 REP .45         -.19
    N6   cap x org      (EFF)     .57       .69     8.1e-12      .73

The organism-intrinsic candidate N4 misses both thresholds. In the
COMPETENT background its shape matches Round 1 (r .94): large scratch
helps (R^2 .60 at scratch 319 with surprise .33) and surprise weighting
hurts, the scratch benefit shrinking as surprise weighting pushes lives
toward the floor -- two main effects compressed by a floor, not a
crossover.

EXPLORATORY (not preregistered; ensorain/d1/boundary_explore.py): the
DIVERGED / not split (49% of Round-1 lives) is predicted by main effects
alone at validation AUC .860; adding all pairwise couplings gives .860
with worse log-loss. Divergence drivers: TT memory, low lam, many sweeps,
surprise weighting, disturbance, noise.

Running reading after two rounds: in these worlds, competence and its
failure are governed by MAIN EFFECTS; the couplings found are
construction artifacts or floor compression. The phase-behaviour thesis
is not supported HERE -- but uniform random dials put 97% of lives in
dead regions, a weak place to look for couplings (hence Round 3).
