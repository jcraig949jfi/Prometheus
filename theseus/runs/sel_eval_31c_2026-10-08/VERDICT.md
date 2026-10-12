# THESEUS-31c verdict (prereg roles/Theseus/prereg/2026-10-08_task_selection/, b9a8413da)

Runs (PYTHONHASHSEED=0, ecology-only, --g0-readers --cond-ops --aligned-binding --elite-grids
pca --pop-cap 300 --dark-protect-gens 3 --elite-protect-k 150 --seed-select 1.5):
  TASKSEL-J   v0_2t_2026-10-08   (--quality task: J at V 4, k 4, 200/200)
  TASKSEL-REP v0_2tr_2026-10-08  (--quality rep)
Scans: composition_v3 on each (gates inside); sel_eval (J at V 4, k 4, 400/400, 100 viable D).

GATES: planted 40/40, neg_bg 0/40, neg_recall 0/40 in BOTH scans. PASS.
MANIPULATION CHECK: D mean J .964 (TASKSEL-J) vs .856 (TASKSEL-REP); one-sided Mann-Whitney
p .00058. PASSES -- task selection took.
PRIMARY H-SEL-COMP: D genomes with an in-context composition: 1/120 (J) vs 0/120 (REP);
one-sided Fisher p .50. Other lanes: G 3/120 vs 0/120; E 0/115 vs 0/120; S 0/120 vs 0/120.
VERDICT: INDETERMINATE (J share above REP point-wise, not significant).

Reading: selection on cue recall raised task capability but did not assemble writer/reader
compositions. The task is solvable without composition (the 1-part relay control scores J
.97), and relays are far easier to reach than an aligned writer + inert reader pair, so
selection takes the cheap route. Composition will only be selected for when it is NECESSARY:
successor THESEUS-36 designs a task no single-part mechanism can solve (readout restricted so
the stored cue must be re-released by a second part at query time) and repeats 31c on it.

Predictions: U1 manipulation passes RIGHT; U2 H-SEL-COMP supported WRONG; U3 D share >= 5%
WRONG (1/120).
