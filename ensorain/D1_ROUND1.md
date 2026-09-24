# D-series Round 1 report (exploratory; nominations, not results)

Currency: 2026-09-24. Rows ensorain/runs/d1_round1.jsonl (4,800 lives,
4,797 OK, 3 ERROR), analysis d1_round1_analysis.json / _stdout.txt, both
produced by ensorain/d1/analyze.py frozen at db02e27a6.

Controls: shuffled ruler nominated 0% of pairs; the planted cap x persist
coupling was nominated (q ~ 0). Section B is powered and valid.

T1 COUPLINGS -- 14 distinct replicated pairs, NO crossovers. Classified
here by the SEAT (a reading, written before Round 2):
  by construction (accounting: EFF = (U - U_NOMEM)/P and U contains
    price x compute): sweeps x kappa, scratch x kappa,
    err_frac x kappa; lam x cap (P in the denominator) plausibly
  by construction (definitional): world_family x org_family (structure
    match, known from E2); org_family x start (start only defined for
    TT/LR); org_family x {lam, forget, cap, scratch, replay, disturb}
    (each knob acts on a different parameter array per family)
  CANDIDATE (organism-intrinsic dial x dial, on competence, replicated in
    raw and rank scale): scratch x surprise_alpha  (timescale separation x
    surprise weighting), F 7.9, q 9e-5, validation pattern r .79.
T2 PHASES -- not supported. 2.4% of lives learn (held-out R^2 >= .5);
  the coupled logistic model is WORSE on validation (log-loss .148 vs
  .097). The real dichotomy in dial space is DIVERGED vs not: 54% of
  lives end at clipped R^2 <= -0.8.
T3 PRECURSORS -- none nominated (all q = 1.0).
MAIN EFFECTS dominate (held-out R^2, Spearman, disc / val, replicated):
  lam (stability) +.45/+.45; forget +.21/+.17; sweeps -.20/-.18;
  surprise_alpha -.17/-.18; disturb -.12/-.08; scratch +.12/+.10;
  err_frac -.08/-.09; noise -.07/-.05; replay -.05/-.10.
  Not replicated / ~0: dream_ratio, p_restruct, kappa (on R^2), persist,
  drift, cap. In a random background, every "plasticity" knob
  (low lam, disturbance, surprise weighting, deeper refits) HURTS and
  stabilising knobs (high lam, forgetting-as-shrinkage) help.
Seat predictions: P1 (main effects dominate) RIGHT; P2 (replay x drift or
lam x drift) WRONG -- neither nominated; P3 (dreams x noise) WRONG; P4
(precursor) WRONG.
