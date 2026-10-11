# THESEUS-33 verdict (prereg roles/Theseus/prereg/2026-10-08_degeneracy/, e782e3e28)

Run: python -m theseus.synth.task_degen --tag degeneracy_2026-10-08 --workers 4 (checkpointed;
killed once at the 2 h background limit and resumed; lens-lane genomes are slow because
lensmap runs a Tyche lens every step). Population: the 31b carrier-size-0 genomes (109) +
40 gate controls. Pairwise knockouts at V 8, k 8, task seed 0; drop >= .2.

GATE: redundant_relay degenerate 20/20; single_relay carrier size 1 in 20/20, degenerate 0.
PASSES.

Per arm (carrier-size-0 genomes: degenerate = some critical pair / distributed = no critical
single or pair), against the arm's 31b capable knockout set:
  D  24 of 40: degenerate 10, distributed 14      E  28 of 40: 15 / 13
  R  16 of 40: 14 / 2                             A  12 of 40: 10 / 2
  B  10 of 40: 8 / 2   C 9 of 40: 8 / 1   P 4 of 35: 4 / 0   G0 6 of 25: 6 / 0
H-DEGEN (no-single-point-of-failure share): D 24/40 > one-shot 23/115 (one-sided Fisher
p 4.8e-6) but D vs R 16/40 p .059 (> .05). VERDICT: INDETERMINATE.

Preregistered descriptive (pair structure), which is the new information: among genomes with
no single point of failure, other arms almost always hold the cue in exactly TWO redundant
carriers (a critical pair exists: R 14/16, A 10/12, one-shot 20/23, G0 6/6), while deep
descendants mostly hold it DISTRIBUTED over three or more overlapping paths (D 14/24, E
13/28). Share of capable genomes with a distributed carrier: D 14/40 vs R 2/40 (Fisher
p .0007) vs one-shot 3/115 (p 3e-7). These p-values are POST HOC (the distributed share was
not the preregistered test) -- successor THESEUS-35 preregisters it on a fresh master seed.
Commonest D critical pairs: react+react (4), react+lensmap (3).

Predictions: Z1 gate RIGHT; Z2 H-DEGEN supported WRONG (indeterminate); Z3 most D
carrier-size-0 genomes are DISTRIBUTED RIGHT (14/24).
