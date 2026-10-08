# THESEUS-30c preregistration -- in-context pairwise epistasis (composition detector v3)

Currency: 2026-10-08. Committed before any run of theseus/synth/composition_v3.py except
a crash test on one arm genome (8 rules, 0 pairs, 0.8 s); no control genome was scored.

## Why

30b (9a329ab29): with a validated whole-genome detector (v2), every v0_1 arm has 0
compositions -- but v2 requires the WHOLE genome to be the two inert parts, which a
10-14-rule genome full of active rules almost never can be. v3 asks the question in
context: do two rules exist that each do nothing when added to the rest of the genome,
yet act together?

## Detector v3

(i, j) is an in-context composition iff trace(G-{j}) == trace(G-{i,j}) and
trace(G-{i}) == trace(G-{i,j}) and trace(G) != trace(G-{i,j}), bitwise at IC seeds 0, 1.

## Design

Gate built and scored inside the same job (seed 20261008, 40 each): planted (active
background of 4-8 rules from memory-free ops + writer "remember" into memory m + reader
"inject"/"modulate" reading m at random positions), neg_bg (background alone), neg_recall
(background + writer + "recall"). Arms: the identical v0_1 sample of 23b/30b.

## Decision rule

GATE: planted pair found in >= 80% of planted genomes; neg_bg with any composition <= 5%;
writer/recall pair found in <= 5% of neg_recall. Gate fails -> INSTRUMENT FAILED, arms not
read as evidence.
Gate passes:
  - per arm: share of genomes with >= 1 in-context composition;
  - H-COMP: D share > one-shot (P+B+C) share and > R share, one-sided Fisher p < 0.05
    each -> SUPPORTED; D <= both -> NOT SUPPORTED; else INDETERMINATE;
  - every arm 0 -> WALL-IN-CONTEXT-AT-v0_1.

## Predictions

W1 gate passes.                                                     p = 0.8
W2 at least one arm has >= 1 genome with an in-context composition. p = 0.6
W3 H-COMP is not SUPPORTED.                                         p = 0.8

Compute: per genome 1 + n + n(n-1)/2 trace pairs at 2 seeds; ~1100 genomes, ~1.5 CPU-hours.
