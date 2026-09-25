# PTE-C1 A0 findings (physics census, 5000 cells, closed 14:43Z)

Currency: 2026-09-24. Rows: ~/ananke_runs/pte-c1/cells.jsonl (wave A0),
summarised in a0_interactions.json beside this file, produced by
prometheus/ananke/analysis_a0.py (committed 47b1e4b27 BEFORE it was run;
rung cutoffs declared in its header). Plan: ../ANALYSIS_PLAN_C1_A0.md.
A0 ran 5000/5000, 0 failed, 0 censored.

## 1. The ladder, per 1000 cells per family (design-independent rungs)

  family  L1 perturbable  L2 distal influence  L2' relay/latch plant
  RELAY   109             7                    19   (L2' given L2: 0/7)
  XOR     108             3                    0    (plant not designed for XOR)
  MAJ     226             6                    0
  FLIP    196             18 (local teacher path, not distal)   0
  HOLD    156             279 (local by design)                  879

Reading, stated at the strength the data allow:
- In the comm families, perturbability is common (11-23%) and distal
  influence of a random program is rare (0.3-0.7%): a ~20-35x drop. This
  is the operator's "reactivity vs functional transport" gap, now on a
  design-independent rung.
- CAVEAT that limits it: L1 is predicted almost entirely by PROGRAM-SPACE
  dials (the RELAY L1 tree splits on rules, prog_len, state_dim; AUC
  0.91-0.96 from single dials, ratios add nothing). The L2 proxy uses the
  same random programs. So A0 cannot separate "this physics cannot carry
  influence" from "random programs rarely relay". That separation is A1's
  job (living vs uniform arms) and the B phys-track's.
- In RELAY, the 7 distal-influence cells and the 19 plant-viable cells
  are DISJOINT. The two middle rungs do not measure one thing.

## 2. Interaction analysis (preregistered test)

L1: no ratio EXPLAINS (single dials already reach AUC 0.91-0.96 out of
sample; ratios add <= 0.005; the family-permuted null sits at 0.41-0.57).
L2 and L2': INDETERMINATE in every comm family and pooled -- fewer than
the declared 10 positives in the FIT half (pooled comm L2 rate 0.5%,
L2' 0.6%). The interaction law the operator asked about cannot be
fitted from A0 at this prevalence. That is an eligibility result: a
sparse region needs targeted sampling (B transects), not a bigger census.

## 3. Exploratory (not preregistered; n = 19; hypotheses only)

RELAY plant viability by level (viable / cells):
  decay_shift  0: 19/245   1: 0/255   3: 0/250   6: 0/250
  economy      off 10/301  low 9/335  high 0/364
  loss         0: 8/251  .1: 9/235  .3: 2/261  .6: 0/253
  delta        16: 14/328  8: 3/321  4: 2/351
  lat_base     1: 10/361  2: 7/306  4: 2/333
Every viable cell has decay 0: an AND of gates (no decay, economy not
high, loss <= .3, enough time budget) rather than one ratio. Most likely
mechanism: the relay plant suppresses echoes with "re-emit only if my
value changed"; any decay changes the value every tick, so the plant
re-emits continuously and its own echoes swamp the next cue. If so this
is a DESIGN failure (L2'), not a physics limit on transport -- the B
phys-track decay transect, and a symmetric-decay or decay-aware plant
variant (ANANKE-20), are the tests. Not claimed until they run.

## 4. What this changes

Nothing in C1 (frozen). For interpretation: A1 is now the decisive wave
for the ladder's L2 -> L3 step, because A0's L2 is prior-bound. For C2:
the "habitable zone" must be defined by an EVOLVED or intervention-
verified transport rung, not by random-program L2 or by one plant.
