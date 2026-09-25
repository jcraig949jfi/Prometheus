# D-series Round 3 report (local design inside the competent regime)

Currency: 2026-09-24. Rows d3_round3.jsonl (4,800 lives, all OK);
analysis d3_round3_analysis.json / _stdout.txt (ensorain/d1/analyze.py
generalised, committed at e02119d46 before the rows).

CONTROLS PASS: shuffled ruler nominates 0 pairs; planted kappa x noise
nominated (q ~ 0). INSTRUMENT POSITIVE CONTROL: p_restruct x start
NOMINATED on NLMSE (F 8.3, q .010, validation pattern r 1.00). The
instrument sees real mechanisms here, so Round 3's nulls count.
But the control's SHAPE refutes the seat's mechanism story: restructuring
hurts a correctly ordered memory most (NLMSE .135 -> -.135 across
p_restruct terciles) and does NOT rescue a wrongly ordered one (-.25 ->
-.34). Accepting swaps on a noisy batch is destructive; "restructuring
can only help a wrong start" was false. Recorded in the ledger.

ORGANISM-INTRINSIC COUPLINGS on NLMSE (unclipped competence ruler):
  scratch x start   F 17.9, q 2.3e-6, r .99, survives rank scale.
                    Larger scratch helps both, but twice as much with the
                    right representation (+.47 vs +.23 across terciles):
                    timescale separation pays when the structure is right.
                    Amplifier, not crossover.
  cap x replay      F 5.0, q .015, r .95 (not in rank scale). Replay
                    costs only under capacity pressure (lowest cap tercile
                    -.16 -> -.33; neutral with slack). Seat P2 half-right:
                    the cost appears, no benefit does.
EFF nominations are dominated by x kappa (price x compute: accounting),
plus scratch x cap, scratch x start, scratch x drift.
T2 PHASES: not supported (12% learn; coupled model log-loss worse by
2.4%). T3 PRECURSORS: none (319 firing lives; surprise falls before FIRE
in both halves, -.70 / -.41, but q .40).
MAIN EFFECTS (NLMSE, disc/val): scratch +.35/+.32, drift -.20/-.18,
lam +.17/+.15, p_restruct -.17/-.14, sweeps -.16/-.17, forget +.14/+.12,
cap +.14/+.18; start dominant (Kruskal H 281).
Seat predictions: P1 control nominated RIGHT, crossover WRONG, mechanism
WRONG; P2 replay x cap RIGHT in part; P3 lam x drift WRONG; P4 at most 4
besides control: WRONG on EFF (11 distinct incl. accounting), RIGHT on
NLMSE (2); P5 phases not supported RIGHT.
Round 4 (fixed in PREREG_D3): fresh-seed grids for all 11 non-control
nominations, ensorain/d1/round4.py, alpha .05/11.
