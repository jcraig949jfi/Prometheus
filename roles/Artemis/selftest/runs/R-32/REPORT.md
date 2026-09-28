REPORT -- is a circuit's value a property of the world, the circuit, or its partner?

1. WHAT I SET OUT TO TEST
The Ludus bench measures hand-written decision rules ("circuits", e.g. the myopic
stopping rule r0003) inside exactly solved push-your-luck worlds. The seat first
concluded that a circuit's value is mainly a property of the world (on-policy
variance decomposition), then demoted that verdict after a state-occupancy
control, and left open whether a world-indexed representation r_i(W) would ever
beat a flat per-circuit catalogue. The record also contains a zero cell (r0003
with the optimal partner scores 0.0 on Coloretto) while the ledger still reads
"partial loss untested / first failure: none", and r0003 is blocked on its
maturity ladder by a "partner spread of 1.0000". I tested, prospectively
(held-out worlds), whether indexing circuits by world properties beats a flat
catalogue, both for predicting magnitudes and for the decision that matters
(which circuit to deploy); and I diagnosed what actually produces the zero cells
that motivated the "partner / world" story. Two sibling questions in the package
(the audited Martian Dice rules; whether adversaries create a new interface) I
touched only lightly or not at all -- see section 4.

2. WHAT I DID
Code and data: repository origin/main (6ff2b2f8a; the ludus/ tree is unchanged
since fb858dd5c). Exported with `git archive origin/main ludus` into
work/R-32/src and run there only. Inputs read: ludus/atlas/cycle004_partner_matrix.json,
cycle004_identified_design.json, cycle005_occupancy.json, transfer_matrix.json,
circuit_maturity.json, CIRCUIT_LEDGER.md, ludus/fossils/FOSSIL_r0003_2026-08-27.json,
roles/Ludus/CYCLE_004_VERDICT_basis_audit.md, CYCLE_005_verdict_demotion.md
(all @ origin/main). Scripts (all in work/R-32):
 - run_all.py a  : extended synthetic FOUNDRY factorial, 128 worlds =
   gate{0,1} x decoy{0,1} x arity{2,3} x capacity{2,4} x p_bust{.1,.25,.5,.7}
   x loss{ruin, 50% retained via DecayFoundry}. For each world: exact E cells
   (5 STOP circuits + optimal stop) x (5 SELECT partners + optimal select), and
   reference-occupancy regret per STOP circuit (the seat's own
   ludus/bench/occupancy.py estimand). Reproduction check: the 16 p_bust=0.25
   ruin worlds reproduce the committed cycle-4 matrix to max |diff| 5e-7 over
   576 cells.
 - analyse.py    : leave-one-world-out and leave-one-property-level-out
   prediction of held-out worlds. Predictors: FLAT (circuit mean over training
   worlds), IDX_ADD (per-circuit ridge regression on world-property dummies),
   IDX_INT (same plus all pairwise interactions), IDX_NN1 (mean of training
   worlds differing in exactly one property). Metrics: MAE of magnitudes;
   pick-regret (true best minus true value of the circuit the predictor would
   deploy); best-pick rate; Kendall tau of predicted vs true ranking.
 - run_all.py b  : Coloretto diagnosis (what r0003 does at the initial state).
 - tie_test.py   : r0003 as committed (`STOP iff not (e_gain > p_dead*pot)`)
   vs a one-character variant r0003s (`STOP iff e_gain < p_dead*pot`, i.e.
   continue on exact ties) against every partner in the 16-world cycle-4
   factorial, the 16-world "identified" design (p_bust varied) and in Lucky
   Numbers and Coloretto; cycle-4 decomposition recomputed with the variant
   using the seat's own decompose/rank_stability/leave_one_out.
 - real_worlds.py: the 4 reconstructed real worlds (Martian Dice, Can't Stop,
   Lucky Numbers, Coloretto), optimal partner, with Martian Dice as
   reconstructed (08-27) vs as audited (09-16, columns taken from the
   committed transfer_matrix.json), committed vs tie-fixed r0003.
 - run_all.py c  (recompute full audited Martian Dice matrix) timed out at 900 s
   and was abandoned; the committed transfer-matrix columns were used instead.
Outputs: work/R-32/out/{foundry_ext,analysis,coloretto_diag,tie_test,real_worlds}.json

3. RESULT
(a) The Coloretto zero, the Lucky Numbers zero, and the "fossil" gated-world
zeros are one instrument artifact, not a world or partner effect.
In Coloretto there are 0 death branches in 296,925 states, so r0003's risk term
is always 0; at the empty initial state pot=0 and expected immediate gain=0, and
the committed rule stops on the 0>=0 tie, banking 0. Same mechanism in Lucky
Numbers (no death) and in gated FOUNDRY worlds (pot is 0 until a zero-gain
prerequisite is taken, which is exactly what the optimal partner takes).
Continuing on exact ties (r0003s):
   world / partner=OPTIMAL          r0003 committed   r0003s
   COLORETTO                        0.000             0.999
   LUCKY_NUMBERS                    0.000             1.000
   FOUNDRY gate=1,k=3 (6 worlds)    0.000             1.000
In the fossil world FOUNDRY[gate=1,k=3,cap=4], r0003s equals the OPTIMAL stop
rule in all 6 partner cells (1.0, 0, .75, 0, 0, 1.0); the remaining "partner
spread 1.0000" is the partner's floor, which the optimal stopper shares.
Normalising each cell by the optimal stopper under the same partner,
r0003s retains >= 0.944 against every partner in all 18 worlds (committed
r0003: min 0.0). Coloretto is therefore not a test of partial loss at all (no
death event); the controlled partial-loss test already exists: r0003 = 1.000 in
all 64 DecayFoundry worlds (min 1.0) -- partial loss is not a cliff for r0003.
Aggregate effect of the fix on the cycle-4 identified decomposition is small
(circuit 0.0998 -> 0.1087, world 0.3497 -> 0.3377, cross-partner tau 0.972 ->
0.983) because weak-partner zeros dominate; its effect on r0003's own record is
total.

(b) Flat catalogue vs world-indexed r_i(W), 128 synthetic worlds, held-out world:
                         MAE     pick-regret  best-pick  rank-tau
  E, optimal partner
    FLAT                0.199    0.0043       0.79       0.76
    IDX_ADD             0.112    0.0047       0.80       0.83
    IDX_INT             0.071    0.0048       0.83       0.84
    IDX_NN1             0.100    0.0007       0.98       0.90
  reference-weighted regret (partner-free, the seat's primary estimand)
    FLAT                0.203    0.0012       0.88       0.79
    IDX_ADD             0.104    0.0016       0.86       0.93
    IDX_INT             0.057    0.0087       0.75       0.86
    IDX_NN1             0.092    0.0012       0.88       0.94
World-indexing roughly halves-to-thirds the magnitude error when the held-out
world is an interpolation inside the factorial. For choosing which circuit to
deploy, the flat catalogue is already near-perfect (mean regret 0.004 and 0.001
of optimal EV) because r0003/r0015 are at or near the top in almost every world;
only the nearest-neighbour index reduces it further, by ~0.004. Under
extrapolation (hold out an entire property level) the regression indexes are
often WORSE than flat for deployment: e.g. holding out a p_bust level, pick
regret FLAT 0.004 vs IDX_ADD 0.113 vs IDX_INT 0.141; holding out gate, every
predictor fails (max regret 1.0) and none is reliably better. Ruin-only (64)
and the seat's 16-world identified design give the same pattern. The
occupancy-demotion kill condition does not fire here: under reference weighting
circuit share 0.53 > circuit x world 0.25 (128 worlds), 0.45 > 0.29 (16).

(c) Real (reconstructed) worlds, optimal partner, 4 worlds:
  MD version / r0003           circuit  cxw   cross-world tau  flat LOWO MAE
  reconstructed / committed    0.41    0.58   0.04             0.37
  reconstructed / tie-fixed    0.60    0.31   0.39             0.24
  audited / committed          0.45    0.50   0.26             0.34
  audited / tie-fixed          0.61    0.29   0.41             0.22
Flat leave-one-world-out pick regret on these 4 worlds is <= 0.06 in all
variants. The audited Martian Dice rules reorder its STOP column (never-bank
r0004: 0.23 -> 0.97; r0003 drops from 1st to 4th, 0.987 -> 0.937), which is a
large world-fidelity effect on ranks but not on which circuit a catalogue
would deploy.
Plain conclusion: a world-indexed r_i(W) beats a flat catalogue at predicting
HOW MUCH a circuit retains in an unseen world that is an interpolation of seen
property levels, but essentially never at deciding WHICH circuit to use, and it
is worse than flat when asked to extrapolate. The strongest "the value belongs
to the partner / the world" evidence (the 0.0 vs 1.0 swings) was produced by a
tie-breaking choice in r0003's definition at pot = 0.

4. DID IT RESOLVE THE QUESTION
Partly. Resolved: the Coloretto zero cell (artifact, not a partial-loss
failure), the partner-spread block on r0003 (artifact plus partner floor), and a
prospective flat-vs-indexed comparison on the synthetic family. Not resolved:
(i) real-world r_i(W) cannot be tested -- 4 reconstructed worlds with no shared
property vocabulary are too few to fit or hold out an index; (ii) the full
re-run of the partner matrix under the audited Martian Dice rules was not
completed (timed out; used committed 3-partner columns), and I did not re-walk
every maturity rung under the audited rules; (iii) the adversary / denial-
interface question was not attempted: the bench's exact solver is single-agent
solitaire and building a two-player world is outside a 4-hour, 1-CPU-hour budget.
The synthetic result rests on one generator (FOUNDRY) whose properties are
exactly the index variables, which favours the indexed models.

5. CONSEQUENCES
- Instrument defect (Ludus seat; anyone reusing ludus/bench/circuits.py):
  r0003 stops on exact ties `e_gain == p_dead*pot`, including at pot = 0 where
  continuing is free. This manufactures the 0.0000 cells recorded in the r0003
  fossil, Lucky Numbers and Coloretto. The ledger's r0003 entry, the maturity
  block "partner spread 1.0000 in FOUNDRY[gate=1,k=3,cap=4]" and the cycle-4
  narrative ("partner swing concentrated in gate & not-decoy") should be
  re-examined with a tie-continue variant registered as a new circuit (the old
  one kept as a fossil). PARTNER_ROBUST should be measured relative to the
  optimal stopper under the same partner; raw spread counts the partner's own
  floor.
- False premise: Coloretto has no death event, so it cannot test r0003's
  "total vs partial loss on death" precondition; the ledger's "Untested where
  loss is partial" is actually answered by the committed DecayFoundry cells
  (r0003 = 1.0 in all of them) and should say so.
- Clean mostly-null on the representation question: the seat's decision not to
  build r_i(W) is supported for deployment purposes; an index is worth it only
  if magnitudes (not choices) are the product, and only by interpolation.
- Reproduction: cycle-4 FOUNDRY cells reproduced to 5e-7; the occupancy
  demotion's kill condition does not fire on a 128-world extension.
- Harness gap: the "identified design" (p_bust varied) has no committed script
  and no committed cells, only its summary; it had to be reconstructed.
Who should know: the Ludus seat (owner of the bench and ledger), and any seat
consuming r0003 / the cycle-4 verdict as evidence about ecological dependence of
mechanisms.

6. COST
About 1.5 hours of my time. CPU about 14 minutes total (extended factorial 2 s;
Coloretto diagnosis 43 s; tie test 80 s; abandoned audited-Martian-Dice full
matrix ~11 CPU-min before a 900 s timeout; analysis seconds). Peak RSS 1.2 GB,
at most 2 processes. Not done: audited Martian Dice full 6x6 partner matrix,
maturity-rung re-walk under audited rules, anything on adversaries/self-play.
